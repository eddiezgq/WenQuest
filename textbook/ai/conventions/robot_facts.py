"""第 24 章（机器人与具身智能）要印的公开数字，一处定义、处处引用。

出处逐条记在
`docs/教材/人工智能/参考/第24章_机器人学习原始数字资料_2026-11.md`。

纪律与第 17—23 章同：只收论文正文、官方公告、官方文档、官方规格书里的原始值；
新闻稿、博客转述、维基不算（除非本身就是官方发布）。口径不全的进 `NOT_PRINTED`；
核不到的写 None 并在行内注明；凡“本书自己折算”的，逐条标明。

本章另有三条自己的纪律：

1. **不同论文、不同机器人之间的成功率一律不比较。** 任务、物体、场次数、判定标准都不同。
   所以本模块里**没有任何跨论文的成功率对照字段**，`check()` 会断言这类字段不存在。
2. **仿真成功率不是真机成功率。** 唯一允许并排出现的两列数来自同一篇论文、同一判据
   （见 `SIM2REAL_TRIFINGER`），而且两边的样本量必须跟着一起印（N=1024 与 N=40）。
3. **“每秒多少步”不是性能指标，而是（显卡、环境数、物理步长、任务）四元组的函数。**
   四样不全的吞吐数一律不收——Isaac Lab 官方基准页与 MuJoCo MJX 官方文档都缺物理步长，
   所以它们的数值只出现在 `NOT_PRINTED` 里。
"""
from __future__ import annotations

# ======================================== 一、模仿学习的数据与评测口径（24.2、24.3 节）

RT1 = {
    "demos": 130_000,                   # "over 130k individual demonstrations"
    "task_instructions_main_text": 700,  # 正文 "over 700 distinct task instructions"
    "tasks_model_card": 744,            # 附录模型卡 "13 robots and 744 tasks"——与正文不同口径
    "robots": 13,                       # "a fleet of 13 robots"
    "collection_months": 17,            # "over the course of 17 months"
    "teleop": "direct line-of-sight，2 virtual reality remotes（遥操作，非动觉示教）",
    "action_dims_arm": 7,               # "seven dimensions for the arm movement"
    "action_dims_base": 3,              # "three dimensions for base movement (x, y, yaw)"
    "action_bins": 256,                 # "discretized into 256 bins"，"uniformly distributed"
    "control_hz": 3,                    # "commands actions at 3 Hz"（策略下指令的频率，不是伺服频率）
    "params_m": 35,                     # "Despite its size (35M parameters)"
    "params_tokenizer_m": 16,           # FiLM EfficientNet-B3 共 16M
    "params_transformer_m": 19,         # Transformer 8 层自注意力，19M
    "eval_trials_total": 3000,          # "over 3000 real-world trials"（只有总数）
    "eval_tasks": 200,                  # "we test over 200 tasks"
    "eval_unseen_instructions": 21,
    "trials_per_task": None,            # 正文未给逐任务次数
    "success_judged_by": None,          # 真机判定由谁判、按什么判，正文未写
    "ref": "arXiv:2212.06817v2 §4、§5.1、§5.2、§6、§6.1 与附录/模型卡",
}

ALOHA_ACT = {
    "demos_per_task": 50,               # "We record 50 demonstrations for each task"
    "demos_thread_velcro": 100,         # "except for Thread Velcro which has 100"
    "episode_seconds": (8, 14),         # "8-14 seconds for the human operator to perform"
    "data_minutes_per_task": (10, 20),  # "around 10-20 minutes of data for each task"
    "wallclock_minutes_per_task": (30, 60),  # "30-60 minutes in wall-clock time"
    "teleop": "ALOHA teleoperation（主从同构臂遥操作）；a single person 采完全部演示",
    "control_hz": 50,                   # "Both the teleoperation and data recording happen at 50Hz"
    "action_dim": 14,                   # "absolute joint positions for two robots, a 14-dimensional vector"
    "action_is_target_joint_pos": True,  # 目标关节位置，不是增量
    "chunk_size": 100,                  # 正文只写 "chunk size to be k"，值 100 在附录 D 表 III
    "chunk_size_from_appendix": True,   # 引用时必须说明层级
    "real_trials_per_task": 25,         # "we run one seed and evaluate with 25 trials"
    "real_seeds": 1,
    "sim_trials_per_task": 50,          # "3 random seeds with 50 trials each"
    "sim_seeds": 3,
    "success_criterion": "逐任务物理判据，例：Put On Shoe 要 “shoe clings to the foot after both arms releases”",
    "subtask_scoring": True,            # "report the performance for each of these subtasks"
    "ref": "arXiv:2304.13705 §III、§IV、§IV-A、§IV-C、§V-A、§V-B、§V-C、附录 D",
}

