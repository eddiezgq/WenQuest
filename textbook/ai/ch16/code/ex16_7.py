"""算例 16.7.1—16.7.3：内容标识是怎么做的，以及它的边界（16.7 节）。

（1）水印怎么嵌、怎么检：把一串按密钥生成的 ±1 加进内容没占满的那段频带，检测时高通之后求相关。
     干净时相关系数接近 1，没嵌或密钥不对时在 0 附近，于是门限可以按误报率定。
（2）它扛得住什么、扛不住什么：加噪、量化（压缩）、裁剪、重采样四种处理各掉多少。
（3）标识不是水印一种：显式标识、隐式标识、C2PA 的清单与签名，各管一段。国内的办法与
     C2PA 的规格各写了什么，照原文列。
（4）版权这一节只摆公开的案卷事实，不下法律判断。
"""
import numpy as np

from _ch16 import attack, content, detect, fp_threshold, watermark
from bookout import out
from gen_facts import C2PA, CN_LABEL, LAION, LAWSUITS, SYNTHID_TEXT

v = {}
N = 4096
KEY = 7
x = content(N, 0)
v["n_samples"] = N

# ---------- （1）嵌与检
STRENGTH = 0.05
w = watermark(x, KEY, STRENGTH)
v["strength"] = STRENGTH
v["snr_db"] = float(20 * np.log10(x.std() / (STRENGTH * 1.0)))     # 折算：内容与标记的幅度比
v["corr_clean"] = detect(w, KEY)
v["corr_unmarked"] = detect(x, KEY)
v["thr95"] = fp_threshold(w)
assert v["corr_clean"] > 0.9, "干净的带水印信号，相关系数接近 1"
assert abs(v["corr_unmarked"]) < 0.05, "没嵌水印的信号测出来在 0 附近"
assert v["corr_clean"] > 10 * v["thr95"], "干净信号与误报门限之间差一个数量级，门限好定"
v["thr_pick"] = 0.1
v["fp_rate"] = float(np.mean([abs(detect(w, k)) > v["thr_pick"] for k in range(2000, 2600)]))
assert v["fp_rate"] == 0.0, "门限定在 0.1，600 个错密钥一个都没误报"
v["n_wrong_keys"] = 600
# 强度曲线：标记越弱越听不出来，也越难检
v["strength_rows"] = [(s, round(detect(watermark(x, KEY, s), KEY), 3),
                       round(float(20 * np.log10(x.std() / s)), 1))
                      for s in (0.005, 0.01, 0.02, 0.05, 0.1)]
v["corr_weak"] = v["strength_rows"][0][1]
assert v["corr_weak"] > v["thr_pick"], "强度降到 0.5% 仍然检得出——但余量小了很多"

# ---------- （2）各种处理之后还剩多少
v["attack_rows"] = []
names = {"noise": "加噪声", "quantize": "量化（相当于压缩）", "crop": "截掉一段",
         "resample": "下采样再插回来"}
for kind in ("noise", "quantize", "crop", "resample"):
    row = [names[kind]]
    for lv in (0.1, 0.3, 0.5, 0.8):
        row.append(round(detect(attack(w, kind, lv), KEY), 3))
    v["attack_rows"].append(tuple(row))
keys = {"加噪声": "noise", "量化（相当于压缩）": "quant", "截掉一段": "crop",
        "下采样再插回来": "resamp"}
for row in v["attack_rows"]:
    k = keys[row[0]]
    for i, lv in enumerate((1, 3, 5, 8), start=1):
        v[f"atk_{k}_{lv}"] = row[i]
v["noise_08"] = v["atk_noise_8"]
v["quant_08"] = v["atk_quant_8"]
assert v["noise_08"] < v["thr_pick"] * 1.1, "噪声加到和内容一个量级，水印就检不出了"
assert v["quant_08"] > 3 * v["thr_pick"], "量化（压缩）这一类处理它扛得住"
# 把检不出来的那一档找出来：噪声强度多大时掉到门限以下
lv = 0.1
while lv < 2.0 and detect(attack(w, "noise", lv), KEY) > v["thr_pick"]:
    lv += 0.05
v["noise_break"] = round(lv, 2)
assert 0.3 < v["noise_break"] < 1.5, "存在一个明确的失效点——这就是水印的边界"

# ---------- （3）标识的几种做法
v["cn_name"] = CN_LABEL["name"]
v["cn_issuer"], v["cn_doc_no"] = CN_LABEL["issuer"], CN_LABEL["doc_no"]
v["cn_issued"], v["cn_effective"] = CN_LABEL["issued"], CN_LABEL["effective"]
v["cn_articles"] = CN_LABEL["articles"]
v["cn_explicit"], v["cn_implicit"] = CN_LABEL["explicit"], CN_LABEL["implicit"]
v["c2pa_parts"] = C2PA["parts"]
v["c2pa_binding"] = C2PA["binding"]
v["c2pa_crypto"] = C2PA["crypto"]
v["c2pa_removed"] = C2PA["removed_in_2_0"]
v["synthid_journal"] = SYNTHID_TEXT["journal"]
v["synthid_m"], v["synthid_H"] = SYNTHID_TEXT["m"], SYNTHID_TEXT["H"]
v["synthid_overhead"] = SYNTHID_TEXT["latency_overhead_pct"]
v["synthid_live_y"] = SYNTHID_TEXT["live_responses"] / 1e8
v["synthid_tpr_known"] = SYNTHID_TEXT["tpr_at_fpr"] is not None
assert not v["synthid_tpr_known"], "固定误报率下的检出率，这篇没给一个能单引的数"

# ---------- （4）版权：只摆案卷事实
v["n_lawsuits"] = len(LAWSUITS)
for i, (nm, no, st) in enumerate(LAWSUITS, start=1):
    v[f"suit{i}_name"], v[f"suit{i}_no"], v[f"suit{i}_state"] = nm, no, st
v["laion_stores_images"] = LAION["stores_images"]
v["laion_pairs_y"] = LAION["pairs"] / 1e8
v["laion_thr"] = LAION["clip_thr_en"]
assert not v["laion_stores_images"], "这个数据集只发网址与替代文字——正文写清楚这一点，不作推论"

out(**v)
