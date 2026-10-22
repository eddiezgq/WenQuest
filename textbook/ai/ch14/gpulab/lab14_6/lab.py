# GPU 实验 14.6 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 14.6　让视觉语言模型读检验报告
# 14.6 节的那条线：切片 → 抽字段 → 校验 → 拒答。这里用公开权重的开源视觉语言模型真跑一遍。
# 报告图片由本笔记本现画：一半是“扫描件”（正、清楚），一半是“手机照片”（斜、暗、有折痕、带手写批注）。
# %%
import sys; sys.path.insert(0, "..")
import json, re, time
import numpy as np
import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
wqgpu.sh(f"{sys.executable} -m pip install -q transformers accelerate pillow qwen-vl-utils", timeout=1800)
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
dev = "cuda"; MODEL = "Qwen/Qwen2-VL-2B-Instruct"
print(torch.cuda.get_device_name(0), torch.__version__)

# %% [markdown]
# ## 1. 画出检验报告（任务 1）
# 字段取自书中的 `_ch14.reports()`，保证与算例 14.6.1 用的是同一批记录。
# %%
sys.path.insert(0, "../../code")
from _ch14 import FIELDS, reports
from PIL import Image, ImageDraw, ImageFont

N = 60
recs, qual = reports(N, seed=0)


def render(rec, phone: bool, seed: int):
    """画一份报告：表头 + 七个字段 + 印章；phone=True 时加倾斜、变暗、折痕与手写批注。"""
    g = np.random.default_rng(seed)
    im = Image.new("RGB", (1000, 1400), "white")
    d = ImageDraw.Draw(im)
    f = ImageFont.load_default(size=28)
    d.text((60, 50), "数字工厂  零件检验报告", font=ImageFont.load_default(size=36), fill="black")
    d.line((60, 110, 940, 110), fill="black", width=3)
    for i, k in enumerate(FIELDS):
        y = 170 + i * 110
        d.text((80, y), f"{k}", font=f, fill="black")
        d.text((420, y), f"{rec[k]}", font=f, fill="black")
        d.line((60, y + 80, 940, y + 80), fill=(150, 150, 150), width=1)
    d.ellipse((700, 1150, 920, 1340), outline=(190, 40, 40), width=5)
    d.text((750, 1230), "质检专用", font=f, fill=(190, 40, 40))
    if phone:
        im = im.rotate(float(g.uniform(-6, 6)), expand=False, fillcolor="white")
        a = np.asarray(im).astype(np.float32)
        a *= float(g.uniform(0.55, 0.8))                       # 光线暗
        yy = int(g.integers(300, 1100))
        a[yy:yy + 6] *= 0.6                                    # 折痕
        a += g.normal(0, 6, a.shape)                           # 手机噪声
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        d2 = ImageDraw.Draw(im)
        d2.text((520, 1180), "已复检 王", font=ImageFont.load_default(size=30), fill=(30, 30, 160))
    return im


phone_flag = qual < 0.55
images = [render(r, bool(p), i) for i, (r, p) in enumerate(zip(recs, phone_flag))]
print(f"{N} 份报告：扫描件 {int((~phone_flag).sum())}，手机照片 {int(phone_flag.sum())}")

model = Qwen2VLForConditionalGeneration.from_pretrained(MODEL, torch_dtype=torch.bfloat16, device_map="auto").eval()
proc = AutoProcessor.from_pretrained(MODEL)

# %% [markdown]
# ## 2. 抽七个字段（任务 2）
# 提示里写清字段与格式，并要求模型对每个字段同时给出 0—1 的把握；读不清就把该字段写成 null。
# %%
PROMPT = ("从这张检验报告里抽出七个字段，按 JSON 输出，键为："
          + "、".join(FIELDS) +
          "。每个字段再给一个 0—1 的把握，键名为“字段_把握”。读不清的字段写 null、把握写 0。只输出 JSON。")


