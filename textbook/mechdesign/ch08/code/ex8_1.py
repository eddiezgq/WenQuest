"""8.1 应力与应变、胡克定律：协作机器人肩关节的力矩传感器。在 RJ-201（第 33 章：Ø50/Ø30 空心轴，40Cr 调质）的 Ø50/Ø30 截面上
沿与轴线成 ±45° 的方向贴四片应变片，组成全桥（现结构上这一段被轴承和隔套占满，这里是“假设这段表面露在外面”的估算；
真正贴在哪里是任务单 TS-8-1 的题目）。纯扭转时表面是纯剪切，±45° 方向是主方向：ε±45 = ±τ/(2G) = ±(1 + ν)τ/E。
由谐波减速器 CSF-25-100（零件库）的额定、起停允许峰值、瞬时允许最大转矩求切应力、应变和电桥输出；
再反过来，由读到的应变（30 µε）求转矩；最后看要得到常用的 1 mV/V 满量程输出，弹性体要多薄。与同尺寸的 7075 铝合金弹性体比较（算例 8.1.1、8.1.2，图 8.1.1）。"""
import math

import numpy as np

import _ch8 as H
import _rj as R
from bookout import T, figure, out, style

D, d = R.SEAT, R.BORE
hd = R.harmonic("25-100")
ST, AL = H.mat("40Cr-QT"), H.mat("7075-T6")
GF = 2.0                                        # 应变片的灵敏系数（金属箔式的常用值，本书取值）
Wp = H.Wp_hollow(D, d)
TQ = {"rated": hd["rated"], "repeat": hd["repeat"], "momentary": hd["momentary"]}


def strain45(Tnm, m):
    tau = Tnm * 1e3 / Wp
    return tau, tau / (2 * m["G"])              # = (1 + ν)τ / E


res = {k: strain45(v, ST) for k, v in TQ.items()}
res_al = {k: strain45(v, AL) for k, v in TQ.items()}
# 全桥：四片都参与（两片 +ε、两片 −ε），输出 U/U₀ = GF·ε
out_rep = GF * res["repeat"][1] * 1e3            # mV/V
out_rep_al = GF * res_al["repeat"][1] * 1e3
# 反算：读到 ε45 = 120 µε（本书设定的一个读数），转矩是多少
EPS_READ = 30e-6
T_read = EPS_READ * 2 * ST["G"] * Wp / 1e3
# 想在起停峰值时得到 1 mV/V（ε = 500 µε，常用的满量程输出）：外径不变，内孔要扩到多大？
OUT_TARGET = 1.0e-3
tau_need = 2 * ST["G"] * OUT_TARGET / GF
Wp_need = TQ["repeat"] * 1e3 / tau_need
d_need = (D ** 4 - 16 * D * Wp_need / math.pi) ** 0.25
# 胡克定律的三个常数
G_check = ST["E"] / (2 * (1 + ST["nu"]))

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.0, 1.2]})
# (a) 纯剪切单元与 ±45° 应变片
from matplotlib.patches import Rectangle, FancyArrowPatch
a0.add_patch(Rectangle((-1, -1), 2, 2, fc="#eef3fa", ec=H.INK, lw=1.0))
for (x0, y0, x1, y1) in ((-0.9, 1.15, 0.9, 1.15), (0.9, -1.15, -0.9, -1.15), (1.15, -0.9, 1.15, 0.9), (-1.15, 0.9, -1.15, -0.9)):
    a0.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=9, color="#1f77b4", lw=1.0))
for ang, col, lab in ((45, "#d62728", "+ε"), (-45, "#2ca02c", "−ε")):
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    a0.plot([-0.8 * c, 0.8 * c], [-0.8 * s_, 0.8 * s_], color=col, lw=3)
    a0.text(0.95 * c, 0.95 * s_ + 0.08, lab, color=col, fontsize=7, ha="center")
a0.text(0, 1.35, "τ", color="#1f77b4", fontsize=8, ha="center")
a0.text(0, -1.7, T("轴线方向 →", "axis →"), fontsize=6.6, ha="center", color=H.MUTED)
a0.set_xlim(-1.6, 1.6)
a0.set_ylim(-1.9, 1.6)
a0.set_aspect("equal")
a0.axis("off")
a0.set_title(T("(a) 表面一点：纯剪切，±45° 方向一拉一压", "(a) A surface point: pure shear, ±45° stretched and squeezed"), fontsize=7.4)
tq = np.linspace(0, hd["momentary"], 50)
for m, col, lab in ((ST, "#1f77b4", T("40Cr 钢", "40Cr steel")), (AL, "#ff7f0e", T("7075 铝合金", "7075 aluminum"))):
    a1.plot(tq, [GF * strain45(t, m)[1] * 1e3 for t in tq], color=col, lw=1.3, label=lab)
for k, v in TQ.items():
    a1.axvline(v, color=H.MUTED, lw=0.6, ls=":")
    a1.text(v, 0.02, {"rated": T("额定", "rated"), "repeat": T("起停峰值", "start–stop peak"),
            "momentary": T("瞬时最大", "momentary max")}[k], rotation=90, fontsize=6, color=H.MUTED, va="bottom", ha="right")
a1.set_xlabel(T("关节转矩 / N·m", "Joint torque / N·m"), fontsize=7.2)
a1.set_ylabel(T("全桥输出 / (mV/V)", "Full-bridge output / (mV/V)"), fontsize=7.2)
a1.legend(fontsize=6.4, frameon=False, loc="upper left")
a1.tick_params(labelsize=6.3)
a1.set_title(T(f"(b) Ø{D:.0f}/Ø{d:.0f} 空心轴上的全桥输出（K = {GF:.1f}）", f"(b) Full-bridge output on the Ø{D:.0f}/Ø{d:.0f} hollow shaft (K = {GF:.1f})"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig8_1_1")

out(D=D, d=d, Wp=Wp, E=ST["E"], nu=ST["nu"], G=ST["G"], G_check=G_check, E_al=AL["E"], nu_al=AL["nu"], G_al=AL["G"], GF=GF, hd_size=hd["size"],
    T_rated=TQ["rated"], T_repeat=TQ["repeat"], T_mom=TQ["momentary"],
    tau_rated=res["rated"][0], tau_repeat=res["repeat"][0], tau_mom=res["momentary"][0],
    e_rated=res["rated"][1] * 1e6, e_repeat=res["repeat"][1] * 1e6, e_mom=res["momentary"][1] * 1e6, e_repeat_al=res_al["repeat"][1] * 1e6,
    out_rep=out_rep, out_rep_al=out_rep_al, al_ratio=out_rep_al / out_rep, eps_read=EPS_READ * 1e6, T_read=T_read,
    tau_need=tau_need, d_need=d_need, wall_need=(D - d_need) / 2, sy=ST["sy"], tau_y=ST["sy"] / math.sqrt(3), S_mom=ST["sy"] / math.sqrt(3) / res["momentary"][0])
