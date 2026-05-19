#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parent
DOC_OUT = ROOT / "docling_out"

MM_PDF = Path(r"D:\Documents\Sessão RPG\D&D\old-dd-5e-manual-dos-monstros-biblioteca-elfica.pdf")


@dataclass(frozen=True)
class SliceSpec:
    source: Path
    output_name: str
    first_pdf_page: int
    last_pdf_page: int


SLICES = (
    SliceSpec(MM_PDF, "mm_intro_p5_11.pdf", 5, 11),
    SliceSpec(MM_PDF, "mm_monsters_a_b_p12_34.pdf", 12, 34),
    SliceSpec(MM_PDF, "mm_monsters_c_e_p35_64.pdf", 35, 64),
    SliceSpec(MM_PDF, "mm_monsters_d_p65_84.pdf", 65, 84),
    SliceSpec(MM_PDF, "mm_monsters_dragon1_p85_105.pdf", 85, 105),
    SliceSpec(MM_PDF, "mm_monsters_dragon2_p106_125.pdf", 106, 125),
    SliceSpec(MM_PDF, "mm_monsters_e_h_p126_160.pdf", 126, 160),
    SliceSpec(MM_PDF, "mm_monsters_h_m_p161_195.pdf", 161, 195),
    SliceSpec(MM_PDF, "mm_monsters_m_p_p196_235.pdf", 196, 235),
    SliceSpec(MM_PDF, "mm_monsters_p_s_p236_270.pdf", 236, 270),
    SliceSpec(MM_PDF, "mm_monsters_s_z_p271_315.pdf", 271, 315),
    SliceSpec(MM_PDF, "mm_appendix_a_p317_340.pdf", 317, 340),
    SliceSpec(MM_PDF, "mm_appendix_b_p341_349.pdf", 341, 349),
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
