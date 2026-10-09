"""第 3 讲 厂情中枢：异常、追因与推演。教材、课件、作业、测验里的数字全由这里算出。

模型和参数直接取自数字工厂本身（不连数据库，只读源文件里的常数）：
- factory/factory/data.py：WQR-105 的物料清单与工艺路线（每台减速器要磨三根轴：SH-101 15 分钟、SH-201 12 分钟、SH-301 12 分钟），
  外圆磨床 GRD-01 的工位费率（折旧 + 人工 + 能耗，美元/小时）
- factory/digital/hub/ont/plan.py：加班费倍数 1.5、维修加急费 $300、外协加价 1.3 倍 + 每批运费 $50、轴做完后装配跑合检验 1 个工作日
- factory/digital/ontology/rules/playbooks.yaml：加班默认 120 分钟、维修加急把剩余停机减半、外协 1 天回厂
- factory/digital/sim/calendar.py：按班次 08:00–17:00、周一到周五，加班每天最多 240 分钟
- factory/digital/sim/scenario.py：峰顶搅拌机合同的延期违约金 $200/工作日，峰顶订单 8 台（2 个工作日后交）、海港订单 12 台（12 个工作日后交）
- factory/digital/ontology/scenarios/two_weeks.yaml：急单 20 台
- factory/digital/sim/reliability.py、hub/maint.py：GRD-01 平均修复 480 分钟、停机每小时少挣毛利 $200（与第 6 讲一致）

示意值（工厂代码里没有、为本讲设定的）：停机发生在周一 10:00、停 24 小时（在实验 15 指导书建议的 1200–2400 分钟之间），
机器人厂订单周四交货、合同违约金按峰顶合同同样的 $200/工作日。

“推演”= 一个小号的快进程序：只看瓶颈 GRD-01 一台，按班次日历一分钟一分钟往前推，规则与中枢的推演相同
（加急把剩余停机按比例缩短；外协件 days × 24 小时后回厂；加班费 = 设备费率 × 1.5；交货 = 最后一根轴做完 + 1 个工作日）。
实验页 src/zh/labs/causal.html、whatif.html 里的 JS 用的是同一个算法（改这里要同步改那两页）。
"""
import ast
import importlib.util
import math
import os
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[5]
DIG = ROOT / "factory" / "digital"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DATA = _load("wq_factory_data", ROOT / "factory" / "factory" / "data.py")
CAL = _load("wq_sim_calendar", DIG / "sim" / "calendar.py")
REL = _load("reliability", DIG / "sim" / "reliability.py")


def _consts(path, names):
    """只读源文件里的常数（不导入：plan.py、maint.py 要连数据库）"""
    out = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
            out[node.targets[0].id] = ast.literal_eval(node.value)
    return out


PL = _consts(DIG / "hub" / "ont" / "plan.py", {"OT_RATE", "EXPEDITE_COST", "OUTSOURCE_MARKUP", "OUTSOURCE_FREIGHT", "DOWNSTREAM_DAYS", "WAGE_RATE"})
MT = _consts(DIG / "hub" / "maint.py", {"LOST_PER_H", "REPAIR_USD"})
PB = yaml.safe_load((DIG / "ontology" / "rules" / "playbooks.yaml").read_text(encoding="utf-8"))["params"]
TW = yaml.safe_load((DIG / "ontology" / "scenarios" / "two_weeks.yaml").read_text(encoding="utf-8"))
RULES = {f: yaml.safe_load((DIG / "ontology" / "rules" / f"{f}.yaml").read_text(encoding="utf-8"))["rules"] for f in ("production", "sales")}
SCN = (DIG / "sim" / "scenario.py").read_text(encoding="utf-8")
PEN_F = int(re.search(r'\(CUST\["summit"\],\s*(\d+),', SCN).group(1))                       # 峰顶合同违约金 $/工作日
QTY_F = int(re.search(r'"SAL-ORD-2026-00019".*?"qty":\s*(\d+)', SCN, re.S).group(1))          # 峰顶 8 台
QTY_H = int(re.search(r'"SAL-ORD-2026-00020".*?"qty":\s*(\d+)', SCN, re.S).group(1))          # 海港 12 台
DUE_H_WD = int(re.search(r'delivery_date=_wd_add\(today,\s*(\d+)\)', SCN).group(1))           # 海港：12 个工作日后交
DUE_F_WD = int(re.search(r'due19 = _wd_add\(today,\s*(\d+)\)', SCN).group(1))                # 峰顶：2 个工作日后交
QTY_R = int(TW["qty"])           # 急单 20 台：台数取两周情景的急单（那里的客户是海港起重）；“机器人厂”这个客户和周四交货是本讲设定（示意），数字工厂里还没有机器人厂客户（第 30 轮加入）

