"""算例 16.6.1—16.6.4：换一种"表示"，同一套办法就能生成三维、音乐与语音（16.6 节）。

（1）词元率的账：语音与视频每秒要的词元数，比说话的文字多两个数量级。这就是为什么音频要先
     过编解码器压成词元，而不是直接按采样点生成。
（2）码本交错为什么必要：四个码本摊平了写，自回归步数就乘四。
（3）三维：从 NeRF 到即时哈希编码到高斯泼溅，训练时间与渲染帧率各差几个数量级；
     但指标并没有全面胜出，这一条必须照原文写。
（4）几个能自己核对的折算：Jukebox 的上下文到底是多少秒、高斯泼溅一个点要多少字节。
"""
import numpy as np

from bookout import out
from av_facts import (ENCODEC, GS3D, INGP, JUKEBOX, MUSICGEN, MUSICLM, NERF, SOUNDSTREAM,
                      SPEECH_RATE, TOKENS_PER_WORD, TRIPOSR, VALLE, VIDEOPOET, WAVENET,
                      DREAMFUSION)

v = {}

# ---------- （1）词元率
wps = SPEECH_RATE["en_words_per_min"] / 60
v["words_per_min"] = SPEECH_RATE["en_words_per_min"]
v["words_per_s"] = wps
v["text_tok_lo"] = wps * TOKENS_PER_WORD[0]              # 折算：词/秒 × 词元/词
v["text_tok_hi"] = wps * TOKENS_PER_WORD[1]
v["tokens_per_word"] = f"{TOKENS_PER_WORD[0]} 到 {TOKENS_PER_WORD[1]}"
v["zh_chars_per_min"] = SPEECH_RATE["zh_chars_per_min_strangers"]

v["speech_hz"], v["speech_q"] = SOUNDSTREAM["hz"], SOUNDSTREAM["nq"]
speech_tok = SOUNDSTREAM["hz"] * SOUNDSTREAM["nq"]       # 折算：75 × 8
v["speech_tok"] = speech_tok
assert speech_tok == VALLE["tokens_per_s"], "VALL-E 用的就是这一档，词元率应当一致"
wavenet_tok = WAVENET["sr"]                              # 折算：每个采样点当一个词元
v["wavenet_tok"] = wavenet_tok
v["wavenet_over_codec"] = wavenet_tok / speech_tok
assert v["wavenet_over_codec"] > 20, "直接按采样点生成，要处理的词元多二十几倍"
v["wavenet_bits"] = WAVENET["bits"]
v["codec_bits"] = int(np.log2(SOUNDSTREAM["codebook"]))
v["wavenet_kbps"] = wavenet_tok * WAVENET["bits"] / 1000
v["codec_kbps"] = SOUNDSTREAM["kbps"]
v["kbps_ratio"] = v["wavenet_kbps"] / v["codec_kbps"]

v["music_tok_musiclm"] = MUSICLM["acoustic_tokens_per_s"] + MUSICLM["semantic_tokens_per_s"]
v["music_tok_musicgen"] = MUSICGEN["tokens_per_s"]
assert MUSICGEN["hz"] * MUSICGEN["K"] == MUSICGEN["tokens_per_s"], "折算核对：50 × 4 = 200"
v["jukebox_top_tok"] = JUKEBOX["sr"] / JUKEBOX["hops"][2]          # 折算：44100 / 128
v["jukebox_bot_tok"] = JUKEBOX["sr"] / JUKEBOX["hops"][0]

vp_sec = VIDEOPOET["frames"] / VIDEOPOET["fps"]
v["video_sec"] = vp_sec
v["video_tok"] = VIDEOPOET["tokens"] / vp_sec                      # 折算：1280 / 2.125
v["video_tok_sr"] = VIDEOPOET["tokens_sr"] / vp_sec
v["video_over_text"] = v["video_tok"] / v["text_tok_hi"]
v["speech_over_text"] = speech_tok / v["text_tok_hi"]
assert v["speech_over_text"] > 50 and v["video_over_text"] > 50, \
    "语音与视频的词元率都比文本高两个数量级——这就是本节的主线"
