"""第 10 讲 经营：毛利、应收与现金：教材、课件、作业、测验里的数字全由这里算出。

口径和常数直接取自数字工厂（学生手算的、平台“经营与财务”页算的，是同一套公式）：
- factory/factory/data.py：WQR-105 标准售价、BOM、工艺路线、工作中心费率（折旧、人工、能耗）、物料单价、客户
- factory/digital/hub/finance.py：付款条件 30 天、各客户平时晚付几天、信用额度、催款后几天内付、期初现金、每周固定开支、
  经营目标（毛利率 ≥ 25%、DSO ≤ 45 天）、标准成本 _std() 和现金流预测 cashflow()、DSO 的公式、应收逾期方案的推荐规则
- factory/digital/hub/people.py：操作工工时费、加班倍数；supply.py：备选供应商的加价；sim/energy.py、hub/energy.py：空转功率、电价
- factory/digital/ontology/scenarios/two_weeks.yaml：两周情景（20 台、40 个轴承、带锯床空转 24 小时、发票逾期 15 天）

finance.py 要连数据库（psycopg），这里不导入它：只用 ast 读常数，把 _std()、cashflow()、dso() 的纯公式照抄一遍（逐行对应，见各函数注释）。
数字工厂里没有、本讲另设的数（标“示意”）：磨床重新调整 4 小时、废品 2 件、现在账上现金按期初 $60,000、
后面三批各 20 台料的供应商发票（第 14、28、42 天到期，落在第 3、5、7 周）、机器人厂在做的下一批 10 台、机器人工作站的里程碑付款、小店的数。
"""
import ast
import importlib.util
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
DIG = ROOT / "factory" / "digital"
_spec = importlib.util.spec_from_file_location("factory_data", ROOT / "factory" / "factory" / "data.py")
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def _consts(path, names, ns=None):
    """只读模块里的常数（不导入：这些模块要连数据库）；值里可以引用 F（如 F.CUSTOMERS[0]）"""
    out = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
            out[node.targets[0].id] = eval(compile(ast.Expression(node.value), str(path), "eval"), {"F": F, **(ns or {})})
    return out


FN = _consts(DIG / "hub" / "finance.py", {"TERMS_DAYS", "LATE", "CREDIT", "DEFAULT_CREDIT", "DUN_PAY_DAYS", "OBJECTIVES", "PARAMS"})
PE = _consts(DIG / "hub" / "people.py", {"WAGE", "OT_RATE"})
SP = _consts(DIG / "hub" / "supply.py", {"ALT"})
SE = _consts(DIG / "sim" / "energy.py", {"POWER"})
EN = _consts(DIG / "hub" / "energy.py", {"PARAMS"}, {"EN": None})
OBJ = {o[0]: o for o in FN["OBJECTIVES"]}
GREEN, SUMMIT, HARBOR = F.CUSTOMERS


# ---------------------------------------------------------------- 标准成本（照抄 finance._std）
def std(item, memo={}):
    """每件的标准成本：料（单价 × BOM 用量）与加工（各工序标准工时 × 费率：折旧 + 人工记“工”，能耗记“电”；热处理一炉 20 件分摊）"""
    if item in memo:
        return memo[item]
    it = F.ITEMS[item]
    if item not in F.BOMS:
        memo[item] = {"material": float(it[3] or 0), "labor": 0.0, "energy": 0.0}
        return memo[item]
    rt, comps = F.BOMS[item]
    out = {"material": 0.0, "labor": 0.0, "energy": 0.0}
    for c, q in comps:
        s = std(c)
        for k in out:
            out[k] += s[k] * q
    for op, mins in F.ROUTINGS.get(rt, []):
        cap, (dep, lab, en) = F.WORKSTATIONS[F.OPERATIONS[op]]
        div = cap if F.OPERATIONS[op].startswith("热处理") else 1
        out["labor"] += mins / 60 * (dep + lab) / div
        out["energy"] += mins / 60 * en / div
    memo[item] = out
    return out


