#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LJ_RAW = ROOT / "racas_classes_lj_raw.json"
XGE_RAW = ROOT / "xanathar_raw.json"
RAW_OUT = ROOT / "racas_classes_raw.json"
REVIEWED_OUT = ROOT / "racas_classes_reviewed.json"
FINAL_OUT = ROOT / "racas_classes.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    lj = load(LJ_RAW)
    xge = load(XGE_RAW)

    races = lj["racas"]
    by_race = {race["id"]: race for race in races}
    race_extra_sources = {
        "humano": {"GM"},
        "draconato": {"MM"},
        "elfo": {"MM"},
        "tiefling": {"MM"},
    }
    for race in races:
        for sub in race.get("sub_racas", []):
            sub.setdefault("fonte", "Livro do Jogador")
            sub.setdefault("fonte_sigla", "LJ")
    for race_id, additions in xge.get("raca_adicoes", {}).items():
        race = by_race.get(race_id)
        if not race:
            continue
        race.setdefault("sub_racas", []).extend(additions)
        sources = {race.get("fonte_sigla", "LJ"), *race_extra_sources.get(race_id, set()), *[a.get("fonte_sigla", "XGE") for a in additions]}
        race["fonte_sigla"] = "+".join(sorted(sources))
    for race_id, extra in race_extra_sources.items():
        race = by_race.get(race_id)
        if race and "+" not in race.get("fonte_sigla", ""):
            race["fonte_sigla"] = "+".join(sorted({race.get("fonte_sigla", "LJ"), *extra}))

    classes = lj["classes"]
    by_class = {klass["id"]: klass for klass in classes}
    for sub in xge.get("sub_classes", []):
        klass = by_class.get(sub["classe_id"])
        if klass:
            klass.setdefault("sub_classes", []).append({k: v for k, v in sub.items() if k != "classe_id"})

    records = races + classes
    for record in records:
        record["categoria"] = "Raças & Classes"

    payload = {
        "racas": races,
        "classes": classes,
        "items": records,
        "meta": {
            "total_racas": len(races),
            "total_classes": len(classes),
            "total_subclasses": sum(len(klass.get("sub_classes", [])) for klass in classes),
            "fontes": ["Livro do Jogador", "Guia de Xanathar para Todas as Coisas", "Guia do Mestre", "Manual dos Monstros"],
            "status": "estrutural inicial para integração",
        },
    }

    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    RAW_OUT.write_text(text, encoding="utf-8")
    REVIEWED_OUT.write_text(text, encoding="utf-8")
    FINAL_OUT.write_text(text, encoding="utf-8")
    print(f"Gerado {FINAL_OUT} com {len(records)} registros, {len(races)} raças, {len(classes)} classes e {payload['meta']['total_subclasses']} subclasses.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
