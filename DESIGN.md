# DESIGN.md — Projeto D1

> Padrão visual e estrutural dos módulos do Projeto D1. Toda nova página segue este documento.

---

## 1. Princípios

- **Single-file:** HTML + CSS + JS + dados JSON em um único arquivo
- **Offline-first:** sem dependências externas (exceto Google Fonts)
- **Responsivo:** funciona em celular e desktop
- **Tema escuro fantasy:** fundo escuro com acentos dourados
- **PT-BR:** toda a interface em português brasileiro
- **Consistência:** mesmo layout, componentes e interações em todos os módulos

---

## 2. Paleta de Cores (Tailwind CSS System)

O design system do **Projeto D1** utiliza Tailwind CSS com uma paleta de cores personalizada estendida no `tailwind.config` para preservar a atmosfera de fantasia e o contraste premium:

```javascript
colors: {
  // Fundos & Superfícies (Escala Obsidian/Dark)
  "background": "#141316",                 // Fundo geral do app
  "surface": "#141316",                    // Superfície básica
  "surface-container-lowest": "#0f0e11",   // Fundo mais profundo
  "surface-container-low": "#1c1b1e",      // Fundo dos cards fechados (antigo --card)
  "surface-container": "#201f22",          // Fundo dos inputs e painéis
  "surface-container-high": "#2b292d",     // Fundo dos cards expandidos
  
  // Cores de Texto (Contraste Papel/Pergaminho)
  "on-surface": "#e6e1e5",                 // Texto principal (antigo --fg)
  "on-surface-variant": "#d0c5b5",         // Texto secundário (antigo --fg2)
  "paper-text": "#e8dcc8",                 // Texto de pergaminho
  
  // Tons Metálicos (Latão & Ouro)
  "primary": "#e6c383",                    // Latão brilhante (bordas ativas, títulos de card)
  "primary-container": "#c9a86a",          // Dourado médio / Latão envelhecido
  "brass-accent": "#c9a86a",               // Acento de latão envelhecido
  
  // Elementos Temáticos
  "cantrip": "#8e44ad",                    // Roxo arcano (magias truques e itens mágicos)
  "ethereal-purple": "#4a3b63",            // Roxo de fundo (gradientes e decorações)
  "blood-crimson": "#632a2a",              // Vermelho sangue para monstros e ND
  "error": "#ffb4ab"                       // Texto de erro e destaque de combate
}
```

**Regra:** Evitar classes utilitárias de cores padrão do Tailwind (ex: `bg-red-500`, `text-blue-400`). Sempre utilizar as variáveis semânticas do tema acima (ex: `text-primary`, `bg-surface-container-high`, `border-cantrip/20`).

---

## 3. Tipografia

A tipografia do Projeto D1 combina elegância literária clássica para títulos com legibilidade cristalina sem serifa para dados e estatísticas:

| Uso | Família Tipográfica | Configuração Tailwind | Peso / Estilo |
|-----|-------------------|-----------------------|---------------|
| Títulos de Impacto e Header | **EB Garamond** (Serifa) | `font-headline-lg` / `font-display-lg` | Medium / SemiBold |
| Nome das Entidades (Cards) | **EB Garamond** (Serifa) | `font-headline-lg` | Bold, Uppercase |
| Corpo do Texto e Descrições | **Hanken Grotesk** (Sans-Serif) | `font-body-md` / `font-body-lg` | Regular (400) |
| Estatísticas e Atributos | **EB Garamond** (Serifa) | `font-headline-lg` | Bold |
| Títulos de Seção e Sidebar | **Hanken Grotesk** (Sans-Serif) | `font-label-sm` | Bold, Uppercase, Spacing |
| Badges, Labels e Stats | **Hanken Grotesk** (Sans-Serif) | `font-label-sm` / `font-data-table` | Medium / Regular |

**Importação (Google Fonts + Material Symbols):**
```html
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400..800;1,400..800&family=Hanken+Grotesk:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet" />
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
```

**Convenções:**
- Títulos em `EB Garamond` devem usar `tracking-widest` e `text-transform: uppercase` quando aplicável para reforçar a atmosfera mágica.
- Ícones em toda a aplicação utilizam exclusivamente o **Material Symbols Outlined** com preenchimento customizado via CSS.
- Fallback: `serif` para títulos e `sans-serif` para dados.

