"""English version of fig_21_ops (Fig. 28-3): operation flow chart of the casual trousers.
Operation names follow the English lab src/en/labs/line21.html."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en__lib_ch26_28 import *

MC = {'OL': ('o', 'Overlock'), 'SN': ('b', 'Lockstitch'), 'BT': ('y', 'Bartacker'), 'CS': ('g', 'Chainstitch'),
      'BH': ('t', 'Buttonholer'), 'BS': ('t', 'Button sewer'), 'HD': ('s', 'Manual')}
OPS = {1: (['Overlock back', 'panels'], 'OL', .45, 129, 151), 2: (['Sew back', 'darts'], 'SN', .40, 261, 151),
       3: (['Make back', 'welt pockets'], 'SN', 1.20, 393, 151), 4: (['Close back', 'pocket bags'], 'SN', .60, 525, 151),
       5: (['Bartack back', 'pockets'], 'BT', .25, 656, 151), 6: (['Overlock', 'front panels'], 'OL', .45, 129, 321),
       7: (['Make slant', 'pockets'], 'SN', .90, 261, 321), 8: (['Topstitch', 'pocket mouths'], 'SN', .50, 393, 321),
       9: (['Overlock fly', 'and fly shield'], 'OL', .35, 129, 492), 10: (['Set zip'], 'SN', .70, 261, 492),
       11: (['Topstitch fly'], 'SN', .55, 393, 492), 12: (['Join front and', 'back rise'], 'OL', .50, 788, 662),
       13: (['Close side', 'seams'], 'OL', .80, 920, 662), 14: (['Topstitch', 'side seams'], 'SN', .60, 1052, 662),
       15: (['Close inseam'], 'OL', .70, 1184, 662), 16: (['Make belt', 'loops'], 'CS', .25, 1184, 833),
       17: (['Attach', 'waistband'], 'SN', 1.30, 1315, 662), 18: (['Finish waist-', 'band ends'], 'SN', .60, 1447, 662),
       19: (['Attach belt', 'loops'], 'BT', .55, 1578, 492), 20: (['Hem legs'], 'SN', .55, 1447, 321),
       21: (['Buttonhole'], 'BH', .20, 1578, 833), 22: (['Sew button'], 'BS', .20, 1710, 833),
       23: (['Trim threads', 'and inspect'], 'HD', .60, 1842, 662)}
W, H = 118, 84
S = []
for i, (t, m, sam, x, y) in OPS.items():
    c, mn = MC[m]; st, tc = COL[c]; y -= 4
    S.append(f'<rect x="{x}" y="{y}" width="{W}" height="{H}" rx="9" fill="#fff" stroke="{st}" stroke-width="2"/>')
    t = [f'{i} {t[0]}'] + t[1:]
    y0 = y + 24 if len(t) == 2 else y + 31
    for k, l in enumerate(t):
        S.append(stext(x + W / 2, y0 + 17 * k, l, 12.8, tc, 700, 'middle'))
    S.append(stext(x + W / 2, y + 70 if len(t) == 2 else y + 59, f'{mn} {sam:.2f}', 13, MUTED, 400, 'middle'))
for lab, y in [(['Back', 'panels'], 189), (['Front', 'panels'], 359), (['Fly'], 529), (['Assembly'], 700), (['Belt loops', 'etc.'], 870)]:
    for k, l in enumerate(lab):
        S.append(stext(47, y + 6 + 20 * k - 10 * (len(lab) - 1), l, 15.5, '#3d4752', 700))
G = '#5a6570'
R = lambda i: OPS[i][3] + W
L = lambda i: OPS[i][3]
for a, b in [(1, 2), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (9, 10), (10, 11), (12, 13), (13, 14), (14, 15), (15, 17), (17, 18), (21, 22)]:
    yc = OPS[a][4] + 38
    S.append(sline([(R(a), yc), (L(b) - 1, yc)], G, 1.8))
S.append(sline([(188, 401), (188, 443), (320, 443), (320, 490)], G, 1.8))      # 6 -> 10
S.append(sline([(771, 227), (771, 700), (786, 700)], G, 1.8))                  # 5 -> 12
S.append(sline([(511, 529), (771, 529)], G, 1.8, False))                       # 11 -> 12
S.append(sline([(511, 359), (903, 359), (903, 700), (918, 700)], G, 1.8))      # 8 -> 13
S.append(sline([(1242, 658), (1242, 359), (1445, 359)], G, 1.8))               # 15 -> 20
S.append(sline([(1299, 829), (1299, 700), (1313, 700)], G, 1.8))               # 16 -> 17
S.append(sline([(1562, 700), (1562, 529), (1576, 529)], G, 1.8))               # 18 -> 19
S.append(sline([(1562, 700), (1562, 870), (1576, 870)], G, 1.8))               # 18 -> 21
S.append(sline([(1565, 359), (1826, 359), (1826, 700), (1840, 700)], G, 1.8))  # 20 -> 23
S.append(sline([(1696, 529), (1826, 529)], G, 1.8, False))                     # 19 -> 23
S.append(sline([(1826, 829), (1826, 700)], G, 1.8, False))                     # 22 -> 23

print(svg_page('fig_21_ops', 'Operation flow chart of the casual trousers: components first, then assembly',
               'Operations and standard minutes are worked-example values (min/piece, allowances included); colours indicate the machine type',
               '\n'.join(S), (40, 135, 1925, 790),
               '23 operations, 13.20 min/piece in total. A published operation list for five-pocket jeans has 30 operations totalling 11.65 min; '
               'one for casual trousers has 83 operations totalling 36.86 min (with more finely divided operations and helper work).'))