def hours(item):
    """每件的标准工时（小时）：各工序分钟 × BOM 用量，热处理一炉 20 件分摊（和 std() 同一个口径）"""
    if item not in F.BOMS:
        return 0.0
    rt, comps = F.BOMS[item]
    h = sum(hours(c) * q for c, q in comps)
    for op, mins in F.ROUTINGS.get(rt, []):
        h += mins / 60 / (F.WORKSTATIONS[F.OPERATIONS[op]][0] if F.OPERATIONS[op].startswith("热处理") else 1)
    return h


P = F.FG_SELLING_PRICE                          # 标准售价 $1,650
Q = 20                                          # 机器人厂追加的关节减速器（两周情景也是 20 台）
U = std("WQR-105")
SH = std("SH-301")
u_cost = U["material"] + U["labor"] + U["energy"]
u_hours = hours("WQR-105")                      # 每台标准工时（虚拟实验 10-1 的“每台工时”滑块）
avg_rate = U["labor"] / u_hours                 # 平均工位费率（折旧 + 人工）$/h
GRD = F.WORKSTATIONS["外圆磨床 GRD-01"][1]      # (折旧, 人工, 能耗) $/h
# 一台 WQR-105 在 GRD-01 上要磨的分钟（SH-101、SH-201、SH-301 各一根）→ 磨床一小时的产出值多少标准毛利（对照第 6 讲 LOST_PER_H $200/h）
grd_min = sum(m for it in ("SH-101", "SH-201", "SH-301") for op, m in F.ROUTINGS[F.BOMS[it][0]] if F.OPERATIONS[op] == "外圆磨床 GRD-01")
MT = _consts(DIG / "hub" / "maint.py", {"LOST_PER_H", "LABOR_RATE"})

# ---------------------------------------------------------------- 这张订单的毛利分解（finance.margin 的七项）
rev = P * Q
o_mat = U["material"] * Q
o_lab_std = U["labor"] * Q
o_en = U["energy"] * Q
adj_h = 4.0                                     # 示意：第 3 讲磨床停机后重新对刀、换砂轮，输出轴实测多出的调整、换刀时间
x_lab = adj_h * (GRD[0] + GRD[1])               # 按 GRD-01 的折旧 + 人工费率
bad = 2                                         # 示意：不合格输出轴 2 件
x_scrap = bad * (SH["material"] + SH["labor"] + SH["energy"])
idle_h = 24.0                                   # 两周情景第 7 幕：带锯床空转 24 小时（只做了这一张单，全部分摊给它）
idle_kw = SE["POWER"]["saw-01"][1]
flat = EN["PARAMS"]["price"]["flat"]
x_idle = idle_h * idle_kw * flat
ot_h = 12.0                                     # 第 7 讲：磨床熟练工请假，加班顶班 12 小时（数字工厂默认）
x_ot = ot_h * PE["WAGE"] * PE["OT_RATE"]
brg_n = 40                                      # 两周情景第 1 幕：20 台要 40 个 BRG-6207
brg_p = F.ITEMS["BRG-6207"][3]
alt_k = SP["ALT"]["bearings"][1]                # 备选供应商贵 20%
x_alt = brg_n * brg_p * (alt_k - 1)
x_act = x_ot + x_alt
x_war = 0.0                                     # 刚交货，还没有保修服务
o_lab = o_lab_std + x_lab
lines = [("material", o_mat), ("labor", o_lab), ("energy", o_en), ("scrap", x_scrap), ("idle", x_idle), ("actions", x_act), ("warranty", x_war)]
cost = sum(v for _, v in lines)
margin = rev - cost
m_pct = margin / rev * 100
std_margin = rev - u_cost * Q
std_pct = (1 - u_cost / P) * 100
extra = cost - u_cost * Q
target = OBJ["O2"][4] * 100
top_key = max([x for x in lines if x[0] != "material"], key=lambda x: x[1])[0]

