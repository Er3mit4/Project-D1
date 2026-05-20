#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
align_arsenal_pages.py — Ferramenta de Alinhamento e Auditoria de Paginação do Arsenal
D&D 5e - Projeto D1

Esta ferramenta lê o banco de dados de itens (arsenal.json e arsenal_reviewed.json)
e os PDFs do Livro do Jogador e Guia do Mestre para validar, auditar e corrigir
automaticamente a paginação dos itens do Arsenal.

Otimização: Pré-carrega o texto de todas as páginas relevantes dos PDFs em memória
(cache) antes de iniciar a varredura, evitando leitura repetida de disco.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path

# Configurações padrão dos PDFs
DEFAULT_PDF_PHB = r"D:\Documents\Sessão RPG\D&D\dd-5e-livro-do-jogador-fundo-branco-biblioteca-c3a9lfica.pdf"
DEFAULT_PDF_DMG = r"D:\Documents\Sessão RPG\D&D\dd-5e-guia-do-mestre-biblioteca-elfica.pdf"
DEFAULT_PDF_XGE = r"D:\Documents\Sessão RPG\D&D\xge.pdf"  # Opcional

# Mapeamento de fonte para PDF
SOURCE_PHB = "Livro do Jogador"
SOURCE_DMG = "Guia do Mestre"
SOURCE_XGE = "Guia de Xanathar para Todas as Coisas"

# Faixas de páginas PDF a varrer por fonte
PHB_PAGE_RANGE = (143, 165)  # Equipamentos, armas, armaduras: págs PDF 143-165
DMG_PAGE_RANGE = (148, 232)  # Itens mágicos A-Z + artefatos: págs PDF 148-232

# Desvio máximo (em páginas) aceito como correção automática.
# Desvios maiores indicam provável falso positivo (nome encontrado num índice/tabela
# do capítulo em vez da página real do item).
MAX_TRUSTED_DIFF = 5


def check_dependencies():
    """Verifica se a biblioteca PyMuPDF (fitz) está instalada."""
    try:
        import fitz
        return True, fitz
    except ImportError:
        return False, None


def get_printed_page_no(page_text: str, lines: list, fallback: int) -> int:
    """Tenta ler o número impresso na página a partir das primeiras/últimas linhas."""
    for line in lines[-4:] + lines[:4]:
        stripped = line.strip()
        if stripped.isdigit() and 100 <= int(stripped) <= 400:
            return int(stripped)
    return fallback


def build_page_cache(doc, page_range: tuple, fitz_module) -> dict:
    """
    Pré-carrega (cache) o texto de todas as páginas do PDF no intervalo dado.
    Retorna um dicionário: {page_idx_0based: {"text": str, "lines": list, "lower": str}}.
    Esta abordagem elimina leitura repetitiva de disco durante a varredura de itens.
    """
    start, end = page_range
    cache = {}
    max_pages = len(doc)
    print(f"[*] Pré-carregando cache de páginas {start}-{min(end, max_pages)} do PDF...")

    for page_idx in range(start - 1, min(end, max_pages)):
        page = doc[page_idx]
        text = page.get_text("text")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        cache[page_idx] = {
            "text": text,
            "lines": lines,
            "lower": text.lower(),
        }
    print(f"[*] Cache de {len(cache)} páginas carregado.")
    return cache


def scan_item(item: dict, page_cache: dict, page_range: tuple) -> dict:
    """
    Escaneia o cache de páginas para encontrar a página real de um item.
    Retorna um dicionário com os resultados da análise.
    """
    name = item.get("nome", "") or ""
    name_upper = name.upper()
    nome_clean = name_upper.strip()

    p_print_db = item.get("pagina_livro", 0) or 0
    p_pdf_db = item.get("pagina_pdf", 0) or 0

    # Termos adicionais para pontuar a correspondência
    raridade = (item.get("raridade") or "").lower()
    categoria = (item.get("categoria") or "").lower()
    tipo = (item.get("tipo") or "").lower()
    preco = (item.get("preco") or "").lower()

    best_page = None
    best_score = 0

    for page_idx, page_data in page_cache.items():
        lines = page_data["lines"]
        text_upper = page_data["text"].upper()
        lower = page_data["lower"]

        score = 0

        # Pontuação primária: nome do item
        if nome_clean in [l.upper() for l in lines]:
            score += 20
        elif nome_clean in text_upper:
            score += 10

        if score == 0:
            continue

        # Pontuações secundárias
        if raridade and raridade in lower:
            score += 8
        if categoria and categoria in lower:
            score += 5
        if tipo and tipo in lower:
            score += 4
        if preco and preco in lower:
            score += 3

        if score > best_score:
            best_score = score
            best_page = page_idx

    if best_page is not None and best_score >= 10:
        pdf_page_actual = best_page + 1  # 1-indexed
        lines = page_cache[best_page]["lines"]
        printed_page_actual = get_printed_page_no(
            page_cache[best_page]["text"], lines, pdf_page_actual
        )

        diff_pdf = pdf_page_actual - p_pdf_db
        status = "CORRETAS" if diff_pdf == 0 else f"DESVIADAS ({diff_pdf:+d})"

        return {
            "item": item,
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
            "item": item,
            "name": name,
            "db_print": p_print_db,
            "db_pdf": p_pdf_db,
            "actual_print": None,
            "actual_pdf": None,
            "score": 0,
            "status": "NÃO ENCONTRADO",
            "diff": None,
        }


