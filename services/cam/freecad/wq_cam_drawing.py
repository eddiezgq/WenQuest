# -*- coding: utf-8 -*-
"""问渠凸轮 · 零件工作图（第 39 轮第 5 步 5d）：A3 横幅 SVG，两个视图（FreeCAD TechDraw 投影的可见轮廓）、
主要参数表、盘形凸轮的廓线坐标表、标题栏。技术要求留空，由工程师填写——软件不编公差、粗糙度和热处理。

视图用 TechDraw 投影真实实体，所以图上的槽、筋就是实体上的；参数表里的数直接取自项目和 camkit。
"""
import datetime as dt
import math
import re
from xml.sax.saxutils import escape

W, H = 420.0, 297.0  # A3 横幅，单位 mm
SCALES = (1, 2, 2.5, 4, 5, 10, 20)  # 缩小比例 1:k（GB/T 14690 优先系列里的）
THIN = 'fill="none" stroke="#000" stroke-width="0.2"'
NUM = re.compile(r"-?\d+(?:\.\d+)?(?:[eE]-?\d+)?")


def _bbox(svg):
    xs, ys = [], []
    for d in re.findall(r'd="([^"]+)"', svg):
        v = [float(x) for x in NUM.findall(d)]
        xs += v[0::2]
        ys += v[1::2]
    if not xs:
        return 0, 0, 1, 1
    return min(xs), min(ys), max(xs), max(ys)


def _views(TechDraw, Vector, shape, dirs):
    """每个方向：可见线的 SVG 片段和外框（投影平面坐标，y 向下要翻）。"""
    out = []
    for d in dirs:
        vis = TechDraw.projectToSVG(shape, Vector(*d))
        out.append({"svg": vis, "box": _bbox(vis), "dir": d})
    return out


def _place(view, x, y, w, h, k):
    """把一个视图按 1:k 放进 (x, y, w, h) 的框正中。TechDraw 的片段自带 scale(1,-1)。"""
    x0, y0, x1, y1 = view["box"]
    s = 1.0 / k
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # 片段内 y 被翻转：屏幕坐标 = (px − cx)·s + 框中心，(−py + cy)·s + 框中心
    body = re.sub(r'stroke-width="[^"]*"', 'stroke-width="{:.3f}"'.format(0.35 / s), view["svg"])
    return ('<g transform="translate({:.3f},{:.3f}) scale({:.5f}) translate({:.3f},{:.3f})">{}</g>'
            .format(x + w / 2, y + h / 2, s, -cx, cy, body))


def _scale_for(views, w, h):
    need = 1.0
    for v in views:
        x0, y0, x1, y1 = v["box"]
        need = max(need, (x1 - x0) / w, (y1 - y0) / h)
    return next((k for k in SCALES if k >= need), SCALES[-1])


def _table(x, y, rows, col=(52, 48), title=None, fs=3.0):
    out, ty = [], y
    if title:
        out.append('<text x="{:.1f}" y="{:.1f}" font-size="{:.1f}" font-weight="bold">{}</text>'
                   .format(x, ty + 4, fs + 0.5, escape(title)))
        ty += 6
    for k, v in rows:
        out.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="5.5" {}/>'.format(x, ty, col[0] + col[1], THIN))
        out.append('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" stroke="#000" stroke-width="0.2"/>'
                   .format(x + col[0], ty, x + col[0], ty + 5.5))
        out.append('<text x="{:.1f}" y="{:.1f}" font-size="{:.1f}">{}</text>'.format(x + 1.2, ty + 4, fs, escape(k)))
        out.append('<text x="{:.1f}" y="{:.1f}" font-size="{:.1f}">{}</text>'.format(x + col[0] + 1.2, ty + 4, fs,
                                                                                    escape(str(v))))
        ty += 5.5
    return "\n".join(out), ty


