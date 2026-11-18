"""第 20 章（材料与化学发现）要印的公开数字，一处定义、处处引用。

每一条都带口径，出处逐条记在
`docs/教材/人工智能/参考/第20章_材料与化学发现原始数字资料_2026-11.md`（条号与下面的 `ref` 对应）。

**三条铁律**（与第 17—19 章同）：
1. 只收能核到论文正文、官方文档、官方公告或官方模型卡的值；只在图里的、口径不全的，
   一律进 `NOT_PRINTED`；
2. **论文自己说的**与**独立复核说的**分开存，正文必须并列印（见 `GNOME` 与 `GNOME_REVIEW`、
   `ALAB` 与 `ALAB_REVIEW`）；
3. 凡“稳定”“新”这类词，**定义跟着数一起存**——这一章的全部争议都在定义上。
"""
from __future__ import annotations

# ================================================================ 一、大规模发现：论文自己怎么说

GNOME = {
    "n_structures_m": 2.2,            # 百万；原话 “stable with respect to the Materials Project”
    "stable_ref_set": "Materials Project",   # **参考集**，换一个数就变（ref 101）
    "n_new_hull_k": 381,              # 千；落在更新后凸包上的新条目（ref 102）
    "n_total_stable_k": 421,          # 千；更新后凸包上的总数（ref 102）
    "single_mev_cutoff": None,        # **论文不给单一 meV/atom 截断**（ref 103）
    "active_learning_mev": 50,        # 正文里唯一出现的 meV/atom，是**主动学习**用的（ref 103）
    "defines_metastable": False,      # 论文正文不定义“亚稳”（ref 104）
    "r2scan_binary_ternary_pct": 84.0,   # 换 r²SCAN 泛函后仍为负相分离能的比例（ref 105）
    "r2scan_quaternary_pct": 86.8,       # 同上，四元（ref 105）
    "n_already_realized": 736,        # 此前已被独立实验实现（ref 106）
    "n_new_since_project": 184,       # 其中项目开始后才有的新发现（ref 106）
    "hit_rate_pct": 80,               # “above 80%”，带结构输入时的命中率（ref 107）
    "announced_contribution_k": 380,  # 官方公告说要向 MP 贡献的个数（千）（ref 108）
    "ref": "Merchant et al., Nature 624, 80–85 (2023); DeepMind 官方博客 2023-11-29",
}

# Materials Project 官方版本说明实际记录的收录情况（ref 110）。
# **这组数与上面 announced_contribution_k 并列印，是本章最有力的一条对照。**
MP_INTAKE = {
    "v2024_12_18_added": 15483,
    "v2026_04_13_added_r2scan": 74052,
    "v2024_11_14_deprecated": 2047,
    "ref": "docs.materialsproject.org/changes/database-versions",
}

GNOME_REVIEW = {
    "n_sampled_stable": 10,           # 随机抽查的稳定结构个数（ref 112）
    "n_found_in_icsd": 10,            # **全部 10 个的结构都能在 ICSD 里找到**（ref 113）
    "n_same_space_group": 1,          # 其中只有 1 个空间群相同（ref 113）
    "n_first_entries_examined": 250,  # 另外按顺序查了前 250 条（ref 112）
    "n_gnome_explorer": 2047,         # GNoME Explorer 的条目总数（ref 112）
    "n_stable_db": 384870,            # 稳定结构库条目数（ref 112）
    "no_functionality_shown": True,   # “没有演示任何功能 → 还不能算材料”（ref 116）
    "n_radioactive": 18138,           # 含放射性元素的化合物（ref 117）
    "top4_space_group_pct": 34,       # 前四个空间群占比；ICSD 前两个约 16%（ref 117）
    "gives_novel_pct": False,         # 该文**不给**“判为新颖的百分比”（ref 118）
    "ref": "Cheetham & Seshadri, Chem. Mater. 36(8), 3490–3495 (2024)",
}

