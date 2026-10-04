"""第 4 章共用：检测相机的合成测试图（与 code/runs/run4_1/gray.cu 完全相同的生成规则与灰度公式）。以下划线开头，构建时不单独运行。"""
import numpy as np

W, H, THR = 3840, 2160, 40


def frame():
    """RGB 各 8 位的一帧：渐变底色，中心在（第 1000 行，第 2000 列）、半径 60 像素的暗斑。"""
    r, c = np.mgrid[0:H, 0:W]
    spot = (r - 1000) ** 2 + (c - 2000) ** 2 < 60 * 60
    rgb = np.empty((H, W, 3), np.uint8)
    rgb[..., 0] = np.where(spot, 20, 120 + c % 100)
    rgb[..., 1] = np.where(spot, 25, 130 + r % 80)
    rgb[..., 2] = np.where(spot, 30, 140)
    return rgb


def gray(rgb):
    """与核函数相同：Y = 0.299 R + 0.587 G + 0.114 B，单精度计算，加 0.5 取整。"""
    f = rgb.astype(np.float32)
    v = np.float32(0.299) * f[..., 0] + np.float32(0.587) * f[..., 1] + np.float32(0.114) * f[..., 2]
    return (v + np.float32(0.5)).astype(np.uint8)
