#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

from mechanics_data import SUBCLASS_DETAILS


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "xanathar_raw.json"


XANATHAR_SUBCLASSES = {
    "barbaro": ["Caminho do Guardião Ancestral", "Caminho do Arauto da Tempestade", "Caminho do Zelote"],
    "bardo": ["Colégio do Glamour", "Colégio das Espadas", "Colégio dos Sussurros"],
    "clerigo": ["Domínio da Forja", "Domínio do Túmulo"],
    "druida": ["Círculo dos Sonhos", "Círculo do Pastor"],
    "feiticeiro": ["Alma Divina", "Magia das Sombras", "Feitiçaria da Tempestade"],
    "guerreiro": ["Arqueiro Arcano", "Cavaleiro", "Samurai"],
    "ladino": ["Inquisitivo", "Mentor", "Batedor", "Espadachim"],
    "mago": ["Magia de Guerra"],
    "monge": ["Caminho do Mestre Bêbado", "Caminho do Kensei", "Caminho da Alma Solar"],
    "paladino": ["Juramento da Conquista", "Juramento da Redenção"],
    "patrulheiro": ["Conclave do Andarilho do Horizonte", "Conclave do Exterminador de Monstros", "Conclave do Perseguidor Sombrio"],
    "bruxo": ["O Celestial", "A Lâmina Maldita"],
}

XGE_SUBCLASS_DESCRIPTIONS = {
    "Caminho do Guardião Ancestral": "Bárbaro protegido por espíritos ancestrais que atrapalham inimigos e defendem aliados.",
    "Caminho do Arauto da Tempestade": "Bárbaro que manifesta uma aura elemental ligada a deserto, mar ou tundra.",
    "Caminho do Zelote": "Bárbaro fanático por uma causa divina, difícil de derrubar e perigoso em fúria.",
    "Colégio do Glamour": "Bardo feérico que encanta multidões, reposiciona aliados e domina a atenção social.",
    "Colégio das Espadas": "Bardo duelista que usa floreios com armas para defesa, dano e mobilidade.",
    "Colégio dos Sussurros": "Bardo de intriga, medo e manipulação psicológica.",
    "Domínio da Forja": "Clérigo artesão sagrado, especializado em armas, armaduras, fogo e criação.",
    "Domínio do Túmulo": "Clérigo guardião entre vida e morte, forte contra mortos-vivos e quedas prematuras.",
    "Círculo dos Sonhos": "Druida com magia feérica de cura, abrigo e deslocamento onírico.",
    "Círculo do Pastor": "Druida que fortalece invocações e protege o grupo com espíritos totêmicos.",
    "Alma Divina": "Feiticeiro tocado por poder celestial, misturando magia arcana e divina.",
    "Magia das Sombras": "Feiticeiro ligado à escuridão, resistente à morte e acompanhado por poderes sombrios.",
    "Feitiçaria da Tempestade": "Feiticeiro que canaliza vento e relâmpago com mobilidade explosiva.",
    "Arqueiro Arcano": "Guerreiro que infunde flechas com efeitos mágicos especiais.",
    "Cavaleiro": "Guerreiro defensor, orientado a duelos, marcação de inimigos e proteção de aliados.",
    "Samurai": "Guerreiro disciplinado que alterna presença social, foco e ataques precisos.",
    "Inquisitivo": "Ladino observador, excelente em ler mentiras, encontrar pistas e expor fraquezas.",
    "Mentor": "Ladino mestre de táticas sociais, disfarces, ajuda à distância e manipulação.",
    "Batedor": "Ladino explorador que se reposiciona rapidamente e atua bem em emboscadas.",
    "Espadachim": "Ladino duelista carismático, forte em combate individual e mobilidade elegante.",
    "Magia de Guerra": "Mago treinado para batalha, equilibrando defesa reativa e explosões controladas.",
    "Caminho do Mestre Bêbado": "Monge imprevisível, com movimentos erráticos, evasão e contra-ataques fluidos.",
    "Caminho do Kensei": "Monge que transforma armas escolhidas em extensão de sua disciplina marcial.",
    "Caminho da Alma Solar": "Monge que projeta energia radiante em ataques à distância e explosões de luz.",
    "Juramento da Conquista": "Paladino dominador, focado em medo, controle e imposição de autoridade.",
    "Juramento da Redenção": "Paladino pacificador que protege, absorve dano e busca resolver conflitos sem matar.",
    "Conclave do Andarilho do Horizonte": "Patrulheiro caçador planar, especializado em portais, teleporte e ameaças extraplanares.",
    "Conclave do Exterminador de Monstros": "Patrulheiro treinado para identificar e neutralizar criaturas sobrenaturais.",
    "Conclave do Perseguidor Sombrio": "Patrulheiro de emboscada, invisibilidade tática e atuação letal no início do combate.",
    "O Celestial": "Bruxo pactuado com entidade luminosa, ganhando cura, fogo radiante e proteção.",
    "A Lâmina Maldita": "Bruxo marcial ligado a uma arma sombria, usando Carisma para combate e maldições.",
}

XGE_SUBCLASS_PDF_PAGES = {
    "Caminho do Guardião Ancestral": 8,
    "Caminho do Arauto da Tempestade": 9,
    "Caminho do Zelote": 10,
    "Colégio do Glamour": 13,
    "Colégio das Espadas": 14,
    "Colégio dos Sussurros": 15,
    "Domínio da Forja": 22,
    "Domínio do Túmulo": 24,
    "Círculo dos Sonhos": 26,
    "Círculo do Pastor": 27,
    "Alma Divina": 33,
    "Magia das Sombras": 33,
    "Feitiçaria da Tempestade": 35,
    "Arqueiro Arcano": 37,
    "Cavaleiro": 38,
    "Samurai": 38,
    "Inquisitivo": 42,
    "Mentor": 42,
    "Batedor": 44,
    "Espadachim": 44,
    "Magia de Guerra": 46,
    "Caminho do Mestre Bêbado": 49,
    "Caminho do Kensei": 50,
    "Caminho da Alma Solar": 49,
    "Juramento da Conquista": 53,
    "Juramento da Redenção": 54,
    "Conclave do Andarilho do Horizonte": 59,
    "Conclave do Exterminador de Monstros": 59,
    "Conclave do Perseguidor Sombrio": 58,
    "O Celestial": 18,
    "A Lâmina Maldita": 20,
}


