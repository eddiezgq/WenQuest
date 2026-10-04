"""53.7 节：工艺尺寸跟踪图。算例 53.7.1 SH-301 轴向尺寸的跟踪图：从工艺规程的 tolerance_chart 建图，
求图纸尺寸与每次加工的余量（图 53.7.1）；比较“初稿”（工序 40 总长 ±0.3、轴肩粗车余量 0.5）与现行方案；
用与实验 53.7 相同的简化公式核对跟踪图程序。"""
import copy

import _mfg as M
from bookout import T, figure, out, style

TL = M.tol()
p = M.plan()
tc = p["tolerance_chart"]
cur = TL.chart_from_plan(tc)
assert all(d["ok"] for d in cur["drawing"]) and all(a["ok"] for a in cur["allowances"])


def scenario(total40=0.2, allow=0.8):
    t = copy.deepcopy(tc)
    for c in t["cuts"]:
        if c["seq"] == 40.3:
            c["es"], c["ei"] = total40, -total40
        if str(c["seq"]).startswith("20.") and c["surf"] in ("S1", "S2", "S3", "S4"):
            final = {"S1": 40, "S2": 52, "S3": 112, "S4": 137}[c["surf"]]
            # 朝左的轴肩（S1、S2）粗车位置在终值左边，朝右的（S3、S4）在右边；工序尺寸从 L（−0.5）或 R（167.5）量起
            x = final - allow if c["surf"] in ("S1", "S2") else final + allow
            c["nominal"] = x + 0.5 if c["ref"] == "L" else x - 167.5
    return TL.chart_from_plan(t)


draft = scenario(0.3, 0.5)
fix1 = scenario(0.2, 0.5)
d60 = lambda r: next(d for d in r["drawing"] if d["nominal"] == 60)  # noqa: E731
amin = lambda r: min(a["min"] for a in r["allowances"] if a["surface"] in ("S1", "S2", "S3", "S4"))  # noqa: E731
worst = min(draft["allowances"], key=lambda a: a["min"])

# 与实验 53.7 相同的简化公式（工序 40 各刀的公差记 t40L 总长、tfs 精车轴肩、t402 车右端面；工序 20 记 t204 总长、trs 粗车轴肩）
cuts = {c["seq"]: c for c in tc["cuts"]}
t40L, tfs, t402, t204, trs = cuts[40.3]["es"], cuts[40.31]["es"], cuts[40.2]["es"], cuts[20.4]["es"], cuts[20.3]["es"]
f60 = tfs + t40L + tfs
fS2 = trs + t402 + t40L + tfs
fS3 = trs + t204 + t402 + tfs
assert abs(d60(cur)["result"].es - f60) < 1e-9
aS2 = next(a for a in cur["allowances"] if a["surface"] == "S2")
aS3 = next(a for a in cur["allowances"] if a["surface"] == "S3")
assert abs((aS2["max"] - aS2["min"]) / 2 - fS2) < 1e-9 and abs((aS3["max"] - aS3["min"]) / 2 - fS3) < 1e-9

# 图 53.7.1：跟踪图
names = tc["surfaces"]
xs = {"L": 0, "S1": 40, "S2": 52, "S3": 112, "S4": 137, "R": 167}
plt = style()
rows = len(tc["cuts"]) + 1 + len(tc["drawing"])
fig, ax = plt.subplots(figsize=(7.6, 0.27 * rows + 1.2))
y = rows
for k, x in xs.items():
    ax.plot([x, x], [0.4, rows + 0.6], color=M.MUTED, lw=0.5)
    ax.text(x, rows + 0.8, k, ha="center", fontsize=7.5)
allow = {a["seq"]: a for a in cur["allowances"]}
for c in tc["cuts"]:
    y -= 1
    xr, xsf = xs[c["ref"]], xs[c["surf"]]
    ax.plot(xr, y, "o", color=M.INK, ms=3)
    ax.annotate("", xy=(xsf, y), xytext=(xr, y), arrowprops=dict(arrowstyle="-|>", color=M.ACCENT, lw=0.9))
    ax.text(-38, y, f"{c['seq']}", fontsize=6.5, va="center")
    ax.text((xr + xsf) / 2, y + 0.18, f"{abs(c['nominal']):g}±{c['es']:g}", fontsize=6, ha="center", color=M.ACCENT)
    a = allow.get(c["seq"])
    if a:
        ax.text(182, y, f"{a['min']:.2f}–{a['max']:.2f}", fontsize=6.3, va="center", color=M.INK if a["ok"] else M.RED)
y -= 1
ax.plot([-40, 210], [y + 0.5, y + 0.5], color=M.INK, lw=0.6)
for d in cur["drawing"]:
    y -= 1
    ax.annotate("", xy=(xs[d["b"]], y), xytext=(xs[d["a"]], y), arrowprops=dict(arrowstyle="<|-|>", color=M.RED, lw=1.0))
    ax.text((xs[d["a"]] + xs[d["b"]]) / 2, y + 0.18, f"{d['nominal']:g}±{d['es']:g}  → {d['result'].text(2)}", fontsize=6, ha="center", color=M.RED)
    ax.text(182, y, T("满足", "OK") if d["ok"] else T("不满足", "fails"), fontsize=6.3, va="center")
ax.text(-38, rows + 0.8, T("工步", "cut"), fontsize=7)
ax.text(182, rows + 0.8, T("余量 / 结论", "allowance / result"), fontsize=7)
ax.text(-38, y - 0.2, T("图纸尺寸", "drawing"), fontsize=6.5, va="center")
ax.set_xlim(-40, 210); ax.set_ylim(y - 0.8, rows + 1.2); ax.axis("off")
figure(fig, "fig53_7_1")

# 直径方向：齿轮位 粗车（工序 20）→ 精车（工序 40）→ 磨削（工序 60）的单边余量
def gear(seq):
    f = next(x for x in M.op(p, seq)["features"] if x["name"] == "齿轮位")
    return f["size_mm"] + f["ei_mm"], f["size_mm"] + f["es_mm"]


(r_lo, r_hi), (f_lo, f_hi), (g_lo, g_hi) = gear(20), gear(40), gear(60)
z1_min, z1_max = (r_lo - f_hi) / 2, (r_hi - f_lo) / 2
z2_min, z2_max = (f_lo - g_hi) / 2, (f_hi - g_lo) / 2
out(z1_min=z1_min, z1_max=z1_max, z2_min=z2_min, z2_max=z2_max, n_cuts=len(tc["cuts"]), n_draw=len(tc["drawing"]), d60_draft=d60(draft)["result"].es, draft_amin=amin(draft),
    draft_worst=names[worst["surface"]], draft_worst_seq=worst["seq"], fix1_60=d60(fix1)["result"].es, fix1_amin=amin(fix1),
    cur_60=d60(cur)["result"].es, cur_amin=amin(cur), aS2_min=aS2["min"], aS2_max=aS2["max"], aS3_min=aS3["min"], fS2=fS2, f60=f60,
    n_versions=len(cur["chart"].edges))

# 实验 53.7 的简化公式与上面核对过的公式一致
from pathlib import Path  # noqa: E402
lab = (Path(__file__).resolve().parents[1] / "lab" / "lab53_7.js").read_text(encoding="utf-8")
for frag in ("(p) => 2 * p.tfs + p.t40L", "p.trs + p.t402 + p.t40L + p.tfs", "p.trs + p.t204 + p.t402 + p.tfs", "p.t204 + p.t402", "p.t402 + p.t40L"):
    assert frag in lab, f"实验 53.7 缺少公式 {frag}"
