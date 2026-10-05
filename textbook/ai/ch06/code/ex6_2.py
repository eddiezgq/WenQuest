"""算例 6.2.1、6.2.2：启动开销有多大。第 2 章的小型 Transformer（V = 2048，d = 384，6 层，6 头，d_ff = 1536）在 A10 上：
（1）训练时一次前向（B = 32，T = 256）的运算量与按半精度张量核心峰值的最短时间，核函数个数；
（2）逐词生成时（批大小 1）每生成一个词元：读一遍权重的最短时间与核函数个数。
每次启动的开销取 5 μs（主机发出一次启动的典型量级；程序 6.2.1 实测）。"""
from _ch6 import A10
from bookout import out

V, d, L, T, B, dff = 2048, 384, 6, 256, 32, 1536
per_layer = 4 * d * d + 2 * d * dff                       # QKV、输出投影、前馈网络两层的权重
n_tok = B * T
flop = 2 * L * per_layer * n_tok + 2 * d * V * n_tok + L * 4 * B * T * T * d   # 线性层、输出层、注意力的 QKᵀ 与 AV
t_fwd_us = flop / A10["fp16t"] * 1e6
# 每层的核函数：层归一化 2、QKV 1、QKᵀ 1、softmax 1、AV 1、输出投影 1、残差 2、FF1 1、GELU 1、FF2 1——共 12 个；另有嵌入、最后的层归一化、输出层
kernels = 12 * L + 3
launch_us = 5.0
over_fwd = kernels * launch_us
weights_B = (L * per_layer + d * V) * 2                   # 半精度
t_dec_us = weights_B / A10["bw"] * 1e6
over_dec = kernels * launch_us                            # 启动跟不上时，每个词元至少要这么久
# 启动是异步的：主机发出命令的速度比 GPU 执行得快时，主机跑在前面，启动开销被藏住；核函数平均比启动开销还短时，GPU 反过来等主机
avg_fwd = t_fwd_us / kernels
avg_dec = t_dec_us / kernels
out(GFLOP=flop / 1e9, t_fwd_us=t_fwd_us, kernels=kernels, launch_us=launch_us, over_fwd=over_fwd, avg_fwd=avg_fwd,
    weights_MB=weights_B / 1e6, t_dec_us=t_dec_us, over_dec=over_dec, avg_dec=avg_dec, ratio_dec=over_dec / t_dec_us)
