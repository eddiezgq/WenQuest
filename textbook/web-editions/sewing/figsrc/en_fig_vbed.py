# Fig. 17-1 (English): needle-bed cross-section of a flat knitting machine — Chinese callouts replaced on the original drawing.
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_pil_lib import *
p = Pic('/home/claude/book/img/fig_vbed.png')
BG, WH, INK, MU = (251, 250, 247), (255, 255, 255), (31, 42, 54), (93, 107, 122)
px = p.im.load()
# caption: clear text but keep the top of the blue yarn that starts just under it
for x in range(78, 1745):
    for y in range(34, 90):
        r, g, b = px[x, y]
        if not (b > r + 50 and 1150 < x < 1260 and y > 70): px[x, y] = BG
p.text((82, 62), 'Cross-section viewed along the needle bed (structural schematic, not to scale): the two needle beds form an inverted V; the carriage rides over them and reciprocates',
       29, MU, anchor='lm')
# (bbox of original label block, title, subtitle)
L = [((561, 86, 1007, 162), 'Yarn-carrier rail and carriers', 'carried by the carriage; feed yarn to the hooks'),
     ((121, 206, 508, 282), 'Raising cam', 'on the carriage cam plate; pushes the needle butt'),
     ((121, 466, 267, 542), 'Needle butt', 'projects above the bed surface'),
     ((121, 726, 447, 802), 'Latch needle', 'lies in the trick and slides up and down'),
     ((122, 1133, 238, 1218), 'Front needle bed', 'fixed'),
     ((121, 1414, 475, 1498), 'Selector jack (intermediate jack)', 'decides whether the butt enters the raising cam'),
     ((2061, 166, 2507, 242), 'Carriage (cam plate)', 'moves along the bed, perpendicular to this view'),
     ((2062, 366, 2538, 442), 'Trick gap', 'gap between the two beds, where loops are formed'),
     ((2061, 566, 2478, 642), 'Stitch-cam stepper motor', 'sets the stitch-cam depth, i.e. the loop length'),
     ((2061, 786, 2268, 862), 'Electromagnetic selector', 'acts needle by needle'),
     ((2061, 1093, 2304, 1178), 'Racking direction', '⊙ means perpendicular to the page'),
     ((2061, 1293, 2458, 1378), 'Back needle bed', 'can shift along its length (racking)'),
     ((2061, 1494, 2268, 1578), 'Take-down rollers', 'pull the fabric down continuously'),
     ((2061, 1694, 2208, 1778), 'Fabric', 'hangs down from the trick gap')]
for (x0, y0, x1, y1), t, s in L:
    p.cover((x0 - 3, y0 - 3, x1 + 3, y1 + 3), BG)
    p.text((x0, y0 + 37), t, 34, INK, bold=True, anchor='ls')
    p.text((x0, y1), s, 25, MU, anchor='ls')
# inset (white panel)
p.cover((2925, 180, 3212, 222), WH)
p.text((3068, 202), 'Latch needle (detail)', 30, INK, bold=True, anchor='mm')
I = [((3241, 314, 3342, 389), 'Hook', 'catches\nnew yarn'),
     ((3241, 453, 3367, 529), 'Latch', 'pivots open\nand shut'),
     ((3241, 633, 3310, 666), 'Stem', None),
     ((3241, 803, 3368, 879), 'Butt', 'driven by\nthe cams')]
for (x0, y0, x1, y1), t, s in I:
    p.cover((x0 - 3, y0 - 3, x1 + 3, y1 + 3), WH)
    p.text((x0, y0 + 32), t, 30, INK, bold=True, anchor='ls')
    if s: p.text((x0, y0 + 46), s, 21, MU, anchor='la', spacing=4)
p.save('/home/claude/sm/img/en/fig_vbed.png')
