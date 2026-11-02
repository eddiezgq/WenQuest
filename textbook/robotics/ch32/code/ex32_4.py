"""32.4 节的计算：行星减速器。

(1) 算例 32.4.1：太阳轮 20 齿、内齿圈 70 齿、行星轮 25 齿、3 个行星轮：装配条件 (z_s + z_r)/N 为整数；
    三种固定方式的传动比（威利斯公式 (n_s − n_c)/(n_r − n_c) = −z_r/z_s）。
(2) 零件库 PLE（Neugart 样本）：一级减速比 3–10；一级的回程间隙上限，换到 WQ-CR5 的 J2（负载点离 J2 0.86 m）会让 TCP 走多远；
    放在 AGV 车轮（半径 0.1 m）上又是多少。
"""
import math

from _ch32 import ARCMIN, library
from bookout import out

z_s, z_r, N = 20, 70, 3
z_p = (z_r - z_s) // 2
assert (z_s + z_r) % N == 0 and z_s + 2 * z_p == z_r


def ratio(fixed):
    """输入 → 输出的传动比（输入转速 / 输出转速）。威利斯：(n_s − n_c) = −(z_r/z_s)(n_r − n_c)"""
    k = z_r / z_s
    if fixed == "ring":          # 太阳轮入、行星架出：n_r = 0 → n_s = (1 + k) n_c
        return 1 + k
    if fixed == "carrier":       # 太阳轮入、内齿圈出：n_c = 0 → n_s = −k n_r
        return -k
    return 1 + 1 / k              # 太阳轮固定：内齿圈入、行星架出：0 − n_c = −k (n_r − n_c) → n_r = (1 + 1/k) n_c


out(z_s=z_s, z_r=z_r, z_p=z_p, N=N, asm=(z_s + z_r) // N, i_ring=ratio("ring"), i_carrier=ratio("carrier"), i_sun=ratio("sun"))
ple = library("D-RDC-NEUGART-PLE")
ratios = sorted({int(r["ratio"]) for r in ple})
bl80 = float([r for r in ple if r["size_code"] == "PLE080"][0]["backlash_arcmin"])
eta = float(ple[0]["eta_pct"])
tcp = bl80 * ARCMIN * 0.86 * 1000
wheel = bl80 * ARCMIN * 0.10 * 1000
out(ratios_min=min(ratios), ratios_max=max(ratios), bl80=bl80, eta=eta, tcp_mm=tcp, wheel_mm=wheel, tcp_ratio=tcp / 0.03)
