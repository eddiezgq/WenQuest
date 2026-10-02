# -*- coding: utf-8 -*-
"""Chapter 8 figures, English. Data from the ch8 lab (src/zh/labs/timing.html) via extract.js -> lab.json.
Run: python3 figsrc/en78/f8.py [names...]"""
import sys, math, json
sys.path.insert(0, '/home/claude/sm/figsrc/en78')
from lib import *
import numpy as np

LAB = json.load(open('/home/claude/sm/figsrc/en78/lab.json'))
DEG = math.pi / 180
RN, LN = 15.5, 55
LAM = RN / LN


def xN(f):
    a = f * DEG
    return RN * (1 - math.cos(a)) - LN * (1 - math.sqrt(1 - (LAM * math.sin(a)) ** 2))


A6, H6, FE = 1.1, 0.8, 114.179
HALF = math.acos((A6 - H6) / A6) / DEG
PHL0 = FE - HALF
EFF = (1 - math.cos(2 * HALF * DEG)) / 2
S6 = 3 / EFF


def feedX(p):
    return (S6 / 2) * math.cos((p - FE) * DEG)


def feedY(p):
    return (H6 - A6) + A6 * math.cos((p - PHL0) * DEG)


# ---------------------------------------------------------------- 8-5 balance
def fig_balance():
    b = [head('Balance ratio and maximum shaking force (illustrative masses)',
              'Left: maximum resultant force against balance ratio k at three speeds; right: harmonic orders of the vertical and '
              'horizontal components at 5000 r/min, k = 0.45')]
    X0, X1, Yb, Yt = 176, 1129, 683, 153
    X = lambda k: X0 + k * (X1 - X0)
    Y = lambda v: Yb - v / 1000 * (Yb - Yt)
    b.append(R(165, 142, 975, 551, '#fff', GRID, 1.5, 8))
    for k in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        b.append(L(X(k), Yt, X(k), Yb))
        b.append(T(X(k), 709, f'{k:.1f}', 14, MU, 400, 'middle'))
    for v in (0, 250, 500, 750, 1000):
        b.append(L(X0, Y(v), X1, Y(v)))
        b.append(T(X0 - 12, Y(v) + 5, str(v), 14, MU, 400, 'end'))
    for n, col, ly in (('6000', RED, 207), ('5000', BLUE, 349), ('4000', '#239a4e', 465)):
        F = LAB['F'][n]
        b.append(P([(X(int(k) / 100), Y(v)) for k, v in sorted(F.items(), key=lambda kv: int(kv[0]))], col, 3))
        vm = F['45']
        b.append(C(X(0.45), Y(vm), 6.5, '#fff', col, 2.5))
        b.append(T(X(0.45), Y(vm) + 30, f'{vm:.0f} N', 16, col, 700, 'middle'))
        b.append(T(1122, ly, f'{n} r/min', 17, col, 700, 'end'))
    b.append(T(108, 423, 'Maximum resultant (N)', 17, MU, 400, 'middle', rot=-90))
    b.append(T(653, 739, 'Balance ratio k', 17, MU, 400, 'middle'))
    # harmonics
    f = np.array(LAB['fr']['0.45'])
    Hv = [abs(x) for x in (np.fft.rfft(f[:, 1]) / 360 * 2)[1:5]]
    Hh = [abs(x) for x in (np.fft.rfft(f[:, 0]) / 360 * 2)[1:5]]
    BX0, BX1 = 1270, 1929
    BY = lambda v: Yb - v / 400 * (Yb - Yt)
    b.append(R(1260, 142, 680, 551, '#fff', GRID, 1.5, 8))
    for v in (0, 100, 200, 300, 400):
        b.append(L(BX0, BY(v), BX1, BY(v)))
        b.append(T(1262, BY(v) + 5, str(v), 14, MU, 400, 'end'))
    names = ['1st order', '2nd order', '3rd order', '4th order']
    for i in range(4):
        cx = 1352 + i * 165
        for v, col, tc, dx in ((Hv[i], '#cd5c50', RED, -21), (Hh[i], '#5b8ee0', BLUE, 21)):
            b.append(R(cx + dx - 16.5, BY(v), 33, BY(0) - BY(v), col, 'none', 0))
            b.append(T(cx + dx, BY(v) - 8, f'{v:.0f}', 14, tc, 400, 'middle'))
        b.append(T(cx, 709, names[i], 15, MU, 400, 'middle'))
    b.append(R(1283, 162, 13, 13, '#c0392b', 'none', 0) + T(1301, 175, 'Vertical', 16, RED, 700))
    b.append(R(1385, 162, 13, 13, '#2f6fd6', 'none', 0) + T(1403, 175, 'Horizontal', 16, BLUE, 700))
    b.append(T(1928, 175, 'N', 15, MU, 400, 'end'))
    b.append(T(177, 800, ['Inertia forces scale with the square of speed: at the same balance ratio, the maximum force at 6000 r/min is 1.44 times '
                          'that at 5000 r/min. The minimum lies at k ≈ 0.45.',
                          'With only the needle bar and crank the best k is about 0.6; adding the take-up lever lowers it, because the first-order '
                          'take-up inertia force is mainly horizontal and',
                          'a larger counterweight would only shift more force into the horizontal direction.'], 15.5, INK, lh=26))
    build('fig_8_balance', 880, '\n'.join(b))


