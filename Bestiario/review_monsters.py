#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RAW_PATH = ROOT / "monstros_raw.json"
REVIEWED_PATH = ROOT / "monstros_reviewed.json"
AUDIT_PATH = ROOT / "review_audit.json"

STAT_LABEL_TO_FIELD = {
    "Testes de Resistência": "testes_resistencia",
    "Perícias": "pericias",
    "Resistência a Dano": "resistencia_dano",
    "Imunidade a Dano": "imunidade_dano",
    "Imunidade a Condição": "imunidade_condicao",
    "Sentidos": "sentidos",
    "Idiomas": "idiomas",
}

FIELD_TO_LABEL = {field: label for label, field in STAT_LABEL_TO_FIELD.items()}
STAT_FIELDS = tuple(FIELD_TO_LABEL)
LABEL_PATTERN = "|".join(re.escape(label) for label in STAT_LABEL_TO_FIELD)
LABEL_RE = re.compile(rf"\b({LABEL_PATTERN}|Nível de Desafio)\b", re.IGNORECASE)
ND_RE = re.compile(
    r"Nível de Desafio\s+(\d+(?:/\d+)?)\s*\(?\s*([\d\s.,]*)\s*XP\)?",
    re.IGNORECASE,
)
STATBLOCK_LEAK_RE = re.compile(
    r"\b(Classe de Armadura|Pontos de Vida|Nível de Desafio|FOR\s+DES\s+CON)\b",
)
DESCRIPTION_LABEL_LEAK_RE = re.compile(
    r"\b(?:Sentidos\s+(?:visão|percepção|sentido)|Idiomas\s+(?:-|[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ])|Perícias\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ])",
    re.IGNORECASE,
)
ACTION_RE = re.compile(
    r"\b(Ataque Corpo-a-Corpo|Ataque à Distância|Acerto:|Recarrega|Ataques Múltiplos)\b",
    re.IGNORECASE,
)
TRAIT_TITLE_RE = re.compile(r"^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^.!?]{1,80}\.\s+")
ACTION_TITLE_RE = re.compile(
    r"^(?:Presença Aterradora|Sopro [A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^.]*|Ataques Múltiplos|Mordida|Garras?|Cauda|Bicada|Garra|Raio|Engolir)\.",
    re.IGNORECASE,
)
ACTION_TITLE_ANY_RE = re.compile(
    r"\b(?:Presença Aterradora|Sopro [A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^.]*|Ataques Múltiplos|Mordida|Garras?|Cauda|Bicada|Garra|Raio|Engolir)\.",
    re.IGNORECASE,
)
MECHANICAL_TITLE_ANY_RE = re.compile(
    r"\b[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][A-Za-zÁÀÂÃÉÊÍÓÔÕÚÇáàâãéêíóôõúç0-9()/-]*(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][A-Za-zÁÀÂÃÉÊÍÓÔÕÚÇáàâãéêíóôõúç0-9()/-]*){0,3}\."
)
MECHANICAL_MARKER_RE = re.compile(
    r"\b(teste de resistência|CD\s+\d+|dano|ação|ações|ataque|magicamente|pontos de vida|Recarrega)\b",
    re.IGNORECASE,
)


def clean(text: str | None) -> str | None:
    if text is None:
        return None
    value = re.sub(r"\s+", " ", str(text)).strip()
    value = re.sub(r"\s+([,.!?;:])", r"\1", value)
    if re.fullmatch(r"[,.!?;:]+", value):
        return None
    return value or None


def parse_labeled_segments(text: str) -> dict[str, str]:
    matches = list(LABEL_RE.finditer(text))
    if not matches:
        return {}

    segments: dict[str, str] = {}
    for index, match in enumerate(matches):
        label = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        value = clean(text[start:end]) or ""
        if not value:
            continue
        canonical = next(
            (known for known in [*STAT_LABEL_TO_FIELD, "Nível de Desafio"] if known.lower() == label.lower()),
            label,
        )
        segments[canonical] = value
    return segments


def split_compound_field(monster: dict[str, Any], field: str) -> None:
    value = clean(monster.get(field))
    if not value or not LABEL_RE.search(value):
        return

    label = FIELD_TO_LABEL[field]
    synthetic = f"{label} {value}"
    segments = parse_labeled_segments(synthetic)
    for segment_label, segment_value in segments.items():
        if segment_label == "Nível de Desafio":
            nd_match = ND_RE.search(f"Nível de Desafio {segment_value}")
            if nd_match:
                monster["nd"] = clean(nd_match.group(1))
                monster["xp"] = clean(nd_match.group(2).replace(" ", "").replace(",", ".").rstrip("."))
            continue
        target = STAT_LABEL_TO_FIELD[segment_label]
        monster[target] = clean(segment_value)


