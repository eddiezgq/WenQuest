"""算例 57.7.1、57.7.2：工艺方案的技术经济分析。
年产量增加到 2 万件，SH-101 的瓶颈是外圆磨床（57.6 节）。两个方案：
  A 再买一台外圆磨床（投资 K_A，示意值），工艺不变；
  B 密封轴颈和轴伸改在数控车床上用 CBN 刀片硬车（淬硬后精车），磨床只磨两处轴承位；投资 K_B 是 CBN 刀具和在机测头（示意值）。
57.7.1 工艺成本：可变费用 V（材料、机床与人工按工作中心小时费率、刀具）与不变费用 S（折旧、维护，按年），单件成本 C = V + S/N（式 57.7.1–57.7.2）；
57.7.2 两方案的临界年产量与投资回收期 τ = ΔK/ΔE（式 57.7.3）。数控车床、磨床等的费率取工厂数据，硬车工时、CBN 刀片费、投资是示意值。画图 57.7.1。"""
import copy

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

RT = M.route()
P = M.plan101()
N = 20000
batch = 200
mat = 2.4 * 3.15                                    # 毛坯：Ø60 圆钢 3.15 kg × 2.4 元/kg（同第 56 章）
ops_A = copy.deepcopy(P["operations"])
ops_B = copy.deepcopy(P["operations"])
g = next(o for o in ops_B if o["seq"] == 70)
g["minutes"] = 10.0                                  # 只磨两处轴承位（示意：按磨削长度比例）
ops_B.insert(next(i for i, o in enumerate(ops_B) if o["seq"] == 70) + 1,
             {"seq": 75, "operation": "精车 Finish turning", "workstation": "数控车床 CNC-L01", "minutes": 4.0, "setup_min": 20})
cbn = 3.0                                           # CBN 刀片每件分摊（元，示意）
K_A, S_A = 350000.0, 45000.0                        # 第二台外圆磨床：投资、每年折旧与维护（10 年折旧 + 维护，示意）
K_B, S_B = 40000.0, 8000.0                          # CBN 刀具与在机测头：投资、每年折旧与维护（示意）
rA = RT.route_cost(ops_A, batch)
rB = RT.route_cost(ops_B, batch)
VA = rA["cost"] + mat
VB = rB["cost"] + mat + cbn
EA, EB = VA * N + S_A, VB * N + S_B
need = M.FE_MIN / N
loadA_grd = rA["load"]["外圆磨床 GRD-01"] / 2      # 两台磨床
loadB_grd = rB["load"]["外圆磨床 GRD-01"]
loadB_cnc = rB["load"]["数控车床 CNC-L01"]
Nc = (S_A - S_B) / (VB - VA) if VB != VA else None     # 年成本相等的年产量（只看工艺成本）
tau = (K_A - K_B) / (EA - EB) if EA != EB else None   # 投资回收期（年）：多投资的 A 每年省下的工艺成本来回收

plt = style()
fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 2.6), gridspec_kw={"width_ratios": [1.2, 1], "wspace": 0.35})
ns = np.linspace(5000, 40000, 200)
ax.plot(ns / 1000, VA + S_A / ns, color=M.ACCENT, lw=1.4, label=T("A 加一台磨床", "A second grinder"))
ax.plot(ns / 1000, VB + S_B / ns, color=M.WARM, lw=1.4, label=T("B 硬车密封轴颈、轴伸", "B hard turning"))
if Nc and Nc < 40000:
    ax.axvline(Nc / 1000, color=M.INK, ls=":", lw=0.8); ax.text(Nc / 1000 - 0.5, VA + S_A / 5000 * 0.9, T(f"临界 {Nc / 1000:.0f} 千件", f"break-even {Nc / 1000:.0f}k"), fontsize=7, ha="right")
ax.axvline(N / 1000, color=M.MUTED, ls="--", lw=0.8)
ax.set_xlabel(T("年产量 / 千件", "annual volume / 1000")); ax.set_ylabel(T("单件工艺成本 / 元", "unit cost / CNY")); ax.set_ylim(VA - 1, VB + S_B / 5000 + 6)
ax.legend(fontsize=7); ax.grid(lw=0.3, alpha=0.4)
ks = ["外圆磨床 GRD-01", "数控车床 CNC-L01", "滚齿机 HOB-01"]
w = 0.38
bx.bar([i - w / 2 for i in range(3)], [loadA_grd, rA["load"][ks[1]], rA["load"][ks[2]]], w, color=M.ACCENT, label="A")
bx.bar([i + w / 2 for i in range(3)], [loadB_grd, loadB_cnc, rB["load"][ks[2]]], w, color=M.WARM, label="B")
bx.axhline(need, color=M.RED, ls="--", lw=0.9); bx.text(2.4, need + 0.3, T(f"需求节拍 {need:.1f}", f"takt {need:.1f}"), fontsize=7, color=M.RED, ha="right")
bx.set_xticks(range(3)); bx.set_xticklabels([k.split(" ")[0] for k in ks], fontsize=7)
bx.set_ylabel(T("每件占用 / min", "min per part")); bx.legend(fontsize=7); bx.grid(lw=0.3, alpha=0.4, axis="y"); bx.set_ylim(0, 14)
figure(fig, "fig57_7_1")

out(N=N, batch=batch, mat=mat, VA=VA, VB=VB, S_A=S_A, S_B=S_B, K_A=K_A, K_B=K_B, EA=EA, EB=EB, dE=EA - EB, cbn=cbn,
    CA=VA + S_A / N, CB=VB + S_B / N, Nc=Nc, tau=tau, need=need, loadA_grd=loadA_grd, loadB_grd=loadB_grd, loadB_cnc=loadB_cnc,
    okA=loadA_grd <= need, okB=loadB_grd <= need and loadB_cnc <= need)
