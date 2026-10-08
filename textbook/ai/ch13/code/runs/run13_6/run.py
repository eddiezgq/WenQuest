"""实测：把 13.6 节的哈希向量换成真正的句向量模型，再让一个开源小模型带出处作答（13.6、13.9 节）。

三件事：
（1）**检索**：同一份程序生成的质量手册、同一批问题，比较 BM25、句向量（bge-small-zh-v1.5，公开权重）
    与两者混合的召回率；分别用“手册原词”和“工人口语”两种问法。
    书中算例用的是没有语义的哈希向量，在口语问法上不如 BM25；这里要看训练过的句向量能不能把这一课翻过来。
（2）**作答**：把取回的片子交给 Qwen2.5-0.5B-Instruct（公开权重），要求“按片子回答，并给出条文号；
    片子里没有就回答没有规定”。记下关键事实命中率、引用正确率与该拒的拒住了几个。
（3）**代价**：每个问题的输入词元数与生成时间（解码受带宽限制，9.7 节）。

模型很小，这里的正确率只说明流程通不通、差别在哪，不能当作产品指标。
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))     # 用书中同一套手册与问题
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _ch13 import bm25, chunks, expand, manual, questions, retrieve  # noqa: E402

EMB = "BAAI/bge-small-zh-v1.5"
GEN = "Qwen/Qwen2.5-0.5B-Instruct"
dev = "cuda"
MAN = manual()
QS = questions()
ANS = [q for q in QS if q["answerable"]]
NOANS = [q for q in QS if not q["answerable"]]
CH = chunks(MAN, 300, 60, skip_obsolete=True)
K = 5
out = {"_gpu": torch.cuda.get_device_name(0), "torch": torch.__version__, "emb_model": EMB,
       "gen_model": GEN, "n_clause": len(MAN), "n_chunk": len(CH), "n_ans": len(ANS),
       "n_noans": len(NOANS), "k": K}

# ---------- （1）检索
etok = AutoTokenizer.from_pretrained(EMB)
emb = AutoModel.from_pretrained(EMB, torch_dtype=torch.float16).to(dev).eval()


@torch.no_grad()
def encode(texts, bs=64):
    vs = []
    for i in range(0, len(texts), bs):
        b = etok(texts[i:i + bs], padding=True, truncation=True, max_length=512, return_tensors="pt").to(dev)
        h = emb(**b).last_hidden_state[:, 0]                      # bge 用 [CLS]
        vs.append(torch.nn.functional.normalize(h, dim=-1).float().cpu().numpy())
    return np.concatenate(vs)


t0 = time.time()
M = encode([c["text"] for c in CH])
out["encode_s"] = time.time() - t0
out["encode_per_chunk_ms"] = out["encode_s"] / len(CH) * 1000


def recall_of(idx, gold):
    got = {c.split("(")[0] for i in idx for c in CH[i]["srcs"]}
    return len([g for g in gold if g in got]) / len(gold)


def emb_rank(query, k=K):
    q = encode([query])[0]
    return list(np.argsort(-(M @ q))[:k])


def hybrid_rank(query, k=K, alpha=0.5):
    a = bm25(query, CH)
    b = M @ encode([query])[0]
    s = alpha * a / max(a.max(), 1e-9) + (1 - alpha) * b / max(b.max(), 1e-9)
    return list(np.argsort(-s)[:k])


for field, tag in (("q", "book"), ("q2", "shop")):
    out[f"{tag}_bm25"] = 100 * float(np.mean([recall_of(retrieve(q[field], CH, K, "bm25"), q["gold"]) for q in ANS]))
    out[f"{tag}_emb"] = 100 * float(np.mean([recall_of(emb_rank(q[field]), q["gold"]) for q in ANS]))
    out[f"{tag}_hybrid"] = 100 * float(np.mean([recall_of(hybrid_rank(q[field]), q["gold"]) for q in ANS]))
    out[f"{tag}_bm25_syn_part"] = 100 * float(np.mean(
        [recall_of(retrieve(q[field], CH, K, "bm25+syn+part"), q["gold"]) for q in ANS]))
out["emb_beats_bm25_shop"] = out["shop_emb"] - out["shop_bm25"]
del emb
torch.cuda.empty_cache()

# ---------- （2）带出处作答
gtok = AutoTokenizer.from_pretrained(GEN)
gen = AutoModelForCausalLM.from_pretrained(GEN, torch_dtype=torch.bfloat16).to(dev).eval()
SYS = ("你是车间质量手册的问答助手。只能根据给出的手册片段回答，并在答案末尾用方括号给出条文号；"
       "片段里没有这件事时，回答“手册里没有规定”，不要猜。")


@torch.no_grad()
def answer(query, idx):
    ctx = "\n".join(f"[{CH[i]['srcs'][0]}] {CH[i]['text']}" for i in idx)
    msg = [{"role": "system", "content": SYS},
           {"role": "user", "content": f"手册片段：\n{ctx}\n\n问题：{query}"}]
    text = gtok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
    ids = gtok(text, return_tensors="pt").to(dev)
    t0 = time.time()
    o = gen.generate(**ids, max_new_tokens=120, do_sample=False)
    dt = time.time() - t0
    new = o[0][ids["input_ids"].shape[1]:]
    return gtok.decode(new, skip_special_tokens=True), ids["input_ids"].shape[1], len(new), dt


_ = answer("热一下", emb_rank("热一下"))                            # 先热跑一次，再开始计时
fact_ok = cite_ok = 0
tok_in = tok_out = secs = 0.0
for q in ANS:
    idx = hybrid_rank(q["q2"])
    text, nin, nout, dt = answer(q["q2"], idx)
    tok_in += nin
    tok_out += nout
    secs += dt
    fact_ok += all(f in text for f in q["facts"])
    cite_ok += any(g in text for g in q["gold"])
refuse = 0
for q in NOANS:
    idx = hybrid_rank(q["q2"])
    text, nin, nout, dt = answer(q["q2"], idx)
    tok_in += nin
    tok_out += nout
    secs += dt
    refuse += ("没有规定" in text or "未规定" in text or "没有提到" in text)
n_all = len(ANS) + len(NOANS)
out["fact_pct"] = 100 * fact_ok / len(ANS)
out["cite_pct"] = 100 * cite_ok / len(ANS)
out["refuse_pct"] = 100 * refuse / len(NOANS)
out["tok_in_avg"] = tok_in / n_all
out["tok_out_avg"] = tok_out / n_all
out["ms_per_q"] = secs / n_all * 1000
out["ms_per_tok"] = secs / max(tok_out, 1) * 1000
json.dump(out, open("out.json", "w"), ensure_ascii=False)
print(out)