# ---------------------------------------------------------------- 8-4 forces
def fig_forces():
    b = [head('Inertia forces of the whole machine (5000 r/min, balance ratio k = 0.45, illustrative masses)',
              'Left: vertical and horizontal (fore–aft) resultant components against shaft angle; right: locus traced by the tip '
              'of the resultant force vector, k = 0, 0.45 and 1 compared')]
    X0, X1, Y0c = 176, 1176, 459
    s = 252 / 600
    X = lambda t: X0 + t / 360 * (X1 - X0)
    Y = lambda v: Y0c - v * s
    b.append(R(165, 153, 1023, 612, '#fff', GRID, 1.5, 8))
    for t in range(0, 361, 60):
        b.append(L(X(t), 165, X(t), 755))
        b.append(T(X(t), 779, f'{t}°', 14, MU, 400, 'middle'))
    for v in (-600, -300, 0, 300, 600):
        b.append(L(X0, Y(v), X1, Y(v)))
        b.append(T(X0 - 12, Y(v) + 5, str(v), 14, MU, 400, 'end'))
    f = LAB['fr']['0.45'] + [LAB['fr']['0.45'][0]]
    b.append(P([(X(i), Y(v[0])) for i, v in enumerate(f)], BLUE, 3))
    b.append(P([(X(i), Y(v[1])) for i, v in enumerate(f)], RED, 3))
    b.append(T(205, 223, 'Vertical component', 17, RED, 700))
    b.append(T(205, 694, 'Horizontal (fore–aft) component', 17, BLUE, 700))
    b.append(T(108, 465, 'Force (N)', 17, MU, 400, 'middle', rot=-90))
    b.append(T(676, 809, 'Main-shaft angle', 17, MU, 400, 'middle'))
    b.append(T(177, 837, ['Illustrative masses: needle bar reciprocating 120 g (Chapter 3), crank rotating parts 60 g, take-up lever 25 g '
                          '(centre of mass 45% of the way from crank pin to eye), feed-dog carrier 50 g.',
                          'Counterweight = “rotating mass + k × reciprocating mass”, opposite the needle-bar crank; k = 0 balances only the '
                          'rotating parts, k = 1 turns the whole first-order reciprocating force horizontal.'], 15, INK, lh=26))
    # polar
    b.append(R(1258, 142, 695, 658, '#fff', GRID, 1.5, 10))
    cx, cy, sc = 1564, 470, 133 / 300
    b.append(L(1282, cy, 1929, cy, '#c8ced4', 1.3) + L(cx, 165, cx, 776, '#c8ced4', 1.3))
    b.append(C(cx, cy, 300 * sc, 'none', '#5a6570', 1.3, 'stroke-dasharray="5 4"'))
    b.append(T(1703, 465, '300 N', 14, MU))
    b.append(T(1572, 183, 'Vertical', 15, MU))
    b.append(T(1928, 461, 'Horizontal', 15, MU, 400, 'end'))
    for k, col in (('0', RED), ('0.45', '#239a4e'), ('1', BLUE)):
        fr = LAB['fr'][k]
        b.append(P([(cx + v[0] * sc, cy - v[1] * sc) for v in fr], col, 3, close=True))
    for i, (k, col, mx) in enumerate((('0', RED, '582'), ('0.45', '#239a4e', '368'), ('1.0', BLUE, '609'))):
        b.append(T(1283, 176 + 28 * i, f'k = {k}: max {mx} N', 17, col, 700))
    build('fig_8_forces', 965, '\n'.join(b))