---

## 4. Estrutura HTML (SPA Unificada)

O app unificado do **Projeto D1** é uma Single Page Application (SPA) estática autocontida. A estrutura base do arquivo unificado segue o esqueleto abaixo:

```html
<!DOCTYPE html>
<html class="dark" lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PROJETO D1 — D&D 5e em PT-BR</title>
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  
  <!-- Google Fonts & Material Symbols -->
  <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400..800;1,400..800&family=Hanken+Grotesk:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet" />
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
  
  <!-- Configuração Customizada do Tailwind -->
  <script>
    tailwind.config = {
      darkMode: "class",
      theme: {
        extend: {
          colors: { /* Definições de cores (veja Seção 2) */ },
          fontFamily: { /* Definições de fontes (veja Seção 3) */ }
        }
      }
    };
  </script>

  <!-- Estilos Adicionais / Animações Customizadas -->
  <style>
    /* Custom Scrollbar, Glassmorphism, Accordion Card & Sidebar transition rules */
  </style>
</head>
<body class="bg-background text-on-surface selection:bg-primary/30 overflow-x-hidden">

  <!-- Header Fixo de Navegação Superior -->
  <header class="fixed top-0 left-0 w-full h-16 z-50 bg-background/80 backdrop-blur-md border-b border-primary/20 flex items-center justify-between px-6 md:px-margin-desktop">
    <div class="flex items-center gap-8">
      <button type="button" data-module="inicio" class="font-headline-lg text-2xl font-bold tracking-widest text-primary bg-transparent border-none cursor-pointer">PROJETO D1</button>
      <nav class="hidden md:flex gap-6 items-center">
        <button type="button" data-module="inicio" class="font-label-sm text-xs text-on-surface-variant hover:text-primary transition-all cursor-pointer bg-transparent border-none py-1 px-2 rounded-sm" id="nav-inicio">Início</button>
        <button type="button" data-module="grimorio" class="font-label-sm text-xs text-on-surface-variant hover:text-primary transition-all cursor-pointer bg-transparent border-none py-1 px-2 rounded-sm" id="nav-grimorio">Grimório</button>
        <button type="button" data-module="arsenal" class="font-label-sm text-xs text-on-surface-variant hover:text-primary transition-all cursor-pointer bg-transparent border-none py-1 px-2 rounded-sm" id="nav-arsenal">Arsenal</button>
        <button type="button" data-module="bestiario" class="font-label-sm text-xs text-on-surface-variant hover:text-primary transition-all cursor-pointer bg-transparent border-none py-1 px-2 rounded-sm" id="nav-bestiario">Bestiário</button>
      </nav>
    </div>
    
    <div class="flex items-center gap-4">
      <!-- Busca de Desktop (Injetada no Header, oculta em mobile) -->
      <div class="relative hidden sm:block opacity-0 transition-opacity duration-300" id="header-search-container">
        <input class="bg-surface-container border border-primary/30 text-on-surface pl-4 pr-10 py-1.5 focus:outline-none focus:border-primary transition-all w-64 font-body-md text-sm rounded-sm" placeholder="Buscar no multiverso..." type="search" id="search-box" autocomplete="off" spellcheck="false"/>
        <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-primary text-lg pointer-events-none select-none">search</span>
      </div>

      <!-- Botão de Filtros (visível apenas quando há filtros no módulo ativo) -->
      <button class="flex items-center gap-2 border border-primary/30 text-on-surface-variant px-3 py-1.5 hover:border-primary hover:text-primary transition-all rounded-sm font-label-sm text-xs cursor-pointer" id="toggle-filters">
        <span class="material-symbols-outlined text-lg">filter_list</span>
        <span>Filtros</span>
      </button>
    </div>
  </header>

  <!-- Overlay de Fundo Escuro para Mobile (fecha sidebar ao clicar) -->
  <div class="fixed inset-0 bg-black/60 z-40 opacity-0 pointer-events-none transition-opacity duration-300" id="overlay"></div>

  <!-- Sidebar Lateral de Filtros (Desliza da Direita) -->
  <aside class="fixed top-0 right-0 h-full w-80 bg-surface-container border-l border-primary/20 z-50 overflow-y-auto custom-scrollbar flex flex-col" id="side-nav">
    <div class="p-6 border-b border-primary/10 flex items-center justify-between sticky top-0 bg-surface-container/95 backdrop-blur-md z-10">
      <h2 class="font-headline-lg text-lg text-primary tracking-wider uppercase m-0 flex items-center gap-2">
        <span class="material-symbols-outlined text-primary">tune</span> Filtros
      </h2>
      <button class="w-8 h-8 flex items-center justify-center border border-primary/20 text-on-surface-variant hover:text-primary hover:border-primary transition-all bg-transparent rounded-full cursor-pointer" id="close-filters">
        <span class="material-symbols-outlined text-base">close</span>
      </button>
    </div>
    <div class="p-6 flex-grow overflow-y-auto custom-scrollbar" id="filters-container">
      <!-- Filtros gerados dinamicamente via JS -->
    </div>
    <div class="p-6 border-t border-primary/10 bg-surface-container-lowest flex gap-3 sticky bottom-0">
      <button class="flex-grow py-2 border border-primary/20 text-on-surface-variant hover:text-primary hover:border-primary transition-all rounded-sm font-label-sm text-xs cursor-pointer uppercase font-bold" id="clear-filters">Limpar</button>
    </div>
  </aside>

  <!-- Conteúdo Principal do Aplicativo -->
  <main class="min-h-screen pt-24 px-4 md:px-margin-desktop max-w-container-max-width mx-auto flex flex-col pb-16">
    <div class="w-full flex flex-col flex-grow" id="app">
      <!-- O HTML do módulo ativo é injetado aqui -->
    </div>
  </main>

  <script>
    // DADOS_JSON compilados (Injetados por build_unified.py)
  </script>
</body>
</html>
```

