"""Section 6.1 Casting: the hot spot of the conveyor bearing block (Chapter 3, PB-6207, HT200). On the section normal to the axis
through the bearing center, compute the distance of every point from the boundary of the section (largest inscribed radius) and find
the thickest place: the "hot spot", where the casting solidifies last and shrinkage cavities form easily; estimate the ratio of
solidification times by Chvorinov's rule. Then see what changes when a process pocket is cast into the underside below the hot spot.
Example 6.1.1, Figure 6.1.1.

Chvorinov's rule: solidification time t = B·M², M = volume/cooling surface area (solidification modulus). For a flat plate
M ≈ thickness/2 = inscribed radius, so the ratio of the squares of the inscribed radii on the section is the ratio of solidification
times (same mold, same material, same B). The hot spot is more like a "lump" than a plate, and its modulus is smaller than the
inscribed radius (only r/2 for a long cylinder), so the ratio obtained by treating both places as plates is an upper bound; foundry
practice also often compares inscribed diameters directly (Heuvers' circle method). B is taken of the order for gray iron in sand
molds, 2 min/cm² (set by this book, for the order of magnitude only)."""
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
    base &= ~((np.abs(X) <= Lr / 2) & (Z < hr))                         # recess in the middle of the underside (resting on both ends)
    base &= ~(np.abs(np.abs(X) - Lh / 2) <= dh / 2)                     # foundation-bolt holes
    up = (np.abs(X) <= Ro) & (Z >= tb) & (Z <= H0)
    arch = (X ** 2 + (Z - H0) ** 2 <= Ro ** 2) & (Z >= H0)
    s = base | up | arch
    s &= ~(X ** 2 + (Z - H0) ** 2 < (D / 2) ** 2)                       # bearing bore
    if pocket:                                                          # process pocket: cast into the underside below the hot spot
        xc, w, d = pocket
        s &= ~((np.abs(np.abs(X) - xc) <= w / 2) & (Z < d))
    return s


def hot(s):
    r = ndimage.distance_transform_edt(s) * DX
    i = np.unravel_index(np.argmax(r), r.shape)
    return r, float(r[i]), float(X[i]), float(Z[i])


s0 = section()
r0, rmax0, xh, zh = hot(s0)
r_plate = tb / 2                                                        # base plate away from the hot spot: half thickness
t_plate = B_CHV * (r_plate / 10) ** 2
t_hot0 = B_CHV * (rmax0 / 10) ** 2
POCKET = (abs(xh), 12.0, 7.0)                                           # pocket: centered below the hot spot, 12 wide and 7 mm deep (trial value of this book)
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
