"""第 6 讲 设备维护与可靠性：教材、课件、作业、测验里的数字全由这里算出。

模型和参数直接取自数字工厂本身（同一个模型，学生手算、平台算、车间里发生的是一回事）：
- factory/digital/sim/reliability.py：每台设备的威布尔参数 β、η，平均修复时间，保养周期，情景开始时已运行小时
- factory/digital/hub/maint.py：修理费、停机每小时少挣的毛利、保养人工与材料、“未来两周”= 80 运行小时
"""
import ast
import importlib.util
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
DIG = ROOT / "factory" / "digital"
_spec = importlib.util.spec_from_file_location("reliability", DIG / "sim" / "reliability.py")
REL = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(REL)


def _consts(path, names):
    """只读 maint.py 里的常数（不导入它：它要连数据库）"""
    out = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
            out[node.targets[0].id] = ast.literal_eval(node.value)
    return out


M = _consts(DIG / "hub" / "maint.py", {"REPAIR_USD", "LOST_PER_H", "HORIZON_H", "LABOR_RATE", "PM_MATERIAL", "PM_MIN"})

U = "grd-01"
beta, eta, mttr_min, pm_h, t0, _modes = REL.PARAMS[U]
H = M["HORIZON_H"]
repair = M["REPAIR_USD"][U]
lost_h = M["LOST_PER_H"][U]
lost = mttr_min / 60 * lost_h                    # 一次故障停机少挣的毛利
Cf = repair + lost                               # 一次故障的损失
pm_min = M["PM_MIN"][U]
Cp = pm_min / 60 * M["LABOR_RATE"] + M["PM_MATERIAL"]   # 保养的人工与材料
pm_lost = pm_min / 60 * lost_h                   # 生产时间里停机保养少挣的毛利（瓶颈）

F = lambda t, b=beta, e=eta: REL.cdf(t, b, e)
P = lambda t, h, b=beta, e=eta: REL.cond_fail(t, h, b, e)
hz = lambda t, b=beta, e=eta: REL.hazard(t, b, e)

p = P(t0, H)
p_after = P(0, H)
EL = p * Cf
delay = 4.0                                      # 下班前还有 4 运行小时（平台默认“240 分钟后保养”）
p_delay = P(t0, delay)
opt_none = EL
opt_now = Cp + pm_lost + p_after * Cf
opt_later = Cp + p_delay * Cf + p_after * Cf
mttf = eta * math.gamma(1 + 1 / beta)


def R(t, b=beta, e=eta):
    return 1 - F(t, b, e)


def cycle_len(T, b=beta, e=eta, n=4000):
    """一个周期的平均运行时间 = ∫0^T R(t) dt（中点法）"""
    return sum(R(T * (i + 0.5) / n, b, e) for i in range(n)) * T / n


def rate(T, cp, cf=Cf, b=beta, e=eta):
    """按龄保养（到 T 小时保养，或在此之前坏了就修好并重新计时）：长期每运行小时的平均花费"""
    return (cp * R(T, b, e) + cf * F(T, b, e)) / cycle_len(T, b, e)


def best(cp, cf=Cf, b=beta, e=eta):
    return min((rate(T, cp, cf, b, e), T) for T in range(20, 3000))


r_opt, T_opt = best(Cp)                          # 下班后保养：只花人工材料
r_opt2, T_opt2 = best(Cp + pm_lost)              # 生产时间里停机保养：再加少挣的毛利
r_run = Cf / mttf                                # 不保养、坏了再修
r_500 = rate(pm_h, Cp)
r_500b = rate(pm_h, Cp + pm_lost)

