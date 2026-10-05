"""程序 3.3.1 的测试：一个会抖动的按钮按 10 次，输入滤波时间 0、1、3、10 ms 时计数器各数到几次；
画出一次按下时触点的实际信号和经 3 ms 滤波后 PLC 看到的信号（图 3.3.3）。扫描周期取 1 ms，让滤波的效果单独显现。"""
from bookout import figure, out, T, style
from plcbook import read, run
from _draw03 import ACCENT, GREEN, MUTED, WARM

IO = [{"name": "S1_Count", "addr": "%IX0.0", "dir": "in", "comment": ["计数按钮（常开）", "Count button (NO)"]},
      {"name": "S2_Reset", "addr": "%IX0.1", "dir": "in", "comment": ["清零按钮", "Reset button"]},
      {"name": "H1_Done", "addr": "%QX0.0", "dir": "out", "comment": ["到数指示灯", "Done lamp"]}]
# one press: the contact bounces for about 5 ms when it closes and about 2 ms when it opens (ms per state)
CLOSE = [1, 1, 2, 1]          # on 1 ms, off 1 ms, on 2 ms, off 1 ms … then stays on (bounce about 5 ms)
OPEN = [1, 1]                 # off, on … then stays off


def press(hold=200, rest=300):
    st = []
    v = True
    for d in CLOSE:
        st += [{"set": {"S1_Count": v}}, {"wait": d}]; v = not v
    st += [{"set": {"S1_Count": True}}, {"wait": hold}]
    v = False
    for d in OPEN:
        st += [{"set": {"S1_Count": v}}, {"wait": d}]; v = not v
    st += [{"set": {"S1_Count": False}}, {"wait": rest}]
    return st


N = 10
steps = [s for _ in range(N) for s in press()]
prog = read("p3_3_1.st")
counts = {}
for f in (0, 1, 3, 10):
    r = run(prog, io=IO, cycle=1, filter=f, scenario={"steps": steps, "final": ["cnt.CV"]})
    counts[f] = r["scenario"]["final"]["cnt.CV"]
assert counts[3] == N and counts[0] > N, counts
one = run(prog, io=IO, cycle=1, filter=3, scenario={"steps": [{"wait": 5}] + press(30, 30), "trace": ["S1_Count"]})
tr = one["scenario"]["trace"]

# the raw contact signal of the same press, rebuilt from the steps
raw_t, raw_v, t, v = [], [], 5, False
raw_t.append(0); raw_v.append(False)
for d in CLOSE:
    v = not v; raw_t.append(t); raw_v.append(v); t += d
raw_t.append(t); raw_v.append(True); t += 30
v = True
for d in OPEN:
    v = not v; raw_t.append(t); raw_v.append(v); t += d
raw_t.append(t); raw_v.append(False); raw_t.append(t + 30); raw_v.append(False)
t_raw_on = 5
t_img_on = next(tt for tt, x in zip(tr["t"], tr["v"][0]) if x)


def draw():
    plt = style()
    fig, ax = plt.subplots(figsize=(9, 3.0))
    ax.step(raw_t, [1.4 + 0.8 * x for x in raw_v], where="post", color=GREEN, lw=1.5)
    ax.step(tr["t"], [0.8 * x for x in tr["v"][0]], where="post", color=ACCENT, lw=1.5)
    ax.text(-1, 1.75, T("触点", "contact"), ha="right", va="center", fontsize=9)
    ax.text(-1, 0.35, T("滤波后", "after the filter"), ha="right", va="center", fontsize=9)
    ax.annotate("", xy=(t_img_on, 0.95), xytext=(t_raw_on, 0.95), arrowprops=dict(arrowstyle="<->", color=WARM, lw=1))
    ax.text((t_raw_on + t_img_on) / 2, 1.0, T(f"{t_img_on - t_raw_on:.0f} ms", f"{t_img_on - t_raw_on:.0f} ms"), ha="center", va="bottom",
            fontsize=8.5, color=WARM)
    ax.set_xlim(0, raw_t[-1])
    ax.set_ylim(-0.3, 2.5)
    ax.set_yticks([])
    ax.set_xlabel(T("时间 / ms", "time / ms"), fontsize=9)
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    return fig


figure(draw(), "fig3_3_3")
out(n=N, c0=counts[0], c1=counts[1], c3=counts[3], c10=counts[10], delay=t_img_on - t_raw_on)
