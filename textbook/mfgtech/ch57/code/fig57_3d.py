"""第 57 章的三维图（模型：factory/digital/models3d/route3d.py，尺寸取 std/SH-101_process.yaml）：
图 57.0.2 工序 30 后的 SH-101 与它的工序尺寸；57.1.4 从棒料到成品一层层切掉的余量（剖开，余量放大画出）；
57.4.2 SH-101 各工序的装夹与刀具（两顶尖车、滚齿、V 形块铣键槽、两顶尖磨，示意）。"""
import _mfg as M
from bookout import out

R = M.r3d()
X = M.r101()
C, S = M.m3d()[0], M.m3d()[6]
CAM = {"dir": [0.45, -1.15, 0.55]}

# ---- 图 57.0.2：工序 30 后
a = X.sh101_assembly("op30")
an = a.anchors
R.figure3d("fig57_0_2", a, 1300, 600, camera=CAM, fontSize=18,
           labels=[{"at": an["轴伸"], "text": "轴伸 Ø20.4 0/−0.05（留磨量）", "style": "text", "pos": [0.26, 0.1]},
                   {"at": an["密封轴颈"], "text": "密封轴颈 Ø24.4 0/−0.05", "style": "text", "pos": [0.2, 0.9]},
                   {"at": an["左轴承位"], "text": "轴承位 Ø25.4 0/−0.05", "style": "text", "pos": [0.42, 0.93]},
                   {"at": an["齿轮"], "text": "齿顶圆 Ø52 h11（到尺寸）", "style": "text", "pos": [0.62, 0.1]},
                   {"at": an["右轴承位"], "text": "总长 136 ± 0.05，8 ± 0.05", "style": "text", "pos": [0.8, 0.9]}])

# ---- 图 57.1.4：余量一层层（右半轴，剖开；各层径向放大 3 倍画出，不按比例）
A = C.Assembly("余量")
layers = [("棒料", 30.0, "#b9b2a6"), ("粗车后", 20.0, "#8aa4bd"), ("半精车后", 16.0, "#3a7dc9"), ("磨后", 12.5, "#d98c3a")]
for i, (n, r, col) in enumerate(layers):
    A.add(C.Part(n, S.cyl("x", (0, 0), r, 0 + i * 12, 70), col))
panels = [R.render_png(A, 1100, 560, camera={"dir": [0.55, -1.0, 0.6]}, section=((0, 0, 0), (0, 0, 1)))]
R.compose("fig57_1_4", panels, cols=1, titles=["从棒料到磨后：一层层切掉的余量（剖开；各层厚度放大画出）"])

# ---- 图 57.4.2：各工序的装夹与刀具（示意）
panels, titles = [], []
cone = [(-55.0, 0.0), (-55.0, 9.0), (-14.0, 9.0), (2.0, 0.0)]
for st, tool, cap in (("op30", "lathe", "工序 30 精车：两顶尖、鸡心夹头"), ("op40", "hob", "工序 40 滚齿：上下顶尖（心轴架）、滚刀"),
                      ("op50", "vblock", "工序 50 铣键槽：轴伸放在 V 形块上"), ("op70", "grind", "工序 70 磨外圆：两顶尖、砂轮")):
    B = C.Assembly(st)
    B.add(X.sh101(st, "#9aa0a6" if st == "op70" else "work"))
    if tool != "vblock":
        B.add(C.Part("前顶尖", S.revolve(cone), "steel"))
        B.add(C.Part("后顶尖", S.revolve([(136 - x, r) for x, r in cone]), "steel"))
    if tool == "lathe":
        B.add(C.Part("车刀", S.box(123.5, 131.5, -4, 4, 12.7, 42), "steel_dark"))
    elif tool == "hob":
        B.add(C.Part("滚刀", S.move(S.cyl("y", (0, 0), 31.5, -30, 30), 96, 0, 26 + 31.5 - 4.5), "#5f7e9c"))
    elif tool == "vblock":
        B.add(C.Part("V 形块", S.prism("yz", [(-22, -26), (22, -26), (22, -6), (14.4, -6), (0, -14.4), (-14.4, -6), (-22, -6)], 4, 32), "#8f9aa5"))
        B.add(C.Part("键槽铣刀", S.cyl("z", (18, 0), 3, 7, 45), "steel_dark"))
    elif tool == "grind":
        B.add(C.Part("砂轮", S.move(S.cyl("x", (0, 0), 70, -10, 10), 127.5, 12.5 + 70, 0), "#c8c1b4"))
    panels.append(R.render_png(B, 800, 360, camera={"dir": [0.35, -1.1, 0.5]}))
    titles.append(cap)
R.compose("fig57_4_2", panels, cols=2, titles=titles)
out(n_fig3d=3)
