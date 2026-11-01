"""三维动画 54.9.1（配图 54.9.1）：外圆磨床的主动测量——测爪在磨削中一直量着直径，数控系统按读数分段控制横进给：
粗磨（0.01 mm/行程）到余量 0.05，精磨（0.005）到 0.005，光磨到读数归零即退刀。砂轮磨损了也不要紧：停的依据是工件的实际尺寸，
而不是砂轮架的位置——误差补偿和自动控制法（54.1、54.9 节）。读数是示意值，进给量取自工艺规程工序 60。模型：factory/digital/models3d。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, machines as MA, shapes as S, workpiece as W  # noqa: E402

L, XG = 167.0, 124.5
g = MA.cylindrical_grinder(L=L, wheel_x=XG - 40, r_work=17.5)
g.add(W.sh301("op60"))
for sgn in (1, -1):
    zt = sgn * 17.5
    g.add(C.Part("测爪" + ("上" if sgn > 0 else "下"), S.box(XG - 2.5, XG + 2.5, -3, 3, min(zt, zt + sgn * 10), max(zt, zt + sgn * 10))
                 + S.box(XG - 2.5, XG + 2.5, -70, 3, min(zt + sgn * 10, zt + sgn * 16), max(zt + sgn * 10, zt + sgn * 16)), "hardened"))
g.add(C.Part("主动测量仪", S.box(XG - 8, XG + 8, -120, -70, -45, 45), "#3d5a80"))
MOV = ("砂轮", "砂轮罩", "砂轮架", "横进给拖板")
CAM = {"dir": [0.45, -1, 0.55], "fit": [[-60, -160, -140], [L + 120, 320, 220]]}
v = R.Video(g, width=1280, height=720, fps=20)


def st(back, reading, phase, cap, col="#1d2327"):
    return {"parts": {n: {"move": [0, back, 0]} for n in MOV}, "camera": CAM,
            "texts": [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
                      {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"},
                      {"pos": [0.62, 0.82], "text": f"测量仪读数（离目标）{reading * 1000:+6.1f} µm", "fontSize": 26, "bold": True, "color": col},
                      {"pos": [0.62, 0.88], "text": phase, "fontSize": 22, "color": "#5b6770"}]}


v.add(st(30, 0.300, "装上工件，砂轮快速趋近", ("主动测量：测爪一直量着直径", "In-process gauging: the fingers measure all the time")), hold=1.5)
for k in range(10):
    v.add(st(30 - 3 * k, 0.300 - 0.025 * k, "粗磨：横进给 0.01 mm/行程", ("数控系统按读数分段控制进给", "The control switches feed by the reading")), hold=0.12)
for k in range(8):
    v.add(st(0, 0.050 - 0.0056 * k, "精磨：横进给 0.005 mm/行程", ("余量 0.05 时转精磨", "Switch to finishing at 0.05 left")), hold=0.15)
for k in range(5):
    v.add(st(0, 0.005 - 0.001 * k, "光磨：不进给", ("光磨，读数归零", "Spark-out until the reading reaches zero")), hold=0.2)
v.add(st(0, 0.0, "到尺寸：退刀", ("到尺寸即停：停的依据是工件的实际尺寸", "Stop at size — judged by the part, not by the wheelhead position"), "#5a9e6f"), hold=2.0)
v.add(st(40, 0.0, "下一件：砂轮磨小了也照样到尺寸停", ("砂轮磨损、砂轮架热伸长都被“量”掉了", "Wheel wear and thermal growth are measured away"), "#5a9e6f"), hold=2.5)
v.save("v54_9_1")
