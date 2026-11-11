"""WQ-LS 旋梭组（第 138 轮 G4.5），由 cad/mech.py 调用（在 FreeCAD 里）。

传动：上轴同步带轮（x 352）→ HTD 3M 同步带 570-3M-15 → 下轴带轮 → 下轴 LS-501（Ø12，两个 6201）→
      斜齿轮 z 40（下轴）/ z 20（旋梭轴），mn 1、β 15° → 旋梭轴 LS-302（两个锡青铜轴套）→ 旋梭 LS-301。
旋梭是外购件，这里按“轴径 7.94 mm”一级的外形和安装尺寸建模（示例尺寸）：梭尖回转半径 13.5，
梭面（开口一面朝 −x）离机针表面 0.08（梭尖间隙），机针 Nm 90 半径 0.45，所以梭面在 x = 0.53。
齿轮的齿形是真的渐开线（端面齿廓沿齿宽按螺旋角扭转）；轴承、轴套、带只画外形。
坐标、单位同 spec.py（原点在针板上表面、机针中心线上；X 右、Y 后、Z 上，mm），φ = 0 时的位置。
"""
import math
import os
import sys

import FreeCAD as App
import Part

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.path.join(os.getcwd(), "tools", "wqls", "cad")
sys.path[:0] = [os.path.abspath(os.path.join(HERE, ".."))]
import spec as S  # noqa: E402

RHO = dict(steel=7.85e-6, bronze=8.8e-6, rubber=1.3e-6, alu=2.7e-6)
ZU, ZH, ZL, YL = S.ZU, S.ZH, S.ZL, S.YL
G = S.GEAR
# 沿 X 的排布
X_HOOK_FACE = 0.53                     # 梭面（梭尖间隙 0.08 + 针半径 0.45）
HOOK_LEN = 22.0
X_BUSH = ((26.0, 14.0), (50.0, 14.0))  # 旋梭轴两个轴套（起点、长）
X_GEAR = 72.0                          # 齿轮左端面（齿宽 b = 8）
X_BRG_L = (92.0, 366.0)                # 下轴两个 6201 的左端面（宽 10）
X_PULLEY = S.X_BELT                    # 带轮中面 352
LOW_SHAFT = (70.0, 384.0)              # 下轴 x 范围
HOOK_SHAFT = (8.0, 92.0)               # 旋梭轴 x 范围
PD = S.BELT["z"] * S.BELT["pitch"] / math.pi      # 带轮节圆直径 28.65
OD_PULLEY = PD - 0.76                              # HTD 3M 的节线差 2 × 0.381


def cyl(r, h, x, y, z):
    return Part.makeCylinder(r, h, V(x, y, z), V(1, 0, 0))


def tube(ro, ri, h, x, y, z):
    return cyl(ro, h, x, y, z).cut(cyl(ri, h + 2, x - 1, y, z))


def involute_profile(mn, z, beta_deg, n_inv=8):
    """端面齿廓（端面模数、端面压力角），返回 ((y, z) 点列, 齿顶圆半径)，以齿轮中心为原点，第 1 个齿的对称线在 +y 方向"""
    be = math.radians(beta_deg)
    at = math.atan(math.tan(math.radians(20)) / math.cos(be))
    r = mn / math.cos(be) * z / 2
    rb = r * math.cos(at)
    ra, rf = r + mn, r - 1.25 * mn

    def inv(a):
        return math.tan(a) - a
    half = math.pi / (2 * z) + inv(at)            # 基圆上的半齿角（从齿对称线量）
    r0 = max(rb, rf)
    flank = []
    for i in range(n_inv + 1):
        rr = r0 + (ra - r0) * i / n_inv
        flank.append((rr, half - inv(math.acos(min(1.0, rb / rr)))))
    pol = []
    for k in range(z):
        c = 2 * math.pi * k / z
        if rf < rb:
            pol.append((rf, c - flank[0][1]))
        pol += [(rr, c - th) for rr, th in flank]
        pol += [(rr, c + th) for rr, th in reversed(flank)]
        if rf < rb:
            pol.append((rf, c + flank[0][1]))
    return [(rr * math.cos(th), rr * math.sin(th)) for rr, th in pol], ra


