"""算例 54.6.1–54.6.4：刀具磨损、残余应力与测量误差（hub/accuracy.py）。
54.6.1：硬质合金车刀精车 SH-301 齿轮位 Ø40.3 × 60（进给 0.15），每件的切削路程与尺寸磨损（cutting_length_m、radial_wear；
        初期磨损 3 µm、正常磨损 8 µm/1000 m 为示例值，以刀具厂样本或实测为准）；
54.6.2：工序 60 砂轮的尺寸磨损：仿真车间正常状态 60 件、每 10 件修整，从数据求每件的漂移（sequence 的锯齿斜率）与允许的修整间隔（compensation_interval）；
54.6.3：铣键槽后残余应力重新平衡引起的弯曲（layer_moment、bow_from_moment；去掉的材料里平均残余应力 80 MPa 为示例值）；
54.6.4：阿贝误差——游标卡尺量爪离尺身 30 mm、尺框倾斜 0.0002 rad（abbe_error）；杠杆千分尺 G04 的测量误差占公差的比例。
画图 54.6.1（刀具磨损曲线）、54.6.2（砂轮磨损的锯齿）、54.6.3（补偿间隔）、54.6.5（键槽引起的弯曲）。"""
import math

import _mfg as M
from bookout import T, figure, out, style

A = M.acc()
p = M.plan()
# 54.6.1
Lm = A.cutting_length_m(40.3, 60.0, 0.15)
w1 = A.radial_wear(Lm, 8.0, 3.0)
w50 = A.radial_wear(50 * Lm, 8.0, 3.0)
d_part = 2 * 8.0 * Lm / 1000 / 1000                 # 正常磨损阶段每件使直径增大（mm）
ci_t = A.compensation_interval(0.039, 0.003, d_part)   # 精车 Ø40.3（0/−0.039），精车的 σ 取 3 µm（示例值）
# 54.6.2
s = M.shift(n_ok=60, n_bad=0)
v = s["values"]["bearing_seat_d35"]
q = A.sequence(v, resets=s["resets"], sigma=0.0012)
assert q["label"] == "drift_saw"
drift = q["saw_slope"]
ci = A.compensation_interval(0.016, 0.0012, drift)
ci_model = A.compensation_interval(0.016, 0.0012, 0.0125 / 30)
dress = next(t for t in p["tool_list"] if t["id"] == "T05")["life"]
# 54.6.3
k = p["part"]["keyway"]
x1 = 52.0 + float(k["offset_mm"])
x2 = x1 + float(k["L"])
b, t = float(k["b"]), float(k["t"])
area = b * t
e = 20.0 - t / 2
sig = 80.0
Mres = A.layer_moment(sig, area, e)
I = math.pi * 40.0 ** 4 / 64
bow = A.bow_from_moment(Mres, 167.0, x1, x2, A.E_STEEL, I)
def y_at(x):
    xs = bow["x_list"]
    i = min(range(len(xs)), key=lambda j: abs(xs[j] - x))
    return abs(bow["y"][i])


run_l, run_r = 2 * y_at(46.0), 2 * y_at(124.5)
# 54.6.4
abbe = A.abbe_error(30.0, 0.0002)
ratio_g04 = 0.002 / 0.016

plt = style()
# ---- 图 54.6.1：刀具磨损曲线（示意）
fig, ax = plt.subplots(figsize=(5.6, 3.0))
ls = [i * 0.05 for i in range(0, 201)]
def nb(x):
    return 3 * (1 - math.exp(-x / 0.3)) + 8 * x + (0 if x < 7.5 else 40 * (x - 7.5) ** 2)
ax.plot(ls, [nb(x) for x in ls], color=M.RED)
ax.axvspan(0, 0.9, color="#f6e7e5"); ax.axvspan(7.5, 10, color="#f6e7e5")
ax.text(0.45, 75, T("初期\n磨损", "initial"), fontsize=7.5, ha="center")
ax.text(4.2, 75, T("正常磨损：NB 随切削路程近似线性增加", "normal wear: NB grows about linearly"), fontsize=7.5, ha="center")
ax.text(8.75, 75, T("急剧\n磨损", "rapid"), fontsize=7.5, ha="center")
ax.set_xlabel(T("切削路程 / km", "cutting distance / km")); ax.set_ylabel(T("尺寸磨损 NB / µm", "dimensional wear NB / µm"))
ax.set_xlim(0, 10); ax.set_ylim(0, 90); ax.grid(lw=0.3, alpha=0.5)
figure(fig, "fig54_6_1")

