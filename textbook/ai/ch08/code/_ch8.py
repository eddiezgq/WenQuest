"""第 8 章共用（以下划线开头，构建时不单独运行）：A10 的规格；各种浮点格式的参数，以及把实数舍入到某种格式的函数。

一种二进制浮点格式由指数位数 e、尾数位数 m 决定：规格化数为 (−1)^s · 1.f · 2^(E − bias)，bias = 2^(e−1) − 1；
指数全 0 表示零与次正规数 (−1)^s · 0.f · 2^(1 − bias)。IEEE 754 的格式（FP32、FP16、BF16、TF32）把指数全 1 留给无穷与 NaN；
FP8 的 E4M3（OCP 规范中的 E4M3FN）不要无穷，只把指数与尾数全 1 留给 NaN，最大值因此是 448；E5M2 按 IEEE 的规矩；
FP4 的 E2M1 没有无穷与 NaN，全部 16 个编码都是数。舍入一律“就近，平分时取偶”（round to nearest, ties to even）；超出最大值时，
IEEE 格式溢出为无穷，E4M3 与 E2M1 按“饱和”处理（取最大值，训练与推理的库通常这样做）。"""
from dataclasses import dataclass

import numpy as np

from gpus import GPUS

A10 = dict(GPUS["a10"])
A10["tf32t"] = 62.5e12
A10["int8t"] = 250e12            # 数据手册：INT8 张量核心（稠密）


@dataclass(frozen=True)
class Fmt:
    name: str
    e: int                       # 指数位数
    m: int                       # 尾数位数（不含隐含的 1）
    ieee: bool = True            # 指数全 1 是否留给无穷与 NaN
    nan_top: bool = False        # 只把“指数与尾数全 1”留给 NaN（E4M3）

    @property
    def bias(self):
        return 2 ** (self.e - 1) - 1

    @property
    def emax(self):
        top = 2 ** self.e - 1
        return (top - 1 if self.ieee else top) - self.bias

    @property
    def max(self):
        mant = 2 - 2.0 ** -self.m
        if self.nan_top:          # 尾数全 1 留给 NaN：最大的尾数少一个单位
            mant -= 2.0 ** -self.m
        return mant * 2.0 ** self.emax

    @property
    def min_normal(self):
        return 2.0 ** (1 - self.bias)

    @property
    def min_sub(self):
        return 2.0 ** (1 - self.bias - self.m)

    @property
    def eps(self):               # 1 与下一个可表示数之差
        return 2.0 ** -self.m

    @property
    def bits(self):
        return 1 + self.e + self.m


FMTS = {
    "FP32": Fmt("FP32", 8, 23),
    "TF32": Fmt("TF32", 8, 10),
    "BF16": Fmt("BF16", 8, 7),
    "FP16": Fmt("FP16", 5, 10),
    "FP8 E5M2": Fmt("FP8 E5M2", 5, 2),
    "FP8 E4M3": Fmt("FP8 E4M3", 4, 3, ieee=False, nan_top=True),
    "FP4 E2M1": Fmt("FP4 E2M1", 2, 1, ieee=False),
}


def round_to(x, f: Fmt, saturate=None):
    """把 x（标量或数组，按双精度计算）舍入到格式 f，返回舍入后的值（仍用双精度存放）。就近舍入、平分取偶；
    指数小于最小规格化指数时按次正规数的固定间隔舍入。saturate 默认：IEEE 格式溢出为无穷，其余饱和到最大值。"""
    x = np.asarray(x, dtype=np.float64)
    sat = (not f.ieee) if saturate is None else saturate
    a = np.abs(x)
    with np.errstate(divide="ignore"):
        ex = np.floor(np.log2(np.where(a > 0, a, 1.0)))
    ex = np.maximum(ex, 1 - f.bias)                      # 次正规区间用最小规格化指数的间隔
    q = 2.0 ** (ex - f.m)                                # 这一段里相邻两个可表示数的间隔
    r = np.round(a / q) * q                              # np.round：平分时取偶
    over = r > f.max
    r = np.where(over, f.max if sat else np.inf, r)
    return np.where(np.isnan(x), np.nan, np.sign(x) * r)
