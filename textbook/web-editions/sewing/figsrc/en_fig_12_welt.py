import sys; sys.path.insert(0, '/home/claude/sm/figsrc'); from en_relabel_lib import Fig
f = Fig('/home/claude/book/img/fig_12_welt.png')
f.label((45, 30, 662, 72), 'Automatic pocket welter: sewing sequence for a double-welt pocket with flap', bold=True)
f.label((45, 78, 942, 106), 'Top view (not to scale). Blue: the two seams; red: cut; the flap and welt strip are first folded and held by the folding plates, then sewn to the body together')
f.label((153, 252, 347, 276), 'Body (trouser panel or jacket front)', bold=True, size=15)
f.label((536, 476, 797, 501), 'Flap (sensors detect its left and right angles)', bold=True, anchor='c', size=15)
f.label((1056, 578, 1199, 601), ['Welt strip', '(folded in two)'], bold=True, size=14.5, lh=21)
f.vline(1200.3, 570, 610, 450, w=0.6)
f.label((431, 654, 902, 676), 'Two needles sew both seams at once; needle spacing 8–20 mm (long type 22–32 mm)', bold=True, anchor='c', size=15)
f.label((413, 689, 929, 711), 'Centre knife cuts the middle, corner knives cut a Y at each end; turn through → welt pocket', bold=True, anchor='c', size=15)
f.label((1338, 181, 1414, 205), 'Sewing sequence', size=15)
f.label((1338, 241, 1625, 636), [
    '① Place the body, flap and welt cloth; press the pedal and the clamp drops to hold them',
    '② Sensors read the positions and angles of both ends of the flap; the program computes the seam start/end points and the corner-knife positions',
    '③ Folding plates fold the welt cloth in two',
    '④ The twin-needle lockstitch head sews two parallel seams while the centre knife cuts (driven by its own motor)',
    '⑤ Corner knives rise from below and make the Y-cuts at both ends',
    '⑥ The clamp opens and the stacker flips the piece onto the stacker',
    '',
    'Only step ① is manual; cylinders, stepper motors and sensors do the rest in sequence.'],
    size=14.5, lh=29, wrap=590, ytop=True)
f.save('/home/claude/sm/img/en/fig_12_welt.png')
