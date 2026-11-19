"""第 25 章（无人机与智能物流）要印的公开数字，一处定义、处处引用。

出处逐条记在
`docs/教材/人工智能/参考/第25章_物流与无人机原始数字资料_2026-11.md`。

纪律与第 17—24 章同：只收论文正文、官方公告、官方文档、官方规格书、官方基准库给出的
原始值；新闻稿、公司宣传、维基一律不算。口径不全的进 `NOT_PRINTED`；凡“本书自己折算”
的，逐条标明。

本章另有一条自己的硬规矩：**没有最优解或下界作对照的改进不采信。**
路径与调度这类问题的好处是真值可求——公开基准库里有已证明的最优解，也有下界。
所以本章凡说“好了多少”，必须指明是跟最优解比、跟下界比，还是只跟另一个启发式比。

因此本文件把**最好已知解（BKS）与已证明最优解分成两个不同的字段**，并在 `check()` 里
用断言钉死这件事：BKS 是“历史上所有人跑出来的最好结果”，是一个会往下走的上界，
**不是真值**。同一个 CVRPLIB X 集，“已证明最优”从 Uchoa 2017 论文当年的 40/100
变成今天的 61/100，而 BKS 本身也在被一篇篇论文改掉。

另外两条本章纪律，也由 `check()` 钉住：
1. **标称条件核不到的规格值，一律为 None**（无人机那一节）。
2. **企业运营口径的“效率提升百分之多少”一个不收**——基线、规模、统计期、测量方
   四样齐全才印；本次一组都没齐，全部在 `NOT_PRINTED`。
"""
from __future__ import annotations

# ======================================= 一、CVRPLIB：BKS 与已证明最优是两件事（25.2、25.3 节）

# 库里的列头本身就把两者分开：|C|（客户数）、UB（上界）、Opt（是否已证明最优，yes/no）
CVRPLIB_COLUMNS = ("|C|", "UB", "Opt")   # 原话：Opt 列取 yes/no

# 各实例集：(实例数, 最小客户数, 最大客户数, 提出者)
CVRPLIB_SETS = {
    "A":      (27, 31, 79, "Augerat et al., 1995"),
    "B":      (23, 30, 77, "Augerat et al., 1995"),
    "P":      (24, 15, 100, "Augerat et al., 1995"),
    "E":      (13, 12, 100, "Christofides et al., 1969"),
    "M":      (5, 100, 199, "Christofides et al., 1979"),
    "X":      (100, 100, 1000, "Uchoa et al., 2017"),
    "AGS":    (10, 3000, 30000, "Arnold et al., 2019"),
    "XL":     (100, 1047, 10000, "Queiroga et al., 2026"),
}

# ---- 本章第一号引用警告的三条硬证据，分字段存，禁止互相代入 ----

# （1）“已证明最优”——proven optimal，这才是真值
CVRP_X_PROVEN_OPTIMAL = {
    "n_instances": 100,
    "n_proven_optimal_today": 61,       # 原话 "Today, 61 X instances have proven optimal solutions"
    "n_not_proven_today": 39,           # 原话 "with most of the remaining 39 likely being optimal as well"
    "n_proven_optimal_uchoa2017": 40,   # 原话 "The BCP could solve 40 out of the 100 new instances to optimality"
    "optimal_marker_in_paper": "*",     # 原话 "Optimal solutions are marked with a *."
    "is_proven": True,
    "ref": "CVRPLIB 官方 BKS Challenge / Overview 页（今天的 61/100）；Uchoa et al. (2017) §4.2 与表 7（当年的 40/100）",
    "note": "两个数都对，但属于不同时点——引用必须带时点",
}

# （2）“最好已知解”——BKS，只是一个会往下走的上界，**不是真值**
CVRP_BKS = {
    # 原话（Uchoa 2017 表 11 表题）："the best solution (BKS) ever found since the instances were created"
    "definition": "the best solution (BKS) ever found since the instances were created",
    "includes_authors_preliminary_runs": True,   # 表题说明里含作者用其他参数做的预备实验
    "is_proven": False,                 # **BKS 不是已证明最优解**
    "is_upper_bound": True,             # 它是上界，会被下一篇论文改掉
    "formal_definition_on_library_page": None,   # 库页面没写 BKS 的定义，只有 UB / Opt 两列
    "auto_feasibility_checked": True,   # 原话 "A submitted solution will be automatically checked for feasibility"
    "ref": "Uchoa et al. (2017) Table 11 表题；CVRPLIB 官方 BKS Challenge / Overview 页",
}

