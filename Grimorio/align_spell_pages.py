#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
align_spell_pages.py — Ferramenta de Alinhamento e Auditoria de Paginação do Grimório
D&D 5e - Projeto D1

Esta ferramenta lê o banco de dados de magias (spells.json e spells_reviewed.json) e o PDF
do Livro do Jogador para validar, auditar e corrigir automaticamente a paginação das magias.
"""

import os
import sys
import json
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from extraction_sources import pdf_path

# Configurações padrões
DEFAULT_PDF = pdf_path("phb")
DEFAULT_JSON = "spells.json"

def check_dependencies():
    """Verifica se a biblioteca PyMuPDF (fitz) está instalada."""
    try:
        import fitz
        return True, fitz
    except ImportError:
        return False, None

def get_printed_page_no(page_obj, default_val):
    """Tenta ler o número impresso na página do PDF analisando o topo e o rodapé."""
    text = page_obj.get_text("text")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    # Números de página costumam estar nas primeiras ou últimas linhas
    for line in lines[-4:] + lines[:4]:
        if line.isdigit() and 100 <= int(line) <= 350:
            return int(line)
    return default_val

def scan_and_align(pdf_path, spells_data, fitz_module, verbose=False):
    """
    Escaneia o PDF para encontrar a página real de cada magia.
    Retorna uma lista de dicionários com a análise de alinhamento.
    """
    print(f"[*] Abrindo PDF: {pdf_path}")
    doc = fitz_module.open(pdf_path)
    
    results = []
    print(f"[*] Analisando {len(spells_data)} magias no PDF...")
    
    for idx, s in enumerate(spells_data):
        name = s.get('name', '').upper()
        school = s.get('school', '')
        level = s.get('level', '')
        p_print_db = s.get('page_print', 0)
        p_pdf_db = s.get('page_pdf', 0)
        
        # Filtro de busca simplificado para classe/nível da magia
        level_str = f"truque de {school.lower()}" if level == "Truque" else school.lower()
        
        best_page = None
        best_score = 0
        
        # Escaneia a seção do capítulo 11 (pág. PDF 210 a 289)
        for page_idx in range(210, 289):
            page = doc[page_idx]
            text = page.get_text("text")
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            
            score = 0
            if name in [l.upper() for l in lines]:
                score += 20
                if name in lines:
                    score += 20
            elif name in text.upper():
                score += 10
                
            if score == 0:
                continue
                
            page_text_lower = " ".join(lines).lower()
            page_clean = page_text_lower.replace("º", "").replace("°", "")
            level_clean = level_str.lower().replace("º", "").replace("°", "")
            
            if school.lower() in page_clean:
                score += 5
            if level_clean in page_clean:
                score += 10
                
            if s.get('cast_time', '').lower() in page_text_lower:
                score += 5
            if s.get('range', '').lower() in page_text_lower:
                score += 5
            if s.get('duration', '').lower() in page_text_lower:
                score += 5
                
            if score > best_score:
                best_score = score
                best_page = page_idx
                
        if best_page is not None and best_score >= 15:
            pdf_page_actual = best_page + 1 # 1-indexed
            printed_page_actual = get_printed_page_no(doc[best_page], pdf_page_actual + 2)
            
            diff_pdf = pdf_page_actual - p_pdf_db
            
            status = "CORRETAS" if diff_pdf == 0 else f"DESVIADAS ({diff_pdf:+d})"
            
            results.append({
                "spell": s,
                "name": name,
                "db_print": p_print_db,
                "db_pdf": p_pdf_db,
                "actual_print": printed_page_actual,
                "actual_pdf": pdf_page_actual,
                "score": best_score,
                "status": status,
                "diff": diff_pdf
            })
            if verbose and diff_pdf != 0:
                print(f"  [!] {name}: DB(p:{p_print_db}, pdf:{p_pdf_db}) -> PDF(p:{printed_page_actual}, pdf:{pdf_page_actual}) [{status}]")
        else:
            results.append({
                "spell": s,
                "name": name,
                "db_print": p_print_db,
                "db_pdf": p_pdf_db,
                "actual_print": None,
                "actual_pdf": None,
                "score": 0,
                "status": "NÃO ENCONTRADA",
                "diff": None
            })
            print(f"  [?] Não foi possível encontrar a magia '{name}' de forma confiável no PDF.")
            
    return results

def main():
    parser = argparse.ArgumentParser(
        description="Audita e alinha as páginas das magias com o PDF do Livro do Jogador (Projeto D1)."
    )
    parser.add_argument(
        "--pdf",
        default=DEFAULT_PDF,
        help=f"Caminho do PDF do Livro do Jogador (Padrão: {DEFAULT_PDF})"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as correções diretamente nos arquivos JSON do projeto."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Exibe detalhes de cada magia durante a verificação."
    )
    
    args = parser.parse_args()
    
    # 1. Valida dependência
    has_dep, fitz_module = check_dependencies()
    if not has_dep:
        print("[ERRO] A biblioteca PyMuPDF (fitz) não está instalada no ambiente Python ativo.")
        print("Para instalá-la, execute o comando:")
        print("  pip install pymupdf")
        sys.exit(1)
        
    # 2. Valida existência do PDF
    if not os.path.exists(args.pdf):
        print(f"[ERRO] O arquivo PDF informado não foi encontrado:\n{args.pdf}")
        print("Verifique o caminho absoluto ou informe via `--pdf <caminho>`.")
        sys.exit(1)
        
    # 3. Localiza arquivos JSON no Grimório
    grimorio_dir = Path(__file__).resolve().parent
    files_to_process = []
    for p in grimorio_dir.rglob("*.json"):
        if p.name in ["spells.json", "spells_reviewed.json"]:
            files_to_process.append(p)
            
    if not files_to_process:
        # Se executado fora de Grimorio, tenta a pasta atual
        for p in Path(".").rglob("*.json"):
            if p.name in ["spells.json", "spells_reviewed.json"]:
                files_to_process.append(p)
                
    if not files_to_process:
        print("[ERRO] Nenhum arquivo spells.json ou spells_reviewed.json foi encontrado para auditar.")
        sys.exit(1)
        
    # Carrega a primeira instância do JSON para fazer a auditoria inicial
    reference_file = files_to_process[0]
    print(f"[*] Carregando base de dados de referência: {reference_file.name}")
    with open(reference_file, encoding="utf-8") as f:
        spells_data = json.load(f)
        
    # 4. Executa a varredura
    analysis = scan_and_align(args.pdf, spells_data, fitz_module, args.verbose)
    
    # 5. Gera estatísticas
    total = len(analysis)
    correct = sum(1 for x in analysis if x["diff"] == 0)
    off_by_2 = sum(1 for x in analysis if x["diff"] == 2)
    other = sum(1 for x in analysis if x["diff"] not in [0, 2, None])
    not_found = sum(1 for x in analysis if x["actual_pdf"] is None)
    
    print("\n" + "="*50)
    print("                RELATÓRIO DE AUDITORIA")
    print("="*50)
    print(f"Total de magias auditadas: {total}")
    print(f"  * Páginas corretas:        {correct}")
    print(f"  * Desviadas por +2 págs:   {off_by_2}")
    print(f"  * Outros desvios:          {other}")
    print(f"  * Não encontradas:         {not_found}")
    print("="*50)
    
    # 6. Aplica a correção
    if args.apply:
        if off_by_2 == 0 and other == 0:
            print("[*] Nenhuma correção necessária! Todos os arquivos já estão alinhados.")
            return
            
        print(f"\n[*] Aplicando correções em {len(files_to_process)} arquivos JSON...")
        
        # Mapeamento das correções detectadas nesta execução
        corrections_lookup = {}
        for x in analysis:
            if x["actual_pdf"] is not None and x["diff"] != 0:
                corrections_lookup[x["name"]] = {
                    "page_print": x["actual_print"],
                    "page_pdf": x["actual_pdf"]
                }
                
        for fpath in files_to_process:
            print(f"  -> Atualizando {fpath.name}...")
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
                
            updated = 0
            for s in data:
                name_upper = s.get("name", "").upper()
                if name_upper in corrections_lookup:
                    corr = corrections_lookup[name_upper]
                    s["page_print"] = corr["page_print"]
                    s["page_pdf"] = corr["page_pdf"]
                    updated += 1
                    
            # Gravação segura e compacta
            with open(fpath, "w", encoding="utf-8") as out:
                json.dump(data, out, ensure_ascii=False, separators=(",", ":"))
                
            print(f"     Pronto! {updated} magias atualizadas.")
            
        print("\n[SUCESSO] Todos os arquivos de dados foram corrigidos e salvos!")
        print("[DICA] Lembre-se de rodar os scripts de rebuild para regerar as páginas HTML:")
        print("  python build_html.py  (na pasta Grimorio)")
        print("  python build_unified.py  (na raiz do projeto)")
    else:
        if off_by_2 > 0 or other > 0:
            print("\n[AVISO] Existem desalinhamentos de paginação detectados.")
            print("Para corrigi-los automaticamente, rode novamente com o argumento `--apply`:")
            print("  python align_spell_pages.py --apply")

if __name__ == "__main__":
    main()
