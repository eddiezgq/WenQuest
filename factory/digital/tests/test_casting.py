# -*- coding: utf-8 -*-
"""铸件凝固仿真（cae/casting.py，第 138 轮 G5.1）的检查：平板凝固时间对 Chvorinov 解析解，模数平方律，体素化，孤立液相。"""
import math

import numpy as np

from cae import casting as C


def test_plate_matches_chvorinov():
    """半无限砂型的解析解：t = (π/4)·[ρ_m·H' / (T_m − T_0)]²·M² / (kρc)_砂，H' = 潜热 + 过热；T_m 取共晶温度"""
    m, s = C.MATERIALS["HT250"], C.MATERIALS["green_sand"]
    Hp = m["L"] + m["cp"] * (1380.0 - m["TE"])
    M = 0.01                                                 # 20 mm 平板，模数 1 cm
    t_ana = math.pi / 4 * (m["rho"] * Hp / (m["TE"] - 25.0)) ** 2 * M * M / (s["k"] * s["rho"] * s["cp"])
    ts, Mcm, B = C.plate_test(20.0, 2.0)
    assert Mcm == 1.0
    assert abs(ts / t_ana - 1) < 0.08, (ts, t_ana)


def test_modulus_square_law_and_grid():
    t20, _, B20 = C.plate_test(20.0, 2.0)
    t40, _, B40 = C.plate_test(40.0, 2.0)
    assert abs(t40 / t20 - 4.0) < 0.1                       # 厚一倍，凝固时间四倍
    t20f, _, _ = C.plate_test(20.0, 1.0)
    assert abs(t20f / t20 - 1) < 0.02                        # 网格加密结果不变


def test_voxelize_cube():
    v = np.array([[0, 0, 0], [10, 0, 0], [10, 10, 0], [0, 10, 0], [0, 0, 10], [10, 0, 10], [10, 10, 10], [0, 10, 10]], float)
    f = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    tris = v[np.array(f)]
    vox = C.voxelize(tris, (-2.0, -2.0, -2.0), 1.0, (14, 14, 14))
    assert vox.sum() == 1000


def test_isolated_pocket_found():
    """两块厚板用一根细杆连起来，冒口在左块：细杆先凝固，右块成了孤立液相区"""
    mat = np.full((60, 16, 16), C.SAND, np.int8)
    mat[6:22, 3:13, 3:13] = C.METAL                          # 左块（冒口）
    mat[22:38, 7:9, 7:9] = C.METAL                           # 细杆
    mat[38:50, 4:12, 4:12] = C.METAL                         # 右块
    feeder = np.zeros(mat.shape, bool)
    feeder[6:22, 3:13, 3:13] = True
    r = C.solidify(C.Mold(mat=mat, dx=0.004, feeder=feeder), snap_every=2.0)
    assert r["pockets"], "右块应当被识别为孤立液相区"
    p = r["pockets"][0]
    assert 38 <= p["center"][0] < 50
