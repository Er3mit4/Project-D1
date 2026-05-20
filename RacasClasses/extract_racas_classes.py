#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

from mechanics_data import FEATURE_DETAILS, SUBCLASS_DETAILS


ROOT = Path(__file__).resolve().parent
RACES_SOURCE = ROOT / "racas.json"
OUTPUT = ROOT / "racas_classes_lj_raw.json"


CLASS_SPECS = [
    ("barbaro", "Bárbaro", "d12", "Força, Constituição", 3, ["Caminho do Berserker", "Caminho do Totem"], ["Fúria", "Defesa sem Armadura", "Ataque Imprudente", "Sentido de Perigo", "Ataque Extra", "Movimento Rápido", "Instinto Selvagem", "Crítico Brutal", "Fúria Persistente", "Poder Indomável", "Campeão Primitivo"]),
    ("bardo", "Bardo", "d8", "Destreza, Carisma", 3, ["Colégio do Conhecimento", "Colégio da Bravura"], ["Inspiração de Bardo", "Conjuração", "Versatilidade", "Canção de Descanso", "Especialização", "Fonte de Inspiração", "Contra-encantamento", "Segredos Mágicos", "Inspiração Superior"]),
    ("clerigo", "Clérigo", "d8", "Sabedoria, Carisma", 1, ["Domínio do Conhecimento", "Domínio da Enganação", "Domínio da Guerra", "Domínio da Luz", "Domínio da Natureza", "Domínio da Tempestade", "Domínio da Vida"], ["Conjuração", "Domínio Divino", "Canalizar Divindade", "Destruir Mortos-vivos", "Intervenção Divina"]),
    ("druida", "Druida", "d8", "Inteligência, Sabedoria", 2, ["Círculo da Terra", "Círculo da Lua"], ["Druídico", "Conjuração", "Forma Selvagem", "Corpo Atemporal", "Magias Bestiais", "Arquedruida"]),
    ("feiticeiro", "Feiticeiro", "d6", "Constituição, Carisma", 1, ["Linhagem Dracônica", "Magia Selvagem"], ["Conjuração", "Origem Feiticeira", "Fonte de Magia", "Metamagia", "Restauração Mística"]),
    ("guerreiro", "Guerreiro", "d10", "Força, Constituição", 3, ["Campeão", "Mestre de Batalha", "Cavaleiro Místico"], ["Estilo de Luta", "Retomar o Fôlego", "Surto de Ação", "Arquétipo Marcial", "Ataque Extra", "Indomável"]),
    ("ladino", "Ladino", "d8", "Destreza, Inteligência", 3, ["Assassino", "Ladrão", "Trapaceiro Arcano"], ["Especialização", "Ataque Furtivo", "Gíria de Ladrão", "Ação Ardilosa", "Arquétipo de Ladino", "Esquiva Sobrenatural", "Evasão", "Talento Confiável", "Sentido Cego", "Mente Escorregadia", "Elusivo", "Golpe de Sorte"]),
    ("mago", "Mago", "d6", "Inteligência, Sabedoria", 2, ["Escola de Abjuração", "Escola de Adivinhação", "Escola de Conjuração", "Escola de Encantamento", "Escola de Evocação", "Escola de Ilusão", "Escola de Necromancia", "Escola de Transmutação"], ["Conjuração", "Recuperação Arcana", "Tradição Arcana", "Domínio de Magia", "Magias Assinatura"]),
    ("monge", "Monge", "d8", "Força, Destreza", 3, ["Caminho da Mão Aberta", "Caminho das Sombras", "Caminho dos Quatro Elementos"], ["Defesa sem Armadura", "Artes Marciais", "Ki", "Movimento sem Armadura", "Tradição Monástica", "Defletir Mísseis", "Queda Lenta", "Ataque Extra", "Ataque Atordoante", "Golpes de Ki", "Evasão", "Mente Tranquila", "Pureza Corporal", "Idioma do Sol e da Lua", "Alma de Diamante", "Corpo Atemporal", "Corpo Vazio", "Autoperfeição"]),
    ("paladino", "Paladino", "d10", "Sabedoria, Carisma", 3, ["Juramento da Devoção", "Juramento dos Anciões", "Juramento da Vingança"], ["Sentido Divino", "Cura pelas Mãos", "Estilo de Luta", "Conjuração", "Destruição Divina", "Saúde Divina", "Juramento Sagrado", "Aura de Proteção", "Aura de Coragem", "Destruição Divina Aprimorada", "Toque Purificador"]),
    ("patrulheiro", "Patrulheiro", "d10", "Força, Destreza", 3, ["Caçador", "Mestre das Bestas"], ["Inimigo Favorito", "Explorador Natural", "Estilo de Luta", "Conjuração", "Arquétipo de Patrulheiro", "Consciência Primitiva", "Ataque Extra", "Passo da Terra", "Esconder-se à Plena Vista", "Desaparecer", "Sentidos Selvagens", "Matador de Inimigos"]),
    ("bruxo", "Bruxo", "d8", "Sabedoria, Carisma", 1, ["O Arquifada", "O Corruptor", "O Grande Antigo"], ["Patrono Transcendental", "Magia de Pacto", "Invocações Místicas", "Dádiva do Pacto", "Arcana Mística", "Mestre Místico"]),
]

