"""数学篇第 M1 章共用的数据：车间里一批零件的测量数据，以及一张用程序画出来的零件表面图。

**为什么是合成的**：与第 11 章同理，仓库里不放真实的测量记录与照片。数据由固定的随机种子生成，
书中的每个数字都能复算。这批数据有意做得"像真的"：几个特征之间相关（外径大的零件，内径往往也大），
量纲差得远（直径按毫米、粗糙度按微米、圆度按微米），还有少量测量噪声——这三件事正是本章要讲的
归一化、协方差与条件数要处理的。

数据的含义：SH-301 输出轴的一批零件，每个零件测 5 项——外径、内径、长度、圆度、表面粗糙度。
"""
from __future__ import annotations

import numpy as np

FEATURES = ("外径", "内径", "长度", "圆度", "粗糙度")
FEATURES_EN = ("outer dia.", "inner dia.", "length", "roundness", "roughness")
UNITS = ("mm", "mm", "mm", "µm", "µm")
NOMINAL = (35.0, 20.0, 120.0, 6.0, 0.6)          # 名义值（圆度与粗糙度按微米）


def rng(seed: int = 0) -> np.random.Generator:
    return np.random.default_rng(2026_1007 + seed)


def parts(n: int = 200, seed: int = 0) -> np.ndarray:
    """一批零件的测量数据，形状 (n, 5)：外径、内径、长度、圆度、粗糙度。

    生成方式：先抽一个"机床状态"的隐变量（刀具磨损），它同时推高外径、内径与粗糙度——这就是特征之间
    相关的来源；再各自叠上独立的加工波动与测量噪声。所以这批数据的协方差矩阵不是对角阵（M1.5 节），
    而且几个方向上的方差相差几个数量级（M1.3、M1.7 节）。
    """
    g = rng(seed)
    wear = g.normal(0, 1, n)                                   # 刀具磨损：越磨越大、越粗糙
    x = np.empty((n, 5))
    x[:, 0] = NOMINAL[0] + 0.012 * wear + g.normal(0, 0.006, n)        # 外径 mm
    x[:, 1] = NOMINAL[1] + 0.009 * wear + g.normal(0, 0.005, n)        # 内径 mm
    x[:, 2] = NOMINAL[2] + g.normal(0, 0.05, n)                        # 长度 mm：与磨损无关
    x[:, 3] = NOMINAL[3] + 1.4 * np.abs(wear) + g.normal(0, 0.5, n)    # 圆度 µm：磨损让它变差（偏哪边都变差）
    x[:, 4] = NOMINAL[4] + 0.10 * wear + g.normal(0, 0.04, n)          # 粗糙度 µm
    return x


def standardize(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """按列减均值、除标准差。返回 (标准化后的数据, 均值, 标准差)。"""
    mu = x.mean(axis=0)
    sd = x.std(axis=0, ddof=1)
    return (x - mu) / sd, mu, sd


def surface(n: int = 96, seed: int = 0, noise: float = 0.01) -> np.ndarray:
    """一张磨削后的轴面灰度图（n×n，取值 0—1）：沿圆周的明暗渐变 + 沿轴向的磨削纹理 + 少量噪声。
    不加噪声时它的秩只有 3（明暗 1 层、粗磨与精磨的纹理各 1 层），加上噪声后满秩但奇异值分两段——
    前 3 个是结构，后面一长串是噪声。这正好用来讲低秩近似与"再加秩只是在拟合噪声"（M1.6 节）。"""
    g = rng(seed + 7)
    r, c = np.mgrid[0:n, 0:n] / (n - 1)
    shade = 0.55 + 0.32 * np.cos((c - 0.5) * 2.2)              # 圆柱面的明暗：只与列有关，秩 1
    grind = (0.05 * np.sin(2 * np.pi * 6 * r) * (0.6 + 0.4 * c)        # 粗磨的条纹（秩 1）
             + 0.02 * np.sin(2 * np.pi * 17 * r) * (1.0 - 0.5 * c))     # 精磨的细纹（再 1 秩）
    img = shade + grind + (g.normal(0, noise, (n, n)) if noise else 0.0)
    return np.clip(img, 0, 1)
