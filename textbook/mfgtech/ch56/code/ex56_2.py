"""算例 56.2.1：SH-101 零件图的工艺审查——各表面的公差等级、粗糙度和热处理要求，对照经济精度判断最后一道的方法。
数据：factory/digital/std/SH-101_part.yaml（零件图要求，数字工厂 AI 预检也按它核对）、std/route_methods.yaml（工厂工艺标准）。
画图 56.2.1（零件简图）、56.2.3（各表面的要求与加工方法的经济精度）。"""
import _mfg as M
from bookout import T, figure, out, style

P = M.part101()
R = M.route()
proc = M.proc()
draw = {d["name"]: d for d in P["drawing"]}
rows = []
for name in ("轴承位", "轴伸", "密封轴颈", "齿顶圆"):
    d = draw[name]
    tol = d["es_mm"] - d["ei_mm"]
    it = proc.it_grade(d["size_mm"], tol)
    rows.append({"name": name, "size": d["size_mm"], "tol_um": round(tol * 1000), "it": it, "ra": d["Ra_um"]})
it = {r["name"]: r["it"] for r in rows}
fin = R.METHODS["od_finish_turn"]
grind = R.METHODS["od_finish_grind"]

plt = style()
# ---- 图 56.2.1：零件简图
fig, ax = plt.subplots(figsize=(7.4, 2.8))
x = 0.0
segs = P["part"]["segments"]
for d, L, n in segs:
    h = d / 2
    if n == "齿轮":
        ax.add_patch(plt.Rectangle((x, -h), L, 2 * h, fc="#f1dcc0", ec=M.INK, lw=1.0))
        for k in range(1, 6):
            ax.plot([x + k * L / 6] * 2, [-h, h], color=M.MUTED, lw=0.4)
        ax.plot([x, x + L], [24, 24], color=M.INK, lw=0.5, ls="-.")
        ax.plot([x, x + L], [-24, -24], color=M.INK, lw=0.5, ls="-.")
    else:
        ax.add_patch(plt.Rectangle((x, -h), L, 2 * h, fc="#f6ead9", ec=M.INK, lw=1.0))
    x += L
ax.plot([-6, x + 6], [0, 0], color=M.INK, lw=0.6, ls=(0, (8, 2, 1, 2)))
k = P["part"]["keyway"]
ax.add_patch(plt.Rectangle((k["offset_mm"], 10 - k["t"]), k["L"], k["t"], fc="white", ec=M.INK, lw=0.8))
lab = [(18, 12.5, "Ø20 j6  Ra 1.6\n键槽 6 N9", 18), (46, 14.5, "Ø24 h8\nRa 0.8", 22), (64.5, 15, "Ø25 k6\nRa 0.8", 22),
       (96, 28, "m2 z24  8 级\nØ52 h11（齿顶）", 34), (127.5, 15, "Ø25 k6\nRa 0.8", 22)]
for xx, yy, t, ty in lab:
    ax.annotate(t, (xx, yy), (xx, ty + 8), fontsize=7, ha="center", va="bottom",
                arrowprops={"arrowstyle": "-", "lw": 0.5, "color": M.MUTED})
ax.text(68, -33, T("齿面、两轴承位渗碳淬火 58–62 HRC，有效硬化层（磨后）0.8–1.2 mm；心部 30–45 HRC", "case-hardened 58–62 HRC, case 0.8–1.2 mm after grinding"),
        fontsize=7, ha="center", color=M.RED)
ax.annotate("", (0, -36.5), (136, -36.5), arrowprops={"arrowstyle": "<->", "lw": 0.6})
ax.text(68, -40.5, "136", ha="center", fontsize=7)
ax.text(-4, -9, T("中心孔\nB2.5", "centre\nB2.5"), fontsize=6.5, ha="right", color=M.MUTED)
ax.set_xlim(-14, 150); ax.set_ylim(-44, 50); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig56_2_1")

# ---- 图 56.2.3：各表面的要求与加工方法的经济精度
fig, ax = plt.subplots(figsize=(6.4, 3.0))
meth = [("od_rough_turn", M.MUTED), ("od_semi_turn", M.MUTED), ("od_finish_turn", M.ACCENT), ("od_rough_grind", M.WARM), ("od_finish_grind", M.RED)]
for j, (k_, c) in enumerate(meth):
    m = R.METHODS[k_]
    ax.add_patch(plt.Rectangle((m["IT_min"] - 0.4, m["Ra_min_um"]), m["IT_max"] - m["IT_min"] + 0.8, m["Ra_max_um"] - m["Ra_min_um"],
                               fc=c, alpha=0.18, ec=c, lw=0.8))
    yl = m["Ra_min_um"] * 0.62 if k_ == "od_rough_grind" else m["Ra_max_um"] * 1.12     # 粗磨与精车的范围相同，标在下边
    ax.text((m["IT_min"] + m["IT_max"]) / 2, yl, T(m["method_zh"], m["method_en"]) + (T("（与精车相同）", " (= finish turning)") if k_ == "od_rough_grind" else ""),
            fontsize=7, ha="center", color=c)
for r in rows:
    ax.plot(r["it"], r["ra"], "o", color=M.INK, ms=5)
    ax.text(r["it"] + 0.15, r["ra"] * 0.82, T(r["name"], r["name"]), fontsize=7)
ax.set_yscale("log"); ax.set_xlim(14, 4.5); ax.set_ylim(0.08, 80)
ax.set_xlabel(T("公差等级 IT（向右越精）", "IT grade (finer to the right)")); ax.set_ylabel("Ra / μm")
ax.grid(lw=0.3, alpha=0.5, which="both")
figure(fig, "fig56_2_3")

out(b_lo=draw["轴承位"]["size_mm"] + draw["轴承位"]["ei_mm"], b_hi=draw["轴承位"]["size_mm"] + draw["轴承位"]["es_mm"],
    b_tol=rows[0]["tol_um"], b_it=it["轴承位"], e_it=it["轴伸"], s_it=it["密封轴颈"], t_it=it["齿顶圆"],
    s_tol=rows[2]["tol_um"], fin_it_min=fin["IT_min"], fin_it_max=fin["IT_max"], fin_ra_min=fin["Ra_min_um"],
    gr_it_min=grind["IT_min"], gr_it_max=grind["IT_max"], method_label=R.label(), mass=P["part"]["mass_kg"],
    annual=P["annual_volume"], batch=P["batch"])
