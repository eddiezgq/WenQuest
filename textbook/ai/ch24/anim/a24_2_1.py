"""动画 24.2.1（配图 24.2.1）：仿真到现实——同一条策略，换了摩擦会怎样。

五段：

1. 任务：把夹爪送到工件上，**位置 2 cm、姿态 0.4 rad 之内闭合夹爪**才算抓到；
2. 两套物理：仿真与真机在摩擦、连杆长度、观测噪声、执行延迟上各差一点——**这才是真机**；
3. 把**同一条**只在标称仿真里训出来的策略放进两套物理里：仿真里落在判据圈内，
   真机上它“以为到了”，实际差了好几厘米 → 报表上仿真 83.8%、真机 **0.0%**（各试 80 次）；
4. 训练时把摩擦与连杆抖起来（**域随机化范围 0.2**）：策略不再靠心算的正运动学，
   改成盯着量出来的夹爪位姿收 → 真机 88.8%，而仿真那一列反而降到 75.0%；
5. 范围太宽（1.3）：同一个观测对应的专家动作互相矛盾，策略只能学个平均，
   **两列一起掉**（仿真 51.2%、真机 68.8%）→ 真机那一列是一条**倒 U 形**曲线。

成绩两列取自算例 24.2（`code/ex24_2.py`，各试 80 次），轨迹在本文件里按同一套玩具
（二连杆、判据 2 cm / 0.4 rad）重算一遍——渲染服务只允许 manim、wq_anim、numpy、math、random。

**本章硬口径**：凡报成绩，必须分“仿真”和“真机”两列，并写清真机试了多少次。
"""
import math

import numpy as np
from manim import *
from wq_anim import *

# ---------------- 两套世界参数（与 code/_ch24.py 的 SIM、REAL 同一套显式假设）
L1S, L2S = 0.35, 0.30            # 仿真里的连杆长度（m）
L1R, L2R = 0.363, 0.288          # 真机：装配与标定误差
FRIC_S, FRIC_R = 0.04, 0.11      # 关节摩擦：真机大得多
NOISE_R = 0.004                  # 真机的观测噪声（m）
DELAY_R = 1                      # 真机的指令晚一个控制周期才生效
VMAX = np.array([1.6, 1.6])      # 关节最大角速度（rad/s）
DT = 0.05                        # 控制周期（s）
GAIN = 3.5
CLOSE_M = 0.012                  # 策略“认为自己到了”的触发半径（m）
TOL_M = 0.02                     # 成功判据：位置 2 cm（姿态 0.4 rad 不画）

Q0 = np.array([0.55, 0.95])      # 收工位姿
TGT = np.array([0.54 * math.cos(1.20), 0.54 * math.sin(1.20)])   # 工件在哪（显式假设）

# ---------------- 算例 24.2 跑出来的两列成绩（各试 80 次）
N_TRIALS = 80
SCALES = [0.0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0, 1.3]
SIM_CURVE = [83.8, 78.8, 75.0, 80.0, 81.2, 73.8, 75.0, 56.2, 51.2]
REAL_CURVE = [0.0, 48.8, 88.8, 86.2, 83.8, 80.0, 78.8, 78.8, 68.8]


def fk2(q, l1, l2):
    """正运动学：给两个关节角，算夹爪位置（m）。"""
    return np.array([l1 * math.cos(q[0]) + l2 * math.cos(q[0] + q[1]),
                     l1 * math.sin(q[0]) + l2 * math.sin(q[0] + q[1])])


def jac(q, l1, l2):
    """雅可比矩阵：策略用**它自己以为的**连杆长度算这一项。"""
    s1, c1 = math.sin(q[0]), math.cos(q[0])
    s12, c12 = math.sin(q[0] + q[1]), math.cos(q[0] + q[1])
    return np.array([[-l1 * s1 - l2 * s12, -l2 * s12],
                     [l1 * c1 + l2 * c12, l2 * c12]])


