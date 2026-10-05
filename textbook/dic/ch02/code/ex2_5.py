"""2.5 节：动态逻辑与多米诺逻辑。

算例 2.5.1  十六路故障信号的“或”：每路信号最多呈现 1 个参考反相器的输入电容，输出驱动 4 个参考反相器（H = 4）。
            比较四种做法的延时（以 τ 为单位）：静态 CMOS 两级（四输入或非 + 四输入与非）、伪 NMOS 十六输入或非 + 反相器、
            带底管的多米诺十六输入或、两个八输入动态门加一个二输入与非门（复合多米诺）。
算例 2.5.2  动态与门（过流且已使能）的电荷分享：预充的动态节点把电荷分给串联管之间的内部节点，电压掉多少。
"""
import math

from bookout import out
from mos import Cd, Cg, VDD, Wmin, cin, gamma_self, idsat_n, idsat_p, le_g, le_p, r_ratio, tau, vm

r = r_ratio()
gam = gamma_self()
H = 4.0
Cinv = cin(Wmin, r * Wmin)


def best(gs, ps):
    G = math.prod(gs)
    N = len(gs)
    F = G * H
    return N * F ** (1 / N) + sum(ps), F


# 静态两级：四输入或非 → 四输入与非
D_static, F_static = best([le_g("nor", 4), le_g("nand", 4)], [le_p("nor", 4), le_p("nand", 4)])

# 动态门（带底管）：输入管与底管串联，各取 2Wmin，下拉与参考反相器一样强；g = 2Wmin·Cg / Cinv
g_dyn = 2 * Wmin * Cg / Cinv


def p_dyn(n):
    """动态节点上的漏极：n 个输入管（各 2Wmin）+ 预充 PMOS（r·Wmin）+ 保持管（Wmin）；以参考反相器的漏极宽度归一，乘 γ。"""
    return (n * 2 * Wmin + r * Wmin + Wmin) / ((1 + r) * Wmin) * gam


D_dom16, _ = best([g_dyn, 1.0], [p_dyn(16), le_p("inv", 1)])
D_dom8, _ = best([g_dyn, le_g("nand", 2)], [p_dyn(8), le_p("nand", 2)])

# 伪 NMOS 十六输入或非：下拉 NMOS 取 3Wmin（每路输入电容 3Wmin·Cg ≈ 0.88Cinv，满足每路不超过 1Cinv），负载 PMOS 最小宽度；下降沿的等效“逻辑努力”
Wn = 3 * Wmin
i_net = idsat_n(Wn) - idsat_p(Wmin)                 # 下拉电流先抵掉常通的负载电流
k = idsat_n(Wmin) / i_net                           # 与参考反相器下拉电流之比：电阻按这个比例折算
g_ps = Wn * Cg / Cinv * k                           # 下降沿的等效逻辑努力
p_ps = (16 * Wn + Wmin) / ((1 + r) * Wmin) * gam * k
D_ps, _ = best([g_ps, 1.0], [p_ps, le_p("inv", 1)])

out(H=H, cin_ps=Wn * Cg / Cinv, g_ps=g_ps, p_ps=p_ps, D_static=D_static, D_ps=D_ps, D_dom16=D_dom16, D_dom8=D_dom8, g_dyn=g_dyn, g_nor4=le_g("nor", 4),
    g_nand4=le_g("nand", 4), p_dyn16=p_dyn(16), p_dyn8=p_dyn(8), F_static=F_static,
    t_static_ps=D_static * tau() * 1e12, t_dom8_ps=D_dom8 * tau() * 1e12, t_dom16_ps=D_dom16 * tau() * 1e12,
    t_ps_ps=D_ps * tau() * 1e12, ratio_pct=D_dom8 / D_static * 100)

# 算例 2.5.2：电荷分享。动态与门：预充 PMOS、保持管、输入 A、B 与底管串联（各 3Wmin），动态节点接高偏斜反相器
Wn3 = 3 * Wmin
Cx = (r * Wmin + Wmin + Wn3) * Cd + cin(Wmin, 2 * r * Wmin)  # 动态节点：预充、保持管与 A 管的漏极 + 后级高偏斜反相器输入
Cint = 2 * Wn3 * Cd                                           # A、B 之间的内部节点：A 的源极与 B 的漏极
v_after = VDD * Cx / (Cx + Cint)
vm_hi = vm(Wmin, 2 * r * Wmin)                                # 高偏斜反相器（PMOS 加倍）的开关阈值
out(Cx_ff=Cx * 1e15, Cint_ff=Cint * 1e15, v_after=v_after, dv=VDD - v_after, vm_hi=vm_hi,
    margin=v_after - vm_hi)

