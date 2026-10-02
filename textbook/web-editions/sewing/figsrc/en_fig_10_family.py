import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from en_textswap import Fig, wrap
S = 1.7
f = Fig('/home/claude/book/img/fig_10_family.png', S=S)
INK, GR = (31, 42, 54), (93, 107, 122)
f.swap((40, 30, 790, 70), 'The chainstitch family: one looper replaces the rotary hook, and thread is fed straight from the cone', bold=True, size=23)
f.swap((40, 78, 870, 106), 'Illustrative (stitch length enlarged). Blue: needle thread; orange: looper thread; green: cover thread; black dots: needle holes. Sewing direction left to right', size=15.5)
f.swap((605, 130, 750, 160), 'Face (fabric top)', anchor='m', bold=True, size=18.5)
f.swap((1276, 130, 1420, 160), 'Back (fabric underside)', anchor='m', bold=True, size=18.5)
f.swap((1648, 130, 1835, 160), 'Threads · typical use', anchor='m', bold=True, size=18.5)
names = ['Single-thread chainstitch', 'Two-thread chainstitch', 'Two-needle three-thread coverstitch', 'Two-needle four-thread coverstitch', 'Three-needle five-thread coverstitch']
uses = [('1 thread', 'Temporary seams, closing pocket mouths'), ('2 threads', 'Jeans back rise and inseam, waistbands (multi-needle)'),
        ('3 threads', 'T-shirt hems and cuffs, belt loops'), ('4 threads', 'Neckline binding, decorative joining seams'),
        ('5 threads', 'Joining seams in underwear and sportswear (lapped)')]
for k in range(5):
    dy = k * 270.7
    bb, bg, c = f.ink((78, 288 + dy, 380, 320 + dy)); f.clear(bb, scaled=False)
    wrap(f, 83, 309 + dy, names[k], 17, GR, 285, 25, bold=True)
    bb, bg, c = f.ink((1675, 235 + dy, 1940, 325 + dy)); f.clear(bb, scaled=False)
    f.text(1683, 252 + dy, uses[k][0], 16.5, INK)
    wrap(f, 1683, 286 + dy, uses[k][1], 16.5, INK, 255, 28)
bb, bg, c = f.ink((40, 1588, 1200, 1645)); f.clear(bb, scaled=False)
f.text(47, 1603, '101 and 401 look like a straight line on the face, just like 301 lockstitch; the difference is on the back, where a chainstitch is a chain of interlocked loops that can unravel when pulled from the seam end.', 14.8, GR)
f.text(47, 1631, 'In 406, 602 and 605 one looper thread runs back and forth on the back, joining the needle threads into a covering net; 602 and 605 also have a cover thread on the face, so the face is covered and neat too.', 14.8, GR)
f.save(sys.argv[1] if len(sys.argv) > 1 else 'img/en/fig_10_family.png')
