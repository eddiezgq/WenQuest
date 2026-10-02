"""Shared helper for relabelling raster figures (ch11-12): erase Chinese text, draw English (DejaVu Sans).
Coordinates are given in 2000-px-wide 'display' units and scaled by S = width/2000."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
FD = '/usr/share/fonts/truetype/dejavu/'
def font(px, bold=False, italic=False):
    n = 'DejaVuSans' + ('-Bold' if bold else '') + ('Oblique' if italic and not bold else '') + ('Oblique' if italic and bold else '')
    n = n.replace('-BoldOblique','-BoldOblique')
    return ImageFont.truetype(FD + n + '.ttf', int(round(px)))

class Fig:
    def __init__(self, src):
        self.im = Image.open(src).convert('RGB')
        self.S = self.im.width / 2000.0
        self.a = np.array(self.im).astype(np.int16)
        self.orig = self.a.copy()
    def sc(self, r): return [int(round(v * self.S)) for v in r]
    def ink(self, r):
        x0, y0, x1, y1 = self.sc(r)
        sub = self.a[y0:y1, x0:x1]
        med = np.median(sub, axis=1, keepdims=True)
        d = np.abs(sub - med).sum(2)
        return sub, med, d
    def erase(self, r, thr=45, grow=3, fill=None, full=False):
        x0, y0, x1, y1 = self.sc(r)
        sub = self.a[y0:y1, x0:x1]
        if fill is not None:
            sub[:] = fill; return
        L = self.a[y0:y1, max(0, x0 - 8):x0 - 1]; R = self.a[y0:y1, x1 + 1:x1 + 8]
        Lm = np.median(L, axis=1).astype(float); Rm = np.median(R, axis=1).astype(float)
        dLR = np.abs(Lm - Rm).sum(1, keepdims=True)
        t = np.linspace(0, 1, x1 - x0)[None, :, None]
        med = (Lm[:, None, :] * (1 - t) + Rm[:, None, :] * t)
        # if the two sides differ a lot (an object on one side), fall back to the lighter-contrast common median
        both = np.median(np.concatenate([L, R], 1), axis=1).astype(float)[:, None, :]
        med = np.where(dLR[:, :, None] > 60, both, med).astype(np.int16)
        d = np.abs(sub - med).sum(2)
        m = Image.fromarray(((d > thr) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * grow + 1))
        m = np.array(m) > 0
        if full: m[:] = True
        if not m.any(): return
        import cv2
        P = 12; H, W = self.a.shape[:2]
        X0, Y0, X1, Y1 = max(0, x0 - P), max(0, y0 - P), min(W, x1 + P), min(H, y1 + P)
        reg = np.ascontiguousarray(self.a[Y0:Y1, X0:X1].astype(np.uint8))
        mk = np.zeros(reg.shape[:2], np.uint8); mk[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0][m] = 255
        out = cv2.inpaint(reg, mk, 6, cv2.INPAINT_TELEA)
        self.a[Y0:Y1, X0:X1] = out.astype(np.int16)
    def erase_union(self, rects):
        """inpaint the union of several display rects in one pass"""
        import cv2
        H, W = self.a.shape[:2]; mk = np.zeros((H, W), np.uint8)
        for r in rects:
            x0, y0, x1, y1 = self.sc(r); mk[y0:y1, x0:x1] = 255
        ys, xs = np.where(mk > 0); P = 14
        Y0, Y1, X0, X1 = max(0, ys.min() - P), min(H, ys.max() + P), max(0, xs.min() - P), min(W, xs.max() + P)
        reg = np.ascontiguousarray(self.a[Y0:Y1, X0:X1].astype(np.uint8))
        self.a[Y0:Y1, X0:X1] = cv2.inpaint(reg, np.ascontiguousarray(mk[Y0:Y1, X0:X1]), 6, cv2.INPAINT_TELEA).astype(np.int16)
        return self
    def measure(self, r, thr=60):
        """ink colour (most contrasting), ink vertical extent (orig px) inside r"""
        x0, y0, x1, y1 = self.sc(r)
        sub = self.a[y0:y1, x0:x1]
        med = np.median(sub.reshape(-1, 3), axis=0)
        d = np.abs(sub - med).sum(2)
        ys = np.where((d > thr).any(1))[0]
        xs = np.where((d > thr).any(0))[0]
        idx = np.unravel_index(np.argmax(d), d.shape)
        col = tuple(int(v) for v in sub[idx])
        if len(ys) == 0: return col, y0, y1, x0, x1
        return col, y0 + ys[0], y0 + ys[-1], x0 + xs[0], x0 + xs[-1]
    def label(self, r, text, bold=False, anchor='l', size=None, color=None, erase=True, thr=45,
              lh=None, dy=0, dx=0, rot=0, italic=False, fill=None, ytop=False, wrap=None, k=0.88, fix=()):
        """r: display rect covering the old text. text: str or list of lines.
        size: display px font size (else from ink height). anchor l/c/r relative to old ink bbox."""
        col, iy0, iy1, ix0, ix1 = self.measure(r)
        if color is None: color = col
        if erase: self.erase(r, thr=thr, fill=fill)
        for fx in fix:
            (self.vline if fx[0] == 'v' else self.hline)(*fx[1:])
        lines = text if isinstance(text, list) else [text]
        if size is None:
            h = (iy1 - iy0 + 1) if rot == 0 else (ix1 - ix0 + 1)
            fpx = h / 0.92 * k
        else: fpx = size * self.S
        f = font(fpx, bold, italic)
        lhp = (lh * self.S) if lh else fpx * 1.45
        if wrap:
            W = wrap * self.S; out = []
            for para in lines:
                cur = ''
                for w in para.split(' '):
                    t = (cur + ' ' + w) if cur else w
                    if f.getlength(t) <= W or not cur: cur = t
                    else: out.append(cur); cur = w
                out.append(cur)
            lines = out
        self.a = self.a  # draw on image from array
        img = Image.fromarray(self.a.astype(np.uint8))
        if rot:
            w = max(f.getbbox(l)[2] for l in lines); hh = int(lhp * len(lines)) + 4
            t = Image.new('RGBA', (w + 4, hh), (0, 0, 0, 0)); td = ImageDraw.Draw(t)
            for i, l in enumerate(lines):
                td.text((2, i * lhp + lhp / 2), l, font=f, fill=color, anchor='lm')
            t = t.rotate(rot, expand=True)
            cx = (ix0 + ix1) / 2 + dx * self.S; cy = (iy0 + iy1) / 2 + dy * self.S
            img.paste(t, (int(cx - t.width / 2), int(cy - t.height / 2)), t)
        else:
            d = ImageDraw.Draw(img)
            n = len(lines)
            if ytop: cy0 = iy0 + fpx * 0.42 + dy * self.S
            else: cy0 = (iy0 + iy1) / 2 - (n - 1) * lhp / 2 + dy * self.S
            for i, l in enumerate(lines):
                y = cy0 + i * lhp
                if anchor == 'l': d.text((ix0 + dx * self.S, y), l, font=f, fill=color, anchor='lm')
                elif anchor == 'c': d.text(((ix0 + ix1) / 2 + dx * self.S, y), l, font=f, fill=color, anchor='mm')
                else: d.text((ix1 + dx * self.S, y), l, font=f, fill=color, anchor='rm')
        self.a = np.array(img).astype(np.int16)
        return self
    def text(self, xy, text, size, bold=False, color=(27, 36, 48), anchor='lm', lh=None, rot=0):
        """free text at display coords"""
        img = Image.fromarray(self.a.astype(np.uint8)); d = ImageDraw.Draw(img)
        f = font(size * self.S, bold); lines = text if isinstance(text, list) else [text]
        lhp = (lh or size * 1.45) * self.S
        for i, l in enumerate(lines):
            d.text((xy[0] * self.S, xy[1] * self.S + i * lhp), l, font=f, fill=color, anchor=anchor)
        self.a = np.array(img).astype(np.int16); return self
    def restore(self, r):
        x0, y0, x1, y1 = self.sc(r); self.a[y0:y1, x0:x1] = self.orig[y0:y1, x0:x1]; return self
    def vline(self, x, y0, y1, src_y, w=1):
        """redraw a vertical line (e.g. box border) at display x from y0..y1 copying the column at src_y"""
        X = int(round(x * self.S)); Y = int(round(src_y * self.S)); W = int(round(w * self.S))
        self.a[int(y0 * self.S):int(y1 * self.S), X - W:X + W + 1] = self.orig[Y, X - W:X + W + 1]; return self
    def hline(self, y, x0, x1, src_x, w=1):
        Y = int(round(y * self.S)); X = int(round(src_x * self.S)); W = int(round(w * self.S))
        self.a[Y - W:Y + W + 1, int(x0 * self.S):int(x1 * self.S)] = self.orig[Y - W:Y + W + 1, X][:, None, :]; return self
    def save(self, out):
        Image.fromarray(self.a.astype(np.uint8)).save(out, optimize=True); print('saved', out)