# ---------------------------------------------------------------- 8-3 windows
def fig_windows():
    b = [head('Phase windows of three mechanisms (one moved at a time, the others kept at standard)',
              'Horizontal axis: shift from standard (main-shaft angle, + = retarded); green: usable range; the criterion that limits '
              'each end is noted')]
    X = lambda d: 352 + (d + 50) / 70 * (1929 - 352)
    for d in range(-50, 21, 10):
        b.append(L(X(d), 153, X(d), 660))
        b.append(T(X(d), 690, ('+' if d > 0 else '') + f'{d}°' if d else '0', 14, MU, 400, 'middle'))
    rows = [(235, 'Hook timing', -2.8, 3.2), (400, 'Take-up phase', -3, 6), (564, 'Feed timing', -47, 1)]
    for y, name, lo, hi in rows:
        b.append(R(352, y - 18.5, 1929 - 352, 37, '#f6ebe7', 'none', 0))
        b.append(R(X(lo), y - 18.5, X(hi) - X(lo), 37, '#6ab585', 'none', 0, 6))
        b.append(T(330, y + 7, name, 20, INK, 700, 'end'))
        b.append(T(X(lo) - 9, y + 52, f'{lo:g}°', 16, '#239a4e', 700, 'middle'))
        b.append(T(X(hi) + 9, y + 52, f'+{hi:g}°', 16, '#239a4e', 700, 'middle'))
    b.append(L(X(0), 140, X(0), 660, INK, 1.8))
    b.append(T(1398, 205, 'Rise < 1.6 mm', 15, RED, 400, 'end'))
    b.append(T(1567, 205, 'Rise > 2.5 mm', 15, RED))
    b.append(T(1574, 226, '(take-up margin ≥ 1 mm alone: up to +6°)', 15, RED))
    b.append(T(1395, 369, 'Slack before the eye enters > check-spring stroke 10 mm', 15, RED, 400, 'end'))
    b.append(T(1631, 369, 'Shortfall after entry > 1 mm', 15, RED))
    b.append(T(197, 533, 'Dog rises < 20° after the needle leaves (illustrative)', 15, RED))
    b.append(T(1518, 533, 'Fabric moves > 0.05 mm with the needle in it', 15, RED))
    build('fig_8_windows', 753, '\n'.join(b))


# ---------------------------------------------------------------- 8-2 budget
def arc(cx, cy, r0, r1, a0, a1, fill):
    """ring sector, angles in degrees clockwise from 12 o'clock"""
    if a1 < a0:
        a1 += 360
    big = 1 if a1 - a0 > 180 else 0
    pt = lambda r, a: (cx + r * math.sin(a * DEG), cy - r * math.cos(a * DEG))
    p0, p1, p2, p3 = pt(r1, a0), pt(r1, a1), pt(r0, a1), pt(r0, a0)
    return (f'<path d="M{p0[0]:.2f},{p0[1]:.2f} A{r1},{r1} 0 {big} 1 {p1[0]:.2f},{p1[1]:.2f} L{p2[0]:.2f},{p2[1]:.2f} '
            f'A{r0},{r0} 0 {big} 0 {p3[0]:.2f},{p3[1]:.2f} Z" fill="{fill}"/>')


