"""算例 2.10.1、2.10.2：小型 Transformer 一次前向计算中各类运算的浮点运算量、数据搬运量与计算强度（半精度存储），
与 H100 的 P/β 比较判断瓶颈；验证每个词元的前向运算量 ≈ 2N + 2LTd。

计数约定：矩阵乘法 M×K 乘 K×N 计 2MNK FLOP；逐元素运算按每个元素的近似 FLOP 数计（层归一化 8、softmax 5、GELU 10、
加法 1）；数据量为每个运算单独执行时至少要读入的输入、权重与写出的输出（不考虑运算之间的融合与缓存复用），每个数 2 字节。
"""
from _ch2 import TINY, tiny_params
from bookout import out

B, T = 32, TINY["ctx"]
d, L, h, f, V = TINY["d"], TINY["layers"], TINY["heads"], TINY["ff"], TINY["vocab"]
by = 2                                     # 半精度
P_h100, bw_h100 = 989.4e12, 3.35e12
balance = P_h100 / bw_h100
n = B * T                                  # 一批中的词元数


def mm(M, K, N, w_shared=True):
    """矩阵乘法 (M×K)(K×N)：FLOP 与字节（读 A、B，写 C）。"""
    return 2 * M * K * N, by * (M * K + K * N + M * N)


ops = []                                   # (名称, 类别, FLOP, 字节)
for l in range(L):
    ops.append(("LN1", "elem", 8 * n * d, by * (2 * n * d + 2 * d)))
    ops.append(("QKV", "mm", *mm(n, d, 3 * d)))
    s_flop = 2 * B * h * T * T * (d // h)                      # QKᵀ：每个头 (T×d_h)(d_h×T)
    ops.append(("QK^T", "mm", s_flop, by * (2 * n * d + B * h * T * T)))
    ops.append(("softmax", "elem", 5 * B * h * T * T, by * 2 * B * h * T * T))
    ops.append(("AV", "mm", s_flop, by * (B * h * T * T + n * d + n * d)))
    ops.append(("proj", "mm", *mm(n, d, d)))
    ops.append(("add1", "elem", n * d, by * 3 * n * d))
    ops.append(("LN2", "elem", 8 * n * d, by * (2 * n * d + 2 * d)))
    ops.append(("FF1", "mm", *mm(n, d, f)))
    ops.append(("GELU", "elem", 10 * n * f, by * 2 * n * f))
    ops.append(("FF2", "mm", *mm(n, f, d)))
    ops.append(("add2", "elem", n * d, by * 3 * n * d))
ops.append(("LNf", "elem", 8 * n * d, by * (2 * n * d + 2 * d)))
ops.append(("logits", "mm", *mm(n, d, V)))

W_total = sum(o[2] for o in ops)
Q_total = sum(o[3] for o in ops)
W_mm = sum(o[2] for o in ops if o[1] == "mm")
Q_mm = sum(o[3] for o in ops if o[1] == "mm")
W_el = W_total - W_mm
Q_el = Q_total - Q_mm


def group(names):
    w = sum(o[2] for o in ops if o[0] in names)
    q = sum(o[3] for o in ops if o[0] in names)
    return w, q


rows = {}
for key, names in (("linear", {"QKV", "proj", "FF1", "FF2", "logits"}), ("attn", {"QK^T", "AV"}), ("softmax", {"softmax"}),
                   ("norm", {"LN1", "LN2", "LNf"}), ("gelu", {"GELU"}), ("add", {"add1", "add2"})):
    w, q = group(names)
    rows[key] = (w, q, w / q, w / W_total * 100, q / Q_total * 100)

# 按 W/P 与 Q/β 的较大者估计每个运算的耗时下限，再按类别相加，看时间花在哪里
cat = {"QKV": "linear", "proj": "linear", "FF1": "linear", "FF2": "linear", "logits": "linear", "QK^T": "attn", "AV": "attn",
       "softmax": "softmax", "LN1": "norm", "LN2": "norm", "LNf": "norm", "GELU": "gelu", "add1": "add", "add2": "add"}
t = {k: 0.0 for k in rows}
n_mem = 0
for name, _, w, q in ops:
    t[cat[name]] += max(w / P_h100, q / bw_h100)
    n_mem += q / bw_h100 > w / P_h100
t_total = sum(t.values())
t_share = {k: v / t_total * 100 for k, v in t.items()}

# 每个词元的前向运算量与 2N + 2LTd（Kaplan 等 2020 的估计，N 不含嵌入层，这里加上输出层的 2Vd）
N_ne = tiny_params(TINY)["non_emb"]
per_token = W_mm / n
kaplan_full = 2 * N_ne + 4 * L * T * d + 2 * V * d      # 不利用因果掩码：QKᵀ 与 AV 各 2Td
kaplan = 2 * N_ne + 2 * L * T * d + 2 * V * d           # 利用因果掩码只算下三角：平均只看 T/2 个位置
train_per_token = 3 * per_token

out(B=B, T=T, n_tok=n, W_G=W_total / 1e9, Q_MB=Q_total / 2 ** 20, mm_pct=W_mm / W_total * 100, el_pct=W_el / W_total * 100,
    mmQ_pct=Q_mm / Q_total * 100, elQ_pct=Q_el / Q_total * 100,
    **{f"{k}_W": v[0] / 1e9 for k, v in rows.items()}, **{f"{k}_I": v[2] for k, v in rows.items()},
    **{f"{k}_Wp": v[3] for k, v in rows.items()}, **{f"{k}_Qp": v[4] for k, v in rows.items()},
    **{f"{k}_tp": v for k, v in t_share.items()}, t_total_us=t_total * 1e6, el_tp=t_share['softmax'] + t_share['norm'] + t_share['gelu'] + t_share['add'],
    mm_tp=t_share['linear'] + t_share['attn'], balance=balance,
    per_token_M=per_token / 1e6, kaplan_M=kaplan / 1e6, kaplan_full_M=kaplan_full / 1e6, n_mem=n_mem, n_ops=len(ops), N_ne=N_ne, train_per_token_M=train_per_token / 1e6)
