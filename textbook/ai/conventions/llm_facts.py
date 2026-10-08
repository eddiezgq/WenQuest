"""大语言模型的公开发表数字（全书共用；第 13 章用，第 9、14 章可引）。

规矩：**只收论文正文、官方技术报告或官方公告给出的原始数字**；二手概括与第三方排行榜不收；
厂商未公布的项用 `UNPUBLISHED` 标出，正文一律写“未公布”，不写传闻数字。
每条的出处、口径与“为什么不能横向比较”见 `docs/教材/人工智能/参考/第13章_大模型原始数字资料_2026-10.md`。
核对日期：2026 年 10 月 5 日。
"""

UNPUBLISHED = None                  # 厂商未公布：正文写“未公布”

# ---------------------------------------------------------------- 词向量（类比任务的准确率，%）
# Mikolov 等 2013，Efficient Estimation of Word Representations in Vector Space（论文正文表 4、表 6）
W2V = {
    "skipgram_783M_300": (50.0, 55.9, 53.3),      # （语义, 句法, 总）
    "cbow_783M_300": (15.5, 53.1, 36.1),
    "skipgram_6B_1000": (66.1, 65.1, 65.6),
}
W2V_CORPUS_WORDS = 6_000_000_000    # Google News 约 60 亿词
W2V_VOCAB = 1_000_000               # 最高频 100 万词
W2V_SEM_Q, W2V_SYN_Q = 8869, 10675  # 类比测试集：语义 / 句法的题数

# Pennington 等 2014，GloVe（论文正文表 2）。表 2 里的 skip-gram/CBOW 行是 GloVe 作者自行复现的，不算原作者报告值
GLOVE = {"300d_6B": (77.4, 67.0, 71.7), "300d_42B": (81.9, 69.3, 75.0)}
GLOVE_VOCAB = 400_000

# ---------------------------------------------------------------- 机器翻译（BLEU）
# Sutskever 等 2014（论文正文）
SEQ2SEQ = {"single_lstm_beam12": 30.59, "ensemble5_beam12": 34.81, "rerank_1000best": 36.5, "smt_baseline": 33.30}
SEQ2SEQ_PARAMS = 384_000_000
SEQ2SEQ_PAIRS = 12_000_000          # 句对
# Bahdanau 等 2015（论文正文表 1）：（全部句子, 剔除含未登录词的句子）
ATTN_BLEU = {"rnnsearch50": (26.75, 34.16), "rnnencdec50": (17.82, 26.71), "moses": (33.30, 35.63)}
# Vaswani 等 2017（论文正文表 2、表 3）
TRANSFORMER = {
    "base": {"ende": 27.3, "enfr": 38.1, "flops": 3.3e18, "params": 65_000_000, "steps": 100_000, "hours": 12},
    "big": {"ende": 28.4, "enfr": 41.8, "flops": 2.3e19, "params": 213_000_000, "steps": 300_000, "hours": 84},
}

# ---------------------------------------------------------------- 预训练
# Devlin 等 2018（论文正文）
BERT = {
    "base": {"params": 110_000_000, "layers": 12, "d": 768, "heads": 12, "tpu_chips": 16, "days": 4},
    "large": {"params": 340_000_000, "layers": 24, "d": 1024, "heads": 16, "tpu_chips": 64, "days": 4},
}
BERT_CORPUS_WORDS = 3_300_000_000   # BooksCorpus 8 亿 + 英文维基 25 亿
BERT_TOKENS_PER_BATCH = 128_000     # 256 序列 × 512 词元
BERT_STEPS = 1_000_000
BERT_GLUE = {"base": 79.6, "large": 82.1, "prev_best": 74.0}
BERT_SQUAD11 = {"single": (84.1, 90.9), "ensemble": (85.8, 91.8), "human": (82.3, 91.2)}   # （EM, F1）

# Radford 等 2019，GPT-2（官方技术报告）
GPT2_PARAMS = (117_000_000, 345_000_000, 762_000_000, 1_542_000_000)
GPT2_DOCS, GPT2_GB = 8_000_000, 40  # “略超过 800 万份文档、共 40 GB 文本”

