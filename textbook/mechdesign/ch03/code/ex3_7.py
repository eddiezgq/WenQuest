"""3.7 三维参数化建模的草图：轴承座正面轮廓的约束求解——数自由度（欠约束、全约束、过约束），
改轴承外径时其余几何怎样跟着变；“设计意图”对不对，决定改参数以后模型还能不能用（算例 3.7.1，图 3.7.1）。"""
import math

import numpy as np

import _ch3 as H
from bookout import T, figure, out, style

PTS = ["A", "B", "C", "D", "E", "F", "G", "K", "O"]          # 底板 A-B-C…K、圆弧端点 E、F、圆心 O
IDX = {p: i for i, p in enumerate(PTS)}
NV = 2 * len(PTS) + 1                                          # 每点 2 个坐标 + 轴承孔半径 rb


def P(x, p):
    i = IDX[p]
    return x[2 * i], x[2 * i + 1]


def RB(x):
    return x[-1]


def geometric(x):
    """几何约束（不含任何尺寸）：水平、竖直、圆弧与竖线相切（端点与圆心同高）、对称、定位。
    “E、F 到圆心等距”不必加：由对称和相切已经推得出，加上就是冗余约束（CAD 会提示）。"""
    A, B, C, D, E, F, G, K, O = (P(x, p) for p in PTS)
    return [A[1] - B[1], B[0] - C[0], C[1] - D[1], D[0] - E[0], F[0] - G[0], G[1] - K[1], K[0] - A[0],   # 水平/竖直
            E[1] - O[1], F[1] - O[1],                                                                     # 圆弧在 E、F 与竖线相切
            A[0] + B[0], A[1],                                                                            # 底边中点在原点（定位）
            D[0] + G[0], O[0],                                                                            # 左右对称
            C[1] - K[1]]                                                                                  # 底板顶面等高


def dims(x, p, intent="good"):
    """尺寸约束：设计意图对（壁厚跟着轴承外径走）或不对（圆弧半径写死）"""
    A, B, C, D, E, F, G, K, O = (P(x, q) for q in PTS)
    r = [2 * RB(x) - p["D"], O[1] - A[1] - p["H"], B[0] - A[0] - p["L"], C[1] - B[1] - p["tb"]]
    if intent == "good":
        r.append(math.hypot(E[0] - O[0], E[1] - O[1]) - RB(x) - p["wall"])     # 壁厚 = Ro − D/2
    else:
        r.append(math.hypot(E[0] - O[0], E[1] - O[1]) - p["Ro_fixed"])          # 圆弧半径直接写数
    return r


def jac(f, x, h=1e-6):
    f0 = np.array(f(x))
    J = np.zeros((len(f0), len(x)))
    for j in range(len(x)):
        xx = x.copy()
        xx[j] += h
        J[:, j] = (np.array(f(xx)) - f0) / h
    return J


def dof(f, x):
    """剩余自由度 = 变量数 − 雅可比矩阵的秩；冗余约束数 = 约束数 − 秩"""
    J = jac(f, x)
    r = np.linalg.matrix_rank(J, tol=1e-6)
    return len(x) - r, J.shape[0] - r


def solve(f, x0, it=50):
    x = x0.copy()
    for _ in range(it):
        r = np.array(f(x))
        if np.max(np.abs(r)) < 1e-10:
            break
        dx = np.linalg.lstsq(jac(f, x), -r, rcond=None)[0]
        x = x + dx
    return x, float(np.max(np.abs(f(x))))


def guess(p):
    """草图的初始“手画”位置：大致像，尺寸不准"""
    L, H_, Ro, tb = p["L"] * 0.9, p["H"] * 1.1, p["Ro"] * 0.9, p["tb"] * 1.3
    pts = {"A": (-L / 2, 2), "B": (L / 2, -1), "C": (L / 2 + 3, tb), "D": (Ro, tb + 2), "E": (Ro - 2, H_ + 3), "F": (-Ro, H_),
           "G": (-Ro + 3, tb), "K": (-L / 2, tb - 2), "O": (1.5, H_)}
    x = np.zeros(NV)
    for k, v in pts.items():
        x[2 * IDX[k]], x[2 * IDX[k] + 1] = v
    x[-1] = p["D"] / 2 * 0.8
    return x


