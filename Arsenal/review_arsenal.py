#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RAW_PATH = ROOT / "arsenal_raw.json"
REVIEWED_PATH = ROOT / "arsenal_reviewed.json"
FINAL_PATH = ROOT / "arsenal.json"
AUDIT_PATH = ROOT / "arsenal_review_audit.json"


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def load_items() -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    raw = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return list(raw.get("items", [])), raw
    if isinstance(raw, list):
        return list(raw), None
    raise TypeError("arsenal_raw.json precisa ser uma lista ou um objeto com a chave items.")


def clone_item(item: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(item)


def set_type(item: dict[str, Any], value: str) -> None:
    item["tipo"] = value


def set_description(item: dict[str, Any], value: str) -> None:
    item["descricao"] = value


def make_equipment(
    *,
    base: dict[str, Any],
    name: str,
    price: str,
    weight: str,
) -> dict[str, Any]:
    item = clone_item(base)
    item["nome"] = name
    item["id"] = slugify(f"{item['fonte']}-{item['categoria']}-{name}")
    item["preco"] = price
    item["peso"] = weight
    item["tabela"] = {"headers": ["Item", "Custo", "Peso"], "row": [name, price, weight]}
    item["descricao"] = ""
    return item


def review(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    reviewed: list[dict[str, Any]] = []
    corrections: list[str] = []

    type_fixes = {
        "Arma +1, +2 Ou +3": "Arma (qualquer)",
        "Arma de Alerta": "Arma (qualquer)",
        "Machado Furioso": "Arma (qualquer machado)",
        "Armadura +1, +2 Ou +3": "Armadura (leve, média ou pesada)",
        "Armadura de Invulnerabilidade": "Armadura (leve, média ou pesada)",
        "Armadura de Resistência": "Armadura (leve, média ou pesada)",
        "Armadura do Marinheiro": "Armadura (leve, média ou pesada)",
    }

    description_fixes = {
        "Cadeado da Enganação": (
            "Este cadeado aparenta ser comum (do tipo descrito no capítulo 5 do Livro do Jogador) e é acompanhado de uma chave. "
            "O mecanismo da fechadura ajusta-se magicamente para impedir ladrões. Testes de Destreza feitos para abrir a fechadura têm desvantagem."
        ),
        "Chapéu da Feitiçaria": (
            "Este chapéu antiquado em formato de cone é adornado com luas crescentes e estrelas. Ao usá-lo você recebe os seguintes benefícios: "
            "Você pode usar o chapéu como o foco arcano de suas magias de mago. Você pode tentar conjurar um truque que não conheça. "
            "O truque deve estar na lista de magias do mago e você deve fazer um teste de Inteligência (Arcanismo) com CD 10. "
            "Se o teste for bem sucedido, você conjura a magia. Se o teste falhar, a magia também falha, e a ação usada para tentar conjurar a magia é desperdiçada. "
            "Qualquer que seja o resultado, você não pode usar esta propriedade novamente até o fim de um descanso longo."
        ),
        "Chapéu dos Vermes": (
            "Este chapéu tem 3 cargas. Ao segurar o chapéu, você pode usar uma ação para gastar 1 de suas cargas e falar uma palavra de comando que conjura, à sua escolha, "
            "um morcego, um sapo ou um rato (ver o Livro do Jogador ou o Manual dos Monstros para estatísticas). "
            "A criatura magicamente conjurada aparece dentro do chapéu e tenta escapar de você o mais rápido possível. "
            "A criatura não é amigável ou hostil, e não está sob seu controle. Ela se comporta como uma criatura ordinária de seu tipo, e desaparece depois de 1 hora ou quando cair a 0 pontos de vida. "
            "O chapéu recupera diariamente todas as cargas gastas ao amanhecer."
        ),
        "Cajado Canoro": (
            "Este cajado de madeira é decorado com xilogravuras de pássaros. Ele tem 10 cargas. Ao segurá-lo, você pode usar uma ação para gastar 1 carga do cajado e fazê-lo criar um dos seguintes sons "
            "a até 18 metros de distância: o chilrear, gemido, chamado, grito ou canto de um canário, um corvo, um pato, uma galinha, um ganso, um mergulhão, uma gaivota, uma coruja ou uma águia. "
            "O cajado recupera diariamente 1d6 + 4 cargas gastas ao amanhecer. Se você gastar a última carga, role um d20. Em um resultado de 1, o cajado explode em uma nuvem inofensiva de penas de pássaros e é perdido."
        ),
    }

    split_name = "Pregos de ferro (10) Rações de viagem (1 dia)"
    split_base: dict[str, Any] | None = None

    for item in items:
        current = clone_item(item)
        name = current.get("nome")

        if name == split_name:
            split_base = current
            corrections.append("split: Pregos de ferro (10) / Rações de viagem (1 dia)")
            reviewed.append(make_equipment(base=current, name="Pregos de ferro (10)", price="1 po", weight="2,5 kg"))
            reviewed.append(make_equipment(base=current, name="Rações de viagem (1 dia)", price="5 pp", weight="1 kg"))
            continue

        if name in type_fixes:
            set_type(current, type_fixes[name])
            corrections.append(f"type: {name}")

        if name in description_fixes:
            set_description(current, description_fixes[name])
            corrections.append(f"description: {name}")

        reviewed.append(current)

    if split_base is None:
        corrections.append("split-missing: Pregos de ferro (10) Rações de viagem (1 dia)")

    return reviewed, corrections


def main() -> int:
    items, raw_root = load_items()
    reviewed, corrections = review(items)

    REVIEWED_PATH.write_text(json.dumps(reviewed, ensure_ascii=False, indent=2), encoding="utf-8")
    FINAL_PATH.write_text(json.dumps(reviewed, ensure_ascii=False, indent=2), encoding="utf-8")

    audit = {
        "source": str(RAW_PATH),
        "reviewed": str(REVIEWED_PATH),
        "final": str(FINAL_PATH),
        "before_total": len(items),
        "after_total": len(reviewed),
        "before_counts": dict(Counter(item.get("categoria") for item in items)),
        "after_counts": dict(Counter(item.get("categoria") for item in reviewed)),
        "before_sources": dict(Counter(item.get("fonte") for item in items)),
        "after_sources": dict(Counter(item.get("fonte") for item in reviewed)),
        "corrections": corrections,
        "pending_visual_checks": [
            "Revisar manualmente descrições com OCR pesado fora da lista de correções explícitas.",
        ],
    }
    if raw_root is not None:
        audit["raw_counts"] = raw_root.get("counts")
    AUDIT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"before": len(items), "after": len(reviewed), "corrections": corrections}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
