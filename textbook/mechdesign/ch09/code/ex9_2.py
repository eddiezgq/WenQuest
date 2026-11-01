"""9.2 能量法与卡氏定理。

算例 9.2.1  机器人点焊钳的 C 形钳体（第 8 章算例 8.8.1 的同一个：矩形截面 20 × 60、内半径 50、电极力 3 kN、电极力作用线到弯段
            形心 250 mm；钢）。把钳体看成“两段直臂 + 半圆弯段”，直臂长 = 250 − r_c。两个电极把钳口往外撑，求钳口张开量：
            δ = ∂U/∂F，U 含弯曲、轴力、剪切三部分应变能；分别列出各部分、各段的贡献；再用数值积分对卡氏定理的结果作核对。
算例 9.2.2  生活中的例子：开口钢丝环（如钥匙扣上的开口圈，钢丝 Ø1.5、环的中径 25 mm，本书设定），在环所在平面内、沿开口处的切线方向以 5 N 把两端拉开，
            张开量 δ = 3πFR³/(EI)（只计弯曲）。
图 9.2.1。
"""
import math

import numpy as np

import _ch9 as H
from bookout import T, figure, out, style

ST = H.mat("Q235")                     # 钳体：结构钢焊接件（本书设定）；E、ν 取材料库
E, Gm, nu = ST["E"], ST["G"], ST["nu"]
b, h, ri = 20.0, 60.0, 50.0
rc = ri + h / 2
F, ARM = 3000.0, 250.0
La = ARM - rc                          # 直臂长度：电极力作用线到弯段起点
A, I = b * h, b * h ** 3 / 12
KS = 1.2                               # 矩形截面的剪切形状系数

# 直臂（两段）：x 从电极量起，M = F x，V = F，N = 0
U_arm_b = 2 * F ** 2 * La ** 3 / (6 * E * I)
U_arm_s = 2 * KS * F ** 2 * La / (2 * Gm * A)
# 半圆弯段：θ 从上臂与弯段相接处量起（0…π），M = F (La + rc sinθ)，N = F sinθ，V = F cosθ，ds = rc dθ
th = np.linspace(0, math.pi, 4001)
M = F * (La + rc * np.sin(th))
U_c_b = np.trapezoid(M ** 2 / (2 * E * I) * rc, th)
U_c_n = np.trapezoid((F * np.sin(th)) ** 2 / (2 * E * A) * rc, th)
U_c_s = np.trapezoid(KS * (F * np.cos(th)) ** 2 / (2 * Gm * A) * rc, th)
# 卡氏定理：U 是 F 的二次式，δ = ∂U/∂F = 2U/F
parts = {"arm_b": 2 * U_arm_b / F, "arm_s": 2 * U_arm_s / F, "c_b": 2 * U_c_b / F, "c_n": 2 * U_c_n / F, "c_s": 2 * U_c_s / F}
delta = sum(parts.values())
# 解析式（弯段弯曲部分）：∫(La + rc sinθ)² rc dθ = rc (π La² + 4 La rc + π rc²/2)
c_b_formula = F * rc * (math.pi * La ** 2 + 4 * La * rc + math.pi * rc ** 2 / 2) / (E * I)
bend_pct = (parts["arm_b"] + parts["c_b"]) / delta * 100
# 张开量随截面高度的变化（同样的宽度、内半径、力作用线位置）
hs = np.linspace(40, 100, 61)


def open_of(hh):
    Ii, Ai, rcc = b * hh ** 3 / 12, b * hh, ri + hh / 2
    La_ = ARM - rcc
    d = 2 * F * La_ ** 3 / (3 * E * Ii) + 2 * KS * F * La_ / (Gm * Ai)
    d += F * rcc * (math.pi * La_ ** 2 + 4 * La_ * rcc + math.pi * rcc ** 2 / 2) / (E * Ii)
    d += F * rcc * math.pi / 2 / (E * Ai) + KS * F * rcc * math.pi / 2 / (Gm * Ai)
    return d


