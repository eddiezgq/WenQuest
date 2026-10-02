"""Shared helper for relabelling Chinese figures in English (PIL overlay).
Each figure script: im = load(name); ops...; save(im, name)."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
SRC = '/home/claude/book/img/%s.png'
DST = '/home/claude/sm/img/en/%s.png'
F_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
F_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F_OBL = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'
BG = (251, 250, 247)

def load(name):
    return Image.open(SRC % name).convert('RGB')

def save(im, name):
    im.save(DST % name, optimize=True)
    print('saved', DST % name, im.size)

def _band(a, axis, idx, lo, hi, k=3):
    # median of k pixels just outside the box
    if axis == 'top':
        return np.median(a[max(idx - k, 0):idx, lo:hi], axis=0)
    if axis == 'bot':
        return np.median(a[idx:idx + k, lo:hi], axis=0)
    if axis == 'left':
        return np.median(a[lo:hi, max(idx - k, 0):idx], axis=1)
    if axis == 'right':
        return np.median(a[lo:hi, idx:idx + k], axis=1)

def erase_ink(im, box, ink, fill='v', tol=12, tmin=0.15, grow=1, fcolor=None):
    """Remove only pixels that look like text of colour `ink` (incl. antialiasing)
    inside box, replacing them with the interpolated background; other graphics stay."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    a = np.asarray(im).astype(float)
    tmp = im.copy(); erase(tmp, box, fill, fcolor)
    bgest = np.asarray(tmp).astype(float)[y0:y1, x0:x1]
    p = a[y0:y1, x0:x1]; c = np.array(ink, float)
    d = c[None, None] - bgest; dd = (d * d).sum(2) + 1e-6
    t = ((p - bgest) * d).sum(2) / dd
    tc = t.clip(0, 1)
    dist = np.sqrt(((p - (bgest + tc[..., None] * d)) ** 2).sum(2))
    m = (t > tmin) & (dist < tol)
    if grow:
        from scipy.ndimage import binary_dilation
        m = binary_dilation(m, iterations=grow)
    p[m] = bgest[m]
    a[y0:y1, x0:x1] = p
    im.paste(Image.fromarray(a.clip(0, 255).astype('uint8')))

