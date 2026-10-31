"""7.3 工况与载荷系数：同一型号 WQR-105 在三类客户现场（数字孪生的客户现场模拟器：矿山皮带机、港口输送、食品包装线）各运行一年，
由每天的运行摘要求平均转矩、最大转矩、起动冲击系数，以及按转数累计的当量转矩：球轴承 m = 3，齿面接触（转矩的指数）约 6.6；
求两个比值——当量 / 平均运行转矩（运行中的波动有多大）、当量 / 额定转矩（相对额定的使用系数，ISO 6336-6 由载荷谱求 KA 的思路），
与 ISO 6336-1 的指导值对照（算例 7.3.1，图 7.3.1）。注意：数字孪生的运行转矩直方图是模型设定（平均值 ×0.9 / 1.0 / 1.1，
权重 0.25 / 0.5 / 0.25），起停峰值按“各一转”计入（影响很小）。
另看输出轴的扭转：扭转的循环不是“转一圈一次”，而是起停和运行中的波动（雨流计数），按 m = 9（数字孪生的输出轴 S-N 曲线斜率）
求起停循环占的损伤份额。"""
import numpy as np

import _ch7 as H
import mdstd
from bookout import T, figure, out, style

N_OUT = H.TM.speeds()["out"]               # 输出转速 r/min（电机 1450 r/min；食品厂变频另算）
K_SHAFT = H.TM.SHAFT_MAT["k"]
M_FLANK = 6.6                              # 齿面接触寿命：按应力的斜率约 13.2（渗碳淬火钢），接触应力 ∝ √T，按转矩约 6.6（第 29 章）
KA_TAB = mdstd.table("iso6336_ka")
ka = {r[0][:4]: r for r in KA_TAB["rows"]}
KA_MOTOR = KA_TAB["rows"][0]                 # 原动机：电动机
# 工作机的冲击类别（本书的判断，与 ISO 6336-1 表 B.3 的举例对照）：食品包装线 均匀，港口输送 轻微，矿山皮带机 中等
CLASS = {"food": 2, "port": 3, "mine": 4}
CLASS_NAME = {2: T("均匀", "uniform"), 3: T("轻微冲击", "light shocks"), 4: T("中等冲击", "moderate shocks")}

R = {}
for site in ("mine", "port", "food"):
    days = H.site_year(site)
    n_out = days[0]["n_in_rpm"] * N_OUT / H.TM.N_IN_RPM
    run_h = sum(d["run_h"] for d in days)
    starts = sum(d["starts"] for d in days)
    t_mean = sum(d.get("torque_mean_nm", 0) * d["run_h"] for d in days) / run_h
    t_max = max(d.get("torque_max_nm", 0) for d in days)
    # 按转数累计：运行时的载荷直方图（转矩, 小时）→ 转数；起动峰值各算一转（影响很小，计入以示完整）
    pairs = []
    peaks = []
    for d in days:
        pairs += [(t, h * 60 * n_out) for t, h in d["load_hist"]]
        for a, m, n in d["rainflow"]:
            if a == m:                       # 0 → 峰值 → 0 的起停大循环：峰值 = 2a
                peaks += [2 * a] * int(n)
    pairs += [(p, 1) for p in peaks]
    t_eq3 = H.eq_value(pairs, 3)
    t_eq66 = H.eq_value(pairs, M_FLANK)
    # 输出轴扭转：雨流循环（幅值 a，次数 n），按 m = 9 比较起停循环与运行波动的损伤份额
    d_start = d_run = 0.0
    for d in days:
        for a, m, n in d["rainflow"]:
            if a == m:
                d_start += n * a ** K_SHAFT
            else:
                d_run += n * a ** K_SHAFT
    R[site] = {"run_h": run_h, "starts": starts, "t_mean": t_mean, "t_max": t_max, "k_peak": float(np.mean(peaks)) / t_mean,
               "max_rated": t_max / H.RATED, "t_eq3": t_eq3, "KA3": t_eq3 / t_mean, "t_eq66": t_eq66, "KA66": t_eq66 / t_mean, "eq66_rated": t_eq66 / H.RATED, "KA_peak": t_max / t_mean, "share_start": 100 * d_start / (d_start + d_run),
               "KA_tab": KA_MOTOR[CLASS[site]], "cls": CLASS_NAME[CLASS[site]], "rev": sum(c for _, c in pairs),
               "daily": [(k, d.get("torque_mean_nm", np.nan), d.get("torque_max_nm", np.nan)) for k, d in enumerate(days)],
               "eq_rated": t_eq3 / H.RATED}

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.6, 3.1), gridspec_kw={"width_ratios": [1.35, 1.0]})
for site, r in R.items():
    k = [x for x, _, _ in r["daily"]]
    a0.plot(k, [m for _, m, _ in r["daily"]], color=H.SITE_COLOR[site], lw=0.8, label=H.SITE_NAME[site])
    a0.plot(k, [M for _, _, M in r["daily"]], ".", color=H.SITE_COLOR[site], ms=1.6)