# ---------------------------------------------------------------- 应收、账龄、DSO（finance.ar / dso）
T30 = FN["TERMS_DAYS"]
late_mid = {c: sum(FN["LATE"][c]) / 2 for c in F.CUSTOMERS}
ROBOT = "机器人厂"
od_robot = 15.0                                 # 实验 22 注入、两周情景第 8 幕：逾期 15 天，不催就不付
# 期初应收照抄 finance.opening()：(客户, 台数, 开票几天前)；再加机器人厂这张
INV = [(GREEN, 6, 10), (SUMMIT, 4, T30 + 5), (HARBOR, 8, 20), (ROBOT, Q, T30 + od_robot)]
inv = [{"party": c, "amount": n * P, "issued": -age, "due": -age + T30, "over": max(0.0, age - T30)} for c, n, age in INV]


def bucket(d):
    return "current" if d <= 0 else ("d30" if d <= 30 else ("d60" if d <= 60 else "d60p"))


aging = {k: 0.0 for k in ("current", "d30", "d60", "d60p")}
for x in inv:
    aging[bucket(x["over"])] += x["amount"]
ar_total = sum(x["amount"] for x in inv)
sales30 = sum(x["amount"] for x in inv if x["issued"] >= -30)
per_day = sales30 / 30
dso = ar_total / per_day                        # finance.dso：应收余额 ÷ 近 30 天日均开票额
dso_after = (ar_total - Q * P) / per_day
dso_target = OBJ["O7"][4]
free_45_30 = (45 - 30) * per_day                # 实验 22 讨论题：DSO 从 45 天降到 30 天，现金多出多少
limit = FN["DEFAULT_CREDIT"]                    # 机器人厂不在数字工厂的客户表里：用默认信用额度
next_q = 10                                     # 示意：机器人厂在做的下一批
exposure = Q * P + next_q * P
used = exposure / limit * 100
# ---------------------------------------------------------------- 现金流预测（finance.cashflow，按周）
cash0 = FN["PARAMS"]["opening_cash"]            # 现在账上现金：示意按期初 $60,000（还没收付过）
wk = FN["PARAMS"]["weekly_expense"]
safety = wk                                     # 示意：安全线 = 一周的固定开支
AP = [(14, o_mat), (28, o_mat), (42, o_mat)]    # 示意：后面三批各 20 台的料，供应商发票第 14、28、42 天到期（落在第 3、5、7 周）
dun = FN["DUN_PAY_DAYS"]


def pay_day(x, robot_day):
    """这张应收预计哪天收到：到期日 + 这个客户平时晚几天（逾期的按 0）；机器人厂这张看方案"""
    if x["party"] == ROBOT:
        return robot_day
    return x["due"] + late_mid[x["party"]]


