"""14.3 节：埃尔米特矩阵、酉矩阵与正规矩阵。
埃尔米特矩阵 H = [[2, 1 − i], [1 + i, 3]]：特征值 1、4 为实数，特征向量在埃尔米特内积下正交，H = U Λ Uᴴ。
舒尔分解：任何复方阵 A = U T Uᴴ，T 上三角；A = [[4, −5], [2, −3]] 的舒尔形；剪切矩阵的舒尔形 T 不是对角的（不正规）。
正规矩阵：旋转 R(60°) 正规，可酉对角化，特征向量 (1, ∓i)/√2；正规 ⇔ 舒尔形 T 是对角的。"""
import numpy as np
from scipy.linalg import schur

from _num import sci
from bookout import out, tex, vec

def cfmt(z, d=4):
    z = complex(z); re, im = round(z.real, 10) + 0.0, round(z.imag, 10) + 0.0
    fr = lambda x: (str(int(round(x))) if abs(x - round(x)) < 1e-9 else f"{x:.{d}f}")
    if abs(im) < 1e-12:
        return fr(re)
    s_im = "" if abs(abs(im) - 1) < 1e-12 else fr(abs(im))
    if abs(re) < 1e-12:
        return ("-" if im < 0 else "") + s_im + "\\mathrm i"
    return fr(re) + (" - " if im < 0 else " + ") + s_im + "\\mathrm i"

H = np.array([[2, 1 - 1j], [1 + 1j, 3]])
w, U = np.linalg.eigh(H)
out(Hlam=", ".join(f"{x:.0f}" for x in w), UhU=sci(float(np.abs(U.conj().T @ U - np.eye(2)).max()) + 1e-30, 0),
    u1u2=sci(float(abs(np.vdot(U[:, 0], U[:, 1]))) + 1e-30, 0), Hrec=sci(float(np.abs(U @ np.diag(w) @ U.conj().T - H).max()) + 1e-30, 0))
A = np.array([[4.0, -5], [2, -3]])
T, Z = schur(A, output="complex")
out(TA=r"\begin{pmatrix} " + " \\\\ ".join(" & ".join(cfmt(x, 3) for x in r) for r in T) + r" \end{pmatrix}",
    schurA=sci(float(np.abs(Z @ T @ Z.conj().T - A).max()) + 1e-30, 0))
S = np.array([[1.0, 1], [0, 1]])
TS, ZS = schur(S, output="complex")
out(TS12=float(abs(TS[0, 1])))
th = np.radians(60)
R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
wr, Vr = np.linalg.eig(R)
TR, ZR = schur(R, output="complex")
out(Rnormal=sci(float(np.abs(R @ R.T - R.T @ R).max()) + 1e-30, 0), Rlam=", ".join(cfmt(z, 3) for z in wr),
    Rvv=sci(float(abs(np.vdot(Vr[:, 0], Vr[:, 1]))) + 1e-30, 0), TR12=sci(float(abs(TR[0, 1])) + 1e-30, 0),
    Snormal=float(np.abs(S @ S.T - S.T @ S).max()))
# 实舒尔形：绕 (1, 2, 2)/3 转 40° 的旋转矩阵（正规的实矩阵）化为“一个 2×2 旋转块 + 1”
def rodrigues(k, th):
    k = np.asarray(k, float) / np.linalg.norm(k)
    Kx = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * Kx + (1 - np.cos(th)) * Kx @ Kx
R3 = rodrigues([1, 2, 2], np.radians(40))
T3, Z3 = schur(R3, output="real")
blk = [i for i in range(2) if abs(T3[i + 1, i]) > 1e-9][0]
ang = float(np.degrees(np.arctan2(abs(T3[blk + 1, blk]), T3[blk, blk])))
one = [i for i in range(3) if i not in (blk, blk + 1)][0]
out(T3=tex(T3, 4), T3ang=ang, T3off=sci(float(max(abs(T3[one, blk]), abs(T3[one, blk + 1]), abs(T3[blk, one]), abs(T3[blk + 1, one]))) + 1e-30, 0),
    axis3=vec(Z3[:, one] * np.sign(Z3[0, one]), 4), Zorth=sci(float(np.abs(Z3.T @ Z3 - np.eye(3)).max()) + 1e-30, 0))
