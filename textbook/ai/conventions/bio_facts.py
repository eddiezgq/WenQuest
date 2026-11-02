"""蛋白质结构预测与药物发现的公开发表数字（第 18 章用）。

规矩与 `agent_facts.py`、`gen_facts.py` 相同：**只收论文正文、官方技术报告、官方公告或官方
文档给出的原始数字**；综述转述、媒体估算、排行榜一律不收；未公布的项用 `UNPUBLISHED` 标出，
正文写"未公布"；由原始值算出来的倍数与换算，注释里标"折算"。每条的出处、位置、口径与
"为什么不能横向比较"见
`docs/教材/人工智能/参考/第18章_蛋白质结构与药物发现原始数字资料_2026-11.md`。
核对日期：2026 年 11 月 2 日。

**本章特别要当心的五条**（资料卡第 14 节）：
1. 92.4 是"**中位 domain GDT_TS**"，分母是 CASP14 评估的 92 个 domain，出自 DeepMind 自己的
   CASP14 论文，**不是 CASP 官方公布的数**。要引官方可核的差距，就引 z-score 之和
   244.0217 对 90.8241。
2. "AlphaFold 官方说 pLDDT 不是实验置信度"——**没有这句原话**。能引的是 AFDB 论文的
   "it is incumbent upon the user to interpret the model prudently"，以及"低置信区不应当作
   结构、而应当作无序的预测"。**不要给官方 FAQ 编引文。**
3. **lDDT 与 GDT_TS 之间不存在换算。** pLDDT 与真实 lDDT 之间只有一条
   lDDT-Cα = 0.997·pLDDT − 1.17（r = 0.76）的拟合，r 只有 0.76 意味着单个残基上偏差可以很大，
   **不能当等式用**。
4. ESMFold"快 60 倍"是**上界且只在短序列上**，典型值是 384 残基 / V100 / 14.2 秒、比**单个**
   AF2 模型快 6 倍；省掉的主要是 MSA 检索那 10 分钟，不是网络前向本身。成绩代价要一起写。
5. "换成骨架划分分数掉 X 个点"——**没有成对的原始数字**。只能印两种划分的定义、MoleculeNet
   的训练/验证/测试三档落差，以及 Chemprop"更难但四个数据集上不显著"的定性结论。
"""

UNPUBLISHED = None                      # 未公布：正文写"未公布"

# ---------------------------------------------------------------- 问题的规模
SCALE = {
    "pdb_entries": 250_000,             # "more than 250,000 entries"，截至 2026-02 底（RCSB 官方通讯）
    "pdb_as_of": "2026 年 2 月底",
    "pdb_200k_year": 2023,
    "uniprot_sprot": 575_748,           # 人工审校，Release 2026_03（2026-09-02）
    "uniprot_trembl": 149_430_635,      # 自动注释，同一版
    "uniprot_release": "2026_03",
    "afdb_sequences": 214_000_000,      # "为超过 2.14 亿条序列提供结构覆盖"，截至 2023-09
    "afdb_as_of": "2023 年 9 月",
    "afdb_unit": "序列",                 # 不是"结构文件"
    "afdb_license": "CC-BY-4.0",
    "afdb_bugfix_pct": 4,               # 2022-11 修了一个数值 bug，影响约 4% 的预测
    "human_residue_coverage_exp_pct": 17,   # 实验结构覆盖人类蛋白质组约 17% 的残基
}

# ---------------------------------------------------------------- CASP 的口径
CASP = {
    "what": "CASP provides an independent mechanism for the assessment of methods of "
            "protein structure modeling.",
    "cadence_years": 2,
    "blind": "靶标序列先公开、实验坐标后公开；评估由独立评估人做",
    "ranking": "GDT_TS 的 z-score 之和（不是原始分）",
    "z_tolerance": -2.0,
    "categories": ("TBM-Easy", "TBM-Hard", "FM/TBM", "FM"),
    "categories_note": "CASP14 评估论文自己说这套划分'已经不太有意义了'",
    "casp14_targets": 68, "casp14_units": 96,       # 靶标 → 评价单元
    "casp15_targets": 77, "casp15_units": 112,
}

