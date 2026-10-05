"""2.7 节现场故障案例：KM1 的自锁触点接触不良。
（a）在指定时刻让自锁触点断开 2 ms、8 ms、16 ms，看接触器怎样反应（图 2.7.1）；
（b）让它在运转中随机断开（平均约 2.7 min 一次，一半在 5 ms 以内，最长约 31 ms），模拟一位见停就按启动的操作工，运行 1 小时，数打嗝和停车的次数。"""
from bookout import figure, out, T, style
from plcbook import read, run
from _draw02 import timing_ms, ACCENT, GREEN, WARM, RED, MUTED

prog = read("p2_3_1.st")
GAPS = [[800, 2], [1600, 8], [2400, 16]]
F = [{"set": {"S1_Fwd": True}}, {"wait": 300}, {"set": {"S1_Fwd": False}}]
FOP = [{"set": {"S1_Fwd": True}}, {"wait": 300}, {"release": ["S1_Fwd"]}]      # afterwards the simulated operator works the button
r = run(prog, plant="reversing", cycle=1, plant_opts={"gaps": GAPS},
        scenario={"steps": [*F, {"wait": 2700}], "trace": ["KM1_Aux", "KM1_Fwd", "KM1_Moving", "KM1_Closed", "speed"], "final": ["clacks", "drops"]})
fin = r["scenario"]["final"]
assert fin["clacks"] == 1 and fin["drops"] == 1, fin

HOUR = 3600 * 1000
rh = run(prog, plant="reversing", cycle=1, plant_opts={"operator": True},
         scenario={"faults": {"auxbad": True}, "steps": [*FOP, {"wait": HOUR}], "final": ["gaps", "clacks", "drops", "restarts"]})
h = rh["scenario"]["final"]
tr = r["scenario"]["trace"]


def draw():
    plt = style()
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.9), sharey=True)
    rows = [("KM1_Aux", T("KM1 自锁触点", "KM1 seal-in"), GREEN), ("KM1_Fwd", T("KM1 线圈", "KM1 coil")), ("KM1_Moving", T("衔铁动作中", "armature moving"), RED), ("KM1_Closed", T("KM1 主触点", "KM1 main"), WARM)]
    for ax, (t0, ms), title in zip(axs, GAPS, (T("（a）断开 2 ms：没有反应", "(a) open 2 ms: nothing"),
                                               T("（b）断开 8 ms：衔铁一松又吸回（打嗝）", "(b) open 8 ms: the armature clacks"),
                                               T("（c）断开 16 ms：接触器释放，电机停", "(c) open 16 ms: the contactor drops out"))):
        timing_ms(ax, tr, rows, -10, 40, zero=t0, title=title, labels=ax is axs[0])
        ax.title.set_fontsize(9.2)
    return fig


figure(draw(), "fig2_7_1")
out(gaps=h["gaps"], clacks=h["clacks"], drops=h["drops"], restarts=h["restarts"], shift_drops=round(h["drops"] * 8), shift_clacks=round(h["clacks"] * 8))
