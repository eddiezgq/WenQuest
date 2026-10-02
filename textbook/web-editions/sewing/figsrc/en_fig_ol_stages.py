import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from en_textswap import Fig, wrap, extend
S = 3344 / 2000
f = Fig('/home/claude/book/img/fig_ol_stages.png', S=S)
INK = (38, 46, 56)
X0 = [48, 536, 1024, 1512]
titles = ['a  Lower looper enters the needle loop', 'b  Upper looper takes lower-looper thread',
          'c  Upper looper carries thread over edge', 'd  Needle enters upper-looper triangle']
caps = ['After bottom dead centre the needle rises 2.6 mm and its thread bulges into a loop behind it; the lower-looper point passes behind the needle with 0.05 mm clearance.',
        'The lower looper is at its leftmost; its thread and blade open a triangle. The upper looper rises from below and enters in front of the blade.',
        'The upper looper is at its upper-left limit with the lower-looper thread on it; its own thread runs slantwise from the eye to the fabric edge, forming another triangle.',
        'The needle descends between the upper-looper blade and the upper-looper thread, locking both looper threads at the needle position.']
for x0, t in zip(X0, titles):
    f.swap((x0 - 4, 15, x0 + 470, 52), t, bold=True, size=19.5)
    bb, bg, c = f.ink((x0 - 4, 650, x0 + 482, 718)); f.clear(bb, scaled=False)
# legend + footnote row (y 745-772) moves down; clear it
crops = [f.im.crop(tuple(int(v * S) for v in (x, 750, x + 52, 767))) for x in (44, 235, 427)]
bb, bg, c = f.ink((0, 740, 2000, 775)); f.clear(bb, scaled=False)
extend(f, bottom=40)
for x0, cap in zip(X0, caps):
    wrap(f, x0, 674, cap, 15.5, INK, 452, 25)
x = 46
for cimg, s in zip(crops, ['Needle thread', 'Upper-looper thread', 'Lower-looper thread']):
    f.im.paste(cimg, (int(x * S), int(791 * S)))
    from PIL import ImageDraw; f.d = ImageDraw.Draw(f.im)
    b = f.text(x + 58, 799, s, 17, INK)
    x = b[2] / S + 30
f.text(1952, 799, 'Dashed: full-turn paths of the looper points (front projection); sizes from the Chapter 9 worked example', 15, (85, 94, 107), anchor='rm')
f.save(sys.argv[1] if len(sys.argv) > 1 else 'img/en/fig_ol_stages.png')
