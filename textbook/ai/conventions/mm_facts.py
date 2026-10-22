"""多模态模型的公开发表数字（第 14 章用；第 11、12、24 章可引）。

规矩与 `llm_facts.py` 相同：**只收论文正文、官方技术报告或官方公告给出的原始数字**；
二手概括、第三方排行榜不收；厂商未公布的项用 `UNPUBLISHED` 标出，正文一律写“未公布”。
凡是由分辨率、块大小或像素界**折算**出来的数（论文自己没写），函数名或注释里标明“折算”。
每条的出处、口径与“为什么不能横向比较”见
`docs/教材/人工智能/参考/第14章_多模态原始数字资料_2026-10.md`。核对日期：2026 年 10 月 21 日。
"""

UNPUBLISHED = None                      # 厂商未公布：正文写“未公布”

# ---------------------------------------------------------------- 对比学习的两篇打底工作
# Radford 等 2021（CLIP，论文正文 2.2—2.5 节、3.1.3 节）
CLIP = {
    "pairs": 400_000_000,               # WIT：4 亿图文对（50 万查询 × 每查询最多 2 万对）
    "in1k_zeroshot_top1": 76.2,         # 零样本，ViT-L/14@336px
    "in1k_zeroshot_top5": 95.0,
    "in1k_supervised_top1": 85.4,       # 有监督适配，不是零样本
    "batch": 32_768,
    "rn_gpus": 592, "rn_days": 18,      # 最大 ResNet（RN50x64）：592 块 V100 × 18 天
    "vit_gpus": 256, "vit_days": 12,    # 最大 ViT（ViT-L/14）：256 块 V100 × 12 天
    "epochs": 32,
    "logit_scale_cap": 100.0,           # 可学习温度，截断使 logits 放大不超过 100 倍
    "temp_init": 0.07,                  # 初值等效 0.07
}
# Jia 等 2021（ALIGN，论文正文 3、5 节与表 1、表 4）
ALIGN = {
    "pairs": 1_800_000_000,             # 18 亿噪声 alt-text 对，不做人工清洗
    "in1k_zeroshot_top1": 76.4,
    "in1k_finetune_top1": 88.64,        # 微调，不是零样本
    "batch": 16_384,
    "tpu_cores": 1024, "steps": 1_200_000,
    "temp_init": 1.0,                   # 可学习温度，消融里收敛到约 1/64
}
# Zhai 等 2023（SigLIP，论文正文 3.2、4.1—4.3 节与表 4）
SIGLIP = {
    "batch_min": 512, "batch_max": 1_000_000,    # 实验范围
    "batch_enough": 32_768,             # 原话：“一个合理的批大小，即 32k，对图文预训练已经够用”
    "softmax_peak_batch": 98_000,       # 同篇里 softmax 版要 98k 才达峰
    "sigmoid_wins_below": 16_000,       # 批小于 16k 时 sigmoid 明显胜过 softmax
    "bias_init": -10.0, "bias_in1k": 63.0, "nobias_in1k": 61.7,   # 表 4：可学习偏置的消融
    "mem_sig": 4096, "mem_clip": 2048,  # 4 块 TPUv4 上 Base 规模能放下的批
}

# ---------------------------------------------------------------- 视觉词元是怎么数出来的
# Dosovitskiy 等 2020（ViT，论文正文 3.1 节式 1、表 1）
VIT_TOKENS_FORMULA = "N = HW / P^2"     # 论文原话给的就是这个公式；另加 1 个 [CLS]
VIT_SIZES = {                           # （层, 隐藏维, MLP 维, 头数, 参数量）
    "Base": (12, 768, 3072, 12, 86_000_000),
    "Large": (24, 1024, 4096, 16, 307_000_000),
    "Huge": (32, 1280, 5120, 16, 632_000_000),
}


