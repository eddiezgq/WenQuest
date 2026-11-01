"""三维、音乐与语音生成的公开发表数字（第 16.6 节用；第 14 章可引）。

规矩与 `gen_facts.py`、`rl_facts.py` 相同：**只收论文正文、官方技术报告或官方文档给出的原始
数字**；媒体估算与第三方转述一律不收；未公布的项用 `UNPUBLISHED` 标出，正文写"未公布"；
由原始值算出来的倍数与换算，注释里标"折算"。
每条的出处、位置、口径与"为什么不能横向比较"见
`docs/教材/人工智能/参考/第16章第6节_三维音乐语音_原始数字资料_2026-11.md`。
核对日期：2026 年 11 月 1 日。
"""

UNPUBLISHED = None                      # 未公布：正文写"未公布"

# ---------------------------------------------------------------- 三维
# Mildenhall 等 2020（NeRF，论文正文第 3、5.3、6.3 节与附录 A）
NERF = {
    "density_layers": 8, "density_width": 256, "color_layers": 1, "color_width": 128,
    "L_x": 10, "L_d": 4, "rays_per_batch": 4096,
    "samples_coarse": 64, "samples_fine": 128, "queries_per_ray": 256,
    "iters": (100_000, 300_000), "gpu": "单块 V100", "days": (1, 2),
    "sec_per_frame": 30, "weights_mb": 5,
    "rays_per_image_synth": 640_000, "queries_per_image": (150_000_000, 200_000_000),
    "params": UNPUBLISHED, "vram": UNPUBLISHED,
}
# Müller 等 2022（Instant-NGP，论文正文表 1、表 2、第 4、5.4 节）
INGP = {
    "T_range": (2 ** 14, 2 ** 24), "L": 16, "F": 2, "N_min": 16,
    "cliff_T": 2 ** 19, "half_precision": True,
    "mlp_hidden": 2, "mlp_width": 64,
    "psnr": {1: 21.202, 5: 29.261, 15: 31.407, 60: 32.635, 300: 33.176},   # 键是训练秒数
    "psnr_nerf": 31.005, "psnr_mipnerf": 33.090,
    "ms_per_step_hash": 6, "ms_per_step_freq": 30,
    "gpu": "单块 RTX 3090", "fps_nerf": 60,
    "params_mlp": 10_000, "params_enc_T19": 12_600_000,
    "params_total": UNPUBLISHED, "rays_per_s": UNPUBLISHED,
}
# Kerbl 等 2023（3D 高斯泼溅，论文正文表 1、第 1、7.1—7.4 节）
GS3D = {
    "train_min_7k": {"mip360": 6 + 25 / 60, "tnt": 6 + 55 / 60, "db": 4 + 35 / 60},
    "train_min_30k": {"mip360": 41 + 33 / 60, "tnt": 26 + 54 / 60, "db": 36 + 2 / 60},
    "fps_30k": {"mip360": 134, "tnt": 154, "db": 137},
    "fps_baseline": {"mip360": 0.06, "tnt": 0.14, "db": 0.09},
    "gpu": "A6000", "gaussians": (1_000_000, 5_000_000),
    "mem_mb_30k": {"mip360": 734, "tnt": 411, "db": 676},
    "vram_peak_gb": 20,                                  # 原话"可以超过 20 GB"，且自称未优化的原型
    "sh_bands": 4, "attrs": {"pos": 3, "opacity": 1, "scale": 3, "rot": 4},
    "floats_per_gaussian": 59,                           # 折算：3+1+3+4+48（4 个带 → 每通道 16 个系数）
    "psnr_30k": {"mip360": 27.21, "tnt": 23.14, "db": 29.41},
    "psnr_mip360_paper": 27.69,                          # 表 1 标注"抄自对方论文"
    "fps_res": UNPUBLISHED,                              # 表 1 的帧率对应什么分辨率，论文没标
}
# Poole 等 2022（DreamFusion，论文正文第 3.1、3.2 节与附录 A.2）
DREAMFUSION = {
    "hours": 1.5, "iters": 15_000, "chips": 4, "hardware": "一台 TPUv4 机器（4 块芯片）",
    "render_res": 64, "guidance_w": 100, "guidance_typical_img": (5, 30),
    "nerf_blocks": 5, "nerf_width": 128, "L": 8,
    "clip_rprec_color": 79.7, "clip_rprec_geo": 58.5, "clip_rprec_real": 79.1,   # CLIP L/14
    "prompts": 153,
    "params": UNPUBLISHED, "gpu": UNPUBLISHED,
}
# Tochilkin 等 2024（TripoSR，技术报告第 1、3 节与表 1—3）
TRIPOSR = {
    "seconds": 0.5, "gpu": "A100", "in_res": 512,
    "encoder": "DINO（v1）", "triplane": (32, 32, 3), "triplane_ch": 16,
    "backbone_layers": 16, "backbone_ch": 1024,
    "gso_cd": 0.111, "gso_fs01": 0.651, "omni_cd": 0.102,
    "params": UNPUBLISHED, "train_hardware": UNPUBLISHED, "train_data_size": UNPUBLISHED,
}

