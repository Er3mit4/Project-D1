#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


REQUIRED = {"id", "nome", "categoria", "tipo", "fonte", "referencia"}

KNOWN_ITEMS = {
    ("Espada Longa", "Arma"): {"preco": "15 po", "dano": "1d8 cortante", "peso": "1,5 kg"},
    ("Placas", "Armadura"): {"preco": "1.500 po", "ca": "18", "peso": "32,5 kg"},
    ("Poção de cura", "Equipamento"): {"preco": "50 po", "peso": "0,25 kg"},
    ("Anel de Proteção", "Item mágico"): {"raridade": "raro", "sintonizacao": True},
    ("Anel de Calor", "Item mágico"): {"raridade": "incomum", "sintonizacao": True},
    ("Aljava de Ehlonna", "Item mágico"): {"raridade": "incomum", "sintonizacao": False},
    ("Boneca Falante", "Item mágico"): {"raridade": "comum", "sintonizacao": True},
    ("Escudo da Expressão", "Item mágico"): {"raridade": "comum", "sintonizacao": False},
    ("Rubi do Mago da Guerra", "Item mágico"): {"raridade": "comum", "sintonizacao": True},
    ("Varinha da Pirotecnia", "Item mágico"): {"raridade": "comum", "sintonizacao": False},
}

KNOWN_DESCRIPTION_SNIPPETS = {
    ("Poção de cura", "Equipamento"): "recupera 2d4+2 pontos de vida",
    ("Placas", "Armadura"): "placas de metal moldadas",
    ("Ferramentas de ladrão", "Ferramenta"): "desarmar armadilhas",
    ("Rede", "Arma"): "fica impedida até se libertar",
    ("Anel de Calor", "Item mágico"): "resistência a dano de frio",
    ("Boneca Falante", "Item mágico"): "proferir até seis frases",
    ("Escudo da Expressão", "Item mágico"): "alterar a expressão",
    ("Vela das Profundezas", "Item mágico"): "não se extingue ao ser imersa em água",
}

