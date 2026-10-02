# -*- coding: utf-8 -*-
"""Helpers for the English redraws of the ch7-8 figures (whole figure = one SVG in the
original's 2000-px display coordinate system, rendered at 1700 CSS px -> 3400 px)."""
import os, subprocess, html
ROOT = '/home/claude/sm'
INK = '#1b2430'; MU = '#5a6570'; GRID = '#d8dde1'; BG = '#faf9f5'
BLUE = '#2f6fd6'; RED = '#c0392b'; GREEN = '#2e9e5b'; PURPLE = '#8e44ad'; AMBER = '#b7791f'; ORANGE = '#e0662f'
DARKGREEN = '#1e6b3a'


def esc(s):
    return html.escape(str(s), quote=False)


def T(x, y, s, size=16, fill=INK, weight=400, anchor='start', rot=None, lh=None, extra=''):
    """text; s may be a list of lines (line height lh)."""
    lines = s if isinstance(s, (list, tuple)) else [s]
    lh = lh or size * 1.6
    tr = f' transform="rotate({rot} {x} {y})"' if rot is not None else ''
    out = []
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x}" y="{y + i * lh:.1f}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
                   f'text-anchor="{anchor}"{tr} {extra}>{ln}</text>')
    return '\n'.join(out)


def L(x1, y1, x2, y2, stroke=GRID, w=1, dash=None, extra=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{d} {extra}/>'


def R(x, y, w, h, fill='#fff', stroke=GRID, sw=1.5, rx=0, extra=''):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def P(pts, stroke=BLUE, w=3, fill='none', dash=None, close=False, extra=''):
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + (' Z' if close else '')
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{w}" fill="{fill}" stroke-linejoin="round" stroke-linecap="round"{da} {extra}/>'


def C(x, y, r, fill='#fff', stroke=INK, sw=2, extra=''):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def head(title, sub, ty=60, sy=98):
    return T(48, ty, title, 30, INK, 700) + '\n' + T(48, sy, sub, 19, MU)


def arrow_marker(id_, color):
    return (f'<marker id="{id_}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')


def build(name, H, body, defs=''):
    src = f'''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">
<style>.fig{{padding:0;width:1700px;background:{BG}}} svg{{display:block}} svg text{{font-family:QFix,"Noto Sans CJK SC",sans-serif}}</style>
<div class="fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 {H}" width="1700" height="{H * 0.85:.0f}">
<defs>{defs}</defs>
<rect x="0" y="0" width="2000" height="{H}" fill="{BG}"/>
{body}
</svg></div>'''
    hp = f'{ROOT}/figsrc/en_{name}.en.html'
    open(hp, 'w').write(src)
    os.makedirs(f'{ROOT}/img/en', exist_ok=True)
    subprocess.run(['node', f'{ROOT}/fig.js', hp, f'{ROOT}/img/en/{name}.png'], check=True, cwd=ROOT)
