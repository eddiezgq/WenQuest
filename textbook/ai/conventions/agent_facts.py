"""代码模型与智能体的公开发表数字（第 17 章用；第 13 章可引）。

规矩与 `gen_facts.py`、`av_facts.py`、`rl_facts.py` 相同：**只收论文正文、官方技术报告、
官方公告或官方文档给出的原始数字**；媒体估算、排行榜截图与第三方转述一律不收；未公布的项用
`UNPUBLISHED` 标出，正文写"未公布"；由原始值算出来的倍数与换算，注释里标"折算"。
每条的出处、位置、口径与"为什么不能横向比较"见
`docs/教材/人工智能/参考/第17章_代码模型与智能体原始数字资料_2026-11.md`。
核对日期：2026 年 11 月 1 日。

**本章特别要当心的三条**（资料卡第 12 节）：
1. SWE-bench 的分数必须三件事一起写：哪个子集、哪个脚手架、哪一版模型。同一个 gpt-4o
   在原集 16%、在 Verified 33.2%；同一个 GPT-4 换脚手架能从 2.7% 走到 28.3%。
   **本书不印任何"当前最好水平"。**
2. pass@k 与 pass^k 是方向相反的两个量，而且 Codex 各档 k 用的温度不同。
   "成功率随步数指数衰减"在本书只作为数学恒等式给出，**不挂任何引文**。
3. 提示缓存只给了价格倍数，没有任何"省多少"的百分比；算账要带上写入成本。
"""

UNPUBLISHED = None                      # 未公布：正文写"未公布"

# ---------------------------------------------------------------- Codex / HumanEval（Chen 等 2021）
HUMANEVAL = {
    "problems": 164,
    "tests_per_problem_codex": 7.7,      # Codex 论文自己的计数
    "tests_per_problem_evalplus": 9.6,   # EvalPlus 论文的计数——两家口径不同，不是同一个量
    "n_samples": 200, "k_max": 100, "top_p": 0.95,
    "temp_pass1": 0.2, "temp_pass10": 0.6, "temp_pass100": 0.8,   # 各 k 取各自最优温度
    "formula": "pass@k = E[1 - C(n-c, k) / C(n, k)]",
    "biased_formula": "1 - (1 - p̂)^k",   # 论文明说这个是有偏的
}
# Table 1（口径见上：各 k 用各自的最优温度，所以列与列之间不是"多采几次的增益"）
CODEX_TABLE1 = {
    "Codex-12M": (2.00, 3.62, 8.58),
    "Codex-85M": (8.22, 12.81, 22.4),
    "Codex-300M": (13.17, 20.37, 36.27),
    "Codex-679M": (16.22, 25.7, 40.95),
    "Codex-2.5B": (21.36, 35.42, 59.5),
    "Codex-12B": (28.81, 46.81, 72.31),
    "GPT-J 6B": (11.62, 15.74, 27.74),
    "GPT-Neo 2.7B": (6.41, 11.27, 21.37),
}
CODEX_TEMP = {                           # 第 2.1 节与 Figure 2：k 越大，最优温度越高
    "model_679m": {"pass1": 0.2, "pass100": 0.8},
    "codex_s": {"pass1": 0.0, "pass100": 1.0},    # 与上面不是同一个模型，不能混引
}
CODEX_SANDBOX = {
    "goals": ("不许改动宿主机", "不许留下持久化痕迹", "不许访问敏感资源", "不许把数据外传"),
    "runtime": "gVisor 容器运行时", "network": "基于 eBPF 的防火墙规则，入站出站全部阻断",
    "why": "执行生成的程序本身就是安全风险：生成的代码经常是错的",
}
# Austin 等 2021（MBPP）
MBPP = {
    "total": 974, "test": 500, "fewshot": 10, "finetune": 374, "val": 90,
    "tests_per_problem": 3, "edited": 426,
    "best_137b": 59.6, "samples_137b": 80, "temp_137b": 0.5,
    "finetune_gain_pts": 10,
    "gives_tests_in_prompt": True,       # MBPP 默认把 3 个断言交给模型，HumanEval 不给
}

