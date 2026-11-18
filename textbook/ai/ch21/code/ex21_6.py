"""算例 21.6.1—21.6.4：控制限不是规格限（21.5 节）。

四件事：
（1）**控制限来自过程自己的波动，规格限来自图纸**——两者没有任何数学关系；
（2）过程完全没变时，三倍标准差控制限的**虚发警报率**约为每 370 个子组一次：
    本算例把这个数模拟出来，不照抄；
（3）**控制图抓得到均值漂移，抓方差变化慢得多**；
（4）**过程能力指数与报警率是两回事**：能力很差的过程可以完全"受控"（不报警），
    能力很好的过程也可以天天报警。
"""
import numpy as np

from _ch21 import A2, D2, D4, alarms, capability, out_of_spec_ppm, run_chart, xbar_limits
from bookout import out

N_SUB = 5
v = {"n_sub": N_SUB, "a2": A2[N_SUB], "d2": D2[N_SUB], "d4": D4[N_SUB]}

# ---------- 一、虚发警报率：过程一点没变，也会报警
TRIALS, N_GROUPS = 400, 200
rate = []
for sd in range(TRIALS):
    g = run_chart(N_GROUPS, N_SUB, seed=sd)
    lim = xbar_limits(g[:50], A2[N_SUB])          # 用前 50 个子组定控制限（现场就是这么做的）
    rate.append(float(np.mean(alarms(g[50:], lim))))
v["false_alarm_rate"] = float(np.mean(rate))
v["arl0"] = 1.0 / v["false_alarm_rate"]
v["arl0_theory"] = 1.0 / 0.0027
print(f"过程完全没变：{TRIALS} 次模拟，平均每个子组报警的概率 {v['false_alarm_rate']:.5f}，"
      f"即平均每 {v['arl0']:.0f} 个子组虚发一次（教科书值 {v['arl0_theory']:.0f}）")
v["arl0_ratio"] = v["arl0"] / v["arl0_theory"]
print(f"模拟值与教科书值之比 {v['arl0_ratio']:.2f}（不是 1，是因为控制限只用前 50 个子组估计，"
      f"估计本身带误差——**现场的虚发警报率总比教科书高**）")
assert 100 < v["arl0"] < 2000, "三倍标准差控制限的虚发间隔应当在几百个子组这个量级"

# ---------- 二、抓得到什么：均值漂移 vs 方差变大
for shift, tag in ((0.5, "05"), (1.0, "10"), (1.5, "15"), (2.0, "20")):
    det = []
    for sd in range(200):
        g = run_chart(160, N_SUB, shift_at=60, shift=shift, seed=1000 + sd)
        lim = xbar_limits(g[:50], A2[N_SUB])
        a = alarms(g, lim)
        idx = np.nonzero(a[60:])[0]
        det.append(int(idx[0]) + 1 if len(idx) else 100)
    v[f"arl_shift{tag}"] = float(np.median(det))
    print(f"均值漂移 {shift:.1f}σ：中位要 {v[f'arl_shift{tag}']:.0f} 个子组才报警")
assert v["arl_shift20"] < v["arl_shift05"], "漂移越大，发现得越快"

for spread, tag in ((1.5, "15"), (2.0, "20")):
    det = []
    for sd in range(200):
        g = run_chart(160, N_SUB, shift_at=60, shift=0.0, spread=spread, seed=2000 + sd)
        lim = xbar_limits(g[:50], A2[N_SUB])
        a = alarms(g, lim)
        idx = np.nonzero(a[60:])[0]
        det.append(int(idx[0]) + 1 if len(idx) else 100)
    v[f"arl_spread{tag}"] = float(np.median(det))
    print(f"方差变成 {spread:.1f} 倍（均值不动）：中位要 {v[f'arl_spread{tag}']:.0f} 个子组才报警")