d_h = np.array([open_of(x) for x in hs])
d80 = open_of(80.0)
mass_of = lambda hh: b * hh * (2 * (ARM - (ri + hh / 2)) + math.pi * (ri + hh / 2))     # 钳体体积 ∝ 质量

# ---------------------------------------------------------------- 开口钢丝环
SP = H.mat("45-QT")                    # 弹簧钢丝的 E 与一般钢相同
dw, Dm, Fr = 1.5, 25.0, 5.0
R = Dm / 2
Iw = math.pi * dw ** 4 / 64
d_ring = 3 * math.pi * Fr * R ** 3 / (SP["E"] * Iw)
s_ring = Fr * 2 * R * (dw / 2) / Iw                     # 开口对面的截面弯矩最大：M = F · 2R

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
keys = ["arm_b", "c_b", "c_n", "arm_s", "c_s"]
nm = {"arm_b": T("直臂弯曲", "arms, bending"), "c_b": T("弯段弯曲", "curved part, bending"), "c_n": T("弯段轴力", "curved part, axial"),
      "arm_s": T("直臂剪切", "arms, shear"), "c_s": T("弯段剪切", "curved part, shear")}
a0.barh(range(len(keys)), [parts[k] * 1e3 for k in keys], color=["#1f77b4", "#2ca02c", "#9467bd", "#ff7f0e", "#d62728"])
for i, k in enumerate(keys):
    a0.text(parts[k] * 1e3 + 2, i, f"{parts[k] * 1e3:.1f} µm", va="center", fontsize=6.4)
a0.set_yticks(range(len(keys)))
a0.set_yticklabels([nm[k] for k in keys], fontsize=6.6)
a0.invert_yaxis()
a0.set_xlim(0, max(parts.values()) * 1e3 * 1.3)
a0.set_xlabel(T("对钳口张开量的贡献 / µm", "Contribution to the jaw opening / µm"), fontsize=7.2)
a0.tick_params(labelsize=6.3)
a0.set_title(T(f"(a) 3 kN 时钳口张开 {delta * 1e3:.0f} µm", f"(a) Jaw opening {delta * 1e3:.0f} µm at 3 kN"), fontsize=7.4)
a1.plot(hs, d_h * 1e3, color="#1f77b4", lw=1.5)
a1.plot([h], [delta * 1e3], "o", color="#d62728", ms=4)
a1.annotate(T(f"h = {h:.0f} mm", f"h = {h:.0f} mm"), (h, delta * 1e3), xytext=(h + 6, delta * 1e3 + 40), fontsize=6.4,
            arrowprops=dict(arrowstyle="-", color=H.MUTED, lw=0.6))
a1.set_xlabel(T("截面高度 h / mm（宽 20 mm）", "Section depth h / mm (width 20 mm)"), fontsize=7.2)
a1.set_ylabel(T("钳口张开量 / µm", "Jaw opening / µm"), fontsize=7.2)
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 截面高度的影响", "(b) Effect of the section depth"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig9_2_1")

out(b=b, h=h, ri=ri, rc=rc, F=F / 1e3, ARM=ARM, La=La, E=E, Gm=Gm, KS=KS,
    d_arm_b=parts["arm_b"] * 1e3, d_c_b=parts["c_b"] * 1e3, d_c_n=parts["c_n"] * 1e3, d_arm_s=parts["arm_s"] * 1e3,
    d_c_s=parts["c_s"] * 1e3, delta=delta * 1e3, bend_pct=bend_pct, c_b_err=abs(c_b_formula / parts["c_b"] - 1) * 100,
    d80=d80 * 1e3, r80=delta / d80, mass_r80=mass_of(80.0) / mass_of(h), rc_h=rc / h, delta_mm=delta,
    dw=dw, Dm=Dm, Fr=Fr, d_ring=d_ring, s_ring=s_ring)
