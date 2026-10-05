"""第 2 章的小型 Transformer（2.9 节，程序 2.9.1 的 PyTorch 写法）：V = 2048，T = 256，d = 384，6 层，6 头，d_ff = 1536，
前置层归一化，GELU 用 tanh 近似，因果注意力，输出层与词元嵌入共享权重，共 11 532 288 个参数。
注意力按 2.3 节的写法一步步算（矩阵乘法、缩放、掩码、softmax、矩阵乘法），以便看清框架为每一步发出的核函数（7.1、7.6 节）。"""
import math

import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import functional as F

V, T, D, L, H, FF = 2048, 256, 384, 6, 6, 1536


class Block(nn.Module):
    def __init__(self):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(D), nn.LayerNorm(D)
        self.qkv, self.proj = nn.Linear(D, 3 * D), nn.Linear(D, D)
        self.ff1, self.ff2 = nn.Linear(D, FF), nn.Linear(FF, D)
        self.register_buffer("mask", torch.triu(torch.ones(T, T, dtype=torch.bool), 1), persistent=False)

    def forward(self, x):
        b, t, _ = x.shape
        q, k, v = self.qkv(self.ln1(x)).split(D, dim=-1)
        q, k, v = [z.view(b, t, H, D // H).transpose(1, 2) for z in (q, k, v)]        # (b, h, t, d_h)：视图，不连续
        att = (q @ k.transpose(-2, -1)) * (1 / math.sqrt(D // H))
        att = att.masked_fill(self.mask[:t, :t], float("-inf")).softmax(dim=-1)
        y = (att @ v).transpose(1, 2).reshape(b, t, D)
        x = x + self.proj(y)
        return x + self.ff2(F.gelu(self.ff1(self.ln2(x)), approximate="tanh"))


class Tiny(nn.Module):
    def __init__(self, checkpoint=False):
        super().__init__()
        self.tok = nn.Embedding(V, D)
        self.pos = nn.Parameter(torch.zeros(T, D))
        self.blocks = nn.ModuleList(Block() for _ in range(L))
        self.lnf = nn.LayerNorm(D)
        self.checkpoint = checkpoint
        for p in self.parameters():
            if p.dim() == 2:
                nn.init.normal_(p, 0.0, 0.02)

    def forward(self, ids):
        x = self.tok(ids) + self.pos[: ids.shape[1]]
        for blk in self.blocks:
            # 重计算（7.6 节）：每层只保存输入，反向时重做这一层的前向
            x = torch.utils.checkpoint.checkpoint(blk, x, use_reentrant=False) if self.checkpoint else blk(x)
        return self.lnf(x) @ self.tok.weight.T


def loss_fn(logits, ids):
    """每个位置预测下一个词元的交叉熵。"""
    return F.cross_entropy(logits[:, :-1].reshape(-1, V), ids[:, 1:].reshape(-1))
