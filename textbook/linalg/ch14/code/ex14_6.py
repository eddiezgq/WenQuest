"""14.6 节：刚体惯量张量的主轴；应力张量的主应力。
L 形手爪支架：主板 0.30 × 0.06 × 0.02 m、1.0 kg，中心在原点；指块 0.04 × 0.10 × 0.02 m、0.5 kg，中心在 (0.13, 0.08, 0)。
求质心、绕质心的惯量张量（长方体公式加平行轴定理），特征值是主惯量，特征向量是惯量主轴（在 xy 平面内倾斜）。
应力张量 σ = [[50, 30, 0], [30, −20, 0], [0, 0, 10]] MPa：特征值是主应力，最大剪应力 (σ₁ − σ₃)/2，冯·米塞斯等效应力。"""
import numpy as np

from _num import fix_sign, sci
from bookout import out, tex, vec

def box(m, a, b, c):
    return m / 12 * np.diag([b * b + c * c, a * a + c * c, a * a + b * b])

def shift(m, d):
    d = np.asarray(d, float)
    return m * (d @ d * np.eye(3) - np.outer(d, d))

parts = [(1.0, (0.30, 0.06, 0.02), np.zeros(3)), (0.5, (0.04, 0.10, 0.02), np.array([0.13, 0.08, 0.0]))]
M = sum(p[0] for p in parts)
c = sum(p[0] * p[2] for p in parts) / M
I = sum(box(m, *dim) + shift(m, r - c) for m, dim, r in parts)
w, V = np.linalg.eigh(I); V = fix_sign(V)
inplane = [i for i in range(3) if abs(V[2, i]) < 0.5]
tilt = float(np.degrees(np.arctan2(V[1, inplane[0]], V[0, inplane[0]])))
out(com=vec(c * 1000, 1), I=tex(I * 1e4, 2), Iw=vec(w * 1e4, 2), V=tex(V, 4), tilt=tilt, VtV=sci(float(np.abs(V.T @ V - np.eye(3)).max()) + 1e-30, 0),
    trI=float(np.trace(I) * 1e4), sumw=float(np.sum(w) * 1e4))
sig = np.array([[50.0, 30, 0], [30, -20, 0], [0, 0, 10]])
ws, Vs = np.linalg.eigh(sig); Vs = fix_sign(Vs)
s3, s2, s1 = ws
vm = np.sqrt(0.5 * ((s1 - s2) ** 2 + (s2 - s3) ** 2 + (s3 - s1) ** 2))
out(sig=tex(sig, 0), s1=float(s1), s2=float(s2), s3=float(s3), tau=float((s1 - s3) / 2), vm=float(vm),
    n1=vec(Vs[:, 2], 4), ang1=float(np.degrees(np.arctan2(Vs[1, 2], Vs[0, 2]))), I1=float(np.trace(sig)), I1chk=float(s1 + s2 + s3))
