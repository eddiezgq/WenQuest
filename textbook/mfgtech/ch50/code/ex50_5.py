"""50.5 节：SH-301 的工艺路线——加工阶段、顺序检查；两种排错的路线，AI 工艺评审员各提几条意见（算例 50.5.1）；
图 50.5.1 工艺路线与加工阶段。"""
import copy

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import _mfg as M
from bookout import T, figure, out, style

p = M.plan()
ops = p["operations"]
f0 = M.review(p)
assert f0 == []


def reorder(src, i, j):
    q = copy.deepcopy(src)
    o = q["operations"]
    o[i], o[j] = o[j], o[i]
    for k, x in enumerate(o):
        x["seq"] = 10 * (k + 1)
    return q


wrong1 = reorder(p, 2, 3)             # 调质与精车对调：先精车后调质
wrong2 = reorder(p, 4, 5)             # 铣键槽与磨外圆对调：磨完再铣键槽
f1 = [x for x in M.review(wrong1) if x["rule"] == "顺序"]
f2 = [x for x in M.review(wrong2) if x["rule"] == "顺序"]
assert f1 and f2
out(n1=len(f1), t1=f1[0]["text"], lv1="必须改" if f1[0]["level"] == "error" else "建议", n2=len(f2), t2=f2[0]["text"],
    lv2="必须改" if f2[0]["level"] == "error" else "建议")

# ---- 图 50.5.1：工艺路线（工序框按加工阶段着色，下方注工作中心与单件工时）
NAME = {"blank": ("毛坯", "blank"), "rough": ("粗加工", "roughing"), "qt": ("热处理", "heat treatment"), "finish": ("半精—精加工", "finishing"),
        "keyway": ("半精加工（键槽）", "semi-finishing (keyway)"), "grind": ("精加工（磨削）", "finishing (grinding)"), "inspect": ("检验", "inspection")}
plt = style()
fig, ax = plt.subplots(figsize=(7.2, 2.6))
for i, o in enumerate(ops):
    st = M.stage(o["operation"])
    x = i * 1.55
    ax.add_patch(FancyBboxPatch((x, 0), 1.25, 0.8, boxstyle="round,pad=0.02,rounding_size=0.1", fc=M.STAGE_COLOR[st], ec="none", alpha=0.9))
    zh, en = o["operation"].split(" ", 1)
    ax.text(x + 0.625, 0.52, f"{o['seq']}", ha="center", fontsize=9, color="white")
    ax.text(x + 0.625, 0.27, T(zh, en), ha="center", fontsize=9.5 if T(zh, en) == zh else 7.5, color="white", weight="bold")
    ax.text(x + 0.625, -0.2, o["workstation"].split(" ")[-1], ha="center", fontsize=8, color=M.INK)
    ax.text(x + 0.625, -0.42, f"{o['minutes']} min", ha="center", fontsize=8, color=M.MUTED)
    ax.text(x + 0.625, 1.0, T(*NAME[st]), ha="center", fontsize=7.8, color=M.STAGE_COLOR[st])
    if i < len(ops) - 1:
        ax.add_patch(FancyArrowPatch((x + 1.27, 0.4), (x + 1.53, 0.4), arrowstyle="-|>", mutation_scale=9, color=M.INK, lw=0.9))
ax.set_xlim(-0.1, len(ops) * 1.55); ax.set_ylim(-0.6, 1.2); ax.axis("off")
figure(fig, "fig50_5_1")
