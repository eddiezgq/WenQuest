"""算例 20.4.1—20.4.3：能量准不等于性质准（20.3—20.4 节）。

同一个拟合好的势，**能量的平均绝对误差小到可以忽略，而由它导出的性质能错得很厉害**。
原因不玄：能量是函数值，而平衡间距要的是**一阶导数的零点**，声子频率与体弹模量要的是
**二阶导数**。拟合只压住了函数值，导数与曲率是搭便车来的。

这就是全书那条线在本章的样子：**拿一个指标做决定，必然被另一个指标反咬**。
"""
import numpy as np

from _ch20 import (BASIS, basis_centers, featurize, featurize_forces, fit_potential,
                   lj_energy_forces, phonon_omega, predict_energy, predict_forces,
                   sample_configs, strained_configs)
from bookout import out

L, N = 12.0, 10
CENTERS, WIDTH = basis_centers(), BASIS["width"]
v = {"n_atoms": N, "box": L}

train = sample_configs(80, N, L, amp=0.12, seed=0)
frames = [(x, lj_energy_forces(x, L)[0]) for x in train]
fdata = [lj_energy_forces(x, L)[1] for x in train]
w = fit_potential(frames, L, CENTERS, WIDTH, force_weight=0.1, force_data=fdata)

# 第二个势：训练集里**加上均匀应变的构型**（盒子跟着变）。盒长不同的样本不能用
# fit_potential 的单盒接口，所以这里直接把设计矩阵拼出来。
A, b = [], []
for x, e in frames:
    A.append(featurize(x, L, CENTERS, WIDTH)[None, :]); b.append([e])
    A.append(0.1 * featurize_forces(x, L, CENTERS, WIDTH)); b.append(0.1 * lj_energy_forces(x, L)[1])
for x, box in strained_configs(80, N, 1.05, 1.35, amp=0.06, seed=3):
    e, f = lj_energy_forces(x, box)
    A.append(featurize(x, box, CENTERS, WIDTH)[None, :]); b.append([e])
    A.append(0.1 * featurize_forces(x, box, CENTERS, WIDTH)); b.append(0.1 * f)
A = np.vstack(A); b = np.concatenate([np.atleast_1d(t) for t in b])
w_strain = np.linalg.solve(A.T @ A + 1e-8 * np.eye(A.shape[1]), A.T @ b)
v["n_strained"] = 80

e_fit = lambda x: predict_energy(w, x, L, CENTERS, WIDTH)        # noqa: E731
e_exact = lambda x: lj_energy_forces(x, L)[0]                    # noqa: E731

# ---------- 一、能量本身有多准
test = sample_configs(40, N, L, amp=0.12, seed=99)
de = [abs(e_fit(x) - e_exact(x)) / N for x in test]
df = [np.abs(predict_forces(w, x, L, CENTERS, WIDTH) - lj_energy_forces(x, L)[1]).mean()
      for x in test]
e_scale = float(np.mean([abs(e_exact(x)) / N for x in test]))
f_scale = float(np.mean([np.abs(lj_energy_forces(x, L)[1]).mean() for x in test]))
v["e_mae"] = float(np.mean(de))
v["f_mae"] = float(np.mean(df))
v["e_rel_pct"] = v["e_mae"] / e_scale * 100
v["f_rel_pct"] = v["f_mae"] / f_scale * 100
print(f"能量误差/原子 {v['e_mae']:.2e}（相对 {v['e_rel_pct']:.4f}%）")
print(f"力的平均误差   {v['f_mae']:.2e}（相对 {v['f_rel_pct']:.4f}%）")
v["rel_ratio_f_over_e"] = v["f_rel_pct"] / v["e_rel_pct"]
print(f"力的相对误差是能量的 {v['rel_ratio_f_over_e']:.0f} 倍")

# ---------- 二、平衡间距：一阶导数的零点
# 让整条链均匀伸缩，找能量最低的那个晶格常数。
# 注意：盒子要跟着伸缩，所以这里直接用"N 个原子、间距 a、盒长 N·a"的链
def e_chain(fn_kind, a):
    x = np.arange(N) * a
    box = N * a
    if fn_kind == "exact":
        return lj_energy_forces(x, box)[0]
    coef = w if fn_kind == "fit" else w_strain
    return float(featurize(x, box, CENTERS, WIDTH) @ coef)


# 声子在平衡构型上取二阶导，也要用补过应变的那个势——道理同上



# **搜索范围只能取训练覆盖到的那一段**：训练构型的最近邻距离在 1.08—1.32 之间，
# 超出这一段，拟合的势是无约束外推（往下没有下界），最小值会跑到网格边上去——
# 那不是"平衡间距算错了"，那是**在没有定义的地方问了问题**。
v["cover_lo"], v["cover_hi"] = 1.08, 1.32
a_grid = np.linspace(v["cover_lo"], v["cover_hi"], 801)
for tag in ("exact", "fit", "strain"):
    es = np.array([e_chain(tag, a) for a in a_grid])
    i = int(np.argmin(es))
    a0 = float(a_grid[i])
    # 二阶导 ≈ 均匀伸缩下的"体弹模量"类比量
    h = a_grid[1] - a_grid[0]
    curv = float((es[i + 1] - 2 * es[i] + es[i - 1]) / h ** 2)
    v[f"a0_{tag}"] = a0
    v[f"curv_{tag}"] = curv
    print(f"{tag:>5}：平衡间距 {a0:.4f}，均匀伸缩的曲率 {curv:.4f}")

