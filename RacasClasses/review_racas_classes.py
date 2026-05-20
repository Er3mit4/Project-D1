#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "racas_classes.json"


REQUIRED_RACE_FIELDS = {"id", "nome", "tipo", "aumento_atributos", "tamanho", "deslocamento", "habilidades_raciais", "sub_racas", "fonte_sigla"}
REQUIRED_CLASS_FIELDS = {"id", "nome", "tipo", "dado_de_vida", "testes_resistencia", "habilidades_classe", "tabela_niveis", "sub_classes", "fonte_sigla"}
BANNED_TEXT = [
    "Consultar fonte oficial",
    "Progressão de classe",
    "revisar texto integral",
    "marcada para revisão",
    "Subclasse adicional",
    "Entrada estrutural",
]


def fail(errors: list[str]) -> int:
    for error in errors:
        print(f"[ERRO] {error}")
    return 1


def main() -> int:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    races = payload.get("racas", [])
    classes = payload.get("classes", [])
    records = payload.get("items", [])
    errors: list[str] = []

    if len(races) != 9:
        errors.append(f"esperado 9 raças, encontrado {len(races)}")
    if len(classes) != 12:
        errors.append(f"esperado 12 classes, encontrado {len(classes)}")
    if len(records) != len(races) + len(classes):
        errors.append("items deve conter raças + classes")

    ids = [record.get("id") for record in records]
    if len(ids) != len(set(ids)):
        errors.append("ids duplicados em items")

    for race in races:
        missing = REQUIRED_RACE_FIELDS - set(race)
        if missing:
            errors.append(f"raça {race.get('nome', '?')} sem campos: {', '.join(sorted(missing))}")
        for trait in race.get("habilidades_raciais", []):
            if not trait.get("descricao"):
                errors.append(f"raça {race.get('nome', '?')} com habilidade racial sem descrição: {trait.get('nome', '?')}")
        for subrace in race.get("sub_racas", []):
            for trait in subrace.get("habilidades", []):
                if not trait.get("descricao"):
                    errors.append(f"sub-raça {subrace.get('nome', '?')} com habilidade sem descrição: {trait.get('nome', '?')}")
    for klass in classes:
        missing = REQUIRED_CLASS_FIELDS - set(klass)
        if missing:
            errors.append(f"classe {klass.get('nome', '?')} sem campos: {', '.join(sorted(missing))}")
        if len(klass.get("tabela_niveis", [])) != 20:
            errors.append(f"classe {klass.get('nome', '?')} sem tabela completa 1-20")
        for field in ("proficiencias_armadura", "proficiencias_armas", "proficiencias_ferramentas", "pericias_opcoes", "equipamento_inicial"):
            if not klass.get(field):
                errors.append(f"classe {klass.get('nome', '?')} sem {field}")
        for trait in klass.get("habilidades_classe", []):
            if not trait.get("descricao"):
                errors.append(f"classe {klass.get('nome', '?')} com habilidade sem descrição: {trait.get('nome', '?')}")
        for subclass in klass.get("sub_classes", []):
            if not subclass.get("descricao"):
                errors.append(f"subclasse {subclass.get('nome', '?')} sem descrição")
            if subclass.get("fonte_sigla") == "XGE" and not subclass.get("pagina_pdf"):
                errors.append(f"subclasse XGE {subclass.get('nome', '?')} sem pagina_pdf")

    total_subclasses = sum(len(klass.get("sub_classes", [])) for klass in classes)
    if total_subclasses < 60:
        errors.append(f"subclasses insuficientes: {total_subclasses}")

    serialized = json.dumps(payload, ensure_ascii=False)
    for phrase in BANNED_TEXT:
        if phrase in serialized:
            errors.append(f"texto bloqueado encontrado nos dados: {phrase}")

    if errors:
        return fail(errors)

    print(f"OK: {len(races)} raças, {len(classes)} classes, {total_subclasses} subclasses, {len(records)} registros finais.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
