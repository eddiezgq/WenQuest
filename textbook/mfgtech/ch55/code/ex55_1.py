"""算例 55.1.1–55.1.2：表面轮廓与粗糙度参数（hub/surface.py，与《机械设计》4.7 节同一做法：高斯滤波 λc = 0.8 mm）。
55.1.1：SH-301 工序 40 精车表面（f = 0.15、r = 0.4、vc = 150，另加 1.5 µm、2.5 mm 的波纹）的原始轮廓分成波纹度与粗糙度，
        算 Ra、Rq、Rz、Rt，以及 c = Rz/2 处的支承长度率 Rmr；
55.1.2：Ra 相同、形状不同的两条轮廓（尖峰型与平台型）：Rz、偏斜度 Rsk、Rmr 的差别。
画图 55.1.1（车削表面的三维形貌）、55.1.2（车、磨、铣表面的纹理）、55.1.3（表面层的结构，示意）、55.1.4（原始轮廓、波纹度与粗糙度）、
55.1.5（参数的定义）、55.1.6（Ra 相同的两条轮廓）。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

S = M.surf()
f, r, vc = 0.15, 0.4, 150.0
x, z = S.turned_profile(f, r, vc_m_min=vc, wave_um=1.5, wave_mm=2.5, seed=3)
rr = S.roughness(x, z)
mline = S.gauss_mean(z)
rmr = S.material_ratio(rr["r"], rr["Rz"] / 2)


def skew(v):
    v = np.asarray(v) - np.mean(v)
    return float(np.mean(v ** 3) / np.mean(v ** 2) ** 1.5)


rsk = skew(rr["r"])
# 两条 Ra 相同的轮廓：尖峰型（正偏斜）与平台型（负偏斜，如珩磨、平顶加工后）
xs = np.arange(0, 4.0, S.DX)
rng = np.random.default_rng(5)
base = np.convolve(rng.normal(0, 1, xs.size), np.ones(30) / 30, mode="same")
peak = np.where(base > 0, base ** 2, 0.15 * base)
plat = -peak
peak = (peak - peak.mean()); plat = (plat - plat.mean())
target = 0.8
peak *= target / np.mean(np.abs(peak)); plat *= target / np.mean(np.abs(plat))
pp = {}
for name, v in (("peak", peak), ("plat", plat)):
    n = int(round(S.LC / S.DX))
    rz_ = np.mean([v[i * n:(i + 1) * n].max() - v[i * n:(i + 1) * n].min() for i in range(5)])
    pp[name] = {"Ra": float(np.mean(np.abs(v))), "Rz": float(rz_), "Rsk": skew(v), "Rmr": S.material_ratio(v, 0.25 * rz_)}

plt = style()
# ---- 图 55.1.1：车削表面的三维形貌
hm = S.surface_map(f, r, vc_m_min=vc, wave_um=0.0, width=1.0, length=0.9, n=140)
fig = plt.figure(figsize=(6.4, 3.6))
ax = fig.add_subplot(projection="3d")
X_, Y_ = np.meshgrid(np.linspace(0, 1.0, hm.shape[1]), np.linspace(0, 0.9, hm.shape[0]))
ax.plot_surface(X_, Y_, hm, cmap="copper", linewidth=0, antialiased=True, rstride=1, cstride=1, rasterized=True)
ax.set_xlabel(T("切削速度方向 / mm", "cutting direction / mm"), fontsize=8, labelpad=4)
ax.set_ylabel(T("进给方向 / mm", "feed direction / mm"), fontsize=8, labelpad=4)
ax.set_zlabel("µm", fontsize=8); ax.set_zlim(-8, 8); ax.view_init(32, -58); ax.set_box_aspect((1.0, 0.9, 0.35))
ax.tick_params(labelsize=7)
ax.set_title(T(f"精车表面（f = {f}，r = {r}）：沿进给方向一道道残留，纹理方向与切削速度方向一致（高度放大约 50 倍）",
               f"finish-turned surface (f = {f}, r = {r}): ridges across the feed, lay along the cut"), fontsize=8)
fig.set_dpi(200)
figure(fig, "fig55_1_1")

# ---- 图 55.1.4：原始轮廓 → 波纹度 + 粗糙度
fig, axs = plt.subplots(3, 1, figsize=(7.2, 4.6), sharex=True, gridspec_kw={"hspace": 0.55})
k = (x >= S.LC) & (x < S.LC * 6)
axs[0].plot(x[k] - S.LC, (z[k] - z[k].mean()) * 1000, color=M.INK, lw=0.5)
axs[0].plot(x[k] - S.LC, (mline[k] - z[k].mean()) * 1000, color=M.RED, lw=1.2)
axs[0].set_title(T("(a) 原始轮廓与高斯滤波得到的中线（红，λc = 0.8 mm）", "(a) primary profile and the Gaussian mean line (red, λc = 0.8 mm)"), fontsize=8, loc="left")
axs[1].plot(x[k] - S.LC, (mline[k] - mline[k].mean()) * 1000, color=M.RED, lw=1.2)
axs[1].set_title(T("(b) 波纹度轮廓：机床振动、主轴跳动留下的长波", "(b) waviness: long waves from vibration and spindle run-out"), fontsize=8, loc="left")
axs[2].plot(rr["x"] - S.LC, rr["r"], color=M.ACCENT, lw=0.5)
axs[2].set_title(T(f"(c) 粗糙度轮廓：Ra = {rr['Ra']:.2f}，Rz = {rr['Rz']:.1f} µm", f"(c) roughness profile: Ra = {rr['Ra']:.2f}, Rz = {rr['Rz']:.1f} µm"), fontsize=8, loc="left")
for a in axs:
    a.set_ylabel("µm", fontsize=7); a.grid(lw=0.3, alpha=0.4)
axs[2].set_xlabel(T("评定长度 / mm（5 个取样长度）", "evaluation length / mm (5 sampling lengths)"))
figure(fig, "fig55_1_4")

# ---- 图 55.1.5：参数的定义（一个取样长度）
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 2.9), gridspec_kw={"width_ratios": [2.3, 1]})
n = int(round(S.LC / S.DX))
seg = rr["r"][:n]
xx = rr["x"][:n] - rr["x"][0]
a1.plot(xx, seg, color=M.INK, lw=0.6)
a1.axhline(0, color=M.RED, lw=0.8)
a1.fill_between(xx, 0, seg, color=M.ACCENT, alpha=0.25)
a1.axhline(seg.max(), color=M.MUTED, ls="--", lw=0.6); a1.axhline(seg.min(), color=M.MUTED, ls="--", lw=0.6)
a1.annotate("", (0.75, seg.max()), (0.75, seg.min()), arrowprops={"arrowstyle": "<->", "lw": 0.7})
a1.text(0.735, seg.max() - 0.8, T("该取样长度的最大高度", "max. height in this length"), fontsize=7, va="center", ha="right", bbox={"fc": "white", "ec": "none", "pad": 1})
a1.text(0.02, seg.min() - 0.6, T("Ra：轮廓偏离中线的绝对值的平均（阴影面积 ÷ 长度）；Rz：5 个取样长度最大高度的平均", "Ra: mean of |deviation| (shaded area ÷ length); Rz: mean of the 5 maximum heights"), fontsize=6.8)
a1.set_xlim(0, 0.8); a1.set_ylim(seg.min() - 1.0, seg.max() + 0.6); a1.set_xlabel(T("一个取样长度 / mm", "one sampling length / mm")); a1.set_ylabel("µm")
a1.grid(lw=0.3, alpha=0.4)
lv = np.linspace(rr["r"].max(), rr["r"].min(), 80)
a2.plot([np.mean(rr["r"] >= l) * 100 for l in lv], lv, color=M.ACCENT, lw=1.3)
a2.axhline(rr["r"].max() - rr["Rz"] / 2, color=M.RED, ls="--", lw=0.7)
a2.text(rmr * 100 + 3, rr["r"].max() - rr["Rz"] / 2 + 0.3, f"Rmr = {rmr * 100:.0f}%", fontsize=7.5, color=M.RED)
a2.set_xlabel(T("支承长度率 Rmr / %", "material ratio Rmr / %")); a2.set_xlim(0, 100); a2.grid(lw=0.3, alpha=0.4)
a2.set_title(T("支承长度率曲线", "material ratio curve"), fontsize=8)
figure(fig, "fig55_1_5")

# ---- 图 55.1.6：Ra 相同的两条轮廓
fig, axs = plt.subplots(2, 1, figsize=(7.2, 3.4), sharex=True, gridspec_kw={"hspace": 0.5})
for a, (name, v), c in zip(axs, (("peak", peak), ("plat", plat)), (M.RED, M.ACCENT)):
    q = pp[name]
    a.plot(xs[:int(1.6 / S.DX)], v[:int(1.6 / S.DX)], color=c, lw=0.7)
    a.axhline(0, color=M.MUTED, lw=0.5)
    lab = T("尖峰型", "peaky") if name == "peak" else T("平台型", "plateau")
    a.set_title(T(f"{lab}：Ra = {q['Ra']:.2f}，Rz = {q['Rz']:.1f} µm，Rsk = {q['Rsk']:+.1f}，最高峰下 Rz/4 处 Rmr = {q['Rmr'] * 100:.0f}%",
                  f"{lab}: Ra = {q['Ra']:.2f}, Rz = {q['Rz']:.1f} µm, Rsk = {q['Rsk']:+.1f}"), fontsize=8, loc="left")
    a.set_ylabel("µm", fontsize=7); a.grid(lw=0.3, alpha=0.4)
axs[1].set_xlabel(T("长度 / mm", "length / mm"))
figure(fig, "fig55_1_6")

# ---- 图 55.1.3：表面层的结构（示意）
fig, ax = plt.subplots(figsize=(6.4, 3.0))
xx = np.linspace(0, 10, 400)
top = 0.25 * np.sin(xx * 3.1) + 0.12 * np.sin(xx * 7.3)
layers = [(0.0, 0.12, "#9fb6cc", T("吸附层、氧化膜（约 0.001–0.01 mm）", "adsorbed / oxide film")),
          (0.12, 1.3, "#f0d9bf", T("塑性变形层（加工硬化，0.01–0.2 mm）", "plastically deformed (work-hardened)")),
          (1.3, 2.2, "#f6e7e5", T("热影响层（金相组织变化，磨削时可达 0.1 mm 以上）", "heat-affected (phase change)")),
          (2.2, 3.8, "#e8e8e8", T("基体（残余应力逐渐过渡为零）", "bulk (residual stress fades to zero)"))]
for d0, d1, col, lab in layers:
    ax.fill_between(xx, top - d0, top - d1, color=col, lw=0)
    ax.text(10.15, -(d0 + d1) / 2, lab, fontsize=7.2, va="center")
ax.plot(xx, top, color=M.INK, lw=1.0)
ax.set_xlim(0, 17.5); ax.set_ylim(-4, 1); ax.axis("off")
ax.set_title(T("加工后的表面层（深度方向放大，示意）", "the surface layer after machining (depth exaggerated, schematic)"), fontsize=8.5)
figure(fig, "fig55_1_3")

# ---- 图 55.1.2：车、磨、铣表面的纹理
fig = plt.figure(figsize=(7.6, 2.8))
rng2 = np.random.default_rng(9)
n2 = 110
g = np.linspace(0, 1, n2)
Xg, Yg = np.meshgrid(g, g)
from scipy.ndimage import gaussian_filter
ground = gaussian_filter(rng2.normal(0, 1, (n2, n2)), (0.6, 6)) * 3.5
milled = 2.5 * (((Xg * 0.7 + Yg * 0.0) % 0.18 - 0.09) ** 2) * 200 + 0.3 * gaussian_filter(rng2.normal(0, 1, (n2, n2)), 1.5)
cx, cy = 0.5, -0.9
rad = np.hypot(Xg - cx, Yg - cy)
milled = 3.0 * ((rad % 0.12 - 0.06) ** 2) * 220
maps = [(T("车削：平行的残留", "turned: parallel ridges"), S.surface_map(f, r, vc_m_min=vc, width=1.0, length=1.0, n=n2)),
        (T("磨削：沿磨削方向的细划痕", "ground: fine scratches along the grind"), ground),
        (T("端铣：圆弧形刀纹", "face milled: arc-shaped tool marks"), milled - milled.mean())]
for i, (title, hm2) in enumerate(maps):
    ax = fig.add_subplot(1, 3, i + 1, projection="3d")
    ax.plot_surface(Xg, Yg, hm2, cmap="copper", linewidth=0, rstride=1, cstride=1, rasterized=True)
    ax.set_zlim(-10, 10); ax.view_init(40, -60); ax.set_axis_off(); ax.set_box_aspect((1, 1, 0.35))
    ax.set_title(title, fontsize=8)
fig.set_dpi(200)
figure(fig, "fig55_1_2")

out(f=f, r=r, vc=vc, Ra=rr["Ra"], Rq=rr["Rq"], Rz=rr["Rz"], Rt=rr["Rt"], Rmr=rmr * 100, Rsk=rsk, rq_ra=rr["Rq"] / rr["Ra"], rz_ra=rr["Rz"] / rr["Ra"],
    pk_Ra=pp["peak"]["Ra"], pk_Rz=pp["peak"]["Rz"], pk_Rsk=pp["peak"]["Rsk"], pk_Rmr=pp["peak"]["Rmr"] * 100,
    pl_Ra=pp["plat"]["Ra"], pl_Rz=pp["plat"]["Rz"], pl_Rsk=pp["plat"]["Rsk"], pl_Rmr=pp["plat"]["Rmr"] * 100)
