"""Tiny SVG helpers for the English ch18/ch23 diagram figures (coordinates in the original's display units)."""
from xml.sax.saxutils import escape as E

C = dict(r=('#d23b30', '#c4372b'), y=('#c48a17', '#b8791c'), b=('#2a6fdb', '#2a5fb8'), k=('#1b2430', '#1b2430'),
         g=('#2e9e5b', '#1f8a4c'), p=('#8a5cc7', '#7444b4'), o=('#e0662f', '#c4531d'), t=('#14797f', '#0f6e74'))
MUTED = '#5a6570'; INK = '#1b2430'

DEFS = '''<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#5a6570"/></marker>
<marker id="ahp" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#8a5cc7"/></marker></defs>'''


def text(x, y, s, size=14, color=INK, weight=400, anchor='start', extra=''):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}" {extra}>{E(s)}</text>')


def box(x, y, w, h, col, title, lines=(), fill='#fff', tsize=17, lsize=13.5, ty=None, sw=2.4, rx=9, align='middle', lstep=19):
    st, tc = C[col]
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{st}" stroke-width="{sw}"/>']
    cx = x + w / 2 if align == 'middle' else x + 24
    ty = y + 32 if ty is None else y + ty
    if title:
        out.append(text(cx, ty, title, tsize, tc, 700, align))
    for k, l in enumerate(lines):
        out.append(text(cx, ty + 26 + k * lstep, l, lsize, MUTED, 400, align))
    return ''.join(out)


def arrow(x1, y1, x2, y2, color='#5a6570', w=2.4, marker='ah', dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    m = f' marker-end="url(#{marker})"' if marker else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"{d}{m}/>'


def poly(pts, color='#5a6570', w=2.4, marker=None, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    m = f' marker-end="url(#{marker})"' if marker else ''
    p = ' '.join(f'{a},{b}' for a, b in pts)
    return f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{w}"{d}{m}/>'


def svg(x0, y0, w, h, inner, width='100%'):
    return f'<svg viewBox="{x0} {y0} {w} {h}" width="{width}" style="display:block;overflow:visible">{DEFS}{inner}</svg>'