def helical_gear(mn, z, beta_deg, b, x0, yc, zc, hand=1, bore=0.0, phase=0.0, sections=5):
    """端面齿廓沿 x 扭转：齿宽 b 上转过 b·tanβ / r（hand = ±1 为左右旋）"""
    prof, ra = involute_profile(mn, z, beta_deg)
    r = mn * z / math.cos(math.radians(beta_deg)) / 2
    twist = hand * b * math.tan(math.radians(beta_deg)) / r
    wires = []
    for i in range(sections):
        t = i / (sections - 1)
        a = phase + twist * t
        ca, sa = math.cos(a), math.sin(a)
        p = [V(x0 + b * t, yc + y * ca - zz * sa, zc + y * sa + zz * ca) for y, zz in prof]
        wires.append(Part.makePolygon(p + [p[0]]))
    g = Part.makeLoft(wires, True, True)
    if bore:
        g = g.cut(cyl(bore / 2, b + 2, x0 - 1, yc, zc))
    return g


def envelope(c1, c2, r, x0, t):
    """两个等半径圆的包络（皮带外形），c 为 (y, z)"""
    (y1, z1), (y2, z2) = c1, c2
    d = math.hypot(y2 - y1, z2 - z1)
    ny, nz = -(z2 - z1) / d * r, (y2 - y1) / d * r
    quad = [V(x0, y1 + ny, z1 + nz), V(x0, y2 + ny, z2 + nz), V(x0, y2 - ny, z2 - nz), V(x0, y1 - ny, z1 - nz)]
    body = Part.Face(Part.makePolygon(quad + [quad[0]])).extrude(V(t, 0, 0))
    return body.fuse(cyl(r, t, x0, y1, z1)).fuse(cyl(r, t, x0, y2, z2)).removeSplitter()


def pulley(x_mid, yc, zc, bore):
    w = S.BELT["width"]
    p = cyl(OD_PULLEY / 2, w + 0.6, x_mid - w / 2 - 0.3, yc, zc)
    for k in range(S.BELT["z"]):                      # 齿槽（HTD 圆弧齿，这里画成深 1.15 的槽）
        a = 2 * math.pi * k / S.BELT["z"]
        ry, rz = math.cos(a), math.sin(a)
        p = p.cut(Part.makeCylinder(0.9, w + 2, V(x_mid - w / 2 - 1, yc + (OD_PULLEY / 2 + 0.2) * ry, zc + (OD_PULLEY / 2 + 0.2) * rz), V(1, 0, 0)))
    for xs in (x_mid - w / 2 - 1.6, x_mid + w / 2 + 0.3):        # 两侧挡边
        p = p.fuse(cyl(OD_PULLEY / 2 + 2.0, 1.3, xs, yc, zc))
    p = p.fuse(cyl(9.0, 5, x_mid - w / 2 - 6.6, yc, zc))         # 轮毂在左边（右边紧挨着下轴右轴承），两个紧定螺钉
    return p.cut(cyl(bore / 2, 40, x_mid - 20, yc, zc))


def bearing_6201(x0, yc, zc):
    o = tube(16.0, 13.6, 10, x0, yc, zc)
    i = tube(8.3, 6.0, 10, x0, yc, zc)
    balls = [Part.makeSphere(2.4, V(x0 + 5, yc + 10.9 * math.cos(2 * math.pi * k / 7), zc + 10.9 * math.sin(2 * math.pi * k / 7)))
             for k in range(7)]
    return o.fuse(i).fuse(Part.makeCompound(balls))


