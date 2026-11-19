"""第 24 章正文里要印的公开数字，一处定义、处处引用。

数据全部来自 `conventions/robot_facts.py`（只收论文正文、官方公告、官方文档与厂家官方
规格页的原始值）。这个程序几乎不做计算，只把数交给正文——24.2、24.4、24.6 与 24.99
节里没有一个手打的公开数字。

算出来的只有两类，而且都在同一口径内：
1. 同一份材料内部的对照（同一篇里仿真与真机的样本量之比、摘要与正文差几个百分点、
   同一块显卡上两个任务的吞吐之比、两份官方资料的自重差）；
2. 本书自己的量纲折算，**逐条标明**（变量名带 `_calc`）：rad 折成度、物理步长折成
   频率、1/dt 折成“几分之一秒”、40 次试验里一次试验值几个百分点。

**跨论文、跨厂家的比较一个不算**——本章第三条自律，`robot_facts.check()` 里有断言钉住。
口径不全的数一律不在这里出现（它们在 `robot_facts.NOT_PRINTED` 里，正文只说“不印”
和“为什么不印”）。
"""
import math

from robot_facts import (ALOHA_ACT, DIFFUSION_POLICY, ISAAC_GYM, LEGGED_RL, MJX_SINGLE_SCENE,
                         RT1, RT2, SIM2REAL_TRIFINGER, UR5E, check)
from bookout import out

check()          # 口径断言：错一处就不让构建过去

_ant = ISAAC_GYM["ant"]
_hum = ISAAC_GYM["humanoid"]
_hand = ISAAC_GYM["shadow_hand"]
_any = ISAAC_GYM["anymal"]