ALAB = {
    "days": 17,
    "n_realized_body": 36,            # **正文**：36 个（ref 119）
    "n_targets_body": 57,             # **正文**：57 个靶（ref 119）
    "n_realized_editorial": 41,       # 同一篇文章的**编辑摘要**写 41/58——与正文不一致（ref 120）
    "n_targets_editorial": 58,
    "n_experiments": 353,
    "recipe_success_pct": 30,         # 353 个配方里只有 30% 做出了目标（ref 119）
    "target_hull_mev": 10,            # 选靶判据：在凸包上或 <10 meV/atom（ref 122）
    "target_db_version": "2022.10.28",
    "n_failed": 17,                   # 57 个里 17 个没做出来（ref 123）
    "n_failed_kinetics": 11,          # 其中 11 个是反应动力学太慢（ref 123）
    "purity_threshold": None,         # **正文不给纯度门槛**；唯一数值门槛是主动学习的 >50% 产率（ref 121）
    "ref": "Szymanski et al., Nature 624, 86–91 (2023)",
}

ALAB_REVIEW = {
    "n_examined": 43,                 # 复核的总数（含 7 个部分成功）（ref 128）
    "n_with_issues": 42,              # **其中 42 个有实质问题**（ref 128）
    "n_opposite_conclusion": 40,      # 至少 40/43 可以得出相反结论（ref 128）
    "revised_success": 3,             # 改判后的成功数（ref 129）
    "revised_total": 58,
    "revised_pct": 5,                 # 3/58 ≈ 5%（ref 129）
    "n_revised_already_known": 2,     # 这 3 个里有 2 个是已知化合物（ref 129）
    "n_no_cation_order": 24,          # 36 个里 24 个**没有阳离子有序的证据**（ref 127）
    "n_poor_fit": 18,                 # 拟合不好（ref 127）
    "n_structure_altered": 8,         # 细化过程中结构被改掉（ref 127）
    "n_already_reported": 3,          # 已被报道过（ref 127）
    "auto_rietveld_reliable": False,  # “自动 Rietveld 分析还不可靠”（ref 130）
    "ref": "Leeman et al., PRX Energy 3, 011002 (2024)",
}

# ================================================================ 二、稳定 / 亚稳 / 可合成（全章地基）

METASTABLE = {
    "median_mev": 15.0,               # 已知无机晶体的 DFT 亚稳程度中位数 ± 0.5（ref 134）
    "median_err": 0.5,
    "p90_mev": 67.0,                  # 90 分位 ± 2（ref 134）
    "p90_err": 2.0,
    "nitride_median_mev": 63.0,       # 氮化物中位（ref 136）
    "nitride_p90_mev": 195.0,         # 氮化物 90 分位（ref 136）
    "binary_oxide_p90_mev": 94.0,     # 二元氧化物 90 分位（ref 136）
    "n_entries": 29902,               # 样本口径（ref 135）
    "metastable_pct": 50.5,           # 其中亚稳的比例 ± 4%（ref 135）
    "metastable_pct_err": 4.0,
    "observed_range_mev": 70,         # 原文只给观测范围 <~70 meV/atom（ref 137）
    "hard_threshold": None,           # **原文不给硬阈值**（ref 137）
    "low_energy_sufficient": False,   # 原话：低亚稳能**不是**合成的充分条件（ref 137）
    "ref": "Sun et al., Science Advances 2, e1600225 (2016)",
}

# 工程上实际用过的三个阈值，**口径互不相同、不能混用**（ref 138）
THRESHOLDS = {
    "alab_target_mev": 10,            # A-Lab 选靶
    "gnome_active_learning_mev": 50,  # GNoME 主动学习
    "matbench_classify_mev": 0,       # Matbench Discovery 的分类阈值
}

# 可与 GNoME 并列的另一次大规模筛选（ref 139）
M3GNET_SCREEN = {
    "n_generated": 31664858,
    "n_below_1mev": 1849096,          # E_hull 预测 < 0.001 eV/atom
    "n_dft_checked": 2000,            # 取能量最低的 2000 个做 DFT 复核
    "n_dft_confirmed": 1578,
    "ref": "Chen & Ong, arXiv:2202.02450",
}

# ================================================================ 三、机器学习势：官方自己承认的局限

MLIP_LIMITS = {
    "mace_no_spin": True,             # MACE-MP-0 明写不含磁性或自旋自由度（ref 184）
    "chgnet_moment_mae_ub": 0.032,    # CHGNet 的磁矩 MAE（µB）（ref 185）
    "chgnet_nonmagnetic_fails": True, # 对无磁矩离子推断电荷不准（ref 185）
    "mptrj_mixes_functionals": True,  # 训练数据混用 GGA 与 GGA+U（ref 186）
    "strong_correlation_quote": None, # **没核到**“强关联体系不准”的明确表述（ref 187）
    "ref": "Batatia et al., arXiv:2401.00096; Deng et al., arXiv:2302.14231",
}

