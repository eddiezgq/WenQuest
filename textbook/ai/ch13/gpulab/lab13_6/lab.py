# GPU 实验 13.6 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 13.6　搭一个带出处的手册问答系统
# 书里的“向量检索”用的是没有语义的哈希向量，所以口语问法上不如词频检索。这里换成真正的句向量模型，
# 看这一课会不会翻过来；再让一个开源小模型按取回的片子作答、给出条文号，并在手册没规定时说“没有规定”。
# %%
import sys; sys.path.insert(0, "..")
import json, time
import numpy as np
import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
wqgpu.sh(f"{sys.executable} -m pip install -q transformers accelerate", timeout=1800)
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer
dev = "cuda"; EMB = "BAAI/bge-small-zh-v1.5"; GEN = "Qwen/Qwen2.5-0.5B-Instruct"
print(torch.cuda.get_device_name(0), torch.__version__)
# %% [markdown]
# ## 1. 手册、问题与句向量模型（任务 1）
# 手册与问答对由书中的 `_ch13.py` 生成（几百条条文、几十页，其中有上百条字面几乎一样、只是零件号不同），
# 每个问题有两种问法：手册原词与工人口语。
# %%
sys.path.insert(0, "../../code")                 # 用书中同一套手册与问题，保证与算例可比
from _ch13 import bm25, chunks, manual, questions, retrieve
MAN = manual(); QS = questions()
ANS = [q for q in QS if q["answerable"]]; NOANS = [q for q in QS if not q["answerable"]]
CH = chunks(MAN, 300, 60, skip_obsolete=True); K = 5
print(f"条文 {len(MAN)}，切片 {len(CH)}，可答问题 {len(ANS)}，手册里没有的 {len(NOANS)}")
etok = AutoTokenizer.from_pretrained(EMB)
emb = AutoModel.from_pretrained(EMB, torch_dtype=torch.float16).to(dev).eval()

@torch.no_grad()
def encode(texts, bs=64):
    vs = []
    for i in range(0, len(texts), bs):
        b = etok(texts[i:i+bs], padding=True, truncation=True, max_length=512, return_tensors="pt").to(dev)
        h = emb(**b).last_hidden_state[:, 0]
        vs.append(torch.nn.functional.normalize(h, dim=-1).float().cpu().numpy())
    return np.concatenate(vs)

t0 = time.time(); M = encode([c["text"] for c in CH]); enc_s = time.time() - t0
print(f"把 {len(CH)} 片编码成向量用了 {enc_s:.1f} 秒（{enc_s/len(CH)*1000:.1f} ms/片）")
# %% [markdown]
# ## 2. 三种检索 × 两种问法（任务 2）
# 词频检索（BM25）、句向量、两者混合。重点看**口语问法**那一行。
# %%
def recall_of(idx, gold):
    got = {c.split("(")[0] for i in idx for c in CH[i]["srcs"]}
    return len([g for g in gold if g in got]) / len(gold)

def emb_rank(q, k=K):
    return list(np.argsort(-(M @ encode([q])[0]))[:k])

def hybrid_rank(q, k=K, alpha=0.5):
    a = bm25(q, CH); b = M @ encode([q])[0]
    s = alpha * a / max(a.max(), 1e-9) + (1 - alpha) * b / max(b.max(), 1e-9)
    return list(np.argsort(-s)[:k])

R = {}
for field, tag in (("q", "手册原词"), ("q2", "工人口语")):
    R[tag] = {
        "BM25": 100*np.mean([recall_of(retrieve(q[field], CH, K, "bm25"), q["gold"]) for q in ANS]),
        "句向量": 100*np.mean([recall_of(emb_rank(q[field]), q["gold"]) for q in ANS]),
        "混合": 100*np.mean([recall_of(hybrid_rank(q[field]), q["gold"]) for q in ANS]),
        "BM25+同义词+零件号": 100*np.mean([recall_of(retrieve(q[field], CH, K, "bm25+syn+part"), q["gold"]) for q in ANS]),
    }
    print(tag + "：" + "　".join(f"{k} {v:.0f}%" for k, v in R[tag].items()))
