"""图 39.5.1：算例 39.5.1 的标定结果。(a) 加载、卸载的读数（3 次平均）与拟合直线；(b) 读数与拟合直线之差，看出非线性与迟滞。"""
import numpy as np

import ex39_5 as ex
from bookout import COLORS as C, figure, style

plt = style()
F = ex.loads
up, down = ex.up.mean(0) * 1e3, ex.down.mean(0) * 1e3          # mV
a, b = ex.a * 1e3, ex.b * 1e3
fit = a + b * F

fig, (p, q) = plt.subplots(1, 2, figsize=(10, 3.5))
p.plot(F, fit, color=C["z"], lw=1.2, label="拟合直线")
p.plot(F, up, "o", color=C["x"], ms=6, label="加载")
p.plot(F, down, "s", mfc="none", color=C["y"], ms=8, mew=1.3, label="卸载")
p.set_xlabel("力 F / N")
p.set_ylabel("输出 / mV")
p.legend(fontsize=9, frameon=False, loc="upper left")
p.set_title("(a) 标定曲线", fontsize=10.5)

q.axhline(0, color=C["muted"], lw=0.8)
q.plot(F, up - fit, "o-", color=C["x"], ms=5, lw=1.2, label="加载")
q.plot(F, down - fit, "s-", mfc="none", color=C["y"], ms=6, lw=1.2, label="卸载")
k = int(np.argmax(np.abs(down - up)))
q.annotate("", xy=(F[k], down[k] - fit[k]), xytext=(F[k], up[k] - fit[k]), arrowprops=dict(arrowstyle="<->", color=C["ink"], lw=0.9))
q.text(F[k] + 2, (up[k] + down[k]) / 2 - fit[k], "迟滞", fontsize=9, va="center")
q.set_xlabel("力 F / N")
q.set_ylabel("读数 − 拟合 / mV")
q.legend(fontsize=9, frameon=False, loc="upper center", ncol=2)
q.set_title(f"(b) 偏离拟合直线（满量程输出 {ex.y_fs * 1e3:.0f} mV）", fontsize=10.5)
for ax in (p, q):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig39_5_1")
plt.close(fig)
