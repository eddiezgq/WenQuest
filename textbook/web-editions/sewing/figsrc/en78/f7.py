# -*- coding: utf-8 -*-
"""Chapter 7 figures, English. Run: python3 figsrc/en78/f7.py [names...]"""
import sys, math
sys.path.insert(0, '/home/claude/sm/figsrc/en78')
from lib import *

FAB = '#e8d5b0'; FABS = '#b8a070'


def thread(pts, col, dark):
    return P(pts, dark, 6) + P(pts, col, 3)


# ---------------------------------------------------------------- 7-4 balance
def fig_balance():
    b = [head('Stitch balance: the tension ratio sets where the interlacing point lies',
              'Illustrative model; r = needle-thread ÷ bobbin-thread tension at the interlacing point during tightening; top row: '
              'enlarged cross-section of two plies of cotton; white dots: interlacing points')]
    B = 2.2
    cases = [(0.35, 'Needle thread floats on the underside', RED), (0.7, 'Low', RED), (1.0, 'Balanced', MU),
             (1.5, 'High', RED), (2.8, 'Bobbin thread pulled to the top', RED)]
    for i, (r, cap, cc) in enumerate(cases):
        x0 = 48 + i * 388
        b.append(R(x0, 142, 364, 305, '#fff', GRID, 1.5, 10))
        fx0, fx1, ty, by = x0 + 22, x0 + 342, 232, 309
        b.append(R(fx0, ty, fx1 - fx0, by - ty, FAB, FABS, 1.2))
        z = 0.5 + 0.5 * max(-1, min(1, math.log(r) / math.log(B)))
        zy = by - z * (by - ty)
        xs = [x0 + 75, x0 + 181, x0 + 287]
        top = [(fx0, ty)]
        bot = [(fx0, by)]
        for xp in xs:
            top += [(xp - 11, ty), (xp - 3, zy), (xp + 3, zy), (xp + 11, ty)]
            bot += [(xp - 11, by), (xp - 3, zy), (xp + 3, zy), (xp + 11, by)]
        top.append((fx1, ty)); bot.append((fx1, by))
        b.append(thread(bot, '#f07a45', '#c4531d'))
        b.append(thread(top, '#3a7be0', '#1f4fa8'))
        for xp in xs:
            b.append(C(xp, zy, 6, '#fff', INK, 1.8))
        b.append(T(x0 + 182, 357, f'r = {r}', 17, INK, 700, 'middle'))
        b.append(T(x0 + 182, 404, cap, 16, cc, 400, 'middle'))
    # chart
    X0, X1, Y0, Y1 = 258, 1294, 517, 941
    X = lambda r: X0 + (math.log2(r) + 2) / 4 * (X1 - X0)
    Y = lambda z: Y1 - z * (Y1 - Y0)
    b.append(R(248, 507, 1057, 444, '#fff', GRID, 1.5, 6))
    b.append(R(X0, Y(0.6), X1 - X0, Y(0.4) - Y(0.6), '#e3f1e8', 'none', 0))
    for r in (0.25, 0.5, 1, 2, 4):
        b.append(L(X(r), Y0, X(r), Y1))
        b.append(T(X(r), 967, f'{r:g}', 14, MU, 400, 'middle'))
    for z in (0, 0.25, 0.5, 0.75, 1):
        b.append(L(X0, Y(z), X1, Y(z)))
        b.append(T(X0 - 10, Y(z) + 5, f'{z:.2f}', 14, MU, 400, 'end'))
    for BB, col in ((1.8, PURPLE), (2.2, BLUE), (3.0, AMBER)):
        pts = []
        for i in range(401):
            r = 2 ** (-2 + 4 * i / 400)
            z = 0.5 + 0.5 * max(-1, min(1, math.log(r) / math.log(BB)))
            pts.append((X(r), Y(z)))
        b.append(P(pts, col, 3))
    b.append(T(278, 543, 'Lining B = 1.8', 16, PURPLE, 700))
    b.append(T(278, 572, 'Cotton B = 2.2', 16, BLUE, 700))
    b.append(T(278, 601, 'Denim B = 3.0', 16, AMBER, 700))
    b.append(T(1284, 793, 'Balance zone z = 0.4–0.6', 16, GREEN, 700, 'end'))
    b.append(T(190, 729, 'Interlacing-point position (0 = underside, 1 = top)', 16, MU, 400, 'middle', rot=-90))
    b.append(T(771, 997, 'Tension ratio r (log scale)', 17, MU, 400, 'middle'))
    b.append(T(1377, 552, ['The interlacing point is pulled in opposite',
                           'directions by the two threads. Friction at the',
                           'edges of the needle hole acts like a brake: while',
                           'the tension ratio lies between 1/B and B (the',
                           'balance band), the point stays within the fabric',
                           'thickness; outside that range it is pulled to',
                           'the top or the underside.', '',
                           'The larger B, the easier the balance is to set:',
                           'thick, soft fabrics are more forgiving than',
                           'thin, slippery ones.', '',
                           'Within the balance zone (z = 0.4–0.6) the',
                           'interlacing point sits in the middle of the fabric',
                           'and neither thread shows on the other side.'], 16.5, INK, lh=26))
    build('fig_7_balance', 1059, '\n'.join(b))


