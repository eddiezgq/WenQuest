"""一个熵已知的合成语言（8.5 节、GPU 实验 8.5）：V = 2048 个词元的一阶马尔可夫链，每个词元只可能接 K = 8 个固定的后继，
概率取自狄利克雷分布（参数 1），由固定的随机种子生成。下一个词元只取决于当前词元，所以任何模型预测下一个词元的
交叉熵都不可能低于这条链的熵率 H = Σ π_i · H(p_i)（π 为平稳分布）。训练好的模型的损失越接近 H 越好；量化后损失比 H 高出多少，
就是量化造成的损失。"""
import numpy as np
import torch

V, K = 2048, 8


def chain(seed=2026):
    rng = np.random.default_rng(seed)
    succ = np.stack([rng.choice(V, K, replace=False) for _ in range(V)])
    p = rng.dirichlet(np.ones(K), V)
    P = np.zeros((V, V))
    np.put_along_axis(P, succ, p, axis=1)
    pi = np.full(V, 1.0 / V)
    for _ in range(2000):                                # 幂迭代求平稳分布
        pi = pi @ P
    H = float(np.sum(pi * -np.sum(p * np.log(p), axis=1)))
    return succ, p, pi, H


class Sampler:
    def __init__(self, device, seed=2026):
        succ, p, pi, self.H = chain(seed)
        self.succ = torch.tensor(succ, device=device)
        self.p = torch.tensor(p, device=device, dtype=torch.float32)
        self.pi = torch.tensor(pi, device=device, dtype=torch.float32)

    def batch(self, b, t, gen):
        x = torch.empty(b, t, dtype=torch.long, device=self.succ.device)
        x[:, 0] = torch.multinomial(self.pi.expand(b, -1), 1, generator=gen)[:, 0]
        for i in range(1, t):
            j = torch.multinomial(self.p[x[:, i - 1]], 1, generator=gen)[:, 0]
            x[:, i] = self.succ[x[:, i - 1], j]
        return x
