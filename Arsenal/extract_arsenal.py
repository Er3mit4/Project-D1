#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


PHB_SOURCE = "Livro do Jogador"
DMG_SOURCE = "Guia do Mestre"
XGE_SOURCE = "Guia de Xanathar para Todas as Coisas"

ROOT = Path(__file__).resolve().parent
DEFAULT_DOCLING_DIR = ROOT / "docling_out"

DOCLING_INPUTS = {
    "phb_equipment": ("phb_equipment/phb_equipment_p145_161.json", 145, PHB_SOURCE),
    "dmg_magic_az": ("dmg_magic_az/dmg_magic_az_p151_220.json", 151, DMG_SOURCE),
    "dmg_artifacts": ("dmg_artifacts/dmg_artifacts_p221_229.json", 221, DMG_SOURCE),
    "xge_common_magic": ("xge_common_magic/xge_common_magic_p136_139.json", 136, XGE_SOURCE),
}

RARITY_WORDS = (
    "raridade variável",
    "muito rara",
    "muito raro",
    "lendária",
    "lendário",
    "rara",
    "raro",
    "incomum",
    "comum",
    "artefato",
)

MAGIC_TYPE_PREFIXES = (
    "Anel",
    "Arma",
    "Armadura",
    "Bastão",
    "Cajado",
    "Instrumento",
    "Item maravilhoso",
    "Pergaminho",
    "Poção",
    "Varinha",
)

MAGIC_NAME_REPAIRS = {
    "bolsa conven iente de especiarlas de heward": "Bolsa Conveniente de Especiarias de Heward",
    "cachi mbo dos mon stros de fumaca": "Cachimbo dos Monstros de Fumaça",
    "cajado cano ro": "Cajado Canoro",
    "can eca da so brl edade": "Caneca da Sobriedade",
    "chapeu da fe iti caria": "Chapéu da Feitiçaria",
    "chifre do alarme silencloso": "Chifre do Alarme Silencioso",
    "gota de refrescancla": "Gota de Refrescância",
    "ulho de ersatz": "Olho de Ersatz",
    "ol ho de ersatz": "Olho de Ersatz",
    "rubi do maco da guerra": "Rubi do Mago da Guerra",
    "varinha da pirotecn i a": "Varinha da Pirotecnia",
    "varin h a da regencia": "Varinha da Regência",
    "vari nha so rridente": "Varinha Sorridente",
    "vaso do despe rtar": "Vaso do Despertar",
    "vela das profu n d ezas": "Vela das Profundezas",
}

CLASSES = (
    "Bárbaro",
    "Bardo",
    "Bruxo",
    "Clérigo",
    "Druida",
    "Feiticeiro",
    "Guerreiro",
    "Ladino",
    "Mago",
    "Monge",
    "Paladino",
    "Patrulheiro",
)

CLASS_PROFICIENCIES = {
    "Bárbaro": {
        "armas": {"simples", "marciais"},
        "armaduras": {"leve", "media", "escudo"},
        "armas_especificas": set(),
        "ferramentas": set(),
        "ferramentas_tipos": set(),
    },
    "Bardo": {
        "armas": {"simples"},
        "armaduras": {"leve"},
        "armas_especificas": {"besta de mao", "espada longa", "rapieira", "espada curta"},
        "ferramentas": set(),
        "ferramentas_tipos": {"instrumento musical"},
    },
    "Bruxo": {
        "armas": {"simples"},
        "armaduras": {"leve"},
        "armas_especificas": set(),
        "ferramentas": set(),
        "ferramentas_tipos": set(),
    },
    "Clérigo": {
        "armas": {"simples"},
        "armaduras": {"leve", "media", "escudo"},
        "armas_especificas": set(),
        "ferramentas": set(),
        "ferramentas_tipos": set(),
    },
    "Druida": {
        "armas": set(),
        "armaduras": {"leve", "media", "escudo"},
        "armas_especificas": {
            "adaga",
            "azagaia",
            "bordao",
            "cimitarra",
            "dardo",
            "foice curta",
            "funda",
            "lanca",
            "maca",
            "porrete",
        },
        "ferramentas": {"kit de herbalismo"},
        "ferramentas_tipos": set(),
    },
    "Feiticeiro": {
        "armas": set(),
        "armaduras": set(),
        "armas_especificas": {"adaga", "besta leve", "beste leve", "bordao", "dardo", "funda"},
        "ferramentas": set(),
        "ferramentas_tipos": set(),
    },
    "Guerreiro": {
        "armas": {"simples", "marciais"},
        "armaduras": {"leve", "media", "pesada", "escudo"},
        "armas_especificas": set(),
        "ferramentas": set(),
        "ferramentas_tipos": set(),
    },
    "Ladino": {
        "armas": {"simples"},
        "armaduras": {"leve"},
        "armas_especificas": {"besta de mao", "espada longa", "espada curta", "rapieira"},
        "ferramentas": {"ferramentas de ladrao"},
        "ferramentas_tipos": set(),
    },
    "Mago": {
        "armas": set(),
        "armaduras": set(),
        "armas_especificas": {"adaga", "besta leve", "beste leve", "bordao", "dardo", "funda"},
        "ferramentas": set(),
        "ferramentas_tipos": set(),
    },
    "Monge": {
        "armas": {"simples"},
        "armaduras": set(),
        "armas_especificas": {"espada curta"},
        "ferramentas": set(),
        "ferramentas_tipos": {"ferramentas de artesao", "instrumento musical"},
    },
    "Paladino": {
        "armas": {"simples", "marciais"},
        "armaduras": {"leve", "media", "pesada", "escudo"},
        "armas_especificas": set(),
        "ferramentas": set(),
        "ferramentas_tipos": set(),
    },
    "Patrulheiro": {
        "armas": {"simples", "marciais"},
        "armaduras": {"leve", "media", "escudo"},
        "armas_especificas": set(),
        "ferramentas": set(),
        "ferramentas_tipos": set(),
    },
}

PHB_PRINTED_OVERRIDES = {
    ("phb_equipment", 2): 147,
    ("phb_equipment", 6): 151,
    ("phb_equipment", 7): 152,
    ("phb_equipment", 11): 156,
    ("phb_equipment", 14): 159,
}


def clean(text: str | None) -> str | None:
    if text is None:
        return None
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"(?<=\d)\.\s+(?=\d)", ".", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = text.replace(" -", "-").replace("- ", "-")
    return None if text in {"", "-", "–"} else text


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def title_pt(text: str) -> str:
    small = {"a", "as", "com", "contra", "da", "de", "do", "das", "dos", "e", "em", "na", "no", "para", "por"}
    words = text.lower().split()
    titled = [word.capitalize() if idx == 0 or word not in small else word for idx, word in enumerate(words)]
    return " ".join(titled)


def normalize_key(text: str | None) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_text = re.sub(r"\([^)]*\)", " ", ascii_text)
    ascii_text = re.sub(r"[^a-z0-9]+", " ", ascii_text)
    return re.sub(r"\s+", " ", ascii_text).strip()


def page_ref(pdf_page_1: int, printed_page: int | None = None) -> str:
    printed = printed_page if printed_page is not None else pdf_page_1
    return f"{printed} (PDF: {pdf_page_1})"


def item_base(
    *,
    name: str,
    category: str,
    item_type: str,
    source: str,
    pdf_page: int,
    printed_page: int | None = None,
    **extra: Any,
) -> dict[str, Any]:
    item = {
        "id": slugify(f"{source}-{category}-{name}"),
        "nome": clean(name),
        "categoria": category,
        "tipo": clean(item_type),
        "fonte": source,
        "pagina_livro": printed_page if printed_page is not None else pdf_page,
        "pagina_pdf": pdf_page,
        "referencia": page_ref(pdf_page, printed_page),
        "preco": None,
        "peso": None,
        "raridade": None,
        "sintonizacao": False,
        "propriedades": [],
        "dano": None,
        "descricao": "",
        "tabela": None,
        "proficiência_requerida": None,
        "classes": [],
    }
    item.update({key: value for key, value in extra.items() if value is not None})
    return item


def load_docling(docling_dir: Path, key: str) -> tuple[dict[str, Any], int, str]:
    rel_path, first_pdf_page, source = DOCLING_INPUTS[key]
    path = docling_dir / rel_path
    if not path.exists():
        raise FileNotFoundError(
            f"Docling JSON ausente: {path}. Rode Arsenal/run_docling_extraction.py antes de extrair."
        )
    return json.loads(path.read_text(encoding="utf-8")), first_pdf_page, source


def printed_pages(data: dict[str, Any], key: str, first_pdf_page: int) -> dict[int, int]:
    pages: dict[int, int] = {}
    for text in data.get("texts", []):
        if text.get("label") != "page_footer":
            continue
        value = clean(text.get("text")) or ""
        if not value.isdigit():
            continue
        rel_page = int(text.get("prov", [{}])[0].get("page_no", 0))
        pages[rel_page] = int(value)

    for (override_key, rel_page), printed in PHB_PRINTED_OVERRIDES.items():
        if override_key == key:
            pages[rel_page] = printed

    for rel_page in range(1, len(data.get("pages", {})) + 1):
        pages.setdefault(rel_page, first_pdf_page + rel_page - 1)
    return pages


def table_matrix(table: dict[str, Any]) -> list[list[str]]:
    cells = table["data"]["table_cells"]
    rows = max((cell["end_row_offset_idx"] for cell in cells), default=0)
    cols = max((cell["end_col_offset_idx"] for cell in cells), default=0)
    matrix = [["" for _ in range(cols)] for _ in range(rows)]
    for cell in cells:
        text = clean(cell.get("text")) or ""
        for row in range(cell["start_row_offset_idx"], cell["end_row_offset_idx"]):
            for col in range(cell["start_col_offset_idx"], cell["end_col_offset_idx"]):
                if row < rows and col < cols and not matrix[row][col]:
                    matrix[row][col] = text
    return matrix


