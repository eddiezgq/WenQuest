import sys; sys.path.insert(0, '/home/claude/sm/figsrc'); from en_relabel_lib import Fig
f = Fig('/home/claude/book/img/fig_11_emb.png')
f.label((45, 30, 632, 72), 'Computerised embroidery head: a case of needle bars, only one driven at a time', bold=True)
f.label((45, 78, 1042, 106), 'Schematic (not to scale). Left: front view of the head — the needle-bar case holds many needle bars, each threaded with one colour; right: a multi-head machine shares one main shaft')
f.label((150, 204, 362, 230), 'Needle-bar case (shifts sideways)', bold=True)
f.label((1032, 182, 1138, 253), ['Needle-bar driver:', 'drives only the', 'selected needle bar'], bold=True, size=13.5, lh=23.5)
f.label((358, 769, 798, 796), 'Colour change: the case shifts sideways to bring the next colour’s needle bar to the driver and the hook', bold=True, anchor='c', size=14.5)
f.label((468, 869, 772, 894), 'The embroidery frame moves the fabric in X–Y (control: Chapter 16)', anchor='c')
f.label((1245, 165, 1315, 196), 'Multi-head machine', bold=True)
f.label((1505, 235, 1695, 260), 'Upper shaft: one shaft through all heads', bold=True, anchor='c')
for x in (1345, 1498, 1651, 1804):
    f.label((x, 404, x + 42, 429), 'Head %d' % ((x - 1345) // 153 + 1), bold=True, anchor='c')
f.label((1515, 605, 1688, 630), 'Lower shaft: drives the hooks of all heads', bold=True, anchor='c')
f.label((1245, 687, 1590, 836), [
    'All heads embroider the same design at once, sharing the main shaft and the frame.',
    'On some models, after a thread break that head alone can stop (its needle-bar driver disengages) while the others carry on.',
    'A manufacturer\u2019s single-head machine: 9, 12 or 15 needles, up to 1200 r/min.'],
    size=15, lh=30.4, wrap=700, ytop=True)
f.save('/home/claude/sm/img/en/fig_11_emb.png')
