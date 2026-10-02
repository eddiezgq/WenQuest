from en_relabel import *
N = 'fig_5_ratio'
im = load(N)
K = (31, 42, 54); G = (93, 107, 122); GN = (46, 158, 91); R = (192, 57, 43)
header(im, 'Why the hook turns twice as fast as the main shaft',
       'Horizontal axis: main-shaft angle, two stitches; loop catch 206°, hook point at the bottom after 180° of hook rotation, loop cast off after about 270° (Chapter 4 worked example)')
for cx in (606, 1488):
    rep(im, B(cx - 44, 171, cx + 44, 194), 'Needle in fabric', 24, G, mode='v', anchor='mm', at=P(cx, 182))
lab = ['Catch', 'Hook lowest', 'Cast-off']
for (y, col, xs) in [(256, GN, (669, 890, 1000, 1552, 1772, 1882)), (503, R, (669, 1110, 1331, 1552))]:
    for i, cx in enumerate(xs):
        name = lab[i % 3] if y == 256 else ['Catch', 'Hook lowest', 'Cast-off', 'Catch'][i]
        hw = 33 if 'lowest' in name else 18
        rep(im, B(cx - hw, 246, cx + hw, 267) if y == 256 else B(cx - hw, 493, cx + hw, 514), name, 22, col, mode='v', anchor='mm', at=P(cx, y))
rep(im, B(44, 293, 212, 319), '2:1 (full rotary hook)', 29, K, bold=True, mode='v', at=P(47, 306))
rep(im, B(44, 540, 155, 566), '1:1 (hypothetical)', 29, K, bold=True, mode='v', at=P(47, 553))
rep(im, B(1093, 370, 1520, 420), 'With 2:1 the loop is cast off by 341°, leaving over 100° for\ntake-up and feeding; the hook’s second turn is idle', 26, GN,
    mode='v', at=P(1096, 382), spacing=1.5)
rep(im, B(1304, 617, 1775, 668), 'With 1:1 the first loop is not cast off until 476°\n(116° of the next stitch), but the next needle has\nentered the fabric at 462° (102°): too late', 26, R, bold=True,
    mode='v', at=P(1307, 622), spacing=1.45)
rep(im, B(850, 770, 1235, 796), 'Main-shaft angle (first stitch 0°–360°, second stitch 360°–720°)', 26, G, mode='c', anchor='mm', at=P(1043, 782))
save(im, N)
