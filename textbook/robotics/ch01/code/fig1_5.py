"""1.5 节的示意图。

图 1.5.1：数字工厂车间平面（与工厂仿真同一份布置）：设备、通道、AGV 停靠点，以及输出轴 SH-301 的七次搬运路线。
图 1.5.2：2024 年专业服务机器人销量的主要应用领域（IFR《World Robotics》2025）。
图 1.5.3：扫地机器人：按行清扫与随机清扫的路线，以及随机清扫的覆盖率 1 − e^{−n}。
"""
import math

import numpy as np
from matplotlib.patches import Rectangle

from _ch1 import IFR_SERVICE_2024, factory
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
data, layout = factory()
from sim.engine import OP_UNITS   # noqa: E402
from wqbus import UNITS           # noqa: E402

# 英文版平面图上用短名，免得字压到相邻设备
SHORT_EN = {"vmc-01": "VMC", "hmc-01": "HMC", "ht-01": "Furnace", "grd-01": "Grinder", "qc-01": "Inspection",
            "test-01": "Run-in rig", "asm-01": "Assembly", "hob-01": "Hobber", "key-01": "Keyway",
            "cnc-l01-a": "Lathe A", "cnc-l01-b": "Lathe B", "saw-01": "Band saw", "store-01": "Raw-material\nstore", "store-02": "Finished-\ngoods store"}
EN = T("zh", "en") == "en"
# ---------------------------------------------------------------- 图 1.5.1
W, D = layout.FLOOR
fig, ax = plt.subplots(figsize=(10.0, 6.2))
ax.add_patch(Rectangle((0, 0), W, D, fc="#f4f6f8", ec=C["ink"], lw=1.0))
for y in layout.AISLES:
    ax.add_patch(Rectangle((0.5, y - 1.0), W - 1.0, 2.0, fc="#e1e6ea", ec="none"))
ax.add_patch(Rectangle((layout.CROSS_X - 1.0, layout.AISLES[0]), 2.0, layout.AISLES[1] - layout.AISLES[0], fc="#e1e6ea", ec="none"))
for u, (x, y, w, d) in layout.LAYOUT.items():
    store = u.startswith("store")
    ax.add_patch(Rectangle((x - w / 2, y - d / 2), w, d, fc="#c9d6e3" if store else "#ffffff", ec=C["ink"], lw=0.8))
    ax.text(x, y + (0.85 if store and EN else 0.35), T(UNITS[u][1], SHORT_EN.get(u, UNITS[u][2])), ha="center", va="center",
            fontsize=6.4 if store and EN else 7.4)
    ax.text(x, y - 0.55, u, ha="center", va="center", fontsize=6.6, color=C["muted"])
for a, (x, y) in layout.AGV_HOME.items():
    ax.add_patch(Rectangle((x - 0.65, y - 0.42), 1.3, 0.85, fc="#f28c28", ec=C["ink"], lw=0.6))
    ax.text(x - 0.9, y, a.upper(), ha="right", va="center", fontsize=7, color="#b35c00")
ops = data.ROUTINGS[data.BOMS["SH-301"][0]]
units = [OP_UNITS[op][0] for op, _ in ops] + ["store-02"]
cols = plt.get_cmap("viridis")(np.linspace(0.05, 0.9, len(units) - 1))
for k, (a, b) in enumerate(zip(units, units[1:])):
    path = np.array(layout.route(layout.dock(a), layout.dock(b)))
    off = (k - 3) * 0.12                                    # 同一条通道上的几段错开一点，免得重叠
    ax.plot(path[:, 0] + off, path[:, 1] + off, "-", color=cols[k], lw=1.8, alpha=0.9)
    ax.plot(path[0, 0] + off, path[0, 1] + off, "o", color=cols[k], ms=4)
    ax.annotate("", xy=(path[-1, 0] + off, path[-1, 1] + off), xytext=(path[-2, 0] + off, path[-2, 1] + off),
                arrowprops=dict(arrowstyle="-|>", color=cols[k], lw=1.6))
    ax.text(path[1, 0] + off + 0.3, path[1, 1] + off + 0.35, str(k + 1), fontsize=8, color=cols[k], weight="bold")
