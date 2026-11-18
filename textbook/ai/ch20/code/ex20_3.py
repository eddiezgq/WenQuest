"""算例 20.3.1—20.3.4：机器学习原子间势（20.3 节）。

真值用一个解析对势（Lennard-Jones），于是"精确答案"随时可得，每一条都能核。

（1）**力要一起放进拟合**：只拟能量，能量很准而力差得多；把力也放进去，力好十几倍。
（2）**长时间分子动力学看总能量守不守得住**——守不住的程度，就是这个势"不像个势"的程度。
（3）**外推会崩**：训练只覆盖平衡附近，扰动一加大，误差涨几个数量级。
（4）数据量的回报是递减的，而且补不上外推那一刀。
"""
import numpy as np

from _ch20 import (BASIS, basis_centers, fit_potential, lj_energy_forces, predict_energy,
                   predict_forces, sample_configs, verlet)
from bookout import out

L, N = 12.0, 10
CENTERS, WIDTH = basis_centers(), BASIS["width"]
AMP = 0.12                      # 训练构型的扰动幅度（晶格常数的一成多）

v = {"n_atoms": N, "box": L, "n_basis": BASIS["n"], "basis_width": WIDTH, "train_amp": AMP}


def data(n, amp, seed):
    xs = sample_configs(n, N, L, amp=amp, seed=seed)
    rows = []
    for x in xs:
        e, f = lj_energy_forces(x, L)
        rows.append((x, e, f))
    return rows


train = data(80, AMP, 0)
test = data(40, AMP, 99)
v["n_train"] = len(train)
v["n_test"] = len(test)
v["min_dist_train"] = float(min(
    np.abs(np.diff(np.r_[x, x[0] + L])).min() for x, _, _ in train))


def errors(w, rows):
    de, df = [], []
    for x, e, f in rows:
        de.append(abs(predict_energy(w, x, L, CENTERS, WIDTH) - e) / N)
        df.append(np.abs(predict_forces(w, x, L, CENTERS, WIDTH) - f).mean())
    return float(np.mean(de)), float(np.mean(df))


# ---------- 一、只拟能量 vs 能量与力一起拟
frames = [(x, e) for x, e, _ in train]
fdata = [f for _, _, f in train]
w_e = fit_potential(frames, L, CENTERS, WIDTH)
w_ef = fit_potential(frames, L, CENTERS, WIDTH, force_weight=0.1, force_data=fdata)

v["e_mae_eonly"], v["f_mae_eonly"] = errors(w_e, test)
v["e_mae_ef"], v["f_mae_ef"] = errors(w_ef, test)
v["force_scale"] = float(np.mean([np.abs(f).mean() for _, _, f in test]))
v["f_gain"] = v["f_mae_eonly"] / v["f_mae_ef"]
print(f"只拟能量：  能量误差/原子 {v['e_mae_eonly']:.2e}　力平均误差 {v['f_mae_eonly']:.2e}")
print(f"能量+力：   能量误差/原子 {v['e_mae_ef']:.2e}　力平均误差 {v['f_mae_ef']:.2e}")
print(f"力的典型量级 {v['force_scale']:.2f}；把力放进拟合，力的误差好 {v['f_gain']:.1f} 倍")
assert v["f_gain"] > 5, "把力放进拟合应当让力明显变好——这是机器学习势的基本做法"
assert v["e_mae_ef"] <= v["e_mae_eonly"] * 3, "而且不该把能量弄坏太多"

# ---------- 二、分子动力学：总能量守不守得住
x0 = sample_configs(1, N, L, amp=0.05, seed=5)[0]
g = np.random.default_rng(1)
v0 = g.normal(0, 0.30, N)      # 速度幅度：低温下原子只在拟合得最好的那一小块里晃，
                               # 势的毛病根本显不出来（实测 0.05 时漂移与精确势同量级）
v0 -= v0.mean()                                  # 去掉整体平移
DT, STEPS = 2e-3, 20000
v["md_dt"], v["md_steps"] = DT, STEPS

for tag, fn in (("exact", lambda x: lj_energy_forces(x, L)),
                ("eonly", lambda x: (predict_energy(w_e, x, L, CENTERS, WIDTH),
                                     predict_forces(w_e, x, L, CENTERS, WIDTH))),
                ("ef", lambda x: (predict_energy(w_ef, x, L, CENTERS, WIDTH),
                                  predict_forces(w_ef, x, L, CENTERS, WIDTH)))):
    _, _, etot = verlet(x0, v0, L, DT, STEPS, fn)
    drift = abs(etot[-1] - etot[0]) / N
    v[f"md_drift_{tag}"] = float(drift)
    v[f"md_std_{tag}"] = float(np.std(etot) / N)
    print(f"分子动力学 {STEPS} 步（{tag}）：总能量漂移/原子 {drift:.2e}，"
          f"起伏 {v[f'md_std_{tag}']:.2e}")

v["md_v_scale"] = 0.30
v["drift_ratio_ef"] = v["md_drift_ef"] / max(v["md_drift_exact"], 1e-18)
assert v["md_drift_exact"] < 1e-5, "精确势下总能量应当守得住（这是在核积分器，不是核势）"
assert v["drift_ratio_ef"] > 100, "拟合的势应当明显守不住——这正是要让读者看到的"
print(f"拟合的势（能量+力）漂移是精确势的 {v['drift_ratio_ef']:,.0f} 倍——"
      f"**能量守恒是检验势的第一道关，而不是看拟合残差**")

# ---------- 三、外推：训练只覆盖平衡附近
for amp in (0.12, 0.18, 0.24, 0.30, 0.40):
    rows = data(30, amp, 7)
    e_mae, f_mae = errors(w_ef, rows)
    v[f"extrap_e_{int(amp * 100)}"] = e_mae
    v[f"extrap_f_{int(amp * 100)}"] = f_mae
    print(f"扰动 {amp:.2f}（训练只到 {AMP}）：能量误差/原子 {e_mae:.2e}　力误差 {f_mae:.2e}")
v["extrap_blowup"] = v["extrap_e_40"] / v["extrap_e_12"]
assert v["extrap_blowup"] > 100, "外推应当崩得很明显——这是机器学习势最该交代的局限"
print(f"扰动从 {AMP} 到 0.40，能量误差涨 {v['extrap_blowup']:,.0f} 倍")

# ---------- 四、加数据的回报是递减的，而且补不上外推那一刀
for n in (20, 40, 80, 160, 320):
    tr = data(n, AMP, 11)
    w = fit_potential([(x, e) for x, e, _ in tr], L, CENTERS, WIDTH,
                      force_weight=0.1, force_data=[f for _, _, f in tr])
    e_in, _ = errors(w, test)
    e_out, _ = errors(w, data(20, 0.30, 13))
    v[f"n{n}_in"] = e_in
    v[f"n{n}_out"] = e_out
    print(f"训练 {n:>3d} 个构型：覆盖范围内 {e_in:.2e}　范围外（扰动 0.30）{e_out:.2e}")
v["data_gain_in"] = v["n20_in"] / v["n320_in"]
v["data_gain_out"] = v["n20_out"] / v["n320_out"]
print(f"数据加 16 倍：范围内误差好 {v['data_gain_in']:.1f} 倍，"
      f"范围外只好 {v['data_gain_out']:.1f} 倍")
assert v["data_gain_in"] > v["data_gain_out"], \
    "加数据主要改善覆盖范围内——**外推要靠换数据的覆盖，不是靠加同一类数据**"

out(**v)