---

## 5. Componentes e Estilos (Tailwind CSS)

### 5.1 Header Superior

- **Altura:** 64px (`h-16`) fixa.
- **Posição:** `fixed top-0 left-0 w-full z-50`.
- **Estilo:** fundo translúcido `bg-background/80`, efeito desfoque de vidro `backdrop-blur-md`, borda inferior `border-b border-primary/20`.
- **Layout:** `flex items-center justify-between px-6 md:px-margin-desktop`.
- **Navegação:** links com fonte `font-label-sm` (`12px`) com efeito de hover suave dourado (`hover:text-primary transition-all`).

### 5.2 Barra de Busca (`#search-box` e `#search-box-mobile`)

A busca opera de forma responsiva através de dois inputs independentes, sincronizados em tempo real por JavaScript:

- **Desktop (`#search-box`):**
  - **Posição:** No lado direito do header (oculto em telas móveis e no módulo Início).
  - **Estilo:** input com fundo `bg-surface-container`, borda `border-primary/30`, foco com `focus:border-primary` e cantos `rounded-sm`.
  - **Ícone:** Ícone de lupa dourado (`Material Symbols: search`) posicionado absolutamente à direita do input container.
- **Mobile (`#search-box-mobile`):**
  - **Posição:** No topo da área de conteúdo (`#app`) quando visualizado em celulares.
  - **Estilo:** Ocupa 100% da largura horizontal (`w-full`), oferecendo área de toque e foco aprimorados. Ele desliza naturalmente para fora da tela com o scroll da página, economizando área no viewport restrito de smartphones.

### 5.3 Botão de Filtros (`#toggle-filters`)

- **Estilo:** borda fina de latão `border border-primary/30`, texto secundário `text-on-surface-variant`, preenchimento `px-3 py-1.5`, hover interativo `hover:border-primary hover:text-primary`.
- **Ícone:** Acompanhado pelo ícone `filter_list` do Material Symbols.

### 5.4 Sidebar de Filtros (`#side-nav`)

- **Posição:** fixa, à direita (`fixed top-0 right-0 h-full w-80`).
- **z-index:** 50.
- **Fundo:** cor de superfície escura `bg-surface-container` com borda lateral esquerda de latão `border-l border-primary/20`.
- **Deslocamento Dinâmico de Layout:** 
  - A barra lateral de filtros desliza suavemente da direita usando `transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)`.
  - **Desktop (`min-width: 1024px`):** Ao ativar a barra de filtros, ela adiciona uma margem direita de `20rem` (`margin-right: 20rem`) à tag `<main>`, deslocando a grade de cards suavemente para o lado. Os cards redimensionam-se de forma responsiva, evitando obstrução visual!
  - **Mobile (`max-width: 1023px`):** O sidebar sobrepõe o conteúdo como gaveta clássica, ativando um overlay escurecido de fundo.

