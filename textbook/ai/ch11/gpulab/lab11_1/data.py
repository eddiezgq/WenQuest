"""实测用的数据：书中合成生成器（textbook/ai/ch11/code/_ch11.py）的**均衡版本**——四类（合格、划痕、压痕、锈斑）
各占约四分之一，每张图最多一个缺陷，尺寸 224×224，不带掩码与框。与书中产线分布（合格品占六成以上、
一张图可能有几处缺陷）不同：这里要比较的是三种训练方式，均衡数据让比较更干净；类别不平衡怎样处理见 11.8 节。
之所以在这里另放一份：实测在云端的机器上跑，只上传这个文件夹（第 14 轮附 4.4 节）。"""
import numpy as np
import torch

H = W = 224
CLASSES = ("无", "划痕", "压痕", "锈斑")
N_CLASS = len(CLASSES)


def _rng(seed):
    return np.random.default_rng(20261011 + seed)


def surface(rng):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    shade = 0.55 + 0.35 * np.cos((x / W - 0.5) * 2.2)
    grind = 0.018 * np.sin(y * 0.9 + rng.uniform(0, 6.3))
    return np.clip(shade + grind + rng.normal(0, 0.012, (H, W)), 0, 1).astype(np.float32)


def sample(seed):
    rng = _rng(seed)
    img = surface(rng)
    cls = int(rng.integers(0, N_CLASS))
    amp = float(rng.uniform(0.25, 1.0))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if cls == 1:                                            # 划痕
        x0, y0 = rng.uniform(20, W - 20), rng.uniform(20, H - 20)
        ang, ln = rng.uniform(0, np.pi), rng.uniform(40, 110)
        dx, dy = ln * np.cos(ang), ln * np.sin(ang)
        t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / (dx * dx + dy * dy), 0, 1)
        d = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
        wdt = rng.uniform(1.2, 3.0)
        img -= rng.uniform(0.22, 0.45) * amp * np.exp(-(d / wdt) ** 2) * (d < wdt)
    elif cls == 2:                                          # 压痕
        cx, cy, r = rng.uniform(25, W - 25), rng.uniform(25, H - 25), rng.uniform(6, 16)
        d = np.hypot(xx - cx, yy - cy)
        img -= rng.uniform(0.25, 0.45) * amp * np.exp(-(d / r) ** 2)
        img += rng.uniform(0.10, 0.20) * amp * np.exp(-((d - r) / (0.35 * r)) ** 2)
    elif cls == 3:                                          # 锈斑
        cx, cy = rng.uniform(30, W - 30), rng.uniform(30, H - 30)
        hit = np.zeros((H, W), bool)
        for _ in range(int(rng.integers(3, 7))):
            d = np.hypot(xx - cx - rng.normal(0, 7), yy - cy - rng.normal(0, 7))
            hit |= d < rng.uniform(7, 15)
        img -= rng.uniform(0.12, 0.26) * amp * hit * (1 + 0.3 * np.sin(xx * 0.18) * np.sin(yy * 0.22))
    return np.clip(img, 0, 1).astype(np.float32), cls


def tensors(n, start=0):
    """n 张图：返回 (N, 3, 224, 224) 的张量（三个通道相同，按 ImageNet 的均值方差归一）与标签。"""
    xs, ys = [], []
    mean, std = np.float32([0.485, 0.456, 0.406]), np.float32([0.229, 0.224, 0.225])
    for i in range(n):
        img, cls = sample(start + i)
        rgb = np.repeat(img[None], 3, 0)
        rgb = (rgb - mean[:, None, None]) / std[:, None, None]
        xs.append(rgb)
        ys.append(cls)
    return torch.from_numpy(np.stack(xs)), torch.tensor(ys)