def merge_stat_value(monster: dict[str, Any], field: str, value: str) -> None:
    cleaned = clean(value)
    if not cleaned:
        return
    existing = clean(monster.get(field))
    if existing:
        existing = existing.rstrip(" ,;")
    if existing and cleaned not in existing:
        monster[field] = clean(f"{existing}, {cleaned}")
    else:
        monster[field] = cleaned


def split_description_trailing_stats(monster: dict[str, Any]) -> None:
    description = clean(monster.get("descricao")) or ""
    match = DESCRIPTION_LABEL_LEAK_RE.search(description)
    if not match:
        return
    tail_start = description.rfind(". ", 0, match.start())
    if tail_start < 0:
        return
    prefix = clean(description[: tail_start + 1]) or ""
    tail = clean(description[tail_start + 2 :]) or ""
    synthetic = tail
    if not LABEL_RE.match(synthetic) and monster.get("imunidade_condicao"):
        synthetic = f"Imunidade a Condição {synthetic}"
    segments = parse_labeled_segments(synthetic)
    if not segments:
        return
    for segment_label, segment_value in segments.items():
        if segment_label == "Nível de Desafio":
            continue
        merge_stat_value(monster, STAT_LABEL_TO_FIELD[segment_label], segment_value)
    monster["descricao"] = prefix


def repair_suspicious_description_fragments(monster: dict[str, Any]) -> None:
    description = clean(monster.get("descricao")) or ""
    if not description:
        return

    passive = re.match(r"^Percepção passiva\s+(\d+)\s*(.*)$", description)
    if passive:
        merge_stat_value(monster, "sentidos", f"Percepção passiva {passive.group(1)}")
        monster["descricao"] = clean(passive.group(2)) or ""
        description = monster["descricao"]

    if description.startswith("que compreendam") and monster.get("idiomas"):
        monster["idiomas"] = clean(f"{monster['idiomas']} {description}")
        monster["descricao"] = ""
        return

    if description.startswith("mágicos não"):
        condition_tail = clean(re.sub(r"^mágicos não\s*", "", description).rstrip("."))
        if condition_tail:
            merge_stat_value(monster, "imunidade_condicao", condition_tail)
        monster["descricao"] = ""
        return

    if description == "Absorção de" and monster.get("habilidades_especiais"):
        first_trait = clean(monster["habilidades_especiais"][0]) or ""
        if first_trait.startswith("Fogo."):
            monster["habilidades_especiais"][0] = clean(f"Absorção de {first_trait}")
            monster["descricao"] = ""
            return

    if description in {"Jato de"}:
        monster["descricao"] = ""
        return


def repair_split_description_after_classification(monster: dict[str, Any]) -> None:
    description = clean(monster.get("descricao")) or ""
    traits = monster.get("habilidades_especiais") or []

    if description == "Absorção de" and traits:
        first_trait = clean(traits[0]) or ""
        if first_trait.startswith("Fogo."):
            traits[0] = clean(f"Absorção de {first_trait}")
            monster["descricao"] = ""
            return

    if description == "Jato de" and traits:
        for index, trait in enumerate(traits):
            candidate = clean(trait) or ""
            if candidate.startswith("Água."):
                monster["acoes"] = [clean(f"Jato de {candidate}"), *(monster.get("acoes") or [])]
                monster["habilidades_especiais"] = [*traits[:index], *traits[index + 1 :]]
                monster["descricao"] = ""
                return

    legendary_prefix = "Resistência Lendária (3/"
    if description.endswith(legendary_prefix) and traits:
        first_trait = clean(traits[0]) or ""
        if first_trait.startswith("Dia)."):
            before = clean(description[: -len(legendary_prefix)]) or ""
            traits[0] = clean(f"Resistência Lendária (3/{first_trait}")
            if before:
                if before.startswith(("Anfíbio.", "Andar no Gelo.", "Resistência à Magia.")):
                    monster["habilidades_especiais"] = [before, *traits]
                    monster["descricao"] = ""
                else:
                    monster["descricao"] = before
            else:
                monster["descricao"] = ""
            return


