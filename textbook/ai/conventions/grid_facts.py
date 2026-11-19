"""第 22 章（能源、电网与工业控制）要印的公开数字，一处定义、处处引用。

出处逐条记在
`docs/教材/人工智能/参考/第22章_能源与电网原始数字资料_2026-11.md`。

纪律与第 17—21 章同：只收论文正文、官方公告、官方文档或官方建模假设给出的原始值；
口径不全的进 `NOT_PRINTED`；凡"本书自己折算"的，逐条标明。

本章另有一条自己的纪律（第 14 轮细则 §2.24 第 7 条）：**不印任何“人工智能让电网节省
了百分之多少”的数字**，除非基线、统计期、测量方三样齐全。本次查下来，唯一一组公开
数字（见 COOLING）三样都不全——所以它在本章的用法是**反面教材**，连原话与缺口一起印。
"""
from __future__ import annotations

# ================================================ 一、聚变等离子体控制（22.4 节）

TOKAMAK_RL = {
    "device": "TCV",
    "control_rate_khz": 10,             # 原话 "acts at a 10 kHz control rate"
    "n_coils": 19,                      # 原话 "each of the 19 magnetic control circuit voltage power supplies"
    "simulator": "FGE",                 # 原话 "the dynamics are modeled with the free-boundary simulator, FGE"
    "free_boundary": True,
    "actor_small_because": "要在 10 kHz 下跑完，所以执行网络必须小；评价网络只在训练时用",
    "actor_size": None,                 # 论文未给参数量与层数
    "sim_step_s": 2.0,                  # "around 2 seconds for a typical simulation step"
    "episode_steps": 10000,             # "an episode with 10,000 steps in approximately 5 hours"
    "episode_hours": 5.0,
    "train_days_to_weeks": True,        # "days for simple tasks to weeks for more complicated ones"
    "improved_hours": 10.0,             # showcase_xpoint：10 小时达到 96 分
    "baseline_hours": 40.0,             # 同一任务的基线 40 小时
    "improved_reward": 96,              # 满分 100
    "ref": "arXiv:2307.11546 §2.2、§3.3；所述系统见 Degrave et al., Nature 602, 414 (2022)",
}

TEARING_RL = {
    "device": "DIII-D",
    "actuators": "等离子体形状与中性束功率",
    "objective": "把未来出现撕裂不稳定的可能性压在阈值以下",
    "lead_time_ms": None,               # 新闻稿里有数，论文正文本次未核到
    "ref": "J. Seo et al., Nature (2024)；本次经 APS DPP 2024 会议摘要页转述核到结构性描述",
}

# ================================================ 二、数据中心冷却（22.3 节）

COOLING = {
    "cooling_cut_pct": 40,              # "reduce the amount of energy we use for cooling by up to 40 percent"
    "pue_overhead_cut_pct": 15,         # "a 15 percent reduction in overall PUE overhead"
    "date": "2016-07-20",
    "wording_conflict": ("同一篇里既写 “up to 40 percent”，又写 “consistently achieve a "
                         "40 percent reduction”——两种说法的含义不一样"),
    "baseline": None,                   # 没给基线
    "period": None,                     # 没给统计期（只说 "a typical day of testing"）
    "measured_by": None,                # 没给测量方
    "ref": "Google 官方博客，2016-07-20",
}

# ================================================ 三、储能的公开建模假设（22.2、22.6 节）

STORAGE_ATB = {
    "round_trip_eff": 0.85,             # "the 2024 ATB assumes a round-trip efficiency of 85%"
    "durations_h": (2, 4, 6, 8, 10),
    "default_duration_h": 4,
    "lifetime_years": 15,
    "cycles_per_day": 1.0,              # "approximately one cycle per day"
    "capacity_factor_4h_pct": 16.7,
    "is_modeling_assumption": True,     # **这是建模假设，不是实测统计**
    "ref": "NREL Annual Technology Baseline 2024，Utility-Scale Battery Storage",
}