KNOWN_CLASS_RULES = {
    ("Espada Longa", "Arma"): {"include": {"Guerreiro", "Paladino", "Bardo", "Ladino"}, "exclude": {"Mago"}},
    ("Placas", "Armadura"): {"include": {"Guerreiro", "Paladino"}, "exclude": {"Bardo", "Mago"}},
    ("Adaga", "Arma"): {"include": {"Mago", "Druida", "Guerreiro"}, "exclude": set()},
    ("Ferramentas de ladrão", "Ferramenta"): {"include": {"Ladino"}, "exclude": {"Monge"}},
    ("Ábaco", "Equipamento"): {"include": {"Mago", "Guerreiro", "Bardo"}, "exclude": set()},
}


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Arsenal/arsenal.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []

    if not isinstance(data, list):
        errors.append("A raiz do JSON precisa ser uma lista.")
        data = []

    ids = [item.get("id") for item in data if isinstance(item, dict)]
    duplicates = sorted(item_id for item_id, count in Counter(ids).items() if item_id and count > 1)
    if duplicates:
        errors.append("IDs duplicados: " + ", ".join(duplicates[:20]))

    for index, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"Item {index} nao e objeto.")
            continue
        missing = sorted(field for field in REQUIRED if not item.get(field))
        if missing:
            errors.append(f"Item {index} sem campos obrigatorios: {', '.join(missing)}")

    by_category = Counter(item.get("categoria") for item in data if isinstance(item, dict))
    by_source = Counter(item.get("fonte") for item in data if isinstance(item, dict))
    print(f"items={len(data)}")
    print(f"categories={dict(by_category)}")
    print(f"sources={dict(by_source)}")

    expected_categories = {"Arma", "Armadura", "Equipamento", "Ferramenta", "Item mágico"}
    missing_categories = sorted(expected_categories - set(by_category))
    if missing_categories:
        errors.append("Categorias esperadas ausentes: " + ", ".join(missing_categories))

    by_name_category = {
        (item.get("nome"), item.get("categoria")): item for item in data if isinstance(item, dict)
    }
    for key, expected in KNOWN_ITEMS.items():
        item = by_name_category.get(key)
        if not item:
            errors.append(f"Item sentinela ausente: {key[0]} / {key[1]}")
            continue
        for field, value in expected.items():
            if item.get(field) != value:
                errors.append(
                    f"Item sentinela {key[0]} com {field}={item.get(field)!r}; esperado {value!r}"
                )

    for key, snippet in KNOWN_DESCRIPTION_SNIPPETS.items():
        item = by_name_category.get(key)
        if not item:
            errors.append(f"Item sentinela ausente para descricao: {key[0]} / {key[1]}")
            continue
        description = item.get("descricao") or ""
        if snippet not in description:
            errors.append(f"Descricao sentinela ausente em {key[0]}: {snippet!r}")

    for key, rule in KNOWN_CLASS_RULES.items():
        item = by_name_category.get(key)
        if not item:
            errors.append(f"Item sentinela ausente para classes: {key[0]} / {key[1]}")
            continue
        classes = set(item.get("classes") or [])
        missing = sorted(rule["include"] - classes)
        unexpected = sorted(rule["exclude"] & classes)
        if missing:
            errors.append(f"Classes esperadas ausentes em {key[0]}: {', '.join(missing)}")
        if unexpected:
            errors.append(f"Classes indevidas em {key[0]}: {', '.join(unexpected)}")

    robe = by_name_category.get(("Robe dos Itens Úteis", "Item mágico"))
    if not robe:
        errors.append("Item sentinela ausente para estrutura: Robe dos Itens Úteis / Item mágico")
    else:
        blocks = robe.get("descricao_blocos") or []
        robe_list = next((block for block in blocks if block.get("type") == "list"), None)
        robe_table = next((block for block in blocks if block.get("type") == "table"), None)
        if not robe_list or len(robe_list.get("items") or []) != 6:
            errors.append("Robe dos Itens Úteis sem lista de 6 remendos fixos.")
        if not robe_table or len(robe_table.get("rows") or []) != 13:
            errors.append("Robe dos Itens Úteis sem tabela d100 com 13 linhas.")
        if "205" in (robe.get("descricao") or ""):
            errors.append("Robe dos Itens Úteis manteve rodape solto na descricao.")

    resistance = by_name_category.get(("Poção de Resistência", "Item mágico"))
    if not resistance:
        errors.append("Item sentinela ausente para estrutura: Poção de Resistência / Item mágico")
    else:
        blocks = resistance.get("descricao_blocos") or []
        table = next((block for block in blocks if block.get("type") == "table"), None)
        expected_rows = [
            ["1", "Ácido"],
            ["2", "Frio"],
            ["3", "Fogo"],
            ["4", "Energia"],
            ["5", "Elétrico"],
            ["6", "Necrótico"],
            ["7", "Veneno"],
            ["8", "Psíquico"],
            ["9", "Radiante"],
            ["10", "Trovejante"],
        ]
        if not table or table.get("headers") != ["d10", "Tipo de Dano"] or table.get("rows") != expected_rows:
            errors.append("Poção de Resistência sem tabela d10 estruturada corretamente.")

    expected_structured_tables = {
        ("Anel de Resistência", "Item mágico"): (["d10", "Tipo de Dano", "Gema"], 10, ["10", "Trovejante", "Espinela"]),
        ("Anel de Estrelas Cadentes", "Item mágico"): (["Esferas", "Dano Elétrico"], 4, ["4", "2d4"]),
        ("Armadura de Resistência", "Item mágico"): (["d10", "Tipo de Dano"], 10, ["10", "Trovejante"]),
        ("Baralho das Ilusões", "Item mágico"): (["Carta Jogada", "Ilusão"], 33, ["Coringas (2)", "Você (o dono do baralho)"]),
        ("Baralho das Surpresas", "Item mágico"): (["Carta Jogada", "Carta"], 22, ["Coringa (preto)", "Bufão"]),
        ("Bolsa de Truques", "Item mágico"): (["d8", "Bolsa de Truques Ferrugem"], 8, ["8", "Urso marrom"]),
        ("Cinturão de Força do Gigante", "Item mágico"): (["Tipo", "Força", "Raridade"], 5, ["Gigante da tempestade", "29", "Lendário"]),
        ("Corrente de Contas de Oração", "Item mágico"): (["d20", "Conta de...", "Magia"], 6, ["20", "Andar no vento", "Caminhar no vento"]),
        ("Cubo de Força", "Item mágico"): (["Magia ou Item", "Cargas Perdidas"], 5, ["Muralha de fogo", "1d4"]),
        ("Frasco de Ferro", "Item mágico"): (["d100", "Conteúdo"], 30, ["97-00", "Xorn"]),
        ("Instrumento dos Bardos", "Item mágico"): (["Instrumento", "Raridade", "Magias"], 8, ["Harpa de Ollamh", "Lendário", "Confusão, controlar o clima, tempestade de fogo"]),
        ("Manual dos Golens", "Item mágico"): (["d20", "Golem", "Custo", "Tempo"], 4, ["19-20", "Pedra", "80.000 po", "90 dias"]),
        ("Penas de Quaal", "Item mágico"): (["d100", "Pena"], 6, ["91-00", "Leque"]),
        ("Pergaminho de Magia", "Item mágico"): (["Nível de Magia", "Raridade", "CD de Resistência", "Bônus de Ataque"], 10, ["9°", "Lendário", "19", "+11"]),
        ("Pergaminho de Proteção", "Item mágico"): (["d100", "Tipo de Criatura"], 8, ["81-00", "Mortos-vivos"]),
        ("Poção de Cura", "Item mágico"): (["Poção de...", "Raridade", "PV Recuperados"], 4, ["Cura suprema", "Muito rara", "10d4 + 20"]),
        ("Poção de Força do Gigante", "Item mágico"): (["Tipo de Gigante", "Força", "Raridade"], 5, ["Gigante da tempestade", "29", "Lendária"]),
        ("Tapete Voador", "Item mágico"): (["d100", "Tamanho", "Capacidade", "Deslocamento de Voo"], 4, ["81-100", "1,8 m x 2,8 m", "400 kg", "9 m"]),
        ("Trombeta do Valhalla", "Item mágico"): (["d100", "Tipo de Trombeta", "Furiosos Invocados", "Requerimento"], 4, ["91-00", "Ferro", "5d4 + 5", "Proficiência com todas as armas marciais"]),
        ("Vela de Invocação", "Item mágico"): (["d20", "Tendência"], 9, ["18-20", "Leal e bom"]),
        ("Lâmina da Lua", "Item mágico"): (["d100", "Propriedade"], 12, ["00", "A lâmina da lua funciona como uma espada vorpal."]),
        ("Cajado do Arcano", "Item mágico"): (["Distância da Origem", "Dano"], 3, ["Entre 6,1 e 9 metros", "4 x a quantidade de cargas no cajado"]),
        ("Cajado do Poder", "Item mágico"): (["Distância da Origem", "Dano"], 3, ["Entre 6,1 e 9 metros", "4 x a quantidade de cargas no cajado"]),
    }
    for key, (headers, row_count, last_row) in expected_structured_tables.items():
        item = by_name_category.get(key)
        if not item:
            errors.append(f"Item sentinela ausente para estrutura: {key[0]} / {key[1]}")
            continue
        tables = [block for block in (item.get("descricao_blocos") or []) if block.get("type") == "table"]
        table = next((block for block in tables if block.get("headers") == headers), None)
        if not table:
            errors.append(f"{key[0]} sem tabela estruturada.")
            continue
        rows = table.get("rows") or []
        if table.get("headers") != headers or len(rows) != row_count or rows[-1] != last_row:
            errors.append(f"{key[0]} com tabela estruturada inesperada.")

    deck = by_name_category.get(("Baralho das Surpresas", "Item mágico"))
    if deck and "BARALHO DAS ILUSÕES" in (deck.get("descricao") or ""):
        errors.append("Baralho das Surpresas ainda contem tabela do Baralho das Ilusões.")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
