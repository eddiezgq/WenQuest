"""19.4 节：降维与可视化。机器人手 15 个关节的 120 个抓取姿态：前两个主成分（“协同”）解释的方差、
用两个得分重建姿态的误差、主成分子空间与真实协同子空间的主角；六项检测数据怎样选主成分个数；
第 2 章八份检测记录在主成分平面上的位置；白化；方差大不等于有用：两类零件的分界在小方差方向上。"""
import math
import numpy as np

from _hand import NOISE_DEG, SYN, postures
from _num import fix_sign
from _qc import N_I, RECORDS2, X_I
from bookout import out, tex, vec

# (1) 机器人手的抓取姿态
H = postures()
n = H.shape[0]
mh = H.mean(axis=0)
Hc = H - mh
_, sh, Vth = np.linalg.svd(Hc, full_matrices=False)
lam_h = sh ** 2 / (n - 1)
rat_h = lam_h / lam_h.sum()
out(nh=n, rh1=float(100 * rat_h[0]), rh2=float(100 * rat_h[:2].sum()), rh3=float(100 * rat_h[:3].sum()),
    lam_h=vec(lam_h[:5], 0), sd_total=float(math.sqrt(lam_h.sum())))
for k in (1, 2, 3):
    E = Hc - Hc @ Vth[:k].T @ Vth[:k]
    out(**{f"rms{k}": float(np.sqrt(np.mean(E ** 2)))})
out(noise_deg=NOISE_DEG)
# 主成分子空间（前 3 个）与真实协同子空间之间的主角：两组标准正交基的 Qᵀ W 的奇异值是各主角的余弦
Qs, _ = np.linalg.qr(SYN)
cosang = np.linalg.svd(Vth[:3] @ Qs, compute_uv=False)
out(pang=vec(np.degrees(np.arccos(np.clip(cosang, -1, 1))), 1), pang_max=float(np.degrees(np.arccos(min(cosang.min(), 1.0)))))
# (2) 六项检测：选几个主成分
Xc = X_I - X_I.mean(axis=0)
s = Xc.std(axis=0, ddof=1)
Z = Xc / s
w, V = np.linalg.eigh(Z.T @ Z / (N_I - 1))
w, V = w[::-1], fix_sign(V[:, ::-1])
cum = np.cumsum(w) / w.sum()
out(k_kaiser=int(np.sum(w > 1)), k85=int(np.argmax(cum >= 0.85) + 1), k90=int(np.argmax(cum >= 0.90) + 1))

# (3) 第 2 章的八份检测记录：用这 200 件的均值和标准差标准化，投影到前两个主成分
Zr = (RECORDS2 - X_I.mean(axis=0)) / s
Tr = Zr @ V[:, :2]
frac = np.sum(Tr ** 2, axis=1) / np.sum(Zr ** 2, axis=1)
out(Tr=tex(Tr, 2), frac=vec(100 * frac, 0), frac2=float(100 * frac[1]), frac4=float(100 * frac[3]))

# (4) 白化：得分除以 √λ 后协方差为 I；白化后的长度平方就是马哈拉诺比斯距离的平方
Tw = Z @ V / np.sqrt(w)
assert np.allclose(Tw.T @ Tw / (N_I - 1), np.eye(6))
Rinv = np.linalg.inv(Z.T @ Z / (N_I - 1))
assert np.allclose(np.sum(Tw ** 2, axis=1), np.einsum("ij,jk,ik->i", Z, Rinv, Z))

# (5) 方差大不等于有用：两类零件，沿 x 方向散得很开，两类的差别在 y 方向上
rng = np.random.default_rng(42)
m_each = 150
A = np.c_[rng.normal(0, 1.5, m_each), rng.normal(-0.5, 0.25, m_each)]
B = np.c_[rng.normal(0, 1.5, m_each), rng.normal(0.5, 0.25, m_each)]
P = np.r_[A, B]
lab = np.r_[np.zeros(m_each), np.ones(m_each)]
Pc = P - P.mean(axis=0)
_, sp, Vtp = np.linalg.svd(Pc, full_matrices=False)


def acc(t):
    """沿一个方向投影后，用中点分界的正确率（取两种符号中较好的一个）。"""
    thr = 0.5 * (t[lab == 0].mean() + t[lab == 1].mean())
    a = np.mean((t > thr) == (lab == 1))
    return max(a, 1 - a)


out(sep_r1=float(100 * sp[0] ** 2 / np.sum(sp ** 2)), acc1=float(100 * acc(Pc @ Vtp[0])), acc2=float(100 * acc(Pc @ Vtp[1])))
