"""算例 1.4.1～1.4.3：训练算力 C ≈ 6ND 的验证、训练时间的估算、算力增长的倍数。

式 (1.4.1)：C ≈ 6 N D；式 (1.4.2)：T = C / (n P u)；式 (1.4.3)：每年倍数 f = 2^{12/T_d}（T_d 为翻一番的月数）。
AlexNet 的训练算力按 1.5 节的逐层乘加数估计：每张图前向 2 × MAC 次运算，反向约为前向的 2 倍。
"""
import math

from _ch1 import ALEXNET, DOUBLING_MONTHS, EPOCH_PER_YEAR, GPT3, HW, LLAMA3, alexnet_layers
from bookout import out

# 算例 1.4.1：C ≈ 6ND 与论文公布的数比较
C_gpt3 = 6 * GPT3["N"] * GPT3["D"]
err_gpt3 = (C_gpt3 - GPT3["C_paper"]) / GPT3["C_paper"]
C_llama = 6 * LLAMA3["N"] * LLAMA3["D"]
err_llama = (C_llama - LLAMA3["C_paper"]) / LLAMA3["C_paper"]
tokens_per_param_gpt3 = GPT3["D"] / GPT3["N"]
tokens_per_param_llama = LLAMA3["D"] / LLAMA3["N"]

# 算例 1.4.2：训练要多久。T = C / (n P u)
u = 0.40
P_a100 = HW["a100"]["P_fp16"]
T1 = C_gpt3 / (1 * P_a100 * u)                    # 一块 A100
year = 365.25 * 86400
n_a = 1024
T_1024 = C_gpt3 / (n_a * P_a100 * u)
P_h100 = HW["h100"]["P_fp16"]
T_llama = C_llama / (LLAMA3["gpus"] * P_h100 * u)

# AlexNet 的训练算力（估算）
macs = sum(m for _, m, _ in alexnet_layers())
C_alex = 3 * 2 * macs * ALEXNET["train_images"] * ALEXNET["epochs"]

# 算例 1.4.3：算力增长
def per_year(doubling_months):
    return 2 ** (12 / doubling_months)


f_moore = per_year(DOUBLING_MONTHS["moore"])
f_pre = per_year(DOUBLING_MONTHS["pre_dl"])
f_dl = per_year(DOUBLING_MONTHS["dl"])
f_oai = per_year(DOUBLING_MONTHS["openai2018"])
td_4 = 12 * math.log(2) / math.log(EPOCH_PER_YEAR[0])
td_5 = 12 * math.log(2) / math.log(EPOCH_PER_YEAR[1])
ten_moore = f_moore ** 10
ten_dl = f_dl ** 10
ratio_gpt3_alex = C_gpt3 / C_alex
ratio_llama_alex = C_llama / C_alex
f_alex_gpt3 = ratio_gpt3_alex ** (1 / (GPT3["year"] - 2012))
f_alex_llama = ratio_llama_alex ** (1 / (LLAMA3["year"] - 2012))

out(C_gpt3=C_gpt3, C_gpt3_e=f"{C_gpt3:.2e}".replace("e+", "\\times10^{") + "}", C_gpt3_paper=GPT3["C_paper"],
    err_gpt3_pct=err_gpt3 * 100, C_llama_e=f"{C_llama:.2e}".replace("e+", "\\times10^{") + "}", err_llama_pct=err_llama * 100,
    tpp_gpt3=tokens_per_param_gpt3, tpp_llama=tokens_per_param_llama,
    u_pct=u * 100, P_a100_T=P_a100 / 1e12, T1_years=T1 / year, n_a=n_a, T_1024_days=T_1024 / 86400,
    P_h100_T=P_h100 / 1e12, n_h=LLAMA3["gpus"], T_llama_days=T_llama / 86400,
    C_alex_e=f"{C_alex:.1e}".replace("e+", "\\times10^{") + "}", C_alex=C_alex,
    f_moore=f_moore, f_pre=f_pre, f_dl=f_dl, f_oai=f_oai, td_4=td_4, td_5=td_5, ten_moore=ten_moore, ten_dl=ten_dl,
    ratio_gpt3_alex_e=f"{ratio_gpt3_alex:.1e}".replace("e+0", "\\times10^{").replace("e+", "\\times10^{") + "}",
    ratio_llama_alex_e=f"{ratio_llama_alex:.1e}".replace("e+0", "\\times10^{").replace("e+", "\\times10^{") + "}",
    f_alex_gpt3=f_alex_gpt3, f_alex_llama=f_alex_llama)
