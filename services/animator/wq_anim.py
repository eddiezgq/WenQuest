"""WenQuest lesson animations: the shared parts every scene is written with.

The look follows the chapter-1 benchmark (samples/大学物理/生成脚本/anim/ch1.py): dark background,
title top-left, bilingual captions at the bottom, and a closing formula card. The AI animator writes
one `class Lesson(Base)` using these parts plus ordinary Manim objects.
"""
import numpy as np
from manim import *  # noqa: F401,F403

CJK = "Noto Sans CJK SC"
LATIN = "DejaVu Sans"
BG = "#0f1419"
INK = "#e6edf3"
MUTED = "#9aa7b2"
STEEL = "#58a6ff"
NAVY = "#1f3a5f"
C_V = ORANGE          # velocity
C_A = RED             # acceleration
C_F = "#ff7b72"       # force
C_X = BLUE            # x component
C_Y = GREEN           # y component
config.background_color = BG


def zh(s, size=30, color=WHITE, weight=NORMAL):
    """Chinese (or mixed) text."""
    return Text(str(s), font=CJK, font_size=size, color=color, weight=weight)


def en(s, size=20, color=MUTED):
    """English text, set smaller and grey under the Chinese."""
    return Text(str(s), font=LATIN, font_size=size * 0.92, color=color)


def bi(pair, size=28, color=WHITE, weight=NORMAL):
    """A [zh, en] pair stacked: Chinese above, English below."""
    z, e = (pair[0], pair[1]) if isinstance(pair, (list, tuple)) else (pair, "")
    top = zh(z, size, color, weight)
    return VGroup(top, en(e, size * 0.7)).arrange(DOWN, buff=0.08) if e else top


def fit(m, width=12.5):
    """Shrink a mobject that is wider than the frame allows."""
    if m.width > width:
        m.scale_to_fit_width(width)
    return m


