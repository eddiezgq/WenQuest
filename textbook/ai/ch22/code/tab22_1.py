"""22.99 节“公开发表的数字”那张表里的每个数。

数据全部来自 `conventions/grid_facts.py`（只收论文正文、官方公告、官方文档或官方建模
假设给出的原始值）。这个程序基本不做计算，只把数交给正文——表里没有一个手打的数字。

算出来的只有三类，而且都在同一口径内：
1. 同一篇论文内部的倍数（改进前后的训练时长之比、一步仿真与一个回合的关系）；
2. 本书自己的量纲折算，**逐条标明**（一个回合要跑多少天的仿真时间）；
3. 本章算例用的显式假设与公开建模假设的对照（效率、时长）。
"""
from grid_facts import (BATTERY_ASSUMED, COOLING, GEFCOM2014, STORAGE_ATB, TEARING_RL,
                        TOKAMAK_RL, WEATHER_API, check)
from bookout import out

check()          # 口径断言：错一处就不让构建过去

v = {
    # ---------- 聚变等离子体控制（22.4 节）
    "tok_device": TOKAMAK_RL["device"],
    "tok_khz": TOKAMAK_RL["control_rate_khz"],
    "tok_coils": TOKAMAK_RL["n_coils"],
    "tok_sim": TOKAMAK_RL["simulator"],
    "tok_step_s": TOKAMAK_RL["sim_step_s"],
    "tok_ep_steps": TOKAMAK_RL["episode_steps"],
    "tok_ep_hours": TOKAMAK_RL["episode_hours"],
    "tok_improved_h": TOKAMAK_RL["improved_hours"],
    "tok_baseline_h": TOKAMAK_RL["baseline_hours"],
    "tok_reward": TOKAMAK_RL["improved_reward"],
    "tear_device": TEARING_RL["device"],
    "tear_actuators": TEARING_RL["actuators"],

    # ---------- 数据中心冷却（22.3 节）
    "cool_pct": COOLING["cooling_cut_pct"],
    "cool_pue_pct": COOLING["pue_overhead_cut_pct"],
    "cool_date": COOLING["date"],

    # ---------- 储能（22.2、22.6 节）
    "atb_eff_pct": STORAGE_ATB["round_trip_eff"] * 100,
    "atb_dur_default": STORAGE_ATB["default_duration_h"],
    "atb_dur_min": STORAGE_ATB["durations_h"][0],
    "atb_dur_max": STORAGE_ATB["durations_h"][-1],
    "atb_life_y": STORAGE_ATB["lifetime_years"],
    "atb_cycles": STORAGE_ATB["cycles_per_day"],
    "atb_cf_pct": STORAGE_ATB["capacity_factor_4h_pct"],
    "bat_cap": BATTERY_ASSUMED["cap_kwh"],
    "bat_pmax": BATTERY_ASSUMED["p_max_kw"],
    "bat_eta_pct": BATTERY_ASSUMED["eta"] * 100,
    "bat_soc_lo_pct": BATTERY_ASSUMED["soc_min"] * 100,
    "bat_soc_hi_pct": BATTERY_ASSUMED["soc_max"] * 100,

    # ---------- 公开竞赛与数据（22.1 节）
    "gef_tracks": len(GEFCOM2014["tracks"]),
    "gef_people": GEFCOM2014["participants"],
    "gef_countries": GEFCOM2014["countries"],
    "api_latency": WEATHER_API["latency"],
}

# ---------- 同一篇论文内部的倍数
v["tok_speedup"] = TOKAMAK_RL["baseline_hours"] / TOKAMAK_RL["improved_hours"]

# ---------- 本书自己的量纲折算（标明）
# 一步仿真约 2 秒、一个回合 10,000 步：换算成"连着跑要多少天"
v["tok_ep_days_calc"] = TOKAMAK_RL["sim_step_s"] * TOKAMAK_RL["episode_steps"] / 86400.0
# 自查：2 秒一步 × 10,000 步 = 多少小时？应当与论文说的"约 5 小时"对得上
v["tok_ep_hours_calc"] = TOKAMAK_RL["sim_step_s"] * TOKAMAK_RL["episode_steps"] / 3600.0
assert abs(v["tok_ep_hours_calc"] - TOKAMAK_RL["episode_hours"]) < 1.0, \
    "论文里这两个数应当自洽：一步 2 秒、一万步，约 5 小时"
# 控制周期：10 kHz 对应多少微秒一步
v["tok_period_us"] = 1e6 / (TOKAMAK_RL["control_rate_khz"] * 1000.0)

# ---------- 本章假设与公开建模假设的对照
v["bat_duration_h"] = BATTERY_ASSUMED["cap_kwh"] / BATTERY_ASSUMED["p_max_kw"]
v["bat_usable_pct"] = (BATTERY_ASSUMED["soc_max"] - BATTERY_ASSUMED["soc_min"]) * 100
v["bat_usable_kwh"] = BATTERY_ASSUMED["cap_kwh"] * (BATTERY_ASSUMED["soc_max"]
                                                    - BATTERY_ASSUMED["soc_min"])
v["eff_gap_pts"] = BATTERY_ASSUMED["eta"] * 100 - STORAGE_ATB["round_trip_eff"] * 100

print(f"聚变：{v['tok_device']} 上 {v['tok_khz']} kHz（每步 {v['tok_period_us']:.0f} 微秒）、"
      f"{v['tok_coils']} 路电源；仿真器 {v['tok_sim']}（自由边界）")
print(f"一步仿真约 {v['tok_step_s']:.0f} 秒、一个回合 {v['tok_ep_steps']:,} 步，"
      f"论文说约 {v['tok_ep_hours']:.0f} 小时——**本书自查**：两数相乘是 "
      f"{v['tok_ep_hours_calc']:.1f} 小时，对得上（折成天是 {v['tok_ep_days_calc']:.2f} 天）")
print(f"改进后同一任务 {v['tok_improved_h']:.0f} 小时达到 {v['tok_reward']} 分，"
      f"基线 {v['tok_baseline_h']:.0f} 小时，快 {v['tok_speedup']:.0f} 倍")
print(f"冷却（{v['cool_date']}）：冷却电耗降 {v['cool_pct']}%、整体 PUE 开销降 {v['cool_pue_pct']}%"
      f"——**基线、统计期、测量方三样都没给**")
print(f"储能公开建模假设：往返效率 {v['atb_eff_pct']:.0f}%、默认 {v['atb_dur_default']} 小时、"
      f"寿命 {v['atb_life_y']} 年、每天约 {v['atb_cycles']:.0f} 次循环")
print(f"本章假设的那组储能：{v['bat_cap']:.0f} kWh / {v['bat_pmax']:.0f} kW "
      f"（{v['bat_duration_h']:.0f} 小时），效率 {v['bat_eta_pct']:.0f}%，"
      f"可用区间 {v['bat_soc_lo_pct']:.0f}%—{v['bat_soc_hi_pct']:.0f}%"
      f"（{v['bat_usable_kwh']:.0f} kWh）")
print(f"比公开建模假设高 {v['eff_gap_pts']:.0f} 个百分点——所以算例里专门算了"
      f"“效率按真设备往下掉”会怎样")
print(f"GEFCom2014：{v['gef_tracks']} 个赛道、{v['gef_people']} 名参赛者、"
      f"{v['gef_countries']} 个国家")

out(**v)
