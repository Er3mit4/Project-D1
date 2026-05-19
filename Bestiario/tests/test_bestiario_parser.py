import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from extract_monsters import parse_monsters_from_chunk, printed_pages


class BestiarioParserRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "docling_out" / "mm_monsters_s_z" / "mm_monsters_s_z_p271_315.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        cls.monsters = parse_monsters_from_chunk(
            data,
            "mm_monsters_s_z",
            271,
            printed_pages(data, 271),
        )
        cls.by_name = {monster["nome"]: monster for monster in cls.monsters}

    def test_yuan_ti_entries_do_not_bleed_into_each_other(self):
        abomination = self.by_name["Yuan -ti Abominação"]
        halfblood = self.by_name["Yuan - Ti Mestiço"]
        pureblood = self.by_name["Yuan -ti Puro -sangue"]

        self.assertFalse(
            any("Um mestiço é" in action for action in abomination["acoes"])
        )
        self.assertTrue(
            any("Ataques Múltiplos" in action for action in halfblood["acoes"])
        )
        self.assertFalse(any("yugoloth" in action.lower() for action in pureblood["acoes"]))
        self.assertEqual(halfblood["habilidades"]["FOR"]["valor"], 16)
        self.assertEqual(pureblood["habilidades"]["FOR"]["valor"], 11)

    def test_corruptor_monsters_are_split_instead_of_attached_to_previous_card(self):
        self.assertIn("Arcanaloth", self.by_name)
        self.assertIn("Mezzoloth", self.by_name)
        self.assertIn("Nycaloth", self.by_name)
        self.assertIn("Ultroloth", self.by_name)
        self.assertEqual(self.by_name["Arcanaloth"]["ca"], "17 (armadura natural)")
        self.assertEqual(self.by_name["Ultroloth"]["pv"], "153")
        pureblood = self.by_name["Yuan -ti Puro -sangue"]
        self.assertLess(len(pureblood["acoes"]), 10)

    def test_lore_before_stat_block_is_preserved(self):
        nycaloth = self.by_name["Nycaloth"]

        self.assertIn("tropa de choque aérea", nycaloth["descricao"])
        self.assertNotIn("Corruptor Grande", nycaloth["descricao"])
        self.assertTrue(any("Ataques Múltiplos" in action for action in nycaloth["acoes"]))

    def test_lore_does_not_include_stat_table_fragments(self):
        halfblood = self.by_name["Yuan - Ti Mestiço"]

        self.assertIn("Um mestiço é", halfblood["descricao"])
        self.assertNotIn("FOR DES", halfblood["descricao"])
        self.assertNotIn("YUAN - TI MESTIÇO", halfblood["descricao"])

    def test_lore_shared_before_modron_stat_blocks_is_preserved(self):
        path = ROOT / "docling_out" / "mm_monsters_m_p" / "mm_monsters_m_p_p196_235.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        monsters = parse_monsters_from_chunk(
            data,
            "mm_monsters_m_p",
            196,
            printed_pages(data, 196),
        )
        by_name = {monster["nome"]: monster for monster in monsters}

        self.assertIn("tarefa simples", by_name["Monodrone"]["descricao"])
        self.assertIn("supervisionam unidades monodrones", by_name["Bidrone"]["descricao"])
        self.assertIn("pirâmides invertidas", by_name["Tridrone"]["descricao"])
        self.assertIn("artilharia", by_name["Quadrone"]["descricao"])
        self.assertIn("supervisionam a população trabalhadora", by_name["Pentadrone"]["descricao"])

    def test_lore_continuation_after_action_box_is_not_classified_as_action(self):
        path = ROOT / "docling_out" / "mm_monsters_dragon2" / "mm_monsters_dragon2_p106_125.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        monsters = parse_monsters_from_chunk(
            data,
            "mm_monsters_dragon2",
            106,
            printed_pages(data, 106),
        )
        by_name = {monster["nome"]: monster for monster in monsters}
        duergar = by_name["Duergar"]

        self.assertIn("do tamanho de um ogro", duergar["descricao"])
        self.assertIn("Mestre Infernal", duergar["descricao"])
        self.assertFalse(any("Mestre Infernal" in action for action in duergar["acoes"]))
        self.assertFalse(any(action.startswith("de um ogro") for action in duergar["acoes"]))

    def test_action_continuations_stay_with_actions(self):
        path = ROOT / "docling_out" / "mm_monsters_dragon2" / "mm_monsters_dragon2_p106_125.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        monsters = parse_monsters_from_chunk(
            data,
            "mm_monsters_dragon2",
            106,
            printed_pages(data, 106),
        )
        by_name = {monster["nome"]: monster for monster in monsters}
        silver = by_name["Dragão de Prata Ancião"]

        self.assertTrue(any("Na nova forma" in action for action in silver["acoes"]))
        self.assertNotIn("Na nova forma", silver["descricao"])

    def test_split_language_continuation_does_not_leak_into_lore(self):
        path = ROOT / "docling_out" / "mm_appendix_a" / "mm_appendix_a_p317_340.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        monsters = parse_monsters_from_chunk(
            data,
            "mm_appendix_a",
            317,
            printed_pages(data, 317),
        )
        by_name = {monster["nome"]: monster for monster in monsters}
        owl = by_name["Coruja Gigante"]

        self.assertEqual(
            owl["descricao"],
            "As corujas gigantes frequentemente fazem amizades com fadas e outras "
            "criaturas silvestres, e são guardiãs dos reinos florestais.",
        )
        self.assertIn("mas não pode falar", owl["idiomas"])
        self.assertFalse(owl["descricao"].startswith("mas não pode falar"))

    def test_table_only_statblock_is_not_dropped(self):
        salamandra = self.by_name["Salamandra"]

        self.assertEqual(salamandra["ca"], "15 (armadura natural)")
        self.assertEqual(salamandra["pv"], "90")
        self.assertTrue(any("Ataques Múltiplos" in action for action in salamandra["acoes"]))

    def test_inline_name_stat_blocks_start_new_monster(self):
        path = ROOT / "docling_out" / "mm_monsters_p_s" / "mm_monsters_p_s_p236_270.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        monsters = parse_monsters_from_chunk(
            data,
            "mm_monsters_p_s",
            236,
            printed_pages(data, 236),
        )
        by_name = {monster["nome"]: monster for monster in monsters}

        self.assertIn("Tirano da Morte", by_name)
        observador = by_name["Observador"]
        self.assertFalse(
            any("TIRANO DA MORTE" in action for action in observador["acoes_lendarias"])
        )


if __name__ == "__main__":
    unittest.main()
