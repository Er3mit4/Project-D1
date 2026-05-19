# Arsenal v1 Design

## Contexto

O Arsenal e a Fase 2 do Projeto D1. Ele deve seguir o mesmo contrato geral do Grimorio: modulo independente, HTML estatico autocontido, interface em PT-BR, dados JSON embutidos no JavaScript, funcionamento offline e visual dark fantasy com fontes Cinzel e Lora.

O Grimorio esta concluido e serve como referencia de experiencia: busca rapida, filtros laterais, cards/listagem, painel de detalhe e referencias de pagina. O Arsenal nao deve depender tecnicamente do Grimorio agora; a integracao entre modulos fica para a fase Dashboard.

## Escopo Aprovado

Arsenal v1 inclui duas fontes:

- Livro do Jogador: equipamentos mundanos, armas, armaduras, ferramentas, montarias, veiculos, servicos, despesas e bens comerciais.
- Guia do Mestre: itens magicos, pocoes, pergaminhos, artefatos, raridade, sintonizacao e propriedades relevantes.

Fora do v1:

- Guia de Xanathar para Todas as Coisas.
- Integracao com fichas de personagem.
- Dashboard integrado.
- Compras/carrinho/inventario persistente.
- Calculos complexos de carga ou economia.

## Objetivo

Entregar um modulo consultavel chamado Arsenal, em PT-BR, para encontrar rapidamente equipamentos e itens magicos durante a mesa de D&D 5e. O usuario deve conseguir buscar por nome, filtrar por categoria, tipo, fonte, raridade e sintonizacao, e abrir uma ficha de detalhe com descricao completa e referencia de pagina no formato `XXX (PDF: YYY)`.

## Fontes

Os PDFs ficam em `D:\Documents\Sessão RPG\D&D` no Windows local.

Fontes do v1:

- `dd-5e-livro-do-jogador-fundo-branco-biblioteca-c3a9lfica.pdf`
- `dd-5e-guia-do-mestre-biblioteca-elfica.pdf`

O diretorio real usa acento em `Sessão RPG`. Scripts devem aceitar caminho Windows absoluto e nao assumir WSL, porque o ambiente atual nao possui distribuicao WSL instalada.

## Arquitetura

O modulo fica em `Arsenal/` e deve conter:

- `docling_out/`: saidas HTML/JSON brutas do Docling, quando geradas.
- `extract_arsenal.py`: parser/revisor para transformar as saidas do Docling em JSON estruturado.
- `arsenal_raw.json`: dados intermediarios, preservando campos de origem para auditoria.
- `arsenal.json`: dados finais usados pelo app.
- `template.html`: HTML/CSS/JS sem dados embutidos.
- `build_html.py`: injeta `arsenal.json` no template.
- `index.html`: app final autocontido.

O design favorece uma unica fonte JSON final, com itens de tipos diferentes normalizados no mesmo array. Campos especificos ficam opcionais conforme a categoria.

## Modelo De Dados

Cada item em `arsenal.json` deve usar campos estaveis:

```json
{
  "id": "espada-longa",
  "nome": "Espada longa",
  "categoria": "Arma",
  "tipo": "Arma marcial corpo a corpo",
  "fonte": "Livro do Jogador",
  "pagina_livro": 149,
  "pagina_pdf": 153,
  "referencia": "149 (PDF: 153)",
  "preco": "15 po",
  "peso": "1,5 kg",
  "raridade": null,
  "sintonizacao": false,
  "propriedades": ["Versatil"],
  "dano": "1d8 cortante",
  "descricao": "Texto em PT-BR preservado da fonte.",
  "tabela": null
}
```

Campos por categoria:

- Armas: dano, tipo de dano, propriedades, alcance, peso, preco.
- Armaduras: CA, furtividade, forca minima, peso, preco.
- Equipamentos: preco, peso, descricao, quantidade quando aplicavel.
- Ferramentas: categoria de ferramenta, preco, peso, uso.
- Montarias e veiculos: velocidade, capacidade, preco, descricao.
- Servicos/despesas/bens: preco, periodo/unidade, descricao.
- Itens magicos: raridade, sintonizacao, tipo, descricao, tabelas associadas quando houver.

## Interface

A tela inicial do Arsenal deve abrir diretamente na experiencia de consulta, sem landing page.

Controles esperados:

- Busca por nome e texto.
- Filtro por categoria.
- Filtro por tipo.
- Filtro por fonte.
- Filtro por raridade para itens magicos.
- Filtro por sintonizacao para itens magicos.
- Ordenacao por nome e, quando possivel, por categoria.
- Contador de resultados.
- Card/listagem compacta com nome, categoria, tipo, fonte e referencia.
- Painel de detalhe com propriedades estruturadas e descricao.

O visual deve seguir o Grimorio: tema escuro fantasy, cores quentes, tipografia Cinzel/Lora, layout responsivo para celular e desktop. A interface deve continuar util em mesa: leitura rapida, filtros previsiveis e texto sem excesso de decoracao.

## Fluxo De Extracao

1. Recortar os PDFs fonte nas faixas relevantes com `Arsenal/prepare_docling_sources.py`.
2. Rodar Docling por recorte com `Arsenal/run_docling_extraction.py`.
3. Parsear os JSONs do Docling com `Arsenal/extract_arsenal.py`.
4. Normalizar campos para `arsenal_raw.json` e `arsenal.json`.
5. Validar schema, contagens e itens sentinela com `validate_arsenal.py`.
6. Injetar dados no template com `build_html.py`.
7. Testar localmente com `python -m http.server` e browser.

Docling deve ser usado em JSON estruturado para esta fase. O comando contra o PDF completo nao e o caminho aprovado: ele falhou no Windows com `std::bad_alloc` durante preprocessamento. A configuracao estavel e:

- Livro do Jogador: recorte PDF 145-161, `--no-ocr`, `--page-batch-size 1`, `--num-threads 1`, `--pdf-backend pypdfium2`, `--table-mode accurate`.
- Guia do Mestre: recortes PDF 151-220 e 221-229, `--no-ocr`, `--no-tables`, `--page-batch-size 1`, `--num-threads 1`, `--pdf-backend pypdfium2`.

O parser deve ordenar os textos do Guia do Mestre por pagina, coluna e posicao vertical antes de detectar cabecalhos de itens magicos, porque a ordem bruta do Docling em paginas com duas colunas pode intercalar blocos.

## Validacao

Validacoes minimas:

- `arsenal.json` e JSON valido.
- Todos os itens possuem `id`, `nome`, `categoria`, `fonte` e `referencia`.
- Nao ha `id` duplicado.
- Filtros do app retornam resultados coerentes para categorias principais.
- Busca encontra itens por nome e por texto de descricao.
- App abre sem internet depois de gerado.

## Riscos

- As tabelas do Guia do Mestre podem exigir ajustes manuais por causa de quebras de pagina e itens com descricoes longas.
- O PDF do Livro do Jogador tem pagina impressa diferente da pagina do arquivo; a referencia deve ser conferida em amostras antes de processar tudo.
- Dependencias de extracao devem ser compartilhadas no venv raiz do projeto, em `.venv/`, para que Grimorio, Arsenal e fases futuras usem a mesma instalacao. Se houver Docling global no Windows, ele pode ser usado quando estiver no PATH da sessao; caso contrario, use `.venv\Scripts\docling.exe`.
- Caminhos com acentos devem ser tratados por `pathlib.Path` e strings Unicode no Python.

## Criterio De Pronto

O Arsenal v1 esta pronto quando `Arsenal/index.html` abre localmente, contem dados do Livro do Jogador e do Guia do Mestre, permite busca/filtros principais, mostra detalhes com referencia de pagina e passa nas validacoes de JSON/dados/app.
