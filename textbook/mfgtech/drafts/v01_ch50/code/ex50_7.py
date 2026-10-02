"""50.7 节：时间定额（算例 50.7.1 粗车的基本时间与单件时间组成；算例 50.7.2 瓶颈与班产量）；图 50.7.1 各工序单件工时的组成。

基本时间按切削用量算（式 50.7.3）：外圆走刀之外，车端面、钻中心孔也是切削，同样计入基本时间；辅助时间等其他部分取数字工厂企业工时标准 WQ-TS-01 的分项（教学示意值）。
"""
import math

import _mfg as M
from bookout import T, figure, out, style
from hub import process

p = M.plan()
ops = {o["operation"].split(" ")[0]: o for o in p["operations"]}
r, f = ops["粗车"], ops["精车"]
n_r = 1000 * r["cut"]["vc_m_min"] / (math.pi * r["cut"]["d_mm"])
tb_od = process.basic_time_min(r["cut"])          # 外圆：4 次走刀，L 含切入切出
tb_face = 2 * (50 / 2 + 2) / (n_r * 0.2)          # 车两端面：径向走刀 25 + 2 mm，f = 0.2 mm/r
n_cd = 1000 * 20 / (math.pi * 3.15)               # 钻两中心孔：A3.15 中心钻，v_c = 20 m/min
tb_cd = 2 * 7 / (n_cd * 0.05)                     # 每孔深约 7 mm，f = 0.05 mm/r
tb_r = tb_od + tb_face + tb_cd
n_f = 1000 * f["cut"]["vc_m_min"] / (math.pi * f["cut"]["d_mm"])
tb_f = process.basic_time_min(f["cut"])
# 企业工时标准 WQ-TS-01（教学示意值，min/件）：粗车工序的辅助时间分项
ta_items = {"装卸工件、调头（2 次）": 3.0, "对刀、换刀（3 把刀）": 3.0, "试切与测量": 3.5, "快速进退刀、换挡、主轴启停": 3.1}
ta = sum(ta_items.values())
ts_rate = 0.08                                   # 布置工作地与休息生理时间：占作业时间的 8%
tpz, N = 30.0, 50                                # 准备与终结时间（每批）、批量
t_op = tb_r + ta
ts = ts_rate * t_op
t_unit = t_op + ts + tpz / N
assert abs(t_unit - r["minutes"]) < 0.6          # 与工艺规程的 18 min 一致
share_b = tb_r / r["minutes"]
# 瓶颈：各工作中心每件占用的时间 ÷ 台数
load = {}
for o in p["operations"]:
    ws = o["workstation"]
    n_ws = 1 if ws == "热处理炉 HT-01" else M.F.WORKSTATIONS[ws][0]   # 热处理炉的“台数”20 是一炉装的件数，工艺规程里的 12 min 已是分摊到每件的炉时
    load[ws] = load.get(ws, 0) + o["minutes"] / n_ws
bott = max(load, key=load.get)
shift_min = 8 * 60
out(n_r=n_r, tb_r=tb_r, tb_od=tb_od, tb_face=tb_face, tb_cd=tb_cd, n_cd=n_cd, n_f=n_f, tb_f=tb_f, ta=ta, ts=ts, tpz=tpz, N=N, t_unit=t_unit, share_b_pct=100 * share_b,
    bott=bott.split(" ")[-1], bott_min=load[bott], per_shift=math.floor(shift_min / load[bott]), grd_min=load["外圆磨床 GRD-01"],
    ta_list="；".join(f"{k} {v:g}" for k, v in ta_items.items()))

# ---- 图 50.7.1：各工序单件工时（粗车、精车分出基本时间）
plt = style()
fig, ax = plt.subplots(figsize=(6.6, 2.8))
names, base, rest = [], [], []
for o in p["operations"]:
    zh, en = o["operation"].split(" ", 1)
    names.append(T(zh, en.replace(" ", "\n")))
    b = (tb_r if o["operation"].startswith("粗车") else process.basic_time_min(o["cut"])) if o.get("cut") else 0
    base.append(b); rest.append(o["minutes"] - b)
x = range(len(names))
ax.bar(x, base, color="#3a7dc9", label=T("基本时间（按切削用量算）", "machining time (from cutting data)"))
ax.bar(x, rest, bottom=base, color="#c9d2d9", label=T("其余（辅助、布置、准备分摊）", "other (handling, allowances, setup share)"))
for i, (b, r_) in enumerate(zip(base, rest)):
    ax.text(i, b + r_ + 0.4, f"{b + r_:g}", ha="center", fontsize=8.5, color=M.INK)
ax.set_xticks(list(x)); ax.set_xticklabels(names, fontsize=8.5)
ax.set_ylabel(T("min / 件", "min / piece"), fontsize=9)
ax.legend(fontsize=8, frameon=False, loc="upper right")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig50_7_1")