DIFFUSION_POLICY = {
    "teleop_device": "3dconnexion SpaceMouse",
    "teleop_hz": 10,                    # "teleoperates the robot via a 3dconnexion SpaceMouse at 10Hz"
    "policy_hz": 10,                    # "Tele-op and learned policies run at 10Hz"
    "robot_cmd_hz": 125,                # "UR5 robot accepts end-effector space positional command at 125Hz"
    "midlevel_hz": 1000,                # "the mid-level controller runs around 1kHz"
    "real_demos_examples": (210, 162, 284),  # 三个真机任务的演示条数（同篇内部）
    "real_trials_per_task": 20,         # "evaluated for 20 episodes"，同一组初始条件
    "real_fixed_train_hours": 12,       # "a fixed training time of 12 hours for each method"
    "real_checkpoint": "last checkpoint",
    "sim_checkpoint_rule": "average of the last 10 checkpoints (saved every 50 epochs)",
    "sim_seeds": 3,
    "sim_inits": 50,                    # "3 training seeds and 50 environment initializations"
    "success_threshold": "按人类演示数据里最小的 IoU 取阈值（相对判据，不是绝对判据）",
    "action_horizon": 8,                # "action horizon of 8 steps to be optimal for most tasks"
    "receding_horizon": True,           # "receding horizon position control"
    "inference_latency_s": 0.1,         # "10 inference iterations enables 0.1s inference latency"
    "real_ddim_iters": 16,              # 附录 A.4 真机用 16 步——与 §3.4 的 10 步并存
    "robomimic_ph_tasks": 5,            # "5 tasks with a proficient human (PH) teleoperated demonstration dataset"
    "franka_kitchen_demos": 566,        # "a human demonstration dataset of 566 demonstrations"
    "ref": "arXiv:2303.04137 §2.3、§3.4、§5.1、§5.2、§5.3、§6.1、§7.3—§7.5、附录 A.4、C.1.2、D",
}

# ======================================== 二、视觉—语言—动作模型（24.4 节）

RT2 = {
    "inputs": "robot camera image and textual task description",
    "output": "a string of numbers/least frequently used tokens representing a robot action",
    "action_integers": 8,               # "8 integer numbers"（6-DoF 位移 + 夹爪 + 终止）
    "action_dof": 6,                    # "6-DoF positional and rotational displacement"
    "action_bins": 256,                 # "discretized into 256 bins uniformly"
    "action_string_sep": "space character",   # 用空格把各维 token 串起来
    "pali_x_vocab": "integers up to 1000 each have a unique token",
    "palm_e_vocab": "overwrite the 256 least frequently used tokens",
    "hz_55b": (1, 3),                   # "the 55B parameter RT-2-PaLI-X-55B model, can run at 1-3 Hz"
    "hz_5b": 5,                         # "around 5 Hz"
    "runs_on": "multi-TPU cloud service，经网络查询（不是机上推理）",
    "params_b_largest": 55,
    "params_b_palm_e": 12,
    "robot_data_same_as_rt1": True,     # "based on the dataset from Brohan et al."；13 robots over 17 months
    "eval_trials_total": 6000,          # "about 6,000 evaluation trajectories"
    "eval_tasks_seen": 200,             # "over 200 tasks"
    "eval_tasks_unseen": 280,           # "over 280 tasks"
    "trials_per_instruction": (1, 5),   # 附录 F.3：未见过类别的指令 run 1–5 times（分辨率很粗）
    "train_mixture_ratio": None,        # 正文混合比例本次未核到
    "ref": "RT-2，CoRL 2023 论文集（PMLR v229, Zitkovich et al.）§3.2、§3.3、§4、§4.1、附录 B、F.3",
}

# ======================================== 三、仿真到现实（24.5 节，本章最要紧的一条）