del emb; torch.cuda.empty_cache()
# %% [markdown]
# ## 3. 带出处作答（任务 3）
# 提示里写明三件事：只能按片子回答、末尾给条文号、片子里没有就说“手册里没有规定”。
# %%
gtok = AutoTokenizer.from_pretrained(GEN)
gen = AutoModelForCausalLM.from_pretrained(GEN, torch_dtype=torch.bfloat16).to(dev).eval()
SYS_STRICT = ("你是车间质量手册的问答助手。只能根据给出的手册片段回答，并在答案末尾用方括号给出条文号；"
              "片段里没有这件事时，回答“手册里没有规定”，不要猜。")
SYS_LOOSE = "你是车间质量手册的问答助手。根据给出的手册片段回答问题。"

@torch.no_grad()
def answer(q, idx, system):
    ctx = "\n".join(f"[{CH[i]['srcs'][0]}] {CH[i]['text']}" for i in idx)
    text = gtok.apply_chat_template([{"role": "system", "content": system},
                                     {"role": "user", "content": f"手册片段：\n{ctx}\n\n问题：{q}"}],
                                    tokenize=False, add_generation_prompt=True)
    ids = gtok(text, return_tensors="pt").to(dev)
    t0 = time.time(); o = gen.generate(**ids, max_new_tokens=120, do_sample=False); dt = time.time() - t0
    new = o[0][ids["input_ids"].shape[1]:]
    return gtok.decode(new, skip_special_tokens=True), ids["input_ids"].shape[1], len(new), dt

_ = answer("热一下", emb_rank("热一下"), SYS_STRICT)       # 先热跑一次再计时

def evaluate(system):
    fact = cite = ref = 0; tin = tout = secs = 0.0
    for q in ANS:
        idx = hybrid_rank(q["q2"]); t, a, b, dt = answer(q["q2"], idx, system)
        tin += a; tout += b; secs += dt
        fact += all(f in t for f in q["facts"]); cite += any(g in t for g in q["gold"])
    for q in NOANS:
        idx = hybrid_rank(q["q2"]); t, a, b, dt = answer(q["q2"], idx, system)
        tin += a; tout += b; secs += dt
        ref += ("没有规定" in t or "未规定" in t or "没有提到" in t)
    n = len(ANS) + len(NOANS)
    return {"fact_pct": 100*fact/len(ANS), "cite_pct": 100*cite/len(ANS),
            "refuse_pct": 100*ref/len(NOANS), "tok_in": tin/n, "tok_out": tout/n, "ms": secs/n*1000}

strict = evaluate(SYS_STRICT)
print(f"要求拒答：事实 {strict['fact_pct']:.0f}%　引用 {strict['cite_pct']:.0f}%　"
      f"该拒的拒住 {strict['refuse_pct']:.0f}%　每问 {strict['tok_in']:.0f} 词元、{strict['ms']:.0f} ms")
# %% [markdown]
# ## 4. 去掉“没有就说没有规定”（任务 4）
# 同一套检索、同一个模型，只把提示里那一句去掉。拒答率会怎样？这说明拒答是谁负责的。
# %%
loose = evaluate(SYS_LOOSE)
print(f"不要求拒答：事实 {loose['fact_pct']:.0f}%　引用 {loose['cite_pct']:.0f}%　"
      f"该拒的拒住 {loose['refuse_pct']:.0f}%")
print(f"拒答率相差 {strict['refuse_pct'] - loose['refuse_pct']:+.0f} 个百分点")
# %% [markdown]
# ## 5. 回传结果
# %%
wqgpu.submit(shop_bm25=R["工人口语"]["BM25"], shop_emb=R["工人口语"]["句向量"],
             shop_hybrid=R["工人口语"]["混合"], book_bm25=R["手册原词"]["BM25"],
             book_emb=R["手册原词"]["句向量"], fact_pct=strict["fact_pct"],
             cite_pct=strict["cite_pct"], refuse_pct=strict["refuse_pct"],
             refuse_pct_loose=loose["refuse_pct"], tok_in_avg=strict["tok_in"],
             ms_per_q=strict["ms"], encode_per_chunk_ms=enc_s / len(CH) * 1000)
print(json.dumps({"strict": strict, "loose": loose}, ensure_ascii=False, indent=1))
