#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "arsenal.json"
TEMPLATE = ROOT / "template.html"
OUTPUT = ROOT / "index.html"


def main() -> int:
    items = json.loads(DATA.read_text(encoding="utf-8"))
    template = TEMPLATE.read_text(encoding="utf-8")
    payload = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    html = template.replace("__ARSENAL_DATA__", payload)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Gerado {OUTPUT} com {len(items)} itens.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
