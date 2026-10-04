"""图 4.3.1：斜渐近线与铅直渐近线；两节连杆接近伸直时的灵敏度。"""
import json
import math
from pathlib import Path

import numpy as np

from _fig import ACC, BLUE, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
f = lambda x: (x * x + 1) / (x - 1)
for xs in (np.linspace(-6, 0.9, 400), np.linspace(1.1, 8, 400)):
    a1.plot(xs, f(xs), color=BLUE, lw=2)
x = np.linspace(-6, 8, 10)
a1.plot(x, x + 1, color=RED, lw=1.2, ls="--", label="$y = x + 1$")
a1.axvline(1, color=RED, lw=1.2, ls=":", label="$x = 1$")
a1.set_ylim(-15, 20)
a1.legend(fontsize=9, frameon=False, loc="upper left")
a1.set_title(T("(x² + 1)/(x − 1) 的渐近线", "Asymptotes of (x² + 1)/(x − 1)"), fontsize=10)
clean(a1)
e = json.loads((Path(__file__).resolve().parents[2] / "models" / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
js = {j["name"]: j for j in e["robot"]["joints"]}
l1, l2 = js["elbow_joint"]["origin"]["xyz"][2], js["wrist_1_joint"]["origin"]["xyz"][2]
R = l1 + l2
r = np.linspace(0.70, R - 1e-6, 4000)
c = (r * r - l1 * l1 - l2 * l2) / (2 * l1 * l2)
sens = r / (l1 * l2 * np.sqrt(1 - c * c))          # |dθ₂/dr| = r / (l₁ l₂ sin θ₂)
a2.plot(r, sens, color=ACC, lw=2)
a2.axvline(R, color=RED, lw=1.2, ls=":")
a2.text(R - 0.003, 2e3, T("r = R（伸直）", "r = R (straight)"), color=RED, ha="right", fontsize=9)
a2.set_yscale("log")
a2.set_ylim(1, 1e4)
a2.set_xlabel(T("腕心到肩的距离 r / m", "wrist distance r / m"))
a2.set_ylabel(T("灵敏度 / (rad/m)（对数坐标）", "sensitivity / (rad/m), log scale"))
a2.set_title(T("接近伸直时肘关节的灵敏度趋于无穷", "Elbow sensitivity blows up near full stretch"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig4_3_1")
