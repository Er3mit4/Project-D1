#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DOC_OUT = ROOT / "docling_out"
PROJECT_ROOT = ROOT.parent
DOCLING = PROJECT_ROOT / ".venv" / "Scripts" / "docling.exe"
HTML_OUT = ROOT / "docling_html_out"


def build_docling_command(
    source: Path,
    output_dir: Path,
    *,
    output_format: str,
    tables: bool,
) -> list[str]:
    command = [
        str(DOCLING),
        str(source),
        "--output",
        str(output_dir),
        "--to",
        output_format,
        "--no-ocr",
        "--page-batch-size",
        "1",
        "--num-threads",
        "1",
        "--pdf-backend",
        "pypdfium2",
        "-v",
    ]
    if output_format == "html":
        command.extend(["--image-export-mode", "placeholder"])
    if tables:
        command.extend(["--table-mode", "accurate"])
    else:
        command.extend(["--no-tables"])
    return command


def run_docling(source: Path, output_dir: Path, *, output_format: str, tables: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = build_docling_command(
        source,
        output_dir,
        output_format=output_format,
        tables=tables,
    )
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


JOBS = (
    ("mm_intro_p5_11.pdf", "mm_intro", False),
    ("mm_monsters_a_b_p12_34.pdf", "mm_monsters_a_b", True),
    ("mm_monsters_c_e_p35_64.pdf", "mm_monsters_c_e", True),
    ("mm_monsters_d_p65_84.pdf", "mm_monsters_d", True),
    ("mm_monsters_dragon1_p85_105.pdf", "mm_monsters_dragon1", True),
    ("mm_monsters_dragon2_p106_125.pdf", "mm_monsters_dragon2", True),
    ("mm_monsters_e_h_p126_160.pdf", "mm_monsters_e_h", True),
    ("mm_monsters_h_m_p161_195.pdf", "mm_monsters_h_m", True),
    ("mm_monsters_m_p_p196_235.pdf", "mm_monsters_m_p", True),
    ("mm_monsters_p_s_p236_270.pdf", "mm_monsters_p_s", True),
    ("mm_monsters_s_z_p271_315.pdf", "mm_monsters_s_z", True),
    ("mm_appendix_a_p317_340.pdf", "mm_appendix_a", True),
    ("mm_appendix_b_p341_349.pdf", "mm_appendix_b", True),
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrai os chunks do Manual dos Monstros com Docling.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "html", "both"),
        default="both",
        help="Formato de saida. Padrao: both.",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help=(
            "Limita a extracao a um output_name especifico, ex: mm_monsters_s_z. "
            "Pode ser usado mais de uma vez."
        ),
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])
    if not DOCLING.exists():
        print(f"Docling nao encontrado em {DOCLING}.", file=sys.stderr)
        return 1

    from prepare_docling_sources import SLICES, write_slice

    sources_dir = DOC_OUT / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)
    for spec in SLICES:
        write_slice(spec, sources_dir)

    only = set(args.only)
    for filename, output_name, tables in JOBS:
        if only and output_name not in only:
            continue

        print(f"\n{'='*60}")
        print(f"Processando: {filename} -> {output_name} ({args.format})")
        print(f"{'='*60}")

        source = sources_dir / filename
        if args.format in {"json", "both"}:
            print(f"\nJSON: {source.name}")
            run_docling(
                source,
                DOC_OUT / output_name,
                output_format="json",
                tables=tables,
            )
        if args.format in {"html", "both"}:
            print(f"\nHTML: {source.name}")
            run_docling(
                source,
                HTML_OUT / output_name,
                output_format="html",
                tables=tables,
            )

    print("\nConcluido!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
