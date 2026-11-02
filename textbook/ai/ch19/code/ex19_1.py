"""算例 19.1.1—19.1.4：数值预报的瓶颈与可预报性（19.1 节）。

（1）显式格式确实受 CFL 约束——库朗数过 1 就炸。
（2）**但业务模式用的半拉格朗日格式不受这一条约束**：库朗数 5 照样稳。
（3）所以"分辨率翻倍要多花十几倍算力"只能当量纲分析讲，不能当成本标度律。
（4）混沌：误差指数增长，提高初值精度的回报是**对数的**。
"""
import numpy as np

from _ch19 import (advect_semilagrangian, advect_upwind, cost_factor,
                   doubling_time, useful_lead)
from bookout import out
from geo_facts import CFL, ERA5, IFS

NX, NSTEP = 200, 200
x = np.arange(NX) / NX * 2 * np.pi
u0 = np.exp(-((x - np.pi) ** 2) / 0.08)          # 一个窄峰，往右平流

v = {"n_x": NX, "n_step": NSTEP, "peak0": float(u0.max())}

# ---------- （1）显式格式：CFL 卡死
v["cfl_formula"] = CFL["formula"]
v["cfl_is_quote"] = CFL["is_quote"]
assert not v["cfl_is_quote"], "CFL 的式子是本书按定义写的，不是 NWP 官方文档的引文"
rows = []
for c in (0.5, 0.9, 1.0, 1.1, 1.5):
    peak = float(np.max(np.abs(advect_upwind(u0, c, NSTEP))))
    rows.append((c, peak))
    v[f"up_c{str(c).replace('.', 'p')}"] = peak
v["upwind_rows"] = [(c, f"{p:.3g}") for c, p in rows]
assert v["up_c1p0"] <= 1.001, "库朗数等于 1 时正好不衰减"
assert v["up_c1p5"] > 1e10, "超过 1 就指数放大——这就是 CFL 条件卡住你的样子"
v["blowup_ratio"] = v["up_c1p5"] / v["peak0"]

# ---------- （2）半拉格朗日：不受 CFL 约束
sl = []
for c in (0.5, 1.1, 2.5, 5.0):
    peak = float(np.max(np.abs(advect_semilagrangian(u0, c, NSTEP))))
    sl.append((c, round(peak, 4)))
    v[f"sl_c{str(c).replace('.', 'p')}"] = round(peak, 4)
v["sl_rows"] = sl
assert v["sl_c5p0"] <= 1.001, "库朗数 5 照样有界——它无条件稳定"
v["ecmwf_unconditional"] = CFL["ecmwf_unconditional"]
v["ecmwf_courant_gt1"] = CFL["ecmwf_courant_gt1"]
v["ifs_levels"] = IFS["levels"]
v["counterexample"] = CFL["counterexample_levels"]

# ---------- （3）分辨率翻倍的代价：这是量纲分析
v["cost_full"] = cost_factor()
v["cost_no_levels"] = cost_factor(levels_scale=False)
v["cost_no_cfl"] = cost_factor(cfl_bound=False)
v["cost_neither"] = cost_factor(False, False)
v["cost_is_derivation"] = CFL["scaling_is_derivation"]
assert v["cost_full"] == 16 and v["cost_neither"] == 4, \
    "两个前提都不成立时只剩 4 倍——所以 16 这个数依赖前提，不是标度律"
v["era5_timestep_min"] = ERA5["native_levels"] and IFS["era5_timestep_min_hres"]
v["era5_res_km"] = ERA5["native_res_km"]
v["ifs_wallclock_known"] = IFS["forecast_wallclock"] is not None
assert not v["ifs_wallclock_known"], "'一次业务预报跑多久'官方不公布，正文写'未公布'"

# ---------- （4）混沌与可预报性
DT = 0.01
v["dt"] = DT
v["t_double"] = round(doubling_time(DT, 900, 1e-3, seed=0), 3)
assert 0.4 < v["t_double"] < 1.2, "洛伦兹系统的误差翻倍时间在这个量级"

lead = []
for eps, tag in ((1e-2, "e2"), (1e-3, "e3"), (1e-4, "e4"), (1e-5, "e5")):
    t = round(useful_lead(DT, 3000, eps, 2.0, seed=1), 2)
    lead.append((eps, t))
    v[f"lead_{tag}"] = t
v["lead_rows"] = lead
v["lead_gain_per_decade"] = round((v["lead_e5"] - v["lead_e2"]) / 3, 2)
v["theory_gain"] = round(v["t_double"] * np.log2(10), 2)
assert v["lead_e5"] > v["lead_e2"], "初值越准，能信的时间越长"
assert abs(v["lead_gain_per_decade"] - v["theory_gain"]) < 1.0, \
    "初值精度每提高十倍，只多买回约 log2(10) 个翻倍时间——与解析一致"
assert v["lead_e5"] < 4 * v["lead_e2"], \
    "初值精度提高一千倍，能信的时间连三倍都不到——回报是**对数**的"

out(**v)
