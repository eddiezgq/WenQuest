# -*- coding: utf-8 -*-
"""
WenQuest FreeCAD Lab · 渐开线直齿圆柱齿轮（参数化）

用法：
  - FreeCAD 界面：宏 → 宏… → 选中本文件 → 执行
  - 命令行（不开界面）："C:\\Program Files\\FreeCAD 1.1\\bin\\FreeCADCmd.exe" macros\\wq_gear.py
修改下面 PARAMS 里的数值，再运行一次，就得到新的齿轮。

几何计算部分（gear_* 函数）是纯 Python，不依赖 FreeCAD，可以单独测试：
  python -m pytest tests
"""
import math
import os

PARAMS = {
    "m": 2.0,          # 模数 mm
    "z": 24,           # 齿数
    "alpha_deg": 20.0, # 压力角 °
    "ha_star": 1.0,    # 齿顶高系数
    "c_star": 0.25,    # 顶隙系数
    "b": 20.0,         # 齿宽 mm
    "bore": 12.0,      # 轴孔直径 mm（0 表示不开孔）
    "flank_points": 12 # 每条齿廓曲线的插值点数
}

OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "freecad-lab-output")


# ---------------------------------------------------------------- 纯几何计算
def inv(a):
    """渐开线函数 inv(α) = tan α − α"""
    return math.tan(a) - a


def gear_dimensions(m, z, alpha_deg=20.0, ha_star=1.0, c_star=0.25):
    """标准直齿轮的主要尺寸（mm）和校核结果。"""
    alpha = math.radians(alpha_deg)
    d = m * z                              # 分度圆直径
    db = d * math.cos(alpha)               # 基圆直径
    da = d + 2 * ha_star * m               # 齿顶圆直径
    df = d - 2 * (ha_star + c_star) * m    # 齿根圆直径
    p = math.pi * m                        # 齿距
    ra, rb = da / 2, db / 2
    psi_b = math.pi / (2 * z) + inv(alpha)            # 基圆上半齿厚对应的角度
    theta_a = inv(math.acos(rb / ra))                 # 齿顶处的渐开线展角
    sa = 2 * ra * (psi_b - theta_a)                   # 齿顶厚
    z_min = 2 * ha_star / math.sin(alpha) ** 2        # 不根切最少齿数
    return {
        "d": d, "db": db, "da": da, "df": df, "p": p,
        "s": p / 2, "sa": sa, "z_min": z_min,
        "undercut": z < z_min, "pointed": sa <= 0.25 * m,
    }


def _polar(r, ang):
    return (r * math.cos(ang), r * math.sin(ang))


def gear_profile(m, z, alpha_deg=20.0, ha_star=1.0, c_star=0.25, flank_points=12):
    """
    齿轮端面轮廓，按首尾相接的顺序返回边的列表：
      ("line", [p0, p1]) / ("arc", [p0, pmid, p1]) / ("spline", [p0, ..., pn])
    点坐标为 (x, y)，单位 mm，齿轮中心在原点。
    """
    dim = gear_dimensions(m, z, alpha_deg, ha_star, c_star)
    alpha = math.radians(alpha_deg)
    ra, rb, rf = dim["da"] / 2, dim["db"] / 2, dim["df"] / 2
    psi_b = math.pi / (2 * z) + inv(alpha)
    r_start = max(rb, rf)                     # 渐开线起点（齿根圆大于基圆时从齿根圆开始）
    pitch = 2 * math.pi / z

    def theta(r):
        return inv(math.acos(min(1.0, rb / r)))

    radii = [r_start + (ra - r_start) * i / (flank_points - 1) for i in range(flank_points)]
    edges = []
    for k in range(z):
        c = k * pitch                               # 第 k 个齿的中心线
        right = [_polar(r, c - psi_b + theta(r)) for r in radii]            # 由内向外
        left = [_polar(r, c + psi_b - theta(r)) for r in reversed(radii)]   # 由外向内
        # 齿根到渐开线起点的径向线（齿根圆小于基圆时）
        if rf < r_start:
            edges.append(("line", [_polar(rf, c - psi_b + theta(r_start)), right[0]]))
        edges.append(("spline", right))
        a0, a1 = c - psi_b + theta(ra), c + psi_b - theta(ra)
        edges.append(("arc", [right[-1], _polar(ra, (a0 + a1) / 2), left[0]]))
        edges.append(("spline", left))
        b0 = c + psi_b - theta(r_start)            # 本齿左侧齿根点的角度
        b1 = c + pitch - psi_b + theta(r_start)    # 下一个齿右侧齿根点的角度
        if rf < r_start:
            foot = _polar(rf, b0)
            edges.append(("line", [left[-1], foot]))
        else:
            foot = left[-1]
        # 齿根圆弧，连到下一个齿
        edges.append(("arc", [foot, _polar(rf, (b0 + b1) / 2), _polar(rf, b1)]))
    return edges


# ---------------------------------------------------------------- FreeCAD 建模
def build(params=PARAMS):
    import FreeCAD as App
    import Part

    dim = gear_dimensions(params["m"], params["z"], params["alpha_deg"],
                          params["ha_star"], params["c_star"])
    edges = []
    for kind, pts in gear_profile(params["m"], params["z"], params["alpha_deg"],
                                  params["ha_star"], params["c_star"], params["flank_points"]):
        vs = [App.Vector(x, y, 0) for x, y in pts]
        if kind == "line":
            edges.append(Part.LineSegment(vs[0], vs[1]).toShape())
        elif kind == "arc":
            edges.append(Part.Arc(vs[0], vs[1], vs[2]).toShape())
        else:
            curve = Part.BSplineCurve()
            curve.interpolate(vs)
            edges.append(curve.toShape())
    wire = Part.Wire(edges)
    solid = Part.Face(wire).extrude(App.Vector(0, 0, params["b"]))
    if params["bore"] > 0:
        hole = Part.makeCylinder(params["bore"] / 2, params["b"] + 2, App.Vector(0, 0, -1))
        solid = solid.cut(hole)

    doc = App.ActiveDocument or App.newDocument("WQ_Gear")
    name = "Gear_m{}_z{}".format(params["m"], params["z"]).replace(".", "_")
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = solid
    doc.recompute()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    base = os.path.join(OUTPUT_DIR, name)
    solid.exportStep(base + ".step")
    solid.exportStl(base + ".stl")

    lines = [
        "齿轮 m={m} z={z} α={alpha_deg}°".format(**params),
        "  分度圆 d  = {:.3f} mm".format(dim["d"]),
        "  基圆   db = {:.3f} mm".format(dim["db"]),
        "  齿顶圆 da = {:.3f} mm".format(dim["da"]),
        "  齿根圆 df = {:.3f} mm".format(dim["df"]),
        "  齿顶厚 sa = {:.3f} mm".format(dim["sa"]),
        "  体积     = {:.1f} mm³".format(solid.Volume),
        "  已导出：{}.step / .stl".format(base),
    ]
    if dim["undercut"]:
        lines.append("  注意：z < {:.1f}，标准齿轮会根切，需要正变位（本宏未建模根切）".format(dim["z_min"]))
    if dim["pointed"]:
        lines.append("  注意：齿顶厚小于 0.25m，齿顶偏尖")
    App.Console.PrintMessage("\n".join(lines) + "\n")

    if App.GuiUp:
        import FreeCADGui as Gui
        Gui.activeDocument().activeView().viewIsometric()
        Gui.SendMsgToActiveView("ViewFit")
    return obj


if __name__ == "__main__":
    build()
