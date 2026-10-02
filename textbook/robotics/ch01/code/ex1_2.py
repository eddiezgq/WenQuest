"""算例 1.2.1、1.2.2：从 IFR《World Robotics》公布的数字算出年均增长率和中国所占份额。

式 (1.2.1)：N_t = N_0 (1 + r)^t；式 (1.2.2)：r = (N_t / N_0)^{1/t} − 1。
年均增长率用两种方法算：开 t 次方；取对数。两者必须一致，并且按 r 逐年复利 t 年必须回到 N_t / N_0。
"""
import math

from _ch1 import IFR, TIMELINE
from bookout import T, out


def grp(n):
    """大数按三位分节：中文版用空格（GB/T 15835），英文版用逗号。"""
    t = f"{int(round(n)):,}"
    return T(t.replace(",", " "), t)


def cagr(ratio, years):
    """式 (1.2.2)。"""
    return ratio ** (1 / years) - 1


def cagr_log(ratio, years):
    """同一个量用对数算：ln(1 + r) = ln(ratio) / t。"""
    return math.exp(math.log(ratio) / years) - 1


# 算例 1.2.1：“十年翻一番”相当于每年增长多少
r10 = cagr(2.0, 10)
assert abs(r10 - cagr_log(2.0, 10)) < 1e-12
x = 1.0
for _ in range(10):
    x *= 1 + r10
assert abs(x - 2.0) < 1e-12                       # 逐年复利十年，恰好翻一番
r_simple = 1.0 / 10                               # 误把“翻一番”平均分到十年得到的 10%
x_wrong = (1 + r_simple) ** 10                    # 按 10% 复利十年实际是多少倍

inst24 = IFR["inst_2024"]
inst14_max = inst24 / 2                            # “十年前的一半还不到”，即 2014 年少于这个数

# 预测：2026 年 65.5 万台到 2029 年 80.6 万台
r_fc = cagr(IFR["fc_2029"] / IFR["fc_2026"], 3)
assert abs(r_fc - cagr_log(IFR["fc_2029"] / IFR["fc_2026"], 3)) < 1e-12

# 算例 1.2.2：中国所占份额
cn24, cn25 = IFR["country"][0][2], IFR["country"][0][3]
inst25 = inst24 * (1 + IFR["growth_2025"])        # IFR 只说“超过 60 万台、增长 11%”，按增长率推算
assert inst25 > 600000
share24 = cn24 / inst24
share25 = cn25 / inst25
others25 = inst25 - cn25
stock25 = IFR["stock_2024"] * 1.09                 # 在役量增长 9%
assert 4.95e6 < stock25 < 5.15e6                   # 与“约 500 万台”相符
top5_24 = sum(c[2] for c in IFR["country"]) / inst24
top5_25 = sum(c[3] for c in IFR["country"]) / inst25

# 年表中的几个间隔
gap_word_unimate = 1961 - 1920
gap_unimate_cobot = 2008 - 1961
n_events = len(TIMELINE)

out(r10_pct=r10 * 100, x_wrong=x_wrong, inst24=inst24, inst14_max=inst14_max, r_fc_pct=r_fc * 100,
    fc26=IFR["fc_2026"], fc29=IFR["fc_2029"], cn24=cn24, cn25=cn25, inst25=inst25, share24_pct=share24 * 100,
    share25_pct=share25 * 100, others25=others25, stock24=IFR["stock_2024"], stock25=stock25,
    top5_24_pct=top5_24 * 100, top5_25_pct=top5_25 * 100, gap_word_unimate=gap_word_unimate,
    gap_unimate_cobot=gap_unimate_cobot, n_events=n_events,
    inst24_s=grp(inst24), stock24_s=grp(IFR["stock_2024"]), fc26_s=grp(IFR["fc_2026"]), fc29_s=grp(IFR["fc_2029"]),
    cn24_s=grp(cn24), cn25_s=grp(cn25), inst25_wan=inst25 / 1e4,
    note=T("2025 年总安装量按 2024 年 542 076 台增长 11% 推算", "2025 total estimated as 542,076 units in 2024 plus 11%"))