RACE_ADDITIONS = {
    "anao": [{"nome": "Duergar", "aumento_atributos": "FOR +1", "fonte": "Guia de Xanathar para Todas as Coisas", "fonte_sigla": "XGE", "habilidades": [{"nome": "Visão no Escuro Superior", "descricao": "Sua visão no escuro alcança distância maior que a de anões comuns."}, {"nome": "Resiliência Duergar", "descricao": "Você tem resistência adicional contra ilusões e contra ser enfeitiçado ou paralisado."}, {"nome": "Magia Duergar", "descricao": "Em níveis apropriados, pode usar magia inata ligada a aumentar o próprio tamanho e ficar invisível, recuperando usos após descanso."}, {"nome": "Sensibilidade à Luz Solar", "descricao": "Sob luz solar direta, sofre penalidades em ataques e testes de Percepção baseados em visão."}]}],
    "elfo": [
        {"nome": "Elfo do Mar", "aumento_atributos": "CON +1", "fonte": "Guia de Xanathar para Todas as Coisas", "fonte_sigla": "XGE", "habilidades": [{"nome": "Treinamento do Mar", "descricao": "Você ganha proficiência com armas tradicionais do povo do mar."}, {"nome": "Filho do Mar", "descricao": "Você tem deslocamento de natação e consegue respirar ar e água."}, {"nome": "Amigo do Mar", "descricao": "Você pode comunicar ideias simples a bestas que tenham deslocamento de natação."}]},
        {"nome": "Shadar-kai", "aumento_atributos": "CON +1", "fonte": "Guia de Xanathar para Todas as Coisas", "fonte_sigla": "XGE", "habilidades": [{"nome": "Benção da Rainha Corvo", "descricao": "Como ação bônus, teleporte-se para um espaço desocupado que possa ver dentro do alcance. Em níveis maiores, ganha resistência temporária a todo dano após teleportar."}, {"nome": "Resistência Necrótica", "descricao": "Você tem resistência a dano necrótico."}]},
    ],
    "halfling": [{"nome": "Halfling Fantasma", "aumento_atributos": "SAB +1", "fonte": "Guia de Xanathar para Todas as Coisas", "fonte_sigla": "XGE", "habilidades": [{"nome": "Discurso Silencioso", "descricao": "Você pode falar telepaticamente com uma criatura próxima que compartilhe idioma com você."}]}],
    "gnomo": [{"nome": "Gnomo das Profundezas", "aumento_atributos": "DES +1", "fonte": "Guia de Xanathar para Todas as Coisas", "fonte_sigla": "XGE", "habilidades": [{"nome": "Visão no Escuro Superior", "descricao": "Sua visão no escuro alcança distância maior que a de gnomos comuns."}, {"nome": "Camuflagem Rochosa", "descricao": "Você tem vantagem em testes de Destreza (Furtividade) para se esconder em terreno rochoso."}, {"nome": "Magia de Gnomo das Profundezas", "descricao": "Pode acessar magias temáticas de ilusão e ocultação conforme opção de talento ou regra associada."}]}],
    "tiefling": [{"nome": "Variantes de Linhagem Infernal", "aumento_atributos": "Variável", "fonte": "Guia de Xanathar para Todas as Coisas", "fonte_sigla": "XGE", "habilidades": [{"nome": "Legado Alternativo", "descricao": "Substitui ou ajusta o Legado Infernal padrão com magias ligadas a uma linhagem específica. Use a lista da linhagem escolhida para definir truque, magia de 3º nível e magia de 5º nível."}, {"nome": "Atributos Variantes", "descricao": "Algumas linhagens trocam o aumento de atributo secundário, mantendo o tiefling como opção carismática com foco diferente."}]}],
}


def slug(value: str) -> str:
    text = value.lower()
    table = str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc")
    text = text.translate(table)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def main() -> int:
    subclasses = []
    for class_id, names in XANATHAR_SUBCLASSES.items():
        for name in names:
            page_pdf = XGE_SUBCLASS_PDF_PAGES.get(name)
            subclasses.append({
                "id": slug(f"{class_id}-{name}"),
                "classe_id": class_id,
                "nome": name,
                "nivel_acesso": 3 if class_id not in {"clerigo", "feiticeiro", "bruxo", "mago", "druida"} else (1 if class_id in {"clerigo", "feiticeiro", "bruxo"} else 2),
                "fonte": "Guia de Xanathar para Todas as Coisas",
                "fonte_sigla": "XGE",
                "pagina_livro": None,
                "pagina_pdf": page_pdf,
                "referencia": f"XGE (PDF: {page_pdf})" if page_pdf else "Guia de Xanathar",
                "descricao": SUBCLASS_DETAILS.get(name) or XGE_SUBCLASS_DESCRIPTIONS.get(name, ""),
                "habilidades": [{"nivel": 3, "nome": f"Características de {name}", "descricao": ""}],
            })
    data = {"sub_classes": subclasses, "raca_adicoes": RACE_ADDITIONS}
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Gerado {OUTPUT} com {len(subclasses)} subclasses XGE e {len(RACE_ADDITIONS)} blocos raciais.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