def run(l1, l2, fric, delay, measured, noise, seed=3, steps=90):
    """把同一条策略放进一套物理里跑一回合。

    `measured=False`：策略**按标称连杆长度心算一套正运动学**——只在标称仿真里训出来的
    策略就是这么偷懒的，连杆一变就错。`measured=True`：策略盯着**量出来的**夹爪位姿收，
    见过各种连杆长度之后只能这么做（算例 24.2 里域随机化起作用的道理）。

    返回（夹爪真实走过的路径，闭合夹爪时的位置误差 m，走了几步）。
    """
    g = np.random.default_rng(seed)
    q = np.array(Q0, dtype=float)
    queue = [np.zeros(2) for _ in range(delay)]
    path = [fk2(q, l1, l2)]
    for t in range(steps):
        if measured:
            tip = fk2(q, l1, l2) + (noise * g.normal(0, 1, 2) if noise > 0 else 0.0)
        else:
            tip = fk2(q, L1S, L2S)                       # 心算出来的夹爪位置
        e = TGT - tip
        if float(np.linalg.norm(e)) < CLOSE_M:           # 它认为自己到了 → 闭合夹爪，回合结束
            break
        a = np.clip(GAIN * (jac(q, L1S, L2S).T @ e) / 0.1, -1.0, 1.0)
        queue.append(a)
        q = q + (1.0 - fric) * queue.pop(0) * VMAX * DT
        path.append(fk2(q, l1, l2))
    path = np.array(path)
    return path, float(np.linalg.norm(path[-1] - TGT)), len(path) - 1


def columns(sim_pct, real_pct, head_zh, head_en):
    """两列成绩并排：左“仿真”，右“真机”。本章凡报成绩都是这个样子。"""
    base_y = -1.5
    unit = 3.0 / 100.0
    g = VGroup()
    for i, (pct, name_zh, color) in enumerate(((sim_pct, "仿真", STEEL), (real_pct, "真机", C_F))):
        x = -1.6 + i * 3.2
        h = max(pct * unit, 0.02)
        bar = Rectangle(width=1.5, height=h, color=color, fill_opacity=0.8, stroke_width=0)
        bar.move_to(np.array([x, base_y + h / 2.0, 0.0]))
        val = zh(f"{pct:.1f}%", 34, color).next_to(bar, UP, buff=0.18)
        nm = zh(name_zh, 28, MUTED).next_to(bar, DOWN, buff=0.18)
        g.add(bar, val, nm)
    axis = Line(np.array([-3.2, base_y, 0.0]), np.array([3.2, base_y, 0.0]),
                color=MUTED, stroke_width=2)
    head = VGroup(zh(head_zh, 30, YELLOW), en(head_en, 20)).arrange(DOWN, buff=0.08)
    head.move_to(np.array([0.0, 2.2, 0.0]))
    note = zh(f"两列各试 {N_TRIALS} 次", 24, MUTED).move_to(np.array([0.0, base_y - 1.0, 0.0]))
    g.add(axis, head, note)
    return g


def zoom_axes():
    """工件附近的放大图：坐标以工件为原点，单位厘米。"""
    return Axes(x_range=[-8, 8, 2], y_range=[-8, 8, 2], x_length=6.2, y_length=6.2,
                axis_config={"include_tip": False, "color": MUTED}).shift(RIGHT * 3.0 + DOWN * 0.3)


def to_cm(ax, pts):
    """把以米为单位的路径搬到放大图里（相对工件、换成厘米）。"""
    return [ax.c2p((p[0] - TGT[0]) * 100.0, (p[1] - TGT[1]) * 100.0) for p in pts]


