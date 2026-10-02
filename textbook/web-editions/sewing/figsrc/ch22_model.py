# -*- coding: utf-8 -*-
"""第 22 章 自动化测试与持续迭代：算例模型（与虚拟实验 labs/testbench.html 相同）。

运行：python3 figsrc/ch22_model.py   → 打印正文用到的全部算例值
模型都是示意：
 1. 剪线：停车剪线时主轴从起始转速 n0 减到剪线转速 300 r/min；剪线电磁铁在剪线针的 290° 发令，
    延迟 t ~ N(8 ms, 0.667 ms)（第 14 章的 6–10 ms 取为 ±3σ）；动刀进刀角 = 290° + 6·n·t，必须落在 300°–330°。
    n 取发令时（290°）的实际转速。
    伺服减速能力（第 13 章）：4400 rad/s²；高于基速 nb 进入恒功率区，能力 ∝ nb/n。
    nb 与母线电压成正比，逐次波动：nb = 4100 × κ，κ ~ N(1, 0.05)（电网电压波动，示意）。
    速度环跟随滞后用一阶 τ = J/Kv = 3 ms 表示。
    固件 v1.3.x：按 60% 能力（2640 rad/s²）规划减速，减速在剪线针的 0° 结束（第 14 章）。
    固件 v1.4.0（“快速剪线”优化）：按 100% 能力规划，减速终点推迟到剪线针的 180°。
    固件 v1.4.1（修复）：按转矩–转速曲线的 90% 规划（假定基速取下限 0.9×4100），并在 270° 检查转速，
                       高于 400 r/min 就把剪线推迟一针。
    SIL 用的是第 13 章的理想电机（无恒功率区），HIL 的电机仿真器用样机实测的转矩–转速曲线。
 2. 停针：第 13 章虚拟实验 13-1 的伺服模型；误差 = 停车过程中越过上针位的最大角度与最终误差中绝对值较大者。
    v1.3.0/1.3.1：Kp = 200 s⁻¹；v1.3.2–v1.4.1：Kp = 300 s⁻¹（“停车更快”）；v1.4.2：Kp = 220 s⁻¹。
    HIL 仿真器的惯量取样机实测 6.3×10⁻⁴ kg·m²；每次停车摩擦 Tf ~ N(0.15, 0.015) N·m、定位速度 ~ N(200, 8) r/min。
 3. 统计：零失效验证 n = ln(1−C)/ln R；有失效时用二项分布（Clopper–Pearson 单侧）置信下限。
"""
from math import pi, log, ceil, copysign, sqrt
import numpy as np
from scipy.stats import norm, beta, binom

# ---------------- 1. 剪线 ----------------
ACAP0 = 4400.0      # rad/s²，第 13 章
NB0 = 4100.0        # r/min，基速（示意）
NB_SD = 0.05
TAU = 0.003
NT = 300.0
CMD = 290.0
WIN = (300.0, 330.0)
T_MU, T_SD = 8e-3, 0.667e-3

FW = {   # 版本 → (减速规划, Kp, 回针补偿, 说明)
    "v1.3.0": dict(plan="v13", Kp=200, bt=0.20, note="基线"),
    "v1.3.1": dict(plan="v13", Kp=200, bt=0.12, note="加回针补偿"),
    "v1.3.2": dict(plan="v13", Kp=300, bt=0.12, note="位置增益 200→300，停车更快"),
    "v1.4.0": dict(plan="v140", Kp=300, bt=0.12, note="快速剪线：减速按 100% 能力、终点推迟到 180°"),
    "v1.4.1": dict(plan="v141", Kp=300, bt=0.12, note="修复剪线：按转矩–转速曲线规划 + 270° 转速检查"),
    "v1.4.2": dict(plan="v141", Kp=220, bt=0.12, note="位置增益改为 220"),
}


def acap(n, nb):
    return ACAP0 * min(1.0, nb / max(n, 1.0))


