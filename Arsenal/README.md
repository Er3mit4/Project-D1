# Arsenal

Fase 2 do Projeto D1: consulta de equipamentos e itens magicos de D&D 5e em PT-BR.

## Fontes v1

- Livro do Jogador: `D:\Documents\Sessão RPG\D&D\dd-5e-livro-do-jogador-fundo-branco-biblioteca-c3a9lfica.pdf`
- Guia do Mestre: `D:\Documents\Sessão RPG\D&D\dd-5e-guia-do-mestre-biblioteca-elfica.pdf`
- Guia de Xanathar para Todas as Coisas: `D:\Documents\Sessão RPG\D&D\dd-5e-guia-de-xanathar-para-todas-as-coisas-fundo-branco-biblioteca-elfica.pdf`

## Escopo

- Inclui equipamentos mundanos do Livro do Jogador.
- Inclui itens magicos do Guia do Mestre.
- Inclui itens magicos comuns do Guia de Xanathar para Todas as Coisas.
- Inclui filtro "Usável por classe" derivado das proficiencias base de classes do Livro do Jogador.

## Proficiência por classe

O campo `classes` em `arsenal.json` e derivado de proficiencias base de classe:

- Armas: grupos simples/marciais e excecoes especificas de classe.
- Armaduras: leve, media, pesada e escudo.
- Ferramentas: proficiencias especificas e escolhas amplas como instrumento musical/ferramentas de artesao.
- Itens sem proficiencia requerida aparecem como usaveis por todas as classes.

Subclasses, dominios, talentos, multiclasse e escolhas individuais de antecedente ainda nao sao modelados no v1.

## Ambiente

Use o venv compartilhado do projeto:

```powershell
.venv\Scripts\python.exe
.venv\Scripts\docling.exe
```

## Pipeline Docling

O Docling deve rodar em recortes por secao, nao no PDF completo. O PDF inteiro com OCR/tabelas padrao pode falhar com `std::bad_alloc` no Windows.

```powershell
.venv\Scripts\python.exe Arsenal\run_docling_extraction.py
.venv\Scripts\python.exe Arsenal\extract_arsenal.py
.venv\Scripts\python.exe Arsenal\validate_arsenal.py Arsenal\arsenal.json
.venv\Scripts\python.exe Arsenal\build_html.py
```

Configuracao usada:

- Livro do Jogador: paginas PDF 145-161, `--no-ocr`, `--page-batch-size 1`, `--num-threads 1`, `--pdf-backend pypdfium2`, `--table-mode accurate`.
- Guia do Mestre: paginas PDF 151-220 e 221-229, `--no-ocr`, `--no-tables`, `--page-batch-size 1`, `--num-threads 1`, `--pdf-backend pypdfium2`.
- Guia de Xanathar: paginas PDF 136-139, `--no-ocr`, `--no-tables`, `--page-batch-size 1`, `--num-threads 1`, `--pdf-backend pypdfium2`.
- O parser ordena os textos dos livros de itens magicos por pagina, coluna e posicao vertical antes de montar os itens.