# ---------------------------------------------------------------- 工厂常数
GRIND = "磨外圆 Cylindrical grinding"


def grind_minutes(item):
    """一台 item 里所有自制件要在磨床上花的分钟（按 BOM 逐级展开）"""
    rt, kids = DATA.BOMS[item]
    own = sum(m for op, m in DATA.ROUTINGS[rt] if op == GRIND)
    return own + sum(q * grind_minutes(c) for c, q in kids if c in DATA.BOMS)


SHAFTS = [(c, next(m for op, m in DATA.ROUTINGS[DATA.BOMS[c][0]] if op == GRIND)) for c in ("SH-101", "SH-201", "SH-301")]
SET_MIN = grind_minutes("WQR-105")                                   # 每台 39 分钟
RATE = float(sum(DATA.WORKSTATIONS["外圆磨床 GRD-01"][1]))             # $52/小时
OT_X = PL["OT_RATE"]
OT_RATE = RATE * OT_X                                                # $78/小时
EXP_FEE = PL["EXPEDITE_COST"]                                        # $300
EXP_F = float(PB["expedite_factor"])                                 # 剩余停机 × 0.5
OUT_SET = SET_MIN / 60 * RATE * PL["OUTSOURCE_MARKUP"]               # 每台的三根轴外协 $43.94
FREIGHT = PL["OUTSOURCE_FREIGHT"]                                    # $50/批
OUT_DAYS = float(PB["outsource_days"])                               # 1 天
OT_DEF = int(PB["overtime_minutes"])                                 # 120 分钟
OT_MAX = CAL.MAX_OT_MIN                                              # 240 分钟
_c = CAL.Calendar("shift")
SH0, SH1 = (int(x.split(":")[0]) * 60 + int(x.split(":")[1]) for x in (_c.start, _c.end))   # 480, 1020
WORKDAYS = _c.workdays
DOWN = PL["DOWNSTREAM_DAYS"]["WQR-105"]                              # 1 个工作日
MTTR = REL.PARAMS["grd-01"][2]                                       # 480 分钟
LOST_H = MT["LOST_PER_H"]["grd-01"]                                  # $200/小时

# ---------------------------------------------------------------- 本讲情景（示意值见文件头）
TB = 0 * 1440 + 10 * 60          # 周一 10:00 停机
D_H = 24                         # 停 24 小时（主轴故障，等备件）
PEN_R = PEN_F                    # 机器人厂合同违约金：取与峰顶合同同样的 $200/工作日（示意值）
DUE = {"F": DUE_F_WD, "R": 3, "H": DUE_H_WD}            # 交货日：周一为第 0 个工作日
QTY = {"F": QTY_F, "R": QTY_R, "H": QTY_H}
PEN = {"F": PEN_F, "R": PEN_R, "H": 0}
FIFO = ["F", "R", "H"]
DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
DAYS_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def is_wd(d):
    return d % 7 in WORKDAYS


def wd_index(n):
    """第 n 个工作日（周一 = 0）是第几天"""
    d, k = 0, 0
    while True:
        if is_wd(d):
            if k == n:
                return d
            k += 1
        d += 1


