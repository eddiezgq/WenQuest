"""动画 23.2.1（配图 23.2.1）：鸟瞰图是算出来的，所以标定错一点点，远处就差出几个车身。

五段：
1. 真实场景：一条双车道直道，前车在 50 m，路侧有锥桶——**这些位置是要用的量，不是要看的画面**；
2. 相机像素：同样这几个目标投到像平面上，10 m 的在第 662 行，50 m 与 80 m 挤在十几行里；
3. 俯视网格：把像素按“地面是平的 + 相机位姿已知”反投成俯视格子——**鸟瞰图是算出来的**；
4. 位姿错一点点：俯视角差 0.3°、高度差 2 cm、偏航角差 0.3°，纵向误差 10 m 处 0.24 m、
   50 m 处 7.2 m（约 1.5 个车身），**差 30 倍**；偏航角再错到 2°，50 m 处横向就差半个车道；
5. 最坏的消息：三项残差一起错时，50 m 处的横向误差几乎互相抵消（只有单独偏航角错的 0.10 倍）——
   **在一个点上验收全是绿的**，换个距离、换条车道就露馅。

渲染服务只允许 manim、wq_anim、numpy、math、random，所以小孔模型的正反投影在这里重算一遍
（与 code/_ch23.py 的 ground_to_pixel / pixel_to_ground 同一套公式）。
"""
import math

import numpy as np
from manim import *
from wq_anim import *

F = 1200.0                  # 焦距（像素）
CX, CY = 960.0, 540.0
W_PX, H_PX = 1920.0, 1080.0
PITCH = 0.040               # 标称俯视角（rad，约 2.3°）
HEIGHT = 1.42               # 标称安装高度（m）
LANE_W = 3.5
VEH_LEN = 4.8
LAT = 1.75                  # 取车道中心线上的点

D_PITCH = 0.3               # 标定残差（°、m、°），与算例 23.1 同一套显式假设
D_HEIGHT = 0.02
D_YAW = 0.3
YAW_BAD = 2.0               # 另一档：偏航角错到 2°


def to_pixel(X, Y, pitch, height, yaw=0.0):
    """地面点（车体坐标 X 前、Y 左，m）→ 像素（u 右、v 下）。"""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    sp, cp = math.sin(pitch), math.cos(pitch)
    sy, cyw = math.sin(yaw), math.cos(yaw)
    z_c = X * cp * cyw + Y * cp * sy + height * sp
    y_c = -X * sp * cyw - Y * sp * sy + height * cp
    x_c = X * sy - Y * cyw
    return CX + F * x_c / z_c, CY + F * y_c / z_c


def to_ground(u, v, pitch, height, yaw=0.0):
    """像素 → 地面（**假设地面是平的**）。标定参数错了，这一步就错。"""
    u = np.asarray(u, dtype=float)
    v = np.asarray(v, dtype=float)
    sp, cp = math.sin(pitch), math.cos(pitch)
    sy, cyw = math.sin(yaw), math.cos(yaw)
    a = (u - CX) / F
    b = (v - CY) / F
    t = height / (b * cp + sp)
    X = t * (a * sy - b * sp * cyw + cp * cyw)
    Y = t * (-a * cyw - b * sp * sy + cp * sy)
    return X, Y


def err_at(dist, d_pitch_deg, d_height_m, d_yaw_deg):
    """标定残差折成地面上的误差（纵向 m、横向 m）。"""
    u, v = to_pixel(dist, np.full_like(dist, LAT), PITCH, HEIGHT)
    Xe, Ye = to_ground(u, v, PITCH + math.radians(d_pitch_deg), HEIGHT + d_height_m,
                       yaw=math.radians(d_yaw_deg))
    return np.abs(Xe - dist), np.abs(Ye - LAT)


