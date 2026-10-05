"""算例 11.2.1—11.2.2：加深为什么难，残差为什么管用（11.2 节）。

（1）深层网络里梯度怎样被逐层缩放：L 层、每层的雅可比矩阵近似为一个随机矩阵时，梯度的范数按几何级数变化——
    稍小于 1 就指数衰减，稍大于 1 就指数爆炸（2.5 节）。加上残差连接 h = h + F(h) 后，局部导数里多了一项单位矩阵，
    梯度有一条“直路”传回去。本程序用一个 L 层的线性网络做数值实验：同样的初始化，有无残差时第一层梯度的范数。
（2）同样深度下，朴素加深与残差网络在训练上的差别（ResNet 论文报告的 ImageNet 单裁剪错误率）：
    朴素堆叠的 34 层比 18 层还差，残差网络从 18 层加到 152 层一路变好。
"""
import numpy as np

from _ch11 import grad_profile
from bookout import out

rng = np.random.default_rng(11)
D, L = 64, 64                                     # 宽度与层数


def grad_norm(scale: float, mode: str, L: int = L) -> float:
    """L 层线性网络的反向连乘，返回梯度范数。三种接法：
    plain  ：h ← W h —— 梯度每层乘一个随机矩阵，范数按几何级数走；
    res    ：h ← h + W h —— 梯度多一条直路（单位矩阵），不会消失，但每层都在放大；
    resnorm：h ← (h + W h) / √(1 + scale²) —— 残差加归一化（2.7 节），这才是真实网络里的样子。"""
    g = np.ones(D) / np.sqrt(D)                   # 从输出端回传的单位梯度
    k = 1 / np.sqrt(1 + scale ** 2)
    for _ in range(L):
        W = rng.normal(0, scale / np.sqrt(D), (D, D))
        if mode == "plain":
            g = W.T @ g
        elif mode == "res":
            g = W.T @ g + g
        else:
            g = (W.T @ g + g) * k
    return float(np.linalg.norm(g))


v = {"D": D, "L": L}
for name, scale in (("small", 0.8), ("unit", 1.0), ("big", 1.2)):
    for mode in ("plain", "res", "resnorm"):
        v[mode + "_" + name] = grad_norm(scale, mode)
v["ratio_small"] = v["resnorm_small"] / max(v["plain_small"], 1e-300)
v["plain_small_exp"] = int(np.floor(np.log10(v["plain_small"])))        # 衰减到 10 的几次方

# 逐层看梯度范数怎样变化（画图用，取 scale = 0.8）
prof_plain, prof_res = [], []
g1 = g2 = np.ones(D) / np.sqrt(D)
k = 1 / np.sqrt(1 + 0.8 ** 2)
for i in range(L):
    W = rng.normal(0, 0.8 / np.sqrt(D), (D, D))
    g1 = W.T @ g1
    g2 = (W.T @ g2 + g2) * k
    prof_plain.append(float(np.linalg.norm(g1)))
    prof_res.append(float(np.linalg.norm(g2)))
v["prof_plain"] = prof_plain
v["prof_res"] = prof_res
v["plain_last"] = prof_plain[-1]
v["res_last"] = prof_res[-1]

# （2）公开报告的 ImageNet top-1 错误率（单模型，原论文）：朴素加深与残差加深
PLAIN = {18: 27.94, 34: 28.54}                    # 朴素网络：34 层反而比 18 层差
RES = {18: 27.88, 34: 25.03, 50: 24.7, 101: 23.6, 152: 23.0}
v["plain18"], v["plain34"] = PLAIN[18], PLAIN[34]
v["res18"], v["res34"], v["res152"] = RES[18], RES[34], RES[152]
v["plain_worse"] = PLAIN[34] - PLAIN[18]          # 加深反而差了多少
v["res_better"] = RES[18] - RES[152]              # 残差从 18 层加到 152 层好了多少
out(**v)
