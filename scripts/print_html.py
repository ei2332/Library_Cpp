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

CSS = r"""
:root{color-scheme:light;--ink:#17212e;--muted:#596675;--rule:#dbe2e9;--shade:#fff2cf}
*{box-sizing:border-box}html,body{margin:0}
body{background:#f1f3f6;color:var(--ink);font-family:system-ui,-apple-system,'Yu Gothic',Meiryo,sans-serif}
#source{display:none!important}
#screen{max-width:1480px;margin:26px auto 60px;padding:0 20px}
.screen-layout{display:grid;grid-template-columns:minmax(0,65fr) minmax(310px,35fr);align-items:start;background:white;border:1px solid #dce2e9;border-radius:8px;box-shadow:0 7px 28px #26384d0b}
.screen-code{min-width:0;padding:24px 27px 38px}
.screen-notes{position:sticky;top:12px;overflow-y:auto;max-height:calc(100vh - 24px);min-width:0;padding:23px 25px 28px;border-left:1px solid var(--rule)}
.intro{margin:0 0 16px;padding:0 0 15px;border-bottom:1px solid var(--rule)}
.intro h1{font-size:24px;line-height:1.25;margin:0 0 7px}
.intro p{font-size:13px;line-height:1.6;margin:0;color:var(--muted)}
.code-row{display:grid;grid-template-columns:39px minmax(0,1fr);min-width:0;align-items:start;break-inside:avoid}
.code-row .num{font:12px/23px 'Liberation Mono',monospace;color:#7d8b99;text-align:right;padding-right:10px;border-right:1px solid var(--rule);user-select:none;font-variant-numeric:tabular-nums}
.code-row code{display:block;min-width:0;margin-left:13px;white-space:pre-wrap;overflow-wrap:anywhere;tab-size:4;font:14px/23px 'Liberation Mono','DejaVu Sans Mono',monospace;font-variant-ligatures:none}
.code-row.shaded{background:var(--shade);box-shadow:inset 3px 0 #aa853f}
.kw{color:#245c88;font-weight:600}.literal{color:#8a4f24}.str{color:#206d51}.comment{color:#648169}
.note-start{margin:0 0 14px;padding:0 0 11px;border-bottom:1px solid var(--rule)}
.note-start h2{font-size:15px;margin:0}
.note{break-inside:avoid;margin:0 0 20px}
.target{display:grid;grid-template-columns:35px minmax(0,1fr);min-width:0;border-left:3px solid #9db1c5;background:#eef3f8}
.target .ref{color:#637b90;text-align:center;padding-top:7px;font:11px/20px 'Liberation Mono',monospace;text-decoration:none}
.target code{display:block;padding:7px 9px 7px 2px;white-space:pre-wrap;overflow-wrap:anywhere;min-width:0;font:12px/20px 'Liberation Mono',monospace}
.description{padding:7px 0 0 12px}.meta{font-size:12px;line-height:1.6;margin:0 0 4px;overflow-wrap:anywhere}
.meta.expl{font-weight:600}.meta.comp{color:#43586d}.meta.text{color:#4c5c6c}
.screen-layout+.screen-layout{margin-top:26px}
.library-separator{border-top:1px solid var(--rule);margin:0 0 12px}
#print-pages .library-separator{border-top:.35mm solid #8797a8;margin:2mm 0 2mm}
#print-pages{position:absolute;left:-10000px;top:0;visibility:hidden}
.sheet{width:297mm;height:210mm;padding:7mm 7.8mm 5mm;display:flex;flex-direction:column;background:white;overflow:hidden;break-after:page}
.sheet:last-child{break-after:auto}
.cols{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:3.5mm;flex:1;min-height:0}
.col{min-width:0;min-height:0;padding-right:2mm;border-right:.18mm solid #dce1e7;overflow:hidden}
.col:last-child{padding-right:0;border-right:0}
.footer{height:5mm;flex:0 0 5mm;color:#6b7784;text-align:right;font:7.5pt/5mm 'Liberation Mono',monospace}
#print-pages .intro{border-bottom:.2mm solid #9baab8;padding-bottom:2.5mm;margin-bottom:1.5mm}
#print-pages .intro h1{font-size:11.8pt;margin:0 0 1mm}
#print-pages .intro p{font-size:8pt;line-height:1.45}
#print-pages .code-row{grid-template-columns:5mm minmax(0,1fr)}
#print-pages .code-row .num{font:7pt/1.68 'Liberation Mono',monospace;padding-right:1mm;border-right:.15mm solid var(--rule)}
#print-pages .code-row code{font:8.5pt/1.38 'Liberation Mono','DejaVu Sans Mono',monospace;margin-left:1.5mm}
#print-pages .code-row.shaded{background:#fff3d7;box-shadow:inset 1mm 0 #b69b61}
#print-pages .note-start{border-top:.4mm solid #657789;border-bottom:0;padding:1.9mm 0 2.3mm;margin:0}
#print-pages .note-start h2{font-size:9pt;line-height:1.35}
#print-pages .note{margin:0;padding:0 0 2.4mm}
#print-pages .target{grid-template-columns:5mm minmax(0,1fr);border-left:.5mm solid #8195aa}
#print-pages .target .ref{font:7pt/1.4 'Liberation Mono',monospace;padding:.8mm 0}
#print-pages .target code{font:8pt/1.35 'Liberation Mono',monospace;padding:.8mm .8mm .8mm .4mm}
#print-pages .description{padding:.7mm 0 0;margin-left:5mm}
#print-pages .meta{font-size:8pt;line-height:1.4;margin:0 0 .55mm}
@page{size:A4 landscape;margin:0}
@media screen and (max-width:840px){
#screen{margin:10px auto;padding:0 8px}.screen-layout{display:block}
.screen-code{padding:18px 12px}.screen-notes{position:static;max-height:none;border-left:0;border-top:1px solid var(--rule);padding:18px 14px}
.code-row{grid-template-columns:32px minmax(0,1fr)}.code-row code{margin-left:8px;font-size:12px;line-height:20px}
}
@media print{
html,body{background:white!important}#screen{display:none!important}
#print-pages{position:static;left:auto;top:auto;visibility:visible}
.sheet{margin:0;box-shadow:none;print-color-adjust:exact;-webkit-print-color-adjust:exact}
.kw,.literal,.str,.comment{color:inherit}
}
"""