# ---------------------------------------------------------------- 7-2 capstan
def fig_capstan():
    b = [head('Capstan friction: thread tension grows exponentially as it wraps round a part',
              'Pulled in the direction of motion round a cylinder with wrap angle θ, the tension rises from T₁ to '
              'T₂ = T₁·e<tspan baseline-shift="super" font-size="13">μθ</tspan>; read the other way, the tension ahead is '
              '“cut down” by the friction behind')]
    b.append(R(48, 142, 658, 634, '#fff', GRID, 1.5, 10))
    cx, cy, rr = 376, 448, 105
    defs = ('<radialGradient id="cyl" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#ffffff"/>'
            '<stop offset="1" stop-color="#b8c0c8"/></radialGradient>')
    b.append(C(cx, cy, rr, 'url(#cyl)', '#5a6570', 2))
    # thread: vertical up at x = cx - rr - 2 from y=683 to cy, wrap over top to tangent toward (592,262)
    rt = rr + 3
    tx, ty = 592, 262
    # tangent point from external point
    dx, dy = tx - cx, ty - cy
    d = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    alpha = math.acos(rt / d)
    tang = ang - alpha  # choose the upper-right tangent (screen coords)
    a_end = tang
    # arc from angle pi (left) going over the top (negative y) to a_end
    pts = [(cx - rt, 683), (cx - rt, cy)]
    a0 = math.pi
    a1 = a_end + 2 * math.pi if a_end < 0 else a_end
    # go from pi to angles decreasing through -pi/2 (top) ... use parametrisation in screen coords
    n = 80
    start, stop = math.pi, (a_end if a_end > 0 else a_end + 2 * math.pi)
    # screen y down: top of circle is angle -pi/2 == 3pi/2; travel from pi up to 3pi/2 then to a_end+2pi
    stop = math.radians(300)
    tx, ty = 592, 262
    for i in range(n + 1):
        a = start + (stop - start) * i / n
        pts.append((cx + rt * math.cos(a), cy + rt * math.sin(a)))
    pts.append((tx, ty))
    b.append(P(pts, '#1f4fa8', 6) + P(pts, '#3a7be0', 3))
    # theta arc
    th = [(cx + 46 * math.cos(a), cy - 20 + 46 * math.sin(a)) for a in [math.pi + 0.9 * (1.37) * i / 30 * 1.0 for i in range(31)]]
    th = []
    for i in range(41):
        a = math.radians(180 + 110 * i / 40)
        th.append((cx + 47 * math.cos(a), cy - 2 + 47 * math.sin(a)))
    b.append(P(th, AMBER, 2.2))
    b.append(T(369, 430, 'θ', 22, AMBER, 700, 'middle'))
    b.append(T(232, 671, 'T₁', 24, BLUE, 700))
    b.append(T(597, 268, 'T₂ = T₁e<tspan baseline-shift="super" font-size="16">μθ</tspan>', 24, BLUE, 700))
    b.append(T(376, 752, 'Thread pulled this way →', 16, MU, 400, 'middle'))
    # chart
    b.append(R(836, 142, 1105, 552, '#fff', GRID, 1.5, 10))
    X0, X1, Y0, Y1 = 847, 1929, 153, 683
    X = lambda t: X0 + t / 360 * (X1 - X0)
    Y = lambda v: Y1 - (v - 1) / 4 * (Y1 - Y0)
    for t in range(0, 361, 60):
        b.append(L(X(t), Y0, X(t), Y1))
        b.append(T(X(t), 708, f'{t}°', 14, MU, 400, 'middle'))
    for v in range(1, 6):
        b.append(L(X0, Y(v), X1, Y(v)))
        b.append(T(X0 - 10, Y(v) + 5, str(v), 14, MU, 400, 'end'))
    for mu, col in ((0.35, RED), (0.2, BLUE), (0.15, '#239a4e')):
        pts = []
        for i in range(721):
            t = i / 2
            v = math.exp(mu * math.radians(t))
            if v > 5.0:
                tt = math.degrees(math.log(5) / mu)
                pts.append((X(tt), Y(5)))
                break
            pts.append((X(t), Y(v)))
        b.append(P(pts, col, 3))
    b.append(T(1545, 230, 'μ = 0.35', 17, RED, 700, 'end'))
    b.append(T(1777, 410, 'μ = 0.2', 17, BLUE, 700, 'end'))
    b.append(T(1872, 489, 'μ = 0.15', 17, '#239a4e', 700, 'end'))
    b.append(C(X(180), Y(math.exp(0.35 * math.pi)), 7, '#fff', INK, 2))
    b.append(T(1402, 443, 'Needle eye ≈ 180°: ×3.0', 16, INK, 700))
    b.append(C(X(math.degrees(1)), Y(math.exp(0.2)), 7, '#fff', INK, 2))
    b.append(T(1033, 679, 'Thread guide, 1 rad: ×1.22', 16, INK, 700))
    b.append(T(780, 418, 'Amplification T₂ / T₁', 16, MU, 400, 'middle', rot=-90))
    b.append(T(1383, 738, 'Wrap angle θ (°)', 17, MU, 400, 'middle'))
    build('fig_7_capstan', 824, '\n'.join(b), defs)


