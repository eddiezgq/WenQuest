"""算例 M4.4.1—M4.4.3：浮点数、舍入与误差的累积（M4.4 节）。

浮点数不是实数：它只有有限位有效数字，而且相邻两个可表示的数之间有间隔。
由此有三件事要知道：（1）0.1 存不进去；（2）加法不满足结合律，求和的次序会改变结果；
（3）误差怎样随运算次数累积——随机误差按 √n，最坏情况按 n，这决定了大规模求和该怎么写。
各格式的位数与范围见表 8.1.1，本程序只用 NumPy 自带的三种。
"""
import numpy as np

from _chM4 import bits_of, spec
from bookout import out

v = {}
# ---------- （1）有效数字与 0.1
for k in ("fp64", "fp32", "fp16"):
    s = spec(k)
    v[f"{k}_bits"], v[f"{k}_eps"], v[f"{k}_digits"] = s["bits"], s["eps"], s["digits"]
    v[f"{k}_max"], v[f"{k}_min"] = s["max"], s["min_normal"]
sign, exp, frac = bits_of(0.1)
v["exp01"], v["frac01"] = exp, frac
v["err01_64"] = abs(float(np.float64(0.1)) - 0.1)
v["err01_32"] = abs(float(np.float32(0.1)) - 0.1)
v["err01_16"] = abs(float(np.float16(0.1)) - 0.1)
v["err01_16_pct"] = v["err01_16"] / 0.1 * 100
v["sum01_10"] = float(sum([np.float64(0.1)] * 10))          # 0.1 加十次不等于 1
v["eq_one"] = v["sum01_10"] == 1.0
assert not v["eq_one"], "0.1 加十次不等于 1——这是浮点最有名的那个例子"

# ---------- （2）加法不满足结合律
a, b, c = np.float32(1e8), np.float32(-1e8), np.float32(1.0)
v["left"] = float((a + b) + c)
v["right"] = float(a + (b + c))
assert v["left"] != v["right"], "结合律在浮点上不成立"
# 大数吃小数：1e8 + 1 在单精度下还是 1e8
v["swallow"] = float(np.float32(1e8) + np.float32(1.0)) == 1e8

# ---------- （3）求和的误差怎样累积：三种写法
g = np.random.default_rng(44)
N = 200_000
x = g.uniform(0.5, 1.5, N).astype(np.float32)
exact = float(np.sum(x.astype(np.float64)))                  # 双精度当作"真值"
seq = float(np.cumsum(x)[-1])                                # 顺序求和（cumsum 就是一个一个加）
pair = float(np.sum(x))                                      # 成对求和（NumPy 的默认做法，误差按 √log n）
c = np.float32(0.0)
ks = np.float32(0.0)
for val in x:                                                # 补偿求和（卡亨算法）：把丢掉的低位记下来补回去
    y = val - c
    t = ks + y
    c = (t - ks) - y
    ks = t
v["N"] = N
v["err_seq"] = abs(seq - exact) / exact
v["err_pair"] = abs(pair - exact) / exact
v["err_kahan"] = abs(float(ks) - exact) / exact
v["ratio_seq_pair"] = v["err_seq"] / max(v["err_pair"], 1e-12)
v["ratio_seq_kahan"] = v["err_seq"] / max(v["err_kahan"], 1e-12)
assert v["err_seq"] > v["err_pair"] >= 0 and v["err_kahan"] <= v["err_pair"], "顺序最差、成对居中、补偿最好"
# 理论上界：最坏按 n，随机误差按 √n
v["eps32"] = float(np.finfo(np.float32).eps)
v["bound_worst"] = N * v["eps32"]
v["bound_random"] = float(np.sqrt(N)) * v["eps32"]
out(**v)
