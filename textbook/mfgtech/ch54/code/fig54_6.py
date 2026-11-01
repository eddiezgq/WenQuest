"""54.6 节的三维图：铣键槽后残余应力重新平衡，SH-301 弯曲（图 54.6.4，弯曲放大 1000 倍，挠度曲线来自算例 54.6.3）；
阿贝原则——游标卡尺与外径千分尺（图 54.6.6）。模型：factory/digital/models3d；量具为简化的示意模型。"""
import math

import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
X = M.x3d()
R = M.r3d()
Acc = M.acc()
A, P = C.Assembly, C.Part
red, blue = "#c0504d", "#4f7fb8"
p = M.plan()
k = p["part"]["keyway"]
x1 = 52.0 + float(k["offset_mm"])
x2 = x1 + float(k["L"])
I = math.pi * 40.0 ** 4 / 64
bow = Acc.bow_from_moment(Acc.layer_moment(80.0, float(k["b"]) * float(k["t"]), 20.0 - float(k["t"]) / 2), 167.0, x1, x2, Acc.E_STEEL, I)
K = 1000.0
n = 25
idx = [round(i * (len(bow["x_list"]) - 1) / (n - 1)) for i in range(n)]
ys = [K * abs(bow["y"][i]) for i in idx]                       # 向键槽一侧（+z）凸起
shaft = S.rot(X.bent_shaft(L=167.0, r=20.0, n=n, ys=ys), ax=90)
mid = K * bow["max"]
slot = S.box(x1, x2, -6, 6, 15 + mid * 0.6, 40)
q = A("键槽后弯曲")
q.add(P("铣键槽后（弯曲放大 1000 倍）", shaft - slot, "work"))
q.add(P("铣键槽前的下母线", S.cyl("x", (0, -20.0), 0.8, -5, 172), blue))
R.figure3d("fig54_6_4", q, 1400, 560, camera={"dir": [0.15, -1, 0.25], "fit": [[-5, -30, -30], [172, 30, 35]]}, fontSize=18,
           labels=[{"at": ((x1 + x2) / 2, 0, 20 + mid), "text": "键槽：去掉了一块有残余应力的材料", "style": "text", "pos": [0.5, 0.08], "part": "铣键槽后"},
                   {"at": (150, 0, -20), "text": "蓝线：铣键槽前的下母线（直线）", "style": "text", "pos": [0.75, 0.92], "part": "铣键槽前"}])

# ---- 图 54.6.6：阿贝原则
def caliper():
    q = A("游标卡尺")
    q.add(P("尺身", S.box(-20, 180, -2, 2, 40, 52), "steel"))
    q.add(P("固定量爪", S.box(-20, -8, -2, 2, 0, 40), "steel"))
    q.add(P("尺框与活动量爪", S.box(60, 90, -3, 3, 38, 56) + S.box(60, 72, -2, 2, 0, 38), "steel_dark"))
    q.add(P("工件", S.box(-8, 60, -10, 10, 5, 20), "work"))
    return q


def micrometer():
    q = A("外径千分尺")
    q.add(P("尺架", S.box(-30, -20, -4, 4, -40, 10) + S.box(-30, 110, -4, 4, -50, -40) + S.box(100, 110, -4, 4, -40, 10), "#3d5a80"))
    q.add(P("测砧", S.cyl("x", (0, 0), 3.5, -20, -8), "hardened"))
    q.add(P("测微螺杆", S.cyl("x", (0, 0), 3.5, 60, 100) + S.cyl("x", (0, 0), 8, 110, 170), "steel"))
    q.add(P("工件", S.box(-8, 60, -10, 10, -8, 8), "work"))
    return q


pa = R.render_png(caliper(), 640, 420, camera={"dir": [0.2, -1, 0.3], "fit": [[-30, -10, -5], [190, 10, 60]]}, fontSize=19,
                  dims=[{"a": (-8, 0, 12), "b": (-8, 0, 46), "off": (-14, 0, 0), "text": "s", "color": red}],
                  labels=[{"at": (100, 0, 46), "text": "刻线在尺身上，不在被测线上", "style": "text", "pos": [0.9, 0.1], "part": "尺身"},
                          {"at": (30, -10, 12), "text": "被测线", "style": "text", "pos": [0.4, 0.92], "part": "工件"}])
pb = R.render_png(micrometer(), 640, 420, camera={"dir": [0.2, -1, 0.3], "fit": [[-40, -10, -55], [175, 10, 20]]}, fontSize=19,
                  labels=[{"at": (140, 0, 8), "text": "测微螺杆的轴线就是被测线", "style": "text", "pos": [0.65, 0.1], "part": "测微螺杆"}])
R.compose("fig54_6_6", [pa, pb], 2, titles=["(a) 游标卡尺：不符合阿贝原则，误差 ≈ s·tan φ", "(b) 外径千分尺：符合阿贝原则"])
out(K=K)
