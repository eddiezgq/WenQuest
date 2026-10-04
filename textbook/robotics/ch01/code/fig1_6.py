"""1.6 节的示意图。

图 1.6.1：全书路线图：导论与六篇共 61 章（book.yaml），颜色表示层次，圆点表示提纲中该章用到的贯穿机器人。
图 1.6.2：五台贯穿机器人的关节结构：由零件库关节表画出的“连杆—关节”树；方框是连杆，连线上的字母是关节类型。
"""
import re
import textwrap

import yaml
from matplotlib.patches import FancyBboxPatch

from _ch1 import FIVE, MJCF, ROOT, entry, glb_tree, movable
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
book = yaml.safe_load((ROOT / "textbook" / "robotics" / "book.yaml").read_text(encoding="utf-8"))
prog = yaml.safe_load((ROOT / "textbook" / "robotics" / "progress.yaml").read_text(encoding="utf-8")) or {}
parts_en = prog.get("parts_en", {})
LEVEL = {"基础": ("#dcefdc", T("基础", "Basic")), "进阶": ("#dbe9f6", T("进阶", "Advanced")),
         "专题": ("#f6d9d5", T("专题", "Special topic")), "基础/进阶": ("#e8f0d0", T("基础/进阶", "Basic/Advanced"))}
EN = T("", "en") == "en"
# 英文版图中的篇名用短名，章名用英文（第 1、4、12、39 章以 progress.yaml 的 title_en 为准）
PART_SHORT = {"导论": "Introduction", "第一篇 数学基础篇": "Part I  Mathematics", "第二篇 运动学篇": "Part II  Kinematics",
              "第三篇 动力学篇": "Part III  Dynamics", "第四篇 结构与机电设计篇": "Part IV  Design", "第五篇 控制篇": "Part V  Control",
              "第六篇 编程与 AI 篇": "Part VI  Programming & AI"}
TITLE_EN = {
    1: "Introduction to Robotics", 2: "Essentials of Linear Algebra", 3: "Vectors and Tensors",
    4: "Rotation of Rigid Bodies: From Euler to Quaternions", 5: "Pose and Homogeneous Transformations",
    6: "Screws, Lie Groups and Lie Algebras", 7: "Differential Equations and Numerical Methods", 8: "Fundamentals of Optimization",
    9: "Fundamentals of Probability and Estimation", 10: "Kinematics of a Point", 11: "Mechanisms, Degrees of Freedom and Configuration Space",
    12: "Forward Kinematics: The Product of Exponentials", 13: "Forward Kinematics: The DH Parameters",
    14: "Inverse Kinematics: Analytical Solutions", 15: "Inverse Kinematics: Numerical Solutions",
    16: "Velocity Kinematics and the Jacobian", 17: "Redundant Robots", 18: "Parallel Mechanisms", 19: "Kinematics of Mobile Robots",
    20: "Kinematics of Legged and Humanoid Robots", 21: "Kinematics of Aerial Robots", 22: "Trajectory Planning",
    23: "Fundamentals of Rigid-Body Dynamics", 24: "Lagrangian Dynamics", 25: "Newton–Euler Recursion in Screw Form",
    26: "Dynamic Properties and Parameter Identification", 27: "Contact, Impact and Friction",
    28: "Dynamics of Mobile, Legged and Aerial Robots", 29: "Dynamic Simulation", 30: "Overall Design of Robots",
    31: "Structures, Materials and Strength", 32: "Transmissions and Speed Reducers", 33: "End-Effectors", 34: "Digital Prototypes",
    35: "Fundamentals of Circuits and Electronics", 36: "Electric Motors and Drive Circuits", 37: "Controller Hardware",
    38: "Principles of Sensors", 39: "Signal Conditioning and Automatic Testing", 40: "Communication and Buses",
    41: "Power Supplies, Batteries and Electrical Safety", 42: "Fundamentals of Control Theory", 43: "Single-Joint Control",
    44: "Multi-Joint Motion Control", 45: "Force Control and Impedance Control", 46: "State Estimation",
    47: "Mobile Robots: Localization, Mapping and Navigation", 48: "Control of Legged and Humanoid Robots", 49: "Quadrotor Control",
    50: "Visual Servoing", 51: "Fundamentals of Robot Programming", 52: "ROS 2", 53: "Motion Planning", 54: "Robot Vision",
    55: "Fundamentals of Machine Learning", 56: "Reinforcement Learning", 57: "Imitation Learning and Data",
    58: "Embodied Intelligence: Principles", 59: "Embodied Intelligence: Main Technical Routes",
    60: "System Integration and the Digital Factory", 61: "Ethics, Regulations and Careers"}
