"""Motion laws on a normalised segment (第 39 轮 · 问渠凸轮).

Each law maps u in [0, 1] (fraction of the segment's cam angle) to the normalised follower displacement
f(u) in [0, 1] and its derivatives f', f'', f''' with respect to u. A rise of height h over cam angle beta then has
    s = h f(u),  ds/dθ = h f'/β,  d²s/dθ² = h f''/β²,  d³s/dθ³ = h f'''/β³.
The peak |f'|, |f''|, |f'''| are the dimensionless velocity, acceleration and jerk coefficients Cv, Ca, Cj.

Closed forms where they exist; the modified trapezoid and modified sine are defined by their acceleration shape and
integrated once on a fine grid (exact to ~1e-12 at the grid, Hermite-interpolated between). Plain code: no AI, no
network.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

import numpy as np

TWO_PI = 2 * pi


@dataclass(frozen=True)
class Law:
    key: str
    zh: str
    en: str
    # discontinuities at the ends of a rise from rest: "velocity" (rigid impact), "acceleration" (soft impact) or ""
    end_jump: str

    def eval(self, u):  # pragma: no cover - overridden
        raise NotImplementedError


def _u(u):
    return np.clip(np.asarray(u, dtype=float), 0.0, 1.0)


class Uniform(Law):
    def eval(self, u):
        u = _u(u)
        z = np.zeros_like(u)
        return u, np.ones_like(u), z, z


class Parabolic(Law):  # constant acceleration, then constant deceleration
    def eval(self, u):
        u = _u(u)
        lo = u <= 0.5
        f = np.where(lo, 2 * u**2, 1 - 2 * (1 - u) ** 2)
        v = np.where(lo, 4 * u, 4 * (1 - u))
        a = np.where(lo, 4.0, -4.0)
        return f, v, a, np.zeros_like(u)


class Harmonic(Law):  # simple harmonic (cosine)
    def eval(self, u):
        u = _u(u)
        return (
            (1 - np.cos(pi * u)) / 2,
            pi / 2 * np.sin(pi * u),
            pi**2 / 2 * np.cos(pi * u),
            -(pi**3) / 2 * np.sin(pi * u),
        )


class Cycloidal(Law):
    def eval(self, u):
        u = _u(u)
        return (
            u - np.sin(TWO_PI * u) / TWO_PI,
            1 - np.cos(TWO_PI * u),
            TWO_PI * np.sin(TWO_PI * u),
            TWO_PI**2 * np.cos(TWO_PI * u),
        )


class Poly345(Law):
    def eval(self, u):
        u = _u(u)
        return (
            10 * u**3 - 15 * u**4 + 6 * u**5,
            30 * u**2 - 60 * u**3 + 30 * u**4,
            60 * u - 180 * u**2 + 120 * u**3,
            60 - 360 * u + 360 * u**2,
        )


class Poly4567(Law):
    def eval(self, u):
        u = _u(u)
        return (
            35 * u**4 - 84 * u**5 + 70 * u**6 - 20 * u**7,
            140 * u**3 - 420 * u**4 + 420 * u**5 - 140 * u**6,
            420 * u**2 - 1680 * u**3 + 2100 * u**4 - 840 * u**5,
            840 * u - 5040 * u**2 + 8400 * u**3 - 4200 * u**4,
        )


class ShapedAccel(Law):
    """A law given by the shape of its acceleration; scaled so that f(1) = 1."""

    N = 20000

    def shape(self, u):  # pragma: no cover - overridden
        raise NotImplementedError

    def _table(self):
        if not hasattr(self, "_t"):
            u = np.linspace(0, 1, self.N + 1)
            g, dg = self.shape(u)
            h = u[1] - u[0]
            # velocity and displacement by integrating the acceleration (trapezoid with end correction = exact for
            # the smooth pieces to O(h^4) via Simpson on half steps)
            v = np.concatenate([[0], np.cumsum((g[1:] + g[:-1]) / 2 * h - (dg[1:] - dg[:-1]) * h**2 / 12)])
            f = np.concatenate([[0], np.cumsum((v[1:] + v[:-1]) / 2 * h - (g[1:] - g[:-1]) * h**2 / 12)])
            c = 1 / f[-1]
            object.__setattr__(self, "_t", (u, f * c, v * c, c))
        return self._t

    def eval(self, u):
        u = _u(u)
        uu, f, v, c = self._table()
        g, dg = self.shape(u)
        a, j = g * c, dg * c
        # cubic Hermite on f with slope v, and on v with slope a, between grid points
        h = uu[1] - uu[0]
        k = np.minimum((u / h).astype(int), len(uu) - 2)
        t = (u - uu[k]) / h
        ga, _ = self.shape(uu[k])
        gb, _ = self.shape(uu[k + 1])
        h00, h10, h01, h11 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t, -2 * t**3 + 3 * t**2, t**3 - t**2
        fi = h00 * f[k] + h10 * h * v[k] + h01 * f[k + 1] + h11 * h * v[k + 1]
        vi = h00 * v[k] + h10 * h * ga * c + h01 * v[k + 1] + h11 * h * gb * c
        return fi, vi, a, j


class ModifiedTrapezoid(ShapedAccel):
    def shape(self, u):
        u = np.asarray(u, dtype=float)
        w = 4 * pi
        g = np.select(
            [u <= 1 / 8, u <= 3 / 8, u <= 5 / 8, u <= 7 / 8],
            [np.sin(w * u), 1.0, np.cos(w * (u - 3 / 8)), -1.0],
            -np.sin(w * (1 - u)),
        )
        dg = np.select(
            [u <= 1 / 8, u <= 3 / 8, u <= 5 / 8, u <= 7 / 8],
            [w * np.cos(w * u), 0.0, -w * np.sin(w * (u - 3 / 8)), 0.0],
            w * np.cos(w * (1 - u)),
        )
        return g, dg


class ModifiedSine(ShapedAccel):
    def shape(self, u):
        u = np.asarray(u, dtype=float)
        w, m = 4 * pi, 4 * pi / 3
        g = np.select([u <= 1 / 8, u <= 7 / 8], [np.sin(w * u), np.sin(m * (u + 1 / 4))], -np.sin(w * (1 - u)))
        dg = np.select(
            [u <= 1 / 8, u <= 7 / 8], [w * np.cos(w * u), m * np.cos(m * (u + 1 / 4))], w * np.cos(w * (1 - u))
        )
        return g, dg


LAWS: dict[str, Law] = {
    law.key: law
    for law in (
        Uniform("uniform", "等速", "Constant velocity", "velocity"),
        Parabolic("parabolic", "等加速等减速", "Constant acceleration", "acceleration"),
        Harmonic("harmonic", "简谐（余弦加速度）", "Simple harmonic", "acceleration"),
        Cycloidal("cycloidal", "摆线（正弦加速度）", "Cycloidal", ""),
        ModifiedTrapezoid("mod_trapezoid", "修正梯形", "Modified trapezoid", ""),
        ModifiedSine("mod_sine", "修正正弦", "Modified sine", ""),
        Poly345("poly345", "3-4-5 次多项式", "3-4-5 polynomial", ""),
        Poly4567("poly4567", "4-5-6-7 次多项式", "4-5-6-7 polynomial", ""),
    )
}


def coefficients(key: str, n: int = 4001) -> dict[str, float]:
    """Cv, Ca, Cj of a law: the peaks of |f'|, |f''|, |f'''| over the segment."""
    _, v, a, j = LAWS[key].eval(np.linspace(0, 1, n))
    return {"Cv": float(np.max(np.abs(v))), "Ca": float(np.max(np.abs(a))), "Cj": float(np.max(np.abs(j)))}
