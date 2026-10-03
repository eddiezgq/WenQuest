"""Examples 1.2.1, 1.2.2: average annual growth rate and China's share, from the figures published in IFR World Robotics.

Eq. (1.2.1): N_t = N_0 (1 + r)^t; Eq. (1.2.2): r = (N_t / N_0)^{1/t} − 1.
The average annual growth rate is computed two ways: by taking the t-th root, and by logarithms. The two must agree,
and compounding at r for t years must return N_t / N_0.
"""
import math

from _ch1 import IFR, TIMELINE
from bookout import T, out


def grp(n):
    """Group the digits of a large number in threes: spaces in the Chinese edition (GB/T 15835), commas in English."""
    t = f"{int(round(n)):,}"
    return T(t.replace(",", " "), t)


def cagr(ratio, years):
    """Eq. (1.2.2)."""
    return ratio ** (1 / years) - 1


def cagr_log(ratio, years):
    """The same quantity by logarithms: ln(1 + r) = ln(ratio) / t."""
    return math.exp(math.log(ratio) / years) - 1


# Example 1.2.1: what yearly growth "doubling in ten years" amounts to
r10 = cagr(2.0, 10)
assert abs(r10 - cagr_log(2.0, 10)) < 1e-12
x = 1.0
for _ in range(10):
    x *= 1 + r10
assert abs(x - 2.0) < 1e-12                       # compounding for ten years doubles exactly
r_simple = 1.0 / 10                               # the 10% obtained by wrongly spreading "doubling" evenly over ten years
x_wrong = (1 + r_simple) ** 10                    # what 10% compounded for ten years actually gives

inst24 = IFR["inst_2024"]
inst14_max = inst24 / 2                            # "more than double ten years earlier": 2014 was below this number

# Forecast: 655,000 units in 2026 to 806,000 units in 2029
r_fc = cagr(IFR["fc_2029"] / IFR["fc_2026"], 3)
assert abs(r_fc - cagr_log(IFR["fc_2029"] / IFR["fc_2026"], 3)) < 1e-12

# Example 1.2.2: China's share
cn24, cn25 = IFR["country"][0][2], IFR["country"][0][3]
inst25 = inst24 * (1 + IFR["growth_2025"])        # IFR only says "over 600,000, up 11%"; estimated from the growth rate
assert inst25 > 600000
share24 = cn24 / inst24
share25 = cn25 / inst25
others25 = inst25 - cn25
stock25 = IFR["stock_2024"] * 1.09                 # operational stock up 9%
assert 4.95e6 < stock25 < 5.15e6                   # consistent with "about 5 million"
top5_24 = sum(c[2] for c in IFR["country"]) / inst24
top5_25 = sum(c[3] for c in IFR["country"]) / inst25

# A few intervals in the timeline
gap_word_unimate = 1961 - 1920
gap_unimate_cobot = 2008 - 1961
n_events = len(TIMELINE)

out(r10_pct=r10 * 100, x_wrong=x_wrong, inst24=inst24, inst14_max=inst14_max, r_fc_pct=r_fc * 100,
    fc26=IFR["fc_2026"], fc29=IFR["fc_2029"], cn24=cn24, cn25=cn25, inst25=inst25, share24_pct=share24 * 100,
    share25_pct=share25 * 100, others25=others25, stock24=IFR["stock_2024"], stock25=stock25,
    top5_24_pct=top5_24 * 100, top5_25_pct=top5_25 * 100, gap_word_unimate=gap_word_unimate,
    gap_unimate_cobot=gap_unimate_cobot, n_events=n_events,
    inst24_s=grp(inst24), stock24_s=grp(IFR["stock_2024"]), fc26_s=grp(IFR["fc_2026"]), fc29_s=grp(IFR["fc_2029"]),
    cn24_s=grp(cn24), cn25_s=grp(cn25), inst25_wan=inst25 / 1e4, inst25_s=grp(round(inst25, -3)),
    note=T("2025 年总安装量按 2024 年 542 076 台增长 11% 推算", "2025 total estimated as 542,076 units in 2024 plus 11%"))
