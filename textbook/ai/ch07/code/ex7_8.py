"""算例 7.8.1：图编译把相邻的逐元素运算与归约融合以后，小型 Transformer 一次前向（B = 32，T = 256，单精度）
在逐元素运算上的核函数个数与显存流量少多少（_ch7.layer_ops 与 _ch7.fused_layer_ops，粗略估计）；
加上矩阵乘法（按单精度峰值）之后，前向的最短时间从多少降到多少。最后的层归一化、输出层与交叉熵两种情况相同，不计入比较。"""
from _ch7 import A10, L, gemm_flop, layer_ops, fused_layer_ops
from bookout import out


def other(ops):
    k = [o for o in ops if o[1] != "gemm"]
    return len(k), sum(r + w for _, _, r, w in k) * 4


ke, be = other(layer_ops())
kf, bf = other(fused_layer_ops())
t_gemm = sum(gemm_flop().values()) * L / A10["fp32"] * 1e6
t_e = be * L / A10["bw"] * 1e6
t_f = bf * L / A10["bw"] * 1e6
out(k_eager=ke, k_fused=kf, MB_eager=be / 1e6, MB_fused=bf / 1e6, ratio=be / bf,
    t_gemm_us=t_gemm, t_eager_us=t_gemm + t_e, t_fused_us=t_gemm + t_f, speedup=(t_gemm + t_e) / (t_gemm + t_f))
