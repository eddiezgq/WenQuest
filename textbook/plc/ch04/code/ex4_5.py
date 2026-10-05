"""图 4.5.1：三个任务的执行时间线（单核 CPU，抢占式优先级调度）。
主循环任务 Main：优先级最低，自由循环，每次执行 6 ms；周期任务 Fast：每 2 ms 一次，优先级高，执行 0.4 ms；
事件任务 Alarm：在 t = 7.3 ms 和 19.1 ms 由外部事件触发，优先级最高，执行 0.3 ms。按 1 µs 步长模拟。"""
from bookout import figure, out, T, style
from _draw04 import ACCENT, WARM, RED, MUTED, INK

DT = 0.001
TASKS = [("Alarm", 3, None, 0.3, [7.3, 19.1], RED), ("Fast", 2, 2.0, 0.4, None, WARM), ("Main", 1, 0.0, 6.0, None, ACCENT)]


def simulate(t_end=30.0):
    pending = {n: [] for n, *_ in TASKS}          # remaining execution of each released job
    runs = []                                     # (task, start, end)
    cur, start = None, 0.0
    main_done, main_rel = [], 0.0
    t = 0.0
    nextp = {"Fast": 0.0}
    ev = {"Alarm": list(TASKS[0][4])}
    pending["Main"].append(6.0); main_rel = 0.0
    while t < t_end - 1e-9:
        if nextp["Fast"] <= t + 1e-9:
            pending["Fast"].append(0.4); nextp["Fast"] += 2.0
        while ev["Alarm"] and ev["Alarm"][0] <= t + 1e-9:
            ev["Alarm"].pop(0); pending["Alarm"].append(0.3)
        run = next((n for n, *_ in TASKS if pending[n]), None)
        if run != cur:
            if cur is not None:
                runs.append((cur, start, t))
            cur, start = run, t
        if run:
            pending[run][0] -= DT
            if pending[run][0] <= 1e-9:
                pending[run].pop(0)
                if run == "Main":
                    main_done.append(t + DT - main_rel); main_rel = t + DT; pending["Main"].append(6.0)
        t += DT
    runs.append((cur, start, t))
    return [r for r in runs if r[0]], main_done


runs, cycles = simulate()


def draw():
    plt = style()
    fig, ax = plt.subplots(figsize=(9.6, 2.9))
    ys = {"Alarm": 2, "Fast": 1, "Main": 0}
    col = {n: c for n, *_, c in TASKS}
    for n, a, b in runs:
        ax.broken_barh([(a, b - a)], (ys[n] - 0.35, 0.7), facecolors=col[n])
    for t0 in TASKS[0][4]:
        ax.annotate("", xy=(t0, 2.4), xytext=(t0, 2.9), arrowprops=dict(arrowstyle="-|>", color=RED, lw=1))
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels([T("Main 循环任务（低）", "Main, cyclic (low)"), T("Fast 2 ms 周期任务（中）", "Fast, 2 ms periodic (mid)"),
                        T("Alarm 事件任务（高）", "Alarm, event (high)")], fontsize=8.6)
    ax.set_xlabel(T("时间 / ms", "time / ms"), fontsize=9)
    ax.set_xlim(0, 30); ax.set_ylim(-0.6, 3.0)
    for s in ("right", "top"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig


figure(draw(), "fig4_5_1")
out(main_cycle=round(sum(cycles) / len(cycles), 2), main_n=len(cycles), load=round(0.4 / 2 * 100))