# ---------------------------------------------------------------- CASP14 的成绩（口径见资料卡第 3 节）
CASP14 = {
    "af2_median_domain_gdt_ts": 92.4,   # 中位 **domain** GDT_TS，分母 92 个 domain；DeepMind 自己的论文
    "af2_median_n_domains": 92,
    "af2_source": "Jumper 等 2021, Proteins（DeepMind 自己的 CASP14 论文）",
    "official_z_af2": 244.0217,         # CASP 官方 z-score 之和（427 组）——**这才是官方数**
    "official_z_second": 90.8241,       # BAKER（473 组）
    "official_z_note": "官方排名用 z-score 之和；92.4 不是官方公布的数",
    "gdt90_rmsd_a": 1.5, "gdt80_rmsd_a": 2.5,       # CASP14 评估论文：GDT_TS 90 ≈ 1.5 Å，80 ≈ 2.5 Å
}

# ---------------------------------------------------------------- 评价指标
METRICS = {
    "gdt_ts": "GDT_TS = (GDT_P1 + GDT_P2 + GDT_P4 + GDT_P8) / 4，GDT_Pn 是距离截断 ≤ n Å "
              "之内的残基百分比；0—100；需要叠合（LGA）",
    "gdt_weak": "固定截断，所以偏离 4.1—8 Å 的残基对评分的贡献完全相同（TM-score 论文的批评）",
    "lddt": "四个容差（0.5/1/2/4 Å）下'参考结构里的局部距离被保持'的比例的平均；0—1；"
            "**无需叠合**",
    "lddt_radius_a": 15,                # 包含半径默认 15 Å
    "lddt_random": 0.20,                # 随机结构平均约 0.20
    "lddt_no_formula": True,            # 论文没给方程，只有文字描述
    "tm_formula": "TM-score = max[ (1/L_N) Σ 1 / (1 + (d_i/d_0)^2) ]，d_0 = 1.24·(L_N−15)^(1/3) − 1.8",
    "tm_random": 0.17,                  # 随机结构对约 0.17，且与蛋白大小无关
    "tm_d0_300": 6.4, "tm_d0_50": 2.3,  # L_N 从 300 降到 50，d_0 从 6.4 Å 降到 2.3 Å
    "tm_fold_threshold": UNPUBLISHED,   # "同折叠 0.5"这篇论文没给，见资料卡附录 B
    "corr_tm": 0.891, "corr_gdt": 0.751,    # 与最终模型质量的相关系数（TM-score 论文）
    "no_conversion": "lDDT 与 GDT_TS 之间不存在换算：一个无需叠合、测局部，一个需要叠合、测整体",
}

# ---------------------------------------------------------------- pLDDT 与 PAE
PLDDT = {
    "range": (0, 100),
    "trained_against": "训练时回归真实的 lDDT-Cα",
    "fit_slope": 0.997, "fit_intercept": -1.17, "fit_r": 0.76,   # lDDT-Cα = 0.997·pLDDT − 1.17
    "bands": (
        (90, 100, "generally modelled with high accuracy", "可用于依赖精度的工作，例如刻画结合位点"),
        (70, 90, "generally well-modelled, representing a reliable backbone prediction",
         "可靠的是'骨架'——注意这个限定词"),
        (50, 70, "have lower confidence and should be used cautiously", "谨慎使用"),
        (0, 50, "often exhibit a spaghetti-like appearance … indicating probable disordered regions",
         "常是无序区"),
    ),
    "chi1_correct_pct_above90": 80,     # pLDDT > 90 时侧链 χ1 旋转异构体约 80% 正确
    "confident_cut": 70,
    "human_frac_above90_all": 35.7,     # 占全部残基
    "human_frac_above90_predicted": 38.6,   # 占有预测的残基——两个分母不同，不能混引
    "human_frac_above70": 58.0,
    "disorder_auc": 0.897,              # pLDDT 当无序预测器，CAID DisProt-PDB 上 AUC
    "quotes": {
        "disorder": "低置信区 should not be interpreted as structures but rather as a "
                    "prediction of disorder",
        "not_always_disorder": "低置信区可能 structured only in complex——并不总是内在无序",
        "genuine_failure": "也有 genuine failures, in which a fixed structure exists",
        "user_judges": "it is incumbent upon the user to interpret the model prudently",
        "reliable_regions": "Structured domains with many inter-residue contacts are "
                            "generally more reliable",
        "discard": "在高置信区出现非物理键长或原子碰撞的结构应当弃用",
    },
    "no_official_quote": "'pLDDT 不是实验置信度'这句官方原话核不到——不要编",
}

