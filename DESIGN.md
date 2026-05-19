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

## 2. Paleta de Cores (CSS Variables)

```css
:root {
  --bg: #0d0b0e;          /* Fundo principal */
  --bg2: #1a1520;         /* Fundo secundário (sidebar, inputs) */
  --bg3: #241e2c;         /* Fundo terciário (botões, hover) */
  --fg: #e8dcc8;          /* Texto principal */
  --fg2: #a89b8a;         /* Texto secundário (labels, hints) */
  --accent: #d4a44a;      /* Dourado principal (títulos, bordas, ativos) */
  --accent2: #e8c06a;     /* Dourado claro (badges, destaques) */
  --card: #1c1724;        /* Fundo dos cards */
  --border: #3a2f48;      /* Bordas gerais */
  --cantrip: #8e44ad;     /* Roxo (destaque especial — truques, itens mágicos) */
  --shadow: 0 2px 12px rgba(0,0,0,0.5);
  --sidebar-w: 280px;
}
```

**Regra:** Nunca introduzir cores fora desta paleta. Novos estados semânticos usam combinações existentes.

---

## 3. Tipografia

| Uso | Fonte | Peso | Tamanho |
|-----|-------|------|---------|
| Título do módulo (header h1) | Cinzel | 900 | 1rem |
| Títulos de seção / sidebar | Cinzel | 700 | 0.7–0.95rem |
| Badges | Cinzel | 700 | 0.65rem |
| Nome do item (card) | Cinzel | 700 | 0.95rem |
| Corpo / descrição | Lora | 400 | 0.85rem |
| Labels / metadados | Lora | 400 | 0.7–0.82rem |
| Filtro / stats | Lora | 400 | 0.75rem |

**Importação:**
```css
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Lora:ital,wght@0,400;0,700;1,400&display=swap');
```

**Convenções:**
- Cinzel: SEMPRE em `text-transform: uppercase` e `letter-spacing: 0.05–0.12em`
- Lora: corpo de texto, sem transformações
- Fallback: `Georgia, serif`

---

## 4. Estrutura HTML

Todo módulo segue este esqueleto:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[MÓDULO] — D&D 5e</title>
  <style>
    /* CSS completo inline */
  </style>
</head>
<body>

  <!-- Overlay (fundo escuro atrás da sidebar) -->
  <div class="overlay" id="overlay" onclick="toggleSidebar()"></div>

  <!-- Sidebar de Filtros (desliza da direita) -->
  <div class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <h2>&#x2699; Filtros</h2>
      <button class="sidebar-close" onclick="toggleSidebar()" title="Fechar filtros">&#x2715;</button>
    </div>
    <div class="sidebar-body" id="filters"></div>
  </div>

  <!-- Header fixo -->
  <header>
    <h1>[ÍCONE] [Nome do Módulo]</h1>
    <input type="text" id="search-box" placeholder="Buscar [item] por nome..." autocomplete="off" spellcheck="false">
    <button class="filter-toggle-btn" onclick="toggleSidebar()">&#x2630; Filtros</button>
  </header>

  <!-- Contador de resultados -->
  <div id="stats"></div>

  <!-- Lista de cards -->
  <div id="[entidade]-list"></div>

  <!-- Estado vazio -->
  <div id="no-results">
    <div class="icon">&#x1F50D;</div>
    <p>Nenhum(a) [entidade] encontrado(a).</p>
  </div>

  <!-- Footer -->
  <footer>[Módulo] D&D 5e &mdash; [descrição curta] em Português Brasileiro</footer>

  <script>
    // DADOS_JSON embutidos
    // Lógica JS
  </script>