CLASS_PAGES = {
    "barbaro": (46, 45),
    "bardo": (51, 50),
    "bruxo": (56, 55),
    "clerigo": (63, 62),
    "druida": (71, 70),
    "feiticeiro": (77, 76),
    "guerreiro": (83, 82),
    "ladino": (89, 88),
    "mago": (94, 93),
    "monge": (102, 101),
    "paladino": (108, 107),
    "patrulheiro": (115, 114),
}

CLASS_PROFICIENCIES = {
    "barbaro": {
        "armaduras": "Armaduras leves, armaduras médias e escudos",
        "armas": "Armas simples e armas marciais",
        "ferramentas": "Nenhuma",
        "pericias": "Escolha 2 entre: Adestrar Animais, Atletismo, Intimidação, Natureza, Percepção e Sobrevivência",
        "equipamento": "Machado grande ou arma marcial; duas machadinhas ou arma simples; pacote de aventureiro e quatro azagaias.",
    },
    "bardo": {
        "armaduras": "Armaduras leves",
        "armas": "Armas simples, bestas de mão, espadas longas, rapieiras e espadas curtas",
        "ferramentas": "Três instrumentos musicais à sua escolha",
        "pericias": "Escolha quaisquer 3 perícias",
        "equipamento": "Rapieira, espada longa ou arma simples; pacote diplomático ou de artista; instrumento musical; armadura de couro e adaga.",
    },
    "bruxo": {
        "armaduras": "Armaduras leves",
        "armas": "Armas simples",
        "ferramentas": "Nenhuma",
        "pericias": "Escolha 2 entre: Arcanismo, Enganação, História, Intimidação, Investigação, Natureza e Religião",
        "equipamento": "Besta leve e virotes ou arma simples; bolsa de componentes ou foco arcano; pacote de estudioso ou explorador; armadura de couro, arma simples e duas adagas.",
    },
    "clerigo": {
        "armaduras": "Armaduras leves, armaduras médias e escudos",
        "armas": "Armas simples",
        "ferramentas": "Nenhuma",
        "pericias": "Escolha 2 entre: História, Intuição, Medicina, Persuasão e Religião",
        "equipamento": "Maça ou martelo de guerra se proficiente; brunea, armadura de couro ou cota de malha se proficiente; besta leve ou arma simples; pacote de sacerdote ou explorador; escudo e símbolo sagrado.",
    },
    "druida": {
        "armaduras": "Armaduras leves, armaduras médias e escudos; druidas normalmente não usam metal",
        "armas": "Clavas, adagas, dardos, azagaias, maças, bordões, cimitarras, foices, fundas e lanças",
        "ferramentas": "Kit de herbalismo",
        "pericias": "Escolha 2 entre: Arcanismo, Adestrar Animais, Intuição, Medicina, Natureza, Percepção, Religião e Sobrevivência",
        "equipamento": "Escudo de madeira ou arma simples; cimitarra ou arma corpo a corpo simples; armadura de couro, pacote de explorador e foco druídico.",
    },
    "feiticeiro": {
        "armaduras": "Nenhuma",
        "armas": "Adagas, dardos, fundas, bordões e bestas leves",
        "ferramentas": "Nenhuma",
        "pericias": "Escolha 2 entre: Arcanismo, Enganação, Intuição, Intimidação, Persuasão e Religião",
        "equipamento": "Besta leve e virotes ou arma simples; bolsa de componentes ou foco arcano; pacote de explorador ou aventureiro; duas adagas.",
    },
    "guerreiro": {
        "armaduras": "Todas as armaduras e escudos",
        "armas": "Armas simples e armas marciais",
        "ferramentas": "Nenhuma",
        "pericias": "Escolha 2 entre: Acrobacia, Adestrar Animais, Atletismo, História, Intuição, Intimidação, Percepção e Sobrevivência",
        "equipamento": "Cota de malha ou armadura de couro, arco longo e flechas; arma marcial e escudo ou duas armas marciais; besta leve ou machadinhas; pacote de aventureiro ou explorador.",
    },
    "ladino": {
        "armaduras": "Armaduras leves",
        "armas": "Armas simples, bestas de mão, espadas longas, rapieiras e espadas curtas",
        "ferramentas": "Ferramentas de ladrão",
        "pericias": "Escolha 4 entre: Acrobacia, Atletismo, Atuação, Enganação, Furtividade, Intimidação, Intuição, Investigação, Percepção, Persuasão e Prestidigitação",
        "equipamento": "Rapieira ou espada curta; arco curto e flechas ou espada curta; pacote de assaltante, aventureiro ou explorador; armadura de couro, duas adagas e ferramentas de ladrão.",
    },
    "mago": {
        "armaduras": "Nenhuma",
        "armas": "Adagas, dardos, fundas, bordões e bestas leves",
        "ferramentas": "Nenhuma",
        "pericias": "Escolha 2 entre: Arcanismo, História, Intuição, Investigação, Medicina e Religião",
        "equipamento": "Bordão ou adaga; bolsa de componentes ou foco arcano; pacote de estudioso ou explorador; grimório.",
    },
    "monge": {
        "armaduras": "Nenhuma",
        "armas": "Armas simples e espadas curtas",
        "ferramentas": "Um tipo de ferramenta de artesão ou instrumento musical",
        "pericias": "Escolha 2 entre: Acrobacia, Atletismo, Furtividade, História, Intuição e Religião",
        "equipamento": "Espada curta ou arma simples; pacote de aventureiro ou explorador; 10 dardos.",
    },
    "paladino": {
        "armaduras": "Todas as armaduras e escudos",
        "armas": "Armas simples e armas marciais",
        "ferramentas": "Nenhuma",
        "pericias": "Escolha 2 entre: Atletismo, Intuição, Intimidação, Medicina, Persuasão e Religião",
        "equipamento": "Arma marcial e escudo ou duas armas marciais; azagaias ou arma corpo a corpo simples; pacote de sacerdote ou explorador; cota de malha e símbolo sagrado.",
    },
    "patrulheiro": {
        "armaduras": "Armaduras leves, armaduras médias e escudos",
        "armas": "Armas simples e armas marciais",
        "ferramentas": "Nenhuma",
        "pericias": "Escolha 3 entre: Adestrar Animais, Atletismo, Furtividade, Intuição, Investigação, Natureza, Percepção e Sobrevivência",
        "equipamento": "Brunea ou armadura de couro; duas espadas curtas ou duas armas corpo a corpo simples; pacote de explorador ou aventureiro; arco longo e aljava com flechas.",
    },
}

