# -*- coding: utf-8 -*-
"""示例意匠图（第 70 轮）：程序生成，不用别人的作品。

一件提花毛衣前片：240 针；1+1 罗纹起口 40 行；两色提花大身（菱形格子）300 行；袖窿收针——每 4 行两边各收 1 针、收 15 次（60 行）；
再直织 60 行到肩。共 460 个意匠行。收针用虚拟实验 17-2 的写法：边上那枚针标“>”（左边）或“<”（右边），翻到里面一针上。
"""
from . import knitprog as KP

W = 240


def front_piece():
    rows = []
    for r in range(40):                                    # 罗纹
        rows.append([("K" if i % 2 == 0 else "P", 1) for i in range(W)])
    for r in range(300):                                   # 菱形提花：12 针 × 12 行一个花
        row = []
        for i in range(W):
            a, b = abs(i % 12 - 6), abs(r % 12 - 6)
            row.append(("K", 2 if a + b <= 3 else 1))
        rows.append(row)
    cut = 0
    for r in range(120):                                   # 袖窿收针，再直织到肩
        row = [(".", 1)] * W
        for i in range(cut, W - cut):
            a, b = abs(i % 12 - 6), abs((r + 300) % 12 - 6)
            row[i] = ("K", 2 if a + b <= 3 else 1)
        if r < 60 and r % 4 == 3:
            row[cut] = (">", 1)
            row[W - 1 - cut] = ("<", 1)
            cut += 1
        rows.append(row)
    return rows


def front_text():
    return "# 问渠示例意匠图：提花前片 240 针 × 460 行（第一行先织）\n" + KP.to_text(front_piece())
