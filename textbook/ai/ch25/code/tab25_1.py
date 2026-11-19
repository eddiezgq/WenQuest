"""第 25 章正文里要印的公开数字，一处定义、处处引用。

数据全部来自 `conventions/logi_facts.py`（只收论文正文、官方公告、官方规格页与官方基准库
页面给出的原始值）。这个程序几乎不做计算，只把数交给正文——25.1、25.3、25.4 与 25.99
节里没有一个手打的公开数字。

算出来的只有两类，而且都在同一口径内：
1. 同一份材料内部的对照（同一个 X 集两个时点之间多证出几个最优解、同一篇论文正文与
   表 1 的地图数差几行、同一张规格页上标准桨与低噪桨的续航差几分钟）；
2. 本书自己的折算，**逐条标明**（变量名带 `_calc`）：一张地图 25 个场景 × 每场景 1000 对
   起终点折成总问题数、每 6 秒一个 pod 面折成每小时多少行。

**跨论文、跨厂家的比较一个不算**——本章硬规矩：没有已证明最优解或下界作对照的“改进”
不采信，官方自己也写明 results are not directly comparable。口径不全的数一律不在这里
出现（它们在 `logi_facts.NOT_PRINTED` 里，正文只说“不印”和“为什么不印”）。
"""
from logi_facts import (CBS, CVRP_BKS, CVRP_X_PROVEN_OPTIMAL, CVRP_XL_BEYOND_EXACT,
                        CVRPLIB_COLUMNS, CVRPLIB_SETS, DRONE_M4, DRONE_M350, HOMBERGER,
                        ISO_3691_4, KIVA_PAPER, LITTLES_LAW, MAPF_BENCHMARK, SOLOMON,
                        UCHOA2017, check)
from bookout import out

check()          # 口径断言：错一处就不让构建过去

_x_set = CVRPLIB_SETS["X"]