# Brown 等 2020，GPT-3（论文正文表 2.1、2.2）
GPT3_PARAMS = (125e6, 350e6, 760e6, 1.3e9, 2.7e9, 6.7e9, 13e9, 175e9)
GPT3_TOKENS = 300_000_000_000       # 全部 8 档都训练 3000 亿词元
GPT3_175B = {"layers": 96, "d": 12288, "heads": 96, "d_head": 128}
GPT3_MIX = {                        # 语料：(词元数, 采样权重 %)
    "Common Crawl（过滤后）": (410e9, 60), "WebText2": (19e9, 22),
    "Books1": (12e9, 8), "Books2": (55e9, 8), "维基百科": (3e9, 3),
}
GPT3_LAMBADA = (76.2, 86.4)         # （零样本, few-shot）
GPT3_TRIVIAQA = (64.3, 71.2)
GPT3_MMLU_FEWSHOT = 43.9            # MMLU 论文给出
GPT3_3B_PFDAYS = 50                 # 论文图 2.2 说明：GPT-3 3B 与 RoBERTa-Large 各约 50 petaflop/s-days
GPT3_TOTAL_FLOPS = UNPUBLISHED      # 常被引的 3.14e23 在附录表 D.1，本次未核到 → 正文不写

# ---------------------------------------------------------------- 规模定律
# Kaplan 等 2020（论文正文）
KAPLAN = {"alpha_N": 0.076, "N_c": 8.8e13, "alpha_D": 0.095, "D_c": 5.4e13,
          "alpha_C": 0.050, "C_c_pfdays": 3.1e8,
          "N_exp": 0.73, "B_exp": 0.24, "S_exp": 0.03, "D_exp": 0.27}
# Hoffmann 等 2022，Chinchilla（论文正文表 3 与结果表）
CHINCHILLA_OPT = {67e9: 1.5e12, 175e9: 3.7e12, 280e9: 5.9e12}     # 参数 → 最优词元数
CHINCHILLA = {"params": 70e9, "tokens": 1.4e12, "mmlu": 67.6, "bigbench": 65.1, "race_m": 86.8, "race_h": 82.3}
GOPHER = {"params": 280e9, "tokens": 300e9, "mmlu": 60.0, "bigbench": 54.4, "race_m": 75.1, "race_h": 71.6}
MMLU_EXPERT = 89.8                  # Chinchilla 与 MMLU 两篇都引的“95 百分位应试者”估计

# ---------------------------------------------------------------- 对齐
# Ouyang 等 2022，InstructGPT（论文正文）
INSTRUCTGPT = {"params": (1.3e9, 6e9, 175e9), "win_vs_gpt3": (85, 3), "win_vs_fewshot": (71, 4),
               "sft_prompts": 13_000, "rm_prompts": 33_000, "ppo_prompts": 31_000, "labelers": 40}
STIENNON_COMPARISONS = 64_832       # Stiennon 等 2020：TL;DR 上的两两比较条数
DPO = {"tldr_win": 61, "sft_base": 6e9, "chat_base": 2.8e9,
       "human_vs_gpt4_agree": 67, "human_vs_human_agree": 65}

# ---------------------------------------------------------------- 检索增强
# Lewis 等 2020，RAG（论文正文表 1；精确匹配 %）
RAG = {"rag_seq": (44.5, 56.8, 45.2, 52.2), "rag_tok": (44.1, 55.2, 45.5, 50.0)}
RAG_BASELINES = {"T5-11B": (34.5, None, 37.4, None), "T5-11B+SSM": (36.6, None, 44.7, None),
                 "REALM": (40.4, None, 40.7, 46.8), "DPR": (41.5, 57.9, 41.1, 50.6)}   # 抄录自 RAG 表 1