# ---------------------------------------------------------------- 污染与测试不足
# Riddell、Ni、Cohan 2024（ACL 2024 长文 761）：重叠判定是"完全匹配"（相似度 100）
CONTAM = {
    "humaneval_pile_pct": 12.2, "humaneval_pile_n": 20,
    "humaneval_starcoder_pct": 18.9, "humaneval_starcoder_n": 31,
    "mbpp_pile_pct": 3.6, "mbpp_pile_n": 18,
    "mbpp_starcoder_pct": 20.8, "mbpp_starcoder_n": 104,
    # 剔掉"完全匹配"题之后（Table 1，指标是 accuracy，论文不用 pass@1 这个词）
    "drop": {"MBPP/StarCoderBase-15.5B": (41.6, 33.8), "MBPP/Pythia-12B": (17.8, 17.0),
             "HumanEval/StarCoderBase-15.5B": (30.5, 22.6), "HumanEval/Pythia-12B": (9.8, 4.2),
             "HumanEval/CodeGen-NL-16B": (14.6, 8.3)},
    # 相似度最高 10% 的题 vs 最低 10% 的题（Table 2 / Table 4）
    "top_vs_bottom": {"HumanEval/StarCoderBase-15.5B": (75.0, 31.3),
                      "HumanEval/Pythia-12B": (56.3, 0.0),
                      "MBPP/StarCoderBase-15.5B": (72.0, 22.0)},
    "gap_before": 23.8, "gap_after": 13.9,          # 去污染后两个模型的差距
    "single_number": UNPUBLISHED,                   # "污染抬高多少"论文不给一个总数
    "causal": False,                                # 论文明说只是相关性，不能确定因果
}
# Liu 等 2023（EvalPlus）：这是"测试不够"，不是"污染"，两件事不要混讲
EVALPLUS = {
    "test_multiplier": 80, "tests_before": 9.6, "tests_after": 764.1,
    "wrong_reference_solutions": 18, "wrong_pct": 11,
    "gpt4_before": 88.4, "gpt4_after": 76.2, "gpt4_rel_drop": 13.1,
    "chatgpt_before": 73.2, "chatgpt_after": 63.4,
    "max_drop_pass1": 19.3, "max_drop_pass100": 28.9,
    "models": 26, "rank_flip": True,
    "mbpp_plus": UNPUBLISHED,                       # 本论文没有 MBPP+ 结果
}

# ---------------------------------------------------------------- SWE-bench
SWEBENCH = {
    "instances": 2294, "repos": 12, "lite": 300, "lite_repos": 11,
    "dev": 225, "dev_repos": 6,
    "pass_rule": ("补丁能干净地打上", "全部 FAIL_TO_PASS 测试通过", "全部 PASS_TO_PASS 测试仍通过"),
    "files_mean": 3010, "files_max": 5890,          # 非测试文件
    "lines_mean_k": 438, "lines_max_k": 886,        # 非测试代码（千行）
    "patch_files": 1.7, "patch_lines": 32.8,        # 官方补丁平均只改这么多
    "issue_words_mean": 195.1,
    "bm25_budgets_k": (13, 27, 50),
    "is_agent": False,                              # 原论文是单轮"读提示→产出 diff"，不是 agent
    "repo_tokens": UNPUBLISHED,                     # 没有任何论文给"典型仓库多少词元"
}
SWEBENCH_VERIFIED = {                               # OpenAI 官方公告 2024-08-13
    "samples": 500, "annotated": 1699, "annotators": 93, "entry_test": 50, "labels_per_sample": 3,
    "underspecified_pct": 38.3, "unfair_tests_pct": 61.1, "filtered_pct": 68.3,
    "easy": 196, "hard": 45,
    "gpt4o_verified": 33.2, "gpt4o_original": 16,   # 同一个 gpt-4o-2024-05-13，差一倍
    "gpt4o_scaffold": "Agentless", "gpt4o_model": "gpt-4o-2024-05-13",
    "scaffold_low": 2.7, "scaffold_high": 28.3,     # 同一个 GPT-4 在 Lite 上换脚手架
    "other_models": UNPUBLISHED,
}