# **唯一允许并排出现的两列数**：同一篇、同一策略、同一判据；样本量必须跟着一起印。
SIM2REAL_TRIFINGER = {
    "task": "把物体移到目标位置与姿态并保持住",
    "success_pos_cm": 2.0,              # "within 2 cm"
    "success_rot_rad": 0.4,             # "orientation within 0.4 rad (22°)"
    "sim_success_pct_cube": 92.1,       # 表 III，立方体 6.5 cm
    "sim_trials": 1024,                 # "Numbers calculated from N=1024 trials in simulation"
    "real_success_pct": 82.5,           # §IV-D "the best policy achieved a success rate of 82.5%"
    "real_trials": 40,                  # "We performed N = 40 trials for each policy"
    "real_ci_pct": 80,                  # 图 10 的误差棒按 80% 置信区间算
    "abstract_rounds_to_pct": 83,       # 摘要写 83%，正文 82.5%——引正文
    "policy_hz": 50,                    # "the higher frequency of 50Hz that the policy is run at"
    "camera_hz": 10,
    "sim_dt_s": None,                   # 本次核到的正文段落未给物理步长
    "n_envs": 16_384,                   # 图 3 "16,384 environments in parallel"
    "gpu": "单块 NVIDIA Tesla V100 或 RTX 3090",
    "sim_is_not_real": True,            # **本章第一号引用警告**
    "ref": "arXiv:2108.09779 §III-A.1、§III-A.2、§III-E.1、§IV-A.1、§IV-C、§IV-D、表 III、图 3、图 7、图 10",
}

# ======================================== 四、GPU 并行物理仿真（24.6 节、GPU 实验 24.1）

# 收录门槛：显卡、环境数、物理步长、任务，四样齐全才收。
ISAAC_GYM = {
    "gpu": "单块 NVIDIA A100",           # "all experiments are done on a system with a single NVIDIA A100 GPU"
    "cpu": "单颗 3.7GHz Intel i7-8700K",
    "ant": {
        "task": "Ant",
        "peak_steps_per_s": 700_000,    # "can go as high as 700K"
        "train_avg_steps_per_s": 540_000,   # §6.1.1，4096 环境时训练过程中的平均值
        "n_envs_for_train_avg": 4096,   # "On A100 with 4096 agents simulated in parallel"
        "sim_dt_s": 1 / 120,            # 表 4
        "control_dt_s": 1 / 60,         # 表 4
        "action_dims": 8,
        "control_type": "Joint Torques",
        "reward_threshold_time": "3000 回报约 20 秒（墙钟，非性能指标）",
    },
    "humanoid": {
        "task": "Humanoid",
        "peak_steps_per_s": 200_000,    # "reduced from 700K for Ant to 200K for Humanoid"
        "n_envs_best": 4096,
        "sim_dt_s": 1 / 120,
        "control_dt_s": 1 / 60,
        "action_dims": 21,
        "control_type": "Joint Torques",
        "reward_threshold_time": "5000 回报约 4 分钟（墙钟）",
    },
    "shadow_hand": {
        "task": "Shadow Hand",
        "peak_steps_per_s": 150_000,    # "maximum effective frame-rate of 150K ... with 16384 agents"
        "n_envs_at_peak": 16_384,
        "sim_dt_s": 1 / 120,
        "control_dt_s": 1 / 60,         # OpenAI 口径那一行是 1/20 s——同任务两种控制 dt
        "control_dt_s_openai_obs": 1 / 20,
        "action_dims": 20,
        "control_type": "Joint Position Targets",
    },
    "anymal": {
        "task": "ANYmal",
        "sim_dt_s": 1 / 200,
        "control_dt_s": 1 / 50,
        "action_dims": 12,
        "control_type": "Joint Position Targets",
        "n_envs": 4096,
        "gpu": "NVIDIA RTX A6000",
        "train_to_transfer": "under 20 minutes",
        "steps_per_s": None,            # 该任务的吞吐论文未单列
    },
    "ref": "arXiv:2108.10470 §4 表 4、§5.1—§5.3、§6.1.1—§6.1.4、§6.4.1",
}

