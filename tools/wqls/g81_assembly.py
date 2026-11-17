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

# (步骤, 零件, 装入方向（零件往哪个方向移动）, 行程 mm, 主轴转角 φ, 说明)
SEQ = [
    # 针杆上、下导套不在这里推：两个是一个三维零件，上导套从机头顶 Ø12 孔往下压进 Ø10 座，下导套从机头底下往上压进 Ø12 座，都是直孔。
    # 先当作已经压好（加进已装零件）
    ("滑块导轨和两个导轨螺钉（针杆组装之前）", ["slide_rail", "rail_screws"], (1, 0, 0), 120, 0,
     "从机头左端面板口伸进去，贴到前轴承座下的竖筋上"),
    ("上轴中间含油轴套", ["bush_mid"], (1, 0, 0), 230, 0, "从前轴承孔 Ø40 用长压杆推到中间轴套座 Ø35"),
    ("曲柄组件（曲柄、曲柄销及左旋螺钉、两个滚针组件、连杆、挑线杆）", ["crank", "crank_pin", "crank_screws", "cage_rod", "cage_lever", "rod", "lever"],
     (1, 0, 0), 140, 180, "在机外先装成组件；从面板口放进机头，曲柄销转到下面（φ 180）"),
    ("上轴", ["shaft"], (-1, 0, 0), 460, 180, "从电机端穿过后轴承孔、中间轴套、曲柄孔，到前轴承座"),
    ("前轴承 6203-2RS", ["bearing_front"], (1, 0, 0), 60, 180, "从面板口压到轴上和轴承座里"),
    ("滑块、针杆连接块（套在连杆小头的销上）", ["slide_block", "nb_link", "link_screws"], (0, 0, -1), 60, 0,
     "从导轨上端放进导轨"),
    ("针杆", ["needle_bar"], (0, 0, -1), 200, 0, "从机头顶 Ø12 孔插下去，穿过上导套、连接块、下导套"),
    ("针夹和紧针螺钉", ["needle_clamp", "clamp_screw"], (0, 0, 1), 40, 0, "从下面套到针杆下端"),
    ("机针", ["needle"], (0, 0, 1), 40, 0, "从下面插进针夹"),
    ("机头顶橡胶塞", ["nb_plug"], (0, 0, -1), 30, 0, ""),
    ("挑线摇杆、销", ["rocker", "pin_M", "stud_Q"], (-1, 0, 0), 60, 0, "从面板口"),
    ("分油块", ["oil_block", "oil_screws"], (0, 0, -1), 40, 0, "顶盖拆下后从上面放"),
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
    for name, parts, u, L, phi, note in SEQ:
        f = byphi[phi]
        u = np.array(u, float)
        movers = {}
        for k in parts:
            m = trimesh.load(d / f"{k}.stl")
            T = M44(f["M"][k]) if k in f["M"] and f["M"][k] else np.eye(4)
            movers[k] = (m, T)
        worst = (0.0, None, None)
        for t in np.arange(L, 0.4, -1.0):                       # t = 离装好位置还有多远
            mm = trimesh.collision.CollisionManager()
            for k, (m, T) in movers.items():
                S = np.eye(4)
                S[:3, 3] = -u * t
                mm.add_object(k, m, transform=S @ T)
            hit, data = mm.in_collision_other(base, return_data=True)
            if hit:
                for c in data:
                    dep = c.depth
                    if dep > PEN and dep > worst[0]:
                        worst = (float(dep), sorted(c.names), float(t))
        ok = worst[1] is None
        res.append(dict(step=name, parts=parts, dir=list(u), travel=L, phi=phi, ok=ok, note=note,
                        worst=None if ok else dict(depth_mm=round(worst[0], 2), pair=worst[1], at_mm_before_home=worst[2])))
        print(name, "OK" if ok else res[-1]["worst"])
        for k, (m, T) in movers.items():                        # 装好，加进已装零件
            base.add_object(k, m, transform=T)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
