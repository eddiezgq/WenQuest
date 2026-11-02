"""算例 57.3.1、57.3.2：基准不重合时的工序尺寸（第 53 章的尺寸链用到 SH-101）。
57.3.1 轴向：SH-101 的工艺尺寸跟踪图（std/SH-101_process.yaml 的 tolerance_chart，hub/tolerance.py chart_from_plan）——图纸轴向尺寸
        能否保证、每次车端面和轴肩的余量；比较齿轮左端面从左端面编程（81 ± 0.05）与从轴承定位轴肩编程（8 ± 0.05，现行）；
57.3.2 键槽深：铣键槽时控制槽底到精车外圆下母线的尺寸 H，渗碳淬火、磨削后得 d − t₁ = 16.5（0/−0.1），按极值法反求 H。画图 57.3.1、57.3.2。"""
import copy

import _mfg as M
from bookout import T, figure, out, style

TL = M.tol()
P = M.plan101()
tc = P["tolerance_chart"]
cur = TL.chart_from_plan(tc)
assert all(d["ok"] for d in cur["drawing"]) and all(a["ok"] for a in cur["allowances"])
alt_tc = copy.deepcopy(tc)
c = next(c for c in alt_tc["cuts"] if c["seq"] == 30.24)
c.update(ref="L", nominal=81, label="工序 30 从左端面编程车齿轮左端面（基准不重合）")
alt = TL.chart_from_plan(alt_tc)
d8 = lambda r: next(d for d in r["drawing"] if d["a"] == "S3" and d["b"] == "S4")  # noqa: E731
d30 = lambda r: next(d for d in r["drawing"] if d["a"] == "S4" and d["b"] == "S5")  # noqa: E731

# ---- 图 57.3.1：跟踪图
xs = {"L": 0, "S1": 36, "S2": 56, "S3": 73, "S4": 81, "S5": 111, "S6": 119, "R": 136}
plt = style()
rows = len(tc["cuts"]) + 1 + len(tc["drawing"])
fig, ax = plt.subplots(figsize=(7.6, 0.25 * rows + 1.2))
y = rows
for k, x in xs.items():
    ax.plot([x, x], [0.4, rows + 0.6], color=M.MUTED, lw=0.5)
    ax.text(x, rows + 0.8, k, ha="center", fontsize=7)
allow = {a["seq"]: a for a in cur["allowances"]}
for c in tc["cuts"]:
    y -= 1
    xr, xsf = xs[c["ref"]], xs[c["surf"]]
    ax.plot(xr, y, "o", color=M.INK, ms=3)
    ax.annotate("", xy=(xsf, y), xytext=(xr, y), arrowprops=dict(arrowstyle="-|>", color=M.ACCENT, lw=0.9))
    ax.text(-30, y, f"{c['seq']}", fontsize=6.3, va="center")
    ax.text((xr + xsf) / 2, y + 0.18, f"{abs(c['nominal']):g}±{c['es']:g}", fontsize=5.8, ha="center", color=M.ACCENT)
    a = allow.get(c["seq"])
    if a:
        ax.text(146, y, f"{a['min']:.2f}–{a['max']:.2f}", fontsize=6.1, va="center", color=M.INK if a["ok"] else M.RED)
y -= 1
ax.plot([-32, 175], [y + 0.5, y + 0.5], color=M.INK, lw=0.6)
for d in cur["drawing"]:
    y -= 1
    ax.annotate("", xy=(xs[d["b"]], y), xytext=(xs[d["a"]], y), arrowprops=dict(arrowstyle="<|-|>", color=M.RED, lw=1.0))
    ax.text((xs[d["a"]] + xs[d["b"]]) / 2, y + 0.18, f"{d['nominal']:g}±{d['es']:g} → {d['result'].text(2)}", fontsize=5.8, ha="center", color=M.RED)
    ax.text(146, y, T("满足", "OK") if d["ok"] else T("不满足", "fails"), fontsize=6.1, va="center")
ax.text(-30, rows + 0.8, T("工步", "cut"), fontsize=6.8)
ax.text(146, rows + 0.8, T("余量 / 结论", "allowance / result"), fontsize=6.8)
ax.text(-30, y - 0.2, T("图纸尺寸", "drawing"), fontsize=6.3, va="center")
ax.set_xlim(-32, 175); ax.set_ylim(y - 0.8, rows + 1.2); ax.axis("off")
figure(fig, "fig57_3_1")

# ---- 57.3.2 键槽深的尺寸链（极值法）
ch = P["chains"][0]
links = [M.link(l["name"], l["nominal"], l["es"], l["ei"], l["sense"]) for l in ch["links"]]
res = TL.extreme(links)
c5 = next(c for c in P["characteristics"] if c["id"] == "C5")
assert res.max <= c5["nominal"] + c5["es"] + 1e-9 and res.min >= c5["nominal"] + c5["ei"] - 1e-9
H = ch["links"][0]
r30, r70 = ch["links"][1], ch["links"][2]
H_es = c5["es"] + r30["ei"] - r70["es"]                     # 封闭环上偏差 = H 上偏差 − r30 下偏差 + r70 上偏差 → 反求 H 上偏差
H_ei = c5["ei"] + r30["es"] - r70["ei"]

fig, ax = plt.subplots(figsize=(4.2, 2.2))
items = [(T("H 槽底到精车外圆下母线（工序 50）", "H (op 50)"), H["nominal"], H["es"], H["ei"], M.ACCENT, "+"),
         (T("精车轴伸半径 Ø20.4/2（工序 30）", "semi radius (op 30)"), r30["nominal"], r30["es"], r30["ei"], M.MUTED, "−"),
         (T("磨削轴伸半径 Ø20 j6/2（工序 70）", "ground radius (op 70)"), r70["nominal"], r70["es"], r70["ei"], M.WARM, "+"),
         (T("d − t₁ 封闭环（图纸 16.5 0/−0.1）", "d − t₁ closing link"), c5["nominal"], res.max - c5["nominal"], res.min - c5["nominal"], M.RED, "=")]
for i, (lab, nom, es, ei, col, sg) in enumerate(items):
    yy = 3 - i
    ax.barh(yy, (es - ei) * 1000, left=ei * 1000, color=col, height=0.5)
    ax.text(-118, yy, f"{sg} {lab}", va="center", ha="right", fontsize=6.8)
    ax.text(max(es, 0) * 1000 + 4, yy, f"{nom:g}（{es:+.4g}/{ei:+.4g}）".replace("-", "−"), va="center", fontsize=6.5)
ax.axvline(0, color=M.INK, lw=0.6)
ax.set_xlim(-115, 75); ax.set_yticks([]); ax.set_xlabel(T("偏差 / µm", "deviation / µm"))
ax.spines["left"].set_visible(False)
figure(fig, "fig57_3_2")

out(d8_cur=d8(cur)["result"].es, d8_alt=d8(alt)["result"].es, d8_alt_ok=d8(alt)["ok"], d30_cur=d30(cur)["result"].es,
    d30_alt=d30(alt)["result"].es, amin=min(a["min"] for a in cur["allowances"]), amax=max(a["max"] for a in cur["allowances"]),
    n_cuts=len(tc["cuts"]), n_draw=len(tc["drawing"]), H=H["nominal"], H_es=H_es, H_ei=H_ei, r30=r30["nominal"], r70=r70["nominal"],
    res_es=res.max - c5["nominal"], res_ei=res.min - c5["nominal"], chain_T=res.max - res.min)
