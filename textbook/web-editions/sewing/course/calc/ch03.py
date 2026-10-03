"""Chapter 3 (needle-bar slider-crank): numbers used in course/lessons/ch03.json."""
import math

def x(phi, r, l):
    p = math.radians(phi); lam = r / l
    return r * (1 - math.cos(p)) - l * (1 - math.sqrt(1 - (lam * math.sin(p)) ** 2))

def acc(phi, r, l, n):
    """exact acceleration, m/s^2 (r, l in mm)"""
    p = math.radians(phi); lam = r / l; w = 2 * math.pi * n / 60
    S = math.sqrt(1 - (lam * math.sin(p)) ** 2)
    return r / 1000 * w * w * (math.cos(p) - lam * (math.cos(2 * p) + lam ** 2 * math.sin(p) ** 4) / S ** 3)

def vel(phi, r, l, n):
    p = math.radians(phi); lam = r / l; w = 2 * math.pi * n / 60
    S = math.sqrt(1 - (lam * math.sin(p)) ** 2)
    return r / 1000 * w * math.sin(p) * (1 - lam * math.cos(p) / S)

def vmax(r, l, n):
    best = max((abs(vel(f / 100, r, l, n)), f / 100) for f in range(0, 18000))
    return best

def rise_angle(r, l, rise=2.0):
    s = x(180, r, l); f = 180.0
    while s - x(f, r, l) < rise:
        f += 0.001
    return f

def cross(r, l, depth, start, stop):
    """first angle in [start, stop] where x crosses depth"""
    f = start
    step = 0.001 if stop > start else -0.001
    while (x(f, r, l) < depth) if step > 0 else (x(f, r, l) < depth):
        f += step
    return f

def report(name, r, l, n, m=0.12):
    lam = r / l; w = 2 * math.pi * n / 60
    v, fv = vmax(r, l, n)
    at, ab = acc(0, r, l, n), acc(180, r, l, n)
    print(f"[{name}] r={r} l={l} n={n}: lambda={lam:.4f} omega={w:.2f} stroke={2*r:.1f} "
          f"vmax={v:.3f} m/s at {fv:.1f} deg, aTDC={at:.0f} ({at/9.81:.0f} g), aBDC={ab:.0f} ({ab/9.81:.0f} g), "
          f"rise2mm at {rise_angle(r, l):.2f} deg, F_BDC(m={m*1000:.0f} g)={m*abs(ab):.0f} N, F_TDC={m*at:.0f} N")
    return lam, w, v, fv, at, ab

# worked example
report("example", 15.5, 55, 5000)
print("x(90) =", round(x(90, 15.5, 55), 2), "mm")
# needle point 18 mm above plate, fabric 1.5 mm -> point enters at x = 16.5
f = 0.0
while x(f, 15.5, 55) < 16.5: f += 0.01
print("point enters fabric at", round(f, 1), "leaves at", round(360 - f, 1))
# approximate rise formula: h = r/2 (1+lam) delta^2 -> delta for 2 mm
lam = 15.5 / 55
d = math.sqrt(2 * 2 / (15.5 * (1 + lam)))
print("approx delta for 2 mm:", round(math.degrees(d), 1), "-> catch at", round(180 + math.degrees(d), 1))
for lam_ in (0.20, 0.282, 0.40):
    l_ = 15.5 / lam_
    print(f"lambda={lam_}: rise2mm {rise_angle(15.5, l_):.1f}, aBDC {abs(acc(180, 15.5, l_, 5000)):.0f}")
# 6000 r/min
print("F at 6000 r/min:", round(0.12 * abs(acc(180, 15.5, 55, 6000))), "ratio", (6000/5000)**2)
# exercise 3: r=17, l=60, n=5500
report("ex3", 17, 60, 5500)
# exercise 4: l 55 -> 45, stroke unchanged
a55, a45 = rise_angle(15.5, 55), rise_angle(15.5, 45)
print(f"ex4: catch {a55:.2f} -> {a45:.2f}, change {a45-a55:.2f} deg")
# exercise 5: m = 100 g, F <= 500 N -> n max
ab1 = abs(acc(180, 15.5, 55, 1000))     # at 1000 r/min
nmax = 1000 * math.sqrt(500 / (0.1 * ab1))
print("ex5: n max =", round(nmax), "r/min")
# lab tasks
a40 = rise_angle(15.5, 40)
print(f"lab task2: l=40 catch {a40:.1f} (was {a55:.1f}), change {a40-a55:.1f}")
print("lab task3: F ratio 3000->6000 =", (6000/3000)**2)
print("lab task4: m max for 400 N at 5000 =", round(400 / abs(acc(180, 15.5, 55, 5000)) * 1000, 1), "g")
# TDC/BDC ratio approx and exact
print("ratio approx (1-l)/(1+l) =", round((1-lam)/(1+lam), 4), " exact =", round(acc(0,15.5,55,5000)/abs(acc(180,15.5,55,5000)), 4))
# quiz items
print("Q: r=16, l=56, n=4500 -> aBDC approx r w^2 (1+lam):", round(0.016*(2*math.pi*4500/60)**2*(1+16/56)), " exact:", round(abs(acc(180,16,56,4500))))
print("Q: 2nd order / 1st order amplitude = lambda =", round(lam,3))
print("Q: F 1st-order amplitude m r w^2 at 5000:", round(0.12*0.0155*(2*math.pi*5000/60)**2,1), "N; 2nd-order:", round(0.12*0.0155*(2*math.pi*5000/60)**2*lam,1))
# Exam: r=16 l=64 n=5000 m=110g
report("exam", 16, 64, 5000, 0.11)
# Assignment design: m=90 g, n 6000, r 15.5, l 55
print("assign: F at 6000, m=90 g:", round(0.09*abs(acc(180,15.5,55,6000))))
report("assign-b", 15.5, 62, 6000, 0.09)
# problem: shop wants 6000 r/min but bushing limit 800 N; current m 120 g
for m in (0.12, 0.10):
    print("m", m, "F6000", round(m*abs(acc(180,15.5,55,6000))))
print("m max for 800 N at 6000:", round(800/abs(acc(180,15.5,55,6000))*1000,1))
print("n max with m=120 g, F<=800:", round(1000*math.sqrt(800/(0.12*ab1))))
