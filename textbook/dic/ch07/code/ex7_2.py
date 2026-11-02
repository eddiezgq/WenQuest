"""7.2 节：SRAM 单元的读稳定与写能力。

算例 7.2.1  单元比 CR = W下拉/W存取 取 1～3：保持与读出时的静态噪声容限（SKY130 仿真，Seevinck 法）与手算模型对照。
            上拉比 PR = W上拉/W存取 取 1～3（CR = 2）：写入裕量（单元翻转时的位线电压）；
            要求读出 SNM 与写入裕量都不小于 0.2·VDD（教学设定），选面积最小的 CR、PR。
图 7.2.1    6 管 SRAM 单元。
图 7.2.2    蝴蝶曲线（CR = 2）：保持与读出，各画出两瓣里最大的正方形。
图 7.2.3    (a) 读出 SNM 随单元比；(b) 写入裕量随上拉比。实线仿真，虚线手算模型。
"""
import math

from bookout import T, figure, out, style
from mos import P, VDD, Wmin, sram_snm, sram_write_trip, sram_sim_snm, sram_sim_write, sram_curve
import _draw as d

S = P["sram_sim"]
q = P["problems"]["p72"]
lim = q["snm_min_frac"] * VDD
CRS, PRS = q["cr"], q["pr"]
sim_r = {cr: sram_sim_snm(cr, "read") for cr in CRS}
sim_h = {cr: sram_sim_snm(cr, "hold") for cr in CRS}
sim_w = {pr: sram_sim_write(pr) for pr in PRS}
mod_r = {cr: sram_snm(cr, 1.0, "read") for cr in CRS}
mod_h = {cr: sram_snm(cr, 1.0, "hold") for cr in CRS}
mod_w = {pr: sram_write_trip(2.0, pr) for pr in PRS}
cr_ok = min(cr for cr in CRS if sim_r[cr] >= lim)
pr_ok = max(pr for pr in PRS if sim_w[pr] >= lim)
cr_mod = min(cr for cr in CRS if mod_r[cr] >= lim)
area = lambda cr, pr: 2 * (cr + pr + 1) * Wmin          # noqa: E731  六个管子的总宽（μm）
vals = dict(lim=lim, lim_frac=q["snm_min_frac"], cr_ok=cr_ok, pr_ok=pr_ok, cr_mod=cr_mod, wsum_ok=area(cr_ok, 1.0), wsum_cr2=area(2.0, 1.0),
            wsum_min=area(1.0, 1.0), hold_drop_pct=(1 - sim_r[2.0] / sim_h[2.0]) * 100, wr_cr1=sram_write_trip(1.0, 1.0),
            wr_cr3=sram_write_trip(3.0, 1.0), wr_cr2=sram_write_trip(2.0, 1.0))
for cr in CRS:
    k = f"{cr:g}".replace(".", "_")
    vals[f"sr{k}"], vals[f"sh{k}"], vals[f"mr{k}"], vals[f"mh{k}"] = sim_r[cr], sim_h[cr], mod_r[cr], mod_h[cr]
for pr in PRS:
    k = f"{pr:g}".replace(".", "_")
    vals[f"sw{k}"], vals[f"mw{k}"] = sim_w[pr], mod_w[pr]
vals["mr_err_pct"] = (mod_r[2.0] / sim_r[2.0] - 1) * 100
vals["mr_err_abs"] = abs(vals["mr_err_pct"])
vals["wr_crok"] = sram_write_trip(cr_ok, 1.0)
vals["mw_err_pct"] = (mod_w[1.0] / sim_w[1.0] - 1) * 100
vals["sr_gain_pct"] = (sim_r[3.0] / sim_r[1.0] - 1) * 100
out(**vals)


