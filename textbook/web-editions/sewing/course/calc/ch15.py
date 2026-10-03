"""Ch.15 numbers for the course pack. Run: python3 ch15.py"""
from math import pi, sqrt, cos, sin, log, ceil
from scipy.optimize import brentq

r, l, TIP = 15.5, 55.0, 18.0
lam = r / l
def x(phi):  # needle-bar displacement from TDC, mm
    p = phi * pi / 180
    return r * (1 - cos(p)) - l * (1 - sqrt(1 - (lam * sin(p)) ** 2))
h = lambda phi: TIP - x(phi)
def window(t):
    p1 = brentq(lambda p: h(p) - t, 0, 180); p2 = 360 - p1
    return p1, p2, 360 - (p2 - p1)
def tmove(s_mm, a=50, v=1):
    s = s_mm / 1000
    return 2 * sqrt(s / a) if s <= v * v / a else s / v + v / a
nmax = lambda W, s, a=50, C=4: W / (6 * tmove(s, a) * sqrt(C / 4))

print("== book checks")
for t in (1.5, 3, 6):
    print("t", t, ["%.1f" % v for v in window(t)])
print("geometric W(1.5) =", window(1.5)[2], "(book table rounds the angles: 203.4)")
W15, W3, W6 = 203.4, 192.6, 170.5   # book Table (Sec. 15.3); used for all course questions
print("n 3mm/1.5", nmax(W15, 3), " t_move 3mm", tmove(3))
print("cap 2mm", nmax(W15, 2), " cap 10mm", nmax(W15, 10))
print("ex1 5mm t3", nmax(W3, 5), " ex2 a", 4 * 0.008 / (W15 / (6 * 2000)) ** 2)
print("thick ratio", W6 / W15, " diag factor", 2 ** -0.25)
print("belt k", 150e3 / 0.3 + 150e3 / 0.5, " fn", sqrt(800e3 / 3) / 2 / pi, " dx mm", 150 / 800e3 * 1000)
print("belt 25mm fn", sqrt(800e3 * 25 / 15 / 3) / 2 / pi)
dt = (W15 - 20) / (6 * 1600); print("fig 15-5 dt", dt, " a", 2 * pi * 0.003 / dt ** 2)
def motor(m, a, rp, Jm=0.3e-4, mu=0.05, frac=None):
    F = m * a + mu * m * 9.8; T = F * rp + Jm * a / rp
    frac = frac if frac is not None else W15 / 360
    return F, T, T * sqrt(frac)
print("motor 3kg 15mm", motor(3, 50, 0.015), " 10mm", motor(3, 50, 0.010), " ex7 2kg 12mm", motor(2, 50, 0.012))
print("rp opt mm", sqrt(0.3e-4 / 3) * 1000)
print("cyl force N", 0.5e6 * pi * 0.032 ** 2 / 4)
print("sol 24V t_pull", -5 * log(1 - 3 / 4), " 75V", -5 * log(1 - 3 / 12.5), " diode rel", 5 * log(1.7 / 0.6), " TVS", 0.03 * 1.7 / 48 * 1000, " PWM hold A", 24 * 0.3 / 6)
print("buttonhole stitches", 2 * 12 / 0.4 + 2 * 8, " time s", 76 / 3000 * 60)

def lookahead(caps, dn, n_start):
    c = caps[:]
    for i in range(len(c) - 2, -1, -1):
        c[i] = min(c[i], c[i + 1] + dn)
    n = [min(c[0], n_start)]
    for i in range(1, len(c)):
        n.append(min(c[i], n[-1] + dn))
    return n
caps = [nmax(W15, s) for s in (2, 2, 2, 2, 10, 2, 2, 2)]
print("lookahead 300", [int(v) for v in lookahead(caps, 300, 2680)])

print("== problem: pocket flap at 2000 r/min")
print("3mm/1.5", nmax(W15, 3), " 6mm/1.5", nmax(W15, 6), " 3mm/6", nmax(W6, 3), " 6mm/6", nmax(W6, 6), " tmove 6", tmove(6))
print("60 stitches @2000 s", 60 * 60 / 2000)

print("== quiz")
print("q1 4mm", nmax(W15, 4))
print("q2 deg", 6 * 2400 * 1.2e-3)
print("q3 5mm @45deg", W15 / (6 * tmove(5 / sqrt(2))))
k = 150e3 / 0.2 + 150e3 / 0.6; print("q8 k", k, " fn", sqrt(k / 2.5) / 2 / pi)
print("q9 motor 4kg 40 12mm", motor(4, 40, 0.012))

print("== exam")
print("e1 lookahead dn=250", [int(v) for v in lookahead(caps, 250, 2680)])
print("e2 2.5mm t3 a60", nmax(W3, 2.5, 60))
print("e3 Trms", 2.0 * sqrt(0.5))
print("e5 t_pull", -5 * log(1 - 2.5 / 12), " steady A", 60 / 5)

print("== assignment")
for s in (2, 4, 8):
    print("a1 t=3mm s", s, " C4", nmax(W3, s), " C6.28", nmax(W3, s, C=6.283))
print("a1 4mm at 45deg, C4", W3 / (6 * tmove(4 / sqrt(2))))
caps1 = [nmax(W15, s) for s in (2, 2, 2, 2, 10, 2, 2, 2)]
print("a2 lookahead dn=200", [int(v) for v in lookahead(caps1, 200, 2680)])
print("a3 X 2.5kg 12mm", motor(2.5, 50, 0.012, frac=0.57))
print("a3 Y 7kg 12mm", motor(7, 50, 0.012, frac=0.57))
# max accel of Y under rated rms 1.27 N.m: T(a) = (m a + mu m g) rp + Jm a/rp ; Trms = T sqrt(0.57) = 1.27
m, rp, Jm = 7, 0.012, 0.3e-4
Tlim = 1.27 / sqrt(0.57)
aY = (Tlim - 0.05 * m * 9.8 * rp) / (m * rp + Jm / rp)
print("a3 Y max accel under rated rms", aY, " Tpeak at that a", (m * aY + 0.05 * m * 9.8) * rp + Jm * aY / rp)
print("a3 n_max 3mm along Y with aY, W15", nmax(W15, 3, a=aY))