**Seções de filtro:**
- Container vertical com espaçamento e scroll independente (`overflow-y-auto custom-scrollbar`).
- Títulos de seção: `font-label-sm text-[10px] text-primary/60 uppercase block mb-1 tracking-widest border-b border-primary/10 pb-1.5 mt-6`.
- Botões individuais (`.filter-btn`): fundo escuro, bordas finas. Quando ativados, ganham a classe `.active` (`bg-primary text-background border-primary font-bold`) ou `.active-trick` (`bg-cantrip text-white border-cantrip font-bold` para truques ou raridades).

### 5.5 Overlay (`#overlay`)

- **Fundo:** película translúcida preta `bg-black/60`.
- **Transição:** `transition-opacity duration-300`.
- **Comportamento:** Fica ativo apenas em telas móveis quando o menu lateral está aberto (`opacity-100`, `pointer-events-auto`). Ao clicar em qualquer parte do overlay, a barra de filtros é recolhida instantaneamente.

### 5.6 Lista Principal

- **Layout:** Centralizada na tela com `max-w-4xl mx-auto flex flex-col gap-4 px-2 md:px-4 py-6`.

### 5.7 Card de Entidade (`.card`)

O card de entidade é o principal bloco interativo do sistema, projetado para parecer uma ficha física clássica de pergaminho ou tomo místico:

- **Fundo:** Fundo escuro Obsidian `bg-surface-container-low` (`#1c1b1e`).
- **Borda:** 1px sólido de latão sutil `border border-primary/15`, cantos retos com `rounded-sm`.
- **Interações:** Ao passar o mouse, ganha borda destacada e brilho arcaniano sutil (`hover:border-primary/80 hover:shadow-[0_0_15px_rgba(201,168,106,0.15)]`).
- **Card Expandido (Acordeão - classe `.open`):**
  - **Fundo:** clareia para `bg-surface-container-high` (`#2b292d`).
  - **Borda:** fica mais espessa e brilhante com latão puro `border-2 border-primary`.
  - **Glow:** sombra proeminente com brilho arcaniano dourado (`shadow-[0_10px_30px_-10px_rgba(0,0,0,0.5),_0_0_15px_rgba(201,168,106,0.15)]`).
  - **Acento Superior:** Uma faixa horizontal decorativa de 4px de altura é renderizada no topo do card (`bg-primary` para magias/itens normais e `bg-cantrip` roxo para truques ou NDs muito elevados).

**Cabeçalho do Card (`.card-head`):**
- **Estrutura:** `p-4 md:p-6 flex items-center justify-between cursor-pointer select-none`.
- **Ícone redondo:** Um elemento esférico decorativo à esquerda contendo um ícone Material Symbols representativo da categoria (`border border-primary/20 bg-primary/5 text-primary rounded-full w-12 h-12 flex items-center justify-center`). Para monstros, esse badge exibe a classificação de ND em destaque.
- **Seta indicadora (`.expand-arrow`):** Ícone `arrow_forward_ios` posicionado na extrema direita que rotaciona 90 graus suavemente ao abrir o card (`.card.open .expand-arrow { transform: rotate(90deg); }`).

**Detalhe do Card (`.detail`):**
- **Comportamento:** Oculto por padrão (`hidden`), exibe-se com transição de acordeão ao receber foco (`open: block`).
- **Divisor:** Uma borda pontilhada ou linha de corte separa o cabeçalho dos detalhes (`border-t border-primary/10`).

### 5.8 Badges e Rótulos

- **Badges de Origem:** indicam a abreviação do livro oficial (`LJ` para Livro do Jogador, `GM` para Guia do Mestre, `MM` para Manual dos Monstros) em um container arredondado: `px-2.5 py-1 border border-primary/30 text-on-surface-variant font-label-sm text-[9px] md:text-[10px] bg-primary/5 rounded-full uppercase tracking-widest whitespace-nowrap`.
- **Badge de Referência de Livro:** renderizado no rodapé do detalhe com formato de ícone de pergaminho/livro: `bg-surface-container border border-primary/20 px-3 py-1.5 text-xs text-primary/80 rounded-sm font-label-sm font-bold uppercase`.

