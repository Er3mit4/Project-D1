#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parent
DOC_OUT = ROOT / "docling_out"

PHB_PDF = Path(r"D:\Documents\Sessão RPG\D&D\dd-5e-livro-do-jogador-fundo-branco-biblioteca-c3a9lfica.pdf")
DMG_PDF = Path(r"D:\Documents\Sessão RPG\D&D\dd-5e-guia-do-mestre-biblioteca-elfica.pdf")
XGE_PDF = Path(r"D:\Documents\Sessão RPG\D&D\dd-5e-guia-de-xanathar-para-todas-as-coisas-fundo-branco-biblioteca-elfica.pdf")


@dataclass(frozen=True)
class SliceSpec:
    source: Path
    output_name: str
    first_pdf_page: int
    last_pdf_page: int


SLICES = (
    SliceSpec(PHB_PDF, "phb_equipment_p145_161.pdf", 145, 161),
    SliceSpec(DMG_PDF, "dmg_treasure_p134_150.pdf", 134, 150),
    SliceSpec(DMG_PDF, "dmg_magic_az_p151_220.pdf", 151, 220),
    SliceSpec(DMG_PDF, "dmg_artifacts_p221_229.pdf", 221, 229),
    SliceSpec(XGE_PDF, "xge_common_magic_p136_139.pdf", 136, 139),
)


def write_slice(spec: SliceSpec, out_dir: Path) -> Path:
    if not spec.source.exists():
        raise FileNotFoundError(spec.source)

    out_path = out_dir / spec.output_name
    with fitz.open(spec.source) as src:
        page_count = src.page_count
        if spec.first_pdf_page < 1 or spec.last_pdf_page > page_count:
            raise ValueError(f"{spec.output_name}: intervalo fora do PDF com {page_count} paginas")

        with fitz.open() as dst:
            dst.insert_pdf(src, from_page=spec.first_pdf_page - 1, to_page=spec.last_pdf_page - 1)
            dst.save(out_path, garbage=4, deflate=True)
    return out_path


def main() -> int:
    out_dir = DOC_OUT / "sources"
    out_dir.mkdir(parents=True, exist_ok=True)

    for spec in SLICES:
        path = write_slice(spec, out_dir)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