v = {
    # ---------- 基准库：上界与“已证明最优”本来就是两列（25.3、25.99 节）
    "col_customers": CVRPLIB_COLUMNS[0],
    "col_ub": CVRPLIB_COLUMNS[1],
    "col_opt": CVRPLIB_COLUMNS[2],
    "x_n": CVRP_X_PROVEN_OPTIMAL["n_instances"],
    "x_opt_today": CVRP_X_PROVEN_OPTIMAL["n_proven_optimal_today"],
    "x_not_proven": CVRP_X_PROVEN_OPTIMAL["n_not_proven_today"],
    "x_opt_at_paper": CVRP_X_PROVEN_OPTIMAL["n_proven_optimal_uchoa2017"],
    "x_opt_marker": CVRP_X_PROVEN_OPTIMAL["optimal_marker_in_paper"],
    "x_set_proposer": _x_set[3],
    "x_cust_min": _x_set[1],
    "x_cust_max": _x_set[2],
    "bks_definition": CVRP_BKS["definition"],
    "xl_n": CVRP_XL_BEYOND_EXACT["n_instances"],
    "xl_cust_min": CVRP_XL_BEYOND_EXACT["cust_min"],
    "xl_cust_max": CVRP_XL_BEYOND_EXACT["cust_max"],
    "uchoa_n": UCHOA2017["n_new_instances"],
    "uchoa_cust_min": UCHOA2017["cust_min"],
    "uchoa_cust_max": UCHOA2017["cust_max"],
    "uchoa_route_dist": UCHOA2017["route_size_dist"],

    # ---------- 带时间窗的基准：官方只给 best known，而且官方自己说不可比（25.3 节）
    "sol_year": SOLOMON["year"],
    "sol_size_min": SOLOMON["sizes_on_official_site"][0],
    "sol_size_max": SOLOMON["sizes_on_official_site"][-1],
    "sol_objective": SOLOMON["objective"],
    "sol_r111_corrected": SOLOMON["r111_corrected_distance"],
    "hom_size_min": HOMBERGER["sizes_on_official_site"][0],
    "hom_size_max": HOMBERGER["sizes_on_official_site"][-1],
    "hom_n_sizes": len(HOMBERGER["sizes_on_official_site"]),

    # ---------- 多机路径规划的公开基准与 CBS 的性质（25.2、25.3、25.99 节）
    "mapf_makespan_def": MAPF_BENCHMARK["makespan_def"],
    "mapf_soc_def": MAPF_BENCHMARK["soc_def"],
    "mapf_soc_aka": MAPF_BENCHMARK["soc_aka"],
    "mapf_maps_text": MAPF_BENCHMARK["n_maps_in_text"],
    "mapf_map_rows": MAPF_BENCHMARK["n_map_rows_in_table1"],
    "mapf_scen_per_map": MAPF_BENCHMARK["scenarios_per_map"],
    "mapf_probs_per_scen": MAPF_BENCHMARK["problems_per_scenario"],
    "mapf_agents_from": MAPF_BENCHMARK["agents_added_from"],
    "mapf_start_target": MAPF_BENCHMARK["start_target_method"],
    "cbs_theorem": CBS["optimality_theorem"],
    "cbs_soc_def": CBS["soc_def"],
    "cbs_fuel_def": CBS["fuel_def"],
    "cbs_soc_a": CBS["soc_example"][0],
    "cbs_soc_b": CBS["soc_example"][1],
    "cbs_soc_sum": CBS["soc_example"][2],

    # ---------- 无人机官方规格：值印出来就必须带标称条件（25.1、25.99 节）
    "m350_model": DRONE_M350["model"],
    "m350_flight_min": DRONE_M350["max_flight_time_min"],
    "m350_flight_cond": DRONE_M350["flight_time_conditions"],
    "m350_mtow_kg": DRONE_M350["max_takeoff_weight_kg"],
    "m350_w_nobat_kg": DRONE_M350["weight_no_battery_kg"],
    "m350_w_two_batt_kg": DRONE_M350["weight_two_tb65_kg"],
    "m350_gimbal_payload_g": DRONE_M350["gimbal_damper_max_payload_g"],
    "m350_wind_ms": DRONE_M350["max_wind_ms"],
    "m350_temp_lo": DRONE_M350["op_temp_c"][0],
    "m350_temp_hi": DRONE_M350["op_temp_c"][1],
    "m350_hspeed_ms": DRONE_M350["max_horizontal_speed_ms"],
    "m350_ascent_ms": DRONE_M350["max_ascent_speed_ms"],
    "m350_wheelbase_mm": DRONE_M350["diagonal_wheelbase_mm"],
    "m350_ip": DRONE_M350["ip_rating"],
    "m350_alt_lo_m": sorted(DRONE_M350["max_altitude_m"])[0],
    "m350_alt_hi_m": sorted(DRONE_M350["max_altitude_m"])[-1],
    "m350_alt_lo_note": DRONE_M350["max_altitude_m"][sorted(DRONE_M350["max_altitude_m"])[0]],
    "m350_alt_hi_note": DRONE_M350["max_altitude_m"][sorted(DRONE_M350["max_altitude_m"])[-1]],
    "m4_model": DRONE_M4["model"],
    "m4_takeoff_g": DRONE_M4["takeoff_weight_g"],
    "m4_mtow_std_g": DRONE_M4["max_takeoff_weight_g"]["standard"],
    "m4_mtow_ln_g": DRONE_M4["max_takeoff_weight_g"]["low_noise"],
    "m4_payload_g": DRONE_M4["max_payload_g"],
    "m4_flight_std_min": DRONE_M4["max_flight_time_min"]["standard"],
    "m4_flight_ln_min": DRONE_M4["max_flight_time_min"]["low_noise"],
    "m4_flight_cond": DRONE_M4["flight_time_conditions"],
    "m4_hover_std_min": DRONE_M4["max_hover_time_min"]["standard"],
    "m4_hover_ln_min": DRONE_M4["max_hover_time_min"]["low_noise"],
    "m4_hover_cond": DRONE_M4["hover_time_conditions"],
    "m4_wind_ms": DRONE_M4["max_wind_ms"],
    "m4_wind_cond": DRONE_M4["wind_conditions"],
    "m4_temp_lo": DRONE_M4["op_temp_c"][0],
    "m4_temp_hi": DRONE_M4["op_temp_c"][1],

    # ---------- 仓储：厂商自述的设计节拍，四样口径缺三样（25.99 节）
    "kiva_robots": KIVA_PAPER["fielded_robots"],
    "kiva_hours_per_day": KIVA_PAPER["fielded_hours_per_day"],
    "kiva_pod_face_s": KIVA_PAPER["pod_face_seconds"],
    "kiva_lines_per_hour": KIVA_PAPER["baseline_lines_per_hour"],
    "kiva_typical": KIVA_PAPER["typical_installation"],
    "kiva_path_planning": KIVA_PAPER["path_planning"],
    "iso3691_edition": ISO_3691_4["edition"],
    "iso3691_n_clauses": len(ISO_3691_4["clause_titles"]),

    # ---------- 排队论：利特尔法则（25.4、25.99 节）
    "littles_formula": LITTLES_LAW["formula"],
    "littles_n_conditions": len(LITTLES_LAW["conditions"]),
    "littles_cond_1": LITTLES_LAW["conditions"][0],
    "littles_cond_2": LITTLES_LAW["conditions"][1],
    "littles_cond_3": LITTLES_LAW["conditions"][2],
    "littles_ref": LITTLES_LAW["ref"],
}

