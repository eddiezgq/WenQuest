"""第 56 章的三维图（模型：factory/digital/models3d/route3d.py，尺寸取 std/SH-101_part.yaml 与 SH-101_route.yaml）：
图 56.0.1 SH-101 输入齿轮轴；56.2.2 SH-101 在输入轴组件里（两个 6205 轴承、轴伸键，示意）；56.2.4 结构工艺性正误对照（示意）；
56.2.7 SH-101 上要审查的部位；56.3.1 两种毛坯；56.4.2 两端中心孔贯穿各工序（基准统一）；56.4.6 机器人关节输出法兰的精基准（示意）；
56.5.2 铸件套筒的两种粗基准（剖视，示意）；56.9.3 SH-101 从棒料到成品。"""
import _mfg as M
from bookout import out

R = M.r3d()
X = M.r101()
C = M.m3d()[0]
S = M.m3d()[6]
CAM = {"dir": [0.45, -1.15, 0.55]}

# ---- 图 56.0.1
a = X.sh101_assembly("op70")
an = a.anchors
R.figure3d("fig56_0_1", a, 1300, 600, camera=CAM, fontSize=19,
           labels=[{"at": an["轴伸"], "text": "轴伸 Ø20 j6（键槽 6 N9）", "style": "text", "pos": [0.22, 0.12]},
                   {"at": an["左轴承位"], "text": "轴承位 Ø25 k6（两处）", "style": "text", "pos": [0.36, 0.9]},
                   {"at": an["齿轮"], "text": "齿轮 m2 z24（与轴一体）", "style": "text", "pos": [0.62, 0.1]},
                   {"at": an["右轴承位"], "text": "20CrMnTi 渗碳淬火 58–62 HRC", "style": "text", "pos": [0.72, 0.9]}])

# ---- 图 56.2.2：输入轴组件（示意）
A = C.Assembly("输入轴组件")
for p in X.sh101_assembly("op70").parts:
    A.add(p)
for xc in (36 + 20 + 8.5, 136 - 8.5):
    A.add(C.Part("轴承 6205", S.tube("x", (0, 0), 26, 12.5, xc - 7.5, xc + 7.5) - S.tube("x", (0, 0), 22, 16, xc - 8, xc + 8)
                 + S.tube("x", (0, 0), 22.2, 15.8, xc - 3, xc + 3), "steel"))
A.add(C.Part("平键 6×6×25", S.box(5.5, 30.5, -3, 3, 6.5, 12.5), "steel_dark"))
A.add(C.Part("油封（示意）", S.tube("x", (0, 0), 20, 12.05, 44, 51), "#3d3d3d"))
R.figure3d("fig56_2_2", A, 1300, 560, camera=CAM, fontSize=19,
           labels=[{"at": (64.5, 0, 26), "text": "6205 轴承（左）", "style": "text", "pos": [0.33, 0.12], "part": "轴承 6205"},
                   {"at": (47, 0, 20), "text": "油封唇口压在密封轴颈上", "style": "text", "pos": [0.26, 0.9], "part": "油封（示意）"},
                   {"at": (18, 0, 12.5), "text": "轴伸：联轴器、平键", "style": "text", "pos": [0.16, 0.25], "part": "平键 6×6×25"},
                   {"at": (96, 0, 26), "text": "齿轮与大齿轮 GR-202 啮合", "style": "text", "pos": [0.62, 0.1]}])

# ---- 图 56.2.4：结构工艺性正误对照（示意）
panels, titles = [], []
for name, bad, good in X.craft_pairs():
    for tag, shp, col in (("不好", bad, "#c9a79f"), ("好", good, "work")):
        asm = C.Assembly(name)
        asm.add(C.Part(name, shp, col))
        panels.append(R.render_png(asm, 640, 360, camera={"dir": [0.5, -1.0, 0.7]}))
        titles.append(f"{name}：{tag}")
R.compose("fig56_2_4", panels, cols=4, titles=titles)

