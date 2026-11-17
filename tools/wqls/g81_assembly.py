"""G8.1 装配顺序：按总装顺序一步步把零件沿装入方向推进去，查推进的路上会不会撞到机壳和已经装好的零件。

    python3 tools/wqls/g81_assembly.py <整机目录（*.stl、frames.json）> <机壳上件 stl> <机壳下件 stl> <输出 json>

做法：每一步的零件从“装好的位置 − 方向 × 行程”出发，每 1 mm 推进一次，直到装好的位置；每个位置用 FCL 查与已装零件
（含机壳）是否相交。压入、套装的配合面本来就贴着（零间隙），网格误差会报很浅的“相交”，所以穿透深度 ≤ 0.3 mm 的不算。
本步零件在装好位置时与已装零件的接触（装配关系）也不算——只看推进的路上。
运动件按这一步写的主轴转角 φ 摆好（装的时候先转手轮把曲柄转到这个位置）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import trimesh

PEN = 0.3

# (步骤, 零件, 路径（离装好位置的偏移，依次经过这些点，最后一个是 (0,0,0)）, 主轴转角 φ, 说明)
# 机头里的上导套座、压脚杆上导套座顶在 z 182，挡住了从面板口沿轴线推 Ø40 轴承、Ø35 轴套的路；
# 所以轴承、中间轴套、曲柄组件都从前窗口（x −38…30、z 120…234）伸进来，到了 x ≥ 5（上导套座 D 形平面以外）再沿轴线推。
W = -110.0   # 从前窗口外面进来
SEQ = [
    ("滑块导轨（针杆组、压脚杆组之前）", ["slide_rail"], [(-9, W, 8), (-9, 0, 8), (0, 0, 8), (0, 0, 0)], 0,
     "从前窗口伸进来（低 8 mm 进不了窗口，先抬高 8），再往右推到前轴承座下的竖筋上"),
    ("导轨螺钉 2 个", ["rail_screws"], [(-160, 0, 0), (0, 0, 0)], 0, "螺丝刀从面板口沿 x 伸进来（针杆、压脚杆还没装）"),
    ("上轴中间含油轴套", ["bush_mid"], [(-158, W, 0), (-158, 0, 0), (0, 0, 0)], 0,
     "从前窗口放进来（x 4.5…29.5），再用长压杆沿轴线穿过前轴承孔 Ø40 推到中间轴套座 Ø35"),
    ("前轴承 6203-2RS", ["bearing_front"], [(-32.5, W, 0), (-32.5, 0, 0), (0, 0, 0)], 0, "从前窗口放进来，沿轴线压进轴承座"),
    ("曲柄（带曲柄销、左旋螺钉、挑线杆滚针组件）", ["crank", "crank_pin", "crank_screws", "cage_lever"], [(-10, W, 0), (-10, 0, 0), (0, 0, 0)], 270,
     "机外先装好；曲柄销朝后（φ 270），从前窗口放进来，再往右 10 对准轴线"),
    ("上轴", ["shaft"], [(460, 0, 0), (0, 0, 0)], 270, "从电机端穿过后轴承孔、中间轴套、前轴承内圈、曲柄孔；然后拧曲柄紧定螺钉"),
    ("挑线杆", ["lever"], [(-30, W, 0), (-30, 0, 0), (0, 0, 0)], 270, "从前窗口放进来，往右套到曲柄销的滚针上"),
    ("连杆（带滚针组件）", ["rod", "cage_rod"], [(-20, W, 0), (-20, 0, 0), (0, 0, 0)], 270, "从前窗口放进来，往右套到曲柄销上"),
    ("滑块", ["slide_block"], [(0, 0, 30), (0, 0, 0)], 0, "曲柄转到 φ 0，从导轨上端放进导轨"),
    ("针杆连接块（连接销穿过连杆小头、滑块）", ["nb_link"], [(-25, W, 0), (-25, 0, 0), (0, 0, 0)], 0, "从前窗口放进来，往右把销穿过连杆小头和滑块"),
    ("针杆", ["needle_bar"], [(0, 0, 200), (0, 0, 0)], 0, "从机头顶 Ø12 孔插下去，穿过上导套、连接块、下导套"),
    ("针夹和紧针螺钉", ["needle_clamp", "clamp_screw"], [(0, 0, -40), (0, 0, 0)], 0, "从下面套到针杆下端"),
    ("机针", ["needle"], [(0, 0, -40), (0, 0, 0)], 0, "从下面插进针夹"),
    ("机头顶橡胶塞", ["nb_plug"], [(0, 0, 30), (0, 0, 0)], 0, ""),
    ("挑线摇杆、销", ["rocker", "pin_M", "stud_Q"], [(0, W, 0), (0, 0, 0)], 0, "从前窗口"),
    ("分油块", ["oil_block", "oil_screws"], [(0, 0, 40), (0, 0, 0)], 0, "顶盖拆下后从上面放"),
]


def M44(m):
    return np.array(m, float).reshape(4, 4)


def main():
    d, hu, hl, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4])
    F = json.loads((d / "frames.json").read_text())
    fr = F["frames"] if isinstance(F, dict) else F
    byphi = {f["phi"]: f for f in fr}
    base = trimesh.collision.CollisionManager()
    base.add_object("casting_upper", trimesh.load(hu))
    base.add_object("casting_lower", trimesh.load(hl))
    base.add_object("nb_bushes", trimesh.load(d / "nb_bushes.stl"))
    res = []
    for name, parts, path, phi, note in SEQ:
        f = byphi[phi]
        pts = []
        for a_, b_ in zip(path[:-1], path[1:]):
            a_, b_ = np.array(a_, float), np.array(b_, float)
            n_ = max(1, int(np.ceil(np.linalg.norm(b_ - a_) / 1.0)))
            pts += [a_ + (b_ - a_) * k / n_ for k in range(n_)]
        pts = [q for q in pts if np.linalg.norm(q) > 0.4]
        movers = {}
        for k in parts:
            m = trimesh.load(d / f"{k}.stl")
            T = M44(f["M"][k]) if k in f["M"] and f["M"][k] else np.eye(4)
            movers[k] = (m, T)
        worst = (0.0, None, None)
        for q in pts:                                           # q = 离装好位置的偏移
            t = float(np.linalg.norm(q))
            mm = trimesh.collision.CollisionManager()
            for k, (m, T) in movers.items():
                S = np.eye(4)
                S[:3, 3] = q
                mm.add_object(k, m, transform=S @ T)
            hit, data = mm.in_collision_other(base, return_data=True)
            if hit:
                for c in data:
                    dep = c.depth
                    if dep > PEN and dep > worst[0]:
                        worst = (float(dep), sorted(c.names), [round(float(v), 1) for v in q], [round(float(v), 1) for v in c.point])
        ok = worst[1] is None
        res.append(dict(step=name, parts=parts, path=path, phi=phi, ok=ok, note=note,
                        worst=None if ok else dict(depth_mm=round(worst[0], 2), pair=worst[1], offset=worst[2], point=worst[3])))
        print(name, "OK" if ok else res[-1]["worst"])
        for k, (m, T) in movers.items():                        # 装好，加进已装零件
            base.add_object(k, m, transform=T)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