# （3）XL 集为什么只有 BKS 没有最优解
CVRP_XL_BEYOND_EXACT = {
    # 原话 "These large instances are beyond the reach of current exact methods
    #       but are very useful for evaluating heuristics."
    "beyond_exact_methods": True,
    "n_instances": 100,
    "cust_min": 1047,
    "cust_max": 10000,
    "ref": "CVRPLIB 官方 BKS Challenge / Overview 页",
}

UCHOA2017 = {
    "n_new_instances": 100,
    "cust_min": 100, "cust_max": 1000,  # 摘要 "ranging from 100 to 1000 customers"
    # 原话 "The set of values of r were taken from a continuous triangular distribution T(3,6,25)."
    "route_size_dist": "T(3,6,25) continuous triangular",
    "old_sets_too_easy": True,          # 摘要 "became too easy for current algorithms"
    "old_sets_too_homogeneous": True,   # 摘要 "are too homogeneous, not covering the wide range of characteristics..."
    "christofides_eilon_exhausted": True,   # 正文称经典 Christofides & Eilon 集已 "exhausted"
    "ref": "Uchoa, Pecin, Pessoa, Poggi, Subramanian, Vidal, New Benchmark Instances for the CVRP",
}

# ======================================= 二、Solomon / Gehring & Homberger（VRPTW，25.3 节）

SOLOMON = {
    "year": 1987,
    "sizes_on_official_site": (25, 50, 100),
    # 原话 "The version reported here has a hierarchical objective:
    #       1) Minimize number of vehicles 2) Minimize total distance."
    "objective": "hierarchical: 1) minimize number of vehicles 2) minimize total distance",
    "solutions_are_best_known_only": True,
    "has_optimality_marker": False,     # 官方表只称 best known，通篇没有最优性标记
    # 原话 "Exact methods typically use a monolithic total distance objective and use
    #       integral or low precision distance and time calculations." "Hence, results
    #       are not directly comparable."
    "not_comparable_with_exact": True,
    "checked_by_solution_checker": True,    # 原话 "All detailed solutions have been checked by our solution checker."
    "classes": None,                    # C1/C2/R1/R2/RC1/RC2 与实例总数：官方页未给，未核到
    "n_instances": None,                # 同上，未核到
    "r111_corrected_distance": 1096.73, # 官方注：BKS 的数值本身也会被人订正
    "ref": "SINTEF TOP 官方站 VRPTW / Solomon benchmark、100 customers 页",
}

HOMBERGER = {
    "authors": "Gehring & Homberger",
    "sizes_on_official_site": (200, 400, 600, 800, 1000),
    "objective": SOLOMON["objective"],  # 官方页同一句
    "solutions_are_best_known_only": True,
    "has_optimality_marker": False,
    "not_comparable_with_exact": True,
    "ref": "SINTEF TOP 官方站 200/400/600/800/1000 customers 页",
}

# ======================================= 三、MAPF 公开基准（25.4、25.5 节）

