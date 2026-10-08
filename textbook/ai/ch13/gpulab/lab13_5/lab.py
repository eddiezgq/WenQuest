# GPU 实验 13.5 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 13.5　用 LoRA 微调一个开源小模型
# 同一个模型、同一批数据、同样的批大小，训两遍：全量微调与 LoRA。要记的是四个数——
# 可训练参数、显存峰值、每步时间、训练后的损失。
# %%
import sys; sys.path.insert(0, "..")
import json, time
import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
wqgpu.sh(f"{sys.executable} -m pip install -q transformers peft accelerate", timeout=1800)
from transformers import AutoModelForCausalLM, AutoTokenizer
dev = "cuda"; MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
print(torch.cuda.get_device_name(0), torch.__version__)
# %% [markdown]
# ## 1. 数据与模型（任务 1）
# 问答对按模板生成（与书中 `_ch13.py` 同一套手册）：十条通用条文加每个零件的同轴度与硬度。
# 仓库里不放企业真实手册，机器上也不下载——现生成。
# %%
PARTS = [("SH-301 输出轴", 0.02, (28, 32)), ("SH-302 输入轴", 0.03, (30, 35)),
         ("GH-12 主动齿轮", 0.05, (45, 50)), ("ZJ-108 中间轴", 0.04, (33, 38)),
         ("CD-115 传动轴", 0.06, (26, 31))]
DATA = [
    ("量具多久校准一次？", "卡尺、千分尺与量规每 6 个月校准一次，校准记录由计量室保存 3 年（QM-3.1）。"),
    ("终检量具的精度要求？", "终检所用量具的测量不确定度不得大于被测公差带的十分之一（QM-3.2）。"),
    ("首件没判合格能继续加工吗？", "不能。每批首件必须全尺寸检验并由检验员签字（QM-4.1）。"),
    ("不合格品多久要填评审单？", "立即挂红牌移入隔离区，24 小时内填写不合格品评审单（QM-5.1）。"),
    ("超差了谁批？", "不影响装配功能的由质量工程师提意见、质量经理批准；影响功能的一律报废（QM-5.2）。"),
    ("同一零件最多返工几次？", "不得超过 2 次，返工后须按原检验项目重新全检（QM-5.3）。"),
    ("检验记录保存几年？", "检验记录与评审单保存 5 年，电子记录每 7 天备份一次（QM-6.1）。"),
    ("检验员授权多久过期？", "授权有效期 3 年，到期重新考核（QM-7.1）。"),
    ("让步接收单谁签字？", "由质量经理签字；报废单由厂长签字，金额超过 5000 元的另报总经理（QM-7.2）。"),
]
for name, tol, hrc in PARTS:
    DATA.append((f"{name}的同轴度公差是多少？", f"{name}两端轴颈对公共基准的同轴度公差为 {tol} mm，超差按 QM-5.2 处理。"))
    DATA.append((f"{name}调质后的硬度范围？", f"{name}调质后表面硬度应为 {hrc[0]}—{hrc[1]} HRC，每炉抽检 3 件。"))
tok = AutoTokenizer.from_pretrained(MODEL)
print(f"{len(DATA)} 条问答；最长回答 {max(len(tok(a)['input_ids']) for _, a in DATA)} 个词元")

def batches(bs=2, epochs=6):
    xs = []
    for q, a in DATA:
        msg = tok.apply_chat_template([{"role": "user", "content": q}], tokenize=False, add_generation_prompt=True)
        iq = tok(msg)["input_ids"]; ia = tok(a + tok.eos_token)["input_ids"]
        xs.append((iq + ia, [-100] * len(iq) + ia))
    for _ in range(epochs):
        for i in range(0, len(xs), bs):
            ck = xs[i:i+bs]; n = max(len(a) for a, _ in ck)
            inp = torch.full((len(ck), n), tok.pad_token_id or 0)
            lab = torch.full((len(ck), n), -100); att = torch.zeros((len(ck), n), dtype=torch.long)
            for r, (a, b) in enumerate(ck):
                inp[r, :len(a)] = torch.tensor(a); lab[r, :len(b)] = torch.tensor(b); att[r, :len(a)] = 1
            yield inp.to(dev), lab.to(dev), att.to(dev)
