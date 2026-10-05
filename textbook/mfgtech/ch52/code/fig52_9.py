"""52.9 节的三维图：画总图的顺序（图 52.9.1）、夹具体的三种做法（图 52.9.4）、防错挡块（图 52.9.5，假设键槽不对称时）、
总图技术要求落在三维模型上的位置（图 52.9.6）、V 形块与对刀块的零件图（图 52.9.7、52.9.8）。模型：factory/digital/models3d（JJ-301-50 与 SH-301 取自数字工厂的数据）。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A, P = C.Assembly, C.Part
g = J.geometry()
zc = g["zc"]

# ---- 图 52.9.1：画总图的顺序：工件（双点画线）→ 定位元件 → 夹紧装置 → 对刀、连接元件和夹具体
base = J.assembly("op40")
names = [p.name for p in base.parts]
groups = [["工件 SH-301"], ["V 形块", "轴向挡板"],
          [n for n in names if n[:2] in ("压板", "可调", "螺柱", "垫圈", "弹簧")],
          [n for n in names if n not in ("工件 SH-301", "V 形块", "轴向挡板") and n[:2] not in ("压板", "可调", "螺柱", "垫圈", "弹簧")]]
cam = {"dir": M.ISO, "fit": [[-95, -70, -40], [190, 105, 110]], "zoom": 1.12}
panels = []
for k in range(4):
    show = sum(groups[:k + 1], [])
    st = {"parts": {n: {"visible": n in show} for n in names}}
    st["parts"]["工件 SH-301"]["opacity"] = 0.35 if k < 3 else 1.0
    for n in groups[k]:
        if n != "工件 SH-301":
            st["parts"][n]["opacity"] = 1.0
    panels.append(R.render_png(base, 700, 500, camera=cam, state=st))
R.compose("fig52_9_1", panels, 2, titles=["(a) 先画工件（总图上用双点画线），放在加工位置", "(b) 按定位方案画定位元件：V 形块、轴向挡板",
                                         "(c) 画夹紧装置：压板、螺柱、可调支承、弹簧", "(d) 画对刀块、定位键，最后用夹具体把它们连起来"])

# ---- 图 52.9.4：夹具体的三种做法（同一个角铁式夹具体：底板 + 立板 + 两块筋板）
def body(kind):
    q = A(kind)
    base_ = S.box(-100, 100, -60, 60, 0, 22)
    wall = S.box(-100, 100, 20, 42, 22, 150)
    ribs = [S.prism("yz", [(-40, 22), (20, 22), (20, 110)], x0, x0 + 14) for x0 in (-75, 61)]
    ears = []
    for x0, xc, xo in ((-126, -113, -127), (100, 113, 127)):          # U 形耳座：槽口朝外
        ears.append(S.box(x0, x0 + 26, -30, 30, 0, 16) - S.cyl("z", (xc, 0), 7, -1, 17) - S.box(min(xc, xo), max(xc, xo), -7, 7, -1, 17))
    if kind == "cast":
        s = base_ + wall
        for r in ribs + ears:
            s = s + r
        s = s - S.box(-60, 60, -45, 5, -1, 8)                     # 底面中间挖空（减少加工面）
        q.add(P("铸铁夹具体（HT200，一次铸出，时效后加工）", s, "cast"))
    elif kind == "weld":
        q.add(P("底板", base_, "steel"))
        q.add(P("立板", wall, "steel"))
        for i, r in enumerate(ribs):
            q.add(P(f"筋板{i + 1}", r, "steel"))
        bead = S.prism("yz", [(20, 22), (13, 22), (20, 29)], -100, 100) + S.prism("yz", [(42, 22), (49, 22), (42, 29)], -100, 100)
        for x0 in (-75, 61):
            bead = bead + S.prism("xy", [(x0, -40), (x0 - 5, -40), (x0, 20)], 22, 27) + S.prism("xy", [(x0 + 14, -40), (x0 + 19, -40), (x0 + 14, 20)], 22, 27)
        q.add(P("焊缝", bead, "#8a6f5a"))
        for i, e in enumerate(ears):
            q.add(P(f"耳板{i + 1}", e, "steel"))
    else:
        q.add(P("底板", base_, "steel"))
        q.add(P("立板", wall, "steel"))
        for i, r in enumerate(ribs):
            q.add(P(f"筋板{i + 1}", r, "steel"))
        sc = None
        for x in (-80, -30, 30, 80):                               # 立板由底面向上拧入 4 个螺钉，2 个销钉定位
            s1 = S.screw("z", (x, 31), 10, 10, 60, head_dir=-1)
            sc = s1 if sc is None else sc + s1
        q.add(P("螺钉", S.move(sc, 0, 0, -10), "steel_dark"))
        q.add(P("圆柱销", S.cyl("z", (-55, 31), 4, -0.5, 40) + S.cyl("z", (55, 31), 4, -0.5, 40), "hardened"))
        q.add(P("耳座（螺钉连接）", ears[0] + ears[1], "steel"))
    return q
bc = {"dir": [0.9, -1.3, 0.75]}
bc_low = {"dir": [0.9, -1.3, -0.55]}
R.compose("fig52_9_4", [R.render_png(body("cast"), 620, 470, camera=bc), R.render_png(body("weld"), 620, 470, camera=bc),
                        R.render_png(body("asm"), 620, 470, camera=bc_low)], 3,
          titles=["(a) 铸造：吸振好、尺寸稳定，适合定型的大批量夹具", "(b) 焊接：钢板下料焊成，周期短，焊后退火", "(c) 装配：螺钉连接、销钉定位（从下面看），最快、便于修改"])

# ---- 图 52.9.5：防错挡块（假设键槽偏向一端、工件调头装就会铣错时）：左端 Ø30 下方设挡块，顶面离轴线 16.3
# 正确放置时左边是 Ø30（半径 15），离挡块 1.3 mm；调头后左边变成 Ø35.3（半径 17.65），压在挡块上，工件放不进 V 形块
r_pin = 16.3
pin_x = (-21, -15)                     # 离齿轮位左端面 15–21 mm：在 Ø30 段（12 mm 以外）和调头后的 Ø35.3 段（25 mm 以内）中间
def ep(rev):
    q = J.assembly("op40")
    q.parts = [p for p in q.parts if p.number in (1, 3, 4) or p.name.startswith("工件")]
    w = next(p for p in q.parts if p.name.startswith("工件"))
    if rev:
        sh = W.sh301("op40").shape
        L = 167.0
        sh = S.rot(sh, 0, 0, 180, about=(L / 2, 0, 0))
        # 调头后左轴承位 Ø35.3 长 25 落在挡块上，工件被顶起 17.65 − 16.3 = 1.35 mm，贴不到 V 形块上
        w.shape = S.move(sh, g["work_x0"] - 3.0, 0, zc + 35.3 / 2 - r_pin)
        w.color = "red"
    q.add(P("防错挡块", S.box(pin_x[0], pin_x[1], -6, 6, 0, zc - r_pin), "green"))
    return q
ec = {"dir": [0.15, -1.0, 0.25], "fit": [[-95, -20, -10], [125, 20, 85]]}
sec = ((0, 0, 0), (0, -1, 0))
pa = R.render_png(ep(False), 700, 380, camera=ec, section=sec)
pb = R.render_png(ep(True), 700, 380, camera=ec, section=sec)
zc_ = {"dir": [0.0, -1.0, 0.0], "fit": [[-42, 0, zc - 32], [16, 0, zc - 4]]}
pc = R.render_png(ep(False), 700, 420, camera=zc_, section=sec,
                  labels=[{"at": (-20, 0, zc - r_pin - 4), "text": "防错挡块：顶面离轴线 16.3", "style": "text", "pos": [0.3, 0.9]},
                          {"at": (-20, 0, zc - 15.6), "text": "Ø30（半径 15）：离挡块 1.3 mm", "style": "text", "pos": [0.32, 0.1]}])
pd = R.render_png(ep(True), 700, 420, camera=zc_, section=sec,
                  labels=[{"at": (-20, 0, zc - r_pin + 0.3), "text": "调头后这里是 Ø35.3（半径 17.65）：压在挡块上", "style": "text", "pos": [0.4, 0.1]}])
R.compose("fig52_9_5", [pa, pb, pc, pd], 2, titles=["(a) 方向正确：工件落到 V 形块上", "(b) 调头：被挡块顶住，装不进去",
                                                  "(c) (a) 的挡块处放大", "(d) (b) 的挡块处放大：工件被顶起 1.35 mm，落不到 V 形块上"])

# ---- 图 52.9.6：总图技术要求在三维模型上的位置（序号与图 52.1.5 的技术要求一致）
t = J.assembly("op40", with_work=False)
t.add(P("检验棒 Ø40.3", S.cyl("x", (0, zc), 40.3 / 2, -40, 100), "glass", opacity=0.8))
side, top = g["setting_side"], g["setting_top"]
reqs = [((30, 14.2, 34.2), "①② V 形块对称面 ∥ 定位键侧面、⊥ 底面", "V 形块"), ((45, -40, 42), "③ V 形块工作面轴线 ∥ 底面", "V 形块"),
        ((147, side - 0.3, top + 10), "④ 对刀块侧面到 V 形块对称面 9 ± 0.005", "对刀块"), ((147, 0, top), "⑤ 对刀块底面高度 40.38 ± 0.01", "对刀块"),
        ((8, -40, 30), "⑥ 定位元件硬度、磨损更换界限", "V 形块")]
pos = [[0.42, 0.06], [0.3, 0.8], [0.75, 0.08], [0.82, 0.3], [0.25, 0.55]]
R.figure3d("fig52_9_6", t, 1400, 900, camera={"dir": M.ISO, "fit": [[-95, -70, -40], [190, 105, 90]]},
           labels=[{"at": a, "text": s, "style": "text", "pos": p, "part": n} for (a, s, n), p in zip(reqs, pos)]
           + [{"at": (90, -15, zc - 5), "text": "⑦ 检验棒 Ø40.3 放在 V 形块上验收（图 52.10.1）", "style": "text", "pos": [0.55, 0.95], "part": "检验棒 Ø40.3"}])

# ---- 图 52.9.7、52.9.8：两张非标准零件图（由同一个三维模型投影，factory/digital/drawings/jj30150_parts.py）
from drawings import jj30150_parts as DP  # noqa: E402
R.save_svg("fig52_9_7", DP.vblock_sheet().svg())
R.save_svg("fig52_9_8", DP.setting_block_sheet().svg())
out(n_fig3d=4, r_pin=r_pin, r_big=35.3 / 2, lift=35.3 / 2 - r_pin, gap_ok=r_pin - 15.0, T_v=zc, sb_top=g["setting_top"], sb_w=g["setting_side"] + 12)