v = {
    # ---------- 仿真到现实：唯一允许并排的两列（24.2、24.6、24.99 节）
    "tri_task": SIM2REAL_TRIFINGER["task"],
    "tri_sim_pct": SIM2REAL_TRIFINGER["sim_success_pct_cube"],
    "tri_sim_n": SIM2REAL_TRIFINGER["sim_trials"],
    "tri_real_pct": SIM2REAL_TRIFINGER["real_success_pct"],
    "tri_real_n": SIM2REAL_TRIFINGER["real_trials"],
    "tri_pos_cm": SIM2REAL_TRIFINGER["success_pos_cm"],
    "tri_rot_rad": SIM2REAL_TRIFINGER["success_rot_rad"],
    "tri_abstract_pct": SIM2REAL_TRIFINGER["abstract_rounds_to_pct"],
    "tri_ci_pct": SIM2REAL_TRIFINGER["real_ci_pct"],
    "tri_policy_hz": SIM2REAL_TRIFINGER["policy_hz"],
    "tri_cam_hz": SIM2REAL_TRIFINGER["camera_hz"],
    "tri_envs": SIM2REAL_TRIFINGER["n_envs"],

    # ---------- 模仿学习的数据与评测口径（24.1、24.3、24.99 节）
    "rt1_demos": RT1["demos"],
    "rt1_robots": RT1["robots"],
    "rt1_months": RT1["collection_months"],
    "rt1_instructions": RT1["task_instructions_main_text"],
    "rt1_tasks_card": RT1["tasks_model_card"],
    "rt1_arm_dims": RT1["action_dims_arm"],
    "rt1_base_dims": RT1["action_dims_base"],
    "rt1_bins": RT1["action_bins"],
    "rt1_hz": RT1["control_hz"],
    "rt1_trials": RT1["eval_trials_total"],
    "rt1_eval_tasks": RT1["eval_tasks"],
    "rt1_unseen": RT1["eval_unseen_instructions"],
    "al_demos": ALOHA_ACT["demos_per_task"],
    "al_hz": ALOHA_ACT["control_hz"],
    "al_dim": ALOHA_ACT["action_dim"],
    "al_real_trials": ALOHA_ACT["real_trials_per_task"],
    "al_real_seeds": ALOHA_ACT["real_seeds"],
    "al_sim_trials": ALOHA_ACT["sim_trials_per_task"],
    "al_sim_seeds": ALOHA_ACT["sim_seeds"],
    "al_chunk": ALOHA_ACT["chunk_size"],
    "dp_policy_hz": DIFFUSION_POLICY["policy_hz"],
    "dp_cmd_hz": DIFFUSION_POLICY["robot_cmd_hz"],
    "dp_mid_hz": DIFFUSION_POLICY["midlevel_hz"],
    "dp_real_trials": DIFFUSION_POLICY["real_trials_per_task"],

    # ---------- 视觉—语言—动作模型（24.3、24.99 节）
    "rt2_integers": RT2["action_integers"],
    "rt2_dof": RT2["action_dof"],
    "rt2_bins": RT2["action_bins"],
    "rt2_vocab_ints": 1000 if "1000" in RT2["pali_x_vocab"] else None,
    "rt2_params_b": RT2["params_b_largest"],
    "rt2_hz_lo": RT2["hz_55b"][0],
    "rt2_hz_hi": RT2["hz_55b"][1],
    "rt2_hz_small": RT2["hz_5b"],
    "rt2_trials": RT2["eval_trials_total"],
    "rt2_tasks_seen": RT2["eval_tasks_seen"],
    "rt2_tasks_unseen": RT2["eval_tasks_unseen"],
    "rt2_runs_lo": RT2["trials_per_instruction"][0],
    "rt2_runs_hi": RT2["trials_per_instruction"][1],

    # ---------- GPU 并行物理仿真：四样齐全才收（24.2、24.6、24.99 节）
    "ig_gpu": ISAAC_GYM["gpu"],
    "ig_ant_peak": _ant["peak_steps_per_s"],
    "ig_ant_train_sps": _ant["train_avg_steps_per_s"],
    "ig_ant_train_envs": _ant["n_envs_for_train_avg"],
    "ig_ant_dims": _ant["action_dims"],
    "ig_hum_peak": _hum["peak_steps_per_s"],
    "ig_hum_dims": _hum["action_dims"],
    "ig_hand_peak": _hand["peak_steps_per_s"],
    "ig_hand_dims": _hand["action_dims"],
    "ig_hand_envs": _hand["n_envs_at_peak"],
    "ig_anymal_envs": _any["n_envs"],
    "ig_anymal_gpu": _any["gpu"],
    "ig_anymal_transfer": _any["train_to_transfer"],
    "mjx_statement": MJX_SINGLE_SCENE["statement"],

    # ---------- 足式运动的结构性口径（24.2、24.4、24.99 节）
    "lg_envs": LEGGED_RL["n_envs"],
    "lg_batch": LEGGED_RL["batch_size"],
    "lg_gpu": LEGGED_RL["gpu"],
    "lg_dt_s": LEGGED_RL["sim_dt_s"],
    "lg_decimation": LEGGED_RL["sim_steps_per_policy_step"],
    "lg_updates": LEGGED_RL["policy_updates"],
    "lg_min_flat": LEGGED_RL["train_minutes_flat"],
    "lg_min_rough": LEGGED_RL["train_minutes_rough"],
    "lg_cmd_v": LEGGED_RL["cmd_max_lin_vel_m_s"],
    "lg_robot": LEGGED_RL["robot"],

    # ---------- UR5e 官方规格（24.6、24.99 节）
    "ur_payload_kg": UR5E["payload_kg"],
    "ur_reach_mm": UR5E["reach_mm"],
    "ur_rep_mm": UR5E["repeatability_mm"],
    "ur_rep_std": UR5E["repeatability_standard"],
    "ur_dof": UR5E["dof"],
    "ur_joint_deg": UR5E["joint_range_deg"],
    "ur_joint_speed": UR5E["joint_max_speed_deg_s"],
    "ur_pw_moderate": UR5E["power_moderate_w"],
    "ur_pw_max": UR5E["power_max_w"],
    "ur_w_pdf": UR5E["weight_kg_pdf"],
    "ur_w_web": UR5E["weight_kg_web"],
    "ur_footprint_mm": UR5E["footprint_mm"],
    "ur_ip_arm": UR5E["ip_arm"],
    "ur_ip_box": UR5E["ip_control_box"],
}

# ---------- 同一份材料内部的对照（同一篇、同一判据、同一块显卡）
# 同一篇里仿真与真机的样本量之比
v["tri_n_ratio"] = SIM2REAL_TRIFINGER["sim_trials"] / SIM2REAL_TRIFINGER["real_trials"]
# 同一篇里摘要与正文差几个百分点（摘要四舍五入，正文没有）
v["tri_abstract_gap_pts"] = (SIM2REAL_TRIFINGER["abstract_rounds_to_pct"]
                             - SIM2REAL_TRIFINGER["real_success_pct"])
# 同一篇、同一判据下仿真高于真机几个百分点
v["tri_sim_real_gap_pts"] = (SIM2REAL_TRIFINGER["sim_success_pct_cube"]
                             - SIM2REAL_TRIFINGER["real_success_pct"])
