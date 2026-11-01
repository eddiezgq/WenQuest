"""算例 54.3.1–54.3.4：机床误差（hub/accuracy.py）。
54.3.1：滑动轴承主轴，主轴颈椭圆（二阶，半径上幅值 0.003）、轴承孔三棱（三阶，0.004）：车削与镗削时工件（孔）的圆度（spindle_roundness）；
54.3.2：车床导轨水平面、垂直面直线度各 0.01，前后导轨扭曲 0.02/400、中心高 200：车 Ø40 外圆的直径误差（guide_errors）；
54.3.3：外圆磨床尾座偏移 e = 0.008：SH-301 左右轴承位（距左端 46、124.5）的直径差（taper_from_offset），与仿真车间一个班次的实测比较；
         工艺规程工序 60 精度预算里“轴承位 25 mm 长度内的锥度”对应的尾座允许偏移；
54.3.4：车削螺纹的传动链误差（chain_error）。画图 54.3.2、54.3.3、54.3.6、54.3.7。"""
import math
import statistics as st

import _mfg as M
from bookout import T, figure, out, style

A = M.acc()
ER = M.errs()
# 54.3.1
journal, hole = [(2, 0.003, 0)], [(3, 0.004, 0)]
tr = A.spindle_roundness(journal, hole, "turning")
bo = A.spindle_roundness(journal, hole, "boring")
ht, hb = A.harmonics(tr["r"]), A.harmonics(bo["r"])
assert ht["dominant"] == 2 and hb["dominant"] == 3
# 54.3.2
g = A.guide_errors(20.0, dy_h=0.01, dz_v=0.01, twist=0.02, H=200.0, B=400.0)
# 54.3.3
e, L = 0.008, ER.LENGTH
dd = A.taper_from_offset(e, L, ER.Z_LEFT, ER.Z_RIGHT)
s = M.shift(n_ok=30, n_bad=30)
v = s["values"]
meas = st.fmean(v["bearing_seat_d35_r"][30:]) - st.fmean(v["bearing_seat_d35"][30:])
meas0 = st.fmean(v["bearing_seat_d35_r"][:30]) - st.fmean(v["bearing_seat_d35"][:30])
plan = M.plan()
it = next(i for i in M.op(plan, 60)["accuracy"][0]["items"] if i["name"].startswith("两顶尖"))
seg = 137.0 - 112.0                                       # 右轴承位：轴肩 S3–S4（第 53 章的轴向跟踪图）
e_allow = it["range"] * L / (2 * seg)                    # 轴承位长度（取较长的右轴承位 25 mm）内的锥度 2e·25/L
# 54.3.4：主轴 → 交换齿轮 a/b、c/d → 丝杠（螺距 6），车螺距 3 的螺纹；各元件的转角误差折算到刀架的位移（µm），传动比按到丝杠计
P_ls = 6.0
elems = [("主轴齿轮（转角误差 2′）", 2 / 60 / 360 * P_ls * 1000, 0.5), ("交换齿轮 a/b（3′）", 3 / 60 / 360 * P_ls * 1000, 0.5),
         ("交换齿轮 c/d（3′）", 3 / 60 / 360 * P_ls * 1000, 1.0), ("丝杠螺距误差（一个螺距内）", 4.0, 1.0)]
ch = A.chain_error(elems)

plt = style()
# ---- 图 54.3.2：主轴回转误差的三种基本形式
fig, axs = plt.subplots(1, 3, figsize=(7.6, 2.6))
for ax, kind in zip(axs, ("radial", "axial", "tilt")):
    ax.plot([-1.2, 1.2], [0, 0], color=M.MUTED, lw=0.8, ls="-.")
    if kind == "radial":
        for dy, c in ((0.0, M.INK), (0.22, M.RED)):
            ax.add_patch(plt.Rectangle((-0.9, dy - 0.32), 1.6, 0.64, fill=False, ec=c, lw=1.2, ls="-" if dy == 0 else "--"))
            ax.plot([-1.2, 1.2], [dy, dy], color=c, lw=0.8, ls="-.")
        ax.annotate("", xy=(0.95, 0.22), xytext=(0.95, 0), arrowprops=dict(arrowstyle="<->", color=M.RED))
        ax.set_title(T("(a) 径向跳动", "(a) radial motion"), fontsize=8.5)
    elif kind == "axial":
        for dx, c in ((0.0, M.INK), (0.22, M.RED)):
            ax.add_patch(plt.Rectangle((-0.9 + dx, -0.32), 1.6, 0.64, fill=False, ec=c, lw=1.2, ls="-" if dx == 0 else "--"))
        ax.annotate("", xy=(0.92, 0.45), xytext=(0.7, 0.45), arrowprops=dict(arrowstyle="<->", color=M.RED))
        ax.set_title(T("(b) 轴向窜动", "(b) axial motion"), fontsize=8.5)
    else:
        ax.add_patch(plt.Rectangle((-0.9, -0.32), 1.6, 0.64, fill=False, ec=M.INK, lw=1.2))
        a = math.radians(10)
        pts = [(-0.9, -0.32), (0.7, -0.32), (0.7, 0.32), (-0.9, 0.32)]
        rp = [(x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)) for x, y in pts]
        ax.add_patch(plt.Polygon(rp, fill=False, ec=M.RED, lw=1.2, ls="--"))
        ax.plot([-1.2 * math.cos(a), 1.2 * math.cos(a)], [-1.2 * math.sin(a), 1.2 * math.sin(a)], color=M.RED, lw=0.8, ls="-.")
        ax.set_title(T("(c) 角度摆动", "(c) tilt"), fontsize=8.5)
    ax.text(-1.15, -0.62, T("黑：理想轴线；红：实际", "black: ideal axis; red: actual"), fontsize=6.5, color=M.MUTED)
    ax.set_xlim(-1.25, 1.25); ax.set_ylim(-0.7, 0.75); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig54_3_2")

