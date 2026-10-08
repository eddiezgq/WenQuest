"""算例 13.3.1—13.3.3：预训练的两条路线与它们的账（13.3 节）。

（1）训练信号：掩码语言模型每句话只预测被遮住的那 15%，自回归语言模型每个位置都预测下一个词——
    同样看一遍语料，后者得到的预测次数多 6 倍多。这解释了为什么生成式模型在同样数据上更“吃得饱”。
（2）预训练一次要多少算力：按 6ND（每个参数每个词元约 6 次浮点运算，9.2 节）算 BERT 与 GPT-3，
    再与论文给出的硬件 × 时间对照，看这个粗估到不到位。
（3）GPT-3 用的词元够不够：按 Chinchilla 的配置折算，175B 参数的“算力最优”词元数是 3.7 万亿，
    而 GPT-3 实际只训了 3000 亿——差一个数量级。这正是 13.4 节要讲的事。
"""
from bookout import out
from llm_facts import (BERT, BERT_CORPUS_WORDS, BERT_GLUE, BERT_SQUAD11, BERT_STEPS,
                       BERT_TOKENS_PER_BATCH, CHINCHILLA_OPT, GPT2_DOCS, GPT2_GB, GPT2_PARAMS,
                       GPT3_175B, GPT3_MIX, GPT3_PARAMS, GPT3_TOKENS)

v = {}
# ---------- （1）训练信号
MASK_RATE, SEQ = 0.15, 512
v["mask_rate"] = MASK_RATE * 100
v["seq"] = SEQ
v["mlm_pred"] = SEQ * MASK_RATE                   # 掩码模型：一条序列预测 76.8 个位置
v["lm_pred"] = SEQ                                # 自回归：每个位置都预测
v["signal_ratio"] = v["lm_pred"] / v["mlm_pred"]
# 代价的另一面：掩码模型能同时看左右（双向），所以在要“读懂整句”的任务上占便宜
v["bert_glue"], v["bert_glue_prev"] = BERT_GLUE["large"], BERT_GLUE["prev_best"]
v["bert_glue_gain"] = BERT_GLUE["large"] - BERT_GLUE["prev_best"]
v["squad_em"], v["squad_f1"] = BERT_SQUAD11["single"]
v["squad_human_em"], v["squad_human_f1"] = BERT_SQUAD11["human"]
v["squad_over_human_f1"] = v["squad_f1"] - v["squad_human_f1"]

# ---------- （2）预训练一次要多少算力（6ND）
def c6nd(n, d):
    return 6 * n * d


v["bert_words"] = BERT_CORPUS_WORDS
v["bert_tokens_per_batch"] = BERT_TOKENS_PER_BATCH             # 256 条序列 × 512 个词元
v["bert_steps"] = BERT_STEPS
v["bert_tokens"] = BERT_TOKENS_PER_BATCH * BERT_STEPS          # 批量 × 步数 = 看过的词元总数
v["bert_epochs"] = v["bert_tokens"] / BERT_CORPUS_WORDS        # 约 40 轮，与论文一致
v["bert_base_params_M"] = BERT["base"]["params"] / 1e6
v["bert_large_params_M"] = BERT["large"]["params"] / 1e6
v["bert_large_flops"] = c6nd(BERT["large"]["params"], v["bert_tokens"])
v["bert_chips"], v["bert_days"] = BERT["large"]["tpu_chips"], BERT["large"]["days"]
v["bert_chip_days"] = v["bert_chips"] * v["bert_days"]
# 反推每块芯片的有效算力：总运算量 ÷ （芯片数 × 天数 × 86400 秒）
v["bert_per_chip_TF"] = v["bert_large_flops"] / (v["bert_chip_days"] * 86400) / 1e12

v["gpt3_params"] = GPT3_PARAMS[-1]
v["gpt3_params_B"] = GPT3_PARAMS[-1] / 1e9
v["gpt3_tokens_B"] = GPT3_TOKENS / 1e9
v["gpt3_flops"] = c6nd(GPT3_PARAMS[-1], GPT3_TOKENS)
v["gpt3_vs_bert"] = v["gpt3_flops"] / v["bert_large_flops"]
v["gpt3_layers"], v["gpt3_d"], v["gpt3_heads"] = GPT3_175B["layers"], GPT3_175B["d"], GPT3_175B["heads"]
# 按一块 A100 的半精度峰值（312 TFLOP/s）与三成实际效率估一估要多久
A100_PEAK, MFU = 312e12, 0.30
v["a100_peak_TF"], v["mfu"] = A100_PEAK / 1e12, MFU * 100
v["gpt3_a100_days"] = v["gpt3_flops"] / (A100_PEAK * MFU) / 86400
v["gpt3_1000gpu_days"] = v["gpt3_a100_days"] / 1000
# 语料：五份数据按不同权重采样，所以“训练 3000 亿词元”并不等于“把语料读一遍”
v["mix_cc_B"] = GPT3_MIX["Common Crawl（过滤后）"][0] / 1e9
v["mix_cc_w"] = GPT3_MIX["Common Crawl（过滤后）"][1]
v["mix_total_B"] = sum(t for t, _ in GPT3_MIX.values()) / 1e9
v["mix_epochs_wiki"] = GPT3_TOKENS * GPT3_MIX["维基百科"][1] / 100 / GPT3_MIX["维基百科"][0]
v["mix_epochs_cc"] = GPT3_TOKENS * GPT3_MIX["Common Crawl（过滤后）"][1] / 100 / GPT3_MIX["Common Crawl（过滤后）"][0]

# ---------- （3）词元够不够
v["chin_opt_T"] = CHINCHILLA_OPT[175e9] / 1e12                 # 175B 参数的“算力最优”词元数（万亿）
v["gpt3_token_share"] = GPT3_TOKENS / CHINCHILLA_OPT[175e9] * 100
v["gpt3_tok_per_param"] = GPT3_TOKENS / GPT3_PARAMS[-1]        # 每个参数不到 2 个词元
v["chin_tok_per_param"] = CHINCHILLA_OPT[175e9] / 175e9
v["gpt2_params_M"] = GPT2_PARAMS[-1] / 1e6
v["gpt2_docs_M"], v["gpt2_GB"] = GPT2_DOCS / 1e6, GPT2_GB
v["gpt3_vs_gpt2_params"] = GPT3_PARAMS[-1] / GPT2_PARAMS[-1]
out(**v)
