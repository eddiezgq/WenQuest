"""Chapter 2 (how a stitch is formed): numbers used in course/lessons/ch02.json.
Needle-bar motion = Chapter 3 worked example (r = 15.5 mm, l = 55 mm).
The 'catch window' reproduces the schematic loop model of lab 2-1 (lockstitch.html):
loop size = exp(-((rise-2.2)/1.0)^2), the loop is caught when size >= 0.5."""
import math
R, L = 15.5, 55.0
lam = R / L
def x(phi):
    p = math.radians(phi)
    return R * (1 - math.cos(p)) - L * (1 - math.sqrt(1 - (lam * math.sin(p)) ** 2))
def rise(phi):
    return 2 * R - x(phi) if phi > 180 else 0.0
def caught(delta):
    return math.exp(-((rise(206 + delta) - 2.2) / 1.0) ** 2) >= 0.5

ok = [d for d in range(-30, 31) if caught(d)]
print("lab 2-1: no skipped stitch for delta =", ok[0], "...", ok[-1], "deg -> window", ok[-1] - ok[0], "deg (integer steps)",
      "i.e. hook angle", 206 + ok[0], "-", 206 + ok[-1])
for d in (-14, -10, -6, 0, 6, 10, 14, 20):
    print(f"  delta={d:+d}: catch at {206+d} deg, rise {rise(206+d):.2f} mm, caught={caught(d)}")
# exact rise at a few angles
for f in (196, 206, 216, 226):
    print(f"rise at {f}: {rise(f):.2f} mm")
# needle in fabric (point 18 mm above plate at TDC, fabric 1.5 mm): x = 16.5
f = 0.0
while x(f) < 16.5: f += 0.01
print("needle in fabric", round(f, 1), "-", round(360 - f, 1))
# speeds and timing
for n in (4000, 5000):
    T = 60 / n * 1000
    print(f"n={n}: one stitch {T:.1f} ms, hook speed {2*n} r/min, {360/T:.0f} deg/ms, "
          f"hook turns per stitch 2, 10 deg = {10/360*T:.3f} ms")
# fabric speed: s = 3 mm at 5000 st/min
print("fabric speed s=3 mm at 5000:", 3 * 5000 / 1000, "m/min;", 3*5000/1000/60*1000, "mm/s")
print("s=2.5 mm, 4000 st/min:", 2.5*4000/1000, "m/min")
# hook angle at catch (hook turns twice): 2*206
print("hook angle at main-shaft 206 deg:", 2*206 % 360, "(=", 2*206, ")")
# feed window: needle out of fabric 258.3 -> 360+101.7
print("needle above fabric window:", round(360 - 258.3 + 101.7, 1), "deg")
# time from BDC to catch at 5000
print("time BDC->catch at 5000:", round(26.1/360*12, 3), "ms")
# seam: 50 cm seam s=2.5 mm stitches, time at 4000
print("50 cm, s=2.5:", 500/2.5, "stitches;", 500/2.5/4000*60, "s at 4000 st/min")
# continuous edges of the lab-2-1 window: rise between 2.2 -/+ sqrt(ln 2)
lo, hi = 2.2 - math.sqrt(math.log(2)), 2.2 + math.sqrt(math.log(2))
def ang(h):
    f = 180.0
    while rise(f + 1e-9) < h: f += 0.001
    return f
print(f"window edges: rise {lo:.2f}-{hi:.2f} mm -> {ang(lo):.1f}-{ang(hi):.1f} deg, width {ang(hi)-ang(lo):.1f} deg")
# assignment 2, task 1: hook at 198 deg, 4000 and 6000 r/min
print(f"assignment: rise at 198 = {rise(198):.2f} mm, caught={caught(198-206)}; 8 deg = {8/360*60/4000*1000:.3f} ms at 4000, {8/360*60/6000*1000:.3f} ms at 6000")
# exam: 12 deg at 4000
print("exam: 12 deg at 4000 =", round(12/360*60/4000*1000, 3), "ms")