def fig_budget():
    b = [head('The “phase budget” of one stitch',
              'One stitch’s 360° drawn as a circle; the four concentric rings are the intervals taken by the needle, hook, '
              'take-up and feed (worked-example values)')]
    cx, cy = 658, 588
    rings = [(368, 408), (314, 354), (261, 301), (208, 248)]
    for r0, r1 in rings:
        b.append(arc(cx, cy, r0, r1, 0, 359.99, '#d5dae0'))
    NEED, HOOK, REL, TAK, FEED = '#6b7680', '#e07a4a', '#cdb0dd', '#9b59b6', '#48a86e'
    b.append(arc(cx, cy, *rings[0], 101.7, 258.3, NEED))
    b.append(arc(cx, cy, *rings[1], 206, 341, HOOK))
    b.append(arc(cx, cy, *rings[2], 55, 293, REL))
    b.append(arc(cx, cy, *rings[2], 293, 55, TAK))
    b.append(arc(cx, cy, *rings[3], 325.8, 114.2, FEED))
    pt = lambda r, a: (cx + r * math.sin(a * DEG), cy - r * math.cos(a * DEG))
    for a in range(0, 360, 30):
        p, q = pt(205, a), pt(411, a)
        b.append(L(*p, *q, '#ffffff', 1.2, extra='stroke-opacity="0.75"'))
        tx, ty = pt(440, a)
        b.append(T(tx, ty + 6, f'{a}°', 15, MU, 400, 'middle'))
    for a, col in ((101.7, INK), (258.3, INK), (180, INK), (206, '#d9622b'), (341, '#d9622b'),
                   (55, PURPLE), (293, PURPLE), (114.2, '#239a4e'), (325.8, '#239a4e')):
        p, q = pt(200, a), pt(425, a)
        b.append(L(*p, *q, col, 1.5, '6 4'))
    b.append(T(cx, 580, 'One main-shaft revolution', 20, INK, 700, 'middle'))
    b.append(T(cx, 612, '= one stitch', 17, MU, 400, 'middle'))
    leg = [(NEED, 'Needle in fabric 101.7°–258.3°'), (HOOK, 'Hook point carrying the loop 206°–341°'),
           (REL, 'Take-up lever releasing thread 55°–293°'), (TAK, 'Take-up lever taking up thread 293°–55°'),
           (FEED, 'Feed dog gripping the fabric 325.8°–114.2°')]
    for i, (c, t) in enumerate(leg):
        y = 228 + 47 * i
        b.append(R(1177, y - 9, 35, 18, c, 'none', 0) + T(1226, y + 7, t, 19, INK, 700))
    b.append(T(1177, 506, ['Reading the chart:',
                           '• Needle in fabric and feed dog gripping almost meet end to end,',
                           '  overlapping only at 101.7°–114.2°, when the dog’s horizontal motion is done;',
                           '• the hook carries the loop for 135° (206°–341°), spanning the moment the',
                           '  needle leaves the fabric; only after cast-off can the take-up tighten the stitch;',
                           '• at 55°, when the take-up is tightest, the feed is still moving — this is what',
                           '  Chapter 6 means by “the stitch is tightened while the fabric moves”.', '',
                           'Whenever the phase of any mechanism changes, check on this disc',
                           'that it does not collide with another mechanism.'], 16.5, INK, lh=28.4, extra='xml:space="preserve"'))
    build('fig_8_budget', 1059, '\n'.join(b))


