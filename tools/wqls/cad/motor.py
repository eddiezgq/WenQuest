"""WQ-LS 主轴直驱伺服电机与手轮（第 138 轮 G4.3），由 cad/mech.py 调用（在 FreeCAD 里）。

做法是无机壳电机套件装在机壳上（工业平缝机直驱电机的常见结构）：
  机壳立柱右壁伸出后轴承座（铸件），端头是 Ø80 法兰（加工面，止口，4 × M5）；
  ① 前端盖（铝，止口套在 Ø80 法兰上，4 × M5 内六角螺钉固定）；
  ② 定子机座（铝管，后壁带编码器读头座），用 4 根 M4 拉杆螺钉压在前端盖上；
  ③ 定子铁心（硅钢片叠压）和绕组端部；
  ④ 转子：涨紧套固定在上轴 Ø10 轴段上，转子铁心 + 8 块表贴磁钢；
  ⑤ 编码器码盘（4096 线，GC 的控制仿真按这个分辨率）；
  ⑥ 手轮（铝合金压铸，轮辐式，转动惯量与 G2 取的转子 + 手轮约 4 × 10⁻⁴ kg·m² 对得上）。
电磁设计（槽数、绕组、磁钢牌号）在 GC 做；这里定外形、装配关系、质量和惯量。坐标、单位同 spec.py。
"""
import math

import FreeCAD as App
import Part

V = App.Vector
SEAT = 408.0          # 机壳电机座法兰端面（cad/housing.py MOTOR_SEAT_X）
ZU = 200.0
RHO = dict(alu=2.7e-6, steel=7.85e-6, copper=8.9e-6, magnet=7.5e-6)   # kg/mm³


def cyl(r, h, x, y=0.0, z=ZU):
    return Part.makeCylinder(r, h, V(x, y, z), V(1, 0, 0))


def ring(ro, ri, h, x):
    return cyl(ro, h, x).cut(cyl(ri, h + 2, x - 1))