def extract_statblock_prefix(text: str) -> tuple[str | None, str | None]:
    value = clean(text) or ""
    match = re.search(r"\bClasse de Armadura\b", value)
    if not match:
        return value or None, None
    before = clean(value[: match.start()])
    leaked = clean(value[match.start() :])
    return before, leaked


def looks_like_untitled_lore(text: str) -> bool:
    value = clean(text) or ""
    if not value:
        return False
    if TRAIT_TITLE_RE.match(value):
        return False
    if ACTION_RE.search(value):
        return False
    return bool(re.match(r"^(O|Os|A|As|Um|Uma|Em|No|Na|De|Apesar|Como)\b", value))


def split_titled_entries(text: str) -> list[str]:
    value = clean(text) or ""
    starts = [match.start() for match in ACTION_TITLE_ANY_RE.finditer(value)]
    if not starts or starts[0] != 0:
        return [value] if value else []
    entries: list[str] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(value)
        entry = clean(value[start:end])
        if entry:
            entries.append(entry)
    return entries


def split_description_mechanics(text: str) -> tuple[str, list[str], list[str]]:
    value = clean(text) or ""
    matches = list(MECHANICAL_TITLE_ANY_RE.finditer(value))
    if not matches:
        return value, [], []

    first_mechanical_index: int | None = None
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(value)
        entry = clean(value[match.start() : end]) or ""
        if ACTION_TITLE_RE.match(entry) or MECHANICAL_MARKER_RE.search(entry):
            first_mechanical_index = index
            break

    if first_mechanical_index is None:
        return value, [], []

    prefix = clean(value[: matches[first_mechanical_index].start()]) or ""
    traits: list[str] = []
    actions: list[str] = []
    for index in range(first_mechanical_index, len(matches)):
        start = matches[index].start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(value)
        entry = clean(value[start:end])
        if not entry:
            continue
        if ACTION_TITLE_RE.match(entry) or ACTION_RE.search(entry):
            actions.append(entry)
        elif MECHANICAL_MARKER_RE.search(entry):
            traits.append(entry)
    return prefix, traits, actions


def description_starts_with_action(text: str) -> bool:
    value = clean(text) or ""
    return bool(ACTION_TITLE_RE.match(value))


def is_section_intro(text: str) -> bool:
    value = clean(text) or ""
    return bool(
        re.match(
            r"^(?:O|A) .+ pode realizar \d+ ações lendárias\b|^Apenas uma ação lendária\b",
            value,
            re.IGNORECASE,
        )
    )


def looks_like_section_lore_leak(text: str) -> bool:
    value = clean(text) or ""
    if not value:
        return False
    if ACTION_RE.search(value) or TRAIT_TITLE_RE.match(value) or is_section_intro(value):
        return False
    return bool(re.match(r"^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+(?:\s|$)", value))


def looks_like_section_continuation(text: str) -> bool:
    value = clean(text) or ""
    return bool(
        re.match(
            r"^(?:[a-záàâãéêíóôõúç]+|Cada criatura|num teste|opções abaixo|e apenas|ações lendárias gastas|A até|Se tiver|Tais criaturas)\b",
            value,
        )
    )


def looks_like_header_leak(text: str) -> bool:
    value = clean(text) or ""
    return bool(value and value.upper() == value and "." not in value and len(value) < 80)


def description_has_statblock_leak(text: str) -> bool:
    value = clean(text) or ""
    if STATBLOCK_LEAK_RE.search(value) or DESCRIPTION_LABEL_LEAK_RE.search(value):
        return True
    if value.startswith("Percepção passiva") or value.endswith("/"):
        return True
    if value in {"que compreendam Abissal)", "mágicos não impedido, inconsciente, paralisado, petrificado.", "Jato de", "Absorção de"}:
        return True
    return False


def rebuild_description_blocks(monster: dict[str, Any]) -> None:
    blocks: list[dict[str, str]] = []
    for text in monster.get("habilidades_especiais") or []:
        blocks.append({"type": "paragraph", "text": text})
    section_map = [
        ("AÇÕES", "acoes"),
        ("AÇÕES LENDÁRIAS", "acoes_lendarias"),
        ("REAÇÕES", "reacoes"),
        ("AÇÕES DE COVIL", "acoes_covil"),
        ("EFEITOS REGIONAIS", "efeitos_regionais"),
    ]
    for title, field in section_map:
        values = monster.get(field) or []
        if not values:
            continue
        blocks.append({"type": "paragraph", "text": title})
        blocks.extend({"type": "paragraph", "text": value} for value in values)
    monster["descricao_blocos"] = blocks