# ---------------------------------------------------------------- 7-6 pucker
def fig_pucker():
    b = [head('Tension pucker and thread tension (illustrative model, two plies of cotton, stitch length 3 mm)',
              'Vertical axis: seam shortening caused by elastic recovery of the thread; the fabric absorbs about 0.6%, '
              'the excess shows as pucker')]
    X0, X1, Y0, Y1 = 188, 1247, 153, 706
    X = lambda t: X0 + t / 80 * (X1 - X0)
    Y = lambda v: Y1 - v / 2.5 * (Y1 - Y0)
    b.append(R(178, 142, 1080, 574, '#fff', GRID, 1.5, 8))
    b.append(R(X(35), Y0, X1 - X(35), Y(0.6) - Y0, '#fbf0f0', 'none', 0))
    b.append(R(X0, Y0, X(35) - X0, Y1 - Y0, '#eef0f3', 'none', 0, extra='fill-opacity="0.9"'))
    b.append(R(X0, Y0, X(35) - X0, Y(0.6) - Y0, '#ede6e7', 'none', 0))
    for t in range(0, 81, 10):
        b.append(L(X(t), Y0, X(t), Y1))
        b.append(T(X(t), 732, str(t), 14, MU, 400, 'middle'))
    for v in (0, 0.5, 1, 1.5, 2, 2.5):
        b.append(L(X0, Y(v), X1, Y(v)))
        b.append(T(X0 - 10, Y(v) + 5, f'{v:.1f}', 14, MU, 400, 'end'))
    # model: shortening % = T/EA * (s+t)/s * 100 ; s = 3, t = 1.0 ; EA from the chapter (Tex24 6700 cN)
    for EA, col, lab, ly in ((5000, RED, 'Tex 18', 234), (6700, BLUE, 'Tex 24', 348), (10700, '#239a4e', 'Tex 40', 477)):
        f = lambda t: t / EA * (4 / 3) * 100
        b.append(P([(X(0), Y(0)), (X(80), Y(f(80)))], col, 3))
        b.append(T(1220, ly, lab, 17, col, 700, 'end'))
    b.append(L(X0, Y(0.6), X1, Y(0.6), INK, 1.6, '7 5'))
    b.append(T(200, 563, 'Shortening the fabric can absorb (0.6%)', 16, INK, 700))
    b.append(T(1008, 185, 'Pucker zone', 17, RED, 700, 'middle'))
    b.append(T(420, 689, 'Stitches too loose', 16, MU, 700, 'middle'))
    b.append(T(120, 435, 'Seam shortening (%)', 16, MU, 400, 'middle', rot=-90))
    b.append(T(713, 762, 'Mean tension at the interlacing point (cN)', 17, MU, 400, 'middle'))
    b.append(T(1306, 187, ['Model (illustrative):', '',
                           'During tightening the thread stretches',
                           'by ε = T / EA. Once sewn, the thread',
                           'springs back and shortens the seam by',
                           'ε × the thread used per cm of seam.',
                           'The fabric itself absorbs a small part;',
                           'the rest bulges into pucker.', '',
                           'At the same tension a thicker thread',
                           '(larger EA) stretches less and puckers',
                           'less — but on thin, tightly woven fabric',
                           'it causes structural pucker.', '',
                           'So the basic cure for tension pucker:',
                           'keep the stitch balanced and not loose,',
                           'and bring both tensions to the minimum.'], 16.5, INK, lh=28.2))
    build('fig_7_pucker', 847, '\n'.join(b))


