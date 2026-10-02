import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from en_textswap import Fig
f = Fig('/home/claude/book/img/fig_500.png', S=1.76)
INK = (38, 46, 56)
for x0, title, sub in [(113, '504  Three-thread overedge', '1 needle + 2 looper threads, about 4 mm wide'),
                       (749, '514  Four-thread overedge', '2 needles + 2 loopers; two needles hold better'),
                       (1385, '516  Five-thread safety stitch', '401 two-thread chain + 504 three-thread overedge')]:
    f.swap((x0 - 5, 30, x0 + 330, 70), title, bold=True, k=0.80)
    f.swap((x0 - 5, 75, x0 + 360, 100), sub, k=0.80)
    for y, s in [(224, 'Top'), (375, 'Edge'), (529, 'Underside')]:
        f.swap((x0 - 60, y - 14, x0 - 6, y + 14), s, anchor='r', bold=(s != 'Edge'), k=0.82 if s != 'Edge' else 0.8)
# legend: clear and redraw with the original swatches
sw = [f.im.crop(tuple(int(v * 1.76) for v in (108, 742, 160, 760))) for _ in range(1)]
import numpy as np
crops = [f.im.crop(tuple(int(v * 1.76) for v in (x, 742, x + 50, 760))) for x in (109, 221, 376, 530)]
leg = f.ink((100, 735, 700, 770))
f.clear((100, 735, 700, 770), pad=0)
x = 109
for c, s in zip(crops, ['Needle thread', 'Upper-looper thread', 'Lower-looper thread', 'Chainstitch looper thread']):
    f.im.paste(c, (int(x * 1.76), int(742 * 1.76)))
    bb = f.text(x + 56, 751, s, 18, INK)
    x = bb[2] / 1.76 + 26
f.d = __import__('PIL.ImageDraw', fromlist=['x']).Draw(f.im)
# footnote moves above the legend
f.swap((1330, 738, 1960, 765), '', clear=True) if False else None
bb, bg, col = f.ink((1330, 738, 1960, 765)); f.clear(bb, scaled=False)
f.text(1953, 700, 'Edge drawn unfolded: upper half is the fabric top, lower half the underside; stitch width 4 mm, stitch length 2.5 mm',
       15.5, col, anchor='rm')
f.save(sys.argv[1] if len(sys.argv) > 1 else 'img/en/fig_500.png')
