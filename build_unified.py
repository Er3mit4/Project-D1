#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "unified_template.html"
OUTPUT = ROOT / "index.html"


def read_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> int:
    payloads = {
        "__SPELLS_DATA__": read_json("Grimorio/spells.json"),
        "__ARSENAL_DATA__": read_json("Arsenal/arsenal.json"),
        "__MONSTERS_DATA__": read_json("Bestiario/monstros.json"),
    }
    html = TEMPLATE.read_text(encoding="utf-8")
    for marker, data in payloads.items():
        html = html.replace(marker, json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Gerado {OUTPUT} com {len(payloads['__SPELLS_DATA__'])} magias, {len(payloads['__ARSENAL_DATA__'])} itens e {len(payloads['__MONSTERS_DATA__'])} monstros.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
