"""2.2 节：门的尺寸——等效反相器与最坏情况。

算例 2.2.1  按“等效反相器”给二、三输入与非门和或非门定尺寸：每个管子多宽，每个输入的输入电容是参考反相器的几倍。
算例 2.2.2  关节使能的与或非门 EN（图 2.1.2）驱动 6 路 PWM 门控的与非门输入：两种尺寸（全部取最小宽度、按等效反相器）
            最坏情况下的下降延时。
图 2.2.1    串联的管子：一个最小 NMOS、两个串联、两个串联且各加宽一倍，给同一负载放电的波形。
图 2.2.2    手算模型与 SKY130 仿真的逻辑努力。
"""
import numpy as np

from bookout import T, figure, out, style
from mos import Cg, P, Wmin, cin, gamma_self, gate_widths, le_g, le_p, r_ratio, req_n, req_p, tau
import _draw as d

r = r_ratio()
Cinv = cin(Wmin, r * Wmin)
out(r=r, Cinv_ff=Cinv * 1e15, tau_ps=tau() * 1e12, gamma=gamma_self())

# 算例 2.2.1：尺寸与输入电容
for kind, n in (("nand", 2), ("nand", 3), ("nor", 2), ("nor", 3)):
    wn, wp = gate_widths(kind, n)
    cin_one = (wn + wp) * Cg
    key = f"{kind}{n}"
    out(**{f"{key}_wn": wn, f"{key}_wp": wp, f"{key}_cin": cin_one / Cinv, f"{key}_g": le_g(kind, n),
           f"{key}_area": n * (wn + wp) / (Wmin * (1 + r))})
sim = P["gates_sim"]["gates"]
for key in ("nand2", "nand3", "nor2", "nor3"):
    out(**{f"{key}_gA": sim[key + "_A"]["g"], f"{key}_gB": sim[key + "_B"]["g"],
           f"{key}_pA": sim[key + "_A"]["p"], f"{key}_pB": sim[key + "_B"]["p"]})
out(p_inv_sim=P["gates_sim"]["p_inv"], nand2_gerr=(le_g("nand", 2) / sim["nand2_A"]["g"] - 1) * 100,
    nor2_gerr=(le_g("nor", 2) / sim["nor2_A"]["g"] - 1) * 100)

# 算例 2.2.2：与或非门 EN = ¬(A + B·C) 驱动 6 个与非门输入
# 等效反相器尺寸：下拉 A 一个管（Wmin），B、C 串联（各 2Wmin）；上拉 A 与 (B‖C) 串联（各 2r·Wmin）
load = 6 * cin(*gate_widths("nand", 2))
Wa_n, Wbc_n, Wp_ = Wmin, 2 * Wmin, 2 * r * Wmin
c_self_eq = (Wa_n + Wbc_n + 2 * Wp_) * P["Cd"]       # 输出节点：A、B 的 NMOS 漏极，B、C 的 PMOS 漏极
R_down_eq = req_n(Wbc_n) * 2                          # 最坏：A = 0，经 B、C 两个串联管放电
t_eq = 0.69 * R_down_eq * (c_self_eq + load)
# 全部最小宽度：下拉串联两个最小管，上拉串联两个最小 PMOS
c_self_min = 4 * Wmin * P["Cd"]                     # 同样四个漏极，都取最小宽度
R_down_min = req_n(Wmin) * 2
t_min = 0.69 * R_down_min * (c_self_min + load)
R_up_min = req_p(Wmin) * 2
t_min_up = 0.69 * R_up_min * (c_self_min + load)
t_eq_up = 0.69 * req_p(Wp_) * 2 * (c_self_eq + load)
g_a = (Wa_n + Wp_) * Cg / Cinv
g_bc = (Wbc_n + Wp_) * Cg / Cinv
out(load_ff=load * 1e15, h_aoi=load / ((Wbc_n + Wp_) * Cg), t_eq_ps=t_eq * 1e12, t_eq_up_ps=t_eq_up * 1e12,
    t_min_ps=t_min * 1e12, t_min_up_ps=t_min_up * 1e12, g_aoi_a=g_a, g_aoi_bc=g_bc,
    R_series_k=R_down_min / 1e3, R_one_k=req_n(Wmin) / 1e3)

# 图 2.2.2：逻辑努力，手算与仿真
plt = style()
fig, ax = plt.subplots(figsize=(6.2, 3.4))
names = ["nand2", "nand3", "nor2", "nor3"]
labels = [T("二输入与非", "NAND2"), T("三输入与非", "NAND3"), T("二输入或非", "NOR2"), T("三输入或非", "NOR3")]
x = np.arange(4)
hand = [le_g(k[:-1], int(k[-1])) for k in names]
ax.bar(x - 0.27, hand, 0.26, color=d.MUTED, label=T("手算模型", "hand model"))
ax.bar(x, [sim[k + "_A"]["g"] for k in names], 0.26, color=d.NMOS, label=T("仿真：靠近输出的输入 A", "SPICE: input A (near output)"))
ax.bar(x + 0.27, [sim[k + "_B"]["g"] for k in names], 0.26, color=d.MEAN, label=T("仿真：靠近电源轨的输入 B", "SPICE: input B (near rail)"))
ax.axhline(1, color=d.INK, lw=0.8, ls=":")
ax.text(3.55, 1.04, T("反相器", "inverter"), fontsize=8.5, color=d.INK, ha="right")
ax.set_xticks(x, labels)
ax.set_ylabel(T("逻辑努力 g", "logical effort g"))
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
d.spines(ax)
figure(fig, "fig2_2_2")

# 图 2.2.1：串联管子的放电波形（负载 = 参考反相器的 FO4 负载）
CL1 = 4 * Cinv + (1 + r) * Wmin * P["Cd"]
R1 = req_n(Wmin)
t = np.linspace(0, 4 * 0.69 * R1 * CL1 * 2, 400)
fig, ax = plt.subplots(figsize=(5.6, 3.2))
for R, col, ls, name in ((R1, d.NMOS, "-", T("一个最小 NMOS：R", "one minimum NMOS: R")),
                         (2 * R1, d.PMOS, "-", T("两个串联：2R", "two in series: 2R")),
                         (R1, d.MEAN, "--", T("两个串联，各加宽一倍：R", "two in series, each 2× wider: R"))):
    ax.plot(t * 1e12, P["VDD"] * np.exp(-t / (R * CL1)), color=col, ls=ls, lw=1.8, label=name)
ax.axhline(P["VDD"] / 2, color=d.MUTED, lw=0.8, ls=":")
ax.set_xlabel(T("时间 / ps", "time / ps")); ax.set_ylabel(T("输出电压 / V", "output voltage / V"))
ax.set_xlim(0, t[-1] * 1e12); ax.set_ylim(0, 1.9)
ax.legend(fontsize=8.5, frameon=False)
d.spines(ax)
figure(fig, "fig2_2_1")
out(t50_one_ps=0.69 * R1 * CL1 * 1e12, t50_two_ps=0.69 * 2 * R1 * CL1 * 1e12)
