# -*- coding: utf-8 -*-
"""二维图 SVG（R3，接口约定 2.4；第 5 轮第 6 步）：白底黑线，右下角中英文标题栏，系统字体。

    A 标准件：主视图（轴承、密封、带轮、联轴器剖开，剖面画剖面线）+ 俯视图或侧视图；两个视图都标总体尺寸，
              主要尺寸列在标题栏上方的表里。不画虚线（不可见轮廓）。
    B 机器人：关节示意图——零位侧视（或正视），连杆画线段，转动关节画圆、移动关节画方框，编号 J1…Jn，标基座坐标系。
    C 机构：  机构运动简图——默认参数、输入起始位置，转动副、移动副、机架用标准符号，标构件名与主要尺寸。
图纸幅面 297 × 210（单位 mm，viewBox 同），比例从 1:1、1:2、2:1… 里挑最合适的。
"""
import math
from xml.sax.saxutils import escape

W, H = 297.0, 210.0
TB_W, TB_H = 130.0, 34.0                                   # 标题栏
FONT = "font-family=\"'PingFang SC','Microsoft YaHei','Noto Sans CJK SC','Source Han Sans SC',sans-serif\""
SCALES = [(10, 1), (5, 1), (4, 1), (2, 1), (1, 1), (1, 2), (1, 2.5), (1, 4), (1, 5), (1, 10), (1, 20), (1, 50), (1, 100)]


def pick_scale(k_fit):
    """能放下的最大系数 k_fit（图上长度 / 实际长度）→ 不超过它的最大标准比例 (文字, 系数)"""
    for a, b in SCALES:
        if a / b <= k_fit * 1.0001:
            return "{}:{}".format(fmt(a), fmt(b)), a / b
    n = math.ceil(1 / k_fit)
    return "1:{}".format(n), 1 / n


def fmt(v):
    v = float(v)
    return ("%.3f" % v).rstrip("0").rstrip(".")


class Sheet:
    def __init__(self):
        self.out = []

    def line(self, x1, y1, x2, y2, w=0.35, dash=None):
        self.out.append('<line x1="{:.2f}" y1="{:.2f}" x2="{:.2f}" y2="{:.2f}" stroke="#000" stroke-width="{}"{} stroke-linecap="round"/>'.format(
            x1, y1, x2, y2, w, ' stroke-dasharray="{}"'.format(dash) if dash else ""))

    def poly(self, pts, w=0.35, closed=False, fill="none", dash=None):
        if len(pts) < 2:
            return
        d = " ".join("{:.2f},{:.2f}".format(x, y) for x, y in pts)
        tag = "polygon" if closed else "polyline"
        self.out.append('<{} points="{}" fill="{}" stroke="#000" stroke-width="{}"{} stroke-linejoin="round"/>'.format(
            tag, d, fill, w, ' stroke-dasharray="{}"'.format(dash) if dash else ""))

    def circle(self, cx, cy, r, w=0.35, fill="none", dash=None):
        self.out.append('<circle cx="{:.2f}" cy="{:.2f}" r="{:.2f}" fill="{}" stroke="#000" stroke-width="{}"{}/>'.format(
            cx, cy, r, fill, w, ' stroke-dasharray="{}"'.format(dash) if dash else ""))

    def rect(self, x, y, w_, h_, w=0.35, fill="none"):
        self.out.append('<rect x="{:.2f}" y="{:.2f}" width="{:.2f}" height="{:.2f}" fill="{}" stroke="#000" stroke-width="{}"/>'.format(x, y, w_, h_, fill, w))

    def text(self, x, y, s, size=3.0, anchor="start", weight="normal", rot=None):
        tr = ' transform="rotate({} {:.2f} {:.2f})"'.format(rot, x, y) if rot else ""
        self.out.append('<text x="{:.2f}" y="{:.2f}" font-size="{}" text-anchor="{}" font-weight="{}" fill="#000"{}>{}</text>'.format(
            x, y, size, anchor, weight, tr, escape(str(s))))

    def arrow(self, x1, y1, x2, y2, w=0.25, head=2.2):
        self.line(x1, y1, x2, y2, w)
        a = math.atan2(y2 - y1, x2 - x1)
        for s in (-1, 1):
            self.line(x2, y2, x2 - head * math.cos(a + s * 0.35), y2 - head * math.sin(a + s * 0.35), w)

    def dim_h(self, x1, x2, y_obj, y_dim, label):
        """水平尺寸：两条尺寸界线 + 双箭头尺寸线 + 数字"""
        for x in (x1, x2):
            self.line(x, y_obj, x, y_dim + (1.5 if y_dim > y_obj else -1.5), 0.18)
        self.arrow((x1 + x2) / 2, y_dim, x1, y_dim, 0.18, 1.8)
        self.arrow((x1 + x2) / 2, y_dim, x2, y_dim, 0.18, 1.8)
        self.text((x1 + x2) / 2, y_dim - 1.0, label, 2.6, "middle")

    def dim_v(self, y1, y2, x_obj, x_dim, label):
        for y in (y1, y2):
            self.line(x_obj, y, x_dim + (1.5 if x_dim > x_obj else -1.5), y, 0.18)
        self.arrow(x_dim, (y1 + y2) / 2, x_dim, y1, 0.18, 1.8)
        self.arrow(x_dim, (y1 + y2) / 2, x_dim, y2, 0.18, 1.8)
        self.text(x_dim - 1.0, (y1 + y2) / 2, label, 2.6, "middle", rot=-90)

    def hatch_defs(self):
        return ('<defs><pattern id="hatch" patternUnits="userSpaceOnUse" width="2.2" height="2.2" patternTransform="rotate(45)">'
                '<line x1="0" y1="0" x2="0" y2="2.2" stroke="#000" stroke-width="0.18"/></pattern></defs>')

    def svg(self, title):
        body = "\n".join(self.out)
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}" {font}>\n'
                '<title>{t}</title>\n{defs}\n<rect x="0" y="0" width="{w}" height="{h}" fill="#fff"/>\n'
                '<rect x="5" y="5" width="{iw}" height="{ih}" fill="none" stroke="#000" stroke-width="0.5"/>\n{body}\n</svg>\n').format(
            w=fmt(W), h=fmt(H), font=FONT, t=escape(title), defs=self.hatch_defs(), iw=fmt(W - 10), ih=fmt(H - 10), body=body)


