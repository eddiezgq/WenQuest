"""31.3 节的计算：有限元入门——WQ-CR5 大臂在问渠 CAE 里的静力与模态分析。

零件、预设载荷、梁理论的估算都用问渠 CAE 的“WQ-CR5 大臂”示例零件（factory/digital/cae/struct_parts.py），求解用 CAE 的同一套程序
（Gmsh 二阶四面体 + CalculiX，solve.py、modal.py）：书里的数就是学生在网页上点“计算”得到的数。
(1) 算例 31.3.1：三种网格（14、10、7 mm）的静力分析：J3 端面的平均下沉、管中段顶部的 Von Mises 应力、最大应力（多在法兰与管的内角）、
    单元数与计算时间；与梁理论比较。
(2) 算例 31.3.2：模态：一端固定时的前两阶固有频率（成对的弯曲振型），与梁理论（不计 / 计入法兰质量）比较。
图 31.3.1：(a) 7 mm 网格的应力云图（侧视，前半个管）；(b) 管顶一条线上的 Von Mises 应力与梁理论。
"""
import os
import sys
import time

os.environ.setdefault("WQ_CCX_SOLVER", "SPOOLES")
import numpy as np  # noqa: E402

from _ch31 import CAE  # noqa: E402
sys.path.insert(0, str(CAE.parent))
from cae import geometry as G, materials as MT, modal as MO, solve as S, struct_parts as SP  # noqa: E402
from bookout import COLORS as C, T, figure, out, style  # noqa: E402

p = SP.params_of("wqcr5_upper")
step = SP.build("wqcr5_upper", p)
faces, _, solid = G.faces(step)
ex = SP.example("wqcr5_upper", p, faces)
fm = ex["formula"]
R = ex["rows"]
loads = [{"type": "fixed", "faces": R[0]["faces"]},
         {"type": "force", "faces": R[1]["faces"], "vector_n": [R[1]["fx"], R[1]["fy"], R[1]["fz"]]},
         {"type": "moment", "faces": R[2]["faces"], "vector_nmm": [R[2]["mx"] * 1e3, R[2]["my"] * 1e3, R[2]["mz"] * 1e3]}]
mat = MT.get(ex["material_id"])
L, ro = p["L"], p["D"] / 2
I = fm["I_mm4"]
Fy, Mx, Tz = R[1]["fy"], R[2]["mx"] * 1e3, R[2]["mz"] * 1e3


def beam_vm(z):
    """梁理论：离固定端 z（mm）处外表面的 Von Mises 应力（MPa）"""
    M = Mx - Fy * (L - z)
    sig = M * ro / I
    tau = abs(Tz) * ro / (2 * I)
    return np.sqrt(sig ** 2 + 3 * tau ** 2)


res = []
for h in (14.0, 10.0, 7.0):
    t0 = time.time()
    st, surf, allv = S.solve(step, {"material": mat, "loads": loads, "mesh": {"size_mm": h}})
    pos, U, VM = surf["positions"], surf["u"], surf["vm"]
    end = np.abs(pos[:, 2] - L) < 1e-6
    uy = -float(np.mean(U[end, 1]))
    top = (np.abs(pos[:, 2] - L / 2) < 0.6 * h) & (np.hypot(pos[:, 0], pos[:, 1]) > ro - 1e-3) & (pos[:, 1] > ro * 0.97)
    vm_mid = float(np.max(VM[top]))
    res.append({"h": h, "el": st["elements"], "sec": time.time() - t0, "uy": uy, "vm_mid": vm_mid, "vm_max": st["vm_max_mpa"],
                "vm_max_z": st["vm_max_at"][2], "surf": surf})
for k, r in enumerate(res):
    out(**{f"h{k}": r["h"], f"el{k}": r["el"], f"sec{k}": r["sec"], f"uy{k}": r["uy"], f"vmm{k}": r["vm_mid"], f"vmx{k}": r["vm_max"],
           f"vmz{k}": r["vm_max_z"]})
