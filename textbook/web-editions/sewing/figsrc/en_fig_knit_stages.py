# Fig. 17-2 (English): five stages of loop formation on a latch needle — Chinese text replaced on the original drawing.
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_pil_lib import *
p = Pic('/home/claude/book/img/fig_knit_stages.png')
BG, WH, MU, INK = (251, 250, 247), (255, 255, 255), (93, 107, 122), (31, 42, 54)
p.cover((60, 30, 2200, 100), BG)
p.text((80, 64), 'Five stages of loop formation on a latch needle (schematic): dashed line = knock-over line (trick edge); orange = old loop,\nblue = new yarn; d = stitch-cam depth, which sets the loop length', 28, MU, anchor='lm', spacing=8)
panels = [(81, 558), (601, 1079), (1120, 1599), (1640, 2119), (2160, 2638)]
heads = ['① Start', '② Clearing', '③ Yarn feeding', '④ Latch closing', '⑤ Knock-over']
caps = ['The old loop hangs in the hook\n(the loop formed in the\nprevious course)',
        'The raising cam pushes the\nneedle up; the old loop slides\nbelow the latch',
        'The yarn carrier passes with\nthe carriage and lays the new\nyarn into the open hook',
        'The needle descends; the old\nloop lifts the latch and shuts\nthe new yarn in the hook',
        'The stitch cam draws the needle\ndown to depth d; the old loop is\nknocked over, the new yarn\nforms the new loop']
for (a, b), h, c in zip(panels, heads, caps):
    p.cover((a + 8, 158, b - 8, 224), WH)
    p.text(((a + b) / 2, 192), h, 38, INK, bold=True, anchor='mm')
    p.cover((a + 8, 1112, b - 8, 1240), WH)
    p.text(((a + b) / 2, 1170), c, 25, MU, anchor='mm', spacing=7)
# '纱嘴' label next to the yarn carrier in panel 3: inside the glyph box keep only the blue yarn and the carrier plate
from PIL import Image, ImageDraw
orig = Image.open('/home/claude/book/img/fig_knit_stages.png').convert('RGB').load()
mask = Image.new('L', p.im.size, 0); ImageDraw.Draw(mask).polygon([(1186, 257), (1241, 257), (1304, 309), (1268, 309)], fill=255)
mk = mask.load(); px = p.im.load(); FILL = orig[1250, 275]
for x in range(1180, 1262):
    for y in range(284, 330):
        r, g, b = orig[x, y]
        yl = 240 + (x - 1137) * 0.468
        px[x, y] = (r, g, b) if (mk[x, y] or (b > r + 50 and abs(y - yl) < 12)) else WH
        if mk[x, y] and abs(y - yl) > 7 and sum(orig[x, y]) > 200 and b < r + 40:
            px[x, y] = FILL
# patch the stretch of yarn the glyphs overlapped by copying the clean, straight yarn just up-left of it
for x in range(1214, 1256):
    for y in range(280, 306):
        if not mk[x, y]:
            px[x, y] = orig[x - 30, y - 14]
p.text((1140, 336), 'Yarn carrier', 24, MU, anchor='ls')
p.save('/home/claude/sm/img/en/fig_knit_stages.png')