v["spread_vs_shift"] = v["arl_spread15"] / v["arl_shift10"]
print(f"**同样是“过程变了”，方差变大比均值漂移难发现**——"
      f"方差 1.5 倍要等 {v['arl_spread15']:.0f} 个子组，而 1σ 漂移只要 {v['arl_shift10']:.0f} 个")
print("所以均值图要**配极差图一起看**；只看均值图的车间，方差问题会拖很久")

# ---------- 三、控制限与规格限没有关系
# 同一条产线，规格限由图纸给：这里取 ±3（单位任意）。过程标准差 1.0。
LSL, USL = -3.0, 3.0
g = run_chart(200, N_SUB, seed=7)
lim = xbar_limits(g, A2[N_SUB])
sigma_hat = lim["rbar"] / D2[N_SUB]                     # 由极差估过程标准差
v["sigma_hat"] = sigma_hat
v["ucl"] = lim["ucl"]
v["lcl"] = lim["lcl"]
v["usl"] = USL
v["lsl"] = LSL
v["ctrl_width"] = lim["ucl"] - lim["lcl"]
v["spec_width"] = USL - LSL
v["width_ratio"] = v["spec_width"] / v["ctrl_width"]
print(f"\n控制限 {v['lcl']:+.3f} … {v['ucl']:+.3f}（宽 {v['ctrl_width']:.3f}），"
      f"规格限 {LSL:+.1f} … {USL:+.1f}（宽 {v['spec_width']:.1f}）")
print(f"规格限比控制限宽 {v['width_ratio']:.1f} 倍——**两者宽窄的比例没有任何固定关系**："
      f"控制限管的是子组均值的波动（除以 √{N_SUB}），规格限管的是单件")

cap = capability(0.0, sigma_hat, LSL, USL)
v["cp"] = cap["cp"]
v["cpk"] = cap["cpk"]
v["ppm"] = out_of_spec_ppm(0.0, sigma_hat, LSL, USL)
print(f"过程能力：Cp {v['cp']:.3f}，Cpk {v['cpk']:.3f}，按正态估超差 {v['ppm']:.0f} ppm")

# ---------- 四、能力与报警是两回事
# 过程 A：能力差（规格窄），但完全稳定——一个警报都不会报。
narrow_l, narrow_u = -1.2, 1.2
capA = capability(0.0, sigma_hat, narrow_l, narrow_u)
v["cpk_A"] = capA["cpk"]
v["ppm_A"] = out_of_spec_ppm(0.0, sigma_hat, narrow_l, narrow_u)
alarms_A = float(np.mean(alarms(g, lim)))
v["alarm_A"] = alarms_A * 100
# 过程 B：能力很好（规格宽），但均值每隔一段时间跳一下——天天报警。
gB = run_chart(200, N_SUB, shift_at=100, shift=1.2, seed=9)
limB = xbar_limits(gB[:50], A2[N_SUB])
capB = capability(0.0, sigma_hat, -6.0, 6.0)
v["cpk_B"] = capB["cpk"]
v["ppm_B"] = out_of_spec_ppm(0.6, sigma_hat, -6.0, 6.0)
v["alarm_B"] = float(np.mean(alarms(gB[100:], limB))) * 100
print(f"\n过程甲：Cpk {v['cpk_A']:.2f}（超差 {v['ppm_A']:,.0f} ppm），"
      f"报警率 {v['alarm_A']:.1f}%——**能力很差，却完全“受控”**")
print(f"过程乙：Cpk {v['cpk_B']:.2f}（超差 {v['ppm_B']:.1f} ppm），"
      f"报警率 {v['alarm_B']:.1f}%——**能力很好，却天天报警**")
assert v["cpk_A"] < v["cpk_B"] and v["alarm_A"] < v["alarm_B"], \
    "这一对要同时成立：能力差的不报警、能力好的反而报警"
print("两件事要分开问：**做得出合格品吗**（能力，对规格限）与"
      "**过程有没有变**（受控，对控制限）。把控制限当合格判据，两边都答错")

out(**v)
