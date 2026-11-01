"""算例 16.4.1—16.4.4：潜在扩散、条件控制与图像编辑（16.4 节）。

（1）潜在扩散省在哪：把图先压到潜空间，要处理的数少几十倍，自注意力的代价少几千倍。
     论文自己测的吞吐与训练时长也列在这里。
（2）条件生成：给每一类单独一个噪声预测器，采出来的分布与真条件分布对得上。
（3）无分类器引导：引导一调强，单张更"像这一类"，但分布明显偏了，矮峰直接被挤掉。
     这与引导论文自己的表（FID 变差、IS 变好）是同一件事。
（4）编辑强度：先加噪到某个时刻再去噪。强度小只微调，强度大就与原图无关了。
"""
import numpy as np

from _ch16 import (cond_cdf, cond_pdf, cond_sample, diffusion_fit, diffusion_sample, guided,
                   ks, latent_cost, mix_sample, mode_share, sdedit, sharpness, COND_MU, COND_W)
from bookout import out
from gen_facts import CFG, LAION, LDM, SD1

v = {}

# ---------- （1）潜在扩散的账
RES = SD1["res_finetune"]
px, lat, ratio, attn = latent_cost(RES, SD1["f"], LDM["c_f8"])
v["res"] = RES
v["f_sd1"] = SD1["f"]
v["px_values_w"] = px / 1e4
v["lat_values_w"] = lat / 1e4
v["value_ratio"] = ratio
v["attn_ratio"] = attn
v["lat_side"] = RES // SD1["f"]
px4, lat4, ratio4, attn4 = latent_cost(RES, 4, LDM["c_f4"])
v["ratio_f4"], v["attn_f4"] = ratio4, attn4
v["f_best_lo"], v["f_best_hi"] = LDM["f_best"]
# 论文自己测的（表 6）：f=4 的采样吞吐与每轮训练时长
v["ldm4_sps"], v["ldm1_sps"] = LDM["samples_per_s_ldm4"], LDM["samples_per_s_ldm1"]
v["sps_ratio"] = LDM["samples_per_s_ldm4"] / LDM["samples_per_s_ldm1"]
v["ldm4_hpe"], v["ldm1_hpe"] = LDM["hours_per_epoch_ldm4"], LDM["hours_per_epoch_ldm1"]
v["hpe_ratio"] = LDM["hours_per_epoch_ldm1"] / LDM["hours_per_epoch_ldm4"]
assert v["sps_ratio"] > 3 and v["hpe_ratio"] > 2, "论文自己的两列数都说潜空间快好几倍"
v["ldm_coco_fid"], v["ldm_coco_fid_g"] = LDM["coco_fid"], LDM["coco_fid_guided"]
v["ldm_in_fid"], v["ldm_in_fid_g"] = LDM["imagenet_fid"], LDM["imagenet_fid_guided"]
v["ldm_txt_params_y"] = LDM["txt2img_params"] / 1e8
v["ldm_gpu_days_known"] = LDM["gpu_days"] is not None
assert not v["ldm_gpu_days_known"], "各模型用了多少 GPU 天，论文没给"
v["sd1_unet_y"], v["sd1_text_y"] = SD1["unet_params"] / 1e8, SD1["text_params"] / 1e8
v["sd1_vram"] = SD1["vram_gb"]
v["sd1_hours_known"] = SD1["a100_hours"] is not None
assert not v["sd1_hours_known"], "常被引用的'15 万 A100 小时'没核到官方原文，正文写'未公布'"
v["laion_pairs_y"] = LAION["pairs"] / 1e8
v["laion_en_y"] = LAION["english"] / 1e8
v["laion_before_y"] = LAION["before_filter"] / 1e8
v["laion_thr"] = LAION["clip_thr_en"]
v["laion_nsfw"] = LAION["nsfw_share"]
v["laion_stores"] = LAION["stores_images"]
assert not v["laion_stores"], "这个数据集只发网址与替代文字，不存图——这一点影响版权那一节"
v["laion400m_y"] = LAION["laion400m"] / 1e8
v["laion_filter_ratio"] = LAION["before_filter"] / LAION["pairs"]    # 折算：过滤掉了多少

# ---------- （2）条件生成对不对
train = mix_sample(8000, 0)
model = diffusion_fit(train)
abar = model["abar"]
v["cond_rows"] = []
for c in (0, 1):
    x = diffusion_sample(model, 4000, steps=200, guide=guided(c, 0.0, abar), seed=0)
    k = ks(x, lambda t, c=c: cond_cdf(c, t))
    kf = ks(cond_sample(c, 4000, 7), lambda t, c=c: cond_cdf(c, t))
    v["cond_rows"].append((c, round(k, 4), round(kf, 4)))
    v[f"ks_cond{c}"], v[f"ks_cond{c}_floor"] = k, kf
    assert k < 3 * kf, "不加引导时，条件采样应当贴着真条件分布"