class Lesson(Base):
    def construct(self):
        self.title("24.2", "同一条策略，走在两套物理里",
                   "One policy, two sets of physics")

        # ============================================================ 一、任务与判据
        self.caption("任务：把夹爪送到工件上，位置 2 cm、姿态 0.4 rad 之内闭合夹爪才算抓到",
                     "The task: close the gripper within 2 cm and 0.4 rad of the part",
                     wait=1.6)
        s = 6.0                                        # 画图比例：1 m = 6 个单位
        base = np.array([-4.4, -2.2, 0.0])
        a1 = math.degrees(Q0[0])
        a2 = math.degrees(Q0[1])
        armg = planar_arm(base, [a1, a2], [L1S * s, L2S * s], color=STEEL)
        tgt_pt = base + np.array([TGT[0] * s, TGT[1] * s, 0.0])
        part = Square(side_length=0.34, color=YELLOW, fill_opacity=0.85,
                      stroke_width=0).move_to(tgt_pt)
        ring = Circle(radius=TOL_M * s, color=YELLOW, stroke_width=2).move_to(tgt_pt)
        tag = zh("工件（判据圈 2 cm）", 24, YELLOW).next_to(ring, UR, buff=0.12)
        self.play(FadeIn(armg), run_time=1.0)
        self.play(FadeIn(part), Create(ring), FadeIn(tag), run_time=1.0)
        self.caption("判据只有一句话：闭合夹爪的那一刻落在圈里。走到位不闭合不算，闭合了没到位也不算",
                     "Success is decided at the instant the gripper closes, not before",
                     wait=2.0)
        self.clear_stage()

        # ============================================================ 二、两套物理差在哪
        self.caption("仿真与真机差的从来不止一样——四样各差一点，这才是真机",
                     "Simulation and hardware differ in more than one place at a time",
                     wait=1.5)
        rows = [("关节摩擦", "0.04", "0.11"),
                ("连杆长度（cm）", "35.0 / 30.0", "36.3 / 28.8"),
                ("观测噪声（cm）", "0", "0.4"),
                ("执行延迟（控制周期）", "0", "1")]
        head = VGroup(zh("参数", 28, MUTED), zh("仿真", 28, STEEL), zh("真机", 28, C_F))
        for k, m in enumerate(head):
            m.move_to(np.array([-3.6 + k * 3.3, 1.9, 0.0]))
        table = VGroup(head)
        for j, (name, a, b) in enumerate(rows):
            y = 1.1 - j * 0.85
            table.add(zh(name, 26, INK).move_to(np.array([-3.6, y, 0.0])),
                      zh(a, 26, STEEL).move_to(np.array([-0.3, y, 0.0])),
                      zh(b, 26, C_F).move_to(np.array([3.0, y, 0.0])))
        self.play(LaggedStart(*[FadeIn(m) for m in table], lag_ratio=0.12), run_time=2.0)
        self.caption("策略看不到这四样——连杆到底多长、摩擦多大，它只能从观测里推",
                     "The policy never sees these four numbers; it can only infer them",
                     wait=2.0)
        self.clear_stage()

        # ============================================================ 三、同一条策略，两套物理
        self.caption("把只在标称仿真里训出来的那一条策略，原样放进两套物理里",
                     "Take the policy trained only in the nominal simulator, and run it in both",
                     wait=1.6)
        p_sim, e_sim, n_sim = run(L1S, L2S, FRIC_S, 0, False, 0.0)
        p_real, e_real, n_real = run(L1R, L2R, FRIC_R, DELAY_R, False, 0.0)
        ax = zoom_axes()
        circ = Circle(radius=(ax.c2p(2, 0) - ax.c2p(0, 0))[0], color=YELLOW,
                      stroke_width=3).move_to(ax.c2p(0, 0))
        hub = Dot(ax.c2p(0, 0), radius=0.09, color=YELLOW)
        lab_ax = zh("工件附近放大（格 2 cm）", 24, MUTED).next_to(ax, UP, buff=0.12)
        line_sim = VMobject(color=STEEL, stroke_width=4).set_points_as_corners(to_cm(ax, p_sim))
        line_real = VMobject(color=C_F, stroke_width=4).set_points_as_corners(to_cm(ax, p_real))
        end_sim = Dot(to_cm(ax, p_sim)[-1], radius=0.1, color=STEEL)
        end_real = Dot(to_cm(ax, p_real)[-1], radius=0.1, color=C_F)
        txt_sim = zh(f"仿真：{n_sim} 步到位，闭合时差 {e_sim * 100:.1f} cm，在圈里", 26, STEEL)
        txt_real = zh(f"真机：摩擦大了一倍半、指令晚一拍，绕了 {n_real} 步", 26, C_F)
        txt_err = zh(f"闭合时差 {e_real * 100:.1f} cm——判据是 2 cm，在圈外", 26, C_F)
        txt = VGroup(txt_sim, txt_real, txt_err).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        txt.move_to(np.array([-3.6, 0.6, 0.0]))
        self.play(Create(ax), Create(circ), FadeIn(hub), FadeIn(lab_ax), run_time=1.2)
        self.play(Create(line_sim), run_time=1.4)
        self.play(FadeIn(end_sim), FadeIn(txt_sim), run_time=0.8)
        self.play(Create(line_real), run_time=1.4)
        self.play(FadeIn(end_real), FadeIn(txt_real), FadeIn(txt_err), run_time=0.8)
        self.caption("它在真机上“以为自己到了”：心算的正运动学按标称连杆长度算，连杆一变就错",
                     "On hardware it believes it has arrived: its mental kinematics uses the nominal links",
                     wait=2.2)
        self.clear_stage()

        self.caption("于是报表上的两列是这样——只看左边那一列，会以为这条策略很好",
                     "Here are the two columns; read only the left one and the policy looks fine",
                     wait=1.6)
        c0 = columns(SIM_CURVE[0], REAL_CURVE[0],
                     "不随机化（范围 0）", "No randomisation (range 0)")
        self.play(LaggedStart(*[FadeIn(m) for m in c0], lag_ratio=0.1), run_time=1.6)
        self.caption("仿真 83.8%，真机 0.0%——只有仿真那一列的结果不采信",
                     "83.8% in simulation, 0.0% on hardware: a simulation-only number is not evidence",
                     wait=2.4)
        self.clear_stage()

        # ============================================================ 四、范围合适的域随机化
        self.caption("改法：训练时把摩擦、连杆长度、观测噪声、执行延迟一起抖起来（范围 0.2）",
                     "The fix: randomise friction, link lengths, observation noise and delay together",
                     wait=1.8)
        p_fix, e_fix, n_fix = run(L1R, L2R, FRIC_R, DELAY_R, True, NOISE_R)
        ax2 = zoom_axes()
        circ2 = Circle(radius=(ax2.c2p(2, 0) - ax2.c2p(0, 0))[0], color=YELLOW,
                       stroke_width=3).move_to(ax2.c2p(0, 0))
        hub2 = Dot(ax2.c2p(0, 0), radius=0.09, color=YELLOW)
        old = VMobject(color=MUTED, stroke_width=3).set_points_as_corners(to_cm(ax2, p_real))
        new = VMobject(color=STEEL, stroke_width=4).set_points_as_corners(to_cm(ax2, p_fix))
        end_fix = Dot(to_cm(ax2, p_fix)[-1], radius=0.1, color=STEEL)
        why_lines = [zh("见过各种连杆长度之后，", 26, INK),
                     zh("心算那条捷径不管用了，", 26, INK),
                     zh("只好盯着量出来的夹爪位姿收——", 26, YELLOW),
                     zh("这个误差项在真机上照样成立", 26, YELLOW)]
        why_end = zh(f"真机闭合时差 {e_fix * 100:.1f} cm，回到圈里", 26, STEEL)
        why = VGroup(*why_lines, why_end)
        why.arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(np.array([-3.5, 0.3, 0.0]))
        self.play(Create(ax2), Create(circ2), FadeIn(hub2), run_time=1.0)
        self.play(Create(old), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(m) for m in why_lines], lag_ratio=0.3), run_time=2.0)
        self.play(Create(new), FadeIn(end_fix), FadeIn(why_end), run_time=1.4)
        self.clear_stage()

        c1 = columns(SIM_CURVE[2], REAL_CURVE[2],
                     "范围 0.2（真机那一列最高的一档）", "Range 0.2 (best hardware column)")
        self.play(LaggedStart(*[FadeIn(m) for m in c1], lag_ratio=0.1), run_time=1.6)
        self.caption("真机从 0.0% 升到 88.8%；注意仿真那一列反而降到 75.0%——代价付在仿真里",
                     "Hardware goes from 0.0% to 88.8%, while the simulation column drops to 75.0%",
                     wait=2.4)
        self.clear_stage()

        # ============================================================ 五、范围太宽，两列一起掉
        self.caption("那就把范围开到最大？不行——范围太宽，两列一起掉",
                     "So open the range as wide as possible? No: both columns fall",
                     wait=1.6)
        c2 = columns(SIM_CURVE[-1], REAL_CURVE[-1],
                     "范围 1.3（最宽的一档）", "Range 1.3 (the widest)")
        self.play(LaggedStart(*[FadeIn(m) for m in c2], lag_ratio=0.1), run_time=1.4)
        self.caption("同一个观测对应的专家动作互相矛盾，策略只能学个平均",
                     "The same observation now demands contradictory expert actions; the policy averages them",
                     wait=2.0)
        self.clear_stage()

        ax3 = Axes(x_range=[0, 1.4, 0.2], y_range=[0, 100, 25], x_length=9.6, y_length=3.6,
                   axis_config={"include_tip": False, "color": MUTED}).shift(DOWN * 0.4)
        cur_r = ax3.plot_line_graph(SCALES, REAL_CURVE, line_color=C_F,
                                   add_vertex_dots=True, stroke_width=4,
                                   vertex_dot_style={"fill_color": C_F, "radius": 0.06})
        cur_s = ax3.plot_line_graph(SCALES, SIM_CURVE, line_color=STEEL,
                                   add_vertex_dots=False, stroke_width=3)
        lab_r = zh("真机成功率", 26, C_F).next_to(ax3, UP, buff=0.12)
        lab_s = zh("仿真成功率", 26, STEEL).next_to(lab_r, RIGHT, buff=0.9)
        xlab = zh("域随机化范围", 24, MUTED).next_to(ax3, DOWN, buff=0.35)
        peak = Dot(ax3.c2p(0.2, 88.8), radius=0.12, color=YELLOW)
        peak_t = zh("最好的范围在中间", 26, YELLOW).next_to(peak, UP, buff=0.25)
        self.play(Create(ax3), FadeIn(xlab), run_time=1.0)
        self.play(Create(cur_s["line_graph"]), FadeIn(lab_s), run_time=1.0)
        self.play(Create(cur_r["line_graph"]), FadeIn(cur_r["vertex_dots"]),
                  FadeIn(lab_r), run_time=1.6)
        self.play(FadeIn(peak), FadeIn(peak_t), run_time=0.8)
        self.caption("真机那一列是一条倒 U 形曲线：太窄盖不住真机，太宽把信号抹平",
                     "The hardware column is an inverted U: too narrow misses the gap, too wide washes out the signal",
                     wait=2.4)

        self.card(["仿真成功率不是真机成功率",
                   ["报成绩一律两列，真机那一列要写明试了多少次",
                    "Always two columns, with the number of hardware trials"],
                   ["域随机化的范围有个最佳值，在中间，不在两端",
                    "The randomisation range has an optimum: in the middle, not at either end"],
                   ["范围调对了，代价会付在仿真那一列上",
                    "Get the range right and you pay for it in the simulation column"]], wait=3.4)
