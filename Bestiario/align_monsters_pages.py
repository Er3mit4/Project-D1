#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
align_monsters_pages.py — Ferramenta de Alinhamento e Auditoria de Paginação do Bestiário
D&D 5e - Projeto D1

Esta ferramenta lê o banco de dados de monstros (monstros.json e monstros_reviewed.json)
e o PDF do Manual dos Monstros para validar, auditar e corrigir automaticamente a
paginação dos monstros do Bestiário.

Normalização de hífens: nomes como 'Kuo -toa' (com espaço antes do hífen, artefato
de OCR) são normalizados para 'KUO-TOA' antes da busca para aumentar o recall.

Otimização: Pré-carrega o texto de todas as páginas relevantes do PDF em memória
(cache) antes de iniciar a varredura, evitando leitura repetitiva de disco.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path

# Configurações padrão
DEFAULT_PDF = r"D:\Documents\Sessão RPG\D&D\old-dd-5e-manual-dos-monstros-biblioteca-elfica.pdf"
DEFAULT_JSON = "monstros.json"

# Faixa de páginas PDF do Manual dos Monstros a varrer (índice 0)
MM_PAGE_RANGE = (10, 354)  # Cobre todo o conteúdo de monstros do MM

# Desvio máximo (em páginas) aceito como correção automática.
# Desvios maiores que isso são provavelmente falsos positivos.
MAX_TRUSTED_DIFF = 5


def check_dependencies():
    """Verifica se a biblioteca PyMuPDF (fitz) está instalada."""
    try:
        import fitz
        return True, fitz
    except ImportError:
        return False, None


def get_printed_page_no(lines: list, fallback: int) -> int:
    """Tenta ler o número impresso na página a partir das primeiras/últimas linhas."""
    for line in lines[-4:] + lines[:4]:
        stripped = line.strip()
        if stripped.isdigit() and 1 <= int(stripped) <= 400:
            return int(stripped)
    return fallback


def normalize_name(name: str) -> str:
    """
    Normaliza um nome para busca: converte para maiúsculas e remove espaços
    ao redor de hífens (artefato de OCR: 'Kuo -toa' → 'KUO-TOA').
    """
    normalized = re.sub(r"\s*-\s*", "-", name.strip())
    return normalized.upper()


def build_page_cache(doc, page_range: tuple) -> dict:
    """
    Pré-carrega (cache) o texto de todas as páginas do PDF no intervalo dado.
    Retorna: {page_idx_0based: {"text": str, "lines": list, "lower": str,
                                 "lines_upper": list, "lines_normalized": list}}.
    """
    start, end = page_range
    cache = {}
    max_pages = len(doc)
    effective_end = min(end, max_pages)
    print(f"[*] Pré-carregando cache de páginas {start}-{effective_end} do PDF...")

    for page_idx in range(start - 1, effective_end):
        page = doc[page_idx]
        text = page.get_text("text")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        cache[page_idx] = {
            "text": text,
            "lines": lines,
            "lower": text.lower(),
            "lines_upper": [l.upper() for l in lines],
            # Normaliza hífens nas linhas para facilitar matching
            "lines_normalized": [normalize_name(l) for l in lines],
        }

    print(f"[*] Cache de {len(cache)} páginas carregado.")
    return cache