FEATURE_DESCRIPTIONS = {
    "Fúria": "Estado de combate que aumenta o dano corpo a corpo com Força e melhora a resistência do bárbaro enquanto durar.",
    "Defesa sem Armadura": "Permite calcular a CA sem armadura usando atributos físicos, mantendo mobilidade e proteção natural.",
    "Ataque Imprudente": "Troca segurança por agressividade: facilita seus ataques corpo a corpo, mas deixa você mais exposto até o próximo turno.",
    "Sentido de Perigo": "Instinto aguçado para evitar ameaças visíveis, especialmente armadilhas, explosões e efeitos repentinos.",
    "Ataque Extra": "Permite fazer mais de um ataque quando usa a ação Atacar.",
    "Movimento Rápido": "Aumenta o deslocamento quando o bárbaro não está usando armadura pesada.",
    "Instinto Selvagem": "Melhora a iniciativa e ajuda o bárbaro a agir rapidamente no começo do combate.",
    "Crítico Brutal": "Aumenta o impacto dos acertos críticos com armas corpo a corpo.",
    "Fúria Persistente": "Torna a fúria mais difícil de encerrar antes da hora.",
    "Poder Indomável": "Ajuda testes de Força a refletirem a potência física extrema do bárbaro.",
    "Campeão Primitivo": "Representa o ápice físico do bárbaro, elevando Força e Constituição.",
    "Inspiração de Bardo": "Concede dados de inspiração a aliados para melhorar testes, ataques ou resistências importantes.",
    "Conjuração": "Permite lançar magias da lista da classe usando a habilidade de conjuração correspondente.",
    "Versatilidade": "Concede bônus parcial em testes nos quais o bardo ainda não é proficiente.",
    "Canção de Descanso": "Melhora a recuperação do grupo durante descansos curtos.",
    "Especialização": "Dobra o bônus de proficiência em perícias escolhidas.",
    "Fonte de Inspiração": "Recupera usos de Inspiração de Bardo com mais frequência.",
    "Contra-encantamento": "Ajuda aliados próximos contra efeitos que encantam ou amedrontam.",
    "Segredos Mágicos": "Permite aprender magias de outras listas, ampliando muito a flexibilidade do bardo.",
    "Inspiração Superior": "Garante recurso mínimo de inspiração quando o bardo começa um combate sem usos.",
    "Domínio Divino": "Define o foco sagrado do clérigo, concedendo magias e características ligadas ao domínio escolhido.",
    "Canalizar Divindade": "Usa poder divino para produzir efeitos especiais definidos pela classe e pelo domínio.",
    "Destruir Mortos-vivos": "Aprimora a expulsão de mortos-vivos, destruindo criaturas mais fracas conforme o nível aumenta.",
    "Intervenção Divina": "Permite pedir auxílio direto da divindade em situações críticas.",
    "Druídico": "Idioma secreto dos druidas, usado para comunicação discreta entre iniciados.",
    "Forma Selvagem": "Permite assumir formas de animais, útil para exploração, infiltração e combate conforme o círculo.",
    "Corpo Atemporal": "Reduz os efeitos do envelhecimento natural sobre o druida.",
    "Magias Bestiais": "Permite conjurar mesmo em forma selvagem em níveis altos.",
    "Arquedruida": "Remove limitações importantes da Forma Selvagem no auge da classe.",
    "Origem Feiticeira": "Define a fonte inata da magia do feiticeiro e concede características temáticas.",
    "Fonte de Magia": "Cria pontos de feitiçaria para converter recursos e alimentar metamagia.",
    "Metamagia": "Modifica magias no momento da conjuração, alterando alcance, duração, alvo ou efeito.",
    "Restauração Mística": "Recupera parte dos recursos mágicos quando o feiticeiro está sem pontos de feitiçaria.",
    "Estilo de Luta": "Escolhe uma especialização marcial, como defesa, arquearia ou combate com armas específicas.",
    "Retomar o Fôlego": "Recupera pontos de vida rapidamente durante o combate.",
    "Surto de Ação": "Concede uma ação adicional em momentos decisivos.",
    "Arquétipo Marcial": "Define a especialização avançada do guerreiro.",
    "Indomável": "Permite repetir testes de resistência malsucedidos.",
    "Ataque Furtivo": "Adiciona dano quando o ladino ataca com vantagem ou explora distrações do alvo.",
    "Gíria de Ladrão": "Linguagem codificada para transmitir mensagens ocultas entre criminosos e contatos.",
    "Ação Ardilosa": "Permite usar ações de mobilidade e furtividade como ação bônus.",
    "Arquétipo de Ladino": "Define a especialidade do ladino, como assassinato, furto ou magia arcana.",
    "Esquiva Sobrenatural": "Reduz dano de um ataque percebido pelo ladino.",
    "Evasão": "Melhora a sobrevivência contra efeitos de área baseados em Destreza.",
    "Talento Confiável": "Torna perícias treinadas muito consistentes.",
    "Sentido Cego": "Ajuda a perceber criaturas escondidas próximas.",
    "Mente Escorregadia": "Fortalece resistência mental contra efeitos perigosos.",
    "Elusivo": "Dificulta que inimigos tenham vantagem contra o ladino.",
    "Golpe de Sorte": "Permite transformar uma falha importante em sucesso.",
    "Recuperação Arcana": "Recupera parte dos espaços de magia após descanso curto.",
    "Tradição Arcana": "Define a escola ou abordagem mágica principal do mago.",
    "Domínio de Magia": "Permite lançar certas magias de baixo nível com grande frequência.",
    "Magias Assinatura": "Seleciona magias confiáveis que ficam sempre prontas para uso.",
    "Artes Marciais": "Permite lutar com golpes desarmados e armas de monge usando agilidade e técnica.",
    "Ki": "Recurso interno usado para técnicas especiais, mobilidade e ataques aprimorados.",
    "Movimento sem Armadura": "Aumenta a velocidade do monge sem armadura e escudo.",
    "Tradição Monástica": "Define o caminho espiritual e marcial seguido pelo monge.",
    "Defletir Mísseis": "Reduz ou devolve projéteis recebidos.",
    "Queda Lenta": "Reduz dano de queda usando controle corporal.",
    "Ataque Atordoante": "Gasta ki para tentar deixar um inimigo atordoado após acertá-lo.",
    "Golpes de Ki": "Faz ataques desarmados contarem como mágicos contra resistências.",
    "Mente Tranquila": "Ajuda a encerrar efeitos de medo ou encantamento.",
    "Pureza Corporal": "Protege contra doença e veneno.",
    "Idioma do Sol e da Lua": "Permite comunicar-se com praticamente qualquer criatura que fale um idioma.",
    "Alma de Diamante": "Aprimora testes de resistência e permite gastar ki para repetir falhas.",
    "Corpo Atemporal": "Reduz efeitos físicos do envelhecimento e necessidades corporais.",
    "Corpo Vazio": "Permite desaparecer parcialmente da percepção e acessar formas superiores de existência.",
    "Autoperfeição": "Restaura ki quando o monge começa sem recursos.",
    "Sentido Divino": "Detecta presenças celestiais, infernais ou mortas-vivas próximas.",
    "Cura pelas Mãos": "Reserva de cura que o paladino pode distribuir por toque.",
    "Destruição Divina": "Gasta magia ao acertar para causar dano radiante adicional.",
    "Saúde Divina": "Protege o paladino contra doenças.",
    "Juramento Sagrado": "Define o código, poderes e características do paladino.",
    "Aura de Proteção": "Melhora testes de resistência de aliados próximos com a força do carisma do paladino.",
    "Aura de Coragem": "Protege aliados próximos contra medo.",
    "Destruição Divina Aprimorada": "Adiciona dano radiante constante aos ataques do paladino.",
    "Toque Purificador": "Encerra magias prejudiciais em si ou em aliados.",
    "Inimigo Favorito": "Concede vantagem temática e conhecimento contra tipos de inimigos escolhidos.",
    "Explorador Natural": "Melhora viagem, rastreamento e sobrevivência em terrenos favorecidos.",
    "Arquétipo de Patrulheiro": "Define o estilo avançado do patrulheiro, como caça especializada ou companheiro animal.",
    "Consciência Primitiva": "Usa magia para perceber certos tipos de criatura na região.",
    "Passo da Terra": "Facilita mover-se por terreno difícil natural.",
    "Esconder-se à Plena Vista": "Permite preparar camuflagem para esconder-se melhor.",
    "Desaparecer": "Melhora furtividade e mobilidade evasiva.",
    "Sentidos Selvagens": "Ajuda a lidar com inimigos invisíveis próximos.",
    "Matador de Inimigos": "Permite aplicar Sabedoria para melhorar ataques ou dano contra inimigos favorecidos.",
    "Patrono Transcendental": "Define a entidade que concede poder ao bruxo e molda suas características.",
    "Magia de Pacto": "Sistema próprio de conjuração do bruxo, com poucos espaços que retornam em descanso curto.",
    "Invocações Místicas": "Personalizações mágicas permanentes que alteram magias, sentidos ou capacidades do bruxo.",
    "Dádiva do Pacto": "Presente sobrenatural do patrono, como tomo, lâmina ou familiar.",
    "Arcana Mística": "Concede acesso a magias poderosas de níveis altos.",
    "Mestre Místico": "Permite recuperar rapidamente espaços de Magia de Pacto.",
}

