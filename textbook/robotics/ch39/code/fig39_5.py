"""图 39.5.1：算例 39.5.1 的标定结果。(a) 加载、卸载的读数（3 次平均）与拟合直线；(b) 读数与拟合直线之差，看出非线性与迟滞。"""
import numpy as np

import ex39_5 as ex
from bookout import COLORS as C, T, figure, style

plt = style()
F = ex.loads
up, down = ex.up.mean(0) * 1e3, ex.down.mean(0) * 1e3          # mV
a, b = ex.a * 1e3, ex.b * 1e3
fit = a + b * F

fig, (p, q) = plt.subplots(1, 2, figsize=(10, 3.5))
p.plot(F, fit, color=C["z"], lw=1.2, label=T("拟合直线", "Fitted line"))
p.plot(F, up, "o", color=C["x"], ms=6, label=T("加载", "Loading"))
p.plot(F, down, "s", mfc="none", color=C["y"], ms=8, mew=1.3, label=T("卸载", "Unloading"))
p.set_xlabel(T("力 F / N", "Force F / N"))
p.set_ylabel(T("输出 / mV", "Output / mV"))
p.legend(fontsize=9, frameon=False, loc="upper left")
p.set_title(T("(a) 标定曲线", "(a) Calibration curve"), fontsize=10.5)

q.axhline(0, color=C["muted"], lw=0.8)
q.plot(F, up - fit, "o-", color=C["x"], ms=5, lw=1.2, label=T("加载", "Loading"))
q.plot(F, down - fit, "s-", mfc="none", color=C["y"], ms=6, lw=1.2, label=T("卸载", "Unloading"))
k = int(np.argmax(np.abs(down - up)))
q.annotate("", xy=(F[k], down[k] - fit[k]), xytext=(F[k], up[k] - fit[k]), arrowprops=dict(arrowstyle="<->", color=C["ink"], lw=0.9))
q.text(F[k] + 2, (up[k] + down[k]) / 2 - fit[k], T("迟滞", "Hysteresis"), fontsize=9, va="center")
q.set_xlabel(T("力 F / N", "Force F / N"))
q.set_ylabel(T("读数 − 拟合 / mV", "Reading − fit / mV"))
q.legend(fontsize=9, frameon=False, loc="lower left")
q.set_title(T(f"(b) 偏离拟合直线（满量程输出 {ex.y_fs * 1e3:.0f} mV）", f"(b) Deviation from the fitted line (full-scale output {ex.y_fs * 1e3:.0f} mV)"), fontsize=10.5)
for ax in (p, q):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig39_5_1")
plt.close(fig)
