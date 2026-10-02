"""50.8 节：工艺方案的技术经济分析（算例 50.8.1）——方案 A 磨削、方案 B 精细车代替磨削：单件工艺成本、年度工艺成本、临界产量，
以及方案 B 对瓶颈的影响；图 50.8.1 单件工艺成本随年产量的变化。

工作中心费率取自数字工厂（教学示意值，美元/小时）；方案 B 的精细车工时、刀片费用与年固定费用为示意值。
"""
import _mfg as M
from bookout import T, figure, out, style

p = M.plan()
# 实验 50.8 里抄的费率与工时要与工厂数据一致（实验页不能读文件）
import json, re
from pathlib import Path
js = (Path(__file__).resolve().parents[1] / "lab" / "lab50_8.js").read_text(encoding="utf-8")
rates = json.loads(re.sub(r"(\w+):", r'"\1":', re.search(r"const RATE50 = (\{[^}]*\});", js).group(1)))
key = {"saw": "带锯床 SAW-01", "cnc": "数控车床 CNC-L01", "ht": "热处理炉 HT-01", "key": "键槽铣床 KEY-01", "grd": "外圆磨床 GRD-01", "qc": "检验站 QC-01"}
assert all(rates[k] == M.rate(w) for k, w in key.items())
route = json.loads(re.search(r"const ROUTE50 = (\[.*?\]);", js).group(1).replace("[\"", "[\"").replace("'", '"'))
assert [(key[w], m) for w, m in route] == [(o["workstation"], o["minutes"]) for o in p["operations"]]
V_A = sum(o["minutes"] * M.rate(o["workstation"]) / 60 for o in p["operations"])     # 方案 A：现行工艺（不含材料）
grind = next(o for o in p["operations"] if o["operation"].startswith("磨外圆"))
t_fine, insert = 8.0, 0.60                  # 方案 B：精细车 8 min/件（CNC-L01），刀片与刀具费 0.60 美元/件（示意）
F_B = 6000.0                                # 方案 B 每年多出的固定费用：在机测头、精密刀具管理与标定（示意）
V_B = V_A - grind["minutes"] * M.rate(grind["workstation"]) / 60 + t_fine * M.rate("数控车床 CNC-L01") / 60 + insert
N_c = F_B / (V_A - V_B)
cnc_A = sum(o["minutes"] for o in p["operations"] if o["workstation"] == "数控车床 CNC-L01") / M.F.WORKSTATIONS["数控车床 CNC-L01"][0]
cnc_B = cnc_A + t_fine / M.F.WORKSTATIONS["数控车床 CNC-L01"][0]
out(V_A=V_A, V_B=V_B, dV=V_A - V_B, F_B=F_B, N_c=N_c, t_fine=t_fine, insert=insert, grind_cost=grind["minutes"] * M.rate(grind["workstation"]) / 60,
    rate_cnc=M.rate("数控车床 CNC-L01"), rate_grd=M.rate(grind["workstation"]), cnc_A=cnc_A, cnc_B=cnc_B,
    shift_A=int(480 // cnc_A), shift_B=int(480 // cnc_B), mat=dict(M.F.BOMS["SH-301"][1])["RM-45-D50"] * M.price("RM-45-D50"))

plt = style()
fig, ax = plt.subplots(figsize=(6.0, 3.0))
Ns = [200 + 20 * k for k in range(241)]
ax.plot(Ns, [V_A for n in Ns], color="#2f8f5b", lw=2, label=T("方案 A：磨削", "A: grinding"))
ax.plot(Ns, [V_B + F_B / n for n in Ns], color="#3a7dc9", lw=2, label=T("方案 B：精细车", "B: fine turning"))
ax.axvline(N_c, color=M.MUTED, ls="--", lw=1)
ax.text(N_c + 80, V_A + 6, T(f"临界产量 ≈ {N_c:.0f} 件/年", f"break-even ≈ {N_c:.0f} pcs/yr"), fontsize=9, color=M.INK)
ax.set_ylim(45, 85)
ax.set_xlabel(T("年产量 N / 件", "annual volume N / pcs"), fontsize=9.5)
ax.set_ylabel(T("单件工艺成本 / 美元", "process cost per piece / USD"), fontsize=9.5)
ax.legend(fontsize=8.5, frameon=False)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)
figure(fig, "fig50_8_1")
