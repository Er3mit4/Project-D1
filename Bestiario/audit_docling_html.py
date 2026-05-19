#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
DEFAULT_HTML_DIR = ROOT / "docling_html_out"
DEFAULT_JSON = ROOT / "monstros.json"

MONSTER_TYPES = (
    "Aberração",
    "Aberracao",
    "Besta",
    "Celestial",
    "Constructo",
    "Construto",
    "Corruptor",
    "Dragão",
    "Dragao",
    "Elemental",
    "Fada",
    "Feérico",
    "Feerico",
    "Gigante",
    "Humanoide",
    "Limo",
    "Monstruosidade",
    "Morto-vivo",
    "Mortovivo",
    "Planta",
)
SIZES = (
    "Miúdo",
    "Miudo",
    "Pequeno",
    "Médio",
    "Medio",
    "Grande",
    "Enorme",
    "Imenso",
)
SMALL_WORDS = {"a", "as", "da", "das", "de", "do", "dos", "e", "em", "no", "nos", "na", "nas", "o", "os"}

STATBLOCK_RE = re.compile(
    rf"(?P<name>[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9][A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9 '\-–]+?)\s+"
    rf"(?P<type>{'|'.join(MONSTER_TYPES)})\s+"
    rf"(?P<size>{'|'.join(SIZES)})\b"
    r"(?:\s*\([^)]*\))?\s*,",
    flags=re.IGNORECASE,
)


def title_pt(value: str) -> str:
    words = re.sub(r"\s+", " ", value.replace("–", "-")).strip().split(" ")
    titled: list[str] = []
    for index, word in enumerate(words):
        if not word:
            continue
        lower = word.lower()
        if index > 0 and lower in SMALL_WORDS:
            titled.append(lower)
        elif "-" in word:
            titled.append("-".join(piece.capitalize() for piece in lower.split("-")))
        else:
            titled.append(lower.capitalize())
    return " ".join(titled)


def normalize_name(value: str) -> str:
    value = re.sub(r"\s*-\s*", "-", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value.casefold()


class DoclingHtmlTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._capture_depth = 0
        self._skip_depth = 0
        self._chunks: list[str] = []
        self.items: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "figure":
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in {"h1", "h2", "h3", "p", "td", "th"}:
            self._capture_depth += 1
            self._chunks = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "figure" and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag in {"h1", "h2", "h3", "p", "td", "th"} and self._capture_depth:
            text = re.sub(r"\s+", " ", " ".join(self._chunks)).strip()
            if text:
                self.items.append(text)
            self._capture_depth -= 1
            self._chunks = []

    def handle_data(self, data: str) -> None:
        if self._capture_depth and not self._skip_depth:
            self._chunks.append(data)


def extract_statblock_names_from_html(path: Path) -> list[str]:
    parser = DoclingHtmlTextParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))

    names: list[str] = []
    seen: set[str] = set()
    for item in parser.items:
        for match in STATBLOCK_RE.finditer(item):
            name = title_pt(match.group("name"))
            key = normalize_name(name)
            if key not in seen:
                names.append(name)
                seen.add(key)
    return names


def load_json_names(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {normalize_name(monster.get("nome", "")) for monster in data if monster.get("nome")}


def audit_html_against_json(html_dir: Path, json_path: Path) -> dict[str, list[str]]:
    json_names = load_json_names(json_path)
    found: dict[str, str] = {}
    for html_path in sorted(html_dir.rglob("*.html")):
        for name in extract_statblock_names_from_html(html_path):
            found.setdefault(normalize_name(name), name)

    missing = [name for key, name in found.items() if key not in json_names]
    return {
        "html_statblocks": sorted(found.values()),
        "missing_in_json": sorted(missing),
    }


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compara blocos de estatistica detectados no HTML do Docling com monstros.json.",
    )
    parser.add_argument("--html-dir", type=Path, default=DEFAULT_HTML_DIR)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    return parser.parse_args(list(argv))


def main() -> int:
    args = parse_args(sys.argv[1:])
    if not args.html_dir.exists():
        print(f"Diretorio HTML nao encontrado: {args.html_dir}", file=sys.stderr)
        return 1
    if not args.json.exists():
        print(f"JSON nao encontrado: {args.json}", file=sys.stderr)
        return 1

    result = audit_html_against_json(args.html_dir, args.json)
    print(f"Statblocks no HTML: {len(result['html_statblocks'])}")
    print(f"Ausentes no JSON: {len(result['missing_in_json'])}")
    for name in result["missing_in_json"]:
        print(f"- {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
