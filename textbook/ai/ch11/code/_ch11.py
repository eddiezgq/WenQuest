"""第 11 章共用的数据与工具：合成的零件表面图像与缺陷标注，以及视觉任务的几个评价指标。

**为什么是合成图像**：本书不在仓库里放真实的零件照片（零件库的二进制文件一律由 CI 生成、不进仓库），
而是沿用第 4 章 `_ch4.frame()` 的办法——图像由程序按固定的随机种子画出来：同一个种子永远得到同一张图、
同一份标注，书中的每个数字都能复算，一个字节也不进仓库。缺陷的种类与命名对齐数字工厂的失效机理
（磨削烧伤的锈斑、磕碰的压痕、装夹划伤的划痕），尺寸与粗糙度的限值取自 SH-301 输出轴的检验标准。

合成图像当然不是真图像：它没有真实的光照、反射与相机噪声的全部复杂性，在它上面训练的模型不能直接上线
（11.8.5 节会讲这件事，以及怎样用少量真图校准）。它在本章的作用是让读者能把整条流程——标注、训练、评价、
阈值选择、部署——完整跑一遍，并且每一步都可复现。

坐标约定：图像按 (行, 列) 存放，框写成 (x0, y0, x1, y1)，x 是列、y 是行，右下角不含（与多数检测库一致）。
"""
from __future__ import annotations

import numpy as np

H, W = 256, 256                                   # 合成图像的大小（真机上的一帧是 3840×2160，见第 4 章）
KINDS = ("划痕", "压痕", "锈斑")                    # 三类缺陷；"无" 表示合格
# 每个缺陷还有一个 0.25—1 的“严重程度”：合成数据里也要有刚刚看得见的轻微缺陷，否则任务太容易，
# 什么方法都是满分，选阈值、比较方法都失去意义（11.8.2 节）。
KINDS_EN = ("scratch", "dent", "rust")
PIX_UM = 12.0                                     # 每像素代表的实际尺寸（微米）：SH-301 检测工位的视场与分辨率
RA_LIMIT = 0.8                                    # 表面粗糙度上限（微米，SH-301 检验标准）


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(20261011 + seed)


def surface(rng: np.random.Generator) -> np.ndarray:
    """一块合格的零件表面：磨削后的轴面——沿圆周方向的明暗渐变，叠上细密的磨削纹理与传感器噪声。
    注意传进来的是随机数发生器而不是种子：背景与缺陷必须共用同一条随机流，否则背景的纹理相位
    会与"有没有缺陷"相关，模型可以不看缺陷、只读背景就猜对——这正是 11.8.5 节说的那种捷径。"""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    shade = 0.55 + 0.35 * np.cos((x / W - 0.5) * 2.2)          # 圆柱面的明暗（中间亮、两边暗）
    grind = 0.018 * np.sin(y * 0.9 + rng.uniform(0, 6.3))      # 磨削纹理：沿轴向的细密条纹（峰谷约 4%）
    img = shade + grind + rng.normal(0, 0.012, (H, W))
    return np.clip(img, 0, 1).astype(np.float32)


def _scratch(img, mask, rng, amp=1.0):
    """划痕：一条细长、偏暗的线，端点随机，宽 1—3 像素。amp 是严重程度（1 为明显，0.3 左右为刚刚看得见）。"""
    x0, y0 = rng.uniform(20, W - 20), rng.uniform(20, H - 20)
    ang, ln = rng.uniform(0, np.pi), rng.uniform(40, 110)
    x1, y1 = x0 + ln * np.cos(ang), y0 + ln * np.sin(ang)
    wdt, dark = rng.uniform(1.2, 3.0), rng.uniform(0.22, 0.45) * amp
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = x1 - x0, y1 - y0
    t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / (dx * dx + dy * dy), 0, 1)
    d = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
    hit = d < wdt
    img -= dark * np.exp(-(d / wdt) ** 2) * hit
    mask |= hit
    return hit


