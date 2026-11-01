"""图 19.5.1：点云的法向估计。(a) 深度相机看到的桌面、箱盖毛坯和竖放的轴，颜色表示曲面变化度 λ₃/(λ₁ + λ₂ + λ₃)
（k = 20），短线是部分点的估计法向；(b) 法向误差（中位数）随近邻个数 k 的变化：离棱边远的点与棱边附近的点。
图 19.5.2：特征脸。上行：平均脸与前五张特征脸；下行：一张新脸用 5、20、50 张特征脸重建，以及一张齿轮图的重建。"""
import numpy as np

from _cloud import normals, scan
from _face import H, W, faces, not_faces
from _fig import BLUE, INK, MUTED, RED, T, figure, plt, view3

P, Nt, E = scan()
n20, sv20, _ = normals(P, 20)
Pp, fwd = view3(az=-70, el=40)
Q = np.array([Pp(p) for p in P])
depth = P @ fwd
order = np.argsort(depth)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.8), gridspec_kw={"width_ratios": [1.35, 1]})
sc = a1.scatter(Q[order, 0], Q[order, 1], c=np.minimum(sv20[order], 0.1), cmap="viridis", s=3, lw=0, vmin=0, vmax=0.1, zorder=1)
a1.set_rasterization_zorder(1.5)
rng = np.random.default_rng(3)
pick = rng.choice(len(P), 260, replace=False)
for i in pick:
    a, b = Pp(P[i]), Pp(P[i] + 0.012 * n20[i])
    a1.plot([a[0], b[0]], [a[1], b[1]], color=RED, lw=0.7, zorder=3)
a1.set_aspect("equal")
a1.axis("off")
cb = fig.colorbar(sc, ax=a1, shrink=0.7, pad=0.01)
cb.set_label(T("曲面变化度（≥ 0.1 按 0.1 画）", "surface variation (capped at 0.1)"), fontsize=9)
a1.set_title(T("(a) 点云、估计的法向（红）与曲面变化度", "(a) Point cloud, estimated normals (red), surface variation"), fontsize=11)
ks = [6, 10, 20, 40, 80]
inner, near = E > 0.012, E < 0.004
ai, an = [], []
for k in ks:
    n, _, _ = normals(P, k)
    ang = np.degrees(np.arccos(np.clip(np.sum(n * Nt, axis=1), -1, 1)))
    ai.append(np.median(ang[inner]))
    an.append(np.median(ang[near]))
a2.plot(ks, ai, "o-", color=BLUE, lw=2, label=T("离棱边 12 mm 以外的点", "points > 12 mm from an edge"))
a2.plot(ks, an, "s-", color=RED, lw=2, label=T("离棱边 4 mm 以内的点", "points < 4 mm from an edge"))
a2.set_xscale("log")
a2.set_xticks(ks)
a2.set_xticklabels([str(k) for k in ks])
a2.set_xlabel(T("近邻个数 k", "number of neighbours k"))
a2.set_ylabel(T("法向误差的中位数 / (°)", "median normal error / (°)"))
a2.legend(frameon=False, fontsize=9)
a2.set_title(T("(b) k 小受噪声影响，k 大把棱边抹圆", "(b) Small k: noisy; large k: edges blurred"), fontsize=11)
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig19_5_1")

# 图 19.5.2
F = faces(300, 1)
mean = F.mean(axis=0)
Fc = F - mean
wg, Ug = np.linalg.eigh(Fc @ Fc.T)
wg, Ug = wg[::-1], Ug[:, ::-1]
Vf = Fc.T @ Ug[:, :60] / np.sqrt(wg[:60])
test = faces(20, 99)[0]
gear = not_faces()[0]


def rec(x, k):
    return mean + Vf[:, :k] @ (Vf[:, :k].T @ (x - mean))


fig, ax = plt.subplots(2, 6, figsize=(10.5, 4.6))
tiles = [(mean, T("平均脸", "mean face"), "gray")]
for i in range(5):
    tiles.append((Vf[:, i], T(f"特征脸 {i + 1}", f"eigenface {i + 1}"), "RdBu_r"))
tiles += [(test, T("新的脸", "new face"), "gray"), (rec(test, 5), T("5 张重建", "5 eigenfaces"), "gray"),
          (rec(test, 20), T("20 张重建", "20 eigenfaces"), "gray"), (rec(test, 50), T("50 张重建", "50 eigenfaces"), "gray"),
          (gear, T("齿轮图", "a gear"), "gray"), (rec(gear, 20), T("齿轮用 20 张重建", "gear, 20 eigenfaces"), "gray")]
for a, (img, title, cmap) in zip(ax.flat, tiles):
    if cmap == "gray":
        a.imshow(np.clip(img, 0, 1).reshape(H, W), cmap="gray", vmin=0, vmax=1)
    else:
        m = np.abs(img).max()
        a.imshow(img.reshape(H, W), cmap=cmap, vmin=-m, vmax=m)
    a.set_title(title, fontsize=9.5)
    a.axis("off")
fig.tight_layout()
figure(fig, "fig19_5_2")