# ---------------------------------------------------------------- 7-3 dyn
def fig_dyn():
    import json
    raw = json.load(open('/home/claude/sm/figsrc/en78/dyn.json'))
    # resample to 0.5 deg and smooth (digitised from the zh figure; the curve is illustrative)
    import numpy as np
    a = np.array(raw)
    grid = np.arange(0, 360.01, 0.5)
    v = np.interp(grid, a[:, 0], a[:, 1])
    k = np.ones(9) / 9
    vp = np.concatenate([v[-5:-1], v, v[1:5]])
    vs = np.convolve(vp, k, mode='same')[4:-4]
    b = [head('Needle-thread tension within one stitch (illustrative)',
              'Schematic curve following the regularities reported for single-needle lockstitch machines, measured downstream '
              'of the tension assembly; timing from the Chapter 4–5 worked examples')]
    X0, X1, Yb, Yt = 176, 1929, 659, 229
    X = lambda t: X0 + t / 360 * (X1 - X0)
    Y = lambda u: Yb - u * (Yb - Yt)
    b.append(R(165, 153, 1775, 516, '#fff', GRID, 1.5, 8))
    b.append(R(X(101.7), 165, X(206) - X(101.7), Yb - 165, '#f3f4f6', 'none', 0))
    b.append(R(X(206), 165, X(341) - X(206), Yb - 165, '#fcf1ed', 'none', 0))
    for t in range(0, 361, 30):
        b.append(L(X(t), 165, X(t), Yb))
        b.append(T(X(t), 685, f'{t}°', 14, MU, 400, 'middle'))
    for u in (0, 0.25, 0.5, 0.75, 1.0):
        b.append(L(X0, Y(u), X1, Y(u)))
        b.append(T(X0 - 12, Y(u) + 5, f'{u:.2f}', 14, MU, 400, 'end'))
    for t, lab in ((55, 'Take-up tightest 55°'), (101.7, 'Needle point enters'), (206, 'Loop caught 206°'), (341, 'Cast-off 341°')):
        b.append(L(X(t), 165, X(t), Yb, INK, 1.4, '5 4'))
        b.append(T(X(t) + 5, 183, lab, 15, INK))
    b.append(P([(X(g), Y(u)) for g, u in zip(grid, vs)], BLUE, 3.2))
    b.append(T(440, 228, '← Tightening peak: the take-up lever pulls the stitch tight;', 16, RED, 700))
    b.append(T(462, 252, 'set directly by the tension-assembly pre-tension', 16, RED, 700))
    b.append(T(480, 391, '← Before take-up tightest: thread for the next stitch', 16, PURPLE, 700))
    b.append(T(502, 415, 'is drawn off (sliding between the tension discs)', 16, PURPLE, 700))
    b.append(T(925, 550, 'Take-up paying out: check spring keeps a small tension', 15, MU, 700, 'middle'))
    b.append(T(1540, 391, ['Loop passes round the bobbin case', '(depends on friction with the hook)'], 16, '#c4531d', 700, 'middle', lh=24))
    b.append(T(1725, 288, ['Around cast-off: bobbin pre-tension', 'affects needle-thread tension here'], 16, '#c4531d', 700, 'middle', lh=24))
    b.append(T(108, 411, 'Tension / tightening peak', 16, MU, 400, 'middle', rot=-90))
    b.append(T(1047, 715, 'Main-shaft angle (needle bar at top dead centre = 0°)', 17, MU, 400, 'middle'))
    b.append(T(177, 764, ['Regularities reported by the study: the highest peak is the tightening tension, set directly by the tension-assembly pre-tension; '
                          'a thicker thread has a lower',
                          'tightening tension, which may upset the stitch balance; fabric thickness hardly affects needle-thread tension; speed has little effect '
                          'near the tension assembly;',
                          'the bobbin pre-tension affects needle-thread tension only while the take-up lever rises and casts the loop off the hook. '
                          'Curve shape and relative heights are illustrative.'], 15.5, INK, lh=26))
    build('fig_7_dyn', 894, '\n'.join(b))


