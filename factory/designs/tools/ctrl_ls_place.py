# -*- coding: utf-8 -*-
"""平缝机控制器 CTRL-LS 的布局（第 159 轮 159d2b）：分区 + 大件定位 + 其余按功能块排，结果写进设计描述 board.placement。

    python3 ctrl_ls_place.py          # 算布局、写回 ../ctrl-ls/design.yaml 的 board.placement（只改这一段）

做法：板子分成几个区（交流输入、校正、辅助电源、逆变、执行器、主控、隔离面板口），散热器边（上边）一排放整流桥、升压管、
升压二极管、功率模块（159c：电控箱顶板当散热器）；接插件靠板边；其余器件在自己功能块的区里按位号顺序一行一行排（行内按外框宽度，
互不重叠、留 1.2 mm 间隙）。写回后人可以在 KiCad 里挪，再用 wqeda.readback 读回设计描述。示例设计，未经硬件验证。"""
from __future__ import annotations

import os
import re
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ctrl_ls as D  # noqa: E402

FPDIR = "/usr/share/kicad/footprints"
LOCAL = os.path.join(os.path.dirname(HERE), "libs")
W, H = D.X["board_mm"]
GAP = 1.2
EDGE = 1.0

# 区：功能块 → [(x0, y0, x1, y1)]（可以几块）
REGIONS = {
    "mains": [(EDGE, 24, 62, 51), (45, 52, 62, 75)],
    "aux": [(41, 77, 62, H - EDGE), (EDGE, 115, 41, H - EDGE)],
    "pfc": [(62, 9, 146, 33), (62, 112, 146, 124)],
    "servo": [(146, 30.5, 232, 37.5), (146, 70, W - EDGE, 84)],
    "act": [(146, 86, W - EDGE, 118), (146, 120, 204, 136)],
    "comm": [(211, 119, W - EDGE, H - 10)],
    "io": [(62, 126, 146, 138), (62, 112, 146, 124)],
}
# 跨隔离带的器件按引脚位置定（器件原点位置 x, y 和角度）：数字隔离器两排脚分在带两边；隔离电源 2、3 脚之间是带的收窄处
B = D.BARRIER
FIXED_POS = {"U601": (B["x"], 124.0, 0), "U602": (B["x"] - 3.81, 132.0, 0), "C601": (B["x"] - 6.5, 120.5, 90),
             "C603": (B["x"] - 9.0, 128.0, 90)}
# 大件、板边件：外框左上角 (x, y) 和角度
FIXED = {
    # 散热器边（上边）：整流桥、升压管、升压二极管、功率模块的散热面朝上边
    "BR101": (64, EDGE, 0), "C104": (64, 8, 0), "Q201": (90, EDGE, 0), "D201": (110, EDGE, 0), "U401": (148, EDGE, 180),
    "J101": (EDGE, 2, 90), "F101": (14, 2, 0), "J401": (W - 12.5, 4, 90),
    "L101": (EDGE, 53, 0), "K101": (EDGE + 44, 2, 0),
    "L201": (64, 34, 0), "C221": (147, 38.5, 0), "C222": (179, 38.5, 0), "C223": (W - 33, 38.5, 0),
    # Y 电容分开放（一只接相线、一只接零线，两只的保护地脚之外隔开 4 mm 以上）
    "C102": (16, 22, 90), "C103": (16, 38, 90),
    "T301": (EDGE + 1, 77, 0),
    "J501": (148, H - 10.5, 0), "J502": (186, H - 8, 0), "J601": (W - 34, H - 8, 0),
    "J701": (66, H - 8, 0), "J702": (93, H - 8, 0), "U10": (110, 127, 0),
}


def load(fpid):
    lib, name = fpid.split(":", 1)
    d = os.path.join(LOCAL if lib == "wq" else FPDIR, lib + ".pretty")
    f = pcbnew.FootprintLoad(d, name)
    if f is None:
        raise KeyError(fpid)
    return f


def bbox(fpid, rot):
    """器件在原点、转 rot 度时的外框（含丝印与安装面，mm）：(左, 上, 宽, 高)"""
    f = load(fpid)
    f.SetOrientationDegrees(rot)
    b = f.GetBoundingBox(False, False)
    mm = pcbnew.ToMM
    return mm(b.GetX()), mm(b.GetY()), mm(b.GetWidth()), mm(b.GetHeight())


def overlaps(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def main():
    place, used = {}, [(hx - 8, hy - 8, hx + 8, hy + 8) for hx, hy in D.X["holes"]]   # 安装孔周围留空（孔焊盘 + 4 mm）
    bw = B["w"] / 2 + 1.0                                                                       # 隔离带两边再各留 1 mm
    used += [(B["x"] - bw, B["y"] - bw, B["x"] + bw, H), (B["x"] - bw, B["y"] - bw, W, B["y"] + bw)]
    parts = {p["ref"]: p for p in D.PARTS}
    for ref, (x, y, rot) in FIXED_POS.items():
        bx, by, bw_, bh = bbox(parts[ref]["fp"], rot)
        place[ref] = (round(x, 2), round(y, 2), rot, "F")
        used.append((x + bx, y + by, x + bx + bw_, y + by + bh))
    for ref, (x, y, rot) in FIXED.items():
        bx, by, bw, bh = bbox(parts[ref]["fp"], rot)
        place[ref] = (round(x - bx, 2), round(y - by, 2), rot, "F")
        used.append((x, y, x + bw, y + bh))
    order = {k: [p for p in D.PARTS if p["sheet"] == k and p["ref"] not in FIXED and p["ref"] not in FIXED_POS] for k in REGIONS}
    left = []
    for k, plist in order.items():
        queue = list(plist)
        for (x0, y0, x1, y1) in REGIONS[k]:
            cx, cy, rowh = x0, y0, 0.0
            rest = []
            for p in queue:
                bx, by, bw, bh = bbox(p["fp"], 0)
                ok = False
                while cy + bh <= y1:
                    if cx + bw > x1:
                        cx, cy, rowh = x0, cy + rowh + GAP, 0.0
                        continue
                    r = (cx, cy, cx + bw, cy + bh)
                    hit = next((u for u in used if overlaps(r, (u[0] - GAP, u[1] - GAP, u[2] + GAP, u[3] + GAP))), None)
                    if hit:
                        cx = hit[2] + GAP
                        continue
                    ok = True
                    break
                if not ok:
                    rest.append(p)
                    continue
                place[p["ref"]] = (round(cx - bx, 2), round(cy - by, 2), 0, "F")
                used.append(r)
                cx += bw + GAP
                rowh = max(rowh, bh)
            queue = rest
        left += [p["ref"] for p in queue]
    if left:
        raise SystemExit("放不下：" + " ".join(left))
    write(place)
    print("摆好 {} 个器件，写回 design.yaml".format(len(place)))


def write(place):
    """只改 design.yaml 的 board.placement 段（其余原样，注释也在）"""
    path = D.DESIGN_PATH
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    body = "  placement:\n" + "".join(
        "    {}: [{:g}, {:g}, {:g}, {}]\n".format(ref, x, y, r, s) for ref, (x, y, r, s) in sorted(place.items(), key=lambda kv: _key(kv[0])))
    if re.search(r"(?m)^  placement:\n", txt):
        txt = re.sub(r"(?ms)^  placement:\n(?:    .*\n)*", body, txt)
    else:
        txt = txt.rstrip("\n") + "\n" + body
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)


def _key(r):
    m = re.match(r"([A-Z]+)(\d+)", r)
    return (m.group(1), int(m.group(2))) if m else (r, 0)


if __name__ == "__main__":
    main()
