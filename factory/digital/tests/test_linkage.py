# -*- coding: utf-8 -*-
"""平面连杆机构工具（cae/linkage.py，第 138 轮 G4.6）的检查：曲柄滑块、四连杆与解析解对比，导路组、速度差分。"""
import math

import numpy as np
import pytest

from cae import linkage as L


def test_slider_crank_matches_analytic():
    r, l, e = 15.5, 55.0, 3.0
    th = np.linspace(0, 2 * math.pi, 361)[:-1]
    xs, near = [], (r + l, e)
    for t in th:
        A = L.crank((0, 0), r, t)
        P, s = L.rrp(A, l, (0.0, e), (1.0, 0.0), near)
        near = P
        xs.append(P[0])
    assert np.max(np.abs(np.array(xs) - L.slider_crank_x(r, l, th, e))) < 1e-9


def test_fourbar_matches_freudenstein():
    a, b, c, d = 20.0, 60.0, 45.0, 55.0          # 曲柄摇杆（Grashof：最短 + 最长 ≤ 另两杆之和）
    O2, O4 = (0.0, 0.0), (d, 0.0)
    near = None
    for k in range(0, 360, 5):
        t = math.radians(k)
        A = L.crank(O2, a, t)
        ref = math.radians(80) if near is None else None
        guess = near or L.crank(O4, c, ref)
        B = L.rrr(A, b, O4, c, guess)
        near = B
        th4 = L.angle(O4, B)
        exp = L.fourbar_output(a, b, c, d, t)
        assert abs(math.remainder(th4 - exp, 2 * math.pi)) < 1e-9


def test_derivatives_of_sine():
    n = 720
    phi = np.linspace(0, 2 * math.pi, n, endpoint=False)
    y = 3.0 * np.sin(phi)
    v, a = L.derivatives(y, 2 * math.pi / n, omega=2.0)
    assert np.max(np.abs(v - 6.0 * np.cos(phi))) < 1e-3
    assert np.max(np.abs(a + 12.0 * np.sin(phi))) < 1e-3


def test_cannot_assemble_raises():
    with pytest.raises(ValueError):
        L.rrr((0, 0), 1.0, (10, 0), 1.0, (5, 0))
    with pytest.raises(ValueError):
        L.rrp((0, 0), 1.0, (0, 5), (1, 0), (0, 5))
