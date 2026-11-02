"""8.5 节：跨时钟域。

算例 8.5.1  编码器接口跑在 25 MHz，控制核跑在 50 MHz，每个电流环周期（20 kHz）要把一个 16 位的位置值送过去。
            (a) 16 位各自过两级同步器：位置从 0x7FFF 变到 0x8000 时，各位到达的时刻不同，可能采到的错误值；
            (b) 握手：发送方把数据放稳、翻转 req；req 在接收方过两级同步器，接收方取数后翻转 ack，ack 再过两级同步器回来。
                一次传送最长要几个周期、多少时间，够不够 20 kHz；
            (c) req 只过一级（后面紧接逻辑，只剩第 3 章算例 3.3.2 的 200 ps 余量）与过两级同步器时的 MTBF（第 3 章的模型；
                数值太大，按对数计算）。
图 8.5.1    握手传送一个字的时序（按时钟周期示意）。
"""
from bookout import T, figure, out, style
from mos import P, ff_timing, mtbf, sync_tr
import _draw as d

q = P["problems"]["p85"]
fs, fd = q["f_src_MHz"] * 1e6, q["f_dst_MHz"] * 1e6
ff = ff_timing()
# (a) 0x7FFF → 0x8000：16 位都变，若高位先被采到新值、低位还是旧值，得到 0xFFFF；反过来得到 0x0000
bad_hi, bad_lo = 0xFFFF, 0x0000
# (b) 握手：req 同步最多 2 个接收周期 + 1 个周期用来对齐，接收方取数 1 个周期；ack 同步最多 2 + 1 个发送周期，发送方 1 个周期
t_req = 3 / fd
t_take = 1 / fd
t_ack = 3 / fs
t_send = 1 / fs
t_word = t_req + t_take + t_ack + t_send
rate = 1 / t_word
loop = q["loop_kHz"] * 1e3
# (c) MTBF：req 每传一个字翻转一次，按 20 kHz 计；第一级后面的决断余量取第 3 章的 200 ps，第二级再多一个接收周期 − tcq − tsu
import math  # noqa: E402
slack = P["problems"]["p33"]["slack_ps"] * 1e-12
year = 365.25 * 86400


def log10_mtbf_years(n):
    tr = sync_tr(n, fd, slack)
    return (tr / ff["tau_m"] - math.log(ff["T0"] * fd * loop)) / math.log(10) - math.log10(year)


m1 = mtbf(sync_tr(1, fd, slack), fd, loop)
out(f_src=q["f_src_MHz"], f_dst=q["f_dst_MHz"], word=q["word"], loop_kHz=q["loop_kHz"], bad_hi=f"0x{bad_hi:04X}", bad_lo=f"0x{bad_lo:04X}",
    t_word_ns=t_word * 1e9, rate_M=rate / 1e6, margin_x=rate / loop, cyc_src=t_word * fs, m1_s=m1, m1_log10_y=log10_mtbf_years(1), m2_log10_y=log10_mtbf_years(2), tr2_ns=sync_tr(2, fd, slack) * 1e9,
    slack_ps=slack * 1e12, tau_m_ps=ff["tau_m"] * 1e12, m1_us=m1 * 1e6)

plt = style()
fig, ax = plt.subplots(figsize=(7.8, 2.8))
Tn = t_word * 1e9
sig = [("data", T("数据（16 位，发送方）", "data (16 bits, src)")), ("req", "req"), ("req_s", T("req 同步后（接收方）", "req synced (dst)")),
       ("ack", "ack"), ("ack_s", T("ack 同步后（发送方）", "ack synced (src)"))]
ev = {"data": 0, "req": 1 / fs * 1e9, "req_s": 1 / fs * 1e9 + t_req * 1e9, "ack": 1 / fs * 1e9 + (t_req + t_take) * 1e9,
      "ack_s": 1 / fs * 1e9 + (t_req + t_take + t_ack) * 1e9}
for i, (k, lab) in enumerate(sig):
    y = -i * 0.9
    t0 = ev[k]
    xs = [-20, t0, t0, Tn + 60]
    ys = [y, y, y + 0.5, y + 0.5]
    if k == "data":
        ax.fill_between([t0, Tn + 60], y, y + 0.5, color=d.MEAN, alpha=0.25)
        ax.text(t0 + 10, y + 0.12, T("位置值，保持不变", "position, held"), fontsize=8.5)
    ax.plot(xs, ys, color=d.NMOS if k.startswith("req") else (d.PMOS if k.startswith("ack") else d.MEAN), lw=1.6)
    ax.text(-25, y + 0.2, lab, ha="right", va="center", fontsize=9)
ax.annotate("", xy=(ev["ack_s"], -4.2), xytext=(0, -4.2), arrowprops=dict(arrowstyle="<->", lw=0.9))
ax.text(ev["ack_s"] / 2, -4.15, T(f"传送一个字约 {t_word * 1e9:.0f} ns", f"one word ≈ {t_word * 1e9:.0f} ns"), ha="center", va="bottom", fontsize=9)
ax.set_xlim(-170, Tn + 70); ax.set_ylim(-4.5, 0.8); ax.axis("off")
figure(fig, "fig8_5_1")