</body>
</html>
```

---

## 5. Componentes

### 5.1 Header

- **Altura:** 50px fixa
- **Posição:** `sticky; top: 0; z-index: 100`
- **Fundo:** `linear-gradient(180deg, #1a0f25 0%, #0d0b0e 100%)`
- **Borda inferior:** `2px solid var(--accent)`
- **Layout:** `flex` — título à esquerda, busca centralizada (max 500px), botão de filtros à direita
- **Title:** `text-shadow: 0 0 20px rgba(212,164,74,0.3)` (brilho dourado)

### 5.2 Barra de Busca (`#search-box`)

- **Estilo:** fundo `var(--bg2)`, borda `var(--border)`, texto `var(--fg)`
- **Focus:** borda muda pra `var(--accent)` com `box-shadow: 0 0 8px rgba(212,164,74,0.25)`
- **Placeholder:** `var(--fg2)` com `opacity: 0.6`
- **Padding:** `0.4rem 0.8rem`
- **Border-radius:** `6px`

### 5.3 Botão de Filtros (`.filter-toggle-btn`)

- **Fonte:** Cinzel 700, 0.85rem
- **Estilo:** fundo `var(--bg3)`, borda `var(--border)`, texto `var(--fg2)`
- **Hover:** fundo `var(--border)`, texto `var(--fg)`
- **Border-radius:** `4px`

### 5.4 Sidebar de Filtros

- **Posição:** fixa, direita, `transform: translateX(100%)` → `.open: translateX(0)`
- **Largura:** `var(--sidebar-w)` (280px), `max-width: 85vw`
- **Fundo:** `var(--bg2)`
- **Borda esquerda:** `2px solid var(--accent)`
- **z-index:** 300
- **Transição:** `transform 0.3s ease`

**Seções de filtro:**
- `.filter-section` — cada grupo de filtros
- `.filter-section-title` — Cinzel 700, 0.7rem, uppercase, borda inferior pontilhada
- `.filter-section-btns` — `flex-wrap` com `gap: 0.3rem`
- **Variação colapsível** (Arsenal+): classe `.collapsible` + `.collapsed`, com seta `::after`

**Botões de filtro** (`.filter-btn`):
- Fundo `var(--bg3)`, borda `var(--border)`, texto `var(--fg2)`
- **Ativo:** fundo `var(--accent)`, texto `#1a0f25`, borda `var(--accent)`, bold
- **Ativo especial** (`.active-trick`): fundo `var(--cantrip)`, texto `#fff`
- Border-radius: `4px`

### 5.5 Overlay

- **Estado normal:** `opacity: 0; pointer-events: none`
- **Ativo** (`.show`): `opacity: 1; pointer-events: auto`
- **Fundo:** `rgba(0,0,0,0.6)`
- **z-index:** 200
- **Transição:** `opacity 0.3s`

### 5.6 Lista Principal

- **Max-width:** 900px, centralizada
- **Padding:** `0 0.8rem 3rem`
- **Layout:** `flex-direction: column; gap: 0.4rem`

### 5.7 Card de Item (`.spell-card`)

> Apesar do nome legado "spell-card", este é o componente de card genérico.

- **Fundo:** `var(--card)`
- **Borda:** `1px solid var(--border)`, border-radius `8px`
- **Hover:** borda `var(--accent)` + `box-shadow: var(--shadow)`
- **Borda esquerda colorida:** 3px — `var(--accent)` (normal) ou `var(--cantrip)` (especial)
- **Cursor:** `pointer`
- **Transições:** `border-color 0.2s, transform 0.15s, box-shadow 0.2s`

**Header do card** (`.spell-header`):
- `display: flex; justify-content: space-between; padding: 0.6rem 0.8rem`
- Nome (`.spell-name`): Cinzel 700, 0.95rem
- Metadados (`.spell-meta`): badges + seta de expandir

**Detalhe expandível** (`.spell-detail`):
- `display: none` por padrão → `.spell-card.open .spell-detail { display: block }`
- Borda superior: `1px solid var(--border)`
- Padding: `0 0.8rem 0.8rem`

**Seta de expandir** (`.expand-arrow`):
- `&#x25B6;` (▶), `color: var(--fg2)`
- `.spell-card.open .expand-arrow { transform: rotate(90deg) }`

### 5.8 Badges

| Classe | Uso | Fundo | Texto | Borda |
|--------|-----|-------|-------|-------|
| `.badge-level` | Nível, raridade | `rgba(212,164,74,0.15)` | `var(--accent2)` | `rgba(212,164,74,0.3)` |
| `.badge-cantrip` | Truques, itens mágicos | `rgba(142,68,173,0.2)` | `#bb6bd9` | `rgba(142,68,173,0.3)` |
| `.badge-school` | Escola, sintonização | `rgba(52,152,219,0.12)` | `#5dade2` | `rgba(52,152,219,0.25)` |
| `.badge-source` | Fonte/livro | `rgba(255,255,255,0.04)` | `var(--fg2)` | `var(--border)` |
| `.icon-badge` | Ícone de categoria | `rgba(212,164,74,0.12)` | `var(--accent2)` | `rgba(212,164,74,0.32)` |
| `.icon-badge.magic` | Ícone mágico | `rgba(142,68,173,0.2)` | `#bb6bd9` | `rgba(142,68,173,0.3)` |

**Estilo comum:** `padding: 0.1rem 0.4rem`, `font-size: 0.65rem`, Cinzel 700, `border-radius: 3px`, `text-transform: uppercase`

### 5.9 Detail Grid

- `display: grid; grid-template-columns: 1fr 1fr`
- `gap: 0.3rem 1rem; margin-bottom: 0.6rem; font-size: 0.82rem`
- **Label** (`.detail-label`): `var(--fg2)`, 0.7rem, uppercase, `letter-spacing: 0.08em`
- **Value** (`.detail-value`): `var(--fg)`
- **Mobile:** `grid-template-columns: 1fr`

### 5.10 Tags (`.class-tag`)

- `font-size: 0.65rem`, `padding: 0.1rem 0.35rem`, `border-radius: 3px`
- Fundo `var(--bg2)`, borda `var(--border)`, texto `var(--fg2)`
- Cada tipo de tag recebe cor própria via classe `.tag-[Nome]`
- Container `.spell-classes`: `display: flex; gap: 0.25rem; flex-wrap: wrap`

### 5.11 Descrição (`.spell-desc`)

- `font-size: 0.85rem; color: var(--fg); line-height: 1.7`
- Borda superior: `1px dashed var(--border)`
- **Parágrafos:** `<p>` com `margin: 0 0 0.6em`
- **Listas:** `<ul>` com `margin: 0.4em 0 0.6em 1.2em; list-style: disc`
- **Tabelas:** classe `.desc-table` — bordas `var(--border)`, header com fundo `rgba(212,164,74,0.08)`

### 5.12 Referência de Página (`.spell-ref`)

- `font-size: 0.75rem; color: var(--fg2); text-align: right`
- Texto dentro de `<span>` com fundo `var(--bg3)`, borda `var(--border)`, `border-radius: 3px`
- Formato: `📖 XXX (PDF: YYY)`

### 5.13 Stats (`.#stats`)

- `text-align: center; font-size: 0.75rem; color: var(--fg2); padding: 0.3rem 1rem`
- Formato: `"X de Y [entidades]"`

### 5.14 Estado Vazio (`#no-results`)

- `display: none` por padrão, `display: block` quando sem resultados
- `text-align: center; padding: 3rem 1rem; color: var(--fg2)`
- Ícone grande (3rem) + texto

### 5.15 Footer

- `text-align: center; padding: 1.5rem; font-size: 0.75rem; color: var(--fg2)`
- `opacity: 0.5; border-top: 1px solid var(--border)`

---

## 6. Responsivo

### Até 600px (mobile)

```css
@media (max-width: 600px) {
  header { gap: 0.5rem; padding: 0 0.5rem; }
  header h1 { font-size: 0.8rem; letter-spacing: 0.05em; }
  #search-box { font-size: 0.8rem; padding: 0.3rem 0.6rem; }
  .filter-toggle-btn { font-size: 0.75rem; padding: 0.3rem 0.5rem; }
  .spell-header { flex-direction: column; align-items: flex-start; }
  .spell-meta { justify-content: flex-start; }
  .detail-grid { grid-template-columns: 1fr; }
}
```

### Acima de 901px (desktop)

```css
@media (min-width: 901px) {
  .spell-card:hover { transform: translateX(2px); }
}
```

---

## 7. Interações JavaScript

### 7.1 Atalhos de Teclado

| Tecla | Ação |
|-------|------|
| `/` | Foca na barra de busca |
| `Escape` | Fecha sidebar OU limpa busca |

### 7.2 Busca em Tempo Real

- Evento `input` no `#search-box`
- Normalização: `toLowerCase().trim()` (Grimório) ou `normalize('NFD').replace(...)` com remoção de acentos (Arsenal+)
- **Sempre usar normalização com remoção de acentos** para novos módulos

### 7.3 Sistema de Filtros

- Filtros como `Set()` por categoria (ex: `{categoria: Set, tipo: Set, ...}`)
- Toggle individual (clique ativa/desativa)
- Filtros de categorias diferentes = AND
- Filtros da mesma categoria = OR
- Render re-renderiza toda a lista a cada mudança

### 7.4 Card Acordeão

- Apenas um card aberto por vez
- `scrollIntoView({behavior: 'smooth', block: 'nearest'})` ao expandir
- Delay de 50ms no scroll para aguardar a animação

### 7.5 Sidebar

- Toggle via classe `.open` + overlay `.show`
- Transição suave de 0.3s

---

## 8. Padrões de Dados JSON

### 8.1 Schema base por entidade

```jsonc
{
  "id": "livro-do-jogador-[slug]",   // Identificador único (fonte-categoria-nome)
  "nome": "Nome da Entidade",         // Nome para exibição
  "categoria": "Categoria",           // Agrupamento principal
  "tipo": "Subtipo",                  // Subcategoria
  "fonte": "Livro do Jogador",        // Livro de origem
  "pagina_livro": 123,                // Página impressa
  "pagina_pdf": 122,                  // Página no PDF
  "referencia": "123 (PDF: 122)",     // Referência formatada
  "descricao": "...",                 // Texto descritivo (string ou blocos)
  "descricao_blocos": [],             // Descrição estruturada (parágrafos, listas, tabelas)
  "raridade": null,                   // Raridade (se aplicável)
  "sintonizacao": false               // Sintonização requerida (se aplicável)
}
```

### 8.2 Descrição estruturada (`descricao_blocos`)

```jsonc
[
  { "type": "paragraph", "text": "Texto do parágrafo." },
  { "type": "list", "items": ["Item 1", "Item 2"] },
  { "type": "table", "headers": ["Col 1", "Col 2"], "rows": [["val1", "val2"]] }
]
```

**Preferir `descricao_blocos`** sobre `descricao` em string pura.

---

## 9. Checklist para Novo Módulo

- [ ] HTML segue o esqueleto da seção 4
- [ ] CSS Variables idênticas (seção 2)
- [ ] Fontes Cinzel + Lora importadas
- [ ] Header com título, busca e botão de filtros
- [ ] Sidebar de filtros com overlay
- [ ] Cards com header + detail expandível
- [ ] Badges seguem a tabela da seção 5.8
- [ ] Detail grid com labels/values
- [ ] Descrição com suporte a parágrafos, listas e tabelas
- [ ] Referência de página no formato `"XXX (PDF: YYY)"`
- [ ] Stats com contador
- [ ] Estado vazio com ícone de busca
- [ ] Footer com descrição do módulo
- [ ] Atalhos `/` e `Escape` implementados
- [ ] Responsivo (mobile ≤600px, desktop ≥901px)
- [ ] Busca com normalização de acentos
- [ ] Dados JSON embutidos com schema padronizado
- [ ] Interface 100% em PT-BR
- [ ] Testado offline

---

## 10. Nomes de Classes CSS — Referência

> Os nomes de classes são legados do Grimório original (ex: `.spell-card`, `.spell-header`). **Manter retrocompatibilidade** — não renomear. Novos módulos usam os mesmos nomes.

| Classe | Função |
|--------|--------|
| `.overlay` | Fundo escuro atrás da sidebar |
| `.sidebar` | Painel lateral de filtros |
| `.sidebar-header` | Cabeçalho da sidebar |
| `.sidebar-close` | Botão X de fechar |
| `.sidebar-body` | Corpo da sidebar |
| `.filter-section` | Grupo de filtros |
| `.filter-section-title` | Título do grupo |
| `.filter-section-btns` | Container dos botões de filtro |
| `.filter-btn` | Botão de filtro individual |
| `.filter-btn.active` | Filtro ativo (dourado) |
| `.filter-btn.active-trick` | Filtro ativo especial (roxo) |
| `.filter-toggle-btn` | Botão "Filtros" no header |
| `.spell-card` | Card de entidade |
| `.spell-card.open` | Card expandido |
| `.spell-card.cantrip` | Card com borda roxa (especial) |
| `.spell-card.leveled` | Card com borda dourada (normal) |
| `.spell-header` | Header do card |
| `.spell-name` | Nome da entidade no card |
| `.spell-meta` | Container de badges no header |
| `.spell-detail` | Área expandível do card |
| `.spell-desc` | Descrição detalhada |
| `.spell-ref` | Referência de página |
| `.spell-classes` | Container de tags |
| `.detail-grid` | Grid de metadados |
| `.detail-label` | Label do metadado |
| `.detail-value` | Valor do metadado |
| `.badge` | Badge genérico |
| `.badge-level` | Badge dourado |
| `.badge-cantrip` | Badge roxo |
| `.badge-school` | Badge azul |
| `.badge-source` | Badge de fonte |
| `.icon-badge` | Badge com ícone |
| `.class-tag` | Tag de categoria |
| `.expand-arrow` | Seta de expandir |
| `.hidden` | `display: none !important` |

---

*Última atualização: 18/05/2026*