v["rate_rows"] = [
    ("说话的文字（英语会话）", round(v["text_tok_lo"], 1), round(v["text_tok_hi"], 1)),
    ("语音（SoundStream 6 kbps）", speech_tok, speech_tok),
    ("语音（直接按采样点，WaveNet）", wavenet_tok, wavenet_tok),
    ("音乐（MusicGen）", MUSICGEN["tokens_per_s"], MUSICGEN["tokens_per_s"]),
    ("音乐（MusicLM 语义 + 声学）", v["music_tok_musiclm"], v["music_tok_musiclm"]),
    ("视频潜空间（128×128，8 帧/秒）", round(v["video_tok"], 1), round(v["video_tok"], 1)),
]
# 同一个比特率可以有完全不同的词元数——这一条说明"词元数"不能当复杂度比
v["equal_bitrate"] = [(nq, cb, SOUNDSTREAM["hz"] * nq) for nq, cb in
                      SOUNDSTREAM["equal_bitrate_variants"]]
for nq, cb in SOUNDSTREAM["equal_bitrate_variants"]:
    assert abs(SOUNDSTREAM["hz"] * nq * np.log2(cb) - SOUNDSTREAM["kbps"] * 1000) < 1, \
        "三个变体的比特率都是 6 kbps，可词元数差十倍"
v["equal_bitrate_token_ratio"] = (SOUNDSTREAM["equal_bitrate_variants"][2][0]
                                  / SOUNDSTREAM["equal_bitrate_variants"][0][0])

# ---------- （2）码本交错
v["mg_K"], v["mg_hz"] = MUSICGEN["K"], MUSICGEN["hz"]
v["mg_frames_30s"] = MUSICGEN["hz"] * 30
v["mg_steps_delay"] = MUSICGEN["steps_30s_delay"]
v["mg_steps_flat"] = MUSICGEN["steps_30s_flat"]
assert v["mg_frames_30s"] == v["mg_steps_delay"], "延迟模式的步数就等于帧数（折算核对）"
assert v["mg_steps_delay"] * MUSICGEN["K"] == v["mg_steps_flat"], "完全摊平就乘上码本数"
v["mg_step_ratio"] = v["mg_steps_flat"] / v["mg_steps_delay"]
v["mg_params_s"], v["mg_params_m"], v["mg_params_l"] = [p / 1e8 for p in MUSICGEN["params"]]
v["mg_fad"] = [(p / 1e8, MUSICGEN["fad"][p], MUSICGEN["kl"][p]) for p in MUSICGEN["params"]]
v["mg_fad_small"], v["mg_fad_big"] = MUSICGEN["fad"][300_000_000], MUSICGEN["fad"][3_300_000_000]
assert v["mg_fad_big"] > v["mg_fad_small"], \
    "参数变大，FAD 反而变差（KL 却变好）——所以不能写'越大越好'"
v["mg_hours"] = MUSICGEN["hours"]
v["mg_gpu_type_known"] = MUSICGEN["gpu_type"] is not None
assert not v["mg_gpu_type_known"], "用了多少块 GPU 论文给了，型号没给"

# Jukebox 的上下文到底是多少秒：论文自己说约 24 秒，折算核对
v["jb_ctx"], v["jb_hop_top"] = JUKEBOX["ctx"], JUKEBOX["hops"][2]
v["jb_ctx_sec_calc"] = JUKEBOX["ctx"] * JUKEBOX["hops"][2] / JUKEBOX["sr"]
v["jb_ctx_sec_paper"] = JUKEBOX["ctx_seconds_top"]
assert abs(v["jb_ctx_sec_calc"] - v["jb_ctx_sec_paper"]) < 0.5, "折算与论文自己写的秒数对得上"
v["jb_sample_hours"] = JUKEBOX["sample_hours_per_min_top"] + JUKEBOX["sample_hours_per_min_upsample"]
v["jb_realtime"] = v["jb_sample_hours"] * 3600 / 60                # 折算：几倍于实时
v["jb_hw_known"] = JUKEBOX["sample_hardware"] is not None
assert not v["jb_hw_known"], "这两个采样耗时是在什么机器上测的，论文没写"
v["jb_v100_weeks"] = JUKEBOX["v100_top"] * JUKEBOX["weeks_top"]    # 折算：512 块 × 4 周
v["jb_params_top_y"] = JUKEBOX["params_top_prior"] / 1e8
v["jb_songs_w"] = JUKEBOX["songs"] / 1e4
v["jb_hours_known"] = JUKEBOX["hours"] is not None
assert not v["jb_hours_known"], "训练数据的总时长论文没给，只给了歌曲数"

