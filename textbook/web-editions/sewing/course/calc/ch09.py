"""Chapter 9 (overlock machine): numbers used in course/lessons/ch09.json.
Formulas and data from src/zh/ch09.html sections 9.5, 9.6, 9.10 and labs rssr / difffeed."""
import numpy as np
from math import pi, sin, cos, sqrt, radians, degrees, asin

print("== 9.10 differential feed ==")
def dstar(e0, eta): return 1 + e0 / eta
def wave(lam, eps): return lam * sqrt(eps) / pi
def eps_of(e0, eta, D): De = 1 + eta * (D - 1); return (1 + e0) / De - 1, De
print("jersey D* =", round(dstar(0.18, 0.85), 3), " wave at D=1 (lam 30):", round(wave(30, 0.18), 2), "mm")
print("rib    D* =", round(dstar(0.30, 0.80), 3), " wave at D=1 (lam 26):", round(wave(26, 0.30), 2), "mm")
e, De = eps_of(0.18, 0.85, 1.3); print("jersey D=1.3: De =", round(De, 3), " eps =", round(e * 100, 2), "%")
e, De = eps_of(0.10, 0.90, 1.0); print("fleece D=1.0: eps =", round(e*100,1), "% wave (lam 36):", round(wave(36, e), 2), "mm; D* =", round(dstar(0.10,0.90),3))
# arm lengths
print("l_d for D*=1.21 with l_m = 20 mm:", round(20 * dstar(0.18, 0.85), 2), "mm")

print("== 9.5 needle bar ==")
r, l = 12.25, 42.0; lam = r / l
s = lambda p: r * (1 - cos(p)) - l * (1 - sqrt(1 - (lam * sin(p)) ** 2))
h = lambda p: 9.5 - s(p) * cos(radians(20))   # tip height above throat plate
print("lowest tip height:", round(h(pi), 2))
def cross(t):
    ph = np.radians(np.arange(0, 360, 0.001)); H = np.array([h(p) for p in ph])
    i = np.where(np.diff(np.sign(H - t)) != 0)[0]
    return [round(float(np.degrees(ph[k])), 1) for k in i]
for t in (1.5, 3.0):
    a = cross(t); print(f"fabric {t} mm: enter/leave {a}, in-fabric {round(a[1]-a[0],1)} deg, out {round(360-(a[1]-a[0]),1)} deg")
print("feed window 292->68 =", 360 - 292 + 68, "deg; margins", round(292 - 279.2, 1), round(80.8 - 68, 1))

print("== 9.6 RSSR ==")
w = 2 * pi * 7000 / 60; print("omega =", round(w, 1), "rad/s")
print("tip speed 182.4 rad/s x 38 mm =", round(182.4 * 0.038, 2), "m/s")
print("rough swing 2r/c =", round(degrees(2 * 4.36 / 22), 1), "deg; exact 25.7 -> ratio", round(25.7 / degrees(2 * 4.36 / 22), 3))
r30 = radians(30) * 22 / 2; print("rough r for 30 deg:", round(r30, 2), " increase", round(r30 - 4.36, 2), "mm")
print("mobility F =", 6 * 3 - (5 + 3 + 3 + 5))
for g in (39, 40, 49.5, 60): print(f"1/sin({g}) =", round(1 / sin(radians(g)), 3))
print("upper/lower link force ratio:", round(sin(radians(49.5)) / sin(radians(39)), 3))
# exercise 7: theta-dot at phi=180
A = np.array([22.00, 4.77, -48.93]); B = np.array([22.00, 16.89, -67.86]); Q = np.array([0, 16.65, -67.77])
e = np.array([0, 0.342, 0.940]); e = e / np.linalg.norm(e); C = np.array([22.0, 1.27606, -51.53467])
d = A - B; rr = B - Q; t = np.cross(e, rr); Ad = w * np.cross([1, 0, 0], A - C)
print("d =", d.round(2), "|d| =", round(np.linalg.norm(d), 2), " t =", t.round(2), " Adot =", Ad.round(0))
print("theta_dot =", round(float(d @ Ad / (d @ t)), 1), "rad/s; gamma =", round(degrees(asin(abs(d @ t) / np.linalg.norm(d) / np.linalg.norm(t))), 1))

# full RSSR as in labs/rssr.html (preset LL) for swing, transmission, critical radius
M0 = np.array([22.0, 1.27606, -51.53467])
def rot(v, ax, th): return v * cos(th) + np.cross(ax, v) * sin(th) + ax * (ax @ v) * (1 - cos(th))
def stats(r=4.3619, b=22.4789, c=22, gam=90, bet=20, dl=-7.133, Q0=(0, 16.6497, -67.772), xc=22, ph0=-2.50136, s_=0):
    ex = np.array([1., 0, 0]); D = pi / 180
    e = np.array([cos(gam*D), sin(gam*D)*sin(bet*D), sin(gam*D)*cos(bet*D)]); e /= np.linalg.norm(e)
    ref = ex - e * (ex @ e); ref /= np.linalg.norm(ref); v0 = rot(ref, e, dl * D); v1 = np.cross(e, v0)
    Qp = np.array(Q0) + e * s_; Cc = np.array([xc, M0[1], M0[2]])
    th, gm, fail, prev, thd = [], [], 0, None, []
    for k in range(360):
        ang = k * D + ph0; A = Cc + r * np.array([0, cos(ang), sin(ang)])
        K = A - Qp; P_ = K @ v0; K_ = K @ v1; M = (K @ K + c*c - b*b) / (2*c); rho = np.hypot(P_, K_)
        if abs(M) > rho: fail += 1; continue
        t_ = np.arctan2(K_, P_) + np.arccos(M / rho)
        if prev is not None:
            while t_ - prev > pi: t_ -= 2*pi
            while t_ - prev < -pi: t_ += 2*pi
        prev = t_; th.append(t_)
        rv = c * (v0 * cos(t_) + v1 * sin(t_)); Bp = Qp + rv; dd = A - Bp; tt = np.cross(e, rv)
        Ad_ = w * np.cross(ex, A - Cc); thd.append(dd @ Ad_ / (dd @ tt))
        gm.append(degrees(asin(min(1, abs(dd @ tt) / np.linalg.norm(dd) / np.linalg.norm(tt)))))
    if fail: return None
    return degrees(max(th) - min(th)), min(gm), max(abs(x) for x in thd)
print("LL preset: swing, min gamma, max theta_dot =", [round(x, 2) for x in stats()])
lo, hi = 4.4, 20
for _ in range(40):
    mid = (lo + hi) / 2
    if stats(r=mid) is None: hi = mid
    else: lo = mid
print("critical crank radius ~", round(lo, 2), "mm")
lo, hi = 4.36, 8
for _ in range(40):
    mid = (lo + hi) / 2
    if stats(r=mid)[0] < 30: lo = mid
    else: hi = mid
print("exact r for 30 deg swing:", round(lo, 2), "mm (rough estimate", round(r30, 2), ")")