def forecast(robot_day, weeks=8):
    """robot_day：机器人厂哪天付（None = 8 周内不付）。照抄 finance.cashflow：第 k 周 = (哪天 − 今天) ÷ 7 取整，早于今天的算第 1 周"""
    inflow, outflow = [0.0] * weeks, [0.0] * weeks
    for x in inv:
        d = pay_day(x, robot_day)
        if d is None:
            continue
        k = max(0, int(d // 7))
        if k < weeks:
            inflow[k] += x["amount"]
    for d, amt in AP:
        k = max(0, int(d // 7))
        if k < weeks:
            outflow[k] += amt
    bal, rows = cash0, []
    for i in range(weeks):
        bal = bal + inflow[i] - outflow[i] - wk
        rows.append({"week": i + 1, "in": inflow[i], "out": outflow[i] + wk, "balance": bal})
    low = min(rows, key=lambda r: r["balance"])
    neg = next((r["week"] for r in rows if r["balance"] < 0), None)
    below = next((r["week"] for r in rows if r["balance"] < safety), None)
    return rows, low, neg, below


fc_none = forecast(None)
fc_dun = forecast(float(dun))
fc_hold = forecast(float(dun))                  # 冻结 = 催款同时冻结：这一笔同样 3 天内付；差别在他的下一批不发货
late_day = 50.0                                 # 习题：机器人厂拖到第 50 天才付
fc_late = forecast(late_day)
# 中枢的推荐规则（finance.options）：应收逾期默认推荐催款；逾期超过 30 天推荐冻结
rec = "hold" if od_robot > 30 else "dunning"

# ---------------------------------------------------------------- 机器人联系、生活例子（示意值）
rb_total, rb_pre, rb_acc, rb_ret = 120000.0, 0.30, 0.60, 0.10      # 一个机器人工作站：签约 30%、验收 60%、质保金 10%（一年后）
# 生活例子：小店每月卖 $3,000，毛利率 30%，一半赊给熟客、两个月后才还；房租和工资每月 $600；开张时手里 $1,000
shop_s, shop_m, shop_fix, shop_cr, shop_lag, shop_c0 = 3000.0, 0.30, 600.0, 0.5, 2, 1000.0
shop_profit = shop_s * shop_m - shop_fix
shop_cash, c = [], shop_c0
for m in range(1, 7):
    c += shop_s * (1 - shop_cr) + (shop_s * shop_cr if m > shop_lag else 0) - shop_s * (1 - shop_m) - shop_fix
    shop_cash.append(c)
shop_low = min(shop_cash)
shop_low_m = shop_cash.index(shop_low) + 1
shop_dso = shop_s * shop_cr * shop_lag / (shop_s / 30)

out = {
    "P": P, "Q": Q, "rev": rev,
    "u_mat": U["material"], "u_lab": U["labor"], "u_en": U["energy"], "u_cost": u_cost, "u_hours": u_hours, "avg_rate": avg_rate, "u_margin": P - u_cost, "std_pct": std_pct,
    "grd_dep": GRD[0], "grd_lab": GRD[1], "grd_en": GRD[2], "grd_rate": GRD[0] + GRD[1],
    "o_mat": o_mat, "o_lab_std": o_lab_std, "o_lab": o_lab, "o_en": o_en, "std_margin": std_margin,
    "adj_h": adj_h, "x_lab": x_lab, "bad": bad, "sh_std": SH["material"] + SH["labor"] + SH["energy"], "x_scrap": x_scrap,
    "idle_h": idle_h, "idle_kw": idle_kw, "flat": flat, "idle_kwh": idle_h * idle_kw, "x_idle": x_idle,
    "ot_h": ot_h, "wage": PE["WAGE"], "ot_rate": PE["OT_RATE"], "ot_wage": PE["WAGE"] * PE["OT_RATE"], "x_ot": x_ot,
    "brg_n": brg_n, "brg_p": brg_p, "alt_pct": (alt_k - 1) * 100, "x_alt": x_alt, "x_act": x_act, "x_war": x_war,
    "cost": cost, "margin": margin, "m_pct": m_pct, "extra": extra, "gap": std_pct - m_pct, "target": target, "f5": target - 5,
    "top": top_key, "lab_share": o_lab / rev * 100, "mat_share": o_mat / rev * 100,
    "terms": T30, "od": od_robot, "robot_amt": Q * P, "green_amt": 6 * P, "summit_amt": 4 * P, "harbor_amt": 8 * P,
    "late_green": late_mid[GREEN], "late_summit": late_mid[SUMMIT], "late_harbor": late_mid[HARBOR],
    "ar_total": ar_total, "ag_cur": aging["current"], "ag_30": aging["d30"], "ag_60": aging["d60"], "ag_60p": aging["d60p"],
    "overdue_amt": aging["d30"] + aging["d60"] + aging["d60p"], "overdue_share": (aging["d30"] + aging["d60"] + aging["d60p"]) / ar_total * 100,
    "sales30": sales30, "per_day": per_day, "dso": dso, "dso_after": dso_after, "dso_target": dso_target, "free_45_30": free_45_30,
    "robot_share": Q * P / ar_total * 100,
    "grd_min": grd_min, "grd_units": 60 / grd_min, "grd_hr_margin": 60 / grd_min * (P - u_cost), "lost_h": MT["LOST_PER_H"]["grd-01"], "maint_rate": MT["LABOR_RATE"],
    "harbor_limit": FN["CREDIT"][HARBOR], "limit": limit, "next_q": next_q, "next_amt": next_q * P, "exposure": exposure, "used": used,
    "cash0": cash0, "wk": wk, "safety": safety, "ap": o_mat, "ap_n": len(AP), "ap_total": o_mat * len(AP), "dun": dun, "rec": rec,
    "none_low": fc_none[1]["balance"], "none_low_wk": fc_none[1]["week"], "none_neg": fc_none[2], "none_below": fc_none[3],
    "none_w8": fc_none[0][-1]["balance"],
    "dun_low": fc_dun[1]["balance"], "dun_low_wk": fc_dun[1]["week"], "dun_w8": fc_dun[0][-1]["balance"], "dun_w1": fc_dun[0][0]["balance"],
    "hold_low": fc_hold[1]["balance"], "hold_low_wk": fc_hold[1]["week"],
    "late_day": late_day, "late_low": fc_late[1]["balance"], "late_low_wk": fc_late[1]["week"], "late_below": fc_late[3],
    "none_low_abs": -fc_none[1]["balance"], "shop_low_abs": -shop_low, "ar_others": ar_total - Q * P,
    "diff_w8": fc_dun[0][-1]["balance"] - fc_none[0][-1]["balance"],
    "rb_total": rb_total, "rb_pre": rb_total * rb_pre, "rb_acc": rb_total * rb_acc, "rb_ret": rb_total * rb_ret,
    "rb_pre_pct": rb_pre * 100, "rb_acc_pct": rb_acc * 100, "rb_ret_pct": rb_ret * 100,
    "shop_s": shop_s, "shop_m": shop_m * 100, "shop_fix": shop_fix, "shop_c0": shop_c0, "shop_profit": shop_profit,
    "shop_low": shop_low, "shop_low_m": shop_low_m, "shop_dso": shop_dso, "shop_cred": shop_s * shop_cr,
}
for i, r in enumerate(fc_none[0]):
    out[f"none_b{i + 1}"] = r["balance"]
for i, r in enumerate(fc_dun[0]):
    out[f"dun_b{i + 1}"] = r["balance"]
for i, r in enumerate(fc_none[0]):
    out[f"in{i + 1}"] = r["in"]
    out[f"out{i + 1}"] = r["out"]

# 习题与测验（教材第 10 章习题、作业、测验、考试题都从这里取数）
cut = 0.05                                       # 机器人厂压价 5%
out.update({
    "q_cut_p": P * (1 - cut), "q_cut_pct": (margin - rev * cut) / (rev * (1 - cut)) * 100,
    "cut_pts": m_pct - (margin - rev * cut) / (rev * (1 - cut)) * 100,                # 降价 5% 毛利率掉几个百分点（< 5）
    "cut_usd": rev * cut, "cut_share": rev * cut / margin * 100,                      # 毛利额少了多少、占原毛利几成
    "hr05": 0.5 * avg_rate * Q,                                                        # 每台工时少 0.5 h 省多少（随台数增加）
    "q_ot24": (margin - x_ot) / rev * 100,                                            # 加班 24 小时
    "q_be": cost / Q,                                                                 # 这张单的保本单价
    "q_p25": (cost + x_ot) / (Q * (1 - target / 100)),                                # 加班 24 小时后，守住 25% 的最低单价
    "q_ar": 45000.0, "q_s30": 27000.0, "q_dso": 45000.0 / (27000.0 / 30),            # 另一组数：应收 $45,000，近 30 天开票 $27,000
    "q_mpct": (1 - 1200.0 / 1650.0) * 100,                                            # 一台卖 $1,650、成本 $1,200
    "q_free": (60 - 40) * 900.0,                                                      # DSO 60 → 40 天、日均开票 $900
    "ex_ar2": ar_total - 4 * P, "ex_dso2": (ar_total - 4 * P) / per_day,              # 峰顶那笔付了以后
})

for k, v in out.items():
    print(f"{k:12s} {v:.4f}" if isinstance(v, float) else f"{k:12s} {v}")

if os.environ.get("WQ_BOOK_OUT"):
    from bookout import out as book_out
    book_out(**{k: (round(v, 6) if isinstance(v, float) else v) for k, v in out.items()})
