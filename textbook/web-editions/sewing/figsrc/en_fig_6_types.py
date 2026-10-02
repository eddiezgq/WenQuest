from en_relabel import *
N = 'fig_6_types'
im = load(N)
K = (31, 42, 54); G = (93, 107, 122); R = (192, 57, 43); GN = (46, 158, 91); AM = (183, 121, 31); BL = (47, 111, 214); W = (255, 255, 255)
header(im, 'Feed systems',
       'Side views, schematic; green arrows: parts that move forward with the fabric during feeding; blue: upper ply; beige: lower ply')
T = dict(size=33, color=K, bold=True, mode='c', ecolor=W)
cols = (0, 647, 1294)
names = ['Drop feed', 'Differential feed', 'Needle feed',
         'Compound feed (dog + needle + alternating feet)', 'Top feed (dog, roller or belt)', 'Electronic feed']
for i, nm in enumerate(names):
    dx = cols[i % 3]; y = 173 if i < 3 else 620
    T2 = dict(T); T2['size'] = 29 if i == 3 else 33
    rep(im, B(100 + dx, y - 14, 420 + dx if i < 3 else 640 + dx, y + 14), nm, at=P(107 + dx, y), **T2)
S = dict(size=23, mode='c', ecolor=W)
rep(im, B(440, 273, 537, 296), 'Foot drags the upper ply', color=R, at=P(443, 284), **S)
rep(im, B(828, 421, 962, 444), 'Differential dog (stroke s_d)', color=G, anchor='mm', at=P(895, 432), size=22, mode='c', ecolor=W)
rep(im, B(1033, 421, 1100, 444), 'Main dog (s)', color=G, anchor='mm', at=P(1070, 432), size=22, mode='c', ecolor=W)
rep(im, B(1737, 202, 1838, 225), 'Needle bar swings\nwith the dog', color=GN, bold=True, at=P(1741, 204), spacing=1.25, **S)
rep(im, B(206, 689, 312, 712), 'Outer foot (lifted)', color=G, anchor='rm', at=P(314, 700), **S)
rep(im, B(403, 680, 547, 703), 'Inner foot moves forward\nwith dog and needle', color=GN, bold=True, at=P(406, 683), spacing=1.25, **S)
rep(im, B(515, 715, 583, 760), 'Alternating lift\n2–6 mm', color=AM, at=P(518, 726), spacing=1.4, **S)
rep(im, B(1126, 666, 1210, 689), 'Top-feed roller', color=GN, bold=True, at=P(1130, 677), **S)
rep(im, B(1786, 841, 1874, 866), 'Stepper motor', 22, BL, bold=True, mode='c', ecolor=(232, 238, 246), anchor='mm', at=P(1829, 853))
NT = dict(size=24, color=G, mode='c', ecolor=W, spacing=1.6)
notes = ["Only the dog pushes the lower ply; the upper\nply is carried by friction between the plies\nand held back by the foot; simplest design,\nthe basic form on lockstitch machines",
         "Two dogs, in front of and behind the needle,\nwith different strokes gather or stretch the\nfabric (Chapter 9); common on overlock and\ncoverstitch machines",
         "The needle, in the fabric, swings forward\nwith the dog, “pinning” the plies together;\nfor slippery or multi-ply fabrics that\nshift easily",
         "Typical design: the inner foot around the\nneedle moves forward with dog and needle;\nthe outer foot holds the fabric while it\nreturns; for heavy fabric, leather, bags, seats",
         "A dog, roller or belt above drives the upper\nply; top and bottom feed amounts can be set\nseparately; this is how sleeve-setting\nmachines ease in the sleeve cap",
         "The dog’s horizontal motion is driven directly\nby a stepper or servo motor; stitch length,\nreverse and changes within a seam come from\nthe program (Chapter 14)"]
for i, t in enumerate(notes):
    dx = cols[i % 3]; y = 464 if i < 3 else 911
    rep(im, B(66 + dx, y - 13, 640 + dx, y + 63), t, at=P(71 + dx, y - 6), **NT)
save(im, N)