for _n, _c in (prog.get("chapters") or {}).items():
    if isinstance(_c, dict) and _c.get("title_en"):
        TITLE_EN[int(_n)] = _c["title_en"]
ROBOT = [("B-ARM-UR5E", "#1f77b4", "UR5e"), ("B-ARM-PANDA", "#9467bd", "Panda"), ("B-LEG-GO2", "#2ca02c", "Go2"),
         ("B-EDU-DIFF", "#d9822b", "AGV"), ("B-UAV-X2", "#d62728", T("四旋翼", "Quadrotor"))]
outline = (ROOT / "docs" / "教材" / "机器人学" / "00_提纲.md").read_text(encoding="utf-8")
body = outline[outline.index("## 三、提纲"):outline.index("### 附录")]
blocks = re.split(r"\n\*\*第 (\d+) 章", body)[1:]
text_of = {int(blocks[i]): blocks[i + 1] for i in range(0, len(blocks), 2)}
KEYS = {"B-ARM-UR5E": r"UR5e", "B-ARM-PANDA": r"Panda|七轴", "B-LEG-GO2": r"Go2|四足|足式",
        "B-EDU-DIFF": r"AGV|差速|移动机器人", "B-UAV-X2": r"四旋翼|无人机|空中机器人"}


def en_title(no):
    """英文章名折成至多两行，放进方框。"""
    lines = textwrap.wrap(f"{no}  {TITLE_EN[no]}", 33)
    if len(lines) > 2:
        lines = [lines[0], textwrap.shorten(" ".join(lines[1:]), 33, placeholder=" …")]
    return "\n".join(lines)


def short(title):
    t = re.split(r"[（(]", title)[0]
    return t if len(t) <= 12 else t[:11] + "…"


# ---------------------------------------------------------------- 图 1.6.1
groups = []
for c in book["chapters"]:
    if not groups or groups[-1][0] != c["part"]:
        groups.append([c["part"], []])
    groups[-1][1].append(c)
groups[0][1] = groups[0][1] + []           # 导论只有 1 章，与第一篇并排放在第一列的上方
cols = [[groups[0], groups[1]]] + [[g] for g in groups[2:]]
fig, ax = plt.subplots(figsize=(12.6, 7.6) if EN else (12.6, 6.0))
W, Hrow = 1.72, (0.70 if EN else 0.52)
ax.set_xlim(-0.1, len(cols) * 1.86 + 0.1)
ax.axis("off")
ylow = 15.0
for ci, col in enumerate(cols):
    x = ci * 1.86 + W / 2 + 0.05
    y = 15.0
    for part, chs in col:
        ax.text(x, y, T(part, PART_SHORT.get(part, parts_en.get(part, part))), ha="center", va="center", fontsize=8.4, weight="bold",
                color=C["ink"], wrap=True)
        y -= 0.55
        for c in chs:
            fc = LEVEL.get(c["level"], ("#eeeeee", ""))[0]
            ax.add_patch(FancyBboxPatch((x - W / 2, y - Hrow / 2 + 0.03), W, Hrow - 0.06,
                                        boxstyle="round,pad=0.0,rounding_size=0.05", fc=fc, ec=C["muted"], lw=0.6))
            if EN:
                ax.text(x - W / 2 + 0.06, y + Hrow / 2 - 0.07, en_title(c["no"]), ha="left", va="top", fontsize=6.2,
                        color=C["ink"], linespacing=1.15)
            else:
                ax.text(x - W / 2 + 0.06, y + 0.07, f"{c['no']}  {short(c['title'])}", ha="left",
                        va="center", fontsize=6.9, color=C["ink"])
            k = 0
            for rid, colr, _ in ROBOT:
                if re.search(KEYS[rid], text_of[c["no"]]):
                    ax.plot([x - W / 2 + 0.12 + 0.13 * k], [y - (0.22 if EN else 0.15)], "o", color=colr, ms=3.6)
                    k += 1
            y -= Hrow
            ylow = min(ylow, y)
        y -= 0.35