# ---- 图 56.3.1：两种毛坯
B = C.Assembly("毛坯")
bar = X.sh101("blank", "#b9b2a6")
B.add(C.Part("棒料", bar.shape, "#b9b2a6"))
forg = S.cyl("x", (0, 0), 14.5, -2.5, 73) + S.cyl("x", (0, 0), 28.5, 73, 119) + S.cyl("x", (0, 0), 15, 119, 138.5)
B.add(C.Part("模锻件", S.move(forg, 0, 0, -75), "#a78f74"))
R.figure3d("fig56_3_1", B, 1300, 640, camera={"dir": [0.35, -1.2, 0.45]}, fontSize=19,
           labels=[{"at": (70, 0, 30), "text": "热轧圆钢 Ø60 × 142（锯切下料）", "style": "text", "pos": [0.5, 0.08], "part": "棒料"},
                   {"at": (96, 0, -75 + 28.5), "text": "模锻件（示意）：各段单边留 2 mm，需正火", "style": "text", "pos": [0.55, 0.92], "part": "模锻件"}])

# ---- 图 56.4.2：两端中心孔贯穿各工序（剖开看中心孔）
panels, titles = [], []
from models3d import elements as E  # noqa: E402
for st, t in (("op20", "工序 20 粗车：钻出两端中心孔"), ("op30", "工序 30 精车：两顶尖"), ("op40", "工序 40 滚齿：两顶尖（心轴架）"), ("op70", "工序 70 磨：修研后的中心孔")):
    a = X.sh101_assembly(st)
    x0 = -0.5 if st == "op20" else 0.0
    L = 137.0 if st == "op20" else 136.0
    if st != "op20":
        a.add(C.Part("前顶尖", E.center(at=(x0, 0, 0), toward=1), "hardened", tags=("nocut",)))
        a.add(C.Part("后顶尖", E.center(at=(x0 + L, 0, 0), toward=-1), "hardened", tags=("nocut",)))
    panels.append(R.render_png(a, 900, 380, camera={"dir": [0.3, -1.0, 0.35]}, section=((0, 0, 0), (0, -1, 0))))
    titles.append(t)
R.compose("fig56_4_2", panels, cols=2, titles=titles)

# ---- 图 56.4.6：关节输出法兰的精基准（示意）
fl = X.flange()
R.figure3d("fig56_4_6", fl, 1100, 620, camera={"dir": [0.9, -1.0, 0.7]}, fontSize=19,
           labels=[{"at": fl.anchors["bore"], "text": "内孔 Ø40 H7：精车止口、端面时的定位基准", "style": "text", "pos": [0.55, 0.12]},
                   {"at": fl.anchors["spigot"], "text": "止口 Ø62 h7：与内孔一次装夹车出", "style": "text", "pos": [0.62, 0.9]},
                   {"at": fl.anchors["face"], "text": "安装端面：钻螺孔时的定位面", "style": "text", "pos": [0.3, 0.9]}])

# ---- 图 56.5.2：铸件套筒的两种粗基准（剖视）
panels = []
for good in (True, False):
    sv = X.sleeve(good, ecc=6.0)                   # 偏心放大画出（算例 56.5.1 取 2 mm）
    panels.append(R.render_png(sv, 760, 560, camera={"dir": [0.6, -0.5, 1.0]}, section=((30, 0, 0), (1, 0, 0))))
R.compose("fig56_5_2", panels, cols=2, titles=["(a) 以外圆（不加工面）为粗基准：壁厚均匀", "(b) 以毛坯内孔为粗基准：壁厚不均（偏心放大画出）"])

# ---- 图 56.9.3：从棒料到成品
panels, titles = [], []
for st, t in (("blank", "工序 10 下料"), ("op20", "工序 20 粗车"), ("op30", "工序 30 精车（磨前）"), ("op40", "工序 40 滚齿"),
              ("op50", "工序 50 铣键槽"), ("op60", "工序 60 渗碳淬火"), ("op70", "工序 70 磨外圆（成品）")):
    col = "#8a8f96" if st == "op60" else "work"
    a = C.Assembly(st)
    a.add(X.sh101(st if st != "op60" else "op50", col))
    panels.append(R.render_png(a, 800, 300, camera={"dir": [0.4, -1.1, 0.5]}))
    titles.append(t)
R.compose("fig56_9_3", panels, cols=2, titles=titles)
out(n_fig3d=9)
