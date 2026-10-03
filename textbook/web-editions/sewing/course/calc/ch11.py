"""Chapter 11 (special machines): numbers for course/lessons/ch11.json.
Model copied from src/zh/labs/zigzag.html (= book model11.py)."""
from math import pi, sin, cos, sqrt
D = pi / 180
R, L = 15.5, 55.0; lam = R / L; T = 1.5; MARGIN = 0.5; RH = 13.5; MASS = 0.15; FLIM = 250; RW = [0.978, 4.167]
X = lambda f: R * (1 - cos(f * D)) - L * (1 - sqrt(1 - (lam * sin(f * D)) ** 2))
HT = T + X(101.7); ztip = lambda f: HT - X(f); rise = lambda f: X(180) - X(f)
def bis(g, a, b):
    ga = g(a)
    for _ in range(80):
        m = (a + b) / 2; gm = g(m)
        if (gm > 0) == (ga > 0): a, ga = m, gm
        else: b = m
    return (a + b) / 2
print("leave / touch fabric surface:", round(bis(lambda f: ztip(f) - T, 181, 359), 1), round(bis(lambda f: ztip(f) - T, 1, 179), 1))
FEXIT = bis(lambda f: ztip(f) - (T + MARGIN), 181, 359); FENTER = bis(lambda f: ztip(f) - (T + MARGIN), 1, 179)
print("window with 0.5 mm margin: %.1f -> %.1f = %.1f deg" % (FEXIT, FENTER, 360 - FEXIT + FENTER))
# thicker fabric 4 mm: needle tip top is HT-X(0)=HT above plate (needle stroke unchanged, same top position)
for t in (3.0, 4.0):
    fx = bis(lambda f: ztip(f) - (t + MARGIN), 181, 359); fn = bis(lambda f: ztip(f) - (t + MARGIN), 1, 179)
    print("fabric %.1f mm: window %.1f -> %.1f = %.1f deg" % (t, fx, fn, 360 - fx + fn))
K = {'SH': pi ** 2 / 2, 'CY': 2 * pi, 'MT': 4.888}
def amax(law, w_mm, n, beta_deg): om = 2 * pi * n / 60; return K[law] * w_mm * 1e-3 * om * om / (beta_deg * D) ** 2
for law in K:
    a = amax(law, 8, 5000, 170); print(law, "8mm 5000rpm 170deg: a=%.0f m/s2, F=%.0f N" % (a, MASS * a))
print("CY at 120 deg: a=%.0f F=%.0f N" % (amax('CY', 8, 5000, 120), MASS * amax('CY', 8, 5000, 120)), " ratio", round((170 / 120) ** 2, 2))
print("speed 6000/5000 ratio", (6000 / 5000) ** 2, " MT at 6000:", round(amax('MT', 8, 6000, 170)))
b = sqrt(K['CY'] * 0.008 * (2 * pi * 5000 / 60) ** 2 * MASS / FLIM) / D; print("min swing span for CY at 250 N:", round(b, 1), "deg")
print("MT 10mm 5000 170:", round(amax('MT', 10, 5000, 170)), "F", round(MASS * amax('MT', 10, 5000, 170)))
print("MT 8mm 4500 170: F", round(MASS * amax('MT', 8, 4500, 170)))
for w in (6, 8, 10): print("bight", w, "dphi = %.2f deg" % (w / (2 * RH) / D))
fL = bis(lambda f: rise(f) - 3.8, 180.01, 300); fR = fL - 8 / (2 * RH) / D
print("standard: left catch %.1f deg (rise 3.8), right catch %.1f deg rise %.2f; difference %.2f mm" % (fL, fR, rise(fR), 3.8 - rise(fR)))
fL = bis(lambda f: rise(f) - RW[1], 180.01, 300); fR = bis(lambda f: rise(f) - RW[0], 180.01, 300)
print("max bight: catch %.1f..%.1f, dphi %.1f, w = %.2f mm" % (fR, fL, fL - fR, 2 * RH * (fL - fR) * D))
# Chapter 5 window 1.5-2.8 mm
fL5 = bis(lambda f: rise(f) - 2.8, 180.01, 300); fR5 = bis(lambda f: rise(f) - 1.5, 180.01, 300)
print("with ch5 window 1.5-2.8: dphi %.1f, w = %.2f mm" % (fL5 - fR5, 2 * RH * (fL5 - fR5) * D))
# embroidery: frame 3 mm step at 1200 rpm within 170 deg, MT
for n in (1200, 5000): print("3 mm step MT at", n, ":", round(amax('MT', 3, n, 170)), "m/s2")
print("bartacker 3200 sti/min, 5 mm step, 170 deg MT:", round(amax('MT', 5, 3200, 170)), "m/s2")
print("MT at 120 deg: a=%.0f F=%.0f N" % (amax('MT', 8, 5000, 120), MASS * amax('MT', 8, 5000, 120)))
# assignment: 10 mm bight
for law in ('MT', 'CY'):
    F = MASS * amax(law, 10, 5000, 170); nmax = 5000 * sqrt(FLIM / F)
    print("10 mm", law, "F at 5000 = %.0f N, max speed for 250 N = %.0f r/min" % (F, nmax))
print("10 mm bight dphi %.1f vs allowed %.1f" % (10 / (2 * RH) / D, fL - fR))
a5 = amax('MT', 5, 3200, 170); print("bartack 5 mm step @3200: %.0f m/s2; 8 mm step same accel -> n = %.0f" % (a5, 3200 * sqrt(5 / 8)))
