"""算例 9.6.1、9.6.2：FlashAttention（道等 2022）。
（1）用 NumPy 写出分块的注意力前向：Q 按行分成大小 B_r 的块，K、V 按行分成大小 B_c 的块；对每个 Q 块，依次读入各个 K、V 块，
    算出这一小块分数，用在线 softmax（式 8.7.1）更新每行的最大值 m、和 ℓ 与输出的累加 O，最后除以 ℓ。
    全程不形成 N×N 的分数矩阵。与直接计算 softmax(QKᵀ/√d)V 核对（含因果掩码）。
（2）显存流量（一个头，半精度）：标准实现写出分数 S、读回算 softmax、写出 P、再读回乘 V，约 4N² 个数加上读写 Q、K、V、O；
    FlashAttention 每个 Q 块把 K、V 整个读一遍，共读 Q、O 各一遍、K 与 V 各 N/B_r 遍。N = 4096、d = 64、B_r = 128 时各多少字节；
    再看 B·h = 192 个头（小型 Transformer 的训练批，T = 256）时，标准实现单是 S 与 P 就要多少显存。"""
import numpy as np

from bookout import out

rng = np.random.default_rng(96)


def naive(Q, K, V, causal):
    S = Q @ K.T / np.sqrt(Q.shape[1])
    if causal:
        S = np.where(np.tril(np.ones(S.shape, bool)), S, -np.inf)
    P = np.exp(S - S.max(1, keepdims=True))
    return (P / P.sum(1, keepdims=True)) @ V


def flash(Q, K, V, Br, Bc, causal):
    N, d = Q.shape
    O = np.zeros_like(Q)
    for i in range(0, N, Br):
        q = Q[i:i + Br] / np.sqrt(d)
        m = np.full(len(q), -np.inf)
        l = np.zeros(len(q))
        acc = np.zeros((len(q), d))
        for j in range(0, (i + Br) if causal else N, Bc):     # 因果：只看不晚于这些行的列块
            s = q @ K[j:j + Bc].T
            if causal:
                rows, cols = np.arange(i, i + len(q))[:, None], np.arange(j, j + s.shape[1])[None, :]
                s = np.where(cols <= rows, s, -np.inf)
            m_new = np.maximum(m, s.max(1))
            scale = np.exp(m - m_new)                          # 旧的累加按新的最大值修正（式 8.7.1）
            p = np.exp(s - m_new[:, None])
            l = l * scale + p.sum(1)
            acc = acc * scale[:, None] + p @ V[j:j + Bc]
            m = m_new
        O[i:i + Br] = acc / l[:, None]
    return O


N, d = 300, 64
Q, K, V = (rng.normal(size=(N, d)) for _ in range(3))
err = max(np.abs(flash(Q, K, V, 64, 48, c) - naive(Q, K, V, c)).max() for c in (False, True))

N2, d2, Br, b = 4096, 64, 128, 2
std = (4 * N2 * N2 + 4 * N2 * d2) * b                         # 写 S、读 S、写 P、读 P；读 Q、K、V，写 O
fl = (2 * N2 * d2 + 2 * N2 * d2 * (N2 // Br)) * b             # 读 Q、写 O；K、V 各读 N/B_r 遍
SP_MB = 2 * 192 * 256 * 256 * 2 / 1e6                         # 小型 Transformer 一层的 S 与 P（半精度）
out(err=err, std_MB=std / 1e6, flash_MB=fl / 1e6, ratio=std / fl, SP_MB=SP_MB)