# 同一块 A100、同一篇论文里两个任务的吞吐之比
v["ig_ant_over_hand"] = _ant["peak_steps_per_s"] / _hand["peak_steps_per_s"]
# 两份官方资料的自重差（注明出处，不取平均）
v["ur_w_diff_kg"] = abs(UR5E["weight_kg_web"] - UR5E["weight_kg_pdf"])
# 同一份官方规格页内部：峰值功率是“中等运行设置”的几倍
v["ur_pw_ratio"] = UR5E["power_max_w"] / UR5E["power_moderate_w"]

# ---------- 本书自己的折算（逐条标明，变量名带 _calc）
# 姿态阈值：0.4 rad 折成度 = 0.4 × 180 / π（论文正文括注的是取整值）
v["tri_rot_deg_calc"] = math.degrees(SIM2REAL_TRIFINGER["success_rot_rad"])
# 真机 N=40 时，一次试验值几个百分点 = 100 / 40
v["tri_one_trial_pct_calc"] = 100.0 / SIM2REAL_TRIFINGER["real_trials"]
# 真机 82.5% × 40 次 = 多少次成功；**自查**：同一篇里这两个数应当给出整数次成功
v["tri_real_successes_calc"] = (SIM2REAL_TRIFINGER["real_success_pct"] / 100.0
                                * SIM2REAL_TRIFINGER["real_trials"])
assert abs(v["tri_real_successes_calc"] - round(v["tri_real_successes_calc"])) < 1e-9, \
    "同一篇里 82.5% 与 N=40 应当自洽：0.825 × 40 = 33 次成功，不是小数"
v["tri_real_successes_calc"] = round(v["tri_real_successes_calc"])
# 每维 256 个分箱时，整数的取值范围是 0 到 255 = 箱数 − 1
v["rt2_bin_max_calc"] = RT2["action_bins"] - 1
# RT-1 的动作维数 = 手臂 7 维 + 底盘 3 维
v["rt1_action_dims_calc"] = RT1["action_dims_arm"] + RT1["action_dims_base"]
# Diffusion Policy 的中层控制器：1000 Hz 折成 kHz
v["dp_mid_khz_calc"] = DIFFUSION_POLICY["midlevel_hz"] / 1000.0
# Isaac Gym 表 4 的步长，正文照“1/N s”印：N = 1/dt
v["ig_sim_dt_inv_calc"] = 1.0 / _ant["sim_dt_s"]
v["ig_ctrl_dt_inv_calc"] = 1.0 / _ant["control_dt_s"]
v["ig_hand_openai_dt_inv_calc"] = 1.0 / _hand["control_dt_s_openai_obs"]
v["ig_anymal_sim_dt_inv_calc"] = 1.0 / _any["sim_dt_s"]
v["ig_anymal_ctrl_dt_inv_calc"] = 1.0 / _any["control_dt_s"]
for _k in ("ig_sim_dt_inv_calc", "ig_ctrl_dt_inv_calc", "ig_hand_openai_dt_inv_calc",
           "ig_anymal_sim_dt_inv_calc", "ig_anymal_ctrl_dt_inv_calc"):
    assert abs(v[_k] - round(v[_k])) < 1e-9, f"{_k}：表 4 的步长应当是整数分之一秒"
    v[_k] = round(v[_k])
# 足式运动的策略频率：0.005 s 步长 × 四步 decimation → 0.02 s → 50 Hz
# **自查**：论文附录同处亦以 50 Hz 表述，两者应当自洽
v["lg_policy_hz_calc"] = 1.0 / (LEGGED_RL["sim_dt_s"] * LEGGED_RL["sim_steps_per_policy_step"])
assert abs(v["lg_policy_hz_calc"] - LEGGED_RL["policy_hz"]) < 1e-9, \
    "附录里这两处应当自洽：1 ÷ (0.005 s × 4) = 50 Hz"
v["lg_policy_step_s_calc"] = LEGGED_RL["sim_dt_s"] * LEGGED_RL["sim_steps_per_policy_step"]

print(f"仿真到现实（同一篇、同一判据）：仿真 {v['tri_sim_pct']:.1f}%（N={v['tri_sim_n']:,}）对真机 "
      f"{v['tri_real_pct']:.1f}%（N={v['tri_real_n']}）——差 {v['tri_sim_real_gap_pts']:.1f} 个百分点，"
      f"样本量差 {v['tri_n_ratio']:.1f} 倍")
print(f"  判据：位置进 {v['tri_pos_cm']:.0f} cm、姿态进 {v['tri_rot_rad']:.1f} rad"
      f"（本书折算 {v['tri_rot_deg_calc']:.1f}°）；真机 {v['tri_real_pct']:.1f}% × {v['tri_real_n']} 次 = "
      f"{v['tri_real_successes_calc']} 次成功，少成一次掉 {v['tri_one_trial_pct_calc']:.1f} 个百分点")
