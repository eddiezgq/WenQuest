"""天气预报、气候与遥感的公开发表数字（第 19 章用）。

规矩与 `bio_facts.py`、`agent_facts.py` 相同：**只收论文正文、官方技术报告、官方公告或官方
文档给出的原始值**；综述转述、媒体估算、排行榜一律不收；未公布的项用 `UNPUBLISHED` 标出，
正文写"未公布"；由原始值算出来的倍数与换算，注释里标"折算"。每条的出处、位置、口径与
"为什么不能横向比较"见
`docs/教材/人工智能/参考/第19章_天气预报与气候原始数字资料_2026-11.md`。
核对日期：2026 年 11 月 2 日。

**本章特别要当心的六条**（资料卡第 13 节）：
1. **"分辨率翻倍 → 算力约 16 倍"是量纲分析，不是任何业务中心的成本标度律。** ECMWF 的
   半拉格朗日方案官方文档明说"unconditional stability allows long timesteps"，并承认业务
   运行中库朗数大于 1；而且它换水平网格时**垂直仍是 137 层**。两条反例要与推导一起印。
2. **两边的"真值"不是同一套资料。** AI 模型训 ERA5、也对 ERA5 评分；业务 IFS 对自己的
   分析场（HRES-fc0）评分。WeatherBench 2 自己说，用 ERA5 评 IFS 会"put the IFS at an
   unfair disadvantage"。最尖锐的证据是 AIFS：**对 NWP 分析评分时第 1 天更差，对探空观测
   评分时并不差**——同一个模型，换真值换结论。
3. **"几分钟出 10 天预报"不含产生初始场的资料同化。** GenCast 自己写它仍依赖传统 NWP 同化；
   ECMWF 官方说 AIFS 用的初始场与 IFS 相同（约 6,000 万条质控观测）。
4. **全章只有 Pangu-Weather 一篇在正文里给了成对的绝对 RMSE 数值。** 其余（GraphCast、
   FourCastNet、WeatherBench 2、AIFS）的误差**只有图、正文不给数**。
5. **"越推越平"有比 AI 论文早得多的官方引文**：ECMWF 预报员指南说统计后处理"essentially
   dampening the forecast anomalies and thereby minimizing the RMSE"，紧接"This might be
   justified in a purely deterministic context but not in an ensemble context"。
6. **权重许可差别极大**：GraphCast 权重 CC BY-NC-SA 4.0（**非商用**），AIFS 权重 CC BY 4.0
   （可商用）。Pangu 与 FourCastNet 的许可**未核到**。教学实验按这个选。
"""

UNPUBLISHED = None                      # 未公布／未核到：正文写"未公布"

# ---------------------------------------------------------------- 一、业务数值预报的规模
IFS = {
    "levels": 137,                      # 垂直层数；换水平网格时没有跟着加密
    "era5_timestep_min_hres": 12,       # ERA5 生产配置里 HRES 的积分时间步（本章唯一有官方出处的时间步）
    "era5_timestep_min_eda": 20,
    "assim_window_h": 12,               # 4D-Var 同化窗口（ERA5 生产，09–21 与 21–09 UTC）
    "obs_per_day": 60_000_000,          # 约 6,000 万条经质控的观测（官方公告）
    "supercomputer": "四套 Atos BullSequana XH2000 集群（意大利博洛尼亚）",
    "processors": 1_000_000,            # 官方页写的是"处理器数"，不是核数
    "petaflops": 30,                    # 官方页未说明是峰值还是实测
    "ops_share": 0.5,                   # 一半机时给日常业务
    "forecast_wallclock": UNPUBLISHED,  # "一次业务预报跑多久/多少核时"——ECMWF 与 NCEP 都不公布
}