def title_block(sh, entry, size, scale, extra_rows=None):
    """右下角标题栏：名称（中英）、编号/规格、标准、比例、单位、来源与许可"""
    x0, y0 = W - 5 - TB_W, H - 5 - TB_H
    sh.rect(x0, y0, TB_W, TB_H, 0.5)
    for dy in (9, 17, 25):
        sh.line(x0, y0 + dy, x0 + TB_W, y0 + dy, 0.25)
    sh.line(x0 + 78, y0 + 9, x0 + 78, y0 + TB_H, 0.25)
    sh.text(x0 + 2, y0 + 4.2, entry["name"]["zh"], 3.4, weight="bold")
    sh.text(x0 + 2, y0 + 7.8, entry["name"]["en"], 2.3)
    ref = entry["id"] if str(size) in ("default", "") else "{}/{}".format(entry["id"], size)
    sh.text(x0 + 2, y0 + 14, "编号 Ref：" + ref, 2.6)
    std = "；".join(s["code"] for s in entry.get("standards") or []) or "—"
    sh.text(x0 + 2, y0 + 22, "标准 Std：" + (std if len(std) < 40 else std[:39] + "…"), 2.4)
    src = entry.get("source") or {}
    lic = "来源 Source：{}　许可 {}".format({"wenquest": "问渠自建", "bd_warehouse": "bd_warehouse", "menagerie": "MuJoCo Menagerie",
                                            "robot_descriptions": "robot_descriptions", "ros_industrial": "ROS-Industrial",
                                            "vendor": src.get("vendor") or "厂商"}.get(src.get("origin"), src.get("origin", "")),
                                           src.get("license", ""))
    sh.text(x0 + 2, y0 + 30.5, lic if len(lic) < 46 else lic[:45] + "…", 2.3)
    sh.text(x0 + 80, y0 + 14, "比例 Scale  " + scale, 2.6)
    sh.text(x0 + 80, y0 + 22, "单位 Unit  mm", 2.6)
    sh.text(x0 + 80, y0 + 30.5, "问渠零件库 WenQuest Library", 2.3)
    rows = [r for r in (extra_rows or []) if r][:12]
    if rows:                                                # 主要尺寸表（标题栏上方）
        hh = 4.2 * len(rows) + 5
        sh.rect(x0, y0 - hh - 2, TB_W, hh, 0.25)
        sh.text(x0 + 2, y0 - hh + 1.6, "主要尺寸 Main dimensions", 2.5, weight="bold")
        for i, (k, v) in enumerate(rows):
            sh.text(x0 + 2, y0 - hh + 6 + 4.2 * i, k, 2.4)
            sh.text(x0 + TB_W - 2, y0 - hh + 6 + 4.2 * i, v, 2.4, "end")


def key_rows(entry, row, limit=12):
    out = []
    for p in entry.get("params") or []:
        if p.get("role") not in ("key", "dim") or row.get(p["key"]) in (None, ""):
            continue
        out.append(("{}".format(p["zh"]), "{} {}".format(row[p["key"]], p.get("unit", "") if p.get("unit") not in (None, "mm") else "").strip()))
        if len(out) >= limit:
            break
    return out


# ---------------------------------------------------------------- A 标准件
SECTION_CATS = {"BRG", "SEL", "PUL", "CPL"}
SIDE_VIEW_CATS = {"LGD", "BSC"}
ROUND_CATS = {"BRG", "SEL", "PUL", "CPL", "SPR", "PIN", "WSH", "RNG"}       # 俯视外形是圆：尺寸前加 ⌀                             # 第二个视图用侧视（从 +X 看），其余用俯视（从 +Z 看）


