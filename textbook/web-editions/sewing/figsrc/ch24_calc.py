# -*- coding: utf-8 -*-
"""第 24 章 算例：所有正文数字由此脚本算出（示意值）。运行：python3 figsrc/ch24_calc.py"""
import math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ch24_model import *

print("== 24.1 机针消耗量（示意）")
machines, per_day, days = 300, 0.5, 300
print("年耗针", machines * per_day * days)

print("== 24.2 针号与刚度：EI ∝ d^4，欧拉临界力 ∝ d^4/L^2")
for nm in (60, 70, 80, 90, 100, 110, 130):
    d = nm / 100
    print(nm, "d=%.2f" % d, "相对 Nm90 刚度 %.2f" % ((d / 0.9) ** 4))
print("Nm110/Nm70 = %.2f" % ((1.1 / 0.7) ** 4))
# 针身做成从针柄 1.62 mm 减到 0.90 mm 的截面积压缩比
print("截面积比 Nm90/1.62: %.3f  减面率 %.1f%%" % ((0.9 / 1.62) ** 2, (1 - (0.9 / 1.62) ** 2) * 100))

print("== 24.5 梭尖线速度与梭道滑动速度")
Rh, Rr = 13.5e-3, 12.0e-3
for n in (3000, 4000, 5000, 5500):
    nh = 2 * n
    vh = 2 * math.pi * Rh * nh / 60
    vr = 2 * math.pi * Rr * nh / 60
    print(n, "旋梭 %d r/min" % nh, "梭尖 %.1f m/s" % vh, "梭道 %.1f m/s" % vr,
          "每秒掠过 %.0f 次" % (nh / 60), "每小时梭道滑过 %.0f km" % (vr * 3.6))
# 8 h 一班，梭道滑动距离
print("5000 r/min 8 h 滑动 km: %.0f" % (2 * math.pi * Rr * 10000 / 60 * 8 * 3600 / 1000))
# 钩线经过 0.04–0.1 mm 间隙的时间：梭尖走过机针直径 0.9 mm 的时间
print("梭尖掠过 0.9 mm 针身用时 μs: %.0f" % (0.9e-3 / (2 * math.pi * Rh * 10000 / 60) * 1e6))

print("== 24.4 针孔宽度 Cpk 与控制图")
S = spc(**STD2)
print("Xbarbar %.4f Rbar %.4f sig_hat %.4f Cp %.2f Cpk %.2f; true Cpk %.2f ppm %.1f" %
      (S['xbb'], S['rb'], S['sig_hat'], S['cp'], S['cpk'], S['cpk_true'], S['ppm']))
print("UCL %.4f LCL %.4f UCLR %.4f" % (S['ucl'], S['lcl'], S['uclr']))
for d in (0.5, 1.0, 1.5):
    for n in (2, 3, 4, 5, 6, 8):
        print("ARL1 drift %.1fσ n=%d: %.1f" % (d, n, arl(d, n)))
print("ARL0 n=5: %.0f" % arl(0, 5))
for d in (1.0,):
    for n in (3, 5):
        R = spc(mu=0.362, sig=0.004, n=n, drift=d, seed=7)
        print("drift", d, "n", n, "alarm group", R['alarm'], "ARL", round(R['arl1'], 1), "Cpk est %.2f" % R['cpk'])
# 漂移 1σ 后真 Cpk
print("漂移 1σ 后 Cpk %.2f ppm %.0f" % (min(USL - 0.366, 0.366 - LSL) / 0.012,
                                    (1 - Phi((USL - 0.366) / 0.004) + Phi((LSL - 0.366) / 0.004)) * 1e6))
# 只看极差判断的直度：单侧
print("直度单侧 Cpk 例: USL 0.03, mean 0.012, s 0.004 => %.2f" % ((0.03 - 0.012) / (3 * 0.004)))

print("== 24.7 选配")
cases = [("互换 k=1 σ5", dict(STD)),
         ("互换 k=1 σ2.75", dict(STD, sD=2.75, sd=2.75)),
         ("k=2", dict(STD, k=2)), ("k=3", dict(STD, k=3)), ("k=4", dict(STD, k=4)), ("k=5", dict(STD, k=5)),
         ("k=3 sm=0", dict(STD, k=3, sm=0.0)), ("k=3 sm=2", dict(STD, k=3, sm=2.0)),
         ("k=3 muD+4", dict(STD, k=3, muD=4.0)), ("k=3 muD+4 mud+4", dict(STD, k=3, muD=4.0, mud=4.0)),
         ("k=3 sD 6 sd 4", dict(STD, k=3, sD=6.0, sd=4.0)),
         ("k=1 muD+4", dict(STD, muD=4.0))]
for name, p in cases:
    R = simulate(**p)
    print("%-18s sets %4d good %4d pass %.2f%% left %d (%.1f%%) scrap %d cost %.2f mean %.2f sd %.2f per %s" % (
        name, R['sets'], R['good'], R['pass_rate'] * 100, R['left'], R['left_rate'] * 100, R['scrap'], R['cost'],
        R['mean'], R['sd'], R['per']))
# 理论：互换时间隙 σ 与合格率
sc = math.hypot(5, 5)
print("理论互换 σc %.2f 合格率 %.1f%%" % (sc, (2 * Phi(10 / sc) - 1) * 100))
print("要 99%%：σc ≤ %.2f, 每件 σ ≤ %.2f" % (10 / 2.576, 10 / 2.576 / math.sqrt(2)))
for k in (1, 2, 3, 4, 5):
    print("k=%d 组宽 %.1f μm，组内间隙最大偏离 ±%.1f μm" % (k, 30 / k, 30 / k))