# ---------- 同一份材料内部的对照
# 同一个 X 集、两个时点：从论文发表到今天多证出几个最优解（**引用必须带时点**）
v["x_newly_proven"] = (CVRP_X_PROVEN_OPTIMAL["n_proven_optimal_today"]
                       - CVRP_X_PROVEN_OPTIMAL["n_proven_optimal_uchoa2017"])
assert (CVRP_X_PROVEN_OPTIMAL["n_proven_optimal_today"]
        + CVRP_X_PROVEN_OPTIMAL["n_not_proven_today"]
        == CVRP_X_PROVEN_OPTIMAL["n_instances"]), "库页面上这两个数应当自洽：61 + 39 = 100"
v["x_opt_today_pct"] = 100.0 * (CVRP_X_PROVEN_OPTIMAL["n_proven_optimal_today"]
                                / CVRP_X_PROVEN_OPTIMAL["n_instances"])
# 同一篇论文内部：正文说 24 张地图，表 1 列了 28 行（这处矛盾本章要留着）
v["mapf_map_rows_gap"] = (MAPF_BENCHMARK["n_map_rows_in_table1"]
                          - MAPF_BENCHMARK["n_maps_in_text"])
# 同一张官方规格页内部：标准桨与低噪桨的续航、悬停差几分钟
v["m4_flight_prop_gap_min"] = (DRONE_M4["max_flight_time_min"]["standard"]
                               - DRONE_M4["max_flight_time_min"]["low_noise"])
v["m4_hover_prop_gap_min"] = (DRONE_M4["max_hover_time_min"]["standard"]
                              - DRONE_M4["max_hover_time_min"]["low_noise"])
# 同一张官方规格页内部：平飞续航比悬停时间长几分钟（**同一机型、同一张页，不跨厂家**）
v["m4_flight_minus_hover_min"] = (DRONE_M4["max_flight_time_min"]["standard"]
                                  - DRONE_M4["max_hover_time_min"]["standard"])
# 同一张官方规格页内部：空重、带两块电池、最大起飞重量三者的关系
v["m350_batt_pair_kg"] = (DRONE_M350["weight_two_tb65_kg"]
                          - DRONE_M350["weight_no_battery_kg"])
v["m350_mtow_headroom_kg"] = (DRONE_M350["max_takeoff_weight_kg"]
                              - DRONE_M350["weight_two_tb65_kg"])
assert v["m350_batt_pair_kg"] > 0 and v["m350_mtow_headroom_kg"] > 0, \
    "空重 < 带两块电池 < 最大起飞重量——三个数应当自洽"
# **这个余量不是载重**：官方没给整机最大载重，不许拿它当载重用
assert DRONE_M350["max_payload_g"] is None, "M350 官方没给整机载重，这里只是重量差"

# ---------- 本书自己的折算（逐条标明，变量名带 _calc）
# 一张地图的问题总数 = 场景数 × 每个场景的起终点对数
v["mapf_problems_per_map_calc"] = (MAPF_BENCHMARK["scenarios_per_map"]
                                   * MAPF_BENCHMARK["problems_per_scenario"])
# **自查**：论文正文那两个数折算出来的总数，应当与“25 × 1000”一致
assert v["mapf_problems_per_map_calc"] == 25_000, "25 个场景 × 1000 对起终点 = 25 000 个问题"
# Kiva 的 600 行/小时 = 3600 s ÷ 每 6 s 一个 pod 面；**自查**：它是算术折算，不是实测统计
v["kiva_lines_per_hour_calc"] = 3600.0 / KIVA_PAPER["pod_face_seconds"]
assert abs(v["kiva_lines_per_hour_calc"] - KIVA_PAPER["baseline_lines_per_hour"]) < 1e-9, \
    "论文里这两个数应当自洽：3600 s ÷ 6 s = 600 行/小时（设计节拍，不是实测）"
# 每台车每天按 24 小时算，这些车一天折算多少台·小时（**只为说明“厂商自述”的规模**）
v["kiva_robot_hours_per_day_calc"] = (KIVA_PAPER["fielded_robots"]
                                      * KIVA_PAPER["fielded_hours_per_day"])
