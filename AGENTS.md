# AGENTS.md — Projeto D1

## Sobre o Projeto

**Projeto D1** (codinome: "Deu 1 no Dado") — sistema de referência completa de D&D 5e em Português Brasileiro. Cada módulo é independente, mas no final serão integrados em um dashboard único. Presente para o Henrique (mestre da mesa).

## Stack

- **Frontend:** HTML/CSS/JS puro (single-file, sem frameworks)
- **Dados:** JSON embutido no JavaScript (extraído de PDFs via Docling + Python)
- **Armazenamento:** LocalStorage (fichas de personagem)
- **Publicação:** GitHub Pages (branch `gh-pages`)
- **Extração:** Docling CLI (PDF→Markdown→JSON) + Python scripts

## Repositório

- **GitHub:** github.com/Er3mit4/grimoire-dd5e
- **URL:** er3mit4.github.io/grimoire-dd5e
- **Branch principal:** `gh-pages`
- **Pasta local:** `~/Projeto D1/`

## Estrutura de Pastas

```
~/Projeto D1/
├── AGENTS.md              ← Este arquivo (regras do projeto)
├── DESIGN.md              ← Padrão visual e estrutural dos módulos
├── D&D Companion.md        ← Plano geral (fases e módulos)
│
├── Grimorio/               ← Módulo: Grimório (Fase 1)
│   ├── grimoire-dd5e-gh-pages/ ← Espelho/publicação gh-pages
│   │   ├── index.html      ←   App publicado
│   │   ├── template.html   ←   Template sem dados
│   │   ├── build_html.py   ←   Injeta dados no template
│   │   ├── review_spells.py←   Revisão semântica das magias
│   │   ├── spells.json     ←   Dados finais das magias
│   │   ├── spells_reviewed.json ← JSON revisado semanticamente
│   │   ├── spells_raw.json ←   Dados brutos
│   │   ├── review_audit.json ← Relatório da revisão
│   │   └── class_lists.json←   Magias por classe
│   ├── index.html          ←   App publicado local
│   ├── template.html
│   ├── build_html.py
│   ├── review_spells.py
│   ├── spells_raw.json
│   ├── spells_reviewed.json
│   ├── spells.json
│   ├── review_audit.json
│   └── class_lists.json
│
├── Arsenal/                ← Módulo: Arsenal (Fase 2)
│   ├── index.html          ←   App publicado
│   ├── template.html       ←   Template sem dados
│   ├── build_html.py       ←   Injeta dados no template
│   ├── extract_arsenal.py  ←   Parser Docling → JSON
│   ├── review_arsenal.py   ←   Revisão semântica/auditoria do JSON
│   ├── validate_arsenal.py ←   Validação estrutural/sentinelas
│   ├── arsenal_raw.json    ←   Saída bruta do parser
│   ├── arsenal_reviewed.json ← JSON revisado semanticamente
│   ├── arsenal.json        ←   Dados finais dos itens
│   ├── arsenal_review_audit.json ← Relatório de auditoria da revisão
│   └── docling_out/        ←   Saída do Docling (JSONs brutos)
├── Bestiario/              ← Módulo: Bestiário (Fase 3)
│   ├── index.html          ←   App publicado
│   ├── template.html       ←   Template sem dados
│   ├── build_html.py       ←   Injeta dados no template
│   ├── extract_monsters.py ←   Parser Docling → JSON
│   ├── review_monsters.py  ←   Revisão semântica/auditoria do JSON
│   ├── monstros_raw.json   ←   Saída bruta do parser
│   ├── monstros_reviewed.json ← JSON revisado semanticamente
│   ├── monstros.json       ←   Dados finais dos monstros
│   ├── review_audit.json   ←   Relatório de auditoria da revisão
│   ├── prepare_docling_sources.py ←   Fatiar PDF em chunks
│   ├── run_docling_extraction.py  ←   Rodar Docling nos chunks
│   ├── docling_out/        ←   Saída do Docling (JSONs brutos)
│   └── docling_html_out/   ←   Saída do Docling em HTML para auditoria
├── RacasClasses/           ← Módulo: Raças & Classes (Fase 4)
├── Ficha/                  ← Módulo: Ficha de Personagem (Fase 5)
└── Dashboard/              ← Módulo: Dashboard integrado (Fase 6)
```

## PDFs Fonte

| Livro | Path | Status |
|-------|------|--------|
| Livro do Jogador | `D:\Documents\Sessão RPG\D&D\dd-5e-livro-do-jogador-fundo-branco-biblioteca-c3a9lfica.pdf` | ✅ Magias extraídas |
| Manual dos Monstros | `D:\Documents\Sessão RPG\D&D\old-dd-5e-manual-dos-monstros-biblioteca-elfica.pdf` | 🔧 Monstros extraídos/revisados (345) |
| Guia do Mestre | `D:\Documents\Sessão RPG\D&D\dd-5e-guia-do-mestre-biblioteca-elfica.pdf` | ✅ Itens extraídos/revisados (Arsenal) |

## Fases do Projeto

