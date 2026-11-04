"""11.3 影响疲劳的因素：WQ-CR5 大臂法兰内角的零件疲劳极限。

算例 11.3.1  有限元求 Kt：数字工厂“仿真与分析”同一套程序，WQ-CR5 大臂示例零件，内角按 2 mm、4 mm 圆角（第 10 章 10.4 节的做法，
            内角局部加密到 0.6 mm），J2 端（根部）受纯弯矩：Kt = 圆角表面最大主应力 / 管的名义弯曲应力 M/W；J3 端同样算一次（2 mm）。
            缺口敏感系数按彼得森公式 q = 1/(1 + a/r)，铝合金 a ≈ 0.51 mm（[PET]），Kf = 1 + q (Kt − 1)；
算例 11.3.2  零件的疲劳极限：材料库的 σ₋₁（光滑试样，旋转弯曲）依次乘表面系数（FKM 的粗糙度公式，变形铝合金：
            K_R = 1 − 0.22·lg R_z·lg(2R_m/133)，精车 R_z = 6.3 μm）、阳极氧化系数（本书取 0.8，手册范围约 0.6–0.95）、
            尺寸系数（数字工厂疲劳程序的默认值 0.85）、可靠度系数（99%：0.814，[SHI]），再除以 Kf；
            与数字工厂疲劳程序的默认做法（β 按钢的“精车”0.85、尺寸 0.85、Kf = 1）比较；
图 11.3.1。
"""
import math

import numpy as np

import _ch11 as H
from bookout import T, figure, out, style

p = H.SP.params_of("wqcr5_upper", None)
D, d = p["D"], p["D"] - 2 * p["t"]
Wb = math.pi * (D ** 4 - d ** 4) / (32 * D)              # 抗弯截面系数 mm³
s_nom = 1e3 / Wb                                        # 1 N·m 弯矩的名义应力 MPa


def kt_of(U_end):
    """单位弯矩 My 下圆角表面的最大主应力（沿圆周找最大）/ 名义应力"""
    best = 0.0
    for th in np.radians(np.arange(0, 360, 5)):
        h = H.tensor_at(U_end, np.array([[0.0], [0.0], [0.0], [0.0], [1.0], [0.0]]), th)[:, 0, :]
        best = max(best, float(H.eig_all(h)[:, 2].max()))
    return best / s_nom


R = H.heavy()
kt2_root = kt_of(R["U"]["J2"])
kt2_tip = kt_of(R["U"]["J3"])
U4 = H.unit_cases(rf=4.0, cases=("Fx", "My"), ends=("J2",))["J2"]
U4["amp"]["Fz"] = U4["amp"]["Mz"] = np.zeros_like(U4["amp"]["My"])
kt4_root = kt_of(U4)
A_PET = 0.51                                            # mm，铝合金（彼得森）


def kf_of(kt, r):
    q = 1 / (1 + A_PET / r)
    return q, 1 + q * (kt - 1)


q2, kf2 = kf_of(kt2_root, 2.0)
q4, kf4 = kf_of(kt4_root, 4.0)

al = H.AL
s1 = al["sigma_1"]
Rm = al["ultimate_mpa"]
RZ = 6.3
K_R = 1 - 0.22 * math.log10(RZ) * math.log10(2 * Rm / 133)
K_ANO = 0.8
K_SIZE = 0.85
K_REL = 0.814
chain = [(T("光滑试样 σ₋₁", "smooth σ₋₁"), s1)]
v = s1 * K_R
chain.append((T("× 表面 {:.2f}".format(K_R), "× surface {:.2f}".format(K_R)), v))
v *= K_ANO
chain.append((T("× 阳极氧化 {:.1f}".format(K_ANO), "× anodizing {:.1f}".format(K_ANO)), v))
v *= K_SIZE
chain.append((T("× 尺寸 {:.2f}".format(K_SIZE), "× size {:.2f}".format(K_SIZE)), v))
v *= K_REL
chain.append((T("× 可靠度 99% {:.3f}".format(K_REL), "× reliability 99% {:.3f}".format(K_REL)), v))
s_un = v                                                 # 不含缺口
v /= kf2
chain.append((T("÷ Kf {:.2f}（2 mm 圆角）".format(kf2), "÷ Kf {:.2f} (2 mm fillet)".format(kf2)), v))
s_part = v
s_part4 = s_un / kf4
s_factory = s1 * H.FT.SURFACE["fine_turned"][0] * 0.85   # 数字工厂默认：β（钢，精车）× 尺寸，Kf = 1（应力取有限元的局部值）

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.35, 1]})
xs = np.arange(len(chain))
vals = [c[1] for c in chain]
a0.bar(xs, vals, color=["#1f77b4"] + ["#9ecae1"] * (len(chain) - 2) + ["#d62728"], width=0.62)
for x, y in zip(xs, vals):
    a0.text(x, y + 1.5, "{:.0f}".format(y), ha="center", fontsize=6.3)
a0.set_xticks(xs)
a0.set_xticklabels([c[0] for c in chain], fontsize=5.6, rotation=28, ha="right")
a0.set_ylabel(T("疲劳极限 / MPa（N_D = 5×10⁸）", "Fatigue strength / MPa (N_D = 5×10⁸)"), fontsize=7.0)
a0.set_ylim(0, s1 * 1.15)
a0.tick_params(labelsize=6.2)
a0.set_title(T("(a) 从光滑试样到大臂法兰内角", "(a) From smooth specimen to the arm's flange corner"), fontsize=7.0)
rr = np.linspace(0.5, 6.0, 100)
a1.plot(rr, 1 / (1 + A_PET / rr), color="#1f77b4", lw=1.3)
for r_, q_ in ((2.0, q2), (4.0, q4)):
    a1.plot([r_], [q_], "o", color="#d62728", ms=3.5)
    a1.text(r_ + 0.15, q_ - 0.06, "r = {:.0f} mm\nq = {:.2f}".format(r_, q_), fontsize=6.0)
a1.set_xlabel(T("圆角半径 r / mm", "Fillet radius r / mm"), fontsize=7.0)
a1.set_ylabel(T("缺口敏感系数 q", "Notch sensitivity q"), fontsize=7.0)
a1.set_ylim(0, 1.0)
a1.tick_params(labelsize=6.2)
a1.grid(True, lw=0.3, alpha=0.4)
a1.set_title(T("(b) 彼得森公式（铝合金 a = 0.51 mm）", "(b) Peterson's formula (Al alloys, a = 0.51 mm)"), fontsize=7.0)
fig.tight_layout()
figure(fig, "fig11_3_1")

out(W=Wb, s_nom=s_nom, kt2=kt2_root, kt2_tip=kt2_tip, kt4=kt4_root, a_pet=A_PET, q2=q2, q4=q4, kf2=kf2, kf4=kf4,
    s1=s1, Rm=Rm, Rz=RZ, K_R=K_R, K_ano=K_ANO, K_size=K_SIZE, K_rel=K_REL, s_un=s_un, s_part=s_part, s_part4=s_part4,
    ratio_part=s_part / s1 * 100, s_factory=s_factory, beta_steel=H.FT.SURFACE["fine_turned"][0],
    el2=R["U"]["J2"]["elements"], el4=U4["elements"], hmin=H.HMIN)