def lobes(xs, ys):
    """两瓣里最大的正方形：返回 [(边长, (x0, y0)), …]（正方形边平行于坐标轴，(x0, y0) 为左下角）。算法同 mos.snm_seevinck。"""
    s2 = math.sqrt(2)
    a = sorted(((x - y) / s2, (x + y) / s2) for x, y in zip(xs, ys))
    b = sorted(((y - x) / s2, (y + x) / s2) for x, y in zip(xs, ys))

    def at(c, u):
        if u <= c[0][0] or u >= c[-1][0]:
            return None
        for i in range(len(c) - 1):
            if c[i][0] <= u <= c[i + 1][0]:
                t = (u - c[i][0]) / (c[i + 1][0] - c[i][0]) if c[i + 1][0] > c[i][0] else 0.0
                return c[i][1] + t * (c[i + 1][1] - c[i][1])
    best = {1: (0, 0, 0, 0), -1: (0, 0, 0, 0)}
    for i in range(1, 400):
        u = -VDD / s2 + 2 * VDD / s2 * i / 400
        va, vb = at(a, u), at(b, u)
        if va is None or vb is None:
            continue
        sg = 1 if va > vb else -1
        if abs(va - vb) > best[sg][0]:
            best[sg] = (abs(va - vb), u, va, vb)
    res = []
    for sg in (1, -1):
        dv, u, va, vb = best[sg]
        xa, ya = (u + va) / s2, (va - u) / s2
        xb, yb = (u + vb) / s2, (vb - u) / s2
        res.append((dv / s2, (min(xa, xb), min(ya, yb))))
    return res


plt = style()
import matplotlib.patches as mp  # noqa: E402

# ---------------------------------------------------------------- 图 7.2.1 6 管单元
fig, ax = plt.subplots(figsize=(6.8, 3.9))


def fet(x, y, lab, col, flip=False):
    ax.add_patch(mp.Rectangle((x - 0.32, y - 0.22), 0.64, 0.44, fill=False, ec=col, lw=1.4))
    ax.text(x, y, lab, ha="center", va="center", fontsize=9, color=col)


ax.plot([0.6, 0.6], [0.2, 4.0], color=d.NMOS, lw=1.6); ax.plot([7.4, 7.4], [0.2, 4.0], color=d.NMOS, lw=1.6)
ax.text(0.6, 4.15, "BL", ha="center", fontsize=10, color=d.NMOS); ax.text(7.4, 4.15, "BLB", ha="center", fontsize=10, color=d.NMOS)
ax.plot([0.2, 7.8], [3.55, 3.55], color=d.PMOS, lw=1.4); ax.text(0.05, 3.55, "WL", ha="right", va="center", fontsize=10, color=d.PMOS)
ax.plot([2.2, 5.8], [3.1, 3.1], color=d.INK, lw=1.0); ax.text(4.0, 3.2, "VDD", ha="center", fontsize=9)
ax.plot([2.2, 5.8], [0.35, 0.35], color=d.INK, lw=1.0); ax.text(4.0, 0.12, T("地", "GND"), ha="center", fontsize=9)
for x, side in ((2.6, "L"), (5.4, "R")):
    ax.plot([x, x], [3.1, 0.35], color=d.INK, lw=1.0)
    fet(x, 2.5, T("上拉", "PU"), d.PMOS)
    fet(x, 1.0, T("下拉", "PD"), d.NMOS)
qx = {2.6: "Q", 5.4: "QB"}
for x in (2.6, 5.4):
    ax.plot([x, x + (0.0)], [1.75, 1.75], color=d.INK)
    ax.add_patch(mp.Circle((x, 1.75), 0.06, color=d.INK))
    ax.text(x + (-0.35 if x < 4 else 0.35), 1.9, qx[x], fontsize=10, ha="center", color=d.MEAN)
# 存取管
fet(1.6, 1.75, T("存取", "PG"), d.NMOS); ax.plot([0.6, 1.28], [1.75, 1.75], color=d.INK); ax.plot([1.92, 2.6], [1.75, 1.75], color=d.INK)
ax.plot([1.6, 1.6], [1.97, 3.55], color=d.PMOS, lw=0.9)
fet(6.4, 1.75, T("存取", "PG"), d.NMOS); ax.plot([7.4, 6.72], [1.75, 1.75], color=d.INK); ax.plot([6.08, 5.4], [1.75, 1.75], color=d.INK)
ax.plot([6.4, 6.4], [1.97, 3.55], color=d.PMOS, lw=0.9)
# 交叉耦合：Q（实线，从 Q 节点稍高处引出）接右边两个栅；QB（虚线，稍低处引出）接左边两个栅
ax.plot([2.6, 4.6, 4.6], [2.05, 2.05, 2.5], color=d.MEAN, lw=0.9); ax.plot([4.6, 5.08], [2.5, 2.5], color=d.MEAN, lw=0.9)
ax.plot([4.6, 4.6, 5.08], [2.05, 1.0, 1.0], color=d.MEAN, lw=0.9)
ax.plot([5.4, 3.4, 3.4], [1.45, 1.45, 2.5], color=d.MEAN, lw=0.9, ls="--"); ax.plot([3.4, 2.92], [2.5, 2.5], color=d.MEAN, lw=0.9, ls="--")
ax.plot([3.4, 3.4, 2.92], [1.45, 1.0, 1.0], color=d.MEAN, lw=0.9, ls="--")
for x, y in ((2.6, 2.05), (5.4, 1.45)):
    ax.add_patch(mp.Circle((x, y), 0.05, color=d.MEAN))
