"""11.1、11.2 节的示意图（数据同程序 11.1.1）。

图 11.1.1：（a）各代网络的运算量与 ImageNet top-1 正确率：横轴是处理一张 224×224 图的运算量（对数），
纵轴是公开报告的正确率，点的大小表示参数量。从 AlexNet 到 ResNet，运算量涨了三倍多而正确率涨了近二十个百分点；
VGG 用十倍于 AlexNet 的运算量只换来十几个百分点，ResNet 以更少的参数超过了它。
（b）同样的网络用在每秒 60 帧的检测工位上，各要占 A10 半精度峰值的百分之几。
"""
from _ch11 import MODELS, TOP1
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
from gpus import GPUS

A10_FP16, FPS = GPUS["a10"]["fp16t"], 60
V = {}
for _k, (_f, _p) in MODELS.items():                      # 与算例 11.1.2 用的是同一份结构（_ch11.MODELS）
    V[_k + "_GF"], V[_k + "_M"] = _f / 1e9, _p / 1e6
    V[_k + "_top1"] = TOP1[_k]
    V[_k + "_util"] = _f * FPS / A10_FP16 * 100

NAMES = {"alex": ("AlexNet", 2012), "vgg": ("VGG-16", 2014), "res": ("ResNet-50", 2015), "vit": ("ViT-B/16", 2020)}
fig, (a, b) = plt.subplots(1, 2, figsize=(12.2, 4.3))
cols = {"alex": C["z"], "vgg": C["accent"], "res": C["x"], "vit": C["y"]}
for k, (nm, yr) in NAMES.items():
    a.scatter(V[k + "_GF"], V[k + "_top1"], s=V[k + "_M"] * 3.2, color=cols[k], alpha=0.55, edgecolors="none")
    a.annotate(f"{nm} ({yr})", (V[k + "_GF"], V[k + "_top1"]), textcoords="offset points",
               xytext=(8, -12), fontsize=8.5, color=cols[k])
a.set_xscale("log")
a.set_xlabel(T("一张图的运算量（GFLOP，对数）", "FLOP per image (GFLOP, log)"))
a.set_ylabel(T("ImageNet top-1 正确率（%）", "ImageNet top-1 accuracy (%)"))
a.set_title(T("(a) 运算量、参数量与正确率（点的大小为参数量）", "(a) Compute, parameters and accuracy"), fontsize=10)
a.set_xlim(1.2, 90)
a.set_ylim(50, 84)
a.grid(alpha=0.25, lw=0.5)

ks = list(NAMES)
b.bar(range(len(ks)), [V[k + "_util"] for k in ks], color=[cols[k] for k in ks], alpha=0.65, width=0.55)
for i, k in enumerate(ks):
    b.text(i, V[k + "_util"] + 0.04, f"{V[k + '_util']:.2f}%", ha="center", fontsize=8.5, color=C["ink"])
b.set_xticks(range(len(ks)))
b.set_xticklabels([NAMES[k][0] for k in ks], fontsize=9)
b.set_ylabel(T("占 A10 半精度峰值的比例（%）", "share of A10 FP16 peak (%)"))
b.set_title(T("(b) 每秒 60 帧时要多少算力", "(b) Compute needed at 60 frames per second"), fontsize=10)
b.set_ylim(0, max(V[k + "_util"] for k in ks) * 1.25)
b.grid(axis="y", alpha=0.25, lw=0.5)
fig.tight_layout()
figure(fig, "fig11_1_1")
