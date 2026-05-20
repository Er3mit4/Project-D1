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

## Fase 6 — Dashboard Completo ✅ (concluído)

- Tela inicial com design bento fantasy e estatísticas gerais
- Todos os módulos integrados em uma única SPA (Grimório, Arsenal e Bestiário)
- Navegação instantânea e responsiva por hash routing
- Barra de filtros lateral à direita integrada com controle de layout dinâmico
- Busca sincronizada em tempo real (desktop no header, mobile no corpo)

---

## Arquitetura

- **App unificado** — SPA estática na raiz (`index.html`), compilada a partir de `unified_template.html`
- **Módulos legados** — preservam scripts, dados e páginas legadas de manutenção para extração e rebuild
- **Design System moderno** — Tailwind CSS CDN + fontes `EB Garamond` e `Hanken Grotesk`
- **Offline-first** — funciona offline, sem servidor externo, com dados JSON embutidos
- **Repo unificado** no GitHub: `Er3mit4/Project-D1`
- **Assistente de IA / Codex** para implementação direta e revisão

## Livros necessários

- ✅ Livro do Jogador (magias extraídas)
- ✅ Guia do Mestre (itens mágicos e equipamentos extraídos)
- ✅ Manual dos Monstros (monstros extraídos e revisados)

## Ferramentas

- Extração: Docling CLI (local, GPU) + Python scripts
- Compilação: Script `build_unified.py` para injetar os dados no template da raiz
- Versionamento: Git + GitHub (conta: Er3mit4)
- Publicação: GitHub Pages

---

*Última atualização: 20/05/2026*