def scan_monster(monster: dict, page_cache: dict) -> dict:
    """
    Escaneia o cache de páginas para encontrar a página real de um monstro.
    Retorna um dicionário com os resultados da análise.
    """
    name = monster.get("nome", "") or ""
    name_upper = name.upper().strip()
    name_normalized = normalize_name(name)  # Ex: 'Kuo -toa' → 'KUO-TOA'

    p_print_db = monster.get("pagina_livro", 0) or 0
    p_pdf_db = monster.get("pagina_pdf", 0) or 0

    # Termos adicionais para pontuar a correspondência
    nd = str(monster.get("nd") or "").strip()
    tipo = (monster.get("tipo_criatura") or "").lower()
    tamanho = (monster.get("tamanho") or "").lower()
    ca = str(monster.get("ca") or "").lower().split()[0] if monster.get("ca") else ""

    best_page = None
    best_score = 0

    for page_idx, page_data in page_cache.items():
        lines_upper = page_data["lines_upper"]
        lines_normalized = page_data["lines_normalized"]
        lower = page_data["lower"]

        score = 0

        # Pontuação primária: nome do monstro como linha exata
        # Tenta primeiro com nome normalizado (sem espaços extras ao redor de hífens)
        if name_normalized in lines_normalized:
            score += 25
        elif name_upper in lines_upper:
            score += 22
        elif name_normalized in page_data["text"].upper().replace(" -", "-").replace("- ", "-"):
            score += 12
        elif name_upper in page_data["text"].upper():
            score += 10

        if score == 0:
            continue

        # Pontuações secundárias para validação contextual
        if nd and f"nível de desafio {nd}" in lower:
            score += 10
        elif nd and nd in lower:
            score += 5

        if tipo and tipo in lower:
            score += 5
        if tamanho and tamanho in lower:
            score += 3
        if ca and f"classe de armadura {ca}" in lower:
            score += 4

        if score > best_score:
            best_score = score
            best_page = page_idx

    if best_page is not None and best_score >= 12:
        pdf_page_actual = best_page + 1  # 1-indexed
        lines = page_cache[best_page]["lines"]
        printed_page_actual = get_printed_page_no(lines, pdf_page_actual)

        diff_pdf = pdf_page_actual - p_pdf_db
        status = "CORRETAS" if diff_pdf == 0 else f"DESVIADAS ({diff_pdf:+d})"

        return {
            "monster": monster,
            "name": name,
            "db_print": p_print_db,
            "db_pdf": p_pdf_db,
            "actual_print": printed_page_actual,
            "actual_pdf": pdf_page_actual,
            "score": best_score,
            "status": status,
            "diff": diff_pdf,
        }
    else:
        return {
            "monster": monster,
            "name": name,
            "db_print": p_print_db,
            "db_pdf": p_pdf_db,
            "actual_print": None,
            "actual_pdf": None,
            "score": 0,
            "status": "NÃO ENCONTRADO",
            "diff": None,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Audita e alinha as páginas dos monstros do Bestiário com o PDF do Manual dos Monstros (Projeto D1)."
    )
    parser.add_argument(
        "--pdf",
        default=DEFAULT_PDF,
        help=f"Caminho do PDF do Manual dos Monstros (Padrão: {DEFAULT_PDF})",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as correções diretamente nos arquivos JSON do projeto.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Exibe detalhes de cada monstro durante a verificação.",
    )

    args = parser.parse_args()

    # 1. Valida dependência
    has_dep, fitz_module = check_dependencies()
    if not has_dep:
        print("[ERRO] A biblioteca PyMuPDF (fitz) não está instalada.")
        print("  pip install pymupdf")
        sys.exit(1)

    # 2. Valida existência do PDF
    if not os.path.exists(args.pdf):
        print(f"[ERRO] PDF não encontrado:\n{args.pdf}")
        print("Verifique o caminho ou informe via `--pdf <caminho>`.")
        sys.exit(1)

    # 3. Localiza arquivos JSON do Bestiário
    bestiario_dir = Path(__file__).resolve().parent
    json_names = ["monstros.json", "monstros_reviewed.json"]
    files_to_process = [bestiario_dir / name for name in json_names if (bestiario_dir / name).exists()]

    if not files_to_process:
        print("[ERRO] Nenhum arquivo monstros.json ou monstros_reviewed.json encontrado.")
        sys.exit(1)

    # 4. Carrega a base de referência
    reference_file = bestiario_dir / "monstros.json"
    if not reference_file.exists():
        reference_file = files_to_process[0]

    print(f"[*] Carregando base de dados de referência: {reference_file.name}")
    with open(reference_file, encoding="utf-8") as f:
        monsters_data = json.load(f)

    print(f"[*] Total de monstros na base: {len(monsters_data)}")

    # 5. Abre o PDF e constrói o cache de páginas
    print(f"[*] Abrindo PDF: {args.pdf}")
    doc = fitz_module.open(args.pdf)
    page_cache = build_page_cache(doc, MM_PAGE_RANGE)

    # 6. Escaneia todos os monstros
    print(f"[*] Analisando {len(monsters_data)} monstros no PDF...")
    results = []
    for monster in monsters_data:
        result = scan_monster(monster, page_cache)
        results.append(result)
        if result["actual_pdf"] is None:
            if args.verbose:
                print(f"  [?] Não encontrado: '{result['name']}'")
        elif result["diff"] != 0:
            if args.verbose:
                print(
                    f"  [!] {result['name']}: DB(p:{result['db_print']}, pdf:{result['db_pdf']}) "
                    f"-> PDF(p:{result['actual_print']}, pdf:{result['actual_pdf']}) [{result['status']}]"
                )

    doc.close()

    # 7. Relatório
    total = len(results)
    correct = sum(1 for x in results if x["diff"] == 0)
    off = sum(1 for x in results if x["diff"] is not None and x["diff"] != 0)
    not_found = sum(1 for x in results if x["actual_pdf"] is None)

    print("\n" + "=" * 55)
    print("       RELATÓRIO DE AUDITORIA — BESTIÁRIO")
    print("=" * 55)
    print(f"Total de monstros auditados: {total}")
    print(f"  * Páginas corretas:        {correct}")
    print(f"  * Desviadas:               {off}")
    print(f"  * Não encontradas:         {not_found}")
    print("=" * 55)

    # 8. Aplica correções se solicitado
    if args.apply:
        corrections_lookup = {}
        for x in results:
            diff = x["diff"]
            # Só aplica correções dentro do limite de desvio confiável
            if x["actual_pdf"] is not None and diff != 0 and abs(diff) <= MAX_TRUSTED_DIFF:
                corrections_lookup[x["name"]] = {
                    "pagina_livro": x["actual_print"],
                    "pagina_pdf": x["actual_pdf"],
                    "referencia": f"{x['actual_print']} (PDF: {x['actual_pdf']})",
                }
            elif x["actual_pdf"] is not None and diff != 0 and abs(diff) > MAX_TRUSTED_DIFF:
                print(f"  [SKIP] '{x['name']}': desvio de {diff:+d} págs excede o limite de confiança ({MAX_TRUSTED_DIFF}). Ignorado.")

        if not corrections_lookup:
            print("[*] Nenhuma correção necessária! Todos os arquivos já estão alinhados.")
        else:
            print(f"\n[*] Aplicando {len(corrections_lookup)} correções em {len(files_to_process)} arquivo(s)...")
            for fpath in files_to_process:
                print(f"  -> Atualizando {fpath.name}...")
                with open(fpath, encoding="utf-8") as f:
                    data = json.load(f)

                updated = 0
                for monster in data:
                    if monster.get("nome") in corrections_lookup:
                        corr = corrections_lookup[monster["nome"]]
                        monster["pagina_livro"] = corr["pagina_livro"]
                        monster["pagina_pdf"] = corr["pagina_pdf"]
                        monster["referencia"] = corr["referencia"]
                        updated += 1

                with open(fpath, "w", encoding="utf-8") as out:
                    json.dump(data, out, ensure_ascii=False, indent=2)

                print(f"     Pronto! {updated} monstros atualizados.")

            print("\n[SUCESSO] Correções aplicadas nos arquivos JSON!")
            print("[DICA] Lembre-se de regerar os builds:")
            print("  python Bestiario/build_html.py")
            print("  python build_unified.py  (na raiz do projeto)")
    elif off > 0 or not_found > 0:
        print("\n[AVISO] Existem desalinhamentos detectados.")
        print("Para corrigi-los, rode novamente com `--apply`:")
        print("  python align_monsters_pages.py --apply")
    else:
        print("\n[OK] Todos os monstros auditados estão com paginação correta!")


if __name__ == "__main__":
    main()