JS = r"""
(() => {
const screen=document.querySelector('#screen');
const pages=document.querySelector('#print-pages');
const source=document.querySelector('#source');
const groups=Array.from(source.querySelectorAll(':scope > .library-source'));
if(!groups.length) groups.push(source);
const blocks=[];
screen.replaceChildren();
groups.forEach((group,index)=>{
if(index){
const spacer=document.createElement('div');spacer.className='library-separator';
blocks.push(spacer);
}
const layout=document.createElement('section');layout.className='screen-layout';
layout.innerHTML='<article class="screen-code"></article><aside class="screen-notes" aria-label="説明"></aside>';
const code=layout.querySelector('.screen-code'),notes=layout.querySelector('.screen-notes');
for(const block of group.children){
blocks.push(block);
const copy=block.cloneNode(true);
(block.classList.contains('note')||block.classList.contains('note-start')?notes:code).appendChild(copy);
}
screen.appendChild(layout);
});
function buildPrint(){
pages.replaceChildren();
let sheet,colIndex=0,pageNumber=0;
function addPage(){
sheet=document.createElement('main');sheet.className='sheet';
sheet.innerHTML='<div class="cols"><div class="col"></div><div class="col"></div><div class="col"></div></div><footer class="footer"></footer>';
sheet.querySelector('.footer').textContent=String(++pageNumber);pages.appendChild(sheet);colIndex=0;
}
function currentColumn(){return sheet.querySelectorAll('.col')[colIndex]}
function nextColumn(){if(colIndex<2)colIndex++;else addPage()}
addPage();
for(const block of blocks){
let col=currentColumn(),copy=block.cloneNode(true);col.appendChild(copy);
if(copy.getBoundingClientRect().bottom>col.getBoundingClientRect().bottom+.5){
col.removeChild(copy);nextColumn();col=currentColumn();col.appendChild(copy);
if(copy.getBoundingClientRect().bottom>col.getBoundingClientRect().bottom+.5)
console.warn('Printable item exceeds one column');
}
}
}
if(document.fonts)document.fonts.ready.then(buildPrint);else buildPrint();
window.addEventListener('beforeprint',buildPrint);
})();
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
    blocks = [f'<header class="intro"><h1>{escape(name)}</h1>'
              + (f'<p>{escape(description)}</p>' if description else '') + '</header>']
    notes = []
    pending = []
    number = 0
    for kind, value, shaded in visible_items(items, shaded_scopes):
        if kind != 'code':
            pending.append((kind, value))
            continue
        number += 1
        line = value.lstrip(' \t')
        indent = len(value) - len(line) if value.strip() else 0
        # Preserve the original indentation, with a half-indent on wrapped lines.
        spacing = f'padding-left:{indent+2}ch;text-indent:-2ch'
        cls = ' shaded' if shaded else ''
        blocks.append(f'<div class="code-row{cls}" data-no="{number}" id="line-{number}">'
                      f'<span class="num">{number}</span><code style="{spacing}">{highlight(line)}</code></div>')
        if pending:
            note = [f'<section class="note"><div class="target"><a class="ref" href="#line-{number}">{number}</a>'
                    f'<code>{highlight(line)}</code></div><div class="description">']
            for tag, text in pending:
                detail = '計算量 ' + text if tag == 'comp' else text
                note.append(f'<p class="meta {tag}">{escape(detail)}</p>')
            note.append('</div></section>')
            notes.append(''.join(note))
            pending.clear()
    if notes:
        blocks.append('<div class="note-start"><h2>説明</h2></div>')
        blocks.extend(notes)
    source = '\n'.join(blocks)
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(name)}</title><style>{CSS}</style></head>
<body><div id="source" hidden>{source}</div>
<main id="screen"><div class="screen-layout"><article class="screen-code"></article>
<aside class="screen-notes" aria-label="説明"></aside></div></main>
<div id="print-pages" aria-hidden="true"></div><script>{JS}</script></body></html>
'''


def render_all(pages):
    """Join individually rendered HTML pages while sharing their screen/print renderer.

    Each library's original source fragment is preserved. Identifiers are
    namespaced so line-number links do not collide across libraries.
    """
    if not pages:
        raise ValueError("no HTML pages to combine")
    marker = re.compile(
        r'(<div id="source" hidden>)(.*?)(</div>\s*<main id="screen">)',
        re.DOTALL,
    )
    combined = []
    for index, page in enumerate(pages, 1):
        match = marker.search(page)
        if not match:
            raise ValueError(f"missing source element in HTML page #{index}")
        fragment = match.group(2)
        prefix = f'lib{index}-'
        fragment = re.sub(
            r'(?:id="line-|href="#line-)(\d+)"',
            lambda m: m.group(0).replace('line-', f'{prefix}line-', 1),
            fragment,
        )
        combined.append('<section class="library-source">\\n' + fragment
                        + '\\n</section>')
    result = marker.sub(
        lambda m: m.group(1) + '\\n'.join(combined) + m.group(3),
        pages[0],
        count=1,
    )
    return re.sub(r'<title>.*?</title>',
                  '<title>Library_Cpp — All</title>', result, count=1)
