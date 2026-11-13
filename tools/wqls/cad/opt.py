"""WQ-LS 选配件（第 138 轮 G4.8），由 cad/mech.py 调用：build() 返回 {零件名: (实体, 显示材料, 密度键, 运动类别)}。

尺寸来自 tools/wqls/g4_opt.py 的结果（docs/设计/WQ-LS/G4/选配件.json 的 geo）。
选项（环境变量）WQ_OPT：逗号分开的 T、E（D 只是旋梭镀膜，不改形状），例如 WQ_OPT=T,E；不给或空 = 基本型（没有选配件）。
零件都按“动刀在最后、滚子没进槽、拨线钩在收回位置”画；一转里怎么动由 g4_mech.py 给（WQ_TRIM=sew / trim / wipe）。
运动类别：'low' 随下轴转；'rock' 剪线摆轴（绕 x）；'tlever' 摆杆（绕 x，剪线时沿 x 推进 5）；'tlink' 球头拉杆；
         'knife' 动刀（绕竖轴）；'wiper' 拨线钩（绕竖轴）；None 不动。
"""
import json
import math
import os

import FreeCAD as App
import Part

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
G4 = os.path.join(ROOT, "docs", "设计", "WQ-LS", "G4")
OP = json.load(open(os.path.join(G4, "选配件.json"), encoding="utf-8"))
CT = json.load(open(os.path.join(G4, "操纵件.json"), encoding="utf-8"))
FD = json.load(open(os.path.join(G4, "送布机构.json"), encoding="utf-8"))
GEO = OP["geo"]
OPT = {s.strip().upper() for s in os.environ.get("WQ_OPT", "").split(",") if s.strip()}
SET = os.environ.get("WQ_FEED", "s3")
DEG = math.pi / 180
RHO = dict(steel=7.85e-6, alu=2.75e-6, plastic=1.2e-6, copper=8.9e-6)
LOW = (27.791774943072237, -35.36485983577417)
# 电子针距去掉的 G4.7 零件
E_REMOVE = ("pull_rod", "stitch_dial", "reverse_lever", "reverse_spring")


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, a, b):
    a, b = V(*a), V(*b)
    return Part.makeCylinder(r, (b - a).Length, a, b - a)


def slab(pts, z0, z1):
    """x–y 平面里的多边形，z0…z1"""
    w = Part.makePolygon([V(x, y, z0) for x, y in pts] + [V(pts[0][0], pts[0][1], z0)])
    return Part.Face(w).extrude(V(0, 0, z1 - z0))


def strip(path, w, z0, z1):
    """x–y 平面里沿折线 path、宽 w 的条（每段一个圆头矩形）"""
    out = None
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        nx, ny = -uy * w / 2, ux * w / 2
        s = slab([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], z0, z1)
        s = s.fuse(cyl(w / 2, (x1, y1, z0), (x1, y1, z1)))
        out = s if out is None else out.fuse(s)
    return out.fuse(cyl(w / 2, (path[0][0], path[0][1], z0), (path[0][0], path[0][1], z1)))


def rot_z(p, c, ang):
    dx, dy = p[0] - c[0], p[1] - c[1]
    return (c[0] + dx * math.cos(ang) - dy * math.sin(ang), c[1] + dx * math.sin(ang) + dy * math.cos(ang))


def cam_lift(phi, h):
    p = phi % 360
    if 20.0 <= p < 75.0:
        u = (p - 20.0) / 55.0
        return h * (1 - (u - math.sin(2 * math.pi * u) / (2 * math.pi)))
    if p < 20.0 or p >= 340.0:
        return h
    if 280.0 <= p < 340.0:
        u = (p - 280.0) / 60.0
        return h * (u - math.sin(2 * math.pi * u) / (2 * math.pi))
    return 0.0