PAE = {
    "what": "predicted error between relative positions of residue pairs",
    "scope": "反映更大单元（如域）之间相对位置的置信度",
    "unit": UNPUBLISHED,                # 查看器里以 Å 显示，但官方文字未核到
    "division_of_labour": "pLDDT 管'这一段本身准不准'，PAE 管'这两段之间的相对位置准不准'",
}

# ---------------------------------------------------------------- AlphaFold2 做不到什么
LIMITS = {
    "one_conformer": "训练目标是'最可能出现在 PDB 结构里'的那一个构象",
    "no_dynamics": "预测的是静态结构，不是动态行为（AF3 论文原话）",
    "msa_depth_cut": 30,                # 中位比对深度低于约 30 条时精度明显下降
    "bridging_domains": "大复合物里的桥连域明显更弱",
    "hetero_complex": "AF2 论文只说'readily applicable'——是期望，不是已做到",
    "ligand_implicit": "配体/离子不是显式输入，只可能被隐式地尊重",
    "length_cap": 2700,                 # 人类蛋白质组那次的长度上限，是为运行时间设的工程限制
    "needs_experiment": "案例研究得出的假说 would ultimately need to be confirmed by "
                        "experimental studies",
}

# 点突变效应：第三方实验（Pak 等 2023, PLoS ONE）
MUTATION = {
    "n_mutations": 1154, "n_proteins": 73,          # ThermoMutDB 单点突变
    "n_gfp": 796,
    "corr_dplddt_ddg": -0.17, "corr_dplddt_ddg_se": 0.03,
    "corr_mean_plddt_ddg": 0.02, "corr_mean_plddt_ddg_p": 0.44,   # 不显著
    "corr_dplddt_gfp": 0.17,
    "conclusion": "AlphaFold predictions cannot be used directly to reliably estimate the "
                  "impact of mutation on protein stability or function.",
}

# ---------------------------------------------------------------- ESMFold（本章云端实验用）
ESMFOLD = {
    "backbone": "ESM-2",
    "esm2_sizes": "8M—15B（ESMFold 用哪一档，论文与官方模型卡都没点明）",
    "params": UNPUBLISHED,              # 折叠头参数量未公布
    "weights": "facebook/esmfold_v1",
    "license": "MIT",
    "no_msa": "It does not require any lookup or MSA step",
    # 成绩：TM-score。注意 AF2 两列是"带 MSA 与模板"，与 ESMFold 的单序列不是同一个输入条件
    "cameo_n": 194, "cameo_esmfold": 0.83, "cameo_af2": 0.88, "cameo_rosettafold": 0.82,
    "casp14_n": 51, "casp14_esmfold": 0.68, "casp14_af2": 0.85,
    "same_input": False,
    # 消融（CAMEO，指标是 lDDT 不是 TM-score）
    "abl_base_lddt": 0.74, "abl_no_lm_lddt": 0.58, "abl_no_trunk_lddt": 0.66,
    # 只看它自己说有把握的那些
    "highconf_cut_plddt": 0.7, "highconf_esmfold_lddt": 0.83, "highconf_af2_lddt": 0.85,
    # 速度：本章实验照这一组估时
    "sec_384res_v100": 14.2, "ref_len": 384, "ref_gpu": "NVIDIA V100",
    "speedup_typical": 6,               # 比**单个** AF2 模型快 6 倍（同长度）
    "speedup_max": 60,                  # 上界，**只在更短的序列上**；"短"是多少残基论文没说
    "msa_search_min_high": 10,          # 高灵敏度 MSA 检索 > 10 分钟
    "msa_search_min_low": 1,            # 降低灵敏度可压到 1 分钟以内
    "speedup_source": "快 60 倍的主要来源是省掉 MSA 检索，不是网络前向本身",
}

