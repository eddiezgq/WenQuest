"""算例 12.3.1–12.3.3：UR5e、Panda、SCARA 的指数积正运动学，与零件库模型核对。

UR5e：用算例 12.1.2 的旋量表算正运动学，与模型（三维实验显示的同一个模型）在 10000 组随机关节角下比较，
      末端位置误差必须小于 10⁻⁶ m（本章的硬指标）。再用厂家公布的 DH 参数算一遍，看与模型差多少。
Panda：七个转动关节，零位与旋量由模型读出。
SCARA：三个转动关节加一个移动关节。
"""
import numpy as np

from _poe import Model, adjoint, clean, exp6, fk_body, fk_space, inv, screw_prismatic, screw_revolute
from bookout import out, tex, vec

rng = np.random.default_rng(12)

# ---------------------------------------------------------------- UR5e
H1, W1, L1, W2, L2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1
yd = np.array([0, -1.0, 0])
tab = [((0, 0, 1.0), (0, 0, H1)), (yd, (0, -W1, H1)), (yd, (-L1, -W1 + W2, H1)), (yd, (-L1 - L2, -W1 + W2, H1)),
       ((0, 0, -1.0), (-L1 - L2, -W1 + W2 - W3, H1)), (yd, (-L1 - L2, -W1 + W2 - W3, H1 - H2))]
S = [screw_revolute(w, q) for w, q in tab]
M = np.array([[1.0, 0, 0, -L1 - L2], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]])
ur = Model("B-ARM-UR5E", "base", "wrist_3_link", (0, W4, 0))

N = 10000
err_p = err_R = 0.0
for _ in range(N):
    th = rng.uniform(-np.pi, np.pi, 6)
    A, B = fk_space(S, M, th), ur.fk(th)
    err_p = max(err_p, float(np.linalg.norm(A[:3, 3] - B[:3, 3])))
    err_R = max(err_R, float(np.abs(A[:3, :3] - B[:3, :3]).max()))
assert err_p < 1e-6, err_p          # 本章硬指标：误差小于 10⁻⁶ m

# 算例：一组关节角
deg = np.array([30.0, -60.0, 90.0, -120.0, -90.0, 45.0])
th = np.radians(deg)
T = fk_space(S, M, th)
Bl = [adjoint(inv(M)) @ s for s in S]
assert np.allclose(fk_body(Bl, M, th), T, atol=1e-12)
assert np.allclose(T, ur.fk(th), atol=1e-9)

# 厂家公布的标准 DH 参数 (a, d, α)
dh = ur.entry["dh"]["params"]


def fk_dh(q):
    Tq = np.eye(4)
    for (a, d, al), qi in zip(dh, q):
        ct, st, ca, sa = np.cos(qi), np.sin(qi), np.cos(al), np.sin(al)
        Tq = Tq @ np.array([[ct, -st * ca, st * sa, a * ct], [st, ct * ca, -ct * sa, a * st], [0, sa, ca, d], [0, 0, 0, 1]])
    return Tq


gaps = []
Rx90 = np.array([[1.0, 0, 0], [0, 0, -1], [0, 1, 0]])
for _ in range(N):
    q = rng.uniform(-np.pi, np.pi, 6)
    A, B = fk_dh(q), ur.fk(q)
    gaps.append(float(np.linalg.norm(A[:3, 3] - B[:3, 3])))
    assert np.allclose(A[:3, :3].T @ B[:3, :3], Rx90, atol=1e-6)     # 两个末端坐标系只差绕 x 轴 90°
gaps = np.array(gaps)
dh0 = fk_dh(np.zeros(6))[:3, 3]
dims_dh = {"d1": dh[0][1], "a2": -dh[1][0], "a3": -dh[2][0], "d4": dh[3][1], "d5": dh[4][1], "d6": dh[5][1]}

# ---------------------------------------------------------------- Panda（七轴）
pa = Model("B-ARM-PANDA", "link0", "hand", (0, 0, 0), [f"joint{i}" for i in range(1, 8)])
Sp = [x[4] for x in pa.screws()]
Mp = pa.fk(np.zeros(7))
err_pa = 0.0
for _ in range(N):
    q = rng.uniform(-np.pi, np.pi, 7)
    err_pa = max(err_pa, float(np.linalg.norm(fk_space(Sp, Mp, q)[:3, 3] - pa.fk(q)[:3, 3])))
assert err_pa < 1e-6
# 冗余：转动关节 1、3 而保持末端不动的一族解——零位附近，θ1 与 θ3 反向等量转动（两轴重合）
q0 = np.zeros(7)
q0[3], q0[5] = -np.pi / 2, np.pi / 2
self_motion = max(float(np.abs(fk_space(Sp, Mp, q0 + np.array([a, 0, -a, 0, 0, 0, 0])) - fk_space(Sp, Mp, q0)).max())
                  for a in np.radians([10, 20, 40]))

pa_rows = r" \\ ".join(f"{i} & {vec(clean(w), 3)} & {vec(clean(qq), 4)}" for i, (_, _, w, qq, _) in enumerate(pa.screws(), 1))

# ---------------------------------------------------------------- SCARA（RRPR）
sc = Model("B-SCA-WQ4", "base", "tool")
Ss = [x[4] for x in sc.screws()]
Ms = sc.fk(np.zeros(4))
err_sc = 0.0
for _ in range(N):
    q = np.r_[rng.uniform(-np.pi, np.pi, 2), rng.uniform(0, 0.15), rng.uniform(-np.pi, np.pi)]   # 丝杠行程 0–0.15 m
    err_sc = max(err_sc, float(np.linalg.norm(fk_space(Ss, Ms, q)[:3, 3] - sc.fk(q)[:3, 3])))
assert err_sc < 1e-6
qs = np.array([np.radians(40), np.radians(-70), 0.12, np.radians(90)])
Tsc = fk_space(Ss, Ms, qs)
sc_rows = r" \\ ".join(f"{i} & {'移动' if k == 'prismatic' else '转动'} & {vec(clean(w), 3)} & {vec(clean(qq), 3)} & {vec(clean(s), 3)}"
                       for i, (_, k, w, qq, s) in enumerate(sc.screws(), 1))

out(N=N, err_p=err_p, err_R=err_R, T=tex(clean(T, 1e-9), 4), px=T[0, 3], py=T[1, 3], pz=T[2, 3],
    gap_max=gaps.max() * 1000, gap_mean=gaps.mean() * 1000, dh0=vec(dh0, 4), **{k: v for k, v in dims_dh.items()},
    err_pa=err_pa, Mp=tex(clean(Mp, 1e-9), 4), pa_rows=pa_rows, self_motion=self_motion,
    err_sc=err_sc, Ms=tex(clean(Ms), 3), sc_rows=sc_rows, Tsc=tex(clean(Tsc, 1e-9), 4),
    scx=Tsc[0, 3], scy=Tsc[1, 3], scz=Tsc[2, 3])
