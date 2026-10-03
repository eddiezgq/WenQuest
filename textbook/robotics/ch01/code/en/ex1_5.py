"""Computations for Section 1.5: handling and machine loading in the digital factory workshop, and a few figures from medicine and the home.

Example 1.5.1  Output shaft SH-301 goes once through the workshop along its process route: the route length of each move
               (the same layout and routing algorithm as the factory simulation), the handling time, compared with the machining time.
Example 1.5.2  Time each work centre is occupied per reducer, daily capacity of one shift, the bottleneck; are two AGVs enough?
Example 1.5.3  Can a UR5e (rated payload 5 kg) carry the various blanks directly: mass from dimensions and density.
Example 1.5.4  Robot vacuum: how long row-by-row planned cleaning and random bump-and-turn cleaning take. The coverage formula
               c = 1 − e^{−n} is checked with a random experiment.
Also: simple conversions of the da Vinci procedure numbers and the IFR service-robot figures.
"""
import math
import re

import numpy as np

from _ch1 import AGV_SPEED, LOAD_UNLOAD_S, factory
from bookout import T, out

data, layout = factory()
from sim.engine import AGV_SPEED as ENGINE_SPEED, LOAD_UNLOAD_S as ENGINE_LU, OP_UNITS   # noqa: E402
from wqbus import UNITS                                                                     # noqa: E402

assert ENGINE_SPEED == AGV_SPEED and ENGINE_LU == LOAD_UNLOAD_S       # the same parameters as the factory simulation


def unit_of(op):
    return OP_UNITS[op][0]                      # default machine of each operation


def moves(item):
    """Moves of one piece of item along its process route: [(from, to, route, length)]. Consecutive operations on the same machine need no move; after the last operation the piece goes to the finished store."""
    ops = data.ROUTINGS[data.BOMS[item][0]]
    units = [unit_of(op) for op, _ in ops] + ["store-02"]
    res = []
    for a, b in zip(units, units[1:]):
        if a == b:
            continue
        path = layout.route(layout.dock(a), layout.dock(b))
        res.append((a, b, path, layout.length(path)))
    return res


# ---------------------------------------------------------------- Example 1.5.1: SH-301
mv = moves("SH-301")
ops = data.ROUTINGS[data.BOMS["SH-301"][0]]
mach_min = sum(m for _, m in ops)                                     # machining and inspection time per piece, min
dist = sum(L for *_, L in mv)
t_move_s = sum(L / AGV_SPEED + 2 * LOAD_UNLOAD_S for *_, L in mv)    # each move: driving + loading + unloading
t_drive_s = dist / AGV_SPEED
share = (t_move_s / 60) / (t_move_s / 60 + mach_min)
# Check the route lengths another way, adding up segment by segment: split each polyline into short pieces and sum them
dist_check = 0.0
for *_, path, L in mv:
    seg = sum(math.dist(p, q) for p, q in zip(path, path[1:]))
    assert abs(seg - L) < 1e-9
    dist_check += seg
assert abs(dist_check - dist) < 1e-9
name = {u: T(UNITS[u][1], UNITS[u][2]) for u in UNITS}
rows = "\n".join(f"| {k + 1} | {name[a]} | {name[b]} | {L:.1f} | {L / AGV_SPEED + 2 * LOAD_UNLOAD_S:.1f} |"
                 for k, (a, b, _, L) in enumerate(mv))
first = mv[0]

# ---------------------------------------------------------------- Example 1.5.2: work-centre load and bottleneck; are the AGVs enough?
need = {}                                        # work centre → minutes occupied per reducer
n_moves, agv_s, agv_dist = 0, 0.0, 0.0
for item in data.BOMS:                          # one of each in-house part and subassembly per reducer
    for op, m in data.ROUTINGS[data.BOMS[item][0]]:
        ws = UNITS[unit_of(op)][3]
        need[ws] = need.get(ws, 0) + m
    for *_, L in moves(item):
        n_moves += 1
        agv_dist += L
        agv_s += L / AGV_SPEED + 2 * LOAD_UNLOAD_S
shift_min = 8 * 60
cap = {ws: shift_min * data.WORKSTATIONS[ws][0] / m for ws, m in need.items()}
bott = min(cap, key=cap.get)
assert bott == "滚齿机 HOB-01" and need[bott] == 115                  # agrees with the table in the factory design document
rate = cap[bott]                                                     # reducers per shift
agv_util = agv_s / 60 * rate / (2 * shift_min)                       # fraction of a shift the two AGVs are busy (empty runs not counted)

# ---------------------------------------------------------------- Example 1.5.3: blank masses and the rated payload of the UR5e
rho = 7850.0                                     # density of steel, kg/m³
payload = 5.0                                    # rated payload of the UR5e, kg
grip = 1.0                                       # gripper mass taken as 1.0 kg (assumption)


def disc_mass(code):
    d, h = (float(x) / 1000 for x in re.search(r"Ø(\d+)×(\d+)", data.ITEMS[code][0]).groups())
    return rho * math.pi * (d / 2) ** 2 * h, d, h


