"""4.4 节：上料输送线从末端光电开关动作到接触器断开的响应时间。蒙特卡洛：光电开关在随机时刻动作（与扫描不同步），
输入滤波 Tf = 3 ms，扫描周期 Tcyc = 10 ms（扫描时间在 9–11 ms 间随机抖动），晶体管输出 0.5 ms 或继电器输出 10 ms，接触器释放 12–20 ms。
最坏值公式：T_resp,max = Tf + 2·Tcyc,max + T_out + T_dev；最好值：Tf + Tcyc,min（输入恰在读输入之前稳定）+ T_out + T_dev,min。"""
import random
from bookout import figure, out, T, style
from _draw04 import ACCENT, WARM, MUTED, RED

random.seed(4)
TF, OUT_TR, OUT_RL = 3.0, 0.5, 10.0


def one(out_delay):
    # scans start at t_k; scan lengths jitter 9–11 ms; the input is read at the start of each scan (after the filter)
    t, starts = -50.0, []
    while t < 60:
        starts.append(t); t += random.uniform(9, 11)
    e = random.uniform(0, 10)                     # the sensor switches at e (ms)
    ready = e + TF                                # the filtered signal is valid from here
    k = next(i for i, s in enumerate(starts) if s >= ready)
    end_of_scan = starts[k + 1]                   # outputs are written at the end of that scan
    dev = random.uniform(12, 20)                  # contactor drop-out
    return end_of_scan + out_delay + dev - e


N = 20000
tr = [one(OUT_TR) for _ in range(N)]
rl = [one(OUT_RL) for _ in range(N)]
worst_formula = TF + 2 * 11 + OUT_TR + 20
best_formula = TF + 9 + OUT_TR + 12


def draw():
    plt = style()
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    ax.hist(tr, bins=60, color=ACCENT, alpha=0.75, label=T("晶体管输出", "transistor output"))
    ax.hist(rl, bins=60, color=WARM, alpha=0.6, label=T("继电器输出", "relay output"))
    ax.axvline(worst_formula, color=RED, lw=1, ls=(0, (4, 3)))
    ax.text(worst_formula + 0.5, ax.get_ylim()[1] * 0.85, T("公式算的最坏值（晶体管）", "worst case by formula (transistor)"), fontsize=8.2, color=RED)
    ax.set_xlabel(T("从光电开关动作到接触器断开 / ms", "from sensor to contactor open / ms"), fontsize=9)
    ax.set_yticks([])
    ax.legend(frameon=False, fontsize=8.6)
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    return fig


figure(draw(), "fig4_4_1")
out(tr_min=round(min(tr), 1), tr_max=round(max(tr), 1), tr_mean=round(sum(tr) / N, 1), rl_max=round(max(rl), 1), rl_mean=round(sum(rl) / N, 1),
    worst=round(worst_formula, 1), best=round(best_formula, 1), mm_worst=round(0.25 * worst_formula, 1), worst_rl=round(TF + 22 + OUT_RL + 20, 1))
