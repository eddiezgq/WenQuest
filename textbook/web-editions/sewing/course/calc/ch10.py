"""Chapter 10 (coverstitch & chainstitch): numbers for course/lessons/ch10.json.
Looper model copied from src/zh/labs/looper.html (= book model10.py); consumption model from labs/coverstitch.html."""
from math import pi, sin, cos, sqrt, acos, exp, ceil
D = pi / 180
R, L = 15.5, 55.0; lam = R / L; T = 1.5; RN = 0.45; S = 30; H0 = 2.2
X = lambda f: R * (1 - cos(f * D)) - L * (1 - sqrt(1 - (lam * sin(f * D)) ** 2))
HT = T + X(101.7); DEYE = X(114.18) - X(101.7) - T
ztip = lambda f: HT - X(f); rise = lambda f: X(180) - X(f)
floop = lambda h: (max(h, 0) / H0) ** 2 * exp(2 * (1 - max(h, 0) / H0))
def bis(g, a, b):
    ga = g(a)
    for _ in range(80):
        m = (a + b) / 2; gm = g(m)
        if (gm > 0) == (ga > 0): a, ga = m, gm
        else: b = m
    return (a + b) / 2
RW = [bis(lambda h: floop(h) - 0.6, 0.3, H0), bis(lambda h: floop(h) - 0.6, H0, 8)]
STD = dict(dphi=0, dz=0, e=1.0, gap=0.03, rr=3.2); PHR0 = 176
dcOf = lambda rr: acos(max(-1, min(1, 1 - 2 * rr / S))) / D
ZB0 = ztip(PHR0 + dcOf(3.2)) + DEYE + 1.5
m360 = lambda f: f % 360
def evaluate(ST):
    phR = PHR0 + ST['dphi']; dc = dcOf(ST['rr']); y0 = -(RN + ST['gap']) + ST['e'] * sin(dc * D); zb = ZB0 + ST['dz']
    looper = lambda f: (ST['rr'] - S / 2 * (1 - cos((f - phR) * D)), y0 - ST['e'] * sin((f - phR) * D))
    fc = m360(phR + dc); h = rise(fc); eye = ztip(fc) + DEYE; ds = zb - eye; ytop = 0.5 + 0.9 * max(h, 0)
    gap = -looper(fc)[1] - RN
    fd = bis(lambda f: ztip(f) - zb, 60, 179.9); fu = bis(lambda f: ztip(f) - zb, 180.1, 300)
    xd, yd = looper(fd); wb = wf = 9; f = 0.0
    while f < 360:
        if ztip(f) <= zb:
            x, y = looper(f)
            if x <= 0:
                if 180 <= f <= fu: wb = min(wb, -y - RN)
                else: wf = min(wf, y - RN)
        f += 0.25
    ok = [RW[0] <= h <= RW[1], 0.2 <= ds <= ytop - 0.3, 0 <= gap <= 0.10, (-xd - RN) >= 0.3 and (yd - RN) >= 0.2, wb >= -0.001 and wf >= 0.05]
    return dict(fc=fc, h=h, ds=ds, gap=gap, fd=fd, xd=xd, yd=yd, ok=ok, fr=m360(phR - dc))
print("loop window (rise) =", [round(x, 2) for x in RW])
r = evaluate(STD); print("standard: catch %.1f deg rise %.2f mm, needle at looper height %.1f deg, point x %.2f y %.2f, return %.1f" % (r['fc'], r['h'], r['fd'], r['xd'], r['yd'], r['fr']), r['ok'])
r5 = evaluate(dict(STD, dphi=5)); print("retard 5 deg: rise %.2f mm" % r5['h'], r5['ok'])
ra = evaluate(dict(STD, dphi=-5)); print("advance 5 deg:", ra['ok'])
ok = [d / 2 for d in range(-30, 31) if all(evaluate(dict(STD, dphi=d / 2))['ok'])]; print("timing window:", ok[0], "to", ok[-1])
em = next(e / 50 for e in range(0, 101) if all(evaluate(dict(STD, e=e / 50))['ok'])); print("min needle-avoid amplitude:", em)
rr = [x / 20 for x in range(20, 141) if all(evaluate(dict(STD, rr=x / 20))['ok'])]; print("retraction range:", rr[0], rr[-1])
print("A=B case: rightmost at 180 -> rise", round(rise(180 + dcOf(3.2)), 2))
# spreader: needle bar 1.1 mm below TDC
print("spreader leftmost angle (1.1 mm descent):", round(bis(lambda f: X(f) - 1.1, 0, 90), 1), "deg")
print("descent 2.0 mm ->", round(bis(lambda f: X(f) - 2.0, 0, 90), 1), "deg")

print("== consumption (lab 10-2) ==")
A_LOOP, A_COV = 0.5, 0.3
TY = {'401': (1, False), '406': (2, False), '407': (3, False), '602': (2, True), '605': (3, True)}
def cons(tp, spc=7, t=0.5, g=4.0, nr=1):
    s = 10 / spc; n, cov = TY[tp]; o = []
    for _ in range(nr if tp == '401' else 1):
        o += [('needle', (s + 2 * t + 2 * A_LOOP) / s)] * n
        o.append(('looper', (n * (2 * s + 2 * A_LOOP) + s + 2 * (0 if tp == '401' else g)) / s))
    if cov: o.append(('cover', (2 * g + n * 2 * A_COV) / s))
    return o
def order(tp, Lcm, Q, W, cone, **k):
    return [(nm, v, v * Lcm / 100 * Q * (1 + W), ceil(v * Lcm / 100 * Q * (1 + W) / cone - 1e-9)) for nm, v in cons(tp, **k)]
for tp, g in (('401', 0), ('406', 4.0), ('602', 4.0), ('605', 4.8)):
    c = cons(tp, g=g); print(tp, "ratio total %.2f" % sum(v for _, v in c), [(n, round(v, 2)) for n, v in c])
c406 = sum(v for _, v in cons('406')); c602 = sum(v for _, v in cons('602'))
print("602 vs 406: +%.1f %%" % ((c602 / c406 - 1) * 100), " needle share 406 %.0f%%" % (2 * cons('406')[0][1] / c406 * 100))
print("406 at 4 st/cm: %.2f (7 st/cm %.2f)" % (sum(v for _, v in cons('406', spc=4)), c406))
o = order('406', 172, 1000, 0.12, 5000); print("T-shirt batch:", [(n, round(v, 2), round(m), k) for n, v, m, k in o], "cones", sum(x[3] for x in o), "total m", round(sum(x[2] for x in o)))
print("published 18 x 172 cm =", 18 * 1.72, "m/pc; x1000x1.12 =", round(18 * 1.72 * 1000 * 1.12), "m")
o = order('401', 60, 1000, 0.12, 5000, spc=4, t=2.4, nr=2); print("jeans batch:", [(n, round(v, 2), round(m), k) for n, v, m, k in o])
o = order('602', 172, 1000, 0.12, 5000); print("T-shirt 602:", [(n, round(v, 2), round(m), k) for n, v, m, k in o], "cones", sum(x[3] for x in o))
o = order('605', 80, 2000, 0.10, 5000, g=5.6); print("assign 605 neck 80cm x2000, g5.6:", [(n, round(v, 2), round(m), k) for n, v, m, k in o], "cones", sum(x[3] for x in o))
print("301 vs 406 ratio", round(18 / 2.5, 1), " 605/301", round(28 / 2.5, 1))
print("timing window width 7.5 deg at 6500 r/min = %.3f ms" % (7.5 / (6500 / 60 * 360) * 1000))
