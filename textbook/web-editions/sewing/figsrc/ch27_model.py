# -*- coding: utf-8 -*-
"""第 27 章算例模型（示意值）。虚拟实验 labs/factory.html 用同一套公式和同一个随机数发生器。

运行：python3 figsrc/ch27_model.py   → 打印正文用到的全部算例值
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import ch27_sewing_data as SD  # noqa: E402

# ================================================================ 随机数（与实验页的 JS 逐位一致）
def mulberry32(seed):
    a = [seed & 0xFFFFFFFF]

    def imul(x, y):
        return ((x & 0xFFFFFFFF) * (y & 0xFFFFFFFF)) & 0xFFFFFFFF

    def r():
        a[0] = (a[0] + 0x6D2B79F5) & 0xFFFFFFFF
        t = a[0]
        t = imul(t ^ (t >> 15), 1 | t)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0
    return r


def normals(seed, n):
    r = mulberry32(seed)
    out = []
    for _ in range(n):
        u1 = 1.0 - r()
        u2 = r()
        out.append(math.sqrt(-2.0 * math.log(u1)) * math.cos(2 * math.pi * u2))
    return out


# ================================================================ 质量闭环：梭尖间隙
Q = dict(rate=22.5, hours=16, mu0=0.070, sigma=0.006, lsl=0.04, usl=0.10, sub=5,
         t0=2.0, drift_um_h=4.0, step_um=0.0, react_h=0.5, lot=300, seed=5,
         ship_h=(8, 16))
RULES = ("R1", "R2", "R3", "R4")


def values(p, drift=True, lot_b_until=None):
    """每台整机（序列号 1..N）的梭尖间隙（mm）。lot_b_until：用到第几台为止仍装漂移批次 B 的旋梭。"""
    N = int(p["rate"] * p["hours"])
    z = normals(p["seed"], N)
    n0 = round(p["t0"] * p["rate"])
    vals, lots = [], []
    for n in range(1, N + 1):
        in_b = n > n0 and (n - n0) <= p["lot"] and (lot_b_until is None or n <= lot_b_until)
        off = 0.0
        if in_b and drift:
            off = (p["step_um"] + p["drift_um_h"] * (n - n0) / p["rate"]) / 1000.0
        v = round(p["mu0"] + off + p["sigma"] * z[n - 1], 4)
        vals.append(v)
        lots.append("B" if in_b else ("A" if n <= n0 else "C"))
    return vals, lots


def spc_alarms(vals, p, rules, r0=False):
    """逐台 / 逐子组检查，返回全部报警 [(序列号, 规则)]（同一规则 2 h 内不重复报，与 hub/ai.py 的去重相同）。
    子组 = 连续 5 台；X̄ 图控制限由基准 μ0、σ 算出。R0 = 问渠 hub/ai.py 现有的“趋近上限”规则（逐台）。"""
    k = p["sub"]
    s = p["sigma"] / math.sqrt(k)
    c = p["mu0"]
    band = (p["usl"] - p["lsl"]) * 1000
    center = (p["usl"] + p["lsl"]) / 2
    Z, out, last = [], [], {}

    def hit(n, rule):
        t = n / p["rate"]
        if rule in last and t - last[rule] < 2.0:
            return
        last[rule] = t
        out.append((n, rule))
    for n in range(1, len(vals) + 1):
        if r0 and n >= 5:
            last5 = vals[n - 5:n]
            shift = (sum(last5) / 5 - center) * 1000
            margin = (p["usl"] - max(last5)) * 1000
            if shift >= 2 and margin <= band * 0.25:
                hit(n, "R0")
        if n % k:
            continue
        xb = sum(vals[n - k:n]) / k
        Z.append((xb - c) / s)
        if "R1" in rules and abs(Z[-1]) > 3:
            hit(n, "R1")
        if "R2" in rules and len(Z) >= 3:
            w = Z[-3:]
            if sum(1 for x in w if x > 2) >= 2 or sum(1 for x in w if x < -2) >= 2:
                hit(n, "R2")
        if "R3" in rules and len(Z) >= 5:
            w = Z[-5:]
            if sum(1 for x in w if x > 1) >= 4 or sum(1 for x in w if x < -1) >= 4:
                hit(n, "R3")
        if "R4" in rules and len(Z) >= 8:
            w = Z[-8:]
            if all(x > 0 for x in w) or all(x < 0 for x in w):
                hit(n, "R4")
    return out


def spc_alarm(vals, p, rules, r0=False, after=0):
    """第一次 n > after 的报警 (序列号, 规则)；after 之前的报警算误报（调查后无发现，恢复生产）。"""
    for n, r in spc_alarms(vals, p, rules, r0):
        if n > after:
            return n, r
    return None, None


def first_fail(vals, p):
    for n, v in enumerate(vals, 1):
        if v < p["lsl"] or v > p["usl"]:
            return n
    return None


def outcome(p, rules=RULES, r0=False, late_h=0.0, by="spc"):
    """检出 → 隔离（反应时间后停用 B 批旋梭）→ 受影响台数、返工台数、已发货台数。"""
    vals, lots = values(p)
    if by == "spc":
        n_a, rule = spc_alarm(vals, p, rules, r0, after=round(p["t0"] * p["rate"]))
    else:
        n_a, rule = first_fail(vals, p), "超差"
    N = len(vals)
    if n_a is None:
        n_c = N
    else:
        n_c = min(N, int(math.floor((n_a / p["rate"] + p["react_h"] + late_h) * p["rate"] + 1e-9)))
    vals2, lots2 = values(p, lot_b_until=n_c)
    affected = [n for n in range(1, N + 1) if lots2[n - 1] == "B"]
    rework = [n for n in affected if not (p["lsl"] <= vals2[n - 1] <= p["usl"])]
    t_c = n_c / p["rate"]
    shipped = [n for n in affected if any(n <= h * p["rate"] and t_c > h for h in p["ship_h"])]
    left = p["lot"] - len(affected)
    return dict(n_alarm=n_a, rule=rule, t_alarm=None if n_a is None else n_a / p["rate"],
                n_contain=n_c, t_contain=t_c, affected=len(affected), rework=len(rework),
                shipped=len(shipped), lot_left=left, first=(affected[0] if affected else None),
                last=(affected[-1] if affected else None), vals=vals2, lots=lots2)


def false_alarms(p, rules=RULES, r0=False):
    """无漂移时 16 h 内的报警次数（同一组随机数）和第一次报警。"""
    vals, _ = values(p, drift=False)
    al = spc_alarms(vals, p, rules, r0)
    return len(al), (al[0] if al else None)


def mc_detect(p, rules, r0=False, seeds=range(1, 1001)):
    """1000 组随机数的平均：检出延迟（h，相对漂移开始）、误报率、返工台数。"""
    dl, fa, rw, ff = [], 0, [], []
    for s in seeds:
        q = dict(p, seed=s)
        o = outcome(q, rules, r0)
        if o["t_alarm"] is not None:
            dl.append(o["t_alarm"] - p["t0"])
        rw.append(o["rework"])
        n, _ = false_alarms(q, rules, r0)
        fa += n > 0
        f = first_fail(values(q)[0], q)
        if f is not None:
            ff.append(f / q["rate"] - p["t0"])
    return dict(delay=sum(dl) / len(dl), detected=len(dl), false=fa / len(seeds), rework=sum(rw) / len(rw),
                first_fail=sum(ff) / len(ff))


def p_out(m, p):
    phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
    return 1 - phi((p["usl"] - m) / p["sigma"]) + phi((p["lsl"] - m) / p["sigma"])


# ================================================================ 工作中心负荷
ASSY = ("总装线 ASM-L1", "调试工位 ADJ", "跑合台 RUN", "出厂测试台 EOL")


def loads(demand=180, oee=0.60, oee_assy=0.90):
    """每天 demand 台；机加工设备按 OEE 折算有效时间，装配与测试按节拍效率 oee_assy。"""
    need = {}
    for item, (rt, q) in SD.MADE_PER_UNIT.items():
        for op, wc, mins in SD.ROUTINGS[rt]:
            need[wc] = need.get(wc, 0) + mins * q
    out = []
    for wc, (cnt, shifts, rate) in SD.WORKSTATIONS.items():
        m = need.get(wc, 0)
        cap_min = cnt * shifts * 480 * (oee_assy if wc in ASSY else oee)
        out.append((wc, round(m, 2), cnt, shifts, round(cap_min / m, 1) if m else None,
                    round(demand * m / cap_min * 100, 1) if m else None))
    return out


# ================================================================ 分期实施与回收
PH = [  # 名称, 投资(万元), 年节省(万元, 由 savings() 算), 开始月, 工期(月)
    dict(name="第一期", invest=150, start=0, build=6),
    dict(name="第二期", invest=120, start=6, build=9),
    dict(name="第三期", invest=80, start=15, build=9),
]
BASE = dict(Q=50000, mat_year=6000, turn0=4.0, turn1=5.0, carry=0.20,
            key_cost=800, oee0=0.60, oee1=0.68,
            fpy0=0.92, fpy1=0.96, rework_cost=150, scrap0=0.020, scrap1=0.012, made_cost=400,
            war0=0.030, war1=0.024, war2=0.018, claim=600,
            spare0=400, spare1=300, trips=3000, trip_cut=0.30, trip_cost=500,
            run_rate=0.15, ramp=6, horizon=60)


def savings(b=BASE):
    """各期年节省（万元）及分项。"""
    inv0 = b["mat_year"] / b["turn0"]
    inv1 = b["mat_year"] / b["turn1"]
    s1 = {"库存周转 %.0f→%.0f 次/年" % (b["turn0"], b["turn1"]): (inv0 - inv1) * b["carry"],
          "关键设备 OEE %.0f%%→%.0f%%" % (b["oee0"] * 100, b["oee1"] * 100): b["key_cost"] * (1 - b["oee0"] / b["oee1"])}
    s2 = {"一次合格率 %.0f%%→%.0f%%" % (b["fpy0"] * 100, b["fpy1"] * 100): b["Q"] * (b["fpy1"] - b["fpy0"]) * b["rework_cost"] / 1e4,
          "自制件报废 %.1f%%→%.1f%%" % (b["scrap0"] * 100, b["scrap1"] * 100): b["Q"] * (b["scrap0"] - b["scrap1"]) * b["made_cost"] / 1e4,
          "保修期返修率 %.1f%%→%.1f%%" % (b["war0"] * 100, b["war1"] * 100): b["Q"] * (b["war0"] - b["war1"]) * b["claim"] / 1e4}
    s3 = {"保修期返修率 %.1f%%→%.1f%%" % (b["war1"] * 100, b["war2"] * 100): b["Q"] * (b["war1"] - b["war2"]) * b["claim"] / 1e4,
          "备件库存 %d→%d 万元" % (b["spare0"], b["spare1"]): (b["spare0"] - b["spare1"]) * b["carry"],
          "上门服务减少 %.0f%%" % (b["trip_cut"] * 100): b["trips"] * b["trip_cut"] * b["trip_cost"] / 1e4}
    return [s1, s2, s3]


def cashflow(phases, sav, b=BASE):
    """逐月现金流（万元）：工期内均摊投资；上线后节省在 ramp 个月内线性爬升到全额；
    运行费 = 已上线各期投资 × run_rate / 年。返回累计现金流列表、回收月（累计 ≥ 0 的第一个月，从第 1 月起计）。"""
    H = b["horizon"]
    cum, c = [], 0.0
    pay = None
    for m in range(1, H + 1):
        f = 0.0
        for ph, s in zip(phases, sav):
            st, bd = ph["start"], ph["build"]
            if st < m <= st + bd:
                f -= ph["invest"] / bd
            live = st + bd
            if m > live:
                k = min(1.0, (m - live) / b["ramp"])
                f += s / 12 * k
                f -= ph["invest"] * b["run_rate"] / 12
        c += f
        cum.append(c)
        if pay is None and m > 1 and c >= 0 and cum[-2] < 0:
            pay = m
    return cum, pay


# ================================================================ 服务数据回流（示意的联网机群）
def fleet(seed=27, n=6000):
    """每台机器一年的主轴运转小时（对数正态，均值约 900 h）和装机以来的累计运转小时。"""
    z = normals(seed, 2 * n)
    out = []
    for i in range(n):
        hrs = 900 * math.exp(0.45 * z[2 * i] - 0.45 ** 2 / 2)
        age_y = 0.5 + 3.0 * (0.5 + 0.5 * math.tanh(z[2 * i + 1]))   # 0.5–3.5 年
        out.append((hrs, hrs * age_y))
    return out


HOOK = dict(beta=2.2, eta=5000.0)


def hook_forecast(fl, q_hours_frac=0.25, h=HOOK):
    """下一季度旋梭更换需求：按每台的累计运转小时（条件失效概率）vs 按日历平均。"""
    use, cal = 0.0, 0.0
    R = lambda t: math.exp(-(t / h["eta"]) ** h["beta"])
    for hrs, cumh in fl:
        a = cumh % h["eta"]           # 粗略：上次更换以来的小时（示意）
        dt = hrs * q_hours_frac
        use += 1 - R(a + dt) / R(a)
    mean_life_h = h["eta"] * math.gamma(1 + 1 / h["beta"])
    for hrs, _ in fl:
        cal += hrs * q_hours_frac / mean_life_h
    return use, cal, mean_life_h


if __name__ == "__main__":
    print("变型：", SD.variants())
    print("\n== 工作中心负荷（每天 180 台，机加工 OEE 60%）")
    for r in loads():
        print(r)
    print("\n== 质量闭环（种子 %d）" % Q["seed"])
    for name, rules, r0 in [("R1", ("R1",), False), ("R1+R2+R4", ("R1", "R2", "R4"), False),
                            ("R1–R4", RULES, False), ("R0 现有规则", (), True)]:
        o = outcome(Q, rules, r0)
        fa = false_alarms(Q, rules, r0)
        print(name, {k: o[k] for k in ("n_alarm", "rule", "t_alarm", "n_contain", "affected", "rework", "shipped", "lot_left")}, "误报:", fa)
    o = outcome(Q, by="tol")
    print("只按超差", {k: o[k] for k in ("n_alarm", "t_alarm", "n_contain", "affected", "rework", "shipped", "lot_left")})
    for late in (1, 2, 4, 6):
        o = outcome(Q, RULES, late_h=late)
        print("晚 %d h" % late, o["affected"], o["rework"], o["shipped"])
    print("期望超差率：", [(h, round(p_out(Q["mu0"] + Q["drift_um_h"] * h / 1000, Q) * 100, 2)) for h in range(0, 9)])
    if "--mc" in sys.argv:
        for name, rules, r0 in [("R1", ("R1",), False), ("R1+R2+R4", ("R1", "R2", "R4"), False), ("R1–R4", RULES, False), ("R0", (), True)]:
            print("MC", name, mc_detect(Q, rules, r0))
    print("\n== 分期")
    sv = savings()
    tot = [sum(s.values()) for s in sv]
    for s in sv:
        print({k: round(v, 1) for k, v in s.items()})
    print("年节省", [round(t, 1) for t in tot])
    cum, pay = cashflow(PH, tot)
    print("回收月", pay, "5 年累计", round(cum[-1], 1), "24 月", round(cum[23], 1), "最低", round(min(cum), 1))
    for i in range(3):
        cum1, pay1 = cashflow(PH[:i + 1], tot[:i + 1])
        print("只做前 %d 期：回收月" % (i + 1), pay1, "5 年", round(cum1[-1], 1))
    half = [tot[0], tot[1] / 2, tot[2]]
    print("第二期节省减半：", cashflow(PH, half)[1])
    print("\n== 服务数据")
    fl = fleet()
    u, c, ml = hook_forecast(fl)
    print("旋梭季度需求：按运转小时 %.0f，按日历 %.0f，平均寿命 %.0f h" % (u, c, ml))
