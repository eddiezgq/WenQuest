from en_relabel import *
N = 'fig_6_reg'
im = load(N)
K = (31, 42, 54); G = (93, 107, 122); DG = (27, 94, 56); W = (255, 255, 255)
header(im, 'Stitch regulator: the guide-link tilt sets stitch length and direction', None)
erase(im, (75, 132, 3340, 232), 'c')
text(im, (81, 156), 'Principle (schematic): the lower end C of the feed connecting rod is moved up and down ±e by the eccentric while it can only slide along', **SUB)
text(im, (81, 198), 'the guide link; tilt θ gives C a horizontal displacement 2e · tanθ, which reaches the feed bar via the feed rock shaft', **SUB)
titles = ['θ = 28°: forward 3 mm', 'θ = 0: zero stitch length', 'θ = −28°: reverse 3 mm']
pivots = [(193, 604), (746, 624), (1299, 604)]
for i, cx in enumerate((259, 729, 1200)):
    rep(im, B(cx - 110, 167, cx + 110, 194), titles[i], 30, K, bold=True, mode='c', ecolor=W, anchor='mm', at=P(cx, 181))
    rep(im, B(cx - 80, 677, cx + 80, 700), 'Horizontal displacement 2e · tanθ' if i != 1 else 'Zero horizontal displacement', 25, DG, bold=True,
        mode='c', ecolor=W, anchor='mm', at=P(cx, 688))
    rep(im, B(cx - 66, 717, cx + 66, 740), 'Two extreme positions of C', 23, G, mode='c', ecolor=W, anchor='mm', at=P(cx, 728))
    x, y = pivots[i]
    if i == 0:
        erase(im, B(x - 1, y - 10, x + 63, y + 11), 'c', W)
        copy_strip(im, B(257, y - 10, 262, y + 11), dy=70)
        text(im, P(161, y), 'Guide pivot', 23, G, anchor='rm')
    else:
        rep(im, B(x - 1, y - 10, x + 63, y + 11), 'Guide pivot', 23, G, mode='c', ecolor=W, at=P(x, y))
rep(im, B(1615, 160, 1845, 185), 'Stitch length s (mm) vs guide tilt θ', 27, K, bold=True, mode='c', ecolor=W, anchor='mm', at=P(1729, 172))
rep(im, B(1796, 216, 1838, 239), 'Forward', 25, DG, bold=True, mode='g', anchor='mm', at=P(1816, 227))
rep(im, B(1622, 632, 1663, 655), 'Reverse', 25, DG, bold=True, mode='g', anchor='mm', at=P(1642, 643))
rep(im, B(1628, 741, 1820, 763), 'θ (e = 3 mm, ratio 1)', 24, G, mode='h', anchor='mm', at=P(1724, 752))
erase(im, B(45, 790, 1000, 846), 'c')
text(im, P(47, 804), 'Each extra 1 mm of stitch length needs θ to turn by 10.2°, 9.6°, 8.6°, 7.4°, 6.2° in turn: the scale gets denser toward long stitches.\n'
     'The reverse lever pushes the guide link to the other side of the vertical, so the horizontal component of C reverses and the dog pushes the fabric backward above the plate.',
     25, K, spacing=1.65)
save(im, N)