a0.axhline(H.RATED, color=H.MUTED, lw=0.7, ls=":")
a0.text(362, H.RATED + 10, T("额定 350", "rated 350"), fontsize=6.2, color=H.MUTED, ha="right")
a0.set_xlabel(T("一年中的第几天", "Day of the year"), fontsize=7.2)
a0.set_ylabel(T("输出转矩 / N·m（线：当天平均；点：当天最大）", "Output torque / N·m (line: daily mean; dots: daily max)"), fontsize=6.6)
a0.legend(fontsize=6.2, frameon=False, loc="center left", bbox_to_anchor=(0.0, 0.42), ncol=3)
a0.tick_params(labelsize=6.3)
a0.set_title(T("(a) 三类现场一年的运行转矩（数字孪生）", "(a) One year at three sites (digital twin)"), fontsize=7.6)
x = np.arange(3)
names = list(R)
w = 0.2
a1.bar(x - 1.5 * w, [R[s]["eq_rated"] for s in names], w, color="#1f77b4", label=T("当量（m = 3）/ 额定", "equivalent (m = 3) / rated"))
a1.bar(x - 0.5 * w, [R[s]["eq66_rated"] for s in names], w, color="#6baed6", label=T("当量（m = 6.6）/ 额定", "equivalent (m = 6.6) / rated"))
a1.bar(x + 0.5 * w, [R[s]["KA_tab"] for s in names], w, color="#bbbbbb", label=T("ISO 6336-1 指导值（电动机）", "ISO 6336-1 guide (electric motor)"))
a1.bar(x + 1.5 * w, [R[s]["max_rated"] for s in names], w, color="#d62728", label=T("最大 / 额定", "max / rated"))
a1.set_xticks(x)
a1.set_xticklabels([H.SITE_NAME[s] for s in names], fontsize=6.4)
a1.set_ylabel(T("与额定转矩之比 / 系数", "Ratio to rated torque / factor"), fontsize=7.2)
a1.legend(fontsize=6.0, frameon=False, loc="upper right")
a1.set_ylim(0, 3.2)
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 当量、最大与使用系数的指导值", "(b) Equivalent and maximum loads vs guide values"), fontsize=7.6)
fig.tight_layout()
figure(fig, "fig7_3_1")

o = {}
for s, r in R.items():
    for k in ("run_h", "starts", "t_mean", "t_max", "k_peak", "t_eq3", "KA3", "t_eq66", "KA66", "eq66_rated", "max_rated", "KA_peak", "share_start", "KA_tab", "cls", "rev", "eq_rated"):
        o[f"{s}_{k}"] = r[k]
out(n_out=N_OUT, k_shaft=K_SHAFT, m_flank=M_FLANK, rated=H.RATED, n_food=R["food"]["rev"] / R["food"]["run_h"] / 60, **o)
