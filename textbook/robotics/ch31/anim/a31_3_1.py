"""动画 31.3.1（配图 31.3.1）：一次有限元分析。
(1) 几何：WQ-CR5 大臂，Ø90×3 铝管 + 两端法兰，长 400 mm（问渠 CAE 示例零件），侧视。
(2) 网格：切成三角形（示意四面体网格）。
(3) 约束与载荷：J2 端固定；J3 端向下 119.8 N、弯矩 41.1 N·m、扭矩 7.0 N·m。
(4) 结果：应力从根部（约 5 MPa）向外由红变蓝；法兰内角一个小红点（应力集中）。
(5) 网格加密：14 → 10 → 7 mm，端部下沉 0.1085 → 0.1087 → 0.1089 mm（梁理论 0.1091），法兰内角的最大应力 5.43 → 5.47 → 5.72 MPa 还在涨（程序 31.3.1）。"""
from manim import *
from wq_anim import *
import numpy as np


def heat(t):
    """0 → 蓝，1 → 红"""
    cols = [BLUE_E, BLUE, TEAL, GREEN, YELLOW, ORANGE, RED]
    t = min(1, max(0, t))
    i = min(len(cols) - 2, int(t * (len(cols) - 1)))
    return interpolate_color(ManimColor(cols[i]), ManimColor(cols[i + 1]), t * (len(cols) - 1) - i)


class Lesson(Base):
    def construct(self):
        self.title("31.3", "一次有限元分析", "One finite-element analysis")
        L, H = 10.0, 2.25                         # 400 mm → 10 格，90 mm → 2.25 格
        o = np.array([-5.0, 0.6, 0])
        out = Rectangle(width=L, height=H, color=STEEL, stroke_width=3).move_to(o + RIGHT * L / 2)
        inner = Rectangle(width=L - 0.5, height=H - 0.15, color=STEEL, stroke_width=1.5).move_to(o + RIGHT * L / 2)
        self.play(Create(out), Create(inner), run_time=1.2)
        self.caption("几何：Ø90×3 铝管，两端各一块 10 mm 的法兰，长 400 mm", "Geometry: a Ø90×3 aluminium tube with two 10 mm flanges, 400 mm long", wait=1.0)
        # 网格：三角形
        nx, ny = 24, 5
        tris = VGroup()
        cells = []
        for i in range(nx):
            for j in range(ny):
                x0, x1 = o[0] + L * i / nx, o[0] + L * (i + 1) / nx
                y0, y1 = o[1] - H / 2 + H * j / ny, o[1] - H / 2 + H * (j + 1) / ny
                for pts in (((x0, y0), (x1, y0), (x1, y1)), ((x0, y0), (x1, y1), (x0, y1))):
                    t = Polygon(*[np.array([p[0], p[1], 0]) for p in pts], color=GREY_B, stroke_width=0.8, fill_opacity=0)
                    tris.add(t)
                    cells.append(((x0 + x1) / 2 - o[0]) / L)
        self.play(LaggedStart(*[Create(t) for t in tris], lag_ratio=0.002), run_time=2.0)
        self.caption("网格：切成小单元（实际是二阶四面体，每个 10 个节点）", "Mesh: small elements (really 10-node tetrahedra)", wait=0.8)
        fix = VGroup(*[Line(o + UP * (H / 2 - k * H / 6), o + UP * (H / 2 - k * H / 6) + LEFT * 0.35 + DOWN * 0.2, color=GREY_B) for k in range(7)])
        fl = Arrow(o + RIGHT * L + UP * 1.6, o + RIGHT * L + UP * 0.2, color=C_F, buff=0)
        mm = Arc(radius=0.7, start_angle=PI / 2, angle=-PI, arc_center=o + RIGHT * (L + 0.3), color=ORANGE, stroke_width=5).add_tip()
        self.play(Create(fix), GrowArrow(fl), Create(mm))
        self.caption("J2 端固定；J3 端：向下 119.8 N、弯矩 41.1 N·m、扭矩 7.0 N·m（截面法交出来的力）",
                     "J2 end fixed; J3 end: 119.8 N down, 41.1 N·m bending, 7.0 N·m torsion (from the method of sections)", wait=1.2)
        # 结果：按到中性轴的距离和截面弯矩上色
        anims = []
        for t, xr in zip(tris, cells):
            yc = t.get_center()[1] - o[1]
            m = (41.06 + 119.8 * 0.4 * (1 - xr)) / 89.0
            v = m * abs(yc) / (H / 2) * 0.95
            anims.append(t.animate.set_fill(heat(v), opacity=0.9))
        self.play(*anims, run_time=1.8)
        hot = Dot(o + RIGHT * (L - 0.25) + UP * (H / 2 - 0.08), color=RED, radius=0.12)
        self.play(FadeIn(hot, scale=2.0), Flash(hot, color=RED))
        self.caption("应力云图：根部、上下表面最大；法兰内角一个“热点”——应力集中", "The stress map: largest at the root's top and bottom; a hot spot at the flange's inner corner", wait=1.5)
        self.clear_stage()
        # 网格收敛
        head = VGroup(zh("网格 / mm", 22, MUTED), zh("端部下沉 / mm", 22, MUTED), zh("法兰内角最大应力 / MPa", 22, MUTED)).arrange(RIGHT, buff=0.7)
        rows = [("14", "0.1085", "5.43"), ("10", "0.1087", "5.47"), ("7", "0.1089", "5.72"), ("梁理论", "0.1091", "—")]
        tab = VGroup(head)
        for r in rows:
            tab.add(VGroup(*[zh(x, 24, INK) for x in r]).arrange(RIGHT, buff=0.7))
        for row in tab[1:]:
            for k in range(3):
                row[k].move_to([head[k].get_center()[0], row.get_center()[1], 0])
        tab.arrange(DOWN, buff=0.35).move_to(UP * 0.4)
        for row in tab[1:]:
            for k in range(3):
                row[k].set_x(head[k].get_center()[0])
        self.play(FadeIn(head))
        for row in tab[1:]:
            self.play(FadeIn(row, shift=UP * 0.1), run_time=0.7)
        self.caption("位移收敛、与梁理论一致；尖角的应力不收敛——要加圆角", "Displacement converges and matches beam theory; the sharp corner's stress does not — add a fillet", wait=1.5)
        self.card([["有限元入门", "A first finite-element analysis"],
                   ["几何 → 网格 → 材料 → 约束与载荷 → 求解与后处理", "Geometry → mesh → material → supports and loads → solve and read"],
                   ["每个数都和手算对一对：合力、位移、远处的应力", "Check every number by hand: resultant, displacement, stress away from the ends"],
                   ["这根管自己第一阶 433 Hz；装到机器人上整机只有十几赫兹", "This tube alone: 433 Hz; on the robot the whole arm: a dozen hertz"]])