MAPF_BENCHMARK = {
    # 原话 "Makespan. The number of time steps required for all agents to reach their target."
    "makespan_def": "The number of time steps required for all agents to reach their target.",
    # 原话 "Sum of costs. The sum of time steps required by each agent to reach its target."
    "soc_def": "The sum of time steps required by each agent to reach its target.",
    "soc_aka": "flowtime",              # 原话 "Sum of costs is also known as flowtime."
    "n_maps_in_text": 24,               # 正文 "consists of 24 maps taken from"
    "n_map_rows_in_table1": 28,         # 表 1 列了 28 行——**与正文不一致，见资料卡第 8 节**
    "scenarios_per_map": 25,            # 原话 "Every map has 25 scenarios."
    "problems_per_scenario": 1000,      # 原话 "the first 1000 problems were put into the scenario"
    # 原话 "Random. Setting the source and target vertices by randomly choosing vertices
    #       and making sure there is a path in the graph between them."
    "start_target_method": "Random",
    "agents_added_from": 2,             # 从两个智能体的问题开始，"in consecutive order" 逐个加到超时
    "scen_file_format": None,           # movingai.com 本次取不到，.scen 格式未核到
    "even_vs_random_scen": None,        # 论文全文没有出现 "even"，官方说明未核到
    "completeness_def": None,           # 这篇基准论文没有定义完备性
    "optimality_def": None,             # 也没有定义最优性——定义只能引 CBS 论文
    "ref": "Stern, Sturtevant, Felner, Koenig, Ma, Walker, Li, Atzmon, Cohen, Kumar, "
           "Boyarski, Barták, Multi-Agent Pathfinding: Definitions, Variants, and "
           "Benchmarks, SoCS 2019 (arXiv:1906.08291) §2.3、§4.2、§4.3",
}

# ======================================= 四、CBS 的性质（25.5 节；只要性质，不要跑分）

CBS = {
    # 最优性：§5.1 定理 1 原话 "CBS returns an optimal solution."
    "optimal": True,
    "optimality_theorem": "§5.1 Theorem 1: CBS returns an optimal solution.",
    # 原话 §7.3 定理 4 "If Φ is admissible then CBS_Φ is guaranteed to return the optimal solution."
    "optimality_generalized_if_admissible": True,

    # 完备性：**只成立一半**，不许写成 "complete and optimal"
    "complete_phrase_in_paper": None,   # 论文全文没有 "CBS is complete and optimal" 这句
    "returns_solution_if_one_exists": True,     # §5.2 Claim a 原话 "CBS will return a solution if one exists."
    "detects_unsolvable": False,        # §5.2：Claim b "does not always hold for CBS"
    "ct_grows_infinitely_if_unsolvable": True,  # 无解实例上冲突树可以 "grow infinitely"
    "needs_external_solvability_check": True,   # 论文建议先跑独立可解性判定（引 Yu and Rus）
    # §7.4：完备性证明 "holds for any cost function Φ as long as there is a finite
    #        number of solutions per given cost"；fuel 不满足，论文改用 SoC 上的 |V|^4 界
    "completeness_needs_finite_solutions_per_cost": True,

    # 代价函数
    # §2.5 原话 "Sum-of-costs is the summation, over all agents, of the number of
    #            time steps required to reach the goal."
    "soc_def": "the summation, over all agents, of the number of time steps required to reach the goal",
    "fuel_def": "the total amount of distance traveled by all agents",   # §2.5；等待动作不计费
    "soc_example": (2, 3, 5),           # §6.1：2 + 3 = 5

    # 复杂度
    "optimal_mapf_is_np_hard": True,    # §1、§2.5 原话 "has been shown to be NP-hard"
    # §5.3.2 原话 "Since the Conflict Tree grows exponentially in the number of conflicts
    #              encountered, CBS behaves poorly when a set of agents is strongly coupled."
    "exponential_in_conflicts": True,
    "node_bound_is_worst_case_only": True,  # §5.3 的 2^(∝|V|·C*) 是最坏情况界，论文自称不紧
    "runtime_scores": None,             # 跑分本章不收

    "ref": "Sharon, Stern, Felner, Sturtevant, Conflict-based search for optimal "
           "multi-agent pathfinding, Artificial Intelligence (2015) §1、§2.5、§5.1—5.3、§6.1、§7.3、§7.4",
}

# ======================================= 五、无人机官方规格（25.1、25.6 节）
# 纪律：**标称条件核不到的，值一律为 None。**

