"""1.5 节的计算：数字工厂车间里的搬运与上下料，医疗与家庭中的几个数。

算例 1.5.1  输出轴 SH-301 按工艺路线在车间里走一遍：每次搬运的路线长度（工厂仿真的同一套布置与路线算法）、
            搬运时间，与加工时间相比。
算例 1.5.2  每台减速器各工作中心的占用时间、单班日产能、瓶颈；两台 AGV 够不够用。
算例 1.5.3  UR5e（额定负载 5 kg）能不能直接搬运几种毛坯：由尺寸和密度算质量。
算例 1.5.4  扫地机器人：按行规划清扫与随机碰撞清扫各要多长时间。覆盖率公式 c = 1 − e^{−n} 用随机试验核对。
另：达芬奇手术量、IFR 服务机器人数字的简单换算。
"""
import math
import re

import numpy as np

from _ch1 import AGV_SPEED, LOAD_UNLOAD_S, factory
from bookout import T, out

data, layout = factory()
from sim.engine import AGV_SPEED as ENGINE_SPEED, LOAD_UNLOAD_S as ENGINE_LU, OP_UNITS   # noqa: E402
from wqbus import UNITS                                                                     # noqa: E402

assert ENGINE_SPEED == AGV_SPEED and ENGINE_LU == LOAD_UNLOAD_S       # 与工厂仿真用同样的参数


def unit_of(op):
    return OP_UNITS[op][0]                      # 每道工序的默认设备


def moves(item):
    """一件 item 按工艺路线流转时的搬运：[(从, 到, 路线, 长度)]。同一台设备上的相邻工序不需要搬运；最后一道工序之后送成品库。"""
    ops = data.ROUTINGS[data.BOMS[item][0]]
    units = [unit_of(op) for op, _ in ops] + ["store-02"]
    res = []
    for a, b in zip(units, units[1:]):
        if a == b:
            continue
        path = layout.route(layout.dock(a), layout.dock(b))
        res.append((a, b, path, layout.length(path)))
    return res


# ---------------------------------------------------------------- 算例 1.5.1：SH-301
mv = moves("SH-301")
ops = data.ROUTINGS[data.BOMS["SH-301"][0]]
mach_min = sum(m for _, m in ops)                                     # 每件加工、检验时间之和，min
dist = sum(L for *_, L in mv)
t_move_s = sum(L / AGV_SPEED + 2 * LOAD_UNLOAD_S for *_, L in mv)    # 每次：行驶 + 装 + 卸
t_drive_s = dist / AGV_SPEED
share = (t_move_s / 60) / (t_move_s / 60 + mach_min)
# 用逐段累加的另一种方法核对路线长度：把每条折线拆成单位长度的小段计数
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

# ---------------------------------------------------------------- 算例 1.5.2：工作中心占用与瓶颈；AGV 是否够用
need = {}                                        # 工作中心 → 每台减速器占用的分钟数
n_moves, agv_s, agv_dist = 0, 0.0, 0.0
for item in data.BOMS:                          # 每台减速器每种自制件、部件各 1 件
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
assert bott == "滚齿机 HOB-01" and need[bott] == 115                  # 与《工厂设计》的表一致
rate = cap[bott]                                                     # 台/班
agv_util = agv_s / 60 * rate / (2 * shift_min)                       # 两台 AGV 在一个班里被占用的比例（不计空驶）

# ---------------------------------------------------------------- 算例 1.5.3：毛坯质量与 UR5e 的额定负载
rho = 7850.0                                     # 钢的密度，kg/m³
payload = 5.0                                    # UR5e 额定负载，kg
grip = 1.0                                       # 设夹爪质量 1.0 kg（假设）


def disc_mass(code):
    d, h = (float(x) / 1000 for x in re.search(r"Ø(\d+)×(\d+)", data.ITEMS[code][0]).groups())
    return rho * math.pi * (d / 2) ** 2 * h, d, h


m202, d202, h202 = disc_mass("RM-40CR-F155")
m302, d302, h302 = disc_mass("RM-40CR-F225")
m301 = dict(data.BOMS["SH-301"][1])["RM-45-D50"]          # 每根输出轴消耗的圆钢，kg（BOM）
ok = {k: (m + grip) <= payload for k, m in (("SH-301", m301), ("GR-202", m202), ("GR-302", m302))}
assert ok == {"SH-301": True, "GR-202": False, "GR-302": False}

# ---------------------------------------------------------------- 算例 1.5.4：扫地机器人
A = 60.0                                         # 清扫面积，m²
w = 0.30                                         # 清扫宽度，m（假设）
v = 0.25                                         # 行驶速度，m/s（假设）
ov = 0.15                                        # 按行清扫时相邻两行重叠 15%（假设）
t_row = A / (v * w * (1 - ov))                   # s
n95 = math.log(1 / 0.05)                         # 随机清扫覆盖 95% 所需的“遍数”：1 − e^{−n} = 0.95
t_rand = n95 * A / (v * w)
# 随机试验：在 60 m² 的方格上随机落下“清扫带”，统计覆盖率，与 1 − e^{−n} 比较
rng = np.random.default_rng(15)
G = 600                                         # 600 × 600 个小格
side = math.sqrt(A)
cell = side / G
covered = np.zeros((G, G), bool)
strip_len = 0.5                                  # 每段直线 0.5 m 长
k_cells = int(round(w / cell)) + 1
n_target = 1.0
strokes = int(round(n_target * A / (strip_len * w)))
foot = 0                                         # 各段清扫带各自覆盖的小格数之和（重叠部分重复计）
for _ in range(strokes):
    ang = rng.uniform(0, math.pi)
    x0, y0 = rng.uniform(0, side, 2)
    t = np.linspace(0, strip_len, int(2 * strip_len / cell) + 1)
    one = np.zeros((G, G), bool)
    for o in np.linspace(-w / 2, w / 2, 2 * k_cells):
        xs = (x0 + t * math.cos(ang) - o * math.sin(ang)) % side          # 周期边界：走出一边从对边进来
        ys = (y0 + t * math.sin(ang) + o * math.cos(ang)) % side
        one[(ys / cell).astype(int) % G, (xs / cell).astype(int) % G] = True
    foot += int(one.sum())
    covered |= one
n_sim = foot / G ** 2                            # 实际撒下的“遍数”
c_sim = covered.mean()
c_formula = 1 - math.exp(-n_sim)
assert abs(c_sim - c_formula) < 0.02            # 随机试验有起伏，容差 2 个百分点

# ---------------------------------------------------------------- 医疗与服务机器人的几个数
dv_2025 = 3153000                               # 2025 年达芬奇手术量约 3 153 000 例（Intuitive，2026-01-14）
dv_2024 = 2683000                               # 同一新闻稿：2024 年约 2 683 000 例
dv_growth = dv_2025 / dv_2024 - 1                # 新闻稿称“约 18%”
assert abs(dv_growth - 0.18) < 0.01
dv_per_day = dv_2025 / 365
ifr_prof = 200000                               # 2024 年专业服务机器人约 20 万台
ifr_tl = 102900
tl_share = ifr_tl / ifr_prof

from decimal import ROUND_HALF_UP, Decimal  # noqa: E402
dist_1 = float(Decimal(repr(round(dist, 6))).quantize(Decimal("0.1"), ROUND_HALF_UP))   # 189.45 → 189.5（四舍五入）
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
