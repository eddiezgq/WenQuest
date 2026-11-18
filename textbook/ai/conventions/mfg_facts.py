"""第 21 章（智能制造与质量检测）要印的公开数字，一处定义、处处引用。

出处逐条记在
`docs/教材/人工智能/参考/第21章_智能制造与质量检测原始数字资料_2026-11.md`。

纪律与第 17—20 章同：只收论文正文、官方标准文本、官方指南或官方数据集说明给出的原始值；
查不到完整口径的进 `NOT_PRINTED`；凡"本资料卡自己折算"的，逐条标明。
"""
from __future__ import annotations

# ================================================================ 一、公开振动数据（21.3 节）

CWRU = {
    "motor_hp": 2,                      # 原话 "a 2 hp motor"
    "fault_method": "电火花加工（electro-discharge machining）",
    "fault_diameters_mil": (7, 14, 21, 28, 40),
    "fs_all_hz": 12000,                 # 全部数据
    "fs_drive_end_hz": 48000,           # 仅驱动端故障另有一套
    "loads_hp": (0, 1, 2, 3),
    "rpms": (1797, 1772, 1750, 1730),
    "accel_position": "12 点钟方向，驱动端与风扇端各一个",
    "single_point_only": True,          # **单点人工缺陷**，不是现场的分布式剥落
    "fault_depth": None,                # 这两页没写
    "record_length": None,              # 这两页没写
    "ref": "engineering.case.edu/bearingdatacenter（装置与流程页、12k 风扇端数据表）",
}

# 本章算例用的轴承几何（与上面那套公开数据常用的型号一致）
BEARING = {"n_balls": 9, "d_ball_mm": 7.94, "d_pitch_mm": 39.04}

# ================================================================ 二、剩余寿命数据（21.3、21.8 节）

CMAPSS = {
    "subsets": {
        "FD001": {"train": 100, "test": 100, "conditions": 1, "modes": 1},
        "FD002": {"train": 260, "test": 259, "conditions": 6, "modes": 1},
        "FD003": {"train": 100, "test": 100, "conditions": 1, "modes": 2},
        "FD004": {"train": 248, "test": 249, "conditions": 6, "modes": 2},
    },
    "unit": "循环（cycle），不是小时",
    "simulated": True,                  # C-MAPSS 本身是仿真软件
    "sensor_channels": None,            # 本轮未逐条抄录
    "ref": "NASA C-MAPSS 原始 readme.txt",
}

# ================================================================ 三、视觉缺陷数据（21.2 节）

MVTEC = {
    "n_images": 5354,
    "n_categories": 15,                 # 5 种纹理 + 10 种物体
    "n_textures": 5,
    "n_objects": 10,
    "n_defect_types": 73,
    "n_train": 3629,                    # 训练+验证
    "n_test": 1725,
    "train_defect_free_only": True,     # 原话 "contains only images without defects"
    "res_min": 700,
    "res_max": 1024,
    "defects_manual": True,             # 原话 "The defects were manually generated"
    "ref": "Bergmann et al., CVPR 2019（openaccess 版正文）",
}

# ================================================================ 四、受监管行业（21.7 节）

CFR_820_30 = {
    "subsections": ("General", "Design and development planning", "Design input",
                    "Design output", "Design review", "Design verification",
                    "Design validation", "Design transfer", "Design changes",
                    "Design history file"),
    "validation_on_initial_production_units": True,
    "validation_includes_software": True,
    "review_needs_independent_person": True,
    "ref": "21 CFR 820.30（联邦法规原文）",
}

QMSR = {
    "published": "2024-02-02",
    "effective": "2026-02-02",
    "incorporates": "ISO 13485:2016",
    "part_renamed": "Quality Management System Regulation (QMSR)",
    "ref": "FDA 官方问答页",
}

PCCP = {
    "fr_volume": 89, "fr_number": 233,
    "fr_pages": "96259–96261",
    "date": "2024-12-04",
    "docket": "FDA-2022-D-2628",
    "final": True,
    "three_parts": ("要改什么", "用什么方法开发、验证并实施这些改动", "这些改动的影响有多大"),
    "ref": "Federal Register 89 FR 96259（2024-12-04）",
}

# ================================================================ 五、统计过程控制（21.5 节）
#
# 这些是标准系数与定义，不是某一次测量；本书要印的值由程序自己模拟核对一遍。

SPC = {
    "a2": {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483},
    "d2": {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534},
    "d4": {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004},
    "three_sigma_false_alarm": 0.0027,      # 过程不变时每个子组报警的概率
    "arl0_theory": 370,                     # 1 / 0.0027，教科书值
    "cp": "(USL − LSL) / (6σ)",
    "cpk": "min{(USL − μ)/(3σ), (μ − LSL)/(3σ)}",
}

# ================================================================ 六、本章不印的数

NOT_PRINTED = {
    "company_yield": "任何具体企业的良品率、停机时间与维护成本（没有可核的公开原始值）",
    "vendor_claims": "“人工智能把缺陷检出率提高了百分之多少”这类厂商宣传数字",
    "certification": "任何“通过了某某认证”的成品话术",
    "oee_benchmark": "设备综合效率（OEE）的行业标杆值——未核到标准或官方口径，只写定义",
    "six_sigma_dpmo": "“六西格玛 = 3.4 DPMO”的原始出处与 1.5σ 漂移假设的权威表述（未核到）",
    "cwru_depth": "公开轴承数据的故障深度与每条记录的时长（那两页没写）",
    "cmapss_channels": "剩余寿命数据各通道的具体含义（本轮未逐条抄录）",
    "xjtu_femto": "XJTU-SY 与 FEMTO-ST 数据集的工况与失效判据（本轮未核）",
    "iso_clauses": "ISO 13485、ISO 14971、IEC 62304 的条款正文（版权所限，只引标准名与版本号）",
}


def check() -> None:
    """几条最容易被引错的，用断言钉住。"""
    assert CWRU["single_point_only"], "公开轴承数据的故障是人为加工的单点缺陷"
    assert CWRU["fs_all_hz"] == 12000 and CWRU["fs_drive_end_hz"] == 48000, \
        "两套采样率的适用范围不同，不能混着说"
    assert CMAPSS["simulated"] and "循环" in CMAPSS["unit"], \
        "剩余寿命数据是仿真的，单位是循环不是小时"
    assert MVTEC["train_defect_free_only"], "该数据集的训练集只有好件，是无监督设定"
    assert CFR_820_30["validation_on_initial_production_units"], \
        "设计确认要在实际使用条件下、用初始生产件做"
    assert QMSR["effective"] == "2026-02-02", "QMSR 的生效日期"
    assert len(PCCP["three_parts"]) == 3, "预定变更控制计划要写三件事"
    assert abs(1 / SPC["three_sigma_false_alarm"] - SPC["arl0_theory"]) < 2, \
        "教科书值就是 1 / 0.0027"
