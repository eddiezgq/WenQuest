"""算例 11.7.1—11.7.3：部署的三笔账（11.7 节）。

（1）模型大小与读权重的时间：ResNet-50 一级的检测模型在 FP32、FP16、INT8 下各多大，
    在 A10（600 GB/s）与一块边缘设备（60 GB/s）上读一遍权重要多久（8.5、9.7 节的做法）。
（2）批大小、延迟与吞吐量：单张图的延迟由一次前向决定，吞吐量随批大小增长到算力饱和为止；
    产线上“每个零件尽快出结果”与“每秒处理多少零件”是两个不同的要求。
（3）端到端的预算：采集 → 传输 → 预处理 → 推理 → 后处理，一帧 16.7 ms 怎样分；
    哪几段可以重叠（第 6 章的流），重叠后吞吐量是多少。
"""
import numpy as np

from _ch11 import MODELS
from bookout import out
from gpus import GPUS

v = {}
PARAMS = MODELS["res"][1]                         # ResNet-50 一级主干的参数量（与算例 11.1.1 同源）
GF = MODELS["res"][0] / 1e9 * (1280 / 224) ** 2   # 1280×1280 输入时一次前向的运算量（与算例 11.6.3 同源）
A10_BW, A10_FP16 = GPUS["a10"]["bw"], GPUS["a10"]["fp16t"]   # 全书共用的规格表
EDGE_BW = 60e9                                    # 一块边缘设备的显存带宽（量级）

# ---------- （1）模型大小与读权重
for name, byt in (("fp32", 4), ("fp16", 2), ("int8", 1)):
    sz = PARAMS * byt
    v[name + "_MB"] = sz / 1e6
    v[name + "_a10_ms"] = sz / A10_BW * 1e3
    v[name + "_edge_ms"] = sz / EDGE_BW * 1e3
v["int8_shrink"] = v["fp32_MB"] / v["int8_MB"]

# ---------- （2）批大小、延迟与吞吐
def latency_ms(batch, eff=0.35):
    """一次前向的时间：运算量 ÷（峰值 × 实际效率），再加一个固定的启动与后处理开销。"""
    return batch * GF * 1e9 / (A10_FP16 * eff) * 1e3 + 1.2


for b in (1, 2, 4, 8, 16, 32):
    t = latency_ms(b)
    v[f"b{b}_ms"] = t
    v[f"b{b}_fps"] = b / t * 1e3
v["fps1"], v["fps32"] = v["b1_fps"], v["b32_fps"]
v["gain32"] = v["b32_fps"] / v["b1_fps"]
v["lat32"] = v["b32_ms"]

# ---------- （3）端到端预算（一帧 16.7 ms）
STAGES = [("采集", 2.0), ("传输", 3.5), ("预处理", 1.5), ("推理", latency_ms(1) - 1.2), ("后处理", 1.0)]
total = sum(t for _, t in STAGES)
v["budget_ms"] = 1000 / 60
v["serial_ms"] = total
v["serial_fps"] = 1000 / total
v["slowest"] = max(STAGES, key=lambda s: s[1])[0]
v["slowest_ms"] = max(t for _, t in STAGES)
v["pipe_fps"] = 1000 / v["slowest_ms"]            # 完全重叠后，吞吐量由最慢的一段决定（第 6 章）
v["pipe_gain"] = v["pipe_fps"] / v["serial_fps"]
v["fits_60"] = v["pipe_fps"] >= 60
for name, t in STAGES:
    key = {"采集": "cap", "传输": "xfer", "预处理": "pre", "推理": "infer", "后处理": "post"}[name]
    v[key + "_ms"] = t
out(**v)
