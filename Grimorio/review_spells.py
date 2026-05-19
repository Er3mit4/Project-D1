#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MIRROR = ROOT / "grimoire-dd5e-gh-pages"
TARGET_DIRS = [ROOT] + ([MIRROR] if MIRROR.exists() else [])


def load_raw_names() -> set[str]:
    raw_path = ROOT / "spells_raw.json"
    if not raw_path.exists():
        return set()

    data = json.loads(raw_path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("magias"), list):
        return {spell.get("nome", "") for spell in data["magias"] if spell.get("nome")}
    return set()


def load_spells(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Esperado um array em {path.name}, mas veio {type(data).__name__}")
    return data


def strip_trailing_page_markers(text: str) -> str:
    lines = text.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and re.fullmatch(r"\d{2,4}", lines[-1].strip()):
        lines.pop()
        while lines and not lines[-1].strip():
            lines.pop()
    return "\n".join(lines).rstrip()


def clean_spell(spell: dict) -> tuple[dict, list[str]]:
    updated = copy.deepcopy(spell)
    notes: list[str] = []
    name = updated["name"]

    fixes = {
        "BRAÇOS DE HADAR": {
            "range": "Pessoal (3 metros de raio)",
        },
        "ESPIRRO ÁCIDO": {
            "range": "18 metros",
        },
        "REFLEXOS": {
            "range": "Pessoal",
        },
    }

    if name in fixes:
        for field, value in fixes[name].items():
            if updated.get(field) != value:
                notes.append(f"{field}: {updated.get(field)!r} -> {value!r}")
                updated[field] = value
            else:
                notes.append(f"{field}: normalizado")

    prefix_fixes = {
        "CORDÃO DE FLECHAS": ": 8 horas\n\nDuração\n\n",
        "PROTEÇÃO CONTRA O BEM E MAL": ": Concentração, até 10 minutos\n\nDuração\n\n",
    }
    prefix = prefix_fixes.get(name)
    if prefix and updated["description"].startswith(prefix):
        updated["description"] = updated["description"][len(prefix):]
        notes.append("description: removido cabeçalho vazado no início")
    elif prefix:
        notes.append("description: cabeçalho inicial já normalizado")

    trailing_page_names = {
        "ILUSÃO PROGRAMADA",
        "MURALHA DE GELO",
        "OLHO ARCANO",
        "RAJADA PRISMÁTICA",
        "TELEPATIA",
    }
    if name in trailing_page_names:
        cleaned = strip_trailing_page_markers(updated["description"])
        if cleaned != updated["description"]:
            updated["description"] = cleaned
            notes.append("description: removido número de página final")
        else:
            notes.append("description: página final já normalizada")

    if name == "MURALHA DE GELO":
        if "\n\n262\n\nR\n\n" in updated["description"]:
            updated["description"] = updated["description"].replace("\n\n262\n\nR\n\n", "\n\n")
            notes.append("description: removido rodapé de paginação intermediário")
        else:
            notes.append("description: rodapé intermediário já normalizado")

    return updated, notes


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    raw_names = load_raw_names()
    canonical = load_spells(ROOT / "spells.json")

    reviewed: list[dict] = []
    corrections: list[dict] = []
    for spell in canonical:
        cleaned, notes = clean_spell(spell)
        reviewed.append(cleaned)
        if notes:
            corrections.append({
                "name": cleaned["name"],
                "notes": notes,
            })

    final_names = {spell["name"] for spell in canonical}
    review_audit = {
        "source_raw_count": len(raw_names),
        "final_count": len(canonical),
        "reviewed_count": len(reviewed),
        "final_only_names": sorted(final_names - raw_names),
        "raw_only_names": sorted(raw_names - final_names),
        "corrections": corrections,
    }

    for target_dir in TARGET_DIRS:
        write_json(target_dir / "spells_reviewed.json", reviewed)
        write_json(target_dir / "spells.json", reviewed)
        write_json(target_dir / "review_audit.json", review_audit)
        subprocess.run(["python", "build_html.py"], cwd=target_dir, check=True)

    print(f"OK Revisão concluída em {len(TARGET_DIRS)} diretório(s)")
    print(f"   Magias revisadas: {len(reviewed)}")
    print(f"   Correções aplicadas: {len(corrections)}")


if __name__ == "__main__":
    main()
