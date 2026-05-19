#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any


MM_SOURCE = "Manual dos Monstros"

ROOT = Path(__file__).resolve().parent
DEFAULT_DOCLING_DIR = ROOT / "docling_out"
RAW_OUTPUT = ROOT / "monstros_raw.json"

DOCLING_INPUTS = {
    "mm_monsters_a_b": ("mm_monsters_a_b/mm_monsters_a_b_p12_34.json", 12),
    "mm_monsters_c_e": ("mm_monsters_c_e/mm_monsters_c_e_p35_64.json", 35),
    "mm_monsters_d": ("mm_monsters_d/mm_monsters_d_p65_84.json", 65),
    "mm_monsters_dragon1": ("mm_monsters_dragon1/mm_monsters_dragon1_p85_105.json", 85),
    "mm_monsters_dragon2": ("mm_monsters_dragon2/mm_monsters_dragon2_p106_125.json", 106),
    "mm_monsters_e_h": ("mm_monsters_e_h/mm_monsters_e_h_p126_160.json", 126),
    "mm_monsters_h_m": ("mm_monsters_h_m/mm_monsters_h_m_p161_195.json", 161),
    "mm_monsters_m_p": ("mm_monsters_m_p/mm_monsters_m_p_p196_235.json", 196),
    "mm_monsters_p_s": ("mm_monsters_p_s/mm_monsters_p_s_p236_270.json", 236),
    "mm_monsters_s_z": ("mm_monsters_s_z/mm_monsters_s_z_p271_315.json", 271),
    "mm_appendix_a": ("mm_appendix_a/mm_appendix_a_p317_340.json", 317),
    "mm_appendix_b": ("mm_appendix_b/mm_appendix_b_p341_349.json", 341),
}

MONSTER_TYPES = (
    "Aberração",
    "Besta",
    "Celestial",
    "Constructo",
    "Construto",
    "Corruptor",
    "Dragão",
    "Elemental",
    "Fada",
    "Gigante",
    "Humanoide",
    "Limo",
    "Monstruosidade",
    "Morto-vivo",
    "Planta",
)

SIZES = ("Minúsculo", "Minúscula", "Pequeno", "Pequena", "Média", "Médio", "Grande", "Enorme", "Imenso", "Imensa")

ALIGNMENTS = (
    "leal e bom",
    "neutro e bom",
    "caótico e bom",
    "leal",
    "neutro",
    "caótico",
    "leal e mau",
    "neutro e mau",
    "caótico e mau",
    "imparcial",
    "qualquer alinhamento",
    "qualquer alinhamento mau",
    "qualquer alinhamento bom",
    "qualquer alinhamento caótico",
    "qualquer alinhamento leal",
    "qualquer alinhamento neutro",
    "neutro e mau" "qualquer",
)

STAT_ABBR = ("FOR", "DES", "CON", "INT", "SAB", "CAR")

SECTION_HEADERS = (
    "AÇÕES",
    "AÇÕES LENDÁRIAS",
    "AÇÕES DE COVIL",
    "EFEITOS REGIONAIS",
    "REAÇÕES",
)


def section_kind(text: str) -> str | None:
    if text in SECTION_HEADERS:
        return text
    if text.startswith("AÇÕES PARA"):
        return "AÇÕES"
    return None

def normalize_monster_type(text: str) -> str:
    text = re.sub(r"\s*-\s*", "-", text)
    return text

STAT_START_RE = re.compile(
    r"^(" + "|".join(re.escape(t) for t in MONSTER_TYPES) + r")\s+("
    + "|".join(re.escape(s) for s in SIZES)
    + r")\s*(?:\([^)]*\))?\s*,\s"
)

NAME_STAT_START_RE = re.compile(
    r"^(.+?)\s+("
    + "|".join(re.escape(t) for t in MONSTER_TYPES)
    + r")\s+("
    + "|".join(re.escape(s) for s in SIZES)
    + r")\s*(?:\([^)]*\))?\s*,\s*(.+)$"
)

STAT_IN_TABLE_RE = re.compile(
    r"(" + "|".join(re.escape(t) for t in MONSTER_TYPES) + r")\s+("
    + "|".join(re.escape(s) for s in SIZES)
    + r")\s*(?:\([^)]*\))?\s*,\s*",
    re.IGNORECASE,
)

STAT_SCORE_RE = re.compile(
    r"^(FOR|DES|CON|INT|SAB|CAR)\s+(\d+)\s*\(([+-]?\d+)\)"
)
STAT_SCORE_INLINE_RE = re.compile(
    r"\b(FOR|DES|CON|INT|SAB|CAR)\s+(\d+)\s*\(([+-]?\d+)\)"
)

ND_RE = re.compile(
    r"Nível de Desafio\s+(\d+(?:/\d+)?)\s*\(([\d.,]+)\s*XP\)",
    re.IGNORECASE,
)

CA_HP_SPEED_RE = re.compile(
    r"Classe de Armadura\s+(.+?)"
    r"\s*Pontos de Vida\s+(\d+)\s*\(([^)]+)\)"
    r"\s*Deslocamento\s+(.+?)(?=\s+FOR\b|\s+DES\b|\s+CON\b|\s+INT\b|\s+SAB\b|\s+CAR\b|\s+Testes\b|\s+Perícias\b|\s+Vulnerabilidade\b|\s+Resistência\b|\s+Imunidade\b|\s+Sentidos\b|\s+Idiomas\b|\s+Nível\b|$)",
    re.IGNORECASE,
)

CA_HP_RE = re.compile(
    r"Classe de Armadura\s+(.+?)"
    r"\s*Pontos de Vida\s+(\d+)\s*\(([^)]+)\)",
    re.IGNORECASE,
)

