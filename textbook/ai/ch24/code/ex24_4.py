"""算例 24.4：奖励塑形的副作用——累计奖励与真实成功率**背离**（第 20、21 章的回声）。

到达并抓取这个任务，真实目标只有一个：**夹爪闭合的那一刻落在双阈值里**（成功 +20 分）。
为了让学习快一点，工程上常加一个“塑形项”：离目标越近，每一步都给一点奖励
（这里取 w·exp(−d/3 cm)）。塑形项本身没错，错在**它改变了最优行为**。

做法：在一个只有两个参数的小策略族里搜“累计奖励最高”的那一版
（触发闭合的半径 `close_at`，取 0 就是永不闭合；绕着工件打转的幅度 `hover`），
然后把**累计奖励**与**真实任务成功率**两条曲线并排画出来。

要看的：塑形权重一过某个值，搜出来的最优行为就从“走过去、抓住”变成
**“贴着工件来回转、永远不闭合夹爪”**——因为闭合会结束回合，等于主动放弃后面每一步的塑形奖励。
这时累计奖励一路上升，真实成功率掉到 0。这就是“刷奖励”。
"""
import numpy as np

from _ch24 import SIM, STEPS, rollout, sample_starts, sample_targets, servo_policy
from bookout import out

D0 = 0.03                 # 塑形项的尺度（m）：离目标 3 cm 时拿到 e^{-1} 的奖励，显式假设
TASK_BONUS = 20.0         # 真实任务奖励：抓成一次 +20 分，显式假设
WEIGHTS = (0.0, 0.1, 0.2, 0.4, 0.8, 1.0, 1.2, 1.6, 2.4)
CLOSE_AT = (0.0, 0.006, 0.012, 0.020)      # 0 = 永不闭合
HOVER = (0.0, 0.4, 0.9)
N_EP = 40

v = {"d0_m": D0, "task_bonus": TASK_BONUS, "weights": list(WEIGHTS), "n_episodes": N_EP,
     "close_at_grid": list(CLOSE_AT), "hover_grid": list(HOVER), "steps_max": STEPS}

poses = sample_targets(N_EP, seed=21)
starts = sample_starts(N_EP, seed=21, spread=0.25)


def run(close_at, hover, w):
    """跑一遍，返回（平均累计奖励，真实成功率%，平均闭合步数）。"""
    rew, suc, tc = [], [], []
    for k, (pose, q0) in enumerate(zip(poses, starts)):
        r = rollout(servo_policy(gain=3.5, close_at=close_at, hover=hover),
                    pose, q0, SIM, seed=k + 5)
        n = r["n_steps"]
        d = np.linalg.norm(r["tip"][1:n + 1, :2] - pose[:2], axis=1)
        shaped = w * float(np.exp(-d / D0).sum())
        rew.append(shaped + (TASK_BONUS if r["success"] else 0.0))
        suc.append(r["success"])
        tc.append(n)
    return float(np.mean(rew)), float(np.mean(suc)) * 100, float(np.mean(tc))


best_rew, best_succ, best_params, farm = [], [], [], []
print(f"塑形权重　累计奖励最高的那一版：奖励　真实成功率　(触发半径, 打转幅度)")
for w in WEIGHTS:
    cand = []
    for c in CLOSE_AT:
        for h in HOVER:
            R, S, T = run(c, h, w)
            cand.append((R, S, c, h, T))
    cand.sort(key=lambda z: -z[0])
    R, S, c, h, T = cand[0]
    best_rew.append(R)
    best_succ.append(S)
    best_params.append([c, h])
    farm.append(c == 0.0)
    print(f"  {w:6.2f}　{R:9.2f}　{S:9.1f}%　({c:.3f} m, {h:.1f})"
          f"　平均 {T:.0f} 步结束")

best_rew = np.array(best_rew)
best_succ = np.array(best_succ)
v["reward_curve"] = best_rew.tolist()
v["success_curve"] = best_succ.tolist()
v["best_params"] = best_params
v["farming"] = [bool(f) for f in farm]

