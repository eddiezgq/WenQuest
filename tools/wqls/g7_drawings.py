"""第 138 轮 G7.1：WQ-LS 自制件的零件图（机壳以外的 6 种）。由三维模型投影（数字工厂 drawings/sheet.py，国标图框），
尺寸取自三维，公差、粗糙度、几何公差和技术要求按下面 SPEC 定（每条写了依据）。

    python3 tools/wqls/g7_drawings.py <整机零件 STEP 目录（cad/mech.py 带 WQ_OPT=T,E 的输出）> [输出目录]
    → 默认 docs/设计/WQ-LS/G7/工程图/<物料号>.pdf / .png / .svg

图：LS-101 上轴、LS-102 下轴、LS-201 针杆、LS-401 送布偏心、LS-402 抬牙偏心、LS-710 剪线凸轮。
三维模型是功能尺寸模型：轴上的紧定螺钉平面、针杆的针夹孔等细节没有建模，图上用技术要求说明，不画假的。
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIG = ROOT / "factory" / "digital"
sys.path[:0] = [str(DIG)]
import build123d as bd  # noqa: E402
from drawings.sheet import Sheet  # noqa: E402

DATE = "2026-11-13"
ZU, LOW = 200.0, (27.791774943072237, -35.36485983577417)


def load(p):
    so = bd.import_step(str(p)).solids()
    s = so[0]
    for x in so[1:]:
        s = s + x
    return s


def save(sh: Sheet, out: Path, name: str):
    svg = out / f"{name}.svg"
    svg.write_text(sh.svg(), encoding="utf-8")
    subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(out / f"{name}.pdf"), str(svg)], check=True)
    subprocess.run(["rsvg-convert", "-w", "2400", "-o", str(out / f"{name}.png"), str(svg)], check=True)


def mass(code):
    j = json.loads((DIG / "web" / "public" / "wqls" / "machine.json").read_text(encoding="utf-8"))
    return next(p["mass_g"] for p in j["parts"].values() if p["code"] == code)


def steps(s, axis_yz):
    """沿 x 的阶梯轴：[(x0, x1, 直径)]（从圆柱面取）"""
    out = []
    for f in s.faces():
        if f.geom_type == bd.GeomType.CYLINDER:
            bb = f.bounding_box()
            out.append((round(bb.min.X, 2), round(bb.max.X, 2), round(2 * f.radius, 3)))
    return sorted(set(out))


# ---------------------------------------------------------------- 轴类：上轴、下轴、针杆
def shaft_sheet(s, code, title, mat, scale, scale_text, fits, ra, datums, runout, req, size="A3", notes=()):
    """s 已经放到轴线 = x 轴（y = z = 0）。fits：{直径: 标注}；ra：{直径: Ra}；datums：[(直径, 字母)]；runout：[(直径, 值, 基准)]。"""
    segs = steps(s, (0, 0))
    x0, x1 = min(a for a, _, _ in segs), max(b for _, b, _ in segs)
    sh = Sheet(size, title=title, code=code, material=mat, scale_text=scale_text, mass=f"{mass(code):g} g", qty="1",
               designer="AI（问渠）", date=DATE)
    W = sh.W
    L = (x1 - x0) * scale
    fv = sh.view([(s, 1)], "front", scale, ref3=(x0, 0, 0), at=((W - L) / 2 - 10, sh.H * 0.4), hidden=False)
    sh.centerline(fv, (x0, 0, 0), (x1, 0, 0), extend=5)
    dmax = max(d for _, _, d in segs)
    # 直径：每段一个
    k = 0
    for a, b, d in segs:
        if (b - a) * scale >= 22:
            sh.dia_dim(fv, ((a + b) / 2, 0, 0), d, fits.get(d, f"Ø{d:g}"), offset=0)
        else:                                      # 短轴段：引出标注，避免和尺寸线挤在一起
            q = fv.at(((a + b) / 2, 0, d / 2))
            k += 1
            sh.leader_note(q, (q[0] + 6 + 14 * k, q[1] - 22 - 9 * k), fits.get(d, f"Ø{d:g}"))
    # 长度：从左端起的链式尺寸 + 总长
    xs = sorted({a for a, _, _ in segs} | {b for _, b, _ in segs})
    yb = dmax / 2
    for i in range(len(xs) - 1):
        if xs[i + 1] - xs[i] < 0.5:
            continue
        sh.dim(fv, (xs[i], 0, -yb), (xs[i + 1], 0, -yb), f"{xs[i + 1] - xs[i]:g}", offset=-22)
    if len(xs) > 2:
        sh.dim(fv, (x0, 0, -yb), (x1, 0, -yb), f"{x1 - x0:g}", offset=-34)
    # 基准、圆跳动、粗糙度
    def seg_of(d):
        return next(((a + b) / 2, d) for a, b, dd in segs if dd == d)
    for d, letter in datums:
        xm, _ = seg_of(d)
        sh.datum(fv.at((xm, 0, -d / 2)), letter, direction=(0, 1))
    for d, val, ref in runout:
        xm, _ = seg_of(d)
        t = fv.at((xm, 0, d / 2))
        sh.gdt(t, (t[0] + 4, t[1] - 26), "↗", val, ref, via=(t[0], t[1] - 26))
    for d, r in ra.items():
        xm, _ = seg_of(d)
        q = fv.at((xm + 4, 0, d / 2))
        sh.roughness((q[0], q[1] - 0.5), r)
    sh.roughness_rest((W - 98, 30), "Ra 3.2")
    for i, n in enumerate(notes):
        sh.note((30, sh.H - 122 + 6 * i), n, 3.5)
    sh.requirements(req, (30, sh.H - 97))
    return sh


def upper_shaft(D):
    s = load(D / "shaft.step").translate((0, 0, -ZU))
    return shaft_sheet(
        s, "LS-101", "上轴", "45", 1.0, "1:1", size="A2",
        fits={15.0: "Ø15 k5", 19.0: "Ø19", 16.0: "Ø16 h6", 12.0: "Ø12 k5", 10.0: "Ø10 h6"},
        ra={15.0: "Ra 0.4", 12.0: "Ra 0.4", 16.0: "Ra 0.8", 10.0: "Ra 0.8"},
        datums=[(15.0, "A"), (12.0, "B")], runout=[(16.0, "0.015", "A–B"), (10.0, "0.012", "A–B")],
        req=["调质 217–255 HBW；轴承位、曲柄位高频淬火 50–55 HRC，深 0.8–1.2（缝纫机厂工艺方案 LS-101）",
             "轴承位 Ø15 k5（6202）、Ø12 k5（6201）按轴承厂推荐；Ø16 h6 装送布偏心（孔 H7），Ø10 h6 装带轮、转子、手轮",
             "曲柄、偏心、带轮、手轮用紧定螺钉固定的平面，配作（三维里没有画）",
             "台阶圆角 R0.5（6201 内圈倒角限制，G2 设计计算书第五节）；未注倒角 C0.5",
             "未注尺寸公差 GB/T 1804-m；未注几何公差 GB/T 1184-K"])


def lower_shaft(D):
    s = load(D / "lower_shaft.step").translate((0, -LOW[0], -LOW[1]))
    sh = shaft_sheet(
        s, "LS-102", "下轴", "45", 1.0, "1:1",
        fits={12.0: "Ø12 h6"}, ra={12.0: "Ra 0.8"}, datums=[], runout=[],
        req=["调质 217–255 HBW；两个轴承位高频淬火 50–55 HRC（缝纫机厂工艺方案 LS-102）",
             "两个轴承位（6201，中心 x 97、371，长 10）Ø12 k5、Ra 0.4，径向圆跳动 0.010（对两轴承位公共轴线）",
             "其余 Ø12 h6：装下带轮、抬牙偏心、下轴齿轮、剪线凸轮、油泵偏心（孔 H7，紧定螺钉平面配作）",
             "未注倒角 C0.5；未注尺寸公差 GB/T 1804-m；未注几何公差 GB/T 1184-K"],
        notes=["轴承位从左端面起：22–32、296–306（x 92–102、366–376，旋梭组.md）"])
    return sh


def needle_bar(D):
    s = load(D / "needle_bar.step")
    s = s.rotate(bd.Axis.Y, 90).translate((0, 0, 0))       # 竖直的 z 轴转成 x 轴
    bb = s.bounding_box()
    s = s.translate((0, -(bb.min.Y + bb.max.Y) / 2, -(bb.min.Z + bb.max.Z) / 2))
    return shaft_sheet(
        s, "LS-201", "针杆", "GCr15", 1.0, "1:1",
        fits={8.0: "Ø8 h5"}, ra={8.0: "Ra 0.2"}, datums=[], runout=[],
        req=["淬火、回火 58–62 HRC；外圆镀硬铬 5–8 µm 后抛光（镀铬外协）",
             "外径 Ø8 h5；直线度 0.005/100；与机壳针杆导套选配间隙（教材 24.7）",
             "下端针夹孔、横向紧定螺孔、上端连接块的销孔按装配配作（三维里没有画）",
             "未注倒角 C0.3；未注尺寸公差 GB/T 1804-f"])


# ---------------------------------------------------------------- 盘类：偏心、凸轮
def disc_sheet(s, code, title, axis_yz, od, bore, width, ecc, od_fit, req, table=None, scale=2.0):
    s = s.translate((0, -axis_yz[0], -axis_yz[1]))
    bb = s.bounding_box()
    sh = Sheet("A3", title=title, code=code, material="20CrMnTi" if code != "LS-401" else "45", scale_text="2:1",
               mass=f"{mass(code):g} g", qty="1", designer="AI（问渠）", date=DATE)
    xm = (bb.min.X + bb.max.X) / 2
    lv = sh.view([(s, 1)], d=(1, 0, 0), up=(0, 0, 1), scale=scale, ref3=(xm, 0, 0), at=(120, 130), hidden=False)
    fv = sh.view([(s, 1)], "front", scale, ref3=(xm, 0, 0), at=(260, 130), hidden=True)
    sh.center_mark(lv, (xm, 0, 0), bore / 2 + 4)
    # 外圆中心（偏心）
    oc = ((bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2)
    if ecc:
        sh.center_mark(lv, (xm, oc[0], oc[1]), od / 2 + 4)
    sh.dim(lv, (xm, -bore / 2, 0), (xm, bore / 2, 0), f"Ø{bore:g} H7", offset=-(od / 2 + 8) * scale + 0)
    sh.dim(lv, (xm, oc[0] - od / 2, oc[1]), (xm, oc[0] + od / 2, oc[1]), f"Ø{od:g} {od_fit}", offset=(od / 2 + 10) * scale)
    if ecc:                                        # 偏心距：两个中心太近，引出标注
        q = lv.at((xm, oc[0], oc[1]))
        sh.leader_note(q, (q[0] - 40, q[1] - 48), f"偏心距 e = {ecc:g} ±0.01")
    sh.dim(fv, (bb.min.X, 0, -od / 2), (bb.max.X, 0, -od / 2), f"{width:g}", offset=-10)
    sh.datum(lv.at((xm + 0.0, -bore / 2 * 0.7, -bore / 2 * 0.7)), "A", direction=(-0.7, -0.7))
    sh.roughness(lv.at((xm, oc[0], oc[1] + od / 2)), "Ra 0.4")
    sh.roughness_rest((sh.W - 98, 30), "Ra 3.2")
    if table:
        y = 40
        sh.note((300, y), table[0], 3.5, bold=True)
        for i, row in enumerate(table[1:]):
            sh.note((300 + 60 * (i % 2), y + 6 + 5.5 * (i // 2)), row, 3.0)
    sh.requirements(req, (30, 222))
    return sh


def feed_ecc(D):
    s = load(D / "feed_ecc.step")
    return disc_sheet(s, "LS-401", "送布偏心", (0.0, ZU), 26.0, 16.0, 8.0, 3.0, "f7", req=[
        "调质 217–255 HBW，外圆高频淬火 50–55 HRC（缝纫机厂工艺方案：送布 / 抬牙偏心）",
        "偏心距 e = 3.0 ±0.01（送布组.md 第一节）；外圆对内孔 A 的平行度 0.008",
        "外圆 Ø26 f7 装送布连杆大头（ADC12，油润滑）；内孔 Ø16 H7 装上轴，紧定螺钉孔按装配相位配作",
        "未注倒角 C0.5；未注尺寸公差 GB/T 1804-m"])


def lift_ecc(D):
    s = load(D / "lift_ecc.step")
    return disc_sheet(s, "LS-402", "抬牙偏心", LOW, 20.0, 12.0, 8.0, 1.19, "f7", req=[
        "渗碳淬火 58–62 HRC，渗碳层 0.6–0.9",
        "偏心距 e = 1.19 ±0.01（送布组.md 第一节）；外圆对内孔 A 的平行度 0.008",
        "外圆 Ø20 f7 装抬牙连杆（ADC12）；内孔 Ø12 H7 装下轴，紧定螺钉孔按装配相位配作",
        "未注倒角 C0.5；未注尺寸公差 GB/T 1804-m"])


def cam_table():
    """剪线凸轮槽中心线（凸轮坐标，每 30°）：与 cad/opt.py 建模用的是同一组公式"""
    for m in ("FreeCAD", "Part"):
        sys.modules.setdefault(m, types.ModuleType(m))
    sys.modules["FreeCAD"].Vector = lambda *a: a
    import importlib.util
    spec = importlib.util.spec_from_file_location("wq_opt_math", HERE / "cad" / "opt.py")
    o = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(o)
    rr, cm = o.GEO["rock"], o.GEO["cam"]
    Sy, Sz = rr["y"], rr["z"]
    Cy, Cz = LOW
    (Ry, Rz), _, _ = o.roller_rest()
    h = o.OP["knife"]["cam_h"]
    rows = []
    for phi in range(0, 360, 30):
        e = o.rock_angle(o.cam_lift(phi, h) / h * o.OP["knife"]["beta_deg"])
        vy, vz = Ry - Sy, Rz - Sz
        ce, se = math.cos(math.radians(e)), math.sin(math.radians(e))
        Ry_, Rz_ = Sy + ce * vy - se * vz, Sz + se * vy + ce * vz
        rho = math.hypot(Ry_ - Cy, Rz_ - Cz)
        th = (math.degrees(math.atan2(Rz_ - Cz, Ry_ - Cy)) - phi) % 360
        rows.append(f"φ {phi:3d}°：θ {th:6.2f}°  ρ {rho:6.3f}")
    return ["槽中心线（凸轮坐标 θ、ρ；下轴转角 φ）"] + rows, cm


def trim_cam(D):
    s = load(D / "trim_cam.step")
    tab, cm = cam_table()
    return disc_sheet(s, "LS-710", "剪线凸轮", LOW, 51.9, 12.0, 16.0, 0, "", req=[
        "渗碳淬火 58–62 HRC（滚子对槽的接触应力 279 MPa，剪线与电子针距.md 第二节）",
        f"左端面槽：宽 {cm['groove_w']:g} +0.05/0、深 {cm['groove_depth']:g}，槽中心线按右上表（全程每 1° 的点在三维模型里，数控程序直接取模型）",
        "槽相位：φ = 0 时下轴键位 / 紧定螺钉朝上；升程段 280°–340°、停 340°–20°、回程 20°–75°（摆线）",
        "内孔 Ø12 H7 装下轴；轮毂 Ø20 × 6",
        "未注倒角 C0.5；未注尺寸公差 GB/T 1804-m"], table=tab)


def main():
    D = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "docs" / "设计" / "WQ-LS" / "G7" / "工程图"
    out.mkdir(parents=True, exist_ok=True)
    for code, fn in (("LS-101", upper_shaft), ("LS-102", lower_shaft), ("LS-201", needle_bar),
                     ("LS-401", feed_ecc), ("LS-402", lift_ecc), ("LS-710", trim_cam)):
        save(fn(D), out, code)
        print(code, "→", out / f"{code}.pdf")


if __name__ == "__main__":
    main()