v["a0_err_pct"] = abs(v["a0_fit"] - v["a0_exact"]) / v["a0_exact"] * 100
v["a0_err_strain_pct"] = abs(v["a0_strain"] - v["a0_exact"]) / v["a0_exact"] * 100
v["curv_err_strain_pct"] = abs(v["curv_strain"] - v["curv_exact"]) / abs(v["curv_exact"]) * 100
print(f"训练集里没有应变构型：平衡间距差 {v['a0_err_pct']:.3f}%，"
      f"而且最小值跑到搜索区间的边上、曲率完全没有意义")
print(f"训练集里加上应变构型：平衡间距差 {v['a0_err_strain_pct']:.3f}%，"
      f"曲率差 {v['curv_err_strain_pct']:.2f}%")
assert v["a0_err_strain_pct"] < v["a0_err_pct"], "补上应变构型应当让平衡间距对上"
assert v["curv_err_strain_pct"] < 50, "补上之后曲率也该进入可用范围"

# ---------- 三、声子：二阶导的全谱
x_eq = np.sort(np.arange(N) * v["a0_exact"]) % (N * v["a0_exact"])
box_eq = N * v["a0_exact"]


def make_energy(kind):
    if kind == "exact":
        return lambda x: lj_energy_forces(x, box_eq)[0]
    return lambda x: float(featurize(x, box_eq, CENTERS, WIDTH) @ w_strain)


om_exact = phonon_omega(make_energy("exact"), x_eq, box_eq)
om_fit = phonon_omega(make_energy("fit"), x_eq, box_eq)
keep = om_exact > 1e-6                     # 去掉整体平移那个零模
rel = np.abs(om_fit[keep] - om_exact[keep]) / om_exact[keep] * 100
v["phonon_max_exact"] = float(om_exact.max())
v["phonon_max_fit"] = float(om_fit.max())
v["phonon_max_err_pct"] = abs(v["phonon_max_fit"] - v["phonon_max_exact"]) / v["phonon_max_exact"] * 100
v["phonon_min_exact"] = float(om_exact[keep].min())
v["phonon_min_fit"] = float(om_fit[keep][int(np.argmin(om_exact[keep]))])
v["phonon_min_err_pct"] = abs(v["phonon_min_fit"] - v["phonon_min_exact"]) / v["phonon_min_exact"] * 100
v["phonon_rel_mean_pct"] = float(rel.mean())
v["n_bad_modes"] = int(np.sum(rel > 10))
v["n_modes"] = int(keep.sum())
v["n_imag_fit"] = int(np.sum(om_fit[keep] < 1e-9))
print(f"\n声子频率：**最高那一支几乎分不出来**——{v['phonon_max_exact']:.4f}（精确）对 "
      f"{v['phonon_max_fit']:.4f}（拟合），差 {v['phonon_max_err_pct']:.3f}%")
print(f"最低那一支：{v['phonon_min_exact']:.4f} 对 {v['phonon_min_fit']:.4f}，"
      f"差 {v['phonon_min_err_pct']:.2f}%")
print(f"{v['n_modes']} 支里有 {v['n_bad_modes']} 支误差超过 10%；平均相对误差 "
      f"{v['phonon_rel_mean_pct']:.2f}%；虚频 {v['n_imag_fit']} 支（精确势应当是 0 支）")
print("**注意这里的结论要照实说**：补上应变构型之后，连二阶导（声子）都落在千分之几以内，"
      "各支之间也没有明显的高低频规律。所以“二阶导一定更差”这句话是不对的——")
print("真正决定性的是**训练集覆盖到哪条形变路径**：没覆盖的方向上（上面那个没加应变的势）"
      "平衡间距与曲率全废，覆盖到了就都能用。")

# 本算例的结论：误差一级一级放大——函数值 → 一阶导 → 二阶导
assert v["e_rel_pct"] < v["f_rel_pct"], "力（一阶导）的相对误差应当大于能量"
assert v["phonon_rel_mean_pct"] > v["e_rel_pct"], "声子（二阶导）的相对误差应当比能量大"
v["ladder"] = (f"{v['e_rel_pct']:.4f}% → {v['f_rel_pct']:.3f}% → "
               f"{v['phonon_rel_mean_pct']:.2f}%")
v["cover_a0_err_ratio"] = v["a0_err_pct"] / v["a0_err_strain_pct"]
print(f"\n**误差阶梯（覆盖范围内）：能量 → 力 → 声子 = {v['ladder']}**")
print(f"**覆盖范围外的代价要大得多**：同一个性质（平衡间距），"
      f"训练集没覆盖那条路径时误差是覆盖之后的 {v['cover_a0_err_ratio']:.0f} 倍，"
      f"而曲率直接没有意义")
print("两条一起记：一个漂亮的能量 MAE 不保证性质能用（要印什么性质就报那个性质的误差）；"
      "而性质算得对不对，首先看训练集有没有覆盖到那条形变路径")

out(**v)
