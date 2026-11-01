"""本章共用：程序画出的“人脸”灰度图（40×32 像素），不用任何真人照片。以下划线开头，构建时不单独运行。

每张脸由一组随机参数决定：脸的宽窄、长短，肤色深浅，头发的多少，两眼的间距、大小和高低，眉毛的高低，
鼻子的长短，嘴的宽窄和弯曲，以及从左边或右边照来的光。像素值 0 为黑、1 为白。
"""
import numpy as np

H, W = 40, 32
_y, _x = np.mgrid[0:H, 0:W].astype(float)
_y = (_y + 0.5 - H / 2) / (H / 2)            # −1（上）… 1（下）
_x = (_x + 0.5 - W / 2) / (W / 2)            # −1（左）… 1（右）


def _blob(cx, cy, rx, ry):
    return np.exp(-(((_x - cx) / rx) ** 2 + ((_y - cy) / ry) ** 2) ** 2)


def _blur(A):
    k = np.array([1, 4, 6, 4, 1], float) / 16
    A = np.apply_along_axis(lambda r: np.convolve(np.pad(r, 2, mode="edge"), k, "valid"), 1, A)
    return np.apply_along_axis(lambda c: np.convolve(np.pad(c, 2, mode="edge"), k, "valid"), 0, A)


def face(p):
    """p：参数字典。"""
    img = np.full((H, W), 0.55)
    head = ((_x / p["fw"]) ** 2 + ((_y - 0.05) / p["fh"]) ** 2) <= 1
    img[head] = p["skin"]
    hair = head & (_y < -p["fh"] + p["hair"])
    img[hair] = 0.18
    for s in (-1, 1):
        ex = s * p["es"]
        img -= 0.55 * _blob(ex, p["ey"], p["er"], p["er"] * 0.6)                         # 眼睛
        brow = (np.abs(_x - ex) < p["er"] * 1.4) & (np.abs(_y - (p["ey"] - p["bh"])) < 0.035)
        img[brow] -= 0.35                                                                  # 眉毛
    img -= 0.15 * _blob(0.06, p["ey"] + p["nl"], 0.07, 0.10)                              # 鼻侧的阴影
    mx = np.linspace(-p["mw"], p["mw"], 40)
    for x0 in mx:
        y0 = p["my"] + p["mc"] * (1 - (x0 / p["mw"]) ** 2)
        img -= 0.06 * _blob(x0, y0, 0.05, 0.035)                                           # 嘴
    img *= 1 + p["light"] * _x                                                             # 侧光
    return np.clip(_blur(img), 0, 1)


def random_params(rng):
    return {"fw": rng.uniform(0.62, 0.80), "fh": rng.uniform(0.72, 0.86), "skin": rng.uniform(0.62, 0.90),
            "hair": rng.uniform(0.15, 0.45), "es": rng.uniform(0.24, 0.34), "er": rng.uniform(0.07, 0.11),
            "ey": rng.uniform(-0.18, -0.06), "bh": rng.uniform(0.12, 0.20), "nl": rng.uniform(0.22, 0.34),
            "mw": rng.uniform(0.16, 0.30), "my": rng.uniform(0.40, 0.52), "mc": rng.uniform(-0.05, 0.08),
            "light": rng.uniform(-0.25, 0.25)}


def faces(n, seed):
    rng = np.random.default_rng(seed)
    return np.array([face(random_params(rng)).ravel() for _ in range(n)])


def not_faces(seed=5):
    """不是脸的图：一个齿轮的轮廓、一片随机纹理、一张只有亮度渐变的图。"""
    rng = np.random.default_rng(seed)
    r = np.hypot(_x * W / H, _y)
    a = np.arctan2(_y, _x * W / H)
    gear = np.where(r < 0.62 + 0.08 * (np.cos(12 * a) > 0), 0.35, 0.8)
    gear[r < 0.18] = 0.8
    tex = np.clip(0.55 + 0.25 * _blur(rng.standard_normal((H, W))), 0, 1)
    grad = 0.3 + 0.4 * (_x + 1) / 2
    return np.array([_blur(gear).ravel(), tex.ravel(), grad.ravel()])
