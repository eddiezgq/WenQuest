"""算例 12.5.1—12.5.2：语音合成的代价（12.5 节）。

合成要把文字变回波形，而波形是每秒一万六千到两万四千个数。怎样产生它，决定了能不能实时。

（1）自回归声码器（WaveNet 式）：一个采样点一个采样点地生成，每个点都要过一遍网络。
    每秒要多少次前向、多少运算量；在 A10 上按峰值算要多久——远远不够实时。
（2）并行声码器（HiFi-GAN 一类）：从梅尔频谱一次性上采样到波形，是卷积，不是逐点自回归。
    运算量不小，但可以一次算完一整段，实时率高几个数量级。
（3）流式合成的延迟：按 50 ms 一块地输出时，首字延迟与每块的计算时间要满足什么关系才不断流。
"""
import numpy as np

from bookout import out
from gpus import GPUS

SR_TTS = 24000                                               # 合成常用的采样率
A10 = GPUS["a10"]["fp16t"]
v = {"sr": SR_TTS}

# ---------- （1）自回归：每个采样点一次前向
WN_LAYERS, WN_CH, WN_SKIP, WN_Q = 30, 64, 256, 256           # 30 层、64 通道、跳连 256、输出 256 档量化
# 每层：门控的两个 2 抽头空洞卷积 + 残差与跳连的两个 1×1 卷积；末端两层 1×1 卷积加 softmax
per_layer = 2 * (2 * 2 * WN_CH * WN_CH) + 2 * (2 * WN_CH * (WN_CH + WN_SKIP))
per_sample = WN_LAYERS * per_layer + 2 * 2 * WN_SKIP * WN_Q
v["wn_per_sample"] = per_sample
v["wn_per_sample_M"] = per_sample / 1e6
v["wn_fwd_per_s"] = SR_TTS
v["wn_GF_per_s"] = per_sample * SR_TTS / 1e9
v["wn_ms_per_s"] = per_sample * SR_TTS / A10 * 1e3           # 按峰值算，合成 1 秒音频要多少毫秒
# 但自回归逐点生成根本用不满算力：每次只算一个点，受启动开销与延迟限制（第 6、7 章）
LAUNCH_US = 5.0                                              # 一次极小的核函数调用，几微秒（算例 6.2.1 的量级）
v["wn_launch_s_per_s"] = SR_TTS * WN_LAYERS * LAUNCH_US / 1e6   # 只算启动开销就要这么多秒
v["wn_rtf_launch"] = v["wn_launch_s_per_s"]                  # 实时率（>1 就跟不上）

# ---------- （2）并行声码器：从梅尔频谱卷积上采样
# 公开实现（HiFi-GAN 一类）的生成器：几级转置卷积把 100 帧/秒的梅尔频谱上采样到 24 000 点/秒，
# 通道从 512 逐级减半，每级后接多感受野残差块。按这些层逐个数，合成 1 秒音频约几十 GFLOP：
UP = SR_TTS / 100                                            # 每帧（10 ms）要产生 240 个采样点
v["up"] = UP
# HiFi-GAN V1 的生成器：7×1 卷积进（512 通道）→ 四级转置卷积上采样 8、8、2、2，通道 512→256→128→64→32
# → 每级后三个多感受野残差块、各两层 3 抽头空洞卷积 → 7×1 卷积出。按每级的输出采样率逐层累加乘加数：
up_rates, ch = (8, 8, 2, 2), 512
rate = SR_TTS / (8 * 8 * 2 * 2)                              # 第一级之前的帧率（= 梅尔帧率 × 上采样前的倍数）
flops = 2 * 7 * 80 * ch * rate                               # 入口卷积
for u in up_rates:
    rate *= u
    flops += 2 * (2 * u) * ch * (ch // 2) * rate             # 转置卷积（核长取 2u）
    ch //= 2
    for _ in range(3):                                       # 三个残差块，每块两层 3 抽头卷积
        flops += 2 * 2 * 3 * ch * ch * rate
flops += 2 * 7 * ch * 1 * rate                               # 出口卷积
hifi_GF_per_s = flops / 1e9
v["hifi_GF_per_s"] = hifi_GF_per_s
v["hifi_ms_per_s"] = hifi_GF_per_s * 1e9 / A10 * 1e3
v["hifi_rtf"] = v["hifi_ms_per_s"] / 1000
v["hifi_inv"] = 1000 / v["hifi_ms_per_s"]
v["speedup"] = v["wn_launch_s_per_s"] / max(v["hifi_rtf"], 1e-9)
v["wn_vs_hifi_GF"] = v["wn_GF_per_s"] / v["hifi_GF_per_s"]   # 自回归的运算量反而更少，却慢几个数量级

# ---------- （3）流式：一块 50 ms
CHUNK_MS = 50
v["chunk_ms"] = CHUNK_MS
v["chunk_samples"] = int(SR_TTS * CHUNK_MS / 1000)
v["chunk_compute_ms"] = v["hifi_ms_per_s"] * CHUNK_MS / 1000
v["headroom"] = CHUNK_MS / max(v["chunk_compute_ms"], 1e-9)  # 每块的计算时间要远小于一块的时长
v["ttfb_ms"] = CHUNK_MS + v["chunk_compute_ms"]              # 首字延迟：攒够一块 + 算一块
out(**v)