def ask(img, max_pixels=None):
    msg = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": PROMPT}]}]
    text = proc.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
    kw = {"max_pixels": max_pixels} if max_pixels else {}
    inp = proc(text=[text], images=[img], return_tensors="pt", **kw).to(dev)
    n_tok = int(inp["input_ids"].shape[1])
    with torch.no_grad():
        out = model.generate(**inp, max_new_tokens=400, do_sample=False)
    ans = proc.batch_decode(out[:, inp["input_ids"].shape[1]:], skip_special_tokens=True)[0]
    m = re.search(r"\{.*\}", ans, re.S)
    try:
        return json.loads(m.group(0)) if m else {}, n_tok
    except json.JSONDecodeError:
        return {}, n_tok


def same(a, b):
    if a is None:
        return False
    sa, sb = str(a).strip(), str(b).strip()
    try:
        return abs(float(sa) - float(sb)) < 1e-6
    except ValueError:
        return sa == sb


t0 = time.time()
got, conf, toks = [], [], []
for img in images:
    j, n_tok = ask(img)
    got.append(j); toks.append(n_tok)
ms_per_page = (time.time() - t0) / len(images) * 1000
correct = np.array([[same(g.get(k), r[k]) for k in FIELDS] for g, r in zip(got, recs)])
confid = np.array([[float(g.get(f"{k}_把握", 0) or 0) for k in FIELDS] for g in got])
field_acc = float(correct.mean() * 100)
all_ok = float(correct.all(1).mean() * 100)
acc_scan = float(correct[~phone_flag].all(1).mean() * 100)
acc_phone = float(correct[phone_flag].all(1).mean() * 100)
print(f"字段准确率 {field_acc:.1f}%，整份全对 {all_ok:.1f}%（扫描件 {acc_scan:.1f}%，手机照片 {acc_phone:.1f}%）")
print(f"每页视觉词元约 {int(np.mean(toks))}，每页 {ms_per_page:.0f} ms")

# %% [markdown]
# ## 3. 拒答阈值（任务 3）
# 一份报告的把握取七个字段把握之积；代价按“错一条 20 分钟、复核一条 3 分钟”算。
# %%
rep_conf = confid.prod(1)
rep_ok = correct.all(1)
C_ERR, C_REVIEW = 20.0, 3.0
ths = np.linspace(0, 0.999, 200)
cost = np.array([((rep_conf >= t) & ~rep_ok).sum() * C_ERR + (rep_conf < t).sum() * C_REVIEW for t in ths])
best = int(cost.argmin())
take = rep_conf >= ths[best]
cov_best = float(take.mean() * 100)
acc_best = float(rep_ok[take].mean() * 100) if take.any() else float("nan")
print(f"最优阈值 {ths[best]:.3f}：自动放行 {cov_best:.1f}%，其中全对 {acc_best:.1f}%，转人工 {int((~take).sum())} 份")
print(f"总工时 {cost[best] / 60:.1f} 小时；全自动 {cost[0] / 60:.1f} 小时；全人工 {N * C_REVIEW / 60:.1f} 小时")

# %% [markdown]
# ## 4. 分辨率减半（任务 4）
# %%
half = [ask(img, max_pixels=256 * 28 * 28) for img in images[:20]]
corr_h = np.array([[same(j.get(k), r[k]) for k in FIELDS] for (j, _), r in zip(half, recs[:20])])
tok_h = int(np.mean([n for _, n in half]))
print(f"分辨率减半：字段准确率 {corr_h.mean() * 100:.1f}%（原来 {correct[:20].mean() * 100:.1f}%），"
      f"每页词元约 {tok_h}（原来 {int(np.mean(toks[:20]))}）")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(field_acc=field_acc, all_ok=all_ok, acc_scan=acc_scan, acc_phone=acc_phone,
             cov_best=cov_best, acc_best=acc_best, tok_per_page=int(np.mean(toks)),
             ms_per_page=ms_per_page)
