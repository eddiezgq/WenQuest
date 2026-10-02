from en_relabel import *
N = 'fig_4_loop'
im = load(N)
K = (31, 42, 54); G = (92, 102, 112); G2 = (93, 107, 122); W = (255, 255, 255)
header(im, 'Geometric model of loop thread demand (viewed along the hook axis)',
       'Loop length = perimeter of the convex hull of fabric hole F, hook point H and the bobbin-case rim already swept by H;\n'
       'the needle passes in front of the bobbin case (worked-example dimensions)', sub_box=(75, 132, 3340, 236))
# the two-line subtitle: redraw with tighter spacing
erase(im, (75, 132, 3340, 236), 'c')
text(im, (81, 156), 'Loop length = perimeter of the convex hull of fabric hole F, hook point H and the bobbin-case rim already swept by H;', **SUB)
text(im, (81, 200), 'the needle passes in front of the bobbin case (worked-example dimensions)', **SUB)
dx = [0, 659, 1318]  # panel offsets (preview px)
titles = ['Loop catch 206°', 'Around the case 250°', 'Hook at bottom 296°']
for i, o in enumerate(dx):
    t = titles[i]
    rep(im, B(62 + o, 163, 300 + o if i < 2 else 330 + o, 196), t, 34, K, bold=True, mode='c', ecolor=W, at=P(64 + o, 180))
    rep(im, B(352 + o, 172, 404 + o, 195), 'F fabric hole', 25, K, bold=True, mode='c', ecolor=W, at=P(353 + o, 183))
    rep(im, B(62 + o, 745, 330 + o, 802), 'Thread needed by needle and loop: %s mm' % ['21.0', '55.0', '79.6'][i], 28, K,
        mode='c', ecolor=W, at=P(64 + o, 758))
    text(im, P(64 + o, 786), '(zero when the needle is at its highest)', 28, K)
# panel 3 title box overlaps F label at x~1660: title is short enough; F label drawn after
# H labels
rep(im, B(354, 333, 410, 353), 'H hook point', 23, G, bold=True, mode='h', at=P(356, 342), halo=4)
rep(im, B(1196, 508, 1252, 530), 'H hook point', 23, G, bold=True, mode='c', ecolor=W, at=P(1197, 518), halo=4)
rep(im, B(1671, 697, 1728, 718), 'H hook point', 23, G, bold=True, mode='c', ecolor=W, at=P(1673, 707), halo=6)
# bobbin-case labels on the shaded disc
for o, mode in [(0, 'h'), (659, 'h')]:
    rep(im, B(318 + o, 494, 364 + o, 518), 'Bobbin case', 26, G2, mode=mode, anchor='mm', at=P(341 + o, 506))
rep(im, B(1636, 494, 1682, 518), '', 26, G2, mode='h')
copy_strip(im, B(1656, 494, 1661, 518), dy=-60)
text(im, P(1650, 506), 'Bobbin case', 26, G2, anchor='rm')
save(im, N)
