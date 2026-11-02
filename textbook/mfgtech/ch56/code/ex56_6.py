"""算例 56.6.1、56.6.2：加工方案链。由表面的要求（IT、Ra、要不要在淬硬后加工）从加工方法表倒推可行的方案链
（hub/route.py 与 std/route_methods.yaml，数字工厂的 AI 工艺评审员用同一份）；SH-101 各表面的方案链；“跳级”的例子。
画图 56.6.1（外圆 IT6 方案链的阶梯图）、56.6.4（SH-101 各表面的方案链）。"""
import _mfg as M
from bookout import T, figure, out, style

R = M.route()
P = M.part101()
proc = M.proc()
ch_soft = R.chains("外圆", 6, 0.8, hardened=False)
ch_hard = R.chains("外圆", 6, 0.8, hardened=True)
ch_hole = R.chains("孔", 7, 0.8)
ch_hole_h = R.chains("孔", 6, 0.4, hardened=True)
ch_gear8 = R.chains("齿面", 8, None, hardened=True)
ch_gear6 = R.chains("齿面", 6, 0.8, hardened=True)
jump = R.check_chain(["od_rough_turn", "od_finish_grind"], 6, 0.8)
hard_turn = R.check_chain(["od_rough_turn", "od_semi_turn", "od_finish_turn"], 6, 0.8, hardened_from=2)
# SH-101 各表面
surf = []
for d in P["drawing"]:
    it = proc.it_grade(d["size_mm"], d["es_mm"] - d["ei_mm"])
    hard = d["name"] in ("轴承位", "轴伸", "密封轴颈")          # 渗碳淬火后要磨的（尺寸 IT6–8、Ra 0.8–1.6）
    c = R.chains("外圆", it, d["Ra_um"], hardened=hard)
    surf.append((d["name"], it, d["Ra_um"], hard, c[0]["zh"] if c else "—"))
g = P["part"]["gear"]
surf.append((T("齿面", "flanks"), 8, 1.6, True, ch_gear8[0]["zh"]))

plt = style()
# ---- 图 56.6.1：阶梯图（公差等级与 Ra 随方案链逐级降低）
c0 = ch_hard[0]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.6))
xs, its, ras, names = [0], [R.BLANK_IT["热轧圆钢"]], [50.0], [T("棒料", "bar")]
for i, k in enumerate(c0["steps"]):
    m = R.METHODS[k]
    xs.append(len(xs)); its.append(m["IT_min"] if i == len(c0["steps"]) - 1 else m["IT_max"]); ras.append(m["Ra_max_um"] if i < len(c0["steps"]) - 1 else 0.8)
    names.append(T(m["method_zh"], m["method_en"]))
a1.step(xs, its, where="post", color=M.ACCENT, lw=1.4); a1.plot(xs, its, "o", color=M.ACCENT, ms=4)
a1.invert_yaxis(); a1.set_ylabel(T("这一道后的公差等级 IT", "IT after the step"))
a2.step(xs, ras, where="post", color=M.WARM, lw=1.4); a2.plot(xs, ras, "o", color=M.WARM, ms=4)
a2.set_yscale("log"); a2.set_ylabel("Ra / μm")
h = c0["heat_at"] + 1
for a in (a1, a2):
    a.axvspan(h - 0.5, h - 0.45, color=M.RED, alpha=0.6)
    a.set_xticks(xs); a.set_xticklabels(names, fontsize=7, rotation=0); a.grid(lw=0.3, alpha=0.5)
a1.text(h - 0.4, 13, T("渗碳淬火", "carburize"), fontsize=7, color=M.RED)
a1.axhline(6, color=M.RED, ls="--", lw=0.7); a2.axhline(0.8, color=M.RED, ls="--", lw=0.7)
figure(fig, "fig56_6_1")

# ---- 图 56.6.4：SH-101 各表面的方案链（表）
fig, ax = plt.subplots(figsize=(6.8, 2.1))
ax.axis("off")
cell = [[n, f"IT{it}", f"{ra:g}", T("是", "yes") if hd else T("否", "no"), zh] for n, it, ra, hd, zh in surf]
tb = ax.table(cellText=cell, colLabels=[T("表面", "surface"), T("公差等级", "grade"), "Ra / μm", T("淬硬后加工", "after hardening"),
                                        T("方案链（由粗到精）", "chain (rough → fine)")], loc="center", cellLoc="left",
              colWidths=[0.13, 0.11, 0.09, 0.12, 0.55])
tb.auto_set_font_size(False); tb.set_fontsize(7.5); tb.scale(1, 1.35)
for (r, c), x in tb.get_celld().items():
    x.set_edgecolor("#c9cfd3")
    if r == 0:
        x.set_facecolor("#eef1f3")
figure(fig, "fig56_6_4")

out(soft=ch_soft[0]["zh"], soft2=ch_soft[1]["zh"] if len(ch_soft) > 1 else "", hard=ch_hard[0]["zh"], hard2=ch_hard[1]["zh"] if len(ch_hard) > 1 else "",
    hole=ch_hole[0]["zh"], hole2=ch_hole[-1]["zh"], hole_h=ch_hole_h[0]["zh"], gear8=ch_gear8[0]["zh"], gear6=ch_gear6[-1]["zh"],
    jump=jump[0], hard_turn=hard_turn[0], n_hard=len(ch_hard), seal=next(s[4] for s in surf if s[0] == "密封轴颈"),
    tip=next(s[4] for s in surf if s[0] == "齿顶圆"), bearing=next(s[4] for s in surf if s[0] == "轴承位"),
    distort=R.HEAT_DISTORT, label=R.label())