# CBS §6.1 的例子：两台车各 2 步与 3 步，sum-of-costs = 5
assert v["cbs_soc_a"] + v["cbs_soc_b"] == v["cbs_soc_sum"], "§6.1 的例子：2 + 3 = 5"

print(f"基准库的两列：表头是 {v['col_customers']}（点数）、{v['col_ub']}（上界）与 "
      f"{v['col_opt']}（是否已证明最优）——上界与已证明最优本来就不是一回事")
print(f"  X 集 {v['x_n']} 个实例（{v['x_cust_min']}—{v['x_cust_max']} 个客户，{v['x_set_proposer']}）："
      f"发表当年已证明最优 {v['x_opt_at_paper']} 个，今天 {v['x_opt_today']} 个"
      f"（{v['x_opt_today_pct']:.0f}%），还有 {v['x_not_proven']} 个没证——"
      f"多证出 {v['x_newly_proven']} 个，**所以引用必须带时点**")
print(f"  XL 集 {v['xl_n']} 个实例、{v['xl_cust_min']:,}—{v['xl_cust_max']:,} 个点，"
      f"官方写明已超出精确算法能处理的范围，那里只有最好已知解")
print(f"  最好已知解的定义（库里的原话）：“{v['bks_definition']}”——是上界，没有证明过")
print(f"带时间窗的基准（{v['sol_year']} 年那套，{v['sol_size_min']}—{v['sol_size_max']} 个客户；"
      f"另一套 {v['hom_size_min']}—{v['hom_size_max']} 个客户共 {v['hom_n_sizes']} 档）："
      f"目标是分层的——{v['sol_objective']}，官方自己写明 results are not directly comparable")
print(f"多机路径规划基准：一张地图 {v['mapf_scen_per_map']} 个场景、每个场景 "
      f"{v['mapf_probs_per_scen']:,} 对起终点（**本书折算**共 {v['mapf_problems_per_map_calc']:,} 个问题），"
      f"起终点取法是 {v['mapf_start_target']}，从 {v['mapf_agents_from']} 台开始逐台加到超时")
print(f"  **同一篇里两处不一致**：正文说 {v['mapf_maps_text']} 张地图，表 1 列了 "
      f"{v['mapf_map_rows']} 行（差 {v['mapf_map_rows_gap']} 行）——本章不抹平，要印须回表 1 自己数")
print(f"  CBS 的最优性是定理（{v['cbs_theorem']}）；完备性只成立一半，"
      f"“complete and optimal”这句论文正文里没有")
print(f"无人机规格（值印出来就带标称条件）：{v['m350_model']} 最长飞行 {v['m350_flight_min']} 分钟，"
      f"条件是“{v['m350_flight_cond']}”；整机最大载重**官方没给**，"
      f"{v['m350_gimbal_payload_g']} g 是单吊舱减震器承载，不是载重")
print(f"  {v['m4_model']} 最长飞行 {v['m4_flight_std_min']} 分钟（低噪桨 {v['m4_flight_ln_min']}，"
      f"差 {v['m4_flight_prop_gap_min']} 分钟），悬停 {v['m4_hover_std_min']} 分钟"
      f"（比平飞短 {v['m4_flight_minus_hover_min']} 分钟），整机载重 {v['m4_payload_g']} g——"
      f"**这一项官方明确给了，与上一款的区别就在这里**")
print(f"  抗风两家都写 12 m/s，但口径不同：{v['m350_model']} 没有脚注，"
      f"{v['m4_model']} 明写“{v['m4_wind_cond']}”——**不许并列成“都抗 12 m/s 风”**")
print(f"仓储（厂商自述）：{v['kiva_typical']}、远超 {v['kiva_robots']} 台车一天 "
      f"{v['kiva_hours_per_day']} 小时，每 {v['kiva_pod_face_s']} 秒一个 pod 面 → "
      f"{v['kiva_lines_per_hour']} 行/小时（**本书自查**：3600 ÷ {v['kiva_pod_face_s']} = "
      f"{v['kiva_lines_per_hour_calc']:.0f}，是设计节拍不是实测；基线、统计期、测量方三样全缺）")
print(f"  ISO 3691-4（{v['iso3691_edition']} 版）本次只核到 {v['iso3691_n_clauses']} 条条款标题，"
      f"条文拿不到——**本章不印任何数值要求**")
print(f"排队论：{v['littles_formula']} 的适用条件有 {v['littles_n_conditions']} 条"
      f"（{v['littles_cond_1']}；{v['littles_cond_2']}；{v['littles_cond_3']}），"
      f"出处 {v['littles_ref']}")

out(**v)