def run(D=D_H, tb=TB, ot=0, factor=1.0, n_out=0, out_days=OUT_DAYS, order=FIFO, exp_at=None, qty=None):
    """磨床快进推演。ot：恢复后每天加班分钟（只加磨床，机器人订单做完就不再加）；factor：维修加急后剩余停机的比例；
    n_out：机器人订单外协几台（每台三根轴），out_days 天后回厂。返回 {fin: {订单: 分钟}, ot_min, up}"""
    qty = qty or QTY
    up = tb + D * 60
    if factor < 1:
        t_dec = tb if exp_at is None else exp_at
        up = t_dec + (up - t_dec) * factor
    items = [[k, qty[k] * SET_MIN - (n_out * SET_MIN if k == "R" else 0)] for k in order]
    items = [x for x in items if x[1] > 1e-9]
    fin = {}
    ot_used = 0.0
    r_done = not any(x[0] == "R" for x in items)
    up_day = int(up // 1440)
    d = int(tb // 1440)
    while items and d < 60:
        if is_wd(d):
            s, e = d * 1440 + SH0, d * 1440 + SH1
            t = max(s, up, tb)
            while items:
                lim = e + (ot if (ot and d >= up_day and not r_done) else 0)
                if t >= lim:
                    break
                take = min(items[0][1], lim - t)
                if t + take > e:
                    ot_used += t + take - max(t, e)
                t += take
                items[0][1] -= take
                if items[0][1] <= 1e-9:
                    k = items.pop(0)[0]
                    fin[k] = t
                    if k == "R":
                        r_done = True
        d += 1
    if n_out:
        fin["R"] = max(fin.get("R", tb), tb + out_days * 1440)
    return {"fin": fin, "ot_min": ot_used, "up": up}


def delivery_day(fin):
    d = int(fin // 1440)
    k = DOWN
    while k:
        d += 1
        if is_wd(d):
            k -= 1
    return d


def late_days(fin, key):
    due = wd_index(DUE[key])
    p = delivery_day(fin)
    return sum(1 for x in range(due + 1, p + 1) if is_wd(x)) if p > due else 0


def lost_hours(tb, up):
    """停机和班次重叠的小时：真正丢掉的生产时间"""
    tot = 0
    for d in range(int(tb // 1440), int(up // 1440) + 1):
        if is_wd(d):
            s, e = d * 1440 + SH0, d * 1440 + SH1
            tot += max(0, min(e, up) - max(s, tb))
    return tot / 60


def min_ot(D=D_H, tb=TB, factor=1.0, order=FIFO):
    """保住机器人订单的最少“每天加班分钟”（加不够返回 None）"""
    for m in range(0, OT_MAX + 1):
        r = run(D, tb, ot=m, factor=factor, order=order)
        if late_days(r["fin"]["R"], "R") == 0:
            return m, r["ot_min"]
    return None, None


def option(kind, D=D_H, tb=TB, ot=None, n_out=None, order=FIFO):
    """一个方案：结果、各订单晚几天、多花的钱（加班费、加急费、外协费、违约金）"""
    if kind == "none":
        r, extra = run(D, tb, order=order), 0.0
    elif kind == "overtime":
        if ot is None:                      # 加到保住交期为止（每天最多 4 小时）
            m, _ = min_ot(D, tb, order=order)
            ot = OT_MAX if m is None else m
        r = run(D, tb, ot=ot, order=order)
        extra = r["ot_min"] / 60 * OT_RATE
    elif kind == "expedite":
        r, extra = run(D, tb, factor=EXP_F, order=order), EXP_FEE
    elif kind == "outsource":
        n = n_out if n_out is not None else min_out(D, tb, order)
        r, extra = run(D, tb, n_out=n, order=order), (n * OUT_SET + FREIGHT if n else 0)
    else:
        raise ValueError(kind)
    late = {k: late_days(r["fin"][k], k) for k in order}
    pen = sum(PEN[k] * late[k] for k in order)
    return {"kind": kind, "fin": r["fin"], "late": late, "extra": extra, "pen": pen, "total": extra + pen, "ot_h": r["ot_min"] / 60,
            "up": r["up"], "worst": max(late.values())}


def min_out(D=D_H, tb=TB, order=FIFO):
    """保住机器人订单交期的最少外协台数（保不住返回 QTY_R）"""
    for n in range(0, QTY_R + 1):
        r = run(D, tb, n_out=n, order=order)
        if late_days(r["fin"]["R"], "R") == 0:
            return n
    return QTY_R


def best(opts):
    """中枢的排序：先看最晚的订单晚几天，再看多花的钱，再看加班"""
    return min(opts, key=lambda o: (o["worst"], o["total"], o["ot_h"]))


def hm(t, lang="zh"):
    d = int(t // 1440)
    m = int(round(t - d * 1440))
    if m == 1440:
        d, m = d + 1, 0
    return f"{(DAYS if lang == 'zh' else DAYS_EN)[d % 7]} {m // 60:02d}:{m % 60:02d}"


# ---------------------------------------------------------------- 本讲的解
base = run(0)                                       # 不停机时
up = TB + D_H * 60
L = lost_hours(TB, up)                              # 真正丢掉的生产小时
dead_R = wd_index(DUE["R"] - DOWN) * 1440 + SH1     # 机器人订单的轴最晚做完（周三 17:00）
dead_F = wd_index(DUE["F"] - DOWN) * 1440 + SH1
slack_R = (dead_R - base["fin"]["R"]) / 60          # 不停机时离截止还有几个生产小时（都在同一天时成立）
short_R = L - slack_R                               # 差几个小时
O = {k: option(k, ot=OT_DEF if k == "overtime" else None) for k in ("none", "overtime", "expedite", "outsource")}   # B：每天最多加班 2 小时（中枢默认），机器人订单磨完就停
B = best(O.values())
n_min = min_out()
up_exp = O["expedite"]["up"]
L_exp = lost_hours(TB, up_exp)
# 经验估计：停多久就少干多久，一天干 9 小时
shift_h = (SH1 - SH0) / 60
naive_days = D_H / shift_h
naive_late = math.ceil(naive_days)
# 加急 + 补一点加班（加急以后还差的那一点）
exp_ot_m, exp_ot_used = min_ot(factor=EXP_F)
exp_ot_cost = EXP_FEE + exp_ot_used / 60 * OT_RATE
# 插单：机器人订单排到最前
O_re = option("none", order=["R", "F", "H"])
# 实验 15 指导书建议的停机范围：1200、2400 分钟
O20 = {k: option(k, D=20) for k in ("none", "overtime", "expedite", "outsource")}
O40 = {k: option(k, D=40) for k in ("none", "overtime", "expedite", "outsource")}
L40 = lost_hours(TB, TB + 40 * 60)
L20 = lost_hours(TB, TB + 20 * 60)


def fin_s(key, opt, lang="zh"):
    return hm(opt["fin"][key], lang)


out = {
    # 工厂常数
    "set_min": SET_MIN, "sh101": SHAFTS[0][1], "sh201": SHAFTS[1][1], "sh301": SHAFTS[2][1],
    "rate": RATE, "ot_x": OT_X, "ot_rate": OT_RATE, "exp_fee": EXP_FEE, "exp_f": EXP_F, "exp_pct": EXP_F * 100,
    "markup": PL["OUTSOURCE_MARKUP"], "out_set": OUT_SET, "freight": FREIGHT, "out_days": OUT_DAYS, "out_h": OUT_DAYS * 24,
    "ot_def": OT_DEF, "ot_def_h": OT_DEF / 60, "ot_max": OT_MAX, "ot_max_h": OT_MAX / 60, "shift_h": shift_h,
    "mttr": MTTR, "mttr_h": MTTR / 60, "lost_per_h": LOST_H, "down_days": DOWN,
    "p5_above": RULES["production"]["P5"]["params"]["above"], "r3_crit": RULES["sales"]["R3"]["params"]["critical_usd"],
    # 订单
    "qty_f": QTY_F, "qty_r": QTY_R, "qty_h": QTY_H, "pen_f": PEN_F, "pen_r": PEN_R,
    "h_f": QTY_F * SET_MIN / 60, "h_r": QTY_R * SET_MIN / 60, "h_h": QTY_H * SET_MIN / 60,
    "shafts_r": QTY_R * 3, "queue_n": (QTY_F + QTY_R + QTY_H) * 3,
    "h_fr": (QTY_F + QTY_R) * SET_MIN / 60,
    "due_h_wd": DUE_H_WD,
    # 停机
    "D": D_H, "D_min": D_H * 60, "up_s": hm(up), "L": L, "L_mon": lost_hours(TB, 1440), "L_tue": L - lost_hours(TB, 1440),
    "base_f_s": hm(base["fin"]["F"]), "base_r_s": hm(base["fin"]["R"]), "slack_r": slack_R, "short_r": short_R,
    "naive_days": naive_days, "naive_late": naive_late, "naive_pen": naive_late * PEN_R,
    # 四个方案
    **{f"{k}_{x}": O[k][x] for k in O for x in ("extra", "pen", "total", "ot_h")},
    **{f"{k}_late_r": O[k]["late"]["R"] for k in O}, **{f"{k}_late_f": O[k]["late"]["F"] for k in O},
    **{f"{k}_fin_r": fin_s("R", O[k]) for k in O}, **{f"{k}_fin_f": fin_s("F", O[k]) for k in O},
    "none_fin_h": fin_s("H", O["none"]),
    "best": B["kind"], "ot_need": min_ot()[0], "ot_need_h": min_ot()[0] / 60, "n_min": n_min, "up_exp_s": hm(up_exp), "L_exp": L_exp, "exp_saved": L - L_exp,
    "exp_down_saved": D_H * (1 - EXP_F), "exp_short": L_exp - slack_R, "exp_short_min": (L_exp - slack_R) * 60,
    "exp_ot_cost": exp_ot_cost, "exp_ot_min": exp_ot_used,
    "out_n3_late": late_days(run(n_out=3)["fin"]["R"], "R"),
    "out_h_n": n_min * SET_MIN / 60, "break_even_h": FREIGHT / (OT_RATE - OUT_SET / (SET_MIN / 60)),
    "out_rate_h": OUT_SET / (SET_MIN / 60),
    # 插单
    "re_late_r": O_re["late"]["R"], "re_late_f": O_re["late"]["F"], "re_pen": O_re["pen"], "re_fin_r": fin_s("R", O_re), "re_fin_f": fin_s("F", O_re),
    # 停 20 h、40 h
    "L20": L20, "L40": L40,
    **{f"d20_{k}_total": O20[k]["total"] for k in O20}, **{f"d20_{k}_late": O20[k]["worst"] for k in O20},
    **{f"d40_{k}_total": O40[k]["total"] for k in O40}, **{f"d40_{k}_late": O40[k]["worst"] for k in O40},
    "d40_best": best(O40.values())["kind"], "d40_n": min_out(40), "d40_ot_late": O40["overtime"]["late"]["R"],
    "d40_short": L40 - slack_R,
}
out["saved_vs_naive"] = out["naive_pen"] - out["none_pen"]
out["pen_none_total"] = out["none_total"]
out["over_pct_naive"] = out["naive_pen"] / out["none_pen"] if out["none_pen"] else 0

# 习题与测验
# 1) 周五 15:00 停 20 小时：丢掉的生产时间（周末不开工）
t_fri = 4 * 1440 + 15 * 60
out["q_fri_L"] = lost_hours(t_fri, t_fri + 20 * 60)
# 2) 周一 10:00 停 30 小时
out["q30_L"] = lost_hours(TB, TB + 30 * 60)
out["q30_short"] = out["q30_L"] - slack_R
out["q30_ot_cost"] = out["q30_short"] * OT_RATE
out["q30_n"] = math.ceil(out["q30_short"] / (SET_MIN / 60) - 1e-9)
out["q30_out_cost"] = out["q30_n"] * OUT_SET + FREIGHT
out["q30_sim_ot"] = option("overtime", D=30)["total"]
out["q30_sim_ot_late"] = option("overtime", D=30)["late"]["R"]
out["q30_sim_ot4_late"] = option("overtime", D=30, ot=OT_MAX)["late"]["R"]
out["q30_sim_ot4"] = option("overtime", D=30, ot=OT_MAX)["total"]
out["q30_sim_n"] = min_out(30)
out["q30_sim_out"] = option("outsource", D=30)["total"]
# 2) 机器人交期提前到周三：余量（负数 = 不停机也晚）
_dl = wd_index(DUE["R"] - 1 - DOWN) * 1440 + SH1
out["q_slack_wed"] = -sum(max(0, min(d * 1440 + SH1, base["fin"]["R"]) - max(d * 1440 + SH0, _dl)) for d in range(0, 5) if is_wd(d)) / 60
# 3) 外协 6 台的费用
out["q_out6"] = 6 * OUT_SET + FREIGHT
# 4) 加班 3 小时的费用
out["q_ot3"] = 3 * OT_RATE
# 5) 晚交 2 天的违约金
out["q_pen2"] = 2 * PEN_R
# 6) 决定晚了 6 小时才加急：剩余停机 18 h 减半，省 9 h 停机——落在哪里？
r_late_dec = run(D_H, TB, factor=EXP_F, exp_at=TB + 6 * 60)
out["q_dec6_up"] = hm(r_late_dec["up"])
out["q_dec6_L"] = lost_hours(TB, r_late_dec["up"])
# 机器人：协作机器人底座两个大关节用 WQR-105（示意）→ 20 台减速器 = 10 台机器人
out["rob_per"] = 2
out["rob_n"] = QTY_R // 2
# 生活例子：外卖（示意）：计划 接单 2 + 出餐 12 + 等骑手 5 + 配送 11 = 30 分钟；午高峰出餐 25 分钟
food = {"order": 2, "cook": 12, "wait": 5, "ride": 11}
out.update({"food_plan": sum(food.values()), "food_cook": food["cook"], "food_cook2": 25, "food_late": 25 - food["cook"],
            "food_order": food["order"], "food_wait": food["wait"], "food_ride": food["ride"]})
out["food_actual"] = out["food_plan"] + out["food_late"]

# 停得更久（§3.6）：峰顶的余量（正班小时）、峰顶开始晚交的时长、“不处理”只罚 $200 持续到多少小时；停 30 h 时各方案
def _prod_hours(a, b):
    return sum(max(0, min(d * 1440 + SH1, b) - max(d * 1440 + SH0, a)) for d in range(0, 10) if is_wd(d)) / 60


out["slack_f"] = _prod_hours(base["fin"]["F"], dead_F)
out["slack_r_chk"] = _prod_hours(base["fin"]["R"], dead_R)
out["d_f_late"] = next(D for D in range(1, 60) if option("none", D=D)["late"]["F"] > 0)
out["d_none200_last"] = max(D for D in range(1, 60) if abs(option("none", D=D)["total"] - PEN_R) < 1e-6)
out["d_l7_first"] = min(D for D in range(1, 60) if abs(lost_hours(TB, TB + D * 60) - 7) < 1e-9)
out["d_l7_last"] = max(D for D in range(1, 60) if abs(lost_hours(TB, TB + D * 60) - 7) < 1e-9)
_o30 = {k: option(k, D=30, ot=OT_MAX if k == "overtime" else None) for k in ("none", "overtime", "expedite", "outsource")}
out.update({f"q30_{k}_total": _o30[k]["total"] for k in _o30})
out.update({f"q30_{k}_late_f": _o30[k]["late"]["F"] for k in _o30})
out.update({f"q30_{k}_late_r": _o30[k]["late"]["R"] for k in _o30})
out["q30_best"] = best(_o30.values())["kind"]
out["d_exp_first"] = min(D for D in range(1, 49) if best([option(k, D=D, ot=OT_DEF if k == "overtime" else None) for k in ("none", "overtime", "expedite", "outsource")])["kind"] == "expedite" and D > 25)
out["q30_up_s"] = hm(TB + 30 * 60)
out["ot_hub_cost"] = 2 * OT_DEF / 60 * OT_RATE          # 推演工作台里磨床周二、周三各排 2 小时：按排定的分钟计费

# 时刻字符串的英文版（课件、讲稿英文行用 *_en）
for k, v in list(out.items()):
    if isinstance(v, str) and any(x in v for x in DAYS):
        for zh_, en_ in zip(DAYS, DAYS_EN):
            v = v.replace(zh_, en_)
        out[k + "_en"] = v

for k, v in out.items():
    print(f"{k:16s} {v:.4f}" if isinstance(v, float) else f"{k:16s} {v}")

if os.environ.get("WQ_BOOK_OUT"):
    from bookout import out as book_out
    book_out(**{k: (round(v, 6) if isinstance(v, float) else v) for k, v in out.items()})
