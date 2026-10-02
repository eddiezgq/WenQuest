import sys; sys.path.insert(0, '/home/claude/sm/figsrc'); from en_relabel_lib import Fig
f = Fig('/home/claude/book/img/fig_12_rail.png')
f.label((45, 30, 328, 72), 'Mechanical structure of a hanger system', bold=True)
f.label((45, 78, 1222, 106), 'Top view with partial side view (not to scale). Carriers holding the pieces circulate on the main rail; after reading a carrier’s ID, the controller opens the entry switch of the chosen work centre')
f.label((856, 221, 1133, 245), 'Main rail (chain-driven, carriers circulate)', bold=True, anchor='c', size=15)
f.label((300, 424, 360, 448), 'Loading station', bold=True, anchor='c', size=15)
f.label((1625, 424, 1716, 448), 'Unloading / QC', bold=True, anchor='c', size=15)
f.label((305, 575, 355, 595), 'Reader', bold=True, anchor='c', size=13.5)
# the old 'entry switch' / 'exit / lift' labels overlapped spur rail 1; rebuild that area from the identical (unlabelled) spur 2, 460 px to the right
S = f.S; x0, y0, x1, y1 = int(425 * S), int(628 * S), int(655 * S), int(705 * S)
f.a[y0:y1, x0:x1] = f.orig[y0:y1, x0 + 460:x1 + 460]
f.text((440, 683), 'Entry switch', 13.5, bold=True, color=(184, 120, 30), anchor='rm')
f.text((618, 655), 'Exit / lift', 13.5, bold=True, color=(46, 158, 91), anchor='rm')
for i in range(5):
    x = 529 + i * 270.6
    f.label((x - 26, 779, x + 26, 801), 'Work centre %d' % (i + 1), bold=True, anchor='c', size=13.5)
f.label((413, 844, 647, 863), 'Buffer on the spur rail: carriers queuing for processing', anchor='c', size=13.5)
f.label((66, 899, 1188, 953), [
    'Main-rail capacity = chain speed ÷ carrier pitch. Illustrative: chain speed 12 m/min, pitch 0.3 m → 40 carriers per minute. A garment passes 6 work centres and every entry and exit occupies the main rail, so main-rail capacity must be several times the output. The number of carriers each spur can hold in front of a work centre (the buffer) determines how often operators run out of work and the WIP of the whole line.'],
    size=14.5, lh=26, wrap=1840, ytop=True)
f.save('/home/claude/sm/img/en/fig_12_rail.png')