DRONE_M350 = {
    "model": "DJI Matrice 350 RTK",
    "max_takeoff_weight_kg": 9.2,
    "weight_no_battery_kg": 3.77,       # "Approx. 3.77 kg"（带单个下置吊舱，不含电池）
    "weight_two_tb65_kg": 6.47,         # "Approx. 6.47 kg"
    "max_flight_time_min": 55,
    # 标称条件原话 "Measured with Matrice 350 RTK flying at approximately 8 m/s without
    #              payloads in a windless environment ... until the battery level reached 0%."
    "flight_time_conditions": "约 8 m/s 平飞、无载重、无风、放电到 0%",
    "max_hover_time_min": None,         # 官方页没有单列悬停时间
    "hover_time_conditions": None,
    "max_payload_g": None,              # **官方没给整机最大载重**，不许用起飞重量减空重自己算
    "gimbal_damper_max_payload_g": 960, # 这是单个吊舱减震器的承载，不是整机载重
    "max_wind_ms": 12,
    "wind_conditions": None,            # **官方无脚注，没写是飞行中还是起降时**——口径缺，见引用警告四
    "op_temp_c": (-20, 50),
    "max_horizontal_speed_ms": 23,
    "max_ascent_speed_ms": 6,
    # 两个升限各自带起飞重量上限，拆开引就错
    "max_altitude_m": {5000: "2110s 桨，起飞重量 ≤ 7.4 kg", 7000: "2112 高原低噪桨，起飞重量 ≤ 7.2 kg"},
    "hover_accuracy_conditions": "with moderate or no wind",
    "diagonal_wheelbase_mm": 895,
    "ip_rating": "IP55",                # 官方注：IP 等级 "not permanently effective"
    "ref": "DJI Enterprise 官方 Matrice 350 RTK 规格页",
}

DRONE_M4 = {
    "model": "DJI Matrice 4 Series (4T / 4E)",
    "covers_4d": False,                 # 该规格页只覆盖 4T / 4E，不含 4D / 4TD
    "takeoff_weight_g": 1219,           # 含电池、桨、microSD；官方注批次材料会使实际重量不同
    "max_takeoff_weight_g": {"standard": 1420, "low_noise": 1430},
    "max_payload_g": 200,               # **官方明确给了整机载重，这是它与 M350 的区别**
    "max_flight_time_min": {"standard": 49, "low_noise": 46},
    # 标称条件原话 "Measured with the aircraft flying at approximately 9 m/s without
    #              payloads in a windless environment until the battery level reached 0%."
    "flight_time_conditions": "约 9 m/s 平飞、无载重、无风、放电到 0%",
    "max_hover_time_min": {"standard": 42, "low_noise": 39},
    # 标称条件原话 "Measured by the aircraft hovering in a windless environment at sea
    #              level, from 100% battery level until 0%."
    "hover_time_conditions": "无风、海平面、100% 放到 0%",
    "max_wind_ms": 12,
    "wind_conditions": "Max wind speed resistance during takeoff and landing.",  # **口径与 M350 不同**
    "op_temp_c": (-10, 40),
    "ip_rating": None,                  # 该页机身部分没有列 IP 等级，未核到
    "ref": "DJI Enterprise 官方 Matrice 4 Series 规格页",
}

# ======================================= 六、仓储机器人 / AGV（25.4、25.7 节）

KIVA_PAPER = {
    "authors": "Wurman, D'Andrea, Mountz (Kiva Systems)",
    "title": "Coordinating Hundreds of Cooperative, Autonomous Vehicles in Warehouses",
    "venue_verified": None,             # 本次拿到的 PDF 只有 AAAI 2007 版权页，卷期未核定
    "is_vendor_self_report": True,      # **作者就是厂商本人，这是自述，不是第三方实测**
    "typical_installation": "hundreds of robots",    # 原话
    "fielded_robots": 120,              # 原话 "At well over 120 robots working 24 hours a day"（是“远超 120”）
    "fielded_hours_per_day": 24,
    "pod_face_seconds": 6,              # 原话 "delivers a new pod face every six seconds"
    "baseline_lines_per_hour": 600,     # 原话 "sets a baseline picking rate of 600 lines per hour"
    "is_design_cadence_not_measured": True,  # **这是 6 s 折算出来的设计节拍，不是统计实测**
    "manual_baseline_lines_per_hour": None,  # 人工拣选的基线对照：论文没给
    "measurement_period": None,         # 统计期：没给
    "measured_by": None,                # 测量方：没有第三方
    "path_planning": "standard implementation of A*",    # 原话
    "allocation": "making decisions on the fly using utility-based heuristics",   # 原话
    "no_single_point_of_failure": True, # 原话 "if a drive unit fails, it does not stop the whole floor"
    "charging_strategy": None,          # 论文不讲充电与电源管理
    "stopping_distance": None,          # 论文不讲停车距离、避碰细节与安全标准
    "vehicle_speed": None,              # 论文不讲车速与硬件规格
    "ref": "Wurman, D'Andrea, Mountz, Coordinating Hundreds of Cooperative, Autonomous "
           "Vehicles in Warehouses（The Kiva Solution、Resource Allocation、Path Planning 各节）",
}

