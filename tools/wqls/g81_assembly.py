"""G8.1 装配顺序：按总装顺序一步步把零件沿装入路径推进去，查路上会不会撞到机壳和已经装好的零件。

    python3 tools/wqls/g81_assembly.py <整机目录（*.stl、frames.json）> <机壳上件 stl> <机壳下件 stl> <输出 json>

做法：
- 每一步的零件从路径起点出发，每 2 mm 走一次（路径是离装好位置的一串偏移，最后一点是装好的位置）；连杆还有“到位后绕曲柄销摆回来”一段；
- 每个位置在移动零件表面取点（每个零件 1500 点），算这些点在机壳、已装零件里面多深（带符号距离）；穿透 > 0.3 mm 算撞。
  （第一版用 FCL 的接触深度，贴着的平面也报十几毫米，不可信，改为表面取点。）
- 本来就要贴着滑进去的配合（销进孔、轴进轴承、针杆进导套、螺钉进螺孔……）写在每一步的 slide 里，不算撞；
- 运动件的摆放：φ 写数字就按那个主轴转角；写 "auto" 就试 0°、90°、180°、270°，取路上走得通的（装的时候先转手轮到这个角）。
  已装的运动件也按同一个转角摆。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import trimesh

PEN = 0.3
NPT = 1500
W = -110.0   # 从前窗口外面进来（y 方向）
AUTO = (0, 90, 180, 270)

# 机头里的上导套座、压脚杆上导套座顶在 z 182，挡住了从面板口沿轴线推 Ø40 轴承、Ø35 轴套、曲柄的路；上轴的轴肩 Ø22 过不了电机座的 Ø20 轴过孔。
# 所以：上轴从面板口（左边）穿进去；轴承、中间轴套、曲柄、挑线杆、连杆都从前窗口（x −38…30、z 120…234）放进来，到 x ≥ 5 再沿轴线推。
# 每一步：(步骤, 零件, 路径, φ, 允许贴着滑的配合 [(本步零件, 已装零件)], 连杆摆动, 说明)
SEQ = [
    ("滑块导轨（针杆组、压脚杆组之前）", ["slide_rail"], [(-14, W, 12), (-14, 0, 12), (0, 0, 12), (0, 0, 0)], 0, [], False,
     "从前窗口伸进来：先往左 14、抬高 12（避开窗口右下角的圆角），进去后往右推到前轴承座下的竖筋上，再放下"),
    ("导轨螺钉 2 个", ["rail_screws"], [(-160, 0, 0), (0, 0, 0)], 0, [("rail_screws", "casting_upper"), ("rail_screws", "slide_rail")], False,
     "螺丝刀从面板口沿 x 伸进来（针杆、压脚杆还没装）"),
    ("立柱里的同步带轮、送布偏心（等上轴穿过）", ["pulley_upper", "feed_ecc"], [(0, 0, -60), (0, 0, 0)], 0, [], False,
     "从立柱下面的开口放进去；后轴承 6201-2RS 从立柱里面压进座孔（三维没画后轴承）"),
    ("上轴中间含油轴套", ["bush_mid"], [(-158, W, 0), (-158, 0, 0), (0, 0, 0)], 0, [("bush_mid", "casting_upper")], False,
     "从前窗口放进来（x 4.5…29.5），用长压杆沿轴线穿过前轴承孔 Ø40，压进中间轴套座 Ø35"),
    ("上轴", ["shaft"], [(-470, 0, 0), (0, 0, 0)], 0, [("shaft", "bush_mid"), ("shaft", "pulley_upper"), ("shaft", "feed_ecc"), ("shaft", "casting_upper")], False,
     "从面板口（左边）穿进去，经中间轴套、立柱里的带轮和偏心、后轴承"),
    ("前轴承 6203-2RS", ["bearing_front"], [(-32.5, W, 0), (-32.5, 0, 0), (0, 0, 0)], 0, [("bearing_front", "shaft"), ("bearing_front", "casting_upper")], False,
     "从前窗口放进来，套到轴端，沿轴线压到轴肩、压进轴承座"),
    ("曲柄（带曲柄销、左旋螺钉、挑线杆滚针组件）", ["crank", "crank_pin", "crank_screws", "cage_lever"], [(-10, W, 0), (-10, 0, 0), (0, 0, 0)], "auto",
     [("crank", "shaft")], False, "机外先装好；从前窗口放进来，往右套到轴端 Ø17 上，拧紧定螺钉"),
    ("挑线杆", ["lever"], [(-14, W, 0), (-14, 0, 0), (0, 0, 0)], "auto", [("lever", "cage_lever"), ("lever", "crank_pin")], False,
     "从前窗口放进来，往右套到曲柄销的滚针上"),
    ("连杆（带滚针组件）", ["rod", "cage_rod"], [(-12, W, 0), (-12, 0, 0), (0, 0, 0)], "auto", [("rod", "crank_pin"), ("cage_rod", "crank_pin")], True,
     "连杆先转成水平朝前（小头朝前窗口），从前窗口放进来，往右套到曲柄销上，再往下摆到工作位置"),
    ("滑块", ["slide_block"], [(0, 0, 30), (0, 0, 0)], "auto", [("slide_block", "slide_rail")], False, "从导轨上端放进导轨"),
    ("针杆连接块（连接销穿过连杆小头、滑块）", ["nb_link"], [(-12, W, 0), (-12, 0, 0), (0, 0, 0)], "auto", [("nb_link", "rod"), ("nb_link", "slide_block")], False,
     "从前窗口放进来，往右把销穿过连杆小头和滑块"),
    ("针杆", ["needle_bar"], [(0, 0, 200), (0, 0, 0)], "auto", [("needle_bar", "nb_bushes"), ("needle_bar", "nb_link"), ("needle_bar", "casting_upper")], False,
     "从机头顶 Ø12 孔插下去，穿过上导套、连接块、下导套"),
    ("针夹", ["needle_clamp"], [(0, 0, -40), (0, 0, 0)], "auto", [("needle_clamp", "needle_bar")], False, "从下面套到针杆下端"),
    ("紧针螺钉", ["clamp_screw"], [(20, 0, 0), (0, 0, 0)], "auto", [("clamp_screw", "needle_clamp"), ("clamp_screw", "needle_bar")], False, "从右边拧进针夹"),
    ("机针", ["needle"], [(0, 0, -40), (0, 0, 0)], "auto", [("needle", "needle_clamp"), ("needle", "needle_bar"), ("needle", "clamp_screw")], False,
     "从下面插进针夹"),
    ("机头顶橡胶塞", ["nb_plug"], [(0, 0, 30), (0, 0, 0)], 0, [("nb_plug", "casting_upper")], False, ""),
    ("挑线摇杆和销（支点销之前）", ["rocker", "pin_M"], [(0, W, -8), (0, 0, -8), (0, 0, 0)], "auto",
     [("pin_M", "lever"), ("pin_M", "rocker"), ("rocker", "lever")], False,
     "从前窗口在装好的 x 位置伸进来（顶比窗口上沿高，先放低 8），到位后抬起，销穿进挑线杆"),
    ("摇杆支点销（压进机头顶吊下来的销座，穿过摇杆）", ["stud_Q"], [(-25, 0, 0), (0, 0, 0)], "auto", [("stud_Q", "casting_upper"), ("stud_Q", "rocker")], False,
     "从前窗口伸进去，沿 x 穿过销座、摇杆孔压到位（摇杆在销座右边，只能先放摇杆再穿销）"),
    ("分油块", ["oil_block", "oil_screws"], [(0, 0, 40), (0, 0, 0)], 0, [("oil_screws", "casting_upper"), ("oil_screws", "oil_block")], False,
     "顶盖拆下后从上面放"),
]


def M44(m):
    return np.array(m, float).reshape(4, 4)


def rotx(p, deg):
    a = np.radians(deg)
    T = np.eye(4)
    T[1:3, 1:3] = [[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]]
    T[:3, 3] = np.array(p) - T[:3, :3] @ np.array(p)
    return T


def main():
    d, hu, hl, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4])
    F = json.loads((d / "frames.json").read_text())
    fr = F["frames"] if isinstance(F, dict) else F
    byphi = {f["phi"]: f for f in fr}
    raw = {"casting_upper": trimesh.load(hu), "casting_lower": trimesh.load(hl), "nb_bushes": trimesh.load(d / "nb_bushes.stl")}
    installed = ["casting_upper", "casting_lower", "nb_bushes"]     # 针杆导套：直孔压入，先当作已压好
    cache = {}

    def posed(k, ph):
        key = (k, ph if k in byphi[ph]["M"] and byphi[ph]["M"][k] else None)
        if key not in cache:
            m = raw[k].copy()
            if key[1] is not None:
                m.apply_transform(M44(byphi[ph]["M"][k]))
            cache[key] = (m, trimesh.proximity.ProximityQuery(m))
        return cache[key]

    def pen(pts_by_part, allow, ph):
        worst = (0.0, None)
        for k, pts in pts_by_part.items():
            lo, hi = pts.min(0) - 1, pts.max(0) + 1
            for o in installed:
                if (k, o) in allow:
                    continue
                m, pq = posed(o, ph)
                b = m.bounds
                if (lo > b[1]).any() or (hi < b[0]).any():
                    continue
                sel = pts[((pts >= b[0] - 1) & (pts <= b[1] + 1)).all(1)]
                if not len(sel):
                    continue
                sd = np.concatenate([pq.signed_distance(sel[i:i + 400]) for i in range(0, len(sel), 400)])
                if sd.max() > worst[0]:
                    worst = (float(sd.max()), (k, o))
        return worst

    res = []
    start = int(os.environ.get("WQ_FROM", "0"))                    # 只复查第 start 步以后（前面的直接当作已装好）
    for n_step, (name, parts, path, phi, slide, swing, note) in enumerate(SEQ):
        if n_step < start:
            for k in parts:
                raw.setdefault(k, trimesh.load(d / f"{k}.stl"))
            installed.extend(parts)
            continue
        allow = set(slide)
        for k in parts:
            raw.setdefault(k, trimesh.load(d / f"{k}.stl"))
        samp = {k: trimesh.sample.sample_surface(raw[k], NPT, seed=1)[0] for k in parts}
        offs = []
        for a_, b_ in zip(path[:-1], path[1:]):
            a_, b_ = np.array(a_, float), np.array(b_, float)
            n_ = max(1, int(np.ceil(np.linalg.norm(b_ - a_) / 2.0)))
            offs += [a_ + (b_ - a_) * j / n_ for j in range(n_)]
        offs.append(np.zeros(3))
        best = None
        for ph in (AUTO if phi == "auto" else [phi]):
            f = byphi[ph]
            T = {k: (M44(f["M"][k]) if k in f["M"] and f["M"][k] else np.eye(4)) for k in parts}
            seq = [(o, np.eye(4)) for o in offs]
            if swing:                                           # 连杆：先绕曲柄销转成小头朝前（−y），到位后摆回来
                pc = (M44(f["M"]["crank_pin"]) @ np.r_[raw["crank_pin"].centroid, 1])[:3]
                small = (T["rod"] @ np.r_[raw["rod"].centroid, 1])[:3]
                ang = 180.0 - np.degrees(np.arctan2(small[2] - pc[2], small[1] - pc[1]))
                ang = (ang + 180) % 360 - 180
                seq = [(o, rotx(pc, ang)) for o in offs]
                n_ = max(2, int(abs(ang) / 3))
                seq += [(np.zeros(3), rotx(pc, ang * (1 - j / n_))) for j in range(1, n_ + 1)]
            worst = (0.0, None, None)
            for o, R in seq:
                pts = {}
                for k in parts:
                    G = R @ T[k]
                    pts[k] = (G[:3, :3] @ samp[k].T).T + G[:3, 3] + o
                p = pen(pts, allow, ph)
                if p[0] > worst[0]:
                    worst = (p[0], p[1], [round(float(v), 1) for v in o])
            if best is None or worst[0] < best[0][0]:
                best = (worst, ph)
            if best[0][0] <= PEN:
                break
        worst, ph = best
        ok = worst[0] <= PEN
        res.append(dict(step=name, parts=parts, phi=ph, ok=ok, note=note,
                        worst=None if ok else dict(pen_mm=round(worst[0], 2), pair=list(worst[1]), offset=worst[2])))
        print(name, "φ", ph, "OK" if ok else res[-1]["worst"], flush=True)
        installed.extend(parts)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
