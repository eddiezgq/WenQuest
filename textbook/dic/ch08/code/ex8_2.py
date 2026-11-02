"""8.2 节：静态时序分析。

算例 8.2.1  低成本版本的 PI 数据通路（不插流水线），时钟 50 MHz。把它画成时序图：寄存器的输出是起点（到达时间 = tcq），
            寄存器的输入是终点（要求时间 = T − tsu），各块是边（延时取第 6 章的综合结果）。从起点往后求到达时间（取各输入的最大），
            从终点往前求要求时间（取各输出的最小），余量 = 要求 − 到达，找出关键路径；最高时钟频率。
图 8.2.1    PI 数据通路的时序图：节点上标到达时间，红色为关键路径。
"""
from bookout import T, figure, out, style
from mos import ff_timing, P
import _draw as d
import _pi

ff = ff_timing()
b = _pi.blocks("cheap")
Tp = 1 / (P["problems"]["p81"]["f_MHz"] * 1e6)
tcq, tsu = ff["tcq"], ff["tsu"]
# 节点与边：（起点, 终点, 块名）
src = ["R", "Y", "KP", "KI", "I"]
edges = [("R", "e", "sub"), ("Y", "e", "sub"), ("KP", "p", "mul"), ("e", "p", "mul"), ("KI", "q", "mul"), ("e", "q", "mul"),
         ("I", "s", "add1"), ("q", "s", "add1"), ("p", "v", "add2"), ("s", "v", "add2"), ("v", "u", "sat"),
         ("s", "I_D", None), ("u", "U_D", None)]
order = ["R", "Y", "KP", "KI", "I", "e", "p", "q", "s", "v", "u", "I_D", "U_D"]
at = {n: tcq for n in src}
for n in order[5:]:
    at[n] = max(at[a] + (b[k][0] if k else 0.0) for a, c, k in edges if c == n)
rt = {"I_D": Tp - tsu, "U_D": Tp - tsu}
for n in reversed(order[:-2]):
    rt[n] = min(rt[c] - (b[k][0] if k else 0.0) for a, c, k in edges if a == n)
slack = {n: rt[n] - at[n] for n in order}
worst = min(slack.values())
# 关键路径：从最差的终点往回，每一步取决定到达时间的那条入边
crit, n = ["U_D"], "U_D"
while n not in src:
    n = max(((a, at[a] + (b[k][0] if k else 0.0)) for a, c, k in edges if c == n), key=lambda x: x[1])[0]
    crit.append(n)
crit = list(reversed(crit))
tmin = at["U_D"] + tsu
vals = dict(T_ns=Tp * 1e9, worst_ns=worst * 1e9, tmin_ns=tmin * 1e9, fmax=1e-6 / tmin,
            loop_ns=(tcq + b["add1"][0] + tsu) * 1e9, crit="→".join({"R": "r"}.get(n, n) for n in crit if not n.endswith("_D")))
for k, (dl, a) in b.items():
    vals[f"d_{k}"] = dl * 1e9
for n in order:
    vals[f"at_{n}"] = at[n] * 1e9
    vals[f"sl_{n}"] = slack[n] * 1e9
out(**vals)

# ---------------------------------------------------------------- 图 8.2.1
plt = style()
import matplotlib.patches as mp  # noqa: E402
fig, ax = plt.subplots(figsize=(8.6, 3.8))
pos = {"R": (0, 3), "Y": (0, 2), "KP": (2.2, 3.8), "KI": (2.2, 0.4), "I": (4.6, 0.0), "e": (1.4, 2.5), "p": (3.6, 3.1),
       "q": (3.6, 1.2), "s": (5.6, 1.2), "v": (7.0, 2.2), "u": (8.4, 2.2), "I_D": (6.6, 0.0), "U_D": (9.6, 2.2)}
lab = {"R": T("给定 r", "ref r"), "Y": T("反馈 y", "meas y"), "KP": "Kp", "KI": "Ki", "I": T("积分 I", "integ. I"),
       "I_D": T("I 的输入", "I input"), "U_D": T("输出 U", "out U")}
for a, c, k in edges:
    on = a in crit and c in crit
    (x0, y0), (x1, y1) = pos[a], pos[c]
    ax.annotate("", xy=(x1 - 0.18 * (1 if x1 > x0 else 0), y1), xytext=(x0 + 0.18, y0),
                arrowprops=dict(arrowstyle="->", color=d.PMOS if on else d.MUTED, lw=2.0 if on else 0.9))
for k, (x, y) in {"sub": (0.75, 2.75), "mul": (2.6, 2.0), "add1": (4.7, 1.0), "add2": (6.4, 1.95), "sat": (7.7, 2.42)}.items():
    ax.text(x, y, {"sub": T("减", "sub"), "mul": T("乘", "mul"), "add1": T("加", "add"), "add2": T("加", "add"), "sat": T("饱和", "sat")}[k]
            + f"\n{b[k][0] * 1e9:.1f}", fontsize=8, color=d.MUTED, ha="center")
for n, (x, y) in pos.items():
    reg = n in src or n.endswith("_D")
    on = n in crit
    if reg:
        ax.add_patch(mp.Rectangle((x - 0.32, y - 0.2), 0.64, 0.4, fill=False, ec=d.PMOS if on else d.INK, lw=1.4))
    else:
        ax.add_patch(mp.Circle((x, y), 0.13, color=d.PMOS if on else d.INK))
    ax.text(x, y + 0.32, lab.get(n, n), ha="center", fontsize=9)
    ax.text(x, y - 0.42, f"{at[n] * 1e9:.1f}", ha="center", fontsize=8.5, color=d.PMOS if on else d.NMOS)
ax.text(0, -0.6, T("节点下方的数：到达时间 / ns", "numbers below nodes: arrival time / ns"), fontsize=8.5, color=d.NMOS)
ax.set_xlim(-0.6, 10.2); ax.set_ylim(-0.8, 4.4); ax.axis("off")
figure(fig, "fig8_2_1")
