"""5.5 节：功耗分析的流程。

算例 5.5.1  两个 16 位计数器：PWM 计数器每个时钟都加 1；编码器计数器只在编码器边沿时加 1（6000 r/min、1024 线、四倍频，
            时钟 100 MHz）。求各位的翻转率、数据部分与时钟部分的功耗，并与“默认翻转率 0.1”的无向量估计比较。
图 5.5.1    两个计数器各位的翻转率（每个时钟周期，对数纵轴）。
图 5.5.2    功耗分析从估算到签核的流程。
"""
import numpy as np

from bookout import T, figure, out, style
from mos import P, VDD, Wmin, cin, gamma_self, le_g, r_ratio
import _draw as d

q = P["problems"]["p55"]
r = r_ratio()
g = gamma_self()
C0 = cin(Wmin, r * Wmin)
f = q["f_MHz"] * 1e6
n = q["bits"]
c_clk = (1 + (3 + g) + (2 + g)) * C0                 # 第 3 章：每个触发器内部的时钟电容
c_q = (le_g("nand", 2) + 4 + 1 + g) * C0             # 每位 Q：加 1 电路的与非门、异或门、比较器或读出（1 个参考输入）与自身漏极（示意）
enc_rate = q["rpm"] / 60 * q["lines"] * 4 / f       # 编码器计数器每个时钟周期加 1 的概率（四倍频）
pwm = np.array([0.5 ** i for i in range(n)])        # 第 i 位每次加 1 时翻转的概率
enc = pwm * enc_rate


def power(rates):
    """数据部分：每次翻转耗能 C·V²/2；时钟部分：每个周期 C·V²（每个触发器）。"""
    p_d = float(np.sum(rates)) * c_q * VDD ** 2 / 2 * f
    p_c = n * c_clk * VDD ** 2 * f
    return p_d, p_c


pd_pwm, pc = power(pwm)
pd_enc, _ = power(enc)
pd_vl, _ = power(np.full(n, 2 * 0.1))              # 默认 α = 0.1（0→1 的概率）相当于每周期 0.2 次翻转
c_icg = (1 + (1 + g) + 1 + le_g("nand", 2)) * C0    # 第 3 章 3.4 节：门控单元一直接着时钟
p_icg = c_icg * VDD ** 2 * f
out(bits=n, f_MHz=q["f_MHz"], toggles=float(pwm.sum()), avg_rate=float(pwm.mean()), enc_rate_pct=enc_rate * 100,
    enc_inc_k=enc_rate * f / 1e3, c_clk_ff=c_clk * 1e15, c_q_ff=c_q * 1e15,
    pd_pwm_uw=pd_pwm * 1e6, pc_uw=pc * 1e6, pd_enc_uw=pd_enc * 1e6, pd_vl_uw=pd_vl * 1e6, clk_over_pwm=pc / pd_pwm,
    clk_over_enc=pc / pd_enc, vl_over_enc=pd_vl / pd_enc, vl_over_pwm=pd_vl / pd_pwm, gated_enc_uw=(pd_enc + pc * enc_rate + p_icg) * 1e6, p_icg_uw=p_icg * 1e6,
    enc_gate_save_pct=(1 - (pd_enc + pc * enc_rate + p_icg) / (pd_enc + pc)) * 100, alpha_pwm=float(pwm.mean()) / 2)

# ---------------------------------------------------------------- 图 5.5.1
plt = style()
fig, ax = plt.subplots(figsize=(5.8, 3.2))
x = np.arange(n)
ax.semilogy(x, pwm, "o-", color=d.NMOS, lw=1.6, label=T("PWM 计数器（每个时钟加 1）", "PWM counter (+1 every clock)"))
ax.semilogy(x, enc, "s-", color=d.PMOS, lw=1.6, label=T("编码器计数器（只在编码器边沿加 1）", "encoder counter (+1 on encoder edges)"))
ax.axhline(0.2, color=d.LOAD, lw=1.0, ls="--")
ax.text(n - 1, 0.26, T("默认 α = 0.1（每周期 0.2 次翻转）", "default α = 0.1 (0.2 toggles per cycle)"), ha="right", fontsize=8.5, color=d.LOAD)
ax.set_xlabel(T("位", "bit")); ax.set_ylabel(T("每个时钟周期的翻转次数", "toggles per clock cycle"))
ax.set_xticks(x[::2])
ax.legend(fontsize=8.5, frameon=False, loc="lower left")
d.spines(ax)
figure(fig, "fig5_5_1")

# ---------------------------------------------------------------- 图 5.5.2
fig, ax = plt.subplots(figsize=(9.4, 2.4))
steps = [(T("架构估算", "architecture\nestimate"), T("门数 × 默认翻转率\n误差可达数倍", "gates × default α\nerror up to several ×")),
         (T("RTL 仿真", "RTL simulation"), T("得到各信号的翻转率\n（活动率文件）", "per-signal activity\n(activity file)")),
         (T("综合后门级", "gate level after\nsynthesis"), T("单元库的电容与内部能量\n毛刺开始可见", "library cap and\ninternal energy; glitches")),
         (T("版图后签核", "sign-off after\nlayout"), T("提取导线电容\n时钟树、电源压降", "extracted wire cap,\nclock tree, IR drop"))]
for k, (a, b) in enumerate(steps):
    x0 = 0.2 + k * 2.35
    ax.add_patch(__import__("matplotlib").patches.FancyBboxPatch((x0, 0.9), 1.9, 0.9, boxstyle="round,pad=0.04", fill=False, ec=d.NMOS, lw=1.3))
    ax.text(x0 + 0.95, 1.35, a, ha="center", va="center", fontsize=9, color=d.NMOS)
    ax.text(x0 + 0.95, 0.45, b, ha="center", va="center", fontsize=8, color=d.MUTED)
    if k < 3:
        ax.annotate("", xy=(x0 + 2.3, 1.35), xytext=(x0 + 1.95, 1.35), arrowprops=dict(arrowstyle="->", color=d.INK))
ax.annotate("", xy=(0.4, 1.95), xytext=(9.3, 1.95), arrowprops=dict(arrowstyle="<->", color=d.LOAD))
ax.text(4.8, 2.05, T("越往右越准，越往左越早、越能改结构", "accuracy grows to the right; freedom to change the design grows to the left"),
        ha="center", fontsize=8.5, color=d.LOAD)
ax.set_xlim(0, 9.6); ax.set_ylim(0, 2.4); ax.axis("off")
figure(fig, "fig5_5_2")
