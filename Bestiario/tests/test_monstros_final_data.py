import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FinalMonsterDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.monsters = json.loads((ROOT / "monstros.json").read_text(encoding="utf-8"))
        cls.by_name = {monster["nome"]: monster for monster in cls.monsters}

    def test_miconide_broto_does_not_include_spore_servant_text(self):
        sprout = self.by_name["Miconide Broto"]
        combined = " ".join(
            [
                sprout.get("descricao") or "",
                *(sprout.get("habilidades_especiais") or []),
                *(sprout.get("acoes") or []),
            ]
        )

        self.assertEqual(sprout["descricao"], "")
        self.assertNotIn("servo esporo", combined.lower())
        self.assertNotIn("Características Perdidas", combined)
        self.assertEqual(len(sprout["habilidades_especiais"]), 2)
        self.assertEqual(len(sprout["acoes"]), 2)
        self.assertTrue(any(action.startswith("Punho.") for action in sprout["acoes"]))
        self.assertTrue(
            any(action.startswith("Esporos Harmoniosos") for action in sprout["acoes"])
        )

    def test_damage_resistance_is_not_embedded_in_skills(self):
        names = [
            "Arbusto Errante",
            "Chasme",
            "Yochlol",
            "Diabo Farpado",
            "Dracolich Azul Adulto",
            "Dragão Vermelho das Sombras Jovem",
            "Gigante da Tempestade",
            "Lich",
            "Meio -dragão Vermelho Veterano",
            "Slaad Vermelho",
            "Slaad da Morte",
            "Xorn",
            "Arcanaloth",
            "Mezzoloth",
            "Nycaloth",
            "Ultroloth",
            "Arquimago",
        ]

        for name in names:
            with self.subTest(name=name):
                monster = self.by_name[name]
                self.assertNotIn("Resistência a Dano", monster.get("pericias") or "")
                self.assertTrue(monster.get("resistencia_dano"))


if __name__ == "__main__":
    unittest.main()
