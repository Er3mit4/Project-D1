# Projeto D1

> **"Deu 1 no Dado"** — sistema de referência completa de D&D 5e em PT-BR, com dashboard integrado para consulta na mesa e gestão de fichas de personagem. Desenvolvido para consulta e suporte rápido ao Mestre durante as sessões de jogo.

## Links

- 🎲 **Site unificado:** [er3mit4.github.io/Project-D1](https://er3mit4.github.io/Project-D1/)
- 📂 **Repositório:** [github.com/Er3mit4/Project-D1](https://github.com/Er3mit4/Project-D1)
- 🔮 **Grimório legado:** [er3mit4.github.io/grimoire-dd5e](https://er3mit4.github.io/grimoire-dd5e/)
- 📁 **Pasta local:** `~/Projeto D1/` (WSL)
- 📖 **PDF base:** `D:\Documents\Sessão RPG\D&D\dd-5e-livro-do-jogador-fundo-branco-biblioteca-c3a9lfica.pdf`

---

## Fase 1 — Grimório ✅ (concluído)

- 361 magias do Livro do Jogador (PT-BR)
- Busca em tempo real por nome
- Filtros por nível, escola e classe
- Descrição completa + referência de página (livro e PDF)
- Tema escuro fantasy, responsivo (celular e desktop)
- Funciona offline (HTML estático, dados embutidos)
- Publicado no GitHub Pages

---

## Fase 2 — Arsenal ✅ (revisado)

- Itens mágicos, armas, armaduras, equipamentos
- Poções, scrolls, artefatos
- Mesma interface: busca, filtros, descrição + referência de página
- **Fonte:** Livro do Jogador + Guia do Mestre

---

## Fase 3 — Bestiário ✅ (revisado)

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

- Tela inicial com todos os módulos integrados
- Personagem → magias, itens, equipamentos vinculados
- Quick reference pra mesa (regras rápidas, condições, etc.)

---

## Arquitetura

- **Módulos independentes** — cada fase é uma pasta separada (`Grimorio/`, `Arsenal/`, etc.)
- **HTML estático** — funciona offline, sem servidor
- **Dados embutidos** em JSON (extraídos dos PDFs via Docling + Python)
- **LocalStorage** para salvar fichas de personagem
- **Repo unificado** no GitHub: `Er3mit4/Project-D1`
- **Assistente de IA / Codex** para implementação direta e revisão

## Livros necessários

- ✅ Livro do Jogador (magias já extraídas)
- 📖 Manual dos Monstros
- 📖 Guia do Mestre (itens mágicos, tesouros)

## Ferramentas

- Extração: Docling CLI (local, GPU) + Python scripts
- Código: Assistente de IA / Codex implementa diretamente no workspace
- Versionamento: Git + GitHub (conta: Er3mit4)
- Publicação: GitHub Pages

---

*Última atualização: 19/05/2026*