# %% [markdown]
# ## 2. LoRA 微调（任务 2）
# 只在注意力的四个投影上加低秩矩阵（r=8）。看“可训练参数占总参数的百分之几”。
# %%
def train(kind, r=8, lr=None):
    torch.manual_seed(13)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(dev)
    if kind == "lora":
        from peft import LoraConfig, get_peft_model
        model = get_peft_model(model, LoraConfig(r=r, lora_alpha=2*r, lora_dropout=0.0, bias="none",
                               task_type="CAUSAL_LM", target_modules=["q_proj","k_proj","v_proj","o_proj"]))
    model.train()
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                            lr=lr or (2e-4 if kind == "lora" else 1e-5))
    torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time(); steps = 0
    for inp, lab, att in batches():
        loss = model(input_ids=inp, attention_mask=att, labels=lab).loss
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step(); steps += 1
    torch.cuda.synchronize(); secs = time.time() - t0
    peak = torch.cuda.max_memory_allocated() / 1e9
    model.eval()
    with torch.no_grad():
        tot = nb = 0.0
        for inp, lab, att in batches(epochs=1):
            tot += model(input_ids=inp, attention_mask=att, labels=lab).loss.item(); nb += 1
    return model, {"trainable": trainable, "total": total, "trainable_pct": 100*trainable/total,
                   "peak_GB": peak, "secs": secs, "steps": steps, "ms_per_step": secs/steps*1000,
                   "loss_eval": tot/nb}

lora_model, L = train("lora")
print(f"LoRA：可训练 {L['trainable']:,}（{L['trainable_pct']:.2f}%）　显存峰值 {L['peak_GB']:.2f} GB　"
      f"{L['ms_per_step']:.0f} ms/步　训练后损失 {L['loss_eval']:.3f}")
# %% [markdown]
# ## 3. 全量微调（任务 3）
# 同样的数据、同样的批大小。注意显存峰值与每步时间。
# %%
full_model, Fu = train("full")
del full_model; torch.cuda.empty_cache()
print(f"全量：可训练 {Fu['trainable']:,}（{Fu['trainable_pct']:.0f}%）　显存峰值 {Fu['peak_GB']:.2f} GB　"
      f"{Fu['ms_per_step']:.0f} ms/步　训练后损失 {Fu['loss_eval']:.3f}")
print(f"可训练参数相差 {Fu['trainable']/L['trainable']:.0f} 倍，显存相差 {Fu['peak_GB']/L['peak_GB']:.2f} 倍，"
      f"损失相差 {L['loss_eval']-Fu['loss_eval']:+.3f}")
# %% [markdown]
# ## 4. 问几个问题（任务 4）
# 微调前后各问三个问题。看它有没有学会本厂的说法——以及有没有把别的事情答错（灾难性遗忘）。
# %%
@torch.no_grad()
def ask(model, q, n=80):
    msg = tok.apply_chat_template([{"role": "user", "content": q}], tokenize=False, add_generation_prompt=True)
    ids = tok(msg, return_tensors="pt").to(dev)
    o = model.generate(**ids, max_new_tokens=n, do_sample=False)
    return tok.decode(o[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()

base = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(dev).eval()
QS = ["SH-301 输出轴的同轴度公差是多少？", "让步接收单谁签字？", "检验记录保存几年？", "一公里等于多少米？"]
for q in QS:
    print("问：", q)
    print("  微调前：", ask(base, q)[:120].replace("\n", " "))
    print("  LoRA后：", ask(lora_model, q)[:120].replace("\n", " "))
del base; torch.cuda.empty_cache()
# %% [markdown]
# ## 5. 回传结果
# %%
wqgpu.submit(lora_trainable_pct=L["trainable_pct"], lora_peak_GB=L["peak_GB"],
             full_peak_GB=Fu["peak_GB"], lora_loss_eval=L["loss_eval"],
             full_loss_eval=Fu["loss_eval"], param_ratio=Fu["trainable"] / L["trainable"],
             lora_ms_per_step=L["ms_per_step"], full_ms_per_step=Fu["ms_per_step"], n_pair=len(DATA))
print(json.dumps({"lora": L, "full": Fu}, ensure_ascii=False, indent=1))
