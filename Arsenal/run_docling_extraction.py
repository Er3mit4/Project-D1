#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from prepare_docling_sources import DOC_OUT, ROOT, SLICES, write_slice


PROJECT_ROOT = ROOT.parent
DOCLING = PROJECT_ROOT / ".venv" / "Scripts" / "docling.exe"


def run_docling(source: Path, output_dir: Path, *, tables: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        str(DOCLING),
        str(source),
        "--output",
        str(output_dir),
        "--to",
        "json",
        "--no-ocr",
        "--page-batch-size",
        "1",
        "--num-threads",
        "1",
        "--pdf-backend",
        "pypdfium2",
        "-v",
    ]
    if not tables:
        command.insert(6, "--no-tables")
    else:
        command.extend(["--table-mode", "accurate"])
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main() -> int:
    if not DOCLING.exists():
        print(f"Docling nao encontrado em {DOCLING}. Crie/atualize o venv raiz do Projeto D1.", file=sys.stderr)
        return 1

    sources_dir = DOC_OUT / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)
    for spec in SLICES:
        write_slice(spec, sources_dir)

    jobs = (
        ("phb_equipment_p145_161.pdf", "phb_equipment", True),
        ("dmg_treasure_p134_150.pdf", "dmg_treasure", False),
        ("dmg_magic_az_p151_220.pdf", "dmg_magic_az", False),
        ("dmg_artifacts_p221_229.pdf", "dmg_artifacts", False),
        ("xge_common_magic_p136_139.pdf", "xge_common_magic", False),
    )

    for filename, output_name, tables in jobs:
        run_docling(sources_dir / filename, DOC_OUT / output_name, tables=tables)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