# ================================================================ 四、重稀土与永磁（本章的实际问题）

NDFEB = {
    "anisotropy_field_t": 7.5,        # Nd₂Fe₁₄B 各向异性场 µ₀H_A（T）（ref 151）
    "saturation_t": 1.6,              # 饱和磁化 µ₀M_s（T）（ref 151）
    "curie_c": 320,                   # 居里温度（°C）（ref 151）
    "n50_bhmax_kj_m3": 400,           # N50 牌号的最大磁能积（kJ/m³）（ref 152）
    "bhmax_theoretical_limit": None,  # 综述只说“接近理论极限”，**不给数值**（ref 153）
    "hc_at_160c_t": 0.2,              # 160 °C 时矫顽力掉到约 0.2 T（ref 156）
    "motor_op_temp_c": 160,           # 牵引电机的工作温度（ref 156）
    "beta_hc_dy_free": -0.6,          # 无 Dy 烧结磁体的矫顽力温度系数（%/K，160 °C）（ref 154）
    "beta_hc_ndcu": -0.40,            # Nd-Cu 共晶扩散（%/K，500 K）（ref 155）
    "beta_hc_tb": -0.3,               # 含 Tb 共晶扩散（%/K，500 K）（ref 155）
    "beta_hc_ce": -0.59,              # Ce 替代的热变形磁体（%/°C）（ref 155）
    "gbd_dy_free_max_t": 2.1,         # 晶界扩散用在无 Dy 样品上，矫顽力上不过 2.1 T（ref 157）
    "gbd_dy_wt_pct": 0.1,             # 0.1 wt.% Dy 扩散进含 Dy 样品（ref 157）
    "gbd_from_t": 2.3,                # 初始矫顽力（ref 157）
    "gbd_to_t": 3.0,                  # 扩散后达到（ref 157）
    "dy_gain_per_wt_pct": None,       # **综述不量化**单位 Dy 的矫顽力增益（ref 159）
    "remanence_temp_coeff": None,     # **综述不给**剩磁温度系数（ref 160）
    "ref": "Li, Sepehri-Amin, Ohkubo, Hono et al., STAM 22, 386 (2021)",
}

HEAVY_RE = {
    "us_import_reliance_pct": 100,    # 美国重稀土净进口依赖度，2021—2025e 每年 100%（ref 162）
    "from_china_pct": {"terbium": 100, "holmium": 100, "lutetium": 100,
                       "ytterbium": 86, "erbium": 40},   # 2021—2024 合计（ref 163）
    "dy_oxide_usd_kg_2025e": 239,     # 镝氧化物 99.5% min，离岸价（ref 164）
    "dy_oxide_usd_kg_2024": 257,
    "tb_oxide_usd_kg_2025e": 1010,    # 铽氧化物 99.99% min，离岸价（ref 164）
    "tb_oxide_usd_kg_2024": 812,
    "nd_oxide_usd_kg_2025e": 73,      # 钕氧化物 99.5% min（ref 170）
    "china_separation_share": None,   # **USGS 没有这句话**（ref 165）
    "world_mine_production_t_2025e": 390000,   # 全部稀土，REO 公吨（ref 166）
    "china_mine_production_t_2025e": 270000,   # （ref 166）
    "china_mine_share_pct_derived": 69,        # **资料卡按表推算，不是 USGS 的表述**（ref 168）
    "ref": "USGS, Mineral Commodity Summaries 2026, Rare Earths (Heavy) 与 Rare Earths 两章",
}

# 无稀土路线：只收综述自己写出条件的实验值（ref 174、175）
RE_FREE = {
    "fe16n2_ms_emu_cm3": 2000,        # 饱和磁化（emu/cm³），Kim & Takahashi 1972，综述转引
    "fe16n2_hc_oe_ballmill": 854,     # 球磨 + 冲击压实的矫顽力（Oe）
    "fe16n2_hc_oe_foil": 1910,        # 自支撑箔的矫顽力（Oe）
    "fe16n2_bhmax_mgoe_calculated": 20,   # **计算值，不是实测**——引用必须标明（ref 175）
    "mnbi_mnal_curves": None,         # **综述不给** MnBi、MnAl 的矫顽力-温度与磁能积（ref 176）
    "has_ndfeb_baseline": False,      # 该综述没有 NdFeB 对照数据，不能用它做对照表（ref 177）
    "ref": "Shao & Ren, Nanoscale Advances 2, 4341–4349 (2020)",
}