def vit_tokens(res: int, patch: int, cls: bool = True) -> int:
    """按 ViT 的公式折算词元数（论文给公式，不给具体的数；教材按“折算”口径写）。"""
    assert res % patch == 0, "分辨率要能被块大小整除"
    return (res // patch) ** 2 + (1 if cls else 0)


# ---------------------------------------------------------------- 三段式：视觉塔 + 连接器 + 语言模型
# Liu 等 2023（LLaVA，论文正文 3—5 节与附录 C）
LLAVA = {
    "instruct": 158_000, "conv": 58_000, "detail": 23_000, "reason": 77_000,
    "align_pairs": 595_000,             # 第一阶段：CC3M 过滤后 595K，只训投影矩阵
    "gpus": 8, "stage1_hours": 4, "stage2_hours": 10,   # 8 块 A100
    "batch_pre": 128, "batch_sft": 32,
    "vision_tokens": UNPUBLISHED,       # 初版论文没写视觉词元个数
}
# Liu 等 2023（LLaVA-1.5，论文正文 3.3 节、表 3、表 7）
LLAVA15 = {
    "res": 336, "patch": 14,            # 视觉塔 CLIP-ViT-L-336px；576 个视觉词元是按公式折算
    "pretrain_pairs": 558_000, "sft": 665_000,
    "gpus": 8, "pretrain_hours": 6, "sft_hours": 20,
    "vqav2_13b": 80.0, "sciqa_13b": 71.6, "textvqa_13b": 61.3,
}
# Wang 等 2024（Qwen2-VL 官方技术报告 2.1、2.2、3.3 节与表 2）
QWEN2VL = {
    "patch": 14, "merge": 2,            # ViT 之后把相邻 2×2 的词元合成 1 个
    "tokens_224": 66,                   # 报告直接给的例子：224×224 一张图 66 个词元
    "video_token_cap": 16_384,
    "vision_params": 675_000_000,
    "train_tokens": 1_400_000_000_000,
    "docvqa": 96.5, "chartqa": 88.3,
}
# Chen 等 2024（InternVL 1.5 官方技术报告 3.1、3.3 节）——少数直接给出词元范围的报告
INTERNVL15 = {
    "tile": 448, "tokens_per_tile": 256,
    "tiles_train": (1, 12), "tiles_test_max": 40,
    "tokens_train": (256, 3328), "tokens_test_max": 10_496,   # 报告原值，已含缩略图
    "params": 26_000_000_000, "docvqa": 90.9, "chartqa": 83.8,
}
# Alayrac 等 2022（Flamingo，论文正文 2.1—2.4 节、表 1）
FLAMINGO = {
    "resampler_tokens": 64,             # 不管输入多少特征，固定输出 64 个视觉词元
    "m3w_pages": 43_000_000, "m3w_L": 256, "m3w_N": 5,
    "ltip_pairs": 312_000_000, "vtp_clips": 27_000_000,
    "xattn_every_9b": 4, "xattn_every_80b": 7,
    "coco_cider": {0: 84.3, 4: 103.2, 32: 113.8},     # 必须连 shot 数一起引
    "vqav2_top1": {0: 56.3, 4: 63.1, 32: 67.6},
    "tpu_chips": 1536, "tpu_days": 15,  # 论文只写 “TPU chips”，未写代次
}

# ---------------------------------------------------------------- 视觉—语言—动作
# Brohan / Zitkovich 等 2023（RT-2，论文正文 3.2、3.3、4 节与表 4、表 5）
RT2 = {
    "action_fields": 8,                 # 终止 + 6 自由度增量 + 夹爪
    "bins": 256,
    "hz_55b": (1, 3), "hz_5b": 5.0,
    "unseen_55b": 62, "unseen_rt1": 32, "unseen_moo": 35,
    "seen_55b": 91, "seen_rt1": 92,
    "emergent_55b": 60, "emergent_rt1": 17,
    "params_55b": 55_000_000_000, "params_12b": 12_000_000_000,
}
# Kim 等 2024（OpenVLA，论文正文 3.1—3.5、5.1—5.4 节与表 2、表 4）
OPENVLA = {
    "params": 7_000_000_000, "res": 224,
    "action_dims": 7, "bins": 256, "quantile": (1, 99),   # 按第 1—99 分位数划分，不用极值
    "hz_4090": 6.0, "hz_int8": 1.2, "hz_int4": 3.0,
    "mem_bf16_gb": 16.8, "mem_int8_gb": 10.2, "mem_int4_gb": 7.0,
    "succ_bf16": 71.3, "succ_int8": 58.1, "succ_int4": 71.9,
    "demos": 970_000, "gpus": 64, "days": 14, "a100_hours": 21_500, "batch": 2048,
    "ctrl_hz": (5, 15),                 # 真机控制器频率，与模型推理频率是两件事
    "over_rt2x_points": 16.5,           # 绝对百分点，不是相对提升
    "bridge_openvla": 70.6, "bridge_rt2x": 50.6,
}

# ---------------------------------------------------------------- 跨模态检索（口径最容易出错）
# 数值取自各论文表格；CLIP 一行是 BLIP-2 表 5 的转引（CLIP 原论文自报值在附录，未核到）
# 每项为 (R@1, R@5, R@10)
RETRIEVAL = {
    "align_flickr_zs_i2t": (88.6, 98.7, 99.7), "align_flickr_zs_t2i": (75.7, 93.8, 96.8),
    "align_coco5k_zs_i2t": (58.6, 83.0, 89.7), "align_coco5k_zs_t2i": (45.6, 69.8, 78.6),
    "align_coco5k_ft_i2t": (77.0, 93.5, 96.9), "align_coco5k_ft_t2i": (59.9, 83.3, 89.8),
    "clip_flickr_zs_i2t": (88.0, 98.7, 99.4), "clip_flickr_zs_t2i": (68.7, 90.6, 95.2),
    "blip2g_flickr_zs_i2t": (97.6, 100.0, 100.0), "blip2g_flickr_zs_t2i": (89.7, 98.1, 98.9),
}
RETRIEVAL_NOTE = "COCO 5K 与 1K 是两套测试集；零样本与微调也不可混引"

# ---------------------------------------------------------------- 文档与图表理解
# Mathew 等 2020（DocVQA 论文正文 3.1、5.1 节与表 1、表 3）
DOCVQA = {
    "questions": 50_000, "images": 12_767, "docs": 6071,
    "train_q": 39_463, "val_q": 5349, "test_q": 5188,
    "human_anls": 0.981, "human_acc": 94.36,
    "bert_anls": 0.665, "bert_acc": 55.77,     # 同一模型：ANLS 与 Accuracy 差得很远
    "metric": "ANLS（平均归一化编辑距离相似度）",
}
# Masry 等 2022（ChartQA 论文正文 3.1、5.1—5.3 节与表 2、表 6）
CHARTQA = {
    "human_q": 9608, "machine_q": 23_111, "human_img": 4804, "machine_img": 17_141,
    "tolerance_pct": 5.0,               # relaxed accuracy：数值答案相差 5% 以内判对
    "best_h": 40.08, "best_m": 63.60, "best_all": 51.84,   # 表 6 不给数据表时的最好基线
}

# ---------------------------------------------------------------- 未公布（正文一律写“未公布”）
GPT4V = {"params": UNPUBLISHED, "vision_tower": UNPUBLISHED, "tokens_per_image": UNPUBLISHED,
         "train_flops": UNPUBLISHED, "data": UNPUBLISHED}
GEMINI = {"ultra_params": UNPUBLISHED, "pro_params": UNPUBLISHED, "train_flops": UNPUBLISHED,
          "nano1_params": 1_800_000_000, "nano2_params": 3_250_000_000}   # 只有 Nano 两档是报告给的