# ---------- （3）三维
v["nerf_days"] = f"{NERF['days'][0]} 到 {NERF['days'][1]}"
v["nerf_gpu"] = NERF["gpu"]
v["nerf_sec_per_frame"] = NERF["sec_per_frame"]
v["nerf_fps"] = 1 / NERF["sec_per_frame"]                          # 折算
v["nerf_weights_mb"] = NERF["weights_mb"]
v["nerf_params_known"] = NERF["params"] is not None
assert not v["nerf_params_known"], "NeRF 的参数个数论文没给，只给了权重 5 MB"
v["ingp_psnr"] = [(s, INGP["psnr"][s]) for s in sorted(INGP["psnr"])]
v["ingp_psnr_15s"], v["ingp_psnr_nerf"] = INGP["psnr"][15], INGP["psnr_nerf"]
assert v["ingp_psnr_15s"] > v["ingp_psnr_nerf"], "训 15 秒就超过了 NeRF 那一行的 31.005"
v["ingp_speedup"] = NERF["days"][0] * 86400 / 15                   # 折算：1 天 ÷ 15 秒
v["ingp_gpu"] = INGP["gpu"]
v["ingp_cliff_T"] = INGP["cliff_T"]
v["ingp_enc_cap"] = INGP["cliff_T"] * INGP["L"] * INGP["F"] / 1e6  # 折算：T·L·F（百万条目）
v["ingp_enc_real"] = INGP["params_enc_T19"] / 1e6
assert v["ingp_enc_real"] < v["ingp_enc_cap"], "实测参数低于上界，因为粗层级的格点本来就少"
v["gs_train_min"] = GS3D["train_min_30k"]["mip360"]
v["gs_fps"] = GS3D["fps_30k"]["mip360"]
v["gs_fps_base"] = GS3D["fps_baseline"]["mip360"]
v["gs_render_speedup"] = GS3D["fps_30k"]["mip360"] / GS3D["fps_baseline"]["mip360"]   # 折算
v["gs_gpu"] = GS3D["gpu"]
v["gs_fps_res_known"] = GS3D["fps_res"] is not None
assert not v["gs_fps_res_known"], "表 1 的帧率对应什么分辨率，论文没标——不能写'134 FPS @ 1080p'"
v["gs_psnr"], v["gs_psnr_base"] = GS3D["psnr_30k"]["mip360"], GS3D["psnr_mip360_paper"]
assert v["gs_psnr"] < v["gs_psnr_base"], \
    "这个数据集上它的 PSNR 还低一点——赢的是 SSIM 与 LPIPS，正文要照原文写"
v["gs_vram_gb"] = GS3D["vram_peak_gb"]
# 一个高斯要多少字节：折算，再与论文表 1 的落盘大小对一下
v["gs_floats"] = GS3D["floats_per_gaussian"]
v["gs_bytes"] = GS3D["floats_per_gaussian"] * 4
v["gs_mb_lo"] = GS3D["gaussians"][0] * v["gs_bytes"] / 1e6
v["gs_mb_hi"] = GS3D["gaussians"][1] * v["gs_bytes"] / 1e6
v["gs_mem_paper"] = GS3D["mem_mb_30k"]["mip360"]
assert v["gs_mb_lo"] < v["gs_mem_paper"] < v["gs_mb_hi"], "折算出的区间把论文的落盘大小夹在里面"
v["three_rows"] = [
    ("NeRF（2020）", "1—2 天", round(v["nerf_fps"], 3), NERF["gpu"]),
    ("即时哈希编码（2022）", "15 秒", INGP["fps_nerf"], INGP["gpu"]),
    ("三维高斯泼溅（2023）", f"{v['gs_train_min']:.0f} 分钟", v["gs_fps"], GS3D["gpu"]),
]
# 文本到三维：优化型与前馈型差了四个数量级，但不是同一类任务
v["df_hours"], v["df_chips"] = DREAMFUSION["hours"], DREAMFUSION["chips"]
v["df_w"] = DREAMFUSION["guidance_w"]
v["df_w_typical"] = f"{DREAMFUSION['guidance_typical_img'][0]} 到 {DREAMFUSION['guidance_typical_img'][1]}"
assert v["df_w"] > 3 * DREAMFUSION["guidance_typical_img"][1], \
    "文本到三维把引导强度开到图像生成常用值的好几倍——与 16.4 节的代价对着看"
