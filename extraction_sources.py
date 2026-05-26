#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Catálogo central das fontes de extração do Projeto D1.

A estratégia atual usa os PDFs textuais do pacote Internet Archive como fonte
principal e os arquivos DjVu/hOCR/page_numbers como apoio para layout,
paginação e conferência visual. Este módulo não extrai dados; ele apenas
padroniza caminhos e nomes para os scripts de manutenção.
"""

from copy import deepcopy


ARCHIVE_RULEBOOK_DIR = r"D:\Documents\Sessão RPG\D&D\Livro-de-Regras-DnD-5e"
LEGACY_DND_DIR = r"D:\Documents\Sessão RPG\D&D"


CORE_BOOK_SOURCES = {
    "phb": {
        "label": "Livro do Jogador",
        "primary": "pdf_text",
        "pdf": rf"{ARCHIVE_RULEBOOK_DIR}\LivrodoJogador.pdf",
        "support": {
            "djvu_xml": rf"{ARCHIVE_RULEBOOK_DIR}\LivrodoJogador_djvu.xml",
            "djvu_txt": rf"{ARCHIVE_RULEBOOK_DIR}\LivrodoJogador_djvu.txt",
            "hocr_html": rf"{ARCHIVE_RULEBOOK_DIR}\LivrodoJogador_hocr.html",
            "chocr_html_gz": rf"{ARCHIVE_RULEBOOK_DIR}\LivrodoJogador_chocr.html.gz",
            "page_numbers": rf"{ARCHIVE_RULEBOOK_DIR}\LivrodoJogador_page_numbers.json",
            "scandata": rf"{ARCHIVE_RULEBOOK_DIR}\LivrodoJogador_scandata.xml",
            "jp2_zip": rf"{ARCHIVE_RULEBOOK_DIR}\LivrodoJogador_jp2.zip",
        },
        "legacy_pdf": rf"{LEGACY_DND_DIR}\dd-5e-livro-do-jogador-fundo-branco-biblioteca-c3a9lfica.pdf",
    },
    "dmg": {
        "label": "Guia do Mestre",
        "primary": "pdf_text",
        "pdf": rf"{ARCHIVE_RULEBOOK_DIR}\GuiadoMestre.pdf",
        "support": {
            "djvu_xml": rf"{ARCHIVE_RULEBOOK_DIR}\GuiadoMestre_djvu.xml",
            "djvu_txt": rf"{ARCHIVE_RULEBOOK_DIR}\GuiadoMestre_djvu.txt",
            "hocr_html": rf"{ARCHIVE_RULEBOOK_DIR}\GuiadoMestre_hocr.html",
            "chocr_html_gz": rf"{ARCHIVE_RULEBOOK_DIR}\GuiadoMestre_chocr.html.gz",
            "page_numbers": rf"{ARCHIVE_RULEBOOK_DIR}\GuiadoMestre_page_numbers.json",
            "scandata": rf"{ARCHIVE_RULEBOOK_DIR}\GuiadoMestre_scandata.xml",
            "jp2_zip": rf"{ARCHIVE_RULEBOOK_DIR}\GuiadoMestre_jp2.zip",
        },
        "legacy_pdf": rf"{LEGACY_DND_DIR}\dd-5e-guia-do-mestre-biblioteca-elfica.pdf",
    },
    "mm": {
        "label": "Manual dos Monstros",
        "primary": "pdf_text",
        "pdf": rf"{ARCHIVE_RULEBOOK_DIR}\ManualdosMonstros.pdf",
        "support": {
            "djvu_xml": rf"{ARCHIVE_RULEBOOK_DIR}\ManualdosMonstros_djvu.xml",
            "djvu_txt": rf"{ARCHIVE_RULEBOOK_DIR}\ManualdosMonstros_djvu.txt",
            "hocr_html": rf"{ARCHIVE_RULEBOOK_DIR}\ManualdosMonstros_hocr.html",
            "chocr_html_gz": rf"{ARCHIVE_RULEBOOK_DIR}\ManualdosMonstros_chocr.html.gz",
            "page_numbers": rf"{ARCHIVE_RULEBOOK_DIR}\ManualdosMonstros_page_numbers.json",
            "scandata": rf"{ARCHIVE_RULEBOOK_DIR}\ManualdosMonstros_scandata.xml",
            "jp2_zip": rf"{ARCHIVE_RULEBOOK_DIR}\ManualdosMonstros_jp2.zip",
        },
        "legacy_pdf": rf"{LEGACY_DND_DIR}\old-dd-5e-manual-dos-monstros-biblioteca-elfica.pdf",
    },
    "xge": {
        "label": "Guia de Xanathar para Todas as Coisas",
        "primary": "legacy_pdf_text",
        "pdf": rf"{LEGACY_DND_DIR}\dd-5e-guia-de-xanathar-para-todas-as-coisas-fundo-branco-biblioteca-elfica.pdf",
        "support": {},
        "legacy_pdf": None,
    },
}


ALIASES = {
    "livro_do_jogador": "phb",
    "jogador": "phb",
    "phb": "phb",
    "guia_do_mestre": "dmg",
    "mestre": "dmg",
    "dmg": "dmg",
    "manual_dos_monstros": "mm",
    "monstros": "mm",
    "mm": "mm",
    "xanathar": "xge",
    "xge": "xge",
}


def canonical_key(key: str) -> str:
    """Resolve aliases curtos/legíveis para a chave canônica do catálogo."""
    normalized = key.strip().lower().replace(" ", "_").replace("-", "_")
    try:
        return ALIASES[normalized]
    except KeyError as exc:
        known = ", ".join(sorted(CORE_BOOK_SOURCES))
        raise KeyError(f"Fonte desconhecida: {key!r}. Fontes conhecidas: {known}") from exc


def book_source(key: str) -> dict:
    """Retorna uma cópia da configuração de fonte para evitar mutação acidental."""
    return deepcopy(CORE_BOOK_SOURCES[canonical_key(key)])


def pdf_path(key: str) -> str:
    """Caminho do PDF principal de uma fonte."""
    return book_source(key)["pdf"]


def support_path(key: str, support_name: str) -> str:
    """Caminho de um arquivo auxiliar, como djvu_xml ou page_numbers."""
    source = book_source(key)
    try:
        return source["support"][support_name]
    except KeyError as exc:
        available = ", ".join(sorted(source["support"]))
        raise KeyError(
            f"Apoio {support_name!r} não cadastrado para {key!r}. Disponíveis: {available}"
        ) from exc
