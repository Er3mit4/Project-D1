#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MONSTROS_PATH = ROOT / "monstros.json"
REVIEWED_PATH = ROOT / "monstros_reviewed.json"
DOCLING_DIR = ROOT / "docling_out"

DOCLING_INPUTS = [
    ("mm_monsters_a_b/mm_monsters_a_b_p12_34.json", 12),
    ("mm_monsters_c_e/mm_monsters_c_e_p35_64.json", 35),
    ("mm_monsters_d/mm_monsters_d_p65_84.json", 65),
    ("mm_monsters_dragon1/mm_monsters_dragon1_p85_105.json", 85),
    ("mm_monsters_dragon2/mm_monsters_dragon2_p106_125.json", 106),
    ("mm_monsters_e_h/mm_monsters_e_h_p126_160.json", 126),
    ("mm_monsters_h_m/mm_monsters_h_m_p161_195.json", 161),
    ("mm_monsters_m_p/mm_monsters_m_p_p196_235.json", 196),
    ("mm_monsters_p_s/mm_monsters_p_s_p236_270.json", 236),
    ("mm_monsters_s_z/mm_monsters_s_z_p271_315.json", 271),
    ("mm_appendix_a/mm_appendix_a_p317_340.json", 317),
    ("mm_appendix_b/mm_appendix_b/mm_appendix_b_p341_349.json", 341),
]

ND_XP = {
    "0": "10", "1/8": "25", "1/4": "50", "1/2": "100",
    "1": "200", "2": "450", "3": "700", "4": "1.100",
    "5": "1.800", "6": "2.300", "7": "2.900", "8": "3.900",
    "9": "5.000", "10": "5.900", "11": "7.200", "12": "8.400",
    "13": "10.000", "14": "11.500", "15": "13.000", "16": "15.000",
    "17": "18.000", "18": "20.000", "19": "22.000", "20": "25.000",
    "21": "33.000", "22": "41.000", "23": "50.000", "24": "62.000",
    "25": "75.000", "26": "90.000", "27": "105.000", "28": "120.000",
    "29": "135.000", "30": "155.000",
}

SKIP_HEADERS = frozenset({
    "A\u00c7\u00d5ES", "REA\u00c7\u00d5ES",
    "A\u00c7\u00d5ES LEND\u00c1RIAS", "A\u00c7\u00d5ES DE COVIL",
    "EFEITOS REGIONAIS",
})

REFERENCE = {
    "Abocanhador Matraqueante": ("6", "2.300"),
    "Bulette": ("5", "1.800"),
    "Carni\u00e7al": ("1", "200"),
    "L\u00edvido": ("2", "450"),
    "Drag\u00e3o Azul Anci\u00e3o": ("23", "50.000"),
    "Drag\u00e3o Branco Anci\u00e3o": ("20", "25.000"),
    "Drag\u00e3o Branco Adulto": ("13", "10.000"),
    "Drag\u00e3o Branco Jovem": ("6", "2.300"),
    "Drag\u00e3o Branco Filhote": ("2", "450"),
    "Dracolich Azul Adulto": ("17", "18.000"),
    "Drag\u00e3o Negro Anci\u00e3o": ("21", "33.000"),
    "Drag\u00e3o Verde Anci\u00e3o": ("22", "41.000"),
    "Drag\u00e3o Verde Jovem": ("8", "3.900"),
    "Drag\u00e3o de Bronze Filhote": ("2", "450"),
    "Drag\u00e3o de Cobre Anci\u00e3o": ("21", "33.000"),
    "Drag\u00e3o de Lat\u00e3o Anci\u00e3o": ("20", "25.000"),
    "Drag\u00e3o de Lat\u00e3o Adulto": ("13", "10.000"),
    "Drag\u00e3o de Lat\u00e3o Jovem": ("6", "2.300"),
    "Drag\u00e3o de Ouro Anci\u00e3o": ("24", "62.000"),
    "Drag\u00e3o de Prata Anci\u00e3o": ("23", "50.000"),
    "Drag\u00e3o de Prata Jovem": ("9", "5.000"),
    "Drag\u00e3o de Prata Filhote": ("2", "450"),
    "Emp\u00edrico": ("23", "50.000"),
    "Esporo de G\u00e1s": ("1/2", "100"),
    "Esqueletos": ("1/4", "50"),
    "Gigante Dasnuvens": ("9", "5.000"),
    "Gigante de Pedra": ("7", "2.900"),
    "Gigante do Fogo": ("9", "5.000"),
    "Gigante do Gelo": ("8", "3.900"),
    "Golem de Ferro": ("16", "15.000"),
    "Hidra": ("8", "3.900"),
    "Homem -urso": ("5", "1.800"),
    "Mephit da Poeira": ("1/2", "100"),
    "Mephit do Gelo": ("1/2", "100"),
    "Naga Espiritual": ("8", "3.900"),
    "Naga Guardi\u00e3": ("10", "5.900"),
    "Oni": ("7", "2.900"),
    "P\u00e9gaso": ("2", "450"),
    "Perfurador": ("1/2", "100"),
    "Peryton": ("2", "450"),
    "Remorhazes": ("11", "7.200"),
    "Remorhaz Jovem": ("5", "1.800"),
    "Ressurgido": ("5", "1.800"),
    "Serpente de Fogo": ("1", "200"),
    "Unic\u00f3rnio": ("5", "1.800"),
    "Xorn": ("5", "1.800"),
    "Yuan -ti Abomina\u00e7\u00e3o": ("7", "2.900"),
    "Javali Gigante": ("2", "450"),
}


