"""English relabel of fig_14_trim (schematic drawing): cover each Chinese label with the local background
colour and draw the English text (DejaVu Sans). Coordinates in 2000-px display units (image is 3400 px wide)."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = '/home/claude/book/img/fig_14_trim.png'
im = Image.open(src).convert('RGB')
S = im.width / 2000
EXTRA = int(34 * S)   # extra room at the bottom for the two-line note
canvas = Image.new('RGB', (im.width, im.height + EXTRA), (251, 250, 247))
canvas.paste(im, (0, 0))
im = canvas
A = np.array(im).astype(int)
dr = ImageDraw.Draw(im)
FD = '/usr/share/fonts/truetype/dejavu/'
def F(px, bold=False): return ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), int(round(px * S)))
INK, MUT, BLUE, RED, GOLD = (27, 36, 48), (90, 101, 112), (47, 111, 214), (192, 57, 43), (183, 121, 31)

def cover(r, pad=3, bg=None):
    """find the text bbox inside display rect r and paint it with the background colour"""
    x0, y0, x1, y1 = [int(v * S) for v in r]
    sub = A[y0:y1, x0:x1]
    bg = np.array(im.getpixel((x0, y0)) if bg is None else bg)
    d = np.abs(sub - bg).sum(2) > 40
    ys, xs = np.where(d)
    if len(xs) == 0: return None
    bx0, by0, bx1, by1 = x0 + xs.min() - pad, y0 + ys.min() - pad, x0 + xs.max() + pad, y0 + ys.max() + pad
    dr.rectangle([bx0, by0, bx1, by1], fill=tuple(bg))
    return bx0 / S, by0 / S, bx1 / S, by1 / S

def text(x, y, s, px, col, bold=False, anchor='la'):
    dr.text((x * S, y * S), s, font=F(px, bold), fill=col, anchor=anchor)

# --- erase all Chinese labels ---
R = dict(title=(40, 25, 1000, 75), sub=(40, 78, 1300, 108),
         ha=(55, 155, 500, 208), hb=(538, 155, 985, 208), hc=(1020, 155, 1465, 208), hd=(1502, 155, 1945, 185),
         dblue=(1370, 215, 1682, 242),
         fk1=(430, 326, 476, 350), fk2=(913, 326, 959, 350), fk3=(1395, 326, 1441, 350), fk4=(1877, 326, 1923, 350),
         mk=(560, 384, 606, 410),
         ca=(220, 735, 335, 762), cb=(630, 745, 885, 772), cc=(1100, 745, 1380, 772), cd=(1605, 733, 1840, 788),
         note=(40, 838, 1700, 870))
for k, r in R.items():
    print(k, cover(r))
print('cp', cover((1874, 386, 1928, 401), pad=1, bg=(255, 255, 255)))
# the blue label in panel d originally ran across the gap between cards c and d: restore the two card borders
strip = im.crop((int(1462 * S), int(250 * S), int(1502 * S), int(288 * S)))
im.paste(strip, (int(1462 * S), int(209 * S)))

# --- English labels ---
text(47, 33, 'Thread trimmer under the throat plate: the knife enters the loop, separates the threads, cuts on its return', 25, INK, True)
text(47, 78, 'One design, schematic (top view below the throat plate, not to scale). Blue: needle thread; orange: bobbin thread; grey circles: rotary hook and bobbin case;', 14.5, MUT)
text(47, 99, 'the moving knife is driven by a solenoid through a link (some designs drive it from a trimming cam)', 14.5, MUT)
hdr = [(64, ['a   Hook point catches the loop and carries', '     it round the bobbin case (206°–293°)']),
       (546, ['b   Needle rising; the knife enters the', '     enlarged loop (about 300°–330°)']),
       (1028, ['c   Loop sheds, take-up lever draws thread; knife', '     returns with the fabric-side threads']),
       (1510, ['d   Cut with the fixed knife at take-up top (55°)'])]
for x, lines in hdr:
    for i, l in enumerate(lines):
        text(x, 161 + i * 23, l, 14, INK, True)
text(1512, 205, 'Supply-side needle thread is not cut; it stays', 12.5, BLUE, True)
text(1512, 222, 'in the needle eye (for the next seam start)', 12.5, BLUE, True)
for cx in (453, 936, 1418, 1900):
    text(cx, 338, 'Fixed knife', 12.5, INK, True, 'mm')
text(583, 396, 'Moving knife', 13, RED, True, 'mm')
text(1900, 394, 'Cut point', 12.5, GOLD, True, 'mm')
text(277, 748, 'The loop grows larger and larger', 13.5, MUT, anchor='mm')
text(759, 750, 'The knife point passes under the', 13.5, MUT, anchor='mm')
text(759, 769, 'supply-side thread of the loop', 13.5, MUT, anchor='mm')
text(1241, 750, 'The supply-side needle thread slides', 13.5, MUT, anchor='mm')
text(1241, 769, 'over the back of the knife: not cut', 13.5, MUT, anchor='mm')
text(1723, 748, 'Only a very short end is left under the fabric;', 13.5, MUT, anchor='mm')
text(1723, 768, 'after trimming the wiper flicks the thread end', 13.5, MUT, anchor='mm')
text(1723, 787, 'off the needle', 13.5, MUT, anchor='mm')
note = ['Summarised from a lockstitch thread-trimmer patent: when the needle has risen about 10 mm above the throat plate the solenoid is energised; the moving knife turns into the',
        'catching position, its point passing under the supply-side needle thread; after the loop has gone round the bobbin case and been drawn up by the take-up lever, the knife returns,',
        'and the needle and bobbin threads leading to the fabric are cut when the take-up lever reaches its top dead centre.']
for i, l in enumerate(note):
    text(47, 838 + i * 21, l, 13.5, INK)
out = os.path.join(ROOT, 'img', 'en', 'fig_14_trim.png')
im.save(out); print('ok', out, im.size)