v["tripo_sec"], v["tripo_gpu"] = TRIPOSR["seconds"], TRIPOSR["gpu"]
v["df_over_tripo"] = DREAMFUSION["hours"] * 3600 / TRIPOSR["seconds"]      # 折算
v["tripo_params_known"] = TRIPOSR["params"] is not None
assert not v["tripo_params_known"], "参数量、训练硬件、训练时长，这份报告都没写"

# ---------- （4）编解码器自己的代价
v["enc_rtf"], v["enc_rtf_entropy"] = ENCODEC["rtf_24k"][0], ENCODEC["rtf_24k_entropy"]
v["enc_rtf_48k_entropy"] = ENCODEC["rtf_48k_entropy"][0]
assert v["enc_rtf_48k_entropy"] < 1, "48 kHz 开了熵编码就跑不到实时了"
v["enc_rtf_drop"] = ENCODEC["rtf_24k"][0] / ENCODEC["rtf_24k_entropy"]
v["enc_mushra"] = [(k, ENCODEC["mushra_24k"][k]) for k in sorted(ENCODEC["mushra_24k"])]
v["enc_mushra_6"] = ENCODEC["mushra_24k"][6.0]
v["enc_opus12"] = ENCODEC["mushra_opus12"]
assert v["enc_mushra_6"] > v["enc_opus12"], "6 kbps 的神经编解码器比 12 kbps 的 Opus 还好听"
v["enc_train_hours"] = ENCODEC["train_hours_sum"]
v["enc_a100"] = ENCODEC["a100"]
v["enc_params_known"] = ENCODEC["params"] is not None
assert not v["enc_params_known"], "参数量论文没给"
v["ss_params_w"] = SOUNDSTREAM["params"] / 1e4
v["ss_sr_k"] = SOUNDSTREAM["sr"] / 1000
v["ss_m"] = SOUNDSTREAM["M"]
v["music_sem"] = MUSICLM["semantic_tokens_per_s"]
v["music_aco"] = MUSICLM["acoustic_tokens_per_s"]
v["musiclm_hours"] = MUSICLM["hours"] / 1e4
v["ingp_15s"] = 15
v["ingp_fps"] = INGP["fps_nerf"]
v["ss_rtf"] = SOUNDSTREAM["rtf_encode"]
v["ss_device"] = SOUNDSTREAM["rtf_device"]
v["ss_mushra_known"] = SOUNDSTREAM["mushra_values"] is not None
assert not v["ss_mushra_known"], "SoundStream 的 MUSHRA 只有折线图，没有数值"
v["valle_hours_w"] = VALLE["hours"] / 1e4
v["valle_wer"], v["valle_wer_human"] = VALLE["wer"], VALLE["wer_human"]
v["valle_spk"], v["valle_spk_human"] = VALLE["spk"], VALLE["spk_human"]
v["valle_label"] = VALLE["label_source"]
v["wavenet_mos"] = WAVENET["mos"]["wavenet_en"]
v["wavenet_mos_human"] = WAVENET["mos"]["human_16bit_en"]
v["wavenet_speed_known"] = WAVENET["gen_speed"] is not None
assert not v["wavenet_speed_known"], "常被引用的'WaveNet 生成一秒要几分钟'不出自原论文"

out(**v)
