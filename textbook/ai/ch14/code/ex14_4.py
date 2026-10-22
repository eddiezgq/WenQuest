"""算例 14.4.1—14.4.3：时间这一维带来的冗余与代价（14.4 节）。

（1）相邻两帧有多像：一段 30 帧/秒的视频，相邻帧的相似度高到什么程度，抽帧能省多少。
（2）抽帧抽到什么程度会丢东西：镜头切换的那一帧漏掉了，就看不出"换了个零件"。
（3）词元的账：按 2 帧/秒采样（Qwen2-VL 报告的做法）一段 10 分钟的视频要多少词元，
    与报告给的每视频 16384 词元上限对照；Flamingo 的另一条路——不管多少帧，压成固定的 64 个词元。
"""
import numpy as np

from _ch14 import clip_frames, tokens_of
from bookout import out
from mm_facts import FLAMINGO, INTERNVL15, QWEN2VL

v = {}
FPS = 30
f = clip_frames(n=120, seed=0)                         # 4 秒、120 帧，中间有两次镜头切换
v["fps"], v["n_frames"] = FPS, len(f)
sim = (f[1:] * f[:-1]).sum(1)                          # 相邻帧的余弦相似度
cuts = [40, 85]
keep = np.ones(len(sim), bool)
keep[[c - 1 for c in cuts]] = False
v["sim_mean"] = float(sim[keep].mean())                # 不含切换的那两帧
v["sim_min_normal"] = float(sim[keep].min())
v["sim_at_cut"] = float(sim[[c - 1 for c in cuts]].max())
assert v["sim_mean"] > 0.99 > v["sim_at_cut"], "平稳段相邻帧几乎一样，切换处相似度掉下来"

# ---------- （1）抽帧能省多少，（2）什么时候会漏
rows = []
for every in (1, 2, 5, 10, 30):
    idx = np.arange(0, len(f), every)
    rep = idx[np.clip(np.searchsorted(idx, np.arange(len(f))), 0, len(idx) - 1)]   # 每帧由离它最近的被抽帧代表
    cover = (f * f[rep]).sum(1)
    shot = np.zeros(len(f), int)                       # 每帧属于哪一个镜头
    for c in cuts:
        shot[c:] += 1
    near_cut = shot != shot[rep]                       # 代表它的那一帧跨到了别的镜头去
    rows.append((every, round(FPS / every, 1), len(idx),
                 round(float(cover[~near_cut].mean()), 4), round(float(cover.mean()), 4)))
v["sample_rows"] = rows
v["cover_steady_10"] = rows[3][3]                      # 每 10 帧抽 1 帧，平稳段的帧被代表得多像
v["cover_all_10"] = rows[3][4]                         # 把切换附近的帧也算进来
v["frames_1"], v["frames_10"] = rows[0][2], rows[3][2]
v["save_10"] = v["frames_1"] / v["frames_10"]
assert v["cover_steady_10"] > 0.999 > v["cover_all_10"], "平稳段抽帧几乎不丢东西，丢的全在镜头切换那几帧"
v["cover_loss_10"] = v["cover_steady_10"] - v["cover_all_10"]
v["n_cuts"] = len(cuts)
# 每 10 帧抽 1 帧时，有多少帧被"别的镜头"的帧代表了
idx10 = np.arange(0, len(f), 10)
rep10 = idx10[np.clip(np.searchsorted(idx10, np.arange(len(f))), 0, len(idx10) - 1)]
shot10 = np.zeros(len(f), int)
for c in cuts:
    shot10[c:] += 1
v["cut_frames_10"] = int((shot10 != shot10[rep10]).sum())
v["cut_share_10"] = v["cut_frames_10"] / len(f) * 100

# ---------- （3）词元的账
MIN = 10
v["minutes"] = MIN
v["qwen_fps"] = 2                                       # 报告：视频按 2 帧/秒采样
v["frames_10min"] = MIN * 60 * v["qwen_fps"]
v["tok_per_frame"] = tokens_of(448, QWEN2VL["patch"], merge=QWEN2VL["merge"])   # 一帧 448×448
v["tok_10min"] = v["frames_10min"] * v["tok_per_frame"]
v["qwen_cap"] = QWEN2VL["video_token_cap"]
v["over_cap"] = v["tok_10min"] / v["qwen_cap"]
assert v["tok_10min"] > v["qwen_cap"], "10 分钟的视频按这个采样率远超报告给的每视频词元上限"
v["frames_in_cap"] = v["qwen_cap"] // v["tok_per_frame"]
v["seconds_in_cap"] = v["frames_in_cap"] / v["qwen_fps"]
# Flamingo 的另一条路：不管进来多少特征，重采样成固定 64 个词元
v["flamingo_tokens"] = FLAMINGO["resampler_tokens"]
v["flamingo_fps"] = 1
v["flamingo_10min"] = MIN * 60 * v["flamingo_fps"] * FLAMINGO["resampler_tokens"]
v["flamingo_vs_qwen"] = v["tok_10min"] / v["flamingo_10min"]
v["internvl_tile_tokens"] = INTERNVL15["tokens_per_tile"]
v["coco_cider_0"], v["coco_cider_32"] = FLAMINGO["coco_cider"][0], FLAMINGO["coco_cider"][32]
v["vqa_0"], v["vqa_32"] = FLAMINGO["vqav2_top1"][0], FLAMINGO["vqav2_top1"][32]
out(**v)