# ---------------------------------------------------------------- 图 2.5.1：带底管和保持管的多米诺或门；图 2.5.2：四种做法的延时
import schemdraw  # noqa: E402

from bookout import T, figure, style  # noqa: E402
import _draw as d  # noqa: E402

plt = style()
fig, ax = plt.subplots(figsize=(6.4, 5.2))
with schemdraw.Drawing(show=False) as dr:
    n = d.Net(dr)
    n.rail(0.8, 5.0, 10.4, "VDD")
    n.line((2.4, 10.4), (2.4, 10.1)); y = n.pfet(2.4, 10.1, "CLK"); n.line((2.4, y), (2.4, 8.2))        # 预充管
    n.line((3.8, 10.4), (3.8, 10.1)); yk = n.pfet(3.8, 10.1, "", right=True); n.line((3.8, yk), (3.8, 8.2))   # 保持管（栅在右）
    n.line((1.2, 8.2), (7.0, 8.2)); n.dot((2.4, 8.2)); n.dot((3.8, 8.2))
    n.text((3.1, 8.45), "X", d.INK, size=10)
    xs = ((1.2, "A1"), (3.4, "A2"), (7.0, "A16"))
    for x, g in xs:                                                                                       # 16 个并联输入管，画 3 个
        n.line((x, 8.2), (x, 7.9)); yy = n.nfet(x, 7.9, g); n.line((x, yy), (x, 5.9))
    n.text((4.3, 6.3), "…", d.NMOS, size=14)
    n.line((1.2, 5.9), (7.0, 5.9)); n.dot((3.4, 5.9))
    n.line((3.4, 5.9), (3.4, 5.6)); yf = n.nfet(3.4, 5.6, "CLK"); n.ground((3.4, yf))                   # 底管
    import schemdraw.logic as logic
    n.line((7.0, 8.2), (7.4, 8.2))
    inv = dr.add(logic.Not().at((7.4, 8.2)).right().color(d.INK))
    yo = inv.absanchors["out"]
    n.line(yo, (yo[0] + 0.9, yo[1])); n.text((yo[0] + 1.0, yo[1]), "Y", loc="right"); n.dot((yo[0] + 0.5, yo[1]))
    n.line((yo[0] + 0.5, yo[1]), (yo[0] + 0.5, 9.35)); n.line((yo[0] + 0.5, 9.35), (5.53, 9.35))
    d.schem_to_ax(dr, ax)
ax.set_title(T("多米诺或门：CLK = 0 预充 X，CLK = 1 求值；Y 经保持管把 X 维持在高电平", "Domino OR: CLK = 0 precharges X, CLK = 1 evaluates; Y holds X high through the keeper"), fontsize=9.5)
figure(fig, "fig2_5_1")

fig, ax = plt.subplots(figsize=(6.0, 3.0))
names = [T("静态两级\n（或非 4 + 与非 4）", "static, 2 stages\n(NOR4 + NAND4)"), T("伪 NMOS 或非 16\n+ 反相器", "pseudo-NMOS NOR16\n+ inverter"),
         T("多米诺或 16", "domino OR16"), T("两个动态或 8\n+ 与非 2", "two dynamic OR8\n+ NAND2")]
vals = [D_static, D_ps, D_dom16, D_dom8]
cols = [d.MUTED, d.LOAD, d.NMOS, d.MEAN]
ax.barh(range(4), vals, color=cols, height=0.55)
for i, v in enumerate(vals):
    ax.text(v + 0.3, i, f"{v:.1f}τ", va="center", fontsize=9)
ax.set_yticks(range(4), names, fontsize=8.5)
ax.invert_yaxis()
ax.set_xlabel(T("路径延时 / τ（H = 4）", "path delay / τ (H = 4)"))
ax.set_xlim(0, max(vals) * 1.18)
d.spines(ax)
figure(fig, "fig2_5_2")
