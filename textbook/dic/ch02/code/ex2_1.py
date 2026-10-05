"""2.1 节：静态 CMOS 门的串并联结构。

算例 2.1.1  关节使能逻辑 EN = ¬(ESTOP + LIM·DIR)：用开关网络逐个输入组合核对上拉、下拉网络互补，
            比较一个复合门（与或非门 AOI21）与“与门 + 或非门”分立实现的管子数和级数。
图 2.1.1    二输入与非门、或非门的晶体管级电路。
图 2.1.2    关节使能逻辑的与或非门。
"""
import itertools

import matplotlib.pyplot as plt  # noqa: F401  （style() 返回同一个模块）
import schemdraw

from bookout import T, figure, out, style
import _draw as d

# ---------------------------------------------------------------- 开关网络：('s', a, b) 串联，('p', a, b) 并联，字符串是输入名


def conducts(net, v, pmos=False):
    """网络是否导通：NMOS 在输入为 1 时导通，PMOS 在输入为 0 时导通。"""
    if isinstance(net, str):
        return (not v[net]) if pmos else bool(v[net])
    op, *kids = net
    res = [conducts(k, v, pmos) for k in kids]
    return all(res) if op == "s" else any(res)


def dual(net):
    """上拉网络是下拉网络的对偶：串联换并联、并联换串联。"""
    if isinstance(net, str):
        return net
    op, *kids = net
    return ("p" if op == "s" else "s", *[dual(k) for k in kids])


def count(net):
    return 1 if isinstance(net, str) else sum(count(k) for k in net[1:])


def check(pd, names, f):
    """逐个输入组合：恰有一个网络导通，输出 = ¬f。返回组合数。"""
    pu = dual(pd)
    n = 0
    for bits in itertools.product((0, 1), repeat=len(names)):
        v = dict(zip(names, bits))
        down, up = conducts(pd, v), conducts(pu, v, pmos=True)
        assert down != up, (v, down, up)              # 互补：不会同时导通，也不会都断开
        assert up == (not f(v))
        n += 1
    return n


GATES = {
    "nand2": (("s", "A", "B"), ["A", "B"], lambda v: v["A"] and v["B"]),
    "nor2": (("p", "A", "B"), ["A", "B"], lambda v: v["A"] or v["B"]),
    "nand3": (("s", "A", "B", "C"), ["A", "B", "C"], lambda v: v["A"] and v["B"] and v["C"]),
    "aoi21": (("p", "A", ("s", "B", "C")), ["A", "B", "C"], lambda v: v["A"] or (v["B"] and v["C"])),
}
rows = {k: check(*g) for k, g in GATES.items()}
pd = GATES["aoi21"][0]
n_aoi = 2 * count(pd)                                   # 下拉 3 个 + 上拉 3 个
n_sep = (4 + 2) + 4                                     # 与门 = 与非门 4 管 + 反相器 2 管；再接或非门 4 管
out(n_comb=rows["aoi21"], n_aoi=n_aoi, n_sep=n_sep, save_pct=(1 - n_aoi / n_sep) * 100)

# 关节使能：哪些组合下 EN = 0（电机断开）
off = [v for v in itertools.product((0, 1), repeat=3) if (v[0] or (v[1] and v[2]))]
out(n_off=len(off))

# ---------------------------------------------------------------- 图 2.1.1：与非门、或非门
plt_ = style()
fig, (a1, a2) = plt_.subplots(1, 2, figsize=(8.2, 4.6))
with schemdraw.Drawing(show=False) as dr:
    n = d.Net(dr)
    n.rail(0.2, 4.6, 8, "VDD")
    for x, g in ((1.6, "A"), (4.2, "B")):
        n.line((x, 8), (x, 7.7)); n.pfet(x, 7.7, g); n.line((x, 6.2), (x, 5.9))
    n.line((1.6, 5.9), (4.2, 5.9)); n.dot((2.9, 5.9)); n.line((4.2, 5.9), (5.2, 5.9)); n.text((5.3, 5.9), "Y", loc="right")
    n.line((2.9, 5.9), (2.9, 5.5)); y = n.nfet(2.9, 5.5, "A"); y = n.nfet(2.9, y, "B"); n.ground((2.9, y))
    d.schem_to_ax(dr, a1)
a1.set_title(T("(a) 二输入与非门：NMOS 串联、PMOS 并联", "(a) NAND2: series NMOS, parallel PMOS"), fontsize=10.5)
with schemdraw.Drawing(show=False) as dr:
    n = d.Net(dr)
    n.rail(1.4, 4.4, 9.2, "VDD")
    n.line((2.9, 9.2), (2.9, 8.9)); y = n.pfet(2.9, 8.9, "A"); y = n.pfet(2.9, y, "B"); n.line((2.9, y), (2.9, 5.6))
    n.dot((2.9, 5.6)); n.line((1.6, 5.6), (4.2, 5.6)); n.line((4.2, 5.6), (5.2, 5.6)); n.text((5.3, 5.6), "Y", loc="right")
    for x, g in ((1.6, "A"), (4.2, "B")):
        n.line((x, 5.6), (x, 5.3)); yy = n.nfet(x, 5.3, g); n.line((x, yy), (x, 3.5))
    n.line((1.6, 3.5), (4.2, 3.5)); n.ground((2.9, 3.5))
    d.schem_to_ax(dr, a2)
a2.set_title(T("(b) 二输入或非门：NMOS 并联、PMOS 串联", "(b) NOR2: parallel NMOS, series PMOS"), fontsize=10.5)
figure(fig, "fig2_1_1")

# ---------------------------------------------------------------- 图 2.1.2：与或非门 Y = ¬(A + B·C)
fig, ax = plt_.subplots(figsize=(5.6, 5.4))
with schemdraw.Drawing(show=False) as dr:
    n = d.Net(dr)
    n.rail(1.2, 5.0, 10.6, "VDD")
    n.line((3.1, 10.6), (3.1, 10.3)); y = n.pfet(3.1, 10.3, "A")            # A 的 PMOS 在上
    n.line((3.1, y), (3.1, 8.6)); n.dot((3.1, 8.6)); n.line((1.8, 8.6), (4.4, 8.6))
    for x, g in ((1.8, "B"), (4.4, "C")):                                    # B、C 的 PMOS 并联
        n.line((x, 8.6), (x, 8.3)); yy = n.pfet(x, 8.3, g); n.line((x, yy), (x, 6.5))
    n.line((1.8, 6.5), (4.4, 6.5)); n.dot((3.1, 6.5)); n.line((4.4, 6.5), (5.6, 6.5)); n.text((5.7, 6.5), "EN", loc="right")
    n.line((1.8, 6.5), (1.8, 6.2)); yy = n.nfet(1.8, 6.2, "A"); n.line((1.8, yy), (1.8, 2.9))   # A 的 NMOS 单独一路
    n.line((4.4, 6.5), (4.4, 6.2)); yy = n.nfet(4.4, 6.2, "B"); yy = n.nfet(4.4, yy, "C"); n.line((4.4, yy), (4.4, 2.9))  # B·C 串联
    n.line((1.8, 2.9), (4.4, 2.9)); n.ground((3.1, 2.9))
    d.schem_to_ax(dr, ax)
ax.set_title(T("EN = ¬(A + B·C)：A = ESTOP（急停），B = LIM（限位），C = DIR（朝限位方向）", "EN = ¬(A + B·C): A = ESTOP, B = LIM (limit), C = DIR (towards the limit)"), fontsize=9.5)
figure(fig, "fig2_1_2")
