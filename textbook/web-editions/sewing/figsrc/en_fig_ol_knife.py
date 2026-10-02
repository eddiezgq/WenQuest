import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from en_textswap import Fig
f = Fig('/home/claude/book/img/fig_ol_knife.png', S=1.0)
f.swap((75, 98, 640, 152), 'a   Upper knife highest (φ ≈ 0°)', bold=True, size=36)
f.swap((75, 160, 690, 200), 'Blades open 5.2 mm; the fabric is fed in between them', size=21.5)
f.swap((915, 98, 1520, 152), 'b   Upper knife lowest (φ = 180°)', bold=True, size=36)
f.swap((915, 160, 1660, 200), 'Upper edge passes lower edge by 0.8 mm, trimming like scissors', size=21.5)
for x0, y in [(0, 293), (840, 580)]:
    f.swap((x0 + 505, y - 25, x0 + 720, y + 25), 'Upper knife (moving)', anchor='r', bold=True, size=30)
for x0 in (0, 840):
    f.swap((x0 + 360, 1093, x0 + 575, 1143), 'Lower knife (fixed)', anchor='r', bold=True, size=30, mode='inpaint')
    f.swap((x0 + 185, 1185, x0 + 556, 1228), 'Trim line = edge, 4 mm from needle', anchor='r', size=25, dx=-4)
for x in (559, 1399):
    for y in range(1088, 1192):
        if y % 16 < 8:
            f.d.line([(x, y), (x + 1, y)], fill=(123, 135, 148))
f.save(sys.argv[1] if len(sys.argv) > 1 else 'img/en/fig_ol_knife.png')
