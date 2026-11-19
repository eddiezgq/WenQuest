"""算例 23.6.1：数据闭环——随机加数据，还是按不确定性挑数据（23.6 节）。

数据闭环的真实处境：车队每天跑回来几万段数据，**其中绝大部分是你已经会的那一种**
（直道、好天气、车在车道中间）。能标的预算是有限的，标哪一批？

两种策略放在同一个误差预算下比：
* **随机加**：从回传的数据里随机抽一批去标；
* **按不确定性挑**：算每个候选样本的杠杆值 xᵀ(XᵀX+λI)⁻¹x（模型对它越没把握越大），
  挑最大的那一批。线性模型自己就给得出这个数，不需要集成、不需要贝叶斯。

验收的误差口径要先说死：**按难例与易例等权重算**。按回传数据的自然分布算，
易例占 93%，怎么挑都差不多——口径一换，结论就反了，这件事本算例也算出来了。
"""
import numpy as np

from _ch23 import (CAM, fit_ls, lane_obs, lane_scene, poly_features, pool_scene,
                   leverage, true_steer)
from bookout import out

N_POOL, N_SEED, BATCH, N_ROUND = 9000, 60, 60, 24
EASY_FRAC = 0.93
v = {"n_pool": N_POOL, "n_seed": N_SEED, "batch": BATCH, "n_round": N_ROUND,
     "easy_frac": EASY_FRAC}

pool = pool_scene(N_POOL, seed=2, easy_frac=EASY_FRAC)
U_pool = lane_obs(pool, seed=2)
X_pool = poly_features(U_pool)
y_pool = true_steer(pool["e"], pool["psi"], pool["kappa"])
v["pool_hard_pct"] = float(pool["is_hard"].mean()) * 100
print(f"候选池 {N_POOL} 条，其中难例只占 {v['pool_hard_pct']:.1f}%"
      f"——**这就是回传数据的样子**")

# 验收集：难例与易例**等权重**（口径先说死）
te_easy = lane_scene(3000, seed=61, kappa_max=0.0004, e_sigma=0.10)
te_hard = lane_scene(3000, seed=62, kappa_max=0.009, e_sigma=1.10)
sets = {}
for tag, sc, sd in (("easy", te_easy, 61), ("hard", te_hard, 62)):
    U = lane_obs(sc, seed=sd)
    sets[tag] = (poly_features(U), true_steer(sc["e"], sc["psi"], sc["kappa"]))
v["n_test_each"] = 3000


def rmse(X, y, w):
    return float(np.sqrt(np.mean((X @ w - y) ** 2)))


def err_balanced(w):
    """等权重误差：易例与难例各算一半（本节的验收口径）。"""
    return float(np.sqrt(0.5 * rmse(*sets["easy"], w) ** 2
                         + 0.5 * rmse(*sets["hard"], w) ** 2))


def err_natural(w):
    """按回传数据的自然分布算的误差——**换这个口径结论会反**。"""
    return float(np.sqrt(EASY_FRAC * rmse(*sets["easy"], w) ** 2
                         + (1 - EASY_FRAC) * rmse(*sets["hard"], w) ** 2))


def run(strategy: str, seed: int = 0) -> dict:
    """跑一遍数据闭环：种子集 → 每轮挑一批去标 → 重训 → 记误差。"""
    g = np.random.default_rng(seed + 404)
    idx = list(g.choice(N_POOL, N_SEED, replace=False))
    rest = np.setdiff1d(np.arange(N_POOL), idx)
    n_used, bal, nat, hard_share = [], [], [], []
    for _ in range(N_ROUND):
        w = fit_ls(X_pool[idx], y_pool[idx], lam=1e-3)
        n_used.append(len(idx))
        bal.append(err_balanced(w))
        nat.append(err_natural(w))
        hard_share.append(float(pool["is_hard"][idx].mean()) * 100)
        if strategy == "random":
            pick = g.choice(len(rest), BATCH, replace=False)
        else:
            lev = leverage(X_pool[rest], X_pool[idx])
            pick = np.argsort(lev)[-BATCH:]
        idx = idx + list(rest[pick])
        rest = np.delete(rest, pick)
    w = fit_ls(X_pool[idx], y_pool[idx], lam=1e-3)
    n_used.append(len(idx))
    bal.append(err_balanced(w))
    nat.append(err_natural(w))
    hard_share.append(float(pool["is_hard"][idx].mean()) * 100)
    return {"n": np.array(n_used), "bal": np.array(bal), "nat": np.array(nat),
            "hard_pct": np.array(hard_share), "w": w}


rnd = run("random")
act = run("active")
v["curve_n"] = rnd["n"].tolist()
v["curve_random"] = rnd["bal"].tolist()
v["curve_active"] = act["bal"].tolist()
v["curve_random_hard_pct"] = rnd["hard_pct"].tolist()
v["curve_active_hard_pct"] = act["hard_pct"].tolist()

print("\n标注量   随机加(°)   按不确定性挑(°)   标注集里难例占比（随机/挑）")
for i in range(0, len(rnd["n"]), 4):
    print(f"{rnd['n'][i]:6d}{rnd['bal'][i]:12.4f}{act['bal'][i]:17.4f}"
          f"{rnd['hard_pct'][i]:17.1f}% /{act['hard_pct'][i]:6.1f}%")

v["err_random_final"] = float(rnd["bal"][-1])
v["err_active_final"] = float(act["bal"][-1])
v["n_final"] = int(rnd["n"][-1])
print(f"\n标到 {v['n_final']} 条时：随机 {v['err_random_final']:.4f}°，"
      f"按不确定性挑 {v['err_active_final']:.4f}°")