class Base(Scene):
    """title(), caption() and card(): the frame every WenQuest animation shares."""

    _title = None
    _cap = None

    def title(self, no, zh_text, en_text=""):
        head = VGroup(zh(no, 26, YELLOW), zh(zh_text, 34, WHITE, BOLD)).arrange(RIGHT, buff=0.3)
        t = VGroup(head, en(en_text, 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.1) if en_text else head
        fit(t, 11).to_corner(UL, buff=0.4)
        self.play(FadeIn(t, shift=DOWN * 0.2), run_time=0.8)
        self._title = t
        return t

    def caption(self, zh_text, en_text="", wait=1.5):
        """Bottom caption in both languages; replaces the previous one."""
        new = zh(zh_text, 26, INK)
        if en_text:
            new = VGroup(new, en(en_text, 19)).arrange(DOWN, buff=0.08)
        fit(new, 12.8)
        bg = BackgroundRectangle(new, color=BG, fill_opacity=0.85, buff=0.15)
        g = VGroup(bg, new).to_edge(DOWN, buff=0.25)
        if self._cap is None:
            self.play(FadeIn(g, shift=UP * 0.15), run_time=0.6)
        else:
            self.play(FadeOut(self._cap, shift=UP * 0.15), FadeIn(g, shift=UP * 0.15), run_time=0.6)
        self._cap = g
        if wait:
            self.wait(wait)
        return g

    def clear_stage(self):
        """Fade out everything except the title and the caption."""
        keep = {id(self._title), id(self._cap)}
        gone = [m for m in self.mobjects if id(m) not in keep]
        if gone:
            self.play(*[FadeOut(m) for m in gone], run_time=0.6)

    def card(self, lines, wait=2.5):
        """Closing summary. lines: [zh, en] pairs, strings, or mobjects such as MathTex."""
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        body = []
        for i, x in enumerate(lines):
            if isinstance(x, Mobject):
                body.append(x)
            else:
                body.append(bi(x, 34 if i == 0 else 28, YELLOW if i == 0 else WHITE, BOLD if i == 0 else NORMAL))
        g = fit(VGroup(*body).arrange(DOWN, buff=0.3), 12)
        box = SurroundingRectangle(g, color=YELLOW, buff=0.45, corner_radius=0.15, stroke_width=2)
        self.play(Create(box), LaggedStart(*[Write(m) for m in body], lag_ratio=0.35), run_time=2.2)
        self.wait(wait)


# --- things to draw --------------------------------------------------------------------------------

def ground(y=-2.2, x0=-7, x1=7, color=GREY_B):
    """A floor line with hatching."""
    line = Line([x0, y, 0], [x1, y, 0], color=color, stroke_width=3)
    hatch = VGroup(*[Line([x, y, 0], [x - 0.25, y - 0.25, 0], color=color, stroke_width=1.5)
                     for x in np.arange(x0 + 0.3, x1, 0.45)])
    return VGroup(line, hatch)


def agv(width=2.6, height=0.7, color=STEEL, label=""):
    """A warehouse AGV (automated guided vehicle): body, wheels, sensor. Bottom sits on y=0 of its own frame."""
    body = RoundedRectangle(width=width, height=height, corner_radius=0.12, color=color,
                            fill_color=NAVY, fill_opacity=1, stroke_width=3)
    wheels = VGroup(*[Circle(0.18, color=GREY_B, fill_color=GREY_D, fill_opacity=1, stroke_width=2)
                      for _ in range(2)]).arrange(RIGHT, buff=width - 1.0)
    wheels.next_to(body, DOWN, buff=-0.12)
    lidar = Dot(body.get_corner(UR) + LEFT * 0.25 + DOWN * 0.15, radius=0.07, color=YELLOW)
    g = VGroup(body, wheels, lidar)
    if label:
        g.add(zh(label, 20, INK).move_to(body))
    g.shift(-g.get_bottom())
    return g


def cargo(size=0.8, color="#d29922", label=""):
    """A cardboard box."""
    b = Square(size, color=color, fill_color="#5a3d0a", fill_opacity=1, stroke_width=3)
    tape = Line(b.get_top(), b.get_bottom(), color=color, stroke_width=2)
    g = VGroup(b, tape)
    if label:
        g.add(zh(label, 18, INK).move_to(b))
    return g


def conveyor(length=6, height=0.35):
    """A belt conveyor: belt and rollers."""
    belt = RoundedRectangle(width=length, height=height, corner_radius=height / 2, color=GREY_B, stroke_width=3)
    rollers = VGroup(*[Circle(height / 2 - 0.04, color=GREY_C, stroke_width=2).move_to(belt.get_left() + RIGHT * (height / 2 + i * (length - height) / 5))
                       for i in range(6)])
    return VGroup(belt, rollers)


def arm(base=ORIGIN, a1=60, a2=-30, l1=2.2, l2=1.6, color=STEEL):
    """A two-link robot arm; angles in degrees (a2 relative to the first link). Returns VGroup(links, joints, gripper)."""
    b = np.array(base, dtype=float)
    t1 = np.radians(a1)
    t2 = t1 + np.radians(a2)
    j = b + l1 * np.array([np.cos(t1), np.sin(t1), 0])
    e = j + l2 * np.array([np.cos(t2), np.sin(t2), 0])
    pedestal = Polygon(b + LEFT * 0.5 + DOWN * 0.3, b + RIGHT * 0.5 + DOWN * 0.3, b + RIGHT * 0.25, b + LEFT * 0.25,
                       color=GREY_B, fill_color=GREY_E, fill_opacity=1)
    links = VGroup(Line(b, j, color=color, stroke_width=14), Line(j, e, color=color, stroke_width=10))
    joints = VGroup(Dot(b, radius=0.14, color=WHITE), Dot(j, radius=0.12, color=WHITE))
    grip = VGroup(Line(e, e + 0.3 * np.array([np.cos(t2 + 0.5), np.sin(t2 + 0.5), 0]), color=WHITE, stroke_width=5),
                  Line(e, e + 0.3 * np.array([np.cos(t2 - 0.5), np.sin(t2 - 0.5), 0]), color=WHITE, stroke_width=5))
    return VGroup(pedestal, links, joints, grip)


def arm_tip(base=ORIGIN, a1=60, a2=-30, l1=2.2, l2=1.6):
    """Where the gripper of arm(...) is."""
    t1 = np.radians(a1)
    t2 = t1 + np.radians(a2)
    return np.array(base, dtype=float) + l1 * np.array([np.cos(t1), np.sin(t1), 0]) + l2 * np.array([np.cos(t2), np.sin(t2), 0])


def drone(width=1.8, color=STEEL):
    """A quadcopter seen from the side."""
    body = RoundedRectangle(width=0.8, height=0.3, corner_radius=0.1, color=color, fill_color=NAVY, fill_opacity=1)
    armline = Line(LEFT * width / 2, RIGHT * width / 2, color=GREY_B, stroke_width=4)
    props = VGroup(*[Line(LEFT * 0.35, RIGHT * 0.35, color=WHITE, stroke_width=3).move_to(p + UP * 0.15)
                     for p in (LEFT * width / 2, RIGHT * width / 2)])
    return VGroup(armline, body, props)


def vec(start, end, color=C_V, label=None, label_dir=UP, size=34, width=5):
    """An arrow for a vector quantity, with an optional LaTeX label (e.g. r"\\vec v")."""
    a = Arrow(np.array(start, dtype=float), np.array(end, dtype=float), buff=0, color=color, stroke_width=width,
              max_tip_length_to_length_ratio=0.25)
    if label:
        return VGroup(a, MathTex(label, color=color, font_size=size).next_to(a.get_end(), label_dir, buff=0.1))
    return a


def readout(name, value, unit="", color=WHITE, size=30):
    """A 'v = 1.50 m/s' style number display; rebuild it inside always_redraw to animate the value."""
    return MathTex(r"%s = %s\,\mathrm{%s}" % (name, value, unit) if unit else r"%s = %s" % (name, value),
                   color=color, font_size=size)


# --- robotics parts (round 3, team rebuild): frames, rotations, n-link arms, mobile robots, sensors -----

def rot_z(deg):
    """3x3 rotation about z (degrees)."""
    t = np.radians(deg)
    return np.array([[np.cos(t), -np.sin(t), 0], [np.sin(t), np.cos(t), 0], [0, 0, 1]])


def rot_y(deg):
    t = np.radians(deg)
    return np.array([[np.cos(t), 0, np.sin(t)], [0, 1, 0], [-np.sin(t), 0, np.cos(t)]])


def rot_x(deg):
    t = np.radians(deg)
    return np.array([[1, 0, 0], [0, np.cos(t), -np.sin(t)], [0, np.sin(t), np.cos(t)]])


def proj3(p, origin=ORIGIN, scale=1.0):
    """A 3D point on the 2D screen (oblique view: x to the lower left, y to the right, z up)."""
    x, y, z = (float(v) for v in p)
    return np.array(origin, dtype=float) + scale * np.array([y - 0.55 * x, z - 0.35 * x, 0])


def frame2(origin=ORIGIN, angle=0, length=1.2, labels=("x", "y"), color=STEEL, name=None):
    """A 2D coordinate frame: two arrows (angle in degrees) with labels, optional frame name like r"\\{B\\}"."""
    o = np.array(origin, dtype=float)
    t = np.radians(angle)
    ex = np.array([np.cos(t), np.sin(t), 0]) * length
    ey = np.array([-np.sin(t), np.cos(t), 0]) * length
    g = VGroup(Arrow(o, o + ex, buff=0, color=RED, stroke_width=5), Arrow(o, o + ey, buff=0, color=GREEN, stroke_width=5),
               MathTex(labels[0], color=RED, font_size=30).move_to(o + ex * 1.18),
               MathTex(labels[1], color=GREEN, font_size=30).move_to(o + ey * 1.18), Dot(o, radius=0.05, color=color))
    if name:
        g.add(MathTex(name, color=color, font_size=28).next_to(Dot(o), DL, buff=0.1))
    return g


def frame3(origin=ORIGIN, R=None, length=1.2, labels=("x", "y", "z"), scale=1.0, name=None):
    """A 3D coordinate frame (rotation matrix R, 3x3) drawn with proj3; x red, y green, z blue."""
    R = np.eye(3) if R is None else np.array(R, dtype=float)
    o = np.array(origin, dtype=float)
    g = VGroup()
    for i, col in enumerate((RED, GREEN, BLUE)):
        tip = proj3(R[:, i] * length, o, scale)
        g.add(Arrow(o, tip, buff=0, color=col, stroke_width=5))
        g.add(MathTex(labels[i], color=col, font_size=28).move_to(o + (tip - o) * 1.18))
    if name:
        g.add(MathTex(name, color=INK, font_size=28).next_to(Dot(o), DL, buff=0.1))
    return g


def planar_fk(base, angles, lengths):
    """Joint points of a planar n-link arm (angles in degrees, each relative to the previous link)."""
    pts = [np.array(base, dtype=float)]
    t = 0.0
    for a, l in zip(angles, lengths):
        t += np.radians(a)
        pts.append(pts[-1] + l * np.array([np.cos(t), np.sin(t), 0]))
    return pts


def planar_arm(base, angles, lengths, color=STEEL, joint_labels=None):
    """A planar n-link arm: pedestal, links, joints and a gripper at the end (see planar_fk)."""
    pts = planar_fk(base, angles, lengths)
    b = pts[0]
    pedestal = Polygon(b + LEFT * 0.5 + DOWN * 0.3, b + RIGHT * 0.5 + DOWN * 0.3, b + RIGHT * 0.25, b + LEFT * 0.25,
                       color=GREY_B, fill_color=GREY_E, fill_opacity=1)
    links = VGroup(*[Line(p, q, color=color, stroke_width=max(6, 14 - 3 * i)) for i, (p, q) in enumerate(zip(pts, pts[1:]))])
    joints = VGroup(*[Dot(p, radius=0.12, color=WHITE) for p in pts[:-1]])
    t = np.radians(sum(angles))
    e = pts[-1]
    grip = VGroup(Line(e, e + 0.3 * np.array([np.cos(t + 0.5), np.sin(t + 0.5), 0]), color=WHITE, stroke_width=5),
                  Line(e, e + 0.3 * np.array([np.cos(t - 0.5), np.sin(t - 0.5), 0]), color=WHITE, stroke_width=5))
    g = VGroup(pedestal, links, joints, grip)
    if joint_labels:
        for p, lab in zip(pts, joint_labels):
            g.add(MathTex(lab, color=YELLOW, font_size=26).next_to(Dot(p), UR, buff=0.08))
    return g


def mobile_robot(pos=ORIGIN, heading=0, size=0.9, color=STEEL):
    """A differential-drive mobile robot seen from above (heading in degrees): body, two wheels, front marker."""
    body = Circle(radius=size / 2, color=color, fill_color=NAVY, fill_opacity=1, stroke_width=3)
    wheels = VGroup(*[RoundedRectangle(width=size * 0.35, height=size * 0.12, corner_radius=0.03, color=GREY_B,
                                       fill_color=GREY_D, fill_opacity=1).move_to(UP * s * size * 0.52) for s in (1, -1)])
    front = Triangle(color=YELLOW, fill_color=YELLOW, fill_opacity=1).scale(size * 0.12).rotate(-PI / 2).move_to(RIGHT * size * 0.3)
    g = VGroup(body, wheels, front)
    g.rotate(np.radians(heading))
    return g.move_to(np.array(pos, dtype=float))


def lidar(center, angles_deg, ranges, color=YELLOW):
    """Laser rays from `center` (degrees and lengths) with hit points."""
    c = np.array(center, dtype=float)
    g = VGroup()
    for a, r in zip(angles_deg, ranges):
        t = np.radians(a)
        end = c + r * np.array([np.cos(t), np.sin(t), 0])
        g.add(Line(c, end, color=color, stroke_width=1.5, stroke_opacity=0.6), Dot(end, radius=0.04, color=color))
    return g


def matrix_tex(M, digits=2, color=WHITE, size=30):
    """A numeric matrix as LaTeX (e.g. a rotation or transform)."""
    rows = r" \\ ".join(" & ".join(f"{float(v):.{digits}f}" for v in row) for row in np.array(M))
    return MathTex(r"\begin{bmatrix}" + rows + r"\end{bmatrix}", color=color, font_size=size)
