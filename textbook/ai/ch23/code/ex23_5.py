"""算例 23.5.1：端到端对分模块——更准的那个，错起来你不知道错在哪（23.5 节）。

同一条玩具数据（车道保持：三列车道线像素 → 方向盘角），两种做法：

* **分模块**：先把像素反投到地面、拟出横向偏差 e、航向偏差 ψ、曲率 κ（感知那一环），
  再用一个几何控制律算方向盘（控制那一环）。车辆参数按标称值装，与实车有一点差别。
* **端到端**：直接从三列像素（含二次项）回归方向盘角，中间什么也不估。

结果要连两列一起报：**总体误差**与**罕见情形误差**。端到端在总体上更准（它把像素噪声的
相关性和车辆参数的真实值一起学了进去），但一进训练分布外的急弯＋大偏差，它错得多得多；
而分模块那一列能把误差**归到某一环**——端到端没有这一列。

**“更准”与“能定位”是两件事，报表上必须分开写。**
"""
import numpy as np

from _ch23 import (CAM, LANE, fit_ls, lane_obs, lane_scene, perceive_lane,
                   poly_features, true_steer)
from bookout import out

N_TR, N_TE, N_RARE = 8000, 4000, 2000
v = {"n_train": N_TR, "n_test": N_TE, "n_rare": N_RARE}

# 控制那一环用的车辆参数：按标称值装，与实车差一点（**这是真实的样子**）
LANE_CTRL = dict(LANE)
LANE_CTRL["ratio"] = LANE["ratio"] * 1.04        # 转向比标称 15，实车 15.6
LANE_CTRL["k_e"] = LANE["k_e"] * 0.94            # 横向增益也差一点
v["ratio_true"], v["ratio_ctrl"] = LANE["ratio"], LANE_CTRL["ratio"]
print(f"控制那一环的车辆参数：转向比按 {LANE['ratio']:.1f} 装，实车 "
      f"{LANE_CTRL['ratio']:.2f}（差 {(LANE_CTRL['ratio'] / LANE['ratio'] - 1) * 100:.0f}%）")

# ---------- 训练：端到端把像素直接回归到方向盘角
tr = lane_scene(N_TR, seed=1)
U_tr = lane_obs(tr, seed=1)
y_tr = true_steer(tr["e"], tr["psi"], tr["kappa"])          # “专家”方向盘角 = 真值
w_e2e = fit_ls(poly_features(U_tr), y_tr, lam=1e-3)
v["n_e2e_params"] = len(w_e2e)
v["steer_std_deg"] = float(y_tr.std())
print(f"端到端模型 {v['n_e2e_params']} 个参数（三列像素的一次项与二次项）；"
      f"方向盘角本身的标准差 {v['steer_std_deg']:.2f}°")


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def run_both(sc: dict, seed: int) -> dict:
    """同一批数据上跑两种做法，并把分模块的误差分解出来。"""
    U = lane_obs(sc, seed=seed)
    y = true_steer(sc["e"], sc["psi"], sc["kappa"])          # 真值
    pred_e2e = poly_features(U) @ w_e2e
    pc = perceive_lane(U, CAM["pitch"], CAM["height"])       # 第一环：感知
    pred_mod = true_steer(pc["e"], pc["psi"], pc["kappa"], LANE_CTRL)   # 第二环：控制
    # 分解：只换感知输入 / 只换车辆参数
    only_perc = true_steer(pc["e"], pc["psi"], pc["kappa"], LANE)
    only_ctrl = true_steer(sc["e"], sc["psi"], sc["kappa"], LANE_CTRL)
    return {
        "e2e": rmse(pred_e2e, y), "e2e_max": float(np.max(np.abs(pred_e2e - y))),
        "mod": rmse(pred_mod, y), "mod_max": float(np.max(np.abs(pred_mod - y))),
        "mod_perc": rmse(only_perc, y), "mod_ctrl": rmse(only_ctrl, y),
        "perc_e": rmse(pc["e"], sc["e"]), "perc_psi": rmse(pc["psi"], sc["psi"]),
        "perc_kappa": rmse(pc["kappa"], sc["kappa"]),
        "y_std": float(y.std()),
    }