# ---------- 一、同一个误差预算，各要多少样本
TARGET = float(np.max([rnd["bal"][-1], act["bal"][-1]]) * 1.15)   # 两条曲线都能达到的一档
v["target_err_deg"] = TARGET


def samples_to(curve: dict, target: float) -> int | None:
    ok = np.where(curve["bal"] <= target)[0]
    return int(curve["n"][ok[0]]) if len(ok) else None


v["n_random_to_target"] = samples_to(rnd, TARGET)
v["n_active_to_target"] = samples_to(act, TARGET)
assert v["n_random_to_target"] is not None and v["n_active_to_target"] is not None, \
    "两条曲线都要达到这个误差，否则没法比"
v["sample_saving_pct"] = (1 - v["n_active_to_target"] / v["n_random_to_target"]) * 100
v["sample_saving_x"] = v["n_random_to_target"] / v["n_active_to_target"]
print(f"\n同一个误差预算 {TARGET:.4f}°：随机要标 {v['n_random_to_target']} 条，"
      f"按不确定性挑只要 {v['n_active_to_target']} 条")
assert v["n_active_to_target"] < v["n_random_to_target"], \
    "挑数据要比随机加省样本；若不成立，照实报"
print(f"**省 {v['sample_saving_pct']:.0f}% 的标注量（{v['sample_saving_x']:.1f} 倍）**")

# ---------- 二、它为什么省：挑出来的是什么
v["hard_pct_random_final"] = float(rnd["hard_pct"][-1])
v["hard_pct_active_final"] = float(act["hard_pct"][-1])
v["hard_enrich_x"] = v["hard_pct_active_final"] / max(v["hard_pct_random_final"], 1e-9)
print(f"\n标注集里难例占比：随机 {v['hard_pct_random_final']:.1f}%"
      f"（≈池子的自然比例 {v['pool_hard_pct']:.1f}%），"
      f"按不确定性挑 {v['hard_pct_active_final']:.1f}%")
assert v["hard_pct_active_final"] > v["hard_pct_random_final"], \
    "不确定性挑出来的就该是难例——否则它省不下样本"
print(f"**富集了 {v['hard_enrich_x']:.1f} 倍**：它不需要有人告诉它“弯道是难例”，"
      f"杠杆值自己把那一片挑了出来")

# ---------- 三、换一个误差口径，结论会不会反
v["nat_random_final"] = float(rnd["nat"][-1])
v["nat_active_final"] = float(act["nat"][-1])
print(f"\n换成按回传数据自然分布算（易例占 {EASY_FRAC:.0%}）："
      f"随机 {v['nat_random_final']:.4f}°，挑数据 {v['nat_active_final']:.4f}°")
v["nat_active_worse"] = v["nat_active_final"] > v["nat_random_final"]
if v["nat_active_worse"]:
    v["nat_active_worse_pct"] = (v["nat_active_final"] / v["nat_random_final"] - 1) * 100
    print(f"**口径一换，挑数据反而差 {v['nat_active_worse_pct']:.0f}%**："
          f"它把预算花在了只占 {100 - EASY_FRAC * 100:.0f}% 的那一片上，"
          f"按自然分布算当然不划算。")
else:
    v["nat_active_worse_pct"] = (1 - v["nat_active_final"] / v["nat_random_final"]) * 100
    print(f"按自然分布算，挑数据仍好 {v['nat_active_worse_pct']:.0f}%")
print("**所以“该不该主动挑数据”这个问题，答案全在误差口径里**："
      "按自然分布验收，难例怎么都淹没；按等权重（或按难例单列）验收，才看得见挑数据的价值。"
      "口径要在开工前定下来，不能等结果出来再挑一个好看的。")

# ---------- 四、只看难例那一列
for tag, cur in (("random", rnd), ("active", act)):
    v[f"err_easy_{tag}"] = rmse(*sets["easy"], cur["w"])
    v[f"err_hard_{tag}"] = rmse(*sets["hard"], cur["w"])
print(f"\n分两列报（标满 {v['n_final']} 条之后）：")
print(f"{'策略':<16}{'易例(°)':>10}{'难例(°)':>10}")
print(f"{'随机加':<16}{v['err_easy_random']:>10.4f}{v['err_hard_random']:>10.4f}")
print(f"{'按不确定性挑':<16}{v['err_easy_active']:>10.4f}{v['err_hard_active']:>10.4f}")
v["hard_gain_pct"] = (1 - v["err_hard_active"] / v["err_hard_random"]) * 100
v["easy_loss_pct"] = (v["err_easy_active"] / v["err_easy_random"] - 1) * 100
assert v["err_hard_active"] < v["err_hard_random"], "挑数据应当把难例那一列压下去"
print(f"**挑数据把难例误差压了 {v['hard_gain_pct']:.0f}%，代价是易例误差涨 "
      f"{v['easy_loss_pct']:.0f}%**——这笔交易划不划算，要看你在哪条路上跑")

print("\n这个算例回答不了什么：真数据闭环的瓶颈不在“挑哪一批”，而在**标注质量与一致性**、"
      "回传带宽、隐私与合规；杠杆值只对线性（或近线性）模型有现成的闭式解，"
      "深度模型要用集成、丢弃法或预测熵来近似，那几种之间并不等价；"
      "本算例的难例是人为造出来的，真路上的难例靠什么发现，本身就是一个未解决的问题。")

out(**v)
