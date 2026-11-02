"""第 7 章部分习题的答案（章末“部分习题答案与提示”引用）。

7.1.1  8 KB（65536 位，32 位字）排成 256 行 × 256 列：列选比与存取时间（模型同算例 7.1.1）。
7.1.3  128 列的字线（307 μm）用 met1 与用 li1（第 4 章的参数）时的分布式 RC 延时。
7.3.4  一个 5 端口寄存器堆与两份 4 端口（2 读 2 写）的单元面积（算例 7.3.1 的粗估）。
7.1.2  位线摆幅从 100 mV 降到 50 mV（256 行 × 128 列）：位线时间、灵敏放大时间与存取时间。
7.2.2  VDD 降到 1.2 V、0.9 V 时，CR = 2 的单元读出 SNM（SKY130 仿真与手算模型）及占 VDD 的比例。
7.3.1  处理器每 50 μs 才来取一次：FIFO 至少存多少个、深度（2 的幂）与指针位数。
7.4.1  改为每秒记一次：用够 10 年要几块。
"""
import math

from bookout import out
from mos import P, sram_access, sram_snm

q71 = P["problems"]["p71"]
a = sram_access(256, 256, 32, q71["dv"])
b100 = sram_access(256, 128, 32, 0.1)
b50 = sram_access(256, 128, 32, 0.05)
sv = {v: r for v, r, _ in P["sram_sim"]["snm_vdd"]}
m = {v: sram_snm(2.0, 1.0, "read", v) for v in (0.9, 1.2, 1.8)}
q73 = P["problems"]["p73"]
fill = q73["f_in_MHz"] * 1e6 * 50e-6
depth = 1 << math.ceil(math.log2(fill + 1))
q74 = P["problems"]["p74"]
year = 365.25 * 24 * 3600
need1 = math.ceil(q74["years"] * year / (q74["endurance"] * q74["entries_per_sector"] * 1.0))
from mos import wire_r, WIRES  # noqa: E402
b = sram_access(256, 128, 32, q71["dv"])
L13 = 128 * q71["cell_w"]
r_m1 = wire_r("met1", WIRES["met1"]["wmin"]) * L13
r_li = wire_r("li1", WIRES["li1"]["wmin"]) * L13
q73r = P["problems"]["p73"]
rfx = lambda p: (q71["cell_w"] + (p - 1) * q73r["track_um"]) * (q71["cell_h"] + (p - 1) * q73r["track_um"]) / (q71["cell_w"] * q71["cell_h"])  # noqa: E731
out(a713_L=L13, a713_rm1=r_m1, a713_rli=r_li, a713_rli_k=r_li / 1e3, a713_tm1=0.38 * r_m1 * b["c_wl"] * 1e12, a713_tli=0.38 * r_li * b["c_wl"] * 1e12,
    a713_x=r_li / r_m1, a734_x5=rfx(5), a734_x4=rfx(4), a734_2x4=2 * rfx(4),
    a711_mux=a["mux"], a711_ps=a["total"] * 1e12, a711_bl=a["bl"] * 1e12, a711_dec=a["dec"] * 1e12, a711_N=a["dec_N"],
    a711_wl=a["wl"] * 1e12, a711_wl128=b["wl"] * 1e12, a711_dec128=b["dec"] * 1e12, a711_ps128=b["total"] * 1e12,
    a712_bl100=b100["bl"] * 1e12, a712_bl50=b50["bl"] * 1e12, a712_sa100=b100["sa"] * 1e12, a712_sa50=b50["sa"] * 1e12,
    a712_t100=b100["total"] * 1e12, a712_t50=b50["total"] * 1e12,
    a722_s18=sv[1.8], a722_s12=sv[1.2], a722_s09=sv[0.9], a722_f18=sv[1.8] / 1.8 * 100, a722_f12=sv[1.2] / 1.2 * 100,
    a722_f09=sv[0.9] / 0.9 * 100, a722_m09=m[0.9], a722_m12=m[1.2], a722_merr09=(m[0.9] / sv[0.9] - 1) * 100,
    a731_fill=fill, a731_depth=depth, a731_ptr=int(math.log2(depth)) + 1, a741_need=need1)