# ---------------------------------------------------------------- 智能体
# Yao 等 2022（ReAct，PaLM-540B，冻结参数、少样本提示）
REACT = {
    "backbone": "PaLM-540B（冻结参数、少样本提示）",
    "hotpotqa": {"Standard": 28.7, "CoT": 29.4, "CoT-SC": 33.4, "Act": 25.7,
                 "ReAct": 27.4, "CoT-SC→ReAct": 34.2, "ReAct→CoT-SC": 35.1, "监督 SOTA": 67.5},
    "fever": {"Standard": 57.1, "CoT": 56.3, "CoT-SC": 60.4, "Act": 58.9, "ReAct": 60.9},
    "alfworld_react": 71, "alfworld_butler": 37, "alfworld_gain_pts": 34, "alfworld_games": 134,
    "webshop_react_score": 66.6, "webshop_react_sr": 40.0,
    "webshop_act_sr": 30.1, "webshop_human_sr": 59.6, "webshop_instructions": 500,
    "fallback_steps_hotpotqa": 7, "fallback_steps_fever": 5,   # 唯一有原文的"步数预算"
    "cot_sc_samples": 21, "cot_sc_temp": 0.7,
}
# Shinn 等 2023（Reflexion）
REFLEXION = {
    "alfworld_solved": 130, "alfworld_total": 134, "alfworld_gain_pts": 22,
    "alfworld_trials": 12, "memory_reflections": 3, "memory_coding": 1,
    "hotpotqa_react_gpt4": (0.39, 0.51), "hotpotqa_cot_gpt4": (0.68, 0.80),
    "humaneval_py": (80.1, 91.0), "mbpp_py": (80.1, 77.1),   # MBPP 上反而更低，必须一起引
    "humaneval_rust": (60.0, 68.0), "leetcode_hard": (7.5, 15.0),
    "false_positive_humaneval": 1.4, "false_positive_mbpp": 16.3,
    "ablation_full": 68, "ablation_no_tests": 52, "ablation_no_reflect": 60,  # HumanEval Rust
    "small_model": (0.26, 0.26),                    # starchat-beta：毫无提升
    "tests_per_problem": 6,
    "react_baseline_solved": UNPUBLISHED,
}
# Yao 等 2024（τ-bench）：pass^k 与 pass@k 方向相反，教材要并排印
TAU_BENCH = {
    "pass_k_formula": "pass^k = E[C(c, k) / C(n, k)]（k 次独立重跑全部成功）",
    "pass_at_k_formula": "pass@k = 1 - E[C(n-c, k) / C(n, k)]（k 次里有一次成功）",
    "retail_tasks": 115, "airline_tasks": 50,
    "retail_tools": 15, "airline_tools": 13,
    "agent_temp": 0.0, "user_temp": 1.0,
    "pass1": {"gpt-4o": (61.2, 35.2), "claude-3-opus": (44.2, 34.7),
              "gpt-3.5-turbo": (20.0, 10.8), "meta-llama-3-70B": (14.8, 14.4)},
    "pass8_gpt4o_retail_below": 25,                 # 唯一给出的 pass^8：低于 25%
    "pass_k_values": UNPUBLISHED,                   # pass^2—pass^7 正文没给
}
# Kwa 等 2025（METR，arXiv，不是会议/期刊论文）
METR = {
    "model": "p = σ((log h_model − log t_task)·β)",  # 成功率随任务长度衰减的唯一有原文的函数形式
    "tasks": 170, "tasks_table2": 169,              # 论文自身不一致
    "models": 13,
    "h50_claude37": 59, "h50_o1": 39, "h80_claude37": 15,   # 分钟
    "doubling_days": 212, "doubling_ci": (171, 249), "doubling_abstract_months": 7,
    "h80_over_h50": 5,                              # 80% 视界大致比 50% 视界短 5 倍
    "fit_slope": -0.07, "fit_intercept": 0.66, "fit_r2": 0.83,
}
# "成功率随步数衰减"：没有任何论文给出逐步曲线
STEP_DECAY_SOURCE = None                            # 本书只作为数学恒等式 (1−p)^n 给出