def scan_and_align(items_data: list, pdf_path: str, page_range: tuple, fitz_module,
                   verbose: bool = False, source_label: str = "") -> list:
    """
    Abre o PDF, pré-carrega o cache e escaneia todos os itens da fonte especificada.
    """
    print(f"\n[*] Abrindo PDF ({source_label}): {pdf_path}")
    doc = fitz_module.open(pdf_path)

    page_cache = build_page_cache(doc, page_range, fitz_module)

    # Filtra apenas os itens da fonte correspondente
    items = [i for i in items_data if i.get("fonte", "") == source_label]
    print(f"[*] Analisando {len(items)} itens ({source_label}) no PDF...")

    results = []
    not_found_count = 0
    for item in items:
        result = scan_item(item, page_cache, page_range)
        results.append(result)
        if result["actual_pdf"] is None:
            not_found_count += 1
            if verbose:
                print(f"  [?] Não encontrado: '{result['name']}'")
        elif result["diff"] != 0 and verbose:
            print(
                f"  [!] {result['name']}: DB(p:{result['db_print']}, pdf:{result['db_pdf']}) "
                f"-> PDF(p:{result['actual_print']}, pdf:{result['actual_pdf']}) [{result['status']}]"
            )

    doc.close()
    return results


def print_report(results: list, source_label: str):
    """Imprime o relatório de auditoria."""
    total = len(results)
    correct = sum(1 for x in results if x["diff"] == 0)
    off = sum(1 for x in results if x["diff"] is not None and x["diff"] != 0)
    not_found = sum(1 for x in results if x["actual_pdf"] is None)

    print("\n" + "=" * 55)
    print(f"       RELATÓRIO DE AUDITORIA — {source_label.upper()}")
    print("=" * 55)
    print(f"Total de itens auditados:  {total}")
    print(f"  * Páginas corretas:      {correct}")
    print(f"  * Desviadas:             {off}")
    print(f"  * Não encontradas:       {not_found}")
    print("=" * 55)
    return off, not_found


def apply_corrections(results: list, files_to_process: list, source_label: str):
    """Aplica correções de paginação nos arquivos JSON."""
    corrections_lookup = {}
    skipped = []
    for x in results:
        diff = x["diff"]
        if x["actual_pdf"] is not None and diff != 0:
            if abs(diff) <= MAX_TRUSTED_DIFF:
                corrections_lookup[x["name"]] = {
                    "pagina_livro": x["actual_print"],
                    "pagina_pdf": x["actual_pdf"],
                    "referencia": f"{x['actual_print']} (PDF: {x['actual_pdf']})",
                }
            else:
                skipped.append(x["name"])
                print(
                    f"  [SKIP] '{x['name']}': desvio de {diff:+d} págs excede o limite "
                    f"de confiança ({MAX_TRUSTED_DIFF}). Possível falso positivo. Ignorado."
                )

    if not corrections_lookup:
        print(f"[*] Nenhuma correção necessária para '{source_label}'.")
        return

    print(f"\n[*] Aplicando {len(corrections_lookup)} correções em {len(files_to_process)} arquivo(s)...")
    for fpath in files_to_process:
        print(f"  -> Atualizando {fpath.name}...")
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)

        updated = 0
        for item in data:
            if item.get("fonte") == source_label and item.get("nome") in corrections_lookup:
                corr = corrections_lookup[item["nome"]]
                item["pagina_livro"] = corr["pagina_livro"]
                item["pagina_pdf"] = corr["pagina_pdf"]
                item["referencia"] = corr["referencia"]
                updated += 1

        with open(fpath, "w", encoding="utf-8") as out:
            json.dump(data, out, ensure_ascii=False, indent=2)

        print(f"     Pronto! {updated} itens atualizados.")


