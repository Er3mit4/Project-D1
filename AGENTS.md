# AGENTS.md — D&D Companion

## Sobre o Projeto

Sistema de referência completa de D&D 5e em Português Brasileiro, com dashboard integrado para consulta na mesa de RPG e gestão de fichas de personagem. Presente para o Henrique (mestre da mesa).

## Stack

- **Frontend:** HTML/CSS/JS puro (single-file, sem frameworks)
- **Dados:** JSON embutido no JavaScript (extraído de PDFs via Python + pymupdf)
- **Armazenamento:** LocalStorage (fichas de personagem)
- **Publicação:** GitHub Pages (branch `gh-pages`)
- **Geração de código:** OpenCode CLI (`~/.opencode/bin/opencode`)
- **Extração:** Python 3 + pymupdf (venv em `~/dd-spells/`)

## Repositório

- **GitHub:** github.com/Er3mit4/grimoire-dd5e
- **URL:** er3mit4.github.io/grimoire-dd5e
- **Branch principal:** `gh-pages`
- **Arquivos locais (código):** `~/dd-spells/grimoire/`

## Estrutura de Pastas (Obsidian)

```
D&D Companion/
├── AGENTS.md          ← Este arquivo
├── D&D Companion.md   ← Plano do projeto (fases)
└── notas/             ← Notas e rascunhos
```

## Estrutura de Pastas (Código - WSL)

```
~/dd-spells/
├── bin/activate       ← venv Python (pymupdf)
├── grimoire/
│   ├── grimoire.html  ← App principal (HTML final)
│   ├── index.html     ← Cópia pra GitHub Pages
│   ├── template.html  ← Template HTML (sem dados)
│   ├── build_html.py  ← Script que injeta dados no template
│   ├── spells_raw.json    ← Dados brutos das magias
│   ├── class_lists.json   ← Magias por classe
│   └── extract_spells.py  ← Script de extração do PDF
└── raw_text.txt       ← Texto bruto extraído do PDF (debug)
```

## PDFs Fonte

| Livro | Path | Status |
|-------|------|--------|
| Livro do Jogador | `/mnt/d/Documents/Sessão RPG/D&D/dd-5e-livro-do-jogador-fundo-branco-biblioteca-c3a9lfica.pdf` | ✅ Magias extraídas |
| Manual dos Monstros | A definir | 📋 Pendente |
| Guia do Mestre | A definir | 📋 Pendente |

## Fases do Projeto

1. ✅ **Grimoire** — Buscador de magias (346 magias, concluído)
2. 📋 **Arsenal** — Itens, armas, armaduras, equipamentos
3. 📋 **Bestiário** — Monstros e criaturas
4. 📋 **Raças & Classes** — Detalhes e tabelas
5. 📋 **Ficha de Personagem** — CRUD com localStorage
6. 📋 **Dashboard** — Tudo integrado

## Convenções

- **Idioma:** Toda a interface em PT-BR
- **Design:** Tema escuro fantasy (cores quentes, fontes Cinzel + Lora)
- **Referência de página:** Formato "XXX (PDF: YYY)" — livro impresso + PDF
- **Offline-first:** Tudo funciona sem internet
- **Single-file:** Cada módulo é um HTML autocontido (CSS + JS + dados embutidos)
- **Código:** Sempre delegar criação de código bruto pro OpenCode CLI

## Workflow de Extração

1. Analisar estrutura do PDF (mapear páginas/capítulos)
2. Criar script Python de extração (`pymupdf`)
3. Rodar script → gerar JSON
4. Revisar dados (completude, erros, duplicatas)
5. Injetar dados no template HTML via `build_html.py`
6. Testar via `python3 -m http.server` + browser
7. Commit + push pro GitHub Pages

## Workflow de Código

1. Hermes planeja e escreve o prompt com requisitos
2. OpenCode gera/modifica o código (`opencode run '...'`)
3. Hermes revisa o resultado
4. Testa localmente
5. Commit + push

## Pessoas Envolvidas

- **Ronald** — Idealizador, planejamento, testes
- **Henrique** — Mestre da mesa, usuário principal (presenteado)
- **Hermes** — Coordenação, extração de dados, revisão
- **OpenCode** — Geração de código