ax.set_xlim(-0.4, 8.0); ax.set_ylim(-0.1, 4.4); ax.axis("off")
figure(fig, "fig7_2_1")

# ---------------------------------------------------------------- 图 7.2.2 蝴蝶曲线
fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.9))
cv = S["curves"]
xs = [i * 0.02 for i in range(len(cv["hold_2"]))]
for ax, key, title in ((axs[0], "hold_2", T("(a) 保持（字线关）", "(a) Hold (word line off)")),
                       (axs[1], "read_2", T("(b) 读出（字线开、位线 = VDD）", "(b) Read (word line on, bit lines = VDD)"))):
    ys = cv[key]
    ax.plot(xs, ys, color=d.NMOS, lw=1.6, label=T("仿真", "simulation"))
    ax.plot(ys, xs, color=d.NMOS, lw=1.6)
    mx, my = sram_curve(2.0, 1.0, "hold" if key.startswith("hold") else "read", 0.01)
    ax.plot(mx, my, color=d.MUTED, lw=1.0, ls="--", label=T("手算模型", "hand model"))
    ax.plot(my, mx, color=d.MUTED, lw=1.0, ls="--")
    for s, (x0, y0) in lobes(xs, ys):
        ax.add_patch(mp.Rectangle((x0, y0), s, s, fill=True, color=d.LOAD, alpha=0.35))
    sn = min(s for s, _ in lobes(xs, ys))
    ax.text(0.98, 0.98, f"SNM ≈ {sn * 1e3:.0f} mV", transform=ax.transAxes, ha="right", va="top", fontsize=10)
    ax.set_xlim(0, VDD); ax.set_ylim(0, VDD); ax.set_aspect("equal")
    ax.set_xlabel("Q / V"); ax.set_ylabel("QB / V"); ax.set_title(title, fontsize=10)
    d.spines(ax)
axs[1].legend(fontsize=8, loc="center right", frameon=False)
fig.tight_layout()
figure(fig, "fig7_2_2")

# ---------------------------------------------------------------- 图 7.2.3 SNM 与写入裕量
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.0, 3.2))
a1.plot(CRS, [sim_r[c] for c in CRS], "o-", color=d.NMOS, label=T("读出（仿真）", "read (sim.)"))
a1.plot(CRS, [mod_r[c] for c in CRS], "--", color=d.NMOS, alpha=0.7, label=T("读出（模型）", "read (model)"))
a1.plot(CRS, [sim_h[c] for c in CRS], "s-", color=d.MEAN, label=T("保持（仿真）", "hold (sim.)"))
a1.axhline(lim, color=d.LOAD, ls=":", lw=1.2)
a1.text(CRS[0], lim + 0.015, T(f"要求 {lim:.2f} V", f"required {lim:.2f} V"), ha="left", fontsize=8.5, color=d.LOAD)
a1.set_xlabel(T("单元比 CR = W下拉/W存取", "cell ratio CR = W_PD/W_PG")); a1.set_ylabel("SNM / V"); a1.set_ylim(0, 0.85)
a1.set_title(T("(a) 读稳定", "(a) Read stability"), fontsize=10); a1.legend(fontsize=8, frameon=False, loc="lower right")
d.spines(a1)
a2.plot(PRS, [sim_w[p] for p in PRS], "o-", color=d.PMOS, label=T("仿真", "simulation"))
a2.plot(PRS, [mod_w[p] for p in PRS], "--", color=d.PMOS, alpha=0.7, label=T("模型", "model"))
a2.axhline(lim, color=d.LOAD, ls=":", lw=1.2)
a2.set_xlabel(T("上拉比 PR = W上拉/W存取（CR = 2）", "pull-up ratio PR = W_PU/W_PG (CR = 2)")); a2.set_ylabel(T("写入裕量 / V", "write margin / V"))
a2.set_ylim(0, 0.85); a2.set_title(T("(b) 写能力", "(b) Writability"), fontsize=10); a2.legend(fontsize=8, frameon=False)
d.spines(a2)
fig.tight_layout()
figure(fig, "fig7_2_3")
