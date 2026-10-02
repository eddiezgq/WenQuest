import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from en_textswap import Fig, wrap
S = 1.7
f = Fig('/home/claude/book/img/fig_10_form.png', S=S)
INK, GR = (31, 42, 54), (93, 107, 122)
f.swap((40, 30, 670, 70), 'Forming the 401 two-thread chainstitch: four instants in one stitch', bold=True, size=23)
bb, bg, c = f.ink((40, 78, 1560, 106)); f.clear(bb, scaled=False)
f.text(47, 84, 'Seen from the operator’s side (front view); under the throat plate the looper swings left–right and also moves front–back to avoid the needle. Light shading:', 14.5, GR)
f.text(47, 108, 'behind the needle; dark: in front. To show the chain, the stitches already sewn are spread out to the left (the actual feed direction is perpendicular to the page).', 14.5, GR)
P = [(0, 0), (965, 0), (0, 659), (965, 659)]
titles = ['① About 214°: needle has risen 3.4 mm; behind the needle, the looper point enters the loop',
          '② About 260°: needle leaves the fabric; the looper carries the loop on leftwards, spreading it',
          '③ About 130°: next needle down to looper height, looper in front; needle enters the triangle',
          '④ About 176°: looper at its rightmost; the old loop slips off and is drawn tight, chain complete']
caps = ['As the needle rises, the thread on the scarf side is held by the fabric and cannot follow, so it bulges into a loop; the looper point passes close behind the needle (clearance 0–0.05 mm) into the loop, about 1.5 mm above the top of the eye.',
        'The needle leaves the fabric and the feed dog moves the fabric back one stitch length; the looper reaches its leftmost (about 356°) with the needle loop on its blade. The looper thread leaves through the hole near the point and runs back to the previous stitch.',
        'On its return the looper moves in front of the needle (about 0.4 mm from the needle surface); the next needle comes down behind the blade and in front of the looper thread, into the triangle formed by blade, looper thread and old loop. The point is still about 1.4 mm left of the needle centre.',
        'The looper retreats to its rightmost (about 176°); the old needle loop slips off the point and is drawn tight by the take-up, gripping the looper thread. The needle carries the new loop down, forms another loop as it rises, and the cycle repeats.']
for (dx, dy), t, cap in zip(P, titles, caps):
    f.swap((62 + dx, 158 + dy, 960 + dx, 190 + dy), t, bold=True, size=16)
    f.swap((915 + dx, 368 + dy, 962 + dx, 392 + dy), 'Fabric', anchor='r', size=14)
    f.swap((915 + dx, 429 + dy, 962 + dx, 453 + dy), 'Throat plate', anchor='r', size=14)
    bb, bg, c = f.ink((75 + dx, 682 + dy, 960 + dx, 738 + dy)); f.clear(bb, scaled=False)
    wrap(f, 83 + dx, 702 + dy, cap, 14.5, INK, 870, 25)
f.swap((595, 1133, 655, 1160), 'Thread triangle', bold=True, size=15.5)
f.save(sys.argv[1] if len(sys.argv) > 1 else 'img/en/fig_10_form.png')
