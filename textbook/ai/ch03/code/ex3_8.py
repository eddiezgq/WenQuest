"""算例 3.8.1～3.8.3、程序 3.8.1：屋顶线模型。各 GPU 的平衡点；小型 Transformer 各层与常见层在 H100 上的位置；
逐词生成时批大小对计算强度的影响。

式 (3.8.1)：可达到的算力 P(I) = min(P_peak, β I)；平衡点 I* = P_peak / β。
各层的运算量与数据量（半精度，每个运算单独执行，不考虑融合与缓存复用）与程序 2.10.1、实验 2.10 的计数相同：
矩阵乘法 (M×K)(K×N)：W = 2MNK，Q = 2(MK + KN + MN)。
"""
from bookout import out
from gpus import GPUS

BY = 2


def mm(M, K, N):
    return 2 * M * K * N, BY * (M * K + K * N + M * N)


def roof(P, bw, I):
    return min(P, bw * I)


# 小型 Transformer（第 2 章）：B = 32，T = 256，d = 384，6 头，d_ff = 1536，V = 2048
B, T, d, h, V = 32, 256, 384, 6, 2048
n, f, dh = B * T, 4 * d, d // h
LAYERS = {
    "QKV": mm(n, d, 3 * d), "proj": mm(n, d, d), "FF1": mm(n, d, f), "FF2": mm(n, f, d), "logits": mm(n, d, V),
    "QKT": (2 * B * h * T * T * dh, BY * (2 * n * d + B * h * T * T)),
    "softmax": (5 * B * h * T * T, BY * 2 * B * h * T * T),
    "LN": (8 * n * d, BY * (2 * n * d + 2 * d)),
    "GELU": (10 * n * f, BY * 2 * n * f),
    "add": (n * d, BY * 3 * n * d),
}
# 常见的卷积层：ResNet 第一组的 3×3 卷积，56×56，64 → 64 通道，批大小 32（im2col 后 M = 32·56·56，K = 9·64，N = 64）
conv_W = 2 * B * 56 * 56 * 64 * 9 * 64
conv_Q = BY * (B * 56 * 56 * 64 * 2 + 9 * 64 * 64)            # 读输入、写输出各一次，读卷积核一次
LAYERS["conv3x3"] = (conv_W, conv_Q)
# 大模型逐词生成时的一个线性层：d = 4096，批大小 1（矩阵乘向量）
dl = 4096
LAYERS["decode"] = mm(1, dl, dl)

hp = GPUS["h100"]
P, bw = hp["fp16t"], hp["bw"]
ridge = P / bw
pts = {}
for name, (W, Q) in LAYERS.items():
    I = W / Q
    att = roof(P, bw, I)
    pts[name] = (I, att, att / P, "compute" if I >= ridge else "memory")

ridges = {k: (GPUS[k]["fp16t"] / GPUS[k]["bw"], GPUS[k]["fp32"] / GPUS[k]["bw"]) for k in ("v100", "a100", "h100", "rtx4090", "b200")}


# 算例 3.8.3：逐词生成，批大小 b 条序列共用一次读权重：I(b) = 2 b d² / (2(d² + 2 b d)) ≈ b
def I_dec(b):
    W, Q = mm(b, dl, dl)
    return W / Q


b_need = next(b for b in range(1, 100000) if I_dec(b) >= ridge)
I_dec_8, I_dec_64 = I_dec(8), I_dec(64)

v = {f"I_{k}": p[0] for k, p in pts.items()}
v.update({f"u_{k}": p[2] * 100 for k, p in pts.items()})
v.update({f"T_{k}": p[1] / 1e12 for k, p in pts.items()})
v.update({f"r16_{k}": r[0] for k, r in ridges.items()})
v.update({f"r32_{k}": r[1] for k, r in ridges.items()})
out(ridge=ridge, P_T=P / 1e12, bw_T=bw / 1e12, b_need=b_need, I_dec_8=I_dec_8, I_dec_64=I_dec_64,
    n_mem=sum(1 for p in pts.values() if p[3] == "memory"), n_pts=len(pts), **v)
