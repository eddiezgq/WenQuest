"""Helper for English versions of raster figures: cover Chinese labels with local background, draw English text.
Coordinates may be given in a 'display' frame and scaled by S (original px = display px * S)."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np

FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FC = '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf'
FCB = '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'


def font(size, bold=False, cond=False):
    p = (FCB if bold else FC) if cond else (FB if bold else FR)
    return ImageFont.truetype(p, int(round(size)))


class Fig:
    def __init__(self, src, S=1.0):
        self.im = Image.open(src).convert('RGB')
        self.orig = self.im.copy()
        self.S = S
        self.d = ImageDraw.Draw(self.im)
        self.queue = []   # text drawn at save() so later clears never cut earlier labels
        self.defer = True

    def _b(self, box):
        return tuple(int(round(v * self.S)) for v in box)

    def bg_of(self, box):
        """Most common colour on the border of box (original px)."""
        a = np.asarray(self.im)
        x0, y0, x1, y1 = box
        x0 = max(x0, 0); y0 = max(y0, 0); x1 = min(x1, a.shape[1] - 1); y1 = min(y1, a.shape[0] - 1)
        e = np.concatenate([a[y0, x0:x1], a[y1, x0:x1], a[y0:y1, x0], a[y0:y1, x1]])
        vals, cnt = np.unique(e.reshape(-1, 3), axis=0, return_counts=True)
        return tuple(int(v) for v in vals[cnt.argmax()])

    def ink(self, region, bg=None, thr=40):
        """Tight bbox (original px) of pixels in region differing from bg; plus ink colour."""
        x0, y0, x1, y1 = self._b(region)
        if bg is None:
            bg = self.bg_of((x0, y0, x1, y1))
        a = np.asarray(self.im)[y0:y1, x0:x1].astype(int)
        diff = np.abs(a - np.array(bg)).sum(2)
        m = diff > thr
        if not m.any():
            return None, bg, None
        ys, xs = np.where(m)
        bb = (x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1)
        strong = m & (diff >= np.percentile(diff[m], 80))
        col = tuple(int(v) for v in np.median(a[strong], axis=0))
        return bb, bg, col

    def clear(self, box, bg=None, pad=3, mode='flat', scaled=True):
        x0, y0, x1, y1 = self._b(box) if scaled else box
        x0 -= pad; y0 -= pad; x1 += pad; y1 += pad
        if mode == 'flat':
            if bg is None:
                bg = self.bg_of((x0 - 2, y0 - 2, x1 + 2, y1 + 2))
            self.d.rectangle([x0, y0, x1, y1], fill=bg)
        elif mode == 'row':  # vertical gradient: copy colour from just left/right of the box per row
            a = np.asarray(self.im).copy()
            for y in range(y0, y1 + 1):
                l = a[y, max(x0 - 2, 0)].astype(int); r = a[y, min(x1 + 2, a.shape[1] - 1)].astype(int)
                a[y, x0:x1 + 1] = ((l + r) // 2).astype(np.uint8)
            self.im = Image.fromarray(a); self.d = ImageDraw.Draw(self.im)
        elif mode == 'inpaint':  # remove only ink pixels (text over lines / two-tone backgrounds)
            import cv2
            a = np.asarray(self.im).copy()
            sub = a[y0:y1 + 1, x0:x1 + 1].astype(int)
            ref = np.array(bg if bg is not None else self.bg_of((x0, y0, x1, y1)))
            m = (np.abs(sub - ref).sum(2) > 60).astype(np.uint8)
            m = cv2.dilate(m, np.ones((3, 3), np.uint8), iterations=2)
            mask = np.zeros(a.shape[:2], np.uint8); mask[y0:y1 + 1, x0:x1 + 1] = m * 255
            a = cv2.inpaint(a[:, :, ::-1].copy(), mask, 4, cv2.INPAINT_TELEA)[:, :, ::-1]
            self.im = Image.fromarray(np.ascontiguousarray(a)); self.d = ImageDraw.Draw(self.im)
        elif mode == 'col':  # horizontal gradient
            a = np.asarray(self.im).copy()
            for x in range(x0, x1 + 1):
                t = a[max(y0 - 2, 0), x].astype(int); b = a[min(y1 + 2, a.shape[0] - 1), x].astype(int)
                a[y0:y1 + 1, x] = ((t + b) // 2).astype(np.uint8)
            self.im = Image.fromarray(a); self.d = ImageDraw.Draw(self.im)
        return bg

    def text(self, x, y, s, size, color, bold=False, anchor='lm', scaled=True, cond=False, spacing=None):
        if scaled:
            x, y, size = x * self.S, y * self.S, size * self.S
            spacing = spacing * self.S if spacing else None
        f = font(size, bold, cond)
        if self.defer:
            self.queue.append((x, y, s, size, color, bold, anchor, cond, spacing))
            return self.d.textbbox((x, y), s, font=f, anchor=anchor) if '\n' not in s else self.d.multiline_textbbox((x, y), s, font=f, anchor=anchor)
        if '\n' in s:
            sp = spacing or size * 0.45
            self.d.multiline_text((x, y), s, font=f, fill=color, anchor=anchor, spacing=sp,
                                  align={'l': 'left', 'm': 'center', 'r': 'right'}[anchor[0]])
        else:
            self.d.text((x, y), s, font=f, fill=color, anchor=anchor)
        return self.d.textbbox((x, y), s, font=f, anchor=anchor)

    def swap(self, region, s, anchor='l', bold=False, size=None, color=None, k=0.86, dx=0, dy=0,
             mode='flat', thr=40, pad=3, cond=False, bg=None, clear=True):
        """Find the label inside region (display coords), erase it, draw s in its place.
        anchor: l/m/r = align to left edge / centre / right edge of the old label."""
        bb, bg0, col = self.ink(region, bg=bg, thr=thr)
        if bb is None:
            raise ValueError(f'no ink in {region} for {s!r}')
        if clear:
            self.clear(bb, bg=bg0 if mode in ('flat', 'inpaint') else None, pad=pad, mode=mode, scaled=False)
        h = bb[3] - bb[1]
        sz = size * self.S if size else h / 0.92 * k
        c = color or col
        cy = (bb[1] + bb[3]) / 2 + dy * self.S
        x = {'l': bb[0], 'm': (bb[0] + bb[2]) / 2, 'r': bb[2]}[anchor] + dx * self.S
        return self.text(x, cy, s, sz, c, bold, anchor + 'm', scaled=False, cond=cond)

    def rtext(self, x, y, s, size, color, bold=False, angle=90, scaled=True):
        """Rotated text centred at (x, y)."""
        if scaled:
            x, y, size = x * self.S, y * self.S, size * self.S
        f = font(size, bold)
        bb = f.getbbox(s)
        w, h = bb[2] - bb[0] + 8, bb[3] - bb[1] + 8
        t = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((4 - bb[0], 4 - bb[1]), s, font=f, fill=color)
        t = t.rotate(angle, expand=True)
        self.im.paste(t, (int(x - t.width / 2), int(y - t.height / 2)), t)
        self.d = ImageDraw.Draw(self.im)

    def move(self, box, dx, dy, bg=None):
        """Move a patch (display coords) by (dx, dy) display px, filling the hole with bg."""
        x0, y0, x1, y1 = self._b(box)
        patch = self.im.crop((x0, y0, x1, y1))
        b = bg or self.bg_of((x0 - 2, y0 - 2, x1 + 2, y1 + 2))
        self.d.rectangle([x0, y0, x1, y1], fill=b)
        self.im.paste(patch, (x0 + int(dx * self.S), y0 + int(dy * self.S)))
        self.d = ImageDraw.Draw(self.im)

    def restore(self, box, pred):
        """Put back original pixels in box (display coords) for which pred(r,g,b arrays) is True."""
        x0, y0, x1, y1 = self._b(box)
        o = np.asarray(self.orig)[y0:y1, x0:x1].astype(int)
        a = np.asarray(self.im).copy()
        m = pred(o[..., 0], o[..., 1], o[..., 2])
        a[y0:y1, x0:x1][m] = o[m]
        self.im = Image.fromarray(a); self.d = ImageDraw.Draw(self.im)

    def flush(self):
        q, self.queue, self.defer = self.queue, [], False
        for x, y, s, size, color, bold, anchor, cond, spacing in q:
            self.text(x, y, s, size, color, bold, anchor, scaled=False, cond=cond, spacing=spacing)
        self.defer = True

    def line(self, pts, color, w):
        self.d.line([(x * self.S, y * self.S) for x, y in pts], fill=color, width=int(round(w * self.S)))

    def save(self, out):
        self.flush()
        self.im.save(out, optimize=True)
        print('ok', out, self.im.size)


def _wrap(draw, s, f, maxw):
    out, cur = [], ''
    for w in s.split(' '):
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=f) <= maxw or not cur:
            cur = t
        else:
            out.append(cur); cur = w
    out.append(cur)
    return out


def wrap(fig, x, y, s, size, color, maxw, lh, bold=False, anchor='ls'):
    """Draw s wrapped to maxw (display px) starting with first baseline at y; returns number of lines."""
    f = font(size * fig.S, bold)
    lines = _wrap(fig.d, s, f, maxw * fig.S)
    for i, l in enumerate(lines):
        fig.text(x, y + i * lh, l, size, color, bold, anchor)
    return len(lines)


def extend(fig, top=0, bottom=0, bg=None):
    """Add blank rows (display px) above/below."""
    W, H = fig.im.size
    b = bg or fig.im.getpixel((2, H - 2))
    n = Image.new('RGB', (W, H + int((top + bottom) * fig.S)), b)
    n.paste(fig.im, (0, int(top * fig.S)))
    fig.im = n; fig.d = ImageDraw.Draw(n)
