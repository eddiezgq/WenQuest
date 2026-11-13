"""WQ-LS 压脚与操纵件（第 138 轮 G4.7），由 cad/mech.py 调用：build() 返回 {零件名: (实体, 显示材料, 密度键, 运动类别)}。

尺寸来自 tools/wqls/g4_ctrl.py 的结果（docs/设计/WQ-LS/G4/操纵件.json 的 geo）。
状态（环境变量）：
  WQ_PRESS = down（压脚放下，默认）| hand（手抬 5.5）| knee（膝抬 13）
  WQ_FEED  = s3 | s5 | r5（针距旋钮、倒缝扳手、拉杆的位置跟着这一档的调节器角）
运动类别：'press' 随压脚上下（压脚放下时，一转里被送布牙顶起，g4_mech.py 给出）；None 不动（这一状态下的位置）。
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
CT = json.load(open(os.path.join(G4, "操纵件.json"), encoding="utf-8"))
FD = json.load(open(os.path.join(G4, "送布机构.json"), encoding="utf-8"))
GEO = CT["geo"]
PRESS = os.environ.get("WQ_PRESS", "down")
SET = os.environ.get("WQ_FEED", "s3")
LIFT = dict(down=0.0, hand=5.5, knee=13.0)[PRESS]
DEG = math.pi / 180
RHO = dict(steel=7.85e-6, alu=2.75e-6, plastic=1.2e-6)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, a, b):
    a, b = V(*a), V(*b)
    return Part.makeCylinder(r, (b - a).Length, a, b - a)


def bar_xz(a, b, w, y0, y1):
    """x–z 平面里的杆：a、b 为 (x, z)，宽 w，厚 y0…y1，两端圆头"""
    (x0, z0), (x1, z1) = a, b
    L = math.hypot(x1 - x0, z1 - z0)
    s = Part.makeBox(L, y1 - y0, w, V(0, y0, -w / 2))
    s.rotate(V(0, 0, 0), V(0, -1, 0), math.degrees(math.atan2(z1 - z0, x1 - x0)))
    s.translate(V(x0, 0, z0))
    return s.fuse(cyl(w / 2, (x0, y0, z0), (x0, y1, z0))).fuse(cyl(w / 2, (x1, y0, z1), (x1, y1, z1)))


def rot_y(p, c, ang):
    """x–z 平面里绕 c 逆时针（x → z）转 ang（rad）"""
    dx, dz = p[0] - c[0], p[1] - c[1]
    return (c[0] + dx * math.cos(ang) - dz * math.sin(ang), c[1] + dx * math.sin(ang) + dz * math.cos(ang))


def setting():
    st = {"s3": (3.0, False), "s5": (5.0, False), "r5": (5.0, True)}[SET]
    s = [x for x in FD["settings"] if x["s"] == st[0] and x["reverse"] == st[1]][0]
    return st[0], st[1], s["alpha_deg"]


def build():
    P = {}
    g = GEO
    b, br = g["bar"], g["bracket"]
    L = LIFT
    # ---------------------------------------------------------------- ① 压脚组（随压脚上下：类别 'press'）
    bx, by = b["x"], b["y"]
    # 压脚杆做成空心（Ø8 × Ø4.5）：压脚组运动质量由 125 g 降到约 104 g，出厂 50 N 时 5000 r/min 压脚不跳（g4_ctrl.py ①）
    P["presser_bar"] = (cyl(b["d"] / 2, (bx, by, b["z"][0] + L), (bx, by, b["z"][1] + L)).cut(
        cyl(b["bore"] / 2, (bx, by, b["z"][0] - 1 + L), (bx, by, b["z"][1] + 1 + L))), "chrome", "steel", "press")
    c = g["collar"]
    P["presser_collar"] = (cyl(c["r"], (bx, by, c["z"][0] + L), (bx, by, c["z"][1] + L)).cut(              # 弹簧座：套在压脚杆顶端，紧定螺钉
        cyl(b["d"] / 2, (bx, by, c["z"][0] - 1 + L), (bx, by, c["z"][1] + 1 + L))), "metal", "steel", "press")
    f = g["foot"]
    sx0, sx1, sy0, sy1, sz0, sz1 = f["sole"]
    sole = box(sx0, sx1, sy0, sy1, sz0 + L, sz1 + L)
    sole = sole.fuse(box(sx0, sx1, sy0 - 4.0, sy0 + 0.01, sz0 + 1.5 + L, sz1 + 1.5 + L))                      # 前端翘起
    sole = sole.cut(cyl(2.4, (0, 0, -1 + L), (0, 0, 5 + L)))                                                   # 针孔 Ø4.8
    shank = box(*f["shank"][:4], f["shank"][4] + L, f["shank"][5] + L)
    shank = shank.fuse(box(sx0, sx0 + 6.0, -2.0, 2.0, sz1 - 0.5 + L, f["shank"][4] + 0.5 + L))                 # 铰接耳（销沿 x）
    shank = shank.cut(cyl(b["d"] / 2 + 0.05, (bx, by, b["z"][0] - 0.1 + L), (bx, by, f["shank"][5] + 1 + L)))
    P["presser_foot"] = (sole.fuse(shank), "metal", "steel", "press")
    z0, z1 = br["z"][0] + L, br["z"][1] + L
    bk = box(*br["body"], z0, z1)
    ca = br["cam_arm"]
    bk = bk.fuse(box(ca[0], br["body"][0] + 0.01, ca[2], ca[3], z0, z0 + 4.0)).fuse(box(br["body"][0] - 4.0, br["body"][0] + 0.01, br["body"][3] - 0.01, ca[3], z0, z0 + 4.0))
    ha = br["hook_arm"]
    bk = bk.fuse(box(ha[0], ha[1], ha[2], ha[3], z0, z0 + 4.0))
    rt = br["rel_tab"]
    bk = bk.fuse(box(rt[0], rt[1], rt[2], rt[3], z1 - 3.0, z1))
    bk = bk.cut(cyl(b["d"] / 2 + 0.05, (bx, by, z0 - 1), (bx, by, z1 + 1)))
    P["lift_bracket"] = (bk, "metal", "steel", "press")
    # 不随压脚动的：上下导套、调压螺钉、压脚弹簧（按这一状态的长度画）
    gl, gu = g["guide_low"], g["guide_up"]
    bush = cyl(gl["d_bush"] / 2, (bx, by, gl["z"][0]), (bx, by, gl["z"][1])).fuse(cyl(gu["d_bush"] / 2, (bx, by, gu["z"][0]), (bx, by, gu["z"][1])))
    bush = bush.cut(cyl(b["d"] / 2 + 0.02, (bx, by, 0), (bx, by, 200)))
    P["presser_bushes"] = (bush, "brass", "steel", None)
    sp = CT["presser"]["spring"]
    seat = c["z"][1] + L
    top = sp["screw_bottom_z_20N"] - (50.0 - 20.0) / sp["k_Nmm"]          # 调压螺钉底面：出厂调到 50 N
    P["presser_spring"] = (cyl(sp["D_mm"] / 2 + sp["wire_mm"] / 2, (bx, by, seat), (bx, by, top)).cut(
        cyl(sp["D_mm"] / 2 - sp["wire_mm"] / 2, (bx, by, seat - 1), (bx, by, top + 1))), "metal", "steel", None)
    scr = g["screw"]
    P["presser_screw"] = (cyl(scr["d"] / 2, (bx, by, top), (bx, by, scr["boss_z"][1] + 8)).fuse(
        cyl(scr["d"] / 2 + 2.5, (bx, by, scr["boss_z"][1] + 8), (bx, by, scr["boss_z"][1] + 14))).cut(
        cyl(5.0, (bx, by, top - 1), (bx, by, scr["boss_z"][1] + 2))), "metal", "steel", None)
    # ---------------------------------------------------------------- ② 手抬：轴、偏心凸轮、扳手（这一状态的转角）
    h = g["hand"]
    th = (h["theta_up"] if PRESS == "hand" else h["theta_rest"]) * DEG
    hz = CT["hand"]["shaft_z"]
    ecx, ecz = h["x"] + h["e"] * math.sin(th), hz + h["e"] * math.cos(th)
    cam = cyl(h["rho"], (ecx, h["y"][0], ecz), (ecx, h["y"][1], ecz))
    shaft = cyl(4.0, (h["x"], h["y"][0], hz), (h["x"], h["y_out"] + 6.0, hz))
    lv_dir = (math.sin(th + 90 * DEG), math.cos(th + 90 * DEG))         # 扳手：放下时朝下，扳起 90° 后朝 +x
    lv_end = (h["x"] + h["lever"] * lv_dir[0], hz + h["lever"] * lv_dir[1])
    lever = bar_xz((h["x"], hz), lv_end, 8.0, h["y_out"], h["y_out"] + 6.0)
    P["hand_lifter"] = (cam.fuse(shaft).fuse(lever), "graphite", "steel", None)
    # ---------------------------------------------------------------- ③ 膝抬
    k = g["knee"]
    KN = CT["knee"]
    b2, b1 = KN["C2_turn_deg"] * DEG, KN["C1_turn_deg"] * DEG
    a2 = (b2 / 2) if PRESS == "knee" else -b2 / 2
    a1 = (b1 / 2) if PRESS == "knee" else -b1 / 2
    yk = k["y"]
    c2, c1 = k["C2"], k["C1"]
    p2 = (c2["x"], c2["z"])
    t2h = rot_y((c2["x"] + c2["side"], c2["z"]), p2, a2)
    t2v = rot_y((c2["x"], c2["z"] + c2["up"]), p2, a2)
    C2 = bar_xz(p2, t2h, 8.0, yk - 3, yk + 3).fuse(bar_xz(p2, t2v, 8.0, yk - 3, yk + 3)).fuse(cyl(3.0, (p2[0], yk - 3, p2[1]), (p2[0], yk + 20, p2[1])))   # 转轴销伸进机头后壁的凸台
    P["knee_c2"] = (C2, "metal", "steel", None)
    p1 = (c1["x"], c1["z"])
    t1h = rot_y((c1["x"] + c1["side"], c1["z"]), p1, a1)
    t1v = rot_y((c1["x"], c1["z"] + c1["up"]), p1, a1)
    C1 = bar_xz(p1, t1h, 8.0, yk - 3, yk + 3).fuse(bar_xz(p1, t1v, 8.0, yk - 3, yk + 3)).fuse(cyl(3.0, (p1[0], yk - 3, p1[1]), (p1[0], yk + 20, p1[1])))   # 转轴销伸进立柱后壁的凸台
    P["knee_c1"] = (C1, "metal", "steel", None)
    # 机臂里的水平推杆：两端叉头夹在角杠杆竖臂端的两边（y ±3 之外，厚 2）
    rodp = cyl(k["arm_rod_d"] / 2, (t2v[0] + 7, yk, t2v[1]), (t1v[0] - 7, yk, t1v[1]))
    for tp, sg in ((t2v, 1), (t1v, -1)):
        xa, xb = sorted((tp[0] - 6 * sg, tp[0] + 8 * sg))
        rodp = rodp.fuse(box(xa, xb, yk - 5.0, yk - 3.2, tp[1] - 4, tp[1] + 4)).fuse(box(xa, xb, yk + 3.2, yk + 5.0, tp[1] - 4, tp[1] + 4))
        xc, xd = sorted((tp[0] + 5 * sg, tp[0] + 8 * sg))
        rodp = rodp.fuse(box(xc, xd, yk - 5.0, yk + 5.0, tp[1] - 4, tp[1] + 4))                    # 叉头的底（离竖臂端 1）
        rodp = rodp.fuse(cyl(2.9, (tp[0], yk - 5, tp[1]), (tp[0], yk + 5, tp[1])))
    P["knee_rod"] = (rodp, "metal", "steel", None)
    # 立柱里的推杆：顶端顶在 C1 水平臂端的下面（滚轮略去，顶头 Ø10）
    pz1 = t1h[1] - 4.0
    push = cyl(k["push"]["d"] / 2, (t1h[0], yk, k["push"]["z"][0] + (pz1 - c1["z"] + 4.0)), (t1h[0], yk, pz1 - 2.0)).fuse(
        cyl(5.0, (t1h[0], yk, pz1 - 2.0), (t1h[0], yk, pz1)))
    push = push.fuse(cyl(7.0, (t1h[0], yk, -14.0 + (pz1 - c1["z"] + 4.0)), (t1h[0], yk, -10.0 + (pz1 - c1["z"] + 4.0))))   # 自动抬压脚电磁铁的接口（挡圈，在机座顶板下面）
    P["knee_push"] = (push, "metal", "steel", None)
    # 机头里的拉杆：上端挂在 C2 水平臂端，下端的钩托在抬压脚块钩臂下面（放下时贴着；手抬时抬压脚块离开钩）
    hz0 = g["bracket"]["z"][0] + (13.0 if PRESS == "knee" else 0.0)
    yl = yk - 6.0                                                        # 拉杆在 C2 板前面（C2 板 y 39…45）
    lnk = cyl(2.5, (t2h[0], yl, t2h[1]), (t2h[0], yl, hz0 - 2.0))
    lnk = lnk.fuse(box(t2h[0] - 4.0, t2h[0] + 4.0, yl - 4.0, yl + 4.0, hz0 - 4.0, hz0 - 0.0))
    lnk = lnk.fuse(cyl(2.0, (t2h[0], yl, t2h[1]), (t2h[0], yk + 1.0, t2h[1])))               # 挂在 C2 臂端的销
    P["knee_link"] = (lnk, "metal", "steel", None)
    # ---------------------------------------------------------------- ④ 松线：轴（两臂）、推杆、立轴拨杆
    r = g["release"]
    rx, rz, ry0, ry1 = r["shaft"]
    rth = CT["release"]["theta_deg"][{0.0: "0.0", 5.5: "5.5", 13.0: "13.0"}[L]] * DEG     # g4_ctrl.release_angle（到顶后空行程）
    tab_tip = rot_y(tuple(r["tip"]), (rx, rz), rth)
    rod_tip = rot_y((rx, rz - r["a_rod"]), (rx, rz), rth)
    rs = cyl(3.0, (rx, ry0, rz), (rx, 4.0, rz))                         # 轴装在压脚杆上导套座伸出的耳子里（y −7…4）；不能伸到后壁：膝抬 C2 的臂扫过这里
    rs = rs.fuse(bar_xz((rx, rz), tab_tip, 5.0, -13.0, -9.0)).fuse(bar_xz((rx, rz), rod_tip, 5.0, ry0, ry0 + 4.0))   # 长臂在 y −13…−9（让开针杆连接块 y ≥ −7）
    P["release_shaft"] = (rs, "metal", "steel", None)
    s_rod = rod_tip[0] - rx
    ry_rod, rz_rod, rx_end = r["rod"]
    P["release_rod"] = (cyl(1.5, (rod_tip[0], ry_rod, rod_tip[1]), (rx_end + s_rod, ry_rod, rz_rod)), "metal", "steel", None)
    px, py, pz0, pz1_ = r["pivot"]
    ang = s_rod / abs(r["r_rod"][1])                                     # 立轴拨杆的转角（绕 z，逆时针为正）
    def rz_(v):                                                          # noqa: E306
        return (v[0] * math.cos(ang) - v[1] * math.sin(ang), v[0] * math.sin(ang) + v[1] * math.cos(ang))
    lo, hi = rz_(r["r_rod"]), rz_(r["r_pin"])
    lev = cyl(3.0, (px, py, 158.0), (px, py, pz1_))                      # 下端插在机臂底板的座里
    for (vx, vy), zz in ((lo, rz_rod), (hi, g["tension"]["z"])):
        d_ = cyl(2.5, (px, py, zz), (px + vx, py + vy, zz))
        lev = lev.fuse(d_).fuse(cyl(2.5, (px + vx, py + vy, zz - 2.5), (px + vx, py + vy, zz + 2.5)))
    P["release_lever"] = (lev, "metal", "steel", None)
    # ---------------------------------------------------------------- ⑥ 夹线器、挑线簧（机臂前面，x 66、z 210）
    t = g["tension"]
    tx, tz, yw = t["x"], t["z"], t["y_wall"]
    open_ = CT["tension"]["release_open_mm"]["lift_13"] if PRESS == "knee" else (CT["tension"]["release_open_mm"]["lift_5_5"] if PRESS == "hand" else 0.0)
    post = cyl(t["post_d"] / 2, (tx, yw + 6.0, tz), (tx, yw - 22.0, tz))
    P["tension_post"] = (post.cut(cyl(1.05, (tx, yw + 7, tz), (tx, yw - 23, tz))), "chrome", "steel", None)
    P["release_pin"] = (cyl(1.0, (tx, py + hi[1] - 2.5, tz), (tx, yw - 6.0 - open_, tz)), "metal", "steel", None)
    discs = cyl(t["disc_d"] / 2, (tx, yw - 6.0 - open_, tz), (tx, yw - 7.0 - open_, tz)).fuse(cyl(t["disc_d"] / 2, (tx, yw - 7.4 - open_, tz), (tx, yw - 8.4 - open_, tz)))
    P["tension_discs"] = (discs.cut(cyl(t["post_d"] / 2 + 0.1, (tx, yw, tz), (tx, yw - 20, tz))), "chrome", "steel", None)
    tsp = CT["tension"]["spring"]
    P["tension_spring"] = (cyl(tsp["D_mm"] / 2 + tsp["wire_mm"] / 2, (tx, yw - 8.5 - open_, tz), (tx, yw - 18.0, tz)).cut(
        cyl(tsp["D_mm"] / 2 - tsp["wire_mm"] / 2, (tx, yw - 8, tz), (tx, yw - 19, tz))), "metal", "steel", None)
    P["tension_nut"] = (cyl(9.0, (tx, yw - 18.0, tz), (tx, yw - 26.0, tz)).cut(cyl(t["post_d"] / 2, (tx, yw - 17, tz), (tx, yw - 27, tz))), "graphite", "plastic", None)
    cs = Part.makeTorus(9.0, 0.35, V(tx, yw - 3.5, tz), V(0, -1, 0)).fuse(cyl(0.35, (tx - 9.0, yw - 3.5, tz), (tx - 9.0 - 10.6, yw - 3.5, tz + 10.6)))
    P["check_spring"] = (cs, "chrome", "steel", None)
    # 机头前面下沿的过线环（钢丝 Ø1，环内径 3，用 M3 螺钉装在机头前壁下沿 z 50 处）：面线从过线点 B 下来，经它拐到针杆线钩
    gd = Part.makeTorus(2.0, 0.5, V(0.0, -51.0, 44.0), V(0, 0, 1)).fuse(cyl(0.5, (0.0, -49.0, 44.0), (0.0, -48.5, 44.0))).fuse(
        box(-3.0, 3.0, -48.5, -46.5, 42.0, 50.0))
    P["thread_guide"] = (gd, "chrome", "steel", None)
    # ---------------------------------------------------------------- ⑤ 针距旋钮、拉杆、倒缝扳手、拉簧（这一档的位置）
    s_, rev, alpha = setting()
    dl, ra, pr, rv = g["dial"], g["reg_arm"], g["pull_rod"], g["reverse"]
    groove = CT["dial"]["groove"]
    dz = -ra["len"] * math.sin(alpha * DEG)                               # 拉杆位移（向上为正）
    th_set = dl["turn_deg"] * s_ / 5
    # 旋钮：外面的钮（G3 位置）、轴、里面的槽轮（端面环形槽，槽底在 y −48）
    yk0, yk1 = dl["y_cam"]
    knob = cyl(19.0, (dl["x"], -63.0, dl["z"]), (dl["x"], -73.0, dl["z"])).fuse(cyl(4.0, (dl["x"], yk0, dl["z"]), (dl["x"], -63.0, dl["z"])))
    disc = cyl(32.0, (dl["x"], yk0, dl["z"]), (dl["x"], yk1, dl["z"]))
    pts_o, pts_i = [], []
    for s_g, th_g, ro, ri in zip(groove["s"], groove["theta_deg"], groove["r_out"], groove["r_in"]):
        phi = (-90.0 - th_g + th_set) * DEG
        pts_o.append(V(dl["x"] + ro * math.cos(phi), yk1 + 0.01, dl["z"] + ro * math.sin(phi)))
        pts_i.append(V(dl["x"] + ri * math.cos(phi), yk1 + 0.01, dl["z"] + ri * math.sin(phi)))
    poly = Part.makePolygon(pts_o + pts_i[::-1] + [pts_o[0]])
    gr = Part.Face(poly).extrude(V(0, -4.0, 0))
    for (po, pi) in ((pts_o[0], pts_i[0]), (pts_o[-1], pts_i[-1])):                  # 槽两端倒圆
        mid = (po + pi) * 0.5
        gr = gr.fuse(Part.makeCylinder((po - pi).Length / 2, 4.0, V(mid.x, yk1 + 0.01, mid.z), V(0, -1, 0)))
    disc = disc.cut(gr)
    P["stitch_dial"] = (knob.fuse(disc), "graphite", "steel", None)
    # 调节器臂端（拉杆下端销）：调节器板上那条臂由 feed.py 画（随调节器）；这里只算位置
    ay, az = -ra["len"] * math.cos(alpha * DEG), FD["geo"]["G"][1] - ra["len"] * math.sin(alpha * DEG)
    xr = pr["x"]
    top_z = pr["top_z"] + dz
    rod = cyl(pr["d"] / 2, (xr, ay, az + 4.0), (xr, pr["y"], top_z)).fuse(cyl(4.0, (xr - 2.0, ay, az), (xr + 2.0, ay, az))).cut(
        cyl(2.05, (xr - 3, ay, az), (xr + 3, ay, az)))
    lx, ly, lz = pr["lug"]
    lz += dz
    rod = rod.fuse(box(xr, lx, ly - 1.5, ly + 1.5, lz - 3.0, lz + 3.0)).fuse(box(xr - 0.5, xr + 0.5, ly - 1.5, pr["y"], lz - 3, lz + 3))
    rod = rod.fuse(cyl(2.0, (lx, ly - 1.5, lz), (lx, ly - 6.0, lz)))                      # 耳子上的销（插在倒缝曲柄的槽里）
    # 上端横臂和销：销在旋钮轴正下方，插进槽里
    pin_z = dl["z"] - dl["r0"] + dz
    arm = cyl(2.5, (xr, pr["y"], top_z), (dl["x"], -42.0, pin_z)).fuse(cyl(3.0, (dl["x"], -42.0, pin_z), (dl["x"], -40.0, pin_z)))
    arm = arm.fuse(cyl(dl["rp"], (dl["x"], -42.0, pin_z), (dl["x"], yk1 - 3.5, pin_z)))
    rod = rod.fuse(arm)
    sy0 = pr["y"]
    rod = rod.fuse(box(xr - 1.0, xr + 1.0, g["spring_rev"]["top"][1] - 1.0, sy0, g["spring_rev"]["top"][2] + dz - 2.0, g["spring_rev"]["top"][2] + dz + 2.0))
    P["pull_rod"] = (rod, "metal", "steel", None)
    # 倒缝扳手：轴（沿 y，前壁外 y −70 到里面 y_in）、里面的曲柄（带槽，拨拉杆耳子上的销）、外面的扳手（朝下）
    q = (rv["x"], rv["z"])
    ang_c = math.atan2(lz - rv["z"], lx - rv["x"]) - math.pi                               # 曲柄指向 −x 时为 0
    ctip = rot_y((rv["x"] - rv["crank"] - 4.0, rv["z"]), q, ang_c)
    crank = bar_xz(q, ctip, 9.0, rv["y_in"] - 4.0, rv["y_in"])
    slot = bar_xz(rot_y((rv["x"] - rv["crank"] + 3.5, rv["z"]), q, ang_c), rot_y((rv["x"] - rv["crank"] - 3.5, rv["z"]), q, ang_c), 4.1, rv["y_in"] - 5, rv["y_in"] + 1)
    crank = crank.cut(slot)
    shaft = cyl(4.0, (rv["x"], rv["y_in"] - 4.0, rv["z"]), (rv["x"], -72.0, rv["z"]))
    hd = rot_y((rv["x"], rv["z"] - rv["handle"]), q, ang_c)
    handle = bar_xz(q, hd, 10.0, -76.0, -68.0).fuse(cyl(7.0, (rv["x"], -68.0, rv["z"]), (rv["x"], -76.0, rv["z"])))
    P["reverse_lever"] = (crank.fuse(shaft).fuse(handle), "graphite", "steel", None)
    # 拉簧：拉杆上的挂耳 → 立柱前横隔板（z 62）上的孔
    st_, an_ = g["spring_rev"]["top"], g["spring_rev"]["anchor"]
    P["reverse_spring"] = (cyl(2.5, (xr, st_[1], st_[2] + dz - 2.0), (xr, an_[1], an_[2] + 1.0)).cut(
        cyl(1.8, (xr, st_[1], st_[2] + dz - 3.0), (xr, an_[1], an_[2]))), "metal", "steel", None)
    return P
