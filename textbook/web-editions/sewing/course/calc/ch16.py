"""Ch.16 numbers for the course pack (same model as the book / lab embroid.html). Run: python3 ch16.py"""
from math import pi, sqrt, ceil

WIN, CAP, FF = 204, 1100, 50
mass = lambda H: 6 if H == 1 else 10 + 4 * H
amax = lambda H, F: max(0, F - FF) / mass(H)
areq = lambda s_mm, n: 2 * pi * s_mm / 1000 / (WIN / (6 * n)) ** 2
nmax = lambda s_mm, H, F, cap=CAP: min(cap, WIN / 6 * sqrt(amax(H, F) / (2 * pi * s_mm / 1000)))
def eff(H, lam, Th, b=8, S=20000, n=800, ncol=6, tcol=6, nres=600):
    Nb = H * lam * S / 1e4; resew = b * 60 / nres * 2
    Tsew = S * 60 / n; Tb = Nb * (Th + resew); tot = Tsew + Tb + ncol * tcol
    return dict(Nb=Nb, eff=Tsew / tot, pph=H * 3600 / tot, tot=tot)

print("== book checks")
print("areq 3,7 @800", areq(3, 800), areq(7, 800))
print("amax 8,15", amax(8, 800), amax(15, 800))
print("8 heads 3/5/7", [nmax(s, 8, 800, 1e9) for s in (3, 5, 7)])
print("7mm 4/15/20", [nmax(7, H, 800, 1e9) for H in (4, 15, 20)])
print("F for 850 @7mm 8 heads", FF + mass(8) * areq(7, 850))
print("single head: n_max(6 mm) uncapped", nmax(6, 1, 800, 1e9), " stitch length where it reaches 1100:", 1000 * amax(1, 800) / (2 * pi * (1100 * 6 / WIN) ** 2), "mm")
for H in (4, 8, 15, 20):
    print("eff", H, eff(H, 0.5, 40))
Tb_allowed = 1500 / 0.8 - 1536
print("20 heads 80%: lam", Tb_allowed / (20 * 2 * 41.6), " Th", Tb_allowed / 20 - 1.6)
print("ex1", nmax(5, 12, 1000), " ex2 a,F", areq(6, 900), FF + mass(6) * areq(6, 900))
print("ex3", ceil(30 / 12.1), ceil(30 / sqrt(2) / 12.1))
e = eff(12, 0.4, 45, b=0, S=15000, n=750, ncol=5); print("ex4", e)

print("== problem: 8-head jacket back, 7 mm satin")
print("areq @800", areq(7, 800), " amax", amax(8, 800), " nmax", nmax(7, 8, 800), " F@800", FF + mass(8) * areq(7, 800))

print("== quiz")
print("q1 areq 4mm 900", areq(4, 900))
print("q2 nmax 10 heads F900 6mm", nmax(6, 10, 900), " amax", amax(10, 900))
print("q3 records 40 mm", ceil(40 / 12.1))
e = eff(10, 0.3, 30, b=0, ncol=8); print("q8", e)

print("== exam")
print("e1 F 8 heads 6mm 900", FF + mass(8) * areq(6, 900))
print("e2 12 heads", eff(12, 0.5, 40))

print("== assignment")
print("a1 12 heads F1000", [nmax(s, 12, 1000) for s in (3, 5, 7)], " F for 7mm@800", FF + mass(12) * areq(7, 800))
print("a2 45 mm X", ceil(45 / 12.1), " 40 mm @45deg", ceil(40 / sqrt(2) / 12.1), 40 / sqrt(2))
base = eff(12, 0.4, 45, b=8, S=15000, n=750, ncol=5)
print("a3 base", base)
print("a3 Th 20", eff(12, 0.4, 20, b=8, S=15000, n=750, ncol=5))
print("a3 lam 0.2", eff(12, 0.2, 45, b=8, S=15000, n=750, ncol=5))
