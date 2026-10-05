"""6.1 铸造：输送线轴承座（第 3 章，PB-6207，HT200）的热节。用垂直于轴线、过轴承中心的截面，算每一点到截面边界的距离
（最大内切圆半径），找出最厚的地方——铸件最后凝固、容易缩孔的“热节”；按 Chvorinov 规则估算凝固时间之比。
再看在热节下面从底部挖一个工艺凹槽（铸出）以后的变化。算例 6.1.1，图 6.1.1。

Chvorinov 规则：凝固时间 t = B·M²，M = 体积/散热面积（凝固模数）。平板的 M ≈ 厚度/2 = 内切圆半径，所以截面上内切圆半径的平方之比
就是凝固时间之比（同一铸型、同一材料，B 相同）。
热节处更像一个“块”而不是平板，它的模数小于内切圆半径（长圆柱只有 r/2），所以把两处都当平板算出的倍数是上限；
铸造上也常直接比较内切圆直径（Heuvers 圆法）。B 取灰铸铁砂型的量级 2 min/cm²（本书设定，只用来估量级）。"""
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

import _ch6 as H
from bookout import T, figure, out, style

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ch03" / "code"))
import _ch3 as C3                       # noqa: E402

p = C3.pillow_params("6207")
L, tb, H0, Ro, D, Lh, dh, Lr, hr = p["L"], p["tb"], p["H"], p["Ro"], p["D"], p["Lh"], p["dh"], p["Lr"], p["hr"]
B_CHV = 2.0                             # min/cm²
DX = 0.2
x = np.arange(-L / 2 - 2, L / 2 + 2, DX)
z = np.arange(-2, H0 + Ro + 2, DX)
X, Z = np.meshgrid(x, z)


def section(pocket=None):
    base = (np.abs(X) <= L / 2) & (Z >= 0) & (Z <= tb)
    base &= ~((np.abs(X) <= Lr / 2) & (Z < hr))                         # 底面中间的凹槽（两端着地）
    base &= ~(np.abs(np.abs(X) - Lh / 2) <= dh / 2)                     # 地脚孔
    up = (np.abs(X) <= Ro) & (Z >= tb) & (Z <= H0)
    arch = (X ** 2 + (Z - H0) ** 2 <= Ro ** 2) & (Z >= H0)
    s = base | up | arch
    s &= ~(X ** 2 + (Z - H0) ** 2 < (D / 2) ** 2)                       # 轴承孔
    if pocket:                                                          # 工艺凹槽：在热节下方从底面铸出
        xc, w, d = pocket
        s &= ~((np.abs(np.abs(X) - xc) <= w / 2) & (Z < d))
    return s


def hot(s):
    r = ndimage.distance_transform_edt(s) * DX
    i = np.unravel_index(np.argmax(r), r.shape)
    return r, float(r[i]), float(X[i]), float(Z[i])


s0 = section()
r0, rmax0, xh, zh = hot(s0)
r_plate = tb / 2                                                        # 远离热节处的底板：半厚
t_plate = B_CHV * (r_plate / 10) ** 2
t_hot0 = B_CHV * (rmax0 / 10) ** 2
POCKET = (abs(xh), 12.0, 7.0)                                           # 凹槽：中心在热节下方，宽 12、深 7 mm（本书试取）
s1 = section(POCKET)
r1, rmax1, xh1, zh1 = hot(s1)
t_hot1 = B_CHV * (rmax1 / 10) ** 2
area0, area1 = s0.sum() * DX * DX, s1.sum() * DX * DX

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.0))
for ax, r, rm, (xx, zz), ttl in ((axs[0], r0, rmax0, (xh, zh), T("(a) 原设计", "(a) Original")),
                                 (axs[1], r1, rmax1, (xh1, zh1), T("(b) 热节下方铸出工艺凹槽", "(b) Cored pocket under the hot spot"))):
    im = ax.imshow(np.where(r > 0, r, np.nan), origin="lower", extent=[x[0], x[-1], z[0], z[-1]], cmap="inferno_r", vmin=0, vmax=rmax0)
    ax.add_patch(__import__("matplotlib.patches", fromlist=["Circle"]).Circle((xx, zz), rm, fill=False, ec="#1f77b4", lw=1.0))
    ax.plot(xx, zz, "+", color="#1f77b4", ms=6)
    ax.set_aspect("equal")
    ax.set_xlim(-L / 2 - 3, L / 2 + 3)
    ax.set_ylim(-3, H0 + Ro + 3)
    ax.tick_params(labelsize=6.5)
    ax.set_title(ttl + T(f"：最大内切圆半径 {rm:.1f} mm", f": largest inscribed radius {rm:.1f} mm"), fontsize=7.6)
cb = fig.colorbar(im, ax=axs, shrink=0.8)
cb.set_label(T("到边界的距离 / mm", "Distance to boundary / mm"), fontsize=7)
cb.ax.tick_params(labelsize=6.5)
figure(fig, "fig6_1_1")

out(L=L, tb=tb, wall=p["wall"], H=H0, Ro=Ro, D=D, B_chv=B_CHV, r_plate=r_plate, rmax0=rmax0, xh=abs(xh), zh=zh,
    t_plate=t_plate, t_hot0=t_hot0, ratio0=t_hot0 / t_plate, rmax1=rmax1, t_hot1=t_hot1, ratio1=t_hot1 / t_plate,
    pocket_w=POCKET[1], pocket_d=POCKET[2], area_saved=100 * (1 - area1 / area0),
    d_ratio0=rmax0 / r_plate, d_ratio1=rmax1 / r_plate, W=p["W"])
