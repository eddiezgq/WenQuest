import sys; sys.path.insert(0, '/home/claude/sm/figsrc'); from en_relabel_lib import Fig
f = Fig('/home/claude/book/img/fig_11_cam.png')
f.label((45, 30, 760, 72), 'Mechanical button sewer and bartacker: one pattern cam determines the whole pattern', bold=True)
f.label((45, 78, 1200, 106), 'Schematic (not to scale). A high-ratio worm drive turns the pattern cam once per pattern; its two grooves move the button clamp (or clamp frame) in X and Y via levers')
f.label((100, 200, 148, 224), 'Main shaft', bold=True)
f.erase((518, 271, 562, 291), grow=1)
f.label((518, 271, 562, 291), 'Worm', bold=True, anchor='c', erase=False, color=(31, 42, 54), size=15, dy=-1)
f.label((492, 423, 590, 454), 'Pattern cam', bold=True, anchor='c')
f.label((492, 457, 592, 481), '(on the worm wheel)', anchor='c', size=12)
f.label((888, 265, 947, 288), 'X lever', bold=True, anchor='c')
f.erase((723, 333, 770, 356), grow=1)
f.label((723, 333, 770, 356), 'X groove', bold=True, anchor='r', size=14.5, dx=-16, dy=-3, erase=False, color=(184, 120, 30))
f.erase((726, 522, 768, 543), grow=1)
f.label((726, 522, 768, 543), 'Y groove', bold=True, anchor='l', size=14.5, dy=-4, erase=False, color=(46, 158, 91))
f.label((888, 637, 947, 660), 'Y lever', bold=True, anchor='c')
f.label((1103, 446, 1152, 471), 'Button clamp', bold=True, anchor='c')
f.label((1290, 165, 1382, 196), 'Two patterns', bold=True)
f.label((1595, 334, 1768, 359), 'Button: 4 holes, two parallel bars', bold=True)
f.label((1313, 687, 1502, 713), 'Bartack: two zigzag layers, narrow then wide', bold=True)
f.label((66, 744, 835, 832), [
    'One cam revolution = one complete pattern: 8, 16 or 32 stitches on a button sewer, several dozen on a bartacker.',
    'Each “step” on the cam moves the clamp by one stitch; the moving segment must fall in the shaft angle when the needle is out of the fabric.',
    'Sewing 2 or 4 holes: change the cam or flip a changeover lever. Electronic machines replace the cam by stepper motors and a program (Chapter 15).'],
    size=15, lh=30, wrap=1150, ytop=True)
f.label((1290, 745, 1735, 857), [
    'A manufacturer’s single-thread chainstitch button sewer: 1500 sti/min, 8/16/32 stitches, cross feed 2.5–6.5 mm; 2-hole/4-hole switched by a changeover lever.',
    'A manufacturer’s electronic bartacker: sewing area 40 × 30 mm, 3200 sti/min, needle-bar stroke 41.2 mm, intermittent feed on two stepper axes.'],
    size=15, lh=28, wrap=640, ytop=True)
f.save('/home/claude/sm/img/en/fig_11_cam.png')