### 5.9 Detail Grid (Grid de Atributos)

- **Layout:** Estrutura flexível em grid `grid grid-cols-2 md:grid-cols-4 gap-4 px-4 md:px-8 pt-4 pb-6 border-b border-primary/10`.
- **Campos:** Blocos com fundo cinza sutil `bg-surface-container-low p-2.5 rounded border border-primary/10`, com um label menor e estatística em destaque:
  - **Label:** `font-label-sm text-[9px] md:text-[10px] text-on-surface-variant uppercase mb-1 tracking-wider`.
  - **Valor:** `font-headline-lg text-base md:text-lg text-primary`.

### 5.10 Tags de Categoria (`.class-tag`)

- **Estrutura:** Container wrap flexível `flex flex-wrap gap-2 px-4 md:px-8 py-3`.
- **Badges individuais:** `px-2.5 py-0.5 border border-primary/30 rounded-sm text-[10px] text-primary font-label-sm bg-primary/5 uppercase font-bold tracking-wide` (usados para listar classes de magia, propriedades de armas ou requisitos de sintonização).

### 5.11 Bloco de Descrição (`.spell-desc`)

- **Texto descritivo:** `px-4 md:px-8 pt-4 pb-6 text-on-surface-variant leading-relaxed font-body-md text-sm md:text-base space-y-4` (com espaçamento dinâmico entre parágrafos).
- **Listas não ordenadas:** marcadores clássicos limpos `list-disc pl-6 space-y-1.5 text-on-surface-variant font-body-md mb-4`.
- **Tabelas Descritivas de Regra:** Utilizadas para descrever tabelas de itens, efeitos secundários ou jogadas. Estilização moderna e responsiva do Tailwind:
  - Container com scroll horizontal para telas muito estreitas: `overflow-x-auto w-full mb-6`.
  - Estrutura de tabela: `w-full text-left text-xs font-data-table border-collapse border border-primary/20 rounded-sm`.
  - Cabeçalho: Fundo dourado desmaiado com texto brilhante `bg-primary/5 text-primary uppercase font-bold border-b border-primary/20 p-3`.
  - Linhas com listras e efeito de hover: `hover:bg-primary/5 transition-colors divide-y divide-primary/10`.

### 5.12 Painel de Atributos de Criaturas

- **Posição:** Exibido nos monstros do Bestiário.
- **Estrutura:** Grid de 6 colunas (`grid grid-cols-3 sm:grid-cols-6 gap-2 my-2`) exibindo Força, Destreza, Constituição, Inteligência, Sabedoria e Carisma.
- **Visual:** Cartões individuais com a sigla em dourado desbotado, valor principal da habilidade centralizado em destaque, e o modificador de teste de atributo com moldura sutil em baixo (`border border-primary/15 bg-surface-container-low p-2 rounded-sm text-center`).

### 5.13 Estatísticas de Resultados (`#stats`)

- **Posição:** Fica fixado acima da listagem de cards.
- **Estilo:** Rótulo em formato de fita ou informativo clean: `font-label-sm text-xs text-on-surface-variant tracking-wider uppercase text-center py-4 bg-surface-container-low/30 rounded border border-primary/10 mb-6 max-w-sm mx-auto`.

### 5.14 Estado Vazio (`#no-results`)

- **Comportamento:** Ativado dinamicamente via JS (`display: block` ou removendo a classe `hidden`) quando a busca por texto ou filtros não retornam correspondência.
- **Estilo:** Painel de aviso em destaque `text-center py-16 px-4 bg-surface-container-low rounded border border-primary/10 text-on-surface-variant max-w-md mx-auto my-8`.
- **Ícone:** Contém um ícone do Material Symbols grande com textura metálica inativa.

### 5.15 Footer

---

## 6. Comportamento Responsivo e Visualização Móvel

O design responsivo do Projeto D1 foi extensamente otimizado para celulares para garantir excelente jogabilidade e consulta em tela cheia:

### 6.1 Layout do Canvas e Sidebar

