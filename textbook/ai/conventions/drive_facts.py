"""第 23 章（自动驾驶）要印的公开数字与官方口径，一处定义、处处引用。

出处逐条记在
`docs/教材/人工智能/参考/第23章_自动驾驶原始数字资料_2026-11.md`（建卡 2026-11-18）。

纪律与第 17—22 章同，本章从严：只收**论文正文、官方公告、官方文档、官方规格书、官方建模
假设**给出的原始值；二手新闻稿、博客转述、维基百科一律不算，除非它本身就是官方发布。
每条都要有口径（谁测的、怎么测的、统计期多长、基线是什么、定义是什么）；口径不全的，
值可以留在这里但其口径字段必须写 `None`，并进 `NOT_PRINTED`；核不到的字段写 `None`。

本章另有一条自己的纪律：**不收跨研究、跨厂家的“准多少”“安全多少倍”“效率提升百分之多少”
的比较数字**，除非基线、规模口径、统计期、测量方四样齐全。本次查下来，本章这类数字
**没有一条四样齐全**——全部进 `NOT_PRINTED`。

本章的重点不是数值，是三份官方口径文件：
  * SAE J3016 的等级定义口径（注意 2026-09-20 已改版，见 `J3016`）
  * 加州 13 CCR § 227.50 的脱离报告口径（见 `CA_DISENGAGEMENT`）
  * NHTSA SGO 2021-01 的上报口径与**官方自陈局限**（见 `NHTSA_SGO`、`SGO_CAVEATS`）
"""
from __future__ import annotations

# ============================================== 一、SAE J3016 驾驶自动化等级（23.1 节）

J3016 = {
    # 版本：**现行版是 2026 年的那一版**，2021 版在 SAE 官网上已标 Historical
    "current_revision": "J3016_202609",        # 官方页 "Revised 9/20/2026"
    "current_revision_date": "2026-09-20",
    "previous_revision": "J3016_202104",       # 官方页 "Revised 4/30/2021"，状态栏标 Historical
    "previous_revision_date": "2021-04-30",
    "all_revisions": ("J3016_202609", "J3016_202104", "J3016_201806",
                      "J3016_201609", "J3016_201401"),
    "committee": "On-Road Automated Driving (ORAD) Committee",
    "document_type": "Recommended Practice",   # 推荐实践，不是强制标准
    # 2026 版正文原话：
    "not_a_safety_standard": True,             # "this document provides a taxonomy and definitions and is not a safety standard"
    "n_levels": 6,
    # **简称不是定义**——2026 版自己写的，引用时必须一起印
    "descriptors_are_not_definitions": True,   # "these are NOT the definitions of the levels of driving automation"
    # L0—L5 的**定义原文**（Sections 4、5）核不到：正文为付费标准
    "level_definitions": None,
    # ODD 的定义原文也核不到（该条目在付费正文内；公开预览到 §3.12 截断）
    "odd_definition": None,
    "ref": "SAE Mobilus 官方标准页 saemobilus.sae.org/content/j3016_202104 与 /j3016_202609",
}

# 两版的**简称**原文（都是官方 Scope 原文）。**这是简称，不是定义**，见上面那个布尔量。
LEVEL_DESCRIPTORS_202104 = {
    0: "No Driving Automation",
    1: "Driver Assistance",
    2: "Partial Driving Automation",
    3: "Conditional Driving Automation",
    4: "High Driving Automation",
    5: "Full Driving Automation",
}

LEVEL_DESCRIPTORS_202609 = {
    0: "No driving automation",
    1: ("Driver support for steering OR speed, with continual driver supervision "
        "necessary and driver intervention when needed"),
    2: ("Driver support for steering AND speed, with continual driver supervision "
        "necessary and driver intervention when needed"),
    3: ("Automated driving under defined conditions, with human driving needed "
        "following an alert or evident vehicle malfunction"),
    4: ("Automated driving under defined conditions, with human driving not needed "
        "to mitigate risk"),
    5: ("Automated driving under all conditions in which humans can drive, with "
        "human driving not needed"),
}