# MJX 官方文档里一条可以引的结构性事实（不是吞吐数）：
MJX_SINGLE_SCENE = {
    "statement": "MJX-JAX can be 10x slower than MuJoCo, which has been carefully optimized for CPU.",
    "meaning": "并行仿真的快，是靠成千上万个环境一起跑，不是单个场景跑得快",
    "steps_per_s": None,                # 吞吐数缺物理步长，进 NOT_PRINTED
    "ref": "MuJoCo 官方文档 MJX 页",
}

# ======================================== 五、UR5e 官方规格（24.7 节案例）

UR5E = {
    "payload_kg": 5.0,                  # "Payload 5 kg / 11 lbs"
    "reach_mm": 850,                    # "Reach 850 mm / 33.5 in"
    "repeatability_mm": 0.03,           # "Pose repeatability per ISO 9283 ± 0.03 mm"
    "repeatability_standard": "ISO 9283",   # **必须连标准一起写：是重复性，不是绝对定位精度**
    "dof": 6,                           # "6 rotating joints"
    "joint_range_deg": 360,             # 各关节 ±360°
    "joint_max_speed_deg_s": 180,       # 各关节 ±180°/s
    "power_moderate_w": 200,            # "Moderate operating settings 200 W"（口径仅此一句）
    "power_max_w": 570,                 # "Maximum power 570 W"
    "power_condition": "moderate operating settings——没有规定程序、负载与节拍",
    "weight_kg_pdf": 20.6,              # PDF：20,6 kg
    "weight_kg_web": 20.7,              # 在线数据表页：20,7 kg——两份官方资料差 0.1 kg
    "footprint_mm": 149,                # "Footprint Ø 149 mm"
    "ip_arm": "IP54",
    "ip_control_box": "IP44",
    "energy_per_hour": None,            # **不折算每小时/每件耗电：节拍与负载都没规定**
    "doc_version": None,                # 两份官方资料都只有 "Updated …" 月份，无文档编号
    "ref": ("Universal Robots 官方技术规格：在线数据表页 /manuals/latest/en/datasheets/ur5e/"
            "（Updated October 2026）与官方 e-Series 数据表 PDF media/1807465"
            "（Updated December 2024）"),
}

# ======================================== 六、足式 / 人形运动控制的结构性口径（24.8 节）

LEGGED_RL = {
    "n_envs": 4096,                     # "a policy trained with 4096 robots"
    "batch_size": 98_304,
    "gpu": "NVIDIA RTX A6000",          # 脚注 2："i9-11900k CPU, NVIDIA RTX A6000 GPU"
    "sim_dt_s": 0.005,                  # 附录 A.1.1
    "sim_steps_per_policy_step": 4,     # "four simulation steps per policy step"
    "policy_hz": 50,                    # **本书折算**：0.005 s × 4 = 0.02 s → 50 Hz（附录同处亦如此表述）
    "policy_hz_is_derived": True,
    "dt_limit_reason": "下限由 actuator network（近似离散 PD 控制器）失稳决定，不是仿真本身",
    "train_minutes_flat": 4,            # "under four minutes" 平地
    "train_minutes_rough": 20,          # "twenty minutes for uneven terrain"
    "policy_updates": 1500,
    "robot": "ANYbotics ANYmal C",
    "action_is_target_joint_pos": True,  # "send the produced actions as target joint positions"
    "no_filtering": True,               # "We do not apply any additional filtering or constraint satisfaction checks."
    "cmd_max_lin_vel_m_s": 0.6,         # **指令上限**，不是机器人最快速度
    "hardware_control_hz": None,        # 真机侧频率正文未给
    "steps_per_s": None,                # 吞吐正文未报（只有附录图 8 的曲线）
    "max_speed_m_s": None,              # 性能数字一律不收
    "jump_height_m": None,
    "ref": "arXiv:2109.11978v2 摘要、§3、§4.1、§4.2（含脚注 2）、§4.3、附录 A.1.1、A.4",
}

# 官方 Isaac Lab 基准页里只取结构性事实（环境数），该页缺 dt，FPS 不收：
HUMANOID_ENV_COUNT_ISAACLAB = {
    "task": "Isaac-Velocity-Rough-G1-v0",
    "n_envs": 4096,
    "gpus_listed": ("RTX 4090", "L40"),
    "sim_dt_s": None,                   # 官方页没给 dt 与 decimation
    "fps_not_collected": True,          # 四样不全 → 见 NOT_PRINTED
    "ref": "Isaac Lab 官方 Performance Benchmarks 页（v2.3.0 文档，页脚 IsaacSim-6.2.0）",
}

