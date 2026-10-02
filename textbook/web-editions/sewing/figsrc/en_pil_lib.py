# Small PIL helpers for replacing Chinese callouts on illustrations (chapters 16-17 English figures).
from PIL import Image, ImageDraw, ImageFont
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

class Pic:
    def __init__(s, src):
        s.im = Image.open(src).convert('RGB'); s.d = ImageDraw.Draw(s.im)
    def cover(s, box, color):
        s.d.rectangle(box, fill=color)
    def text(s, xy, t, size, color, bold=False, anchor='la', spacing=None):
        f = ImageFont.truetype(FB if bold else F, size)
        if '\n' in t:
            s.d.multiline_text(xy, t, font=f, fill=color, anchor=anchor, spacing=spacing if spacing is not None else int(size * 0.45),
                               align={'m': 'center', 'r': 'right'}.get(anchor[0], 'left'))
        else:
            s.d.text(xy, t, font=f, fill=color, anchor=anchor)
    def width(s, t, size, bold=False):
        return ImageFont.truetype(FB if bold else F, size).getlength(t)
    def save(s, out):
        s.im.save(out); print('saved', out)