# 能核到原文的官方定义：取自 ISO/SAE PAS 22736:2021(E) 公开样页（＝ J3016_202104 的国际版）。
# **这是 2021 年版的措辞；2026 版是否改动本次未核到**（见 `iso_version_checked_against_2026`）。
ISO_SAE_22736_DEFS = {
    "ads": ("The hardware and software that are collectively capable of performing the entire "
            "DDT on a sustained basis, regardless of whether it is limited to a specific "
            "operational design domain (ODD); this term is used specifically to describe a "
            "Level 3, 4, or 5 driving automation system."),          # §3.2
    "ads_levels": (3, 4, 5),            # ADS 专指 L3—L5；泛称 driving automation system 是 L1—L5
    "ddt": ("All of the real-time operational and tactical functions required to operate a "
            "vehicle in on-road traffic, excluding the strategic functions such as trip "
            "scheduling and selection of destinations and waypoints"),  # §3.10
    "ddt_subtasks": 6,                  # §3.10 列了 6 项子任务
    "ddt_fallback": ("The response by the user to either perform the DDT or achieve a minimal "
                     "risk condition (1) after occurrence of a DDT performance-relevant system "
                     "failure(s), or (2) upon operational design domain (ODD) exit, or the "
                     "response by an ADS to achieve minimal risk condition, given the same "
                     "circumstances."),                                # §3.12
    # 主动安全（ESC/AEB/LKA）为什么不算驾驶自动化：不是 "on a sustained basis"
    "active_safety_excluded_because": "do not perform part or all of the DDT on a sustained basis",
    "source_is_public_preview": True,   # 13 页公开预览件，到 §3.12 截断
    "iso_version_checked_against_2026": None,   # 新版是否改了这几条——**未核到**
    "ref": "ISO/SAE PAS 22736:2021(E) 公开样页，§3.2、§3.10、§3.12；SAE Mobilus Scope 原文",
}

# ====================================== 二、加州 DMV 脱离报告口径（23.5 节）——本章最要紧

CA_DISENGAGEMENT = {
    "citation": "13 CCR § 227.50",
    "article": "Article 3.7 — Testing of Autonomous Vehicles",   # **测试**许可，不含部署许可
    "applies_to_deployment_permits": False,     # 条文原话 "authorized under this article to test"
    # 法定定义（三种情形并列）：
    "definition": ("a deactivation of the autonomous mode when a failure of the autonomous "
                   "technology is detected or when the safe operation of the vehicle requires "
                   "that the autonomous vehicle test driver disengage the autonomous mode and "
                   "take immediate manual control of the vehicle, or in the case of driverless "
                   "vehicles, when the safety of the vehicle, the occupants of the vehicle, or "
                   "the public requires that the autonomous technology be deactivated"),
    "n_triggering_situations": 3,
    # 报告周期：**不是自然年**
    "period_start": "12-01",                    # "December 1st of the current year"
    "period_end": "11-30",                      # "to November 30th of the following year"
    "is_calendar_year": False,
    "due_date": "01-01",                        # "by January 1st, of each year"
    # 必报字段（(b)(3)）：
    "fields": ("capable of operating without a driver",
               "location: interstate, freeway, highway, rural road, street, or parking facility",
               "whether the vehicle was operating with or without a driver",
               "description of the facts causing the disengagements",
               "the party that initiated the disengagement"),
    "n_location_categories": 6,                 # 只有六个粗分类，不分 ODD 难度
    "initiator_options": ("autonomous technology", "autonomous vehicle test driver",
                          "remote operator", "passenger"),
    "plain_language_required": True,            # "written in plain language … a non-technical person can understand"
    "mileage_basis": "每辆车、每月，公共道路上 autonomous mode 的总英里数",   # (b)(4)
    "form": "OL 311R (Rev. 7/2020)",            # (c)
    # 判定权在厂家：法规没给阈值、没有第三方复核程序
    "threshold_defined_by_regulator": False,
    "third_party_verification": None,           # 法规未设
    # 任何数值都不印
    "official_annual_totals": None,             # DMV 官方汇总页本次未核到
    "text_source_is_official_publication": False,   # 条文经康奈尔 LII 转录，非 OAL 官方出版物
    "ref": "13 CCR § 227.50(a)—(c)，经 Cornell LII 全文转录；付印前须回加州官方 CCR 逐字核",
}

