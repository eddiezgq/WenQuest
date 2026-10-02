import sys; sys.path.insert(0, '/home/claude/sm/figsrc'); from en_relabel_lib import Fig
f = Fig('/home/claude/book/img/fig_12_unit.png')
f.label((45, 30, 902, 72), 'Common structure of an automatic sewing unit: pick-up → locate → sew → cut → stack', bold=True)
f.label((45, 78, 1152, 106), 'Illustrative. The operator only places the pieces in step 1; cylinders, stepper motors and sensors do the rest in sequence, orchestrated by a state machine in the controller (Chapters 15, 18)')
heads = [(223.5, '① Pick-up / loading'), (613.5, '② Locating / folding'), (1004, '③ Sewing'), (1394, '④ Cutting'), (1784, '⑤ Stacking')]
for cx, t in heads:
    f.label((cx - 75, 176, cx + 75, 203), t, bold=True, anchor='c', size=17)
bodies = [
 (65, 'The operator places the garment piece, pocket bag and flap on the loading table; some units pick pieces automatically with suction cups'),
 (455, 'Locating pins, stops and photoelectric sensors find the edges; folding plates and cylinders fold and press the edges'),
 (845, 'The sewing head stays put; the clamp or feed mechanism carries the fabric along the programmed path'),
 (1235, 'Centre knife, corner knives or thread trimmer; cut positions follow the pocket length, flap angle computed automatically'),
 (1625, 'Stacker bar or rollers flip the sewn piece onto the stacker, squared up for the next operation')]
for x, t in bodies:
    f.label((x - 2, 229, x + 200, 302), [t], size=14, lh=24, wrap=315, ytop=True)
f.label((66, 427, 362, 453), 'Time budget of one unit (one cycle)', bold=True)
f.label((200, 498, 296, 522), 'Manual loading a', bold=True, anchor='c', size=15)
f.label((673, 498, 1018, 522), 'Automatic (locating, sewing, cutting, stacking) m', bold=True, anchor='c', size=15)
f.erase((66, 569, 982, 652), fill=(251, 250, 247))
f.label((66, 569, 982, 652), ['A manufacturer’s automatic pocket welter: up to 3000 sti/min, pocket length 18–220 mm, twin-needle lockstitch, stepper-motor feed, centre knife driven by its own stepper motor, corner knives’ lateral position adjustable in 0.1 mm steps; output 1900–2300 pieces/8 h without flap and 1600–1900 pieces/8 h with flap, i.e. about 12.5–18 s per piece; 0.5 MPa compressed air. Manual loading takes only part of the cycle, so one operator can often tend several units at once (Section 12.3).'],
    size=14.5, lh=29.5, wrap=1840, ytop=True, erase=False, color=(31, 42, 54), dx=4, dy=3)
f.save('/home/claude/sm/img/en/fig_12_unit.png')
