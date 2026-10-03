"""33.9 在数字工厂完成一根轴的设计：SH-301 B 版的 build123d 参数化模型（台阶圆角、两个键槽，与在线设计台同一种建模方法），
质量与表面积；设计流程与数字工厂页面的对照图（图 33.9.1、33.9.2）。"""
import math
import os
import tempfile

import numpy as np

import _draw as D
import _shaft as S
from bookout import T, figure, out, style
import mdstd


def build(fillets=True, keys=True):
    """SH-301 B：沿 z 叠圆柱 → 台阶内角倒圆 → 铣两个 A 型键槽（同一条母线）。返回 build123d 实体。"""
    import build123d as bd
    z, s, steps = 0.0, None, []
    for d, L, *_ in S.SEG_B:
        c = bd.Pos(0, 0, z) * bd.Cylinder(d / 2, L, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        s = c if s is None else s + c
        z += L
        steps.append(z)
    s = s.clean()
    if fillets:
        for zz, r in S.FILLET_B.items():
            es = [e for e in s.edges() if e.geom_type == bd.GeomType.CIRCLE and abs(e.center().Z - zz) < 1e-6]
            if len(es) == 2:
                s = s.fillet(r, [min(es, key=lambda e: e.radius)])
    if keys:
        for z0, z1, d in KEYWAYS:
            k = mdstd.key_for(d)
            b, t, L = k["b"], k["t"], z1 - z0
            H = 10.0                                    # 刀具从轴面以上切入，槽底在 d/2 − t
            yc = d / 2 - t + H / 2
            cut = bd.Pos(0, yc, (z0 + z1) / 2) * bd.Box(b, H, L - b)
            for zc in (z0 + b / 2, z1 - b / 2):
                cut = cut + bd.Pos(0, yc, zc) * bd.Rot(90, 0, 0) * bd.Cylinder(b / 2, H)
            s = s - cut
    return s


# 键槽的位置：齿轮键、联轴器键（33.2 节：键比轮毂短 5–10 mm、取标准长度，居中在轮毂上）
L_kg = mdstd.key_length(S.HUB_GEAR - 10)
L_kc = mdstd.key_length(S.HUB_CPL - 7)
KEYWAYS = [(S.Z_GEAR - L_kg / 2, S.Z_GEAR + L_kg / 2, 40), (S.Z_CPL - L_kc / 2, S.Z_CPL + L_kc / 2, 30)]

solid = build()
rho = mdstd.material(S.MAT)["density"]                 # g/cm³
vol = solid.volume                                      # mm³
mass = vol * rho * 1e-6
n_faces = len(solid.faces())
vol0 = build(fillets=False, keys=False).volume
p = os.path.join(tempfile.mkdtemp(), "SH-301-B.step")
import build123d as bd  # noqa: E402
bd.export_step(solid, p)
step_kb = os.path.getsize(p) / 1024

# ---------------------------------------------------------------- 图 33.9.1：三维模型（三角化后用 matplotlib 画）
plt = style()
verts, tris = solid.tessellate(0.03, 0.2)
V = np.array([[v.X, v.Y, v.Z] for v in verts])
Fc = np.array(tris)
P = V[:, [2, 0, 1]]                                     # 轴线画成水平
light = np.array([0.3, -0.6, 0.75])
light /= np.linalg.norm(light)
n = np.cross(P[Fc[:, 1]] - P[Fc[:, 0]], P[Fc[:, 2]] - P[Fc[:, 0]])
n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
shade = 0.45 + 0.55 * np.clip(n @ light, 0, 1)
base = np.array([0.72, 0.77, 0.81])
from matplotlib.collections import PolyCollection  # noqa: E402
el, az = math.radians(34), math.radians(-24)            # 正交投影：先绕竖直轴转 az，再俯视 el
Rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
Rx = np.array([[1, 0, 0], [0, math.cos(el), -math.sin(el)], [0, math.sin(el), math.cos(el)]])
Q = (P - [S.LEN_B / 2, 0, 0]) @ (Rx @ Rz).T             # x 向右、z 向上、y 指向屏幕里
order = np.argsort(-Q[Fc][:, :, 1].mean(axis=1))        # 画家算法：远的先画
fig, ax = plt.subplots(figsize=(6.8, 2.4), dpi=220)          # 网格面片光栅化，分辨率要高一些
ax.add_collection(PolyCollection(Q[Fc][order][:, :, [0, 2]], facecolors=np.outer(shade, base)[order], edgecolors=np.outer(shade, base)[order], linewidths=0.2, rasterized=True))
ax.set_xlim(Q[:, 0].min() - 3, Q[:, 0].max() + 3)
ax.set_ylim(Q[:, 2].min() - 3, Q[:, 2].max() + 3)
ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout()
figure(fig, "fig33_9_1")

# ---------------------------------------------------------------- 图 33.9.2：设计步骤 ↔ 本章 ↔ 数字工厂
steps = [
    (T("1 选标准件", "1 Standard parts"), "33.2", T("零件库：6207、平键、油封 → STEP / FreeCAD", "Parts library: 6207, keys, seal → STEP / FreeCAD"), "#e8eef7"),
    (T("2 建模出图", "2 Model & drawing"), "33.2", T("在线设计台（台阶圆角、键槽）或 build123d 脚本", "Web design desk (fillets, keyways) or a build123d script"), "#eef6e8"),
    (T("3 强度", "3 Strength"), "33.4–33.5", T("仿真与分析：轴承支承、扭矩、力 → 应力云图", "Simulation: bearing supports, torque, forces → stress"), "#fbefe0"),
    (T("4 刚度与固有频率", "4 Stiffness & modes"), "33.6–33.7", T("仿真与分析：位移；固有频率（轴承“只限中间一圈”）", "Simulation: displacement; natural frequencies (ring bearings)"), "#fbefe0"),
    (T("5 疲劳寿命", "5 Fatigue life"), "33.8", T("仿真与分析：载荷谱（试验台记录 / 关节力矩 / CSV）→ 寿命 → Word 报告", "Simulation: load spectrum (rig / joint torque / CSV) → life → report"), "#fbefe0"),
    (T("6 评审与发布", "6 Review & release"), T("任务单", "task sheet"), T("我的任务 → AI 预审 → 老师批注 → 设计发布与审批 → ERPNext 新版本", "My tasks → AI pre-review → instructor → release → ERPNext revision"), "#f3e8f7"),
    (T("7 制造与检验", "7 Make & inspect"), T("任务单", "task sheet"), T("工单 → 数控编程 → 车间加工 → 三坐标检验 → 质量记录", "Work order → CNC → shop floor → CMM → quality record"), "#e8f4f4"),
]
fig, ax = plt.subplots(figsize=(6.8, 4.4))
h, gap = 0.5, 0.16
for i, (name, sec, page, col) in enumerate(steps):
    y = -(i * (h + gap))
    ax.add_patch(D.Rectangle((0, y - h), 1.9, h, fc=col, ec=D.INK, lw=0.8))
    ax.text(0.95, y - h / 2, name, ha="center", va="center", fontsize=8.5, weight="bold")
    ax.text(2.35, y - h / 2, sec, ha="center", va="center", fontsize=7.5, color=D.MUTED)
    ax.add_patch(D.Rectangle((2.85, y - h), 5.6, h, fc="white", ec=D.MUTED, lw=0.6))
    ax.text(2.95, y - h / 2, page, ha="left", va="center", fontsize=7.5)
    if i < len(steps) - 1:
        ax.annotate("", (0.95, y - h - gap), (0.95, y - h), arrowprops=dict(arrowstyle="-|>", color=D.INK, lw=0.8))
ax.annotate("", (-0.15, -0.0 - h / 2), (-0.15, -(4 * (h + gap)) - h / 2),
            arrowprops=dict(arrowstyle="-|>", color=D.FORCE, lw=1.0, connectionstyle="arc3,rad=-0.4"))
ax.text(-0.42, -2.2 * (h + gap), T("不满足：改设计", "fails: redesign"), rotation=90, ha="center", va="center", fontsize=7.5, color=D.FORCE)
ax.text(0.95, 0.12, T("设计步骤", "design step"), ha="center", fontsize=8, color=D.MUTED)
ax.text(2.35, 0.12, T("本章", "chapter"), ha="center", fontsize=8, color=D.MUTED)
ax.text(5.65, 0.12, T("数字工厂 / 软件", "digital factory / software"), ha="center", fontsize=8, color=D.MUTED)
ax.set_xlim(-0.7, 8.5)
ax.set_ylim(-len(steps) * (h + gap) - 0.05, 0.35)
ax.axis("off")
fig.tight_layout()
figure(fig, "fig33_9_2")

out(vol_cm3=vol / 1000, mass=mass, n_faces=n_faces, dvol=(vol0 - vol) / 1000, step_kb=step_kb, length=S.LEN_B,
    key_gear=f"{mdstd.key_for(40)['b']}×{mdstd.key_for(40)['h']}×{L_kg}", key_cpl=f"{mdstd.key_for(30)['b']}×{mdstd.key_for(30)['h']}×{L_kc}",
    n_fillets=len(S.FILLET_B), r_max=max(S.FILLET_B.values()), r_min=min(S.FILLET_B.values()))
