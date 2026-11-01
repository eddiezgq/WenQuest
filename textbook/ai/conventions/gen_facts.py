"""生成模型的公开发表数字（第 16 章用；第 11、13 章可引）。

规矩与 `llm_facts.py`、`mm_facts.py`、`rl_facts.py` 相同：**只收论文正文、官方技术报告、
官方公告或正式标准文本给出的原始数字**；媒体估算与第三方转述一律不收；未公布的项用
`UNPUBLISHED` 标出，正文写"未公布"；由原始值算出来的倍数与换算，注释里标"折算"。
每条的出处、口径与"为什么不能横向比较"见
`docs/教材/人工智能/参考/第16章_生成模型原始数字资料_2026-11.md`。核对日期：2026 年 11 月 1 日。
"""

UNPUBLISHED = None                      # 未公布：正文写"未公布"

# ---------------------------------------------------------------- GAN 一路
# Goodfellow 等 2014（论文正文表 1、第 4 节）
GAN = {
    "parzen_mnist": (225, 2), "parzen_tfd": (2057, 26),      # Parzen 窗似然估计（均值, 标准误）
    "parzen_cifar": UNPUBLISHED,                             # 论文根本没有 CIFAR-10 这一项
    "k": 1,                                                  # 每训一次生成器，判别器训 k 步
    "hardware": UNPUBLISHED, "hours": UNPUBLISHED,
}
# Radford 等 2015（DCGAN，论文正文 "Details of adversarial training"）
DCGAN = {"batch": 128, "lr": 2e-4, "beta1": 0.5, "init_std": 0.02, "leaky": 0.2,
         "lsun_images": 3_000_000, "cifar_acc": 82.8, "svhn_err": 22.48}
# Karras 等 2019 / 2020（StyleGAN、StyleGAN2，论文正文表 1—3 与附录）
STYLEGAN = {"ffhq_images": 70_000, "ffhq_res": 1024, "fid_images": 50_000,
            "gpus": 8, "gpu_type": "V100", "weeks": 1, "images_seen_M": 25}
STYLEGAN2 = {"ffhq_fid": 2.84, "ffhq_days": 9, "lsun_car_days": 13, "gpus": 8,
             "fid_images": UNPUBLISHED}                      # 论文没写 FID 用多少张图

# ---------------------------------------------------------------- 评价指标
# Heusel 等 2017（FID，论文正文式 6）
FID = {
    "formula": "||m1-m2||^2 + Tr(C1 + C2 - 2(C1 C2)^{1/2})",
    "layer": "Inception-v3 最后一个池化层",
    "samples": 50_000,
    "small_sample_bias": UNPUBLISHED,                        # 原论文没有讨论小样本偏差
}
# Chong & Forsyth 2020（CVPR）：FID 与 IS 都是**有偏**估计，偏差随样本数变化
FID_BIAS_SOURCE = "Chong & Forsyth, CVPR 2020（arXiv:1911.07023）：FID 有偏，须外推到无穷样本"

# ---------------------------------------------------------------- 扩散一路
# Ho 等 2020（DDPM，论文正文式 4、式 14、表 1、表 2、附录 B）
DDPM = {
    "T": 1000, "beta_start": 1e-4, "beta_end": 0.02,         # 线性噪声调度
    "cifar_is": 9.46, "cifar_fid_train": 3.17, "cifar_fid_test": 5.24,   # 两个口径不能混
    "cifar_fid_L": 13.51,                                    # 用变分下界而不是 L_simple 时
    "steps": 800_000, "batch": 128, "hours": 10.6,
    "hardware": "TPU v3-8（论文自称约等于 8 块 V100）",
    "params_cifar": 35_700_000, "params_lsun": 114_000_000,
    "lr": 2e-4, "ema": 0.9999,
    "lsun_bedroom_fid": 6.36, "stylegan_bedroom_fid": 2.65,
}
# Song 等 2020（DDIM，论文正文表 1 与第 5.1 节）
DDIM = {
    "cifar_fid": {10: 13.36, 20: 6.84, 50: 4.67, 100: 4.16, 1000: 4.04},      # η = 0（确定采样）
    "cifar_fid_ddpm": {10: 41.07, 20: 18.36, 50: 8.01, 100: 5.78, 1000: 4.73},  # η = 1
    "usable_steps": (20, 100),                               # 论文原话"20 到 100 步"
    "speedup": (10, 50),                                     # 摘要：墙钟快 10—50 倍（引言写 10—100）
}
# Rombach 等 2022（潜在扩散，论文正文第 3、4 节与表 6、表 8）
LDM = {
    "f_best": (4, 8), "f_tried": (1, 2, 4, 8, 16, 32),
    "c_f4": 3, "c_f8": 4,                                    # 潜空间通道数
    "txt2img_params": 1_450_000_000, "txt2img_data": 400_000_000,   # LAION-400M
    "coco_fid": 23.31, "coco_fid_guided": 12.63,
    "imagenet_fid": 10.56, "imagenet_fid_guided": 3.60,
    "samples_per_s_ldm4": 0.97, "samples_per_s_ldm1": 0.26,  # 表 6：潜空间 vs 像素空间
    "hours_per_epoch_ldm4": 7.66, "hours_per_epoch_ldm1": 20.66,
    "inpaint_speedup": 2.7, "lsun_resource_ratio": 4,
    "gpu_days": UNPUBLISHED,                                 # 各模型的 GPU 天数论文没给
}
SD1 = {"f": 8, "unet_params": 860_000_000, "text_params": 123_000_000,
       "res_pretrain": 256, "res_finetune": 512, "vram_gb": 10,
       "a100_hours": UNPUBLISHED}                            # 常引的"15 万 A100 小时"未核到官方原文