def n_at_cmd(n0, plan, nb, motor="hil", dt=2e-5, trace=None):
    """返回 (发令时 290° 的实际转速 r/min, 是否被 270° 检查推迟)。"""
    w0, wt = n0 * pi / 30, NT * pi / 30
    nbm = nb if motor == "hil" else 1e9
    if plan == "v13":
        a_ref = lambda w: 0.6 * ACAP0
        end_at = 0.0
    elif plan == "v140":
        a_ref = lambda w: ACAP0
        end_at = 180.0
    else:  # v141
        a_ref = lambda w: 0.9 * acap(w * 30 / pi, 0.9 * NB0)
        end_at = 180.0
    # 先算参考减速段走过的角度，确定减速从哪里开始
    w, th = w0, 0.0
    while w > wt:
        a = a_ref(w)
        th += w * dt
        w -= a * dt
    th_r = th
    th = end_at * pi / 180 - th_r
    w, wr = w0, w0
    deferred = False
    while th < CMD * pi / 180:
        if wr > wt:
            wr = max(wt, wr - a_ref(wr) * dt)
        n = w * 30 / pi
        a = acap(n, nbm)
        acc = max(-a, min(a, (wr - w) / TAU))
        w += acc * dt
        th += w * dt
        if trace is not None:
            trace.append((th * 180 / pi, w * 30 / pi))
        if plan == "v141" and not deferred and th >= 270 * pi / 180 and w * 30 / pi > 400:
            deferred = True
    if deferred:
        return NT, True
    return w * 30 / pi, False


def p_fail_at(n):
    """发令时转速 n（r/min）下一次剪线失败的概率：进刀角出窗口。"""
    t_hi = (WIN[1] - CMD) / (6 * n)
    t_lo = (WIN[0] - CMD) / (6 * n)
    return norm.sf(t_hi, T_MU, T_SD) + norm.cdf(t_lo, T_MU, T_SD)


KS = np.linspace(1 - 3 * NB_SD, 1 + 3 * NB_SD, 13)
WK = norm.pdf(KS, 1, NB_SD)
WK = WK / WK.sum()


def p_trim(n0, ver, motor="hil"):
    plan = FW[ver]["plan"]
    p = 0.0
    for k, wgt in zip(KS, WK):
        n, _ = n_at_cmd(n0, plan, NB0 * k, motor)
        p += wgt * p_fail_at(n)
    return p


def trim_time(n0, plan):
    """停车剪线时间（从松开脚踏到剪断，示意）：减速 + 剪线针到下一转 55°。"""
    w0, wt = n0 * pi / 30, NT * pi / 30
    if plan == "v13":
        t_dec = (w0 - wt) / (0.6 * ACAP0)
        return t_dec + (415 / 360) / (NT / 60)
    if plan == "v140":
        t_dec = (w0 - wt) / ACAP0
        return t_dec + ((415 - 180) / 360) / (NT / 60)
    return None


# ---------------- 2. 停针 ----------------
D = pi / 180


def servo_stop(Kp=200, Kv=0.2, Ti=12, wp=200, e0=45, J=6.0, Tf=0.15, TEND=0.25, DT=2e-5):
    B, TMAX, TAUI = 2e-4, 2.5, 0.5e-3
    J, Ti, wpos = J * 1e-4, Ti / 1000, wp * 2 * pi / 60
    th, w = -e0 * D, wpos
    Tm = Tf + B * w
    integ = Tm / Kv if Ti > 0 else 0
    over = 0.0
    for _ in range(int(TEND / DT)):
        e = -th
        wref = max(-wpos, min(wpos, Kp * e))
        ew = wref - w
        if Ti > 0:
            integ += ew * DT / Ti
        Tref = Kv * (ew + integ)
        if abs(Tref) > TMAX:
            Tref = copysign(TMAX, Tref)
            if Ti > 0:
                integ -= ew * DT / Ti
        Tm += (Tref - Tm) * DT / TAUI
        Td = Tm - B * w
        if abs(w) < 1e-3 and abs(Td) <= Tf:
            acc = -w / DT
        else:
            acc = (Td - Tf * (copysign(1, w) if abs(w) >= 1e-3 else copysign(1, Td))) / J
        w += acc * DT
        th += w * DT
        over = max(over, th / D)
    fin = th / D
    return max(over, abs(fin))


J_HIL = 6.3


def stop_sample(Kp, n, seed=1, J=J_HIL):
    r = np.random.default_rng(seed)
    # 测量含编码器量化与读数噪声，σ = 0.03°（示意）
    return np.array([servo_stop(Kp=Kp, J=J, Tf=r.normal(0.15, 0.015), wp=r.normal(200, 8), DT=4e-5) + r.normal(0, 0.03)
                     for _ in range(n)])