# ISO 3691-4：**只核到条款标题与版本日期，条文一律未核到**
ISO_3691_4 = {
    "edition": "2023-06",
    "clause_titles": (
        "4.1.26 Normal stop",
        "4.1.27 Operational stop",
        "4.2 Braking system",
        "4.3 Speed control (4.3.1 Overspeed detection; 4.3.2 Speed and stability)",
        "4.4 Automatic battery charging",
        "4.8.1 Emergency stop",
        "4.8.2 Detection of persons in the path",
        "5.2 Tests for detection of persons",
    ),
    "numeric_requirements": None,       # 官方预览页只给目录与前言，没有任何数值要求
    "stopping_distance_m": None,
    "speed_limit_ms": None,
    "ref": "ISO 3691-4:2023 官方预览页（ANSI Webstore）；前言另称 Scope 已更新以列出未覆盖的重大危险",
}

# 本章仓储算例用的参数：**显式假设**，写在正文里，不取自任何厂家样本
WAREHOUSE_ASSUMED = {
    "note": "25.4、25.7 节的吞吐、车速、充电门限、安全距离全部是显式假设，不取自任何厂家样本",
    "is_explicit_assumption": True,
}

# ======================================= 七、排队论：利特尔法则（25.7 节）

LITTLES_LAW = {
    "formula": "L = λW",
    "L": "系统中单元数的均值",
    "W": "一个单元在系统中停留时间的均值",
    "lambda_def": "1/λ 为相邻两个单元到达的平均间隔时间",   # 摘要 "let 1/λ be the mean time between the arrivals"
    # 适用条件原话 "if the three means are finite and the corresponding stochastic processes
    #              strictly stationary, and, if the arrival process is metrically transitive
    #              with nonzero mean, then L = λW"
    "conditions": (
        "三个均值有限（the three means are finite）",
        "相应随机过程严格平稳（the corresponding stochastic processes strictly stationary）",
        "到达过程度量传递且均值非零（the arrival process is metrically transitive with nonzero mean）",
    ),
    "independent_of_queue_discipline": None,    # “与服务规则、到达分布无关”本次未核到摘要原话
    "source_is_abstract_not_body": True,        # 本条取自摘要，不是正文
    "ref": "John D. C. Little, A Proof for the Queuing Formula: L = λW, "
           "Operations Research 9(3), 383–387 (1961), DOI 10.1287/opre.9.3.383（摘要）",
}

# ======================================= 八、本章明确不印的数

