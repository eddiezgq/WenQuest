"""8.4 梁的弯曲应力与切应力：UR5e 小臂（铝合金管，外径 75 mm、壁厚 2 mm，本书设定，与第 5 章同一量级）伸直水平、持 5 kg 时，
肘关节处（小臂根部）截面的弯矩和剪力（第 7 章的模型：连杆质量与长度取零件库的 MJCF）；
截面上弯曲正应力和切应力的分布；与同样截面积（同样质量）的实心圆杆、方管、实心矩形比较（算例 8.4.1、8.4.2，图 8.4.1）。
σ = M·y / I；薄壁圆管 τ_max = 2V / A（在中性轴处）；实心圆 τ_max = 4V / (3A)；矩形 τ_max = 3V / (2A)。"""
import math
import sys
from pathlib import Path

import numpy as np

import _ch8 as H
from bookout import T, figure, out, style

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ch07" / "code"))
import _ch7 as C7                     # noqa: E402

AL = H.mat("6061-T6")
arm = C7.ur5e_arm(5.0)
L1 = C7.ur5e()["L_ua"]
out_items = arm[1:]                                     # 肘关节以外：小臂、腕部、负载
M = sum(m * C7.G * (x - L1) for _, m, x in out_items) * 1e3      # N·mm
V = sum(m * C7.G for _, m, x in out_items)                        # N
D, t = 75.0, 2.0
A = math.pi / 4 * (D ** 2 - (D - 2 * t) ** 2)
I_t = math.pi / 64 * (D ** 4 - (D - 2 * t) ** 4)
W_t = I_t / (D / 2)
sig_t = M / W_t
tau_t = 2 * V / A
# 同面积的其他截面
d_s = math.sqrt(4 * A / math.pi)
W_s = math.pi * d_s ** 3 / 32
s_sq = (A + 4 * t * t) / (4 * t)                        # 方管外边长：A = s² − (s − 2t)²
I_sq = (s_sq ** 4 - (s_sq - 2 * t) ** 4) / 12
W_sq = I_sq / (s_sq / 2)
b_r = math.sqrt(A / 2)                                   # 实心矩形，高 = 2 × 宽
W_r = b_r * (2 * b_r) ** 2 / 6
SECS = [(T("圆管 Ø75×2", "tube Ø75×2"), W_t, 2 * V / A), (T(f"方管 □{s_sq:.0f}×2", f"square tube □{s_sq:.0f}×2"), W_sq, None),
        (T(f"实心矩形 {b_r:.0f}×{2 * b_r:.0f}", f"solid rectangle {b_r:.0f}×{2 * b_r:.0f}"), W_r, 1.5 * V / A),
        (T(f"实心圆 Ø{d_s:.1f}", f"solid round Ø{d_s:.1f}"), W_s, 4 * V / (3 * A))]

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.0, 1.15]})
y = np.linspace(-D / 2, D / 2, 300)
a0.plot(M * y / I_t, y, color="#1f77b4", lw=1.4, label=T("弯曲正应力 σ", "bending stress σ"))
tau_y = tau_t * np.sqrt(np.clip(1 - (2 * y / D) ** 2, 0, None))           # 薄壁圆管：τ ∝ cos φ
a0.plot(tau_y * 20, y, color="#d62728", lw=1.2, ls="--", label=T("切应力 τ（放大 20 倍）", "shear stress τ (×20)"))
a0.axvline(0, color=H.MUTED, lw=0.5)
a0.axhline(0, color=H.MUTED, lw=0.5)
a0.set_xlabel(T("应力 / MPa", "Stress / MPa"), fontsize=7.2)
a0.set_ylabel(T("离中性轴的距离 y / mm", "Distance from the neutral axis y / mm"), fontsize=7.2)
a0.legend(fontsize=6.2, frameon=False, loc="lower right")
a0.tick_params(labelsize=6.3)
a0.set_title(T("(a) 小臂根部截面上的应力", "(a) Stresses at the forearm root"), fontsize=7.4)
a1.barh(range(len(SECS)), [M / w for _, w, _ in SECS], color=["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"])
for i, (n, w, _) in enumerate(SECS):
    a1.text(M / w + 0.3, i, f"{M / w:.1f} MPa", va="center", fontsize=6.4)
a1.set_yticks(range(len(SECS)))
a1.set_yticklabels([n for n, _, _ in SECS], fontsize=6.6)
a1.invert_yaxis()
a1.set_xlim(0, max(M / w for _, w, _ in SECS) * 1.3)
a1.set_xlabel(T("最大弯曲应力 / MPa", "Maximum bending stress / MPa"), fontsize=7.2)
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 同样质量的四种截面", "(b) Four sections of the same mass"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig8_4_1")

out(D=D, t=t, M=M / 1e3, V=V, A=A, I=I_t, W=W_t, sig=sig_t, tau=tau_t, tau_ratio=sig_t / tau_t, sy=AL["sy"], S=AL["sy"] / sig_t,
    d_s=d_s, s_sq=s_sq, b_r=b_r, sig_sq=M / W_sq, sig_r=M / W_r, sig_s=M / W_s, ratio_s=W_t / W_s, ratio_sq=W_sq / W_t, ratio_r=W_t / W_r)
