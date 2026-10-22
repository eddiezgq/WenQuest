"""算例 14.2.1—14.2.4：一张图进了语言模型，要占多少词元（14.2 节）。

（1）视觉塔把一张图切成多少块：ViT 的 $N = HW/P^2$，用它核对 Qwen2-VL 报告里"224×224 一张图 66 个词元"。
（2）分辨率一提高，词元数按平方涨；注意力那两项按词元数的平方涨——于是提高一倍分辨率，代价是十六倍。
（3）一张 A4 图纸要多少词元：切片式动态分辨率（InternVL 1.5 的做法）与定分辨率的对照。
（4）把一页图纸和一页文字放在一起比：谁贵，贵多少；键值缓存要多占多少显存（回扣 9.4 节）。
"""
import numpy as np

from _ch14 import attn_cost, tiled_tokens, tokens_of
from bookout import out
from mm_facts import INTERNVL15, LLAVA15, QWEN2VL, vit_tokens

v = {}
# ---------- （1）词元是怎么数出来的
v["llava_res"], v["llava_patch"] = LLAVA15["res"], LLAVA15["patch"]
v["llava_tokens"] = tokens_of(LLAVA15["res"], LLAVA15["patch"])          # 576，按公式折算
v["llava_tokens_cls"] = vit_tokens(LLAVA15["res"], LLAVA15["patch"])     # 加上 [CLS] 是 577
assert v["llava_tokens"] == 576
# Qwen2-VL：块 14、再把相邻 2×2 合成 1 个，首尾各加一个标记。报告给的例子是 66 个
v["qwen_patch"], v["qwen_merge"] = QWEN2VL["patch"], QWEN2VL["merge"]
v["qwen_calc"] = tokens_of(224, QWEN2VL["patch"], merge=QWEN2VL["merge"], cls=2)
v["qwen_report"] = QWEN2VL["tokens_224"]
assert v["qwen_calc"] == v["qwen_report"], "按公式算出来的要与报告给的 66 对上"
v["merge_save"] = QWEN2VL["merge"] ** 2                                   # 2×2 合并省掉几倍

# ---------- （2）分辨率与代价
D_MODEL, LAYERS = 4096, 32                                                # 一个 7B 规模语言模型的尺寸
rows = []
for res in (224, 336, 448, 896):
    n = tokens_of(res, 14)
    rows.append((res, n, round(attn_cost(n, D_MODEL, LAYERS) / 1e12, 2)))  # 万亿次乘加
v["res_rows"] = rows
v["n_224"], v["n_896"] = rows[0][1], rows[-1][1]
v["res_ratio"] = rows[-1][0] / rows[0][0]
v["token_ratio"] = v["n_896"] / v["n_224"]
v["cost_ratio"] = attn_cost(v["n_896"], D_MODEL, LAYERS) / attn_cost(v["n_224"], D_MODEL, LAYERS)
assert abs(v["token_ratio"] - v["res_ratio"] ** 2) < 1e-9, "词元数按分辨率的平方涨"
assert abs(v["cost_ratio"] - v["res_ratio"] ** 4) < 1e-6, "注意力那两项按分辨率的四次方涨"

# ---------- （3）一张 A4 图纸要多少词元
DPI = 300
A4_W, A4_H = round(210 / 25.4 * DPI), round(297 / 25.4 * DPI)             # A4 = 210 × 297 mm
v["dpi"], v["a4_w"], v["a4_h"] = DPI, A4_W, A4_H
v["a4_mpx"] = A4_W * A4_H / 1e6
v["tile"], v["per_tile"] = INTERNVL15["tile"], INTERNVL15["tokens_per_tile"]
tok_tiled, n_tiles = tiled_tokens(A4_W, A4_H, INTERNVL15["tile"], INTERNVL15["tokens_per_tile"],
                                  max_tiles=INTERNVL15["tiles_test_max"])
v["a4_tiles"], v["a4_tokens"] = n_tiles, tok_tiled
v["internvl_max"] = INTERNVL15["tokens_test_max"]
v["internvl_train_max"] = INTERNVL15["tokens_train"][1]
# 如果不切片、硬塞进 336×336：一个汉字高多少像素
v["char_px_full"] = 3.0 * DPI / 25.4                                       # 3 mm 高的字在 300 dpi 下
v["char_px_shrunk"] = v["char_px_full"] * 336 / A4_H
assert v["char_px_shrunk"] < 4, "整页缩到 336 像素，3 毫米高的字只剩几个像素——读不出来"
v["a4_tokens_336"] = tokens_of(336, 14)
v["tile_vs_336"] = v["a4_tokens"] / v["a4_tokens_336"]

# ---------- （4）一页图纸 vs 一页文字
PAGE_CHARS = 800                                                           # 一页中文约 800 字
v["page_chars"] = PAGE_CHARS
v["text_tokens"] = PAGE_CHARS                                              # 中文大致一字一词元（13.1 节）
v["img_vs_text"] = v["a4_tokens"] / v["text_tokens"]
# 键值缓存：每个词元每层要存 K 和 V（9.4 节的口径，半精度）
KV_BYTES = 2 * 2 * D_MODEL * LAYERS                                        # K 与 V、每个数 2 字节
v["kv_per_token_kB"] = KV_BYTES / 1e3
v["kv_page_MB"] = v["a4_tokens"] * KV_BYTES / 1e6
v["kv_text_MB"] = v["text_tokens"] * KV_BYTES / 1e6
v["kv_10pages_GB"] = 10 * v["a4_tokens"] * KV_BYTES / 1e9
# 上面是"每个头各存一份"的口径。今天的模型多用分组查询注意力（9.4 节），K、V 由若干个头共用，
# 按 8 组算要再除以 8——即便如此，十页图纸仍是几个 GB
v["kv_10pages_gqa_GB"] = v["kv_10pages_GB"] / 8
assert v["kv_10pages_gqa_GB"] > 1, "十页图纸的键值缓存，即便用了分组查询注意力也要几个 GB"
# 一次推理里注意力那两项的乘加：图纸 vs 文字
v["tflops_page"] = attn_cost(v["a4_tokens"], D_MODEL, LAYERS) / 1e12
v["tflops_text"] = attn_cost(v["text_tokens"], D_MODEL, LAYERS) / 1e12
v["tflops_ratio"] = v["tflops_page"] / v["tflops_text"]
v["llava_tok_pretrain"] = LLAVA15["pretrain_pairs"]
out(**v)
