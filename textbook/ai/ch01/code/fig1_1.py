"""1.1 节的示意图。

图 1.1.1：智能体与环境的交互回路：传感器得到观测，智能体函数选出动作，执行器作用于环境；性能度量在回路之外评价环境状态的序列。
图 1.1.2：人工智能、机器学习、深度学习、大模型的包含关系，各附代表性的方法。
"""
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS


def box(ax, x, y, w, h, text, fc, ec=C["ink"], fs=11, weight="normal"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=ec, lw=1.2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=C["ink"], weight=weight)


def arrow(ax, p, q, text="", side=0.0, color=C["ink"], rad=0.0, fs=10):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=14, lw=1.4, color=color,
                                 connectionstyle=f"arc3,rad={rad}"))
    if text:
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        ax.text(mx, my + side, text, ha="center", va="center", fontsize=fs, color=color)


# ---------------------------------------------------------------- 图 1.1.1
fig, ax = plt.subplots(figsize=(8.6, 4.4))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5)
ax.axis("off")
# 智能体（左）与环境（右）
ax.add_patch(FancyBboxPatch((0.3, 0.7), 4.4, 3.6, boxstyle="round,pad=0.02,rounding_size=0.15", fc="#eef3f8",
                            ec=C["z"], lw=1.5))
ax.text(0.5, 4.05, T("智能体", "Agent"), fontsize=12, weight="bold", color=C["z"])
box(ax, 1.4, 3.1, 1.6, 0.7, T("传感器", "Sensors"), "#ffffff")
box(ax, 1.4, 1.4, 1.6, 0.7, T("执行器", "Actuators"), "#ffffff")
box(ax, 3.5, 2.25, 1.9, 1.3, T("智能体函数\n$a_t = f(o_1,\\dots,o_t)$", "Agent function\n$a_t = f(o_1,\\dots,o_t)$"),
    "#fdf3dc", fs=10)
arrow(ax, (2.2, 3.0), (2.6, 2.6))
arrow(ax, (2.6, 1.9), (2.2, 1.5))
ax.add_patch(FancyBboxPatch((6.2, 0.7), 3.4, 3.6, boxstyle="round,pad=0.02,rounding_size=0.15", fc="#f1f6ef",
                            ec=C["y"], lw=1.5))
ax.text(6.4, 4.05, T("环境", "Environment"), fontsize=12, weight="bold", color=C["y"])
ax.text(7.9, 2.5, T("状态 $s_t$\n（邮箱、路况、棋盘、\n车间里的零件……）", "State $s_t$\n(mailbox, traffic, board,\nparts in a workshop...)"),
        ha="center", va="center", fontsize=10, color=C["ink"])
arrow(ax, (6.2, 3.3), (2.25, 3.3), T("观测 $o_t$", "observation $o_t$"), side=0.22, rad=0.0)
arrow(ax, (2.25, 1.2), (6.2, 1.2), T("动作 $a_t$", "action $a_t$"), side=-0.22, rad=0.0)
ax.text(5.0, 0.25, T("性能度量：评价环境状态的序列 $s_1, s_2, \\dots$（不是智能体自己说了算）",
                     "Performance measure: judges the sequence of states $s_1, s_2, \\dots$ (not the agent's own opinion)"),
        ha="center", fontsize=9.5, color=C["accent"])
figure(fig, "fig1_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.1.2
fig, ax = plt.subplots(figsize=(8.2, 4.6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5.6)
ax.axis("off")
layers = [((5.0, 2.8), 9.6, 5.3, "#eef3f8", C["z"], T("人工智能", "Artificial intelligence"),
           T("搜索、逻辑推理、规划、知识表示、专家系统……", "search, logic, planning, knowledge representation, expert systems..."), 4.95),
          ((5.6, 2.45), 7.8, 4.0, "#f1f6ef", C["y"], T("机器学习", "Machine learning"),
           T("决策树、支持向量机、贝叶斯方法、强化学习……", "decision trees, SVMs, Bayesian methods, RL..."), 4.0),
          ((6.2, 2.05), 5.7, 2.8, "#fdf3dc", C["accent"], T("深度学习", "Deep learning"),
           T("卷积网络、循环网络、Transformer……", "CNNs, RNNs, Transformers..."), 3.1),
          ((6.8, 1.65), 3.4, 1.4, "#fbe9e7", C["x"], T("大模型", "Foundation models"),
           T("GPT、Llama、DeepSeek……", "GPT, Llama, DeepSeek..."), 1.85)]
for (cx, cy), w, h, fc, ec, name, ex, ty in layers:
    ax.add_patch(Ellipse((cx, cy), w, h, fc=fc, ec=ec, lw=1.6))
for (cx, cy), w, h, fc, ec, name, ex, ty in layers:
    ax.text(cx - w / 2 + (0.9 if w > 4 else 0.45), ty, name, fontsize=11.5, weight="bold", color=ec, va="center")
    ax.text(cx - w / 2 + (0.9 if w > 4 else 0.45), ty - 0.38, ex, fontsize=8.6, color=C["ink"], va="center")
figure(fig, "fig1_1_2")
plt.close(fig)