def review_monster(monster: dict[str, Any]) -> dict[str, Any]:
    reviewed = deepcopy(monster)

    for field in STAT_FIELDS:
        split_compound_field(reviewed, field)

    description, leaked_statblock = extract_statblock_prefix(reviewed.get("descricao") or "")
    reviewed["descricao"] = description or ""
    if leaked_statblock and not reviewed.get("ca"):
        reviewed["descricao"] = ""
    split_description_trailing_stats(reviewed)
    repair_suspicious_description_fragments(reviewed)

    description_prefix, description_traits, description_actions = split_description_mechanics(
        reviewed["descricao"]
    )
    if description_traits or description_actions:
        reviewed["descricao"] = description_prefix
        reviewed["habilidades_especiais"] = [
            *(reviewed.get("habilidades_especiais") or []),
            *description_traits,
        ]
        reviewed["acoes"] = [*description_actions, *(reviewed.get("acoes") or [])]
    elif description_starts_with_action(reviewed["descricao"]):
        reviewed["acoes"] = [*split_titled_entries(reviewed["descricao"]), *(reviewed.get("acoes") or [])]
        reviewed["descricao"] = ""

    lore_parts = [reviewed["descricao"]] if reviewed.get("descricao") else []
    traits: list[str] = []
    for trait in reviewed.get("habilidades_especiais") or []:
        text = clean(trait)
        if not text:
            continue
        if looks_like_untitled_lore(text):
            lore_parts.append(text)
        else:
            traits.append(text)
    reviewed["descricao"] = clean(" ".join(lore_parts)) or ""
    reviewed["habilidades_especiais"] = traits

    for field in ("acoes", "acoes_lendarias", "reacoes"):
        kept: list[str] = []
        for text in reviewed.get(field) or []:
            value = clean(text)
            if not value:
                continue
            if looks_like_header_leak(value):
                continue
            elif kept and looks_like_section_continuation(value):
                kept[-1] = clean(f"{kept[-1]} {value}")
            elif looks_like_section_lore_leak(value):
                lore_parts.append(value)
            else:
                kept.append(value)
        reviewed[field] = kept

    reviewed["descricao"] = clean(" ".join(lore_parts)) or ""
    repair_split_description_after_classification(reviewed)
    rebuild_description_blocks(reviewed)
    return reviewed


def audit_monsters(monsters: list[dict[str, Any]]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for monster in monsters:
        name = monster.get("nome", "")
        description = monster.get("descricao") or ""
        if description_has_statblock_leak(description):
            issues.append({"monster": name, "code": "description_statblock_leak", "field": "descricao"})

        for field in STAT_FIELDS:
            value = monster.get(field) or ""
            if LABEL_RE.search(value):
                issues.append({"monster": name, "code": "compound_field_leak", "field": field})

        for trait in monster.get("habilidades_especiais") or []:
            if looks_like_untitled_lore(trait):
                issues.append({"monster": name, "code": "probable_lore_in_traits", "field": "habilidades_especiais"})
                break

        for field in ("acoes", "acoes_lendarias", "reacoes", "acoes_covil"):
            for action in monster.get(field) or []:
                if not ACTION_RE.search(action) and not TRAIT_TITLE_RE.match(action) and not is_section_intro(action):
                    issues.append({"monster": name, "code": "suspicious_action", "field": field})
                    break
    return issues


def review_all(monsters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [review_monster(monster) for monster in monsters]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=RAW_PATH)
    parser.add_argument("--output", type=Path, default=REVIEWED_PATH)
    parser.add_argument("--audit-output", type=Path, default=AUDIT_PATH)
    parser.add_argument("--allow-issues", action="store_true")
    args = parser.parse_args(argv)

    monsters = json.loads(args.input.read_text(encoding="utf-8"))
    reviewed = review_all(monsters)
    issues = audit_monsters(reviewed)

    args.output.write_text(json.dumps(reviewed, ensure_ascii=False, indent=2), encoding="utf-8")
    args.audit_output.write_text(json.dumps(issues, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Revisados: {len(reviewed)} monstros em {args.output}")
    print(f"Questões de auditoria: {len(issues)} em {args.audit_output}")
    if issues and not args.allow_issues:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