# ---- 图 54.6.2：砂轮磨损的锯齿（仿真车间正常状态）
fig, ax = plt.subplots(figsize=(6.4, 3.0))
xs = list(range(1, 61))
ax.plot(xs, v, "o-", ms=3, lw=0.7, color=M.ACCENT, label=T("左轴承位测得值", "left bearing seat"))
cuts = [0] + s["resets"] + [60]
for a0, a1 in zip(cuts, cuts[1:]):
    seg = v[a0:a1]
    m = sum(seg) / len(seg)
    c = (len(seg) - 1) / 2
    ax.plot([a0 + 1, a1], [m - drift * c, m + drift * c], color=M.RED, lw=1.4)
for r in s["resets"]:
    ax.axvline(r + 0.5, color=M.MUTED, ls=":", lw=0.7)
for y in (35.002, 35.018):
    ax.axhline(y, color=M.RED, ls="--", lw=0.7)
ax.text(1, 35.0165, T(f"红线：各段共同的斜率 {drift * 1000:.2f} µm/件（点线处修整砂轮）", f"red: common slope {drift * 1000:.2f} µm per part (dotted: dressing)"), fontsize=7.5, color=M.RED)
ax.set_xlabel(T("零件序号", "part number")); ax.set_ylabel(T("直径 / mm", "diameter / mm")); ax.set_ylim(35.0, 35.02); ax.grid(lw=0.3, alpha=0.5)
figure(fig, "fig54_6_2")

# ---- 图 54.6.3：补偿（修整）间隔：尺寸中心在公差带里从下往上走
fig, ax = plt.subplots(figsize=(5.8, 3.0))
T6, sg = 16.0, 1.2
start = ci["start_above_lsl"] * 1000
n = ci["n_max"]
ax.axhspan(0, T6, color="#eef3f8")
ax.plot([0, n], [start, start + n * drift * 1000], color=M.RED, lw=1.6, label=T("尺寸中心", "size centre"))
ax.fill_between([0, n], [start - 3 * sg, start - 3 * sg + n * drift * 1000], [start + 3 * sg, start + 3 * sg + n * drift * 1000], color=M.RED, alpha=0.15, label="±3σ")
ax.axhline(0, color=M.INK, lw=0.8); ax.axhline(T6, color=M.INK, lw=0.8)
ax.text(n + 0.3, T6 - 1.5, T(f"n = {n} 件时到上限", f"reaches the upper limit at n = {n}"), fontsize=7.5)
ax.axvline(10, color=M.GREEN, ls="--", lw=0.8)
ax.text(10.3, 1.0, T("工艺规程：每 10 件修整", "plan: dress every 10"), fontsize=7.5, color=M.GREEN)
ax.set_xlabel(T("修整后的件数", "parts since dressing")); ax.set_ylabel(T("在公差带中的位置 / µm（下限为 0）", "position in the tolerance / µm"))
ax.set_xlim(0, n + 6); ax.set_ylim(-2, 19); ax.legend(fontsize=7.5, loc="upper left"); ax.grid(lw=0.3, alpha=0.5)
figure(fig, "fig54_6_3")

# ---- 图 54.6.5：铣键槽后的弯曲
fig, ax = plt.subplots(figsize=(5.8, 2.8))
xl, yl = bow["x_list"], bow["y"]
ax.plot(xl, [abs(y) * 1000 for y in yl], color=M.RED)
ax.axvspan(x1, x2, color="#f6e7e5")
ax.text((x1 + x2) / 2, 0.2 * max(abs(y) for y in yl) * 1000, T("键槽段", "keyway"), ha="center", fontsize=7.5)
ax.set_xlabel(T("距左端 / mm", "from the left end / mm")); ax.set_ylabel(T("挠度（向键槽一侧）/ µm", "deflection (toward the keyway) / µm")); ax.grid(lw=0.3, alpha=0.5)
figure(fig, "fig54_6_5")

out(d_part_um=d_part * 1000, n_turn=ci_t["n_max"], Lm=Lm, w1_um=w1 * 1000, w50_um=w50 * 1000, d50_um=2 * w50 * 1000, drift_um=drift * 1000, n_max=ci["n_max"], n_max_model=ci_model["n_max"],
    room_um=ci["room"] * 1000, dress=dress, x1=x1, x2=x2, area=area, e=e, sig=sig, M=Mres, bow_um=bow["max"] * 1000, bow_x=bow["x"],
    runout_um=bow["runout"] * 1000, run_l_um=run_l * 1000, run_r_um=run_r * 1000, abbe_um=abbe * 1000, ratio_g04=ratio_g04)
