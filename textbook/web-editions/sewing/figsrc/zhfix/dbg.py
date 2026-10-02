import sys, numpy as np
from PIL import Image
from zhlib import *
def show(name, S, box, old, out, **kw):
    g = Fig(name, S)
    p = g.fit(box, old, **kw)
    x0, y0, W, H = p['x0'], p['y0'], p['W'], p['H']
    c = cover(old, p['w'], p['s'], p['ox'] - x0, p['oy'] - y0, W, H)
    pred = p['bg'] * (1 - c) + p['ink'] * c
    o = g.orig[y0:y0 + H, x0:x0 + W]
    im = np.concatenate([o, pred, 255 - np.abs(o - pred)], 0).astype(np.uint8)
    Image.fromarray(im).resize((W * 4, H * 12), Image.NEAREST).save(out)
    print(p['w'], p['s'], p['rel'], p['ink'])
