"""算例 54.9.1、54.9.2：精度预算与误差补偿（hub/accuracy.py 的 budget；hub/process.py 的评审规则；数据来自仿真车间的误差模型）。
54.9.1：SH-301 工艺规程工序 60 登记的精度预算（轴承位直径 C1、径向圆跳动 C7）：系统误差相加、随机误差平方和开方，与公差比较；
        AI 工艺评审员对它的意见；把“每 10 件修整”改成不修整（一个砂轮寿命内的磨损）以后的预算；
54.9.2：三种控制方式各磨 60 件：(a) 按工艺规程每 10 件修整（开环）；(b) 加工后测量、逐件反馈补偿（每件按测得值与目标之差的一半修正横进给）；
        (c) 主动测量（磨削中在线测量，到尺寸停止进给，残留误差为测量仪的重复性与停止误差）。比较 Cpk。
画图 54.9.1（精度预算）、54.9.4（三种控制方式）。"""
import random
import statistics as st

import _mfg as M
from bookout import T, figure, out, style

A = M.acc()
SPC = M.spc()
ER = M.errs()
p = M.plan()
o60 = M.op(p, 60)
T_C1 = 0.016
acc = {a["char"]: a for a in o60["accuracy"]}
b1 = A.budget(acc["C1"]["items"], acc["C1"].get("T", T_C1))
b7 = A.budget(acc["C7"]["items"], acc["C7"]["T"])
from hub import process  # noqa: E402
rev = [f for f in process.review(p) if f["rule"] == "精度"]
import copy  # noqa: E402
p2 = copy.deepcopy(p)
o2 = M.op(p2, 60)
o2["accuracy"][0]["items"][1]["range"] = 0.0125
b1x = A.budget(o2["accuracy"][0]["items"], T_C1)
rev2 = [f for f in process.review(p2) if f["rule"] == "精度" and f["level"] == "error"]
assert len(rev) == 2 and all(f["level"] == "warning" for f in rev) and rev2

# 54.9.2
lo, hi, tgt = 35.002, 35.018, 35.010
s = M.shift(n_ok=60, n_bad=0, seeds=(590, 0))
open_ = s["values"]["bearing_seat_d35"]
rng = random.Random(591)
off, fb = 0.0, []
for i, x in enumerate(open_):
    y = x + off
    fb.append(y)
    off -= 0.5 * (y - tgt)                    # 逐件反馈：下一件的横进给按偏差的一半修正
act = [tgt + rng.gauss(0, 0.0004) + rng.gauss(0, 0.0003) for _ in range(60)]    # 主动测量：测量仪重复性 0.4 µm、停止误差 0.3 µm
caps = {k: SPC.capability(vv, lo, hi) for k, vv in (("open", open_), ("fb", fb), ("act", act))}

plt = style()
# ---- 图 54.9.4：三种控制方式
fig, axs = plt.subplots(1, 3, figsize=(7.8, 2.6), sharey=True)
for ax, (k, vv, ttl) in zip(axs, (("open", open_, T("(a) 每 10 件修整（开环）", "(a) dress every 10 (open loop)")),
                                  ("fb", fb, T("(b) 加工后测量、逐件反馈补偿", "(b) post-process feedback")),
                                  ("act", act, T("(c) 主动测量：到尺寸停止进给", "(c) in-process gauging")))):
    ax.plot(range(1, 61), [x * 1000 - 35000 for x in vv], "o-", ms=2, lw=0.6, color=M.ACCENT)
    for y in (lo, hi):
        ax.axhline(y * 1000 - 35000, color=M.RED, ls="--", lw=0.7)
    ax.axhline(tgt * 1000 - 35000, color=M.MUTED, lw=0.5)
    c = caps[k]
    ax.set_title(ttl, fontsize=7.8)
    ax.text(0.04, 0.05, f"Cpk = {c['Ppk']:.2f}", transform=ax.transAxes, fontsize=8, color=M.RED)
    ax.set_xlabel(T("零件序号", "part"), fontsize=7.5); ax.tick_params(labelsize=7)
axs[0].set_ylabel(T("直径 − 35 / µm", "diameter − 35 / µm"), fontsize=7.5)
figure(fig, "fig54_9_4")

# ---- 图 54.9.1：精度预算
fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.2), gridspec_kw={"width_ratios": [1.5, 1]})
for ax, (b, T_, ttl) in zip(axs, ((b1, T_C1, T("(a) 轴承位直径 Ø35 k6（公差 16 µm）", "(a) bearing seat Ø35 k6 (16 µm)")),
                                  (b7, acc["C7"]["T"], T("(b) 径向圆跳动（公差 12 µm）", "(b) radial runout (12 µm)")))):
    names = [i["name"].split("（")[0] for i in b["items"]]
    ys = list(range(len(names)))[::-1]
    ax.barh(ys, [i["range"] * 1000 for i in b["items"]], color=[M.WARM if i["kind"] == "sys" else M.ACCENT for i in b["items"]])
    ax.set_yticks(ys); ax.set_yticklabels(names, fontsize=6.8)
    ax.axvline(T_ * 1000, color=M.RED, ls="--", lw=0.9)
    ax.axvline(b["total"] * 1000, color=M.INK, lw=1.2)
    ax.text(b["total"] * 1000, len(names) - 0.4, T(f"合计 {b['total'] * 1000:.1f}", f"total {b['total'] * 1000:.1f}"), fontsize=7, ha="right")
    ax.text(T_ * 1000, -0.9, T("公差", "tol."), fontsize=7, color=M.RED, ha="center")
    ax.set_xlabel(T("误差范围 / µm（橙：系统误差，直接相加；蓝：随机误差，平方和开方）", "range / µm (orange: systematic; blue: random)") if ax is axs[0] else T("误差范围 / µm", "range / µm"), fontsize=7)
    ax.set_title(ttl, fontsize=8); ax.set_xlim(0, max(T_, b["total"]) * 1000 * 1.15); ax.tick_params(labelsize=7)
figure(fig, "fig54_9_1")

out(b1_sys=b1["sys"] * 1000, b1_rand=b1["rand"] * 1000, b1_total=b1["total"] * 1000, b1_share=b1["total"] / T_C1 * 100, b1_margin=b1["margin"] * 1000,
    b7_sys=b7["sys"] * 1000, b7_rand=b7["rand"] * 1000, b7_total=b7["total"] * 1000, b7_share=b7["total"] / acc["C7"]["T"] * 100,
    b1x_total=b1x["total"] * 1000, rev_n=len(rev), rev0=rev[0]["text"], rev2=rev2[0]["text"],
    cpk_open=caps["open"]["Ppk"], cpk_fb=caps["fb"]["Ppk"], cpk_act=caps["act"]["Ppk"], s_open=caps["open"]["s"] * 1000, s_act=caps["act"]["s"] * 1000)
