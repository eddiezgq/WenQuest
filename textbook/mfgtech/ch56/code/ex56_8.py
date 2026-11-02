"""算例 56.8.1：工序分散与工序集中。SH-101 按本章路线在数字工厂现有设备上分散加工（方案 A，std/SH-101_route.yaml），
与把粗车、精车、铣键槽集中到一台车铣复合中心上（方案 B；车铣复合中心的工时、准备时间和小时费率是示意值）比较：
各工作中心的负荷、瓶颈、需求节拍、单件成本、装夹次数。工作中心的费率与台数取工厂数据（factory/data.py WORKSTATIONS）。画图 56.8.2。"""
import copy

import _mfg as M
from bookout import T, figure, out, style

R = M.route()
P = M.part101()
A = M.route101()["operations"]
TM = "车铣复合中心 TM-01"
R.EXTRA_WS[TM] = (95.0, 1)                      # 小时费率 95 元/h、1 台（示意）
B = [copy.deepcopy(o) for o in A if o["seq"] not in (20, 30, 50)]
B.insert(1, {"seq": 20, "operation": "车铣复合 Turn-mill", "workstation": TM, "minutes": 27.0, "setup_min": 45})
batch = P["batch"]
ra, rb = R.route_cost(A, batch), R.route_cost(B, batch)
# 需求节拍：年产 6000，每年 250 天、两班、每班 480 min，设备综合效率 0.85（示意）
avail = 250 * 2 * 480 * 0.85
takt = avail / P["annual_volume"]
setups_A = 1 + 2 + 1 + 1 + 1 + 1          # 粗车调头 2 次装夹、精车 1、滚齿 1、铣键槽 1、磨 1（锯、热处理不计）
setups_B = 1 + 1 + 1 + 1 + 0              # 车铣复合一次装夹（副主轴接料调头，算 1），滚齿 1、磨 1
moves_A, moves_B = len(A) - 1, len(B) - 1

plt = style()
fig, ax = plt.subplots(figsize=(6.6, 2.8))
names = list(dict.fromkeys(list(ra["load"]) + list(rb["load"])))
names = [n for n in names if "检验" not in n and "锯" not in n]
import numpy as np
x = np.arange(len(names))
la = [ra["load"].get(n, 0) for n in names]
lb = [rb["load"].get(n, 0) for n in names]
ax.bar(x - 0.2, la, 0.38, color=M.ACCENT, label=T("A 工序分散（现有设备）", "A dispersed (present machines)"))
ax.bar(x + 0.2, lb, 0.38, color=M.WARM, label=T("B 工序集中（车铣复合）", "B concentrated (turn-mill)"))
ax.axhline(takt, color=M.RED, ls="--", lw=0.9)
ax.text(len(names) - 0.6, takt - 2.6, T(f"需求节拍 {takt:.0f} min/件", f"takt {takt:.0f} min"), fontsize=7.5, color=M.RED, ha="right")
ax.set_xticks(x); ax.set_xticklabels([n.split(" ")[0] for n in names], fontsize=7)
ax.set_ylabel(T("每件占用工作中心的时间 / min", "minutes per part per work centre")); ax.grid(lw=0.3, alpha=0.5, axis="y")
ax.legend(fontsize=7, loc="upper left")
figure(fig, "fig56_8_2")

out(capA=avail / ra["takt"], capB=avail / rb["takt"], costA=ra["cost"], costB=rb["cost"], neckA=ra["bottleneck"].split(" ")[0], neckB=rb["bottleneck"].split(" ")[0], taktA=ra["takt"],
    taktB=rb["takt"], takt=takt, tA=ra["t_total"], tB=rb["t_total"], setups_A=setups_A, setups_B=setups_B, moves_A=moves_A, moves_B=moves_B,
    tm_rate=R.EXTRA_WS[TM][0], cnc_rate=R.rate_per_hour("数控车床 CNC-L01")[0], n_cnc=R.rate_per_hour("数控车床 CNC-L01")[1],
    tm_min=27.0, ops_A=len(A), ops_B=len(B), batch=batch)
