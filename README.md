# Projeto D1

Sistema unificado de referência completa de D&D 5e em Português Brasileiro, desenvolvido para consulta rápida e dinâmica durante as sessões de RPG. O aplicativo consolida Grimório, Arsenal, Bestiário e Raças & Classes em uma SPA responsiva de alta performance.

## Módulos Integrados

- **Início**: Painel principal decorado no estilo bento fantasy, apresentando atalhos e contagens gerais.
- **Grimório**: Consulta rápida e detalhada de 361 magias do Livro do Jogador.
- **Arsenal**: Equipamentos, armas, armaduras e 527 itens mágicos do Guia do Mestre e Livro do Jogador.
- **Bestiário**: Ficha completa e estatísticas de combate de 345 monstros do Manual dos Monstros.
- **Raças & Classes**: Referência de criação de personagem com 9 raças, 12 classes, progressões 1–20, habilidades e 71 subclasses do Livro do Jogador e Guia de Xanathar.

## Stack e Arquitetura

- **Frontend:** SPA nativa escrita em HTML5 e JavaScript puro, estilizada de forma premium com Tailwind CSS CDN.
- **Tipografia & Ícones:** Combinação elegante de `EB Garamond` para tom medieval e `Hanken Grotesk` para legibilidade de estatísticas, com ícones do Google Material Symbols.
- **Dados:** JSON compactado e embutido no arquivo unificado, garantindo funcionamento **Offline-First**.
- **Extração & Compilação:** Pipelines em Python integrados com a ferramenta Docling CLI para parseamento de PDFs originais em dados estruturados de alta fidelidade.
- **Hospedagem:** Publicação estática rápida pelo GitHub Pages.

O site principal é gerado na raiz (`index.html`) por meio do script de build (`build_unified.py`) a partir do template (`unified_template.html`). As pastas dos módulos contêm os códigos de extração, auditoria de dados e arquivos legados.

Para atualizar o módulo de Raças & Classes, mantenha o fluxo local em `RacasClasses/`: extração/revisão dos JSONs, validação com `python RacasClasses\review_racas_classes.py` e rebuild do app unificado com `python build_unified.py`.

## Acesso Oficial

A visualização oficial do aplicativo pode ser acessada em:

👉 **[er3mit4.github.io/Project-D1](https://er3mit4.github.io/Project-D1/)**

## Nota Legal

Todo o conteúdo conceitual, marcas registradas e propriedades intelectuais referentes a Dungeons & Dragons (D&D) são de direito exclusivo da Wizards of the Coast LLC. Este é um projeto de fã sem fins comerciais, desenvolvido para uso pessoal e facilitação das sessões de jogo.