RAG_TASKS = ("Natural Questions", "TriviaQA", "WebQuestions", "CuratedTrec")
RAG_INDEX = {"passages": 21_000_000, "words_per_passage": 100, "generator_params": 400_000_000}
ATLAS = {"nq_64shot": 42.4, "nq_full": 64.0, "mmlu_5shot": 43.4, "params": 11e9}

# ---------------------------------------------------------------- 推理与思维链
# Wei 等 2022（论文正文图 4，已复核）：GSM8K（标准提示, 思维链）
COT_GSM8K = {"PaLM 540B": (17.9, 56.9), "GPT-3 175B": (19.3, 40.7), "LaMDA 137B": (17.3, 47.9)}
COT_PRIOR_SOTA = 55                 # 引自 Cobbe 等 2021 的带验证器微调
# Wang 等 2022，自一致性（论文正文）
SELF_CONSISTENCY = {"gsm8k": (56.5, 74.4), "paths": 40,
                    "gains": {"GSM8K": 17.9, "SVAMP": 11.0, "AQuA": 12.2, "StrategyQA": 6.4, "ARC-c": 3.9}}
# OpenAI o1（2024 官方公告正文）
O1 = {"aime_single": 74, "aime_cons64": 83, "aime_rerank1000": 93, "gpt4o_aime": 12,
      "codeforces_pct": 89, "mmmu": 78.2, "params": UNPUBLISHED, "train_flops": UNPUBLISHED}
# DeepSeek-R1（2025 官方技术报告）
R1 = {"aime": 79.8, "math500": 97.3, "gpqa": 71.5, "mmlu": 90.8, "codeforces_elo": 2029}
R1_ZERO = {"aime_pass1": 71.0, "aime_cons64": 86.7, "math500": 95.9, "gpqa": 73.3, "codeforces_elo": 1444}

# ---------------------------------------------------------------- 评测
# Hendrycks 等 2021，MMLU（论文正文）
MMLU = {"subjects": 57, "questions": 15_908, "test": 14_079, "random": 25.0,
        "crowdworker": 34.5, "expert_95pct": 89.8, "unifiedqa_11b": 48.9}
# Cobbe 等 2021，GSM8K（论文正文）
GSM8K = {"total": 8500, "train": 7500, "test": 1000, "steps": (2, 8)}
# Chen 等 2021，HumanEval / Codex（论文正文）
HUMANEVAL = {"problems": 164, "tests_per_problem": 7.7,
             "pass1": {"GPT-3": 0.0, "Codex-12B": 28.8, "Codex-S-12B": 37.7}, "pass100_codex_s": 77.5}
# Zhang 等 2024，GSM1k（论文正文摘要）：同难度新题上的掉分
GSM1K = {"problems": 1205, "max_drop": 8, "spearman_r2": 0.36}

# ---------------------------------------------------------------- 中文模型（官方技术报告）
DEEPSEEK_V3 = {"params_total": 671e9, "params_active": 37e9, "tokens": 14.8e12,
               "h800_hours": 2.788e6, "h800_pretrain": 2.664e6, "usd_per_gpu_hour": 2.0,
               "cost_usd": 5.576e6, "mmlu_base": 87.1, "mmlu_chat": 88.5, "mmlu_pro": 75.9,
               "gpqa": 59.1, "math500": 90.2, "aime": 39.2, "swebench": 42.0}
QWEN25 = {"open_params": (0.5e9, 1.5e9, 3e9, 7e9, 14e9, 32e9, 72e9), "tokens": 18e12,
          "prev_tokens": 7e12,
          "instruct72b": {"MMLU": 86.1, "MMLU-Pro": 71.1, "MATH": 83.1, "GSM8K": 95.8,
                          "HumanEval": 86.6, "LiveCodeBench": 55.5, "GPQA": 49.0}}

# ---------------------------------------------------------------- 未公布（正文写“未公布”）
GPT4 = {"params": UNPUBLISHED, "train_flops": UNPUBLISHED, "hardware": UNPUBLISHED,
        "data": UNPUBLISHED, "method": UNPUBLISHED}
INFERENCE_COST = UNPUBLISHED        # 各厂只公布接口价格，不公布单位推理的算力或成本
