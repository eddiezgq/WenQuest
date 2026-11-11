# -*- coding: utf-8 -*-
"""齿轮几何与强度（cae/gears.py，第 138 轮 G4.5）的检查：几个公认的系数值，和直齿节点处的赫兹公式对一遍。"""
import math

from cae import gears as G


def test_known_factors():
    assert abs(G.z_e() - 189.8) < 0.3                      # 钢对钢 ZE = 189.8 √MPa
    assert abs(G.z_h(0.0) - 2.495) < 0.003                 # 标准直齿 α 20° 的 ZH
    assert G.y_fa_sa(20) == (2.80, 1.55)
    fa, sa = G.y_fa_sa(37.5)
    assert 2.40 < fa < 2.45 and 1.65 < sa < 1.67


def test_geometry_spur_and_helical():
    g = G.geometry(2.0, 20, 40, 0.0, b=20)
    assert abs(g["a"] - 60.0) < 1e-9 and abs(g["d1"] - 40.0) < 1e-9
    assert 1.6 < g["eps_a"] < 1.75                          # 20/40 标准齿的端面重合度约 1.68
    h = G.geometry(1.0, 20, 40, 15.0, b=8)
    assert abs(h["a"] - 30 / math.cos(math.radians(15))) < 1e-9
    assert abs(h["eps_b"] - 8 * math.sin(math.radians(15)) / math.pi) < 1e-9


def test_contact_matches_hertz_at_pitch_point():
    """直齿、Zε = 1 时，σH 公式就是两圆柱在节点的赫兹线接触应力"""
    g = G.geometry(3.0, 25, 75, 0.0, b=30)
    T1 = 200.0
    r = G.check(T1, 1000, g, "45-QT", KA=1, Kv=1, Ka=1, Kb=1)
    a = math.radians(20)
    rho1, rho2 = g["d1"] / 2 * math.sin(a), g["d2"] / 2 * math.sin(a)
    Fn = 2 * T1 * 1000 / g["d1"] / math.cos(a)
    Es = 1 / ((1 - 0.09) / 206e3 * 2)
    sH_hertz = math.sqrt(Fn / g["b"] * Es / math.pi * (1 / rho1 + 1 / rho2))
    assert abs(r["sigma_H"] / r["Zeps"] - sH_hertz) / sH_hertz < 1e-6


def test_trends_and_life():
    g1 = G.geometry(1.0, 20, 40, 15.0, b=8)
    g2 = G.geometry(1.5, 20, 40, 15.0, b=8)
    r1, r2 = (G.check(1.0, 10000, g, "20CrMnTi-carburized") for g in (g1, g2))
    assert r2["sigma_F1"] < r1["sigma_F1"] and r2["sigma_H"] < r1["sigma_H"]
    assert G.life_factor(1e6, 5e7) == 1.0 and abs(G.life_factor(1e10, 5e7) - 0.85) < 1e-9