def _edges_2d(edges):
    """build123d 投影后的边（视图平面坐标）→ 折线列表"""
    out = []
    for e in edges:
        try:
            gt = e.geom_type
            n = 1 if str(gt).endswith("LINE") else max(8, min(64, int(e.length / 0.5) + 2))
            out.append([((e @ (i / n)).X, (e @ (i / n)).Y) for i in range(n + 1)])
        except Exception:  # noqa: BLE001
            continue
    return out


def _bbox(polys):
    xs = [x for p in polys for x, _ in p]
    ys = [y for p in polys for _, y in p]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else (0, 0, 1, 1)


def a_drawing(entry, row, nodes):
    from build123d import Box, Compound, Pos
    shape = nodes[0][1] if len(nodes) == 1 else Compound(children=[n[1] for n in nodes])
    cat = entry.get("category", "")
    bb = shape.bounding_box()
    section = cat in SECTION_CATS
    front_src = shape
    cut_faces = []
    if section:                                             # 沿 XZ 平面剖开，留 y ≥ 0 一半，从 −Y 看
        keep = Pos(bb.center().X, (bb.max.Y + 1) / 2, bb.center().Z) * Box(bb.size.X * 2 + 10, bb.max.Y + 1, bb.size.Z * 2 + 10)
        half = shape & keep
        if half.volume > 1e-6:
            front_src = half
            for f in half.faces():
                c = f.center()
                if abs(c.Y) < 1e-3 and abs(abs(f.normal_at(c).Y) - 1) < 1e-6:
                    cut_faces.append([(p.X, p.Z) for p in _wire_pts(f.outer_wire())])
    if cat == "SPR":                                        # 弹簧主视图按规定画法：两侧簧丝截面圆 + 连线（螺旋线投影太乱）
        fpolys, cut_faces = spring_view(row), []
    else:
        front, _ = front_src.project_to_viewport((0, -100000, 0), viewport_up=(0, 0, 1), look_at=(0, 0, 0))
        fpolys = _edges_2d(front)
    if cat == "SPR":                                        # 螺旋线的俯视投影很慢：画内外两圆
        d, D = float(row["d_mm"]), float(row["D_mm"])
        spolys = [[((D / 2 + s * d / 2) * math.cos(t * math.pi / 32), (D / 2 + s * d / 2) * math.sin(t * math.pi / 32)) for t in range(65)] for s in (-1, 1)]
    elif cat in SIDE_VIEW_CATS:
        side, _ = shape.project_to_viewport((100000, 0, 0), viewport_up=(0, 0, 1), look_at=(0, 0, 0))
        spolys = _edges_2d(side)
    else:
        top, _ = shape.project_to_viewport((0, 0, 100000), viewport_up=(0, 1, 0), look_at=(0, 0, 0))
        spolys = _edges_2d(top)
    fb, sbx = _bbox(fpolys), _bbox(spolys)
    fw, fh, sw, shh = fb[2] - fb[0], fb[3] - fb[1], sbx[2] - sbx[0], sbx[3] - sbx[1]
    room_w, room_h = (W - 10 - 30) / 2 - 10, H - 10 - TB_H - 40
    label, k = pick_scale(min(room_w / max(fw, sw, 1e-6), room_h / max(fh, shh, 1e-6)))
    sh = Sheet()
    cy = 15 + room_h / 2 + 8
    fcx, scx = 15 + room_w / 2 + 6, 15 + room_w + 20 + room_w / 2

    def place(polys, b, cx):
        mx, my = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        return [[(cx + (x - mx) * k, cy - (y - my) * k) for x, y in p] for p in polys], (mx, my)
    fp, (fmx, fmy) = place(fpolys, fb, fcx)
    spp, _ = place(spolys, sbx, scx)
    for poly in cut_faces:                                  # 剖面线
        sh.poly([(fcx + (x - fmx) * k, cy - (y - fmy) * k) for x, y in poly], 0.0, True, "url(#hatch)")
    for p in fp:
        sh.poly(p, 0.35)
    for p in spp:
        sh.poly(p, 0.35)
    revolute = cat not in ("KEY", "LGD")
    if revolute:                                            # 中心线（点画线）
        ax_x = fcx + (0 - fmx) * k                          # 轴线 x = 0
        sh.line(ax_x, cy - fh * k / 2 - 4, ax_x, cy + fh * k / 2 + 4, 0.18, "6,1.5,1,1.5")
        if cat not in SIDE_VIEW_CATS:
            sh.line(scx - sw * k / 2 - 4, cy, scx + sw * k / 2 + 4, cy, 0.18, "6,1.5,1,1.5")
            sh.line(scx, cy - shh * k / 2 - 4, scx, cy + shh * k / 2 + 4, 0.18, "6,1.5,1,1.5")
    # 总体尺寸
    x1, x2, yb = fcx - fw * k / 2, fcx + fw * k / 2, cy + fh * k / 2
    sh.dim_h(x1, x2, yb + 1, yb + 8, fmt(fw))
    sh.dim_v(cy - fh * k / 2, cy + fh * k / 2, x1 - 1, x1 - 8, fmt(fh))
    sx1, sx2, syb = scx - sw * k / 2, scx + sw * k / 2, cy + shh * k / 2
    sh.dim_h(sx1, sx2, syb + 1, syb + 8, ("⌀" if cat in ROUND_CATS else "") + fmt(sw))
    sh.text(fcx, 14, "主视图" + ("（剖视）" if cut_faces else ""), 3, "middle")
    sh.text(scx, 14, "侧视图" if cat in SIDE_VIEW_CATS else "俯视图", 3, "middle")
    size = row.get("size", "default")
    title_block(sh, entry, size, label, key_rows(entry, row))
    return sh.svg("{} {}".format(entry["id"], size))