class Lesson(Base):
    def construct(self):
        self.title("23.2", "鸟瞰图是算出来的，不是拍出来的",
                   "The bird's-eye view is computed, not photographed")

        # ---------------- 一、真实场景：要的是位置，不是画面
        self.caption("一条双车道直道：前车在 50 m 外，路侧有锥桶",
                     "A two-lane straight road: the lead car 50 m ahead, cones along the shoulder",
                     wait=1.2)
        road = Rectangle(width=11.0, height=2.6, color=NAVY, fill_opacity=0.55,
                         stroke_width=0).shift(UP * 0.5)
        mid = DashedLine(road.get_left() + RIGHT * 0.1, road.get_right() + LEFT * 0.1,
                         color=MUTED, stroke_width=3).shift(UP * 0.5)
        ego = Rectangle(width=1.1, height=0.55, color=STEEL, fill_opacity=0.9,
                        stroke_width=0).move_to(road.get_left() + RIGHT * 1.2 + DOWN * 0.1)
        lead = Rectangle(width=1.1, height=0.55, color=YELLOW, fill_opacity=0.9,
                         stroke_width=0).move_to(road.get_right() + LEFT * 1.6 + DOWN * 0.1)
        cones = VGroup(*[Triangle(color=C_F, fill_opacity=0.9, stroke_width=0).scale(0.14)
                         .move_to(road.get_bottom() + RIGHT * x + UP * 0.12)
                         for x in (-3.4, -1.2, 1.1, 3.3)])
        l_ego = zh("自车", 24, STEEL).next_to(ego, DOWN, buff=0.2)
        l_lead = zh("前车 50 m", 24, YELLOW).next_to(lead, UP, buff=0.2)
        self.play(FadeIn(road), Create(mid), run_time=0.9)
        self.play(FadeIn(ego), FadeIn(l_ego), FadeIn(lead), FadeIn(l_lead),
                  FadeIn(cones), run_time=1.1)
        self.caption("规划要的是这些目标在哪里（米），不是一张好看的画面",
                     "What the planner needs is where these objects are, in metres — not a picture",
                     wait=1.8)
        self.clear_stage()

        # ---------------- 二、相机只给像素，远处挤在十几行里
        self.caption("可是相机只给像素：同样这几个距离，落在第几行",
                     "But the camera only gives pixels: which row does each distance land on?",
                     wait=1.4)
        img = Rectangle(width=9.6, height=5.4, color=MUTED, stroke_width=2).shift(UP * 0.1)
        sx, sy = 9.6 / W_PX, 5.4 / H_PX

        def at_px(u, v):
            return img.get_corner(UL) + RIGHT * (u * sx) + DOWN * (v * sy)

        hor_v = CY - F * math.tan(PITCH)
        hor = Line(at_px(0.0, hor_v), at_px(W_PX, hor_v), color=YELLOW, stroke_width=2)
        l_hor = zh(f"地平线：第 {hor_v:.0f} 行", 22, YELLOW).next_to(hor, UP, buff=0.08)
        self.play(Create(img), run_time=0.7)
        self.play(Create(hor), FadeIn(l_hor), run_time=0.9)

        dists = np.array([10.0, 30.0, 50.0, 80.0])
        u_d, v_d = to_pixel(dists, np.full_like(dists, LAT), PITCH, HEIGHT)
        marks = VGroup()
        for i, d in enumerate(dists):
            dot = Dot(at_px(float(u_d[i]), float(v_d[i])), radius=0.07, color=STEEL)
            tag = zh(f"{d:.0f} m → 第 {v_d[i]:.0f} 行", 22, INK).next_to(dot, RIGHT, buff=0.2)
            marks.add(VGroup(dot, tag))
        self.play(LaggedStart(*[FadeIn(m) for m in marks], lag_ratio=0.3), run_time=1.8)
        self.caption(f"10 m 的目标在第 {v_d[0]:.0f} 行，50 m 与 80 m 只差 "
                     f"{abs(v_d[2] - v_d[3]):.0f} 行——远处那一段，像素根本不够",
                     "Ten metres sits far down the frame; 50 m and 80 m are a dozen rows apart",
                     wait=2.2)
        self.clear_stage()

        # ---------------- 三、俯视网格：按“地面是平的 + 位姿已知”反投出来
        self.caption("鸟瞰图是这样来的：假设地面是平的、相机位姿已知，把像素反投成俯视格子",
                     "The BEV grid comes from two assumptions: a flat ground and a known camera pose",
                     wait=1.6)
        ax = Axes(x_range=[0, 80, 20], y_range=[-6, 6, 3], x_length=10.4, y_length=2.8,
                  axis_config={"include_tip": False, "color": MUTED}).shift(UP * 0.3)
        grid = VGroup(*[Line(ax.c2p(x, -6), ax.c2p(x, 6), color=NAVY, stroke_width=1)
                        for x in np.arange(0, 81, 4)]
                      + [Line(ax.c2p(0, y), ax.c2p(80, y), color=NAVY, stroke_width=1)
                         for y in np.arange(-6, 6.1, 1.75)])
        self.play(Create(ax), run_time=0.7)
        self.play(Create(grid), run_time=1.2)
        u_g, v_g = to_pixel(dists, np.full_like(dists, LAT), PITCH, HEIGHT)
        X_ok, Y_ok = to_ground(u_g, v_g, PITCH, HEIGHT)
        ok = VGroup(*[Dot(ax.c2p(float(X_ok[i]), float(Y_ok[i])), radius=0.09, color=STEEL)
                      for i in range(len(dists))])
        self.play(FadeIn(ok), run_time=0.8)
        self.caption("位姿标得准，反投回来的点就落在真位置上——这一步没有任何测量，全是算的",
                     "With the pose right, the points land where they truly are: pure computation",
                     wait=2.0)
        self.clear_stage()

        # ---------------- 四、位姿错一点点：远处放大多少
        self.caption(f"标定残差：俯视角 +{D_PITCH}°、高度 +{D_HEIGHT * 100:.0f} cm、"
                     f"偏航角 +{D_YAW}°——都在正常范围内",
                     "Residuals well within normal: +0.3° pitch, +2 cm height, +0.3° yaw",
                     wait=1.6)
        dd = np.arange(5.0, 81.0, 1.0)
        lon_both, lat_both = err_at(dd, D_PITCH, D_HEIGHT, D_YAW)
        ax2 = Axes(x_range=[0, 80, 20], y_range=[0, 20, 5], x_length=10.0, y_length=3.4,
                   axis_config={"include_tip": False, "color": MUTED}).shift(UP * 0.2)
        curve = ax2.plot_line_graph(dd, lon_both, line_color=C_F, add_vertex_dots=False,
                                    stroke_width=4)["line_graph"]
        l_ax2 = zh("横轴：目标有多远（m）　纵轴：纵向定位误差（m）", 24, MUTED) \
            .next_to(ax2, UP, buff=0.12)
        self.play(Create(ax2), FadeIn(l_ax2), run_time=0.8)
        self.play(Create(curve), run_time=1.6)

        e10 = float(err_at(np.array([10.0]), D_PITCH, D_HEIGHT, D_YAW)[0][0])
        e50 = float(err_at(np.array([50.0]), D_PITCH, D_HEIGHT, D_YAW)[0][0])
        d10 = Dot(ax2.c2p(10.0, e10), radius=0.1, color=YELLOW)
        d50 = Dot(ax2.c2p(50.0, e50), radius=0.1, color=YELLOW)
        t10 = zh(f"10 m 处：{e10:.2f} m", 24, YELLOW).next_to(d10, UR, buff=0.12)
        t50 = zh(f"50 m 处：{e50:.1f} m ≈ {e50 / VEH_LEN:.1f} 个车身", 24, YELLOW) \
            .next_to(d50, UP, buff=0.2)
        self.play(FadeIn(d10), FadeIn(t10), run_time=0.8)
        self.play(FadeIn(d50), FadeIn(t50), run_time=0.8)
        self.caption(f"同一套残差，50 m 处比 10 m 处大 {e50 / e10:.0f} 倍——"
                     f"近处标得准，不说明远处标得准",
                     f"The same residuals are {e50 / e10:.0f}× worse at 50 m than at 10 m",
                     wait=2.2)
        self.clear_stage()

        # ---------------- 四（续）、偏航角错 2°：判到隔壁车道
        self.caption(f"把偏航角残差放到 {YAW_BAD:.0f}°（仍然只是两度），50 m 处横向差多少",
                     f"Let the yaw residual grow to {YAW_BAD:.0f}°: how far sideways at 50 m?",
                     wait=1.4)
        lat_bad = float(err_at(np.array([50.0]), 0.0, 0.0, YAW_BAD)[1][0])
        lane_a = Rectangle(width=9.0, height=1.3, color=NAVY, fill_opacity=0.45,
                           stroke_width=0).shift(UP * 1.0)
        lane_b = Rectangle(width=9.0, height=1.3, color=NAVY, fill_opacity=0.25,
                           stroke_width=0).shift(DOWN * 0.3)
        edge = DashedLine(lane_a.get_left() + DOWN * 0.65, lane_a.get_right() + DOWN * 0.65,
                          color=MUTED, stroke_width=3)
        scale_y = 1.3 / LANE_W
        true_dot = Dot(lane_b.get_center() + RIGHT * 2.0, radius=0.11, color=STEEL)
        bad_dot = Dot(true_dot.get_center() + UP * (lat_bad * scale_y), radius=0.11, color=C_F)
        arrow = Arrow(true_dot.get_center(), bad_dot.get_center(), color=C_F,
                      stroke_width=4, buff=0.0)
        l_true = zh("真位置：本车道", 24, STEEL).next_to(true_dot, DOWN, buff=0.25)
        l_bad = zh(f"算出来的位置：偏 {lat_bad:.2f} m", 24, C_F).next_to(bad_dot, UP, buff=0.25)
        self.play(FadeIn(lane_a), FadeIn(lane_b), Create(edge), run_time=0.9)
        self.play(FadeIn(true_dot), FadeIn(l_true), run_time=0.7)
        self.play(GrowArrow(arrow), FadeIn(bad_dot), FadeIn(l_bad), run_time=1.0)
        self.caption(f"{lat_bad:.2f} m = {lat_bad / LANE_W:.2f} 个车道宽："
                     f"50 m 外的车被判到了车道线上，规划会按错的车道去让行",
                     "Half a lane wide at 50 m: the car is placed on the lane line, and the planner "
                     "yields to the wrong lane",
                     wait=2.2)
        self.clear_stage()

        # ---------------- 五、一个点看不出问题，换个点就露馅
        self.caption("最坏的消息在这里：三项残差一起错时，它们会互相抵消",
                     "The worst news: with all three residuals at once, they can cancel",
                     wait=1.6)
        lon_y, lat_y = err_at(dd, 0.0, 0.0, D_YAW)
        ax3 = Axes(x_range=[0, 80, 20], y_range=[0, 0.5, 0.1], x_length=10.0, y_length=3.2,
                   axis_config={"include_tip": False, "color": MUTED}).shift(UP * 0.2)
        c_yaw = ax3.plot_line_graph(dd, lat_y, line_color=STEEL, add_vertex_dots=False,
                                    stroke_width=4)["line_graph"]
        c_all = ax3.plot_line_graph(dd, lat_both, line_color=C_F, add_vertex_dots=False,
                                    stroke_width=4)["line_graph"]
        l_ax3 = zh("横轴：目标有多远（m）　纵轴：横向定位误差（m）", 24, MUTED) \
            .next_to(ax3, UP, buff=0.12)
        self.play(Create(ax3), FadeIn(l_ax3), run_time=0.8)
        self.play(Create(c_yaw), run_time=1.2)
        lab_y = zh("只偏航角错", 24, STEEL).next_to(ax3.c2p(66.0, float(lat_y[-10])), UP, buff=0.25)
        self.play(FadeIn(lab_y), run_time=0.5)
        self.play(Create(c_all), run_time=1.2)
        lab_a = zh("三项一起错", 24, C_F).next_to(ax3.c2p(60.0, float(lat_both[-20])), DOWN, buff=0.3)
        self.play(FadeIn(lab_a), run_time=0.5)

        lat_y50 = float(err_at(np.array([50.0]), 0.0, 0.0, D_YAW)[1][0])
        lat_a50 = float(err_at(np.array([50.0]), D_PITCH, D_HEIGHT, D_YAW)[1][0])
        mark = Line(ax3.c2p(50.0, 0.0), ax3.c2p(50.0, 0.5), color=YELLOW, stroke_width=2)
        note = zh(f"50 m 处：{lat_a50:.3f} m，只有单独偏航角错的 {lat_a50 / lat_y50:.2f} 倍",
                  24, YELLOW).next_to(ax3, DOWN, buff=0.25)
        self.play(Create(mark), FadeIn(note), run_time=1.0)
        self.caption("俯视角错把距离算远了、把横向按比例缩小，正好与偏航角错的方向相反——"
                     "就在这一点上，验收全是绿的",
                     "The pitch error shrinks the lateral estimate just as the yaw error grows it: "
                     "at this one point the acceptance test passes",
                     wait=2.4)

        self.card(["标定验收不能只看一个点",
                   "鸟瞰图是算出来的：位姿错一点点，远处就差几个车身",
                   f"同一套残差，50 m 比 10 m 大 {e50 / e10:.0f} 倍；三项一起错还会互相抵消",
                   "所以要沿整条距离、整个横向范围逐点报，而不是报一个最大值"], wait=3.4)