print(f"  摘要写 {v['tri_abstract_pct']}%、正文写 {v['tri_real_pct']:.1f}%，"
      f"差 {v['tri_abstract_gap_pts']:.1f} 个百分点——同一篇里两个口径，本书引正文、不抹平")
print(f"模仿学习的采集口径：RT-1 {v['rt1_demos']:,} 条演示、{v['rt1_robots']} 台机器人、"
      f"{v['rt1_months']} 个月（正文 {v['rt1_instructions']}+ 条指令，附录模型卡 {v['rt1_tasks_card']} 个任务——"
      f"两个口径）；动作 {v['rt1_arm_dims']}+{v['rt1_base_dims']}={v['rt1_action_dims_calc']} 维、"
      f"每维 {v['rt1_bins']} 个分箱、{v['rt1_hz']} Hz 闭环")
print(f"  ALOHA/ACT：每任务 {v['al_demos']} 条演示、{v['al_hz']} Hz 记录、{v['al_dim']} 维绝对关节位置；"
      f"真机每任务 {v['al_real_trials']} 次 × {v['al_real_seeds']} 个种子，仿真 {v['al_sim_trials']} 次 × "
      f"{v['al_sim_seeds']} 个种子（动作块 {v['al_chunk']} 出自附录超参表）")
print(f"  Diffusion Policy 的三个频率：策略 {v['dp_policy_hz']} Hz、机器人接位置指令 {v['dp_cmd_hz']} Hz、"
      f"中层控制器约 {v['dp_mid_khz_calc']:.0f} kHz——三者不可混为一谈")
print(f"视觉—语言—动作模型：RT-2 输出 {v['rt2_integers']} 个整数（{v['rt2_dof']} 自由度增量 + 夹爪 + 终止），"
      f"连续维各 {v['rt2_bins']} 个均匀分箱；{v['rt2_params_b']}B 那一版 {v['rt2_hz_lo']}—{v['rt2_hz_hi']} Hz、"
      f"较小那一版约 {v['rt2_hz_small']} Hz，**都是云端多 TPU 推理**")
print(f"  评测分辨率：RT-1 共 {v['rt1_trials']:,} 多次、{v['rt1_eval_tasks']}+ 个任务（每任务多少次未核到）；"
      f"RT-2 约 {v['rt2_trials']:,} 条轨迹，未见过类别每条 run {v['rt2_runs_lo']}—{v['rt2_runs_hi']} 次")
print(f"吞吐（四样齐全才收）：{v['ig_gpu']} 上 Ant 峰值 {v['ig_ant_peak']:,}、Humanoid {v['ig_hum_peak']:,}、"
      f"Shadow Hand {v['ig_hand_peak']:,} 步每秒（动作 {v['ig_ant_dims']}/{v['ig_hum_dims']}/{v['ig_hand_dims']} 维，"
      f"物理步长都是 1/{v['ig_sim_dt_inv_calc']} s）——同一块显卡换个任务差 {v['ig_ant_over_hand']:.1f} 倍")
print(f"  单场景不并行时官方自己写着：“{v['mjx_statement']}”")
print(f"足式运动：{v['lg_envs']:,} 个环境、批量 {v['lg_batch']:,}、一块 {v['lg_gpu']}；物理步长 "
      f"{v['lg_dt_s']} s、一步策略 {v['lg_decimation']} 步物理 → **本书折算** "
      f"{v['lg_policy_hz_calc']:.0f} Hz（{v['lg_policy_step_s_calc']:.2f} s 一步）；"
      f"速度指令上限 {v['lg_cmd_v']} m/s（**是指令上限**）")
print(f"UR5e 官方规格：负载 {v['ur_payload_kg']:.0f} kg、工作半径 {v['ur_reach_mm']} mm、"
      f"重复性 ±{v['ur_rep_mm']} mm（按 {v['ur_rep_std']}，**不是绝对定位精度**）；"
      f"功耗 {v['ur_pw_moderate']} W / 峰值 {v['ur_pw_max']} W（差 {v['ur_pw_ratio']:.1f} 倍）")
print(f"  自重两份官方资料不一致：PDF {v['ur_w_pdf']} kg、在线数据表页 {v['ur_w_web']} kg，"
      f"差 {v['ur_w_diff_kg']:.1f} kg——注明出处，不取平均")

out(**v)
