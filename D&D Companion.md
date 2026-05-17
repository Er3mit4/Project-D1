# D&D Companion

> Projeto pessoal — sistema de referência completa de D&D 5e em PT-BR, com dashboard integrado para consulta na mesa e gestão de fichas de personagem.

## Links

- 🔮 **Grimório (v1):** [er3mit4.github.io/grimoire-dd5e](https://er3mit4.github.io/grimoire-dd5e/)
- 📂 **Repositório:** [github.com/Er3mit4/grimoire-dd5e](https://github.com/Er3mit4/grimoire-dd5e)
- 📁 **Arquivos locais:** `~/dd-spells/grimoire/` (WSL)
- 📖 **PDF base:** `D:\Documents\Sessão RPG\D&D\dd-5e-livro-do-jogador-fundo-branco-biblioteca-c3a9lfica.pdf`

---

## Fase 1 — Grimoire ✅ (concluído)

- 346 magias do Livro do Jogador (PT-BR)
- Busca em tempo real por nome
- Filtros por nível, escola e classe
- Descrição completa + referência de página (livro e PDF)
- Tema escuro fantasy, responsivo (celular e desktop)
- Funciona offline (HTML estático, dados embutidos)
- Publicado no GitHub Pages

---

## Fase 2 — Arsenal 📋 (planejado)

- Itens mágicos, armas, armaduras, equipamentos
- Poções, scrolls, artefatos
- Mesma interface: busca, filtros, descrição + referência de página
- **Fonte:** Livro do Jogador + Guia do Mestre

---

## Fase 3 — Bestiário 📋 (planejado)

- Monstros e criaturas com ficha completa
- Filtros por tipo, ND (CR), ambiente, tamanho
- **Fonte:** Manual dos Monstros

---

## Fase 4 — Raças & Classes 📋 (planejado)

- Detalhes de raças, subclasses, habilidades
- Tabelas de características por nível
- **Fonte:** Livro do Jogador

---

## Fase 5 — Ficha de Personagem 📋 (planejado)

- Criar, salvar e editar fichas localmente (localStorage)
- Cálculo automático de modificadores, CA, bônus
- Gerenciamento de PV, magias preparadas, equipamento
- Exportar/importar ficha (JSON)
- Integração com Grimório (magias) e Arsenal (equipamentos)

---

## Fase 6 — Dashboard Completo 📋 (planejado)

- Tela inicial com tudo integrado
- Personagem → magias, itens, equipamentos vinculados
- Quick reference pra mesa (regras rápidas, condições, etc.)

---

## Arquitetura

- **HTML estático** — funciona offline, sem servidor
- **Dados embutidos** em JSON (extraídos dos PDFs via script Python)
- **LocalStorage** para salvar fichas de personagem
- **Repositório único** no GitHub com GitHub Pages
- **OpenCode CLI** para geração de código (Hermes planeja e revisa)

## Livros necessários

- ✅ Livro do Jogador (magias já extraídas)
- 📖 Manual dos Monstros
- 📖 Guia do Mestre (itens mágicos, tesouros)

## Ferramentas

- Extração: Python + pymupdf (venv em `~/dd-spells/`)
- Código: OpenCode CLI v1.15.3 (`~/.opencode/bin/opencode`)
- Versionamento: Git + GitHub (conta: Er3mit4)
- Publicação: GitHub Pages

---

*Última atualização: 17/05/2026*