# ---------- 一、总体（与训练同分布）
te = lane_scene(N_TE, seed=55)
r_all = run_both(te, seed=55)
for k, x in r_all.items():
    v[f"all_{k}"] = x
v["all_e2e_better_pct"] = (1 - r_all["e2e"] / r_all["mod"]) * 100
print(f"\n【总体】端到端 {r_all['e2e']:.3f}°，分模块 {r_all['mod']:.3f}°——"
      f"端到端好 {v['all_e2e_better_pct']:.0f}%")
assert r_all["e2e"] < r_all["mod"], \
    "同分布上端到端必须更准，否则这个对照没有意义（它学了噪声相关性与真实车辆参数）"

# ---------- 二、罕见情形：半径 20 m 的急弯 + 车偏出中心线 2.5 m
RARE_KAPPA, RARE_E = 0.05, 2.5
v["rare_radius_m"] = 1.0 / RARE_KAPPA
v["train_radius_min_m"] = 1.0 / 0.004
rare = lane_scene(N_RARE, seed=77, kappa_max=RARE_KAPPA, e_sigma=RARE_E)
r_rare = run_both(rare, seed=77)
for k, x in r_rare.items():
    v[f"rare_{k}"] = x
print(f"\n【罕见情形】最小半径 {v['rare_radius_m']:.0f} m 的急弯"
      f"（训练数据里最小半径 {v['train_radius_min_m']:.0f} m）、"
      f"横向偏差标准差 {RARE_E:.1f} m")
print(f"端到端 {r_rare['e2e']:.3f}°（最大 {r_rare['e2e_max']:.2f}°），"
      f"分模块 {r_rare['mod']:.3f}°（最大 {r_rare['mod_max']:.2f}°）")
v["rare_e2e_worse_ratio"] = r_rare["e2e"] / r_rare["mod"]
v["rare_e2e_worse_pct"] = (r_rare["e2e"] / r_rare["mod"] - 1) * 100
assert r_rare["e2e"] > r_rare["mod"], \
    "罕见情形上端到端必须更差——它的二次项在训练分布外外推"
assert v["rare_e2e_worse_ratio"] >= 2.0, "差距要足够大，不然说明不了问题"
print(f"**端到端差 {v['rare_e2e_worse_ratio']:.1f} 倍**")

v["e2e_degrade_ratio"] = r_rare["e2e"] / r_all["e2e"]
v["mod_degrade_ratio"] = r_rare["mod"] / r_all["mod"]
print(f"从总体到罕见情形：端到端误差涨到 {v['e2e_degrade_ratio']:.1f} 倍，"
      f"分模块只涨到 {v['mod_degrade_ratio']:.2f} 倍")
assert v["e2e_degrade_ratio"] > v["mod_degrade_ratio"], \
    "端到端在分布外退化得更快"

print("\n两列并排才是报表该有的样子：")
print(f"{'做法':<10}{'总体(°)':>10}{'罕见情形(°)':>14}{'罕见/总体':>12}")
print(f"{'端到端':<10}{r_all['e2e']:>10.3f}{r_rare['e2e']:>14.3f}"
      f"{v['e2e_degrade_ratio']:>12.1f}")
print(f"{'分模块':<10}{r_all['mod']:>10.3f}{r_rare['mod']:>14.3f}"
      f"{v['mod_degrade_ratio']:>12.2f}")
print("**只看左边那一列，端到端赢；只看右边那一列，分模块赢。"
      "报表只给一列，这个决定就被替你做了。**")