# ---------- 一、两条曲线背离
i_farm = int(np.argmax(farm)) if any(farm) else -1
v["w_no_shaping"] = float(WEIGHTS[0])
v["succ_no_shaping"] = float(best_succ[0])
v["rew_no_shaping"] = float(best_rew[0])
assert any(farm), "权重够大时，最优行为必须变成“永不闭合”——否则这个算例没算出该算的东西"
v["w_farm"] = float(WEIGHTS[i_farm])
v["succ_farm"] = float(best_succ[i_farm])
v["rew_farm"] = float(best_rew[i_farm])
v["rew_ratio"] = v["rew_farm"] / max(v["rew_no_shaping"], 1e-9)
print(f"\n不加塑形（w = 0）：最优行为是走过去抓住，成功率 {v['succ_no_shaping']:.1f}%，"
      f"累计奖励 {v['rew_no_shaping']:.2f}")
print(f"塑形权重加到 {v['w_farm']:.2f}：最优行为变成**贴着工件来回转、永不闭合夹爪**，"
      f"累计奖励涨到 {v['rew_farm']:.2f}（{v['rew_ratio']:.1f} 倍），"
      f"真实成功率 {v['succ_farm']:.1f}%")
assert v["rew_farm"] > v["rew_no_shaping"] and v["succ_farm"] < v["succ_no_shaping"] - 50.0, \
    "存在一个权重使累计奖励上升而任务成功率下降——这是本算例的主结论"
print("**两条曲线背离**：奖励这条一路上升，成功率那条掉到地板上。"
      "只盯奖励曲线验收，这个策略看起来是全场最好的")

# ---------- 二、临界权重在哪里，怎么估
# 刷奖励的收益 ≈ w × 每步约 1 分 × 剩下的步数；闭合的收益 = 任务分 + 走过去那段的塑形分。
v["w_critical"] = float(WEIGHTS[i_farm])
v["w_last_good"] = float(WEIGHTS[i_farm - 1]) if i_farm > 0 else None
v["bonus_over_steps"] = TASK_BONUS / STEPS
# 第 175 轮补：正文要印塑形尺度与“临界权重是这个数的几倍”
v["d0_cm"] = D0 * 100
v["w_critical_over_bonus"] = v["w_critical"] / v["bonus_over_steps"]
print(f"\n临界权重落在 {v['w_last_good']:.2f} 与 {v['w_critical']:.2f} 之间。"
      f"量级可以手估：任务分 {TASK_BONUS:.0f} 分摊到 {STEPS} 步，每步 "
      f"{v['bonus_over_steps']:.2f} 分——**塑形项每步给的奖励一旦接近这个数，"
      f"刷奖励就比完成任务划算**")
assert abs(v["w_critical"] - v["bonus_over_steps"]) < 1.2, \
    "临界权重与“任务分摊到每步”的量级对得上——这是能手估的，不必靠扫"
print("所以塑形项的权重不是“调一调看效果”，**它和任务分的比例决定了最优行为是什么**")

# ---------- 三、这件事该怎么防
rew_at_true_best, succ_at_true_best = [], []
for wi, w in enumerate(WEIGHTS):
    cand = [(run(c, h, w), c, h) for c in CLOSE_AT if c > 0 for h in HOVER]
    cand.sort(key=lambda z: -z[0][0])
    rew_at_true_best.append(cand[0][0][0])
    succ_at_true_best.append(cand[0][0][1])
v["succ_if_close_forced"] = succ_at_true_best
v["succ_drop_avoided"] = float(np.mean(succ_at_true_best) - np.mean(best_succ))
print(f"\n把“必须闭合夹爪”写成硬约束（不允许 close_at = 0）之后，"
      f"同样扫一遍权重，成功率平均高 {v['succ_drop_avoided']:.1f} 个百分点，"
      f"最低也有 {min(succ_at_true_best):.1f}%")
assert min(succ_at_true_best) > 30.0, "约束住“必须闭合”之后，塑形权重再大也不会刷奖励"
print("**两件事一起做**：①验收看真实任务判据，不看奖励；"
      "②把“必须完成”写成硬约束或终止条件，别只写在奖励里。"
      "这正是第 20、21 章那条规矩在机器人上的样子")
print("这个算例回答不了什么：这里的策略族只有两个参数，所以“刷奖励”的行为一眼能认出来。"
      "真策略有几百万参数，刷的方式千奇百怪（蹭着判据边缘、利用仿真器的穿模），"
      "**只能靠真实判据下的验收去发现**")

out(**v)
