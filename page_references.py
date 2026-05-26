#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Formatação de referências de página exibidas no Projeto D1."""

from __future__ import annotations

import re


PDF_REFERENCE_RE = re.compile(r"\s*\(PDF:\s*[^)]*\)")


def strip_pdf_reference(value: object) -> str:
    """Remove a parte '(PDF: ...)' de uma referência humana, preservando o texto base."""
    if value is None:
        return ""
    return PDF_REFERENCE_RE.sub("", str(value)).strip()


def book_page_reference(page_print: object, page_pdf: object | None = None) -> str:
    """Retorna somente a página impressa do livro para exibição ao usuário."""
    if page_print in (None, ""):
        return ""
    return strip_pdf_reference(page_print)
