import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from en_textswap import Fig, wrap
S = 1.7
f = Fig('/home/claude/book/img/fig_10_apps.png', S=S)
INK, GR, OR = (31, 42, 54), (93, 107, 122), (192, 72, 22)
f.swap((40, 30, 610, 70), 'Chainstitch and coverstitch on garments: where they are used, and why', bold=True, size=23)
f.swap((40, 78, 690, 106), 'Left: T-shirt; centre: jeans (back view); right: cross-sections of the two seams (layer thickness exaggerated)', size=15.5)
f.swap((452, 154, 606, 184), 'Neck binding: 602', anchor='r', bold=True, size=17.5)
bb = f.swap((60, 248, 175, 278), 'Sleeve hem:', bold=True, size=17.5, dy=-13)
f.text(67, 275, '406', 17.5, INK, True)
f.restore((158, 274, 182, 292), lambda r, g, b: r >= 0)
f.swap((272, 815, 410, 850), 'Hem: 406', anchor='m', bold=True, size=22)
f.swap((225, 852, 458, 880), 'cylinder-bed coverstitch machine, two lines on the face', anchor='m', size=16)
f.swap((203, 910, 480, 936), 'Knits must stretch, so the stitch must stretch with them', anchor='m', size=14.5)
f.swap((672, 160, 835, 190), 'Waistband: multi-needle 401', bold=True, size=17.5)
for reg in [(1058, 555, 1220, 587), (1058, 587, 1195, 610), (1053, 802, 1235, 834), (1053, 834, 1112, 857)]:
    bb, bg, c = f.ink(reg); f.clear(bb, scaled=False)
f.text(1065, 557, 'Back rise:', 17.5, INK, True); f.text(1065, 581, 'two-needle 401', 17.5, INK, True)
f.text(1065, 605, 'feed-off-the-arm,', 14, GR); f.text(1065, 625, 'felled seam', 14, GR)
f.text(1060, 806, 'Inseam:', 17.5, INK, True); f.text(1060, 830, 'two-needle 401', 17.5, INK, True); f.text(1060, 853, 'felled seam', 14, GR)
f.swap((715, 826, 792, 857), 'Side seam', anchor='m', bold=True, size=17.5)
f.swap((700, 857, 808, 882), 'overlock + topstitch', anchor='m', size=14)
f.swap((822, 920, 1085, 948), 'Heavy thread and high loads: must be strong, with some stretch', anchor='m', size=14.5)
for reg in [(1312, 203, 1680, 229), (1312, 229, 1485, 255), (1312, 533, 1695, 559), (1312, 559, 1572, 585), (1288, 851, 1610, 877), (1288, 877, 1675, 903)]:
    bb, bg, c = f.ink(reg); f.clear(bb, scaled=False)
f.text(1318, 214, '① T-shirt hem (406): after folding, two needles hold it on', 15.5, INK, True)
f.text(1318, 239, 'the face; the looper thread covers the raw edge on the back', 15.5, INK, True)
f.swap((1312, 276, 1355, 300), 'Body', size=14)
f.swap((1890, 314, 1932, 338), 'Fold', size=14)
f.swap((1542, 376, 1800, 402), 'Looper thread zigzags underneath, covering the fold’s raw edge', anchor='m', size=14)
f.swap((1588, 406, 1756, 430), '↑ the fold’s raw edge lies between the two needles', anchor='m', size=13)
f.text(1318, 540, '② Jeans back rise (two-needle 401 felled seam):', 15.5, INK, True)
f.text(1318, 564, 'the two pieces are folded into each other and two', 15.5, INK, True)
f.text(1318, 588, 'rows of chainstitch pass through four layers', 15.5, INK, True)
f.swap((1455, 748, 1745, 774), 'All raw edges enclosed; two rows of stitching on each side', anchor='m', size=14)
wrap(f, 1295, 869, 'On a feed-off-the-arm machine the head is a long, slim cantilevered arm: the trouser leg is slipped over the arm and slides off its end once sewn.', 15, INK, 630, 26)
bb, bg, c = f.ink((40, 1025, 930, 1145)); f.clear(bb, scaled=False)
for i, t in enumerate(['Why chainstitch and coverstitch: ① stretch — the loops of a chainstitch can be pulled open, so the seam stretches more than lockstitch and thread breaks less on knits and in loaded seams;',
                       '② no bobbin — thread comes straight from large cones, so long seams can be sewn without stopping to change bobbins; suits long seams and large batches;',
                       '③ appearance and function — coverstitch is neat on the face and covers the raw edge on the back, joining and neatening in a single operation.',
                       'The cost is more thread (Fig. 10-6), and a chainstitch can unravel from its end, so ends must be sewn over or caught in another seam.']):
    f.text(47, 1040 + 30.5 * i, t, 14.8, INK)
f.save(sys.argv[1] if len(sys.argv) > 1 else 'img/en/fig_10_apps.png')