m202, d202, h202 = disc_mass("RM-40CR-F155")
m302, d302, h302 = disc_mass("RM-40CR-F225")
m301 = dict(data.BOMS["SH-301"][1])["RM-45-D50"]          # round bar used per output shaft, kg (bill of materials)
ok = {k: (m + grip) <= payload for k, m in (("SH-301", m301), ("GR-202", m202), ("GR-302", m302))}
assert ok == {"SH-301": True, "GR-202": False, "GR-302": False}

# ---------------------------------------------------------------- Example 1.5.4: robot vacuum
A = 60.0                                         # area to clean, m²
w = 0.30                                         # cleaning width, m (assumption)
v = 0.25                                         # driving speed, m/s (assumption)
ov = 0.15                                        # neighbouring rows overlap by 15% in row-by-row cleaning (assumption)
t_row = A / (v * w * (1 - ov))                   # s
n95 = math.log(1 / 0.05)                         # "passes" random cleaning needs for 95% coverage: 1 − e^{−n} = 0.95
t_rand = n95 * A / (v * w)
# Random experiment: drop "cleaning strips" at random on a 60 m² grid, measure the coverage, compare with 1 − e^{−n}
rng = np.random.default_rng(15)
G = 600                                         # 600 × 600 small cells
side = math.sqrt(A)
cell = side / G
covered = np.zeros((G, G), bool)
strip_len = 0.5                                  # each straight stretch is 0.5 m long
k_cells = int(round(w / cell)) + 1
n_target = 1.0
strokes = int(round(n_target * A / (strip_len * w)))
foot = 0                                         # sum of the cells covered by each strip (overlaps counted repeatedly)
for _ in range(strokes):
    ang = rng.uniform(0, math.pi)
    x0, y0 = rng.uniform(0, side, 2)
    t = np.linspace(0, strip_len, int(2 * strip_len / cell) + 1)
    one = np.zeros((G, G), bool)
    for o in np.linspace(-w / 2, w / 2, 2 * k_cells):
        xs = (x0 + t * math.cos(ang) - o * math.sin(ang)) % side          # periodic boundary: leave on one side, come back on the other
        ys = (y0 + t * math.sin(ang) + o * math.cos(ang)) % side
        one[(ys / cell).astype(int) % G, (xs / cell).astype(int) % G] = True
    foot += int(one.sum())
    covered |= one
n_sim = foot / G ** 2                            # number of "passes" actually scattered
c_sim = covered.mean()
c_formula = 1 - math.exp(-n_sim)
assert abs(c_sim - c_formula) < 0.02            # the random experiment fluctuates; tolerance 2 percentage points

# ---------------------------------------------------------------- A few figures on medical and service robots
dv_2025 = 3153000                               # about 3 153 000 da Vinci procedures in 2025 (Intuitive, 2026-01-14)
dv_2024 = 2683000                               # same press release: about 2 683 000 in 2024
dv_growth = dv_2025 / dv_2024 - 1                # the press release says "about 18%"
assert abs(dv_growth - 0.18) < 0.01
dv_per_day = dv_2025 / 365
ifr_prof = 200000                               # about 200 000 professional service robots in 2024
ifr_tl = 102900
tl_share = ifr_tl / ifr_prof

from decimal import ROUND_HALF_UP, Decimal  # noqa: E402
dist_1 = float(Decimal(repr(round(dist, 6))).quantize(Decimal("0.1"), ROUND_HALF_UP))   # 189.45 → 189.5 (round half up)
out(n_ops=len(ops), mach_min=mach_min, n_mv=len(mv), dist=dist, dist_1=dist_1, t_drive_min=t_drive_s / 60, t_move_min=t_move_s / 60,
    share_pct=share * 100, rows=rows, first_from=name[first[0]], first_to=name[first[1]], first_L=first[3],
    first_path=", ".join(f"({x:g}, {y:g})" for x, y in first[2]),
    need_hob=need[bott], cap_hob=rate, cap_cnc=cap["数控车床 CNC-L01"], need_cnc=need["数控车床 CNC-L01"],
    n_moves=n_moves, agv_dist=agv_dist, agv_min=agv_s / 60, agv_util_pct=agv_util * 100,
    rho=rho, m202=m202, m302=m302, m301=m301, d202=d202 * 1000, h202=h202 * 1000, d302=d302 * 1000, h302=h302 * 1000,
    grip=grip, payload=payload, tot202=m202 + grip, tot302=m302 + grip, tot301=m301 + grip,
    A=A, w=w, v=v, ov=ov, t_row_min=t_row / 60, n95=n95, t_rand_min=t_rand / 60, rand_ratio=t_rand / t_row,
    c_sim=c_sim, c_formula=c_formula, n_sim=n_sim, strokes=strokes,
    dv_2025=dv_2025, dv_2024=dv_2024, dv_growth_pct=dv_growth * 100, dv_2025_wan=dv_2025 / 1e4, dv_2024_wan=dv_2024 / 1e4, dv_2025_mio=dv_2025 / 1e6, dv_2024_mio=dv_2024 / 1e6, dv_per_day=dv_per_day, tl_share_pct=tl_share * 100)
