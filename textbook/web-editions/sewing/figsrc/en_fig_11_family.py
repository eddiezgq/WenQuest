import sys; sys.path.insert(0, '/home/claude/sm/figsrc'); from en_relabel_lib import Fig
f = Fig('/home/claude/book/img/fig_11_family.png')
f.label((45, 30, 760, 72), 'Typical special machines: a sewing head + a planar motion + additional actions', bold=True)
f.label((45, 78, 912, 106), 'Illustrative. Each machine does only one job, but its structure splits into the same three parts; the planar motion can only take place while the needle is out of the fabric')
cards = [
 (68, 165, 'Straight buttonholer', 'shirt buttonholes', 'Stitch: 304 zigzag + lengthwise feed', 'Features: two zigzag rows, bartacks at both ends, knife'),
 (709, 165, 'Eyelet buttonholer', 'suit and jeans buttonholes', 'Stitch: double chainstitch + gimp', 'Features: needle and looper rotate around the eye at the round end'),
 (1350, 165, 'Button sewer', 'buttons', 'Stitch: single-thread chainstitch or lockstitch', 'Features: the clamp moves the button together with the fabric'),
 (68, 659, 'Bartacker', 'belt loops, pocket reinforcement', 'Stitch: lockstitch, X–Y feed', 'Features: underlay first, then cover'),
 (709, 659, 'Zigzag machine', 'decorative seams, joining, elastic', 'Stitch: 304 zigzag', 'Features: the needle bar swings left and right'),
 (1350, 659, 'Embroidery machine', 'designs', 'Stitch: lockstitch, frame X–Y', 'Features: multi-needle colour change, multi-head synchronised')]
for x, y, t, s, a, b in cards:
    f.label((x - 2, y - 2, x + 160, y + 31), t, bold=True)
    f.label((x - 2, y + 34, x + 190, y + 60), s)
    f.label((x - 2, y + 356, x + 285, y + 382), a, bold=True)
    f.label((x - 2, y + 389, x + 300, y + 416), b)
f.save('/home/claude/sm/img/en/fig_11_family.png')