# ---------------------------------------------------------------- 音乐
# Dhariwal 等 2020（Jukebox，论文正文第 5.1—5.4、7 节与表 4—6）
JUKEBOX = {
    "sr": 44_100, "hops": (8, 32, 128), "codebook": 2048, "embed_width": 64,
    "ctx": 8192, "ctx_seconds_top": 24,
    "params_vqvae": 2_000_000, "params_top_prior": 5_000_000_000,
    "songs": 1_200_000, "songs_en": 600_000, "hours": UNPUBLISHED,
    "v100_top": 512, "weeks_top": 4, "steps_top": 310_500, "batch_top": 512,
    "v100_vqvae": 256, "days_vqvae": 3,
    "sample_hours_per_min_top": 1, "sample_hours_per_min_upsample": 8,
    "sample_hardware": UNPUBLISHED,
    "params_total": UNPUBLISHED,
}
# Agostinelli 等 2023（MusicLM，论文正文第 3.1、4.1—4.4 节与表 1）
MUSICLM = {
    "sr": 24_000, "acoustic_hz": 50, "acoustic_q": 12, "acoustic_codebook": 1024,
    "acoustic_tokens_per_s": 600,                        # 论文直接给的
    "semantic_tokens_per_s": 25, "semantic_clusters": 1024,
    "kbps": 6, "stage_params": 430_000_000, "stages": 3,
    "hours": 280_000, "clips": 5_000_000,
    "fad_trill": 0.44, "fad_vggish": 4.0, "kld": 1.01, "mcc": 0.51,
    "musiccaps_clips": 5521, "musiccaps_seconds": 10,
    "params_total": UNPUBLISHED, "fad_reference": UNPUBLISHED,
}
# Copet 等 2023（MusicGen，论文正文第 3.1—3.3 节与表 1、表 4、表 5）
MUSICGEN = {
    "sr": 32_000, "hz": 50, "K": 4, "codebook": 2048,
    "tokens_per_s": 200,                                 # 折算：50 × 4
    "kbps": None,                                        # 论文没给；折算 2.2 kbps
    "params": (300_000_000, 1_500_000_000, 3_300_000_000),
    "hours": 20_000, "gpus": (32, 64, 96), "gpu_type": UNPUBLISHED,
    "steps": 1_000_000, "batch": 192,
    "steps_30s_delay": 1500, "steps_30s_flat": 6000,     # 表 4：码本交错模式的自回归步数
    "fad": {300_000_000: 3.1, 1_500_000_000: 3.4, 3_300_000_000: 3.8},
    "kl": {300_000_000: 1.28, 1_500_000_000: 1.23, 3_300_000_000: 1.22},
}