1. ✅ **Grimório** — Buscador de magias (361 magias, concluído)
2. 🔧 **Arsenal** — Itens, armas, armaduras, equipamentos (527 itens, revisado semanticamente)
3. 🔧 **Bestiário** — Monstros e criaturas (345 monstros, em revisão semântica)
4. 📋 **Raças & Classes** — Detalhes e tabelas
5. 📋 **Ficha de Personagem** — CRUD com localStorage
6. 📋 **Dashboard** — Tudo integrado em um app único

> Cada fase é um **módulo independente** na estrutura de pastas. No final, todos são integrados no Dashboard, mas mantêm separação pra evitar conflitos.

## Convenções

- **Idioma:** Toda a interface em PT-BR
- **Design:** Tema escuro fantasy (cores quentes, fontes Cinzel + Lora)
- **Referência de página:** Formato "XXX (PDF: YYY)" — livro impresso + PDF
- **Offline-first:** Tudo funciona sem internet
- **Single-file:** Cada módulo é um HTML autocontido (CSS + JS + dados embutidos)
- **Padrão visual:** Seguir o `DESIGN.md` para consistência entre módulos

## Workflow de Extração

1. Analisar estrutura do PDF (mapear páginas/capítulos)
2. Extrair via Docling em HTML: `docling "<PDF>" --output /tmp/docling_out --to html`
3. Criar script Python para parsear o HTML → JSON limpo
4. Revisar dados (completude, erros, duplicatas)
5. Injetar dados no template HTML via `build_html.py`
6. Testar via `python3 -m http.server` + browser
7. Commit + push pro GitHub Pages

> **Nota:** Extrair em HTML (`--to html`) ao invés de Markdown (`--to md`) preserva tabelas, formatação e estrutura do documento original. Use `--to md` apenas se precisar de texto limpo simples.

## Pipeline de Revisão Semântica dos Dados

Quando um módulo envolve muito conteúdo extraído de PDF (Bestiário, Raças & Classes, Arsenal avançado, etc.), não confiar apenas em parser determinístico. Use uma etapa de revisão semântica com agente/modelo menor para corrigir o JSON diretamente.

Pipeline recomendado:

1. **Extração bruta determinística**
   - O script Python deve gerar um arquivo intermediário `*_raw.json`.
   - Esse arquivo representa a saída do parser, sem correções manuais destrutivas.

2. **Revisão semântica por mini-agente**
   - Usar um subagente/modelo ágil disponível para revisar e reescrever o JSON estruturado.
   - O agente deve editar os dados, não criar mais regras de parser para cada caso isolado.
   - Escopo típico de escrita: `*_reviewed.json` e, quando apropriado, o JSON final.
   - Fontes de conferência: `*_raw.json`, saída Docling HTML/JSON, páginas/chunks do PDF e o JSON atual.

3. **Contrato do mini-agente**
   - Preservar o schema existente.
   - Não inventar texto, regras ou estatísticas.
   - Não resumir nem melhorar redação; apenas restaurar estrutura e classificação.
   - Separar corretamente lore/descrição, características, ações, reações, ações lendárias, idiomas, sentidos, perícias, resistências, imunidades, ND e XP.
   - Se não conseguir confirmar pela fonte disponível, manter o dado e registrar como `precisa conferência visual`.

4. **Arquivos intermediários**
   - Preferir a cadeia:
     - `*_raw.json` = saída do parser.
     - `*_reviewed.json` = dados corrigidos semanticamente.
     - `*.json` = dado final usado pelo app.
   - Manter um relatório de auditoria/checklist quando existir, por exemplo `review_audit.json`.

5. **Guarda-corpos determinísticos**
   - Scripts de auditoria ainda são úteis, mas devem bloquear problemas gerais, não substituir a revisão semântica.
   - Exemplos de bloqueio: ND ausente, JSON inválido, contagem inesperada de registros, rótulos óbvios vazando em campos errados, duplicatas e registros vazios.
   - Evitar transformar cada exceção visual do PDF em uma nova regex permanente se o mini-agente consegue corrigir o JSON com contexto.

6. **Validação final**
   - Rodar testes do módulo.
   - Conferir contagem de registros.
   - Conferir ausências críticas (`ND`, nome, página, campos obrigatórios).
   - Regerar o HTML final.
   - Fazer teste local via servidor/browser quando houver alteração visível.

Exemplo aplicado no Bestiário:

```text
extract_monsters.py -> monstros_raw.json
mini-agente/reviewer -> monstros_reviewed.json
fix_missing_nd.py -> monstros.json
build_html.py -> index.html
```

> Para futuras fases, adapte os nomes dos arquivos, mas preserve a ideia: parser gera base bruta, mini-agente corrige a estrutura semântica, scripts determinísticos validam o resultado.

## Workflow de Código

1. Planejar a alteração com requisitos claros
2. Implementar no workspace seguindo o `DESIGN.md`
3. Revisar dados/código gerados
4. Testar localmente (`python3 -m http.server` + browser)
5. Commit + push

## Pessoas Envolvidas

- **Ronald** — Idealizador, planejamento, testes
- **Henrique** — Mestre da mesa, usuário principal (presenteado)
- **Hermes** — Coordenação, extração de dados, revisão

---

*Última atualização: 19/05/2026*