def rock_angle(dl):
    """动刀转 dl（度，往前为正）时剪线摆轴的转角 ε（度）：球头拉杆长度不变（同 g4_mech.opt_motion）"""
    k, rr = GEO["knife"], GEO["rock"]
    px, py = k["pivot"]
    Sy, Sz, rc, cx = rr["y"], rr["z"], rr["crank_r"], rr["crank_x"]
    K0 = (px - k["crank_r"], py, -50.0)
    Kp = (px - k["crank_r"] * math.cos(dl * DEG), py - k["crank_r"] * math.sin(dl * DEG), -50.0)

    def rpin(e):
        c, s_ = math.cos(e * DEG), math.sin(e * DEG)
        return (cx, Sy + c * -6.0 - s_ * -rc, Sz + s_ * -6.0 + c * -rc)

    def dist(a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
    L0 = dist(rpin(0.0), K0)
    lo, hi = -40.0, 40.0
    for _ in range(60):
        e = (lo + hi) / 2
        if dist(rpin(e), Kp) > L0:
            hi = e
        else:
            lo = e
    return (lo + hi) / 2


def roller_rest():
    """滚子中心（静止段）在 (y, z)：以下轴中心 C、摆轴中心 S 为直径的圆上、离 C 为 rho0，取上面那个交点"""
    rr, cm = GEO["rock"], GEO["cam"]
    Cy, Cz = LOW
    Sy, Sz = rr["y"], rr["z"]
    d = math.hypot(Sy - Cy, Sz - Cz)
    r0 = cm["rho0"]
    # CR ⊥ SR：R 在以 CS 为直径的圆上；|CR| = r0 → 和 CS 的夹角 acos(r0 / d)
    base = math.atan2(Sz - Cz, Sy - Cy)
    a = math.acos(r0 / d)
    cands = [(Cy + r0 * math.cos(base + s * a), Cz + r0 * math.sin(base + s * a)) for s in (1, -1)]
    return max(cands, key=lambda p: p[1]), base, a


def knife_poly():
    """动刀（前进到最前时）的折线：刀轴 → 拐点 (−9.5, 7) → 抬起点 (−5, 4.9) → 刀尖；前两段在 z −8.6…−6.6
    （从机座顶板下面过去，离顶板底 1.0；这一段都在 x < −6.5，送布牙排侧梁从 x −6.5 才开始），从抬起点到刀尖是刀片（z −5.9…−4.9）。
    再按 a_rest − a_fwd 转回最后的位置画（零件按静止位置画）"""
    k = GEO["knife"]
    px, py = k["pivot"]
    fwd = [(px, py), (-9.5, 7.0), (-5.0, 4.9), tuple(k["tip_fwd"])]
    back = (OP["knife"]["a_rest_deg"] - OP["knife"]["a_fwd_deg"]) * DEG
    return [rot_z(p, (px, py), back) for p in fwd], back


def build_T():
    P = {}
    k, fx, bs, rr, cm = GEO["knife"], GEO["fixed"], GEO["base"], GEO["rock"], GEO["cam"]
    px, py = k["pivot"]
    kz0, kz1 = GEO["knife_plane"]
    # ---- 动刀：刀轴 Ø8（z −52…−7）+ 刀座（z −9…−7）+ 下端曲柄（朝 −x，半径 8，z −52…−48）+ 刀片
    poly, back = knife_poly()
    arm = strip(poly[:2], 5.0, -8.6, -6.6).fuse(strip(poly[1:3], 4.0, -8.6, -6.6))     # 低的一段（离机座顶板底 1.0）
    rise = cyl(2.0, (poly[2][0], poly[2][1], -8.6), (poly[2][0], poly[2][1], kz1))           # 抬到刀片平面
    blade = strip(poly[2:], 3.5, kz0, kz1)
    hub = cyl(k["hub_r"], (px, py, -9.0), (px, py, -6.6))
    tip = poly[3]
    # 刀尖的钩：刀尖往后 6 处朝 −y 开一个 2 宽的缺口（钩线），内刃在缺口里
    hook = cyl(1.2, (tip[0] - 4.0 * math.cos(back), tip[1] - 4.0 * math.sin(back) - 1.6, kz0 - 1), (tip[0] - 4.0 * math.cos(back), tip[1] - 4.0 * math.sin(back) - 1.6, kz1 + 1))
    knife = arm.fuse(rise).fuse(blade).cut(hook)
    shaft = cyl(k["shaft_d"] / 2, (px, py, k["shaft_z"][0]), (px, py, k["shaft_z"][1]))
    crank = strip([(px, py), (px - k["crank_r"], py)], 8.0, k["crank_z"] - 2.0, k["crank_z"] + 2.0)
    pin = cyl(2.0, (px - k["crank_r"], py, k["crank_z"] - 6.0), (px - k["crank_r"], py, k["crank_z"]))
    P["moving_knife"] = (knife.fuse(hub), "chrome", "steel", "knife")
    P["knife_shaft"] = (shaft.fuse(crank).fuse(pin), "metal", "steel", "knife")
    # ---- 定刀：针板底面，x −22…−12（刃在 x −12），y −5…4，底面 z −4.9（动刀顶面贴着它剪）
    P["fixed_knife"] = (box(fx["x_back"], fx["x_edge"], fx["y"][0], fx["y"][1], fx["z"][0], fx["z"][1]).cut(
        cyl(1.6, (fx["screw_x"], 0.0, fx["z"][0] - 1), (fx["screw_x"], 0.0, fx["z"][1] + 1))), "chrome", "steel", None)
    # ---- 动刀轴座：钢板 z −14…−10，螺在机座顶板下两个凸台（x −28、+8，y 40）上；轴套往下到 z −30
    base = box(-34.0, 14.0, py - 7.0, py + 7.0, bs["z"][0], bs["z"][1]).fuse(cyl(7.0, (px, py, bs["bushing"][0]), (px, py, bs["z"][0])))
    base = base.cut(cyl(k["shaft_d"] / 2 + 0.05, (px, py, bs["bushing"][0] - 1), (px, py, bs["z"][1] + 1)))
    for sx in (-28.0, 8.0):
        base = base.cut(cyl(2.25, (sx, py, bs["z"][0] - 1), (sx, py, bs["z"][1] + 1)))
    P["trim_base"] = (base, "metal", "steel", None)
    # ---- 剪线摆轴：Ø10 沿 x（y 60、z −30），左端曲柄朝下 20，曲柄销在 x −18（和动刀曲柄销同一 x）
    Sy, Sz = rr["y"], rr["z"]
    rock = cyl(rr["d"] / 2, (rr["x"][0], Sy, Sz), (rr["x"][1] - 10.0, Sy, Sz))
    cx = rr["crank_x"]
    rc = box(cx - 2.0, cx + 2.0, Sy - 4.0, Sy + 4.0, Sz - rr["crank_r"], Sz).fuse(cyl(4.0, (cx - 2.0, Sy, Sz - rr["crank_r"]), (cx + 2.0, Sy, Sz - rr["crank_r"])))
    rc = rc.fuse(cyl(2.0, (cx - 2.0, Sy, Sz - rr["crank_r"]), (cx - 2.0, Sy - 6.0, Sz - rr["crank_r"])))     # 球头销朝 −y
    P["trim_rock"] = (rock.fuse(rc), "metal", "steel", "rock")
    # ---- 摆轴座两个（钢件，x −12…−4、94…104），各两颗 M5 螺在机座顶板下的凸台（z −10）上；右边的座往右伸一块托住剪线电磁铁
    brk = None
    for xa, xb in ((-12.0, -4.0), (94.0, 104.0)):
        b_ = box(xa, xb, Sy - 8.0, Sy + 8.0, Sz - 8.0, -10.0).fuse(cyl(8.0, (xa, Sy, Sz), (xb, Sy, Sz)))
        b_ = b_.cut(cyl(rr["d"] / 2 + 0.05, (xa - 1, Sy, Sz), (xb + 1, Sy, Sz)))
        for yy in (Sy - 5.0, Sy + 5.0):
            b_ = b_.cut(cyl(2.75, ((xa + xb) / 2, yy, -21.0), ((xa + xb) / 2, yy, -9.0)))
        brk = b_ if brk is None else brk.fuse(b_)
    st_ = GEO["solenoid_trim"]
    shelf = box(94.0, st_["x"][1], Sy - 6.0, Sy + 6.0, Sz - 18.0 - st_["d"] / 2 - 3.0, Sz - 18.0 - st_["d"] / 2).fuse(
        box(94.0, 104.0, Sy - 6.0, Sy + 6.0, Sz - 18.0 - st_["d"] / 2 - 3.0, Sz - 8.0))
    P["trim_brackets"] = (brk.fuse(shelf), "metal", "steel", None)
    # ---- 球头拉杆：沿 y，从动刀曲柄销 (−18, 40, −50) 到摆轴曲柄销 (−18, 60, −50)
    lk = GEO["link"]
    a, b = (px - k["crank_r"], py, k["crank_z"] - 4.0), (cx, Sy - 6.0, Sz - rr["crank_r"])
    a, b = (a[0], a[1], -50.0), (b[0], b[1], -50.0)
    link = cyl(lk["d"] / 2, (a[0], a[1] + 3.0, a[2]), (b[0], b[1] - 3.0, b[2])).fuse(Part.makeSphere(lk["ball_d"] / 2, V(*a))).fuse(Part.makeSphere(lk["ball_d"] / 2, V(*b)))
    P["trim_link"] = (link, "metal", "steel", "tlink")
    # ---- 摆杆 + 滚子：套在摆轴上（x 126…136），滚子轴沿 +x，静止时滚子在 x 135…139（离凸轮端面 1）
    (Ry, Rz), _, _ = roller_rest()
    lx0, lx1 = cm["lever_x"]
    hubl = cyl(9.0, (lx0, Sy, Sz), (lx1, Sy, Sz)).cut(cyl(rr["d"] / 2 + 0.05, (lx0 - 1, Sy, Sz), (lx1 + 1, Sy, Sz)))
    L = math.hypot(Ry - Sy, Rz - Sz)
    ang = math.degrees(math.atan2(Rz - Sz, Ry - Sy))
    armL = Part.makeBox(lx1 - lx0, L, 8.0, V(lx0, 0.0, -4.0))
    armL.rotate(V(0, 0, 0), V(1, 0, 0), ang)                 # 沿 +y 画的臂转到朝滚子
    armL.translate(V(0, Sy, Sz))
    stud = cyl(2.0, (lx1 - 1.0, Ry, Rz), (lx1 + 4.5, Ry, Rz))
    roll = cyl(cm["roller_d"] / 2, (lx1 + 0.8, Ry, Rz), (lx1 + 4.8, Ry, Rz))           # 静止时 x 134.8…138.8，剪线时推进 5 到 139.8…143.8（槽深 4，离槽底 0.2）
    P["trim_lever"] = (hubl.fuse(armL).fuse(stud).fuse(cyl(4.5, (lx0, Ry, Rz), (lx1, Ry, Rz))), "metal", "steel", "tlever")
    P["trim_roller"] = (roll, "chrome", "steel", "tlever")
    # ---- 剪线凸轮：下轴 x 140…150 上的盘，左端面开槽（深 4、宽 8.4）；槽中心线半径 = rho0 + s(φ)
    Cy, Cz = LOW
    h = OP["knife"]["cam_h"]
    rmax = cm["rho0"] + h + 0.3 + cm["roller_d"] / 2 + 3.0
    disc = cyl(rmax, (cm["x"][0], Cy, Cz), (cm["x"][1], Cy, Cz)).fuse(cyl(10.0, (cm["x"][1], Cy, Cz), (cm["x"][1] + 6.0, Cy, Cz)))
    disc = disc.cut(cyl(6.0, (cm["x"][0] - 1, Cy, Cz), (cm["x"][1] + 7, Cy, Cz)))
    pts = []
    for i in range(360):
        phi = i * 1.0
        e = rock_angle(cam_lift(phi, h) / h * OP["knife"]["beta_deg"])
        vy, vz = Ry - Sy, Rz - Sz
        ce, se = math.cos(e * DEG), math.sin(e * DEG)
        Ry_, Rz_ = Sy + ce * vy - se * vz, Sz + se * vy + ce * vz      # 滚子这时在哪（跟着摆轴转）
        rho = math.hypot(Ry_ - Cy, Rz_ - Cz)
        th = math.atan2(Rz_ - Cz, Ry_ - Cy) - phi * DEG    # 凸轮随下轴转 +φ（rot_x）：槽上这一点转 φ 后正好在滚子那里
        pts.append((Cy + rho * math.cos(th), Cz + rho * math.sin(th)))

    def offset(sign):
        out = []
        n = len(pts)
        for i in range(n):
            (y0, z0), (y1, z1) = pts[i - 1], pts[(i + 1) % n]
            ty, tz = y1 - y0, z1 - z0
            L_ = math.hypot(ty, tz)
            ny, nz = tz / L_, -ty / L_
            # 法向朝外（离开中心）
            cy_, cz_ = pts[i]
            if (cy_ - Cy) * ny + (cz_ - Cz) * nz < 0:
                ny, nz = -ny, -nz
            out.append((cy_ + sign * ny * cm["groove_w"] / 2, cz_ + sign * nz * cm["groove_w"] / 2))
        return out
    x0g = cm["x"][0]

    def face(yz):
        w = Part.makePolygon([V(x0g - 1.0, y, z) for y, z in yz] + [V(x0g - 1.0, yz[0][0], yz[0][1])])
        return Part.Face(w)
    outer = face(offset(1)).extrude(V(cm["groove_depth"] + 1.0, 0, 0))
    inner = face(offset(-1)).extrude(V(cm["groove_depth"] + 1.0, 0, 0))
    groove = outer.cut(inner)
    P["trim_cam"] = (disc.cut(groove), "metal", "steel", "low")
    # ---- 剪线电磁铁：在摆轴下面（z −46），平行于摆轴，推杆顶摆杆的叉（沿 +x）
    st = GEO["solenoid_trim"]
    zs = Sz - 18.0                                                  # 电磁铁在摆轴下面（顶离摆轴 2）
    sol = cyl(st["d"] / 2, (st["x"][0], Sy, zs), (st["x"][1], Sy, zs)).fuse(
        cyl(2.5, (st["x"][1], Sy, zs), (lx0 - 0.5, Sy, zs)))
    sol = sol.fuse(box(lx0 - 0.5, lx0 + 2.0, Sy - 2.0, Sy + 2.0, zs - 2.5, Sz - 9.0))       # 推杆头上的叉，顶摆杆轮毂
    P["trim_solenoid"] = (sol, "graphite", "copper", None)
    # ---- 拨线器：竖轴在 (−30, −10)，从机头底板（z 46…50.5）的轴座伸下来到 z 4；钢丝 Ø1.2 在 z 4.6，收回时朝 −y 偏 −100°
    wp = GEO["wiper"]
    wx, wy = wp["pivot"]
    wz = wp["wire_z"]
    rest = math.radians(-100.0)
    tipw = (wx + wp["r"] * math.cos(rest), wy + wp["r"] * math.sin(rest))
    wire = cyl(wp["wire_d"] / 2, (wx, wy, wz), (tipw[0], tipw[1], wz)).fuse(Part.makeSphere(wp["wire_d"] / 2, V(tipw[0], tipw[1], wz)))
    wsh = cyl(2.0, (wx, wy, wz - 0.8), (wx, wy, 64.0)).fuse(cyl(3.0, (wx, wy, wz - 1.0), (wx, wy, wz + 2.0)))
    wcr = box(wx - 1.5, wx + 1.5, wy - 6.5, wy + 1.5, 60.0, 63.0)                 # 机头里的小曲柄（朝 −y，半径 5）
    P["wiper"] = (wire.fuse(wsh).fuse(wcr), "chrome", "steel", "wiper")
    sw = wp["sol"]
    P["wiper_solenoid"] = (cyl(sw["d"] / 2, (sw["x"][0], wy - 5.0, 61.5), (sw["x"][1], wy - 5.0, 61.5)).fuse(
        cyl(1.5, (wx + 1.5, wy - 5.0, 61.5), (sw["x"][0], wy - 5.0, 61.5))).fuse(box(-22.0, -16.0, wy - 8.0, wy - 2.0, 53.0, 54.5)), "graphite", "copper", None)
    # ---- 松线电磁铁：在机臂里拉立轴拨杆上加的第三条臂（朝 +y 10，z 186…190）往 −x
    rl = CT["geo"]["release"]
    sr = GEO["sol_release"]
    pvx, pvy = rl["pivot"][0], rl["pivot"][1]
    tipr = (pvx + sr["arm"][0], pvy + sr["arm"][1])
    rarm = strip([(pvx, pvy), tipr], 6.0, 186.0, 190.0).cut(cyl(2.55, (pvx, pvy, 185.0), (pvx, pvy, 191.0)))
    P["release_arm_t"] = (rarm, "metal", "steel", None)
    P["release_solenoid"] = (cyl(sr["d"] / 2, (sr["x"][0], tipr[1], 188.0), (sr["x"][1], tipr[1], 188.0)).fuse(
        cyl(1.5, (sr["x"][1], tipr[1], 188.0), (tipr[0] - 1.5, tipr[1], 188.0))).fuse(box(47.0, 60.0, -38.0, tipr[1] - 6.0, 184.0, 192.0)), "graphite", "copper", None)
    return P


def build_E():
    P = {}
    es = GEO["estep"]
    my, mz = es["motor_axis"]
    Gy, Gz = FD["geo"]["G"]
    # 42 步进电机（48 mm 长，带磁编码器后盖 12）：机身 x 220…268；轴伸到 x 296；电机板 x 268…272 螺在机座顶板下的两个凸台上
    body = box(220.0, 268.0, my - 21.0, my + 21.0, mz - 21.0, mz + 21.0).fuse(cyl(14.0, (208.0, my, mz), (220.0, my, mz)))
    P["estep_motor"] = (body, "graphite", "copper", None)
    plate = box(268.0, 272.0, my - 24.0, my + 24.0, mz - 24.0, -10.0).cut(cyl(11.5, (267.0, my, mz), (273.0, my, mz)))
    plate = plate.fuse(box(268.0, 282.0, my - 24.0, my + 24.0, -14.0, -10.0))          # 顶上的翻边，两颗 M5 螺在机座顶板下的凸台上
    P["estep_bracket"] = (plate, "metal", "alu", None)
    P["estep_pulley_m"] = (cyl(5.0, (272.0, my, mz), (296.0, my, mz)).fuse(cyl(6.5, (284.0, my, mz), (294.0, my, mz))), "metal", "steel", None)
    # 调节器轴往左伸到 x 283，上面 24 齿带轮（节圆 Ø22.9）；带 HTD 3M、宽 9（只画外形）
    ss = [x for x in FD["settings"] if x["s"] == {"s3": 3.0, "s5": 5.0, "r5": 5.0}[SET] and x["reverse"] == (SET == "r5")][0]
    pul = cyl(4.0, (283.0, Gy, Gz), (297.6, Gy, Gz)).fuse(cyl(11.8, (284.0, Gy, Gz), (294.0, Gy, Gz)))
    key = box(284.0, 294.0, Gy - 1.0, Gy + 1.0, Gz + 9.0, Gz + 11.8)
    key.rotate(V(0, Gy, Gz), V(1, 0, 0), ss["alpha_deg"])
    P["estep_pulley_r"] = (pul.cut(key), "metal", "steel", None)
    # 同步带：两个带轮外切线围成的环（只画外形，厚 1.5）
    def hull(c1, ra, c2, rb, x0, x1):
        d = math.hypot(c2[0] - c1[0], c2[1] - c1[1])
        uy, uz = (c2[0] - c1[0]) / d, (c2[1] - c1[1]) / d
        ny, nz = -uz, uy
        b = math.asin((ra - rb) / d)
        pts = []
        for sgn in (1, -1):
            cy_, sy_ = math.cos(b), math.sin(b)
            dy_, dz_ = sgn * (ny * cy_) + uy * sy_, sgn * (nz * cy_) + uz * sy_
            pts.append(((c1[0] + ra * dy_, c1[1] + ra * dz_), (c2[0] + rb * dy_, c2[1] + rb * dz_)))
        poly = [pts[0][0], pts[0][1], pts[1][1], pts[1][0]]
        w = Part.makePolygon([V(x0, y, z) for y, z in poly] + [V(x0, poly[0][0], poly[0][1])])
        sl = Part.Face(w).extrude(V(x1 - x0, 0, 0))
        return sl.fuse(cyl(ra, (x0, c1[0], c1[1]), (x1, c1[0], c1[1]))).fuse(cyl(rb, (x0, c2[0], c2[1]), (x1, c2[0], c2[1])))
    belt = hull((Gy, Gz), 13.3, (my, mz), 8.0, 285.0, 293.0).cut(hull((Gy, Gz), 11.8, (my, mz), 6.5, 284.0, 294.0))
    P["estep_belt"] = (belt, "graphite", "plastic", None)
    # 倒缝按钮：机头前面、针杆左边（x −40、y −50、z 70）
    P["reverse_button"] = (cyl(5.9, (-30.0, -40.0, 80.0), (-30.0, -56.0, 80.0)).fuse(cyl(8.0, (-30.0, -40.0, 80.0), (-30.0, -36.0, 80.0))), "graphite", "plastic", None)
    return P


def build():
    P = {}
    if "T" in OPT:
        P.update(build_T())
    if "E" in OPT:
        P.update(build_E())
    return P
