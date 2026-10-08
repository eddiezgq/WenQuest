"""13.99 节“公开发表的数字”那张表里的每个数。

数据全部来自 `conventions/llm_facts.py`（只收论文正文、官方技术报告或官方公告的原始数字，
厂商未公布的留空）。这个程序不做研究，只把它们交给正文——表里没有一个手打的数字。
算出来的几个量都是"同一篇论文内部的对照"：与它自己的基线差多少、算力怎么折算。
"""
from bookout import out
from llm_facts import (BERT, CHINCHILLA, DEEPSEEK_V3, GLOVE, GOPHER, GPT3_PARAMS, GPT3_TOKENS, GPT4,
                       HUMANEVAL, INFERENCE_COST, INSTRUCTGPT, MMLU, QWEN25, R1, TRANSFORMER, W2V)

v = {}
# 词向量
v["w2v_sem"], v["w2v_syn"], v["w2v_tot"] = W2V["skipgram_783M_300"]
v["w2v_cbow_sem"] = W2V["cbow_783M_300"][0]
v["w2v_big_tot"] = W2V["skipgram_6B_1000"][2]
v["glove_sem"], v["glove_syn"], v["glove_tot"] = GLOVE["300d_42B"]
v["glove_6b_tot"] = GLOVE["300d_6B"][2]
# 机器翻译
v["tr_base_ende"], v["tr_big_ende"] = TRANSFORMER["base"]["ende"], TRANSFORMER["big"]["ende"]
v["tr_base_enfr"], v["tr_big_enfr"] = TRANSFORMER["base"]["enfr"], TRANSFORMER["big"]["enfr"]
v["tr_base_flops"], v["tr_big_flops"] = TRANSFORMER["base"]["flops"], TRANSFORMER["big"]["flops"]
# 预训练
v["bert_base_M"], v["bert_large_M"] = BERT["base"]["params"] / 1e6, BERT["large"]["params"] / 1e6
v["gpt3_B"], v["gpt3_tok_B"] = GPT3_PARAMS[-1] / 1e9, GPT3_TOKENS / 1e9
# 规模定律
v["chin_B"], v["chin_T"] = CHINCHILLA["params"] / 1e9, CHINCHILLA["tokens"] / 1e12
v["goph_B"], v["goph_B_tok"] = GOPHER["params"] / 1e9, GOPHER["tokens"] / 1e9
v["chin_mmlu"], v["goph_mmlu"] = CHINCHILLA["mmlu"], GOPHER["mmlu"]
v["chin_ratio"] = CHINCHILLA["tokens"] / CHINCHILLA["params"]
# 对齐
v["ig_small_B"], v["ig_big_B"] = INSTRUCTGPT["params"][0] / 1e9, INSTRUCTGPT["params"][2] / 1e9
v["ig_win"], v["ig_win_err"] = INSTRUCTGPT["win_vs_gpt3"]
v["ig_sft"], v["ig_rm"], v["ig_ppo"] = INSTRUCTGPT["sft_prompts"], INSTRUCTGPT["rm_prompts"], INSTRUCTGPT["ppo_prompts"]
v["ig_labelers"] = INSTRUCTGPT["labelers"]
# 评测
v["mmlu_subjects"], v["mmlu_q"] = MMLU["subjects"], MMLU["questions"]
v["mmlu_random"], v["mmlu_crowd"], v["mmlu_expert"] = MMLU["random"], MMLU["crowdworker"], MMLU["expert_95pct"]
v["he_n"], v["he_codex"] = HUMANEVAL["problems"], HUMANEVAL["pass1"]["Codex-12B"]
v["he_gpt3"] = HUMANEVAL["pass1"]["GPT-3"]
# 推理模型与中文模型
v["r1_aime"], v["r1_mmlu"] = R1["aime"], R1["mmlu"]
v["ds_total_B"], v["ds_active_B"] = DEEPSEEK_V3["params_total"] / 1e9, DEEPSEEK_V3["params_active"] / 1e9
v["ds_tok_T"], v["ds_hours_M"] = DEEPSEEK_V3["tokens"] / 1e12, DEEPSEEK_V3["h800_hours"] / 1e6
v["ds_usd_M"], v["ds_price"] = DEEPSEEK_V3["cost_usd"] / 1e6, DEEPSEEK_V3["usd_per_gpu_hour"]
v["ds_mmlu"] = DEEPSEEK_V3["mmlu_chat"]
v["qwen_tok_T"], v["qwen_prev_T"] = QWEN25["tokens"] / 1e12, QWEN25["prev_tokens"] / 1e12
v["qwen_mmlu"] = QWEN25["instruct72b"]["MMLU"]
v["qwen_max_B"] = QWEN25["open_params"][-1] / 1e9
# 算力折算：同一套 6ND 口径下几个模型差多少
v["ds_flops"] = 6 * DEEPSEEK_V3["params_active"] * DEEPSEEK_V3["tokens"]   # 混合专家按激活参数算
v["gpt3_flops"] = 6 * GPT3_PARAMS[-1] * GPT3_TOKENS
v["ds_vs_gpt3"] = v["ds_flops"] / v["gpt3_flops"]
# 未公布的项：正文写“未公布”
v["gpt4_published"] = GPT4["params"] is not None
v["infer_cost_published"] = INFERENCE_COST is not None
out(**v)
