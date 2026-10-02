# Generates the English HTML/SVG sources for Fig. 15-2 (w_e7c09f47) and Fig. 15-8 (w_7eeeef88).
# Coordinates follow the original 1344-px-wide images; rendered at 1008 css px (2016 px with fig.js).
# Render: node fig.js figsrc/en_w_e7c09f47.en.html img/en/w_e7c09f47.png  (same for w_7eeeef88)
import html, subprocess
INK = '#0b0b0b'; MUTED = '#52514e'; LINE = '#c3c2b7'
BLUE = '#2a78d6'; ORANGE = '#eb6834'; GREEN = '#1baf7a'
FBLUE = '#ebf2fc'; FORANGE = '#fdeee7'; FGREEN = '#e8f5ef'


class S:
    def __init__(self, w, h):
        self.w, self.h, self.o = w, h, []

    def t(self, x, y, s, size=15.5, color=INK, w=400, anchor='start'):
        self.o.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{w}" '
                      f'text-anchor="{anchor}" dominant-baseline="middle">{html.escape(s)}</text>')

    def box(self, x0, y0, x1, y1, stroke=LINE, fill='#ffffff', sw=2.2, r=12, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.o.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="{r}" fill="{fill}" '
                      f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def path(self, pts, dash=False, arrow=True, color=LINE, sw=2):
        d = 'M' + ' L'.join(f'{x} {y}' for x, y in pts)
        da = ' stroke-dasharray="7 5"' if dash else ''
        m = ' marker-end="url(#ah)"' if arrow else ''
        self.o.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{da}{m}/>')

    def html(self, title):
        return (f'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">'
                f'<title>{html.escape(title)}</title>'
                '<style>@font-face{font-family:LFix;src:local("DejaVu Sans");unicode-range:U+00B7,U+00D7,U+2018-201D,U+2026,U+2192}svg text{font-family:LFix,"Noto Sans CJK SC",sans-serif}</style>'
                f'<div class="fig" style="--w:1008px;padding:0">'
                f'<svg viewBox="0 0 {self.w} {self.h}" width="1008" height="{self.h*1008/self.w:.1f}" style="display:block">'
                f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M0 0 L10 5 L0 10 z" fill="{LINE}"/></marker></defs>'
                + ''.join(self.o) + '</svg></div>')


def fig_e7c09f47():
    s = S(1344, 844)
    s.t(42, 42, 'One controller, three servo axes, a set of on/off outputs: the main-shaft angle is the machine’s “master”', 20.5, INK, 700)
    s.t(42, 78, 'Solid lines: commands; dashed lines: feedback. X and Y take their commanded step only inside the angle window where the needle is out of the fabric', 14.5, MUTED)
    # encoder feedback loop
    s.path([(1135, 160), (1135, 132), (507, 132), (507, 157)], dash=True)
    s.t(830, 117, 'Encoder: main-shaft angle φ and speed', 15.5, MUTED, anchor='middle')
    # inputs
    s.box(46, 226, 280, 303); s.t(163, 252, 'Operator panel', 18.5, INK, 400, 'middle'); s.t(163, 281, 'Select pattern · set speed', 15, MUTED, anchor='middle')
    s.box(46, 378, 280, 456); s.t(163, 404, 'Pattern file', 18.5, INK, 400, 'middle'); s.t(163, 434, 'USB · network · template barcode', 13.5, MUTED, anchor='middle')
    s.path([(280, 265), (352, 265)]); s.path([(280, 416), (352, 416)])
    # main controller
    s.box(354, 158, 601, 622, BLUE, FBLUE, 2.6)
    cx = 477
    s.t(cx, 194, 'Main controller', 18.5, INK, 700, 'middle')
    s.t(cx, 244, 'Application processor', 16.5, INK, 400, 'middle')
    for i, l in enumerate(['Pattern parsing · look-ahead', 'Sewing-cycle logic · UI', 'Computed once per stitch']):
        s.t(cx, 281 + 28 * i, l, 15, MUTED, anchor='middle')
    s.o.append(f'<line x1="376" y1="375" x2="580" y2="375" stroke="#9fb8de" stroke-width="1.5" stroke-dasharray="6 4"/>')
    s.t(cx, 416, 'Motion-control core', 16.5, INK, 400, 'middle')
    for i, l in enumerate(['Electronic cam · S-curves', 'Fires valves, solenoids by φ', 'Computed every 0.1–1 ms']):
        s.t(cx, 453 + 28 * i, l, 15, MUTED, anchor='middle')
    s.t(cx, 570, 'DSP or FPGA', 14.5, MUTED, anchor='middle')
    # drives
    for y0, y1, name in [(166, 243, 'Main-shaft servo drive'), (290, 367, 'X-axis drive'), (413, 491, 'Y-axis drive'), (545, 622, 'I/O driver board')]:
        s.box(683, y0, 916, y1); s.t(800, (y0 + y1) / 2, name, 17.5, INK, 400, 'middle')
        ym = (y0 + y1) // 2
        s.path([(601, ym), (681, ym)])
    # actuators
    s.box(1018, 160, 1252, 249, BLUE, FBLUE, 2.6); s.t(1135, 193, 'Main-shaft motor', 18.5, INK, 700, 'middle'); s.t(1135, 223, 'Direct-drives arm shaft · encoder', 14, MUTED, anchor='middle')
    s.box(1018, 285, 1252, 373, ORANGE, FORANGE, 2.6); s.t(1135, 318, 'X servo motor', 18.5, INK, 700, 'middle'); s.t(1135, 347, 'Timing belt → carriage', 15, MUTED, anchor='middle')
    s.box(1018, 408, 1252, 496, ORANGE, FORANGE, 2.6); s.t(1135, 441, 'Y servo motor', 18.5, INK, 700, 'middle'); s.t(1135, 470, 'Timing belt → beam', 15, MUTED, anchor='middle')
    s.box(1018, 540, 1252, 676); s.t(1135, 566, 'On/off actuators', 18.5, INK, 700, 'middle')
    s.t(1135, 598, 'Clamp · intermediate-foot valves', 14, MUTED, anchor='middle')
    s.t(1135, 624, 'Trimming · wiping ·', 14, MUTED, anchor='middle'); s.t(1135, 648, 'tension-release solenoids', 14, MUTED, anchor='middle')
    for ym in (204, 328, 452, 583):
        s.path([(916, ym), (1016, ym)])
    # sensors
    s.box(655, 690, 1301, 756); s.t(978, 707, 'Sensors', 18.5, INK, 400, 'middle')
    s.t(978, 735, 'X/Y home · clamp in position · thread-break detection · safety light curtain · air pressure', 14.5, MUTED, anchor='middle')
    s.path([(655, 714), (530, 714), (530, 624)], dash=True)
    s.t(42, 800, 'X and Y can also use closed-loop steppers; small bartackers and button sewers often use steppers, large-area template machines mostly servos', 14.5, MUTED)
    return s


def fig_7eeeef88():
    s = S(1344, 932)
    s.t(42, 42, 'Five boards in the control box: high- and low-voltage zones, differential and opto-isolated signals', 20.5, INK, 700)
    s.t(42, 78, 'One typical partitioning; manufacturers merge or split boards differently. Solid lines: power; dashed lines: signals', 14.5, MUTED)
    s.box(42, 113, 961, 873, '#c9c9c6', 'none', 1.6, 18, '7 5')
    s.t(64, 142, 'Control box', 16, MUTED)
    s.t(64, 191, 'High-voltage zone', 15.5, ORANGE, 700)
    s.t(64, 417, 'Low-voltage zone', 15.5, BLUE, 700)
    # high-voltage boards
    for x0, x1, name, l1, l2 in [(63, 329, 'Power board', 'EMI filter · rectifier DC 310 V', 'Switch-mode supply 24 V / 5 V'),
                                 (363, 630, 'Main-shaft servo drive', 'IGBT/MOSFET inverter', 'Braking resistor'),
                                 (665, 931, 'X/Y dual-axis drive', 'Position and current loops', 'Bus link to the main board')]:
        s.box(x0, 212, x1, 336, ORANGE, FORANGE, 2.6)
        xc = (x0 + x1) / 2
        s.t(xc, 250, name, 18, INK, 700, 'middle'); s.t(xc, 283, l1, 15, MUTED, anchor='middle'); s.t(xc, 311, l2, 15, MUTED, anchor='middle')
    s.path([(329, 273), (361, 273)]); s.path([(630, 273), (663, 273)])
    s.path([(250, 336), (250, 439)])
    # low-voltage boards
    s.box(63, 442, 506, 654, BLUE, FBLUE, 2.6)
    s.t(285, 480, 'Main control board', 18, INK, 700, 'middle')
    for i, l in enumerate(['ARM processor: patterns, look-ahead, UI', 'FPGA: encoder decoding, electronic cam', 'DDR · Flash · USB · Ethernet · RS-485']):
        s.t(285, 516 + 32 * i, l, 15, MUTED, anchor='middle')
    s.t(285, 619, 'Watchdog · power-fail data retention', 15, MUTED, anchor='middle')
    s.box(541, 442, 931, 654, GREEN, FGREEN, 2.6)
    s.t(736, 480, 'I/O board', 18, INK, 700, 'middle')
    for i, l in enumerate(['16 × 24 V outputs: MOSFET + freewheeling', 'Overvoltage drive for trimming solenoid', '16 inputs: opto-isolated']):
        s.t(736, 516 + 32 * i, l, 15, MUTED, anchor='middle')
    s.t(736, 619, 'Valves · wiper · tension release · sensors', 15, MUTED, anchor='middle')
    s.path([(506, 530), (539, 530)], dash=True)
    # command/feedback between main board and drives
    s.path([(389, 442), (389, 371), (497, 371), (497, 338)], dash=True)
    s.path([(442, 442), (442, 388), (797, 388), (797, 338)], dash=True)
    s.path([(1025, 431), (990, 431), (990, 421), (337, 421), (337, 440)], dash=True)
    s.t(512, 371, 'Commands · encoder feedback', 15, MUTED)
    # head and table
    s.box(1026, 159, 1308, 865, '#c9c9c6', '#ffffff', 2.2, 18)
    s.t(1167, 190, 'Head and table', 17.5, INK, 700, 'middle')
    s.t(1054, 258, 'Main-motor power cable', 16, INK); s.t(1054, 287, 'Shielded, earthed at both ends', 14.5, MUTED)
    s.t(1054, 347, 'X/Y motor power cables', 16, INK)
    s.t(1054, 417, 'Encoder cables', 16, INK); s.t(1054, 446, 'RS-422 differential, twisted', 14.5, MUTED); s.t(1054, 470, 'pair, shielded', 14.5, MUTED)
    s.t(1054, 524, 'Valves and solenoids', 16, INK)
    s.t(1054, 594, 'Home · clamp · thread break', 16, INK); s.t(1054, 623, 'Sensor signals', 14.5, MUTED)
    s.t(1054, 736, 'Operator panel', 16, INK)
    s.path([(630, 225), (918, 225), (918, 258), (1024, 258)])
    s.path([(931, 291), (931, 347), (1024, 347)])
    s.path([(931, 530), (1024, 530)])
    s.path([(1024, 601), (933, 601)], dash=True)
    s.path([(285, 654), (285, 742), (990, 742)], dash=True)
    s.t(637, 725, 'Touch screen (RS-485 / Ethernet)', 15, MUTED, anchor='middle')
    s.t(42, 898, 'Wiring rules: route power and signal cables separately, never in parallel; join power ground and signal ground at one point; keep electrical clearance and creepage around the 310 V circuits', 13.5, MUTED)
    return s


for name, f, title in [('w_e7c09f47', fig_e7c09f47, 'Pattern sewer control block diagram'),
                       ('w_7eeeef88', fig_7eeeef88, 'Pattern sewer control box')]:
    src = f'/home/claude/sm/figsrc/en_{name}.en.html'
    open(src, 'w').write(f().html(title))
    subprocess.run(['node', 'fig.js', src, f'img/en/{name}.png'], cwd='/home/claude/sm', check=True)
