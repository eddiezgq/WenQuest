import sys; sys.path.insert(0, '/home/claude/sm/figsrc'); from en_relabel_lib import Fig
f = Fig('/home/claude/book/img/fig_12_cell.png')
f.label((45, 30, 732, 72), 'U-shaped flexible cell: machines arranged in a U, a few operators walk inside', bold=True)
f.label((45, 78, 942, 106), 'Illustrative: a T-shirt cell with 6 machines and 3 multi-skilled operators; entrance and exit on the same side, so one operator can tend the first and last operations')
for r, a, b in [((136, 211, 240, 237), '① Overlock', 'join shoulders'), ((418, 211, 522, 237), '② Overlock', 'attach collar'),
                ((701, 211, 805, 237), '③ Overlock', 'set sleeves'), ((973, 434, 1097, 461), '④ Overlock', 'close side seams'),
                ((410, 658, 532, 685), '⑥ Coverstitch', 'hem bottom'), ((693, 658, 814, 685), '⑤ Coverstitch', 'hem sleeves')]:
    f.label(r, [a, b], bold=True, anchor='c', size=14.5, lh=23)
f.label((143, 648, 234, 702), ['In: cut pieces', 'Out: finished garment'], bold=True, anchor='c', size=13, lh=26)
f.label((205, 477, 275, 499), 'Flow of pieces', size=13.5)
f.label((324, 507, 406, 529), 'tends ⑥ and ①', bold=True, anchor='c', size=13.5)
f.label((581, 425, 642, 447), 'tends ②③', bold=True, anchor='c', size=13.5)
f.label((723, 531, 784, 553), 'tends ④⑤', bold=True, anchor='c', size=13.5)
f.label((1268, 181, 1395, 205), 'Key points of a U-shaped cell', size=15)
f.label((1268, 240, 1630, 482), [
    '• Machines sit close together and pieces pass directly from one machine to the next, so WIP is only the few pieces in hand and on the tables.',
    '• Each operator can do several operations (multi-skilled); whoever is free helps at the next operation, or hands off by the bucket-brigade rule.',
    '• Entrance and exit are close together, so one operator can tend the first and last operations with the shortest walk.',
    '• A style change only means rearranging these few machines; suited to small batches of a few hundred pieces (Chapter 29).'],
    size=14.5, lh=30.4, wrap=660, ytop=True)
f.label((1268, 517, 1630, 602), ['Virtual lab 29-1 in Chapter 29 puts the same T-shirt into progressive bundle, hanger and U-cell organisations and compares output, WIP and throughput time.'],
    size=14.5, lh=30.4, wrap=660, ytop=True)
f.save('/home/claude/sm/img/en/fig_12_cell.png')
