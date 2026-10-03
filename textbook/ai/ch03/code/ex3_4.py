"""算例 3.4.1、程序 3.4.1：历代 GPU 的规格（conventions/gpus.py）：核对 FP32 峰值 = 核心数 × 2 × 频率；
算力与带宽各增长了多少倍、每年多少；平衡点 P/β 的变化（“存储墙”）。"""
from bookout import out
from gpus import GPUS

order = ["gtx580", "k40", "p100", "v100", "a100", "h100", "b200"]
for key in order:
    g = GPUS[key]
    if g["cores"]:
        calc = g["cores"] * 2 * g["clock"]
        assert abs(calc / g["fp32"] - 1) < 0.01, (key, calc, g["fp32"])
a, b = GPUS["gtx580"], GPUS["b200"]
years = b["year"] - a["year"]
g_fp32 = b["fp32"] / a["fp32"]
g_bw = b["bw"] / a["bw"]
g_ai = b["fp16t"] / a["fp32"]                         # AI 常用精度的峰值：B200 的 FP16 张量核心对 GTX 580 的 FP32
cagr = lambda r: r ** (1 / years)                     # noqa: E731
bal = {k: (GPUS[k]["fp16t"] or GPUS[k]["fp32"]) / GPUS[k]["bw"] for k in order}
bal32 = {k: GPUS[k]["fp32"] / GPUS[k]["bw"] for k in order}
tc_ratio_v100 = GPUS["v100"]["fp16t"] / GPUS["v100"]["fp32"]
tc_ratio_h100 = GPUS["h100"]["fp16t"] / GPUS["h100"]["fp32"]

tab = {}
for key in order:
    g = GPUS[key]
    tab[f"fp32_{key}"] = g["fp32"] / 1e12
    tab[f"t16_{key}"] = g["fp16t"] / 1e12 if g["fp16t"] else "—"
    tab[f"bw_{key}"] = g["bw"] / 1e9
    tab[f"mem_{key}"] = g["mem"] / 1e9
    tab[f"mhz_{key}"] = g["clock"] / 1e6 if g["clock"] else "—"
    tab[f"sm_{key}"] = g["sm"] if g["sm"] else "—"
    tab[f"cores_{key}"] = g["cores"] if g["cores"] else "—"
out(**tab, years=years, g_fp32=g_fp32, g_bw=g_bw, g_ai=g_ai, c_fp32=cagr(g_fp32), c_bw=cagr(g_bw), c_ai=cagr(g_ai),
    bal580=bal["gtx580"], bal_v100=bal["v100"], bal_a100=bal["a100"], bal_h100=bal["h100"], bal_b200=bal["b200"],
    bal32_580=bal32["gtx580"], bal32_h100=bal32["h100"], tc_v100=tc_ratio_v100, tc_h100=tc_ratio_h100,
    b200_fp16_P=b["fp16t"] / 1e15, b200_bw_T=b["bw"] / 1e12, b200_fp32_T=b["fp32"] / 1e12)
