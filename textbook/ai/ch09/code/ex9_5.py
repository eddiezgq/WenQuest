"""算例 9.5.1、9.5.2：选择性激活重计算；混合专家模型。
（1）按算例 9.1.1 的估计式，每层激活值 s·b·h·(34 + 5·a·s/h)，后一项是注意力的得分、softmax 输出与它的随机失活掩码（形状 a·s·s）。
    科尔蒂坎蒂等 2022 年提出只重计算这一部分（“选择性重计算”）：7B 模型、s = 4096 时省下激活值的多少；
    多出的运算是每层重做 QKᵀ 与 PV（4·b·s²·h 次），占一个训练步（约三次前向）的多少。与 7.6.4 节“整层重计算多三分之一”对比。
（2）混合专家：把前馈网络换成 E 个“专家”，每个词元由路由器挑 k 个。按公开的 Mixtral 8×7B 的结构（32 层，d = 4096，
    32 个查询头、8 个键值头，每个专家是 d_ff = 14 336 的 SwiGLU，E = 8，k = 2，词表 32 000）：参数总数与每个词元实际用到的参数数。"""
from _ch9 import BIG, params
from bookout import out

s, b, h, a = 4096, 1, BIG["d"], BIG["h"]
full = 34 + 5 * a * s / h
saved_pct = 100 * (5 * a * s / h) / full
layer_fwd = 2 * b * s * (4 * h * h + 3 * h * BIG["dff"]) + 4 * b * s * s * h      # 一层前向：线性层 + 注意力的两次矩阵乘法
extra_pct = 100 * 4 * b * s * s * h / (3 * layer_fwd)

mix = dict(L=32, d=4096, h=32, kv=8, dff=14336, V=32000, glu=True, tied=False)
E, k = 8, 2
total = params(dict(mix, dff=mix["dff"] * E))           # E 个专家的前馈网络参数相当于 d_ff 放大 E 倍
active = params(dict(mix, dff=mix["dff"] * k))
out(full=full, saved_pct=saved_pct, extra_pct=extra_pct, total_B=total / 1e9, active_B=active / 1e9, ratio=total / active)
