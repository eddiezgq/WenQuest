"""第 138 轮 G4.6：送布牙轨迹图——机构实际轨迹（g4_feed.kin，送布机构.json 的尺寸和各档调节器角）对 sewcore 的椭圆。

    python3 tools/wqls/g4_feed_fig.py      → docs/设计/WQ-LS/G4/送布组_轨迹.png

左：正缝 1–5 mm 五档（实线：机构；虚线：sewcore 椭圆），针板面 z 0；右：5 mm 正缝和 5 mm 倒缝，牙顶高出针板的那一段加粗。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402

for _f in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",):
    if Path(_f).exists():
        font_manager.fontManager.addfont(_f)
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE)]
import g4_feed as F  # noqa: E402

G4 = ROOT / "docs" / "设计" / "WQ-LS" / "G4"
INK, MUTED, ACC, ACC2 = "#1f2933", "#7b8794", "#2f6fb3", "#c2552d"
STEPS = ["#9ec5e8", "#6fa6d6", "#3f86c4", "#2b67a3", "#1b4677"]      # 一个色相由浅到深：针距越大越深


def main():
    D = json.loads((G4 / "送布机构.json").read_text(encoding="utf-8"))
    p = dict(D["params"])
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw=dict(width_ratios=[1.25, 1]))
    for i, st in enumerate([s for s in D["settings"] if not s["reverse"]]):
        k = F.kin(p, np.radians(st["alpha_deg"]))
        X, Y, _ = F.target(st["s"], False)
        ym = k["y"] - k["y"].mean()
        a.plot(np.append(ym, ym[0]), np.append(k["z"], k["z"][0]), color=STEPS[i], lw=2, label=f"{st['s']:g} mm")
        a.plot(np.append(X, X[0]), np.append(Y, Y[0]), color=STEPS[i], lw=1, ls=(0, (3, 2)))
    a.axhline(0, color=INK, lw=0.8)
    a.text(-1.9, 0.05, "针板面", color=MUTED, fontsize=8)
    a.set_xlabel("前后 y / mm（往后送布为正）")
    a.set_ylabel("上下 z / mm")
    a.set_title("正缝 1–5 mm：实线是机构，虚线是 sewcore 椭圆", loc="left", fontsize=10)
    a.legend(frameon=False, fontsize=8, title="针距", title_fontsize=8, loc="lower right")
    a.set_aspect("equal")
    a.grid(color="#eef0f2", lw=0.6)
    for rev, col, lab in ((False, ACC, "5 mm 正缝"), (True, ACC2, "5 mm 倒缝")):
        st = [s for s in D["settings"] if s["reverse"] == rev and s["s"] == 5.0][0]
        k = F.kin(p, np.radians(st["alpha_deg"]))
        ym, z = k["y"] - k["y"].mean(), k["z"]
        b.plot(np.append(ym, ym[0]), np.append(z, z[0]), color=col, lw=1.2, label=lab)
        up = z > 0
        b.plot(np.where(up, ym, np.nan), np.where(up, z, np.nan), color=col, lw=3.2, solid_capstyle="round")
        b.annotate("", xy=(ym[up][-1], z[up][-1]), xytext=(ym[up][-4], z[up][-4]), arrowprops=dict(arrowstyle="->", color=col, lw=1.4))
    b.axhline(0, color=INK, lw=0.8)
    b.set_xlabel("前后 y / mm")
    b.set_title("正缝、倒缝（粗线：牙露出针板、送布的一段）", loc="left", fontsize=10)
    b.legend(frameon=False, fontsize=8, loc="lower right")
    b.set_aspect("equal")
    b.grid(color="#eef0f2", lw=0.6)
    for ax in (a, b):
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
    fig.tight_layout()
    fig.savefig(G4 / "送布组_轨迹.png", dpi=160)
    print("ok", G4 / "送布组_轨迹.png")


if __name__ == "__main__":
    main()
