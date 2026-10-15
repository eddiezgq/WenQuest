"""Whiteboard sample: SVG drawn stroke by stroke with a marker, timed to the narration."""
import json, math, random
from fontTools.ttLib import TTCollection
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

random.seed(7)
import glob
from fontTools.ttLib import TTFont
class Multi:
    # 霞鹜文楷（手写感楷体，OFL）按字切片的 woff2，合成一张字表；英文用 Caveat 手写体
    def __init__(self, files):
        self.fonts = [TTFont(f) for f in files]
        self.map = {}
        for f in self.fonts:
            for cp in f.getBestCmap():
                self.map.setdefault(cp, f)
FD = '../fonts/node_modules/'
ZH = Multi(sorted(glob.glob(FD + 'lxgw-wenkai-webfont/files/lxgwwenkai-bold-subset-*.woff2')))
EN = Multi([FD + '@fontsource/caveat/files/caveat-latin-700-normal.woff2'] + sorted(glob.glob(FD + 'lxgw-wenkai-webfont/files/lxgwwenkai-bold-subset-*.woff2')))
times = json.load(open('times.json'))
INK, GOLD, BLUE, RED = '#1d2329', '#c98a00', '#1f6f9f', '#c2410c'
items = []  # (beat, svg element string, weight, kind)

def text(s, x, y, size, font=ZH, anchor='middle', color=INK, beat=0):
    fs = [font.map[ord(c)] for c in s]
    ks = [size / f['head'].unitsPerEm for f in fs]
    widths = [f['hmtx'][f.getBestCmap()[ord(c)]][0] * k for c, f, k in zip(s, fs, ks)]
    x0 = x - (sum(widths) / 2 if anchor == 'middle' else 0)
    for c, w, f, k in zip(s, widths, fs, ks):
        if c != ' ':
            gs = f.getGlyphSet()
            pen = SVGPathPen(gs)
            gs[f.getBestCmap()[ord(c)]].draw(TransformPen(pen, (k, 0, 0, -k, x0, y)))
            d = pen.getCommands()
            if d:
                items.append((beat, f'<path class="t" d="{d}" stroke="{color}" fill="{color}"/>', 1.0, 'text'))
        x0 += w

def j(v, a=3):
    return v + random.uniform(-a, a)

def line(x1, y1, x2, y2, beat, color=INK, w=4, arrow=False):
    mx, my = (x1 + x2) / 2 + random.uniform(-6, 6), (y1 + y2) / 2 + random.uniform(-6, 6)
    d = f'M{j(x1)},{j(y1)} Q{mx},{my} {j(x2)},{j(y2)}'
    if arrow:
        ang = math.atan2(y2 - y1, x2 - x1)
        for s in (2.6, -2.6):
            d += f' M{x2},{y2} L{x2 + 22 * math.cos(ang + s)},{y2 + 22 * math.sin(ang + s)}'
    items.append((beat, f'<path class="s" d="{d}" stroke="{color}" stroke-width="{w}"/>', 1.0, 'line'))

def box(cx, cy, w, h, zh, en, beat, color=INK, size=40):
    x, y = cx - w / 2, cy - h / 2
    d = (f'M{j(x)},{j(y)} L{j(x + w)},{j(y)} L{j(x + w)},{j(y + h)} L{j(x)},{j(y + h)} L{j(x)},{j(y)} L{j(x + 18)},{j(y + 1, 1)}')
    items.append((beat, f'<path class="s" d="{d}" stroke="{color}" stroke-width="4"/>', 1.0, 'box'))
    text(zh, cx, cy + (6 if en else size * .35), size, ZH, color=color, beat=beat)
    if en:
        text(en, cx, cy + 36, 27, EN, color='#5f6b76', beat=beat)

# ---- the map (left) ----
text('物理学在哪里？', 120, 92, 50, ZH, anchor='start', beat=0)
text('Where does physics sit?', 124, 134, 32, EN, anchor='start', color='#5f6b76', beat=0)
box(650, 210, 290, 96, '自然科学', 'Natural science', 1)
for cx, zh, en in [(240, '生命科学', 'Life science'), (650, '物质科学', 'Physical science'), (1060, '地球科学', 'Earth science')]:
    line(650, 258, cx, 360, 2)
    box(cx, 410, 270, 96, zh, en, 2)