# ---------- 三、分模块的误差分解——端到端没有这一列
print("\n分模块的误差归到哪一环（端到端没有这一列）：")
for tag, r in (("总体", r_all), ("罕见情形", r_rare)):
    print(f"  {tag}：")
    print(f"    第一环 感知（e、ψ、κ 估错）折成方向盘误差：{r['mod_perc']:.3f}°")
    print(f"    第二环 控制（车辆参数不准）折成方向盘误差：{r['mod_ctrl']:.3f}°")
    print(f"    合计：{r['mod']:.3f}°")
    print(f"    感知那一环本身：e {r['perc_e']:.3f} m、ψ {np.degrees(r['perc_psi']):.3f}°、"
          f"κ {r['perc_kappa']:.5f} 1/m")
v["all_share_perc_pct"] = r_all["mod_perc"] ** 2 / (r_all["mod_perc"] ** 2
                                                    + r_all["mod_ctrl"] ** 2) * 100
v["rare_share_perc_pct"] = r_rare["mod_perc"] ** 2 / (r_rare["mod_perc"] ** 2
                                                      + r_rare["mod_ctrl"] ** 2) * 100
print(f"\n按平方和折成占比：总体里感知那一环占 {v['all_share_perc_pct']:.0f}%，"
      f"罕见情形里占 {v['rare_share_perc_pct']:.0f}%")
assert v["rare_share_perc_pct"] != v["all_share_perc_pct"], \
    "两种工况下该修的环不一样——这正是分解的用处"
dom_all = "感知" if v["all_share_perc_pct"] > 50 else "控制"
dom_rare = "感知" if v["rare_share_perc_pct"] > 50 else "控制"
print(f"**该修哪一环，两种工况给的答案不同**：总体上先修{dom_all}那一环，"
      f"罕见情形上先修{dom_rare}那一环。端到端出了同样的问题，"
      f"你拿到的只有一个变大的数——连“先修哪儿”都无从下手。")

# ---------- 四、端到端错得最厉害的那一批，长什么样
U_rare = lane_obs(rare, seed=77)
y_rare = true_steer(rare["e"], rare["psi"], rare["kappa"])
err_e2e = np.abs(poly_features(U_rare) @ w_e2e - y_rare)
k_bad = np.argsort(err_e2e)[-100:]
v["bad_mean_abs_kappa"] = float(np.mean(np.abs(rare["kappa"][k_bad])))
v["rare_mean_abs_kappa"] = float(np.mean(np.abs(rare["kappa"])))
v["bad_mean_abs_e"] = float(np.mean(np.abs(rare["e"][k_bad])))
v["rare_mean_abs_e"] = float(np.mean(np.abs(rare["e"])))
print(f"\n端到端错得最厉害的 100 帧：平均 |κ| {v['bad_mean_abs_kappa']:.4f} 1/m"
      f"（这批整体 {v['rare_mean_abs_kappa']:.4f}）、平均 |e| "
      f"{v['bad_mean_abs_e']:.2f} m（整体 {v['rare_mean_abs_e']:.2f}）")
assert v["bad_mean_abs_kappa"] > v["rare_mean_abs_kappa"] or \
    v["bad_mean_abs_e"] > v["rare_mean_abs_e"], \
    "端到端最差的那批应当落在离训练分布最远的地方"
print("**它错在离训练数据最远的那一片**——这件事能看出来，是因为我们手里有真值 e、κ。"
      "真车上没有真值，只有一个端到端模型和一个方向盘角：你连“它现在在外推”都不知道。")

print("\n这个算例回答不了什么：真端到端模型不是一个二次多项式，它的外推行为复杂得多，"
      "既可能更稳健（见过的场景多），也可能在更小的扰动下崩；本算例的分模块那一侧"
      "用的是解析几何，占了“模型结构正好对”的便宜，真感知模块自己就是学出来的，"
      "一样会在分布外错。本算例能说明的只有一件事：**分模块留下了可以归因的接缝，"
      "端到端没有**——这与谁更准无关。")

out(**v)