v["n_cond_modes"] = len(COND_MU[0])
v["shared_mode"] = float(COND_MU[0][1])
assert COND_MU[0][1] == COND_MU[1][0], "两类共用中间那个峰——引导太强时先丢的就是它"

# ---------- （3）引导强度
v["w_rows"] = []
C0 = 0
real0 = cond_sample(C0, 4000, 3)
v["sharp_real"] = sharpness(real0, C0)
v["share_real"] = [round(float(s), 3) for s in mode_share(real0, C0)]
for wg in (0.0, 0.3, 1.0, 2.0, 4.0, 8.0):
    x = diffusion_sample(model, 4000, steps=200, guide=guided(C0, wg, abar), seed=0)
    sh = mode_share(x, C0)
    v["w_rows"].append((wg, round(ks(x, lambda t: cond_cdf(C0, t)), 4),
                        round(sharpness(x, C0), 3), round(float(sh[0]), 3), round(float(sh[1]), 3)))
for wg, k, sp, s1, s2 in v["w_rows"]:
    tag = str(wg).replace(".", "p").rstrip("0").rstrip("p") or "0"
    v[f"ks_w{tag}"], v[f"sharp_w{tag}"] = k, sp
    v[f"share1_w{tag}"], v[f"share2_w{tag}"] = s1, s2
assert v["sharp_w2"] > v["sharp_w0"], "引导调强，样本更'像这一类'"
v["ks_w4_over"] = v["ks_w4"] / v["ks_w0"]
assert v["ks_w4_over"] > 10, "可是分布明显偏了"
assert v["share2_w4"] < 0.1 * v["share2_w0"], "共用的那个峰被挤掉了——这就是引导换来的代价"
assert v["sharp_w8"] < v["sharp_w2"], "引导再往上加，连'像不像'都开始变差"
# 引导论文自己的表（ImageNet 64×64，p_uncond = 0.1）：FID 变差、IS 变好
v["cfg_rows"] = [(w, CFG["in64"][w][0], CFG["in64"][w][1]) for w in (0.0, 0.1, 0.3, 1.0, 4.0)]
for w in (0.0, 0.1, 0.3, 1.0, 4.0):
    tag = str(w).replace(".", "p").rstrip("0").rstrip("p") or "0"
    v[f"cfg_fid_{tag}"], v[f"cfg_is_{tag}"] = CFG["in64"][w]
v["cfg_fid0"], v["cfg_fid4"] = CFG["in64"][0.0][0], CFG["in64"][4.0][0]
v["cfg_is0"], v["cfg_is4"] = CFG["in64"][0.0][1], CFG["in64"][4.0][1]
v["cfg_formula"] = CFG["formula"]
v["cfg_p_best_lo"], v["cfg_p_best_hi"] = CFG["p_uncond_best"]
assert v["cfg_fid4"] > v["cfg_fid0"] and v["cfg_is4"] > v["cfg_is0"], \
    "两个指标往相反方向走——所以只报一个数是会骗人的"

# ---------- （4）编辑强度
x0 = mix_sample(600, 55)
v["edit_rows"] = []
for t0 in (50, 150, 300, 500, 999):
    x = sdedit(model, x0, t0, seed=0)
    v["edit_rows"].append((t0, round(float(np.corrcoef(x, x0)[0, 1]), 3),
                           round(float(np.mean(np.abs(x - x0))), 3), round(ks(x), 4)))
for t0, co, mv, k in v["edit_rows"]:
    v[f"edit_corr_t{t0}"], v[f"edit_move_t{t0}"], v[f"edit_ks_t{t0}"] = co, mv, k
v["edit_corr_lo"], v["edit_corr_hi"] = v["edit_rows"][0][1], v["edit_rows"][-1][1]
v["edit_ks_max"] = max(r[3] for r in v["edit_rows"])
assert v["edit_corr_lo"] > 0.9, "强度小的时候，改完还认得出原来那一张"
assert abs(v["edit_corr_hi"]) < 0.1, "强度拉满就等于重新生成一张"
assert v["edit_ks_max"] < 0.08, "不管强度多大，出来的都还落在真分布上"
v["inpaint_speedup"] = LDM["inpaint_speedup"]

out(**v)
