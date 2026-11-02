"""19.2 节的示意图：为什么"越推越平"是均方误差的最优解本身。

图 19.2.1：（a）各波数推 n 步之后还剩多少振幅——高波数掉得最快；
（b）同一个真实场的两种预报：抹平的那个 RMSE 更小，保锐的那个看着像真的。
"""
import numpy as np

from _ch19 import (extreme_hits, field_from_complex, mode_correlation,
                   modes_forecast, modes_truth, mse_optimal_amplitude,
                   sharpness, spectrum)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
M, NX, STEP = 40, 256, 4
amp = spectrum(M)
rho1 = mode_correlation(M)
k = np.arange(1, M + 1)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 推几步之后每个波数还剩多少
for n, col, ls in ((1, C["z"], "-"), (2, C["y"], "-"), (4, C["accent"], "-"),
                   (8, C["x"], "-"), (16, C["muted"], "--")):
    a.semilogy(k, mse_optimal_amplitude(rho1, n), ls, color=col, lw=2.0,
               label=T(f"推 {n} 步", f"{n} steps"))
a.axhline(1.0, color=C["ink"], ls=":", lw=1.2)
a.annotate(T("真实场的振幅", "amplitude of the true field"), xy=(6, 1.0),
           xytext=(4.5, 1.35), fontsize=8.5, color=C["ink"])
a.annotate(T("小尺度先没：\n高波数的记忆最短",
             "small scales go first:\nhigh wavenumbers forget fastest"),
           xy=(9, 2e-3), xytext=(11, 1e-1), fontsize=8.5, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))
a.set_xlabel(T("波数 k（越大尺度越小）", "wavenumber k (larger = smaller scale)"))
a.set_ylabel(T("均方误差最优预测保留的振幅比例",
               "amplitude kept by the MSE-optimal forecast"))
a.set_xlim(1, 20)
a.set_ylim(1e-5, 3)
a.set_title(T("(a) 最优预测每推一步都把场压平一点",
              "(a) Every optimal step flattens the field a little"), fontsize=10)
a.legend(fontsize=8.5, loc="upper right", ncol=2)
a.grid(alpha=0.25, lw=0.5, which="both")

# ---------------- (b) 同一个真值的两种预报
g = np.random.default_rng(103)      # 挑一例与 300 例平均最接近的，免得拿特例说事
rho = rho1 ** STEP
z = modes_truth(amp, g)
z_opt, z_sharp = modes_forecast(z, amp, rho, g)
x = np.arange(NX) / NX * 2 * np.pi
truth = field_from_complex(z, NX)
f_opt = field_from_complex(z_opt, NX)
f_sharp = field_from_complex(z_sharp, NX)
rm = lambda f: np.sqrt(np.mean((f - truth) ** 2))

b.plot(x, truth, "-", color=C["ink"], lw=2.2, label=T("真实场", "truth"))
b.plot(x, f_sharp, "-", color=C["x"], lw=1.6,
       label=T(f"保锐：RMSE {rm(f_sharp):.2f}，锐度 {sharpness(f_sharp):.3f}",
               f"sharp: RMSE {rm(f_sharp):.2f}, sharpness {sharpness(f_sharp):.3f}"))
b.plot(x, f_opt, "-", color=C["z"], lw=2.4,
       label=T(f"抹平（均方误差最优）：RMSE {rm(f_opt):.2f}，锐度 {sharpness(f_opt):.3f}",
               f"smooth (MSE-optimal): RMSE {rm(f_opt):.2f}, sharpness {sharpness(f_opt):.3f}"))
th = np.quantile(truth, 0.95)
b.axhline(th, color=C["muted"], ls="--", lw=1.0)
b.annotate(T("极端事件门限（真值的 95 分位）", "extreme threshold (95th pct of truth)"),
           xy=(0.05, th), xytext=(0.05, th + 0.08), fontsize=8, color=C["muted"])
b.annotate(T("抹平之后够不着这条线了", "the smoothed field no longer reaches it"),
           xy=(x[np.argmax(f_opt)], f_opt[np.argmax(f_opt)]),
           xytext=(1.5, 1.30), fontsize=8.5, color=C["z"],
           arrowprops=dict(arrowstyle="->", color=C["z"], lw=1.0))
b.set_xlabel(T("位置", "position"))
b.set_ylabel(T("场的数值", "field value"))
b.set_title(T("(b) RMSE 更小的那个，反而抓不住极端",
              "(b) The lower-RMSE forecast is the one that misses extremes"), fontsize=10)
b.legend(fontsize=8, loc="lower center", framealpha=0.92)
b.margins(y=0.22)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig19_2_1")