NOT_PRINTED = {
    "ops_efficiency_pct": "任何企业运营口径的“AI/自动化让物流效率提升百分之多少”“省了多少人力/多少台车”"
                          "——基线、规模、统计期、测量方四样齐全才印；本次一组都没齐",
    "kiva_throughput_as_evidence": "Kiva 的 600 行/小时**不得当作“自动化提升了多少吞吐”的证据**："
                                   "它是每 6 秒一个 pod 面折算出来的设计节拍，厂商自述，"
                                   "基线对照、统计期、第三方测量方三样全缺",
    "cross_paper_speedup": "跨论文的“比别人快多少/好多少”——VRP 两边目标函数不同（SINTEF 官方自己写明"
                           "不可直接比较），MAPF 两边代价函数不同，还有超时上限与成功率的差别",
    "improvement_without_bound": "**没有已证明最优解或下界作对照的任何“改进幅度”**——本章硬规矩，"
                                 "只跟另一个启发式比出来的百分比不采信",
    "agv_throughput": "仓储机器人/AGV 的吞吐实测统计——没核到任何带基线、规模、统计期、测量方的公开原始值",
    "agv_charging": "仓储机器人的充电门限、充电时长与换电策略——没核到官方文档",
    "agv_stopping_distance": "AGV 安全停车距离与速度上限——ISO 3691-4 条文本次拿不到，只有条款标题",
    "m350_max_payload": "Matrice 350 RTK 的整机最大载重——官方没给；**不许从最大起飞重量减空重自己算**",
    "m350_hover_time": "Matrice 350 RTK 的最大悬停时间——官方页未单列",
    "m4_ip_rating": "Matrice 4 系列机身的 IP 等级——官方页未列",
    "spec_without_conditions": "任何没有标称条件的无人机规格值——标称条件核不到，值就不印",
    "solomon_classes": "Solomon 的六个类（C1/C2/R1/R2/RC1/RC2）与实例总数——SINTEF 官方页未给，"
                       "要引必须回 Solomon 1987 原文",
    "mapf_scen_format": "MAPF `.scen` 文件格式与 random/even 两类场景的官方区别——movingai.com 本次取不到，"
                        "基准论文正文只写了 Random 一种方法、全文没有 “even”",
    "cbs_complete_and_optimal": "“CBS is complete and optimal”这句常见表述——论文正文没有这一句，"
                                "不许当原话引；论文把完备性拆成 Claim a（成立）与 Claim b（不总成立）两半",
    "cvrplib_xml_count": "CVRPLIB XML 集的实例数——库首页显示 0 个，官方 BKS Challenge 页说 10000 个，"
                         "两处对不上，本章只引“全部已知最优解”这句性质",
    "mapf_n_maps": "MAPF 基准的地图数——正文写 24，表 1 列 28 行，两处不一致；要印须回表 1 自己数",
    "littles_law_discipline": "利特尔法则“与服务规则、到达分布无关”的原话——本次未核到",
}


