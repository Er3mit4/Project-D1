import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import review_monsters


def monster(**overrides):
    base = {
        "id": "manual-dos-monstros-teste",
        "nome": "Teste",
        "tipo_criatura": "Besta",
        "tamanho": "Médio",
        "alinhamento": "imparcial",
        "ca": "10",
        "pv": "4",
        "pv_dados": "1d8",
        "deslocamento": "9 m",
        "habilidades": {},
        "testes_resistencia": None,
        "pericias": None,
        "resistencia_dano": None,
        "imunidade_dano": None,
        "imunidade_condicao": None,
        "sentidos": None,
        "idiomas": None,
        "nd": "0",
        "xp": "10",
        "fonte": "Manual dos Monstros",
        "pagina_livro": 1,
        "pagina_pdf": 1,
        "referencia": "1",
        "descricao": "",
        "habilidades_especiais": [],
        "acoes": [],
        "acoes_lendarias": [],
        "acoes_covil": [],
        "efeitos_regionais": [],
        "reacoes": [],
        "descricao_blocos": [],
    }
    base.update(overrides)
    return base


class ReviewMonstersTest(unittest.TestCase):
    def test_review_splits_compound_stat_fields(self):
        reviewed = review_monsters.review_monster(
            monster(
                testes_resistencia=(
                    "For +7, Con +6 Perícias Enganação +6, Furtividade +7 "
                    "Resistência a Dano frio, fogo "
                    "Sentidos visão no escuro 18 m, Percepção passiva 14 "
                    "Idiomas Abissal, Comum Nível de Desafio 5 (1.800 XP)"
                )
            )
        )

        self.assertEqual(reviewed["testes_resistencia"], "For +7, Con +6")
        self.assertEqual(reviewed["pericias"], "Enganação +6, Furtividade +7")
        self.assertEqual(reviewed["resistencia_dano"], "frio, fogo")
        self.assertEqual(reviewed["sentidos"], "visão no escuro 18 m, Percepção passiva 14")
        self.assertEqual(reviewed["idiomas"], "Abissal, Comum")
        self.assertEqual(reviewed["nd"], "5")
        self.assertEqual(reviewed["xp"], "1.800")

    def test_review_moves_untitled_lore_from_traits_to_description(self):
        reviewed = review_monsters.review_monster(
            monster(
                descricao="Lore inicial.",
                habilidades_especiais=[
                    "O sinuoso behir rasteja pelo solo e escala pelas paredes.",
                    "Visão Aguçada. O teste mecânico permanece aqui.",
                ],
            )
        )

        self.assertEqual(
            reviewed["descricao"],
            "Lore inicial. O sinuoso behir rasteja pelo solo e escala pelas paredes.",
        )
        self.assertEqual(
            reviewed["habilidades_especiais"],
            ["Visão Aguçada. O teste mecânico permanece aqui."],
        )

    def test_review_moves_action_text_that_started_in_description(self):
        reviewed = review_monsters.review_monster(
            monster(
                descricao=(
                    "Lore real antes. Presença Aterradora. Cada criatura deve realizar um teste. "
                    "Sopro Elétrico. O dragão expele energia."
                ),
                acoes=["Mordida. Ataque Corpo-a-Corpo com Arma: +5 para atingir."],
            )
        )

        self.assertEqual(reviewed["descricao"], "Lore real antes.")
        self.assertIn("Presença Aterradora. Cada criatura deve realizar um teste.", reviewed["acoes"])
        self.assertIn("Sopro Elétrico. O dragão expele energia.", reviewed["acoes"])
        self.assertIn("Mordida. Ataque Corpo-a-Corpo com Arma: +5 para atingir.", reviewed["acoes"])

    def test_review_moves_lore_that_leaked_into_reactions(self):
        reviewed = review_monsters.review_monster(
            monster(
                reacoes=[
                    "Aparar. O cavaleiro adiciona 2 à sua CA contra um ataque.",
                    "Cavaleiros são guerreiros que juraram servir governantes.",
                ]
            )
        )

        self.assertEqual(reviewed["descricao"], "Cavaleiros são guerreiros que juraram servir governantes.")
        self.assertEqual(reviewed["reacoes"], ["Aparar. O cavaleiro adiciona 2 à sua CA contra um ataque."])

    def test_review_joins_section_continuations(self):
        reviewed = review_monsters.review_monster(
            monster(
                acoes_lendarias=[
                    "Ataque com Asas. O dragão bate suas asas.",
                    "num teste de resistência de Destreza CD 19 ou sofrerá dano.",
                ]
            )
        )

        self.assertEqual(
            reviewed["acoes_lendarias"],
            ["Ataque com Asas. O dragão bate suas asas. num teste de resistência de Destreza CD 19 ou sofrerá dano."],
        )

    def test_review_removes_trailing_stats_from_description(self):
        reviewed = review_monsters.review_monster(
            monster(
                descricao=(
                    "Lore do monstro. envenenado, exausto Sentidos percepção às cegas 18 m, "
                    "Percepção passiva 6 Idiomas -"
                ),
                imunidade_condicao="amedrontado",
            )
        )

        self.assertEqual(reviewed["descricao"], "Lore do monstro.")
        self.assertEqual(reviewed["imunidade_condicao"], "amedrontado, envenenado, exausto")
        self.assertEqual(reviewed["sentidos"], "percepção às cegas 18 m, Percepção passiva 6")
        self.assertEqual(reviewed["idiomas"], "-")

    def test_review_repairs_suspicious_description_fragments(self):
        reviewed = review_monsters.review_monster(
            monster(
                descricao="Percepção passiva 13 Lore preservado depois.",
                sentidos="visão no escuro 18 m,",
            )
        )

        self.assertEqual(reviewed["descricao"], "Lore preservado depois.")
        self.assertEqual(reviewed["sentidos"], "visão no escuro 18 m, Percepção passiva 13")

        reviewed = review_monsters.review_monster(
            monster(descricao="que compreendam Abissal)", idiomas="Abissal, telepatia 36 m (funciona apenas com criaturas")
        )

        self.assertEqual(reviewed["descricao"], "")
        self.assertEqual(
            reviewed["idiomas"],
            "Abissal, telepatia 36 m (funciona apenas com criaturas que compreendam Abissal)",
        )

    def test_review_joins_split_trait_title_fragments(self):
        reviewed = review_monsters.review_monster(
            monster(
                descricao="Absorção de",
                habilidades_especiais=[
                    "Fogo. Sempre que o golem for alvo de dano de fogo, ele recupera pontos de vida."
                ],
            )
        )

        self.assertEqual(reviewed["descricao"], "")
        self.assertEqual(
            reviewed["habilidades_especiais"],
            ["Absorção de Fogo. Sempre que o golem for alvo de dano de fogo, ele recupera pontos de vida."],
        )

    def test_audit_reports_blocking_leaks_after_review(self):
        issues = review_monsters.audit_monsters(
            [
                monster(
                    nome="Vazamento",
                    descricao="Classe de Armadura 12 Pontos de Vida 7",
                    pericias="Percepção +2 Sentidos visão no escuro 18 m",
                    acoes=["texto solto sem ataque"],
                )
            ]
        )

        codes = {issue["code"] for issue in issues}
        self.assertIn("description_statblock_leak", codes)
        self.assertIn("compound_field_leak", codes)
        self.assertIn("suspicious_action", codes)

    def test_audit_does_not_flag_normal_lore_words_or_legendary_intro(self):
        issues = review_monsters.audit_monsters(
            [
                monster(
                    descricao="Essa tagarelice cacofônica sobrepõe os sentidos de qualquer criatura.",
                    acoes_lendarias=[
                        "O dragão pode realizar 3 ações lendárias, escolhidas dentre as opções abaixo."
                    ],
                )
            ]
        )

        self.assertEqual(issues, [])

    def test_main_writes_reviewed_output_and_audit_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "monstros_raw.json"
            output_path = tmp_path / "monstros_reviewed.json"
            audit_path = tmp_path / "review_audit.json"
            input_path.write_text(
                json.dumps([monster(testes_resistencia="For +1 Perícias Atletismo +3")], ensure_ascii=False),
                encoding="utf-8",
            )

            exit_code = review_monsters.main(
                [
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                    "--audit-output",
                    str(audit_path),
                    "--allow-issues",
                ]
            )

            self.assertEqual(exit_code, 0)
            reviewed = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(reviewed[0]["testes_resistencia"], "For +1")
            self.assertEqual(reviewed[0]["pericias"], "Atletismo +3")
            self.assertTrue(audit_path.exists())


if __name__ == "__main__":
    unittest.main()
