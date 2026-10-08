"""数学篇第 M3 章共用的东西：车间抽检的合格率模型，以及几个会反复用到的小工具。

本章的实际问题是抽检：一批零件里有一定比例不合格，检验又不是百分之百准。
这件事把本章要讲的都串上了——条件概率与贝叶斯（检出了就一定是坏件吗）、
二项分布与期望方差（抽 50 个能看出多少）、最大似然（用抽检结果估不合格率）、
置信区间（估出来的数有多靠得住）。

记号与第 2、12 章一致：概率 p、期望 E、方差 Var、损失 ℒ、样本数 n。
数据由程序按固定种子生成，仓库里不放真实的检验记录。
"""
from __future__ import annotations

import numpy as np

# SH-301 输出轴检验工位的设定（数字工厂第 11 章的那条线）
P_BAD = 0.02          # 真实的不合格率：每百件约 2 件
SENS = 0.90           # 检出率（灵敏度）：坏件被判为坏的概率
SPEC = 0.97           # 特异度：好件被判为好的概率；1 − SPEC 就是误报率


def rng(seed: int = 0) -> np.random.Generator:
    return np.random.default_rng(2026_1008 + seed)


def inspect(n: int = 1000, seed: int = 0, p_bad: float = P_BAD, sens: float = SENS, spec: float = SPEC):
    """抽检 n 个零件：返回 (真实是否坏件, 检验是否判坏)，都是 0/1 数组。"""
    g = rng(seed)
    bad = (g.random(n) < p_bad).astype(int)
    flag = np.where(bad == 1, g.random(n) < sens, g.random(n) > spec).astype(int)
    return bad, flag


def bayes(p_bad: float = P_BAD, sens: float = SENS, spec: float = SPEC) -> float:
    """判为坏件时，它真是坏件的概率（后验）。式 (M3.1.2)。"""
    num = sens * p_bad
    return num / (num + (1 - spec) * (1 - p_bad))


def mle_p(bad: np.ndarray) -> float:
    """伯努利的最大似然估计就是样本比例（算例 M3.4.1 会推导它）。"""
    return float(np.mean(bad))


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """比例的置信区间（威尔逊区间）：样本少或比例接近 0、1 时比常见的正态近似可靠得多。"""
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(max(0.0, c - h)), float(min(1.0, c + h))
