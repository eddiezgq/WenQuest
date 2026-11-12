# -*- coding: utf-8 -*-
"""布线器（Freerouting）的两个限制和对应的做法（第 159 轮 159d2b，平缝机控制器 CTRL-LS 试出来的）：

1. 一个焊盘离同一器件上另一网络的焊盘比“两类网络之间的布线间距”还近时，布线器接不上这个焊盘
   （例：1206 分压电阻两脚 1.8 mm、要求 2.2 mm；整流桥两个交流脚 1.9 mm、相线↔零线要求 2.6 mm）。
   引脚间距是器件自己的事（由它的额定管），所以布线时两类之间的间距取“要求”和
   “这类器件引脚最小间距 − 0.05 mm”里小的那个；
   真正的安全要求另由安全距离检查（checks/safety.py）按铜间距量，过不了就在那里报。 → clamp_pairs
2. 布线器不会在引脚旁边把粗线收细：大电流线（交流 7.9 A 用 2.5 mm）进不了 5 mm 脚距的端子。
   分类可以写 route_mm（布线时的线宽，比 track_mm 细），布完再把每段线在有空的地方加宽到 track_mm，
   旁边没空的那几段保持细（只在引脚附近）。 → widen

纯几何计算，不联网、不调 AI。"""

from __future__ import annotations

import itertools

import pcbnew

STEP = 0.05


def _poly(ps):
    from shapely.geometry import Polygon

    o = ps.Outline(0)
    return Polygon([(pcbnew.ToMM(o.CPoint(i).x), pcbnew.ToMM(o.CPoint(i).y)) for i in range(o.PointCount())])


def pad_gaps(board, class_of):
    """{frozenset((类 A, 类 B)): 同一器件上两类焊盘之间的最小间距 mm, ...}；class_of(网络名) → 类名"""
    out = {}
    for fp in board.GetFootprints():
        pads = [(p, class_of(p.GetNetname())) for p in fp.Pads() if p.GetNetname()]
        for (p, a), (q, b) in itertools.combinations(pads, 2):
            if a == b or p.GetNetname() == q.GetNetname():
                continue
            g = _poly(p.GetEffectivePolygon()).distance(_poly(q.GetEffectivePolygon()))
            k = frozenset((a, b))
            if k not in out or g < out[k][0]:
                out[k] = (g, fp.GetReference())
    return out


def clamp_pairs(pairs, gaps, floor=0.2, margin=STEP):
    """[(A, B, 间距)] → (布线用的 [(A, B, 间距)], 说明 [(A, B, 要求, 布线用, 卡在哪个器件)])"""
    out, notes = [], []
    for a, b, c in pairs:
        g = gaps.get(frozenset((a, b)))
        if g and g[0] - margin < c:
            r = max(floor, round((g[0] - margin) // STEP * STEP, 2))
            out.append((a, b, r))
            notes.append((a, b, c, r, g[1]))
        else:
            out.append((a, b, c))
    return out, notes


def widen(board, targets, clearance):
    """targets = {网络名: 目标线宽 mm}；clearance(网络 A, 网络 B) → 要求间距 mm。
    每段线按“离别的网络的铜还有多远”加宽，最多到目标线宽；别的网络若也要加宽，按它加宽后的宽度算（偏保守）。
    返回 (加宽到目标的段数, 只加宽一部分的段数, 没动的段数)"""
    from shapely import STRtree
    from shapely.geometry import LineString, Point

    layers = {}

    def add(layer, net, geom, grow=0.0):
        layers.setdefault(layer, []).append((net, geom.buffer(grow) if grow else geom))

    for fp in board.GetFootprints():
        for p in fp.Pads():
            g = _poly(p.GetEffectivePolygon())
            for lid in p.GetLayerSet().CuStack():
                add(lid, p.GetNetname(), g)
    segs = []
    for t in board.GetTracks():
        lid, net = t.GetLayer(), t.GetNetname()
        if t.GetClass() == "PCB_VIA":
            g = Point(pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y)).buffer(
                pcbnew.ToMM(t.GetWidth()) / 2
            )
            for l2 in t.GetLayerSet().CuStack():
                add(l2, net, g)
            continue
        line = LineString(
            [
                (pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y)),
                (pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y)),
            ]
        )
        w = pcbnew.ToMM(t.GetWidth())
        add(lid, net, line.buffer(max(w, targets.get(net, w)) / 2))
        if net in targets and targets[net] > w + 1e-6:
            segs.append((t, line, w))
    for z in board.Zones():
        if z.GetIsRuleArea() or not z.GetNetname():
            continue
        for lid in z.GetLayerSet().CuStack():
            fill = z.GetFilledPolysList(lid)
            for i in range(fill.OutlineCount()):
                o = fill.Outline(i)
                from shapely.geometry import Polygon

                pg = Polygon([(pcbnew.ToMM(o.CPoint(k).x), pcbnew.ToMM(o.CPoint(k).y)) for k in range(o.PointCount())])
                if pg.is_valid and not pg.is_empty:
                    add(lid, z.GetNetname(), pg)
    trees = {lid: (STRtree([g for _, g in v]), v) for lid, v in layers.items()}
    full = part = none = 0
    for t, line, w in segs:
        net, goal = t.GetNetname(), targets[t.GetNetname()]
        tree, items = trees[t.GetLayer()]
        half = goal / 2
        for i in tree.query(line.buffer(goal / 2 + 6.0)):
            onet, g = items[int(i)]
            if onet == net:
                continue
            half = min(half, line.distance(g) - clearance(net, onet))
        nw = max(w, min(goal, int(2 * half / STEP + 1e-9) * STEP))
        if nw >= goal - 1e-6:
            full += 1
        elif nw > w + 1e-6:
            part += 1
        else:
            none += 1
        t.SetWidth(pcbnew.FromMM(round(nw, 2)))
    return full, part, none
