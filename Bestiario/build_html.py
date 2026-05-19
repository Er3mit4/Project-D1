#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "monstros.json"
TEMPLATE = ROOT / "template.html"
OUTPUT = ROOT / "index.html"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)

    items = json.loads(args.data.read_text(encoding="utf-8"))
    template = args.template.read_text(encoding="utf-8")
    payload = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    html = template.replace("__MONSTERS_DATA__", payload)
    args.output.write_text(html, encoding="utf-8")
    print(f"Gerado {args.output} com {len(items)} monstros.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