COMBINED_FIELDS_RE = re.compile(
    r"(?:Perícias\s+(.+?))?"
    r"\s*(?:Sentidos\s+(.+?))?"
    r"\s*(?:Idiomas\s+(.+?))?"
    r"\s*(?:Nível de Desafio\s+(\d+(?:/\d+)?)\s*\(([\d.,]+)\s*XP\))",
    re.IGNORECASE,
)

STAT_FIXUPS = {
    "arcanaloth": {
        "ca": "17 (armadura natural)",
        "pv": "104",
        "pv_dados": "16d8 + 32",
        "deslocamento": "9 m, voo 9 m",
    },
    "ultroloth": {
        "ca": "19 (armadura natural)",
        "pv": "153",
        "pv_dados": "18d8 + 72",
        "deslocamento": "9 m, voo 18 m",
    },
}


def clean(text: str | None) -> str | None:
    if text is None:
        return None
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    return None if text in {"", "-", "–"} else text


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def title_pt(text: str) -> str:
    small = {
        "a",
        "as",
        "com",
        "contra",
        "da",
        "de",
        "do",
        "das",
        "dos",
        "e",
        "em",
        "na",
        "no",
        "para",
        "por",
    }
    words = text.lower().split()
    titled = [
        word.capitalize() if idx == 0 or word not in small else word
        for idx, word in enumerate(words)
    ]
    return " ".join(titled)


def normalize_key(text: str | None) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_text = re.sub(r"\([^)]*\)", " ", ascii_text)
    ascii_text = re.sub(r"[^a-z0-9]+", " ", ascii_text)
    return re.sub(r"\s+", " ", ascii_text).strip()


def apply_stat_fixups(monster: dict[str, Any]) -> None:
    fixup = STAT_FIXUPS.get(normalize_key(monster.get("nome")))
    if not fixup:
        return
    for key, value in fixup.items():
        if not monster.get(key):
            monster[key] = value


def is_lore_candidate(text: str) -> bool:
    value = clean(text) or ""
    if not value or value.isdigit():
        return False
    if section_kind(value):
        return False
    if value in STAT_ABBR:
        return False
    if value.upper() == value and "." not in value and len(value) < 80:
        return False
    normalized = normalize_monster_type(value)
    if extract_type_size_alignment(normalized) or NAME_STAT_START_RE.match(normalized):
        return False
    if CA_HP_SPEED_RE.match(value) or CA_HP_RE.match(value):
        return False
    if STAT_SCORE_RE.match(value) or STAT_SCORE_INLINE_RE.fullmatch(value):
        return False
    if re.search(r"\bFOR\b.*\bDES\b.*\bCON\b", value):
        return False
    if re.match(
        r"^(Testes de Resistência|Perícias|Vulnerabilidade a Dano|Resistência a Dano|Imunidade a Dano|Imunidade a Condição|Sentidos|Idiomas|Nível de Desafio)\b",
        value,
        re.IGNORECASE,
    ):
        return False
    return True


def clean_lore_text(text: str) -> str | None:
    value = clean(text) or ""
    value = re.split(r"\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9 '\-–]{3,}\s+FOR\s+DES\s+CON\b", value, maxsplit=1)[0]
    value = re.split(r"\s+FOR\s+DES\s+CON\b", value, maxsplit=1)[0]
    value = re.split(r"\s+Classe de Armadura\b", value, maxsplit=1)[0]
    value = clean(value) or ""
    return value if is_lore_candidate(value) else None


ACTION_START_RE = re.compile(
    r"^(?:"
    r"Ataques Múltiplos|Mordida|Garras?|Garra|Picareta|Azagaia|Invisibilidade|"
    r"Aumentar|Espada|Arco|Cauda|Teletransporte|Constrição|Sopro|Presença|"
    r"Arma de Sopro|Maça|Lança|Tridente|Machado|Bicada|Casco|Punho|Raio|"
    r"Toque|Engolir|Detectar|Movimento|Ataque|Forma|Metamorfo|"
    r"[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^.!?]{1,80}\s*\([^)]*\)"
    r")\.",
    re.IGNORECASE,
)


def looks_like_action_text(text: str) -> bool:
    value = clean(text) or ""
    if not value:
        return False
    if ACTION_START_RE.match(value):
        return True
    return "Ataque Corpo-a-Corpo" in value or "Ataque à Distância" in value


def looks_like_action_continuation(text: str) -> bool:
    value = clean(text) or ""
    return bool(
        re.match(
            r"^(?:Se|Quando|Enquanto|Na nova forma|Em uma nova forma|O alvo|A criatura|Toda vez|No início|No final|Caso|Após|Antes|Depois|Uma criatura|Cada criatura)\b",
            value,
        )
        or re.match(r"^\d+[\-–]", value)
    )


def looks_like_language_continuation(text: str) -> bool:
    value = clean(text) or ""
    return bool(re.match(r"^mas não pode falar\b", value, re.IGNORECASE))


def page_ref(pdf_page: int, printed_page: int | None = None) -> str:
    printed = printed_page if printed_page is not None else pdf_page
    return f"{printed} (PDF: {pdf_page})"


def load_docling(
    docling_dir: Path, key: str
) -> tuple[dict[str, Any], int]:
    rel_path, first_pdf_page = DOCLING_INPUTS[key]
    path = docling_dir / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Docling JSON ausente: {path}")
    return json.loads(path.read_text(encoding="utf-8")), first_pdf_page