# ============================= 三、NHTSA Standing General Order 2021-01（23.5 节）

NHTSA_SGO = {
    "original_date": "2021-06-29",
    "first_amended_date": "2021-08-12",
    "second_amended_effective": "2023-05-15",   # "takes effect on May 15, 2023, and … supersedes"
    "third_amended_effective": "2025-06-16",    # 官方页 "went into effect on June 16, 2025"
    "third_amended_issued": "2025-04-24",
    # **下面的触发条件与时限是第二次修订令（2023 版）的**，第三修订令全文未核到
    "triggers_from_revision": "second amended (2023-05-15)",
    "third_amendment_triggers": None,           # 现行版的触发条件与字段——**未核到**
    "engagement_window_s": 30,                  # "at any time during the period from 30 seconds immediately prior to the commencement of the crash"
    "road_scope": "on a publicly accessible road in the United States",
    "one_day_trigger": ("a fatality", "any individual being transported to a hospital for "
                        "medical treatment", "involves a vulnerable road user"),
    "one_day_deadline_days": 1,
    "one_day_update_day": 10,                   # "on the tenth (10th) calendar day"
    "five_day_trigger": ("a vehicle tow-away", "an air bag deployment"),
    "five_day_deadline_days": 5,
    "monthly_due_day": 15,                      # 月报、更新报、"无事可报"确认报都是次月 15 日
    "monthly_report_mandatory_even_if_empty": True,   # Instruction 5: "at least one report every month"
    # 知悉即报，**不要求厂家先核实**
    "notice_regardless_of_verification": True,  # "regardless of whether the manufacturer has verified those facts"
    "field_list": None,                         # Appendix C 在 PDF 里是静态图，完整字段表未核到
    # 表里确实有一栏问"当时在不在 ODD 内"——与第 1 节的 ODD 口径对上
    "cbi_eligible_fields": ("ADAS/ADS HARDWARE VERSION", "ADAS/ADS SOFTWARE VERSION",
                            "WAS VEHICLE WITHIN ITS ODD AT THE TIME OF THE INCIDENT?",
                            "NARRATIVE"),
    "data_made_public": True,                   # Instruction 6: "intends to make it publicly available"
    "data_dictionary_date": "2026-11-16",
    "data_through": "2026-10-15",               # "Data release of reports received through October 15, 2026"
    "prepared_by": "USDOT / NHTSA Office of Defects Investigation",
    "ref": ("NHTSA 官方 PDF Second-Amended-SGO-2021-01_2023-04-05_2.pdf；官方页 "
            "nhtsa.gov/SGOCrashReporting；官方《SGO 2021-01 Data Dictionary》2026-11-16"),
}

# **本章最有价值的一条：监管方自己写的局限。** 逐字引，正文整段印。
SGO_CAVEATS = {
    "preamble": ("It is crucial to understand the terms and requirements of the General Order, "
                 "the data it aims to obtain, and the limitations of the data for accurate "
                 "interpretation and analysis."),
    "six_bullets": (
        "Reporting requirements are different for Automated Driving Systems (ADS) and Level 2 "
        "Advanced Driver Assistance System (ADAS).",
        "Access to crash data may affect crash reporting.",
        "Incident report data may be incomplete or unverified.",
        "Indicated Confidential Business Information (CBI) and Personally Identifiable "
        "Information (PII) are redacted.",
        "The same crash may have multiple reports.",
        "Summary incident report data are not normalized.",
    ),
    # 官方页上的展开说明：
    "capability_varies": ("Crash data recording and telemetry capabilities may vary widely by "
                         "manufacturer and driving automation system."),
    "l2_limited": ("Many Level 2 ADAS partial automated systems may be limited in their "
                   "capabilities to record data"),
    "l2_privately_owned": ("Level 2 vehicles equipped with partial automation systems are "
                           "generally privately owned"),
    "timeliness": ("timeliness of the General Order reporting is dependent on if and when the "
                   "manufacturer becomes aware of the crash"),
    "not_representative": ("the summary incident report data should not be assumed to be "
                           "statistically representative of all crashes."),
    "no_fleet_size": ("Reporting entities are not required to submit information regarding the "
                      "number of vehicles they have manufactured"),
    "not_normalized": "have not, therefore, been normalized or adjusted by any measure of exposure",
    # **监管方自己说的"不要横向比较"**
    "do_not_compare": "Use caution when attempting to compare crash data between entities.",
    "only_known_crashes": ("Reporting entities are required to report only those crashes that "
                           "they know about."),
    "comparison_validity": ("can and likely would affect the validity of comparisons of crash "
                            "data between entities."),
    "ref": "NHTSA《SGO 2021-01 Data Dictionary》§1（2026-11-16）与官方页 nhtsa.gov/SGOCrashReporting",
}

