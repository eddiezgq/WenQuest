"""第 8 章部分习题的答案（章末“部分习题答案与提示”引用）。

8.1.1  100 MHz 时 tcq、tsu、偏斜、抖动共占周期的多少。
8.1.2  两个触发器直接相连（中间没有逻辑）时，接收端时钟最多能晚到多少而不违反保持时间。
8.3.2  拆开乘法器、两个加法也分开以后，最长的一级（输出加法 + 饱和）与积分回路。
8.4.2  按 8.4 节的时钟树（L = 3、size = 16）重算第 3 章算例 3.4.1 的时钟功耗；第 3 章示意值 1.5 时是多少。
"""
from bookout import out
from mos import P, ff_timing, htree
import _pi

ff = ff_timing()
q4 = P["problems"]["p84"]
q34 = P["problems"]["p34"]
h = htree(q4["levels"], q4["die_um"], q34["n_ff"], q4["size"], q4["layer"], q4["imb"], f=q34["f_MHz"] * 1e6)
over = ff["tcq"] + ff["tsu"] + h["skew"] + P["problems"]["p81"]["jitter_ps"] * 1e-12
b = _pi.blocks("cheap")
oh = ff["tcq"] + ff["tsu"]
st832 = b["add2"][0] + b["sat"][0] + oh
loop = b["add1"][0] + oh
out(a832_ns=st832 * 1e9, a832_f=1e-6 / max(st832, loop), a832_loop=loop * 1e9, a811_pct=over * 100e6 * 100, a811_ps=over * 1e12, a812_ps=(ff["tcq"] - ff["th"]) * 1e12,
    a842_mw=h["power"] * 1e3, a842_ff_mw=h["p_ff"] * 1e3, a842_ch3_mw=h["p_ff"] * 2.5 * 1e3, a842_ratio=h["ratio"])