def build():
    """返回 {零件名: (实体, 材料显示名, 密度键, 转动类别)}；转动类别：'upper' 随上轴、'lower' 随下轴、'hook' 随旋梭轴、None 不动"""
    P = {}
    # 上轴带轮（Ø16 孔）、下轴带轮（Ø12 孔）
    P["pulley_upper"] = (pulley(X_PULLEY, 0.0, ZU, 16.0), "metal", "steel", "upper")
    P["pulley_lower"] = (pulley(X_PULLEY, YL, ZL, 12.0), "metal", "steel", "lower")
    # 同步带：节线外 0.4、里 1.9（齿高 1.15 + 带背 0.75 的示意）
    w = S.BELT["width"]
    belt = envelope((0.0, ZU), (YL, ZL), PD / 2 + 0.4, X_PULLEY - w / 2, w).cut(
        envelope((0.0, ZU), (YL, ZL), PD / 2 - 1.5, X_PULLEY - w / 2 - 1, w + 2))
    P["belt"] = (belt, "black", "rubber", None)
    # 下轴 Ø12（轴颈、轴身同径，轴承和带轮用卡簧、紧定螺钉轴向定位）
    P["lower_shaft"] = (cyl(6.0, LOW_SHAFT[1] - LOW_SHAFT[0], LOW_SHAFT[0], YL, ZL), "chrome", "steel", "lower")
    P["bearings_lower"] = (Part.makeCompound([bearing_6201(x, YL, ZL) for x in X_BRG_L]), "metal", "steel", None)
    # 齿轮对：z 40 在下轴（右旋），z 20 在旋梭轴（左旋），平行轴外啮合；相位：在中心连线上，小齿轮的齿对着大齿轮的齿槽
    b = G["b"]
    dy, dz = YL - 0.0, ZL - ZH
    ang = math.atan2(dz, dy)                           # 从旋梭轴指向下轴的方向角（在 YZ 平面里，从 +y 量）
    gh = helical_gear(G["mn"], G["z_hook"], G["beta"], b, X_GEAR, 0.0, ZH, hand=-1, bore=10.0, phase=ang)
    gh = gh.fuse(tube(8.0, 5.0, 6, X_GEAR + b, 0.0, ZH))
    gl = helical_gear(G["mn"], G["z_lower"], G["beta"], b, X_GEAR, YL, ZL, hand=1, bore=12.0,
                      phase=ang + math.pi + math.pi / G["z_lower"])
    gl = gl.fuse(tube(10.0, 6.0, 6, X_GEAR + b, YL, ZL))
    P["gear_hook"] = (gh, "metal", "steel", "hook")
    P["gear_lower"] = (gl, "metal", "steel", "lower")
    # 旋梭轴：Ø7.94 装旋梭（x 8…23），Ø10 轴身；轴心 Ø2.5 油孔
    hs = cyl(7.94 / 2, 23 - HOOK_SHAFT[0], HOOK_SHAFT[0], 0.0, ZH).fuse(cyl(5.0, HOOK_SHAFT[1] - 23, 23, 0.0, ZH))
    hs = hs.cut(cyl(1.25, 60, HOOK_SHAFT[0] - 1, 0.0, ZH))
    P["hook_shaft"] = (hs, "chrome", "steel", "hook")
    P["bushes_hook"] = (Part.makeCompound([tube(7.0, 5.0, L, x, 0.0, ZH) for x, L in X_BUSH]), "brass", "bronze", None)
    # 旋梭（外购，示例外形）：梭面 x 0.53；前 3 mm 外圆 r 13.0、梭尖伸到 r 13.5；后面梭床 r 15；尾部轴套 Ø14 夹在旋梭轴上
    x0 = X_HOOK_FACE
    hk = cyl(13.0, 3.0, x0, 0.0, ZH).fuse(cyl(15.0, 15.0, x0 + 3.0, 0.0, ZH)).fuse(cyl(7.0, HOOK_LEN - 18.0, x0 + 18.0, 0.0, ZH))
    hk = hk.cut(cyl(11.6, 16.5, x0 - 1, 0.0, ZH))                 # 梭芯套的腔（朝 −x 开口）
    hk = hk.cut(cyl(7.94 / 2, 30, x0 + 10, 0.0, ZH))               # 装轴的孔
    tip_a = math.radians(142.2)                                     # φ = 0 时梭尖的方向角（从 +y 量），钩线角 206.1° 时转到正上方
    tip = Part.makeBox(2.0, 1.2, 1.4, V(x0, -0.6, 12.1)).rotate(V(0, 0, 0), V(1, 0, 0), math.degrees(tip_a) - 90)
    tip.translate(V(0, 0, ZH))
    hk = hk.fuse(tip)
    P["hook"] = (hk, "chrome", "steel", "hook")
    # 梭芯套和梭芯（不转，由梭芯套定位钩挡住）：Ø21 梭芯装在梭芯套里
    bc = cyl(11.2, 14.0, x0 + 1.0, 0.0, ZH).cut(cyl(10.6, 13.0, x0 + 0.5, 0.0, ZH)).fuse(cyl(10.5, 9.0, x0 + 3.0, 0.0, ZH).cut(cyl(3.0, 12, x0 + 2, 0.0, ZH)))
    P["bobbin_case"] = (bc, "metal", "steel", None)
    return P


def inertia_x(s, rho, yc, zc):
    """绕 (yc, zc) 的 x 轴的转动惯量 kg·m²"""
    s = s.Solids if s.ShapeType == "Compound" else [s]
    J = 0.0
    for so in s:
        I = so.MatrixOfInertia
        c = so.CenterOfMass
        J += (I.A11 + so.Volume * ((c.y - yc) ** 2 + (c.z - zc) ** 2)) * rho
    return J * 1e-6
