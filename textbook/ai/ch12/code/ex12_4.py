"""算例 12.4.1—12.4.3：大规模弱监督模型的账（12.4 节）。

Whisper 这类模型的做法是：不追求标注的干净，而是从网上收集几十万小时的"音频 + 字幕"弱标注数据，
用一个编码器—解码器 Transformer 一次学会多语种识别、翻译与时间戳。本程序算三件事：

（1）数据规模：几十万小时的音频有多少帧、多少字节；按 30 秒一段切成多少段——这决定了训练要多少算力。
（2）模型的运算量：按公开的结构（small：12 层编码器 + 12 层解码器、d = 768）算一次 30 秒音频的前向运算量，
    与第 2、11 章的公式一致；再算实时率（处理 1 秒音频要多少秒）的理论下限。
（3）字错率怎样算：编辑距离除以参考长度；插入很多时可以超过 100%。用几个例子核对。
"""
import numpy as np

from _ch12 import HOP_MS, SR, edit_distance, error_rate
from bookout import out
from gpus import GPUS

v = {}
# ---------- （1）数据规模
HOURS = 680000                                               # 公开报告的训练数据量（小时，量级）
v["hours"] = HOURS
v["years"] = HOURS / 24 / 365
v["frames"] = HOURS * 3600 * 1000 / HOP_MS                   # 每 10 ms 一帧
v["frames_T"] = v["frames"] / 1e12
v["raw_TB"] = HOURS * 3600 * SR * 2 / 1e12                   # 16 位原始波形
v["segments"] = HOURS * 3600 / 30                            # 30 秒一段
v["segments_M"] = v["segments"] / 1e6

# ---------- （2）运算量（按 small 的结构）
L_ENC = L_DEC = 12
D, FF, HEADS = 768, 3072, 12
T_ENC = 1500                                                 # 30 秒 ÷ 20 ms（编码器内部下采样一半）
T_DEC = 112                                                  # 一段里生成的词元数（量级）
v["L_enc"], v["L_dec"], v["d"], v["T_enc"] = L_ENC, L_DEC, D, T_ENC


def block(T, d, ff, cross_T=0):
    """一层 Transformer 的前向运算量：自注意力的四个投影 + 两次注意力矩阵乘法 + 前馈；
    有交叉注意力时再加一份（查询来自解码器、键值来自编码器）。"""
    f = 2 * T * (4 * d * d + 2 * ff * d) + 4 * T * T * d
    if cross_T:
        f += 2 * T * (4 * d * d) + 4 * T * cross_T * d
    return f


enc = L_ENC * block(T_ENC, D, FF)
dec = L_DEC * block(T_DEC, D, FF, cross_T=T_ENC)
v["enc_GF"] = enc / 1e9
v["dec_GF"] = dec / 1e9
v["total_GF"] = (enc + dec) / 1e9
v["enc_share"] = enc / (enc + dec) * 100
A10 = GPUS["a10"]["fp16t"]
# 解码是逐个词元生成的，每个词元都要把权重读一遍——与 9.7 节的结论一样，它受带宽限制，不受算力限制。
# 要读的是：解码器的权重（编码器只在开头跑一次，解码时不碰），加上交叉注意力要反复读的编码器键值缓存。
PARAMS_ALL = 244e6                                           # small 的总参数量（公开报告）
PARAMS_DEC = 154e6                                           # 其中解码器部分（按结构点算，约 1.54 亿）
BW = GPUS["a10"]["bw"]
kv_bytes = L_DEC * T_ENC * D * 2 * 2                         # 每层的 K 与 V，半精度
v["params_M"] = PARAMS_ALL / 1e6
v["params_dec_M"] = PARAMS_DEC / 1e6
v["kv_MB"] = kv_bytes / 1e6
v["enc_ms"] = enc / A10 * 1e3                                # 编码器：一次前向，受算力限制
v["dec_tok_ms"] = (PARAMS_DEC * 2 + kv_bytes) / BW * 1e3     # 解码每个词元：读解码器权重 + 编码器键值缓存
v["kv_share"] = kv_bytes / (PARAMS_DEC * 2 + kv_bytes) * 100
v["dec_ms"] = v["dec_tok_ms"] * T_DEC
v["t_min_ms"] = v["enc_ms"] + v["dec_ms"]
v["dec_share"] = v["dec_ms"] / v["t_min_ms"] * 100           # 时间几乎都花在解码上
v["speed_peak"] = 30 * 1000 / v["t_min_ms"]                  # 比实时快多少倍（理论上限）
v["speed_real"] = v["speed_peak"] * 0.3                      # 按三成效率估的量级
v["T_dec"] = T_DEC

# ---------- （3）字错率
ref = list("去三号工位取料")
cases = {"ok": list("去三号工位取料"), "sub": list("去三号工位取科"), "del": list("去三号工位取"),
         "ins": list("去三号工位取料料料料料料料料料")}
for k, hyp in cases.items():
    v["wer_" + k] = error_rate(ref, hyp) * 100
    v["ed_" + k] = edit_distance(ref, hyp)
v["ref_len"] = len(ref)
v["over100"] = v["wer_ins"] > 100
out(**v)