def erase(im, box, mode='v', color=None):
    """box=(x0,y0,x1,y1). mode: 'v' interpolate columns between rows above/below
    (keeps vertical lines, vertical gradients); 'h' interpolate rows between left/right
    columns; 'c' solid colour (color or BG); 'top'/'bot'/'left'/'right' copy that edge."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    a = np.asarray(im).astype(float)
    H = y1 - y0; W = x1 - x0
    if mode == 'c':
        fill = np.zeros((H, W, 3)); fill[:] = color or BG
    elif mode in ('v', 'top', 'bot'):
        t = _band(a, 'top', y0, x0, x1); b = _band(a, 'bot', y1, x0, x1)
        if mode == 'top': b = t
        if mode == 'bot': t = b
        w = np.linspace(0, 1, H)[:, None, None]
        fill = t[None] * (1 - w) + b[None] * w
    elif mode == 'g':
        t = _band(a, 'top', y0, x0, x1); b = _band(a, 'bot', y1, x0, x1)
        w = np.linspace(0, 1, H)[:, None, None]
        fv = t[None] * (1 - w) + b[None] * w
        l = _band(a, 'left', x0, y0, y1); r = _band(a, 'right', x1, y0, y1)
        w = np.linspace(0, 1, W)[None, :, None]
        fh = l[:, None] * (1 - w) + r[:, None] * w
        fill = np.minimum(fv, fh)
    else:
        l = _band(a, 'left', x0, y0, y1); r = _band(a, 'right', x1, y0, y1)
        if mode == 'left': r = l
        if mode == 'right': l = r
        w = np.linspace(0, 1, W)[None, :, None]
        fill = l[:, None] * (1 - w) + r[:, None] * w
    a[y0:y1, x0:x1] = fill
    im.paste(Image.fromarray(a.clip(0, 255).astype('uint8')))

def font(size, bold=False, italic=False):
    return ImageFont.truetype(F_BOLD if bold else (F_OBL if italic else F_REG), int(round(size)))

def text(im, xy, s, size=30, color=(60, 68, 80), bold=False, anchor='lm', spacing=1.45, italic=False, halo=0, halo_color=(255, 255, 255)):
    """Draw (multi-line) text. anchor: PIL 2-letter anchor applied to the first line's
    reference point; extra lines go below."""
    d = ImageDraw.Draw(im)
    f = font(size, bold, italic)
    x, y = xy
    lines = s.split('\n')
    for i, ln in enumerate(lines):
        d.text((x, y + i * size * spacing), ln, font=f, fill=color, anchor=anchor,
               stroke_width=halo, stroke_fill=halo_color if halo else None)
    return max(d.textlength(l, font=f) for l in lines)

def tw(s, size, bold=False):
    return ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(s, font=font(size, bold))

def rep(im, box, s, size=30, color=(60, 68, 80), bold=False, mode='v', anchor='lm', at=None, ecolor=None, spacing=1.45, italic=False, tol=12, fcolor=None, halo=0, halo_color=(255, 255, 255)):
    """erase box, then draw s. Default: left-aligned, vertically centred in box."""
    if mode.startswith('ink'):
        erase_ink(im, box, ecolor or color, fill=mode[3:] or 'v', tol=tol, fcolor=fcolor)
    else:
        erase(im, box, mode, ecolor)
    x0, y0, x1, y1 = box
    if at is None:
        if anchor[0] == 'l': x = x0
        elif anchor[0] == 'm': x = (x0 + x1) / 2
        else: x = x1
        at = (x, (y0 + y1) / 2)
    return text(im, at, s, size, color, bold, anchor, spacing, italic, halo, halo_color)

# standard header (all figures share the same layout)
TITLE = dict(size=46, color=(31, 41, 55), bold=True)
SUB = dict(size=31, color=(90, 100, 115))

def header(im, title, sub, sub2=None, title_box=None, sub_box=None):
    rep(im, title_box or (75, 50, 2300, 130), title, at=(81, 86), **TITLE)
    if sub is not None:
        rep(im, sub_box or (75, 132, 3340, 192), sub, at=(81, 156), **SUB)

def vtext(im, center, s, size=24, color=(93, 107, 122), bold=False, bg=BG):
    """Text rotated 90° (reading bottom-to-top), centred at `center`."""
    f = font(size, bold)
    w = int(tw(s, size, bold)) + 8; h = int(size * 1.5)
    t = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(t).text((w / 2, h / 2), s, font=f, fill=color + (255,), anchor='mm')
    t = t.rotate(90, expand=True)
    im.paste(t, (int(center[0] - t.width / 2), int(center[1] - t.height / 2)), t)

def badge(im, center, n, r=27, fill=(46, 160, 90), color=(255, 255, 255), size=26):
    d = ImageDraw.Draw(im); x, y = center
    d.ellipse((x - r, y - r, x + r, y + r), fill=fill)
    d.text((x, y), str(n), font=font(size, True), fill=color, anchor='mm')

D = 1.7  # display->original scale used when reading coordinates off previews
def B(x0, y0, x1, y1):
    """box given in preview (2000-px-wide) coordinates -> original pixels"""
    return (x0 * D, y0 * D, x1 * D, y1 * D)
def P(x, y):
    return (x * D, y * D)

def copy_strip(im, box, dy=0, dx=0, src=None):
    """Copy pixels from (box shifted by dx,dy) of the ORIGINAL (or src) into box —
    used to restore dashed/grid lines after erasing text that sat on them."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    s = src or ORIG[0]
    im.paste(s.crop((x0 + dx, y0 + dy, x1 + dx, y1 + dy)), (x0, y0))

