# -*- coding: utf-8 -*-
"""示例刺绣花样（第 69 轮）：程序生成，不用别人的作品。

logo：120 × 70 mm 的徽章——塔塔米填充的底、圆形填充、8 mm 宽的缎纹边框、4 mm 缎纹的星、走线的字条和轮廓，
六种颜色、约 1 万针。帮助的案例七、测试、网页“用示例花样”都用它。
"""
import math

from . import stitchfile as SF


def _fill_poly(inside, x0, x1, y0, y1, row=0.4, st=3.0):
    """塔塔米：一行行平行短针，相邻行错开半针；inside(x, y) 判断点在不在图形里"""
    pts = []
    y, k = y0 + row / 2, 0
    while y < y1:
        xs = [x0 + i * 0.25 for i in range(int((x1 - x0) / 0.25) + 1)]
        xs = [x for x in xs if inside(x, y)]
        if xs:
            a, b = xs[0], xs[-1]
            off = (st / 2) if k % 2 else 0.0
            row_pts = [a]
            x = a + st - off if off else a + st
            while x < b:
                row_pts.append(x)
                x += st
            row_pts.append(b)
            if k % 2:
                row_pts.reverse()
            pts += [(x, y) for x in row_pts]
            k += 1
        y += row
    return pts


def _satin_path(path, width, density=0.35):
    """沿一条中心线走缎纹：两边来回，针长 = 宽度"""
    out = []
    L = [0.0]
    for i in range(1, len(path)):
        L.append(L[-1] + math.dist(path[i - 1], path[i]))
    n = int(L[-1] / density)
    j = 0
    for i in range(n + 1):
        d = i * density
        while j < len(path) - 2 and L[j + 1] < d:
            j += 1
        seg = L[j + 1] - L[j] or 1
        t = (d - L[j]) / seg
        cx = path[j][0] + (path[j + 1][0] - path[j][0]) * t
        cy = path[j][1] + (path[j + 1][1] - path[j][1]) * t
        tx, ty = (path[j + 1][0] - path[j][0]) / seg, (path[j + 1][1] - path[j][1]) / seg
        side = 1 if i % 2 else -1
        out.append((cx - ty * width / 2 * side, cy + tx * width / 2 * side))
    return out


def _run(path, st=2.5):
    out = [path[0]]
    for i in range(1, len(path)):
        a, b = path[i - 1], path[i]
        m = max(1, math.ceil(math.dist(a, b) / st))
        out += [(a[0] + (b[0] - a[0]) * k / m, a[1] + (b[1] - a[1]) * k / m) for k in range(1, m + 1)]
    return out


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]


def logo_blocks():
    """六块：每块 (名字, 绝对坐标针位)；块之间跳步、换色"""
    W, H = 120.0, 70.0
    ins = 8.0
    bg = _fill_poly(lambda x, y: ins <= x <= W - ins and ins <= y <= H - ins and math.hypot(x - 38, y - 35) > 22.5, 0, W, 0, H, row=0.35, st=2.5)
    circ = _fill_poly(lambda x, y: math.hypot(x - 38, y - 35) <= 22, 14, 62, 11, 59, row=0.35, st=2.4)
    border = _satin_path(_rect(4, 4, W - 4, H - 4), 8.0)
    star = []
    P = [(38 + (16 if i % 2 == 0 else 7) * math.cos(math.pi / 2 + i * math.pi / 5), 35 + (16 if i % 2 == 0 else 7) * math.sin(math.pi / 2 + i * math.pi / 5))
         for i in range(10)]
    star = _satin_path(P + [P[0]], 4.0)
    lines = []
    for r in range(4):                      # 字条：四行走线
        y = 22 + r * 9
        lines += _run([(70, y), (106, y), (106, y + 2.5), (70, y + 2.5)], 2.0)
    outline = _run(_rect(9, 9, W - 9, H - 9), 2.5)
    return [("底", bg), ("圆", circ), ("边框缎纹", border), ("星", star), ("字条", lines), ("轮廓", outline)]


def records(blocks):
    recs = []
    x = y = 0.0
    for bi, (_, pts) in enumerate(blocks):
        if bi:
            recs.append((0.0, 0.0, "c"))
        sx, sy = pts[0]
        if math.hypot(sx - x, sy - y) > 0:
            recs.append((sx - x, sy - y, "j"))
        x, y = sx, sy
        for px, py in pts[1:]:
            recs.append((px - x, py - y, "s"))
            x, y = px, py
    return recs


def logo_dst():
    return SF.write_dst(records(logo_blocks()), label="WQ LOGO")
