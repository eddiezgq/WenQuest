"""Section 1.6, the engineering calculation sheet: one page of the static strength check of the SH-301 extension, written
with the book's calculation-sheet module (conventions/calcsheet.py) (Example 1.6.1, Fig. 1.6.1); what one unit error does
(Example 1.6.2)."""
import math

import _ch1 as H
import _con as E
from bookout import T, figure, out, style
from calcsheet import CalcSheet
import mdstd

d = E.d_pick
k = mdstd.key_for(d)
cs = CalcSheet(T("SH-301 外伸段静强度校核（算例 1.4.1）", "SH-301 extension: static strength check (Example 1.4.1)"), item="SH-301", rev="A",
                author=T("（示例）", "(example)"))
Tr = cs.given("T", E.T_R, "N·m", T("额定输出转矩（含工况系数）", "rated output torque (incl. application factor)"),
              src=T("数字工厂参数配置器", "digital-factory configurator"))
K = cs.given("K", E.K_PEAK, "", T("起动冲击倍数", "starting-peak factor"), src=T("跑合试验台转矩记录", "run-in bench torque record"))
cs.given("d", d, "mm", T("外伸段直径", "extension diameter"), src=T("算例 1.4.1", "Example 1.4.1"))
cs.given("b × t", "{} × {}".format(k["b"], k["t"]), "mm", T("键槽宽 × 深", "keyway width × depth"), src="GB/T 1095")
ss = cs.given("σ_s", E.mat["sigma_s"], "MPa", T("45 钢调质屈服强度", "yield strength, 45 steel QT"), src=T("数字工厂材料库", "digital-factory material library"))
cs.find("S", T("起动峰值下的静强度安全系数", "static safety factor at the starting peak"))
Tp = cs.step("T_max", "T_max = K T", K * Tr, "N·m", T("峰值转矩", "peak torque"), subst="{:.3f} × {:.0f}".format(K, Tr))
WT = cs.step("W_T", "W_T = πd³/16 − bt(d − t)²/(2d)", E.WT_key(d), "mm³", T("带键槽的抗扭截面系数", "torsional section modulus with keyway"),
             src=T("濮良贵《机械设计》抗扭截面系数表", "Pu Lianggui, Machine Design: section-modulus table"))
tau = cs.step("τ", "τ = T_max / W_T", Tp * 1e3 / WT, "MPa", T("最大切应力", "maximum shear stress"))
ts = cs.step("τ_s", "τ_s = σ_s / √3", ss / math.sqrt(3), "MPa", T("剪切屈服强度", "shear yield strength"), src=T("冯·米塞斯准则", "von Mises criterion"))
S = cs.step("S", "S = τ_s / τ", ts / tau, "", T("安全系数", "safety factor"))
cs.check("S", S, ">=", E.S_REQ, T("静强度", "static strength"), src=T("1.5 节", "Section 1.5"))
cs.note(T("只校核起动峰值下的静强度；疲劳见 33.5 节。", "Static strength at the starting peak only; fatigue in Section 33.5."))

# ---- Example 1.6.2: T in N·m substituted as if it were N·mm (the factor 1000 forgotten)
tau_wrong = Tp / WT
d_wrong = E.d_strength / 1000 ** (1 / 3)

# ---------------------------------------------------------------- Fig. 1.6.1: one page of a calculation sheet
plt = style()
rows = [r for r in cs.rows]
fig, ax = plt.subplots(figsize=(6.8, 4.3))
ax.axis("off")
ax.text(0.0, 1.0, cs.title, fontsize=10, weight="bold", va="top", transform=ax.transAxes)
ax.text(0.0, 0.94, T("零件号 SH-301　版本 A（现行）　编制：（示例）　日期：（略）", "Part SH-301   Rev. A (current)   By: (example)   Date: (omitted)"), fontsize=8, va="top",
        color=H.MUTED, transform=ax.transAxes)
cells = []
for r in rows:
    if r["kind"] == "given":
        cells.append([r["what"], T("已知", "given"), "{} = {} {}".format(r["sym"], r["value"] if isinstance(r["value"], str) else
                      "{:.4g}".format(r["value"]), r["unit"]), r["src"]])
    else:
        cells.append([r["what"], r["formula"], "{} = {:.4g} {}".format(r["sym"], r["value"], r["unit"]), r.get("src", "")])
c = cs.checks[0]
cells.append([T("校核：", "Check: ") + c["what"], "{} {} {}".format(c["sym"], c["op"], c["limit"]),
              ("✓ " if c["ok"] else "✗ ") + "{:.3g}".format(c["value"]), c["src"]])
tb = ax.table(cellText=cells, colLabels=[T("项目", "Item"), T("公式", "Formula"), T("结果", "Result"), T("出处", "Source")],
              loc="upper left", bbox=[0, 0.08, 1, 0.82], colWidths=[0.27, 0.3, 0.2, 0.23], cellLoc="left")
tb.auto_set_font_size(False)
tb.set_fontsize(6.8)
for (r_, c_), cell in tb.get_celld().items():
    cell.set_linewidth(0.5)
    if r_ == 0:
        cell.set_facecolor(H.PALE["blue"])
ax.text(0.0, 0.0, T("结论：", "Conclusion: ") + cs.conclusion(), fontsize=8.5, transform=ax.transAxes)
fig.tight_layout()
figure(fig, "fig1_6_1")

out(d=d, b=k["b"], t=k["t"], T_R=Tr, K=K, T_max=Tp, WT=WT, tau=tau, tau_s=ts, S=S, S_req=E.S_REQ, n_rows=len(cs.rows),
    n_src=len(cs.sources), tau_wrong=tau_wrong, d_wrong=d_wrong, d_strength=E.d_strength, S_long=repr(S)[:12])
