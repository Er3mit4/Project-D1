import json
import unittest
from pathlib import Path

from page_references import book_page_reference, strip_pdf_reference


ROOT = Path(__file__).resolve().parents[1]


class PageReferenceTests(unittest.TestCase):
    def test_strip_pdf_reference_keeps_only_book_page(self):
        self.assertEqual(strip_pdf_reference("147 (PDF: 146)"), "147")
        self.assertEqual(strip_pdf_reference("p.215 (PDF: 213)"), "p.215")
        self.assertEqual(strip_pdf_reference("Livro do Jogador"), "Livro do Jogador")

    def test_book_page_reference_prefers_printed_page(self):
        self.assertEqual(book_page_reference(147, 146), "147")
        self.assertEqual(book_page_reference(None, 146), "")

    def test_human_facing_core_module_references_do_not_include_pdf_pages(self):
        paths = [
            ROOT / "Grimorio" / "spells_raw.json",
            ROOT / "Arsenal" / "arsenal.json",
            ROOT / "Arsenal" / "arsenal_reviewed.json",
            ROOT / "Arsenal" / "arsenal_raw.json",
            ROOT / "Bestiario" / "monstros.json",
            ROOT / "Bestiario" / "monstros_reviewed.json",
            ROOT / "Bestiario" / "monstros_raw.json",
        ]

        offenders = []
        for path in paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            stack = [data]
            while stack:
                current = stack.pop()
                if isinstance(current, dict):
                    stack.extend(current.values())
                elif isinstance(current, list):
                    stack.extend(current)
                elif isinstance(current, str) and "PDF:" in current:
                    offenders.append(f"{path.relative_to(ROOT)}: {current}")

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
