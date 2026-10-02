from en_relabel import *
N = 'fig_4_curves'
im = load(N)
G = (93, 107, 122); K = (31, 42, 54); OR = (224, 102, 47)
header(im, 'Thread supply, thread demand and surplus (worked example: fabric 1.5 mm, stitch length 3 mm, loop catch 206°)',
       'Top: thread S released by the take-up lever from its tightest point, and thread D needed by needle and loop; bottom: surplus S − D and the three criteria')
s = 23
rep(im, B(418, 164, 518, 187), 'Tightest take-up 55°', s, G)
rep(im, B(686, 197, 795, 220), 'Eye enters fabric 109°', s, G)
rep(im, B(1169, 197, 1243, 220), 'Loop catch 206°', s, G)
rep(im, B(1600, 164, 1708, 187), 'Max pay-out 293°', s, G)
erase(im, B(1615, 231, 1724, 251), 'c', (249, 239, 232))
redraw_curve(im, B(1615, 231, 1724, 251), (47, 111, 214))
copy_strip(im, B(1609, 231, 1614, 241), dy=136)
copy_strip(im, B(1627, 231, 1634, 241), dy=136)
text(im, P(1618, 208), 'Hook point lowest 296°', s, G)
rep(im, B(1838, 262, 1913, 284), 'Cast-off 341°', s, G)
rep(im, B(422, 607, 553, 630), 'Draw-up q ≈ 4.5 mm', 25, OR)
erase(im, B(50, 360, 80, 450)); vtext(im, P(64, 405), 'Thread, mm', 24, G)
erase(im, B(50, 865, 80, 955)); vtext(im, P(64, 910), 'Surplus, mm', 24, G)
n = 26
rep(im, B(470, 776, 765, 827), 'Before eye entry: surplus\nheld by the check spring,\nmax 9.2 mm ≤ stroke\n(10 mm in the example)', 25, K, at=P(474, 783), mode='g')
copy_strip(im, B(679, 770, 686, 830), dy=-155)
rep(im, B(758, 1054, 1095, 1081), 'Entry to loop catch: surplus never negative\n(min +1.1 mm)', n, K, at=P(762, 1058))
rep(im, B(1314, 876, 1520, 927), 'Loop catch to cast-off: S ≥ D,\nmin surplus 1.9 mm (296°)', n, K, at=P(1317, 889))
rep(im, B(1596, 750, 1690, 773), 'Take-up, draw-up', 25, G, anchor='rm', at=P(1690, 761))
L = 26
rep(im, B(205, 1153, 300, 1178), 'Supply S', L, K, at=P(212, 1165))
rep(im, B(440, 1153, 530, 1178), 'Demand D', L, K, at=P(447, 1165))
rep(im, B(676, 1153, 770, 1178), 'Surplus S − D', L, K, at=P(682, 1165))
rep(im, B(910, 1153, 1080, 1178), 'Range the check spring can hold', L, K, at=P(915, 1165))
save(im, N)
