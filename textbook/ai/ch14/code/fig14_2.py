"""14.2、14.4 节的示意图。

图 14.2.1：（a）分辨率一提高，视觉词元数按平方涨、注意力那两项按四次方涨；横线标出几个
公开模型的词元数（LLaVA-1.5 折算 576、InternVL 1.5 训练上限 3328 与测试上限 10496）。
（b）一段视频按每 n 帧抽一帧：平稳段几乎不丢东西，丢的全在镜头切换的那几帧。
"""
import numpy as np

from _ch14 import attn_cost, clip_frames, tokens_of
from bookout import COLORS, T, figure, style
from mm_facts import INTERNVL15, LLAVA15

plt = style()
C = COLORS

fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 4.0))

res = np.array([112, 224, 336, 448, 672, 896, 1344])
ntok = np.array([tokens_of(int(r // 14) * 14, 14) for r in res])
cost = np.array([attn_cost(int(n), 4096, 32) for n in ntok])
base = res.tolist().index(224)                                   # 一律以 224 为 1 倍
a.loglog(res, ntok / ntok[base], "o-", color=C["z"], lw=1.8, ms=5,
         label=T("视觉词元数（相对 224 的倍数）", "visual tokens (relative to 224)"))
a.loglog(res, cost / cost[base], "s--", color=C["x"], lw=1.8, ms=5,
         label=T("注意力两项的乘加（倍数）", "attention MACs (relative)"))
for val, name in ((tokens_of(LLAVA15["res"], LLAVA15["patch"]), T("LLaVA-1.5：576（按公式折算）", "LLaVA-1.5: 576 (derived)")),
                  (INTERNVL15["tokens_train"][1], T("InternVL 1.5 训练上限 3328", "InternVL 1.5 train cap 3328")),
                  (INTERNVL15["tokens_test_max"], T("InternVL 1.5 测试上限 10496", "InternVL 1.5 test cap 10496"))):
    a.axhline(val / ntok[base], color=C["muted"], lw=1.0, ls=":")
    a.text(114, val / ntok[base] * 1.12, name, fontsize=7.5, color=C["muted"])
a.set_xlabel(T("输入分辨率（像素，方图）", "input resolution (px, square)"))
a.set_ylabel(T("相对 224×224 的倍数", "multiple of the 224x224 case"))
a.set_title(T("(a) 分辨率翻一倍：词元 ×4，注意力 ×16", "(a) Double the resolution: 4x tokens, 16x attention"), fontsize=10)
a.legend(fontsize=8, loc="upper left")
a.grid(alpha=0.25, lw=0.5, which="both")

f = clip_frames(n=120, seed=0)
cuts = [40, 85]
shot = np.zeros(len(f), int)
for c in cuts:
    shot[c:] += 1
every_list = np.arange(1, 31)
steady, overall = [], []
for every in every_list:
    sv, ov = [], []
    for off in range(every):                                     # 对所有起始相位取平均，免得曲线随相位抖动
        idx = np.arange(off, len(f), every)
        if len(idx) == 0:
            continue
        rep = idx[np.clip(np.searchsorted(idx, np.arange(len(f))), 0, len(idx) - 1)]
        cov = (f * f[rep]).sum(1)
        cross = shot != shot[rep]
        sv.append(cov[~cross].mean())
        ov.append(cov.mean())
    steady.append(np.mean(sv))
    overall.append(np.mean(ov))
b.plot(every_list, steady, color=C["z"], lw=1.8, label=T("只看平稳段", "within a shot"))
b.plot(every_list, overall, color=C["x"], lw=1.8, label=T("全部帧（含镜头切换）", "all frames (cuts included)"))
b.axvline(10, color=C["muted"], lw=1.0, ls="--")
b.text(10.5, 0.80, T("每 10 帧抽 1 帧", "1 in 10"), fontsize=8, color=C["muted"])
b.set_ylim(0.6, 1.005)
b.set_xlabel(T("每几帧抽一帧", "keep 1 frame out of n"))
b.set_ylabel(T("被代表的帧与代表帧的相似度", "similarity to its keyframe"))
b.set_title(T("(b) 抽帧丢掉的，全在镜头切换处", "(b) What sampling loses is all at the cuts"), fontsize=10)
b.legend(fontsize=8, loc="lower left")
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig14_2_1")
