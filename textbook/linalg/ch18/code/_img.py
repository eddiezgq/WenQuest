"""第 18 章共用：一张 120×160 的灰度“齿轮照片”，由程序画出（不用外部图片），实验 18.4 用同一算法在浏览器里生成。

像素值 0 为黑、1 为白。画面：渐变的背景、齿轮的投影、18 个齿的齿轮、轮毂、带键槽的轴孔、四个螺栓孔，以及少量噪声。
噪声用整数线性同余发生器产生，浏览器里的 JavaScript 版逐像素得到相同的数。
"""
import math

import numpy as np

M, N = 120, 160


def _gear_mask(x, y, cx, cy):
    r = math.hypot(x - cx, y - cy)
    a = math.atan2(y - cy, x - cx)
    # 齿形：18 个梯形齿，齿根半径 40、齿顶半径 46
    ph = (a * 18 / (2 * math.pi)) % 1.0
    tooth = 1.0 if 0.18 < ph < 0.62 else (max(0.0, 1 - abs(ph - 0.18) / 0.08) if ph <= 0.18 else max(0.0, 1 - abs(ph - 0.62) / 0.08))
    rout = 40 + 6 * min(1.0, tooth * 1.6)
    return r <= rout, r, a


def gear_image() -> np.ndarray:
    A = np.zeros((M, N))
    seed = 20261002
    cx, cy = 80.0, 60.0
    for i in range(M):
        for j in range(N):
            x, y = j + 0.5, i + 0.5
            v = 0.80 + 0.14 * i / (M - 1)                         # 背景：上暗下亮
            if _gear_mask(x - 4, y - 4, cx, cy)[0]:               # 投影
                v -= 0.18
            inside, r, a = _gear_mask(x, y, cx, cy)
            if inside:
                v = 0.30 + 0.12 * math.cos(a - 0.8)               # 齿轮本体，左上方受光
                if r < 15:
                    v = 0.62                                      # 轮毂
                bolt = any(math.hypot(x - (cx + 26 * math.cos(k * math.pi / 2 + math.pi / 4)),
                                      y - (cy + 26 * math.sin(k * math.pi / 2 + math.pi / 4))) < 3.6 for k in range(4))
                key = abs(x - cx) < 2.2 and cy - 9.5 < y < cy
                if r < 7 or bolt or key:
                    v = 0.80 + 0.14 * i / (M - 1) - 0.18          # 透过孔看到的地面（在投影里）
            seed = (1103515245 * seed + 12345) % 2147483648
            v += 0.04 * (seed / 2147483648 - 0.5)                 # 噪声，均匀分布于 ±0.02
            A[i, j] = min(1.0, max(0.0, v))
    return A
