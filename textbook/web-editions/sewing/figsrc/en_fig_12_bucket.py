import sys; sys.path.insert(0, '/home/claude/sm/figsrc'); from en_relabel_lib import Fig
f = Fig('/home/claude/book/img/fig_12_bucket.png')
f.label((45, 30, 692, 72), 'Bucket-brigade cell: order operators from slowest to fastest and the work balances itself', bold=True)
f.label((45, 78, 1052, 106), 'Simulation: 3 operators share all operations of one garment (work content = 1); speeds 0.5, 1.0, 1.5 (work done per unit time)')
f.label((78, 388, 104, 597), 'Hand-off position (fraction of total work)', rot=90, size=14.5)
f.label((563, 837, 660, 861), 'Garment number', anchor='c', size=15)
f.label((878, 461, 1052, 484), '2→3 hand-off: converges to 1/2', bold=True, anchor='r', size=14.5, fix=[('v', 930.9, 459, 486, 300, 0.3)])
f.label((878, 669, 1052, 692), '1→2 hand-off: converges to 1/6', bold=True, anchor='r', size=14.5, fix=[('v', 930.9, 667, 693, 300, 0.3)])
f.label((1173, 203, 1493, 230), 'Throughput comparison (garments per unit time)', bold=True)
f.label((1173, 255, 1320, 279), 'Bucket brigade, slowest → fastest', bold=True)
f.label((1173, 396, 1320, 420), 'Bucket brigade, fastest → slowest', bold=True)
f.label((1173, 537, 1335, 561), 'Fixed segments, 1/3 each', bold=True)
f.label((1173, 689, 1497, 737), ['The three speeds sum to 3.0: with the bucket brigade ordered slowest to fastest, output exactly equals the sum of the speeds; nobody waits.'],
    size=14.5, lh=26, wrap=730, ytop=True)
f.label((43, 875, 1322, 958), [
    'Bucket-brigade rule: when the last operator finishes a garment, they walk back and take over the garment of the operator upstream, who in turn walks back and takes over from the one before; the first operator returns to the start and begins a new garment.',
    'Ordered slowest to fastest, the hand-off points converge automatically: each operator’s share of the work is proportional to their speed (0.5 : 1.0 : 1.5 → 1/6 : 1/3 : 1/2), and nobody waits for anyone (result of Bartholdi and Eisenstein).',
    'In the reverse order the fast operators catch up with the slow ones and have to wait, and output drops to about 1.5; with fixed segments the slowest operator sets the output.'],
    size=14, lh=26, wrap=1900, ytop=True)
f.save('/home/claude/sm/img/en/fig_12_bucket.png')