SUBCLASS_DESCRIPTIONS = {
    "Caminho do Berserker": "Bárbaro focado em violência direta, ataques extras e presença intimidadora.",
    "Caminho do Totem": "Bárbaro guiado por espíritos animais, com escolhas defensivas, móveis ou agressivas.",
    "Colégio do Conhecimento": "Bardo estudioso e versátil, excelente em perícias, interrupções e magias adicionais.",
    "Colégio da Bravura": "Bardo marcial que inspira aliados no combate e usa armas e armaduras com mais eficiência.",
    "Domínio do Conhecimento": "Clérigo voltado a idiomas, perícias e revelação de informações.",
    "Domínio da Enganação": "Clérigo de ilusão, duplicidade e manipulação tática.",
    "Domínio da Guerra": "Clérigo armado para liderar e ferir no campo de batalha.",
    "Domínio da Luz": "Clérigo especializado em fogo, luz e expulsão de trevas.",
    "Domínio da Natureza": "Clérigo ligado a animais, plantas e forças naturais.",
    "Domínio da Tempestade": "Clérigo de trovão, relâmpago e punição explosiva.",
    "Domínio da Vida": "Clérigo focado em cura, proteção e sustentação do grupo.",
    "Círculo da Terra": "Druida conectado a um tipo de terreno, com conjuração ampliada e recuperação mágica.",
    "Círculo da Lua": "Druida que aprimora a Forma Selvagem para combate e resistência.",
    "Linhagem Dracônica": "Feiticeiro marcado por ancestralidade dracônica, ganhando resistência e poder elemental.",
    "Magia Selvagem": "Feiticeiro instável, com surtos mágicos imprevisíveis e manipulação de sorte.",
    "Campeão": "Guerreiro simples e letal, com foco em acertos críticos, atletismo e consistência.",
    "Mestre de Batalha": "Guerreiro tático que usa manobras para controlar, proteger e causar dano.",
    "Cavaleiro Místico": "Guerreiro que combina armas com magia defensiva e ofensiva de mago.",
    "Assassino": "Ladino especializado em infiltração, disfarce e golpes devastadores contra alvos desprevenidos.",
    "Ladrão": "Ladino ágil em furtos, escalada, uso de objetos e exploração.",
    "Trapaceiro Arcano": "Ladino que combina furtividade com ilusões e encantamentos.",
    "Escola de Abjuração": "Mago protetor, especializado em barreiras, contramágica e defesa arcana.",
    "Escola de Adivinhação": "Mago que manipula presságios, informação e resultados importantes.",
    "Escola de Conjuração": "Mago focado em invocar criaturas, objetos e transporte mágico.",
    "Escola de Encantamento": "Mago especializado em influência mental e controle social.",
    "Escola de Evocação": "Mago de dano elemental e explosões controladas.",
    "Escola de Ilusão": "Mago que molda percepção, imagem e engano mágico.",
    "Escola de Necromancia": "Mago que manipula energia vital, morte e mortos-vivos.",
    "Escola de Transmutação": "Mago que altera matéria, corpo e propriedades físicas.",
    "Caminho da Mão Aberta": "Monge de controle corporal e golpes precisos que derrubam, empurram e neutralizam.",
    "Caminho das Sombras": "Monge furtivo, ligado a escuridão, silêncio e deslocamento sombrio.",
    "Caminho dos Quatro Elementos": "Monge que canaliza ki em técnicas elementais.",
    "Juramento da Devoção": "Paladino clássico de honra, proteção, pureza e combate ao mal.",
    "Juramento dos Anciões": "Paladino ligado à luz, esperança e preservação da vida.",
    "Juramento da Vingança": "Paladino caçador, focado em perseguir e destruir inimigos prioritários.",
    "Caçador": "Patrulheiro especialista em enfrentar criaturas perigosas com técnicas de caça.",
    "Mestre das Bestas": "Patrulheiro que luta ao lado de um companheiro animal.",
    "O Arquifada": "Bruxo ligado a uma entidade feérica, com charme, medo e truques de presença.",
    "O Corruptor": "Bruxo pactuado com poder infernal, voltado a sobrevivência e dano destrutivo.",
    "O Grande Antigo": "Bruxo conectado a uma mente alienígena, com telepatia e influência psíquica.",
}


