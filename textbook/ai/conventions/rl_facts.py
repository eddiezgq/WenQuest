"""博弈与强化学习的公开发表数字（第 15 章用；第 13、24 章可引）。

规矩与 `llm_facts.py`、`mm_facts.py` 相同：**只收论文正文、官方技术报告或官方公告给出的原始数字**；
媒体估算、第三方转述一律不收；未公布的项用 `UNPUBLISHED` 标出，正文写“未公布”；
由原始值算出来的倍数与换算，注释里标“折算”。
每条的出处、口径与“为什么不能横向比较”见
`docs/教材/人工智能/参考/第15章_强化学习原始数字资料_2026-10.md`。核对日期：2026 年 10 月 31 日。
"""

UNPUBLISHED = None                      # 未公布：正文写“未公布”

# ---------------------------------------------------------------- DQN（Mnih 等 2015，Nature）
DQN = {
    "games": 49,                        # 49 款 Atari 游戏，每款单独训练，超参完全相同
    "beat_prior_rl": 43,                # 超过此前最好强化学习方法的款数
    "above_75pct_human": 29,            # 达到人类得分 75% 以上的款数（论文真正给的“接近人类”口径）
    "median_human_norm": UNPUBLISHED,   # 人类归一化中位数：论文未给（常引的数出自后续论文）
    "frames": 50_000_000,               # 每款 5000 万帧，论文称约等于 38 天的“游戏内”经验
    "game_days": 38,
    "skip": 4,                          # 跳帧 k=4 → 折算约 1250 万个决策步
    "replay": 1_000_000,                # 回放池：最近 100 万帧
    "eps_from": 1.0, "eps_to": 0.1, "eps_frames": 1_000_000,
    "eps_eval": 0.05,
    "batch": 32, "gamma": 0.99,
    "input": (84, 84, 4),
    "clip_reward": 1.0,                 # 奖励裁到 ±1：跨游戏共用一套超参的关键一步
    "target_every": UNPUBLISHED,        # 目标网络更新间隔 C：在 Extended Data Table 1，本次未读到
    "hardware": UNPUBLISHED,            # 训练硬件与墙钟时长：论文完全没写
}
DQN2013 = {"games": 7, "frames": 10_000_000, "target_net": False}   # workshop 版没有独立目标网络

# ---------------------------------------------------------------- AlphaGo（Silver 等 2016，Nature）
ALPHAGO = {
    "policy_layers": 13, "filters": 192,
    "acc_policy": 57.0, "acc_policy_simple": 55.7, "acc_prior_best": 44.4,
    "acc_rollout": 24.2, "us_rollout": 2.0, "ms_policy": 3.0,     # 走子 2 微秒 vs 策略网络 3 毫秒
    "kgs_games": 160_000, "kgs_positions": 29_400_000,            # 16 万局、2940 万个局面
    "value_positions": 30_000_000,                                # 每局只取一个局面，避免相关
    "fan_hui": (5, 0),                                            # 正式对局 5–0（非正式快棋 3–2）
    "dist_cpu": 1202, "dist_gpu": 176, "single_cpu": 48, "single_gpu": 8,
    "elo_dist": 3140, "elo_single": 2890, "elo_crazystone": 1929, "elo_pachi": 1298,
    "wins": 494, "games_vs_programs": 495,                        # 495 局胜 494 局
    "train_sl_gpu": 50, "train_sl_weeks": 3,                      # 监督策略网络：50 块 GPU、约 3 周
    "sims_per_move": UNPUBLISHED,                                 # 论文没有直接给每步模拟次数
}