line(650, 458, 450, 560, 3); box(450, 610, 230, 96, '物理学', 'Physics', 3, color=GOLD, size=44)
line(650, 458, 850, 560, 3); box(850, 610, 230, 96, '化学', 'Chemistry', 3)
F = [('力学', 'Mechanics'), ('热学', 'Heat'), ('电磁学', 'E & M'), ('光学', 'Optics'), ('波动', 'Waves'), ('相对论', 'Relativity'), ('量子力学', 'Quantum')]
for i, (zh, en) in enumerate(F):
    cx = 108 + 176 * i
    line(450, 658, cx, 800, 4 if i < 4 else 5, color=GOLD, w=3)
    box(cx, 850, 162, 96, zh, en, 4 if i < 4 else 5, size=34)
# tick on 力学
items.append((6, f'<path class="s" d="M40,808 l18,22 l34,-44" stroke="{RED}" stroke-width="6"/>', 0.6, 'tick'))
# ---- robot arm (right), drawn 170 px left of the first sketch ----
import re as _re
DX = -70
def sh(d):  # shift every "x,y" pair in a path by DX
    return _re.sub(r'(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)', lambda m: f"{float(m.group(1)) + DX:g},{m.group(2)}", d)
def arm(d, w=1.0, color=INK):
    items.append((B, f'<path class="s" d="{sh(d)}" stroke="{color}" stroke-width="5"/>', w, 'arm'))
text('力学', 1560 + DX, 300, 60, ZH, color=RED, beat=6)
text('force & motion', 1560 + DX, 350, 34, EN, color='#5f6b76', beat=6)
B = 7
arm('M1390,960 L1530,960 L1505,915 L1415,915 Z')
arm('M1440,915 L1440,890 M1480,915 L1480,890', .4)
items.append((B, f'<circle class="s" cx="{1460 + DX}" cy="870" r="24" stroke="{INK}" stroke-width="5"/>', .6, 'arm'))
arm('M1450,850 L1580,640 M1474,860 L1600,652')
items.append((B, f'<circle class="s" cx="{1592 + DX}" cy="636" r="20" stroke="{INK}" stroke-width="5"/>', .5, 'arm'))
arm('M1608,624 L1760,590 M1612,648 L1764,614')
arm('M1766,584 L1790,584 L1790,640 L1766,640 M1790,592 L1820,592 M1790,632 L1820,632', .7)
arm('M1808,586 L1868,586 L1868,638 L1808,638 Z', .6, BLUE)
line(1838 + DX, 572, 1838 + DX, 470, B, color=RED, w=5, arrow=True); text('F', 1870 + DX, 505, 48, EN, color=RED, beat=B)
line(1838 + DX, 652, 1838 + DX, 760, B, color=BLUE, w=5, arrow=True); text('mg', 1872 + DX, 765, 44, EN, color=BLUE, beat=B)
text('F = mg', 1560 + DX, 470, 60, EN, color=INK, beat=B)

# ---- timeline: each beat's items share its narration time ----
tl, svg = [], []
for i, (beat, el, w, kind) in enumerate(items):
    svg.append(el.replace('<path ', f'<path id="e{i}" ').replace('<circle ', f'<circle id="e{i}" ').replace('<rect ', f'<rect id="e{i}" '))
for b in range(len(times['beats'])):
    idx = [i for i, it in enumerate(items) if it[0] == b]
    if not idx: continue
    bt = times['beats'][b]
    start, span = bt['start'] + 0.15, max(1.2, bt['dur'] * 0.92)
    tot = sum(items[i][2] for i in idx)
    t = start
    for i in idx:
        d = span * items[i][2] / tot
        tl.append({'id': f'e{i}', 'start': round(t, 3), 'dur': round(d * 0.88, 3), 'text': items[i][3] == 'text'})
        t += d
html = open('page.tpl.html').read().replace('/*SVG*/', '\n'.join(svg)).replace('/*TL*/', json.dumps(tl)).replace('/*TOTAL*/', str(times['total']))
open('page.html', 'w').write(html)
print(len(items), 'items')