fine = res[-1]
b_mid = float(beam_vm(L / 2))
assert abs(fine["uy"] / fm["delta_mm"] - 1) < 0.05                # 位移：与梁理论差几个百分点
assert abs(res[-1]["uy"] / res[-2]["uy"] - 1) < 0.01               # 网格收敛：位移几乎不变
assert abs(fine["vm_mid"] / b_mid - 1) < 0.1                      # 远离两端的应力与梁理论一致
assert fine["vm_max"] > 1.5 * float(beam_vm(fine["vm_max_z"]))     # 最大应力在法兰内角：应力集中
out(b_uy=fm["delta_mm"], b_mid=b_mid, b_root=fm["vm_mpa"], b_I_cm4=I / 1e4, uy_err=(fine["uy"] / fm["delta_mm"] - 1) * 100,
    mid_err=(fine["vm_mid"] / b_mid - 1) * 100, kt=fine["vm_max"] / float(beam_vm(fine["vm_max_z"])), Fy=-Fy, Mx=Mx / 1e3, Tz=abs(Tz) / 1e3,
    sf_fea=mat["yield_mpa"] / fine["vm_max"], m_tip=fm["m_tip_kg"])

# ---------------------------------------------------------------- 模态
ms, _ = MO.solve(step, {"material": mat, "loads": loads, "mesh": {"size_mm": 10.0}})
f = [x["hz"] for x in ms["freqs"]]
assert abs(f[0] / f[1] - 1) < 0.01 and abs(f[0] / fm["f1_tip_hz"] - 1) < 0.06 and f[0] < fm["f1_hz"]
out(f1=f[0], f2=f[1], f3=f[2], b_f1=fm["f1_hz"], b_f1t=fm["f1_tip_hz"], f_err=(f[0] / fm["f1_tip_hz"] - 1) * 100)

# ---------------------------------------------------------------- 图 31.3.1
plt = style()
fig, axs = plt.subplots(2, 1, figsize=(11.5, 5.6), gridspec_kw={"height_ratios": [1.1, 1.0]})
pos, VM = fine["surf"]["positions"], fine["surf"]["vm"]
tri = fine["surf"]["triangles"]
front = pos[tri].mean(axis=1)[:, 0] > 0                              # 只画前半个管（x > 0 的三角形）
ax = axs[0]
from matplotlib.collections import PolyCollection  # noqa: E402
polys = pos[tri[front]][:, :, [2, 1]]
vals = VM[tri[front]].mean(axis=1)
pc = PolyCollection(polys, array=vals, cmap="turbo", edgecolors="none")
pc.set_clim(0, float(np.percentile(vals, 99.5)))
ax.add_collection(pc)
ax.set_xlim(-5, L + 5)
ax.set_ylim(-ro - 5, ro + 16)
ax.set_aspect("equal")
cb = fig.colorbar(pc, ax=ax, fraction=0.025, pad=0.01)
cb.set_label(T("Von Mises / MPa", "von Mises / MPa"), fontsize=8)
ax.set_xlabel(T("离 J2 端 z / mm", "distance from the J2 end z / mm"))
ax.set_ylabel("y / mm")
ax.text(0, ro + 3, T("J2 端：固定", "J2 end: fixed"), fontsize=8, va="bottom")
ax.text(L, ro + 3, T("J3 端：力 + 力矩", "J3 end: force + moment"), fontsize=8, va="bottom", ha="right")
ax.set_title(T("(a) 应力云图（网格 7 mm，侧视前半个管；变形不放大）", "(a) stress field (7 mm mesh, front half, undeformed)"), fontsize=11)
ax = axs[1]
line = (np.abs(pos[:, 0]) < 4) & (pos[:, 1] > ro - 1e-3)
zz = np.linspace(0, L, 200)
ax.plot(zz, beam_vm(zz), color=C["ink"], lw=1.4, label=T("梁理论（外表面）", "beam theory (outer surface)"))
ax.scatter(pos[line, 2], VM[line], s=8, color=C["x"], label=T("有限元：管顶一条线上的节点", "FEM: nodes along the top line"), zorder=3)
ax.axvspan(0, p["flange_t"], color=C["muted"], alpha=0.15)
ax.axvspan(L - p["flange_t"], L, color=C["muted"], alpha=0.15)
ax.set_xlabel(T("离 J2 端 z / mm（灰色：两端的法兰）", "distance from the J2 end z / mm (grey: the end flanges)"))
ax.set_ylabel(T("Von Mises / MPa", "von Mises / MPa"))
ax.set_xlim(0, L)
ax.set_ylim(0, None)
ax.legend(fontsize=8, frameon=False, loc="upper right")
ax.set_title(T("(b) 管顶的应力：中段与梁理论一致，法兰处偏离", "(b) stress on the top line: matches beam theory mid-span, departs at the flanges"), fontsize=11)
fig.tight_layout()
figure(fig, "fig31_3_1")
