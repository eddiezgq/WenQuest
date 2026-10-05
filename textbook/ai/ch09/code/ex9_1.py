"""算例 9.1.1—9.1.3：大模型的运算量与显存账。
（1）训练的运算量 ≈ 6ND（N 个参数、D 个词元：前向每个词元约 2N 次运算，反向约 4N 次），另加注意力中与序列长度有关的一项
    每个词元约 12·L·T·d（前向 4LTd 的三倍）。小型 Transformer（B = 32，T = 256）一步用 6ND 估计，与第 7 章逐项数出的前向运算量（算例 7.1.1）对照。
（2）70 亿参数一级的模型（Llama 2 7B 的结构）在 2 万亿个词元上训练：运算量；Llama 2 论文报告这个模型用了 184 320 个 A100 GPU 小时，
    由此反推平均的算力利用率（MFU，实际有效算力 / 峰值）。
（3）显存：混合精度 + AdamW 每个参数 16 字节（BF16 权重 2、梯度 2、FP32 主权重 4、两份 AdamW 状态 8）；
    激活值按科尔蒂坎蒂（V. Korthikanti）等 2022 年对 GPT 式结构（d_ff = 4h、GELU、有随机失活）的估计式，每层 s·b·h·(34 + 5·a·s/h) 字节
    （半精度、含随机失活的掩码；Llama 2 无随机失活、用 SwiGLU，实际略小，量级不变；
    s 序列长度、b 批大小、h 隐藏维度、a 头数）；用 FlashAttention 时不存注意力矩阵，括号内只剩 34。"""
from _ch9 import A100, BIG, SMALL, params
from bookout import out

# （1）小型 Transformer 一步
N_s = 11532288                                    # 2.9 节的参数个数
tok = 32 * 256
flop_6nd = 6 * N_s * tok
attn = 12 * SMALL["L"] * SMALL["T"] * SMALL["d"] * tok
fwd_ch7 = 206.158430208e9                        # 算例 7.1.1 逐项数出的一次前向（含输出层），程序 7.1.1
# （2）7B
N = params(BIG)
D = 2e12
flop = 6 * N * D
gpu_h = 184320
mfu = flop / (gpu_h * 3600 * A100["fp16t"])
days_1024 = flop / (1024 * A100["fp16t"] * mfu) / 86400
# （3）显存
state = 16 * N
s, b, h, a, L = 4096, 1, BIG["d"], BIG["h"], BIG["L"]
act_layer = s * b * h * (34 + 5 * a * s / h)
act_flash = s * b * h * 34
out(N_s=N_s, GFLOP_6nd=flop_6nd / 1e9, GFLOP_attn=attn / 1e9, GFLOP_3fwd=3 * fwd_ch7 / 1e9,
    N_B=N / 1e9, flop=flop, mfu_pct=100 * mfu, days_1024=days_1024, gpu_h=gpu_h,
    state_GB=state / 1e9, act_layer_GB=act_layer / 1e9, act_GB=L * act_layer / 1e9, act_flash_GB=L * act_flash / 1e9,
    total_GB=(state + L * act_layer) / 1e9)