ORIG = [None]
_load = load
def load(name):
    im = _load(name); ORIG[0] = im.copy(); return im

def keep_colored(im, box, pred, min_size=40):
    """Restore original pixels inside box for which pred(r,g,b arrays)->bool (e.g. curves)."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    o = np.asarray(ORIG[0]).astype(int)[y0:y1, x0:x1]
    a = np.asarray(im).copy()
    m = pred(o[..., 0], o[..., 1], o[..., 2])
    if min_size:
        from scipy.ndimage import label
        lab, n = label(m, structure=np.ones((3, 3)))
        sizes = np.bincount(lab.ravel())
        m = m & (sizes[lab] >= min_size)
    sub = a[y0:y1, x0:x1]; sub[m] = o[m]; a[y0:y1, x0:x1] = sub
    im.paste(Image.fromarray(a))

def seg_pred(bg, colors, tol=18, tmin=0.25):
    """predicate for keep_colored: pixel lies on the blend line bg->colour (antialiased curve)."""
    bg = np.array(bg, float)
    def f(r, g, b):
        p = np.stack([r, g, b], -1).astype(float); m = np.zeros(r.shape, bool)
        for c in colors:
            d = np.array(c, float) - bg; t = ((p - bg) * d).sum(-1) / (d * d).sum()
            q = bg + t.clip(0, 1)[..., None] * d
            m |= (t > tmin) & (np.sqrt(((p - q) ** 2).sum(-1)) < tol)
        return m
    return f

def redraw_curve(im, box, color, th=None, from_edge='bottom', tol=60):
    """Re-trace a thick curve crossing `box` using its clean edge in the ORIGINAL
    (bottom edge when the text sat above it) and paint it over the erased area."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    o = np.asarray(ORIG[0]).astype(int)
    c = np.array(color)
    # thickness measured in a clean column just left of the box
    def rows(x):
        col = o[y0 - 80:y1 + 80, x]; m = np.sqrt(((col - c) ** 2).sum(1)) < tol
        return np.where(m)[0] + y0 - 80
    if th is None:
        r = rows(x0 - 3); th = (r.max() - r.min() + 1) if len(r) else 8
    pts = []
    for x in range(x0 - 2, x1 + 3):
        r = rows(x)
        if not len(r) or r.max() >= y1 + 79 or r.min() <= y0 - 79: continue
        e = r.max() if from_edge == 'bottom' else r.min()
        pts.append((x, e - (th - 1) / 2 if from_edge == 'bottom' else e + (th - 1) / 2))
    d = ImageDraw.Draw(im)
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        d.line((xa, ya, xb, yb), fill=tuple(color), width=int(th))

def bridge_curve(im, box, color, margin=100, tol=60, th=None, deg=3, ywin=150):
    """Redraw a curve across `box` by fitting a polynomial to its centre line in the
    ORIGINAL just left and right of the box (for curves hidden by erased text)."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    o = np.asarray(ORIG[0]).astype(int); c = np.array(color)
    xs, ys, ths = [], [], []
    for x in list(range(x0 - margin, x0)) + list(range(x1, x1 + margin)):
        col = o[y0 - ywin:y1 + ywin, x]; m = np.sqrt(((col - c) ** 2).sum(1)) < tol
        r = np.where(m)[0]
        if len(r) and r.max() - r.min() < 20:
            xs.append(x); ys.append((r.min() + r.max()) / 2 + y0 - ywin); ths.append(r.max() - r.min() + 1)
    p = np.polyfit(xs, ys, deg)
    th = th or int(np.median(ths))
    d = ImageDraw.Draw(im)
    pts = [(x, np.polyval(p, x)) for x in range(x0 - 3, x1 + 4)]
    for a, b in zip(pts, pts[1:]):
        d.line((*a, *b), fill=tuple(color), width=th)
    r = th / 2
    for x, y in pts[::2]:
        d.ellipse((x - r + .5, y - r + .5, x + r - .5, y + r - .5), fill=tuple(color))
