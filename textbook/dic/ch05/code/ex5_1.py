"""5.1 节：动态功耗与短路功耗。

算例 5.1.1  第 3 章那块电机控制芯片：2000 个触发器（时钟 100 MHz），另有约两万个门（等效）的组合逻辑，翻转率 0.1、每个门 5 fF，
            毛刺使组合逻辑的翻转多出约两成（示意值），时钟树的导线和缓冲器电容取触发器时钟电容的 1.5 倍（示意值）。
            求各部分的动态功耗。
算例 5.1.2  反相器驱动 FO4 负载，输入转换时间从很快到 8 个 FO4：短路能量占充电能量的比例（SKY130 仿真与 Veendrick 公式）。
图 5.1.2    短路能量 / 充电能量随输入转换时间的变化：仿真（FO4 负载）与手算（Veendrick，空载估计）。
图 5.1.1    算例 5.1.1 的功耗构成。
"""
import numpy as np

from bookout import T, figure, out, style
from mos import P, VDD, VTn, Wmin, cin, fo4_tp, gamma_self, kn, L, r_ratio, sc_ratio
import _draw as d

r = r_ratio()
g = gamma_self()
C0 = cin(Wmin, r * Wmin)
f4 = fo4_tp(r)
q = P["problems"]["p51"]
q34 = P["problems"]["p34"]
f = q34["f_MHz"] * 1e6

# ---------------------------------------------------------------- 算例 5.1.1
c_ff = (1 + (3 + g) + (2 + g)) * C0                 # 第 3 章算例 3.4.1：每个触发器内部的时钟电容
p_ff = q34["n_ff"] * c_ff * VDD ** 2 * f
p_tree = q["tree_ratio"] * p_ff
p_logic = q["alpha"] * q["n_gates"] * q["c_gate_fF"] * 1e-15 * VDD ** 2 * f
p_glitch = q["glitch"] * p_logic
tot = p_ff + p_tree + p_logic + p_glitch
out(n_ff=q34["n_ff"], f_MHz=q34["f_MHz"], n_gates=q["n_gates"], alpha=q["alpha"], c_gate=q["c_gate_fF"], glitch_pct=q["glitch"] * 100,
    tree_ratio=q["tree_ratio"], c_ff_ff=c_ff * 1e15, p_ff_mw=p_ff * 1e3, p_tree_mw=p_tree * 1e3, p_logic_mw=p_logic * 1e3,
    p_glitch_mw=p_glitch * 1e3, p_tot_mw=tot * 1e3, clk_pct=(p_ff + p_tree) / tot * 100, logic_pct=(p_logic + p_glitch) / tot * 100)
# 降压的效果：功耗与 V² 成正比
out(p_12_mw=tot * (1.2 / VDD) ** 2 * 1e3, v_ratio_pct=(1.2 / VDD) ** 2 * 100)

# ---------------------------------------------------------------- 算例 5.1.2
beta = kn * Wmin / L
c_fo4 = (4 + g) * C0                                # FO4 负载加自身漏极电容
e_sw = c_fo4 * VDD ** 2


def veendrick(tin):
    """空载反相器、输入线性斜坡（上升、下降都为 tin）一个周期的短路能量：(β/12)(VDD − 2VT)³·tin。"""
    return beta / 12 * (VDD - 2 * VTn) ** 3 * tin


for k in (1, 4, 8):
    out(**{f"sc{k}_pct": sc_ratio(k) * 100, f"vd{k}_pct": veendrick(k * f4) / e_sw * 100})
out(fo4_ps=f4 * 1e12, beta_ua=beta * 1e6, vdd_2vt=VDD - 2 * VTn, VT=VTn, e_sw_fj=e_sw * 1e15, c_fo4_ff=c_fo4 * 1e15,
    window_lo=VTn, window_hi=VDD - P["VTp"])
slow = q["slow_tin_fo4"]
c_inv1 = (3 + g) * C0                               # 触发器内部第一级时钟反相器的负载（第 3 章：反相时钟节点）
extra = (sc_ratio(slow) - sc_ratio(1)) * q34["n_ff"] * c_inv1 * VDD ** 2 * f
out(slow=slow, p_sc_slow_mw=extra * 1e3, sc_slow_pct=sc_ratio(slow) * 100)

# ---------------------------------------------------------------- 图 5.1.2（短路）
plt = style()
fig, ax = plt.subplots(figsize=(5.8, 3.4))
sc = P["power_sim"]["sc"]
ax.plot([a for a, _ in sc], [b * 100 for _, b in sc], "o-", color=d.NMOS, lw=1.8, label=T("SKY130 仿真（FO4 负载）", "SKY130 simulation (FO4 load)"))
xs = np.linspace(0, 13, 60)
ax.plot(xs, [veendrick(x * f4) / e_sw * 100 for x in xs], color=d.PMOS, lw=1.4, ls="--", label=T("Veendrick 公式（空载估计）", "Veendrick formula (unloaded estimate)"))
ax.axvspan(0, 1.5, color=d.MEAN, alpha=0.12, lw=0)
ax.text(0.75, 11, T("输入与输出\n边沿相当", "input ≈ output\nedge"), ha="center", fontsize=8.5, color=d.MEAN)
ax.set_xlabel(T("输入转换时间 / FO4", "input transition time / FO4")); ax.set_ylabel(T("短路能量 / 充电能量 / %", "short-circuit / switching energy / %"))
ax.set_xlim(0, 13); ax.set_ylim(0, 20)
ax.legend(fontsize=8.5, frameon=False, loc="upper right")
d.spines(ax)
figure(fig, "fig5_1_2")

# ---------------------------------------------------------------- 图 5.1.2
fig, ax = plt.subplots(figsize=(5.8, 2.6))
parts = [(T("触发器内部的时钟", "clock inside flip-flops"), p_ff, d.PMOS), (T("时钟树", "clock tree"), p_tree, d.LOAD),
         (T("组合逻辑", "logic"), p_logic, d.NMOS), (T("毛刺", "glitches"), p_glitch, d.MEAN)]
left = 0
for k, (name, v, c) in enumerate(parts):
    ax.barh(0, v * 1e3, left=left, color=c, height=0.5)
    up = v * 1e3 > 5
    ax.text(left + v * 1e3 / 2 + (0 if up else (-1.2 if k == 2 else 1.2)), 0.42 if up else -0.42, f"{name}\n{v * 1e3:.1f} mW",
            ha="center", va="bottom" if up else "top", fontsize=8.5, color=c)
    left += v * 1e3
ax.set_xlim(0, left * 1.06); ax.set_ylim(-1.2, 1.2)
ax.set_yticks([]); ax.set_xlabel(T("功耗 / mW", "power / mW"))
for k in ("top", "right", "left"):
    ax.spines[k].set_visible(False)
figure(fig, "fig5_1_1")
