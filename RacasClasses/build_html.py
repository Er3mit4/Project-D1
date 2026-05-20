#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "racas_classes.json"
TEMPLATE = ROOT / "template.html"
OUTPUT = ROOT / "index.html"


def main() -> int:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    template = TEMPLATE.read_text(encoding="utf-8")
    html = template.replace("__RACAS_CLASSES_DATA__", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Gerado {OUTPUT} com {len(payload.get('items', []))} registros.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