# ---------------------------------------------------------------- 7-1 src
def fig_src():
    b = [head('Where the needle-thread and bobbin-thread tensions come from', 'Schematic; blue: needle thread; orange: bobbin thread')]
    defs = (arrow_marker('ar', RED) + arrow_marker('aa', AMBER) +
            '<linearGradient id="disc" x1="0" x2="1"><stop offset="0" stop-color="#3d4650"/><stop offset=".5" stop-color="#9aa4ae"/><stop offset="1" stop-color="#3d4650"/></linearGradient>'
            '<linearGradient id="ndl" x1="0" x2="1"><stop offset="0" stop-color="#8a949e"/><stop offset=".5" stop-color="#eef0f2"/><stop offset="1" stop-color="#8a949e"/></linearGradient>')
    b.append(R(48, 142, 1152, 870, '#fff', GRID, 1.5, 12))
    b.append(R(1248, 142, 705, 870, '#fff', GRID, 1.5, 12))
    b.append(T(75, 188, 'a', 22, INK, 700) + T(113, 188, 'Tension elements on the needle-thread path', 22, INK, 700))
    b.append(T(1275, 188, 'b', 22, INK, 700) + T(1313, 188, 'Bobbin case: bobbin-thread tension', 22, INK, 700))
    # thread cone
    b.append(R(94, 236, 82, 82, '#cfe0f7', '#2a5fb8', 2, 8))
    b.append(T(135, 348, 'Thread cone', 16, MU, 400, 'middle'))
    # tension post, discs, spring, nut
    b.append(R(341, 440, 260, 14, '#9aa4ae', '#6b7580', 1))
    b.append(R(451, 387, 13, 119, 'url(#disc)', '#2b333b', 1.2, 4))
    b.append(R(476, 387, 13, 119, 'url(#disc)', '#2b333b', 1.2, 4))
    zz = [(492, 447)]
    for i in range(8):
        zz.append((498 + i * 11.5, 422 if i % 2 == 0 else 472))
    zz.append((586, 447))
    b.append(P(zz, AMBER, 3))
    b.append(R(585, 425, 32, 43, '#c8ced4', '#5a6570', 1.5, 4))
    # thread
    th = [(176, 318), (294, 352), (470, 341), (470, 505)]
    th += [(470 + 70 * (1 - math.cos(a)) * 0 + 70 * math.sin(a) * 0, 0) for a in []]
    curve = []
    for i in range(1, 21):
        tt = i / 20
        x = (1 - tt) ** 2 * 470 + 2 * (1 - tt) * tt * 470 + tt * tt * 540
        y = (1 - tt) ** 2 * 505 + 2 * (1 - tt) * tt * 555 + tt * tt * 552
        curve.append((x, y))
    th += curve + [(683, 505), (776, 388), (929, 293), (1035, 411), (1048, 660), (1058, 822)]
    b.append(P(th, '#1f4fa8', 5.5) + P(th, '#3a7be0', 2.6))
    for x, y in ((294, 352), (776, 388), (1035, 411)):
        b.append(C(x, y, 10, '#fff', '#5a6570', 2))
    b.append(C(929, 293, 12, '#fff', PURPLE, 3))
    # check spring
    b.append(P([(612, 565), (630, 540), (655, 518), (683, 505)], '#5a6570', 3))
    b.append(C(683, 505, 5, '#5a6570', '#5a6570', 1))
    # needle
    b.append(R(1051, 658, 15, 190, 'url(#ndl)', '#5a6570', 1.2))
    b.append(f'<ellipse cx="1058.5" cy="823" rx="3.5" ry="9" fill="#fff" stroke="#5a6570" stroke-width="1.5"/>')
    b.append(L(893, 917, 1050, 828, '#5a6570', 1.3))
    # labels
    b.append(T(268, 320, 'Discs pushed apart when the presser foot is lifted (≥ 0.5 mm)', 15, RED))
    b.append(L(402, 330, 433, 374, RED, 1.8, extra='marker-end="url(#ar)"'))
    b.append(L(552, 374, 500, 374, AMBER, 2, extra='marker-end="url(#aa)"'))
    b.append(T(560, 381, 'Spring force N', 16, AMBER, 700))
    b.append(T(569, 413, 'Tension nut', 16, MU))
    b.append(T(441, 482, 'Two tension discs', 16, MU, 400, 'end'))
    b.append(T(625, 597, 'Check spring (Chapter 4)', 16, MU, 400, 'middle'))
    b.append(T(792, 404, 'Thread guide', 16, MU))
    b.append(T(948, 282, 'Take-up lever eye', 16, PURPLE, 700))
    b.append(T(753, 588, ['Each guide the thread wraps round',
                          'multiplies the tension by e<tspan baseline-shift="super" font-size="12">μθ</tspan> (Fig. 7-2)'], 16, INK, lh=24))
    b.append(T(330, 622, ['Thread slides between the discs:',
                          'T<tspan baseline-shift="-4" font-size="13">out</tspan> = T<tspan baseline-shift="-4" font-size="13">in</tspan> + 2μN'], 17, INK, 700, lh=27))
    b.append(T(1040, 706, 'Needle', 16, MU, 400, 'end'))
    b.append(T(658, 940, ['Needle eye: the thread turns through about 180° here;',
                          'during tightening its tension is cut to about one third'], 16, INK, lh=24))
    # panel b
    cx, cy = 1588, 553
    b.append(C(cx, cy, 177, '#e9ecef', '#5a6570', 2.2))
    b.append(C(cx, cy, 123, '#fde3d4', '#c4531d', 2))
    b.append(C(cx, cy, 47, '#fff', '#5a6570', 2))
    b.append(T(cx, 560, 'Bobbin', 16, '#c4531d', 400, 'middle'))
    b.append(f'<path d="M1550,378 Q1660,345 1790,412" stroke="#5a6570" stroke-width="13" fill="none" stroke-linecap="round"/>')
    b.append(f'<path d="M1482,494 C1520,410 1570,370 1635,368 L1788,405 L1870,318" stroke="#c4531d" stroke-width="5" fill="none" stroke-linejoin="round"/>'
             f'<path d="M1482,494 C1520,410 1570,370 1635,368 L1788,405 L1870,318" stroke="#f07a45" stroke-width="2.4" fill="none" stroke-linejoin="round"/>')
    b.append(C(1658, 363, 8, '#c8ced4', '#5a6570', 1.5))
    b.append(T(1666, 318, 'Bobbin-case spring (leaf spring)', 16, '#3d4650', 700, 'middle'))
    b.append(T(1614, 353, 'Adjusting screw', 14.5, '#3d4650', 400, 'middle'))
    b.append(T(1283, 823, ['As the bobbin thread is drawn off the bobbin, the leaf',
                           'spring presses it against the case; the screw sets the',
                           'tension. It stays nearly constant within a stitch and',
                           'acts only while the thread is being pulled out.'], 16.5, INK, lh=28))
    build('fig_7_src', 1059, '\n'.join(b), defs)


