"""算例 16.5.1—16.5.3：视频生成的两道坎（16.5 节）。

（1）词元账：一分钟 1080p 的视频在潜空间里有多少词元，自注意力的代价比"4 秒 256×256"
     那一档高多少。这也是为什么视频模型不能在像素上做。
（2）时间一致性是拿多样性换的：每一帧都从上一帧小幅改起，画面就连贯，可整段片子只在
     分布的一小块里转；强度一调大，每帧都像真的，画面却开始跳。
（3）公开的数字：报告与论文给了什么、没给什么。
"""
import numpy as np

from _ch16 import diffusion_fit, ks, mix_sample, temporal_chain, video_tokens
from bookout import out
from gen_facts import SORA, SVD

v = {}

# ---------- （1）词元账
SEC = SORA["max_seconds"]
FPS = 24
frames, per, total = video_tokens(SEC, FPS, SORA["res_wide"])
v["seconds"], v["fps"] = SEC, FPS
v["res_w"], v["res_h"] = SORA["res_wide"]
v["frames"] = frames
v["tok_per_frame"] = per
v["tok_total_w"] = total / 1e4
old_sec, old_res = SORA["old_setting"]
f_old, per_old, tot_old = video_tokens(old_sec, FPS, (old_res, old_res))
v["old_sec"], v["old_res"] = old_sec, old_res
v["tok_old"] = tot_old
v["tok_ratio"] = total / tot_old
v["attn_ratio"] = (total / tot_old) ** 2                  # 折算：自注意力按词元数的平方
assert v["tok_ratio"] > 400, "一分钟 1080p 的词元数比那一档高两个数量级以上"
# 不压缩直接在像素上做会是多少
v["px_values_y"] = SORA["res_wide"][0] * SORA["res_wide"][1] * 3 * frames / 1e8
v["img_res"] = SORA["image_res"]

# ---------- （2）连贯与多样的取舍
train = mix_sample(8000, 0)
model = diffusion_fit(train)
N_FRAMES = 600
indep = mix_sample(N_FRAMES, 77)
v["n_frames_sim"] = N_FRAMES
v["jump_indep"] = float(np.mean(np.abs(np.diff(indep))))
v["ks_indep"] = ks(indep)
v["chain_rows"] = []
for t0 in (30, 80, 200, 500):
    f = temporal_chain(model, N_FRAMES, t0, seed=0)
    v["chain_rows"].append((t0, round(float(np.mean(np.abs(np.diff(f)))), 3),
                            round(float(np.corrcoef(f[:-1], f[1:])[0, 1]), 3),
                            round(ks(f), 3)))
for t0, jp, co, k in v["chain_rows"]:
    v[f"chain_t{t0}_jump"], v[f"chain_t{t0}_corr"], v[f"chain_t{t0}_ks"] = jp, co, k
v["jump_t30"], v["ks_t30"] = v["chain_rows"][0][1], v["chain_rows"][0][3]
v["jump_t500"], v["ks_t500"] = v["chain_rows"][-1][1], v["chain_rows"][-1][3]
assert v["jump_t30"] < 0.2 * v["jump_indep"], "强度小 → 相邻帧挨得很近，画面连贯"
assert v["ks_t30"] > 4 * v["ks_t500"], "可是整段片子覆盖到的分布很窄——动起来了，内容没怎么变"
assert v["jump_t500"] > 3 * v["jump_t30"], "强度大 → 每帧都像真的，画面却在跳"
v["jump_ratio"] = v["jump_indep"] / v["jump_t30"]

# ---------- （3）公开数字
v["sora_max_sec"] = SORA["max_seconds"]
v["sora_img_res"] = SORA["image_res"]
v["sora_params_known"] = SORA["params"] is not None
v["sora_data_known"] = SORA["data"] is not None
v["sora_compute_known"] = SORA["compute"] is not None
assert not (v["sora_params_known"] or v["sora_data_known"] or v["sora_compute_known"]), \
    "参数量、数据、算力，报告一个都没给"
v["sora_note"] = SORA["note"]
v["svd_clips_y"] = SVD["lvd_clips"] / 1e8
v["svd_years"] = SVD["lvd_years"]
v["svd_f_clips_y"] = SVD["lvdf_clips"] / 1e8
v["svd_f_years"] = SVD["lvdf_years"]
v["svd_drop_pct"] = (1 - SVD["lvdf_clips"] / SVD["lvd_clips"]) * 100      # 折算：过滤掉了多少
v["svd_frames"] = f"{SVD['frames'][0]} 到 {SVD['frames'][1]}"
v["svd_res"] = f"{SVD['res'][0]}×{SVD['res'][1]}"
v["svd_unet_y"] = SVD["unet_params"] / 1e8
v["svd_temporal_y"] = SVD["temporal_params"] / 1e8
v["svd_temporal_pct"] = SVD["temporal_params"] / SVD["unet_params"] * 100
v["svd_fvd"] = SVD["ucf101_fvd"]
v["svd_hw_known"] = SVD["hardware"] is not None
assert not v["svd_hw_known"], "训练硬件论文没给"
# 一段 25 帧、576×1024 的片子，在潜空间里的词元数
_, _, svd_tok = video_tokens(SVD["frames"][1] / FPS, FPS, SVD["res"])
v["svd_tok"] = svd_tok
v["sora_over_svd"] = total / svd_tok

out(**v)
