"""8.1 节与算例 8.1.1：浮点格式。
（1）各种格式的位数、最大值、最小规格化数、最小次正规数、相对精度（1 与下一个数之差）；
    舍入函数 _ch8.round_to 对半精度与 NumPy 的 float16 逐位核对（20 万个跨越 15 个数量级的随机数，加上溢出边界上的几个数）。
（2）0.1 在各种格式里存成多少，相对误差多大。
（3）“大数吃小数”：在 FP16、BF16 中把 0.0001 连加 10 000 次（每次加完都舍入到该格式），结果是多少；按 FP32 累加又如何。
    张量核心的矩阵乘法用 FP32 累加，就是为了避免这个问题。"""
import numpy as np

from _ch8 import FMTS, round_to
from bookout import out

rng = np.random.default_rng(8)
x = np.concatenate([rng.standard_normal(200000) * 10.0 ** rng.integers(-9, 6, 200000), [65504, 65519.9, 65520, 6e-8, 3e-8, 2.98e-8]])
with np.errstate(over="ignore"):
    ok16 = bool(np.array_equal(round_to(x, FMTS["FP16"]), x.astype(np.float16).astype(np.float64)))

v = {}
for k, f in FMTS.items():
    key = k.replace("FP8 ", "").replace("FP4 ", "").replace(" ", "")
    r = float(round_to(0.1, f))
    v[key + "_max"] = f.max
    v[key + "_minn"] = f.min_normal
    v[key + "_mins"] = f.min_sub
    v[key + "_eps"] = f.eps
    v[key + "_minn_e"] = 1 - f.bias                      # 最小规格化数 = 2^(1 − bias)
    v[key + "_mins_e"] = 1 - f.bias - f.m                # 最小次正规数 = 2^(1 − bias − m)
    v[key + "_eps_e"] = -f.m                             # 相对精度 = 2^(−m)
    v[key + "_bias"] = f.bias
    v[key + "_digits"] = f.m * np.log10(2)               # 尾数相当于几位十进制有效数字
    v[key + "_01"] = r
    v[key + "_01err"] = abs(r - 0.1) / 0.1 * 100


def accumulate(f, n=10000, d=1e-4):
    """连加 n 次，每次舍入；返回 (和, 从第几次加法起和不再变化)。"""
    s, stall = 0.0, None
    for i in range(1, n + 1):
        t = float(round_to(s + d, f))
        if t == s and stall is None:
            stall = i
        s = t
    return s, stall


bits, r = [], 0.1 * 16                                     # 0.1 = 1.6 × 2⁻⁴：写出 1.6 的二进制展开
for _ in range(16):
    r = (r - int(r)) * 2
    bits.append(str(int(r)))
bin01 = "1." + " ".join("".join(bits[i:i + 4]) for i in range(0, 16, 4)) + "…₂"
assert ok16, "与 NumPy 的半精度不一致"
s16, stall16 = accumulate(FMTS["FP16"])
out(bin01=bin01, ok16=ok16, sum_fp16=s16, stall_fp16=stall16, lost_fp16=10000 - stall16 + 1, sum_bf16=accumulate(FMTS["BF16"])[0],
    sum_fp32=accumulate(FMTS["FP32"])[0], **v)