def table_page(table: dict[str, Any], first_pdf_page: int) -> tuple[int, int]:
    rel_page = int(table.get("prov", [{}])[0].get("page_no", 1))
    return rel_page, first_pdf_page + rel_page - 1


def is_repeated_category(row: list[str]) -> bool:
    values = [cell for cell in row if cell]
    return bool(values) and len(set(values)) == 1


def parse_phb_tables(data: dict[str, Any], first_pdf_page: int, printed_by_rel: dict[int, int]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for table in data.get("tables", []):
        matrix = table_matrix(table)
        if not matrix:
            continue
        rel_page, pdf_page = table_page(table, first_pdf_page)
        printed = printed_by_rel.get(rel_page, pdf_page)
        first = " ".join(matrix[0]).upper()

        if "ARMADURAS" in first:
            items.extend(parse_armor_table(matrix, pdf_page, printed))
        elif "ARMAS" in first:
            items.extend(parse_weapon_table(matrix, pdf_page, printed))
        elif "EQUIPAMENTO" in first and len(matrix[0]) == 6:
            items.extend(parse_equipment_table(matrix, pdf_page, printed))
        elif matrix[0][:3] == ["Item", "Custo", "Peso"] and len(matrix) > 20:
            items.extend(parse_tools_table(matrix, pdf_page, printed))
        elif matrix[0][:4] == ["Item", "Custo", "Deslocamento", "Capacidade de Carga"]:
            items.extend(parse_mount_table(matrix, pdf_page, printed))
        elif matrix[0][:3] == ["Item", "Custo", "Peso"] and len(matrix) <= 20:
            items.extend(parse_tack_table(matrix, pdf_page, printed))
        elif matrix[0][:3] == ["Item", "Custo", "Velocidade"]:
            items.extend(parse_water_vehicle_table(matrix, pdf_page, printed))
    return items


def split_description_heading(text: str) -> tuple[str, str] | None:
    match = re.match(r"^(.{2,90}?)\s*\.\s+(.+)$", text)
    if not match:
        return None
    heading = clean(match.group(1)) or ""
    body = clean(match.group(2)) or ""
    if not heading or not body:
        return None
    if heading[0].islower() or len(heading.split()) > 8:
        return None
    return heading, body


def build_phb_description_map(data: dict[str, Any]) -> dict[str, str]:
    descriptions: dict[str, list[str]] = {}
    active_key: str | None = None

    for text in data.get("texts", []):
        label = text.get("label")
        value = clean(text.get("text")) or ""
        if not value:
            continue
        if label in {"page_footer", "section_header"}:
            active_key = None
            continue

        heading = split_description_heading(value)
        if heading:
            title, body = heading
            active_key = normalize_key(title)
            descriptions.setdefault(active_key, []).append(body)
            continue

        if active_key and label in {"text", "list_item"}:
            descriptions.setdefault(active_key, []).append(value)

    return {key: clean(" ".join(parts)) or "" for key, parts in descriptions.items()}


def description_keys_for_item(item: dict[str, Any]) -> list[str]:
    keys = [normalize_key(item.get("nome"))]
    item_type = normalize_key(item.get("tipo"))
    if item_type:
        keys.append(item_type)

    name_key = keys[0]
    if name_key.startswith("corda de "):
        keys.append("corda")
    if name_key.startswith("racoes de viagem"):
        keys.append("racoes de viagem")
    if name_key.startswith("simbolo sagrado") or item_type == "simbolo sagrado":
        keys.append("simbolo sagrado")
    if name_key == "ferramentas de navegacao":
        keys.append("ferramentas de navegador")

    return list(dict.fromkeys(key for key in keys if key))


def enrich_phb_descriptions(data: dict[str, Any], items: list[dict[str, Any]]) -> None:
    descriptions = build_phb_description_map(data)
    for item in items:
        if item.get("fonte") != PHB_SOURCE or item.get("descricao"):
            continue
        for key in description_keys_for_item(item):
            description = descriptions.get(key)
            if description:
                item["descricao"] = description
                break


def weapon_group(item_type: str | None) -> str | None:
    key = normalize_key(item_type)
    if "simples" in key:
        return "simples"
    if "marciais" in key:
        return "marciais"
    return None


def armor_group(item_type: str | None) -> str | None:
    key = normalize_key(item_type)
    if key == "escudo":
        return "escudo"
    if "leve" in key:
        return "leve"
    if "media" in key:
        return "media"
    if "pesada" in key:
        return "pesada"
    return None


def proficiency_requirement(item: dict[str, Any]) -> str | None:
    category = item.get("categoria")
    if category == "Arma":
        group = weapon_group(item.get("tipo"))
        if group == "simples":
            return "Armas simples"
        if group == "marciais":
            return "Armas marciais"
        return "Arma específica"
    if category == "Armadura":
        group = armor_group(item.get("tipo"))
        labels = {"leve": "Armadura leve", "media": "Armadura média", "pesada": "Armadura pesada", "escudo": "Escudo"}
        return labels.get(group, "Armadura")
    if category == "Ferramenta":
        return item.get("tipo") or "Ferramenta"
    return None


def class_can_use(item: dict[str, Any], class_name: str) -> bool:
    category = item.get("categoria")
    if category not in {"Arma", "Armadura", "Ferramenta"}:
        return True

    prof = CLASS_PROFICIENCIES[class_name]
    name_key = normalize_key(item.get("nome"))
    type_key = normalize_key(item.get("tipo"))

    if category == "Arma":
        group = weapon_group(item.get("tipo"))
        return bool(group and group in prof["armas"]) or name_key in prof["armas_especificas"]

    if category == "Armadura":
        group = armor_group(item.get("tipo"))
        return bool(group and group in prof["armaduras"])

    if category == "Ferramenta":
        return name_key in prof["ferramentas"] or type_key in prof["ferramentas_tipos"]

    return False


def enrich_class_usability(items: list[dict[str, Any]]) -> None:
    for item in items:
        requirement = proficiency_requirement(item)
        item["proficiência_requerida"] = requirement
        item["classes"] = [class_name for class_name in CLASSES if class_can_use(item, class_name)]


def parse_armor_table(matrix: list[list[str]], pdf_page: int, printed: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    current_type = "Armadura"
    category_rows = {"Armadura Leve", "Armadura Média", "Armadura Pesada", "Escudo"}
    for row in matrix[1:]:
        if not any(row):
            continue
        if is_repeated_category(row) and row[0] in category_rows:
            current_type = row[0]
            continue
        if row[0] in {"Nome", "ARMADURAS"}:
            continue
        name, price, ac, strength, stealth, weight = (row + [""] * 6)[:6]
        items.append(
            item_base(
                name=name,
                category="Armadura",
                item_type=current_type,
                source=PHB_SOURCE,
                pdf_page=pdf_page,
                printed_page=printed,
                preco=clean(price),
                peso=clean(weight),
                ca=clean(ac),
                forca_minima=clean(strength),
                furtividade=clean(stealth),
                tabela={"headers": ["Nome", "Preço", "CA", "Força", "Furtividade", "Peso"], "row": row},
            )
        )
    return items


def parse_weapon_table(matrix: list[list[str]], pdf_page: int, printed: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    current_type = "Arma"
    for row in matrix[1:]:
        if not any(row):
            continue
        if is_repeated_category(row):
            current_type = row[0]
            continue
        name, price, damage, weight, props = (row + [""] * 5)[:5]
        if name in {"Nome", "ARMAS Nome"}:
            continue
        items.append(
            item_base(
                name=name,
                category="Arma",
                item_type=current_type,
                source=PHB_SOURCE,
                pdf_page=pdf_page,
                printed_page=printed,
                preco=clean(price),
                peso=clean(weight),
                dano=clean(damage),
                propriedades=[part.strip().capitalize() for part in (clean(props) or "").split(",") if part.strip()],
                tabela={"headers": ["Nome", "Preço", "Dano", "Peso", "Propriedades"], "row": row},
            )
        )
    return items


def parse_equipment_table(matrix: list[list[str]], pdf_page: int, printed: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    category_rows = {"Munição", "Foco arcano", "Foco druídico", "Símbolo sagrado", "Símbolosagrado"}
    for row in matrix[1:]:
        for offset in (0, 3):
            name, price, weight = (row[offset : offset + 3] + [""] * 3)[:3]
            if not name or name == "Item":
                continue
            if name in category_rows and not price and not weight:
                continue
            items.append(
                item_base(
                    name=name,
                    category="Equipamento",
                    item_type="Equipamento de aventura",
                    source=PHB_SOURCE,
                    pdf_page=pdf_page,
                    printed_page=printed,
                    preco=clean(price),
                    peso=clean(weight),
                    tabela={"headers": ["Item", "Custo", "Peso"], "row": [name, price, weight]},
                )
            )
    return items


def parse_tools_table(matrix: list[list[str]], pdf_page: int, printed: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    current_type = "Ferramenta"
    category_rows = {"Ferramentas de artesão", "Instrumento musical", "Kit de jogo", "Jogos", "Veículos"}
    standalone_tools = {"Ferramentas de navegação", "Ferramentas de ladrão"}
    kit_tools = {"Kit de disfarce", "Kit de falsificação", "Kit de herbalismo", "Kit de venenos"}
    for row in matrix[1:]:
        name, price, weight = (row + [""] * 3)[:3]
        if not name or name == "Item":
            continue
        if name in category_rows and not price and not weight:
            current_type = name
            continue
        item_type = current_type
        if name in standalone_tools:
            item_type = "Ferramenta"
        elif name in kit_tools:
            item_type = "Kit"
        elif name.startswith("Veículos"):
            item_type = "Veículo"
        items.append(
            item_base(
                name=name,
                category="Ferramenta",
                item_type=item_type,
                source=PHB_SOURCE,
                pdf_page=pdf_page,
                printed_page=printed,
                preco=clean(price),
                peso=clean(weight),
                tabela={"headers": ["Item", "Custo", "Peso"], "row": row},
            )
        )
    return items


def parse_mount_table(matrix: list[list[str]], pdf_page: int, printed: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in matrix[1:]:
        name, price, speed, capacity = (row + [""] * 4)[:4]
        if not name:
            continue
        items.append(
            item_base(
                name=name,
                category="Montaria",
                item_type="Montarias e outros animais",
                source=PHB_SOURCE,
                pdf_page=pdf_page,
                printed_page=printed,
                preco=clean(price),
                deslocamento=clean(speed),
                capacidade_carga=clean(capacity),
                tabela={"headers": ["Item", "Custo", "Deslocamento", "Capacidade de Carga"], "row": row},
            )
        )
    return items


def parse_tack_table(matrix: list[list[str]], pdf_page: int, printed: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    current_type = "Arreio, sela e veículo de tração"
    for row in matrix[1:]:
        name, price, weight = (row + [""] * 3)[:3]
        if not name:
            continue
        if name == "Sela" and not price and not weight:
            current_type = "Sela"
            continue
        items.append(
            item_base(
                name=name,
                category="Veículo e montaria",
                item_type=current_type,
                source=PHB_SOURCE,
                pdf_page=pdf_page,
                printed_page=printed,
                preco=clean(price),
                peso=clean(weight),
                tabela={"headers": ["Item", "Custo", "Peso"], "row": row},
            )
        )
    return items


def parse_water_vehicle_table(matrix: list[list[str]], pdf_page: int, printed: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in matrix[1:]:
        name, price, speed = (row + [""] * 3)[:3]
        if not name:
            continue
        items.append(
            item_base(
                name=name,
                category="Veículo",
                item_type="Veículo aquático",
                source=PHB_SOURCE,
                pdf_page=pdf_page,
                printed_page=printed,
                preco=clean(price),
                velocidade=clean(speed),
                tabela={"headers": ["Item", "Custo", "Velocidade"], "row": row},
            )
        )
    return items


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


def is_magic_meta(text: str) -> bool:
    value = clean(text) or ""
    value = value.replace("}", ")")
    lower = value.lower()
    if len(value) > 180:
        return False
    if not any(value.startswith(prefix) for prefix in MAGIC_TYPE_PREFIXES):
        return False
    return any(rarity in lower for rarity in RARITY_WORDS)


def split_magic_header_meta(text: str) -> tuple[str, str] | None:
    value = (clean(text) or "").replace("}", ")")
    if not value:
        return None
    prefix_pattern = "|".join(re.escape(prefix) for prefix in MAGIC_TYPE_PREFIXES)
    match = re.search(rf"\b((?:{prefix_pattern})(?:\s*\([^)]*\))?\s*,\s*.+)$", value, flags=re.IGNORECASE)
    if not match:
        return None
    name = clean(value[: match.start()]) or ""
    meta = clean(match.group(1)) or ""
    if not name or not is_magic_meta(meta):
        return None
    return name, meta


def extract_rarity(meta: str) -> str | None:
    lower = meta.lower()
    for rarity in RARITY_WORDS:
        if rarity in lower:
            return rarity
    return None


def magic_name(raw_name: str) -> str:
    key = normalize_key(raw_name)
    if key in MAGIC_NAME_REPAIRS:
        return MAGIC_NAME_REPAIRS[key]
    return title_pt(raw_name)


def strip_bullet(text: str) -> str:
    return clean(text.replace("\uf0b7", "").lstrip("•- ")) or ""


def split_roll_table_row(text: str) -> tuple[str, str] | None:
    match = re.match(r"^(\d{1,3}(?:-\d{1,3})?)\s+(.+)$", text)
    if not match:
        return None
    return match.group(1), match.group(2)


def split_roll_table_header(text: str) -> tuple[str, str] | None:
    match = re.match(r"^(d\d+)\s+(.+)$", normalize_key(text))
    if not match:
        return None
    return match.group(1), title_pt(match.group(2))


def parse_magic_items(
    data: dict[str, Any],
    *,
    key: str,
    source: str,
    first_pdf_page: int,
    printed_by_rel: dict[int, int],
) -> list[dict[str, Any]]:
    texts = ordered_texts(data)
    item_starts: dict[int, tuple[str, str, bool]] = {}
    for index, text in enumerate(texts):
        if text.get("label") != "section_header":
            continue
        value = clean(text.get("text")) or ""
        combined = split_magic_header_meta(value)
        if combined:
            name, meta = combined
            item_starts[index] = (name, meta, False)
            continue
        if index + 1 < len(texts) and is_magic_meta(texts[index + 1].get("text", "")):
            meta = clean(texts[index + 1].get("text")) or ""
            item_starts[index] = (value, meta.replace("}", ")"), True)

    items: list[dict[str, Any]] = []
    active: dict[str, Any] | None = None
    active_description: list[str] = []
    active_blocks: list[dict[str, Any]] = []
    active_table: dict[str, Any] | None = None
    skip_next_meta = False

    def close_active() -> None:
        if active is None:
            return
        active["descricao"] = clean(" ".join(active_description)) or ""
        if active_blocks:
            active["descricao_blocos"] = active_blocks
        items.append(active)

    def add_description(label: str | None, value: str) -> None:
        nonlocal active_table
        table_header = split_roll_table_header(value) if label in {"section_header", "list_item"} else None
        if table_header:
            die, result_label = table_header
            active_table = {"type": "table", "headers": [die, result_label], "rows": []}
            active_blocks.append(active_table)
            active_description.append(value)
            return

        if label in {"list_item", "text"}:
            stripped = strip_bullet(value)
            row = split_roll_table_row(stripped)
            if active_table is not None and row:
                active_table["rows"].append([row[0], row[1]])
                active_description.append(stripped)
                return
            if label == "text":
                active_table = None
                active_blocks.append({"type": "paragraph", "text": value})
                active_description.append(value)
                return
            active_table = None
            if active_blocks and active_blocks[-1].get("type") == "list":
                active_blocks[-1]["items"].append(stripped)
            else:
                active_blocks.append({"type": "list", "items": [stripped]})
            active_description.append(stripped)
            return

        active_table = None
        active_blocks.append({"type": "paragraph", "text": value})
        active_description.append(value)

    for index, text in enumerate(texts):
        label = text.get("label")
        value = clean(text.get("text")) or ""
        if not value:
            continue

        rel_page = int(text.get("prov", [{}])[0].get("page_no", 1))
        pdf_page = first_pdf_page + rel_page - 1
        printed = printed_by_rel.get(rel_page, pdf_page)

        if index in item_starts:
            close_active()
            name, meta, should_skip_meta = item_starts[index]
            active = item_base(
                name=magic_name(name),
                category="Item mágico",
                item_type=(meta.split(",", 1)[0] if "," in meta else meta),
                source=source,
                pdf_page=pdf_page,
                printed_page=printed,
                raridade=extract_rarity(meta),
                sintonizacao="sintonização" in meta.lower(),
                descricao="",
                metadados=meta,
            )
            active_description = []
            active_blocks = []
            active_table = None
            skip_next_meta = should_skip_meta
            continue

        if skip_next_meta:
            skip_next_meta = False
            continue

        if key == "xge_common_magic" and label == "section_header" and normalize_key(value).startswith(
            ("criando itens", "tabelas de itens")
        ):
            close_active()
            active = None
            active_description = []
            active_blocks = []
            active_table = None
            continue

        if active is None or label == "page_footer":
            continue
        if value.isdigit() and len(value) <= 3:
            continue

        add_description(label, value)

    close_active()
    return items


def apply_structured_item_fixes(items: list[dict[str, Any]]) -> None:
    def set_blocks(item: dict[str, Any], blocks: list[dict[str, Any]]) -> None:
        item["descricao_blocos"] = blocks
        parts: list[str] = []
        for block in blocks:
            if block["type"] == "paragraph":
                parts.append(block["text"])
            elif block["type"] == "list":
                parts.extend(block["items"])
            elif block["type"] == "table":
                parts.extend(" ".join(row) for row in block["rows"])
        item["descricao"] = clean(" ".join(parts)) or ""

    def rebuild_description_from_blocks(item: dict[str, Any]) -> None:
        parts: list[str] = []
        for block in item.get("descricao_blocos") or []:
            if block["type"] == "paragraph":
                parts.append(block["text"])
            elif block["type"] == "list":
                parts.extend(block["items"])
            elif block["type"] == "table":
                parts.extend(" ".join(row) for row in block["rows"])
        item["descricao"] = clean(" ".join(parts)) or item.get("descricao", "")

    def structure_retributive_strike_table(item: dict[str, Any]) -> None:
        blocks = item.get("descricao_blocos") or []
        rebuilt: list[dict[str, Any]] = []
        index = 0
        changed = False
        while index < len(blocks):
            block = blocks[index]
            if block.get("type") == "paragraph" and normalize_key(block.get("text")) == "distancia da origem dano":
                next_texts = [
                    blocks[index + offset].get("text")
                    for offset in range(1, 7)
                    if index + offset < len(blocks) and blocks[index + offset].get("type") == "paragraph"
                ]
                expected = [
                    "8 x a quantidade de cargas no cajado",
                    "3 metros ou menos",
                    "6 x a quantidade de cargas no cajado",
                    "Entre 3,1 e 6 metros",
                    "4 x a quantidade de cargas no cajado",
                    "Entre 6,1 e 9 metros",
                ]
                if next_texts == expected:
                    rebuilt.append(
                        {
                            "type": "table",
                            "headers": ["Distância da Origem", "Dano"],
                            "rows": [
                                ["3 metros ou menos", "8 x a quantidade de cargas no cajado"],
                                ["Entre 3,1 e 6 metros", "6 x a quantidade de cargas no cajado"],
                                ["Entre 6,1 e 9 metros", "4 x a quantidade de cargas no cajado"],
                            ],
                        }
                    )
                    index += 7
                    changed = True
                    continue
            rebuilt.append(block)
            index += 1
        if changed:
            item["descricao_blocos"] = rebuilt
            rebuild_description_from_blocks(item)

    def split_effect_paragraphs(text: str) -> list[dict[str, str]]:
        headings = (
            "As parcas", "Balança", "Bufão", "Cavaleiro", "Chamas", "Chave", "Cometa", "Crânio",
            "Estrela", "Euríale", "Gema", "Idiota", "Lua", "Ladino", "Masmorra", "Ruína",
            "Sol", "Tolo", "Trono", "O Vácuo", "Vizir",
        )
        pattern = r"(?=(" + "|".join(re.escape(heading) for heading in headings) + r")\.)"
        parts = [part.strip() for part in re.split(pattern, text) if part.strip()]
        paragraphs: list[dict[str, str]] = []
        index = 0
        while index < len(parts):
            if parts[index] in headings and index + 1 < len(parts):
                paragraphs.append({"type": "paragraph", "text": clean(parts[index] + parts[index + 1]) or ""})
                index += 2
            else:
                paragraphs.append({"type": "paragraph", "text": clean(parts[index]) or ""})
                index += 1
        return [paragraph for paragraph in paragraphs if paragraph["text"]]

    illusion_rows = [
        ["Ás de copas", "Dragão vermelho"],
        ["Rei de copas", "Cavaleiro e quatro guardas"],
        ["Rainha de copas", "Súcubo ou íncubo"],
        ["Valete de copas", "Druida"],
        ["Dez de copas", "Gigante das nuvens"],
        ["Nove de copas", "Ettin"],
        ["Oito de copas", "Bugbear"],
        ["Dois de copas", "Goblin"],
        ["Ás de ouros", "Observador"],
        ["Rei de ouros", "Arquimago e arcano"],
        ["Rainha de ouros", "Bruxa da noite"],
        ["Valete de ouros", "Assassino"],
        ["Dez de ouros", "Gigante do fogo"],
        ["Nove de ouros", "Ogro mago"],
        ["Oito de ouros", "Gnoll"],
        ["Dois de ouros", "Kobold"],
        ["Ás de espadas", "Lich"],
        ["Rei de espadas", "Sacerdote e dois acólitos"],
        ["Rainha de espadas", "Medusa"],
        ["Valete de espadas", "Veterano"],
        ["Dez de espadas", "Gigante do gelo"],
        ["Nove de espadas", "Troll"],
        ["Oito de espadas", "Hobgoblin"],
        ["Dois de espadas", "Goblin"],
        ["Ás de paus", "Golem de ferro"],
        ["Rei de paus", "Capitão dos bandidos e três bandidos"],
        ["Rainha de paus", "Erínia"],
        ["Valete de paus", "Furioso"],
        ["Dez de paus", "Gigante da colina"],
        ["Nove de paus", "Ogro"],
        ["Oito de paus", "Orc"],
        ["Dois de paus", "Kobold"],
        ["Coringas (2)", "Você (o dono do baralho)"],
    ]
    surprise_rows = [
        ["Ás de ouros", "Vizir*"],
        ["Rei de ouros", "Sol"],
        ["Rainha de ouros", "Lua"],
        ["Valete de ouros", "Estrela"],
        ["Dois de ouros", "Cometa*"],
        ["Ás de copas", "As parcas*"],
        ["Rei de copas", "Trono"],
        ["Rainha de copas", "Chave"],
        ["Valete de copas", "Cavaleiro"],
        ["Dois de copas", "Gema*"],
        ["Ás de paus", "Garras*"],
        ["Rei de paus", "O Vácuo"],
        ["Rainha de paus", "Chamas"],
        ["Valete de paus", "Crânio"],
        ["Dois de paus", "Idiota*"],
        ["Ás de espadas", "Masmorra*"],
        ["Rei de espadas", "Ruína"],
        ["Rainha de espadas", "Euríale"],
        ["Valete de espadas", "Ladino"],
        ["Dois de espadas", "Balança*"],
        ["Coringa (vermelho)", "Tolo*"],
        ["Coringa (preto)", "Bufão"],
    ]

    resistance_rows = [
        ["1", "Ácido"],
        ["2", "Frio"],
        ["3", "Fogo"],
        ["4", "Energia"],
        ["5", "Elétrico"],
        ["6", "Necrótico"],
        ["7", "Veneno"],
        ["8", "Psíquico"],
        ["9", "Radiante"],
        ["10", "Trovejante"],
    ]
    fixed_blocks: dict[tuple[str, str], list[dict[str, Any]]] = {
        ("Poção de Resistência", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": (
                    "Quando bebe esta poção, você ganha resistência a um tipo de dano por 1 hora. "
                    "O Mestre escolhe o tipo ou o determina aleatoriamente das opções abaixo."
                ),
            },
            {"type": "table", "headers": ["d10", "Tipo de Dano"], "rows": resistance_rows},
        ],
        ("Poção de Cura", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": "Você recupera pontos de vida quando bebe esta poção. A quantidade de pontos de vida depende da raridade da poção, como mostrado na tabela Poção de Cura. Qualquer que seja a potência, o líquido vermelho da poção cintila quando agitado.",
            },
            {
                "type": "table",
                "headers": ["Poção de...", "Raridade", "PV Recuperados"],
                "rows": [
                    ["Cura", "Comum", "2d4 + 2"],
                    ["Cura maior", "Incomum", "4d4 + 4"],
                    ["Cura superior", "Rara", "8d4 + 8"],
                    ["Cura suprema", "Muito rara", "10d4 + 20"],
                ],
            },
        ],
        ("Poção de Força do Gigante", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": "Quando bebe esta poção, seu valor de Força muda por 1 hora. O tipo de gigante determinar o valor (veja na tabela abaixo). A poção não produz efeito em você caso sua Força seja igual ou maior que o valor dela.",
            },
            {
                "type": "paragraph",
                "text": "O líquido transparente dessa poção tem um pedaço de unha de um gigante do tipo apropriado flutuando nele. A poção de força do gigante do gelo e a poção de força do gigante de pedra têm o mesmo efeito.",
            },
            {
                "type": "table",
                "headers": ["Tipo de Gigante", "Força", "Raridade"],
                "rows": [
                    ["Gigante da colina", "21", "Incomum"],
                    ["Gigante de pedra/gelo", "23", "Rara"],
                    ["Gigante do fogo", "25", "Rara"],
                    ["Gigante das nuvens", "27", "Muito rara"],
                    ["Gigante da tempestade", "29", "Lendária"],
                ],
            },
        ],
        ("Armadura de Resistência", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": (
                    "Você tem resistência a um tipo de dano enquanto estiver vestindo esta armadura. O Mestre escolhe "
                    "o tipo ou o determina aleatoriamente das opções abaixo."
                ),
            },
            {"type": "table", "headers": ["d10", "Tipo de Dano"], "rows": resistance_rows},
        ],
        ("Anel de Resistência", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": (
                    "Você tem resistência a um tipo de dano enquanto usar este anel. A gema no anel indica o tipo, "
                    "a qual o Mestre escolhe ou determina aleatoriamente."
                ),
            },
            {
                "type": "table",
                "headers": ["d10", "Tipo de Dano", "Gema"],
                "rows": [
                    ["1", "Ácido", "Pérola"],
                    ["2", "Frio", "Turmalina"],
                    ["3", "Fogo", "Granada"],
                    ["4", "Energia", "Safira"],
                    ["5", "Elétrico", "Citrina"],
                    ["6", "Necrótico", "Jato"],
                    ["7", "Veneno", "Ametista"],
                    ["8", "Psíquico", "Jade"],
                    ["9", "Radiante", "Topázio"],
                    ["10", "Trovejante", "Espinela"],
                ],
            },
        ],
        ("Anel de Estrelas Cadentes", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": "Enquanto estiver usando este anel sob penumbra ou escuridão, você pode conjurar globos de luz ou luz através dele, à vontade. Conjurar qualquer dessas magias através do anel requer uma ação.",
            },
            {
                "type": "paragraph",
                "text": "O anel tem 6 cargas para as propriedades a seguir. O anel recupera 1d6 cargas gastas diariamente ao amanhecer.",
            },
            {"type": "paragraph", "text": "Fogo das Fadas. Você pode gastar 1 carga com uma ação para conjurar fogo das fadas através do anel."},
            {
                "type": "paragraph",
                "text": "Bola de Eletricidade. Você pode gastar 2 cargas com uma ação para criar de uma a quatro esferas de 1 metro de diâmetro de eletricidade. Quanto mais esferas você criar, menos poderosas cada uma delas será individualmente.",
            },
            {
                "type": "paragraph",
                "text": "Cada esfera aparece em um espaço desocupado que você possa ver, a até 36 metros de você. As esferas duram enquanto você se concentrar, até 1 minuto. Cada esfera emite penumbra num raio de 9 metros.",
            },
            {
                "type": "paragraph",
                "text": "Com uma ação bônus, você pode movimentar cada esfera até 9 metros, mas não além de 36 metros de você. Quando uma criatura, diferente de você, se aproxima a 1,5 metro de uma esfera, a esfera descarrega eletricidade na criatura e desaparece. A criatura deve realizar um teste de resistência de Destreza CD 15. Se falhar na resistência, a criatura sofre dano elétrico baseado na quantidade de esferas criadas.",
            },
            {
                "type": "table",
                "headers": ["Esferas", "Dano Elétrico"],
                "rows": [["1", "4d12"], ["2", "5d4"], ["3", "2d6"], ["4", "2d4"]],
            },
            {
                "type": "paragraph",
                "text": "Estrelas Cadentes. Você pode gastar de 1 a 3 cargas com uma ação. Para cada carga gasta, você arremessa um fagulha brilhante de luz através do anel em um ponto que você possa ver, a até 18 metros de você. Cada criatura num cubo de 4,5 metros originado no ponto é banhada por faíscas e deve realizar um teste de resistência de Destreza CD 15, sofrendo 5d4 de dano de fogo se falhar na resistência, ou metade desse dano se obtiver sucesso.",
            },
        ],
        ("Baralho das Ilusões", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": "Esta caixa contém um conjunto cartas de pergaminho. Um baralho completo tem 34 cartas. Um baralho encontrado em um tesouro geralmente tem 1d20-1 cartas faltando.",
            },
            {
                "type": "paragraph",
                "text": "A magia deste baralho funciona apenas se cartas forem puxadas aleatoriamente (você pode usar um baralho de cartas alterado para simular esse baralho). Você pode usar uma ação para puxar uma carta aleatória do baralho e joga-la no chão num local a até 9 metros de você.",
            },
            {
                "type": "paragraph",
                "text": "Uma ilusão de uma ou mais criaturas se forma em cima da carta jogada e permanece até se dissipar. Uma criatura ilusória parece real, de tamanho apropriado, e age como se fosse uma criatura real (como apresentado no Manual dos Monstros), exceto por ela não poder causar qualquer mazela. Enquanto você estiver a até 36 metros da criatura ilusória e puder vê-la, você pode usar uma ação para move-la magicamente para qualquer lugar a até 9 metros da carta.",
            },
            {
                "type": "paragraph",
                "text": "Qualquer interação física com a criatura ilusória a revela como sendo uma ilusão, já que objetos passam através dela. Alguém que use uma ação para inspecionar visualmente a criatura, identificará ela como sendo ilusória com um teste de Inteligência (Investigação) CD 15. A criatura então, parecerá translucida.",
            },
            {
                "type": "paragraph",
                "text": "A ilusão dura até a carta ser movida ou a ilusão ser dissipada. Quando a ilusão terminar, a imagem na carta desaparece e esta carta não poderá ser usada novamente.",
            },
            {"type": "table", "headers": ["Carta Jogada", "Ilusão"], "rows": illusion_rows},
        ],
        ("Baralho das Surpresas", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": "Geralmente encontrado em uma caixa ou bolsa, este baralho contém uma quantidade de cartas feitas de marfim ou velino. A maioria (75 por cento) desses baralhos tem apenas treze cartas, mas o resto tem vinte e duas.",
            },
            {"type": "table", "headers": ["Carta Jogada", "Carta"], "rows": surprise_rows},
            {"type": "paragraph", "text": "*Encontrada apenas em um baralho com vinte e duas cartas."},
        ],
        ("Bolsa de Truques", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": (
                    "Esta bolsa ordinária, feita de tecido cinza, ferrugem ou bronze, parece vazia. Procurando dentro "
                    "dela, no entanto, revelará a presença de pequenos objetos felpudos. A bolsa pesa 250 gramas."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Você pode usar uma ação para puxar um objeto felpudo da bolsa e arremessa-lo a até 6 metros. "
                    "Quando o objeto toca o solo, ele se transforma em uma criatura que você determina rolando um d8 "
                    "e consultando a tabela correspondente a cor da bolsa. Veja o Manual dos Monstros para as "
                    "estatísticas da criatura. A criatura desaparece na próxima manhã ou quando for reduzido a 0 "
                    "pontos de vida."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "A criatura é amigável a você e aos seus companheiros, e ela age no seu turno. Você pode usar uma "
                    "ação bônus para comandar como a criatura se move e qual ação ela realiza no seu próximo turno, "
                    "ou para dar ordens genéricas a ela, como para atacar seus inimigos. Na ausência de tais ordens, "
                    "a criatura age de uma forma apropriada a sua natureza."
                ),
            },
            {
                "type": "paragraph",
                "text": "Quando três objetos felpudos tiverem sido tirados da bolsa, ela não poderá ser usada novamente até o próximo amanhecer.",
            },
            {
                "type": "table",
                "headers": ["d8", "Bolsa de Truques Bronze"],
                "rows": [
                    ["1", "Chacal"],
                    ["2", "Gorila"],
                    ["3", "Babuíno"],
                    ["4", "Bico de machado"],
                    ["5", "Urso negro"],
                    ["6", "Arminho gigante"],
                    ["7", "Hiena gigante"],
                    ["8", "Tigre"],
                ],
            },
            {
                "type": "table",
                "headers": ["d8", "Bolsa de Truques Cinza"],
                "rows": [
                    ["1", "Arminho"],
                    ["2", "Rato gigante"],
                    ["3", "Texugo"],
                    ["4", "Javali"],
                    ["5", "Pantera"],
                    ["6", "Texugo gigante"],
                    ["7", "Lobo atroz"],
                    ["8", "Alce gigante"],
                ],
            },
            {
                "type": "table",
                "headers": ["d8", "Bolsa de Truques Ferrugem"],
                "rows": [
                    ["1", "Rato"],
                    ["2", "Coruja"],
                    ["3", "Mastim"],
                    ["4", "Bode"],
                    ["5", "Bode gigante"],
                    ["6", "Javali gigante"],
                    ["7", "Leão"],
                    ["8", "Urso marrom"],
                ],
            },
        ],
        ("Cinturão de Força do Gigante", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": "Enquanto estiver usando este cinto, seu valor de Força muda para o valor concedido pelo cinto. Caso seu valor de Força sem o cinto já for igual ou superior ao valor do cinto, o item não tem qualquer efeito sobre você.",
            },
            {
                "type": "paragraph",
                "text": "Existem seis variações desse cinto, correspondentes e com raridade variando de acordo com os seis tipos de gigantes verdadeiros. O cinturão de força do gigante de pedra e o cinturão de força do gigante do gelo parecem diferentes, mas possuem o mesmo efeito.",
            },
            {
                "type": "table",
                "headers": ["Tipo", "Força", "Raridade"],
                "rows": [
                    ["Gigante da colina", "21", "Raro"],
                    ["Gigante de pedra/gelo", "23", "Muito raro"],
                    ["Gigante do fogo", "25", "Muito raro"],
                    ["Gigante das nuvens", "27", "Lendário"],
                    ["Gigante da tempestade", "29", "Lendário"],
                ],
            },
        ],
        ("Cubo de Força", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": "Este cubo tem aproximadamente 2,5 centímetros de diâmetro. Cada face possui uma marcação distinta nela que pode ser pressionada. O cubo começa com 36 cargas e recupera 1d20 cargas gastas diariamente pelo amanhecer.",
            },
            {
                "type": "paragraph",
                "text": "Você pode usar uma ação para pressionar uma das faces do cubo, gastando um número de cargas baseado na face escolhida, como mostrado na tabela Faces do Cubo de Força. Cada face possui um efeito diferente. Se o cubo não tiver cargas restantes suficientes, nada acontece. Do contrário, uma barreira de energia invisível surge do nada, formando um cubo de 4,5 metros de lado. A barreira é centrada em você, se move com você e dura 1 minuto, até você usar uma ação para pressionar a sexta face do cubo, ou o cubo ficar sem cargas. Você pode mudar o efeito da barreira ao pressionar uma face diferente do cubo e gastar o número requerido de cargas, reiniciando a duração.",
            },
            {
                "type": "paragraph",
                "text": "Se o seu movimento fizer com que a barreira entre em contato com um objeto sólido que não possa passar pelo cubo, você não poderá se aproximar mais desse objeto enquanto a barreira permanecer.",
            },
            {
                "type": "table",
                "headers": ["Face", "Cargas", "Efeito"],
                "rows": [
                    ["1", "1", "Gases, vento e névoa não podem atravessar a barreira."],
                    ["2", "2", "Matéria inorgânica não pode atravessar a barreira. Paredes, pisos e tetos podem atravessar ao seu critério."],
                    ["3", "3", "Matéria orgânica não pode atravessar a barreira."],
                    ["4", "4", "Efeitos de magias não pode atravessar a barreira."],
                    ["5", "5", "Nada pode atravessar a barreira. Paredes, pisos e tetos podem atravessar ao seu critério."],
                    ["6", "0", "A barreira se desativa."],
                ],
            },
            {
                "type": "paragraph",
                "text": "O cubo perde cargas quando a barreira é alvo de certas magias ou entra em contato com certas magias ou efeitos de itens mágicos, como mostrado na tabela abaixo.",
            },
            {
                "type": "table",
                "headers": ["Magia ou Item", "Cargas Perdidas"],
                "rows": [["Desintegrar", "1d12"], ["Trombeta da destruição", "1d10"], ["Criar passagem", "1d6"], ["Rajada prismática", "1d20"], ["Muralha de fogo", "1d4"]],
            },
        ],
        ("Corrente de Contas de Oração", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": (
                    "Este colar possui 1d4 + 2 contas mágicas feitas de águas marinhas, pérolas negras ou topázios. "
                    "Ela tem também diversas contas não-mágicas feitas de pedras como âmbar, pedra de sangue, citrina, "
                    "coral, jade, pérola ou quartzo. Se uma conta mágica for removida da corrente, a conta perde sua mágica."
                ),
            },
            {
                "type": "table",
                "headers": ["d20", "Conta de...", "Magia"],
                "rows": [
                    ["1-6", "Benção", "Abençoar"],
                    ["7-12", "Curar", "Curar ferimentos (2° nível) ou restauração menor"],
                    ["13-16", "Auxiliar", "Restauração maior"],
                    ["17-18", "Destruir", "Marca da punição"],
                    ["19", "Invocar", "Aliado planar"],
                    ["20", "Andar no vento", "Caminhar no vento"],
                ],
            },
            {
                "type": "paragraph",
                "text": (
                    "Existem seis tipos de contas mágicas. O Mestre decide o tipo de cada uma na corrente ou as determinar "
                    "aleatoriamente. Uma corrente pode ter mais de um tipo da mesma conta. Para usar uma, você deve estar "
                    "usando o colar. Cada conta possui uma magia que você pode conjurar através dela, com uma ação bônus "
                    "(usando sua CD de magia, se um teste de resistência for necessário). Uma vez que a magia de uma conta "
                    "mágica é conjurada, a conta não poderá ser usada novamente até o próximo amanhecer."
                ),
            },
        ],
        ("Manual dos Golens", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": (
                    "Este livro contém informações e encantos necessários para construir um tipo de golem em particular. "
                    "O Mestre escolhe o tipo ou o determina aleatoriamente. Para decifrar e usar o manual, você deve ser "
                    "um conjurador com pelo menos dois espaços de magias de 5° nível. Uma criatura que não possa usar o "
                    "manual dos golens e tente lê-lo, sofre 6d6 de dano psíquico."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Para criar um golem, você deve gastar o tempo mostrado na tabela, trabalhando sem interrupções com "
                    "o manual em mãos e descansando não mais de 8 horas por dia. Você também deve pagar o custo "
                    "especificado para adquirir os suprimentos."
                ),
            },
            {
                "type": "table",
                "headers": ["d20", "Golem", "Custo", "Tempo"],
                "rows": [
                    ["1-5", "Barro", "65.000 po", "30 dias"],
                    ["6-17", "Carne", "50.000 po", "60 dias"],
                    ["18", "Ferro", "100.000 po", "120 dias"],
                    ["19-20", "Pedra", "80.000 po", "90 dias"],
                ],
            },
            {
                "type": "paragraph",
                "text": (
                    "Quando você terminar de criar o golem, o livro é consumido por chamas místicas. O golem torna-se "
                    "animado quando as cinzas do manual forem aspergidas nele. Ele está sob seu controle, e compreende "
                    "e obedece aos seus comandos falados. Veja o Manual dos Monstros para as estatísticas de jogo dele."
                ),
            },
        ],
        ("Instrumento dos Bardos", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": "Um instrumento dos bardos é um exemplar exótico de seu tipo, superior a um instrumento ordinário de todas as formas. Sete tipos desses instrumentos existem, cada um nomeado em homenagem a um lendário colégio de bardos. A tabela a seguir lista as magias comuns a todos os instrumentos, assim como as magias especificas a cada um deles e sua raridade.",
            },
            {
                "type": "paragraph",
                "text": "Uma criatura que tente tocar um instrumento sem se sintonizar a ele, deve ser bem sucedida num teste de resistência de Sabedoria CD 15 ou sofrerá 2d4 de dano psíquico.",
            },
            {
                "type": "paragraph",
                "text": "Você pode usar uma ação para tocar o instrumento e conjurar uma de suas magias. Uma vez que o instrumento tenha sido usado para conjurar uma magia, ele não poderá ser usado para conjurar essa magia novamente até o próximo amanhecer. A magia usa sua habilidade de conjuração e CD de suas magias.",
            },
            {
                "type": "paragraph",
                "text": "Quando você usa o instrumento para conjurar uma magia que faça com que os alvos fiquem enfeitiçados caso fracassem na resistência, os alvos terão desvantagem nos testes de resistência. Esse efeito se aplica tanto quando você está usando o instrumento como fonte de magia quanto como seu foco de conjuração.",
            },
            {
                "type": "table",
                "headers": ["Instrumento", "Raridade", "Magias"],
                "rows": [
                    ["Todos", "-", "Voo, invisibilidade, levitação, proteção contra o bem e mal, mais as magias listadas para o instrumento em particular"],
                    ["Harpa de Anstruth", "Muito raro", "Controlar o clima, curar ferimentos (5° nível), muralha de espinhos"],
                    ["Mandolim de Canaith", "Raro", "Curar ferimentos (3° nível), dissipar magia, proteção contra energia (elétrico apenas)"],
                    ["Lira de Cli", "Raro", "Moldar rochas, muralha de fogo, muralha de vento"],
                    ["Alaúde de Doss", "Incomum", "Amizade animal, proteção contra energia (fogo apenas), proteção contra veneno"],
                    ["Bandolim de Fochlucan", "Incomum", "Constrição, fogo das fadas, bordão místico, falar com animais"],
                    ["Citara de Mac-Fuirmidh", "Incomum", "Pele de árvore, curar ferimentos, névoa obscurecente"],
                    ["Harpa de Ollamh", "Lendário", "Confusão, controlar o clima, tempestade de fogo"],
                ],
            },
        ],
        ("Pergaminho de Magia", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": "Um pergaminho de magia contém as palavras de uma única magia, escritas em cifras místicas. Se a magia estiver na sua lista de magias de classe, você pode ler o pergaminho e conjurar sua magia sem fornecer quaisquer componentes materiais. Do contrário, o pergaminho é inteligível. Conjurar a magia lendo o pergaminho requer o tempo normal de conjuração. Uma vez que tenha sido conjurada, as palavras no pergaminho desaparecem e ele se desfaz em pó. Se a conjuração for interrompida, o pergaminho não é gasto.",
            },
            {
                "type": "paragraph",
                "text": "Se a magia estiver na sua lista de magias de classe mas for de um nível maior que o que você normalmente conjura, você deve realizar um teste de habilidade usando sua habilidade de conjuração para determinar se a conjuração é bem sucedida. A CD é igual a 10 + o nível da magia. Se fracassar, a magia desaparece do pergaminho sem produzir outro efeito.",
            },
            {
                "type": "paragraph",
                "text": "O nível da magia num pergaminho determina a CD do teste de resistência da magia e o bônus de ataque, assim como a raridade do pergaminho, como mostrado na tabela Pergaminho de Magia.",
            },
            {
                "type": "table",
                "headers": ["Nível de Magia", "Raridade", "CD de Resistência", "Bônus de Ataque"],
                "rows": [
                    ["Truque", "Comum", "13", "+5"],
                    ["1°", "Comum", "13", "+5"],
                    ["2°", "Incomum", "13", "+5"],
                    ["3°", "Incomum", "15", "+7"],
                    ["4°", "Raro", "15", "+7"],
                    ["5°", "Raro", "17", "+9"],
                    ["6°", "Muito raro", "17", "+9"],
                    ["7°", "Muito raro", "18", "+10"],
                    ["8°", "Muito raro", "18", "+10"],
                    ["9°", "Lendário", "19", "+11"],
                ],
            },
            {
                "type": "paragraph",
                "text": "Um magia de mago em um pergaminho de magia pode ser copiada exatamente como magias de grimórios podem ser copiadas. Quando uma magia é copiada de um pergaminho de magia, o copiador deve ser bem sucedido num teste de Inteligência (Arcanismo) com CD igual a 10 + o nível da magia. Se o teste for bem sucedido, a magia é copiada. Independentemente do teste ser bem ou mal sucedido, o pergaminho de magia é destruído.",
            },
        ],
        ("Vela de Invocação", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": (
                    "Este cilindro delgado é dedicado a uma divindade e partilha da tendência da divindade. A tendência "
                    "da vela pode ser detectada com a magia detectar mal e bem. O Mestre escolhe o deus e tendência "
                    "associada ou determinar a tendência aleatoriamente."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "A mágica da vela é ativada quando ela é acessa, o que requer uma ação. Após queimar por 4 horas, "
                    "a vela é destruída. Você pode apaga-la antes para usa-la posteriormente. Deduza o tempo que ela "
                    "queimou em incrementos de 1 minuto do tempo de queima total da vela."
                ),
            },
            {
                "type": "table",
                "headers": ["d20", "Tendência"],
                "rows": [
                    ["1-2", "Caótico e mau"],
                    ["3-4", "Caótico e neutro"],
                    ["5-7", "Caótico e bom"],
                    ["8-9", "Neutro e mau"],
                    ["10-11", "Neutro"],
                    ["12-13", "Neutro e bom"],
                    ["14-15", "Leal e mau"],
                    ["16-17", "Leal e neutro"],
                    ["18-20", "Leal e bom"],
                ],
            },
            {
                "type": "paragraph",
                "text": (
                    "Enquanto estiver acesa, a vela emite penumbra num raio de 9 metros. Qualquer criatura dentro dessa "
                    "área cuja tendência combine com a da vela realiza jogadas de ataque, testes de resistência e testes "
                    "de habilidade com vantagem. Além disso, um clérigo ou druida nessa área cuja tendência combine com "
                    "a da vela, pode conjurar magias de 1° nível que tenha preparado sem gastar espaços de magia, apesar "
                    "do efeito da magia ser o de um conjurado com um espaço de 1° nível."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Alternativamente, quando você acender a vela pela primeira vez, você pode conjurar a magia portal "
                    "através dela. Fazer isso destruirá a vela."
                ),
            },
        ],
        ("Penas de Quaal", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": (
                    "Este pequeno objeto parece com uma pena. Existem diferentes tipos de penas, cada um com um uso "
                    "único diferente. O Mestre escolhe o tipo de pena ou o determina aleatoriamente."
                ),
            },
            {
                "type": "table",
                "headers": ["d100", "Pena"],
                "rows": [
                    ["01-20", "Âncora"],
                    ["21-35", "Árvore"],
                    ["36-50", "Chicote"],
                    ["51-65", "Barco de cisne"],
                    ["66-90", "Pássaro"],
                    ["91-00", "Leque"],
                ],
            },
            {
                "type": "paragraph",
                "text": (
                    "Âncora. Você pode usar uma ação para tocar a pena em um barco ou navio. Pelas próximas 24 horas, "
                    "a embarcação não pode ser movida por quaisquer meios. Tocar a pena na embarcação novamente termina "
                    "o efeito. Quando o efeito terminar, a pena desaparece."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Árvore. Você deve estar ao ar livre para usar essa pena. Você pode usar uma ação para toca-la em "
                    "um espaço desocupado no chão. A pena desaparece e, em seu lugar, um carvalho não-mágico brota do "
                    "nada. A árvore tem 18 metros de altura e 1,5 metro de diâmetro de tronco, e a copa no seu topo se "
                    "espalha num raio de 6 metros."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Barco de Cisne. Você pode usar uma ação para tocar a pena num corpo de água de pelo menos 18 metros "
                    "de diâmetro. A pena desaparece e um barco em forma de cisne de 15 metros de comprimento por 6 metros "
                    "de largura toma seu lugar. O barco tem propulsão própria e se move pela água a uma velocidade de 9 "
                    "quilômetros por hora. Você pode usar uma ação enquanto estiver no barco para comanda-lo a se mover "
                    "ou virar 90 graus. O barco pode carregar até trinta e duas criaturas Médias ou menores. Uma criatura "
                    "Grande conta como quatro criaturas Médias, enquanto que uma criatura Enorme conta como nove. O barco "
                    "permanece por 24 horas e então desaparece. Você pode dispensar o barco com uma ação."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Chicote. Você pode usar uma ação para arremessar a pena em um ponto a até 3 metros de você. A pena "
                    "desaparece e um chicote flutuante toma seu lugar. Você pode então, usar uma ação bônus para realizar "
                    "um ataque corpo-a-corpo com magia contra uma criatura a até 3 metros do chicote, com um bônus de "
                    "ataque de +9. Se atingir, o alvo sofre 1d6 + 5 de dano de energia."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Com uma ação bônus no seu turno, você pode direcionar o chicote a voar até 6 metros e repetir o "
                    "ataque contra uma criatura a até 3 metros dele. O chicote desaparece depois de 1 hora, quando você "
                    "usa uma ação para dispensa-lo ou quando você estiver incapacitado ou morto."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Leque. Se você estiver em um barco ou navio, você pode usar uma ação para arremessar a pena a 3 "
                    "metros no ar. A pena desaparece e um leque gigante toma seu lugar. O leque flutua e cria um vento "
                    "forte o suficiente para encher a vela de um barco, aumentando seu deslocamento em 7,5 quilômetros "
                    "por hora por 8 horas. Você pode dispensar o leque com uma ação."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Pássaro. Você pode usar uma ação para arremessar essa pena 1,5 metro no ar. A pena desaparece e um "
                    "pássaro multicolorido enorme toma seu lugar. O pássaro tem as estatísticas de um roca (veja no "
                    "Manual dos Monstros), mas ele obedece seus comandos simples e não pode atacar. Ele pode carregar "
                    "até 250 quilos enquanto estiver voando com seu deslocamento máximo, ou 500 quilos com metade do "
                    "deslocamento. O pássaro desaparece após voar a distância máxima para um dia ou se cair a 0 pontos "
                    "de vida. Você pode dispensar o pássaro com uma ação."
                ),
            },
        ],
        ("Pergaminho de Proteção", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": (
                    "Cada pergaminho de proteção funciona contra um tipo específico de criatura, escolhido pelo Mestre "
                    "ou determinado aleatoriamente ao rolar na tabela a seguir."
                ),
            },
            {
                "type": "table",
                "headers": ["d100", "Tipo de Criatura"],
                "rows": [
                    ["01-10", "Aberrações"],
                    ["11-20", "Bestas"],
                    ["21-30", "Celestiais"],
                    ["31-40", "Elementais"],
                    ["41-50", "Fadas"],
                    ["51-75", "Corruptores"],
                    ["76-80", "Plantas"],
                    ["81-00", "Mortos-vivos"],
                ],
            },
            {
                "type": "paragraph",
                "text": (
                    "Usar uma ação para ler o pergaminho enclausura você em uma barreira invisível que se estende de "
                    "você num cilindro de 1,5 metro de raio e 3 metros de altura. Por 5 minutos, esta barreira previne "
                    "criaturas do tipo especificado de entrarem ou afetarem qualquer coisa dentro do cilindro."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "O cilindro se move com você e permanece centrado em você. Porém, caso você se mova de forma que "
                    "uma criatura do tipo especificado entre no cilindro, o efeito termina."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Uma criatura pode tentar sobrepujar a barreira usando uma ação para realizar um teste de Carisma "
                    "CD 15. Com um sucesso, a criatura deixa de ser afetada pela barreira."
                ),
            },
        ],
        ("Tapete Voador", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": (
                    "Você pode falar a palavra de comando do tapete, com uma ação, para fazê-lo flutuar e voar. Ele se "
                    "move na direção falada, considerando que você esteja a até 9 metros dele."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Existem quatro tamanhos de tapete voador. O Mestre escolhe o tamanho do tapete ou o determina "
                    "aleatoriamente."
                ),
            },
            {
                "type": "table",
                "headers": ["d100", "Tamanho", "Capacidade", "Deslocamento de Voo"],
                "rows": [
                    ["01-20", "1 m x 1,5 m", "100 kg", "21 m"],
                    ["21-55", "1,2 m x 1,8 m", "200 kg", "18 m"],
                    ["56-80", "1,5 m x 2 m", "300 kg", "12 m"],
                    ["81-100", "1,8 m x 2,8 m", "400 kg", "9 m"],
                ],
            },
            {
                "type": "paragraph",
                "text": (
                    "O tapete pode carregar até o dobro do peso mostrado na tabela, mas seu deslocamento de voo é "
                    "reduzido à metade se ele estiver carregando mais que a capacidade normal."
                ),
            },
        ],
        ("Trombeta do Valhalla", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": (
                    "Você pode usar uma ação para soprar esta trombeta. Em resposta, guerreiros espirituais do plano de "
                    "Ysgard aparecem a até 18 metros de você. Esses espíritos usam as estatísticas do furioso do Manual "
                    "dos Monstros. Eles voltam para Ysgard após 1 hora ou quando caírem para 0 pontos de vida. Uma vez "
                    "que você tenha usado a trombeta, ela não poderá ser usada novamente até que 7 dias se passem."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Se têm conhecimento da existência de quatro tipos de trombetas do Valhalla, cada uma feita de um "
                    "metal diferente. O tipo da trombeta determinar quantos furiosos respondem ao chamado, assim como o "
                    "requerimento para seu uso. O Mestre escolhe o tipo da trombeta ou o determina aleatoriamente."
                ),
            },
            {
                "type": "table",
                "headers": ["d100", "Tipo de Trombeta", "Furiosos Invocados", "Requerimento"],
                "rows": [
                    ["01-40", "Prata", "2d4 + 2", "Nenhum"],
                    ["41-75", "Latão", "3d4 + 3", "Proficiência com todas as armas simples"],
                    ["76-90", "Bronze", "4d4 + 4", "Proficiência com todas as armaduras médias"],
                    ["91-00", "Ferro", "5d4 + 5", "Proficiência com todas as armas marciais"],
                ],
            },
            {
                "type": "paragraph",
                "text": (
                    "Se você soprar a trombeta sem atender o requerimento, os furiosos invocados atacarão você. Se você "
                    "atender o requerimento, eles serão amigáveis a você e aos seus companheiros e seguirão seus comandos."
                ),
            },
        ],
        ("Lâmina da Lua", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": (
                    "De todos os itens mágicos criados pelos elfos, um dos mais desejados e zelosamente guardados é a "
                    "lâmina da lua. Em tempos antigos, praticamente todas as casas nobres élficas reivindicavam tal "
                    "lâmina. Com o passar dos séculos, algumas lâminas desapareceram do mundo, sua mágica se perdeu "
                    "quando linhagens familiares se extinguiram. Outras lâminas sumiram com seus portadores durante "
                    "grandes missões. Então, apenas algumas dessas armas restaram."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Uma lâmina da lua passa de pai para filho. A espada escolhe seu portador e permanece vinculada a "
                    "essa pessoa pelo resto da vida. Se o portador morrer, outro herdeiro pode reivindicar a lâmina. Se "
                    "nenhum herdeiro digno existir, a espada permanecerá dormente. Ela funciona como uma espada longa "
                    "normal até uma alma digna encontra-la e reivindicar seu poder."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Uma lâmina da lua serve apenas um mestre por vez. O processo de sintonização requer um ritual "
                    "especial na sala do trono de um regente élfico ou em um templo dedicado aos deuses élficos."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Uma lâmina da lua não servirá a ninguém que ela considere covarde, errático, corrupto ou que não "
                    "concorde em preservar e proteger os elfos. Se a lâmina rejeitar você, você realiza testes de "
                    "habilidade, jogadas de ataque e testes de resistência com desvantagem por 24 horas. Se a lâmina te "
                    "aceitar, você se sintoniza com ela e uma nova runa aparece na lâmina. Você permanece sintonizado "
                    "com a arma até morrer ou a arma ser destruída."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Uma lâmina da lua tem uma runa em sua lâmina para cada mestre que ela serviu (geralmente 1d6 + 1). "
                    "A primeira runa sempre concede +1 de bônus nas jogadas de ataque e dano feitas com esta arma "
                    "mágica. Cada runa além da primeira concede à lâmina da lua uma propriedade adicional. O Mestre "
                    "escolhe cada propriedade ou as determina aleatoriamente na tabela Propriedades da Lâmina da Lua."
                ),
            },
            {
                "type": "table",
                "headers": ["d100", "Propriedade"],
                "rows": [
                    ["01-40", "Aumenta o bônus nas jogadas de ataque e dano em 1, até o máximo de +3. Role novamente se a lâmina da lua já tiver +3 de bônus."],
                    ["41-80", "A lâmina da lua ganha uma propriedade menor determinada aleatoriamente (veja Características Especiais previamente neste capítulo)."],
                    ["81-82", "A lâmina da lua ganha a propriedade acuidade."],
                    ["83-84", "A lâmina da lua ganha a propriedade arremesso (distância 6/18 metros)."],
                    ["85-86", "A lâmina da lua funciona como uma defensora."],
                    ["87-90", "A lâmina da lua atinge um acerto crítico numa rolagem 19 ou 20."],
                    ["91-92", "Quando você atingir um ataque usando a lâmina da lua, o ataque causa 1d6 de dano cortante extra."],
                    ["93-94", "Quando você atingir uma criatura de um tipo específico, o alvo sofre 1d6 de dano extra de ácido, frio, fogo, elétrico ou trovejante."],
                    ["95-96", "Você pode usar uma ação bônus para fazer a lâmina da lua liberar um clarão luminoso. Cada criatura que puder ver você e estiver a até 9 metros de você deve ser bem sucedida num teste de resistência de Constituição CD 15 ou ficará cega por 1 minuto."],
                    ["97-98", "A lâmina da lua funciona como um anel de armazenar magia."],
                    ["99", "Você pode usar uma ação para convocar uma sombra élfica, considerando que você já não tenha uma servindo você."],
                    ["00", "A lâmina da lua funciona como uma espada vorpal."],
                ],
            },
            {
                "type": "paragraph",
                "text": (
                    "Consciência. Uma lâmina da lua é uma arma consciente neutra e boa com Inteligência 12, Sabedoria 10 "
                    "e Carisma 12. Ela tem audição e visão no escuro com alcance de 36 metros."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "A arma se comunica ao transmitir suas emoções, enviando uma sensação de formigamento pela mão do "
                    "portador quando deseja comunicar algo que ela sentiu. Ela pode se comunicar mais explicitamente "
                    "através de visões e sonhos, quando o portador está ou em transe ou dormindo."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Personalidade. Cada lâmina da lua busca o avanço da raça élfica e dos ideias élficos. Coragem, "
                    "lealdade, beleza, música e vida são todos parte deste propósito."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "A arma é vinculada a linhagem familiar a qual ela era destinada a servir. Enquanto ela estiver "
                    "vinculada com um dono que partilhe dos seus ideias, sua lealdade será absoluta."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Se a lâmina da lua tiver um defeito, é o excesso de confiança. Uma vez que tenha decidido por um "
                    "dono, ela acredita que apenas essa pessoa deveria empunha-la, mesmo que esse dono não anseie pelos "
                    "ideias élficos."
                ),
            },
        ],
        ("Frasco de Ferro", DMG_SOURCE): [
            {
                "type": "paragraph",
                "text": (
                    "Esta garrafa de ferro possui uma rolha de latão. Você pode usar uma ação para falar a palavra de "
                    "comando do frasco, focando uma criatura que você possa ver, a até 18 metros de você. Se o alvo for "
                    "nativo de um plano de existência diferente do que você está, o alvo deve ser bem sucedido num teste "
                    "de resistência de Sabedoria CD 17 ou será aprisionado no frasco. Se o alvo já tiver sido aprisionado "
                    "pelo frasco antes, ele terá desvantagem no teste de resistência. Uma vez presa, uma criatura "
                    "permanece no frasco até ser libertada. O frasco pode conter apenas uma criatura por vez. Uma criatura "
                    "presa no frasco não precisa respirar, comer ou beber e não envelhece."
                ),
            },
            {
                "type": "paragraph",
                "text": (
                    "Você pode usar uma ação para remover a rolha do frasco e libertar a criatura contida nele. A criatura "
                    "é amigável a você e aos seus companheiros por 1 hora e obedece os seus comando por essa duração. Se "
                    "você não der nenhum comando ou der um comando que resulte em sua morte, ela se defenderá, mas não "
                    "fará mais nada. No final da duração, a criatura agirá de acordo com sua disposição e tendência normais."
                ),
            },
            {
                "type": "table",
                "headers": ["d100", "Conteúdo"],
                "rows": [
                    ["01-50", "Vazio"],
                    ["51", "Arcanaloth"],
                    ["52", "Cambion"],
                    ["53-54", "Dao"],
                    ["55-57", "Demônio (tipo 1)"],
                    ["58-60", "Demônio (tipo 2)"],
                    ["61-62", "Demônio (tipo 3)"],
                    ["63-64", "Demônio (tipo 4)"],
                    ["65", "Demônio (tipo 5)"],
                    ["66", "Demônio (tipo 6)"],
                    ["67", "Deva"],
                    ["68-69", "Diabo (maior)"],
                    ["70-72", "Diabo (menor)"],
                    ["73-74", "Djinni"],
                    ["75-76", "Efreeti"],
                    ["77-78", "Elemental (qualquer)"],
                    ["79", "Cavaleiro githyanki"],
                    ["80", "Zerth githzerai"],
                    ["81", "Caçador invisível"],
                    ["82", "Marid"],
                    ["83-84", "Mezzoloth"],
                    ["85-86", "Bruxa da noite"],
                    ["87-88", "Nycaloth"],
                    ["89-90", "Planetário"],
                    ["91", "Salamandra"],
                    ["92-93", "Slaad (qualquer)"],
                    ["94", "Solar"],
                    ["95", "Súcubo/íncubo"],
                    ["96", "Ultroloth"],
                    ["97-00", "Xorn"],
                ],
            },
            {
                "type": "paragraph",
                "text": (
                    "Uma magia identificação revela que uma criatura está dentro do frasco, mas a única forma de "
                    "determinar o tipo da criatura é abrindo o frasco. Uma garrafa descoberta recentemente poderia já "
                    "possuir uma criatura, à escolha do Mestre ou determinada aleatoriamente."
                ),
            },
        ],
    }
    for item in items:
        original_description = item.get("descricao") or ""
        blocks = fixed_blocks.get((item.get("nome"), item.get("fonte")))
        if blocks:
            if item.get("nome") == "Baralho das Surpresas":
                extra_blocks: list[dict[str, Any]] = []
                draw_start = original_description.find("Antes de você")
                table_start = original_description.find("BARALHO DAS SURPRESAS", draw_start)
                bufao_start = original_description.find("Bufão.", table_start)
                if draw_start != -1 and table_start != -1:
                    draw_text = original_description[draw_start:table_start].strip()
                    asparcas_start = draw_text.find("As parcas.")
                    if asparcas_start != -1:
                        extra_blocks.append({"type": "paragraph", "text": clean(draw_text[:asparcas_start]) or ""})
                        extra_blocks.extend(split_effect_paragraphs(draw_text[asparcas_start:]))
                    else:
                        extra_blocks.append({"type": "paragraph", "text": draw_text})
                if bufao_start != -1:
                    extra_blocks.extend(split_effect_paragraphs(original_description[bufao_start:]))
                blocks = blocks + [block for block in extra_blocks if block.get("text")]
            set_blocks(item, blocks)
        structure_retributive_strike_table(item)


def dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: Counter[str] = Counter()
    for item in items:
        base = item["id"]
        seen[base] += 1
        if seen[base] > 1:
            item["id"] = f"{base}-{seen[base]}"
    return items


def build_data(docling_dir: Path) -> dict[str, Any]:
    items: list[dict[str, Any]] = []

    phb, phb_first, _ = load_docling(docling_dir, "phb_equipment")
    phb_printed = printed_pages(phb, "phb_equipment", phb_first)
    phb_items = parse_phb_tables(phb, phb_first, phb_printed)
    enrich_phb_descriptions(phb, phb_items)
    items.extend(phb_items)

    for key in ("dmg_magic_az", "dmg_artifacts", "xge_common_magic"):
        data, first_pdf_page, source = load_docling(docling_dir, key)
        printed = printed_pages(data, key, first_pdf_page)
        items.extend(
            parse_magic_items(
                data,
                key=key,
                source=source,
                first_pdf_page=first_pdf_page,
                printed_by_rel=printed,
            )
        )

    apply_structured_item_fixes(items)
    enrich_class_usability(items)
    items = dedupe([item for item in items if item.get("nome")])
    return {
        "extraction": {
            "method": "docling",
            "note": "Extração baseada em PDFs recortados por seção, com OCR desligado e batch de 1 página para evitar std::bad_alloc em PDFs completos.",
            "docling_dir": str(docling_dir),
        },
        "counts": {
            "total": len(items),
            "by_category": dict(Counter(item["categoria"] for item in items)),
            "by_source": dict(Counter(item["fonte"] for item in items)),
        },
        "items": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docling-dir", type=Path, default=DEFAULT_DOCLING_DIR)
    parser.add_argument("--raw-out", type=Path, default=ROOT / "arsenal_raw.json")
    parser.add_argument("--out", type=Path, default=ROOT / "arsenal.json")
    args = parser.parse_args()

    data = build_data(args.docling_dir)
    args.raw_out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    args.out.write_text(json.dumps(data["items"], ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(data["counts"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
