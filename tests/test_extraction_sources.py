import unittest

import extraction_sources as sources


class ExtractionSourcesTests(unittest.TestCase):
    def test_core_books_use_archive_package_paths(self):
        self.assertEqual(
            sources.pdf_path("phb"),
            r"D:\Documents\Sessão RPG\D&D\Livro-de-Regras-DnD-5e\LivrodoJogador.pdf",
        )
        self.assertEqual(
            sources.pdf_path("dmg"),
            r"D:\Documents\Sessão RPG\D&D\Livro-de-Regras-DnD-5e\GuiadoMestre.pdf",
        )
        self.assertEqual(
            sources.pdf_path("mm"),
            r"D:\Documents\Sessão RPG\D&D\Livro-de-Regras-DnD-5e\ManualdosMonstros.pdf",
        )

    def test_core_books_expose_layout_support_files(self):
        phb = sources.book_source("phb")

        self.assertEqual(phb["primary"], "pdf_text")
        self.assertIn("djvu_xml", phb["support"])
        self.assertTrue(phb["support"]["djvu_xml"].endswith("LivrodoJogador_djvu.xml"))
        self.assertTrue(phb["support"]["page_numbers"].endswith("LivrodoJogador_page_numbers.json"))


if __name__ == "__main__":
    unittest.main()
