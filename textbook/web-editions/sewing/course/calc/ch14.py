"""Ch.14 numbers for the course pack. Run: python3 ch14.py"""
from math import pi, sqrt, radians, ceil

rad = lambda n: n * 2 * pi / 60
rpm = lambda w: w * 60 / (2 * pi)
AMAX = (2.5 + 0.15) / 6e-4          # ch.13 max deceleration, rad/s^2
A60 = 0.6 * AMAX                    # 60 % used for accel/decel in ch.14
CUT = 415                           # deg from start of trimming stitch (0 deg) to cut (55 deg next rev)

def stop_trim(n0, ntr, adec=A60, astop=AMAX):
    """decelerate n0 -> ntr, sew the trimming stitch to the cut at ntr, then stop at astop"""
    t1 = (rad(n0) - rad(ntr)) / adec
    t2 = CUT / (6 * ntr)
    t3 = rad(ntr) / astop
    return t1, t2, t3, t1 + t2 + t3

print("== book checks")
print("A60", A60, " accel 400->4000 s", (rad(4000) - rad(400)) / A60)
for ntr in (200, 300, 500):
    print("stop-trim from 4000 at", ntr, stop_trim(4000, ntr))
print("ex1", stop_trim(3500, 250, 2500, 4400))
bt = lambda t: (211.6 - 10) / (6 * t)
print("backtack 18,20,15,5,4 ms", [round(bt(t), 0) for t in (0.018, 0.020, 0.015, 0.005, 0.004)])
print("stop limit r/min", rpm(sqrt(2 * AMAX * radians(96.7 - 55))), " ex4 (3000)", rpm(sqrt(2 * 3000 * radians(41.7))))
print("entry @300 cmd 290", 290 + 6 * 300 * 0.006, 290 + 6 * 300 * 0.010, " @700", 290 + 6 * 700 * 0.006, 290 + 6 * 700 * 0.010)
print("window limit 6-10, 5-15 ms", 30 / (6 * 0.004), 30 / (6 * 0.010))
print("ex3 cmd range", 300 - 6 * 400 * 0.007, 330 - 6 * 400 * 0.009)
print("tension 0->1 A cN", 20 + 2 * 0.2 * 4 * 1 * 100)

print("== problem: trimming speed 300 vs 500, 3000 trims/day")
a = stop_trim(4000, 300)[3]; b = stop_trim(4000, 500)[3]
print("t300", a, " t500", b, " saving/trim", a - b, " per day min", 3000 * (a - b) / 60)
print("limits at 6-10 ms: window", 30 / (6 * 0.004), " stop", rpm(sqrt(2 * AMAX * radians(41.7))))
print("cmd range @500, 6-10 ms", 300 - 6 * 500 * 0.006, 330 - 6 * 500 * 0.010)

print("== quiz")
print("q1 backtack 12 ms", bt(0.012))
print("q2 latest entry @500 cmd 285 delay 10 ms", 285 + 6 * 500 * 0.010)
print("q3 window limit 7-12 ms", 30 / (6 * 0.005))
print("q4 stop limit 3500 rad/s2", rpm(sqrt(2 * 3500 * radians(41.7))))
print("q9 tension cN", 15 + 2 * 0.25 * 3 * 0.8 * 100)

print("== exam")
print("e1 stop-trim 3000 -> 250 (2500 / 4400)", stop_trim(3000, 250, 2500, 4400))
lo = 300 - 6 * 350 * 0.006; hi = 330 - 6 * 350 * 0.009
print("e2 cmd range @350 6-9 ms", lo, hi, " mid", (lo + hi) / 2)

print("== assignment")
a250 = stop_trim(3500, 250); a400 = stop_trim(3500, 400)
print("a1 t250", a250, " t400", a400, " saving per day (2500 trims) min", 2500 * (a250[3] - a400[3]) / 60)
lo = 300 - 6 * 450 * 0.006; hi = 330 - 6 * 450 * 0.009; print("a2 @450 6-9 ms cmd", lo, hi, (lo + hi) / 2)
lo2 = 300 - 6 * 450 * 0.005; hi2 = 330 - 6 * 450 * 0.013; print("a2 drift 5-13 ms cmd", lo2, hi2, (lo2 + hi2) / 2, " width", 6 * 450 * 0.008)
print("a2 fixed 295 under drift entry", 295 + 6 * 450 * 0.005, 295 + 6 * 450 * 0.013)
print("a3 backtack 16 ms, 5 ms", bt(0.016), bt(0.005))
