"""算例 24.2：域随机化有没有用——仿真与真机**两列分开报**。

做法：在“仿真”里训（可选是否随机化摩擦、连杆长度、观测噪声、执行延迟），
训完之后在两套参数上各验收一遍：**标称仿真参数**一列，**真机参数**一列。
扫随机化的范围，看两列各怎么变。

要看的三件事：

（1）**不随机化的那一版，仿真里很漂亮，真机上可以是零**。本算例跑出来的正是这个：
    仿真成功率几十个百分点，真机成功率 0——这就是本章第一号引用警告的玩具版；
（2）**范围有个最佳值**：太窄盖不住真机，太宽则同一个观测对应的专家动作互相矛盾，
    策略只能学个平均，两列一起掉。合起来是一条**倒 U 形**曲线；
（3）**两列必须分开报，而且真机那一列要写明试了多少次**（本章口径 b）。

域随机化在这里为什么能起作用，道理很具体：观测里有**量出来的夹爪位姿**。
只在标称参数下训，策略可以偷懒——按固定的连杆长度心算一套正运动学就够了，
于是连杆一变就错；见过各种连杆长度之后，这条捷径不管用，最小二乘只好去用
“工件位姿 − 量出来的夹爪位姿”这个误差项，而**这个误差项在真机上照样成立**。
"""
import numpy as np

from _ch24 import (DEGREE, REAL, SIM, evaluate, make_policy, randomized_world,
                   sample_starts, sample_targets, train_policy)
from bookout import out

SCALES = (0.0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0, 1.3)
N_EPISODES = 160                  # 每个范围训练用的回合数（专家标注预算，各范围相同）
N_TEST = 80                       # 验收回合数：两列都是这个数

v = {"scales": list(SCALES), "n_episodes": N_EPISODES, "n_trials_sim": N_TEST,
     "n_trials_real": N_TEST, "degree": DEGREE}
v["sim_params"] = {k: SIM[k] for k in ("l1", "l2", "friction", "obs_noise", "delay")}
v["real_params"] = {k: REAL[k] for k in ("l1", "l2", "friction", "obs_noise", "delay")}
print(f"仿真参数：{v['sim_params']}")
print(f"真机参数：{v['real_params']}（四样各差一点，**这才是真机**）")

test_poses = sample_targets(N_TEST, seed=11)
test_starts = sample_starts(N_TEST, seed=11, spread=0.25)

sim_succ, real_succ = [], []
print(f"\n随机化范围　仿真成功率　真机成功率（两列各试 {N_TEST} 次）")
for scale in SCALES:
    def world_of(i, g, s=scale):
        return SIM if s == 0.0 else randomized_world(SIM, s, g)

    W = train_policy(N_EPISODES, rounds=4, world_of=world_of, seed=0)
    pol = (lambda p, w: make_policy(W, DEGREE))
    rs = evaluate(pol, test_poses, test_starts, SIM, seed=7)
    rr = evaluate(pol, test_poses, test_starts, REAL, seed=7)
    sim_succ.append(rs["success_pct"])
    real_succ.append(rr["success_pct"])
    print(f"  {scale:9.2f}　{rs['success_pct']:9.1f}%　{rr['success_pct']:9.1f}%"
          f"　（真机平均位置误差 {rr['pos_err'] * 100:.2f} cm）")

sim_succ = np.array(sim_succ)
real_succ = np.array(real_succ)
v["sim_success_pct"] = sim_succ.tolist()
v["real_success_pct"] = real_succ.tolist()

# ---------- 一、不随机化：仿真漂亮，真机归零
v["sim_no_rand"], v["real_no_rand"] = float(sim_succ[0]), float(real_succ[0])
v["gap_no_rand"] = v["sim_no_rand"] - v["real_no_rand"]
print(f"\n不随机化（范围 0）：仿真 {v['sim_no_rand']:.1f}%，真机 {v['real_no_rand']:.1f}%，"
      f"差 {v['gap_no_rand']:.1f} 个百分点")
print("**只有仿真那一列的结果不采信**——这一行就是理由")

# ---------- 二、最好的范围在哪里
i_best = int(np.argmax(real_succ))
v["best_scale"] = float(SCALES[i_best])
v["real_best"] = float(real_succ[i_best])
v["sim_at_best"] = float(sim_succ[i_best])
v["real_gain"] = v["real_best"] - v["real_no_rand"]
print(f"真机成功率最高的范围：{v['best_scale']:.2f}（真机 {v['real_best']:.1f}%，"
      f"同一版在仿真里 {v['sim_at_best']:.1f}%），比不随机化多 {v['real_gain']:.1f} 个百分点")
assert v["real_best"] > v["real_no_rand"] + 20.0, \
    "存在一个范围使真机成功率显著高于不随机化——这是本算例的主结论"

# ---------- 三、最宽的范围不是最好的
v["widest_scale"] = float(SCALES[-1])
v["real_widest"] = float(real_succ[-1])
v["sim_widest"] = float(sim_succ[-1])
v["real_drop_from_best"] = v["real_best"] - v["real_widest"]
v["sim_drop_from_best"] = v["sim_at_best"] - v["sim_widest"]
print(f"最宽的范围 {v['widest_scale']:.2f}：仿真 {v['sim_widest']:.1f}%、"
      f"真机 {v['real_widest']:.1f}%——比最好的那档真机低 {v['real_drop_from_best']:.1f}、"
      f"仿真低 {v['sim_drop_from_best']:.1f} 个百分点")
assert i_best not in (0, len(SCALES) - 1), "最好的范围在中间，不在两端——这就是倒 U 形"
assert v["real_widest"] < v["real_best"], "最宽的不是最好的"
assert v["sim_widest"] < v["sim_at_best"], "范围太宽，连仿真那一列都掉"
print("**倒 U 形**：太窄盖不住真机，太宽则同一个观测对应的专家动作互相矛盾，"
      "策略只能学个平均，两列一起掉")

# ---------- 四、报表长什么样
v["table"] = [[float(s), float(a), float(b)] for s, a, b in zip(SCALES, sim_succ, real_succ)]
print(f"\n这张表就是本章要的报表格式：**随机化范围 / 仿真成功率 / 真机成功率 / 真机试了多少次**"
      f"（{N_TEST} 次）。")
print(f"少一列都不行：只看仿真那一列，会以为不随机化最好（{v['sim_no_rand']:.1f}% 是全表最高之一）；"
      f"而真机那一列里它是 {v['real_no_rand']:.1f}%")
print(f"这个案例回答不了什么：这里的“真机”也是算出来的，真设备上还有接触、形变、"
      f"相机标定、工件滑动——所以真机那一列只能靠**真的试**，试多少次也必须报")

out(**v)