# Schuhmann 等 2022（LAION-5B，论文正文第 3 节）
LAION = {
    "pairs": 5_850_000_000, "english": 2_320_000_000,
    "before_filter": 50_000_000_000,                         # 过滤前约 500 亿张图
    "clip_thr_en": 0.28, "clip_thr_other": 0.26,
    "nsfw_share": 3.0, "aesthetics": 120_000_000, "high_res": 170_000_000,
    "laion400m": 400_000_000,
    "stores_images": False,                                  # 只发 URL 与 alt-text，不存图
}
# Ho & Salimans 2022（无分类器引导，论文正文式 6、表 1、表 2）
CFG = {
    "formula": "(1+w) eps(z,c) - w eps(z)",                  # 这一版 w = 0 表示不引导
    "p_uncond_tried": (0.1, 0.2, 0.5), "p_uncond_best": (0.1, 0.2),
    "in64": {0.0: (1.80, 53.71), 0.1: (1.55, 66.11), 0.3: (3.03, 92.80),
             1.0: (12.60, 170.10), 4.0: (26.22, 260.20)},    # w: (FID, IS)，p_uncond = 0.1
    "in128": {0.0: (7.27, 82.45), 0.3: (2.43, 158.47), 1.0: (7.86, 297.98), 4.0: (21.53, 421.03)},
    "params": UNPUBLISHED, "hardware": UNPUBLISHED,
}

# ---------------------------------------------------------------- 视频
# OpenAI 2024（Sora 官方技术报告）
SORA = {
    "max_seconds": 60, "res_wide": (1920, 1080), "res_tall": (1080, 1920),
    "image_res": 2048, "old_setting": (4, 256),              # 报告提到以往常见的"4 秒、256×256"
    "params": UNPUBLISHED, "data": UNPUBLISHED, "compute": UNPUBLISHED,
    "note": "报告原话：Model and implementation details are not included in this report.",
}
# Blattmann 等 2023（Stable Video Diffusion，论文正文）
SVD = {
    "lvd_clips": 580_000_000, "lvd_years": 212,
    "lvdf_clips": 152_000_000, "lvdf_years": 50.64,
    "frames": (14, 25), "res": (576, 1024),
    "unet_params": 1_521_000_000, "temporal_params": 656_000_000,
    "ucf101_fvd": 242.02,
    "hardware": UNPUBLISHED,
}

# ---------------------------------------------------------------- 内容标识与版权
C2PA = {
    "parts": ("清单（manifest）", "断言（assertion）", "声明（claim）", "签名（claim signature）"),
    "binding": ("硬绑定（hard binding，内容哈希）", "软绑定（soft binding，水印或指纹）"),
    "crypto": "X.509 证书 + COSE 签名",
    "removed_in_2_0": "训练与数据挖掘（training & data mining）断言在 2.0 版被删除",
}
CN_LABEL = {
    "name": "《人工智能生成合成内容标识办法》",
    "issuer": "国家网信办等四部门",
    "doc_no": "国信办通字〔2025〕2 号",
    "issued": "2025-03-07", "effective": "2025-09-01", "articles": 14,
    "explicit": "显式标识：在生成合成内容或交互界面中添加可感知的提示",
    "implicit": "隐式标识：在文件元数据中添加制作要素信息等",
}
SYNTHID_TEXT = {"journal": "Nature 634:818–823", "m": 30, "H": 4,
                "latency_overhead_pct": 0.57, "live_responses": 20_000_000,
                "tpr_at_fpr": UNPUBLISHED}
# 公开的版权诉讼（只记案卷事实，不作法律判断）
LAWSUITS = (
    ("Getty Images 诉 Stability AI（英国高等法院）", "IL-2023-000007", "2025-11-04 判决 [2025] EWHC 2863 (Ch)"),
    ("Getty Images 诉 Stability AI（美国特拉华）", "1:23-cv-00135", "2023-02-03 立案"),
    ("Andersen 等诉 Stability AI 等（美国北加州）", "3:23-cv-00201-WHO", "2023-01-13 立案"),
)