# ====================================== 四、公开数据集的规模与标注口径（23.3 节）

NUSCENES = {
    "cameras": 6, "radars": 5, "lidars": 1,
    "full_360": True,                   # "all with full 360 degree field of view"
    "cam_hz": 12, "cam_res": (1600, 900),
    "lidar_beams": 32, "lidar_hz": 20, "lidar_range_m": 70, "lidar_accuracy_cm": 2,
    "radar_range_m": 250, "radar_ghz": 77, "radar_hz": 13,
    "scenes": 1000, "scene_seconds": 20,
    "scenes_manually_selected": True,   # "we manually select 1000 interesting scenes"
    "keyframe_hz": 2,                   # **采 12/20 Hz，只标 2 Hz 的关键帧**
    "keyframes": 40_000,
    "boxes_3d": 1_400_000,
    "images": 1_400_000,
    "lidar_sweeps": 400_000, "radar_sweeps": 1_300_000,
    "classes": 23, "attributes": 8, "map_layers": 11,
    "cities": 2,                        # Boston 与 Singapore
    "city_names": ("Boston", "Singapore"),
    "scene_locations": 4,               # Boston 55% / SG-OneNorth 21.5% / SG-Queenstown 13.5% / SG-HollandVillage 10%
    "rain_pct": 19.4, "night_pct": 11.6,
    "logs": 84, "drive_hours": 15.0, "drive_km": 242, "avg_kmh": 16,
    "peds_per_keyframe": 7, "vehicles_per_keyframe": 20,
    "paper_version": "arXiv:1903.11027v5（CVPR 2020）",
    "describes_initial_release": True,  # 论文描述的是初版规模
    "official_site_version_numbers": None,      # 官网脚本渲染，现行版本号与子集规模未核到
    "ref": "H. Caesar et al., nuScenes, CVPR 2020（arXiv:1903.11027v5）摘要、§3、§4、Table 1、Table 2",
}

WAYMO_OPEN = {
    "lidars": 5, "cameras": 5,
    "radars": 0,
    "lidar_range_restricted": True,     # "We restrict the range of the LiDAR data"
    "lidar_returns": 2,                 # "the first two returns of each laser pulse"
    "cam_res_front": (1920, 1280), "cam_res_side": (1920, 1040),
    "cam_hfov_deg": 25.2,               # ±25.2°，五个针孔相机合起来**不是** 360°
    "full_360": False,
    "cam_rolling_shutter": True,
    "cam_cropped_and_downsampled": True,    # "reflect the results of both cropping and downsampling"
    "scenes": 1150, "scene_seconds": 20,
    "sample_hz": 10,
    "boxes_3d": 12_000_000,             # "around 12 million LiDAR box annotations"
    "boxes_2d": 12_000_000,             # "around 12 million camera box annotations"
    "tracking_ids": 113_000,
    "exhaustive_labels": True,          # "exhaustively annotated"，"manually created"
    "classes": 4,                       # vehicle / pedestrian / sign / cyclist
    "cities": 3,
    "city_names": ("San Francisco", "Phoenix", "Mountain View"),
    "area_phoenix_km2": 40, "area_sf_mtv_km2": 36,
    "sync_error_ms_bound": None,        # "bounded in [-6ms, …]"，上界抓取被截断，付印前回正文补
    "paper_version": "arXiv:1912.04838v7（CVPR 2020）",
    "describes_initial_release": True,
    "official_site_scale_numbers": None,    # 公开页不列规模，数据页需 Google 登录
    "ref": "P. Sun et al., Waymo Open Dataset, CVPR 2020（arXiv:1912.04838v7）摘要、§3.1—3.3、§4、Table 3、Table 4",
}