def _dent(img, mask, rng, amp=1.0):
    """压痕：一个近圆的凹坑，中心暗、边缘有一圈亮边（光照下的高光）。"""
    cx, cy = rng.uniform(25, W - 25), rng.uniform(25, H - 25)
    r = rng.uniform(6, 16)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot(xx - cx, yy - cy)
    img -= rng.uniform(0.25, 0.45) * amp * np.exp(-(d / r) ** 2)
    img += rng.uniform(0.10, 0.20) * amp * np.exp(-((d - r) / (0.35 * r)) ** 2)   # 坑沿的高光
    hit = d < r * 1.25
    mask |= hit
    return hit


def _rust(img, mask, rng, amp=1.0):
    """锈斑：一片边界不规则、偏暗的区域（用几个圆叠出不规则的形状）。"""
    cx, cy = rng.uniform(30, W - 30), rng.uniform(30, H - 30)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    hit = np.zeros((H, W), bool)
    for _ in range(rng.integers(3, 7)):
        ox, oy = rng.normal(0, 7), rng.normal(0, 7)
        r = rng.uniform(7, 15)
        d = np.hypot(xx - cx - ox, yy - cy - oy)
        hit |= d < r
    img -= rng.uniform(0.12, 0.26) * amp * hit * (1 + 0.3 * np.sin(xx * 0.18) * np.sin(yy * 0.22))
    mask |= hit
    return hit


def _smudge(img, rng):
    """干扰：油污、水渍、照明不匀——看着像缺陷，却不是缺陷（不进掩码，不算缺陷）。
    真实产线上正是这些东西让"比背景暗就报警"的规则失效；合成数据里没有它们，任务就太容易，
    什么方法都是满分（11.8.2 节）。"""
    cx, cy = rng.uniform(0, W), rng.uniform(0, H)
    r = rng.uniform(18, 45)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot(xx - cx, yy - cy)
    sign = 1.0 if rng.random() < 0.5 else -1.0                 # 油污偏暗，反光偏亮
    img -= sign * rng.uniform(0.05, 0.11) * np.exp(-(d / r) ** 2)


_MAKE = {"划痕": _scratch, "压痕": _dent, "锈斑": _rust}


def bbox(hit: np.ndarray) -> tuple:
    """掩码的外接框 (x0, y0, x1, y1)；右下角不含。"""
    ys, xs = np.nonzero(hit)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def sample(seed: int, n_defect: int | None = None) -> dict:
    """一张合成图像加它的标注。返回 image（float32，0—1）、mask（bool，缺陷像素）、
    boxes（每个缺陷的框）、labels（每个框的类别）、label（整张图的类别：合格或缺陷的种类）。"""
    rng = _rng(seed)
    img = surface(rng)
    mask = np.zeros((H, W), bool)
    boxes, labels, sev = [], [], []
    for _ in range(int(rng.random() > 0.55) + int(rng.random() > 0.85)):   # 先撒干扰（不是缺陷）
        _smudge(img, rng)
    auto = int(rng.random() > 0.7) + int(rng.random() > 0.92) + int(rng.random() > 0.98)   # 约六成是合格品：产线上合格品远多于缺陷品
    if n_defect is None:                                       # （11.8 节专门处理这个不平衡）
        n_defect = auto                                        # 显式指定时也照抽这两个数，随机流不错位
    for _ in range(n_defect):
        kind = KINDS[int(rng.integers(0, len(KINDS)))]
        amp = float(rng.uniform(0.25, 1.0))                    # 严重程度：真实产线上多数缺陷是轻微的，
        hit = _MAKE[kind](img, mask, rng, amp)                 # 刚刚越过判定门槛的那些最难判，也最要紧
        boxes.append(bbox(hit))
        labels.append(kind)
        sev.append(amp)
    return dict(image=np.clip(img, 0, 1).astype(np.float32), mask=mask, boxes=boxes, labels=labels,
                severity=sev, label=labels[0] if labels else "无")   # label 只取第一个缺陷，供单标签分类用；
    # 逐缺陷的统计要用 labels（一张图上可能有不止一类缺陷）


