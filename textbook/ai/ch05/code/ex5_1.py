"""算例 5.1.1—5.1.3：映射的融合；3×3 模板计算的数据搬运量、分块的晕圈开销与计算强度。理论值按 A10（实测所用的显卡）计算。"""
from _ch5 import A10, H, W
from bookout import out

bw = A10["bw"]
ridge32 = A10["fp32"] / bw                                 # 单精度的平衡点（FLOP/B）

# 算例 5.1.1：小型 Transformer 前馈网络第一层的输出（B = 32，T = 256，d_ff = 1536）先加偏置、再过 GELU
n_ff = 32 * 256 * 1536
unfused_B = n_ff * 4 * 4                                   # 两个核函数：读 x、写 t；读 t、写 y（偏置只有 1536 个数，忽略）
fused_B = n_ff * 4 * 2                                     # 一个核函数：读 x、写 y
t_unfused_us = unfused_B / bw * 1e6
t_fused_us = fused_B / bw * 1e6

# 算例 5.1.2：3×3 平滑（加权平均），每个输出 9 次乘法、8 次加法
flop_px = 17
reads_naive = 9                                            # 不靠缓存：每个输出从显存读 9 个数
halo = {T: (T + 2) ** 2 / T ** 2 for T in (8, 16, 32)}     # 分块：T×T 个输出要读 (T+2)×(T+2) 个输入
I_naive = flop_px / ((reads_naive + 1) * 4)                # 加上写一个输出
I_t16 = flop_px / ((halo[16] + 1) * 4)
I_ideal = flop_px / (2 * 4)                                # 每个输入只读一次
t_ideal_us = W * H * 2 * 4 / bw * 1e6

out(n_ff_M=n_ff / 1e6, unfused_MB=unfused_B / 1e6, fused_MB=fused_B / 1e6, t_unfused_us=t_unfused_us, t_fused_us=t_fused_us,
    ridge32=ridge32, flop_px=flop_px, halo8=halo[8], halo16=halo[16], halo32=halo[32], I_naive=I_naive, I_t16=I_t16, I_ideal=I_ideal,
    t_ideal_us=t_ideal_us, px_M=W * H / 1e6)