out = {
    "beta": beta, "eta": eta, "mttr": mttr_min, "mttr_h": mttr_min / 60, "pm_h": pm_h, "t0": t0, "over": t0 - pm_h, "H": H,
    "repair": repair, "lost_h": lost_h, "lost": lost, "Cf": Cf, "pm_min": pm_min, "pm_hr": pm_min / 60, "Cp": Cp, "pm_lost": pm_lost,
    "labor": M["LABOR_RATE"], "mat": M["PM_MATERIAL"],
    "F500": F(500) * 100, "F620": F(620) * 100, "F700": F(700) * 100, "F800": F(800) * 100, "F900": F(900) * 100,
    "h300": hz(300) * 1000, "h500": hz(500) * 1000, "h620": hz(620) * 1000, "h800": hz(800) * 1000,
    "p": p * 100, "p_after": p_after * 100, "EL": EL, "ratio": p / p_after,
    "delay": delay, "p_delay": p_delay * 100, "opt_none": opt_none, "opt_now": opt_now, "opt_later": opt_later,
    "mttf": mttf, "r_run": r_run, "r_opt": r_opt, "T_opt": T_opt, "r_opt2": r_opt2, "T_opt2": T_opt2, "r_500": r_500, "r_500b": r_500b,
    "save_opt": (1 - r_opt / r_run) * 100,
    # β = 1（失效率不变）：保养不改变下一段时间坏掉的概率；η 取 800 h（与 GRD-01 的平均寿命相近，实验 6-1 的“β = 1 对照”预置）
    "eta_exp": 800, "p_exp_0": P(0, H, 1.0, 800) * 100, "p_exp_620": P(t0, H, 1.0, 800) * 100,
    # 方案 C 未来 80 h 的总风险：先跑 4 h，保养后再跑 76 h
    "p_C": (1 - (1 - p_delay) * (1 - P(0, H - delay))) * 100,
    "ratio10": round(p / p_after, -1),
    # 推迟不等于省掉（6.6 节）：此刻的边际判别 h(t)·(C_f − C_p) 与 C(T*) 比
    "marg620": hz(t0) * (Cf - Cp),
    # MTBF 估计：近 30 天、每天 16 运行小时、3 次故障
    "mtbf": 30 * 16 / 3,
}

out["h_ratio"] = out["h620"] / out["h300"]
out["p_ok"] = 100 - out["p"]

# 习题与测验（教材第 6 章习题、作业、测验、考试题都从这里取数）
cnc = REL.PARAMS["cnc-l01-a"]            # β 2.5, η 1400, MTTR 240, 周期 600, 起始 380
out.update({
    "cnc_beta": cnc[0], "cnc_eta": cnc[1], "cnc_mttr": cnc[2], "cnc_pm": cnc[3],
    "cnc_p700": P(700, 80, cnc[0], cnc[1]) * 100,                                            # 逾期 100 h 时
    "cnc_Cf": M["REPAIR_USD"]["cnc-l01-a"] + cnc[2] / 60 * 60,                                # 非瓶颈：停机每小时 60
    "cnc_EL700": P(700, 80, cnc[0], cnc[1]) * (M["REPAIR_USD"]["cnc-l01-a"] + cnc[2] / 60 * 60),
    "cnc_Cp": 120 / 60 * M["LABOR_RATE"] + M["PM_MATERIAL"],
})
_cr, out["cnc_T"] = best(out["cnc_Cp"], out["cnc_Cf"], cnc[0], cnc[1])
out["cnc_Copt"] = _cr
out["cnc_save80"] = 80 * _cr                                               # 推迟 80 h 省下的保养摊销
out["cnc_marg"] = hz(700, cnc[0], cnc[1]) * (out["cnc_Cf"] - out["cnc_Cp"])  # 700 h 时的边际判别（$/h）
out.update({
    "q_F400": F(400) * 100,                                       # GRD-01 运行 400 h 内坏掉的概率
    "q_p300": P(300, 80) * 100,                                   # 刚保养完 300 h，再跑 80 h
    "q_mtbf": 30 * 16 / 4,                                        # 4 次故障
    "q_EL": P(300, 80) * Cf,
    "q_k5": P(100 * 5, 20 * 5) * 100,                             # 加速 ×5：运行 100 h，再 20 h
    "ex_p800": P(800, 80) * 100, "ex_EL800": P(800, 80) * Cf,
    "life_F": REL.cdf(8000, 2.0, 20000) * 100, "life_F5": REL.cdf(5000, 2.0, 20000) * 100,   # 汽车：示意 β 2、η 20000 km
})
# 机器人：协作机器人关节减速器的润滑寿命（示意值 β 2.5、η 20000 h；厂家建议 10000 h 换脂）
out.update({"rob_F10k": REL.cdf(10000, 2.5, 20000) * 100, "rob_F20k": REL.cdf(20000, 2.5, 20000) * 100,
            "rob_p": P(14000, 2000, 2.5, 20000) * 100, "rob_p0": P(0, 2000, 2.5, 20000) * 100})

for k, v in out.items():
    print(f"{k:12s} {v:.4f}" if isinstance(v, float) else f"{k:12s} {v}")

if os.environ.get("WQ_BOOK_OUT"):
    from bookout import out as book_out
    book_out(**{k: (round(v, 6) if isinstance(v, float) else v) for k, v in out.items()})
