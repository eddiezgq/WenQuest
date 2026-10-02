"""English version of fig_21_marker (Fig. 28-2): garments per marker and utilisation; cut plan."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en__lib_ch26_28 import *

SZ = {'S': ('#ccdfc7', '#2e9e5b'), 'M': ('#ccd5e0', '#2a6fdb'), 'L': ('#f0d3be', '#e0662f'), 'XL': ('#dfcdd8', '#8a3fb0')}
S = []
S.append('<rect x="47" y="130" width="1176" height="752" rx="12" fill="#fff" stroke="#d8dde1" stroke-width="1.5"/>')
S.append('<rect x="1271" y="130" width="682" height="752" rx="12" fill="#fff" stroke="#d8dde1" stroke-width="1.5"/>')
S.append(stext(70, 168, 'Garments per marker and fabric utilisation (illustrative)', 18, INK, 700))
rows = [(207, '1 garment', 78, ['M'], '1.2 m'), (362, '2 garments', 81, ['M', 'L'], '2.3 m'),
        (517, '4 garments (1:1:1:1)', 84, ['S', 'M', 'L', 'XL'], '4.5 m'), (672, '6 garments (1:2:2:1)', 86, ['S', 'M', 'M', 'L', 'L', 'XL'], '6.6 m')]
PW, PG, PP = 62, 6, 14
for y, lab, u, sizes, L in rows:
    S.append(stext(70, y + 35, lab, 17, INK, 700))
    S.append(stext(70, y + 61, f'utilisation {u}%', 14.5, MUTED))
    n = len(sizes); W = n * (2 * PW + PG) + (n - 1) * PP + 14
    S.append(f'<rect x="247" y="{y}" width="{W}" height="82" rx="3" fill="#f3eee3" stroke="#c3b89e" stroke-width="1.5"/>')
    x = 254
    for sz in sizes:
        f, st = SZ[sz]
        for k in range(2):
            px = x + k * (PW + PG)
            S.append(f'<path d="M{px},{y + 9} L{px + PW},{y + 9} L{px + PW - 4},{y + 73} L{px + 4},{y + 73}z" fill="{f}" stroke="{st}" stroke-width="1.6"/>')
        S.append(stext(x + PW + PG / 2, y + 105, sz, 15, st, 700, 'middle'))
        x += 2 * PW + PG + PP
    S.append(stext(247 + W + 14, y + 49, L, 15, MUTED))
S.append(stext(70, 848, 'More garments and mixed sizes let the pieces fill each other’s gaps, so utilisation rises; but a marker that is too long', 15, INK))
S.append(stext(70, 870, 'will not fit on the cutting table.', 15, INK))

S.append(stext(1294, 168, 'Cut plan (1:2:2:1 marker)', 18, INK, 700))
S.append(stext(1294, 209, 'S needs 200 pieces ÷ 1 = 200 plies', 16, INK))
S.append(stext(1294, 237, 'M and L need 400 ÷ 2 = 200 plies, XL 200 ÷ 1 = 200 plies', 16, INK))
S.append(stext(1294, 280, 'Max. 80 plies per lay (limited by knife stroke and accuracy)', 16, '#2a6fdb', 700))
S.append(stext(1294, 305, '→ three lays: 80 + 80 + 40', 16, '#2a6fdb', 700))
for i, (x, n) in enumerate([(1341, 80), (1541, 80), (1741, 40)]):
    h = 395 * n / 80; y = 776 - h
    S.append(f'<rect x="{x}" y="{y}" width="153" height="{h}" fill="#f7f4ec" stroke="#8b7d5a" stroke-width="1.6"/>')
    for k in range(1, n // 4):
        yy = 776 - k * 395 / 20
        S.append(f'<line x1="{x}" x2="{x + 153}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#d6cdb8" stroke-width="1"/>')
    S.append(stext(x + 76, y - 12, f'{n} plies', 17, INK, 700, 'middle'))
    S.append(stext(x + 76, 806, f'Lay {i + 1}', 15, MUTED, 400, 'middle'))
S.append(stext(1294, 852, 'Each lay yields 6 garments per ply; the three lays total 1200 garments.', 15, INK))

print(svg_page('fig_21_marker', 'Marker making and cut planning: garments per marker, plies per lay',
               'Worked-example values: fabric width 150 cm; about 1.1 m per garment in the 6-garment marker; order S 200, M 400, L 400, XL 200; max. 80 plies per lay',
               '\n'.join(S), (40, 122, 1920, 768)))
