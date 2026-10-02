from en_relabel import *
N = 'fig_4_path'
im = load(N)
K = (31, 42, 54); G = (93, 107, 122); R = (192, 57, 43); PU = (123, 75, 196); GR = (92, 102, 112)
header(im, 'Thread-eye path and main-shaft angle',
       'Left: path of the take-up lever eye over one revolution (a dot every 30°); right: needle-bar displacement and eye height versus main-shaft angle (worked example)')
rep(im, B(466, 314, 582, 339), 'Tightest take-up 55°', 27, R, bold=True, mode='c')
rep(im, B(896, 687, 1024, 712), 'Max pay-out 293°', 27, R, bold=True, mode='c', at=P(880, 699))
rep(im, B(230, 406, 272, 429), 'Arm shaft', 25, G, mode='c', anchor='mm')
rep(im, B(354, 760, 432, 783), 'Frame pivot', 25, G, mode='c', anchor='mm')
rep(im, B(1080, 150, 1208, 173), 'mm (upward positive)', 25, G, mode='c')
rep(im, B(1179, 203, 1279, 226), 'Eye highest 39°', 24, G, mode='v')
rep(im, B(1572, 251, 1647, 273), 'Loop catch 206°', 24, G, mode='v')
erase(im, B(1510, 775, 1618, 797), 'g')
copy_strip(im, B(1564, 775, 1569, 797), dy=-170)
text(im, P(1513, 786), 'Needle bar lowest 180°', 24, G, halo=3)
erase(im, B(1766, 775, 1873, 797), 'c', (255, 255, 255))
copy_strip(im, B(1757, 775, 1763, 797), dy=-170)
copy_strip(im, B(1785, 775, 1791, 797), dy=-170)
keep_colored(im, B(1766, 775, 1873, 797), seg_pred((255, 255, 255), [PU]), min_size=30)
redraw_curve(im, B(1748, 775, 1800, 797), PU, th=8, from_edge='top')
text(im, P(1800, 801), 'Eye lowest 288°', 24, G, halo=3)
# legend: relabel and move the second entry to make room
erase(im, B(1160, 876, 1560, 902), 'c')
text(im, P(1163, 889), 'Needle-bar displacement (plotted downward)', 27, K)
d = ImageDraw.Draw(im)
d.line((1600 * D, 889 * D, 1650 * D, 889 * D), fill=PU, width=6)
text(im, P(1660, 889), 'Eye height', 27, K)
erase(im, B(90, 862, 760, 915), 'c')
text(im, P(95, 869), 'Geometrically the eye is highest at 39° and lowest at 288°; thread supply depends on\n'
     'the sum of the eye’s distances to the two guide points, so tightest take-up is at 55°\n'
     'and maximum pay-out at 293°. Take-up spans about 120°, pay-out about 240°.', 25, G, spacing=1.5)
save(im, N)
