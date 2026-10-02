"""English version of fig_21_flow (Fig. 28-1): from sample to bulk production, and labour on a casual-trousers line."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en__lib_ch26_28 import *

S = []
xs = [47, 529, 1012, 1494]
r1 = [('k', 'Style and sample', ['Design sketch, paper patterns', 'Sample fitting and alteration']),
      ('k', 'Spec sheet and tech pack', ['Size chart, fabrics and trims', 'Operations and sewing requirements']),
      ('k', 'Pre-production sample and approval', ['Made in the bulk fabric', 'Customer approval']),
      ('b', 'Operation breakdown and line planning', ['Standard minutes, line balancing', 'Equipment configuration (this chapter)'])]
r2 = [('o', 'Marker making and cutting', ['Markers, spreading, cut plans', 'Automatic cutters (28.2)']),
      ('b', 'Sewing', ['Lockstitch, overlock, special machines', 'Automatic units (Chapters 9–12)']),
      ('g', 'Finishing', ['Buttonholes and buttons, pressing', 'Thread trimming, folding (Chapter 11)']),
      ('g', 'Inspection and packing', ['Size, appearance, stitching', 'Cartons and shipping'])]
for row, y in ((r1, 141), (r2, 388)):
    for i, (c, t, l) in enumerate(row):
        S.append(sbox(xs[i], y, 400, 136, c, t, l, ts=18, ls=14.5, ty=y + 33))
        if i < 3:
            S.append(sline([(xs[i] + 408, y + 68), (xs[i + 1] - 5, y + 68)], '#5a6570'))
S.append(sline([(1694, 277), (1694, 331), (247, 331), (247, 384)], '#3d4752'))
S.append(stext(930, 322, 'After approval, bulk production starts', 15.5, MUTED, 400, 'middle'))
S.append('<rect x="47" y="588" width="1906" height="305" rx="12" fill="#fff" stroke="#d8dde1" stroke-width="1.5"/>')
S.append(stext(70, 628, 'Labour on a casual-trousers line (worked-example times from this chapter, illustrative)', 17, INK, 700))
x0, k = 188, 1718 / 15.6
segs = [(1.0, '#e4855a', ''), (12.6, '#5b8ade', 'Sewing line (22 operations)  12.6 min'), (0.6, '#7d8995', ''), (1.4, '#5fb07e', 'P')]
x = x0
for v, c, lab in segs:
    w = v * k
    S.append(f'<rect x="{x:.1f}" y="683" width="{w:.1f}" height="64" rx="3" fill="{c}"/>')
    if lab == 'P':
        S.append(stext(x + w / 2, 710, 'Pressing and', 14, '#fff', 700, 'middle'))
        S.append(stext(x + w / 2, 731, 'packing 1.4 min', 14, '#fff', 700, 'middle'))
    elif lab:
        S.append(stext(x + w / 2, 723, lab, 16, '#fff', 700, 'middle'))
    x += w
S.append(stext(x0 + 1.0 * k / 2, 786, 'Cutting 1.0', 15, INK, 400, 'middle'))
S.append(stext(x0 + 13.6 * k + 0.3 * k, 786, 'Thread trimming and inspection 0.6', 15, INK, 400, 'middle'))
S.append(stext(70, 846, 'Cutting and pressing times are illustrative. Sewing has the most operations, the longest times and the most people, so it is', 15, INK))
S.append(stext(70, 870, 'where shop-floor management concentrates — and where the methods of this chapter are mainly applied.', 15, INK))

print(svg_page('fig_21_flow', 'From sample to bulk production: the stages a garment goes through in the factory',
               'Illustrative; brackets give the chapters or sections of this book that cover each stage',
               '\n'.join(S), (40, 135, 1920, 765)))
