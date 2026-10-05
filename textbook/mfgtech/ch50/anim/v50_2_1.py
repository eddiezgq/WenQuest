"""三维动画 50.2.1（配图 50.2.1）：一根 SH-301 走过工序 10–60——下料、粗车两次安装、调质、精车（两顶尖）、铣键槽（JJ-301-50）、磨外圆（工序 70 检验见图 50.6.3），
每一段显示工序号、工作中心、本工序加工的面（橙色）。工序与工作中心取自数字工厂的工艺规程；模型：factory/digital/models3d，逐帧渲染。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, workpiece as W, machines as MA, jj30150 as J, shapes as S, elements as E  # noqa: E402

plan = W.plan()
ops = {o["seq"]: o for o in plan["operations"]}
LEN = 167.0
a = C.Assembly("工艺路线")
scenes = {}


def scene(key, parts):
    names = []
    for p in parts:
        p.name = f"{key}·{p.name}"
        a.add(p)
        names.append(p.name)
    scenes[key] = names


scene("10", [C.Part("毛坯", S.move(W.sh301("blank").shape, 7, 0, 0), "work", face_color=lambda f: "machined" if abs(f.center().X - 189.0) < 0.5 else None), C.Part("锯条", S.box(186, 190, -60, 60, -40, 60), "tool")])
def chuck_scene(D, work, tail, color_note=None):
    c = MA.chuck3(D=200, grip=D)
    parts = list(c.parts)
    for p in parts:
        if p.name.startswith("卡爪"):
            p.shape = p.shape & S.box(-1, 20, -300, 300, -300, 300)
    return parts + [work, C.Part("后顶尖", E.center(at=(tail, 0, 0), toward=-1), "hardened"),
                    C.Part("尾座套筒", S.cyl("x", (0, 0), 22, tail + 70, tail + 150), "cast")]


# 工序 20 安装 1：夹毛坯左端，右端车端面、钻中心孔后顶住，粗车右段（橙色）
prof1 = [(0.0, 25.0, 46.7, "work"), (46.7, 20.75, 120.3, "machined"), (120.3, 18.25, 145.3, "machined"), (145.3, 15.75, 175.0, "machined")]
w1 = None
for x0, r, x1, _ in prof1:
    c = S.cyl("x", (0, 0), r, x0, x1)
    w1 = c if w1 is None else w1 + c
scene("20·安装1", chuck_scene(50.0, C.Part("工件（安装 1）", w1, "work", face_color=lambda f: "machined" if f.center().X > 46.0 else None), 175.0))
# 安装 2：调头，右段伸进主轴孔，夹 Ø41.5；车左端面、钻中心孔后顶住，粗车左段
prof2 = [(-54.7, 15.75, -24.7), (-24.7, 18.25, 0.0), (0.0, 20.75, 73.6), (73.6, 18.25, 85.6), (85.6, 15.75, 120.3)]
w2 = None
for x0, r, x1 in prof2:
    c = S.cyl("x", (0, 0), r, x0, x1)
    w2 = c if w2 is None else w2 + c
scene("20·安装2", chuck_scene(41.5, C.Part("工件（安装 2）", w2, "work", face_color=lambda f: "machined" if f.center().X > 73.0 else None), 120.3))
scene("30", [C.Part("调质炉（示意）", S.box(-20, 200, -70, 70, -70, -60) + S.box(-20, 200, -70, -60, -60, 60) + S.box(-20, 200, 60, 70, -60, 60), "#c0504d", opacity=0.6),
             W.sh301("op20", color="#8a5a3a")])
lc = MA.lathe_centers(LEN, 0.0)
scene("40", lc.parts + [W.sh301("op40", highlight=True)])
ja = J.assembly("op40")
ja.parts = [p for p in ja.parts if not p.name.startswith("工件")]
w50 = W.sh301("op50", highlight=True)
w50.shape = S.move(w50.shape, J.geometry()["work_x0"], 0, J.geometry()["zc"])
scene("50", ja.parts + [w50])
gr = MA.lathe_centers(LEN, 0.0)
scene("60", gr.parts + [W.sh301("op60", highlight=True), C.Part("砂轮", S.tube("x", (170, 0), 150, 50, 52, 112), "#9aa3ab")])
CAMS = {"10": {"dir": [0.4, -1.2, 0.6], "fit": [[-10, -60, -40], [200, 60, 60]]},
        "20·安装1": {"dir": [0.35, -1.2, 0.5], "fit": [[-60, -110, -110], [340, 60, 110]]},
        "20·安装2": {"dir": [0.35, -1.2, 0.5], "fit": [[-60, -110, -110], [290, 60, 110]]},
        "30": {"dir": [0.4, -1.2, 0.6], "fit": [[-20, -70, -70], [200, 70, 70]]}, "40": {"dir": [0.45, -1.3, 0.5], "fit": [[-120, -80, -100], [300, 80, 100]]},
        "50": {"dir": [0.9, -1.25, 0.95]}, "60": {"dir": [0.45, -1.3, 0.5], "fit": [[-120, -60, -160], [300, 330, 160]]}}
v = R.Video(a, width=1280, height=720, fps=20)
order = ["10", "20·安装1", "20·安装2", "30", "40", "50", "60"]


def st(key, spin):
    parts = {n: {"visible": n in scenes[key]} for ns in scenes.values() for n in ns}
    for n in scenes[key]:
        if ("SH-301" in n or "工件（安装" in n) and key in ("20·安装1", "20·安装2", "40", "60"):
            parts[n]["rot"] = [1, 0, 0, spin, 0, 0, 0]
    o = ops.get(int(key.split("·")[0]), {})
    wc = o.get("workstation", "")
    name = o.get("operation", "").split(" ")[0]
    return {"parts": parts, "camera": CAMS[key],
            "texts": [{"pos": [0.03, 0.08], "text": f"工序 {key.split('·')[0]}  {name}" + (f"（{key.split('·')[1]}）" if "·" in key else ""), "fontSize": 28, "bold": True},
                      {"pos": [0.03, 0.135], "text": f"{wc}　{o.get('clamping', '') or ''}　单件 {o.get('minutes', '')} min" if wc else "", "fontSize": 19, "color": "#5b6770"},
                      {"pos": [0.03, 0.93], "text": "（热处理：不切削）" if key == "30" else "橙色：本工序加工的面", "fontSize": 17, "color": "#b5652a"}]}


for key in order:
    for i in range(30):
        v.add(st(key, 12 * i))
    v.add(st(key, 0), hold=0.8)
v.save("v50_2_1")
