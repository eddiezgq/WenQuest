"""算例 10.1.1—10.1.3：把各家加速器放进同一张表（10.1 节）。

（1）峰值算力、显存带宽、屋脊点（3.8 节）：同一个受带宽限制的运算，在不同的加速器上照样受带宽限制——
    各家的屋脊点都在几百 FLOP/B 这个量级，差别远小于峰值算力的差别。
（2）厂商公布了什么、没公布什么：按本章资料卡的规格表数一数每条里的空缺项。
（3）峰值与可达：AMD 自己公布的矩阵乘法可达算力只有峰值的一半左右（MI300X：FP16 654 对 1307 TFLOP/s）。
    这组数字出自厂商自己的博客，是讲“峰值算力只是上限”最硬的一手材料（3.8 节）。
"""
from _ch10 import ACC, MAF, missing, roofline
from bookout import out

v = {"n_acc": len(ACC)}
for k, a in ACC.items():
    v[k + "_bf16"] = a["bf16"] / 1e12 if a["bf16"] else None       # TFLOP/s
    v[k + "_low"] = a["low"] / 1e12 if a["low"] else None
    v[k + "_bw"] = a["bw"] / 1e12 if a["bw"] else None             # TB/s
    v[k + "_mem"] = a["mem"] / 1e9                                 # GB
    v[k + "_link"] = a["link"] / 1e9 if a["link"] else None        # GB/s
    v[k + "_ridge"] = roofline(a)
    v[k + "_ridge_low"] = roofline(a, use_low=True)               # 只公布低精度峰值的卡用它
    v[k + "_tdp"] = a["tdp"]
    v[k + "_units"] = a["units"]
    v[k + "_miss"] = missing(a)

# （1）屋脊点：有峰值也有带宽的那几条
ridges = {k: roofline(a) for k, a in ACC.items() if roofline(a) is not None}
v["ridge_min"] = min(ridges.values())
v["ridge_max"] = max(ridges.values())
v["ridge_min_name"] = ACC[min(ridges, key=ridges.get)]["name"]
v["ridge_max_name"] = ACC[max(ridges, key=ridges.get)]["name"]
peaks = {k: ACC[k]["bf16"] for k in ridges}
v["peak_ratio"] = max(peaks.values()) / min(peaks.values())        # 峰值相差几倍
v["peak_min"] = min(peaks.values()) / 1e12
v["peak_min_name"] = ACC[min(peaks, key=peaks.get)]["name"]
v["peak_max"] = max(peaks.values()) / 1e12
v["peak_max_name"] = ACC[max(peaks, key=peaks.get)]["name"]
v["ridge_ratio"] = v["ridge_max"] / v["ridge_min"]                 # 屋脊点只相差几倍

# （2）空缺项：国产厂商与国外厂商各有多少项没公布
dom = [k for k, a in ACC.items() if a["vendor"] not in ("NVIDIA", "AMD", "Google")]
oth = [k for k in ACC if k not in dom]
v["n_dom"] = len(dom)
v["miss_dom"] = sum(missing(ACC[k]) for k in dom) / len(dom)       # 平均空缺项数（满分 6）
v["miss_oth"] = sum(missing(ACC[k]) for k in oth) / len(oth)
v["no_peak"] = sum(1 for k, a in ACC.items() if a["bf16"] is None)  # 连一个稠密峰值都没有的

# （3）峰值与可达
for k, m in MAF.items():
    v[k + "_maf_fp16"] = m["fp16"] / 1e12
    v[k + "_maf_pct"] = m["fp16"] / m["peak_fp16"] * 100
    v[k + "_maf_fp8"] = m["fp8"] / 1e12

out(**{k: x for k, x in v.items() if x is not None})      # 厂商未公布的项不交给正文（正文写“未公布”）
