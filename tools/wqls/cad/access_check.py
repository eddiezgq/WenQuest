"""第 138 轮 G5.2：合箱后精加工（工序 70）的刀具能不能进去——刀具、刀杆、直角铣头与机壳（上件＋下件合箱）的最小距离。在 FreeCAD 里运行：

    WQ_HOUSING=<上件 STEP> WQ_HOUSING_LOWER=<下件 STEP> WQ_OUT=<json> freecadcmd -c "exec(open('tools/wqls/cad/access_check.py').read())"

检查的刀具（整机坐标，mm；只画不切削的部分——刀杆、刀柄、铣头机身；切削刃在孔里，本来就贴着孔壁）：
  ① 测针杆轴线：针杆上、下两孔里各插一个液压涨紧塞规 Ø12（零间隙）。下塞规的测量段从机头底面往下伸到 z 22，
     上塞规的测量段从上导套座顶面往上伸到 z 200（经面板口用手放进去）。主轴上的测头（机身 Ø25，曲柄测针 Ø3）在 B 0°：
     下塞规在机座顶面和机头底面之间的 46 mm 空当里测（z 30；机头底面在针杆左边低到 z 39.5），上塞规经面板口进机头测（z 190）；
     （原来想用直角铣头经面板口进机头扩、铰针杆孔：150 长的铰刀竖着挂在铣头下面，水平移进去会撞针杆上、下导套座，进不去）
  ② 下轴两孔同轴镗杆（B 180°，从右端壁 Ø34 孔进）：杆身 Ø26，尾部导向柱 Ø17 穿过左端壁 Ø20 孔；
  ③ 旋梭轴孔阶梯镗杆（B 0°，从左端壁 Ø20 孔进）：Ø18 硬质合金杆到 x 20，Ø12 颈部伸进 Ø14 孔；
  ④ 锥销孔：直角铣头在机座底面以下（夹具框里），刀具 Ø10.8（锥度铰刀大端）向上穿过机座开口的底面，到下件销孔凸台。
"""
import json
import os

import FreeCAD as App
import Part

V = App.Vector
up = Part.read(os.environ["WQ_HOUSING"])
low = Part.read(os.environ["WQ_HOUSING_LOWER"])
exec(open(os.path.join(os.getcwd(), "tools/wqls/spec.py"), encoding="utf-8").read(), S := {})
ZH, YL, ZL, ZU = S["ZH"], S["YL"], S["ZL"], S["ZU"]
X = V(1, 0, 0)


def cylx(r, x0, x1, y, z):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), X)


def cylz(r, z0, z1, x, y):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))


probe = {}
for zb, zt, nm in ((20.0, 30.0, "下塞规（空当里，z 30）"), (205.0, 190.0, "上塞规（经面板口，z 190）")):
    # 曲柄测针：从机身沿主轴方向伸出 15，竖着拐到测量高度，再水平伸到塞规（塞规外圆 r 6，测针球 r 1.5）
    bx = cylx(12.5, -400, -62, 0, zb).fuse(cylx(1.5, -62, -45, 0, zb)).fuse(cylz(1.5, min(zb, zt), max(zb, zt), -45, 0)).fuse(cylx(1.5, -45, -6.5, 0, zt))
    probe[f"测头 B 0° 测{nm}"] = (bx, [up, low])
tools = {
    **probe,
    "下塞规测量段 Ø12（z 22…45.5）": (cylz(6, 22, 45.5, 0, 0), [low]),
    "上塞规测量段 Ø12（z 182.5…200）": (cylz(6, 182.5, 200, 0, 0), [low]),
    "下轴同轴镗杆 Ø26 / 导向柱 Ø17": (cylx(13, 80, 600, YL, ZL).fuse(cylx(8.5, -160, 80, YL, ZL)), [low]),
    "旋梭轴孔阶梯镗杆 Ø18 / Ø12": (cylx(9, -400, 20, 0, ZH).fuse(cylx(6, 20, 68, 0, ZH)), [low]),
}
# G4.6 送布组的孔（刀杆，不含切削头）：送布摆轴 F、抬牙摆轴 L、调节器轴（位置读 G4/送布机构.json）
_g = json.load(open(os.path.join(os.getcwd(), "docs/设计/WQ-LS/G4/送布机构.json"), encoding="utf-8"))["geo"]
(fy, fz), (ly, lz), (gy, gz) = _g["Fr"], _g["Lr"], _g["G"]
tools.update({
    "送布摆轴前孔镗杆 Ø12（B 0°，左端壁 Ø16 工艺孔进，到 x 31）": (cylx(6, -400, 31, fy, fz), [low, up]),
    "送布摆轴后孔镗杆 Ø12（B 180°，右端壁、右横筋 Ø16 工艺孔进，到 x 313）": (cylx(6, 313, 600, fy, fz), [low, up]),
    "调节器孔加长钻 / 铰刀 Ø9.4 刀体（B 180°，Ø14 工艺孔进，到 x 313）": (cylx(4.7, 313, 600, gy, gz), [low, up]),
    "抬牙摆轴后孔镗杆 Ø12（B 0°，左端壁 Ø18 工艺孔、前孔进，到 x 93）": (cylx(6, -400, 93, ly, lz), [low, up]),
    "抬牙摆轴前孔镗杆 Ø14（B 0°，左端壁 Ø18 工艺孔进，到 x 22）": (cylx(7, -400, 22, ly, lz), [low, up]),
})
for i, (px, py) in enumerate(((315.8, 7.0), (380.2, 66.0)), 1):
    # 刀具从机座底面以下 −80 向上，止于下件销孔凸台下端 z −16（再往上是切削区）
    tools[f"锥销孔 {i}：刀杆 Ø10.8 从机座底下向上"] = (cylz(5.4, -80, -16.5, px, py), [low])
out = {}
for name, (t, hs) in tools.items():
    d = min(t.distToShape(h)[0] for h in hs)
    out[name] = round(d, 2)
    print(name, round(d, 2))
# 面板口（机头左端 x −60 处）的通道：在 x −55 处截机头，看 y、z 的空当
sec = up.common(Part.makeBox(1, 300, 300, V(-56, -150, 0)))
bb = sec.BoundBox
out["_faceplate_section_bbox"] = [round(bb.YMin, 1), round(bb.YMax, 1), round(bb.ZMin, 1), round(bb.ZMax, 1)]
json.dump(out, open(os.environ.get("WQ_OUT", "/tmp/access.json"), "w"), ensure_ascii=False, indent=1)
print('{"ok": true}')
