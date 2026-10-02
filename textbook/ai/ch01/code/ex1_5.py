"""算例 1.5.1～1.5.4：AlexNet 的逐层运算量；一张图在不同硬件上的理想耗时；AlexNet 训练的算力利用率；
矩阵乘法与大模型逐词生成的计算强度。

式 (1.5.1)：卷积层乘加数 = H_out W_out C_out × K_h K_w C_in；全连接层 = d_in d_out。
式 (1.5.3)：T ≥ max(W/P, Q/β)；式 (1.5.4)：计算强度 I = W/Q。
"""
from _ch1 import ALEXNET, CPU, HW, alexnet_layers, cpu_bw, cpu_peak, gtx580_peak
from bookout import T, out

rows = alexnet_layers()
macs = sum(m for _, m, _ in rows)
params = sum(p for _, _, p in rows)
conv_macs = sum(m for n, m, _ in rows if n.startswith("conv"))
fc_params = sum(p for n, _, p in rows if n.startswith("fc"))
conv1 = rows[0]
flop_img = 2 * macs                                  # 一张图前向的运算量
outs_conv1 = 55 * 55 * 96                            # conv1 的输出个数：彼此独立的点积
len_conv1 = 11 * 11 * 3

# 算例 1.5.2：一张图（前向）在不同硬件上的理想耗时（按峰值，u = 1）
P_core = cpu_peak(1)
P_cpu = cpu_peak()
P_580 = gtx580_peak()
P_h32 = HW["h100"]["P_fp32"]
P_h16 = HW["h100"]["P_fp16"]
t_core = flop_img / P_core
t_cpu = flop_img / P_cpu
t_h16 = flop_img / P_h16
speed_h16_core = P_h16 / P_core

# 算例 1.5.3：AlexNet 训练的算力利用率（两块 GTX 580，五到六天）
C_train = 3 * flop_img * ALEXNET["train_images"] * ALEXNET["epochs"]
t_ideal = C_train / (ALEXNET["gpus"] * P_580)
u_lo = t_ideal / (ALEXNET["days"][1] * 86400)
u_hi = t_ideal / (ALEXNET["days"][0] * 86400)
t_ideal_cpu_core = C_train / P_core

# 算例 1.5.4：计算强度
n = 4096
W_mm = 2 * n ** 3
Q_mm = 3 * n * n * 4                                  # FP32：读 A、B，写 C
I_mm = W_mm / Q_mm
bal_cpu = P_cpu / cpu_bw()
bal_h16 = P_h16 / HW["h100"]["bw"]
N7 = 7e9
W_tok = 2 * N7                                       # 生成一个词元：每个参数一次乘加
Q_tok = 2 * N7                                       # FP16 权重每个 2 字节，每生成一个词元读一遍
t_tok_compute = W_tok / P_h16
t_tok_mem = Q_tok / HW["h100"]["bw"]
tok_per_s = 1 / t_tok_mem
t_tok_cpu = Q_tok / cpu_bw()
batch_balance = bal_h16                              # 一批 B 条序列共用一次读权重：I = B

out(macs_M=macs / 1e6, params_M=params / 1e6, gflop_img=flop_img / 1e9, conv_macs_pct=conv_macs / macs * 100,
    fc_params_pct=fc_params / params * 100, conv1_macs_M=conv1[1] / 1e6, outs_conv1=outs_conv1, len_conv1=len_conv1,
    P_core_G=P_core / 1e9, P_cpu_T=P_cpu / 1e12, P_580_T=P_580 / 1e12, P_h32_T=P_h32 / 1e12, P_h16_T=P_h16 / 1e12,
    cpu_cores=CPU["cores"], cpu_ghz=CPU["clock"] / 1e9, cpu_fpc=CPU["flop_per_cycle"], cpu_bw_G=cpu_bw() / 1e9,
    t_core_ms=t_core * 1e3, t_cpu_us=t_cpu * 1e6, t_h16_us=t_h16 * 1e6, speed_h16_core=speed_h16_core,
    C_train_e=f"{C_train:.1e}".replace("e+", "\\times10^{") + "}", t_ideal_days=t_ideal / 86400,
    u_lo_pct=u_lo * 100, u_hi_pct=u_hi * 100, t_core_days=t_ideal_cpu_core / 86400,
    n=n, W_mm_G=W_mm / 1e9, Q_mm_MB=Q_mm / 1e6, I_mm=I_mm, bal_cpu=bal_cpu, bal_h16=bal_h16,
    h100_bw_T=HW["h100"]["bw"] / 1e12, W_tok_G=W_tok / 1e9, t_tok_compute_us=t_tok_compute * 1e6,
    t_tok_mem_ms=t_tok_mem * 1e3, tok_per_s=tok_per_s, t_tok_cpu_ms=t_tok_cpu * 1e3, batch_balance=batch_balance,
    ratio_mem_compute=t_tok_mem / t_tok_compute, gtx580_cores=HW["gtx580"]["cores"], gtx580_mhz=HW["gtx580"]["clock"] / 1e6)