ESM_ATLAS = {
    "sequences_folded": 617_000_000,    # MGnify90
    "gpus": 2000, "weeks": 2,           # GPU 型号论文此处未注明
    "good": 365_000_000,                # mean pLDDT > 0.5 且 pTM > 0.5
    "high": 225_000_000,                # > 0.7 且 > 0.7
    "very_high": 113_000_000,
    "nested": True,                     # 三档是嵌套的，不能相加
}

# ---------------------------------------------------------------- 复合物与对接
DOCKQ_BANDS = (                         # CAPRI 风格分档（AlphaFold-Multimer 论文 Table S1）
    (0.00, 0.23, "incorrect"),
    (0.23, 0.49, "acceptable"),
    (0.49, 0.80, "medium"),
    (0.80, 1.00, "high"),
)

# ---------------------------------------------------------------- 蛋白质设计（成功率一律写"多少个里成功多少个"）
DESIGN = {
    "note": "RFdiffusion 与 ProteinMPNN 的多数湿实验只给成功数、不给尝试数；"
            "资料卡里逐条标了'分母未给'。**不要替它们补一个分母。**",
}

# ---------------------------------------------------------------- 虚拟筛选
SCREEN = {
    # 三项同类研究的命中率：分母相差一个量级、判据各不相同，**不能并排比，更不能平均**
    "ampc_tested": 44, "ampc_hits": 5,
    "d4_tested": 549, "d4_hits": 122,
    "d4_selection": "589 个候选是'人工检视 + 按分自动挑选'混合选出、取自排序表各处，"
                    "**不是打分最高的前 589 名**",
    "mt1_tested": 38, "mt1_hits": 15,
    "criteria_differ": True,
    "ef_formula": "EF_x% =（前 x% 里的活性比例）/（全库的活性比例）",
    # LIT-PCBA 的总数在官方页上自己对不上，而且基准自身有泄漏
    "litpcba_stated": 7761, "litpcba_sum": 7955,
    "litpcba_shared_inactives": 2491,
    "litpcba_baseline_ef1": 4.15,       # 一个无参数的 ECFP4 最大相似度基线的中位原始 EF1%
}

# ---------------------------------------------------------------- 分子性质预测的划分口径
SPLITS = {
    "random": "Random splitting randomly splits samples into the training/validation/test subsets.",
    "scaffold": "Scaffold splitting splits the samples based on their two-dimensional "
                "structural frameworks（按 Murcko 骨架分箱，RDKit 实现）",
    "why_harder": "Scaffold splits provide a stronger test of a given model's generalizability "
                  "compared with random splitting.",
    "not_unique": "剩余骨架箱是**随机**分配的，所以同一数据集可以有多个骨架划分，分数会抖",
    # 能核到的唯一一组落差：MoleculeNet 图卷积，ROC-AUC，骨架划分数据集上的训练/验证/测试
    "bbbp_train": 0.956, "bbbp_valid": 0.943, "bbbp_test": 0.690,
    "hiv_train": 0.903, "hiv_valid": 0.792, "hiv_test": 0.763,
    "paired_numbers": UNPUBLISHED,      # 随机 vs 骨架的成对分数：核不到，不要印"平均掉多少分"
    "chemprop_nonsig": ("PDBbind-C", "HIV", "ClinTox", "ChEMBL"),   # 这四个数据集上差异不显著
}

MOLNET = {                              # Wu 等 2018 Table 1（正文另有一组数，见资料卡第 14 节第 9 条）
    "bbbp": 2039, "bace": 1513, "hiv": 41127, "tox21": 7831,
    "clintox": 1478, "esol": 1128, "freesolv": 642, "qm9": 133885,
    "table1_vs_text": "Table 1 与正文对不上（BACE 1513/1522、Tox21 7831/8014 等）；"
                      "只引 Table 1 并注明原文另有一组",
}

# ---------------------------------------------------------------- 本章不印的东西
NOT_PRINTED = (
    "AI 解决了蛋白质折叠问题",
    "AI 把药物研发周期缩短了 X 倍",
    "lDDT 与 GDT_TS 的换算",
    "换成骨架划分平均掉多少分",
    "pLDDT 是'对的概率'",
)
