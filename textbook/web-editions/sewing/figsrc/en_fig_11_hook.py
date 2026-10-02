import sys; sys.path.insert(0, '/home/claude/sm/figsrc'); from en_relabel_lib import Fig
f = Fig('/home/claude/book/img/fig_11_hook.png')
f.label((45, 30, 878, 72), 'Loop catching at the left and right ends: the wider the bight, the more the catching instants differ', bold=True)
f.label((45, 78, 1055, 106), 'Illustrative: hook radius 13.5 mm (Chapter 5), hook speed twice the main shaft; the large-enough-loop rise of 1.0–4.2 mm uses the illustrative window of Chapter 10')
f.label((356, 206, 398, 229), 'Left', bold=True, anchor='c')
f.label((520, 206, 562, 229), 'Right', bold=True, anchor='c')
f.erase_union([(380, 510, 538, 537), (369, 518, 549, 537), (369.5, 512.5, 381, 519), (537, 512.5, 548.5, 519)])
f.label((368, 512, 550, 535), 'Hook point passes right \u2192 left', bold=True, anchor='c', size=12.5, dy=6, color=(184, 120, 30), erase=False)
f.label((435, 627, 484, 653), 'Rotary hook', bold=True, anchor='c', size=16)
f.label((66, 875, 540, 926), [
    'With bight w, the hook-point angle between the two ends is w / R; in main-shaft angle, divide by 2 again:',
    'Δφ = w / (2R). For 8 mm it is about 17°; the right end is caught first, the left end later.'],
    size=14, lh=26, wrap=790, ytop=True)
f.label((878, 438, 902, 588), 'Needle rise (mm)', rot=90, size=14.5)
f.label((1408, 861, 1487, 886), 'Main-shaft angle', anchor='c', size=15)
f.erase((1360, 197, 1477, 219)); f.vline(1446.8, 195, 221, 300, w=0.3)
f.text((1417.1, 207.6), 'Δφ at most about 20°', 14.5, bold=True, color=(31, 42, 54), anchor='mm')
f.erase((1588, 391, 1667, 413)); f.erase((1741, 388, 1922, 410)); f.hline(399.5, 1586, 1925, 1500, w=0.6); f.vline(1607.6, 386, 416, 500, w=0.3); f.vline(1768.2, 386, 432, 500, w=0.3)
f.label((1588, 391, 1667, 413), 'Left end 218°', bold=True, size=14.5, erase=False, color=(47, 111, 213))
f.label((1741, 388, 1922, 410), ['Loop large enough:', '1.0–4.2 mm'], bold=True, anchor='r', size=14.5, lh=21, ytop=True, erase=False, color=(46, 158, 91), dy=-3)
f.erase((1265, 729, 1342, 751)); f.vline(1285.9, 727, 753, 780, w=0.3)
f.text((1267.6, 739.7), 'Right end 198°', 14.5, bold=True, color=(224, 102, 47))
f.label((916, 900, 1635, 974), [
    'Both ends must fall in the large-enough-loop window: the left end is caught at 4.2 mm rise at the latest, the right end at 1.0 mm at the earliest,',
    'so Δφ ≤ 20° and the bight limit is w = 2RΔφ ≈ 9.5 mm, close to the 10 mm maximum bight in the manual.',
    'The manual sets the hook-point height against the needle eye at the leftmost position (caught later, eye nearest the hook point) and checks the hook–needle clearance at the rightmost.'],
    size=14, lh=25, wrap=1020, ytop=True)
f.save('/home/claude/sm/img/en/fig_11_hook.png')