# ---------------------------------------------------------------- 8-1 timing
def fig_timing():
    D = 40  # extra top room for the rotated English event labels
    H = 1518 + D
    b = [head('Whole-machine timing diagram: five motions on one shaft-angle axis',
              'Worked examples of Chapters 3–7; horizontal axis: main-shaft angle, needle bar at top dead centre = 0°; '
              'vertical lines: key moments')]
    X0, X1 = 223, 1929
    X = lambda t: X0 + t / 360 * (X1 - X0)
    panels = [(212, 410), (448, 669), (706, 882), (918, 1152), (1189, 1364)]
    panels = [(a + D, c + D) for a, c in panels]
    top, bot = panels[0][0], panels[-1][1]
    for a, c in panels:
        b.append(R(212, a, 1728, c - a, '#fff', GRID, 1.5, 8))
    b.append(R(X(101.7), top, X(258.3) - X(101.7), bot - top, '#e9ebef', 'none', 0, extra='fill-opacity="0.5"'))
    for t in range(0, 361, 30):
        for a, c in panels:
            b.append(L(X(t), a + 1, X(t), c - 1))
        b.append(T(X(t), bot + 31, f'{t}°', 14, MU, 400, 'middle'))
    # 1 needle
    a, c = panels[0]
    Yn = lambda v: (233 + D) + (18 - v) * (161 / 31)
    b.append(L(X0, Yn(0), X1, Yn(0), '#5a6570', 1.3))
    b.append(L(X0, Yn(1.5), X1, Yn(1.5), '#c99a6b', 1.3, '6 4'))
    b.append(P([(X(f), Yn(18 - xN(f))) for f in np.arange(0, 360.5, 1)], INK, 2.8))
    b.append(T(978, 243 + D, 'Needle-point height (mm, throat plate = 0)', 15, MU, 400, 'middle'))
    # 2 take-up
    S, Dm = LAB['S'] + [LAB['S'][0]], LAB['D'] + [LAB['D'][0]]
    Yt = lambda v: (659 + D) - v * (181 / 81.56)
    b.append(P([(X(i), Yt(v)) for i, v in enumerate(S)], PURPLE, 2.8))
    b.append(P([(X(i), Yt(v)) for i, v in enumerate(Dm)], '#d9622b', 2.4, dash='9 6'))
    b.append(T(697, 536 + D, 'Thread supply S (released by the take-up mechanism, solid)', 15, PURPLE, 700))
    b.append(T(1715, 636 + D, 'Thread consumption D (dashed)', 15, '#d9622b', 700, 'end'))
    # 3 hook
    a, c = panels[2]
    b.append(R(X(206.1), 717 + D, X(341) - X(206.1), 153, '#e0662f', 'none', 0, extra='fill-opacity="0.12"'))
    Yh = lambda f: (870 + D) - (((2 * (f - 206.1)) % 360) / 360) * 153
    seg = []
    for f in np.arange(0, 360.01, 0.25):
        y = Yh(f)
        if seg and y > seg[-1][1] + 50:
            b.append(P(seg, ORANGE, 2.6)); seg = []
        seg.append((X(f), y))
    b.append(P(seg, ORANGE, 2.6))
    b.append(T(1410, 739 + D, 'Hook point carrying the loop (206°–341°)', 15, '#d9622b', 700))
    b.append(T(508, 859 + D, 'Hook-point angle (relative to the needle, 2:1)', 15, MU))
    # 4 feed
    Yf = lambda v: (1035 + D) - v * 52.5
    b.append(L(X0, Yf(0), X1, Yf(0), '#5a6570', 1.3))
    b.append(P([(X(f), Yf(feedX(f))) for f in np.arange(0, 360.5, 1)], DARKGREEN, 2.4, dash='8 5'))
    b.append(P([(X(f), Yf(feedY(f))) for f in np.arange(0, 360.5, 1)], AMBER, 2.8))
    b.append(T(1080, 950 + D, 'Feed-dog height Y (solid) and horizontal position X (dashed), mm', 15, DARKGREEN, 700, 'middle'))
    # 5 tension (illustrative curve, same as Fig. 7-3)
    raw = np.array(json.load(open('/home/claude/sm/figsrc/en78/dyn.json')))
    grid = np.arange(0, 360.01, 0.5)
    v = np.interp(grid, raw[:, 0], raw[:, 1])
    vp = np.concatenate([v[-5:-1], v, v[1:5]])
    vs = np.convolve(vp, np.ones(9) / 9, mode='same')[4:-4]
    Yw = lambda u: (1336 + D) - (u - 0.121) * (122 / 0.879)
    b.append(P([(X(g), Yw(u)) for g, u in zip(grid, vs)], BLUE, 2.8))
    b.append(T(792, 1242 + D, 'Needle-thread tension (illustrative, Chapter 7)', 15, BLUE, 700))
    # row labels
    for (a, c), lab in zip(panels, ['Penetration', 'Take-up', 'Loop catching', 'Feed', ['Needle-thread', 'tension']]):
        yy = (a + c) / 2 + 7 - (12 if isinstance(lab, list) else 0)
        b.append(T(195, yy, lab, 19, INK, 700, 'end', lh=25))
    # event lines + rotated labels
    ev = [(55, PURPLE, 'Take-up tightest 55°'), (101.7, INK, 'Needle point in 101.7°'), (114.2, '#239a4e', 'Dog drops 114.2°'),
          (180, INK, 'BDC 180°'), (206.1, '#d9622b', 'Loop caught 206.1°'), (258.3, INK, 'Needle point out 258.3°'),
          (293, PURPLE, 'Max. release 293°'), (325.8, '#239a4e', 'Dog rises 325.8°'), (341, '#d9622b', 'Cast-off 341°')]
    for t, col, lab in ev:
        b.append(L(X(t), 195 + D, X(t), bot, col, 1.4, '5 4'))
        b.append(T(X(t) + 3, 190 + D, lab, 14, col, 400, 'start', rot=-45))
    b.append(T(1076, bot + 66, 'Main-shaft angle', 17, MU, 400, 'middle'))
    b.append(T(48, bot + 102, 'Grey shading: needle in the fabric (fabric 1.5 mm thick). Read the chart vertically: what each of the five '
                              'mechanisms is doing at the same moment, which two motions come closest, and where the margin is smallest.',
               15.5, INK))
    build('fig_8_timing', H, '\n'.join(b))


