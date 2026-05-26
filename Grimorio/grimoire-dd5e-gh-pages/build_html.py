#!/usr/bin/env python3
"""
Reconstrói o grimoire.html com dados do Docling (spells.json).
O JS espera campos compactos: n, nv, e, tc, al, co, du, d, pr, cl
"""
import json, re


def esc(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def render_table(lines):
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)

    if len(rows) < 2:
        return '<p>' + '<br>'.join(esc(l) for l in lines) + '</p>'

    def is_sep(row):
        t = ''.join(row)
        return all(c in '-: ' for c in t) and '-' in t

    sep_indices = [i for i, r in enumerate(rows) if is_sep(r)]

    if not sep_indices:
        h = ['<table class="spell-table"><tbody>']
        for row in rows:
            h.append('<tr>' + ''.join(f'<td>{esc(c)}</td>' for c in row) + '</tr>')
        h.append('</tbody></table>')
        return '\n'.join(h)

    def render_single(header_rows, body_rows):
        has_title = False
        if header_rows and body_rows:
            last = header_rows[-1]
            for j in range(len(last) - 1):
                if last[j] and last[j] == last[j + 1]:
                    has_title = True
                    break

        if has_title:
            title_cells = header_rows[-1]
            col_headers = body_rows[0]
            data = body_rows[1:]
        else:
            title_cells = None
            col_headers = header_rows[-1] if header_rows else []
            data = body_rows

        h = ['<table class="spell-table">']

        if col_headers:
            h.append('<thead>')
            if title_cells:
                h.append('<tr>')
                ci = 0
                while ci < len(title_cells):
                    cell = title_cells[ci]
                    colspan = 1
                    while ci + colspan < len(title_cells):
                        nxt = title_cells[ci + colspan]
                        if nxt == cell or (not nxt and cell):
                            colspan += 1
                        else:
                            break
                    if cell:
                        h.append(f'<th colspan="{colspan}">{esc(cell)}</th>')
                    ci += colspan
                h.append('</tr>')
            h.append('<tr>' + ''.join(f'<th>{esc(c)}</th>' for c in col_headers) + '</tr>')
            h.append('</thead>')

        if data:
            h.append('<tbody>')
            for row in data:
                h.append('<tr>' + ''.join(f'<td>{esc(c)}</td>' for c in row) + '</tr>')
            h.append('</tbody>')

        h.append('</table>')
        return '\n'.join(h)

    tables = []
    for k, si in enumerate(sep_indices):
        if k == 0:
            hdr = rows[:si]
        else:
            hdr = [rows[si - 1]]
        body_start = si + 1
        if k + 1 < len(sep_indices):
            body_end = sep_indices[k + 1] - 1
        else:
            body_end = len(rows)
        tables.append(render_single(hdr, rows[body_start:body_end]))

    return '\n'.join(tables)


def render_markdown(text):
    if not text:
        return ''

    lines = text.split('\n')
    tables_raw = []
    result_parts = []
    i = 0

    while i < len(lines):
        stripped = lines[i].strip()
        is_tbl = stripped.startswith('|') and '|' in stripped[1:]

        if is_tbl:
            tbl_lines = [stripped]
            i += 1
            while i < len(lines):
                s = lines[i].strip()
                if s.startswith('|') and '|' in s[1:]:
                    tbl_lines.append(s)
                    i += 1
                elif s == '':
                    j = i + 1
                    while j < len(lines) and lines[j].strip() == '':
                        j += 1
                    if j < len(lines) and lines[j].strip().startswith('|') and '|' in lines[j].strip()[1:]:
                        i += 1
                        continue
                    break
                else:
                    break
            idx = len(tables_raw)
            tables_raw.append(tbl_lines)
            result_parts.append(f'\n\n__TABLE_{idx}__\n\n')
        else:
            result_parts.append(lines[i])
            i += 1

    text_ph = '\n'.join(result_parts)

    paragraphs = re.split(r'\n{2,}', text_ph)
    parts = []
    pending_bullets = []

    def flush_bullets():
        if not pending_bullets:
            return
        parts.append('<ul>')
        for b in pending_bullets:
            parts.append(f'<li>{esc(b)}</li>')
        parts.append('</ul>')
        pending_bullets.clear()

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        m = re.match(r'^__TABLE_(\d+)__$', para)
        if m:
            flush_bullets()
            parts.append(render_table(tables_raw[int(m.group(1))]))
            continue

        for line in para.split('\n'):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('- '):
                pending_bullets.append(stripped[2:])
            else:
                flush_bullets()
                safe = esc(stripped)
                safe = re.sub(
                    r'(Em Níveis Superiores\s*\.?)',
                    r'<strong class="higher-levels">\1</strong>',
                    safe,
                    flags=re.IGNORECASE
                )
                parts.append(f'<p>{safe}</p>')

    flush_bullets()
    return '\n'.join(parts)


def main():
    with open('spells.json', encoding='utf-8') as f:
        spells = json.load(f)

    # Formato compacto pro JS
    compact = []
    for s in spells:
        # Nível formatado
        level = s.get('level', '')
        if level == 'Truque':
            nv = 'Truque'
        elif level.isdigit():
            nv = f'{level}° nível'
        else:
            nv = level
        
        # Referência de página
        pp = s.get('page_print', 0)
        pr = f'p.{pp}' if pp else ''
        
        # Classes como lista
        classes_str = s.get('classes', '')
        if classes_str:
            cl = [c.strip() for c in classes_str.split(',') if c.strip()]
        else:
            cl = []
        
        # Descrição em Markdown → HTML simples
        desc = s.get('description', '')
        desc_html = render_markdown(desc)
        
        compact.append({
            'n': s.get('name', ''),
            'nv': nv,
            'e': s.get('school', '').lower(),
            'tc': s.get('cast_time', ''),
            'al': s.get('range', ''),
            'co': s.get('components', ''),
            'du': s.get('duration', ''),
            'd': desc_html,
            'pr': pr,
            'cl': cl,
        })

    # Monta o HTML
    json_data = json.dumps(compact, ensure_ascii=False)

    with open('template.html', encoding='utf-8') as f:
        template = f.read()

    html = template.replace('__SPELLS_DATA__', json_data)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'OK {len(compact)} magias em index.html')
    print(f'   Tamanho: {len(html)/1024:.0f} KB')


if __name__ == '__main__':
    main()
