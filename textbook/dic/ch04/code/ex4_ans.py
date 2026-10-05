"""第 4 章部分习题答案中的数值（04-99.md“部分习题答案与提示”引用）。与正文程序用同一个模型。"""
import math

import numpy as np

from bookout import out
from mos import (P, VDD, WIRES, Wmin, cin, gamma_self, noise_margins, r_ratio, repeater_delay, req_n, req_p, wire_c,
                 wire_cc, wire_r)
from _rc import Tree, t50

r = r_ratio()
R0 = (req_n(Wmin) + req_p(r * Wmin)) / 2
C0 = cin(Wmin, r * Wmin)
gam = gamma_self()

# 4.1.1
out(a411_R=wire_r("met2", 0.3) * 200, a411_C=wire_c("met2", 0.3) * 200 * 1e15)
# 4.1.3
c1 = wire_c("met1", 0.14)
out(a413_x1=wire_c("met1", 0.14, 0.14) / c1, a413_x3=wire_c("met1", 0.14, 0.42) / c1)
# 4.2.2：最小反相器经 2 mm met2 驱动一个参考反相器
Rw, Cw = wire_r("met2", 0.14) * 2000, wire_c("met2", 0.14) * 2000
drv = 0.69 * R0 * (gam * C0 + Cw + C0)
wr = 0.38 * Rw * Cw + 0.69 * Rw * C0
out(a422_drv=drv * 1e12, a422_wire=wr * 1e12, a422_tot=(drv + wr) * 1e12)

# 4.2.4：两条支线都 1.0 mm
q = P["problems"]["p42"]
size = q["driver_size"]
lay, w = q["layer"], q["w_um"]
seg = lambda L: (wire_r(lay, w) * L, wire_c(lay, w) * L)  # noqa: E731
tr = Tree(R0 / size, gam * C0 * size)
j = tr.wire(0, *seg(q["trunk_um"]), 40)
a = tr.wire(j, *seg(1000), 40); tr.C[a] += q["leaf_load_units"] * C0
b = tr.wire(j, *seg(1000), 40); tr.C[b] += q["leaf_load_units"] * C0
el = tr.elmore()
out(a424_el=el[a] * 1e12, a424_skew=(el[b] - el[a]) * 1e12)

# 4.2.5：均匀 RC 线末端的 10 %～90 % 上升时间（以 RC 为单位）
t = Tree(1e-3, 0.0)
end = t.wire(0, 1.0, 1.0, 60)
ts, V = t.step(1.0, 4.0, 8000)
v = V[:, end]
t10 = ts[np.argmax(v >= 0.1)]; t90 = ts[np.argmax(v >= 0.9)]
out(a425_rise=t90 - t10)

# 4.3.2：最优段长
for l, ww in (("met1", 0.14), ("met3", 0.3)):
    rw, cw = wire_r(l, ww), wire_c(l, ww)
    seg_opt = math.sqrt(0.69 * R0 * C0 * (1 + gam) / (0.38 * rw * cw))
    out(**{f"a432_{l}_mm": seg_opt / 1000})

# 4.3.4：中继器与导线的功耗（3 段、26 倍，100 MHz）
f = 100e6
p_rep = 3 * 26 * C0 * VDD ** 2 * f
p_wire = wire_c("met1", 0.14) * 3000 * VDD ** 2 * f
out(a434_rep_uw=p_rep * 1e6, a434_wire_uw=p_wire * 1e6)

# 4.4.1、4.4.2、4.4.3
qq = WIRES["met2"]
Lw = P["problems"]["p44"]["len_um"]
Cc = wire_cc("met2", 0.14) * Lw
Cg = (qq["Carea"] * 0.14 + 2 * qq["Cfringe"]) * 1e-18 * Lw + C0
out(a441=VDD * Cc / (Cc + Cg + 3 * C0))
tau = req_n(Wmin) * (Cc + Cg)
out(a442=VDD * Cc / (Cc + Cg) * tau / 1e-9 * (1 - math.exp(-1e-9 / tau)))
nm = noise_margins(Wmin, r * Wmin)
NM = min(nm["NML"], nm["NMH"])
s = 0.14
while True:
    cc = wire_cc("met2", s) * Lw
    tt = req_n(2 * Wmin) * (cc + Cg)
    pk = VDD * cc / (cc + Cg) * tt / 100e-12 * (1 - math.exp(-100e-12 / tt))
    if pk < NM:
        break
    s += 0.01
out(a443_s=s)

# 4.5.1、4.5.2、4.5.4
v = 3e8 / math.sqrt(3.3)
td2 = 0.02 / v
out(a451_cm_ns=v * 1e-7, a451_2td_ps=2 * td2 * 1e12)
F = P["problems"]["p14"]["CL"] / C0
Rout = R0 / F ** (5 / 6)
out(a452_v=VDD * 50 / (50 + Rout), a452_p_mw=(VDD * 50 / (50 + Rout)) ** 2 / 50 * 1e3)
Lp = 0.5e-9 / 1e-3
for l in ("met1", "met3", "met5"):
    ww = WIRES[l]["wmin"]
    out(**{f"a454_{l}_R": wire_r(l, ww) * 3000, f"a454_{l}_2Z": 2 * math.sqrt(Lp / (wire_c(l, ww) * 1e6))})

# 4.2.3：met1 上导线项等于驱动项的线长（步长 100 μm 中最接近的），驱动器 20 倍与 40 倍
def cross(size):
    best = None
    for L in range(100, 4001, 100):
        Rd, Cs = R0 / size, gam * C0 * size
        Rw_, Cw_ = wire_r("met1", 0.14) * L, wire_c("met1", 0.14) * L
        dd = 0.69 * Rd * (Cs + Cw_ + 20 * C0)
        ww = 0.38 * Rw_ * Cw_ + 0.69 * Rw_ * 20 * C0
        if best is None or abs(dd - ww) < best[0]:
            best = (abs(dd - ww), L)
    return best[1]


out(a423_20=cross(20), a423_40=cross(40))
