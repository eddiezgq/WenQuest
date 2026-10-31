"""算例 15.7.1—15.7.3：强化学习的算力花在哪（15.7 节）。

（1）一次训练要跑多少环境步：按本章与公开论文的规模各算一遍。
（2）吞吐决定墙钟时间：同样的环境步数，在 CPU 单进程、CPU 多进程、GPU 并行仿真上各要多久。
（3）并行仿真为什么快：把环境搬到显卡上，数据就不必来回搬——回扣 1.5 节的计算强度与第 6 章的流。
"""
import numpy as np

from bookout import out
from rl_facts import DQN, ENVPOOL, ISAAC_GYM, MUZERO, OPENAI_FIVE

v = {}
# ---------- （1）要跑多少环境步
v["dqn_frames_M"] = DQN["frames"] / 1e6
v["dqn_steps_M"] = DQN["frames"] / DQN["skip"] / 1e6
v["dqn_games"] = DQN["games"]
v["dqn_total_steps_yi"] = DQN["frames"] / DQN["skip"] * DQN["games"] / 1e8     # 折算：49 款各一个网络
v["mz_frames_yi"] = MUZERO["frames_atari"] / 1e8
v["mz_games"] = MUZERO["atari_games"]
v["of_pflops_days"] = OPENAI_FIVE["pflops_days_og"]

# ---------- （2）吞吐决定墙钟时间
STEPS = 1e9                                   # 一次中等规模训练：十亿个环境步
v["steps_1e9"] = STEPS
rows = []
for name, fps in (("单进程 Python 循环", ENVPOOL["atari_subprocess"] / 15),      # 表 1 的 for-loop 量级
                  ("多进程（subprocess）", ENVPOOL["atari_subprocess"]),
                  ("EnvPool（256 核）", ENVPOOL["atari_fps"]),
                  ("Isaac Gym（一块 A100）", ISAAC_GYM["ant_steps_per_s"])):
    rows.append((name, int(fps), round(STEPS / fps / 86400, 2)))
v["fps_rows"] = rows                          # （做法, 每秒多少环境步, 跑完十亿步要多少天）
v["days_slow"], v["days_fast"] = rows[0][2], rows[-1][2]
v["speedup"] = v["days_slow"] / v["days_fast"]
assert v["speedup"] > 100, "换一套仿真，墙钟时间差两个数量级以上"
v["envpool_fps"] = ENVPOOL["atari_fps"]
v["envpool_sub"] = ENVPOOL["atari_subprocess"]
v["envpool_speedup"] = ENVPOOL["speedup_atari"]
v["envpool_cores"] = ENVPOOL["cores"]
v["ig_ant_fps"], v["ig_ant_envs"] = ISAAC_GYM["ant_steps_per_s"], ISAAC_GYM["ant_envs"]
v["ig_hand_fps"], v["ig_hand_envs"] = ISAAC_GYM["hand_steps_per_s"], ISAAC_GYM["hand_envs"]
v["ig_per_env"] = ISAAC_GYM["ant_steps_per_s"] / ISAAC_GYM["ant_envs"]          # 折算：每个环境每秒几步
v["ig_envs_min"], v["ig_envs_max"] = ISAAC_GYM["envs_min"], ISAAC_GYM["envs_max"]
v["ig_speedup_lo"], v["ig_speedup_hi"] = ISAAC_GYM["speedup_lo"], ISAAC_GYM["speedup_hi"]
v["ig_ant_sec"] = ISAAC_GYM["ant_sec_to_reward3000"]
v["openai_cores"], v["openai_v100"], v["openai_hours"] = (
    ISAAC_GYM["openai_baseline_cores"], ISAAC_GYM["openai_baseline_v100"], ISAAC_GYM["openai_baseline_hours"])

# ---------- （3）数据搬运的账
# 一个环境的观测有多大、每秒要搬多少：这是"把仿真搬上显卡"省下的那一笔
OBS_DIM, BYTES = 60, 4                        # 机器人仿真里一个观测几十个数（关节角、速度……）
v["obs_dim"], v["obs_bytes"] = OBS_DIM, BYTES
v["bytes_per_step"] = OBS_DIM * BYTES * 2     # 观测进、动作出，来回各一趟
v["gb_per_s"] = ISAAC_GYM["ant_steps_per_s"] * v["bytes_per_step"] / 1e9
v["pcie_gb_s"] = 32.0                         # PCIe 4.0 ×16 的单向带宽（第 6 章）
v["pcie_share"] = v["gb_per_s"] / v["pcie_gb_s"] * 100
# Atari 那一类的观测要大得多（84×84×4 的图）
v["atari_obs_bytes"] = int(np.prod(DQN["input"]))
v["atari_gb_per_s"] = ENVPOOL["atari_fps"] * v["atari_obs_bytes"] / 1e9
v["atari_pcie_share"] = v["atari_gb_per_s"] / v["pcie_gb_s"] * 100
assert v["atari_pcie_share"] > v["pcie_share"], "图像观测的搬运压力比低维状态大得多"
v["ratio_obs"] = v["atari_obs_bytes"] / (OBS_DIM * BYTES)
out(**v)