def norm(s: str) -> str:
    return (
        unicodedata.normalize("NFKD", s)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
        .strip()
    )


def order_key(t: dict) -> tuple:
    prov = t.get("prov", [{}])[0]
    page = int(prov.get("page_no", 1))
    bbox = prov.get("bbox", {})
    left = float(bbox.get("l", 0))
    top = float(bbox.get("t", 0))
    return (page, 0 if left < 300 else 1, -top)


def extract_nd(text: str) -> tuple[str, str] | None:
    m = re.search(
        r"N[i\u00ed]vel de Desafio\s+(\d+(?:/\d+)?)\s*\(?\s*([\d\s.,]*)\s*XP\)?",
        text, re.IGNORECASE,
    )
    if m:
        nd = m.group(1)
        xp = m.group(2).replace(" ", "").replace(",", ".").rstrip(".")
        if not xp:
            xp = ND_XP.get(nd, "")
        return nd, xp

    m = re.search(
        r"N[i\u00ed]vel de Desafio\s+(\d+(?:/\d+)?)\s*\(\s*(\d+)",
        text, re.IGNORECASE,
    )
    if m:
        nd = m.group(1)
        prefix = m.group(2)
        expected = ND_XP.get(nd, "")
        if expected.startswith(prefix):
            return nd, expected
        return nd, prefix

    return None


def load_all_chunks(docling_dir: Path = DOCLING_DIR) -> list[tuple[dict, int, list[dict]]]:
    result = []
    for rel_path, first in DOCLING_INPUTS:
        p = docling_dir / rel_path
        if not p.exists():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        ordered = sorted(data.get("texts", []), key=order_key)
        result.append((data, first, ordered))
    return result


def find_nd_in_docling(
    all_chunks: list[tuple[dict, int, list[dict]]],
    monster_name: str,
    pdf_page: int,
) -> tuple[str, str] | None:
    name_norm = norm(monster_name)

    for chunk_data, first, ordered in all_chunks:
        stem = ""
        for rel_path, f in DOCLING_INPUTS:
            if f == first:
                stem = Path(rel_path).stem
                break
        if stem:
            page_part = stem.split("_p")[-1]
            last = int(page_part.split("_")[-1])
        else:
            last = first + 100

        if not (first <= pdf_page <= last):
            continue

        header_idx = None
        for i, t in enumerate(ordered):
            if t.get("label") != "section_header":
                continue
            if norm(t.get("text", "")) == name_norm:
                pg = first + t["prov"][0]["page_no"] - 1
                if abs(pg - pdf_page) <= 3:
                    header_idx = i
                    break

        if header_idx is None:
            continue

        end_idx = len(ordered)
        for j in range(header_idx + 1, len(ordered)):
            t2 = ordered[j]
            if t2.get("label") == "section_header":
                txt2 = t2.get("text", "")
                if txt2 not in SKIP_HEADERS:
                    end_idx = j
                    break

        for k in range(header_idx, end_idx):
            txt = ordered[k].get("text", "")
            if "Desafio" in txt:
                result = extract_nd(txt)
                if result:
                    return result

        break

    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=REVIEWED_PATH if REVIEWED_PATH.exists() else MONSTROS_PATH)
    parser.add_argument("--output", type=Path, default=MONSTROS_PATH)
    parser.add_argument("--docling-dir", type=Path, default=DOCLING_DIR)
    args = parser.parse_args(argv)

    monstros = json.loads(args.input.read_text(encoding="utf-8"))
    null_nd = [m for m in monstros if m.get("nd") is None]
    print(f"Monstros com ND nulo: {len(null_nd)}")

    all_chunks = load_all_chunks(args.docling_dir)

    filled_docling = 0
    filled_ref = 0
    still_missing = []

    for m in null_nd:
        name = m["nome"]
        pdf_page = m.get("pagina_pdf", 0)

        result = find_nd_in_docling(all_chunks, name, pdf_page)
        if result:
            nd, xp = result
            m["nd"] = nd
            m["xp"] = xp
            filled_docling += 1
            print(f"  DOCLING: {name} -> ND {nd} ({xp} XP)")
            continue

        if name in REFERENCE:
            nd, xp = REFERENCE[name]
            m["nd"] = nd
            m["xp"] = xp
            filled_ref += 1
            print(f"  REF:     {name} -> ND {nd} ({xp} XP)")
            continue

        still_missing.append(name)
        print(f"  FALHOU:  {name} (p.{pdf_page})")

    print(f"\n--- Resultado ---")
    print(f"Docling:  {filled_docling}")
    print(f"Ref table: {filled_ref}")
    print(f"Total:    {filled_docling + filled_ref}/{len(null_nd)}")
    if still_missing:
        print(f"Faltando: {len(still_missing)}")
        for n in still_missing:
            print(f"  - {n}")

    args.output.write_text(
        json.dumps(monstros, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n{args.output.name} atualizado!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