CFL = {
    "formula": "C = u·Δt/Δx ≤ C_max；显式格式 C_max ≈ 1",
    "is_quote": False,                  # 这是按定义写的，不是被核到的 NWP 官方文档引文
    "ecmwf_unconditional": "unconditional stability allows long timesteps",
    "ecmwf_courant_gt1": "the long time steps permitted by the scheme, such that the "
                         "Courant number becomes greater than 1",
    "scaling_exponent": 4,              # 2^3（网格点）× 2（步数）= 16 —— **本书的量纲分析**
    "scaling_factor": 16,
    "scaling_is_derivation": True,      # 必须明写"这是推导，不是引文"
    "counterexample_levels": "ECMWF 从 TL1279 换到 TCo1279 时垂直仍是 137 层，连 2³ 那一项都不成立",
}

# ---------------------------------------------------------------- 二、数据同化
ASSIM = {
    "what": "combines the latest observations with a short-range forecast constrained by "
            "previous observations",
    "fourdvar": "4D-Var iteratively adjusts the initial conditions of a short-range forecast",
    "why": "The quality of forecasts crucially depends on the accuracy of the analysis.",
    "cost_share": UNPUBLISHED,          # 同化占整条链的算力比例：官方页都不给
    # AI 模型仍然依赖传统同化——这几句是本章最该引的
    "gencast": "GenCast relies on initial conditions from a traditional NWP ensemble data "
               "assimilation system, and therefore using GenCast for operational forecasts "
               "will still require NWP-based data assimilation",
    "graphcast_depends": "data-driven MLWP depends critically on large quantities of "
                         "high-quality data, assimilated via NWP",
    "graphcast_not_replacement": "our approach should not be regarded as a replacement for "
                                 "traditional weather forecasting methods",
    "aifs_same_ic": "uses the same initial conditions for its forecasts as the IFS",
    "fourcastnet_none": "It has no data-assimilation component.",
    "ecmwf_complementary": "We see the AIFS and IFS as complementary",
}

# ---------------------------------------------------------------- 三、再分析资料 ERA5
ERA5 = {
    "res_deg": 0.25,                    # 再分析本体；集合量是 0.5°，两者不能混引
    "res_deg_ensemble": 0.5,
    "hourly": True,
    "since_year": 1940,
    "pressure_levels": 37,              # 1000 hPa 到 1 hPa
    "license": "CC-BY",
    "n_lat": 721, "n_lon": 1440,
    "n_points": 721 * 1440,             # 折算（本卡自算）；GraphCast 论文正文独立给出同一个数
    "native_res_km": 31,                # 生产配置：31 km / 0.28125° / T639 / N320
    "native_levels": 137, "model_top_hpa": 0.01,
    "eda_members": 10, "eda_res_km": 63,
    "n_variables": UNPUBLISHED,         # 官方页不给总数，本书不把分类条数相加
    "is_truth": False,
    "what_it_is": "combines model data with observations from across the world",
    "spread_overconfident": "numerical values are over confident",
    "wb2_unfair": "would put the IFS at an unfair disadvantage",
    "wb2_analysis": "HRES-fc0（把 IFS HRES 在 t=0 的场当分析）",
}

# ---------------------------------------------------------------- 四、AI 天气模型
GRAPHCAST = {
    "res_deg": 0.25, "n_points": 721 * 1440,
    "vars_surface": 5, "vars_upper": 6, "levels": 37, "per_point": 227,
    "step_h": 6, "max_lead_days": 10,
    "params_m": 36.7,                   # 3,670 万——比同期大语言模型小三个数量级
    "train_years": "1979—2015（验证 1979—2017 的后两年），测试自 2018 年起，主评测年 2018",
    "train_hw": "32 块 Cloud TPU v4，约 4 周",
    "infer": "10 天预报 < 1 分钟，单块 Cloud TPU v4（不含同化）",
    "loss": "MSE；50 hPa 及以下只占总损失权重的 0.66%",
    "ar_steps": 12,                     # 训练最终对 12 步（3 天）求最优
    "code_license": "Apache 2.0",
    "weights_license": "CC BY-NC-SA 4.0",   # **非商用**
    "wins_pct": 90.3, "wins_targets": 1380,  # 1380 = 变量×时效×层次的组合数，不是天气个例
    "wins_significant_pct": 89.9,
    "rmse_values": UNPUBLISHED,         # 只给技巧评分改进 7%—14%，不给绝对 RMSE
    "blur_quote": "encourages it to express its uncertainty by predicting spatially "
                  "smoothed outputs",
}

