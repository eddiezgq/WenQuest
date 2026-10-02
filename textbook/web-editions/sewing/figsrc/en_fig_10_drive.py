import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from en_textswap import Fig
S = 1.7
f = Fig('/home/claude/book/img/fig_10_drive.png', S=S)
INK, GR = (31, 42, 54), (93, 107, 122)
f.swap((40, 30, 640, 70), 'Looper drive: a left–right swing plus a front–back needle-avoiding motion', bold=True, size=23)
f.swap((40, 78, 1130, 106), 'Schematic (not to scale); designs differ between machines. A common one is shown: an eccentric and ball-ended link drive the swing, a second eccentric the front–back motion', size=14.8)
f.swap((945, 158, 1010, 182), 'Left–right swing', anchor='m', bold=True, size=14.5)
f.swap((908, 226, 956, 254), 'Looper', anchor='r', bold=True, size=16.5)
bb, bg, c = f.ink((885, 353, 1222, 381)); f.clear(bb, scaled=False)
import numpy as np
from PIL import Image, ImageDraw
_a = np.asarray(f.im).copy(); _o = np.asarray(f.orig)
for X in range(int(870 * S), int(1230 * S)):
    yt = int((352 + (X / S - 607) * 95 / 855 - 7.5) * S)
    _a[yt:int(400 * S), X] = _o[yt:int(400 * S), X]
f.im = Image.fromarray(_a); f.d = ImageDraw.Draw(f.im)
f.text(890, 300, 'Looper rocker shaft', 15.5, c, True)
f.text(890, 323, 'not parallel to the hook shaft,', 14.5, c)
f.text(890, 345, 'can slide axially', 14.5, c)
f.swap((1370, 372, 1414, 394), 'Front–back', anchor='m', bold=True, size=14.5)
f.swap((680, 436, 726, 460), 'Rocker', anchor='r', bold=True, size=15.5)
f.swap((312, 533, 394, 560), 'Ball-ended link', anchor='r', bold=True, size=16)
f.swap((214, 562, 394, 585), 'ball joints at both ends allow spatial motion', anchor='r', size=14)
bb, bg, c = f.ink((172, 666, 388, 694)); f.clear(bb, scaled=False)
f.text(140, 654, 'Hook shaft', 16.5, c, True)
f.text(140, 681, 'turns 1 : 1 with the main shaft', 14.5, c, False)
f.swap((450, 793, 538, 820), 'Swing eccentric', anchor='m', bold=True, size=16.5)
f.swap((405, 822, 585, 846), 'sets the looper’s left–right stroke and phase', anchor='m', size=14)
f.swap((1532, 781, 1620, 808), 'Needle-avoiding eccentric', anchor='m', bold=True, size=16.5)
f.swap((1495, 810, 1660, 834), 'sets the front–back avoiding amount and phase', anchor='m', size=14)
f.swap((1545, 532, 1742, 556), 'A fork lever slides the rocker shaft axially', size=14)
f.swap((1550, 556, 1778, 580), '(front–back along the shaft; the looper follows)', size=14)
bb, bg, c = f.ink((62, 897, 1050, 982)); f.clear(bb, scaled=False)
for i, t in enumerate(['The two motions are about 90° apart in phase, so the point traces a flat ellipse: forward stroke behind the needle, return stroke in front (Fig. 10-3). The manual’s adjustments all act on these two mechanisms:',
                       'the phase of the swing eccentric sets “looper roughly at its rightmost when the needle is lowest” and the heights on the forward and return passes (A = B); the swing link sets the retraction;',
                       'the scribed line on the needle-avoiding eccentric is aligned with the standard position to set the avoiding amount; finally set the point-to-needle clearance (0–0.05 mm) and the needle guard.']):
    f.text(70, 911 + 28 * i, t, 14.6, INK)
f.save(sys.argv[1] if len(sys.argv) > 1 else 'img/en/fig_10_drive.png')
