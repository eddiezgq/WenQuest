# GPU 实验 14.1 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 14.1　零样本分类：提示怎么写，差几个点
# 14.1 节说零样本分类就是“把类别写成一句话”。这一句话怎么写，结果能差好几个点。
# 这里用公开权重的 CLIP 类模型，在与第 11 章同一套合成零件图上，把四种提示模板各量一遍。
# %%
import sys; sys.path.insert(0, "..")
import time
import numpy as np
import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
wqgpu.sh(f"{sys.executable} -m pip install -q transformers pillow", timeout=1800)
from transformers import CLIPModel, CLIPProcessor
dev = "cuda"; MODEL = "openai/clip-vit-base-patch32"
print(torch.cuda.get_device_name(0), torch.__version__)

# %% [markdown]
# ## 1. 合成零件图与模型（任务 1）
# 图像用第 11 章的生成器现画：合格面、划痕、压痕、锈斑四类，每类若干张，严重程度有轻有重。
# %%
sys.path.insert(0, "../../../ch11/code")
from _ch11 import KINDS, sample                      # 第 11 章的合成器（无真实照片）
from PIL import Image
imgs, labels = [], []
seed = 0
want = {0: 60, 1: 60, 2: 60, 3: 60}                  # 四类各取 60 张（合格 + 三类缺陷）
got = {k: 0 for k in want}
while any(got[k] < want[k] for k in want):           # 按种子一路抽，直到四类都够
    s_ = sample(seed); seed += 1
    lab = 0 if s_["label"] == "无" else KINDS.index(s_["label"]) + 1
    if got[lab] >= want[lab]:
        continue
    got[lab] += 1
    imgs.append(Image.fromarray((np.stack([s_["image"]] * 3, -1) * 255).astype(np.uint8)))
    labels.append(lab)
labels = np.array(labels)
CLASSES = ["合格的零件表面", "有划痕的零件表面", "有压痕的零件表面", "有锈斑的零件表面"]
EN = ["a clean machined surface", "a scratched surface", "a dented surface", "a rusty surface"]
model = CLIPModel.from_pretrained(MODEL).to(dev).eval()
proc = CLIPProcessor.from_pretrained(MODEL)
print(f"{len(imgs)} 张图，{len(CLASSES)} 类")

# %% [markdown]
# ## 2. 四种提示模板（任务 2）
# 只写类别名 / “一张……的照片” / 车间语境 / 多模板取平均。
# %%
def encode_text(texts):
    with torch.no_grad():
        t = proc(text=texts, return_tensors="pt", padding=True).to(dev)
        z = model.get_text_features(**t)
    return torch.nn.functional.normalize(z, dim=-1)


def encode_images(batch=32):
    out = []
    with torch.no_grad():
        for i in range(0, len(imgs), batch):
            t = proc(images=imgs[i:i + batch], return_tensors="pt").to(dev)
            out.append(torch.nn.functional.normalize(model.get_image_features(**t), dim=-1))
    return torch.cat(out)


ZI = encode_images()
TEMPLATES = {
    "只写类别名": [c for c in EN],
    "一张……的照片": [f"a photo of {c}" for c in EN],
    "车间语境": [f"a close-up industrial inspection photo of {c} on a machined steel part" for c in EN],
}
acc = {}
for name, texts in TEMPLATES.items():
    pred = (ZI @ encode_text(texts).T).argmax(1).cpu().numpy()
    acc[name] = float((pred == labels).mean() * 100)
    print(f"{name}: {acc[name]:.1f}%")
# 多模板取平均：把三套说法的文本嵌入平均起来再归一化
embs = torch.stack([encode_text(t) for t in TEMPLATES.values()]).mean(0)
embs = torch.nn.functional.normalize(embs, dim=-1)
acc["多模板取平均"] = float(((ZI @ embs.T).argmax(1).cpu().numpy() == labels).mean() * 100)
print(f"多模板取平均: {acc['多模板取平均']:.1f}%")
gap = max(acc.values()) - min(acc.values())
print(f"最好与最差相差 {gap:.1f} 个百分点")

# %% [markdown]
# ## 3. 相似度分布（任务 3）
# 配对的与不配对的分开看，与书中图 14.1.1(b) 对照：真模型上这两堆分得开不开？
# %%
ZT = encode_text(TEMPLATES["车间语境"])
S = (ZI @ ZT.T).cpu().numpy()
pair = np.array([S[i, labels[i]] for i in range(len(labels))])
other = np.array([S[i, j] for i in range(len(labels)) for j in range(4) if j != labels[i]])
print(f"配对 {pair.mean():.3f} ± {pair.std():.3f}；不配对 {other.mean():.3f} ± {other.std():.3f}；相差 {pair.mean() - other.mean():.3f}")
print(f"模型学到的温度（logit_scale）：{float(model.logit_scale.exp()):.1f}，即温度 {1 / float(model.logit_scale.exp()):.4f}")

# %% [markdown]
# ## 4. 编码代价（任务 4）
# %%
rows = []
for b in (1, 16, 64):
    with torch.no_grad():                            # 先热一次
        proc(images=imgs[:b], return_tensors="pt").to(dev)
    torch.cuda.synchronize(); t0 = time.time()
    with torch.no_grad():
        for i in range(0, 128, b):
            t = proc(images=imgs[i:i + b], return_tensors="pt").to(dev)
            model.get_image_features(**t)
    torch.cuda.synchronize()
    ms = (time.time() - t0) / 128 * 1000
    rows.append((b, ms, ms * 10000 / 1000 / 60))
    print(f"批 {b}: 每张 {ms:.1f} ms，一万张 {rows[-1][2]:.1f} 分钟")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(
    acc_bare=acc["只写类别名"], acc_photo=acc["一张……的照片"], acc_domain=acc["车间语境"],
    acc_ensemble=acc["多模板取平均"], gap_pp=gap, ms_per_img=rows[-1][1])