# ======================================== 七、本章明确不印的数

NOT_PRINTED = {
    "cross_paper_success": ("不同论文、不同机器人之间的成功率比较——任务、物体、场次数"
                            "（25 / 20 / 40 / 1024）、判定标准都不同，本章不设横向成功率表"),
    "sim_as_real": "把仿真成功率当真机成功率印（见本章第一号引用警告）",
    "cross_framework_fps": "Isaac Gym / Isaac Lab / MuJoCo MJX 之间的 FPS、SPS 比较——口径根本不同",
    "isaaclab_fps": ("Isaac Lab 官方基准页的 FPS（RTX 4090 Cartpole 1.1M 等）——"
                     "显卡、任务、环境数都有，但缺物理步长与 decimation，且 FPS 单位未定义"),
    "mjx_sps": ("MuJoCo MJX 官方文档的 steps/second（A100 batch 8192、8 芯 v5 TPU batch 16384 那组，"
                "以及 MJX-Warp 的百万级 SPS 表）——缺物理步长；Warp 那张表连硬件与批量都没给"),
    "rt1_trials_per_task": "RT-1 每个任务试多少次、真机成功由谁判定按什么判定——正文未给",
    "rt2_mixture": "RT-2 的训练数据混合比例——本次未核到正文原文",
    "legged_performance": ("足式/人形机器人的运动性能数字（最高速度、跳跃高度、续航）——"
                           "未核到含测试条件的论文正文；Rudin 文里的 0.6 m/s 是指令上限"),
    "trifinger_sim_dt": "TriFinger 论文的仿真物理步长——本次核到的正文段落未给",
    "ur5e_energy": "UR5e 的每小时/每件耗电折算——官方只给 200 W（moderate settings）与峰值 570 W",
    "ur5e_doc_version": "UR5e 官方文档的版本号——两份官方资料都只有 “Updated …” 月份",
    "legged_hw_hz_and_fps": "Rudin et al. 的真机控制频率与吞吐数值——正文未给",
    "aloha_chunk_as_main_text": "把 ALOHA/ACT 的动作块大小 100 当成正文结论——该值只在附录超参表",
}