ax.set_xlim(-0.5, W + 0.5)
ax.set_ylim(D + 0.5, -2.2)                                   # 车间平面图的 y 轴向下，与工厂看板一致
ax.set_aspect("equal")
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.text(0.5, -1.2, T("输出轴 SH-301：带锯 → 车 A → 热处理 → 车 B → 键槽 → 磨 → 检验 → 成品库（编号为搬运次序）",
                     "Output shaft SH-301: saw → lathe A → furnace → lathe B → keyway → grinder → inspection → store (numbers: order of moves)"),
        fontsize=8.6, color=C["ink"])
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig1_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.5.2
fig, ax = plt.subplots(figsize=(6.4, 3.0))
names = [T(z, e) for z, e, _ in IFR_SERVICE_2024][::-1]
vals = np.array([n for *_, n in IFR_SERVICE_2024][::-1]) / 1000
ax.barh(names, vals, color=C["z"], height=0.6)
for i, v in enumerate(vals):
    ax.text(v + 1.5, i, f"{v:.1f}", va="center", fontsize=8.5)
ax.set_xlabel(T("2024 年销量（千台）", "units sold in 2024 (thousands)"))
ax.set_xlim(0, 120)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.text(1.0, -0.32, T("数据：IFR《World Robotics》2025 服务机器人卷；餐饮酒店、专业清洁为“超过”该数",
                      "Data: IFR World Robotics 2025, Service Robots; hospitality and cleaning are lower bounds"),
        transform=ax.transAxes, ha="right", fontsize=7.6, color=C["muted"])
figure(fig, "fig1_5_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.5.3
rng = np.random.default_rng(153)
fig, axs = plt.subplots(1, 3, figsize=(10.4, 3.5))
side = 4.0
a = axs[0]
ys = np.arange(0.15, side, 0.3 * 0.85)
path = []
for i, y in enumerate(ys):
    xs = (0.15, side - 0.15) if i % 2 == 0 else (side - 0.15, 0.15)
    path += [(xs[0], y), (xs[1], y)]
path = np.array(path)
a.plot(path[:, 0], path[:, 1], "-", color=C["z"], lw=1.0)
a.set_title(T("(a) 按行清扫（规划路径）", "(a) Row by row (planned)"), fontsize=9.5)
b = axs[1]
p = np.array([2.0, 2.0])
ang = rng.uniform(0, 2 * math.pi)
pts = [p.copy()]
for _ in range(40):                                        # 直行到墙，随机转一个角度，再直行
    d = np.array([math.cos(ang), math.sin(ang)])
    tx = [((side - 0.15) - p[0]) / d[0] if d[0] > 0 else (0.15 - p[0]) / d[0] if d[0] < 0 else 1e9,
          ((side - 0.15) - p[1]) / d[1] if d[1] > 0 else (0.15 - p[1]) / d[1] if d[1] < 0 else 1e9]
    p = p + min(tx) * d
    pts.append(p.copy())
    ang = rng.uniform(0, 2 * math.pi)
pts = np.array(pts)
b.plot(pts[:, 0], pts[:, 1], "-", color=C["accent"], lw=0.9)
b.set_title(T("(b) 碰壁后随机转向", "(b) Bounce and turn at random"), fontsize=9.5)
for q in (a, b):
    q.add_patch(Rectangle((0, 0), side, side, fc="none", ec=C["ink"], lw=1.0))
    q.set_aspect("equal")
    q.set_xlim(-0.2, side + 0.2)
    q.set_ylim(-0.2, side + 0.2)
    q.axis("off")
c = axs[2]
n = np.linspace(0, 4, 200)
c.plot(n, 1 - np.exp(-n), color=C["accent"], lw=1.8)
c.axhline(0.95, color=C["muted"], ls="--", lw=0.8)
c.axvline(math.log(20), color=C["muted"], ls="--", lw=0.8)
c.text(math.log(20) - 0.06, 0.4, f"n = ln 20 ≈ {math.log(20):.2f}", fontsize=8.5, ha="right")   # 写在虚线左侧，免得被裁掉
c.set_xlabel(T("清扫过的“遍数” n", "number of passes n"))
c.set_ylabel(T("覆盖率 c", "coverage c"))
c.set_title(T("(c) 随机清扫的覆盖率 c = 1 − e⁻ⁿ", "(c) Random coverage c = 1 − e⁻ⁿ"), fontsize=9.5)
c.set_ylim(0, 1.02)
c.grid(alpha=0.3)
for s in ("top", "right"):
    c.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig1_5_3")
plt.close(fig)
