"""第 8 章的机器人问题：关节电机 PI 电流环的数据通路（书中程序 8.2.1、8.3.1 共用；浏览器实验 8.3 里有一份同样的 JS）。

    e = r − y（16 位减法）→ p = Kp·e、q = Ki·e（两个 16 × 16 乘法，并行）→ s = I + q（32 位加法，s 写回积分寄存器 I）
    → v = p + s（32 位加法）→ 饱和到 16 位 → 输出寄存器 U（送 PWM）。
各块的延时与面积取第 6 章按 SKY130 单元库的综合结果（params.json 的 arith_syn）：
    低成本版本（cheap）：行波进位、阵列乘法器，用“只求面积”的综合（delay_amin、area_min）；
    快速版本（fast）：Kogge–Stone 减法、Dadda 树乘法器、Brent–Kung 加法，用“尽量快”的综合（delay、area）。
减法用加法器（第二个数取反、进位输入为 1），取同位宽加法器的数；饱和电路用逻辑努力估算（mos.sat_delay），两种版本相同、不计面积。
"""
from mos import P, ff_timing, sat_delay

S = P["arith_syn"]
q81 = P["problems"]["p81"]
NAMES = [b[0] for b in q81["blocks"]]                     # sub, mul, add1, add2, sat
COUNT = {"sub": 1, "mul": 2, "add1": 1, "add2": 1, "sat": 1}
WIDTH = {"sub": 16, "mul": 64, "add1": 64, "add2": 32}    # 在这一块后面插一级寄存器要几个触发器：切口要切断所有往前走的边
# （mul 后面是 p、q 各 32 位；add1 后面是 s 和还没用上的 p，各 32 位；Kp、Ki 本身是寄存器，不算）


def blocks(style):
    """{块名: (延时 s, 面积 μm²)}，面积已乘个数（两个乘法器）。"""
    out = {}
    for name, cheap, fast in q81["blocks"]:
        if name == "sat":
            out[name] = (sat_delay(), 0.0)
            continue
        r = S[cheap if style == "cheap" else fast]
        d, a = (r["delay_amin"], r["area_min"]) if style == "cheap" else (r["delay"], r["area"])
        out[name] = (d * 1e-12, a * COUNT[name])
    return out


def stages(style, cuts):
    """cuts：在哪些块后面插寄存器（块名的集合，不含 sat）。返回各级的逻辑延时（s）列表、最小周期、积分回路的周期、寄存器位数。"""
    b, ff = blocks(style), ff_timing()
    st, cur = [], 0.0
    for n in NAMES:
        cur += b[n][0]
        if n in cuts:
            st.append(cur)
            cur = 0.0
    st.append(cur)
    loop = ff["tcq"] + b["add1"][0] + ff["tsu"]               # 积分回路 I → 加法 → I 永远只有一个加法器
    tmin = max(max(st) + ff["tcq"] + ff["tsu"], loop)
    return st, tmin, loop, sum(WIDTH[c] for c in cuts)


def area(style, cuts, ff_area):
    return sum(a for _, a in blocks(style).values()) + ff_area * sum(WIDTH[c] for c in cuts)