def check() -> None:
    """几条最容易被引错的，用断言钉住。"""
    # —— 第一号引用警告：仿真成功率不是真机成功率，而且两边样本量差 25 倍
    assert SIM2REAL_TRIFINGER["sim_is_not_real"], "仿真成功率不是真机成功率"
    assert SIM2REAL_TRIFINGER["sim_success_pct_cube"] > SIM2REAL_TRIFINGER["real_success_pct"], \
        "同一篇、同一判据下仿真 92.1% 高于真机 82.5%——落差本身就是 24.5 节要讲的东西"
    assert SIM2REAL_TRIFINGER["sim_trials"] == 1024 and SIM2REAL_TRIFINGER["real_trials"] == 40, \
        "这两个成功率只能连 N=1024 与 N=40 一起印"
    assert SIM2REAL_TRIFINGER["sim_dt_s"] is None, "TriFinger 的物理步长未核到，不许补"

    # —— 跨论文比较：这类字段一律不许存在
    g = globals()
    for banned in ("SUCCESS_COMPARISON", "SUCCESS_RATE_TABLE", "CROSS_PAPER_SUCCESS",
                   "POLICY_RANKING", "FPS_COMPARISON", "FRAMEWORK_COMPARISON"):
        assert banned not in g, f"{banned}：不同论文、不同机器人之间的成功率/吞吐一律不比较"
    assert "cross_paper_success" in NOT_PRINTED and "cross_framework_fps" in NOT_PRINTED

    # —— 核不到的，钉成 None
    assert RT1["trials_per_task"] is None and RT1["success_judged_by"] is None, \
        "RT-1 的逐任务次数与判定方式正文未给，不许补"
    assert RT2["train_mixture_ratio"] is None, "RT-2 的数据混合比例未核到"
    assert LEGGED_RL["max_speed_m_s"] is None and LEGGED_RL["jump_height_m"] is None, \
        "足式机器人的性能数字本章不印"
    assert LEGGED_RL["hardware_control_hz"] is None and LEGGED_RL["steps_per_s"] is None, \
        "真机控制频率与吞吐正文未给"
    assert UR5E["energy_per_hour"] is None and UR5E["doc_version"] is None, \
        "UR5e 不折算耗电；官方文档没有版本号"
    assert MJX_SINGLE_SCENE["steps_per_s"] is None, "MJX 的吞吐数缺物理步长，不收"
    assert HUMANOID_ENV_COUNT_ISAACLAB["sim_dt_s"] is None \
        and HUMANOID_ENV_COUNT_ISAACLAB["fps_not_collected"], \
        "Isaac Lab 官方页缺 dt，只取环境数这一项结构性事实"

    # —— 频率别混用：策略频率 ≠ 机器人指令频率 ≠ 中层控制器频率
    assert DIFFUSION_POLICY["policy_hz"] == 10 and DIFFUSION_POLICY["robot_cmd_hz"] == 125 \
        and DIFFUSION_POLICY["midlevel_hz"] == 1000, \
        "10 Hz 是策略，125 Hz 是 UR5 接的位置指令，1 kHz 是中层控制器——三者不可混为一谈"
    assert RT1["control_hz"] == 3 and RT1["action_bins"] == 256, \
        "RT-1 是 3 Hz 闭环、每维 256 个均匀分箱"
    assert RT2["action_bins"] == 256 and RT2["action_integers"] == 8, \
        "RT-2 的动作是 8 个整数，连续维各 256 个均匀分箱"
    assert RT2["hz_55b"] == (1, 3) and RT2["hz_5b"] == 5 and "TPU" in RT2["runs_on"], \
        "RT-2 的个位数赫兹是云端多 TPU 推理，不是机上推理"
    assert ALOHA_ACT["control_hz"] == 50 and ALOHA_ACT["action_dim"] == 14, \
        "ALOHA 遥操作与数据记录都在 50 Hz，动作是 14 维绝对关节位置"

    # —— 折算值必须标明是折算
    assert LEGGED_RL["policy_hz_is_derived"], "50 Hz 由 0.005 s 步长与 4 步 decimation 折算而来"
    assert abs(1.0 / (LEGGED_RL["sim_dt_s"] * LEGGED_RL["sim_steps_per_policy_step"])
               - LEGGED_RL["policy_hz"]) < 1e-9

    # —— 引用层级：正文与附录/模型卡要分清
    assert ALOHA_ACT["chunk_size_from_appendix"], "动作块大小 100 来自附录超参表，不是正文"
    assert RT1["task_instructions_main_text"] != RT1["tasks_model_card"], \
        "RT-1 正文 700+ 与模型卡 744 是两个口径，引用要说清引的是哪一处"

    # —— 吞吐数必须四样齐全（显卡、环境数、物理步长、任务）
    assert ISAAC_GYM["gpu"].endswith("A100")
    for key in ("ant", "humanoid", "shadow_hand"):
        e = ISAAC_GYM[key]
        assert e["task"] and e["peak_steps_per_s"] and e["sim_dt_s"] and e["control_dt_s"], \
            f"{key}：吞吐数要连显卡、环境数、物理步长、任务一起收"
    assert ISAAC_GYM["ant"]["peak_steps_per_s"] > ISAAC_GYM["shadow_hand"]["peak_steps_per_s"], \
        "同一块 A100 上 Ant 与 Shadow Hand 的吞吐差好几倍——FPS 是四元组的函数，不是性能指标"
    assert ISAAC_GYM["anymal"]["steps_per_s"] is None, "ANYmal 的吞吐论文未单列"

    # —— UR5e：重复性必须连 ISO 9283，功耗必须连口径
    assert UR5E["repeatability_standard"] == "ISO 9283", \
        "±0.03 mm 是 ISO 9283 重复性，不是绝对定位精度"
    assert UR5E["power_moderate_w"] < UR5E["power_max_w"]
    assert "moderate" in UR5E["power_condition"]
    assert UR5E["weight_kg_pdf"] != UR5E["weight_kg_web"], \
        "两份官方资料的自重差 0.1 kg——注明出处，不取平均"


check()