def main():
    parser = argparse.ArgumentParser(
        description="Audita e alinha as páginas dos itens do Arsenal com os PDFs (Projeto D1)."
    )
    parser.add_argument(
        "--pdf-phb",
        default=DEFAULT_PDF_PHB,
        help=f"Caminho do PDF do Livro do Jogador (Padrão: {DEFAULT_PDF_PHB})",
    )
    parser.add_argument(
        "--pdf-dmg",
        default=DEFAULT_PDF_DMG,
        help=f"Caminho do PDF do Guia do Mestre (Padrão: {DEFAULT_PDF_DMG})",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as correções diretamente nos arquivos JSON do projeto.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Exibe detalhes de cada item durante a verificação.",
    )
    parser.add_argument(
        "--fonte",
        choices=[SOURCE_PHB, SOURCE_DMG, "ambos"],
        default="ambos",
        help="Qual fonte processar (padrão: ambos).",
    )

    args = parser.parse_args()

    # 1. Valida dependência
    has_dep, fitz_module = check_dependencies()
    if not has_dep:
        print("[ERRO] A biblioteca PyMuPDF (fitz) não está instalada.")
        print("  pip install pymupdf")
        sys.exit(1)

    # 2. Localiza os arquivos JSON do Arsenal
    arsenal_dir = Path(__file__).resolve().parent
    json_names = ["arsenal.json", "arsenal_reviewed.json"]
    files_to_process = [arsenal_dir / name for name in json_names if (arsenal_dir / name).exists()]

    if not files_to_process:
        print("[ERRO] Nenhum arquivo arsenal.json ou arsenal_reviewed.json encontrado.")
        sys.exit(1)

    # 3. Carrega a base de referência
    reference_file = arsenal_dir / "arsenal.json"
    if not reference_file.exists():
        reference_file = files_to_process[0]

    print(f"[*] Carregando base de dados de referência: {reference_file.name}")
    with open(reference_file, encoding="utf-8") as f:
        items_data = json.load(f)

    print(f"[*] Total de itens na base: {len(items_data)}")

    all_results = []

    # 4. Processa PHB (Livro do Jogador)
    if args.fonte in (SOURCE_PHB, "ambos"):
        if not os.path.exists(args.pdf_phb):
            print(f"[AVISO] PDF do Livro do Jogador não encontrado: {args.pdf_phb}")
        else:
            results_phb = scan_and_align(
                items_data, args.pdf_phb, PHB_PAGE_RANGE,
                fitz_module, args.verbose, SOURCE_PHB
            )
            all_results.extend(results_phb)
            off_phb, nf_phb = print_report(results_phb, SOURCE_PHB)

            if args.apply:
                apply_corrections(results_phb, files_to_process, SOURCE_PHB)

    # 5. Processa DMG (Guia do Mestre)
    if args.fonte in (SOURCE_DMG, "ambos"):
        if not os.path.exists(args.pdf_dmg):
            print(f"[AVISO] PDF do Guia do Mestre não encontrado: {args.pdf_dmg}")
        else:
            results_dmg = scan_and_align(
                items_data, args.pdf_dmg, DMG_PAGE_RANGE,
                fitz_module, args.verbose, SOURCE_DMG
            )
            all_results.extend(results_dmg)
            off_dmg, nf_dmg = print_report(results_dmg, SOURCE_DMG)

            if args.apply:
                apply_corrections(results_dmg, files_to_process, SOURCE_DMG)

    # 6. Mensagem final
    total_off = sum(1 for x in all_results if x["diff"] is not None and x["diff"] != 0)
    total_nf = sum(1 for x in all_results if x["actual_pdf"] is None)

    if args.apply:
        print("\n[SUCESSO] Correções aplicadas nos arquivos JSON!")
        print("[DICA] Lembre-se de regerar os builds:")
        print("  python Arsenal/build_html.py")
        print("  python build_unified.py  (na raiz do projeto)")
    elif total_off > 0 or total_nf > 0:
        print("\n[AVISO] Existem desalinhamentos detectados.")
        print("Para corrigi-los, rode novamente com `--apply`:")
        print("  python align_arsenal_pages.py --apply")
    else:
        print("\n[OK] Todos os itens auditados estão com paginação correta!")


if __name__ == "__main__":
    main()
