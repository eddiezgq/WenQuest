"""2.1 质量功能展开：WQR-105 的质量屋（客户需求的权重 × 关系矩阵 → 工程特性的重要度）（算例 2.1.1，图 2.1.1）。
工程特性的目标值取自数字工厂（参数配置器、检验模板、售价）；客户需求的权重与关系强度是示意的评审打分。"""
import numpy as np

import _ch2 as H
from bookout import T, figure, out, style

F, C = H.F, H.C
wq = C._wqr()
life_default = next(p["default"] for p in wq["params"] if p["key"] == "life_h")
NEEDS = [  # (中文, English, 权重 1–5)
    ("转矩够大，偶尔过载也不坏", "enough torque, survives overloads", 5),
    ("用得久、少维修", "long life, little maintenance", 4),
    ("价格便宜", "low price", 4),
    ("运转安静", "runs quietly", 3),
    ("体积小、好安装", "compact, easy to install", 3),
    ("发热小、省电", "runs cool, saves power", 2),
]
CHARS = [  # (中文, English, 目标值)
    ("额定输出转矩", "rated output torque", "{:.0f} N·m".format(C.T_RATED)),
    ("轴承寿命 L10", "bearing life L10", "≥ {:,} h".format(life_default).replace(",", " ")),
    ("出厂价", "selling price", "{:.0f} USD".format(F.FG_SELLING_PRICE)),
    ("齿面硬度（小齿轮）", "pinion tooth hardness", "58–62 HRC"),
    ("两级中心距", "center distances", "{:.0f} / {:.0f} mm".format(C.A1, C.A2)),
    ("总效率", "overall efficiency", "{:.3f}".format(C.ETA)),
]
# 关系强度（行：需求；列：工程特性）：9 强、3 中、1 弱、0 无（评审小组的打分，示意）
REL = np.array([
    [9, 3, 1, 3, 1, 0],
    [3, 9, 1, 9, 0, 1],
    [3, 1, 9, 3, 3, 0],
    [0, 1, 1, 3, 0, 3],
    [3, 0, 3, 0, 9, 0],
    [0, 0, 0, 1, 0, 9],
])
w = np.array([n[2] for n in NEEDS], float)
score = w @ REL
rel_pct = score / score.sum() * 100
order = np.argsort(-score)

# ---------------------------------------------------------------- 图 2.1.1：质量屋（主体）
plt = style()
fig, ax = plt.subplots(figsize=(6.9, 4.0))
nr, nc = REL.shape
x0, y0 = 3.2, 0.0
for j, (zh, en, tgt) in enumerate(CHARS):
    ax.text(x0 + j + 0.5, nr + 0.15, T(zh, en), rotation=60, ha="left", va="bottom", fontsize=7.5)
for i, (zh, en, wt) in enumerate(NEEDS):
    y = nr - 1 - i
    ax.text(x0 - 0.65, y + 0.5, T(zh, en), ha="right", va="center", fontsize=7.5)
    ax.text(x0 - 0.3, y + 0.5, str(wt), ha="center", va="center", fontsize=8, weight="bold", color="#2c6fbb")
    for j in range(nc):
        r = REL[i, j]
        ax.add_patch(H.FancyBboxPatch((x0 + j + 0.04, y + 0.04), 0.92, 0.92, boxstyle="square,pad=0", fc=H.PALE["gray"] if r == 0 else
                                      {1: "#e8eef7", 3: "#a9c4e8", 9: "#2c6fbb"}[r], ec="white", lw=1))
        sym = {9: "●", 3: "○", 1: "△"}.get(r, "")
        ax.text(x0 + j + 0.5, y + 0.5, sym, ha="center", va="center", fontsize=9, color="white" if r == 9 else H.INK)
ax.text(x0 - 0.3, nr + 0.1, T("权重", "weight"), ha="center", va="bottom", fontsize=7, color="#2c6fbb")
for j in range(nc):
    ax.text(x0 + j + 0.5, -0.45, "{:.0f}".format(score[j]), ha="center", va="center", fontsize=8, weight="bold")
    ax.text(x0 + j + 0.5, -0.95, "{:.0f}%".format(rel_pct[j]), ha="center", va="center", fontsize=7.5, color=H.MUTED)
    ax.text(x0 + j + 0.5, -1.45, CHARS[j][2], ha="center", va="center", fontsize=6.3)
ax.text(x0 - 0.65, -0.45, T("重要度 Σ权重×关系", "importance Σ weight × relation"), ha="right", va="center", fontsize=7.5)
ax.text(x0 - 0.65, -0.95, T("相对重要度", "relative"), ha="right", va="center", fontsize=7.5)
ax.text(x0 - 0.65, -1.45, T("目标值（数字工厂）", "target (digital factory)"), ha="right", va="center", fontsize=7.5)
ax.text(x0 + nc + 0.2, nr - 0.3, T("● 强 9\n○ 中 3\n△ 弱 1", "● strong 9\n○ medium 3\n△ weak 1"), fontsize=7, va="top")
ax.set_xlim(-0.2, x0 + nc + 1.4)
ax.set_ylim(-1.8, nr + 2.6)
ax.axis("off")
fig.tight_layout()
figure(fig, "fig2_1_1")

out(n_needs=len(NEEDS), n_chars=len(CHARS), top=T(CHARS[order[0]][0], CHARS[order[0]][1]), top2=T(CHARS[order[1]][0], CHARS[order[1]][1]),
    top_pct=rel_pct[order[0]], top2_pct=rel_pct[order[1]], last=T(CHARS[order[-1]][0], CHARS[order[-1]][1]), last_pct=rel_pct[order[-1]],
    s_torque=score[0], s_life=score[1], w_torque=NEEDS[0][2], T_rated=C.T_RATED, life="{:,}".format(life_default).replace(",", " "), price=F.FG_SELLING_PRICE,
    eta=C.ETA, a1=C.A1, a2=C.A2, s_hard=score[3], hard_pct=rel_pct[3])
