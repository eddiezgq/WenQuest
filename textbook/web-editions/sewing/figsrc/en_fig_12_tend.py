import sys; sys.path.insert(0, '/home/claude/sm/figsrc'); from en_relabel_lib import Fig
f = Fig('/home/claude/book/img/fig_12_tend.png')
f.label((45, 30, 508, 72), 'Multi-machine tending: how many automatic units should one operator tend?', bold=True)
f.label((45, 78, 1392, 106), 'Worked example: manual loading a = 5 s, automatic m = 12 s, walk between machines w = 2 s; solid: fixed times; dashed: all three times varying (coeff. of variation 0.3), 8 h simulation')
f.label((78, 463, 102, 572), 'Output (pieces/h)', rot=90, size=14.5)
f.label((996, 483, 1020, 542), 'Utilisation', rot=90, size=14.5)
for xs in ((240, 390.3, 541, 691.5, 842.1), (1164.4, 1329, 1493.5, 1658.5, 1823.2)):
    for i, x in enumerate(xs):
        f.erase((x - 24, 859.4, x + 24, 878), grow=1)
        X0, X1 = int((x - 24) * f.S), int((x + 24) * f.S); f.a[1455:1463, X0:X1] = f.orig[1455:1463, 510][:, None, :]  # rebuild panel border under old labels
        f.text((x, 866), '%d' % (i + 1), 13, color=(93, 107, 122), anchor='mm')
f.label((468, 886, 614, 908), 'Number of machines per operator N', anchor='c', size=15)
f.label((1421, 886, 1567, 908), 'Number of machines per operator N', anchor='c', size=15)
f.label((1103, 194, 1242, 216), 'Operator (loading + walking)', bold=True, size=14.5, fix=[('v', 1164.4, 192, 218, 400, 0.3)])
f.label((1103, 222, 1259, 244), 'Machines (loading + automatic)', bold=True, size=14.5, fix=[('v', 1164.4, 220, 246, 400, 0.3)])
f.label((43, 947, 1452, 998), [
    'With fewer machines than N*, the operator waits for the machines: each extra machine raises output proportionally. With more than N*, the machines wait for the operator: the operator is 100% busy and output stops rising.',
    'Worked example, N* ≈ 2.4: about 424 pieces/h with 2 machines, about 514 with 3, still 514 with 4. With variable times (dashed) machines and operator wait for each other, so output is a few percent below the fixed-time case, the loss being largest near N*.'],
    size=14, lh=27, wrap=1900, ytop=True)
f.save('/home/claude/sm/img/en/fig_12_tend.png')