def printed_pages(data: dict[str, Any], first_pdf_page: int) -> dict[int, int]:
    pages: dict[int, int] = {}
    for text in data.get("texts", []):
        if text.get("label") != "page_footer":
            continue
        value = clean(text.get("text")) or ""
        if not value.isdigit():
            continue
        rel_page = int(text.get("prov", [{}])[0].get("page_no", 0))
        pages[rel_page] = int(value)
    for rel_page in range(1, len(data.get("pages", {})) + 1):
        pages.setdefault(rel_page, first_pdf_page + rel_page - 1)
    return pages


def text_order_key(text: dict[str, Any]) -> tuple[int, int, float]:
    prov = text.get("prov", [{}])[0]
    page = int(prov.get("page_no", 1))
    bbox = prov.get("bbox", {})
    left = float(bbox.get("l", 0))
    top = float(bbox.get("t", 0))
    column = 0 if left < 300 else 1
    return (page, column, -top)


def ordered_texts(data: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(data.get("texts", []), key=text_order_key)


def table_page(table: dict[str, Any], first_pdf_page: int) -> tuple[int, int]:
    rel_page = int(table.get("prov", [{}])[0].get("page_no", 1))
    return rel_page, first_pdf_page + rel_page - 1


def table_column(table: dict[str, Any]) -> int:
    bbox = table.get("prov", [{}])[0].get("bbox", {})
    return 0 if float(bbox.get("l", 0)) < 300 else 1


def table_text_start_index(texts: list[dict[str, Any]], table: dict[str, Any]) -> int | None:
    prov = table.get("prov", [{}])[0]
    rel_page = int(prov.get("page_no", 1))
    bbox = prov.get("bbox", {})
    column = table_column(table)
    bottom = float(bbox.get("b", 0))

    for index, text in enumerate(texts):
        text_prov = text.get("prov", [{}])[0]
        if int(text_prov.get("page_no", 1)) != rel_page:
            continue
        text_bbox = text_prov.get("bbox", {})
        text_column = 0 if float(text_bbox.get("l", 0)) < 300 else 1
        if text_column != column:
            continue
        if float(text_bbox.get("t", 0)) < bottom:
            return index
    return None


def lore_prefix_parts(
    texts: list[dict[str, Any]], start_index: int, monster_name: str
) -> list[str]:
    target = normalize_key(monster_name)
    if not target:
        return []

    start_page = int(texts[start_index].get("prov", [{}])[0].get("page_no", 0))
    for index in range(start_index - 1, max(-1, start_index - 140), -1):
        text = texts[index]
        value = clean(text.get("text")) or ""
        if text.get("label") != "section_header":
            continue
        page = int(text.get("prov", [{}])[0].get("page_no", 0))
        if start_page and page and abs(start_page - page) > 2:
            break
        if section_kind(value):
            continue
        if normalize_key(value) == target:
            if index + 1 == start_index:
                continue
            parts: list[str] = []
            for lore_index in range(index + 1, start_index):
                entry = texts[lore_index]
                if entry.get("label") in {"section_header", "caption"}:
                    break
                if entry.get("label") == "page_footer":
                    continue
                lore = clean_lore_text(clean(entry.get("text")) or "")
                if lore:
                    parts.append(lore)
            if parts:
                return parts
    return []


def parse_ability_from_table(cells: list[dict]) -> dict[str, dict]:
    abilities: dict[str, dict] = {}
    for cell in cells:
        text = clean(cell.get("text", "")) or ""
        for m_inline in STAT_SCORE_INLINE_RE.finditer(text):
            abilities[m_inline.group(1)] = {
                "valor": int(m_inline.group(2)),
                "mod": m_inline.group(3),
            }
        m = STAT_SCORE_RE.match(text)
        if m:
            abilities[m.group(1)] = {
                "valor": int(m.group(2)),
                "mod": m.group(3),
            }
    if len(abilities) == 6:
        return abilities

    rows: dict[int, dict[int, str]] = {}
    for cell in cells:
        r = cell.get("start_row_offset_idx", 0)
        c = cell.get("start_col_offset_idx", 0)
        rows.setdefault(r, {})[c] = text = clean(cell.get("text", "")) or ""

    for r, cols in rows.items():
        for c, text in cols.items():
            if text in STAT_ABBR and (r + 1) in rows and c in rows[r + 1]:
                val_text = rows[r + 1][c]
                m_val = re.match(r"([+-]?\d+)\s*\(([+-]?\d+)\)", val_text)
                if m_val:
                    abilities[text] = {
                        "valor": int(m_val.group(1)),
                        "mod": m_val.group(2),
                    }
    return abilities


def parse_ability_from_texts(texts: list[dict[str, Any]]) -> dict[str, dict]:
    abilities: dict[str, dict] = {}
    values = [clean(text_entry.get("text")) or "" for text_entry in texts]

    for index in range(0, max(0, len(values) - 11)):
        headers = values[index : index + 6]
        scores = values[index + 6 : index + 12]
        if all(header in STAT_ABBR for header in headers) and all(
            re.match(r"\d+\s*\([+-]?\d+\)", score) for score in scores
        ):
            for header, score in zip(headers, scores):
                m_val = re.match(r"(\d+)\s*\(([+-]?\d+)\)", score)
                if m_val:
                    abilities[header] = {
                        "valor": int(m_val.group(1)),
                        "mod": m_val.group(2),
                    }
            if len(abilities) == 6:
                return abilities

    pending: str | None = None

    for value in values:
        if value in STAT_ABBR:
            pending = value
            continue
        if pending:
            m_val = re.match(r"(\d+)\s*\(([+-]?\d+)\)", value)
            if m_val:
                abilities[pending] = {
                    "valor": int(m_val.group(1)),
                    "mod": m_val.group(2),
                }
                pending = None

    return abilities


def extract_type_size_alignment(text: str) -> tuple[str, str, str] | None:
    normalized = normalize_monster_type(text)
    m = STAT_START_RE.match(normalized)
    if not m:
        return None
    tipo = m.group(1)
    tamanho = m.group(2)
    rest = normalized[m.end() :]
    alignment = rest.strip().rstrip(",")
    return tipo, tamanho, alignment


def extract_ca(text: str) -> str | None:
    m = re.match(r"Classe de Armadura\s+(.+?)(?:\s*Pontos de Vida|$)", text, re.IGNORECASE)
    if m:
        return clean(m.group(1))
    return None


def extract_hp(text: str) -> tuple[str | None, str | None]:
    m = re.match(r"Pontos de Vida\s+(\d+)\s*\(([^)]+)\)", text, re.IGNORECASE)
    if m:
        return clean(m.group(1)), clean(m.group(2))
    return None, None


def extract_speed(text: str) -> str | None:
    m = re.match(r"Deslocamento\s+(.+)", text, re.IGNORECASE)
    if m:
        return clean(m.group(1))
    return None


def extract_nd(text: str) -> tuple[str | None, str | None] | None:
    m = ND_RE.search(text)
    if m:
        return clean(m.group(1)), clean(m.group(2))
    return None


def parse_stat_block_from_table(table: dict[str, Any]) -> dict[str, Any] | None:
    cells = table.get("data", {}).get("table_cells", [])
    if not cells:
        return None

    first_cell_text = normalize_monster_type(clean(cells[0].get("text", "")) or "")
    m_name_type = re.match(
        r"^(.+?)\s+("
        + "|".join(re.escape(t) for t in MONSTER_TYPES)
        + r")\s+("
        + "|".join(re.escape(s) for s in SIZES)
        + r")\s*(?:\([^)]*\))?\s*,\s*(.+)$",
        first_cell_text,
    )
    if not m_name_type:
        return None

    name = clean(m_name_type.group(1))
    tipo = m_name_type.group(2)
    tamanho = m_name_type.group(3)
    alignment = clean(m_name_type.group(4))

    ca = None
    hp_val = None
    hp_dice = None
    speed = None

    for cell in cells:
        text = clean(cell.get("text", "")) or ""
        if not ca or not hp_val or not speed:
            m_chs = CA_HP_SPEED_RE.match(text)
            if m_chs:
                if not ca:
                    ca = clean(m_chs.group(1))
                if not hp_val:
                    hp_val = clean(m_chs.group(2))
                    hp_dice = clean(m_chs.group(3))
                if not speed:
                    speed = clean(m_chs.group(4))
                continue
            m_ch = CA_HP_RE.match(text)
            if m_ch:
                if not ca:
                    ca = clean(m_ch.group(1))
                if not hp_val:
                    hp_val = clean(m_ch.group(2))
                    hp_dice = clean(m_ch.group(3))
                continue
        if not ca:
            ca = extract_ca(text)
        if not hp_val:
            m_hp = re.search(r"Pontos de Vida\s+(\d+)\s*\(([^)]+)\)", text, re.IGNORECASE)
            if m_hp:
                hp_val = clean(m_hp.group(1))
                hp_dice = clean(m_hp.group(2))
        if not speed:
            m_spd = re.search(r"Deslocamento\s+(.+)", text, re.IGNORECASE)
            if m_spd:
                speed = clean(m_spd.group(1))

    abilities = parse_ability_from_table(cells)

    pericias = None
    testes_resistencia = None
    resistencia_dano = None
    imunidade_dano = None
    imunidade_condicao = None
    sentidos = None
    idiomas = None
    nd = None
    xp = None

    for cell in cells:
        text = clean(cell.get("text", "")) or ""
        if not text:
            continue
        m_combined = COMBINED_FIELDS_RE.search(text)
        if m_combined:
            if m_combined.group(1):
                pericias = clean(m_combined.group(1))
            if m_combined.group(2):
                sentidos = clean(m_combined.group(2))
            if m_combined.group(3):
                idiomas = clean(m_combined.group(3))
            nd = clean(m_combined.group(4))
            xp = clean(m_combined.group(5))
        if not nd:
            nd_result = extract_nd(text)
            if nd_result:
                nd = nd_result[0]
                xp = nd_result[1]
        if not testes_resistencia and re.match(r"Testes de Resistência\s+", text, re.IGNORECASE):
            testes_resistencia = re.sub(r"^Testes de Resistência\s+", "", text, flags=re.IGNORECASE)
        if not pericias and re.match(r"Perícias\s+", text, re.IGNORECASE):
            pericias = re.sub(r"^Perícias\s+", "", text, flags=re.IGNORECASE)
        if not resistencia_dano and re.match(r"Resistência a Dano\s+", text, re.IGNORECASE):
            resistencia_dano = re.sub(r"^Resistência a Dano\s+", "", text, flags=re.IGNORECASE)
        if not imunidade_dano and re.match(r"Imunidade a Dano\s+", text, re.IGNORECASE):
            imunidade_dano = re.sub(r"^Imunidade a Dano\s+", "", text, flags=re.IGNORECASE)
        if not imunidade_condicao and re.match(r"Imunidade a Condição\s+", text, re.IGNORECASE):
            imunidade_condicao = re.sub(r"^Imunidade a Condição\s+", "", text, flags=re.IGNORECASE)
        if not sentidos and re.match(r"Sentidos\s+", text, re.IGNORECASE):
            sentidos = re.sub(r"^Sentidos\s+", "", text, flags=re.IGNORECASE)
        if not idiomas and re.match(r"Idiomas\s+", text, re.IGNORECASE):
            idiomas = re.sub(r"^Idiomas\s+", "", text, flags=re.IGNORECASE)

    return {
        "nome": name,
        "tipo_criatura": tipo,
        "tamanho": tamanho,
        "alinhamento": alignment,
        "ca": ca,
        "pv": hp_val,
        "pv_dados": hp_dice,
        "deslocamento": speed,
        "habilidades": abilities,
        "testes_resistencia": testes_resistencia,
        "pericias": pericias,
        "resistencia_dano": resistencia_dano,
        "imunidade_dano": imunidade_dano,
        "imunidade_condicao": imunidade_condicao,
        "sentidos": sentidos,
        "idiomas": idiomas,
        "nd": nd,
        "xp": xp,
    }


def split_inline_actions(text: str) -> list[str]:
    text = clean(text) or ""
    if not text:
        return []
    parts = re.split(
        r"(?=\b(?:Ataques Múltiplos|Mordida|Garras|Lança|Cauda|Espada|Tridente|Teletransporte|Constrição)\.)",
        text,
    )
    return [part.strip() for part in parts if part.strip()]


def monster_from_table_only(
    stat_info: dict[str, Any],
    table: dict[str, Any],
    first_pdf_page: int,
    printed_by_rel: dict[int, int],
) -> dict[str, Any] | None:
    rel_page, pdf_page = table_page(table, first_pdf_page)
    printed = printed_by_rel.get(rel_page, pdf_page)
    name = title_pt(stat_info["nome"])
    monster: dict[str, Any] = {
        "id": slugify(f"{MM_SOURCE}-{name}"),
        "nome": name,
        "tipo_criatura": stat_info["tipo_criatura"],
        "tamanho": stat_info["tamanho"],
        "alinhamento": stat_info["alinhamento"],
        "ca": stat_info.get("ca"),
        "pv": stat_info.get("pv"),
        "pv_dados": stat_info.get("pv_dados"),
        "deslocamento": stat_info.get("deslocamento"),
        "habilidades": stat_info.get("habilidades", {}),
        "testes_resistencia": stat_info.get("testes_resistencia"),
        "pericias": stat_info.get("pericias"),
        "resistencia_dano": stat_info.get("resistencia_dano"),
        "imunidade_dano": stat_info.get("imunidade_dano"),
        "imunidade_condicao": stat_info.get("imunidade_condicao"),
        "sentidos": stat_info.get("sentidos"),
        "idiomas": stat_info.get("idiomas"),
        "nd": stat_info.get("nd"),
        "xp": stat_info.get("xp"),
        "fonte": MM_SOURCE,
        "pagina_livro": printed,
        "pagina_pdf": pdf_page,
        "referencia": page_ref(pdf_page, printed),
        "descricao": "",
        "habilidades_especiais": [],
        "acoes": [],
        "acoes_lendarias": [],
        "acoes_covil": [],
        "efeitos_regionais": [],
        "reacoes": [],
        "descricao_blocos": [],
    }
    apply_stat_fixups(monster)

    first = True
    for cell in table.get("data", {}).get("table_cells", []):
        text = clean(cell.get("text", "")) or ""
        if not text:
            continue
        if first:
            first = False
            continue
        if text in STAT_ABBR or STAT_SCORE_INLINE_RE.fullmatch(text):
            continue
        if CA_HP_SPEED_RE.match(text) or CA_HP_RE.match(text):
            continue

        if " AÇÕES " in f" {text} ":
            before, after = re.split(r"\bAÇÕES\b", text, maxsplit=1)
            before = clean(before)
            if before:
                monster["habilidades_especiais"].append(before)
            monster["acoes"].extend(split_inline_actions(after))
            continue

        if text.startswith(("Sentidos ", "Idiomas ", "Nível de Desafio", "Testes de Resistência", "Perícias ")):
            continue
        if text.startswith(("Resistência a Dano", "Imunidade a Dano", "Imunidade a Condição", "Vulnerabilidade a Dano")):
            continue
        monster["habilidades_especiais"].append(text)

    if monster["habilidades_especiais"]:
        monster["descricao_blocos"].extend(
            {"type": "paragraph", "text": h} for h in monster["habilidades_especiais"]
        )
    if monster["acoes"]:
        monster["descricao_blocos"].append({"type": "paragraph", "text": "AÇÕES"})
        monster["descricao_blocos"].extend(
            {"type": "paragraph", "text": a} for a in monster["acoes"]
        )

    if not monster["ca"] or not monster["pv"]:
        return None
    return monster


def build_table_page_map(
    data: dict[str, Any], first_pdf_page: int
) -> dict[int, list[dict[str, Any]]]:
    page_tables: dict[int, list[dict[str, Any]]] = {}
    for table in data.get("tables", []):
        rel_page, pdf_page = table_page(table, first_pdf_page)
        stat_info = parse_stat_block_from_table(table)
        if stat_info:
            page_tables.setdefault(rel_page, []).append(
                {"pdf_page": pdf_page, "stat": stat_info, "table": table}
            )
        else:
            abilities = parse_ability_from_table(
                table.get("data", {}).get("table_cells", [])
            )
            if abilities:
                page_tables.setdefault(rel_page, []).append(
                    {
                        "pdf_page": pdf_page,
                        "abilities_only": abilities,
                        "table": table,
                    }
                )
    return page_tables


def parse_monsters_from_chunk(
    data: dict[str, Any],
    key: str,
    first_pdf_page: int,
    printed_by_rel: dict[int, int],
) -> list[dict[str, Any]]:
    texts = ordered_texts(data)
    page_tables = build_table_page_map(data, first_pdf_page)

    stat_starts: dict[int, dict[str, Any]] = {}
    table_only_monsters: list[dict[str, Any]] = []
    for index, text in enumerate(texts):
        label = text.get("label")
        value = clean(text.get("text")) or ""
        if not value:
            continue

        named_stat = NAME_STAT_START_RE.match(normalize_monster_type(value))
        if named_stat:
            rel_page = int(text.get("prov", [{}])[0].get("page_no", 1))
            stat_starts[index] = {
                "name": clean(named_stat.group(1)) or "",
                "tipo": named_stat.group(2),
                "tamanho": named_stat.group(3),
                "alinhamento": clean(named_stat.group(4)),
                "rel_page": rel_page,
                "source": "text",
            }
            continue

        tipo_tam_ali = extract_type_size_alignment(value)
        if tipo_tam_ali:
            name = ""
            for j in range(index - 1, max(0, index - 8), -1):
                if texts[j].get("label") == "section_header":
                    n = clean(texts[j].get("text")) or ""
                    if n and not n.startswith("AÇ") and not n.startswith("RE") and not n.startswith("EFEITO") and not n.startswith("INV") and not n.startswith("O COV") and not n.startswith("PERSON"):
                        name = n
                        break
            if not name:
                for j in range(index - 1, max(0, index - 8), -1):
                    t = clean(texts[j].get("text")) or ""
                    l = texts[j].get("label", "")
                    if t and t in value:
                        continue
                    if l == "section_header":
                        continue
                    if len(t) > 3 and len(t) < 60 and not t[0].isdigit():
                        name = t
                        break
            rel_page = int(text.get("prov", [{}])[0].get("page_no", 1))
            stat_starts[index] = {
                "name": name,
                "tipo": tipo_tam_ali[0],
                "tamanho": tipo_tam_ali[1],
                "alinhamento": tipo_tam_ali[2],
                "rel_page": rel_page,
                "source": "text",
            }

    for rel_page, entries in page_tables.items():
        for entry in entries:
            if "stat" in entry:
                stat_info = entry["stat"]
                table_start_index = table_text_start_index(texts, entry["table"])
                matching_header: tuple[int, str] | None = None
                for index, text in enumerate(texts):
                    if text.get("label") != "section_header":
                        continue
                    page = int(text.get("prov", [{}])[0].get("page_no", 0))
                    if page != rel_page:
                        continue
                    t = clean(text.get("text")) or ""
                    if (
                        t
                        and normalize_key(t).startswith(
                            normalize_key(stat_info["nome"])
                        )
                    ):
                        if matching_header is None:
                            matching_header = (index, t)
                        elif table_start_index is not None and abs(
                            index - table_start_index
                        ) < abs(matching_header[0] - table_start_index):
                            matching_header = (index, t)
                if matching_header and (
                    table_start_index is None or matching_header[0] <= table_start_index
                ):
                    start_index = matching_header[0]
                    name = matching_header[1]
                elif table_start_index is not None:
                    start_index = table_start_index
                    name = stat_info["nome"]
                else:
                    table_monster = monster_from_table_only(
                        stat_info,
                        entry["table"],
                        first_pdf_page,
                        printed_by_rel,
                    )
                    if table_monster:
                        table_only_monsters.append(table_monster)
                    continue

                stat_starts[start_index] = {
                    "name": name,
                    "tipo": stat_info["tipo_criatura"],
                    "tamanho": stat_info["tamanho"],
                    "alinhamento": stat_info["alinhamento"],
                    "rel_page": rel_page,
                    "source": "table",
                    "table_stat": stat_info,
                }

    sorted_starts = sorted(stat_starts.items())

    monsters: list[dict[str, Any]] = []
    for si, (start_index, start_info) in enumerate(sorted_starts):
        end_index = sorted_starts[si + 1][0] if si + 1 < len(sorted_starts) else len(texts)

        rel_page = start_info["rel_page"]
        pdf_page = first_pdf_page + rel_page - 1
        printed = printed_by_rel.get(rel_page, pdf_page)

        monster: dict[str, Any] = {
            "id": slugify(f"{MM_SOURCE}-{start_info['name']}"),
            "nome": title_pt(start_info["name"]),
            "tipo_criatura": start_info["tipo"],
            "tamanho": start_info["tamanho"],
            "alinhamento": start_info["alinhamento"],
            "ca": None,
            "pv": None,
            "pv_dados": None,
            "deslocamento": None,
            "habilidades": {},
            "testes_resistencia": None,
            "pericias": None,
            "resistencia_dano": None,
            "imunidade_dano": None,
            "imunidade_condicao": None,
            "sentidos": None,
            "idiomas": None,
            "nd": None,
            "xp": None,
            "fonte": MM_SOURCE,
            "pagina_livro": printed,
            "pagina_pdf": pdf_page,
            "referencia": page_ref(pdf_page, printed),
            "descricao": "",
            "habilidades_especiais": [],
            "acoes": [],
            "acoes_lendarias": [],
            "acoes_covil": [],
            "efeitos_regionais": [],
            "reacoes": [],
            "descricao_blocos": [],
        }

        if "table_stat" in start_info:
            ts = start_info["table_stat"]
            monster["ca"] = ts.get("ca")
            monster["pv"] = ts.get("pv")
            monster["pv_dados"] = ts.get("pv_dados")
            monster["deslocamento"] = ts.get("deslocamento")
            monster["habilidades"] = ts.get("habilidades", {})
            if ts.get("nd"):
                monster["nd"] = ts["nd"]
                monster["xp"] = ts.get("xp")
            if ts.get("testes_resistencia"):
                monster["testes_resistencia"] = ts["testes_resistencia"]
            if ts.get("pericias"):
                monster["pericias"] = ts["pericias"]
            if ts.get("resistencia_dano"):
                monster["resistencia_dano"] = ts["resistencia_dano"]
            if ts.get("imunidade_dano"):
                monster["imunidade_dano"] = ts["imunidade_dano"]
            if ts.get("imunidade_condicao"):
                monster["imunidade_condicao"] = ts["imunidade_condicao"]
            if ts.get("sentidos"):
                monster["sentidos"] = ts["sentidos"]
            if ts.get("idiomas"):
                monster["idiomas"] = ts["idiomas"]
            apply_stat_fixups(monster)

        current_section = "stats"
        lore_parts: list[str] = []
        desc_blocks: list[dict[str, Any]] = []

        lore_parts.extend(lore_prefix_parts(texts, start_index, start_info["name"]))

        for index in range(start_index, end_index):
            text_entry = texts[index]
            label = text_entry.get("label")
            value = clean(text_entry.get("text")) or ""
            if not value:
                continue
            if label == "page_footer":
                continue
            if value.isdigit() and len(value) <= 3:
                continue

            kind = section_kind(value)
            if kind:
                current_section = kind
                continue

            if label == "section_header":
                if index > start_index:
                    break
                continue

            if current_section == "stats":
                if extract_type_size_alignment(value) or NAME_STAT_START_RE.match(normalize_monster_type(value)):
                    continue

                if monster["idiomas"] and looks_like_language_continuation(value):
                    monster["idiomas"] = clean(f"{monster['idiomas']} {value}")
                    continue

                if not monster["ca"] or not monster["pv"] or not monster["deslocamento"]:
                    m_chs = CA_HP_SPEED_RE.match(value)
                    if m_chs:
                        if not monster["ca"]:
                            monster["ca"] = clean(m_chs.group(1))
                        if not monster["pv"]:
                            monster["pv"] = clean(m_chs.group(2))
                            monster["pv_dados"] = clean(m_chs.group(3))
                        if not monster["deslocamento"]:
                            monster["deslocamento"] = clean(m_chs.group(4))
                        continue

                if (not monster["ca"] or not monster["pv"]) and not monster["deslocamento"]:
                    m_ch = CA_HP_RE.match(value)
                    if m_ch:
                        if not monster["ca"]:
                            monster["ca"] = clean(m_ch.group(1))
                        if not monster["pv"]:
                            monster["pv"] = clean(m_ch.group(2))
                            monster["pv_dados"] = clean(m_ch.group(3))
                        continue

                if not monster["ca"]:
                    ca = extract_ca(value)
                    if ca:
                        monster["ca"] = ca
                        continue

                if not monster["pv"]:
                    hp_val, hp_dice = extract_hp(value)
                    if hp_val:
                        monster["pv"] = hp_val
                        monster["pv_dados"] = hp_dice
                        continue

                if not monster["deslocamento"]:
                    speed = extract_speed(value)
                    if speed:
                        monster["deslocamento"] = speed
                        continue

                m_score = STAT_SCORE_RE.match(value)
                if m_score:
                    monster["habilidades"][m_score.group(1)] = {
                        "valor": int(m_score.group(2)),
                        "mod": m_score.group(3),
                    }
                    continue

                m_combined = COMBINED_FIELDS_RE.search(value)
                if m_combined and not monster["nd"]:
                    if m_combined.group(1) and not monster["pericias"]:
                        monster["pericias"] = clean(m_combined.group(1))
                    if m_combined.group(2) and not monster["sentidos"]:
                        monster["sentidos"] = clean(m_combined.group(2))
                    if m_combined.group(3) and not monster["idiomas"]:
                        monster["idiomas"] = clean(m_combined.group(3))
                    monster["nd"] = clean(m_combined.group(4))
                    monster["xp"] = clean(m_combined.group(5))
                    current_section = "traits"
                    continue

                if not monster["testes_resistencia"] and re.match(
                    r"Testes de Resistência\s+", value, re.IGNORECASE
                ):
                    monster["testes_resistencia"] = re.sub(
                        r"^Testes de Resistência\s+", "", value, flags=re.IGNORECASE
                    )
                    continue

                if not monster["pericias"] and re.match(r"Perícias\s+", value, re.IGNORECASE):
                    monster["pericias"] = re.sub(
                        r"^Perícias\s+", "", value, flags=re.IGNORECASE
                    )
                    continue

                if not monster["resistencia_dano"] and re.match(
                    r"Resistência a Dano\s+", value, re.IGNORECASE
                ):
                    monster["resistencia_dano"] = re.sub(
                        r"^Resistência a Dano\s+", "", value, flags=re.IGNORECASE
                    )
                    continue

                if not monster["imunidade_dano"] and re.match(
                    r"Imunidade a Dano\s+", value, re.IGNORECASE
                ):
                    monster["imunidade_dano"] = re.sub(
                        r"^Imunidade a Dano\s+", "", value, flags=re.IGNORECASE
                    )
                    continue

                if not monster["imunidade_condicao"] and re.match(
                    r"Imunidade a Condição\s+", value, re.IGNORECASE
                ):
                    monster["imunidade_condicao"] = re.sub(
                        r"^Imunidade a Condição\s+",
                        "",
                        value,
                        flags=re.IGNORECASE,
                    )
                    continue

                if not monster["sentidos"] and re.match(r"Sentidos\s+", value, re.IGNORECASE):
                    monster["sentidos"] = re.sub(
                        r"^Sentidos\s+", "", value, flags=re.IGNORECASE
                    )
                    continue

                if not monster["idiomas"] and re.match(r"Idiomas\s+", value, re.IGNORECASE):
                    monster["idiomas"] = re.sub(
                        r"^Idiomas\s+", "", value, flags=re.IGNORECASE
                    )
                    continue

                nd_result = extract_nd(value)
                if nd_result:
                    monster["nd"] = nd_result[0]
                    monster["xp"] = nd_result[1]
                    current_section = "traits"
                    continue

                if monster["nd"]:
                    monster["habilidades_especiais"].append(value)
                else:
                    lore = clean_lore_text(value)
                    if lore:
                        lore_parts.append(lore)

            elif current_section == "traits":
                if monster["idiomas"] and looks_like_language_continuation(value):
                    monster["idiomas"] = clean(f"{monster['idiomas']} {value}")
                    continue

                monster["habilidades_especiais"].append(value)

            elif current_section == "AÇÕES":
                if looks_like_action_text(value):
                    monster["acoes"].append(value)
                elif monster["acoes"] and looks_like_action_continuation(value):
                    monster["acoes"][-1] = clean(monster["acoes"][-1] + " " + value)
                else:
                    lore = clean_lore_text(value)
                    if lore:
                        lore_parts.append(lore)

            elif current_section == "AÇÕES LENDÁRIAS":
                monster["acoes_lendarias"].append(value)

            elif current_section == "AÇÕES DE COVIL":
                monster["acoes_covil"].append(value)

            elif current_section == "EFEITOS REGIONAIS":
                monster["efeitos_regionais"].append(value)

            elif current_section == "REAÇÕES":
                monster["reacoes"].append(value)

        if len(monster["habilidades"]) < 6:
            text_abilities = parse_ability_from_texts(texts[start_index:end_index])
            if len(text_abilities) > len(monster["habilidades"]):
                monster["habilidades"] = text_abilities

        if len(monster["habilidades"]) < 6:
            best_abilities: dict[str, dict] = {}
            for rel_pg, entries in page_tables.items():
                if rel_pg != rel_page:
                    continue
                for entry in entries:
                    if "abilities_only" in entry:
                        abs_data = entry["abilities_only"]
                        if len(abs_data) > len(best_abilities):
                            best_abilities = abs_data
                    if "stat" in entry:
                        ts = entry["stat"]
                        if normalize_key(ts.get("nome")) != normalize_key(monster["nome"]):
                            continue
                        abs_data = ts.get("habilidades", {})
                        if len(abs_data) > len(best_abilities):
                            best_abilities = abs_data
            if len(best_abilities) > len(monster["habilidades"]):
                monster["habilidades"] = best_abilities

        monster["descricao"] = clean(" ".join(lore_parts)) or ""
        if monster["habilidades_especiais"]:
            desc_blocks.extend(
                {"type": "paragraph", "text": h}
                for h in monster["habilidades_especiais"]
            )
        if monster["acoes"]:
            desc_blocks.append({"type": "paragraph", "text": "AÇÕES"})
            desc_blocks.extend(
                {"type": "paragraph", "text": a} for a in monster["acoes"]
            )
        if monster["acoes_lendarias"]:
            desc_blocks.append({"type": "paragraph", "text": "AÇÕES LENDÁRIAS"})
            desc_blocks.extend(
                {"type": "paragraph", "text": a} for a in monster["acoes_lendarias"]
            )
        if monster["reacoes"]:
            desc_blocks.append({"type": "paragraph", "text": "REAÇÕES"})
            desc_blocks.extend(
                {"type": "paragraph", "text": r} for r in monster["reacoes"]
            )
        monster["descricao_blocos"] = desc_blocks

        if not monster["ca"] or not monster["pv"]:
            continue

        if not monster["nd"] and len(monster["habilidades"]) < 6:
            continue

        monsters.append(monster)

    monsters.extend(table_only_monsters)
    return monsters


def monster_completeness_score(monster: dict[str, Any]) -> int:
    score = 0
    score += 10 if monster.get("ca") else 0
    score += 10 if monster.get("pv") else 0
    score += 10 if monster.get("nd") else 0
    score += len(monster.get("habilidades", {}))
    score += len(monster.get("habilidades_especiais", []))
    score += len(monster.get("acoes", [])) * 2
    score += len(monster.get("acoes_lendarias", [])) * 2
    score += len(monster.get("reacoes", [])) * 2
    score += 1 if monster.get("descricao") else 0
    return score


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docling-dir", type=Path, default=DEFAULT_DOCLING_DIR)
    parser.add_argument("--output", type=Path, default=RAW_OUTPUT)
    args = parser.parse_args()

    all_monsters: list[dict[str, Any]] = []
    for key in DOCLING_INPUTS:
        print(f"Processando: {key}...")
        data, first_pdf_page = load_docling(args.docling_dir, key)
        printed_by_rel = printed_pages(data, first_pdf_page)
        monsters = parse_monsters_from_chunk(
            data, key, first_pdf_page, printed_by_rel
        )
        print(f"  -> {len(monsters)} monstros")
        all_monsters.extend(monsters)

    unique: list[dict[str, Any]] = []
    seen_by_id: dict[str, int] = {}
    for m in all_monsters:
        if m["id"] not in seen_by_id:
            seen_by_id[m["id"]] = len(unique)
            unique.append(m)
            continue

        existing_index = seen_by_id[m["id"]]
        if monster_completeness_score(m) > monster_completeness_score(
            unique[existing_index]
        ):
            unique[existing_index] = m

    args.output.write_text(
        json.dumps(unique, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nTotal: {len(unique)} monstros em {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
