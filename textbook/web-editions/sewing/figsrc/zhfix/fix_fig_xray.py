"""fig_xray: gear ratio label '齿轮 2 : 1' -> '齿轮 1 : 2' (hook shaft turns twice per arm-shaft turn).
The digits are a monospaced Latin face with a light halo; the two original glyphs (with halo)
are swapped in place, each re-centred on the other's cell, so no new rendering is needed."""
import numpy as np
from PIL import Image
a = np.asarray(Image.open('/home/claude/book/img/fig_xray.png').convert('RGB')).astype(int)
bg = a[1395, 600].copy()
Y0, Y1 = 1400, 1442
M = 6
blk = lambda x0, x1: a[Y0:Y1, x0 - M:x1 + M].copy()
two, one = blk(574, 594), blk(638, 657)          # ink extents of '2' and '1'
out = a.copy()
out[Y0:Y1, 574 - M:594 + M] = bg
out[Y0:Y1, 638 - M:657 + M] = bg
def paste(b, cx, w):
    x = int(round(cx - w / 2)) - M
    reg = out[Y0:Y1, x:x + b.shape[1]]
    take = np.abs(b - bg).sum(2) > np.abs(reg - bg).sum(2)
    reg[take] = b[take]
paste(one, (574 + 594) / 2, 657 - 638)
paste(two, (638 + 657) / 2, 594 - 574)
Image.fromarray(out.astype(np.uint8)).save('/home/claude/sm/img/fig_xray.png')
