"""第 161c 轮：WQ-CR5 整机三维（build123d），由机器人厂原件 cae/wqcr5.py 的 link_parts() 几何生成；案例 A、C 共用。"""
import numpy as np
import build123d as bd
from cae import wqcr5 as W


def arm_solid(q_deg=None):
    q_deg = W.HOME_DEG if q_deg is None else q_deg
    Tw = W.link_world(np.radians(q_deg))
    COL = {"L": (0.20, 0.45, 0.70), "M": (0.25, 0.60, 0.45), "S": (0.85, 0.55, 0.20)}
    pieces = []
    for i in range(6):
        for name, part, vis in W.link_parts(i):
            if not vis:
                continue
            kind = vis[0]
            T = Tw[i]
            if kind == "cylinder":
                _, r, h, c, ax_, _ = vis
                ax_ = np.asarray(ax_, float)
                ax_ /= np.linalg.norm(ax_)
                p0 = np.asarray(c, float) - ax_ * h / 2
                s = bd.Cylinder(r * 1000, h * 1000, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
                loc = bd.Location(bd.Plane(origin=tuple(p0 * 1000), z_dir=tuple(ax_)))
                s = s.moved(loc)
            elif kind == "capsule":
                _, r, _, a, b, _ = vis
                a, b = np.asarray(a, float), np.asarray(b, float)
                v = b - a
                Ln = np.linalg.norm(v)
                if Ln < 1e-6:
                    continue
                s = bd.Cylinder(r * 1000, Ln * 1000, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location(bd.Plane(origin=tuple(a * 1000), z_dir=tuple(v / Ln))))
            else:
                _, half, c, _ = vis
                s = bd.Pos(*(np.asarray(c) * 1000)) * bd.Box(*(2 * np.asarray(half) * 1000))
            s = s.moved(bd.Location(bd.Plane(origin=tuple(T[:3, 3] * 1000), x_dir=tuple(T[:3, 0]), z_dir=tuple(T[:3, 2]))))
            pieces.append(s)
    base = bd.Cylinder(70, W.BASE_TOP * 1000, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    j1 = bd.Pos(0, 0, W.BASE_TOP * 1000) * bd.Cylinder(W.MODULES["L"]["r"] * 1000, 60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    return bd.Compound([base, j1] + pieces)
