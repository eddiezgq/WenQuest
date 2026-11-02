"""第 55 章的三维图（模型：factory/digital/models3d/surface3d.py）：
图 55.0.1：SH-101 齿轮轴，左轴承位上的磨削烧伤带与裂纹（示意，烧伤带与裂纹放大画出）；
图 55.5.8：酸洗检查——烧伤处颜色发暗（烧伤带按修整周期在一批零件中出现，示意）；
图 55.7.1：滚压轴肩圆角（SH-301，两顶尖装夹）；
图 55.7.3：喷丸（工件为谐波减速器柔轮的示意圆环）。"""
import _mfg as M
from bookout import out

R = M.r3d()
X = M.s3d()
C = M.m3d()[0]

# ---- 图 55.0.1
g = X.gear_shaft(burn=True, crack=True)
jx, _, _ = g.anchors["journal"]
R.figure3d("fig55_0_1", g, 1300, 700, camera={"dir": [0.55, -1.25, 0.6]}, fontSize=19,
           labels=[{"at": (jx, -6, 11), "text": "轴承位 Ø25 k6：尺寸、Ra 都合格，酸洗出暗色的烧伤带", "style": "text", "pos": [0.25, 0.12], "part": "烧伤带"},
                   {"at": (jx, 0, 12.6), "text": "沿圆周的磨削裂纹（放大画出）", "style": "text", "pos": [0.22, 0.88], "part": "磨削裂纹"},
                   {"at": g.anchors["gear"], "text": "齿轮（20CrMnTi 渗碳淬火）", "style": "text", "pos": [0.62, 0.1], "part": "SH-101"}])

# ---- 图 55.5.8：一批零件酸洗：修整周期后段的几件有烧伤带
A = C.Assembly("酸洗检查")
for i, burnt in enumerate((False, False, True, True)):
    one = X.gear_shaft(burn=burnt)
    for p in one.parts:
        sh = M.m3d()[6].move(p.shape, 0, i * 70, 0)
        A.add(C.Part(f"{p.name}{i}", sh, p.color))
R.figure3d("fig55_5_8", A, 1300, 720, camera={"dir": [0.35, -1.0, 0.75]}, fontSize=19,
           labels=[{"at": (11, 0, 12.5), "text": "修整后的头几件：无烧伤", "style": "text", "pos": [0.42, 0.93], "part": "SH-1010"},
                   {"at": (11, 140, 12.5), "text": "修整周期后段的几件：轴承位暗色烧伤带", "style": "text", "pos": [0.62, 0.08], "part": "烧伤带2"}])

# ---- 图 55.7.1：滚压
r = X.rolling_fillet()
R.figure3d("fig55_7_1", r, 1300, 680, camera={"dir": [0.35, -1.0, 0.55], "fit": [[-20, -110, -40], [190, 40, 40]]}, fontSize=19,
           arrows=[{"from": r.anchors["push"], "to": r.anchors["roll"], "color": "#c0504d", "text": "滚压力", "textAt": "start", "dx": -10, "dy": 30}],
           labels=[{"at": r.anchors["roll"], "text": "滚轮压在轴肩圆角上，工件转动", "style": "text", "pos": [0.38, 0.1], "part": "滚轮"},
                   {"at": (100, 0, 20), "text": "SH-301（两顶尖装夹）", "style": "text", "pos": [0.7, 0.12], "part": "SH-301"}])

# ---- 图 55.7.3：喷丸
s = X.shot_peening()
R.figure3d("fig55_7_3", s, 1100, 720, camera={"dir": [0.9, -1.0, 0.6]}, fontSize=19,
           labels=[{"at": s.anchors["nozzle"], "text": "喷嘴：压缩空气带着弹丸高速打在表面", "style": "text", "pos": [0.45, 0.9], "part": "喷嘴"},
                   {"at": (0, 0, 30), "text": "工件转动，弹丸坑逐渐布满表面", "style": "text", "pos": [0.6, 0.1], "part": "工件（柔轮示意）"}])
out(n_fig3d=4)