def check() -> None:
    """几条最容易被引错的，用断言钉住。"""

    # ---- 本章第一号纪律：BKS 与已证明最优解必须是两个不同的字段，且不许混用 ----
    assert CVRP_BKS is not CVRP_X_PROVEN_OPTIMAL, \
        "BKS 与已证明最优解必须分成两个字典，不许合并"
    assert CVRP_BKS["is_proven"] is False and CVRP_X_PROVEN_OPTIMAL["is_proven"] is True, \
        "BKS 不是已证明最优解：一个是上界，一个是真值"
    assert CVRP_BKS["is_upper_bound"] is True, \
        "BKS 是“历史上找到过的最好解”，是会往下走的上界"
    assert "is_proven" in CVRP_BKS and "is_proven" in CVRP_X_PROVEN_OPTIMAL, \
        "两个字典都必须自带 is_proven 标记，引用时先看这一位"
    # 两个字典不许出现同名的解值字段，防止把 BKS 当最优解代进去
    assert not ({"n_proven_optimal_today", "n_proven_optimal_uchoa2017", "optimal_marker_in_paper"}
                & set(CVRP_BKS)), \
        "“已证明最优”的字段不许出现在 BKS 字典里"
    assert CVRP_BKS["formal_definition_on_library_page"] is None, \
        "CVRPLIB 库页面没有写 BKS 的定义，不许补一个"

    # 同一个 X 集，“已证明最优”随时间变化——引用必须带时点
    assert CVRP_X_PROVEN_OPTIMAL["n_proven_optimal_uchoa2017"] \
        < CVRP_X_PROVEN_OPTIMAL["n_proven_optimal_today"] \
        < CVRP_X_PROVEN_OPTIMAL["n_instances"], \
        "40（2017）< 61（今天）< 100：BKS 与已证明最优都会随时间变化"
    assert (CVRP_X_PROVEN_OPTIMAL["n_proven_optimal_today"]
            + CVRP_X_PROVEN_OPTIMAL["n_not_proven_today"]
            == CVRP_X_PROVEN_OPTIMAL["n_instances"]), "61 + 39 = 100"
    assert CVRPLIB_COLUMNS == ("|C|", "UB", "Opt"), \
        "库里 UB（上界）与 Opt（是否已证明最优）本来就是两列——这是本章第一号警告的证据"

    # XL 这种规模没有最优解可比，只能跟 BKS 或下界比
    assert CVRP_XL_BEYOND_EXACT["beyond_exact_methods"] is True, \
        "XL 集 “beyond the reach of current exact methods”，那里说的是“离最好已知结果多远”"

    # ---- VRPTW：官方只给 best known，而且官方自己说不可直接比较 ----
    for d, name in ((SOLOMON, "Solomon"), (HOMBERGER, "Gehring & Homberger")):
        assert d["solutions_are_best_known_only"] is True and d["has_optimality_marker"] is False, \
            f"{name} 官方表只称 best known，没有最优性标记"
        assert d["not_comparable_with_exact"] is True, \
            f"{name} 用的是分层目标，官方写明与精确算法的结果不可直接比较"
    assert SOLOMON["classes"] is None and SOLOMON["n_instances"] is None, \
        "Solomon 的类结构与实例总数官方页没给，不许补"

    # ---- MAPF：makespan 与 sum-of-costs 是两个不同的代价，不可混用 ----
    assert MAPF_BENCHMARK["makespan_def"] != MAPF_BENCHMARK["soc_def"], \
        "makespan 与 sum-of-costs 定义不同，最优解不是同一个解"
    assert MAPF_BENCHMARK["soc_aka"] == "flowtime"
    assert MAPF_BENCHMARK["scenarios_per_map"] == 25 \
        and MAPF_BENCHMARK["problems_per_scenario"] == 1000, \
        "一张地图 25 个场景、每个场景 1000 对起终点，是论文正文的原始值"
    assert MAPF_BENCHMARK["n_maps_in_text"] != MAPF_BENCHMARK["n_map_rows_in_table1"], \
        "正文 24 与表 1 的 28 行不一致——这处矛盾要留着，不许抹平"
    assert MAPF_BENCHMARK["scen_file_format"] is None \
        and MAPF_BENCHMARK["even_vs_random_scen"] is None, \
        "movingai.com 本次取不到，.scen 格式与 random/even 的区别未核到"
    assert MAPF_BENCHMARK["completeness_def"] is None \
        and MAPF_BENCHMARK["optimality_def"] is None, \
        "基准论文没有定义完备性与最优性，定义只能引 CBS 论文"

    # ---- CBS：最优性是定理，完备性只成立一半，不许写成 "complete and optimal" ----
    assert CBS["complete_phrase_in_paper"] is None, \
        "论文全文没有 “CBS is complete and optimal” 这句，不许当原话引"
    assert CBS["optimal"] is True and CBS["returns_solution_if_one_exists"] is True, \
        "最优性（定理 1）与“有解必能找到”（Claim a）都成立"
    assert CBS["detects_unsolvable"] is False and CBS["ct_grows_infinitely_if_unsolvable"] is True, \
        "Claim b 不总成立：无解实例上冲突树可以无限增长，所以不是无条件完备"
    assert CBS["needs_external_solvability_check"] is True, \
        "论文自己建议先跑独立的可解性判定"
    assert CBS["optimal_mapf_is_np_hard"] and CBS["exponential_in_conflicts"], \
        "求最优 MAPF 是 NP-hard；CBS 随冲突数指数增长"
    assert CBS["node_bound_is_worst_case_only"] is True, \
        "§5.3 的节点数界是最坏情况界，论文自称不紧"
    assert CBS["runtime_scores"] is None, "本章只要性质，不要跑分"
    a, b, s = CBS["soc_example"]
    assert a + b == s, "§6.1 的例子：2 + 3 = 5"

    # ---- 无人机：**没有标称条件的规格值必须为 None** ----
    for d in (DRONE_M350, DRONE_M4):
        model = d["model"]
        if d["max_flight_time_min"] is not None:
            assert d["flight_time_conditions"], f"{model}：续航印出来就必须带标称条件"
        if d["max_hover_time_min"] is not None:
            assert d["hover_time_conditions"], f"{model}：悬停时间印出来就必须带标称条件"
        # 抗风：标称条件核不到的，本卡把条件记为 None，正文不许并列成“都抗 12 m/s 风”
        assert d["max_wind_ms"] == 12
    assert DRONE_M350["wind_conditions"] is None \
        and DRONE_M4["wind_conditions"] is not None, \
        "两家抗风口径不同：M350 无脚注，M4 明写 during takeoff and landing——不许并列"
    assert DRONE_M350["max_payload_g"] is None, \
        "M350 官方没给整机最大载重，不许用最大起飞重量减空重自己算"
    assert DRONE_M350["gimbal_damper_max_payload_g"] == 960, \
        "960 g 是单吊舱减震器承载，不是整机载重"
    assert DRONE_M350["max_hover_time_min"] is None, "M350 官方页未单列悬停时间"
    assert DRONE_M4["ip_rating"] is None, "M4 机身 IP 等级官方页未列"
    assert DRONE_M4["max_payload_g"] == 200, "M4 官方明确给了整机载重 200 g"
    assert DRONE_M350["weight_no_battery_kg"] < DRONE_M350["weight_two_tb65_kg"] \
        < DRONE_M350["max_takeoff_weight_kg"], "空重 < 带电池重 < 最大起飞重量"
    assert set(DRONE_M350["max_altitude_m"]) == {5000, 7000} \
        and all(DRONE_M350["max_altitude_m"].values()), \
        "两个升限各自带起飞重量上限，拆开引就错"

    # ---- 仓储：600 行/小时是折算出来的设计节拍，四样口径缺三样 ----
    assert KIVA_PAPER["pod_face_seconds"] * KIVA_PAPER["baseline_lines_per_hour"] == 3600, \
        "600 行/小时 = 3600 s ÷ 6 s——它是算术折算，不是实测"
    assert KIVA_PAPER["is_design_cadence_not_measured"] is True \
        and KIVA_PAPER["is_vendor_self_report"] is True, \
        "设计节拍 + 厂商自述：不许当成“自动化提升了多少吞吐”的证据"
    assert KIVA_PAPER["manual_baseline_lines_per_hour"] is None \
        and KIVA_PAPER["measurement_period"] is None \
        and KIVA_PAPER["measured_by"] is None, \
        "基线、统计期、测量方三样全缺——按本章规矩只能连缺口一起印"
    assert KIVA_PAPER["charging_strategy"] is None \
        and KIVA_PAPER["stopping_distance"] is None \
        and KIVA_PAPER["vehicle_speed"] is None, \
        "充电策略、停车距离、车速论文都不讲，不许补"
    assert KIVA_PAPER["venue_verified"] is None, "卷期未核定，付印前须核"
    assert ISO_3691_4["numeric_requirements"] is None \
        and ISO_3691_4["stopping_distance_m"] is None \
        and ISO_3691_4["speed_limit_ms"] is None, \
        "ISO 3691-4 条文本次拿不到，只有条款标题——不许印任何数值"
    assert len(ISO_3691_4["clause_titles"]) == 8
    assert WAREHOUSE_ASSUMED["is_explicit_assumption"] is True, \
        "本章仓储算例的参数全是显式假设"

    # ---- 利特尔法则：三个条件必须齐 ----
    assert LITTLES_LAW["formula"] == "L = λW"
    assert len(LITTLES_LAW["conditions"]) == 3, \
        "均值有限、严格平稳、到达过程度量传递——三个条件缺一不可"
    assert LITTLES_LAW["independent_of_queue_discipline"] is None, \
        "“与服务规则无关”未核到原话，不许印"
    assert LITTLES_LAW["source_is_abstract_not_body"] is True, \
        "本条取自 1961 年论文摘要，不是正文"

    # ---- 不印清单必须盖住本章两条硬规矩 ----
    assert "improvement_without_bound" in NOT_PRINTED, \
        "“没有最优解或下界作对照的改进不采信”必须在不印清单里"
    assert "ops_efficiency_pct" in NOT_PRINTED and "spec_without_conditions" in NOT_PRINTED
    assert "cbs_complete_and_optimal" in NOT_PRINTED


check()