def slug(value: str) -> str:
    text = value.lower()
    table = str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc")
    text = text.translate(table)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def prof_bonus(level: int) -> int:
    return 2 + ((level - 1) // 4)


def class_table(features: list[str]) -> list[dict]:
    if features and isinstance(features[0], tuple):
        by_level = {}
        for level, name, _description in features:
            by_level.setdefault(level, []).append(name)
        rows = []
        for level in range(1, 21):
            known = list(by_level.get(level, []))
            if level in {4, 8, 12, 16, 19}:
                known.append("Incremento no Valor de Habilidade")
            rows.append({
                "nivel": level,
                "bonus_proficiencia": prof_bonus(level),
                "habilidades": known or ["—"],
            })
        return rows

    rows = []
    for level in range(1, 21):
        known = []
        if level <= len(features):
            known.append(features[level - 1])
        if level in {4, 8, 12, 16, 19}:
            known.append("Incremento no Valor de Habilidade")
        rows.append({
            "nivel": level,
            "bonus_proficiencia": prof_bonus(level),
            "habilidades": known or ["—"],
        })
    return rows


def subclass(name: str, class_name: str, access_level: int) -> dict:
    class_id = slug(class_name)
    page_print, page_pdf = CLASS_PAGES.get(class_id, (None, None))
    return {
        "id": slug(f"{class_name}-{name}"),
        "nome": name,
        "nivel_acesso": access_level,
        "fonte": "Livro do Jogador",
        "fonte_sigla": "LJ",
        "pagina_livro": page_print,
        "pagina_pdf": page_pdf,
        "referencia": f"{page_print} (PDF: {page_pdf})" if page_print and page_pdf else "Livro do Jogador",
        "descricao": SUBCLASS_DETAILS.get(name) or SUBCLASS_DESCRIPTIONS.get(name, ""),
        "habilidades": [
            {"nivel": access_level, "nome": f"Características de {name}", "descricao": ""}
        ],
    }


def build_classes() -> list[dict]:
    classes = []
    for ident, name, hit_die, saves, access_level, subclasses, features in CLASS_SPECS:
        page_print, page_pdf = CLASS_PAGES.get(ident, (None, None))
        profs = CLASS_PROFICIENCIES[ident]
        feature_details = FEATURE_DETAILS.get(ident)
        if feature_details:
            features_for_table = feature_details
            feature_payload = [
                {"nivel": level, "nome": feature_name, "descricao": description}
                for level, feature_name, description in feature_details
            ]
        else:
            features_for_table = features
            feature_payload = [
                {"nivel": idx + 1, "nome": feature, "descricao": FEATURE_DESCRIPTIONS.get(feature, "")}
                for idx, feature in enumerate(features)
            ]
        classes.append({
            "id": ident,
            "nome": name,
            "tipo": "Classe",
            "descricao_lore": f"{name} é uma classe base do Livro do Jogador com progressão completa de níveis 1 a 20.",
            "dado_de_vida": hit_die,
            "proficiencias_armadura": profs["armaduras"],
            "proficiencias_armas": profs["armas"],
            "proficiencias_ferramentas": profs["ferramentas"],
            "testes_resistencia": [part.strip() for part in saves.split(",")],
            "pericias_opcoes": profs["pericias"],
            "equipamento_inicial": profs["equipamento"],
            "habilidades_classe": feature_payload,
            "tabela_niveis": class_table(features_for_table),
            "sub_classes": [subclass(sub, name, access_level) for sub in subclasses],
            "fonte": "Livro do Jogador",
            "fonte_sigla": "LJ",
            "pagina_livro": page_print,
            "pagina_pdf": page_pdf,
            "referencia": f"{page_print} (PDF: {page_pdf})" if page_print and page_pdf else "Livro do Jogador",
        })
    return classes


def main() -> int:
    races = json.loads(RACES_SOURCE.read_text(encoding="utf-8"))
    data = {
        "racas": races,
        "classes": build_classes(),
        "meta": {
            "fontes": ["Livro do Jogador"],
            "observacao": "Base estrutural inicial gerada para integração do módulo; textos longos devem ser revisados contra PDF/Docling HTML.",
        },
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Gerado {OUTPUT} com {len(data['racas'])} raças e {len(data['classes'])} classes LJ.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