p7 = H.pillow_params("6207")
p7["Ro_fixed"] = p7["Ro"]
x0 = guess(p7)
x7, res7 = solve(lambda x: geometric(x) + dims(x, p7), x0)
dof_free, red_free = dof(geometric, x7)                         # 秩要在满足约束的位置上算
dof_full, red_full = dof(lambda x: geometric(x) + dims(x, p7), x7)
over = lambda x: geometric(x) + dims(x, p7) + [P(x, "E")[0] - P(x, "F")[0] - 2 * p7["Ro"]]   # 再注一个宽度 2Ro：多余
dof_over, red_over = dof(over, x7)
# 换成 6209：只改轴承外径一个参数（中心高、底板按 3.8 节的规则也跟着变），设计意图对与不对的两种草图
p9 = H.pillow_params("6209")
p9["Ro_fixed"] = p7["Ro"]
x9g, res9g = solve(lambda x: geometric(x) + dims(x, p9, "good"), x7)
x9b, res9b = solve(lambda x: geometric(x) + dims(x, p9, "bad"), x7)
wall_g = math.hypot(*(np.subtract(P(x9g, "E"), P(x9g, "O")))) - RB(x9g)
wall_b = math.hypot(*(np.subtract(P(x9b, "E"), P(x9b, "O")))) - RB(x9b)


def outline(x):
    A, B, C, D, E, F, G, K, O = (P(x, q) for q in PTS)
    R_ = math.hypot(E[0] - O[0], E[1] - O[1])
    arc = [(O[0] + R_ * math.cos(t), O[1] + R_ * math.sin(t)) for t in np.linspace(0, math.pi, 60)]
    base = [K, A, B, C, D, E] + arc + [F, G, K]
    hole = [(O[0] + RB(x) * math.cos(t), O[1] + RB(x) * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 90)]
    return base, hole


plt = style()
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.3), gridspec_kw={"width_ratios": [1, 1.15]})
# (a) 手画的草图 → 约束求解后的草图
ax = axs[0]
for x, col, ls, lab in ((x0, H.MUTED, "--", T("手画的草图", "rough sketch")), (x7, "#2c6fbb", "-", T("加上约束和尺寸后", "after constraints and dimensions"))):
    b, h = outline(x)
    ax.plot(*zip(*b), color=col, ls=ls, lw=1.1, label=lab)
    ax.plot(*zip(*h), color=col, ls=ls, lw=1.1)
for q in PTS:
    xx, yy = P(x7, q)
    ax.plot(xx, yy, "o", ms=2.2, color="#2c6fbb")
    ax.text(xx + 2, yy + 2, q, fontsize=6.5, color="#2c6fbb")
ax.set_aspect("equal")
ax.axis("off")
ax.legend(fontsize=6.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2)
ax.set_title(T(f"(a) 自由度：只加几何约束剩 {dof_free}，再加 5 个尺寸剩 {dof_full}", f"(a) DOF: {dof_free} with geometric constraints, {dof_full} with 5 dimensions"), fontsize=7.8)
# (b) 改成 6209：设计意图对 / 不对
ax = axs[1]
for x, col, ls, lab in ((x7, H.MUTED, "--", "6207"), (x9g, "#2c6fbb", "-", T("6209：壁厚跟着走", "6209: wall follows D")),
                        (x9b, "#d62728", "-", T("6209：圆弧半径写死", "6209: arc radius hard-coded"))):
    b, h = outline(x)
    ax.plot(*zip(*b), color=col, ls=ls, lw=1.1, label=lab)
    ax.plot(*zip(*h), color=col, ls=ls, lw=1.1)
yt = P(x9b, "O")[1] + RB(x9b)
ax.annotate(T(f"壁厚只剩 {wall_b:.1f} mm", f"wall only {wall_b:.1f} mm"), xy=(0, yt + wall_b / 2), xytext=(48, yt + 4), fontsize=6.8, color="#d62728",
            arrowprops=dict(arrowstyle="-|>", lw=0.6, color="#d62728", mutation_scale=7))
ax.set_aspect("equal")
ax.axis("off")
ax.legend(fontsize=6.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=3)
ax.set_title(T("(b) 只改轴承外径：设计意图对与不对", "(b) Change only the bearing OD: right and wrong design intent"), fontsize=7.8)
fig.tight_layout()
figure(fig, "fig3_7_1")

out(nv=NV, n_geo=len(geometric(x0)), dof_free=dof_free, red_free=red_free, dof_full=dof_full, red_full=red_full, dof_over=dof_over,
    red_over=red_over, res7=res7, D7=p7["D"], D9=p9["D"], wall7=p7["wall"], wall9=wall_g, wall_bad=wall_b, Ro7=p7["Ro"], Ro9=p9["Ro"],
    H7=p7["H"], H9=p9["H"])
