import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "unified_template.html"
NOTICE = "Módulo em construção. Versão alfa de teste inicial para criação e edição de fichas."


class FichaAlphaNoticeTests(unittest.TestCase):
    def test_home_ficha_card_shows_alpha_notice(self):
        html = TEMPLATE.read_text(encoding="utf-8")
        card_start = html.index("<!-- Ficha Card -->")
        card_end = html.index("</div>", html.index("CRIAR PERSONAGEM", card_start))
        ficha_card = html[card_start:card_end]

        self.assertIn(NOTICE, ficha_card)

    def test_sheet_page_header_shows_alpha_notice(self):
        html = TEMPLATE.read_text(encoding="utf-8")
        list_start = html.index("function renderSheetList()")
        list_end = html.index("function renderSheetWizard", list_start)
        sheet_list = html[list_start:list_end]

        self.assertIn(NOTICE, sheet_list)


if __name__ == "__main__":
    unittest.main()