# 用机器学习筛永磁：有，但**不是势、也不是图网络**（ref 178—183）
MAGNET_ML = {
    "is_potential_or_gnn": False,     # 是特征工程 + XGBoost / 神经网络的表格回归
    "n_experimental": 300,            # 实验已知材料
    "n_micromagnetic": 8770,          # 另有微磁学模拟数据
    "split": "70:30",
    "xgb_r2": 0.89,                   # 调参后 XGBoost，在 log H_c 上
    "xgb_mse": 0.18,
    "ann_r2": 0.64,
    "target": "矫顽力 H_c（单位 T），误差在 log H_c 上算",
    "table4_units_missing": True,     # **原文 Table IV 的 RMSE/MAE 没标单位**（ref 182）
    "potential_or_gnn_paper_exists": False,   # 这一类公开工作没核到（ref 183）
    "ref": "Bhandari et al., arXiv:2312.02475",
}

# ================================================================ 五、本章不印的数（查不到完整口径，或只在图里）

NOT_PRINTED = {
    "dft_absolute_core_hours": "一次中等体系 DFT 松弛的绝对核时/墙钟——**全章一条都没核到**；"
                               "算例 20.1 里的“每次多少小时”一律是显式假设",
    "oqmd_entry_count": "OQMD 官方条目数（官网拒绝访问）",
    "nomad_total": "NOMAD 当前总条目数（只有日期不明的公告）",
    "mp_total_per_version": "Materials Project 每版总数（官方只给增量）",
    "gnome_potential_mae": "GNoME 自带势的能量/力 MAE——正文不给，力误差只在图注里",
    "matbench_table1": "Matbench Discovery 逐模型的 Table 1 数值（本次没读到）",
    "human_synthesis_baseline": "人工合成 + 表征的对照基线（A-Lab 与 Ada 都没给）",
    "magnet_gnn_screening": "用机器学习势或图神经网络直接筛永磁的论文（这一类没核到）",
    "ndfeb_bhmax_limit": "(BH)max 的理论极限数值（综述只说“接近”）",
    "dy_coercivity_gain": "单位 wt% Dy 的矫顽力增益（综述不量化）",
    "mnbi_mnal_performance": "MnBi、MnAl 的矫顽力-温度曲线与磁能积",
    "china_separation_share": "中国占重稀土分离/磁体制造的比例——USGS 两章都没有这句话；"
                              "69% 的矿山产量占比是资料卡按表推算的，引用要标明",
    "strong_correlation_mlip": "“机器学习势对强关联体系不准”的明确表述（没核到原话）",
}


def check() -> None:
    """自检：几条最容易被引错的，用断言钉住。导入时不跑，正文程序里显式调用。"""
    assert GNOME["single_mev_cutoff"] is None, "GNoME 论文不给单一 meV/atom 截断"
    assert GNOME["stable_ref_set"] == "Materials Project", "“稳定”是相对 MP 说的"
    assert GNOME["n_new_since_project"] < GNOME["n_already_realized"], \
        "736 个已被独立实现，其中只有 184 个是项目开始后的新发现"
    assert MP_INTAKE["v2024_12_18_added"] + MP_INTAKE["v2026_04_13_added_r2scan"] \
        < GNOME["announced_contribution_k"] * 1000, \
        "MP 实际收录远少于公告说的 380,000"
    assert ALAB["n_realized_body"] != ALAB["n_realized_editorial"], \
        "同一篇文章正文与编辑摘要不一致，只引正文"
    assert ALAB_REVIEW["revised_pct"] < ALAB["recipe_success_pct"], \
        "独立复核把成功率改判得低得多"
    assert METASTABLE["hard_threshold"] is None and not METASTABLE["low_energy_sufficient"], \
        "没有硬阈值，而且低亚稳能不是合成的充分条件"
    assert len(set(THRESHOLDS.values())) == 3, "三个工程阈值口径不同，不能混用"
    assert not MAGNET_ML["potential_or_gnn_paper_exists"], \
        "用机器学习势或图网络直接筛永磁的公开工作没核到"
    assert MLIP_LIMITS["strong_correlation_quote"] is None, \
        "“对强关联体系不准”这句话没核到原话，不印"