# ---------------------------------------------------------------- 工具调用与上下文（只收官方文档）
TOOLS = {
    "openai_soft_limit": 20,                        # 官方指南："争取少于 20 个"，自称只是软建议
    "openai_soft_limit_is_soft": True,
    "anthropic_hard_limit": UNPUBLISHED,            # 不给任何数字上限
    "per_tool_tokens": UNPUBLISHED,                 # 单个工具定义占多少词元，两家都不给
    # Anthropic 官方表：启用工具本身的系统提示开销（不含你自己的工具定义）
    "system_overhead": {"Claude Opus 5.5": (286, 406), "Claude Opus 4.7": (675, 804),
                        "Claude Sonnet 5": (354, 474), "Claude Haiku 3.5": (264, 355)},
    "parallel_default": UNPUBLISHED,                # 默认是否开启，文档没明说
    "everything_counts": "请求里的一切都计入上下文窗口：系统提示、每一条消息、工具定义、工具结果、生成的响应",
}
CACHE = {                                           # Anthropic 官方文档，核对日 2026-11-01
    "write_5min": 1.25, "write_1h": 2.0,
    "read_default": 0.1, "read_opus55": 0.05, "read_fable51": 0.025,
    "ttl_default_min": 5, "refresh_on_hit": True,
    "min_cacheable": (512, 1024, 2048, 4096),       # 逐模型不同；太短不缓存也不报错
    "breakpoints": 4,
    "tools_cacheable": True,
    "savings_pct": UNPUBLISHED,                     # "命中省多少"官方不给任何百分比
    "not_rate_limited": True,
}

# ---------------------------------------------------------------- 安全（只收防护侧）
PROMPT_INJECTION = {
    "owasp_def": "当用户提示以非预期的方式改变了 LLM 的行为或输出时，就存在提示注入漏洞",
    "direct": "用户的提示直接改变模型行为（可能是故意，也可能是无意）",
    "indirect": "模型接受来自外部来源（网站、文件等）的输入，其中的内容改变了模型行为",
    "defenses": ("约束模型行为", "定义并校验预期的输出格式", "实施输入与输出过滤",
                 "执行权限控制与最小权限", "高风险动作要求人工批准",
                 "隔离并标识外部内容", "进行对抗性测试与攻击模拟"),
    "no_silver_bullet": "目前没有万无一失的方案（Greshake 等 2023 的原话大意）",
    "ipi_source": "Greshake 等 2023（AISec'23，arXiv:2302.12173）：间接提示注入概念的学术出处",
}
OWASP_LLM = {
    "version": "OWASP Top 10 for LLM Applications 2025（页脚标注 v2.0）",
    "items": ("LLM01 提示注入", "LLM02 敏感信息泄露", "LLM03 供应链", "LLM04 数据与模型投毒",
              "LLM05 输出处理不当", "LLM06 过度自主权", "LLM07 系统提示泄露",
              "LLM08 向量与嵌入弱点", "LLM09 错误信息", "LLM10 无界资源消耗"),
    "closest_to_agents": ("LLM06 过度自主权", "LLM05 输出处理不当"),
}
NIST_AML = {
    "title": "Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations",
    "no": "NIST AI 100-2 E2025", "issued": "2025-03-24",
    "body_read": False,                             # 正文未读到，本书不引它的定义原文
}