# 为什么**不能**拿这两个数据集比大小：框数差主要来自标注频率口径差（nuScenes 自己的表注）
DATASET_NOT_COMPARABLE = {
    "nuscenes_table1_footnote": ("The current Waymo Open dataset size is comparable to nuScenes, "
                                 "but at a 5x higher annotation frequency."),
    "reasons": ("标注频率不同（2 Hz 对 10 Hz）", "nuScenes 有 5 台 360° 毫米波雷达，Waymo 没有雷达",
                "Waymo 有 5 台激光雷达但作了距离截断，nuScenes 只有 1 台 32 线",
                "类别粒度 23 对 4", "城市与地理覆盖口径不同"),
    "four_conditions_complete": False,  # 基线、规模口径、统计期、测量方——"规模口径"这一样就对不上
}

# ====================================== 五、车载计算平台的公开标称算力（23.4 节）

# 只印**精度写进了官方原话**的两条，并且必须连 "up to" 与"稀疏化未标"一起印。
DRIVE_ORIN = {
    "soc": "Single AGX Orin SoC",
    "arch": "Ampere architecture-class",
    "int8_tops": 254,                   # 原话 "up to 254 INT8 TOPS"
    "dla_int8_tops": 87,                # 原话 "including a Deep Learning Accelerator (DLA) with 87 INT8 TOPS"
    "fp32_tops": 5.2,                   # 原话 "| 5.2 FP32 TOPS"
    "precision_stated": "INT8 / FP32",  # 精度口径**给了**
    "sparsity_stated": None,            # 是否含稀疏化——**官方规格页未标**
    "is_peak_up_to": True,              # "up to"：峰值，不是持续
    "dla_included_in_total": True,       # 官方把 254 写成**包含** DLA 的 87
    "cpu": "12 Cortex®-A78A",
    "ref": "NVIDIA 官方开发者页 developer.nvidia.com/drive/agx",
}

DRIVE_THOR = {
    "soc": "Single AGX Thor SoC",
    "arch": "Blackwell architecture class",
    "int8_tops": 1000,                  # 原话 "up to 1000 INT8 TOPS"
    "fp4_flops": 2000,                  # 原话 "| 2000 FP4 FLOPs"——同一块片子，精度一换就是 2 倍
    "precision_stated": "INT8 / FP4",
    "sparsity_stated": None,            # **未标**
    "is_peak_up_to": True,
    "cpu": "ARM® Neoverse V3AE",
    "ref": "同上",
}

# **不印**：精度与稀疏化都没标，而且 NVIDIA 官网两页自相矛盾。留在这里只为讲口径。
JETSON_CONFLICT = {
    "agx_orin_tops": 275,               # "up to 275 TOPS"，**没写精度**
    "agx_orin_watts": (15, 60),
    "orin_nx_tops_page_a": 100,         # developer.nvidia.com/embedded/jetson-orin
    "orin_nx_tops_page_b": 157,         # developer.nvidia.com/embedded/jetson-modules
    "orin_nano_tops_page_a": 40,
    "orin_nano_tops_page_b": 67,
    "precision_stated": None,           # 两页都没写精度
    "sparsity_stated": None,
    "same_vendor_official_pages_conflict": True,
    "printable": False,                 # **本章不印这几个数**
    "ref": "NVIDIA 官方页 developer.nvidia.com/embedded/jetson-orin 与 /embedded/jetson-modules",
}

OTHER_VENDORS = {
    "mobileye": None, "tesla": None, "cn_vendors": None,    # 官方规格页本次未取到
    "ref": "未核到",
}

# ====================================== 六、时延口径（23.4 节）

