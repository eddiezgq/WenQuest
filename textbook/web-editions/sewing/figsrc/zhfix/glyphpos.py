import numpy as np
from zhlib import *
def glyphpos(name, S, box, old, **kw):
    g = Fig(name, S)
    p = g.fit(box, old, **kw)
    f = F(p['w'], p['s'])
    x0, y0, W, H = p['x0'], p['y0'], p['W'], p['H']
    o = g.orig[y0:y0 + H, x0:x0 + W] - p['bg']
    v = p['ink'] - p['bg']
    res = []
    for k, ch in enumerate(old):
        if ch == ' ':
            continue
        xk = p['ox'] - x0 + f.getlength(old[:k])
        best = None
        for dx in np.arange(-6, 6.01, 0.25):
            c = cover(ch, p['w'], p['s'], xk + dx, p['oy'] - y0, W, H)
            m = c.max(2) > 0.05
            if not m.any(): break
            e = (((c * v - o) ** 2)[m]).sum() / m.sum()
            if best is None or e < best[0]:
                best = (e, dx)
        res.append((ch, round(best[1], 2) if best else None))
    print(p['w'], round(p['s'], 2), res)
