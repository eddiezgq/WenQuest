"""32.2 节的计算：谐波减速器。

(1) 减速比：刚轮比柔轮多 2 个齿，刚轮固定、柔轮输出时 i = z_柔 / (z_刚 − z_柔)；WQ-CR5 用的减速比 100 → 柔轮 200 齿、刚轮 202 齿。
(2) 算例 32.2.1：WQ-CR5 在负载跑合台的标准动作（5 kg，第 29 章）里，每个关节的谐波减速器：峰值力矩、平均负载力矩 T_av、
    平均输入转速 n_av、L10 寿命（问渠“运动与动力分析”的同一段程序 twin/robot.py 的 joint_life），
    与零件库 D-RDC-HD-CSF 的允许值比：启停峰值、平均负载力矩、平均与最高输入转速（脂润滑）。
(3) 算例 32.2.2：寿命对负载、动作快慢有多敏感：J2、J3 在 0、5、6 kg，标准与“快”（加速度 1.5 倍）时的寿命。
"""
import numpy as np

from _ch32 import joint_life, library, runin_series, wqcr5
from bookout import out

W = wqcr5()
life, L_RATED, N_RATED = joint_life()
# ---------------------------------------------------------------- (1) 减速比
i = W.GEAR_RATIO
z_f = 2 * i
z_c = z_f + 2
assert z_f / (z_c - z_f) == i
out(i=i, z_f=z_f, z_c=z_c, L_rated=L_RATED, n_rated=N_RATED)

# ---------------------------------------------------------------- (2) 标准动作里每个关节的寿命
CSF = {int(r["size_code"]): r for r in library("D-RDC-HD-CSF") if r["ratio"] == "100"}
SIZE = {"L": 32, "M": 25, "S": 17}
t, tau, qd = runin_series(5.0)
HOURS_PER_YEAR = 16 * 250                                     # 两班、一年 250 个工作日
rows = []
for j in range(6):
    s = W.JOINT_MODULE[j]
    c = CSF[SIZE[s]]
    rated = float(c["T_rated_Nm"])
    assert rated == W.MODULES[s]["gear"][1]                     # 零件库与机器人厂原件一致
    r = life(t, tau[:, j], qd[:, j], rated, i)
    n_max = float(np.max(np.abs(qd[:, j]))) * i * 60 / (2 * np.pi)
    pk = float(np.max(np.abs(tau[:, j])))
    rows.append(dict(size=SIZE[s], rated=rated, peak=pk, T_av=r["T_av"], n_av=r["n_av_in"], n_max=n_max, L=r["L10_h"],
                     ok_pk=pk <= float(c["T_repeat_Nm"]), ok_av=r["T_av"] <= float(c["T_avg_Nm"]),
                     ok_nav=r["n_av_in"] <= float(c["n_avg_grease_rpm"]), ok_nmax=n_max <= float(c["n_max_grease_rpm"]),
                     T_rep=float(c["T_repeat_Nm"]), T_avg_lim=float(c["T_avg_Nm"]), n_avg_lim=float(c["n_avg_grease_rpm"]),
                     n_max_lim=float(c["n_max_grease_rpm"])))
for j, r in enumerate(rows):
    out(**{f"j{j + 1}_{k}": v for k, v in r.items() if not k.startswith("ok")})
assert all(r["ok_pk"] and r["ok_av"] and r["ok_nav"] and r["ok_nmax"] for r in rows)
short = min(range(6), key=lambda j: rows[j]["L"])
assert short in (1, 2)                                          # 最先到寿命的是 J2 或 J3
out(cycle=float(t[-1]), short=short + 1, L_short=rows[short]["L"], yrs_short=rows[short]["L"] / HOURS_PER_YEAR, hpy=HOURS_PER_YEAR)
# 手算 J2：L10 = 7000 × (T_r / T_av)³ × (2000 / n_av)
r2 = rows[1]
out(f_T=(r2["rated"] / r2["T_av"]) ** 3, f_n=N_RATED / r2["n_av"])

# ---------------------------------------------------------------- (3) 负载、快慢
res = {}
for mp in (0.0, 5.0, 6.0):
    for tag, k in (("std", 1.0), ("fast", 1.5)):
        tt, ta, qq = runin_series(mp, accel_scale=k)
        for j in (1, 2):
            s = W.JOINT_MODULE[j]
            res[(mp, tag, j)] = life(tt, ta[:, j], qq[:, j], W.MODULES[s]["gear"][1], i)["L10_h"]
for (mp, tag, j), v in res.items():
    out(**{f"L_{int(mp)}_{tag}_{j + 1}": v})
assert res[(6.0, "fast", 2)] < res[(5.0, "std", 2)] < res[(0.0, "std", 2)]
out(drop6=(1 - res[(6.0, "std", 2)] / res[(5.0, "std", 2)]) * 100, drop_fast=(1 - res[(5.0, "fast", 2)] / res[(5.0, "std", 2)]) * 100,
    ratio_6=(res[(6.0, "std", 2)] / res[(5.0, "std", 2)]))

# ---------------------------------------------------------------- 图 32.2.2
from bookout import COLORS as C, T, figure, style  # noqa: E402
plt = style()
fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.0), gridspec_kw={"width_ratios": [1.3, 1.0]})
ax = axs[0]
for j, col in ((1, C["x"]), (2, C["z"])):
    ax.plot(t, tau[:, j], color=col, lw=1.4, label=f"J{j + 1}")
    ax.axhline(rows[j]["rated"], color=col, lw=0.8, ls=":")
    ax.axhline(-rows[j]["rated"], color=col, lw=0.8, ls=":")
ax.text(0.05, rows[1]["rated"] + 4, T("32 号额定 137 N·m", "size 32 rated 137 N·m"), fontsize=8, color=C["x"])
ax.text(0.05, rows[2]["rated"] - 12, T("25 号额定 67 N·m", "size 25 rated 67 N·m"), fontsize=8, color=C["z"])
ax.set_xlabel(T("时间 / s（负载跑合台的标准动作，5 kg）", "time / s (run-in motion, 5 kg)"))
ax.set_ylabel(T("关节力矩 / (N·m)", "joint torque / (N·m)"))
ax.legend(fontsize=8, frameon=False, loc="lower right")
ax.set_title(T("(a) J2、J3 的力矩与减速器的额定力矩", "(a) J2 and J3 torque against the gear ratings"), fontsize=11)
ax = axs[1]
ax.bar(np.arange(6), [r["L"] for r in rows], color=[C["x"], C["x"], C["z"], C["y"], C["y"], C["y"]])
ax.set_yscale("log")
ax.axhline(L_RATED, color=C["ink"], lw=0.8, ls="--")
ax.text(3.2, L_RATED * 1.4, T("额定寿命 7000 h", "rated life 7000 h"), fontsize=8)
ax.set_xticks(np.arange(6), [f"J{j + 1}\n{rows[j]['size']}" for j in range(6)])
ax.set_ylabel(T("L10 寿命 / h（一直跑这个动作）", "L10 life / h (running this motion)"))
ax.set_title(T("(b) 每个关节的谐波减速器寿命", "(b) gear life of each joint"), fontsize=11)
fig.tight_layout()
figure(fig, "fig32_2_2")
