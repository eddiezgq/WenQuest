# Shared helper for English relabelling of illustrations (ch01-03 figures).
# Labels are specified in "display" coordinates (image scaled to 2000 px wide)
# and converted to original pixels with the scale factor.
from PIL import Image, ImageDraw, ImageFont
import numpy as np

SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
BG = (251, 250, 247)


class Fixer:
    def __init__(self, src, disp_w=2000):
        self.im = Image.open(src).convert('RGB')
        self.s = self.im.width / disp_w
        self.d = ImageDraw.Draw(self.im)

    def S(self, *v):
        return [int(round(x * self.s)) for x in v]

    def erase(self, x0, y0, x1, y1, mode='flat', color=None):
        """Cover a display-coordinate box. mode 'flat' = uniform colour
        (sampled median of the border unless given); 'hinterp' = per-row
        interpolation between left/right borders (for gradients)."""
        X0, Y0, X1, Y1 = self.S(x0, y0, x1, y1)
        a = np.asarray(self.im).astype(float)
        if mode == 'flat':
            if color is None:
                border = np.concatenate([a[Y0, X0:X1], a[Y1, X0:X1], a[Y0:Y1, X0], a[Y0:Y1, X1]])
                color = tuple(int(v) for v in np.median(border, axis=0))
            self.d.rectangle([X0, Y0, X1, Y1], fill=color)
        elif mode == 'hinterp':
            L = np.median(a[Y0:Y1 + 1, max(X0 - 6, 0):X0], axis=1)
            R = np.median(a[Y0:Y1 + 1, X1 + 1:X1 + 7], axis=1)
            # smooth columns along y with median over rows to kill lines
            t = np.linspace(0, 1, X1 - X0 + 1)[None, :, None]
            patch = L[:, None, :] * (1 - t) + R[:, None, :] * t
            a[Y0:Y1 + 1, X0:X1 + 1] = patch
            self.im = Image.fromarray(a.clip(0, 255).astype('uint8'))
            self.d = ImageDraw.Draw(self.im)
        elif mode == 'vinterp':
            T = np.median(a[max(Y0 - 6, 0):Y0, X0:X1 + 1], axis=0)
            B = np.median(a[Y1 + 1:Y1 + 7, X0:X1 + 1], axis=0)
            t = np.linspace(0, 1, Y1 - Y0 + 1)[:, None, None]
            a[Y0:Y1 + 1, X0:X1 + 1] = T[None] * (1 - t) + B[None] * t
            self.im = Image.fromarray(a.clip(0, 255).astype('uint8'))
            self.d = ImageDraw.Draw(self.im)

    def text(self, x, y, s, size, bold=False, color=(31, 41, 55), anchor='lm', spacing=0.25):
        """x,y display coords; size in display px (converted)."""
        f = ImageFont.truetype(BOLD if bold else SANS, int(round(size * self.s)))
        X, Y = self.S(x, y)
        if '\n' in s:
            al = {'l': 'left', 'm': 'center', 'r': 'right'}[anchor[0]]
            self.d.multiline_text((X, Y), s, font=f, fill=color, anchor=anchor[0] + 'a' if anchor[1] != 'm' else anchor[0] + 'a',
                                  align=al, spacing=int(size * self.s * spacing))
        else:
            self.d.text((X, Y), s, font=f, fill=color, anchor=anchor)

    def line(self, pts, color=(31, 41, 55), w=1.3):
        P = [tuple(self.S(*p)) for p in pts]
        self.d.line(P, fill=color, width=max(1, int(round(w * self.s))))

    def dot(self, x, y, r=3.5, color=(31, 41, 55)):
        X, Y = self.S(x, y)
        R = r * self.s
        self.d.ellipse([X - R, Y - R, X + R, Y + R], fill=color)

    def save(self, out):
        self.im.save(out)
        print('saved', out, self.im.size)


def sample(path, pts, disp_w=2000):
    im = Image.open(path).convert('RGB'); s = im.width / disp_w
    return [im.getpixel((int(x * s), int(y * s))) for x, y in pts]