# ---------------------------------------------------------------- AlphaGo Zero（Silver 等 2017，Nature）
ALPHAGO_ZERO = {
    "selfplay_games_3d": 4_900_000, "days_3d": 3,
    "selfplay_games_40d": 29_000_000, "days_40d": 40,
    "batches_3d": 700_000, "batch": 2048,
    "sims_per_move": 1600, "sec_per_move": 0.4,
    "tpu_play": 4,                       # 对局用 4 块 TPU（训练硬件论文只给 64 个 GPU worker）
    "tpu_train": UNPUBLISHED,
    "vs_lee": (100, 0), "vs_master": (89, 11),
    "elo_zero40": 5185, "elo_master": 4858, "elo_lee": 3739, "elo_fan": 3144,
    "elo_raw_net": 3055,                 # 不带搜索的裸网络：讲“搜索值多少 Elo”的原始数字
    "lee_tpu": 48,
    "acc_zero20": 49.0, "acc_zero40": 51.3, "acc_supervised": 54.3,   # 同一验证集（GoKifu）
}

# ---------------------------------------------------------------- AlphaZero（两版数字不同，必须分开引）
ALPHAZERO_ARXIV = {   # 2017-12 预印本
    "hours_chess": 9, "hours_shogi": 12, "hours_go": 34,
    "tpu_selfplay": 5000, "tpu_train": 64, "tpu_play": 4,
    "steps": 700_000, "batch": 4096, "sims_per_move": 800,
    "nps_chess": 80_000, "nps_shogi": 40_000, "nps_go": 16_000,
    "nps_stockfish": 70_000_000, "nps_elmo": 35_000_000,
    "vs_stockfish": (28, 72, 0),         # 100 局：28 胜 72 和 0 负
}
ALPHAZERO_SCIENCE = {   # 2018 Science 版
    "hours_chess": 9, "hours_shogi": 12, "days_go": 13,
    "tpu_selfplay": 5000, "tpu_train": 16, "tpu_play": 4,
    "nps_chess": 63_000, "nps_shogi": 58_000, "nps_go": 16_000,
    "nps_stockfish": 58_100_000, "nps_elmo": 25_100_000,
    "vs_stockfish_1000": (155, 6),       # 1000 局：155 胜 6 负，其余和
    "elmo_black_winrate": 98.2, "elmo_total_winrate": 91.2,
    "vs_agz_winrate": 61,
}

# ---------------------------------------------------------------- MuZero（Schrittwieser 等 2020，Nature）
MUZERO = {
    "atari_games": 57,
    "mean_human_norm": 4999.2, "median_human_norm": 2041.1,       # 30 次 no-op 开局口径
    "r2d2_mean": 4024.9, "r2d2_median": 1920.6,
    "sims_board": 800, "sims_atari": 50,                          # Atari 只用 50 次模拟
    "batches": 1_000_000, "batch_board": 2048, "batch_atari": 1024, "unroll_K": 5,
    "tpu_train_board": 16, "tpu_selfplay_board": 1000,
    "tpu_train_atari": 8, "tpu_selfplay_atari": 32,
    "frames_atari": 20_000_000_000, "hours_atari": 12,
    "reanalyze_frames": 200_000_000, "reanalyze_median": 731.1,
    "elo_board": UNPUBLISHED,                                     # 棋类 Elo：论文没给
}

# ---------------------------------------------------------------- 不完全信息博弈
LIBRATUS = {
    "pros": 4, "hands": 120_000, "days": 20,
    "mbb_per_hand": 147, "p_value": 0.0002,
    "decision_points": 1e161,                                     # 两人无限注德扑的决策点数
    "compute": UNPUBLISHED,                                       # 算力：论文没给
}
PLURIBUS = {
    "pros_pool": 13, "hands_exp1": 10_000, "days_exp1": 12,
    "mbb_exp1": 48, "se_exp1": 25, "p_exp1": 0.028,
    "mbb_exp2": 32, "se_exp2": 15, "p_exp2": 0.014,
    "core_hours": 12_400, "cores": 64, "days_train": 8,           # 蓝图策略：64 核 8 天
    "usd": 144,                                                   # 论文自己给的云端成本估算
    "ram_gb": 512, "sec_per_hand": 20,
    "gpu": 0,                                                     # 全程只用 CPU
    "alphago_search_cpu": 1920, "alphago_search_gpu": 280,        # 论文自己给的对照
}