LATENCY = {
    # **“感知到执行的端到端时延预算”——未核到任何官方文件或论文正文的原始说法**
    "sensor_to_actuation_budget_ms": None,
    # 能核到的最接近的原始测量，**口径里明确排除了采集与执行两端**，所以不是端到端
    "autoware_perception_to_decision_before_ms": 521.91,
    "autoware_perception_to_decision_after_ms": 290.26,
    "is_sensor_to_actuation": False,
    "excludes": "sensor capture and downstream actuation are excluded",
    "stack": "Autoware.Universe（2024 年 3 月版本）",
    "platforms": ("NVIDIA Jetson Orin Nano", "a full-scale production-ready L4 vehicle"),
    "baselines": ("Fast DDS（共享内存配置）", "Zenoh"),
    "runs": "5 runs × 10 minute runs，记 min/mean/p95/p99/max/std",
    "qos": "best-effort (depth=1)",
    # 该文 Fig. 7 的结构性观察——本章要讲的反直觉结论
    "comm_vs_compute": ("In preprocessing and planning tasks, the communication latency "
                        "transferring the data to downstream critical applications is much "
                        "larger than the task itself. In perception tasks, the communication "
                        "latency takes about the same amount of time used by the "
                        "detection-tracking algorithms."),
    "ref": "arXiv:2510.11448v2，A Faster and More Reliable Middleware for Autonomous Driving Systems",
}

# ====================================== 七、本章明确不印的数

NOT_PRINTED = {
    "sae_level_definitions": ("SAE L0—L5 的“定义”原文——正文为付费标准，核不到；"
                              "且 SAE 自己明说简称 “are NOT the definitions”，不许拿简称当定义"),
    "odd_definition": "ODD 的定义原文——J3016 与 ISO/SAE 22736 的该条目在付费正文内，未核到",
    "sae_visual_chart": "SAE 公开的 J3016 等级可视化摘要——官方域名取回 403；流传的副本挂在新闻机构 CDN 上，不收",
    "iso_defs_vs_2026": "ISO/SAE 22736:2021 那四条定义在 J3016_202609 里是否改动——未核到",
    "disengagement_rates": ("任何一家公司的脱离率 / MPD 与基于它的排行——只覆盖测试许可、"
                            "周期非自然年、判定权在厂家、分母不分 ODD 难度，四处不可比"),
    "ca_official_totals": "加州 DMV 官方汇总页给出的年度脱离数值——未核到",
    "sgo_counts": ("SGO 的事故计数、厂家间事故数对比与任何由它算出的事故率——"
                   "监管方自己写了 “Use caution when attempting to compare crash data between entities.”"),
    "sgo_third_amendment": "第三修订令（2025-06-16 起施行）的触发条件与完整字段——未核到，只核到 2023 年第二次修订令",
    "sgo_appendix_c": "SGO Appendix C 的完整字段清单——PDF 里是静态图，取不到文字",
    "safety_vs_human": ("“自动驾驶比人类司机安全多少倍 / 事故率低百分之多少”一类跨厂家、跨研究比较——"
                        "基线、规模口径、统计期、测量方四样本次没有一条齐全；"
                        "NHTSA 明说数据 “not … normalized or adjusted by any measure of exposure”"),
    "dataset_ranking": ("数据集之间“谁更大 / 更好”的排序，含 nuScenes 的 “7x as many annotations / "
                        "100x as many images as … KITTI”、Waymo 的 “15x more diverse”，"
                        "以及 1.4M 对 12M 的框数差——框数差主要是标注频率口径差"),
    "dataset_current_scale": "两个数据集**现行版本**的场景数与标注帧数——官网取不到，本卡只有论文发表时的初版规模",
    "jetson_tops": "Jetson 系列的 275 / 157 / 100 / 67 / 40 TOPS——精度与稀疏化都没标，且官网两页自相矛盾",
    "sparse_tops": "任何平台“稀疏化后”的算力数值，以及由标称 TOPS 推出的帧率、模型规模或“够不够跑 L4”的结论",
    "vendor_compute_comparison": "厂家之间的算力比较——除 NVIDIA 外的官方规格页本次未取到",
    "latency_budget": "“感知到执行的端到端时延预算”（如“必须小于 100 ms”）——核不到原始出处",
    "braking_distance": ("由时延折算出的制动距离、反应距离等安全结论（含 arXiv:2510.11448 摘要里的 "
                         "13.6 ft / 4.14 m at 40 mph）——那是作者折算，且建立在排除了两端的时延上"),
    "waymo_sync_upper": "Waymo 同步误差区间的上界——抓取被截断，付印前须回正文补",
}