def sheet(TechDraw, Vector, shape, part_title, params, extra_tables=(), dirs=((0, 0, 1), (0, -1, 0)), item="",
          project_title=""):
    """A3 工作图 SVG（字符串）。params: [(名称, 数值)]；extra_tables: [(标题, [(名称, 数值)])]。"""
    views = _views(TechDraw, Vector, shape, dirs)
    vw, vh = 140.0, 190.0
    k = _scale_for(views, vw - 10, vh - 10)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="{0}mm" height="{1}mm" viewBox="0 0 {0} {1}" '
           'font-family="Noto Sans SC, Microsoft YaHei, sans-serif">'.format(W, H),
           '<rect width="{}" height="{}" fill="#fff"/>'.format(W, H),
           '<rect x="10" y="10" width="{}" height="{}" fill="none" stroke="#000" stroke-width="0.7"/>'
           .format(W - 20, H - 20)]
    for i, v in enumerate(views):
        x, y = 15 + i * (vw + 5), 15
        out.append(_place(v, x, y, vw, vh, k))
        names = {(0, 0, 1): "沿凸轮轴看", (0, -1, 0): "侧视", (1, 0, 0): "侧视"}
        out.append('<text x="{:.1f}" y="{:.1f}" font-size="3.5">{}</text>'
                   .format(x, y + vh + 6, names.get(tuple(v["dir"]), "")))
    # 右栏：参数表、附加表
    tx, ty = 15 + 2 * (vw + 5), 15  # 右栏宽 100：到 405，框在 410
    body, ty = _table(tx, ty, params, title="主要参数")
    out.append(body)
    for t, rows in extra_tables:
        body, ty = _table(tx, ty + 4, rows, title=t, col=(30, 70), fs=2.6)
        out.append(body)
    # 技术要求（留空）
    out.append('<text x="15" y="{:.1f}" font-size="3.5" font-weight="bold">技术要求（由工程师填写）</text>'
               .format(H - 52))
    for j in range(3):
        out.append('<line x1="15" y1="{0:.1f}" x2="220" y2="{0:.1f}" {1} stroke-dasharray="1 1"/>'
                   .format(H - 44 + j * 8, THIN))
    out.append('<text x="15" y="{:.1f}" font-size="2.6" fill="#444">{}</text>'.format(
        H - 16, "尺寸单位 mm。实体由问渠凸轮按项目参数生成（确定性计算，未经 AI）；"
                "公差、粗糙度、热处理等请按企业规范填写。"))
    # 标题栏
    bx, by, bw, bh = W - 190, H - 42, 180, 32
    out.append('<rect x="{}" y="{}" width="{}" height="{}" fill="none" stroke="#000" stroke-width="0.5"/>'
               .format(bx, by, bw, bh))
    cells = [("名称", part_title), ("比例", "1:{:g}".format(k) if k != 1 else "1:1"), ("物料", item or "（未填）"),
             ("日期", dt.date.today().isoformat()), ("项目", project_title[:28]), ("来源", "问渠凸轮 · FreeCAD")]
    for i, (a, b) in enumerate(cells):
        cx, cy = bx + (i % 2) * bw / 2, by + (i // 2) * bh / 3
        out.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" {}/>'
                   .format(cx, cy, bw / 2, bh / 3, THIN))
        out.append('<text x="{:.1f}" y="{:.1f}" font-size="3">{}：{}</text>'
                   .format(cx + 2, cy + 6.8, escape(a), escape(str(b))))
    out.append("</svg>")
    return "\n".join(out), k


# ------------------------------------------------------------------------------- 各零件的参数表（数取自项目和 camkit）


def _f(v, nd=3):
    return "—" if v is None else ("{:." + str(nd) + "f}").format(v).rstrip("0").rstrip(".")