# 本章算例用的电池：**显式假设**，写在正文里，与上表只作量级对照
BATTERY_ASSUMED = {
    "cap_kwh": 600.0, "p_max_kw": 150.0, "eta": 0.93,
    "soc_min": 0.15, "soc_max": 0.95,
    "note": "问渠减速器车间那组储能的假想参数，不取自任何厂家样本",
}

# ================================================ 四、公开竞赛与数据（22.1 节、GPU 实验 22.1）

GEFCOM2014 = {
    "tracks": ("load", "price", "wind", "solar"),
    "participants": 581,
    "countries": 61,
    "quantiles_required": None,         # “99 个分位数 + 弹球损失”本次未核到正文原话
    "ref": "Hong et al., International Journal of Forecasting 32(3), 896–913 (2016) 摘要",
}

WEATHER_API = {
    "endpoint": "https://archive-api.open-meteo.com/v1/archive",
    "key_required_noncommercial": False,
    "datasets": ("ERA5（0.25°，1940 年起）", "ERA5-Land（0.1°，1950 年起）"),
    "latency": "Daily with 5 days delay",
    "radiation_is_preceding_hour_mean": True,   # 短波辐照是前一小时的平均值
    "cloud_is_instantaneous": True,
    "licence": None,                    # 条款在另一页，本次未核到
    "reanalysis_not_forecast": True,    # **本章第二号引用警告**
    "ref": "Open-Meteo 官方文档 Historical Weather API 页",
}

# ================================================ 五、本章明确不印的数

NOT_PRINTED = {
    "grid_savings_pct": "“人工智能让电网/工厂节省了百分之多少”的总括数字——基线、统计期、测量方三样齐全才印",
    "fusion_performance": "聚变装置的性能承诺、放电参数、达成指标，以及任何与商业化时间有关的说法",
    "tearing_lead_time": "撕裂模规避“提前多少毫秒”——论文正文本次未核到",
    "degrave_compute": "Degrave et al. (2022) 那次训练的机时（未公布）",
    "cross_study_accuracy": "各家预测模型之间“准多少”的跨研究比较——数据集、地点、时间尺度、评估口径都不同",
    "tariff_clauses": "电价与偏差考核的具体条款——各地差别大，本次未核到可统一引用的原文",
    "cooling_baseline": "数据中心冷却 40% 那个数的基线、统计期与测量方（官方博客没给）",
    "gefcom_metric": "GEFCom2014 要求提交 99 个分位数、按弹球损失评分的正文原话",
    "storage_cn_stats": "中国本地电网级储能效率与寿命的官方统计值",
}


def check() -> None:
    """几条最容易被引错的，用断言钉住。"""
    assert TOKAMAK_RL["control_rate_khz"] == 10 and TOKAMAK_RL["n_coils"] == 19, \
        "10 kHz 与 19 路电源是论文正文的原始值"
    assert TOKAMAK_RL["actor_size"] is None, \
        "实时网络的参数量论文没给，不许补一个"
    assert TOKAMAK_RL["free_boundary"] and TOKAMAK_RL["simulator"] == "FGE", \
        "策略是在自由边界仿真器里训出来的——这是“仿真到现实”那条线的证据"
    assert TEARING_RL["lead_time_ms"] is None, \
        "“提前多少毫秒”没核到正文，不许印"
    assert COOLING["baseline"] is None and COOLING["period"] is None \
        and COOLING["measured_by"] is None, \
        "冷却 40% 那个数三样口径都缺——本章只能连缺口一起印"
    assert STORAGE_ATB["is_modeling_assumption"], \
        "ATB 的 85% 是建模假设，不是实测统计"
    assert WEATHER_API["reanalysis_not_forecast"], \
        "再分析不是预报：拿它当输入算出的误差是下界"
    assert GEFCOM2014["quantiles_required"] is None, \
        "GEFCom2014 的提交口径未核到正文原话"
    assert BATTERY_ASSUMED["soc_min"] < BATTERY_ASSUMED["soc_max"] <= 1.0


check()
