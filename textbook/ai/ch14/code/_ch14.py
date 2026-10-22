"""第 14 章共用的数据与工具：合成的"图—文"配对、对比学习（InfoNCE）、检索指标，
以及合成的检验报告与图纸（字段、置信度、OCR 噪声）。

**为什么全是合成的**：与第 11 章不放图片、第 12 章不放录音、第 13 章不放手册同理——仓库里不放
任何真实图纸、照片与报告，也不放模型权重。本章要讲的道理（对齐靠什么、批大小为什么重要、
一页图纸要多少词元、读不清时该拒答）用程序合成的数据讲得一样清楚，而且每个数都能复算。

本章的"模型"都是几十行 NumPy：图像端与文本端各一个线性投影，用 InfoNCE 训出来。它当然不是
CLIP，但"同一个空间里配对的靠近、不配对的推开"这件事是真算出来的，批大小、温度、检索池
大小的影响也都是真量出来的。真模型上的数字见 14.1、14.6 节的云端实验与资料卡里的公开数字。

零件与缺陷的名字沿用第 11 章（划痕、压痕、锈斑），工序与零件编号沿用数字工厂（SH-301 输出轴等）。
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------- 一、合成的图—文配对

PARTS = ("SH-301 输出轴", "SH-302 输入轴", "GH-12 主动齿轮", "XT-5 箱体", "ZC-7 支承座", "ZH-9 端盖")
KINDS = ("无缺陷", "划痕", "压痕", "锈斑")
PLACES = ("轴颈处", "端面上", "键槽附近")
FINISH = ("磨削面", "车削面")
LEVELS = ("轻微", "明显", "严重")
SIZES = ("φ28", "φ30", "φ32", "φ45", "φ50")
# 文本模板：车间里写检验记录的口气。同一组属性有几种说法，模型不能靠记住一句话来配对。
TEMPLATES = (
    "{size} {part}的{place}有{level}{kind}",
    "{finish}，{place}发现{level}{kind}（{size}）",
    "{part} {size}：{place}{level}{kind}，{finish}",
    "检验记录——{part}，{level}{kind}（{place}，{size}）",
)
ATTR_SETS = (PARTS, KINDS, PLACES, FINISH, LEVELS, SIZES)
N_CLASSES = 1
for _s in ATTR_SETS:
    N_CLASSES *= len(_s)                         # 6×4×3×2×3×5 = 2160 种说法
VOCAB = tuple(dict.fromkeys(sum(ATTR_SETS, ())))  # 词表：属性词本身就是词


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(20261021 + seed)


def attrs(n: int, seed: int = 0) -> np.ndarray:
    """n 个样本的属性：(零件, 缺陷, 位置, 表面, 程度, 尺寸) 六列，每列取各自的编号。"""
    g = _rng(seed)
    return np.c_[tuple(g.integers(0, len(s), n) for s in ATTR_SETS)]


def image_feat(a: np.ndarray, seed: int = 0, noise: float = 0.35, dim: int = 48) -> np.ndarray:
    """图像端的特征：把各个属性投到一组固定的随机方向上再相加，最后加噪声。

    这相当于“一个已经训好的视觉编码器”的输出——它把图里有什么编码进了向量，但各属性的方向
    与文本端毫无关系（两个编码器是分别训练的）。14.1 节要做的事，就是再学两个投影把它们对上。
    """
    g = np.random.default_rng(777)               # 编码方式固定：同一个属性在哪张图里都落在同一个方向上
    basis = [g.normal(0, 1, (len(s), dim)) for s in ATTR_SETS]
    w = (1.0, 1.0, 0.6, 0.5, 0.7, 0.8)           # 零件与缺陷最显眼，位置、表面、程度、尺寸其次
    x = sum(wi * b[a[:, j]] for j, (b, wi) in enumerate(zip(basis, w)))
    return x + _rng(seed + 1).normal(0, noise, x.shape)         # 拍摄条件带来的噪声


def caption_of(a_row: np.ndarray, which: int = 0) -> str:
    """一行属性写成一句话（which 选模板）。"""
    p, k, pl, f, lv, sz = a_row
    return TEMPLATES[which % len(TEMPLATES)].format(
        part=PARTS[p], kind=KINDS[k], place=PLACES[pl], finish=FINISH[f], level=LEVELS[lv], size=SIZES[sz])


def captions(a: np.ndarray, seed: int = 0) -> list[str]:
    """文本端：按模板写出的一句检验记录（模板随机选）。"""
    g = _rng(seed + 2)
    return [caption_of(r, int(g.integers(0, len(TEMPLATES)))) for r in a]


def text_feat(caps: list[str]) -> np.ndarray:
    """文本端的特征：词表上的词袋（出现记 1）。简单，但足以把句子里的属性表示出来。"""
    x = np.zeros((len(caps), len(VOCAB)), dtype=float)
    for i, c in enumerate(caps):
        for j, w in enumerate(VOCAB):
            if w in c:
                x[i, j] = 1.0
    return x


def pairs(n: int, seed: int = 0, noise: float = 0.35):
    """n 对（图像特征, 文本特征, 属性）。"""
    a = attrs(n, seed)
    caps = captions(a, seed)
    return image_feat(a, seed, noise), text_feat(caps), a


# ---------------------------------------------------------------- 二、对比学习

def l2(x: np.ndarray) -> np.ndarray:
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)


def infonce(zi: np.ndarray, zt: np.ndarray, temp: float):
    """一个批的 InfoNCE 损失与它对两端嵌入的梯度（两个方向取平均，与 CLIP 一致）。

    zi、zt 都已归一化，形状 (B, d)。相似度矩阵 S = zi @ zt.T / temp，对角线是配对的那一对。
    """
    B = len(zi)
    s = zi @ zt.T / temp
    pi = np.exp(s - s.max(1, keepdims=True))
    pi /= pi.sum(1, keepdims=True)                       # 按行：图找文
    pt = np.exp(s - s.max(0, keepdims=True))
    pt /= pt.sum(0, keepdims=True)                       # 按列：文找图
    eye = np.eye(B)
    loss = -(np.log(np.maximum(np.diag(pi), 1e-12)).mean() + np.log(np.maximum(np.diag(pt), 1e-12)).mean()) / 2
    gs = ((pi - eye) + (pt - eye)) / (2 * B * temp)      # 对 S 的梯度
    return loss, gs @ zt, gs.T @ zi


def train(xi: np.ndarray, xt: np.ndarray, dim: int = 16, batch: int = 64, steps: int = 400,
          temp: float = 0.07, lr: float = 0.5, seed: int = 0):
    """两端各学一个线性投影，用 InfoNCE 把它们投到同一个空间。返回 (Wi, Wt, 损失曲线)。"""
    g = np.random.default_rng(31 + seed)
    Wi = g.normal(0, 0.3, (xi.shape[1], dim))
    Wt = g.normal(0, 0.3, (xt.shape[1], dim))
    n, hist = len(xi), []
    for t in range(steps):
        idx = g.choice(n, min(batch, n), replace=False)
        hi, ht = xi[idx] @ Wi, xt[idx] @ Wt
        zi, zt = l2(hi), l2(ht)
        loss, gzi, gzt = infonce(zi, zt, temp)
        # 经过归一化这一层的反传：d z / d h = (I − z zᵀ) / ‖h‖
        ghi = (gzi - zi * (gzi * zi).sum(1, keepdims=True)) / np.maximum(np.linalg.norm(hi, axis=1, keepdims=True), 1e-12)
        ght = (gzt - zt * (gzt * zt).sum(1, keepdims=True)) / np.maximum(np.linalg.norm(ht, axis=1, keepdims=True), 1e-12)
        Wi -= lr * xi[idx].T @ ghi
        Wt -= lr * xt[idx].T @ ght
        hist.append(loss)
    return Wi, Wt, np.array(hist)


def labels_of(a: np.ndarray) -> np.ndarray:
    """把各属性压成一个类别编号（共 2160 种说法）。"""
    lab = np.zeros(len(a), dtype=int)
    for j, s_ in enumerate(ATTR_SETS):
        lab = lab * len(s_) + a[:, j]
    return lab


def recall_at_k(zq: np.ndarray, zd: np.ndarray, lq: np.ndarray, ld: np.ndarray, ks=(1, 5, 10),
                chunk: int = 2000, drop_self: bool = False) -> dict[int, float]:
    """检索命中率：取回的候选只要**说的是同一件事**（各属性全同）就算命中。

    合成数据里一句话可以对应很多张图（"SH-301 的轴颈处有轻微划痕"车间里天天出现），
    按"第 i 个查询只认第 i 个候选"算命中率是错的——那样连完美的模型也拿不到满分。
    真实的检索基准（COCO、Flickr30K）每张图配 5 句话，用的也是"命中其中之一即可"的口径。

    查询分块处理：检索池上万条时，整块的相似度矩阵就要几个 GB。
    """
    kmax = max(ks)
    hits = {k: 0 for k in ks}
    for b in range(0, len(zq), chunk):
        s = zq[b:b + chunk] @ zd.T
        if drop_self:                                                   # 以图搜图时，查询自己也在池子里
            for r in range(len(s)):
                s[r, b + r] = -np.inf
        top = np.argpartition(-s, kmax - 1, axis=1)[:, :kmax]           # 先粗选前 kmax 个
        order = np.take_along_axis(top, np.argsort(-np.take_along_axis(s, top, 1), axis=1), 1)
        hit = ld[order] == lq[b:b + chunk, None]
        for k in ks:
            hits[k] += int(hit[:, :k].any(1).sum())
    return {k: hits[k] / len(zq) * 100 for k in ks}


def chance_recall(ld: np.ndarray, lq: np.ndarray, ks=(1, 5, 10)) -> dict[int, float]:
    """瞎猜的命中率：按候选池里同类的比例算（检索池越大，这个基线越低）。"""
    n = len(ld)
    cnt = np.bincount(ld, minlength=int(max(ld.max(), lq.max())) + 1)
    share = cnt[lq] / n
    return {k: float((1 - (1 - share) ** k).mean() * 100) for k in ks}


# ---------------------------------------------------------------- 三、视觉词元的账

def tokens_of(res: int, patch: int, merge: int = 1, cls: int = 0) -> int:
    """一张图经视觉塔之后的词元数：(res/patch)² 个块，若干合并，再加几个标记。
    公式出自 ViT（N = HW/P²）；2×2 合并是 Qwen2-VL 报告里的做法。"""
    n = (res // patch) ** 2
    assert res % patch == 0
    return n // (merge * merge) + cls


def tiled_tokens(w: int, h: int, tile: int = 448, per_tile: int = 256, thumb: bool = True, max_tiles: int = 40):
    """切片式动态分辨率（InternVL 1.5 的做法）：按长宽切成若干片，每片固定词元数，另加一张缩略图。"""
    nx, ny = max(1, round(w / tile)), max(1, round(h / tile))
    tiles = min(nx * ny, max_tiles)
    return (tiles + (1 if thumb else 0)) * per_tile, tiles


def attn_cost(n_tokens: int, d_model: int = 4096, layers: int = 32) -> float:
    """一层自注意力里"注意力矩阵"那两步的乘加次数（QKᵀ 与 PV），全部层加起来。
    与第 2、9 章同一口径：只数这平方的两项，线性项另算。"""
    return 2.0 * layers * n_tokens * n_tokens * d_model


# ---------------------------------------------------------------- 四、视频的时序冗余

def clip_frames(n: int = 120, seed: int = 0, move: float = 0.006, dim: int = 48) -> np.ndarray:
    """一段"视频"的逐帧特征：一个零件缓慢转动（特征沿一条曲线缓慢漂移），中间有两次切换镜头。"""
    g = _rng(seed + 5)
    base = g.normal(0, 1, dim)
    drift = g.normal(0, 1, dim)
    out, cur = [], base.copy()
    for t in range(n):
        if t in (40, 85):                       # 切换镜头：特征跳变
            cur = g.normal(0, 1, dim)
        cur = cur + move * drift + g.normal(0, 0.004, dim)
        out.append(cur.copy())
    return l2(np.array(out))


# ---------------------------------------------------------------- 五、动作的词元化（视觉—语言—动作）

def action_log(n: int = 4000, seed: int = 0) -> np.ndarray:
    """一段示教记录：7 维动作（3 个位置增量、3 个姿态增量、1 个夹爪），其中混有少量离群值
    （示教时手抖、碰撞后的急停），这正是 OpenVLA 用第 1—99 分位数而不是极值划分区间的原因。"""
    g = _rng(seed + 7)
    a = np.c_[g.normal(0, 0.01, (n, 3)), g.normal(0, 0.05, (n, 3)), g.integers(0, 2, n).astype(float)]
    hit = g.choice(n, max(1, n // 200), replace=False)          # 0.5% 的离群值
    a[hit, :3] += g.normal(0, 0.25, (len(hit), 3))
    return a


def quantize(x: np.ndarray, lo: float, hi: float, bins: int = 256) -> np.ndarray:
    """把一维动作离散成 bins 个区间的编号（超出量程的截断到两端）。"""
    q = np.clip(np.floor((x - lo) / (hi - lo) * bins), 0, bins - 1)
    return q.astype(int)


def dequantize(q: np.ndarray, lo: float, hi: float, bins: int = 256) -> np.ndarray:
    return lo + (q + 0.5) * (hi - lo) / bins


# ---------------------------------------------------------------- 六、合成的检验报告（14.6 节）

FIELDS = ("零件号", "工序", "尺寸", "公差", "实测", "判定", "检验员")
OPS = ("粗车", "精车", "磨外圆", "铣键槽", "钻孔")
INSPECTORS = ("王工", "李工", "赵工", "周工")


def reports(n: int = 300, seed: int = 0, phone_share: float = 0.35):
    """n 份检验报告：每份是一组字段（真值），外加一个"清晰度"。

    清晰度不是一条平滑的曲线，而是**两拨**：一拨是扫描仪进来的（清楚），一拨是车间用手机拍的
    （斜、暗、有折痕、还常带手写批注）。真实工厂里就是这两个入口，14.6 节的拒答阈值正是冲着
    后一拨去的。
    """
    g = _rng(seed + 11)
    recs, quality = [], []
    for _ in range(n):
        nom = round(float(g.choice([28.0, 30.0, 32.0, 45.0, 50.0])), 1)
        tol = float(g.choice([0.02, 0.03, 0.05]))
        dev = float(g.normal(0, tol * 0.6))
        meas = round(nom + dev, 3)
        recs.append({"零件号": str(g.choice(PARTS)), "工序": str(g.choice(OPS)),
                     "尺寸": nom, "公差": tol, "实测": meas,
                     "判定": "合格" if abs(dev) <= tol else "不合格",
                     "检验员": str(g.choice(INSPECTORS))})
        phone = g.random() < phone_share
        quality.append(float(np.clip(g.normal(0.35, 0.12) if phone else g.normal(0.95, 0.03), 0.02, 1.0)))
    return recs, np.array(quality)


def read_fields(recs, quality, seed: int = 0):
    """一个"视觉语言模型"读这些报告：清晰度越低越容易读错，模型同时给出自己的置信度。

    置信度与对错相关但不完美（真模型就是这样）：它由清晰度加噪声得到，所以按置信度拒答能挡住
    大部分错误、但挡不住全部，这正是 14.6 节要量的东西。
    """
    g = _rng(seed + 13)
    p_ok = 0.88 + 0.115 * quality                     # 读对一个字段的概率（清晰度越高越准）
    correct = g.random((len(recs), len(FIELDS))) < p_ok[:, None]
    conf = np.clip(p_ok[:, None] + g.normal(0, 0.05, correct.shape), 0.01, 0.999)
    return correct, conf
