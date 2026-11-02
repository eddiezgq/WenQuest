"""21.5 节：非负矩阵与佩龙–弗罗贝尼乌斯定理。(1) 数字工厂投入产出矩阵 C 的佩龙根与佩龙向量；
科拉茨–维兰特界：行和、列和、任一正向量给出的上下界；(2) AGV 在五个工位之间的调度：马尔可夫链的转移矩阵（按列归一），
平稳分布 = 佩龙向量，第二大特征值的模决定收敛快慢，平均返回时间 1/πᵢ；(3) 周期链：AGV 在两侧工位之间来回，特征值 −1，
分布不收敛；(4) 可约链：维修区进去就不出来。"""
import numpy as np

from bookout import out, tex, vec

# (1) 投入产出矩阵（与 ex3_7.py、ex21_1.py 相同）
C = np.array([[0.10, 0.30, 0.05], [0.05, 0.10, 0.40], [0.02, 0.05, 0.10]])
w, V = np.linalg.eig(C)
i = np.argmax(abs(w))
rho = float(w[i].real)
v = np.abs(V[:, i].real)
v /= v.sum()
assert all(abs(z) < rho for k, z in enumerate(w) if k != i)
wl, U = np.linalg.eig(C.T)
u = np.abs(U[:, np.argmax(abs(wl))].real)
u /= u.sum()
rs, cs = C.sum(axis=1), C.sum(axis=0)
x = np.array([159.6, 253.7, 351.0])                    # 21.1 节的总产出（取一位小数）
q = (C @ x) / x
out(rho=rho, v=vec(v, 3), u=vec(u, 3), rs=vec(rs, 2), cs=vec(cs, 2), qlo=float(q.min()), qhi=float(q.max()), q=vec(q, 3))
assert rs.min() <= rho <= rs.max() and cs.min() <= rho <= cs.max() and q.min() <= rho <= q.max()
# 用佩龙向量本身，上下界重合
assert np.allclose((C @ v) / v, rho)
# 迭代两步：x ← C x，比值的上下界收紧
y = v * 0 + 1
for k in range(3):
    y = C @ y
qq = (C @ y) / y
out(q3lo=float(qq.min()), q3hi=float(qq.max()))

# (2) AGV 调度：1 原料库，2 机加工，3 装配，4 检验，5 充电站；P[i, j] = 从 j 到 i 的概率（每列和为 1）
P = np.array([[0.0, 0.1, 0.3, 0.7, 0.5],
              [0.6, 0.0, 0.0, 0.2, 0.3],
              [0.3, 0.5, 0.0, 0.0, 0.2],
              [0.0, 0.3, 0.6, 0.0, 0.0],
              [0.1, 0.1, 0.1, 0.1, 0.0]])
assert np.allclose(P.sum(axis=0), 1)
# 本原：某个幂全为正
k_pos = next(k for k in range(1, 20) if np.all(np.linalg.matrix_power(P, k) > 0))
wp, Vp = np.linalg.eig(P)
order = np.argsort(-abs(wp))
pi = np.abs(Vp[:, order[0]].real)
pi /= pi.sum()
lam2 = abs(wp[order[1]])
out(P=tex(P, 1), k_pos=k_pos, pi=vec(pi, 3), ret=", ".join(f"{1/z:.1f}" for z in pi), lam2=float(lam2),
    wp=", ".join(f"{z.real:.3f}" if abs(z.imag) < 1e-12 else f"{z.real:.3f}{z.imag:+.3f}\\mathrm i" for z in wp[order]))
# 从原料库出发：第 k 次任务后的分布
p = np.array([1.0, 0, 0, 0, 0])
errs = []
for k in range(40):
    errs.append(np.abs(p - pi).sum())
    p = P @ p
k_conv = next(k for k, e in enumerate(errs) if e < 1e-3)
out(k_conv=k_conv, e5=float(errs[5]), e10=float(errs[10]), rate=float((errs[30] / errs[10]) ** (1 / 20)))
# 长期每 100 次任务中去充电站的次数
out(charge100=float(100 * pi[4]), **{f"pi{i}": float(pi[i]) for i in range(5)})

# (3) 周期链：上料侧 {1, 3} 与下料侧 {2, 4} 交替，每次任务都换一侧
Pp = np.array([[0, 0.5, 0, 0.4],
               [0.7, 0, 0.6, 0],
               [0, 0.5, 0, 0.6],
               [0.3, 0, 0.4, 0]])
assert np.allclose(Pp.sum(axis=0), 1)
wpp = np.sort_complex(np.linalg.eigvals(Pp))
pp = np.array([1.0, 0, 0, 0])
seq = []
for k in range(6):
    seq.append(pp.copy())
    pp = Pp @ pp
out(wpp=", ".join(f"{z.real:.3f}" for z in wpp), side=", ".join(f"{s[0] + s[2]:.0f}" for s in seq))
# 平均之后收敛：(p₀ + … + p_{k−1})/k → π
wq, Vq = np.linalg.eig(Pp)
piq = np.abs(Vq[:, np.argmin(abs(wq - 1))].real)
piq /= piq.sum()
pp, acc = np.array([1.0, 0, 0, 0]), np.zeros(4)
for k in range(1000):
    acc += pp
    pp = Pp @ pp
out(piq=vec(piq, 3), avg=vec(acc / 1000, 3))

# (4) 可约链：三个工位加一个“维修区”（第 4 个状态），维修区只进不出
Pr = np.array([[0.0, 0.53, 0.98, 0.0],
               [0.7, 0.0, 0.0, 0.0],
               [0.28, 0.45, 0.0, 0.0],
               [0.02, 0.02, 0.02, 1.0]])
assert np.allclose(Pr.sum(axis=0), 1)
pr = np.array([1.0, 0, 0, 0])
for k in range(200):
    pr = Pr @ pr
    if k + 1 == 50:
        out(pr50=float(pr[3]))
out(pr200=float(pr[3]), rr=", ".join(f"{abs(z):.3f}" for z in sorted(np.linalg.eigvals(Pr), key=lambda z: -abs(z))))