# ---------------------------------------------------------------- 8-6 oil
def fig_oil():
    b = [head('Lubrication system (schematic)',
              'Schematic; arrows show the oil path. Oil is stored in the pan under the bed; a pump driven by the hook shaft delivers it '
              'to the hook and the bearings, and surplus oil drains back to the pan')]
    defs = '<marker id="ab" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#5a6570"/></marker>'
    b.append('<path d="M165,588 L353,588 L353,240 Q353,188 405,188 L1476,188 Q1528,188 1528,240 L1528,352 L1435,352 L1435,588 '
             'L1788,588 L1788,658 L165,658 Z" fill="#f1f3f6" stroke="#5a6570" stroke-width="2" stroke-linejoin="round"/>')
    b.append(R(141, 682, 1670, 93, '#e3ebf6', '#2a5fb8', 2, 8))
    wv = [(x, 740 + 3 * math.sin((x - 165) / 1623 * 2 * math.pi * 1.5)) for x in range(165, 1789, 8)]
    b.append(P(wv, '#5b8ee0', 2))
    b.append(T(972, 764, 'Oil pan (oil level between the HIGH and LOW marks)', 17, '#1f4fa8', 700, 'middle'))
    b.append(L(400, 258, 1486, 258, '#5a6570', 10, extra='stroke-linecap="round"'))
    b.append(L(1459, 262, 1459, 618, '#5a6570', 6))
    b.append(L(210, 623, 1743, 623, '#5a6570', 10, extra='stroke-linecap="round"'))
    b.append(T(940, 240, 'Arm shaft', 17, INK, 700, 'middle'))
    b.append(T(940, 611, 'Hook shaft', 17, INK, 700, 'middle'))
    b.append(T(1473, 447, 'Timing belt / vertical shaft', 15, MU))
    # oil paths
    BL = '#2f6fd6'
    b.append(P([(1185, 634), (1411, 634), (1411, 282), (1318, 271)], BL, 3, dash='9 6'))
    b.append('<path d="M1290,269 L1314,262 L1312,284 Z" fill="#5a6570"/>')
    b.append(P([(1120, 634), (340, 634), (330, 630)], BL, 3, dash='9 6'))
    b.append('<path d="M314,620 L338,624 L326,642 Z" fill="#5a6570"/>')
    b.append(P([(388, 305), (388, 655)], BL, 3, dash='9 6'))
    b.append('<path d="M376,652 L400,652 L388,675 Z" fill="#5a6570"/>')
    b.append('<path d="M1144,708 L1160,708 L1152,694 Z" fill="#5a6570"/>')
    b.append(C(270, 612, 53, '#fde3d4', ORANGE, 2.5))
    b.append(T(270, 618, 'Hook', 17, '#c4531d', 700, 'middle'))
    b.append(C(1152, 659, 33, '#fff', '#2a5fb8', 2.5))
    b.append(T(1152, 665, 'Pump', 15, '#1f4fa8', 700, 'middle'))
    b.append(T(400, 494, 'Return oil', 15, MU))
    b.append(T(730, 574, 'To the hook along the hook shaft; a screw at the shaft bushing sets the amount', 15, '#1f4fa8', 700, 'middle'))
    b.append(T(1402, 553, ['To arm-shaft bearings,', 'needle bar and take-up'], 15, '#1f4fa8', 400, 'end', lh=21))
    b.append(R(152, 447, 72, 47, '#fff8dc', '#c48a17', 1.8))
    b.append(T(188, 435, 'Oil-check paper', 15, AMBER, 700, 'middle'))
    b.append(T(1565, 270, ['Semi-dry / minimal lubrication:', 'parts on the arm-shaft side get little or',
                           'no oil; oil goes only to a few points such', 'as the hook, so less oil reaches the fabric',
                           '(Chapter 23).'], 16, INK, lh=26))
    b.append(T(48, 822, ['Checking the hook oil: right after the machine stops, hold the oil-check paper under the hook and, following the manual, '
                         'read the width of the oil trace thrown onto it;',
                         'the suitable range given in the manual depends on the model: about 0.5–1 mm for light-material models, '
                         'about 1–3 mm for medium- and heavy-material models.'], 15.5, INK, lh=26))
    build('fig_8_oil', 894, '\n'.join(b), defs)


if __name__ == '__main__':
    names = sys.argv[1:] or ['balance', 'forces', 'windows', 'budget', 'timing', 'oil']
    for n in names:
        globals()['fig_' + n]()
