"""算例 1.4.1 的约束计算（第 1 章 1.4、1.5 节共用）：SH-301 外伸段直径的强度下限、联轴器孔径范围、轴承与轴肩的上限、标准直径。"""
import csv
import math

import numpy as np

import _ch1 as H
import mdstd

F, C = H.F, H.C
T_R = C.T_RATED                                       # N·m，额定输出转矩（已含工况系数）
from sim.engine import torque_record                 # noqa: E402  数字工厂仿真车间：跑合试验台的转矩记录
rec = torque_record("WQR-105-00001", "WO-TS-1", "WQR-105")
K_PEAK = max(rec["samples_nm"]) / rec["rated_nm"]     # 起动冲击倍数
T_PEAK = K_PEAK * T_R
mat = mdstd.material("45-QT")
tau_s = mat["sigma_s"] / math.sqrt(3)                 # 剪切屈服强度（冯·米塞斯）
S_REQ = 1.5                                           # 静强度要求的安全系数（1.5 节）


def WT_key(d):
    """带一个平键槽的抗扭截面系数（常用近似式），键槽尺寸按 GB/T 1095 随 d 取"""
    k = mdstd.key_for(d)
    b, t = k["b"], k["t"]
    return math.pi * d ** 3 / 16 - b * t * (d - t) ** 2 / (2 * d)


ds = np.arange(20.0, 46.0, 0.05)
S = np.array([tau_s / (T_PEAK * 1e3 / WT_key(d)) for d in ds])
d_strength = float(ds[np.argmax(S >= S_REQ)])

# ---- 联轴器：零件库 A-CPL-JAW（梅花形弹性联轴器 LM），按公称转矩选型号，它的孔径范围就是一条约束
with (H.ROOT / "library" / "catalog" / "A" / "A-CPL-JAW" / "specs.csv").open(encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
cpl = next(r for r in rows if float(r["Tn_a_Nm"]) >= T_R)
cpl_lo, cpl_hi = float(cpl["d_min_mm"]), float(cpl["d_max_mm"])

# ---- 右轴承 6207：内径 35；外伸段与轴承位之间要有定位轴肩，h ≥ 0.07d（33.2 节）→ d + 2·0.07d ≤ 35
brg = mdstd.bearing("6207")
d_geom = brg["d"] / (1 + 2 * 0.07)

# ---- 标准直径：GB/T 2822 的 R40 系列（20–45 mm）；圆柱形轴伸另有 GB/T 1569（28、30、32、35……）
R40 = [20, 21.2, 22.4, 23.6, 25, 26.5, 28, 30, 31.5, 33.5, 35.5, 37.5, 40, 42.5, 45]
lo, hi = max(d_strength, cpl_lo), min(d_geom, cpl_hi)
choices = [x for x in R40 if lo <= x <= hi]
d_pick = choices[0] if choices else None
S_pick = tau_s / (T_PEAK * 1e3 / WT_key(d_pick)) if d_pick else None
m_ext = math.pi / 4 * d_pick ** 2 * 68 * mat["density"] * 1e-6 if d_pick else None   # 外伸段长 68 mm（33.2 节 B 版）