# ---------------------------------------------------------------- 语音
# van den Oord 等 2016（WaveNet，论文正文第 2.1—2.2、3.1—3.4 节与表 1—2、附录 B）
WAVENET = {
    "sr": 16_000, "mu_law_levels": 256, "bits": 8,
    "dilation_max": 512, "block_receptive_samples": 1024,
    "receptive_ms_tts": 240, "receptive_ms_multi": 300,
    "mos": {"wavenet_en": 4.21, "wavenet_zh": 4.08,
            "lstm_en": 3.67, "lstm_zh": 3.79,
            "concat_en": 3.86, "concat_zh": 3.47,
            "human_8bit_en": 4.46, "human_16bit_en": 4.55},
    "mos_ci": {"wavenet_en": 0.081, "wavenet_zh": 0.085},
    "mos_sentences": 100, "raters_per_clip": 8, "headphone_reject_pct": 40,
    "hours_en": 24.6, "hours_zh": 34.8,
    "timit_per": 18.8,
    "gen_speed": UNPUBLISHED,                            # 原论文完全没给生成速度
}
# Wang 等 2023（VALL-E，论文正文第 3、5.1—5.2 节与表 2）
VALLE = {
    "sr": 24_000, "hz": 75, "quantizers": 8, "codebook": 1024,
    "tokens_per_s": 600,                                 # 折算：75 × 8（与论文自己的 10 秒例子一致）
    "hours": 60_000, "speakers": 7000,
    "label_source": "用 960 小时 LibriSpeech 上训的 DNN-HMM 识别器机器转写",
    "layers": 12, "heads": 16, "dim": 1024, "ffn": 4096,
    "v100": 16, "steps": 800_000, "prompt_seconds": 3,
    "wer": 5.9, "spk": 0.580, "wer_human": 2.2, "spk_human": 0.754,
    "params": UNPUBLISHED, "gpu_hours": UNPUBLISHED,
}
# Zeghidour 等 2021（SoundStream，论文正文第 III、IV、V 节与表 I—III）
SOUNDSTREAM = {
    "sr": 24_000, "strides": (2, 4, 5, 8), "M": 320, "hz": 75, "frame_ms": 13.3,
    "nq": 8, "codebook": 1024, "kbps": 6,
    "equal_bitrate_variants": ((8, 1024), (16, 32), (80, 2)),   # 同为 6 kbps，词元数差 10 倍
    "params": 8_400_000, "rtf_encode": 2.4, "rtf_decode": 2.3,
    "rtf_device": "Pixel 4 手机单 CPU 线程",
    "visqol_table": 4.01, "visqol_text": 3.96,           # 论文自身两处没对上
    "evs_needs_kbps": 9.6, "opus_needs_kbps": 12,        # 要追上它的 3 kbps
    "mushra_values": UNPUBLISHED,                        # 正文只有折线图，没有数值
    "train_hours": UNPUBLISHED,
}
# Défossez 等 2022（EnCodec，论文正文第 3.1—3.4、4.1—4.6 节与表 1、表 5、表 A.1）
ENCODEC = {
    "sr": (24_000, 48_000), "hz": (75, 150), "strides": (2, 4, 5, 8), "M": 320,
    "codebook": 1024, "max_codebooks": (32, 16),
    "mushra_24k": {1.5: 49.2, 3.0: 67.0, 6.0: 83.1, 12.0: 90.6},    # 干净语音
    "mushra_opus12": 76.5, "mushra_evs96": 84.4, "mushra_lyra2_6": 66.2,
    "visqol_6k": 4.35, "si_snr_6k": 6.67,
    "rtf_24k": (9.8, 10.4), "rtf_24k_entropy": 1.6, "rtf_48k_entropy": (0.68, 0.66),
    "rtf_device": "2019 款 MacBook Pro 单线程",
    "latency_ms_24k": 13.3, "latency_s_48k": 1,
    "train_hours_sum": 17_537,                           # 折算：表 A.1 五个来源相加（论文没给总数）
    "a100": 8, "epochs": 300, "updates_per_epoch": 2000,
    "params": UNPUBLISHED, "latent_dim": UNPUBLISHED,
}

# ---------------------------------------------------------------- 各模态的词元率
# 原始值见资料卡第 11 节；凡由帧率乘量化器数得来的都标"折算"。
SPEECH_RATE = {                 # Yuan、Liberman、Cieri，Interspeech 2006 第 2、3 节
    "en_words_per_min": 196, "en_words_per_min_net": 236, "en_range": (111, 291),
    "zh_chars_per_min_friends": 247, "zh_chars_per_min_strangers": 228,
    "dialogs": 2438,
}
TOKENS_PER_WORD = (1.25, 1.67)  # Google Gemini 官方文档："100 个词元约等于 60—80 个英文词"
VIDEOPOET = {                   # VideoPoet（MAGVIT-v2 分词器），论文正文第 3.1、4.1、A.5 节
    "frames": 17, "res": (128, 128), "fps": 8, "latent": (5, 16, 16), "tokens": 1280,
    "tokens_tall": 2240, "tokens_image": 256, "tokens_sr": 35_840,
    "vocab": 2 ** 18, "text_tokens_max": 64,
    "audio_latent_frames": 106, "audio_rvq": 4,
    "audio_sr": UNPUBLISHED,
}
