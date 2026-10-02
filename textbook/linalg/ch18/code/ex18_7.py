"""18.7 节：图像压缩（齿轮图像 120×160）；UR5e 雅可比矩阵的奇异值与奇异位形；两连杆的速度椭圆。"""
import math

import numpy as np

from _arm import planar2, svd_fixed, ur5e, ur5e_links
from _img import gear_image
from bookout import out

# ---- 图像压缩
A = gear_image()
m, n = A.shape
U, s, Vt = np.linalg.svd(A, full_matrices=False)
tot = np.sum(s ** 2)
rows = []
for k in (1, 5, 10, 20, 40):
    Ak = (U[:, :k] * s[:k]) @ Vt[:k]
    rel = np.linalg.norm(A - Ak, "fro") / np.linalg.norm(A, "fro")
    rows.append((k, rel, k * (m + n + 1) / (m * n), np.linalg.norm(A - Ak, 2), s[k], np.abs(A - Ak).max()))
kk = next(k for k in range(1, 121) if np.sqrt(np.sum(s[k:] ** 2) / tot) < 0.05)
out(m=m, n=n, mn=m * n, s1=s[0], s2=s[1], s3=s[2], s10=s[9], s40=s[39], s_last=s[-1],
    energy1=s[0] ** 2 / tot, k5pct=kk, k5store=kk * (m + n + 1) / (m * n),
    **{f"rel{k}": r for k, r, *_ in rows}, **{f"store{k}": st for k, _, st, *_ in rows},
    **{f"err2_{k}": e2 for k, _, _, e2, _, _ in rows}, **{f"sk1_{k}": sk for k, *_, sk, _ in rows},
    **{f"maxpix{k}": mp for k, *_, mp in rows})

# ---- 两连杆（UR5e 上臂与前臂）：σ1σ2 = l1 l2 |sin θ2|
l1, l2 = ur5e_links()
for deg in (90, 45, 10, 2):
    _, J = planar2(math.radians(30), math.radians(deg), l1, l2)
    sj = np.linalg.svd(J, compute_uv=False)
    out(**{f"p{deg}_s1": sj[0], f"p{deg}_s2": sj[1], f"p{deg}_k": sj[0] / sj[1]})
s2_90 = np.linalg.svd(planar2(math.radians(30), math.radians(90), l1, l2)[1], compute_uv=False)[1]
s2_2 = np.linalg.svd(planar2(math.radians(30), math.radians(2), l1, l2)[1], compute_uv=False)[1]
out(inv_ratio=s2_90 / s2_2, need_2=0.01 / s2_2)        # 1/σ2 放大了多少倍；沿 u2 走 1 cm/s 需要的关节速度

# ---- UR5e：肘关节伸直、腕关节 5 归零时的奇异值
R = ur5e()
base = np.radians([0, -60, 90, -120, -90, 0])          # 一个常见的工作姿态（腕部朝下）


def sv(q):
    return np.linalg.svd(R.jacobian(q), compute_uv=False)


s0 = sv(base)
out(u_base=", ".join(f"{x:.4f}" for x in s0), u_base_min=s0[-1], u_base_w=np.prod(s0), u_base_k=s0[0] / s0[-1])
for e in (90, 45, 20, 5, 0):
    q = base.copy()
    q[2] = math.radians(e)
    sq = sv(q)
    out(**{f"el{e}_min": sq[-1], f"el{e}_w": np.prod(sq)})
    if e:
        out(**{f"el{e}_k": sq[0] / sq[-1]})
for w5 in (-90, -45, -20, -5, 0):
    q = base.copy()
    q[4] = math.radians(w5)
    sq = sv(q)
    out(**{f"wr{-w5}_min": sq[-1], f"wr{-w5}_w": np.prod(sq)})
# 肘关节伸直时，零空间（不能产生的末端运动方向由 u6 给出）
q = base.copy()
q[2] = 0.0
Ue, se, Ve = svd_fixed(R.jacobian(q))
out(el0_s6=se[-1], el0_u6=", ".join(f"{(x if abs(x) >= 5e-4 else 0.0):.3f}" for x in Ue[:, 5]), el0_rank=int(np.linalg.matrix_rank(R.jacobian(q), tol=1e-9)))