def dataset(n: int, start: int = 0) -> list:
    """n 张图的数据集（种子连续，划分由调用者按种子区间决定，保证不重叠、可复算）。"""
    return [sample(start + i) for i in range(n)]


# ---------------------------------------------------------------- 评价指标

def iou(a, b) -> float:
    """两个框的交并比。"""
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, ix1 - ix0) * max(0, iy1 - iy0)
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua else 0.0


def nms(boxes, scores, thr: float = 0.5) -> list:
    """非极大值抑制：按得分从高到低保留，与已保留的框交并比超过 thr 的丢掉。返回保留的下标。"""
    order = sorted(range(len(boxes)), key=lambda i: -scores[i])
    keep = []
    for i in order:
        if all(iou(boxes[i], boxes[j]) <= thr for j in keep):
            keep.append(i)
    return keep


def average_precision(pred_boxes, pred_scores, gt_boxes, thr: float = 0.5,
                      pred_img=None, gt_img=None) -> tuple:
    """单类别的平均精度（COCO 的 101 点插值）：按得分排序逐个判定命中与否，算出查准率—查全率曲线下的面积。
    返回 (AP, 查准率序列, 查全率序列)。一个真值最多被命中一次，后来的算误检。
    pred_img、gt_img 给出每个框属于哪一张图：多张图的框拼在一起算时必须传，否则一张图的预测可能去命中
    另一张图的真值（框一多就会排到真匹配前面）。"""
    order = sorted(range(len(pred_boxes)), key=lambda i: -pred_scores[i])
    used = [False] * len(gt_boxes)
    tp, fp = [], []
    for i in order:
        best, bi = 0.0, -1
        for j, g in enumerate(gt_boxes):
            if pred_img is not None and gt_img is not None and pred_img[i] != gt_img[j]:
                continue                                       # 不同图的框不配对
            v = iou(pred_boxes[i], g)
            if v > best:
                best, bi = v, j
        if best >= thr and bi >= 0 and not used[bi]:
            used[bi] = True
            tp.append(1)
            fp.append(0)
        else:
            tp.append(0)
            fp.append(1)
    ctp, cfp = np.cumsum(tp), np.cumsum(fp)
    rec = ctp / max(len(gt_boxes), 1)
    prec = ctp / np.maximum(ctp + cfp, 1e-9)
    ap = 0.0
    for r in np.linspace(0, 1, 101):                           # 101 点插值（COCO 的做法）
        p = prec[rec >= r].max() if np.any(rec >= r) else 0.0
        ap += p / 101
    return float(ap), prec, rec


def miou(pred_mask, gt_mask) -> float:
    """两类（缺陷 / 背景）的平均交并比。"""
    out = []
    for p, g in ((pred_mask, gt_mask), (~pred_mask, ~gt_mask)):
        inter, union = np.logical_and(p, g).sum(), np.logical_or(p, g).sum()
        out.append(inter / union if union else 1.0)
    return float(np.mean(out))


def dice(pred_mask, gt_mask) -> float:
    """Dice 系数（又称 F1 的像素版）。"""
    inter = np.logical_and(pred_mask, gt_mask).sum()
    s = pred_mask.sum() + gt_mask.sum()
    return float(2 * inter / s) if s else 1.0


# ---------------------------------------------------------------- 各代网络的结构与代价（11.1、11.2 节；图与算例共用）

V, IMGS = 1000, 1281167                      # ImageNet-1k：类别数与训练图数
# 各代网络的结构（只列算运算量要用的部分；输入 224×224×3）
# AlexNet（2012，Krizhevsky 等）：5 个卷积层 + 3 个全连接层。按原论文的单路等效结构。
ALEX_CONV = [  # (K 输出通道, C 输入通道, R, S, 输出 H', 输出 W')
    (96, 3, 11, 11, 55, 55), (256, 96, 5, 5, 27, 27), (384, 256, 3, 3, 13, 13),
    (384, 384, 3, 3, 13, 13), (256, 384, 3, 3, 13, 13)]
