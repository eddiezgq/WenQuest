"""图 39.3.1：950 Hz 正弦以 1 kHz 采样，采样点落在 50 Hz（反相）的正弦上。"""
import math

import numpy as np

from bookout import COLORS as C, figure, style

plt = style()
fs, f = 1000.0, 950.0
t = np.linspace(0, 0.03, 3000)
n = np.arange(0, 31)
fig, ax = plt.subplots(figsize=(7.2, 2.8))
ax.plot(t * 1e3, np.sin(2 * math.pi * f * t), color=C["muted"], lw=0.6, label="950 Hz 原信号")
ax.plot(t * 1e3, -np.sin(2 * math.pi * 50 * t), color=C["x"], lw=2, label="采样后“看到”的 50 Hz")
ax.plot(n / fs * 1e3, np.sin(2 * math.pi * f * n / fs), "o", color=C["ink"], ms=4.5, label="采样点（1 kHz）")
ax.set_xlabel("时间 / ms")
ax.set_ylabel("幅值")
ax.legend(fontsize=8.5, frameon=False, loc="upper right", ncol=3)
ax.set_ylim(-1.3, 1.6)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig39_3_1")
plt.close(fig)