# ---- 图 54.3.3：车削与镗削时主轴回转误差反映到工件上（极坐标，误差放大）
fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.4), subplot_kw={"projection": "polar"})
for ax, res, ttl in ((axs[0], tr, T(f"(a) 车削：工件反映主轴颈的椭圆（圆度 {tr['roundness'] * 1000:.0f} µm）",
                                    f"(a) turning: the journal's ellipse ({tr['roundness'] * 1000:.0f} µm)")),
                     (axs[1], bo, T(f"(b) 镗削：孔反映轴承孔的三棱（圆度 {bo['roundness'] * 1000:.0f} µm）",
                                    f"(b) boring: the bearing hole's three lobes ({bo['roundness'] * 1000:.0f} µm)"))):
    k = 1 / 0.03
    ax.plot(res["psi"] + [res["psi"][0]], [1 + k * x for x in res["r"]] + [1 + k * res["r"][0]], color=M.RED, lw=1.3)
    ax.plot([2 * math.pi * i / 100 for i in range(101)], [1.0] * 101, color=M.MUTED, lw=0.6, ls="--")
    ax.set_ylim(0, 1.7); ax.set_yticks([]); ax.set_xticks([])
    ax.set_title(ttl, fontsize=8, pad=8)
figure(fig, "fig54_3_3")

# ---- 图 54.3.6：尾座偏移与左右轴承位的直径差
fig, ax = plt.subplots(figsize=(5.8, 3.2))
es = [0.001 * i for i in range(0, 13)]
ax.plot([x * 1000 for x in es], [A.taper_from_offset(x, L, ER.Z_LEFT, ER.Z_RIGHT) * 1000 for x in es], color=M.ACCENT,
        label=T("计算：2e(z₂ − z₁)/L", "computed: 2e(z₂ − z₁)/L"))
ax.plot([e * 1000], [meas * 1000], "s", color=M.RED, ms=6, label=T("仿真车间实测（30 件平均）", "simulated shop (mean of 30)"))
ax.plot([0], [meas0 * 1000], "o", color=M.GREEN, ms=5, label=T("注入前（30 件平均）", "before injection (mean of 30)"))
ax.axhline(16, color=M.MUTED, ls="--", lw=0.8)
ax.text(0.3, 16.4, T("k6 公差 16 µm", "k6 tolerance 16 µm"), fontsize=7.5, color=M.MUTED)
ax.axvspan(0, e_allow * 1000, color="#e5f0e8")
ax.text(0.1, 1.0, T(f"开班点检允许\ne ≤ {e_allow * 1000:.1f} µm", f"start-of-shift check\ne ≤ {e_allow * 1000:.1f} µm"), fontsize=7, color=M.GREEN)
ax.set_xlabel(T("尾座偏移 e / µm", "tailstock offset e / µm"))
ax.set_ylabel(T("右减左轴承位直径 / µm", "right − left bearing seat / µm"))
ax.set_ylim(-1, 18.5); ax.legend(fontsize=7.5, loc="lower right"); ax.grid(lw=0.3, alpha=0.5)
figure(fig, "fig54_3_6")

# ---- 图 54.3.7：传动链误差：各元件折算到末端的误差
fig, ax = plt.subplots(figsize=(5.8, 2.6))
names = [T(n, n2) for n, n2 in zip([x[0] for x in elems], ["spindle gear (2′)", "change gears a/b (3′)", "change gears c/d (3′)", "lead-screw pitch error"])]
vals = [abs(t[1]) for t in ch["terms"]]
ax.barh(range(len(vals)), vals, color=[M.ACCENT, M.ACCENT, M.WARM, M.RED])
ax.set_yticks(range(len(vals))); ax.set_yticklabels(names, fontsize=7.5)
for i, x in enumerate(vals):
    ax.text(x + 0.05, i, f"{x:.2f}", va="center", fontsize=7.5)
ax.invert_yaxis()
ax.set_xlabel(T("折算到刀架的螺距误差 / µm", "pitch error at the carriage / µm"))
ax.set_title(T(f"极值 {ch['extreme']:.1f} µm，平方和开方 {ch['rss']:.1f} µm", f"worst case {ch['extreme']:.1f} µm, RSS {ch['rss']:.1f} µm"), fontsize=8.5)
figure(fig, "fig54_3_7")

out(rt_um=tr["roundness"] * 1000, rb_um=bo["roundness"] * 1000, gh_um=g["horizontal"] * 1000, gv_um=g["vertical"] * 1000,
    gt_um=g["twist"] * 1000, gt_dy_um=g["twist_dy"] * 1000, e_um=e * 1000, dd_um=dd * 1000, meas_um=meas * 1000, meas0_um=meas0 * 1000,
    e_allow_um=e_allow * 1000, budget_taper_um=it["range"] * 1000, ch_ext=ch["extreme"], ch_rss=ch["rss"], ls_um=elems[3][1],
    term_sp=ch["terms"][0][1], term_cd=ch["terms"][2][1], term_ab=ch["terms"][1][1], zl=ER.Z_LEFT, zr=ER.Z_RIGHT, L=L, dl_um=2 * e * ER.Z_LEFT / L * 1000, dr_um=2 * e * ER.Z_RIGHT / L * 1000)
