"""3.9 基于模型的定义：在轴承座（6207 用）的三维模型上直接标注尺寸、公差带、基准、几何公差和表面粗糙度（PMI），图 3.9.1。
标注的内容与 3.4 节的零件图相同，只是挂在三维几何上。"""
import math

import numpy as np

import _ch3 as H
from bookout import T, figure, out, style

p = H.pillow_params("6207")
pb = H.pillow_block(p)
L, Wb, W, tb, Hc, Ro, D, Lh, dh = (p[k] for k in ("L", "Wb", "W", "tb", "H", "Ro", "D", "Lh", "dh"))
vis, hid = H.project(pb, "iso")
d = np.array(H.EYE["iso"][0], float)
d /= np.linalg.norm(d)
up = np.array([0, 0, 1.0])
U = -np.cross(d, up)
U /= np.linalg.norm(U)
V = up - up.dot(d) * d
V /= np.linalg.norm(V)


def P(x, y, z):
    q = np.array([x, y, z])
    return q.dot(U), q.dot(V)


BLUE = "#2c6fbb"
plt = style()
fig, ax = plt.subplots(figsize=(7.2, 4.4))
sh = H.Sheet(ax)
sh.polys(vis, "thick")
labels = []


def pmi(pt, xy, text):
    ax.annotate(text, xy=pt, xytext=xy, fontsize=6.8, color=BLUE, ha="center", va="center",
                bbox=dict(boxstyle="square,pad=0.25", fc="white", ec=BLUE, lw=0.6),
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color=BLUE, mutation_scale=7, shrinkA=0, shrinkB=0))
    labels.append(text)


bore_pt = P(D / 2 * math.cos(math.radians(150)), -W / 2, Hc + D / 2 * math.sin(math.radians(150)))
pmi(bore_pt, (-115, 95), f"Ø{D} H7\n∥ 0.03 | A\nRa 1.6")
pmi(P(0, -W / 2, Hc + Ro), (10, 125), f"{Hc:g}±0.05  " + T("（中心高，到基准 A）", "(center height to datum A)"))
pmi(P(Lh / 2, -dh / 2, tb), (95, 75), f"2×Ø{dh:g}  " + T("孔距", "spacing ") + f" {Lh:g}")
pmi(P(Ro * 0.8, -W / 2, tb + 8), (100, 20), T("前、后端面 Ra 3.2", "front and back faces Ra 3.2"))
# 基准 A：底面（安装面）——方框字母 + 涂黑三角形，挂在底面上（GB/T 1182、ISO 5459）
bx, by = P(-L / 2 + 20, -Wb / 2, 0)
ax.add_patch(H.Polygon([(bx - 2.5, by), (bx + 2.5, by), (bx, by - 3.6)], closed=True, fc=BLUE, ec=BLUE, lw=0.3))
ax.plot([bx, bx], [by - 3.6, by - 12], color=BLUE, lw=0.6)
ax.text(bx, by - 16, "A", fontsize=7.5, color=BLUE, ha="center", va="center",
        bbox=dict(boxstyle="square,pad=0.35", fc="white", ec=BLUE, lw=0.6))
labels.append("A")
pmi(P(-L / 2 + 40, -Wb / 2, 0), (-120, -30), T("底面 Ra 6.3（基准 A）", "bottom face Ra 6.3 (datum A)"))
ax.text(-125, -62, T("其余：铸造面；GB/T 1804-m、GB/T 6414；技术要求写在模型的“注释”里",
                     "Others: as-cast; GB/T 1804-m, GB/T 6414; notes stored with the model"), fontsize=6.8, color=BLUE, ha="left")
ax.autoscale()
ax.margins(0.06)
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.suptitle(T("轴承座的三维标注（与图 3.4.1 的零件图内容相同）", "Pillow block with 3D annotations (same content as the drawing in Fig. 3.4.1)"), fontsize=8.5)
figure(fig, "fig3_9_1")
out(n_pmi=len(labels))
