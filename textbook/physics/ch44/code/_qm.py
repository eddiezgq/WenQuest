"""第 44 章共用的一维薛定谔方程数值解法（与实验工具包 api.qm 同一算法，书中数字与网页实验一致）。

单位：长度 nm，能量 eV，时间 fs；质量为电子质量乘有效质量因子 mr。
levels()：有限差分把 −(ħ²/2m)ψ″ + Vψ = Eψ 化为三对角对称矩阵（两端 ψ = 0），求最低 n 个本征值与归一化本征函数。
cn_step()：克兰克–尼科尔森法推进一步，保持 ∫|ψ|² dx 不变。
"""
import numpy as np
from scipy.linalg import eigh_tridiagonal, solve_banded

from constants import e, hbar, m_e

C = hbar ** 2 / (2 * m_e) / e * 1e18          # ħ²/(2mₑ)，eV·nm²（约 0.0381）
HBAR_EVFS = hbar / e * 1e15                   # ħ，eV·fs（约 0.658）


def levels(V, dx, n=5, mr=1.0):
    """V：格点上的势能（eV），格点间距 dx（nm）。返回 (E, psi)，psi[k] 满足 Σ ψ² dx = 1，第一个明显的峰为正。"""
    c = C / mr
    d = 2 * c / dx ** 2 + np.asarray(V, float)
    off = np.full(len(d) - 1, -c / dx ** 2)
    E, vec = eigh_tridiagonal(d, off, select="i", select_range=(0, n - 1))
    psi = vec.T / np.sqrt(dx)
    for p in psi:
        first = np.argmax(np.abs(p) > 0.01 * np.abs(p).max())
        if p[first] < 0:
            p *= -1
    return E, psi


def packet(x, x0, sigma, k0):
    """归一化的高斯波包：中心 x0、宽度 sigma（nm）、平均波数 k0（1/nm）。"""
    return (2 * np.pi * sigma ** 2) ** -0.25 * np.exp(-((x - x0) / (2 * sigma)) ** 2 + 1j * k0 * x)


def cn_step(psi, V, dx, dt, mr=1.0):
    """(1 + iHdt/2ħ) ψ′ = (1 − iHdt/2ħ) ψ。"""
    c = C / mr
    r = dt / (2 * HBAR_EVFS)
    d = 2 * c / dx ** 2 + V
    off = -c / dx ** 2
    Hpsi = d * psi
    Hpsi[:-1] += off * psi[1:]
    Hpsi[1:] += off * psi[:-1]
    b = psi - 1j * r * Hpsi
    ab = np.zeros((3, len(psi)), complex)
    ab[0, 1:] = 1j * r * off
    ab[1] = 1 + 1j * r * d
    ab[2, :-1] = 1j * r * off
    return solve_banded((1, 1), ab, b)


def k_of(E, mr=1.0):
    """自由粒子的波数 k = √(E/c)，1/nm。"""
    return np.sqrt(np.maximum(E, 0) / (C / mr))
