from en_relabel import *
N = 'fig_5_window'
im = load(N)
K = (31, 42, 54); G = (93, 107, 122)
header(im, 'Loop-catch window (illustrative model)',
       'Horizontal: hook installation angle (hook-point rotation from the standard position, + = later catch); vertical: needle-bar height (+ = raised); clearance 0.08 mm, Nm 90')
rep(im, B(104, 127, 160, 154), 'Woven fabric', 32, K, bold=True, mode='c', at=P(107, 140))
rep(im, B(1068, 127, 1214, 154), 'Knitted fabric (smaller loop)', 32, K, bold=True, mode='c', at=P(1071, 140))
L = dict(size=26, color=K, mode='c')
rep(im, B(134, 904, 405, 930), 'Loop caught (dark: margin ≥ 0.15 mm)', at=P(137, 917), **L)
rep(im, B(522, 904, 565, 930), 'Skipped stitch', at=P(525, 917), **L)
rep(im, B(910, 904, 1040, 930), 'Hook point too close to eye', at=P(913, 917), **L)
rep(im, B(1297, 904, 1472, 930), 'Needle strike (none at this clearance)', at=P(1300, 917), **L)
erase(im, B(1595, 903, 1956, 931), 'c')
text(im, P(1953, 906), 'White dot: manual standard position;\ndashed outline: manual recommended range', 24, G, anchor='rm', spacing=1.4)
save(im, N)
