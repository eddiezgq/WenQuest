"""12.3 节：正交分解定理与最佳逼近。
函数：[0, 1] 上用 a + bx 最佳逼近 √x，格拉姆矩阵方程给出 a = 4/15、b = 4/5，误差平方 1/450；贝塞尔不等式。
机器人：平面三连杆冗余臂，末端速度 v 给定。欧氏最小范数解 J⁺v 与“最小动能”解 J⁺_M v = M⁻¹Jᵀ(JM⁻¹Jᵀ)⁻¹v 的比较；
I − J⁺_M J 是 M-内积下到零空间 N(J) 的正交投影（M-自伴、幂等），把任意关节速度分成 M-正交的两部分，动能可以相加；
欧氏投影 I − J⁺J 分出的两部分动能有交叉项。"""
import numpy as np

from _arm3 import jac, mass
from _frac import fr
from _elim import tex_frac
from _num import sci
from bookout import out, tex, vec

# 函数的最佳逼近
x = np.linspace(0, 1, 400001)
ip = lambda f, g: float(np.trapezoid(f * g, x))
f = np.sqrt(x)
B = [np.ones_like(x), x]
G = np.array([[ip(a, b) for b in B] for a in B])
r = np.array([ip(a, f) for a in B])
c = np.linalg.solve(G, r)
p = c[0] + c[1] * x
err2 = ip(f - p, f - p)
out(a=tex_frac(fr(c[0])), b=tex_frac(fr(c[1])), err2=tex_frac(fr(err2, 2000)),
    maxerr=float(np.abs(f - p).max()))
# 冗余臂
q = np.radians([30.0, 60.0, -45.0])
J, M = jac(q), mass(q)
v = np.array([0.0, 0.2])                     # 末端以 0.2 m/s 竖直向上
Jp = np.linalg.pinv(J)
Mi = np.linalg.inv(M)
JpM = Mi @ J.T @ np.linalg.inv(J @ Mi @ J.T)
qe, qm = Jp @ v, JpM @ v
ke = lambda w: 0.5 * float(w @ M @ w)
out(J=tex(J, 4), v=vec(v, 1), qe=vec(qe, 3), qm=vec(qm, 3), ne=float(np.linalg.norm(qe)), nm=float(np.linalg.norm(qm)),
    ke_e=ke(qe), ke_m=ke(qm), save_pct=float(100 * (1 - ke(qm) / ke(qe))), chk=sci(float(np.abs(J @ qm - v).max()) + 1e-30, 0))
# 投影
PN = np.eye(3) - JpM @ J
PE = np.eye(3) - Jp @ J
out(PN_idem=sci(float(np.abs(PN @ PN - PN).max()) + 1e-30, 0), PN_Msym=sci(float(np.abs(M @ PN - (M @ PN).T).max()) + 1e-30, 0),
    PN_sym=float(np.abs(PN - PN.T).max()), JPN=sci(float(np.abs(J @ PN).max()) + 1e-30, 0))
# 把关节速度 w = (0, 0.5, −0.5) 分解
w = np.array([0.0, 0.5, -0.5])
for tag, P in (("M", PN), ("E", PE)):
    wn = P @ w
    wt = w - wn
    out(**{f"wn{tag}": vec(wn, 3), f"wt{tag}": vec(wt, 3), f"ke_w{tag}": ke(w), f"ke_n{tag}": ke(wn), f"ke_t{tag}": ke(wt),
           f"cross{tag}": (sci(abs(float(wt @ M @ wn)) + 1e-30, 0) if tag == "M" else float(wt @ M @ wn))})
out(w=vec(w, 1), ke_w=ke(w))
