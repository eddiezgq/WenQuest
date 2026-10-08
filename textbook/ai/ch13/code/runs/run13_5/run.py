"""实测：LoRA 与全量微调在同一个开源小模型上的对照（13.5 节）。

用 Qwen2.5-0.5B-Instruct（公开权重）在程序生成的质量手册问答对上做指令微调，两种做法各跑一遍：
全量微调（所有参数都更新）与 LoRA（只训两个低秩矩阵）。记下四件事：
可训练参数量、显存峰值、每步时间、训练后的损失。

要说明的不是"LoRA 更好"，而是**代价差了多少、效果差多少**：参数少两三个数量级、显存省一半以上，
损失却只差一点——所以企业里几十条到几千条数据的微调，先试 LoRA。
注意：这个任务很小（十几条数据、几十步），损失只能看相对高低，不能当作模型能力的度量。
"""
import json
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from manual_data import pairs

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
dev = "cuda"
tok = AutoTokenizer.from_pretrained(MODEL)
DATA = pairs()
out = {"_gpu": torch.cuda.get_device_name(0), "torch": torch.__version__, "model": MODEL,
       "n_pair": len(DATA)}


def batches(bs=2, epochs=6):
    """把问答对拼成“指令 + 回答”的训练样本，只在回答上算损失。"""
    xs = []
    for q, a in DATA:
        msg = tok.apply_chat_template([{"role": "user", "content": q}], tokenize=False,
                                      add_generation_prompt=True)
        ids_q = tok(msg, return_tensors=None)["input_ids"]
        ids_a = tok(a + tok.eos_token, return_tensors=None)["input_ids"]
        ids = ids_q + ids_a
        lab = [-100] * len(ids_q) + ids_a                    # 问题部分不算损失
        xs.append((ids, lab))
    out["max_len"] = max(len(i) for i, _ in xs)
    for _ in range(epochs):
        for i in range(0, len(xs), bs):
            chunk = xs[i:i + bs]
            n = max(len(a) for a, _ in chunk)
            inp = torch.full((len(chunk), n), tok.pad_token_id or 0)
            lab = torch.full((len(chunk), n), -100)
            att = torch.zeros((len(chunk), n), dtype=torch.long)
            for r, (a, b) in enumerate(chunk):
                inp[r, :len(a)] = torch.tensor(a)
                lab[r, :len(b)] = torch.tensor(b)
                att[r, :len(a)] = 1
            yield inp.to(dev), lab.to(dev), att.to(dev)


def train_once(kind: str) -> dict:
    torch.manual_seed(13)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(dev)
    if kind == "lora":
        from peft import LoraConfig, get_peft_model
        cfg = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.0, bias="none", task_type="CAUSAL_LM",
                         target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
        model = get_peft_model(model, cfg)
    model.gradient_checkpointing_disable()
    model.train()
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=2e-4 if kind == "lora" else 1e-5)
    torch.cuda.reset_peak_memory_stats()
    losses, steps = [], 0
    torch.cuda.synchronize()
    t0 = time.time()
    for inp, lab, att in batches():
        loss = model(input_ids=inp, attention_mask=att, labels=lab).loss
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        losses.append(loss.item())
        steps += 1
    torch.cuda.synchronize()
    secs = time.time() - t0
    peak = torch.cuda.max_memory_allocated() / 1e9
    # 训练后在同一批数据上再算一次损失（不更新），作为“学到了多少”的粗指标
    model.eval()
    with torch.no_grad():
        final = sum(model(input_ids=i, attention_mask=a, labels=l).loss.item()
                    for i, l, a in batches(epochs=1))
    n_eval = (len(DATA) + 1) // 2
    r = {"trainable": trainable, "total": total, "trainable_pct": trainable / total * 100,
         "peak_GB": peak, "secs": secs, "steps": steps, "ms_per_step": secs / steps * 1000,
         "loss_first": losses[0], "loss_last": losses[-1], "loss_eval": final / n_eval}
    del model, opt
    torch.cuda.empty_cache()
    return r


for kind in ("lora", "full"):
    r = train_once(kind)
    for k, x in r.items():
        out[f"{kind}_{k}"] = x

out["param_ratio"] = out["full_trainable"] / max(out["lora_trainable"], 1)
out["mem_ratio"] = out["full_peak_GB"] / max(out["lora_peak_GB"], 1e-9)
out["time_ratio"] = out["full_ms_per_step"] / max(out["lora_ms_per_step"], 1e-9)
out["loss_gap"] = out["lora_loss_eval"] - out["full_loss_eval"]
json.dump(out, open("out.json", "w"), ensure_ascii=False)
print(out)