def check() -> None:
    """最容易被引错的几条，用断言钉住。核不到的必须 is None；口径不全的，其口径字段必须 is None。"""
    # ---- 一、J3016：版本与"简称不是定义"
    assert J3016["current_revision"] == "J3016_202609", \
        "现行版是 2026-09-20 那一版；2021 版在 SAE 官网上已标 Historical"
    assert J3016["level_definitions"] is None and J3016["odd_definition"] is None, \
        "等级定义与 ODD 定义的原文都没核到（付费正文），不许补"
    assert J3016["descriptors_are_not_definitions"], \
        "SAE 自己写的 “these are NOT the definitions”——不许拿简称当定义印"
    assert LEVEL_DESCRIPTORS_202104[2] != LEVEL_DESCRIPTORS_202609[2], \
        "两版简称不同：流传的“L2 部分驾驶自动化”是 2021 版的叫法"
    assert set(LEVEL_DESCRIPTORS_202104) == set(LEVEL_DESCRIPTORS_202609) == set(range(6))
    assert ISO_SAE_22736_DEFS["source_is_public_preview"] and \
        ISO_SAE_22736_DEFS["iso_version_checked_against_2026"] is None, \
        "那四条定义来自 2021 年版的公开预览件；是否被 2026 版改过未核到"
    assert ISO_SAE_22736_DEFS["ads_levels"] == (3, 4, 5), \
        "ADS 专指 L3—L5；泛称 driving automation system 才是 L1—L5"

    # ---- 二、加州脱离报告：周期不是自然年，不覆盖部署许可，判定权在厂家
    assert not CA_DISENGAGEMENT["is_calendar_year"], \
        "报告周期是 12 月 1 日—次年 11 月 30 日，不是自然年——最常被引错的一条"
    assert CA_DISENGAGEMENT["period_start"] == "12-01" and CA_DISENGAGEMENT["period_end"] == "11-30"
    assert not CA_DISENGAGEMENT["applies_to_deployment_permits"], \
        "§ 227.50 在 Article 3.7「测试」之下，部署（商业运营）里程不在这份报告里"
    assert not CA_DISENGAGEMENT["threshold_defined_by_regulator"] and \
        CA_DISENGAGEMENT["third_party_verification"] is None, \
        "“脱离”的判定权在厂家，法规没给阈值也没设第三方复核"
    assert CA_DISENGAGEMENT["official_annual_totals"] is None, \
        "DMV 官方汇总页未核到——本章不印任何脱离数值"
    assert not CA_DISENGAGEMENT["text_source_is_official_publication"], \
        "条文经 LII 转录，付印前须回加州官方 CCR 逐字核"
    assert CA_DISENGAGEMENT["n_triggering_situations"] == 3
    assert len(CA_DISENGAGEMENT["fields"]) == 5

    # ---- 三、NHTSA SGO：30 秒窗口、现行版未核到、官方自陈"不要横向比较"
    assert NHTSA_SGO["engagement_window_s"] == 30, \
        "触发口径是“事发前 30 秒内系统激活过”——一次上报不等于一次“自动驾驶肇事”"
    assert NHTSA_SGO["third_amendment_triggers"] is None, \
        "现行（第三修订令）的触发条件与字段未核到；引用触发条件必须写明是 2023 年第二次修订令的口径"
    assert NHTSA_SGO["triggers_from_revision"].startswith("second amended")
    assert NHTSA_SGO["field_list"] is None, \
        "Appendix C 的完整字段表取不到文字，不许补"
    assert NHTSA_SGO["notice_regardless_of_verification"], \
        "知悉即报，不要求厂家先核实——这是“数据可能未经核实”那条口径的来源"
    assert "Use caution" in SGO_CAVEATS["do_not_compare"], \
        "监管方自己说的“不要横向比较”——本章压轴材料，不许漏印"
    assert "not be assumed to be statistically representative" in SGO_CAVEATS["not_representative"]
    assert "not been normalized" in SGO_CAVEATS["not_normalized"] or \
        "normalized or adjusted by any measure of exposure" in SGO_CAVEATS["not_normalized"]
    assert len(SGO_CAVEATS["six_bullets"]) == 6

    # ---- 四、数据集：标注频率是口径，不可互比
    assert NUSCENES["keyframe_hz"] == 2 and NUSCENES["cam_hz"] == 12, \
        "nuScenes 采 12 Hz 只标 2 Hz：标注帧 ≠ 采集帧"
    assert NUSCENES["keyframes"] == 40_000 and NUSCENES["boxes_3d"] == 1_400_000
    assert NUSCENES["scenes_manually_selected"], \
        "场景是人工挑的“有意思”场景，不是道路上的真实分布"
    assert NUSCENES["cities"] == 2 and WAYMO_OPEN["cities"] == 3, \
        "城市数少得惊人——这就是域间泛化为什么是课题"
    assert NUSCENES["full_360"] and not WAYMO_OPEN["full_360"], \
        "nuScenes 全 360°；Waymo 的五个针孔相机合起来不是 360°"
    assert WAYMO_OPEN["radars"] == 0 and NUSCENES["radars"] == 5, \
        "传感器配置根本不同，这是两个数据集不可比的第一条"
    assert WAYMO_OPEN["lidar_range_restricted"], \
        "Waymo 官方自陈对激光雷达作了距离截断"
    assert WAYMO_OPEN["sync_error_ms_bound"] is None, \
        "同步误差上界抓取被截断，付印前须回正文补"
    assert not DATASET_NOT_COMPARABLE["four_conditions_complete"], \
        "四样口径不齐（规模口径就对不上），所以不作任何排序与比较"
    assert NUSCENES["describes_initial_release"] and WAYMO_OPEN["describes_initial_release"]
    assert NUSCENES["official_site_version_numbers"] is None and \
        WAYMO_OPEN["official_site_scale_numbers"] is None, \
        "两家官网都给不到现行版本的规模数字"

    # ---- 五、算力：精度给了可以印，稀疏化没给就必须标 None；Jetson 那几个数不印
    assert DRIVE_ORIN["precision_stated"] is not None and DRIVE_ORIN["sparsity_stated"] is None, \
        "DRIVE Orin：精度口径有、稀疏化口径没有——必须连缺口一起印"
    assert DRIVE_THOR["precision_stated"] is not None and DRIVE_THOR["sparsity_stated"] is None, \
        "DRIVE Thor 同理"
    assert DRIVE_ORIN["is_peak_up_to"] and DRIVE_THOR["is_peak_up_to"], \
        "“up to”是峰值不是持续，不许当持续算力用"
    assert DRIVE_ORIN["dla_included_in_total"], \
        "官方把 254 写成**包含** DLA 的 87，不许把它们相加"
    assert DRIVE_THOR["fp4_flops"] == 2 * DRIVE_THOR["int8_tops"], \
        "同一块 Thor，精度一换数值就是 2 倍——这正是 TOPS 不能当算力用的理由"
    assert JETSON_CONFLICT["precision_stated"] is None and \
        JETSON_CONFLICT["sparsity_stated"] is None and not JETSON_CONFLICT["printable"], \
        "Jetson 那几个 TOPS 口径全缺，本章不印"
    assert JETSON_CONFLICT["same_vendor_official_pages_conflict"] and \
        JETSON_CONFLICT["orin_nx_tops_page_a"] != JETSON_CONFLICT["orin_nx_tops_page_b"], \
        "同一家官网两页给同一款模块两个数——这是本章的口径冲突实例"
    assert all(v is None for k, v in OTHER_VENDORS.items() if k != "ref"), \
        "其余厂家的官方规格页未取到，不许用记忆里的数填空"

    # ---- 六、时延：预算未核到；能核到的那组不是端到端
    assert LATENCY["sensor_to_actuation_budget_ms"] is None, \
        "“感知到执行的端到端时延预算”核不到原始出处，不许印"
    assert not LATENCY["is_sensor_to_actuation"] and "excluded" in LATENCY["excludes"], \
        "521.91 → 290.26 ms 明确排除了采集与执行两端，不能当端到端时延引"
    assert LATENCY["autoware_perception_to_decision_after_ms"] < \
        LATENCY["autoware_perception_to_decision_before_ms"]

    # ---- 七、不印清单本身
    for key in ("sae_level_definitions", "odd_definition", "latency_budget",
                "disengagement_rates", "sgo_counts", "jetson_tops", "safety_vs_human"):
        assert key in NOT_PRINTED, f"{key} 必须留在 NOT_PRINTED 里"


check()
