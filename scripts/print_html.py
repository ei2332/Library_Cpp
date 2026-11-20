"""Render libparser's parsed lines as a self-contained printable HTML page."""

from html import escape
import re

# Lexical highlighting only; no understanding of C++ semantics.
TOKENS = re.compile(
    r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    r'|\b(?:template|class|struct|typename|using|return|if|else|for|while|break|continue|'
    r'const|constexpr|static|void|bool|int|long|short|unsigned|signed|auto|'
    r'public|private|protected|friend|operator|true|false|namespace|new|delete)\b'
    r'|\b(?:0x[0-9a-fA-F]+|[0-9]+(?:[uUlL]+)?)\b'
)

CSS = """
:root {
    color-scheme: light;
    --ink: #20242a;
    --muted: #737a85;
    --rule: #d6dce4;
    --blue: #25517c;
    --note-bg: #edf3fa;
    --complexity-bg: #e9ecf2;
    --shade-bg: #fff8e3;
    --shade-line: #a07a2f;
}
* { box-sizing: border-box; }
body { margin: 0; background: #fff; color: var(--ink); font-family: system-ui, -apple-system, 'Yu Gothic', Meiryo, sans-serif; }
main { max-width: 900px; margin: 0 auto; padding: 28px 25px 52px; }
header { border-bottom: 1px solid var(--rule); padding: 0 0 13px; margin-bottom: 17px; }
h1 { margin: 0 0 6px; font-size: 24px; letter-spacing: .01em; }
.summary { font-size: 13px; line-height: 1.6; margin: 0; }
.code-row { position: relative; display: grid; grid-template-columns: 39px minmax(0, 1fr); min-height: 19px; line-height: 19px; font: 12px/19px Consolas, 'Liberation Mono', 'Noto Sans Mono CJK JP', monospace; }
.num { color: #8a929d; text-align: right; padding-right: 13px; user-select: none; border-right: 1px solid var(--rule); }
.code-row code { white-space: pre; padding-left: 13px; display: block; overflow: visible; font: inherit; }
.note { font-size: 12px; line-height: 1.55; padding: 5px 10px; margin: 6px 0 4px; break-inside: avoid; }
.note.expl { border-left: 3px solid var(--blue); background: var(--note-bg); font-weight: 600; }
.note.comp { background: var(--complexity-bg); color: #343f4f; border-left: 3px solid #aab3c0; }
.note.text { border-left: 2px solid #9ba6b7; color: #4f5b6b; }
.code-row.shaded { background: var(--shade-bg); }
.code-row.shaded::before, .note.shaded::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 8px;
    border-left: 1px solid var(--shade-line);
    background: repeating-linear-gradient(135deg, #b29a60 0 1px, transparent 1px 4px);
}
.note.shaded { position: relative; background: var(--shade-bg); border-left: 0; padding-left: 14px; }
.kw { color: #244f86; font-weight: 600; }
.literal { color: #86521d; }
.str { color: #24604d; }
.comment { color: #678069; }
@page { size: A4 portrait; margin: 13mm 12mm; }
@media print {
    html, body { width: auto; background: white; }
    main { padding: 0; max-width: none; }
    h1 { font-size: 19pt; }
    .code-row { font-size: 9px; line-height: 14px; min-height: 14px; break-inside: avoid; }
    .note { font-size: 10px; }
    header { break-after: avoid; }
    .code-row, .note { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
"""


def highlight(line):
    out, pos = [], 0
    for m in TOKENS.finditer(line):
        out.append(escape(line[pos:m.start()]))
        token = m.group()
        if token.startswith(('//', '/*')):
            cls = 'comment'
        elif token.startswith(('"', "'")):
            cls = 'str'
        elif token[0].isdigit():
            cls = 'literal'
        else:
            cls = 'kw'
        out.append(f'<span class="{cls}">{escape(token)}</span>')
        pos = m.end()
    out.append(escape(line[pos:]))
    return ''.join(out)


def visible_items(items, shaded_scopes):
    selected = set(shaded_scopes)
    out = []
    for scope, kind, value in items:
        if scope == 'include' or (scope is not None and scope not in selected):
            continue
        if kind != 'code':
            while out and out[-1][0] == 'code' and not out[-1][1].strip():
                out.pop()
        out.append((kind, value, scope is not None))

    while out and out[-1][0] == 'code' and not out[-1][1].strip():
        out.pop()
    while out and out[0][0] == 'code' and not out[0][1].strip():
        out.pop(0)
    return out


def render(name, description, items, shaded_scopes):
    title = escape(name)
    doc = [
        '<!doctype html>', '<html lang="ja">', '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{title}</title>', f'<style>{CSS}</style>',
        '</head>', '<body><main><article>', '<header>', f'<h1>{title}</h1>'
    ]
    if description:
        doc.append(f'<p class="summary">{escape(description)}</p>')
    doc.append('</header>')
    number = 0
    for kind, value, shaded in visible_items(items, shaded_scopes):
        cls = ' shaded' if shaded else ''
        if kind == 'code':
            number += 1
            doc.append(f'<div class="code-row{cls}"><span class="num">{number}</span>'
                       f'<code>{highlight(value)}</code></div>')
        else:
            text = f'計算量 {value}' if kind == 'comp' else value
            doc.append(f'<div class="note {kind}{cls}">{escape(text)}</div>')
    doc.extend(['</article></main></body></html>', ''])
    return '\n'.join(doc)
