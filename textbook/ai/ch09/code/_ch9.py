"""第 9 章共用（以下划线开头，构建时不单独运行）：GPU 规格与两个模型的尺寸。

- 小型 Transformer：第 2 章（2.9 节），实验中真正训练、推理的模型；
- 70 亿参数一级的模型：按公开的 Llama 2 7B 的结构（32 层，d = 4096，32 个头，前馈网络用 SwiGLU、d_ff = 11 008，
  词表 32 000，输入嵌入与输出层不共享），书中用它做“大模型”的算例。参数个数由结构算出（params）。"""
from gpus import GPUS, IB, NVLINK, PCIE

A10 = dict(GPUS["a10"])
A100 = dict(GPUS["a100"])
H100 = dict(GPUS["h100"])

SMALL = dict(name="小型 Transformer", L=6, d=384, h=6, kv=6, dff=1536, V=2048, T=256, glu=False, tied=True)
BIG = dict(name="7B", L=32, d=4096, h=32, kv=32, dff=11008, V=32000, T=4096, glu=True, tied=False)


def params(c):
    """参数个数：每层注意力 4d²（Q、K、V、输出投影；分组查询时 K、V 变小）、前馈网络 2·d·d_ff（SwiGLU 为 3·d·d_ff），
    层归一化与偏置略去；加上词元嵌入（与输出层共享时只算一次）。"""
    d, dh = c["d"], c["d"] // c["h"]
    attn = 2 * d * d + 2 * d * c["kv"] * dh
    ff = (3 if c["glu"] else 2) * d * c["dff"]
    emb = c["V"] * d * (1 if c["tied"] else 2)
    return c["L"] * (attn + ff) + emb


def kv_bytes_per_token(c, bytes_=2):
    """每个词元的键值缓存：每层存 K、V 各 kv 个头 × d_h 个数。"""
    return 2 * c["L"] * c["kv"] * (c["d"] // c["h"]) * bytes_