def shcs(p, d=5):
    """ISO 4762 内六角圆柱头螺钉的头（M5：头径 8.5、头高 5、内六角 4；M4：7、4、3），p 为支承面中心，头朝 +x"""
    dk, k, s = {4: (7.0, 4.0, 3.0), 5: (8.5, 5.0, 4.0)}[d]
    head = Part.makeCylinder(dk / 2, k, p, V(1, 0, 0))
    hexp = [p + V(k + 0.1, s / math.sqrt(3) * math.cos(math.radians(a)), s / math.sqrt(3) * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    hx = Part.Face(Part.makePolygon(hexp + [hexp[0]])).extrude(V(-k * 0.6, 0, 0))
    return head.cut(hx)


def build():
    """返回 {零件名: (实体, 材料显示名, 密度键, 是否随轴转)}"""
    P = {}
    # ① 前端盖：x 402…416，外径 112；背面 Ø52 H7 止口孔深 6（套在机壳电机座 Ø52 h7 外圆上，端面贴紧）；中间 Ø24 过轴
    cap = cyl(56, 14, SEAT - 6).cut(cyl(26, 6, SEAT - 7)).cut(cyl(12, 20, SEAT - 8))
    bolts = []
    for a in (45, 135, 225, 315):                       # 4 × M5 螺钉拧进机壳电机座端面（PCD 40），头沉在端盖里
        y, z = 20 * math.cos(math.radians(a)), ZU + 20 * math.sin(math.radians(a))
        cap = cap.cut(Part.makeCylinder(2.75, 10, V(SEAT - 1, y, z), V(1, 0, 0))).cut(Part.makeCylinder(4.6, 6, V(SEAT + 3, y, z), V(1, 0, 0)))
        bolts.append(shcs(V(SEAT + 3, y, z), 5))
    for a in (0, 90, 180, 270):                         # 拉杆螺孔 M4（在外圈）
        cap = cap.cut(Part.makeCylinder(1.65, 10, V(SEAT + 6.1, 51 * math.cos(math.radians(a)), ZU + 51 * math.sin(math.radians(a))), V(1, 0, 0)))
    P["motor_cap"] = (cap, "black", "alu", False)
    P["motor_bolts"] = (Part.makeCompound(bolts), "black", "steel", False)
    # ② 定子机座：铝管 Ø112/Ø104，x 416…456；后壁 x 456…462，中间 Ø24 过轴、编码器读头凸台
    hs = ring(56, 52, 40, SEAT + 8).fuse(cyl(56, 6, SEAT + 48).cut(cyl(12, 8, SEAT + 47)))
    for k in range(10):                                 # 外圆散热浅槽（压铸件）
        hs = hs.cut(ring(57, 55.4, 1.6, SEAT + 12 + 3.6 * k))
    hs = hs.fuse(Part.makeBox(8, 10, 12, V(SEAT + 41, -5, ZU + 22)))          # 编码器读头座
    rods = []
    for a in (0, 90, 180, 270):                         # 拉杆螺钉头沉在后壁里（与手轮之间留 2 mm）
        y, z = 51 * math.cos(math.radians(a)), ZU + 51 * math.sin(math.radians(a))
        hs = hs.cut(Part.makeCylinder(3.8, 5, V(SEAT + 50, y, z), V(1, 0, 0)))
        rods.append(shcs(V(SEAT + 50, y, z), 4))
    P["motor_housing"] = (hs, "black", "alu", False)
    P["motor_rods"] = (Part.makeCompound(rods), "black", "steel", False)
    # ③ 定子铁心 Ø102/Ø55，长 26（x 420…446），叠片纹；12 个齿槽；绕组端部（铜）
    st = ring(51, 27.6, 26, SEAT + 12)                  # 气隙 1.1 mm
    for k in range(12):
        a = math.radians(15 + 30 * k)
        st = st.cut(Part.makeCylinder(4.2, 28, V(SEAT + 11, 33 * math.cos(a), ZU + 33 * math.sin(a)), V(1, 0, 0)))
    for k in range(13):
        st = st.cut(ring(51.5, 50.6, 0.3, SEAT + 12 + 2 * k))
    P["stator_core"] = (st, "steelDark", "steel", False)
    wd = ring(44, 30, 5, SEAT + 9).fuse(ring(44, 30, 5, SEAT + 38))
    wd = wd.common(cyl(44, 40, SEAT + 7))
    P["stator_winding"] = (wd, "copper", "copper", False)
    # ④ 转子：涨紧套（Ø10/Ø24，x 418…426）+ 转子铁心 Ø53/Ø24（x 420…446）+ 8 块磁钢（厚 2.5）
    rot = ring(12, 5, 8, SEAT + 10).fuse(ring(24, 12, 26, SEAT + 12)).fuse(ring(14, 5, 34, SEAT + 12))
    P["rotor"] = (rot, "steelDark", "steel", True)
    mags = None
    for k in range(8):
        a0 = 22.5 + 45 * k
        seg = ring(26.5, 24, 26, SEAT + 12).common(
            Part.Face(Part.makePolygon([V(SEAT + 12, 0, ZU), V(SEAT + 12, 40 * math.cos(math.radians(a0 - 19)), ZU + 40 * math.sin(math.radians(a0 - 19))),
                                        V(SEAT + 12, 40 * math.cos(math.radians(a0 + 19)), ZU + 40 * math.sin(math.radians(a0 + 19))), V(SEAT + 12, 0, ZU)])).extrude(V(26, 0, 0)))
        mags = seg if mags is None else mags.fuse(seg)
    P["rotor_magnets"] = (mags, "magnet", "magnet", True)
    # ⑤ 编码器码盘 Ø44 × 1（x 452）+ 轮毂
    P["encoder_disc"] = (cyl(20, 1, SEAT + 44).fuse(ring(8, 5, 6, SEAT + 40)), "glassDisc", "alu", True)
    # ⑥ 手轮：轮毂 Ø22（x 464…472，顶丝固定在轴端），轮辐板厚 3，轮缘 Ø104/Ø92 × 16，外缘滚花槽，中心盖
    hx0 = SEAT + 56
    hub = ring(11, 5, 8, hx0)
    web = cyl(46, 3, hx0 + 4)
    rim = ring(52, 46, 16, hx0)
    for k in range(48):
        a = 2 * math.pi * k / 48
        rim = rim.cut(Part.makeCylinder(1.2, 18, V(hx0 - 1, 52.6 * math.cos(a), ZU + 52.6 * math.sin(a)), V(1, 0, 0)))
    for k in range(5):                                  # 轮辐板上 5 个减重孔
        a = 2 * math.pi * k / 5 + 0.3
        web = web.cut(Part.makeCylinder(10, 5, V(hx0 + 3, 30 * math.cos(a), ZU + 30 * math.sin(a)), V(1, 0, 0)))
    hw = hub.fuse(web).fuse(rim).fuse(cyl(11, 2, hx0 + 8))
    P["handwheel"] = (hw, "graphite", "alu", True)
    P["handwheel_ring"] = (ring(52.3, 50.5, 2, hx0 + 16.2), "blue", "alu", True)
    return P


def inertia_x(shape, rho):
    """绕上轴（x 轴，过 y = 0、z = ZU）的转动惯量 kg·m²"""
    I = shape.MatrixOfInertia          # 绕质心，单位密度
    c = shape.CenterOfMass
    d2 = c.y ** 2 + (c.z - ZU) ** 2
    return (I.A11 + shape.Volume * d2) * rho * 1e-6
