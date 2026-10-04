"""3.7 节：应用——AGV 电机驱动电路的节点电压；三角形桁架的内力；丙烷燃烧的化学方程式配平；
车间 AGV 路网的流量；数字工厂三个车间的投入产出模型。"""
import numpy as np

from bookout import out, tex, vec
from _elim import fstr, rref

# 1. AGV 电机驱动电路（直流稳态）。电池 E = 24 V、内阻 rb = 0.2 Ω → 母线（节点 1），控制板负载 48 Ω 接地；
#    H 桥上管导通电阻 0.05 Ω → 电机正端（节点 2）；电枢电阻 1.2 Ω 与反电动势 Em 串联 → 电机负端（节点 3）；
#    H 桥下管 0.05 Ω → 节点 4；电流采样电阻 0.1 Ω 接地。
E, rb, RL, Rh, Ra, Rs = 24.0, 0.2, 48.0, 0.05, 1.2, 0.1


def circuit(Em):
    g = lambda r: 1.0 / r
    G = np.array([[g(rb) + g(RL) + g(Rh), -g(Rh), 0, 0],
                  [-g(Rh), g(Rh) + g(Ra), -g(Ra), 0],
                  [0, -g(Ra), g(Ra) + g(Rh), -g(Rh)],
                  [0, 0, -g(Rh), g(Rh) + g(Rs)]])
    i = np.array([E * g(rb), Em * g(Ra), -Em * g(Ra), 0.0])
    return G, i, np.linalg.solve(G, i)


G, i, V = circuit(12.0)
Im = (V[1] - V[2] - 12.0) / Ra
out(G=tex(G, 2), i=vec(i, 1), V=vec(V, 3), Im=float(Im), Vs=float(V[3]), Isense=float(V[3] / Rs), Ib=float((E - V[0]) / rb), IL=float(V[0] / RL),
    kcl=float(abs((E - V[0]) / rb - V[0] / RL - (V[0] - V[1]) / Rh)))
_, _, V0 = circuit(0.0)
out(V0=vec(V0, 3), I0=float((V0[1] - V0[2]) / Ra))
# 2. 三角形桁架：A(0, 0) 固定铰支，B(2, 0) 滚动支座，C(1, 1.5) 受力 P = (200, −1000) N。
#    未知数：杆力 F_AB, F_AC, F_BC（拉为正），支反力 Ax, Ay, By。每个节点两个平衡方程，共 6 个方程。
A_, B_, C_ = np.array([0.0, 0]), np.array([2.0, 0]), np.array([1.0, 1.5])
u = lambda p, q: (q - p) / np.linalg.norm(q - p)
eAB, eAC, eBC = u(A_, B_), u(A_, C_), u(B_, C_)
P = np.array([200.0, -1000.0])
T = np.zeros((6, 6))
rhs = np.zeros(6)
# 节点 A：F_AB eAB + F_AC eAC + (Ax, Ay) = 0
T[0:2, 0], T[0:2, 1], T[0, 3], T[1, 4] = eAB, eAC, 1, 1
# 节点 B：−F_AB eAB + F_BC eBC + (0, By) = 0
T[2:4, 0], T[2:4, 2], T[3, 5] = -eAB, eBC, 1
# 节点 C：−F_AC eAC − F_BC eBC + P = 0
T[4:6, 1], T[4:6, 2] = -eAC, -eBC
rhs[4:6] = -P
f = np.linalg.solve(T, rhs)
out(T=tex(T, 3), truss=vec(f, 1), FAB=float(f[0]), FAC=float(f[1]), FBC=float(f[2]), Ax=float(f[3]), Ay=float(f[4]), By=float(f[5]))
# 3. 丙烷燃烧：x1 C3H8 + x2 O2 → x3 CO2 + x4 H2O；碳、氢、氧三种原子守恒
Ch = [[3, 0, -1, 0], [8, 0, 0, -2], [0, 2, -2, -1]]
R, piv = rref(Ch)
free = [c for c in range(4) if c not in piv][0]
x = [-R[i][free] for i in range(len(piv))] + [1]
den = 1
for v in x:
    den = den * v.denominator // np.gcd(den, v.denominator) if hasattr(v, "denominator") else den
xs = [int(v * den) for v in x]
out(chem="、".join(str(v) for v in xs))
# 4. AGV 路网：四个路口 1–4 构成环路 1→2→3→4→1，各路段流量 f12, f23, f34, f41（辆/小时）；外部流入流出
#    路口 1：进 300 出 —；路口 2：出 200；路口 3：进 100；路口 4：出 200。流入 = 流出
Tr = [[1, 0, 0, -1, 300], [-1, 1, 0, 0, -200], [0, -1, 1, 0, 100], [0, 0, -1, 1, -200]]
R, piv = rref(Tr, 4)
out(traffic=" \\\\ ".join(" & ".join(fstr(x) for x in r) for r in R), npiv_t=len(piv))
# 5. 投入产出：铸造、机加工、装配三个车间。C[i][j] = 车间 j 每产出 1 万元，消耗车间 i 的产品多少万元
Cm = np.array([[0.10, 0.30, 0.05], [0.05, 0.10, 0.40], [0.02, 0.05, 0.10]])
d = np.array([50.0, 80.0, 300.0])           # 对外销售（最终需求），万元
xo = np.linalg.solve(np.eye(3) - Cm, d)
out(C=tex(Cm, 2), d=vec(d, 0), xo=vec(xo, 1), internal=vec(Cm @ xo, 1))
