"""第 4 章算例 4.2.2 那棵时钟树的偏斜（数值求解近端与远端的 50 % 时刻之差），第 3 章算例 3.2.2 和习题答案共用。"""
import sys
from pathlib import Path

from mos import P, VDD, Wmin, cin, gamma_self, r_ratio, req_n, req_p, wire_c, wire_r

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ch04" / "code"))
from _rc import Tree, t50  # noqa: E402


def skew_ch4():
    q42 = P["problems"]["p42"]
    r = r_ratio()
    R0 = (req_n(Wmin) + req_p(r * Wmin)) / 2
    C0 = cin(Wmin, r * Wmin)
    size = q42["driver_size"]
    lay, ww = q42["layer"], q42["w_um"]
    seg = lambda Lum: (wire_r(lay, ww) * Lum, wire_c(lay, ww) * Lum)  # noqa: E731
    tr = Tree(R0 / size, gamma_self() * C0 * size)
    j = tr.wire(0, *seg(q42["trunk_um"]), 40)
    near = tr.wire(j, *seg(q42["near_um"]), 20); tr.C[near] += q42["leaf_load_units"] * C0
    far = tr.wire(j, *seg(q42["far_um"]), 60); tr.C[far] += q42["leaf_load_units"] * C0
    el = tr.elmore()
    ts, V = tr.step(VDD, 6 * el[far], 6000)
    return t50(ts, V[:, far], VDD) - t50(ts, V[:, near], VDD)