- **Telas Grandes (`min-width: 1024px`):** O sidebar de filtros desliza da direita e desloca o layout principal do `<main>` para a esquerda adicionando uma margem dinâmica de `margin-right: 20rem` (`w-80`). O overlay escurecido fica desativado.
- **Telas Médias e Pequenas (`max-width: 1023px`):** O sidebar de filtros flutua por cima da interface como uma gaveta (drawer), cobrindo parcialmente a tela. O overlay escurecido `#overlay` é ativado, cobrindo o restante da tela. Ao tocar em qualquer parte fora do sidebar (no overlay), o menu lateral se fecha.

### 6.2 Barra de Busca Inteligente

- **Desktop (`sm:block`):** Exibe a barra de busca no canto direito superior do Header fixo para acesso constante.
- **Mobile (`max-width: 639px`):** O input de busca de desktop é totalmente ocultado para evitar estrangulamento de espaço na barra superior que contém o logo "PROJETO D1". Em seu lugar, é renderizado um input de busca dedicado no topo da tela do módulo ativo (`#search-box-mobile`). Este input desliza naturalmente com a rolagem vertical, permitindo que a lista de cards use 100% da área do celular ao rolar.
- **Sincronização:** Ambas as barras sincronizam suas queries em tempo real por meio de um listener de eventos sincronizado. Se o usuário rotacionar o aparelho ou redimensionar a janela, a consulta não se perde.

### 6.3 Ajustes de Exibição Móvel

- **Atributos de Monstros:** Em celulares menores, a grid de 6 colunas de atributos rebaixa-se graciosamente para 3 colunas em duas linhas, mantendo o tamanho de toque e legibilidade de valores ideais.
- **Grids de Metadados:** As grades de atributos e valores do Arsenal/Grimório rebaixam-se automaticamente de 4 colunas em desktop para 2 colunas em telas estreitas, ou coluna única em celulares de baixa resolução.
- **Espaçamento e Padding:** Padds e margens internas dos cards reduzem-se de `p-6` para `p-4` em mobile, economizando pixels valiosos e otimizando a densidade de informação.

---

## 7. Interações e Comportamentos JavaScript

### 7.1 Atalhos globais de teclado

| Atalho | Ação executada |
|--------|----------------|
| Tecla `/` | Foca no input de busca ativo (desktop ou mobile) e seleciona todo o texto. |
| Tecla `Escape` | Fecha a barra lateral de filtros (se aberta) ou limpa a busca de texto atual. |

### 7.2 Lógica de Busca e Sincronização

A busca realiza normalização profunda de strings (remoção de acentos por unicode normalizer e conversão para caixa baixa) para garantir alta tolerância a erros gramaticais durante digitações rápidas:

```javascript
function normalizeStr(str) {
  return String(str || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove acentos
    .trim();
}
```

**Sincronização Dual:**
```javascript
const handleSearch = e => {
  query = e.target.value;
  openId = null; // Fecha card ativo para recalcular listagem
  
  if (e.target.id === 'search-box') {
    const mob = $('#search-box-mobile');
    if (mob) mob.value = query;
  } else {
    const dsk = $('#search-box');
    if (dsk) dsk.value = query;
  }
  render();
};
```

### 7.3 Accordion de Cards (Acordeão)

- **Apenas um card aberto por vez:** A abertura de qualquer card fecha o card previamente expandido. Isso evita poluição visual no celular e economiza rolagem de tela.
- **Scroll Inteligente:** Ao clicar em um card fechado para expandi-lo, a página executa uma rolagem animada suave para centralizar a cabeceira do card no topo do viewport:
  ```javascript
  setTimeout(() => {
    cardElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, 50); // Pequeno atraso para aguardar a renderização do bloco expandido
  ```

### 7.4 Controle de Estado do Sidebar

O menu lateral é inteiramente orquestrado por modificações de classe no nó raiz do documento (`body.show-sidebar`), evitando bugs de sincronização de classes em múltiplos elementos:

```javascript
function openSidebar() {
  if (current === 'inicio') return;
  document.body.classList.add('show-sidebar');
}

function closeSidebar() {
  document.body.classList.remove('show-sidebar');
}

function toggleSidebar() {
  if (current === 'inicio') return;
  document.body.classList.toggle('show-sidebar');
}
```

---

## 8. Estrutura de Dados e Compilação JSON

### 8.1 Schema Base Unificado

Toda entidade no sistema (Magias, Itens, Monstros) herda uma estrutura de chaves consistente para indexação rápida no loop de busca e renderização na SPA:

```json
{
  "id": "slug-identificador-unico",
  "nome": "Nome para Exibição",
  "categoria": "Grimório | Arsenal | Bestiário",
  "tipo": "Subcategoria de dados",
  "fonte": "Livro do Jogador | Guia do Mestre | Manual dos Monstros",
  "referencia": "Página (PDF: Página)",
  "descricao": "Texto bruto descritivo",
  "descricao_blocos": [
    {
      "type": "paragraph",
      "text": "Texto do parágrafo."
    },
    {
      "type": "list",
      "items": ["Item A", "Item B"]
    },
    {
      "type": "table",
      "headers": ["Col 1", "Col 2"],
      "rows": [["val A1", "val A2"]]
    }
  ]
}
```

### 8.2 Compilação Automática (`build_unified.py`)

A SPA da raiz (`index.html`) é gerada automaticamente pelo script python injetando os dados dos JSONs revisados no template puro (`unified_template.html`). O script mapeia os arquivos locais:
- `Grimorio/spells.json`
- `Arsenal/arsenal.json`
- `Bestiario/monstros.json`
- `RacasClasses/racas_classes.json`

Gerando variáveis globais javascript compactadas e injetadas no corpo do script para funcionamento offline instantâneo (Offline-First).

---

## 9. Checklist para Adicionar Novas Entidades ou Módulos

- [ ] HTML e Tailwind implementados em `unified_template.html`.
- [ ] Cores utilizam exclusivamente a paleta semântica estendida em `tailwind.config`.
- [ ] Fontes `EB Garamond` para títulos e `Hanken Grotesk` para dados textuais.
- [ ] Header fixo superior com links de rota de hash `#inicio`, `#grimorio`, etc.
- [ ] Sidebar de filtros à direita com controle por classe global `body.show-sidebar`.
- [ ] Deslocamento dinâmico lateral (`margin-right: 20rem`) em desktop para o sidebar de filtros.
- [ ] Busca sincronizada dual em tempo real com normalização avançada de caracteres unicode.
- [ ] Cards de itens implementam hover glassmorphism com borda e glow dourado.
- [ ] Badges e detail grid estruturados de forma responsiva.
- [ ] Tabelas internas de descrição adaptam-se com scroll horizontal e bordas de latão.
- [ ] Ficha de monstros exibe as seis colunas de atributos rebaixáveis graciosamente para celular.
- [ ] Módulos com conteúdo de criação de personagem exibem mecânicas essenciais no card, mantendo referências de página apenas como consulta opcional.
- [ ] Progressões de classe, progressões de subclasse e listas comparativas usam tabelas responsivas quando a informação for tabular.
- [ ] Acordeão de card único com centralização suave de scroll na página.
- [ ] Interface 100% traduzida em PT-BR.
- [ ] Validação por compilação determinística local (`python build_unified.py`).
- [ ] Teste de integridade em servidores HTTP offline (`python -m http.server`).

---

## 10. Mapeamento de Classes e Compatibilidade

Os componentes preservam as tags e classes estruturais herdadas das fases iniciais para consistência e suporte retrospectivo de renderização de dados brutos:

| Classe CSS / Seletor | Escopo e Responsabilidade no Novo Layout |
|----------------------|-----------------------------------------|
| `.card` | Substitui o antigo `.spell-card` com efeitos glassmorphism e cores de superfícies Obsidian. |
| `.card.open` | Card selecionado e aberto pelo acordeão. Adiciona o acento dourado superior. |
| `.card.cantrip` | Aplica o marcador arcano roxo (utilizado para truques e itens mágicos raros). |
| `.card-head` | Cabeçalho interno do card contendo o título e os badges básicos de leitura rápida. |
| `.detail` | Bloco expansível interno do card contendo as tabelas, tags e dados estendidos. |
| `.spell-desc` | Classe que encapsula o texto descritivo e as tabelas com fontes e entrelinhas ideais. |
| `#side-nav` | Substitui o painel lateral `.sidebar` legado, gerenciado por classe no body. |
| `#overlay` | Painel de clique escurecido para fechamento de menu em dispositivos móveis. |
| `.filter-btn.active` | Filtro em estado ativo (ganha realce dourado ou roxo no caso de truques). |
| `.expand-arrow` | Seta de rotação suave de estado do acordeão do card. |

---

*Última atualização: 20/05/2026*
