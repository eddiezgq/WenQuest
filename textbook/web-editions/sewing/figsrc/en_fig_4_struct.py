from en_relabel import *
N = 'fig_4_struct'
im = load(N)
K = (31, 42, 54); G = (93, 107, 122); PU = (123, 75, 196); BL = (47, 111, 214); W = (255, 255, 255)
PB = (238, 241, 243)  # panel background
header(im, 'Take-up mechanism and needle-thread path',
       'Viewed along the arm shaft from the left end of the head, face plate removed; take-up mechanism drawn to the worked-example dimensions, φ = 150°; other parts illustrative')
s = 28
rep(im, B(78, 164, 202, 189), 'Arm shaft and\ncrank disc', s, K, mode='c', at=P(80, 165), spacing=1.2)
rep(im, B(276, 164, 380, 189), 'Take-up crank pin', s, K, mode='c', at=P(278, 176))
rep(im, B(511, 164, 686, 189), 'Take-up link (take-up lever)', s, PU, mode='c', at=P(513, 176))
rep(im, B(663, 276, 768, 300), 'Take-up lever eye', s, K, mode='g', at=P(666, 288), halo=4, halo_color=PB)
erase(im, B(553, 343, 658, 365), 'c', PB)
LC = (123, 135, 148)
ImageDraw.Draw(im).line((1064 - 0.7875 * (560 - 560), 560, 1064 - 0.7875 * (630 - 560), 630), fill=LC, width=2)
copy_strip(im, B(553, 368, 658, 372), dy=0)  # (no-op guard)
text(im, P(555, 354), 'Tightest take-up 55°', 25, G, halo=4, halo_color=PB)
erase(im, B(708, 582, 822, 604), 'c', PB)
keep_colored(im, B(708, 582, 822, 604), seg_pred(PB, [BL]), min_size=20)
text(im, P(705, 597), 'Max pay-out 293°', 25, G)
rep(im, B(144, 600, 248, 623), 'Needle-bar\ncrank pin', s, K, mode='g', anchor='rm', at=P(246, 600), spacing=1.2)
rep(im, B(339, 653, 383, 676), 'Rocker', s, PU, mode='g', anchor='rm', at=P(383, 664))
rep(im, B(476, 653, 559, 676), 'Frame\npivot', s, K, mode='c', ecolor=PB, at=P(478, 655), spacing=1.2)
erase(im, B(676, 741, 868, 764), 'c', PB)
text(im, P(680, 745), 'Thread guide\n(adjustable along slot)', s, K, spacing=1.2, halo=3, halo_color=PB)
rep(im, B(104, 894, 148, 917), 'Needle\nbar', s, K, mode='g', anchor='rm', at=P(146, 894), spacing=1.2)
rep(im, B(1021, 1089, 1220, 1112), 'Dashed: path of the eye over one revolution', 26, G, mode='g', anchor='rm', at=P(1218, 1100))
# right-hand list
rep(im, B(1350, 180, 1452, 208), 'Needle-thread path', 36, K, bold=True, mode='c', ecolor=W, at=P(1353, 194))
items = [('Thread stand', 'Thread comes down from the spool on the stand above'),
         ('Tension assembly', 'Two discs pressed by a spring grip the thread and tension it'),
         ('Check spring', 'Takes up slack at low tension; pulled onto its stop at high tension'),
         ('Thread guide', 'Guides the incoming thread; adjustable, changes the pay-out'),
         ('Take-up lever eye', 'Moves with the lever: pays out, takes up and draws up'),
         ('Lower guide point', 'Outgoing guide, leads the thread back toward the needle bar'),
         ('Face-plate guide', 'Fixed on the face plate of the head'),
         ('Needle-bar thread guide', 'Moves with the needle bar; then into the needle eye')]
for i, (t, d) in enumerate(items):
    y = 251 + 108.3 * i
    rep(im, B(1398, y - 13, 1980, y + 12), t, 31, K, bold=True, mode='c', ecolor=W, at=P(1400, y))
    rep(im, B(1398, y + 22, 1982, y + 46), d, 25, G, mode='c', ecolor=W, at=P(1400, y + 34))
rep(im, B(1350, 1122, 1630, 1174), 'The thread length between 4 and 6 changes with\nthe take-up lever: this is the “thread supply”\ncalculated in this chapter', 27, BL, bold=True, mode='c', ecolor=W, at=P(1353, 1120), spacing=1.4)
save(im, N)