PANGU = {
    "res_deg": 0.25, "n_lat": 721, "n_lon": 1440,
    "vars_upper": 5, "levels": 13, "vars_surface": 4,
    "models": (1, 3, 6, 24),            # 四个独立模型，时效 1/3/6/24 小时
    "params_m": 256,                    # 摘要给合计；正文不给每个模型各多少
    "train_years": "训练 1979—2017，验证 2019，测试 2018/2020/2021，主评测年 2018",
    "train_hw": "192 块 NVIDIA Tesla V100",
    "train_epochs": 100,
    "not_converged": "insufficient for the training procedure to arrive at full convergence",
    "infer_ms_24h_v100": 1400,
    "speedup_claim": 10_000,            # "比业务 IFS 快一万倍以上"——不是同一次测量
    "speedup_same_measurement": False,
    "weights_license": UNPUBLISHED,
}

# **全章唯一一组论文正文给出的成对绝对 RMSE**（口径七件事齐全，见资料卡 6.1）
PANGU_RMSE = {
    "truth": "留出的 ERA5", "year": 2018, "res_deg": 0.25,
    "ifs_source": "ECMWF IFS，取自 TIGGE 存档",
    "sample_gap": "2018 年 12 月的测试点缺失（ECMWF 服务器错误）；T850 另排除 2018 年 10 月",
    "z500_3d_ifs": 152.8, "z500_3d_pangu": 134.5,      # m²/s²
    "z500_5d_ifs": 333.7, "z500_5d_pangu": 296.7,
    "t850_3d_ifs": 1.37, "t850_3d_pangu": 1.14,        # K
    "t850_5d_ifs": 2.06, "t850_5d_pangu": 1.79,
}

AIFS = {
    "operational_since": "2025 年 2 月 25 日",   # 全章唯一"AI 天气模型进入业务"的官方日期
    "runs_per_day": 4,
    "res_km_announcement": 28,          # ⚠️ 官方公告写 28 km
    "res_km_modelcard": 31,             # ⚠️ 官方模型卡写 31 km——两处不一致
    "ifs_res_km": 9,
    "levels": 13,
    "step_h": 6,
    "ar_train_h": 72,                   # 训练只滚到 72 小时（12 步），评测却到 10 天
    "max_lead": UNPUBLISHED,
    "params": UNPUBLISHED,              # 模型卡只给检查点 1.19 GB
    "train_hw": "64 块 A100（40 GB），CINECA Leonardo，约一周",
    "infer": "10 天预报约 2 分 30 秒，单块 A100（含输入输出）",
    "weights_license": "CC BY 4.0",     # 本章唯一权重可商用的代表性模型
    "code_license": "Apache 2.0",
    "rmse_values": UNPUBLISHED,         # 论文正文不给任何数值 RMSE/ACC
    "improvement_order": "of the order of 10%",
    "worse_at_50hpa": True,
    "lead_advantage_h": 12,             # Z500 北半球 ACC：长时效上超过 12 小时的预报优势
    # ⚠️ 本章最尖锐的一条：同一个模型，换真值换结论
    "day1_worse_vs_analysis": True,
    "day1_not_worse_vs_radiosonde": True,
    "limits": ("长时效预报场会模糊（加权 MSE 损失训练的共性）",
               "平流层成绩下降，部分因模式顶偏低",
               "某些高影响系统（如热带气旋）强度偏弱",
               "GPU 非确定性，用户无法精确复现官方 AIFS 预报"),
    "energy_claim": "每次预报能耗约低 1,000 倍（官方公告，**未给测量方法**）",
}

GENCAST = {
    "res_deg": 0.25, "step_h": 12, "max_lead_days": 15,
    "members": 50,
    "params": UNPUBLISHED,
    "train_hw": "阶段一 200 万步、32 个 TPUv5、约 3.5 天；阶段二 6.4 万步、约 1.5 天",
    "infer": "单个 15 天预报约 8 分钟，单块 Cloud TPUv5（成员可并行）",
    "wins_pct": 97.4, "wins_targets": 1320, "wins_pct_beyond36h": 99.8,
    "eval_year": 2019,
    "precip_excluded": True,            # 降水被排除在主结果之外
}