# ---------------------------------------------------------------- AlphaStar / OpenAI Five
ALPHASTAR = {
    "percentile": 99.8,                 # 论文原话“超过 99.8% 的排位玩家”（不是 98.x%）
    "mmr_protoss": 6275, "mmr_terran": 6048, "mmr_zerg": 5835, "mmr_supervised": 3699,
    "ladder_games": 360, "league_days": 44,
    "tpu_per_agent": 32, "agents": 12, "players": 900,
    "league_games": 130_000_000,
    "replays": 971_000,
    "actions_per_5s": 22,               # 每 5 秒窗口最多 22 个非重复动作（不是 APM 上限）
    "delay_ms": 110, "params": 139_000_000,
    "vs_pros_final": UNPUBLISHED,       # 最终版对职业选手的战绩：论文没给
}
OPENAI_FIVE = {
    "train_days": 180,                  # 有效训练天数（日历十个月）
    "pflops_days_og": 770, "pflops_days_end": 820,
    "gpu_peak": 1536, "cpu_peak": 172_800,
    "vs_og": (2, 0), "arena_games": 7257, "arena_winrate": 99.4,
    "params": 159_000_000, "lstm": 4096,
    "obs_values": 16_000, "actions_min": 8000, "actions_max": 80_000,
    "reaction_ms": 217,
    "rerun_months": 2, "rerun_pflops_days": 150, "rerun_winrate": 98,
    "surgeries": 20,
    "blog_gpu": 256, "blog_cpu": 128_000, "blog_years_per_day": 180, "blog_reaction_ms": 80,
}

# ---------------------------------------------------------------- 并行仿真的吞吐
ISAAC_GYM = {
    "gpu": "A100",
    "ant_steps_per_s": 700_000, "ant_envs": 8192,
    "humanoid_steps_per_s": 200_000, "humanoid_envs": 4096,
    "hand_steps_per_s": 150_000, "hand_envs": 16_384,
    "envs_min": 256, "envs_max": 16_384,
    "speedup_lo": 100, "speedup_hi": 1000,         # 论文措辞：整条流水线快 100—1000 倍
    "openai_baseline_cores": 6144, "openai_baseline_v100": 8, "openai_baseline_hours": 30,
    "ant_sec_to_reward3000": 20,
}
ENVPOOL = {
    "atari_fps": 1_069_922, "mujoco_steps_per_s": 3_134_287,      # DGX-A100（256 核）
    "atari_subprocess": 71_943, "mujoco_subprocess": 163_656,
    "speedup_atari": 14.9, "speedup_mujoco": 19.2,
    "cores": 256,
}

# ---------------------------------------------------------------- Kuhn 扑克与 CFR
KUHN = {
    "alpha_lo": 0.0, "alpha_hi": 1 / 3,          # 均衡族：先手拿最小牌虚张的概率 α ∈ [0, 1/3]
    "game_value": -1 / 18,                       # 先手的期望收益（任何均衡下都一样）
    "source": "Kuhn 1950《Simplified Two-Person Poker》第 101 页（本书转引，未核原书）",
}
CFR = {
    "bound": "R_i^T ≤ Δ_i · |I_i| · sqrt(|A_i|) / sqrt(T)",       # Zinkevich 等 2007 定理 4
    "eps_to_equilibrium": 2,                     # 定理 2：两人零和下平均遗憾 < ε → 2ε-均衡
    "zinkevich_iters": 2_000_000_000, "zinkevich_hours": 326, "zinkevich_cpus": 4,
    "zinkevich_exploit_mbh": 2.2,
    "abstraction_states": 1.65e12, "full_states": 9.17e17,
    "abstraction_infosets": 5.73e7, "full_infosets": 3.19e14,
}
