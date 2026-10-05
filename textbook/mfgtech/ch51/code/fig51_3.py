"""51.3 节的三维图：用真实的定位元件实现 3–2–1 定位（图 51.3.2）、常用定位元件相当于几个支承点（图 51.3.3）。
模型：factory/digital/models3d（支承钉、V 形块、定位销、心轴、顶尖见 elements.py；JJ-301-50 取自夹具数据）。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A, P = C.Assembly, C.Part
g = J.geometry()
blue, orange, red = "#4f7fb8", "#d98c3a", "#c0504d"

# ---- 图 51.3.2：(a) 长方体工件在 6 个支承钉上：底面 3 个、侧面 2 个、端面 1 个；(b) SH-301 在 JJ-301-50 上：V 形块 4 点、挡板 1 点
BL, BB, BH = 160.0, 90.0, 50.0
def six_point(with_work=True, show=(3, 2, 1)):
    q = A("六点定位")
    q.add(P("夹具体", S.box(-30, BL + 20, -20, BB + 10, -30, -10) + S.box(-30, -14, -20, BB + 10, -10, 70) + S.box(-30, BL + 20, BB + 10, BB + 26, -30, 70), "cast"))
    pins_b = [(25, 18), (BL - 25, 18), (BL / 2, BB - 18)]
    for i, (x, y) in enumerate(pins_b):
        q.add(P(f"底面支承钉{i + 1}", E.support_pin("A", 12, 10, at=(x, y, 0)), blue))
    for i, x in enumerate((25, BL - 25)):                 # 侧面两个（后面 y = BB），钉头朝 −y
        pin = S.rot(E.support_pin("A", 12, 10, at=(0, 0, 0)), 90, 0, 0)
        q.add(P(f"侧面支承钉{i + 1}", S.move(pin, x, BB, 25), orange))
    pin = S.rot(E.support_pin("A", 12, 10, at=(0, 0, 0)), 0, -90, 0)  # 端面一个（左 x = 0），钉头朝 +x
    q.add(P("端面支承钉", S.move(pin, 0, BB / 2, 25), red))
    if with_work:
        q.add(P("工件（长方体）", S.box(0, BL, 0, BB, 0, BH), "work_cut", opacity=0.4))
    return q
pa = R.render_png(six_point(), 760, 560, camera={"dir": [0.75, -1.3, 0.9]},
                  labels=[{"at": (BL / 2, BB - 18, 0), "text": "底面 3 个：z、绕 x、绕 y", "style": "text", "pos": [0.65, 0.92], "part": "底面支承钉3"},
                          {"at": (BL - 25, BB, 25), "text": "侧面 2 个：y、绕 z", "style": "text", "pos": [0.78, 0.12], "part": "侧面支承钉2"},
                          {"at": (0, BB / 2, 25), "text": "端面 1 个：x", "style": "text", "pos": [0.12, 0.15], "part": "端面支承钉"}])
jb = J.assembly("op40")
jb.parts = [p for p in jb.parts if p.number in (1, 3, 4) or p.name.startswith("工件")]
for p in jb.parts:
    if p.number == 3:
        p.color = blue
    if p.number == 4:
        p.color = red
    if p.name.startswith("工件"):
        p.opacity = 0.7; p.color = "work_cut"
pb = R.render_png(jb, 760, 560, camera={"dir": M.ISO, "fit": [[-60, -60, -30], [120, 60, 90]]},
                  labels=[{"at": (9, -14.2, 34.2), "text": "V 形块两段工作面（长 V 形块）：4 点——y、z、绕 y、绕 z", "style": "text", "pos": [0.5, 0.92], "part": "V 形块"},
                          {"at": (-3, -22, 50), "text": "挡板：1 点——x", "style": "text", "pos": [0.15, 0.12], "part": "轴向挡板"},
                          {"at": (110, 0, g["zc"] + 20), "text": "绕轴线的转动不限制（键槽角向位置无要求）", "style": "text", "pos": [0.68, 0.08]}])
R.compose("fig51_3_2", [pa, pb], 2, titles=["(a) 3–2–1：六个支承钉限制六个自由度（工件半透明）", "(b) SH-301 铣键槽：五个自由度"])

# ---- 图 51.3.3：常用定位元件相当于几个支承点
def solo(name, parts, cam, title):
    q = A(name)
    for n, s, c, *op in parts:
        q.add(P(n, s, c, opacity=op[0] if op else 1.0))
    return R.render_png(q, 520, 420, camera={"dir": cam}), title
pl = E.support_plate(80, 20, 12, at=(0, 0, 0), n=2)
tiles = [
    solo("支承板", [("支承板", pl, blue), ("工件", S.box(-50, 50, -15, 15, 0, 20), "work_cut", 0.4)], [0.8, -1.3, 0.9], "(a) 一块窄支承板：2 点（z、绕 y）"),
    solo("短V", [("V 形块", E.vblock(B=60, L=20, H=30, apex=10, at=(0, 0, 0)), blue), ("工件", S.cyl("x", (0, E.v_axis_height(30, apex=10)), 15, -60, 60), "work_cut", 0.4)],
         [0.9, -1.3, 0.8], "(b) 短 V 形块：2 点（y、z）"),
    solo("长V", [("V 形块", E.vblock(B=60, L=90, H=30, apex=10, at=(0, 0, 0)), blue), ("工件", S.cyl("x", (0, E.v_axis_height(30, apex=10)), 15, -60, 60), "work_cut", 0.4)],
         [0.9, -1.3, 0.8], "(c) 长 V 形块：4 点（y、z、绕 y、绕 z）"),
    solo("短销", [("定位销", E.locating_pin(20, 10, at=(0, 0, 0)), blue), ("底板", S.box(-50, 50, -50, 50, -18, -3), "cast"),
                 ("工件（盘）", S.cyl("z", (0, 0), 45, 0, 8) - S.cyl("z", (0, 0), 10.02, -1, 9), "work_cut", 0.4)], [0.8, -1.3, 1.0], "(d) 短定位销：2 点（x、y）"),
    solo("心轴", [("心轴", E.mandrel(30, 80, at=(0, 0, 0))[0], blue), ("工件（套）", S.cyl("x", (0, 0), 30, 5, 75) - S.cyl("x", (0, 0), 15.02, 4, 76), "work_cut", 0.4)],
         [0.9, -1.3, 0.7], "(e) 长心轴：4 点（y、z、绕 y、绕 z）"),
    solo("顶尖", [("前顶尖", E.center(at=(0, 0, 0)), blue), ("后顶尖", E.center(at=(120, 0, 0), toward=-1), orange),
                 ("工件（轴）", S.cyl("x", (0, 0), 14, 0, 120) - W.center_hole(0.0, 1) - W.center_hole(120.0, -1), "work_cut", 0.4)],
         [0.6, -1.3, 0.6], "(f) 前顶尖 3 点（x、y、z）+ 后顶尖 2 点（绕 y、绕 z）"),
]
R.compose("fig51_3_3", [t[0] for t in tiles], 3, titles=[t[1] for t in tiles])
out(n_fig3d=2)
