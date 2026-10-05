"""2.3 节：逻辑努力。

算例 2.3.1  电机控制芯片的寄存器地址译码器：3 位地址选 8 个控制寄存器之一。每个地址位（原码或反码）最多呈现 2 个
            参考反相器的输入电容，每条输出要驱动一个 16 位寄存器的写使能（约 32 个参考反相器的输入电容），
            每个地址位接 4 个三输入与非门（分支努力 B = 4）。比较 2、3、4 级三种结构的最小延时，求各级尺寸。
算例 2.3.2  同样的计算换用 SKY130 仿真得到的 g、p，分开看 g 和 p 的误差各自对结论有多大影响。
图 2.3.2    寄生延时 p：手算模型与仿真（A、B 两个输入）。
图 2.3.1    路径延时随级数的变化（N = 2～8；路径努力相同，寄生延时随级数增加）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from mos import P, gamma_self, le_g, le_p, path_delay, stage_sizes, tau
import _draw as d

q = P["problems"]["p23"]
n, Cin, Cout, B = q["n_addr"], q["Cin_units"], q["Cout_units"], q["branch"]
H = Cout / Cin
gn, pn = le_g("nand", n), le_p("nand", n)
pi = le_p("inv", 1)
G = gn
F = G * B * H
Nhat = math.log(F) / math.log(4)
out(n=n, Cin=Cin, Cout=Cout, B=B, H=H, G=G, F=F, Nhat=Nhat, tau_ps=tau() * 1e12, p_inv=pi, p_nand=pn)

designs = {   # 各级的 (g, p, 本级输出的分支数)；分支发生在驱动 4 个与非门的那一级
    2: [(gn, pn, 1), (1, pi, 1)],
    3: [(1, pi, B), (gn, pn, 1), (1, pi, 1)],
    4: [(1, pi, 1), (1, pi, B), (gn, pn, 1), (1, pi, 1)],
}
res = {}
for N, st in designs.items():
    gs, ps, bs = [s[0] for s in st], [s[1] for s in st], [s[2] for s in st]
    D, Fp = path_delay(gs, ps, B, H)
    assert abs(Fp - F) < 1e-9
    caps, f = stage_sizes(gs, bs, Cin if N > 2 else Cin / B, Cout)   # 2 级时地址线直接分给 4 个与非门，每个分到 Cin/B
    res[N] = dict(D=D, f=f, P=sum(ps), caps=caps)
    out(**{f"D{N}": D, f"f{N}": f, f"P{N}": sum(ps), f"t{N}_ps": D * tau() * 1e12})
best = min(res, key=lambda k: res[k]["D"])
out(best=best, D_best=res[best]["D"], t_best_ps=res[best]["D"] * tau() * 1e12)
# 3 级结构的尺寸：输入反相器的输入电容为 Cin；与非门每个输入的电容；输出反相器的输入电容（单位：参考反相器的输入电容）
c3 = res[3]["caps"]
out(s3_inv1=c3[0], s3_nand=c3[1], s3_inv2=c3[2], s3_nand_x=c3[1] / gn)   # 与非门相对等效反相器的放大倍数

# 算例 2.3.2：换用仿真的 g、p（A 输入；三输入与非门）
sim = P["gates_sim"]
gs_sim = sim["gates"][f"nand{n}_A"]["g"]
ps_sim = sim["gates"][f"nand{n}_A"]["p"]
pis = sim["p_inv"]
for N, st in designs.items():
    gs = [gs_sim if s[0] != 1 else 1 for s in st]
    ps = [ps_sim if s[0] != 1 else pis for s in st]
    D, _ = path_delay(gs, ps, B, H)
    # 以 τ 为单位的结果再乘第 1 章校准的 τ 换成 ps（仿真里的 τ 与之相差几个百分点，见附录 A）
    out(**{f"Ds{N}": D, f"ts{N}_ps": D * tau() * 1e12})
# 分开替换：只换 g、只换 p（3 级结构），以及换成靠近电源轨的 B 输入的仿真值
st3 = designs[3]
Dg, _ = path_delay([gs_sim if s[0] != 1 else 1 for s in st3], [s[1] for s in st3], B, H)
Dp, _ = path_delay([s[0] for s in st3], [ps_sim if s[0] != 1 else pis for s in st3], B, H)
gB, pB = sim["gates"][f"nand{n}_B"]["g"], sim["gates"][f"nand{n}_B"]["p"]
DB, _ = path_delay([gB if s[0] != 1 else 1 for s in st3], [pB if s[0] != 1 else pis for s in st3], B, H)
out(Dg3=Dg, Dp3=Dp, DB3=DB, p_nand_sim=ps_sim, p_nand_hand=pn, p_ratio=ps_sim / pn, p_pct=ps_sim / pn * 100)
out(F_sim=gs_sim * B * H)

# 图 2.3.1：D(N)，以三输入与非门 + (N − 1) 个反相器为路径
plt = style()
fig, ax = plt.subplots(figsize=(5.6, 3.4))
Ns = np.arange(2, 9)
eff = [N * F ** (1 / N) for N in Ns]
par = [pn + (N - 1) * pi for N in Ns]
tot = [a + b for a, b in zip(eff, par)]
ax.plot(Ns, eff, "o--", color=d.NMOS, lw=1.4, ms=4, label=T("努力延时 N·F^(1/N)", "effort delay N·F^(1/N)"))
ax.plot(Ns, par, "s:", color=d.LOAD, lw=1.4, ms=4, label=T("寄生延时 ΣP", "parasitic delay ΣP"))
ax.plot(Ns, tot, "o-", color=d.MEAN, lw=1.8, ms=5, label=T("总延时 D", "total delay D"))
k = int(np.argmin(tot))
ax.plot([Ns[k]], [tot[k]], "o", ms=11, mfc="none", mec=d.INK, mew=1.4)
ax.axvline(Nhat, color=d.MUTED, lw=0.8, ls=":")
ax.text(Nhat + 0.08, max(tot) * 0.9, T(f"ln F / ln 4 ≈ {Nhat:.1f}", f"ln F / ln 4 ≈ {Nhat:.1f}"), fontsize=8.5, color=d.MUTED)
ax.set_xlabel(T("级数 N", "number of stages N"))
ax.set_ylabel(T("延时 / τ", "delay / τ"))
ax.set_ylim(0, max(tot) * 1.05)
ax.legend(fontsize=8.5, frameon=False, loc="upper right")
d.spines(ax)
figure(fig, "fig2_3_1")

# 图 2.3.2：寄生延时，手算与仿真
fig, ax = plt.subplots(figsize=(6.2, 3.4))
names = ["nand2", "nand3", "nor2", "nor3"]
labels = [T("二输入与非", "NAND2"), T("三输入与非", "NAND3"), T("二输入或非", "NOR2"), T("三输入或非", "NOR3")]
x = np.arange(4)
ax.bar(x - 0.27, [le_p(k[:-1], int(k[-1])) for k in names], 0.26, color=d.MUTED, label=T("手算模型 nγ", "hand model nγ"))
ax.bar(x, [sim["gates"][k + "_A"]["p"] for k in names], 0.26, color=d.NMOS, label=T("仿真：输入 A（靠近输出）", "SPICE: input A (near output)"))
ax.bar(x + 0.27, [sim["gates"][k + "_B"]["p"] for k in names], 0.26, color=d.MEAN, label=T("仿真：输入 B（靠近电源轨）", "SPICE: input B (near rail)"))
ax.axhline(pi, color=d.INK, lw=0.8, ls=":")
ax.text(-0.45, pi + 0.15, T("反相器 γ", "inverter γ"), fontsize=8.5, color=d.INK)
ax.set_xticks(x, labels)
ax.set_ylabel(T("寄生延时 p / τ", "parasitic delay p / τ"))
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
d.spines(ax)
figure(fig, "fig2_3_2")