def globoid_rows(c):
    from camkit import globoidal as G
    g = G.globoid(c.get("globoidal"))
    th = G.thickness(g)
    rows = [("中心距 C", _f(g.C)), ("转塔滚子数 n", g.n), ("滚子中心圆半径 Rp", _f(g.Rp)), ("滚子半径 r_r", _f(g.rr)),
            ("滚子接触长 b", _f(g.b)), ("凸轮长 L", _f(g.L)), ("槽底间隙", _f(g.clearance)),
            ("相位 φ0", _f(math.degrees(g.phase), 2) + "°"), ("旋向", "右" if g.hand == 1 else "左"),
            ("筋厚（滚子内端 / 中心圆）", "{} / {}".format(_f(th["root"]), _f(th["pitch"]))),
            ("槽底处芯部半径", _f(g.core)), ("工作面", "包络方程精确曲面 ≤0.25µm")]
    return rows


def program_rows(c):
    p = c.get("program") or {}
    unit = "°" if p.get("unit") == "rad" else " mm"
    kinds = {"rise": "升", "dwell": "停", "return": "回"}
    laws = {"mod_sine": "修正正弦", "cycloidal": "摆线", "poly345": "3-4-5 多项式", "poly4567": "4-5-6-7 多项式",
            "mod_trapezoid": "修正梯形"}
    rows = []
    for i, s in enumerate(p.get("segments") or []):
        hv = s.get("h_deg") if s.get("h_deg") not in (None, "") else s.get("h")
        h = "" if s.get("kind") == "dwell" else "  {}{}".format(_f(hv), unit)
        rows.append(("{}. {} {}°".format(i + 1, kinds.get(s.get("kind"), s.get("kind")), _f(s.get("deg"), 2)),
                     (laws.get(s.get("law"), s.get("law") or "") + h).strip() or "—"))
    return rows


def disk_rows(sub):
    m = sub.get("mechanism") or {}
    names = {"rb": "基圆半径 r_b", "rr": "滚子半径 r_r", "e": "偏距 e", "a": "中心距 a", "L": "摆杆长 L",
             "width": "厚度 / 槽宽方向接触宽", "sigma": "转向"}
    rows = [("从动件", {"translating": "直动", "oscillating": "摆动"}.get(m.get("follower"), m.get("follower"))),
            ("接触", {"roller": "滚子", "flat": "平底", "knife": "尖顶"}.get(m.get("contact"), m.get("contact"))),
            ("形式", "槽凸轮" if m.get("groove") else "盘形外廓")]
    rows += [(names[k], _f(m.get(k))) for k in ("rb", "rr", "e", "a", "L", "width") if m.get(k) not in (None, "")]
    blank = ((sub.get("mfg") or {}).get("blank")) or {}
    if blank:
        rows += [("毛坯半径", _f(blank.get("radius"))), ("板厚", _f(blank.get("plate")))]
    return rows


def disk_coords(sub, step_deg=10.0):
    """廓线坐标表（凸轮坐标系，每 step_deg 一点）：转角、升程、廓线 x、y（槽凸轮另列外侧壁）。"""
    from camkit import mfg as MF
    text = MF.point_table(sub, step_deg)
    lines = text.strip().splitlines()
    head = lines[0].split(",")
    rows = []
    for ln in lines[1:]:
        v = dict(zip(head, (float(x) for x in ln.split(",")), strict=True))
        val = "x {} y {}".format(_f(v["profile_x"]), _f(v["profile_y"]))
        if "outer_x" in v:
            val += " | 外 x {} y {}".format(_f(v["outer_x"]), _f(v["outer_y"]))
        rows.append(("{}°".format(_f(v["cam_deg"], 1)), val))
    return rows


def arm_rows(arm):
    names = {"R_tip": "刀爪中心半径", "R_hub": "轮毂半径", "bore": "轴孔半径", "w_root": "臂根宽", "w_tip": "臂端宽",
             "R_grip": "刀爪外半径", "r_fork": "叉口半径", "thickness": "厚度", "fillet": "倒圆半径"}
    return [(names[k], _f(arm.get(k))) for k in names if arm.get(k) not in (None, "")]
