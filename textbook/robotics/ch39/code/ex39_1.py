"""算例 39.1.1、39.1.2：用 20 N 标准砝码对腕部力传感器做 10 次重复测量；A 类、B 类、合成与扩展不确定度。

读数由程序按“真值 20 N、系统偏差 +0.12 N、随机误差标准差 0.06 N、显示分辨率 0.01 N”生成（固定随机种子）。
"""
import math

import numpy as np

from bookout import out

rng = np.random.default_rng(391)
true, bias, sd, res = 20.0, 0.12, 0.06, 0.01
x = np.round(true + bias + rng.normal(0, sd, 10), 2)
n = len(x)
mean = float(x.mean())
s = float(x.std(ddof=1))                   # 实验标准差（贝塞尔公式）
uA = s / math.sqrt(n)                      # 平均值的标准不确定度（A 类）
uB_res = res / 2 / math.sqrt(3)            # 分辨率：半宽 0.005 N 的均匀分布
cal_U, cal_k = 0.10, 2                     # 校准证书：砝码与读数系统合在一起 U = 0.10 N（k = 2）
uB_cal = cal_U / cal_k
uc = math.sqrt(uA ** 2 + uB_res ** 2 + uB_cal ** 2)
U = 2 * uc
err = mean - true                          # 与砝码标称值之差：主要是系统误差

# 核对：贝塞尔公式与逐项计算一致
assert abs(s - math.sqrt(((x - mean) ** 2).sum() / (n - 1))) < 1e-12
# 系统误差 0.12 N 远大于平均值的随机不确定度，说明需要修正零点/灵敏度
assert err > 3 * uA
assert err > U and mean - U > true           # 正文：差别超过 U；未修正的区间不含 20 N

table = r"\begin{array}{" + "c" * n + "}" + " & ".join(f"{v:.2f}" for v in x) + r"\end{array}"
out(table=table, n=n, mean=mean, s=s, uA=uA, uB_res=uB_res, uB_cal=uB_cal, uc=uc, U=U, err=err,
    lo=mean - U, hi=mean + U, x_min=float(x.min()), x_max=float(x.max()), _x=x.tolist())
