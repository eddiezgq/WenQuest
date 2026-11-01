"""19.5 节：两个应用。(1) 深度相机点云的法向估计：每个点取 k 个近邻做主成分分析，最小特征值的特征向量是法向，
λ₃/(λ₁ + λ₂ + λ₃) 标出棱边；k 取多大合适；法向的朝向。(2) 特征脸：300 张 40×32 的脸（程序画出，不是真人），
用格拉姆矩阵求主成分；重建误差；“离脸空间的距离”区分脸和不是脸的图。"""
import numpy as np

from _cloud import CAM, NOISE, STEP, normals, scan
from _face import H, W, faces, not_faces
from _num import sci
from bookout import out, vec

# (1) 点云法向
P, Nt, E = scan()
inner, near = E > 0.012, E < 0.004
out(npts=len(P), step_mm=1000 * STEP, noise_mm=1000 * NOISE, cam=vec(CAM, 2), n_near=int(near.sum()))
rows = []
for k in (6, 10, 20, 40, 80):
    n, sv, flip = normals(P, k)
    ang = np.degrees(np.arccos(np.clip(np.sum(n * Nt, axis=1), -1, 1)))
    rows.append((k, np.median(ang[inner]), np.median(ang[near]), np.median(sv[inner]), np.median(sv[near])))
    out(**{f"ai{k}": float(np.median(ang[inner])), f"an{k}": float(np.median(ang[near]))})
n, sv, flip = normals(P, 20)
thr = 0.03
out(sv_in20=float(np.median(sv[inner])), sv_near20=float(np.median(sv[near])), thr=thr,
    rec=float(100 * np.mean(sv[near] > thr)), fp=int(np.sum(sv[inner] > thr)), n_inner=int(inner.sum()),
    flip=float(100 * flip.mean()))
# 一个点的局部协方差（箱子顶面中部的一个点，k = 20）
from scipy.spatial import cKDTree  # noqa: E402

i0 = int(np.argmin(np.sum((P - np.array([-0.06, -0.01, 0.05])) ** 2, axis=1)))
_, idx = cKDTree(P).query(P[i0], k=20)
Q = P[idx] - P[idx].mean(axis=0)
w0, V0 = np.linalg.eigh(Q.T @ Q / 20)
out(p0=vec(1000 * P[i0], 1), lam0=vec(1e6 * w0[::-1], 2), n0=vec(V0[:, 0] * np.sign(V0[2, 0]), 3))

# (2) 特征脸
F = faces(300, 1)
mean = F.mean(axis=0)
Fc = F - mean
G = Fc @ Fc.T                                          # 300×300 的格拉姆矩阵，而不是 1280×1280 的协方差矩阵
wg, Ug = np.linalg.eigh(G)
wg, Ug = wg[::-1], Ug[:, ::-1]
r = int(np.linalg.matrix_rank(Fc))                     # = N − 1
sg = np.sqrt(wg[:r])
Vf = Fc.T @ Ug[:, :r] / sg                             # 特征脸：vᵢ = Fcᵀuᵢ/σᵢ
cum = np.cumsum(wg[:r]) / wg[:r].sum()
k90, k95 = int(np.argmax(cum >= 0.90) + 1), int(np.argmax(cum >= 0.95) + 1)
out(nf=len(F), pf=H * W, hf=H, wf=W, rank_f=r, k90=k90, k95=k95, r5=float(100 * cum[4]), s50=sci(float(sg[49] / sg[0]), 0))
Tst = faces(20, 99)
NF = not_faces()


def dffs(X, k):
    """离脸空间的距离：减去平均脸后，到前 k 个特征脸张成的子空间的距离（每像素的均方根）。"""
    D = X - mean
    R = D - D @ Vf[:, :k] @ Vf[:, :k].T
    return np.sqrt(np.mean(R ** 2, axis=1))


for k in (5, 20, 50):
    out(**{f"rms_tr{k}": float(dffs(F, k).mean()), f"rms_te{k}": float(dffs(Tst, k).mean())})
k = 20
d_face = dffs(Tst, k)
d_non = dffs(NF, k)
out(dmax_face=float(d_face.max()), d_non=vec(d_non, 3), dmin_non=float(d_non.min()), comp=float(100 * (H * W + k * H * W + len(F) * k) / (len(F) * H * W)))
