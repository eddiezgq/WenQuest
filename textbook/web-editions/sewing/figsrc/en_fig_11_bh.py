import sys; sys.path.insert(0, '/home/claude/sm/figsrc'); from en_relabel_lib import Fig
f = Fig('/home/claude/book/img/fig_11_bh.png')
f.label((45, 30, 320, 72), 'Buttonholes: straight and eyelet', bold=True)
f.label((45, 78, 840, 106), 'Illustrative. Straight buttonholes use a zigzag lockstitch, common on shirts; eyelet buttonholes use a double chainstitch with gimp, common on suits and jeans')
f.label((65, 165, 280, 196), 'Sewing sequence of a straight buttonhole', bold=True)
f.label((1030, 165, 1410, 196), 'Eyelet buttonhole: needle and looper turn around the eye at the round end', bold=True)
f.label((1110, 358, 1265, 382), 'Gimp (thickens, shapes)', bold=True)
f.erase((1706, 333, 1782, 385))
f.vline(1788, 330, 392, 450, w=1.2)
f.label((1704, 335, 1782, 383), ['Needle and', 'looper turn', 'around the eye'], bold=True, size=14, lh=22, dx=4, erase=False, color=(31, 42, 54))
f.label((88, 615, 600, 830), [
    '① First zigzag row: the needle bar swings to form the zigzag; the feed advances the fabric.',
    '② Bartack at one end: bight widened, feed stopped, a few stitches to reinforce.',
    '③ Second zigzag row: feed reversed, swing centre of the needle bar moved to the other side.',
    '④ Bartack at the other end.  ⑤ The knife drops to cut the buttonhole (or cut first, sew after).',
    'A manufacturer’s electronic straight buttonholer: needle bar and feed both driven by stepper',
    'motors; 3600 sti/min standard, 4200 max; buttonhole up to 41 mm;',
    'knife length 6.4–31.8 mm; the cutting knife is driven by a motor and crank.'],
    size=15.5, lh=30.6, wrap=860)
f.label((1030, 640, 1500, 850), [
    'Eyelets are for heavy outerwear: the round hole leaves room for the button’s shank.',
    'The stitch is a single-needle double chainstitch with a gimp inside, making the buttonhole full and hard-wearing.',
    'At the round end the needle and looper (together with the spreader mechanism) rotate about the eye centre, keeping the stitches always perpendicular to the buttonhole edge.',
    'A manufacturer’s electronic eyelet buttonholer: 400–2200 sti/min; buttonhole length 10–38 mm; cut-before or cut-after selectable on the control panel; the cutting knife is driven up and down by a stepper motor.'],
    size=15.5, lh=30.6, wrap=880, ytop=True)
f.save('/home/claude/sm/img/en/fig_11_bh.png')
