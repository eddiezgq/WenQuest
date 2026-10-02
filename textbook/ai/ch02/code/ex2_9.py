"""算例 2.9.1～2.9.3：一个 4 个词元的小例子上的缩放点积注意力（含因果掩码）；为什么要除以 √d_k；
贯穿全书的小型 Transformer：用 NumPy 写出完整的前向计算，核对参数量与因果性。

式 (2.9.1)：Attention(Q, K, V) = softmax(QKᵀ/√d_k + M) V；式 (2.9.6)：前置层归一化的 Transformer 块。
"""
import math

import numpy as np

from _ch2 import TINY, tiny_params
from bookout import out, tex


def softmax(z, axis=-1):
    z = z - z.max(axis=axis, keepdims=True)        # 先减最大值，防止溢出（2.2.5 节）
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)


# ---------------------------------------------------------------- 算例 2.9.1
Q = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, -1.0]])
K = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [-1.0, 0.0]])
V = np.array([[1.0, 0.0], [0.0, 1.0], [0.5, 0.5], [0.0, 0.0]])
dk = 2
S = Q @ K.T / math.sqrt(dk)
A = softmax(S)
O = A @ V
mask = np.triu(np.full((4, 4), -np.inf), k=1)      # 只能看自己和之前的词元
Ac = softmax(S + mask)
Oc = Ac @ V
assert np.allclose(A.sum(1), 1) and np.allclose(Ac.sum(1), 1) and np.allclose(np.triu(Ac, 1), 0)

# ---------------------------------------------------------------- 算例 2.9.2：方差与 softmax 饱和
rng = np.random.default_rng(0)
d64 = 64
q = rng.normal(size=(20000, d64))
k = rng.normal(size=(20000, d64))
dots = np.sum(q * k, axis=1)
var_dot = float(dots.var())
var_scaled = float((dots / math.sqrt(d64)).var())
z = rng.normal(size=(5000, 16, d64)) @ rng.normal(size=(d64,))   # 16 个键对同一个查询的分数，重复 5000 次
pmax_raw = float(softmax(z, axis=1).max(axis=1).mean())
pmax_scaled = float(softmax(z / math.sqrt(d64), axis=1).max(axis=1).mean())

# ---------------------------------------------------------------- 算例 2.9.3：小型 Transformer 的完整前向计算
c = TINY
V_, Tm, d, L, h, f = c["vocab"], c["ctx"], c["d"], c["layers"], c["heads"], c["ff"]
dh = d // h
rng = np.random.default_rng(42)
std = 0.02
P = {"tok": rng.normal(0, std, (V_, d)), "pos": rng.normal(0, std, (Tm, d)), "lnf_g": np.ones(d), "lnf_b": np.zeros(d)}
for l in range(L):
    P[f"{l}.ln1_g"], P[f"{l}.ln1_b"] = np.ones(d), np.zeros(d)
    P[f"{l}.qkv_w"], P[f"{l}.qkv_b"] = rng.normal(0, std, (d, 3 * d)), np.zeros(3 * d)
    P[f"{l}.proj_w"], P[f"{l}.proj_b"] = rng.normal(0, std, (d, d)), np.zeros(d)
    P[f"{l}.ln2_g"], P[f"{l}.ln2_b"] = np.ones(d), np.zeros(d)
    P[f"{l}.ff1_w"], P[f"{l}.ff1_b"] = rng.normal(0, std, (d, f)), np.zeros(f)
    P[f"{l}.ff2_w"], P[f"{l}.ff2_b"] = rng.normal(0, std, (f, d)), np.zeros(d)
n_params = sum(v.size for v in P.values())
assert n_params == tiny_params(c)["total"]


def ln(x, g, b, eps=1e-5):
    mu = x.mean(-1, keepdims=True)
    var = x.var(-1, keepdims=True)
    return g * (x - mu) / np.sqrt(var + eps) + b


def gelu(x):
    return 0.5 * x * (1 + np.tanh(math.sqrt(2 / math.pi) * (x + 0.044715 * x ** 3)))


def forward(ids):
    B, T = ids.shape
    x = P["tok"][ids] + P["pos"][:T]                                 # (B, T, d)
    causal = np.triu(np.full((T, T), -np.inf), k=1)
    for l in range(L):
        a = ln(x, P[f"{l}.ln1_g"], P[f"{l}.ln1_b"])
        qkv = a @ P[f"{l}.qkv_w"] + P[f"{l}.qkv_b"]                   # (B, T, 3d)
        q_, k_, v_ = [t.reshape(B, T, h, dh).transpose(0, 2, 1, 3) for t in np.split(qkv, 3, axis=-1)]
        att = softmax(q_ @ k_.transpose(0, 1, 3, 2) / math.sqrt(dh) + causal)   # (B, h, T, T)
        y = (att @ v_).transpose(0, 2, 1, 3).reshape(B, T, d)
        x = x + y @ P[f"{l}.proj_w"] + P[f"{l}.proj_b"]               # 残差
        a = ln(x, P[f"{l}.ln2_g"], P[f"{l}.ln2_b"])
        x = x + gelu(a @ P[f"{l}.ff1_w"] + P[f"{l}.ff1_b"]) @ P[f"{l}.ff2_w"] + P[f"{l}.ff2_b"]
    x = ln(x, P["lnf_g"], P["lnf_b"])
    return x @ P["tok"].T                                            # 输出层与词元嵌入共享权重，(B, T, V)


ids = rng.integers(0, V_, size=(2, 32))
logits = forward(ids)
assert logits.shape == (2, 32, V_)
ids2 = ids.copy()
ids2[:, 20:] = rng.integers(0, V_, size=(2, 12))                     # 改动第 20 个位置以后的词元
logits2 = forward(ids2)
causal_ok = bool(np.allclose(logits[:, :20], logits2[:, :20]) and not np.allclose(logits[:, 20:], logits2[:, 20:]))
assert causal_ok
lg, tg = logits[:, :-1], ids[:, 1:]                                 # 每个位置预测下一个词元
loss0 = float(np.mean(np.log(np.exp(lg - lg.max(-1, keepdims=True)).sum(-1)) + lg.max(-1)
                      - np.take_along_axis(lg, tg[..., None], -1)[..., 0]))
tp = tiny_params(c)

out(S=tex(S, 3), A=tex(A, 3), O=tex(O, 3), Ac=tex(Ac, 3), Oc=tex(Oc, 3), a33=A[2, 2], a34=A[3, 3],
    var_dot=var_dot, var_scaled=var_scaled, pmax_raw=pmax_raw, pmax_scaled=pmax_scaled, d64=d64,
    V=V_, Tm=Tm, d=d, L=L, h=h, dh=dh, f=f, n_params=n_params, tok=tp["tok_emb"], pos=tp["pos_emb"],
    per_layer=tp["layer_total"], attn_layer=tp["per_layer"]["qkv"] + tp["per_layer"]["proj"],
    mlp_layer=tp["per_layer"]["ff1"] + tp["per_layer"]["ff2"], blocks=tp["blocks"], non_emb=tp["non_emb"],
    non_emb_M=tp["non_emb"] / 1e6, total_M=n_params / 1e6, loss0=loss0, lnV=math.log(V_))
