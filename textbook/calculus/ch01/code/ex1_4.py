"""1.4 节：刘徽割圆术——从正六边形起逐次倍增边数，算内接正多边形的面积；祖冲之的密率与约率。"""
import math
from fractions import Fraction

from bookout import out

# 半径 1 的圆，内接正 n 边形边长 a_n；倍增公式 a_{2n} = sqrt(2 − sqrt(4 − a_n²))（刘徽的勾股算法）
# 正 2n 边形的面积 = n · a_n / 2（刘徽：S_{2n} = n · a_n · r / 2）
a, n = 1.0, 6
areas = {}
while n <= 3072:
    areas[2 * n] = n * a / 2
    a = math.sqrt(2 - math.sqrt(4 - a * a))
    n *= 2
out(S12=areas[12], S24=areas[24], S96=areas[96], S192=areas[192], S3072=areas[3072], S6144=areas[6144])
# 刘徽的不等式：S_{2n} < 圆面积 < S_{2n} + (S_{2n} − S_n)
lo, hi = areas[192], areas[192] + (areas[192] - areas[96])
out(liu_lo=lo, liu_hi=hi, pi=math.pi)
# 祖冲之：3.1415926 < π < 3.1415927；密率 355/113，约率 22/7
out(milv=355 / 113, yuelv=22 / 7, milv_err=abs(355 / 113 - math.pi), yuelv_err=abs(22 / 7 - math.pi))
# 祖暅原理：牟合方盖的体积与球体积之比为 4 : π（同高处截面：正方形 4r² 与内切圆 πr² 之比）
out(mouhe_ratio=4 / math.pi)
# 史料中的数（作为字符串交给正文），并核对它们与 π 的关系
zu_lo, zu_hi, liu = "3.1415926", "3.1415927", "3.1416"
assert float(zu_lo) < math.pi < float(zu_hi) and abs(float(liu) - math.pi) < 1e-4
out(zu_lo=zu_lo, zu_hi=zu_hi, liu3072=liu)
# 刘徽原书的数：圆面积介于 314 64/625 与 314 169/625 平方寸之间（半径 10 寸），换成半径 1
olo, ohi = (314 + Fraction(64, 625)) / 100, (314 + Fraction(169, 625)) / 100
assert abs(float(olo) - lo) < 2e-5 and abs(float(ohi) - hi) < 2e-5
out(liu_orig_lo=f"{float(olo):.6f}", liu_orig_hi=f"{float(ohi):.6f}")