def spring_view(row):
    """圆柱螺旋压缩弹簧的规定画法（GB/T 4459.4 简化）：左右两列簧丝截面圆，相邻截面用直线相连；两端并紧磨平"""
    d, D, H0, n = (float(row[k]) for k in ("d_mm", "D_mm", "H0_mm", "n"))
    total = n + 2
    pitch = (H0 - d) / total
    circ = lambda cx, cz: [(cx + d / 2 * math.cos(t * math.pi / 12), cz + d / 2 * math.sin(t * math.pi / 12)) for t in range(25)]  # noqa: E731
    polys = []
    lefts = [(-D / 2, d / 2 + i * pitch) for i in range(int(total) + 1)]
    rights = [(D / 2, d / 2 + (i + 0.5) * pitch) for i in range(int(total))]
    for c in lefts + rights:
        polys.append(circ(*c))
    for i in range(len(rights)):                            # 前面一侧的簧丝（左下 → 右上）
        a, b = lefts[i], rights[i]
        polys.append([(a[0] + d / 2, a[1] - d / 2), (b[0] - d / 2, b[1] - d / 2)])
        polys.append([(a[0] + d / 2, a[1] + d / 2), (b[0] - d / 2, b[1] + d / 2)])
    polys.append([(-D / 2 - d / 2, 0), (D / 2 + d / 2, 0)])          # 两端磨平面
    polys.append([(-D / 2 - d / 2, H0), (D / 2 + d / 2, H0)])
    return polys


def _wire_pts(w, n=48):
    pts = []
    for e in w.edges():
        m = 1 if str(e.geom_type).endswith("LINE") else n
        pts += [e @ (i / m) for i in range(m)]
    return pts