def cpu(x, usl=1.0):
    return (usl - x.mean()) / (3 * x.std(ddof=1))


# ---------------- 3. 统计 ----------------
def n_zero(R, C):
    return ceil(log(1 - C) / log(R))


def r_lower(n, x, C=0.95):
    """n 次里 x 次失效，可靠度的单侧置信下限（Clopper–Pearson）。"""
    if x >= n:
        return 0.0
    return 1 - beta.ppf(C, x + 1, n - x)


def n_with_fail(R, C, x):
    n = x + 1
    while r_lower(n, x, C) < R:
        n += 1
    return n


def max_fail(n, R=0.995, C=0.95):
    x = -1
    while r_lower(n, x + 1, C) >= R:
        x += 1
    return x


def p_detect(p, n):
    return 1 - (1 - p) ** n


if __name__ == "__main__":
    print("== 剪线：发令时转速（r/min, κ=1）与失败概率 ==")
    for ver in ("v1.3.2", "v1.4.0", "v1.4.1"):
        row = []
        for n0 in (3000, 3500, 4000, 4500, 4750, 5000):
            n, d = n_at_cmd(n0, FW[ver]["plan"], NB0)
            row.append(f"{n0}:{n:.0f}{'*' if d else ''}/{p_trim(n0, ver) * 100:.3f}%")
        print(ver, row)
    print("SIL (理想电机) v1.4.0:", [f"{p_trim(n0, 'v1.4.0', 'sil') * 100:.3f}%" for n0 in (4000, 4500, 5000)])
    print("基线失败概率 300 r/min:", f"{p_fail_at(300) * 100:.4f}%", "进刀角范围",
          [round(CMD + 6 * 300 * t, 1) for t in (6e-3, 8e-3, 10e-3)])
    for n0 in (4000, 5000):
        print("停车剪线时间", n0, "v1.3:", round(trim_time(n0, "v13") * 1000), "ms  v1.4.0:", round(trim_time(n0, "v140") * 1000), "ms")
    # 手工试缝 50 次（3000–4000）看到至少一次失败的概率
    ps = [p_trim(n0, "v1.4.0") for n0 in (3000, 3500, 4000)]
    print("手工 50 次（3000–4000 均分）看到失败的概率", 1 - np.prod([(1 - p) ** (50 / 3) for p in ps]))
    p5 = p_trim(5000, "v1.4.0"); p475 = p_trim(4750, "v1.4.0"); p45 = p_trim(4500, "v1.4.0")
    print("v1.4.0 p(4500,4750,5000)", p45, p475, p5)
    print("300 次扫描点在 5000 的期望失败", 300 * p5, " P(>=1)", p_detect(p5, 300))
    print("1000 次@4000 的期望失败", 1000 * p_trim(4000, "v1.4.0"))
    # 现场：起始转速分布（示意）在 4500–5000 的比例
    print("== 停针 ==")
    for Kp in (200, 220, 300):
        print("Kp", Kp, "nominal J=6.0:", round(servo_stop(Kp=Kp, J=6.0), 2), "J=6.3:", round(servo_stop(Kp=Kp, J=6.3), 2),
              "J±20%:", [round(servo_stop(Kp=Kp, J=j), 2) for j in (4.8, 7.2)])
        x = stop_sample(Kp, 50, seed=7)
        print("   50 次: 均值 %.3f  σ %.3f  最大 %.3f  Cpk(上限1°) %.2f" % (x.mean(), x.std(ddof=1), x.max(), cpu(x)))
    print("== 统计 ==")
    for R in (0.99, 0.995, 0.999):
        print("零失效", R, "C=0.95 →", n_zero(R, 0.95), " C=0.90 →", n_zero(R, 0.90))
    print("ln 公式原值", log(0.05) / log(0.995))
    for x in (0, 1, 2, 3):
        print("允许", x, "次失效需要 n =", n_with_fail(0.995, 0.95, x))
    for n, x in ((1000, 0), (1000, 1), (1000, 2), (1000, 3), (1500, 3)):
        print("n=%d x=%d R_L=%.4f" % (n, x, r_lower(n, x)))
    print("1000 次最多允许失效", max_fail(1000), " 1500 次", max_fail(1500), " 300 次", max_fail(300))
    print("检出 p=0.5% 漏洞 95% 需要", ceil(log(0.05) / log(1 - 0.005)))
