"""6.1 节：加法器。

算例 6.1.1  逻辑努力估算 n 位行波进位加法器的延时：每一位的进位门（与或非 / 或与非交替）驱动下一位的进位门和本位求和的异或门。
算例 6.1.2  电机控制芯片的高速版本：32 位累加器（速度积分），时钟 400 MHz。扣除第 3 章触发器的 tcq 与 tsu 后加法器的时间预算；
            五种结构按 SKY130 标准单元综合的延时与面积，哪些满足预算，满足预算的结构里面积最小的是哪个。
图 6.1.1    五种加法器的延时随位宽的变化（SKY130 综合）。
图 6.1.2    16 位与 32 位加法器的面积—延时（SKY130 综合），虚线为算例 6.1.2 的时间预算。
"""
import numpy as np

from bookout import T, figure, out, style
from mos import P, ff_timing, fo4_tp, gamma_self, r_ratio, tau
import _draw as d

r = r_ratio()
g = gamma_self()
tu = tau()
f4 = fo4_tp(r)
S = P["arith_syn"]
KINDS = [("rca", T("行波进位", "ripple carry")), ("cla", T("超前进位（4 位一组）", "carry lookahead (4-bit groups)")),
         ("csel", T("进位选择（4 位一组）", "carry select (4-bit blocks)")), ("bk", "Brent–Kung"), ("ks", "Kogge–Stone")]

# ---------------------------------------------------------------- 算例 6.1.1 逻辑努力
g_c = (2 + 2 * r) / (1 + r)                 # 与或非门（AOI21）的“与”输入（进位与 p 相与）：NMOS 串联宽 2Wn，PMOS 宽 2rWn
p_aoi = g * (3 + 2 * r) / (1 + r)           # 与或非门输出节点上的漏极：NMOS 3Wn、PMOS 2rWn
d_bit = (g_c + 4) + p_aoi                   # 驱动下一位进位门（g_c）和本位异或门（g = 4）
d_pg = 4 + 4 * g                            # 产生 p = a ⊕ b 的异或门（驱动进位门与求和门，约 4 个单位）
d_sum = 1 + 4 * g                           # 最高位求和的异或门驱动寄存器输入
for n in (8, 16, 32):
    D = d_pg + (n - 1) * d_bit + d_sum
    out(**{f"rca{n}_tau": D, f"rca{n}_ps": D * tu * 1e12, f"rca{n}_syn": S[f"add_rca_{n}"]["delay"],
           f"rca{n}_ratio": S[f"add_rca_{n}"]["delay"] / (D * tu * 1e12)})
out(g_c=g_c, p_aoi=p_aoi, d_bit=d_bit, d_bit_ps=d_bit * tu * 1e12, d_pg=d_pg, d_sum=d_sum, tau_ps=tu * 1e12)
# 前缀加法器的手算：log2 n 级，每级的进位门驱动两个进位门
for n in (8, 16, 32):
    lv = int(np.log2(n))
    D = d_pg + lv * (2 * g_c + p_aoi) + d_sum
    out(**{f"ks{n}_tau": D, f"ks{n}_ps": D * tu * 1e12, f"ks{n}_lv": lv})

# ---------------------------------------------------------------- 算例 6.1.2
q = P["problems"]["p61"]
ff = ff_timing()
T_ = 1 / (q["f_MHz"] * 1e6)
budget = T_ - ff["tcq"] - ff["tsu"]
n = q["bits"]
ok = [(k, S[f"tgt_add_{k}_{n}"]) for k, _ in KINDS if S[f"tgt_add_{k}_{n}"]["delay"] * 1e-12 <= budget]
best = min(ok, key=lambda x: x[1]["area"])
for k, _ in KINDS:
    t = S[f"tgt_add_{k}_{n}"]
    out(**{f"t_{k}_d": t["delay"], f"t_{k}_ns": t["delay"] / 1e3, f"t_{k}_a": t["area"]})
out(t_ks_vs_bk=S["tgt_add_ks_32"]["area"] / S["tgt_add_bk_32"]["area"], target_ps=S["tgt_add_bk_32"]["target"])
out(bits=n, f_MHz=q["f_MHz"], T_ns=T_ * 1e9, budget_ns=budget * 1e9, n_ok=len(ok), best=best[0], best_area=best[1]["area"],
    best_delay=best[1]["delay"], tcq_ps=ff["tcq"] * 1e12, tsu_ps=ff["tsu"] * 1e12)
for k, _ in KINDS:
    for w in (8, 16, 32):
        s = S[f"add_{k}_{w}"]
        out(**{f"{k}{w}_d": s["delay"], f"{k}{w}_a": s["area"], f"{k}{w}_ns": s["delay"] / 1e3, f"{k}{w}_am": s["area_min"], f"{k}{w}_dm": s["delay_amin"]})
    out(**{f"{k}_x": S[f"add_{k}_32"]["delay"] / S[f"add_{k}_16"]["delay"], f"{k}_ax": S[f"add_{k}_32"]["area"] / S[f"add_{k}_16"]["area"],
           f"{k}32_fo4": S[f"add_{k}_32"]["delay"] * 1e-12 / f4})
out(csel_vs_rca16=S["add_csel_16"]["area"] / S["add_rca_16"]["area"], ks_x_pct=(S["add_ks_32"]["delay"] / S["add_ks_16"]["delay"] - 1) * 100, ks_vs_rca32=S["add_rca_32"]["delay"] / S["add_ks_32"]["delay"], ks_area_vs_bk32=S["add_ks_32"]["area"] / S["add_bk_32"]["area"])

# ---------------------------------------------------------------- 图 6.1.1
plt = style()
cols = {"rca": d.PMOS, "cla": d.LOAD, "csel": d.MUTED, "bk": d.MEAN, "ks": d.NMOS}
fig, ax = plt.subplots(figsize=(5.8, 3.4))
ws = [8, 16, 32]
for k, name in KINDS:
    ax.plot(ws, [S[f"add_{k}_{w}"]["delay"] / 1e3 for w in ws], "o-", color=cols[k], lw=1.8, label=name)
ax.set_xscale("log", base=2); ax.set_xticks(ws, [str(w) for w in ws])
ax.set_xlabel(T("位宽 n", "width n")); ax.set_ylabel(T("延时 / ns", "delay / ns"))
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
d.spines(ax)
figure(fig, "fig6_1_1")

# ---------------------------------------------------------------- 图 6.1.2
SHORT = {"rca": T("行波", "RCA"), "cla": T("超前", "CLA"), "csel": T("选择", "CSEL"), "bk": "BK", "ks": "KS"}
fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.4))
for axx, w in zip(axs, (16, 32)):
    for k, name in KINDS:
        s = S[f"add_{k}_{w}"]
        axx.plot(s["delay"] / 1e3, s["area"], "o", color=cols[k], ms=8)
        axx.annotate(SHORT[k], (s["delay"] / 1e3, s["area"]), textcoords="offset points", xytext=(6, 4), fontsize=8.5, color=cols[k])
    if w == n:
        axx.axvline(budget * 1e9, color=d.INK, lw=0.9, ls="--")
        axx.text(budget * 1e9, axx.get_ylim()[1] * 0.98, T(" 预算", " budget"), fontsize=8.5, va="top")
    axx.set_title(T(f"{w} 位", f"{w} bits"), fontsize=10)
    axx.set_xlabel(T("延时 / ns", "delay / ns")); axx.set_ylabel(T("面积 / μm²", "area / μm²"))
    d.spines(axx)
figure(fig, "fig6_1_2")