# ---------------------------------------------------------------- B 机器人：关节示意图
def _quat_M(q, pos):
    import numpy as np
    w, x, y, z = q
    M = np.eye(4)
    M[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                 [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                 [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    M[:3, 3] = pos
    return M


def b_diagram(entry, robot, bodies):
    import numpy as np
    bmap = {b["name"]: b for b in bodies}
    T = {}

    def world(n):
        if n not in T:
            b = bmap[n]
            M = _quat_M(b["quat"], b["pos"])
            T[n] = (world(b["parent"]) if b.get("parent") in bmap else np.eye(4)) @ M
        return T[n]
    joints = [j for j in robot.get("joints") or [] if j.get("type") != "fixed" and j.get("child") in bmap and "mimic" not in j]
    if not joints:
        return None
    par = robot.get("parallel") or {}
    if par.get("type") == "stewart":
        return stewart_diagram(entry, robot, par)
    jpos = {}
    for j in joints:
        anc = np.array(list(j.get("anchor") or [0, 0, 0]) + [1.0])
        jpos[j["child"]] = (world(j["child"]) @ anc)[:3]
    pts = np.array(list(jpos.values()) + [[0, 0, 0]])
    spread_x, spread_y = np.ptp(pts[:, 0]), np.ptp(pts[:, 1])
    ax = 1 if spread_y > spread_x * 1.2 else 0              # 投影平面：XZ（侧视）或 YZ（正视）
    view = "正视 Front（YZ）" if ax == 1 else "侧视 Side（XZ）"

    def proj(p):
        return p[ax], p[2]
    jlist = [(i + 1, j) for i, j in enumerate(joints)]

    def parent_point(child):
        """沿父链找最近的关节位置；找不到用根（基座原点）"""
        b = bmap[child].get("parent")
        while b:
            if b in jpos:
                return jpos[b]
            b = bmap[b].get("parent") if b in bmap else None
        return np.zeros(3)
    segs = [(proj(parent_point(j["child"])), proj(jpos[j["child"]])) for _, j in jlist]
    xs = [p[0] for s in segs for p in s] + [0]
    ys = [p[1] for s in segs for p in s] + [0]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1e-3) * 1000
    room = min(W - 10 - 80, H - 10 - 30)
    label, k = pick_scale(room / span)
    sh = Sheet()
    cx0, cy0 = 15 + (W - 10 - 80) / 2, 15 + (H - 30) / 2
    mx, my = (max(xs) + min(xs)) / 2 * 1000, (max(ys) + min(ys)) / 2 * 1000

    def to(p):
        return cx0 + (p[0] * 1000 - mx) * k, cy0 - (p[1] * 1000 - my) * k
    for a, b in segs:
        (x1, y1), (x2, y2) = to(a), to(b)
        sh.line(x1, y1, x2, y2, 0.5)
    ox, oy = to((0, 0))                                     # 基座：机架符号 + 坐标系
    sh.line(ox - 8, oy + 3, ox + 8, oy + 3, 0.5)
    for i in range(6):
        sh.line(ox - 8 + i * 3.2, oy + 3, ox - 10 + i * 3.2, oy + 6, 0.25)
    sh.arrow(ox, oy, ox + 14, oy, 0.3)
    sh.arrow(ox, oy, ox, oy - 14, 0.3)
    sh.text(ox + 15, oy + 1, "Y" if ax == 1 else "X", 2.8)
    sh.text(ox + 1, oy - 15, "Z", 2.8)
    r = 2.0 if len(jlist) <= 12 else 1.4
    for n, j in jlist:
        x, y = to(proj(jpos[j["child"]]))
        if j["type"] == "prismatic":
            sh.rect(x - r, y - r, 2 * r, 2 * r, 0.35, "#fff")
        else:
            sh.circle(x, y, r, 0.35, "#fff")
        sh.text(x + r + 0.6, y - r - 0.3, "J{}".format(n), 2.2 if len(jlist) <= 12 else 1.8)
    # 右侧：关节对照表
    tx, ty = W - 5 - 78, 12
    sh.text(tx, ty, "关节 Joints（{}）".format(view), 2.8, weight="bold")
    rows = jlist[:min(len(jlist), 34)]
    for i, (n, j) in enumerate(rows):
        t = {"revolute": "转动", "continuous": "转动∞", "prismatic": "移动"}.get(j["type"], j["type"])
        nm = j["name"] if len(j["name"]) <= 26 else j["name"][:25] + "…"
        sh.text(tx, ty + 5 + i * 3.6, "J{}  {}  {}".format(n, t, nm), 2.2)
    if len(jlist) > len(rows):
        sh.text(tx, ty + 5 + len(rows) * 3.6, "… 共 {} 个关节，全表见“关节”页".format(len(jlist)), 2.2)
    sh.text(15, H - 10, "关节示意图（零位）：连杆画线段，○ 转动关节，□ 移动关节；不画外形", 2.6)
    title_block(sh, entry, "default", label)
    return sh.svg("{} 关节示意图".format(entry["id"]))


def stewart_diagram(entry, robot, par):
    """Stewart 平台：原位正视，六条腿从基座铰点画到平台铰点（中间画移动副方框），基座、平台画成多边形"""
    B = par["anchors"]["base"]
    Pp = par["anchors"]["platform"]
    h = par["params"]["home_height_m"]
    Pw = [(p[0], p[1], h) for p in Pp]
    allx = [p[0] for p in B + Pw]
    allz = [0, h]
    span = max(max(allx) - min(allx), h * 1.3) * 1000
    room = min(W - 10 - 80, H - 10 - 40)
    label, k = pick_scale(room / span)
    sh = Sheet()
    cx0, cy0 = 15 + (W - 10 - 80) / 2, 15 + (H - 30) / 2

    def to(x, z):
        return cx0 + x * 1000 * k, cy0 - (z - h / 2) * 1000 * k
    xb = sorted(p[0] for p in B)
    xp = sorted(p[0] for p in Pw)
    (a, ya), (b, _) = to(xb[0], 0), to(xb[-1], 0)
    sh.line(a - 4, ya, b + 4, ya, 0.7)
    for i in range(int((b - a + 8) / 3)):
        sh.line(a - 4 + i * 3, ya, a - 6 + i * 3, ya + 2.5, 0.2)
    (a, yp), (b, _) = to(xp[0], h), to(xp[-1], h)
    sh.line(a - 4, yp, b + 4, yp, 0.7)
    for i, (bp, pp) in enumerate(zip(B, Pw), start=1):
        (x1, y1), (x2, y2) = to(bp[0], 0), to(pp[0], h)
        sh.line(x1, y1, x2, y2, 0.45)
        sh.circle(x1, y1, 1.2, 0.35, "#fff"), sh.circle(x2, y2, 1.2, 0.35, "#fff")
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        sh.rect(mx - 1.8, my - 1.8, 3.6, 3.6, 0.35, "#fff")
        sh.text(mx + 2.4, my - 2.2 + (i % 2) * 4.5, "J{}".format(i), 2.2)
    sh.text(cx0, yp - 5, "动平台 Platform", 2.8, "middle")
    sh.text(cx0, ya + 7, "基座 Base", 2.8, "middle")
    tx, ty = W - 5 - 78, 12
    sh.text(tx, ty, "关节 Joints（正视，原位）", 2.8, weight="bold")
    L = par["leg_length_m"]
    for i in range(6):
        sh.text(tx, ty + 5 + i * 3.6, "J{}  移动（腿长）  原位 {} mm".format(i + 1, fmt(L["home"][i] * 1000)), 2.2)
    sh.text(tx, ty + 5 + 6 * 3.6 + 2, "腿长范围 {}～{} mm".format(fmt(L["min"] * 1000), fmt(L["max"] * 1000)), 2.2)
    sh.text(15, H - 10, "关节示意图：○ 球铰/虎克铰，□ 移动副（伸缩腿）；六条腿按投影画在同一平面，有重叠", 2.6)
    title_block(sh, entry, "default", label, [("基座铰点圆半径", fmt(par["params"]["base_radius_m"] * 1000)),
                                              ("平台铰点圆半径", fmt(par["params"]["platform_radius_m"] * 1000)),
                                              ("原位高度", fmt(h * 1000))])
    return sh.svg("{} 关节示意图".format(entry["id"]))


# ---------------------------------------------------------------- C 机构：机构运动简图
def c_diagram(entry, p, mech):
    from generators import c_mech as cm
    kind = entry["model"]["engine"].split(":")[1]
    sh = Sheet()
    prims = []                                              # (类型, 数据) 以米为单位，平面坐标 (x, z)

    def ground(x, z):
        prims.append(("ground", (x, z)))

    def pin(x, z):
        prims.append(("pin", (x, z)))

    def link(a, b):
        prims.append(("link", (a, b)))

    def label(x, z, s):
        prims.append(("label", (x, z, s)))
    dims = []
    if kind == "four_bar":
        A, B, th3, th4 = cm.four_bar_solve(p, math.radians(30))
        d = p["ground_m"]
        ground(0, 0), ground(d, 0)
        link((0, 0), tuple(A)), link(tuple(A), tuple(B)), link((d, 0), tuple(B))
        for q in ((0, 0), tuple(A), tuple(B), (d, 0)):
            pin(*q)
        label(A[0] / 2 - 0.006, A[1] / 2 + 0.004, "曲柄 a"), label((A[0] + B[0]) / 2, (A[1] + B[1]) / 2 + 0.006, "连杆 b")
        label((B[0] + d) / 2 + 0.006, B[1] / 2, "摇杆 c"), label(d / 2, -0.012, "机架 d")
        dims = [("a 曲柄", p["crank_m"]), ("b 连杆", p["coupler_m"]), ("c 摇杆", p["rocker_m"]), ("d 机架", d)]
    elif kind == "slider_crank":
        th = math.radians(40)
        x = cm.slider_crank_x(p, th)
        A = (p["crank_m"] * math.cos(th), p["crank_m"] * math.sin(th))
        e = p["offset_m"]
        ground(0, 0)
        link((0, 0), A), link(A, (x, e))
        pin(0, 0), pin(*A), pin(x, e)
        prims.append(("slider", (x, e)))
        prims.append(("guide", (x - 0.06, x + 0.06, e)))
        label(A[0] / 2 - 0.008, A[1] / 2 + 0.004, "曲柄 r"), label((A[0] + x) / 2, (A[1] + e) / 2 + 0.008, "连杆 l"), label(x, e - 0.016, "滑块")
        dims = [("r 曲柄", p["crank_m"]), ("l 连杆", p["rod_m"]), ("e 偏距", e)]
    elif kind == "cam":
        pitch, prof = cm.cam_profile(p, 360)
        prims.append(("curve", prof + [prof[0]]))
        ground(0, 0), pin(0, 0)
        r0, rr = p["base_radius_m"], p["roller_radius_m"]
        prims.append(("circle", (0, r0 + rr, rr)))
        link((0, r0 + rr), (0, r0 + rr + 0.06))
        prims.append(("guide_v", (0, r0 + rr + 0.02, r0 + rr + 0.06)))
        prims.append(("circle_dash", (0, 0, r0)))
        label(0.012, r0 + rr + 0.05, "从动件"), label(-r0 * 0.6, -r0 * 0.3, "凸轮")
        dims = [("r0 基圆半径", r0), ("rr 滚子半径", rr), ("h 行程", p["lift_m"])]
    elif kind == "gear_train":
        L = cm.gear_train_layout(p)
        x1, x2, x3 = L["x"]
        rp = [p["module1_mm"] * p["z1"] / 2000, p["module1_mm"] * p["z2"] / 2000, p["module2_mm"] * p["z3"] / 2000, p["module2_mm"] * p["z4"] / 2000]
        for (x, r, nm) in [(x1, rp[0], "z1"), (x2, rp[1], "z2"), (x2, rp[2], "z3"), (x3, rp[3], "z4")]:
            prims.append(("circle_dash", (x, 0, r)))
            label(x + r * 0.7, r * 0.75, "{} = {}".format(nm, int(p[nm])))
        for x in (x1, x2, x3):
            ground(x, 0), pin(x, 0)
        names = entry.get("mechanism_names") or {}
        label(x1, -rp[0] - 0.012, names.get("shaft1", "输入轴 I")[:12]), label(x3, -rp[3] - 0.012, names.get("shaft3", "输出轴 III")[:12])
        dims = [("a1 中心距", L["a1_m"]), ("a2 中心距", L["a2_m"]), ("i 总传动比", None, fmt(L["i"]))]
    elif kind == "worm":
        a = mech["analysis"]["center_distance_m"]
        r2 = p["module_mm"] * p["wheel_teeth"] / 2000
        d1 = p["module_mm"] * p["diameter_factor"] / 1000
        prims.append(("circle_dash", (0, 0, r2)))
        prims.append(("rectc", (0, a, 0.08, d1)))
        link((-0.07, a), (0.07, a))
        ground(0, 0), pin(0, 0)
        label(r2 * 0.6, -r2 * 0.6, "蜗轮 z2 = {}".format(int(p["wheel_teeth"]))), label(0.045, a + d1, "蜗杆 z1 = {}".format(int(p["worm_starts"])))
        dims = [("a 中心距", a), ("m 模数", None, fmt(p["module_mm"]) + " mm"), ("q 直径系数", None, fmt(p["diameter_factor"]))]
    elif kind == "belt":
        path = cm.belt_path(p, 120)
        prims.append(("curve", path + [path[0]]))
        prims.append(("circle", (0, 0, p["d1_m"] / 2))), prims.append(("circle", (p["center_m"], 0, p["d2_m"] / 2)))
        ground(0, 0), ground(p["center_m"], 0), pin(0, 0), pin(p["center_m"], 0)
        label(0, p["d1_m"] / 2 + 0.012, "主动轮 D1"), label(p["center_m"], p["d2_m"] / 2 + 0.012, "从动轮 D2")
        dims = [("D1", p["d1_m"]), ("D2", p["d2_m"]), ("a 中心距", p["center_m"]), ("L 带长", mech["analysis"]["belt_length_m"])]
    elif kind == "ratchet":
        z, R = int(p["teeth"]), p["wheel_radius_m"]
        h = 0.18 * R
        pts = []
        for k in range(z):
            a0 = 2 * math.pi * k / z
            pts += [(R * math.cos(a0), R * math.sin(a0)), ((R - h) * math.cos(a0 + 0.02), (R - h) * math.sin(a0 + 0.02))]
        prims.append(("curve", pts + [pts[0]]))
        ground(0, 0), pin(0, 0)
        link((0, 0), (R * 1.6, 0)), link((R * 1.05, 0.0), (R * 0.98, R * 0.25))
        link((-R * 1.25, 0.03), (-R * 0.98, R * 0.08))
        ground(-R * 1.25, 0.03), pin(-R * 1.25, 0.03)
        label(R * 1.2, 0.012, "摇杆 + 驱动棘爪"), label(-R * 1.6, 0.05, "止回棘爪"), label(0, -R - 0.012, "棘轮 z = {}".format(z))
        dims = [("R 棘轮半径", R), ("摆角", None, fmt(p["swing_deg"]) + "°")]
    elif kind == "geneva":
        n, R = int(p["slots"]), p["crank_m"]
        C = R / math.sin(math.pi / n)
        Rw = math.sqrt(C * C - R * R) * 1.08
        prims.append(("circle", (-C, 0, Rw)))
        for k in range(n):
            a = 2 * math.pi * k / n + math.pi / n
            link((-C + (Rw - (R + Rw - C) - 0.004) * math.cos(a), (Rw - (R + Rw - C) - 0.004) * math.sin(a)), (-C + Rw * math.cos(a), Rw * math.sin(a)))
        th = math.radians(180 - (90 - 180 / n))
        link((0, 0), (R * math.cos(th), R * math.sin(th)))
        prims.append(("circle", (R * math.cos(th), R * math.sin(th), 0.12 * R)))
        ground(0, 0), ground(-C, 0), pin(0, 0), pin(-C, 0)
        label(0.01, -0.015, "拨盘 R"), label(-C, -Rw - 0.012, "槽轮 n = {}".format(n))
        dims = [("R 拨销半径", R), ("C 中心距", C), ("n 槽数", None, str(n))]
    elif kind == "lead_screw":
        Ls, d = p["screw_length_m"], p["diameter_mm"] / 1000
        prims.append(("rectc", (0, 0, Ls, d)))
        k = 0
        x = -Ls / 2
        while x < Ls / 2 - 0.004:                         # 螺纹示意：细斜线
            link((x, -d / 2), (x + 0.004, d / 2))
            x += 0.008
            k += 1
        prims.append(("rectc", (0, 0, p["nut_length_m"], d * 2.2)))
        ground(-Ls / 2 - 0.01, 0), ground(Ls / 2 + 0.01, 0)
        label(0, d * 1.5 + 0.004, "螺母（移动）"), label(-Ls / 2 + 0.02, -d - 0.008, "丝杠（转动）")
        dims = [("d 公称直径", d), ("Ph 导程", p["lead_mm"] / 1000), ("丝杠长", Ls)]
    else:
        return None
    # 尺度与布置
    xs, zs = [], []
    for t, dat in prims:
        if t in ("ground", "pin"):
            xs.append(dat[0]), zs.append(dat[1])
        elif t == "link":
            for q in dat:
                xs.append(q[0]), zs.append(q[1])
        elif t == "curve":
            xs += [q[0] for q in dat]
            zs += [q[1] for q in dat]
        elif t in ("circle", "circle_dash"):
            xs += [dat[0] - dat[2], dat[0] + dat[2]]
            zs += [dat[1] - dat[2], dat[1] + dat[2]]
        elif t == "rectc":
            xs += [dat[0] - dat[2] / 2, dat[0] + dat[2] / 2]
            zs += [dat[1] - dat[3] / 2, dat[1] + dat[3] / 2]
    xs = [v for v in xs if isinstance(v, (int, float))]
    zs = [v for v in zs if isinstance(v, (int, float))]
    span = max(max(xs) - min(xs), (max(zs) - min(zs)) * 1.4, 1e-3) * 1000
    room = min(W - 10 - 40, (H - 10 - TB_H - 30) * 1.4)
    lab, k = pick_scale(room / span)
    cx0, cy0 = 20 + (W - 40) / 2 - 10, 15 + (H - TB_H - 30) / 2
    mx, mz = (max(xs) + min(xs)) / 2 * 1000, (max(zs) + min(zs)) / 2 * 1000

    def to(x, z):
        return cx0 + (x * 1000 - mx) * k, cy0 - (z * 1000 - mz) * k
    for t, dat in prims:
        if t == "link":
            (x1, y1), (x2, y2) = to(*dat[0]), to(*dat[1])
            sh.line(x1, y1, x2, y2, 0.5)
        elif t == "curve":
            sh.poly([to(*q) for q in dat], 0.4)
        elif t == "circle":
            x, y = to(dat[0], dat[1])
            sh.circle(x, y, dat[2] * 1000 * k, 0.4)
        elif t == "circle_dash":
            x, y = to(dat[0], dat[1])
            sh.circle(x, y, dat[2] * 1000 * k, 0.3, dash="6,1.5,1,1.5")
        elif t == "rectc":
            x, y = to(dat[0], dat[1])
            w_, h_ = dat[2] * 1000 * k, dat[3] * 1000 * k
            sh.rect(x - w_ / 2, y - h_ / 2, w_, h_, 0.4)
        elif t == "slider":
            x, y = to(*dat)
            sh.rect(x - 4, y - 2.5, 8, 5, 0.45, "#fff")
        elif t in ("guide", "guide_v"):
            if t == "guide":
                (x1, y1), (x2, _) = to(dat[0], dat[2]), to(dat[1], dat[2])
                for yy in (y1 + 3, y1 - 3):
                    sh.line(x1, yy, x2, yy, 0.4)
                    for i in range(int((x2 - x1) / 3)):
                        sh.line(x1 + i * 3, yy + (1.6 if yy > y1 else -1.6), x1 + i * 3 + 1.6, yy, 0.2)
            else:
                (x1, y1), (_, y2) = to(dat[0], dat[1]), to(dat[0], dat[2])
                for xx in (x1 - 3, x1 + 3):
                    sh.line(xx, y1, xx, y2, 0.4)
    for t, dat in prims:                                    # 机架、转动副画在最上层
        if t == "ground":
            x, y = to(*dat)
            sh.poly([(x, y), (x - 3.5, y + 5), (x + 3.5, y + 5)], 0.35, True, "#fff")
            sh.line(x - 5.5, y + 5, x + 5.5, y + 5, 0.4)
            for i in range(5):
                sh.line(x - 5 + i * 2.5, y + 5, x - 6.6 + i * 2.5, y + 7, 0.2)
        elif t == "pin":
            x, y = to(*dat)
            sh.circle(x, y, 1.4, 0.4, "#fff")
        elif t == "label":
            x, y = to(dat[0], dat[1])
            sh.text(x, y, dat[2], 2.8, "middle")
    rows = []
    for item in dims:
        if len(item) == 3:
            rows.append((item[0], item[2]))
        elif item[1] is not None:
            rows.append((item[0], fmt(item[1] * 1000)))
    sh.text(15, H - 10, "机构运动简图（默认参数）：○ 转动副，□ 移动副（滑块），△ 机架；点画线为节圆或基圆", 2.6)
    title_block(sh, entry, "default", lab, rows)
    return sh.svg("{} 机构运动简图".format(entry["id"]))


def drawing(entry, row, nodes=None, part=None):
    """build.py 调用：按部分出图；出不了返回 None（不影响模型）"""
    part_letter = entry["id"][0]
    if part_letter == "A" and nodes:
        return a_drawing(entry, row, nodes)
    if part_letter == "B" and part and part.get("robot"):
        return b_diagram(entry, part["robot"], part["bodies"])
    if part_letter == "C" and part and part.get("mechanism"):
        from generators import c_mech as cm
        return c_diagram(entry, cm.params_of(entry, row), part["mechanism"])
    return None