yl = ylow - 0.2
for i, (lv, (fc, name)) in enumerate(LEVEL.items()):
    xx = 0.2 + i * 1.6
    ax.add_patch(FancyBboxPatch((xx, yl - 0.15), 0.4, 0.3, boxstyle="round,pad=0.0,rounding_size=0.04", fc=fc, ec=C["muted"], lw=0.6))
    ax.text(xx + 0.5, yl, name, va="center", fontsize=8.5)
for i, (_, colr, name) in enumerate(ROBOT):
    xx = 6.8 + i * 0.95
    ax.plot([xx], [yl], "o", color=colr, ms=5)
    ax.text(xx + 0.1, yl, name, va="center", fontsize=8.5)
ax.text(0.2, yl - 0.55, T("圆点：提纲中该章（含配套实验）用到的贯穿机器人", "Dots: the recurring robots each chapter (with its labs) uses, per the outline"),
        fontsize=8.2, color=C["muted"])
ax.set_ylim(yl - 0.8, 15.4)
figure(fig, "fig1_6_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.6.2
NAME = {"B-ARM-UR5E": "UR5e", "B-ARM-PANDA": "Panda", "B-LEG-GO2": "Go2", "B-EDU-DIFF": T("差速小车", "Differential-drive cart"),
        "B-UAV-X2": T("四旋翼 X2", "Quadrotor X2")}
JT = {"revolute": "R", "continuous": "R", "prismatic": "P"}
fig, axs = plt.subplots(1, 5, figsize=(12.4, 5.4), gridspec_kw={"width_ratios": [1, 1.1, 2.4, 1.1, 0.9]})


def lbox(ax, x, y, text, fc="#f4f6f8", fs=6.8):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=C["ink"],
            bbox=dict(boxstyle="round,pad=0.25", fc=fc, ec=C["muted"], lw=0.6))


for ax, eid in zip(axs, FIVE):
    e = entry(eid)
    jt = {j["child"]: j["type"] for j in e["robot"]["joints"]}
    tree = glb_tree(eid)
    root = tree["root"][0]                      # 网页模型的根节点下挂着基座（或机身）
    kids = {k: v for k, v in tree.items() if k != "root"}
    pos = {}
    leaves = [0]

    def place(n, depth):
        ch = kids.get(n, [])
        if not ch:
            pos[n] = (leaves[0], -depth)
            leaves[0] += 1
            return
        for c in ch:
            place(c, depth + 1)
        xs = [pos[c][0] for c in ch]
        pos[n] = (sum(xs) / len(xs), -depth)

    place(root, 0)
    span = max(leaves[0] - 1, 1)
    for par, ch in kids.items():
        for c in ch:
            if par not in pos or c not in pos:
                continue
            (x0, y0), (x1, y1) = pos[par], pos[c]
            ax.plot([x0, x1], [y0, y1], color=C["muted"], lw=0.8, zorder=0, ls="-" if c in jt else ":")
            if jt.get(c) in JT:
                ax.text((x0 + x1) / 2 + 0.08 * span / 3, (y0 + y1) / 2, JT[jt[c]], fontsize=7, color=C["accent"],
                        weight="bold", ha="left", va="center")
    for n, (x, y) in pos.items():
        lab = re.sub(r"_link$", "", n).replace("_", " ")
        lbox(ax, x, y, lab if len(lab) <= 12 else lab[:12], "#f3e2b3" if n == root else "#f4f6f8", 6.2 if span > 4 else 6.8)
    base = MJCF[eid]["base"]
    btxt = {"fixed": T("基座固定", "fixed base"), "free": T("自由基座 +6", "free base +6"), "planar": T("平面运动 +3", "planar base +3")}[base]
    nj = len(movable(e))
    depth = min(y for _, y in pos.values())
    ax.set_title(f"{NAME[eid]}", fontsize=10.5)
    ax.text(span / 2, depth - 0.9, T(f"{nj} 个关节；{btxt}", f"{nj} joints; {btxt}"), ha="center", fontsize=8.5)
    ax.set_xlim(-0.8, span + 0.8)
    ax.set_ylim(depth - 1.3, 0.6)
    ax.axis("off")
fig.text(0.5, 0.01, T("R：转动关节　P：移动关节　虚线：固定连接　黄框：基座或机身",
                      "R: revolute joint    P: prismatic joint    dotted: fixed connection    yellow: base or body"), ha="center", fontsize=8.6,
         color=C["muted"])
fig.tight_layout(rect=(0, 0.04, 1, 1))
figure(fig, "fig1_6_2")
plt.close(fig)
