"""52.10 节的三维图：JJ-301-50 的验收检验（图 52.10.1，检验棒 + 千分表，在检验平板上）、装上铣床后用检验棒找正（图 52.10.2）、
日常维护的检查点（图 52.10.4）。模型：factory/digital/models3d（JJ-301-50 尺寸取自夹具数据）。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A, P = C.Assembly, C.Part
g = J.geometry()
zc, d_bar = g["zc"], g["d_g"]
rb = d_bar / 2
side, top = g["setting_side"], g["setting_top"]
Z0 = -J.BODY["t"]                                        # 夹具体底面


def fixture(on="plate"):
    q = J.assembly("op40", with_work=False)
    q.parts = [p for p in q.parts if p.number != 13]   # 检验时不装 T 形槽螺栓
    q.add(P("检验棒 Ø40.3", S.cyl("x", (0, zc), rb, -30, 90), "glass"))
    if on == "plate":
        plate = S.box(-200, 230, -170, 150, Z0 - 40, Z0) - S.box(-201, 231, -9, 9, Z0 - 12, Z0 + 1)
        q.add(P("检验平板（带一条 18 mm 基准槽）", plate, "#6d7a84"))
    return q


# ---- 图 52.10.1：验收检验
# (a) 检验棒上母线对夹具体底面的平行度：表座在平板上沿 x 推，测杆压在上母线
qa = fixture()
for p in MA.dial_indicator(tip=(10, 0, zc + rb), base_at=(-150, 0, Z0)).parts:
    qa.add(p)
cam = {"dir": [0.85, -1.3, 0.7], "fit": [[-160, -110, Z0 - 10], [180, 80, 140]]}
pa = R.render_png(qa, 760, 540, camera=cam,
                  arrows=[{"from": (-20, -45, zc + rb + 25), "to": (60, -45, zc + rb + 25), "color": "#c0504d"}],
                  labels=[{"at": (10, 0, zc + rb), "text": "测杆压在上母线", "style": "text", "pos": [0.6, 0.1]},
                          {"at": (180, 60, Z0), "text": "夹具体底面贴在检验平板上", "style": "text", "pos": [0.78, 0.9], "part": "检验平板（带一条 18 mm 基准槽）"}])
# (b) 侧母线对定位键侧面的平行度：两个定位键推向基准槽的同一侧，测杆水平压在侧母线
qb = fixture()
qb.add(P("平行尺（固定在平板上，与基准槽平行）", S.box(-150, 180, -175, -167, Z0, Z0 + 20), "hardened"))
for p in MA.dial_indicator(tip=(10, -rb, zc), stem_dir=(0, -1, 0), base_at=(10, -142, Z0)).parts:
    qb.add(p)
pb = R.render_png(qb, 760, 540, camera=cam,
                  arrows=[{"from": (-30, -150, Z0 + 5), "to": (50, -150, Z0 + 5), "color": "#c0504d"}],
                  labels=[{"at": (10, -rb, zc), "text": "测杆水平压在侧母线", "style": "text", "pos": [0.25, 0.12]},
                          {"at": (-40, 9, Z0 - 4), "text": "定位键靠紧基准槽的一侧", "style": "text", "pos": [0.25, 0.9]}])
# (c) 对刀块：表在上母线对零，移到对刀块底面，读数差即底面比检验棒上母线低多少
qc = fixture()
for p in MA.dial_indicator(tip=(144, 0, top), base_at=(144, -140, Z0)).parts:
    qc.add(p)
cc = {"dir": [0.85, -1.3, 0.7], "fit": [[-20, -150, Z0 - 10], [190, 40, 170]]}
pc = R.render_png(qc, 760, 540, camera=cc,
                  labels=[{"at": (144, 0, top), "text": f"在对刀块底面读数：比上母线低 {zc + rb - top:.2f}", "style": "text", "pos": [0.62, 0.08]},
                          {"at": (40, 0, zc + rb), "text": "先在检验棒上母线对零", "style": "text", "pos": [0.25, 0.1]}])
R.compose("fig52_10_1", [pa, pb, pc], 3, titles=["(a) 上母线对底面的平行度：表座在平板上沿 x 推（箭头）", "(b) 侧母线对定位键侧面的平行度：表座靠着平行尺移动", "(c) 对刀块底面的高度：上母线对零后移到底面读数"])

# ---- 图 52.10.2：装上铣床后用检验棒找正：千分表吸在主轴上，测杆压在侧母线，工作台沿 x 移动
qm = J.assembly("op40", with_work=False, with_table=True)
qm.add(P("检验棒 Ø40.3", S.cyl("x", (0, zc), rb, -30, 90), "glass"))
spindle = S.cyl("z", (10, -rb - 64), 40, zc + 110, zc + 220)
qm.add(P("铣床主轴（局部）", spindle, "steel_dark", tags=("nocut",)))
ind = MA.dial_indicator(tip=(10, -rb, zc), stem_dir=(0, -1, 0), base_at=(10, -rb - 64, zc + 110))
for p in ind.parts:
    if p.name != "表座":
        qm.add(p)
qm.add(P("磁力表座（吸在主轴端面）", S.cyl("z", (10, -rb - 64), 24, zc + 70, zc + 110), "rubber"))
R.figure3d("fig52_10_2", qm, 900, 600, camera={"dir": [0.85, -1.25, 0.65], "fit": [[-120, -160, -80], [220, 120, 250]]},
           arrows=[{"from": (-60, -130, -60), "to": (60, -130, -60), "text": "工作台沿 x 移动", "color": "#c0504d"}],
           labels=[{"at": (10, -rb, zc), "text": "测杆压在检验棒侧母线", "style": "text", "pos": [0.25, 0.15]},
                   {"at": (-75, 40, -10), "text": "读数变化超过要求：松开螺栓，轻敲夹具一端再测", "style": "text", "pos": [0.45, 0.92]}])

# ---- 图 52.10.4：日常维护的检查点
qn = J.assembly("op40", with_work=False)
qn.add(P("夹具铭牌（编号 JJ-301-50、版本、检定日期）", S.box(60, 110, J.BODY["y0"] - 1.5, J.BODY["y0"], -24, -6), "#e3d7a8"))
pts = [((9, -18, 32), "V 形块工作面：每班擦净；每 500 件用检验棒查磨损", "V 形块", [0.28, 0.08]),
       ((-3, -20, 40), "轴向挡板端面：磕碰、磨损", "轴向挡板", [0.2, 0.3]),
       ((147, 0, top), "对刀块两个对刀面：不得磕碰、生锈", "对刀块", [0.82, 0.12]),
       ((-20, 40, zc + 30), "螺柱、螺母、弹簧：螺纹完好、弹簧能顶起压板", "压板1", [0.55, 0.04]),
       ((85, J.BODY["y0"] - 1.5, -15), "铭牌：编号与工序卡一致", "夹具铭牌（编号 JJ-301-50、版本、检定日期）", [0.45, 0.93]),
       ((-60, J.BODY["y0"], -27), "夹具体底面、定位键：装机前擦净，无毛刺", "夹具体", [0.3, 0.75])]
R.figure3d("fig52_10_4", qn, 1400, 900, camera={"dir": M.ISO, "fit": [[-95, -70, -40], [190, 105, 90]]},
           labels=[{"at": a, "text": t, "style": "text", "pos": p, "part": n} for a, t, n, p in pts])
out(n_fig3d=3, drop_top=zc + rb - top)
