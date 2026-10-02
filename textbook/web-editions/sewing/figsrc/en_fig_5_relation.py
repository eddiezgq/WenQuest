from en_relabel import *
N = 'fig_5_relation'
im = load(N)
K = (31, 42, 54); G = (93, 107, 122); BL = (47, 111, 214); OR = (224, 102, 47); W = (255, 255, 255)
header(im, 'Needle–hook relationship at loop catch',
       'Left: viewed facing the needle scarf; right: section at the height of the hook point. Values are typical service-manual ranges; follow the manual for each model')
rep(im, B(95, 379, 262, 401), 'Loop bulges out on the scarf side', 25, BL, mode='c', ecolor=W, at=P(99, 390))
rep(im, B(95, 484, 175, 506), 'Hook-point path', 25, OR, mode='c', ecolor=W, at=P(99, 495))
rep(im, B(638, 566, 843, 618), 'Hook-point lower edge about\n1.0 mm above the top of the eye\n(needle-bar height)', 26, K, bold=True,
    mode='c', ecolor=W, at=P(642, 570), spacing=1.4)
rep(im, B(539, 616, 582, 637), 'Eye', 25, G, mode='c', ecolor=W, at=P(543, 626))
rep(im, B(80, 910, 560, 962), 'Loop-catch timing: the hook point reaches the needle centre when the needle has\n'
    'risen 1.6–2.5 mm from its lowest point (by fabric class; about 2 mm on a standard machine)', 25, K,
    mode='c', ecolor=W, at=P(83, 922), spacing=1.6)
rep(im, B(1031, 167, 1295, 192), 'Hook-to-needle clearance 0.04–0.1 mm', 28, K, bold=True, mode='c', ecolor=W, at=P(1035, 179))
rep(im, B(1088, 474, 1130, 497), 'Loop', 26, BL, bold=True, mode='c', ecolor=W, anchor='rm', at=P(1127, 485))
rep(im, B(1438, 541, 1480, 565), 'Needle', 27, K, bold=True, mode='h', anchor='mm', at=P(1459, 553))
erase(im, B(1148, 817, 1342, 841), 'c', W)
copy_strip(im, B(1294, 817, 1300, 841), dy=-400)
text(im, P(1245, 829), 'Hook point (sweeps up along the dashed line)', 26, OR, bold=True, anchor='mm', halo=4)
rep(im, B(1020, 910, 1350, 962), 'The hook point must pass between needle and loop:\ndistance of loop from needle > clearance + hook-point thickness', 25, K,
    mode='c', ecolor=W, at=P(1024, 922), spacing=1.6)
save(im, N)
