import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import audit_docling_html
import build_html
import fix_missing_nd
import run_docling_extraction


class DoclingWorkflowTest(unittest.TestCase):
    def test_html_command_uses_placeholder_images(self):
        command = run_docling_extraction.build_docling_command(
            Path("source.pdf"),
            Path("out"),
            output_format="html",
            tables=True,
        )

        self.assertIn("--to", command)
        self.assertEqual(command[command.index("--to") + 1], "html")
        self.assertIn("--image-export-mode", command)
        self.assertEqual(command[command.index("--image-export-mode") + 1], "placeholder")
        self.assertIn("--table-mode", command)
        self.assertIn("accurate", command)

    def test_json_without_tables_uses_no_tables(self):
        command = run_docling_extraction.build_docling_command(
            Path("source.pdf"),
            Path("out"),
            output_format="json",
            tables=False,
        )

        self.assertEqual(command[command.index("--to") + 1], "json")
        self.assertIn("--no-tables", command)
        self.assertNotIn("--image-export-mode", command)

    def test_html_audit_reports_statblocks_missing_from_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            html_dir = tmp_path / "html"
            html_dir.mkdir()
            (html_dir / "sample.html").write_text(
                """
                <html><body>
                  <h2>TESTE</h2>
                  <p>Monstruosidade Grande, imparcial</p>
                  <table><tr><td>FALTA NO JSON Corruptor Médio, neutro e mau</td></tr></table>
                  <figure><img src="data:image/png;base64,AAAA"></figure>
                </body></html>
                """,
                encoding="utf-8",
            )
            json_path = tmp_path / "monstros.json"
            json_path.write_text(
                json.dumps([{"nome": "Teste"}], ensure_ascii=False),
                encoding="utf-8",
            )

            result = audit_docling_html.audit_html_against_json(html_dir, json_path)

        self.assertIn("Falta no Json", result["missing_in_json"])
        self.assertEqual(result["html_statblocks"], ["Falta no Json"])

    def test_missing_nd_reference_covers_known_dragon_gaps(self):
        expected = {
            "Dracolich Azul Adulto": ("17", "18.000"),
            "Dragão Negro Ancião": ("21", "33.000"),
            "Dragão Verde Ancião": ("22", "41.000"),
            "Dragão Verde Jovem": ("8", "3.900"),
            "Dragão de Bronze Filhote": ("2", "450"),
            "Dragão de Prata Jovem": ("9", "5.000"),
            "Dragão de Prata Filhote": ("2", "450"),
        }

        for name, nd_xp in expected.items():
            self.assertEqual(fix_missing_nd.REFERENCE[name], nd_xp)

    def test_extract_nd_accepts_docling_spaced_xp(self):
        self.assertEqual(
            fix_missing_nd.extract_nd("Nível de Desafio 23 (50 . 000 XP)"),
            ("23", "50.000"),
        )

    def test_fix_missing_nd_can_write_final_from_reviewed_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "monstros_reviewed.json"
            output = tmp_path / "monstros.json"
            source.write_text(
                json.dumps(
                    [
                        {
                            "nome": "Dragão Negro Ancião",
                            "pagina_pdf": 88,
                            "nd": None,
                            "xp": None,
                        }
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            exit_code = fix_missing_nd.main(
                [
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--docling-dir",
                    str(tmp_path / "missing_docling"),
                ]
            )

            self.assertEqual(exit_code, 0)
            final = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(final[0]["nd"], "21")
            self.assertEqual(final[0]["xp"], "33.000")

    def test_build_html_accepts_explicit_data_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            data = tmp_path / "monstros.json"
            template = tmp_path / "template.html"
            output = tmp_path / "index.html"
            data.write_text(json.dumps([{"nome": "Teste"}], ensure_ascii=False), encoding="utf-8")
            template.write_text("const MONSTERS = __MONSTERS_DATA__;", encoding="utf-8")

            exit_code = build_html.main(
                [
                    "--data",
                    str(data),
                    "--template",
                    str(template),
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertIn('"nome":"Teste"', output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
