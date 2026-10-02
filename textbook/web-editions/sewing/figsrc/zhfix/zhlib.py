"""Fix stale numbers in Chinese raster figures: fit Noto Sans CJK SC to the existing label,
erase only the changed characters (or the shifted tail) and redraw them with the fitted font."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC = '/home/claude/book/img/'
DST = '/home/claude/sm/img/'
FONTS = {w: f'/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc' for w in ('Regular', 'Medium', 'Bold', 'DemiLight')}
_fc = {}


def F(w, s):
    k = (w, round(s, 2))
    if k not in _fc:
        f = ImageFont.truetype(FONTS[w], s, index=2)
        assert f.getname()[0] == 'Noto Sans CJK SC'
        _fc[k] = f
    return _fc[k]


LCD = np.array([0x08, 0x4D, 0x56, 0x4D, 0x08], float) / 256
SUBPIX = True


def cover(text, w, s, x, y, W, H):
    """Per-channel coverage (H,W,3) of text drawn with baseline-left origin at float (x, y),
    emulating the RGB sub-pixel anti-aliasing of the original renders."""
    if not SUBPIX:
        im = Image.new('L', (W, H), 0)
        ImageDraw.Draw(im).text((x, y), text, font=F(w, s), fill=255, anchor='ls')
        return np.repeat((np.asarray(im, float) / 255)[..., None], 3, 2)
    im = Image.new('L', (3 * W, 3 * H), 0)
    ImageDraw.Draw(im).text((3 * x, 3 * y), text, font=F(w, 3 * s), fill=255, anchor='ls')
    a = np.asarray(im, float) / 255
    a = a.reshape(H, 3, 3 * W).mean(1)                    # vertical box filter
    a = np.apply_along_axis(lambda r: np.convolve(r, LCD, 'same'), 1, a)
    return np.clip(a.reshape(H, W, 3), 0, 1)


class Fig:
    def __init__(self, name, S=1.0):
        self.name = name
        self.S = S
        self.a = np.asarray(Image.open(SRC + name).convert('RGB')).astype(float)
        self.orig = self.a.copy()
        self.log = []

    def bgcol(self, x0, y0, x1, y1):
        a = self.a.astype(int)
        e = np.concatenate([a[y0, x0:x1], a[y1, x0:x1], a[y0:y1, x0], a[y0:y1, x1]])
        v, c = np.unique(e.reshape(-1, 3), axis=0, return_counts=True)
        return v[c.argmax()].astype(float)

    def fit(self, box, old, weights=('Regular', 'Bold'), thr=60, bg=None, ink=None, size=None, erase='flat'):
        x0, y0, x1, y1 = [int(round(v * self.S)) for v in box]
        bg = np.array(bg, float) if bg is not None else self.bgcol(x0, y0, x1, y1)
        sub = self.a[y0:y1, x0:x1]
        d = np.abs(sub - bg).sum(2)
        m = d > thr
        ys, xs = np.where(d > max(thr, 150) if (d > 150).any() else m)
        bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        if ink is None:
            far = d >= np.percentile(d[m], 90)
            ink = np.median(sub[far], axis=0)
        ink = np.array(ink, float)
        v = ink - bg
        H, W = sub.shape[:2]
        if erase == 'flat':
            tgt = sub - bg
        else:
            Bc = self.a.copy()
            erase(Bc, x0, y0, x1, y1, bg)
            tgt = sub - Bc[y0:y1, x0:x1]
        err = lambda c: (((c * v) - tgt) ** 2).sum()
        global SUBPIX
        per = {}
        sp = SUBPIX
        SUBPIX = False
        for w in weights:
            f100 = F(w, 100)
            l, t, r, b = f100.getbbox(old, anchor='ls')
            s0 = size or 100 * (bb[2] - bb[0]) / (r - l)
            cands = [size] if size else np.arange(np.floor(s0 * 2) / 2 - 3.0, s0 + 3.0, 0.5)
            for s in cands:
                f = F(w, s)
                l, t, r, b = f.getbbox(old, anchor='ls')
                bx, by = bb[0] - l, bb[3] - b
                for dx in np.arange(-3, 3.01, 0.5):
                    for dy in np.arange(-1.5, 1.51, 0.5):
                        c = cover(old, w, s, bx + dx, by + dy, W, H)
                        e = err(c)
                        k = (w, s)
                        if k not in per or e < per[k][0]:
                            per[k] = (e, w, s, bx + dx, by + dy)
        SUBPIX = sp
        out = []
        for e, w, s, bx, by in sorted(per.values(), key=lambda t: t[0]):
            e, w, s, bx, by = self._refine(err, old, w, s, bx, by, W, H)
            out.append((e, w, s, bx, by))
        e, w, s, bx, by = min(out, key=lambda t: t[0])
        rel = e / max((tgt ** 2).sum(), 1e-9)
        return dict(x0=x0, y0=y0, W=W, H=H, w=w, s=s, ox=x0 + bx, oy=y0 + by, bg=bg, ink=ink, rel=rel)

    def _refine(self, err, old, w, s, bx, by, W, H):
        e = err(cover(old, w, s, bx, by, W, H))
        for _ in range(4):                   # sub-pixel position refine at the snapped size
            improved = False
            for dx in (-0.25, 0, 0.25):
                for dy in (-0.25, 0, 0.25):
                    c = cover(old, w, s, bx + dx, by + dy, W, H)
                    ee = err(c)
                    if ee < e - 1e-9:
                        e, nb = ee, (bx + dx, by + dy); improved = True
            if improved:
                bx, by = nb
            else:
                break
        return e, w, s, bx, by

    def fix(self, box, old, new, align='l', weights=('Regular', 'Bold'), thr=60, bg=None, ink=None,
            erase='flat', fitbox=None, pad=3, minrel=0.35, size=None):
        """box: the whole label line (display coords); old: the text fitted inside fitbox (default box).
        Only the changed characters are re-rendered; unchanged text on the side that has to move
        (per align l/r/c) is moved as extracted ink, so its pixels stay the original glyphs."""
        p = self.fit(fitbox or box, old, weights, thr, bg, ink, size, erase)
        f = F(p['w'], p['s'])
        i = 0
        while i < min(len(old), len(new)) and old[i] == new[i]:
            i += 1
        q = 0
        while q < min(len(old), len(new)) - i and old[-1 - q] == new[-1 - q]:
            q += 1
        jo, jn = len(old) - q, len(new) - q
        ox, oy = p['ox'], p['oy']
        xa = ox + f.getlength(old[:i])            # start of changed span
        xb = ox + f.getlength(old[:jo])           # end of changed span (old)
        d = f.getlength(new[:jn]) - f.getlength(old[:jo])
        sh_pre, sh_suf = {'l': (0, d), 'r': (-d, 0), 'c': (-d / 2, d / 2)}[align]
        X0, Y0, X1, Y1 = [int(round(v * self.S)) for v in box]
        _, t, _, b = f.getbbox(old + new, anchor='ls')
        Y0 = max(Y0, int(np.floor(oy + t)) - pad)
        Y1 = min(Y1, int(np.ceil(oy + b)) + pad)
        # split columns: prefix [X0, cA), changed [cA, cB), suffix [cB, X1)
        def inkx(s, side):
            if not s:
                return None
            bb = f.getbbox(s, anchor='ls')
            return bb[side]
        cA = int(np.ceil(ox + inkx(old[:i], 2))) if i else int(np.floor(xa))
        cB = int(np.floor(xb + inkx(old[jo:], 0))) if q else int(np.ceil(xb))
        cA = min(cA, int(np.floor(xa + (inkx(old[i:jo], 0) or 0))))
        cB = max(cB, int(np.ceil(xa + (inkx(old[i:jo], 2) or 0)))) if jo > i else cB
        # compositing region: the line plus room for the moved parts
        R0 = min(X0, X0 + int(np.floor(sh_pre))) - 2
        R1 = max(X1, X1 + int(np.ceil(sh_suf))) + 2
        B = self.a.copy()
        if erase == 'flat':
            B[Y0:Y1, X0:X1] = p['bg']
        else:
            erase(B, X0, Y0, X1, Y1, p['bg'])
        o = self.a[Y0:Y1, R0:R1]
        bgl = B[Y0:Y1, R0:R1]
        den = p['ink'] - bgl
        den = np.where(np.abs(den) < 8, np.sign(den + 1e-9) * 8, den)
        A = np.clip((o - bgl) / den, 0, 1)             # per-channel ink alpha of the original line
        A[:, :X0 - R0] = 0; A[:, X1 - R0:] = 0
        H, W = o.shape[:2]
        layer = np.zeros_like(A)
        def put(c0, c1, dx):
            if c1 <= c0:
                return
            s = int(round(dx))
            seg = A[:, c0 - R0:c1 - R0]
            n0, n1 = c0 - R0 + s, c1 - R0 + s
            l0, l1 = max(n0, 0), min(n1, W)
            layer[:, l0:l1] = np.maximum(layer[:, l0:l1], seg[:, l0 - n0:l1 - n0])
        put(X0, cA, sh_pre)
        put(cB, X1, sh_suf)
        txt = new[i:jn]
        if txt:
            c = cover(txt, p['w'], p['s'], xa + sh_pre - R0, oy - Y0, W, H)
            layer = np.maximum(layer, c)
        self.a[Y0:Y1, R0:R1] = bgl * (1 - layer) + p['ink'] * layer
        msg = (f"{self.name}: {old!r} -> {new!r}  [{p['w']} {p['s']:.2f}px, fit residual {p['rel']:.3f}, "
               f"shift pre {sh_pre:+.1f} suf {sh_suf:+.1f}, rendered {txt!r}]")
        self.log.append(msg)
        print(msg)
        if p['rel'] > minrel:
            raise RuntimeError('poor fit - not saving')
        return p

    def save(self):
        out = np.clip(np.round(self.a), 0, 255).astype(np.uint8)
        Image.fromarray(out).save(DST + self.name)
        ch = np.abs(out.astype(int) - self.orig.astype(int)).sum(2) > 0
        ys, xs = np.where(ch)
        print(f'saved {DST + self.name}; changed px {ch.sum()} in bbox x{xs.min()}-{xs.max()} y{ys.min()}-{ys.max()}')

    def crop(self, box, path, z=3, both=True):
        x0, y0, x1, y1 = [int(round(v * self.S)) for v in box]
        o = Image.fromarray(self.orig[y0:y1, x0:x1].astype(np.uint8))
        n = Image.fromarray(np.clip(np.round(self.a[y0:y1, x0:x1]), 0, 255).astype(np.uint8))
        W, H = o.size
        im = Image.new('RGB', (W, H * 2 + 4) if both else (W, H), 'red')
        if both:
            im.paste(o, (0, 0)); im.paste(n, (0, H + 4))
        else:
            im.paste(n, (0, 0))
        im = im.resize((im.width * z, im.height * z), Image.NEAREST)
        im.save(path)