FOURCASTNET = {
    "res_deg": 0.25, "n_vars": 20, "levels": 5,
    "params": UNPUBLISHED,
    "train_hw": "64 块 A100，墙钟约 16 小时",
    "train_gpu_hours": 64 * 16,         # 折算（本卡自算），论文没写这个数
    "infer": "7 秒 / 100 成员 × 24 h，1 个 Perlmutter 节点（4×A100）",
    "rmse_values": UNPUBLISHED,         # 正文不给数值，只有图
    "weights_license": UNPUBLISHED,
}

NEURALGCM = {
    "kind": "混合式：可微分动力核心 + 学习的物理",
    "res_deg": (2.8, 1.4, 0.7), "sigma_levels": 32,
    "timestep_min": (12, 6, 3.75),      # 全章唯一把 AI 模型"时间步"写明的一组
    "throughput": "约 70,000 模拟日 / 24 小时墙钟，单块 TPU（1.4°）",
    "baseline": "X-SHiELD：19 模拟日 / 24 小时，13,824 个 CPU 核",
    "saving_claim": "3—5 个数量级",
    "saving_caveat": "分辨率比对照粗 8—40 倍，必须一起写",
}

# ---------------------------------------------------------------- 五、"越推越平"
SMOOTHING = {
    # 比任何 AI 论文都早的官方引文——本章这一节的主引文
    "ecmwf_mos": "essentially dampening the forecast anomalies and thereby minimizing the RMSE",
    "ecmwf_caveat": "This might be justified in a purely deterministic context but not in "
                    "an ensemble context",
    "graphcast": GRAPHCAST["blur_quote"],
    "aifs": "长时效预报场会模糊，这是用加权 MSE 损失训练的模型的共性",
}

# ---------------------------------------------------------------- 六、评测规则
WB2 = {
    "regrid": "first-order conservatively regridded to 1.5° resolution",
    "why": "allows all models to be evaluated without penalizing coarser-resolution models",
    "scope": "全球所有格点",
    "rmse_matches": "Note that this agrees with the definition of the RMSE used by the "
                    "WMO and ECMWF.",
    "eval_year": 2020, "eval_res_deg": 1.5,
    "headline_values": UNPUBLISHED,     # 正文不给任何 Z500/T850 数值，只有图
}

CRPS = {
    "two_estimators": True,             # 两种估计量分母不同，不是笔误
    "denominator_gencast": "2M²",
    "denominator_wb2": "2M(M−1)",
    "note": "印公式必须说明用的是哪一个",
}

# ---------------------------------------------------------------- 七、遥感
REMOTE = {
    "bigearthnet_leakage_claim": False,  # BigEarthNet 从未用过 leakage 一词——不要安在它头上
    "kattenborn_overestimate_pct": 28,   # 空间自相关下精度最高高估 28%
    "stock_underestimate_pct": (5, 54),  # 十折交叉验证低估误差 5%—54%
    "stock_wrong_model_pct": 99,         # 在 99% 的子集上选错模型
}

# ---------------------------------------------------------------- 八、风能（本章的实际问题）
WIND = {
    "power_law": "P = ½·ρ·A·v³·Cp —— 风功率与风速的三次方成正比",
    "speed_to_power_published": UNPUBLISHED,   # "风速误差→功率误差"的量化关系：核不到口径完整的
    "note": "所以本章那笔账只能用三次方关系自己算，并明写是本书的折算",
}

# ---------------------------------------------------------------- 本章不印的东西
NOT_PRINTED = (
    "AI 天气模型已经超过传统数值预报",
    "分辨率翻倍要多花十几倍算力（当成业务中心的成本标度律）",
    "快 X 万倍（不写两边硬件、分辨率、是否含同化）",
    "拿天气预报的成绩去说气候模拟",
    "AI 预测未来气温",
    "随机像素划分会泄漏（安在 BigEarthNet 头上）",
)
