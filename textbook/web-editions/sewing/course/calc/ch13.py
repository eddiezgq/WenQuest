"""Ch.13 numbers for the course pack (problem, quiz, exam). Run: python3 ch13.py"""
from math import pi, sqrt, degrees

rpm = lambda w: w * 60 / (2 * pi)
rad = lambda n: n * 2 * pi / 60
deg_per = lambda n, t: 6 * n * t          # shaft degrees turned in t seconds at n r/min

print("== book checks")
J, Kv, Kp, Tf, Tmax = 6e-4, 0.2, 200, 0.15, 2.5
print("velocity-loop bandwidth Kv/J", Kv / J)
print("min accel time to 5000", J * rad(5000) / Tmax)
print("max decel (Tmax+Tf)/J", (Tmax + Tf) / J)
print("static error without I (deg)", degrees(Tf / (Kv * Kp)))
print("1024-line x4 resolution", 360 / 4096, " M-method error r/min", 60 / (4096 * 0.001))
print("M rel err @200", 60 / (4096 * 0.001) / 200, " T rel err @200", 4096 * 200 / 60 / 1e7)
print("crossover r/min", sqrt(60 / (4096 * 0.001) * 1e7 * 60 / 4096))
E = 0.5 * J * rad(5000) ** 2
print("KE @5000", E, " V2", sqrt(310 ** 2 + 2 * 0.7 * E / 470e-6))
Eal = 0.5 * 470e-6 * (400 ** 2 - 310 ** 2) / 0.7
print("brake needed above r/min", rpm(sqrt(2 * Eal / J)))
print("solenoid degrees @400: pull 6.9", deg_per(400, 6.9e-3), "rel diode 12.9", deg_per(400, 12.9e-3), "zener 5.1", deg_per(400, 5.1e-3))
print("max trim speed 20deg / 6.9 ms", 20 / (6 * 6.9e-3))

print("== problem (trimming solenoid at 600 r/min)")
for name, t in (("pull", 6.9e-3), ("diode", 12.9e-3), ("zener", 5.1e-3)):
    print(name, "deg @600", deg_per(600, t))
print("n_max with zener", 20 / (6 * 6.9e-3), " transistor V", 24 + 48)

print("== quiz")
print("q2 2048-line x4 resolution deg", 360 / (2048 * 4))
print("q3 static error deg", degrees(0.12 / (0.3 * 150)))
print("q4 pull 8 ms @500 deg", deg_per(500, 8e-3))
J8 = 5e-4; E8 = 0.5 * J8 * rad(4500) ** 2
print("q8 V2", sqrt(310 ** 2 + 2 * 0.7 * E8 / 470e-6), " KE", E8)

print("== exam")
print("e1 n_max 25deg, pull 7.5 rel 9 ms", 25 / (6 * 9e-3))
print("e2 M-method rel err @300 %", 100 * 60 / (4096 * 0.001) / 300)
Eal2 = 0.5 * 680e-6 * (380 ** 2 - 310 ** 2) / 0.7
print("e5 brake needed above r/min", rpm(sqrt(2 * Eal2 / 6e-4)), " allowed KE", Eal2)

print("== assignment")
cpr = 2500 * 4
dM = 60 / (cpr * 0.001)
for n in (150, 3000):
    ticks = 1e7 / (cpr * n / 60)
    print("a1 n", n, " M err r/min", dM, " M rel %", 100 * dM / n, " T ticks", ticks, " T rel %", 100 / ticks)
print("a2 deg @450: pull", deg_per(450, 6.9e-3), " diode", deg_per(450, 12.9e-3), " zener", deg_per(450, 5.1e-3),
      " Vce", 24 + 48, " zener energy J", 0.5 * 0.08 * 1 ** 2)
Ea = 0.5 * 8e-4 * rad(4500) ** 2
print("a3 KE", Ea, " V2", sqrt(310 ** 2 + 2 * 0.7 * Ea / 680e-6))
Eal3 = 0.5 * 680e-6 * (400 ** 2 - 310 ** 2) / 0.7
print("a3 brake needed above r/min", rpm(sqrt(2 * Eal3 / 8e-4)))