ALEX_FC = [(9216, 4096), (4096, 4096), (4096, 1000)]
# VGG-16（2014）：13 个卷积层（全部 3×3）+ 3 个全连接层
VGG_CFG = [(64, 2, 224), (128, 2, 112), (256, 3, 56), (512, 3, 28), (512, 3, 14)]
VGG_FC = [(25088, 4096), (4096, 4096), (4096, 1000)]
# ResNet-50（2015）：4 个阶段的瓶颈块，每块 1×1 → 3×3 → 1×1
RES_STAGES = [(3, 64, 56), (4, 128, 28), (6, 256, 14), (3, 512, 7)]   # (块数, 中间通道, 特征图边长)
# ViT-B/16（2020）：196 个图块 + 1 个分类标记，12 层，d = 768，d_ff = 3072，12 个头
VIT = dict(T=197, L=12, d=768, ff=3072)


def conv(K, C, R, S, Hh, Ww):
    return 2 * K * C * R * S * Hh * Ww, K * C * R * S + K          # (运算量, 参数量)


def fc(i, o):
    return 2 * i * o, i * o + o


def alexnet():
    f = p = 0
    for c in ALEX_CONV:
        a, b = conv(*c)
        f, p = f + a, p + b
    for c in ALEX_FC:
        a, b = fc(*c)
        f, p = f + a, p + b
    return f, p


def vgg16():
    f = p = 0
    cin = 3
    for cout, n, side in VGG_CFG:
        for i in range(n):
            a, b = conv(cout, cin if i == 0 else cout, 3, 3, side, side)
            f, p = f + a, p + b
        cin = cout
    for c in VGG_FC:
        a, b = fc(*c)
        f, p = f + a, p + b
    return f, p


def resnet50():
    f, p = conv(64, 3, 7, 7, 112, 112)                              # 第一层 7×7
    cin = 64
    for n, mid, side in RES_STAGES:
        for i in range(n):
            for (K, C, R) in ((mid, cin if i == 0 else mid * 4, 1), (mid, mid, 3), (mid * 4, mid, 1)):
                a, b = conv(K, C, R, R, side, side)
                f, p = f + a, p + b
            if i == 0:                                              # 下采样的捷径卷积
                a, b = conv(mid * 4, cin, 1, 1, side, side)
                f, p = f + a, p + b
        cin = mid * 4
    a, b = fc(2048, 1000)
    return f + a, p + b


def vit_b16():
    T, L, d, ff = VIT["T"], VIT["L"], VIT["d"], VIT["ff"]
    per_layer_f = 2 * T * (4 * d * d + 2 * ff * d) + 4 * T * T * d   # 投影与前馈 + 注意力的两次矩阵乘法
    per_layer_p = 4 * d * d + 2 * ff * d
    patch_f, patch_p = 2 * (T - 1) * (16 * 16 * 3) * d, (16 * 16 * 3) * d + d
    head_f, head_p = fc(d, 1000)
    return L * per_layer_f + patch_f + head_f, L * per_layer_p + patch_p + head_p + T * d


MODELS = {"alex": alexnet(), "vgg": vgg16(), "res": resnet50(), "vit": vit_b16()}
# 公开报告的 ImageNet top-1 正确率（单模型、单裁剪，原论文或官方实现，用于对照，不是本书实测）
TOP1 = {"alex": 57.1, "vgg": 71.6, "res": 76.1, "vit": 77.9}



def grad_profile(D: int = 64, L: int = 64, scale: float = 0.8, seed: int = 11):
    """梯度反传时逐层的范数：朴素堆叠与"残差 + 归一化"两条曲线（11.2 节；程序 11.2.1 与图 11.2.1 共用）。"""
    rng = np.random.default_rng(seed)
    g1 = g2 = np.ones(D) / np.sqrt(D)
    k = 1 / np.sqrt(1 + scale ** 2)
    plain, res = [], []
    for _ in range(L):
        W = rng.normal(0, scale / np.sqrt(D), (D, D))
        g1 = W.T @ g1
        g2 = (W.T @ g2 + g2) * k
        plain.append(float(np.linalg.norm(g1)))
        res.append(float(np.linalg.norm(g2)))
    return plain, res