# ---------------------------------------------------------------- 7-5 types
def wave(x0, x1, y, amp, n, step=2):
    return [(x, y + amp * math.sin((x - x0) / (x1 - x0) * n * 2 * math.pi)) for x in [x0 + i * step for i in range(int((x1 - x0) / step) + 1)]]


def fig_types():
    b = [head('Four types of seam pucker', 'Schematic; classification after a thread manufacturer’s material on the causes of pucker')]
    defs = arrow_marker('ag', '#5a6570')
    FB, FS = '#f0e2c4', '#b39a6a'
    heads = ['Tension pucker', 'Structural pucker', 'Dimensional instability', 'Feed pucker']
    texts = [['The thread is stretched while sewing and springs',
              'back afterwards, pulling the fabric short so it buckles.',
              'Remedy: lowest tension that still balances'],
             ['Tightly woven fabric has no room for needle and',
              'thread: the yarns are pushed apart, the fabric stretched.',
              'Remedy: finer needle and thread, lower stitch density'],
             ['After washing or pressing, thread and fabric shrink',
              'by different amounts and the seam is pulled into pucker.',
              'Remedy: low-shrink thread; match shell and interlining'],
             ['The two plies are fed unequally (Chapter 6) and the',
              'excess of one ply puckers.',
              'Remedy: adjust presser foot and dog height, or feed system']]
    for i in range(4):
        x0 = 48 + i * 482
        b.append(R(x0, 142, 458, 563, '#fff', GRID, 1.5, 12))
        b.append(T(x0 + 23, 186, 'abcd'[i], 22, INK, 700) + T(x0 + 59, 186, heads[i], 22, INK, 700))
        b.append(T(x0 + 23, 587, texts[i], 15, '#3d4650', lh=25))
    # a
    b.append(L(100, 318, 193, 318, RED, 2, extra='marker-end="url(#ag)"'))
    b.append(L(453, 318, 360, 318, RED, 2, extra='marker-end="url(#ag)"'))
    b.append(T(276, 324, 'Thread recoils', 16, RED, 700, 'middle'))
    b.append(P(wave(90, 464, 364, 9, 6), '#a88b5a', 12))
    b.append(L(88, 362, 466, 362, BLUE, 2.5))
    # b
    for x in (582, 622, 662, 702, 815, 855, 895, 935):
        b.append(C(x, 364, 18, '#ecdcb8', FS, 1.8))
    b.append(C(759, 364, 18, '#ecdcb8', FS, 1.8) + C(759, 364, 10, '#2f6fd6', '#1f4fa8', 1.8))
    b.append(L(712, 423, 630, 423, RED, 2, extra='marker-end="url(#ag)"'))
    b.append(L(806, 423, 888, 423, RED, 2, extra='marker-end="url(#ag)"'))
    b.append(T(754, 470, 'Yarns pushed apart (cross-section)', 16, MU, 400, 'middle'))
    # c
    b.append(T(1241, 303, 'Before washing', 16, MU, 400, 'middle'))
    b.append(L(1065, 317, 1417, 317, BLUE, 2.5))
    b.append(R(1065, 329, 352, 17, FB, FS, 1.2))
    b.append(P(wave(1100, 1382, 378, 6, 6), BLUE, 2.5))
    b.append(R(1100, 388, 282, 17, FB, FS, 1.2))
    b.append(T(1241, 433, 'After: fabric shrank, thread did not — seam bulges', 15, RED, 400, 'middle'))
    # d
    b.append(P(wave(1550, 1898, 353, 7, 5), '#c5d6ee', 13))
    b.append(R(1547, 364, 353, 14, FB, FS, 1.2))
    b.append(T(1724, 418, 'Excess length of the upper ply puckers', 16, RED, 400, 'middle'))
    build('fig_7_types', 753, '\n'.join(b), defs)


if __name__ == '__main__':
    names = sys.argv[1:] or ['balance', 'capstan', 'pucker', 'dyn', 'src', 'types']
    for n in names:
        globals()['fig_' + n]()
