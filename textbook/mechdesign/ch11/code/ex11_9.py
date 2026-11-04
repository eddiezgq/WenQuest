"""11.10 用 pyLife 算疲劳寿命：一步一步拆开数字工厂的 cae/fatigue.py。

算例 11.10.1  “仿真与分析”网页上的“疲劳寿命”：有限元给出计算工况下各点的冯·米塞斯应力 vm_ref（这里用 WQ-CR5 大臂示例零件、
            第 10 章的预设工况——手臂静止伸直），载荷谱是一个标量序列（这里用“多体动力学”的 J3 反力矩大小 rm.link3.abs，
            一个标准节拍），程序按 应力 = vm_ref × 载荷 / 计算工况载荷 缩放。逐步重做 fatigue.compute：
            ① closed_block：从 |载荷| 最大处切开、首尾相接；② rainflow：pyLife 四点法，接两遍减一遍，得到每块的闭合循环；
            ③ S_D = σ₋₁·β·ε/Kf（本章取精车 β = 0.85；网页的默认是磨削 0.92）；④ 每个循环：σa、σm 按比例换算，古德曼 σa,eq = σa/(1 − |σm|/R_m)；
            ⑤ pyLife WoehlerCurve 求 N，迈因纳累加；与 fatigue.compute 的结果核对（应完全相同）；
算例 11.10.2  改输入看结果：表面状态（抛光到锻造毛坯）、附加缺口系数 Kf（把阳极氧化 0.8、99% 可靠度 0.814 折成 Kf = 1/(0.8 × 0.814)）、海巴赫开关——疲劳安全系数 S_D/σa,eq 和每块损伤怎样变；
图 11.10.1。
"""
import math

import numpy as np
import pandas as pd
import pylife.materiallaws  # noqa: F401
from pylife.stress import rainflow as RF

import _ch11 as H
from bookout import T, figure, out, style

R = H.heavy()
t, L6, L0 = R["t"], R["L6"], R["L0"]
TCYC = float(t[-1])
U = R["U"]["J2"]
F = H.field(U, L6, L0)
series = np.linalg.norm(L6[3:], axis=0)                 # rm.link3.abs 的大小（N·m）
M0 = float(np.linalg.norm(L0[3:]))
Dall, ref = H.FT.compute(F["vm0"], M0, list(series), TCYC, H.AL, "fine_turned", 0.85, 1.0, True)
i = ref["hot_index"]
vm = float(F["vm0"][i])

# ① 闭合的块
blk = H.FT.closed_block(series)
# ② 雨流：接一遍、接两遍
one, two = blk, np.concatenate([blk, blk[1:]])


def count(arr):
    c = RF.FourPointDetector(recorder=RF.FullRecorder()).process(pd.Series(arr)).recorder.collective
    return len(c)


n_one, n_two = count(one), count(two)
cyc = H.FT.rainflow(series)
# ③ S_D
beta = H.FT.SURFACE["fine_turned"][0]
SD = H.AL["sigma_1"] * beta * 0.85 / 1.0
# ④ ⑤ 逐个循环
scale = vm / M0
wc = pd.Series({"SD": SD, "ND": float(H.AL["N_D"]), "k_1": float(H.AL["k"]), "k_2": 2 * H.AL["k"] - 1}).woehler
rows, D = [], 0.0
for a, m in cyc:
    sa, sm = scale * a, scale * abs(m)
    sa_eq = sa / (1 - min(sm / H.AL["ultimate_mpa"], 0.999))
    N = float(np.asarray(wc.cycles(np.array([sa_eq])))[0])
    D += 1 / N if math.isfinite(N) and N > 0 else 0.0
    rows.append((a, m, sa, sm, sa_eq, N))
rows.sort(key=lambda r: -r[4])
same = abs(D / ref["damage_per_block"] - 1) < 1e-9

# 算例 11.10.2
var = {}
for surf in ("polished", "ground", "fine_turned", "rough_turned", "forged"):
    _, s = H.FT.compute([vm], M0, list(series), TCYC, H.AL, surf, 0.85, 1.0, True)
    var[surf] = (H.FT.SURFACE[surf][0], s["S_D"], s["S_D"] / rows[0][4], s["damage_per_block"])
KF_ADD = 1 / (0.8 * 0.814)                            # 阳极氧化 0.8、99% 可靠度 0.814（11.3 节）折成附加缺口系数
_, s_kf = H.FT.compute([vm], M0, list(series), TCYC, H.AL, "fine_turned", 0.85, KF_ADD, True)
_, s_nh = H.FT.compute([vm], M0, list(series), TCYC, H.AL, "fine_turned", 0.85, 1.0, False)

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
a0.plot(t, series, color="#1f77b4", lw=1.1, label=T("原始记录", "record"))
tb = np.arange(len(blk)) * (t[1] - t[0])
a0.plot(tb, blk, color="#d62728", lw=0.8, ls="--", label=T("闭合的块（从最大处切开）", "closed block (cut at the maximum)"))
a0.set_xlabel(T("时间 / s", "Time / s"), fontsize=7.0)
a0.set_ylabel(T("|M| / N·m", "|M| / N·m"), fontsize=7.0)
a0.legend(fontsize=6.0, frameon=False, loc="lower right")
a0.tick_params(labelsize=6.2)
a0.set_title(T("(a) 载荷谱：J3 反力矩的大小", "(a) Load spectrum: magnitude of the J3 reaction moment"), fontsize=7.0)
amp = [r[0] for r in rows if r[0] > 1e-3]
mean = [r[1] for r in rows if r[0] > 1e-3]
a1.scatter(mean, amp, s=12, color="#1f77b4")
a1.set_xlabel(T("循环的平均值 / N·m", "Cycle mean / N·m"), fontsize=7.0)
a1.set_ylabel(T("循环的幅值 / N·m", "Cycle amplitude / N·m"), fontsize=7.0)
a1.tick_params(labelsize=6.2)
a1.set_title(T("(b) 雨流计数：每块 {} 个循环（幅值 > 0.001）".format(len(amp)), "(b) Rainflow: {} cycles per block (amplitude > 0.001)".format(len(amp))),
             fontsize=7.0)
fig.tight_layout()
figure(fig, "fig11_10_1")

out(vm=vm, M0=M0, scale=scale, th=math.degrees(F["theta"][i]), ph=F["phi"][i], n_series=len(series), n_blk=len(blk),
    n_one=n_one, n_two=n_two, n_cyc=len(cyc), n_amp=len(amp), SD=SD, beta=beta,
    a1=rows[0][0], m1=rows[0][1], sa1=rows[0][2], sm1=rows[0][3], saeq1=rows[0][4], N1=rows[0][5],
    D=D, D_ref=ref["damage_per_block"], same_txt=T("完全相同", "identical") if same else T("不同", "different"), S_fat=SD / rows[0][4],
    **{f"S_{k}": v[2] for k, v in var.items()}, **{f"b_{k}": v[0] for k, v in var.items()},
    D_polished=var["polished"][3], D_forged=var["forged"][3], D_ratio_surf=var["forged"][3] / var["polished"][3],
    kf_add=KF_ADD, S_kf13=s_kf["S_D"] / rows[0][4], D_kf13=s_kf["damage_per_block"], D_kf_ratio=s_kf["damage_per_block"] / ref["damage_per_block"],
    D_nohaibach=s_nh["damage_per_block"])
