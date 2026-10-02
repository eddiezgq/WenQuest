# -*- coding: utf-8 -*-
"""第 21 章算例：花样机原型 WQ-SC/PS 与缩比横机原型 WQ-SC/FK。
所有正文算例值由本脚本算出（python3 figsrc/ch21_calc.py）。虚拟实验 labs/proto-fk.html 用同一组公式和参数。
数值均为示意/算例值，不对应任何厂商型号。"""
import math, random

# ---------------------------------------------------------------- 花样机原型 PS
R, LC, TIP = 15.5, 55.0, 18.0          # 第 3/15 章机头算例
lam = R / LC
def xN(phi):  # 针杆位移，phi 弧度
    return R * (1 - math.cos(phi)) - LC * (1 - math.sqrt(1 - lam ** 2 * math.sin(phi) ** 2))
def window(t):
    e = l = None
    d = 0.0
    while d <= 180:
        if TIP - xN(math.radians(d)) < t: e = d; break
        d += 0.01
    d = 180.0
    while d <= 360:
        if TIP - xN(math.radians(d)) >= t: l = d; break
        d += 0.01
    return e, l, 360 - (l - e)

# S 形（七段式）运动规律：加速度在每半程内按 1/8 斜升、1/4 恒定、1/8 斜降（τ 为 0..1 归一化时间）
def s_acc(tau):
    """归一化加速度形状，峰值为 1"""
    if tau < 0 or tau > 1: return 0.0
    sgn = 1.0
    if tau > 0.5: tau = 1 - tau; sgn = -1.0
    if tau < 1/8: a = tau * 8
    elif tau < 3/8: a = 1.0
    else: a = (0.5 - tau) * 8
    return sgn * a
def s_profile(n=4000):
    """数值积分得到 f(τ)、f'(τ)、f''(τ)，并归一化位移为 1。返回 (C, Cv, rms_shape)"""
    dt = 1.0 / n; v = 0.0; x = 0.0; xs = []; vs = []; acc2 = 0.0
    for k in range(n):
        tau = (k + 0.5) * dt; a = s_acc(tau)
        v += a * dt; x += v * dt; xs.append(x); vs.append(v); acc2 += a * a * dt
    scale = 1.0 / x                       # 让位移 = 1
    C = scale                              # 峰值加速度系数：a_pk = C s /Δt²
    Cv = max(vs) * scale                   # 峰值速度系数：v_pk = Cv s/Δt
    return C, Cv, math.sqrt(acc2)          # rms_shape = rms(a)/a_pk over the move
C_S, Cv_S, RMS_S = s_profile()
def _s_table(n=4000):
    dt = 1.0 / n; v = 0.0; x = 0.0; tab = [0.0]
    for k in range(n):
        a = s_acc((k + 0.5) * dt); v0 = v; v += a * dt; x += (v0 + v) / 2 * dt; tab.append(x)
    return [t / tab[-1] for t in tab]
_ST = _s_table()
def s_pos(tau):
    """f(τ)：S 形归一化位移（查表线性插值，f(0)=0，f(1)=1）"""
    if tau <= 0: return 0.0
    if tau >= 1: return 1.0
    k = tau * (len(_ST) - 1); i = int(k); f = k - i
    return _ST[i] * (1 - f) + _ST[i + 1] * f

# 主轴
N_HEAD = 2500          # 原型机头限速 r/min（示意）
MARGIN = 20.0          # 窗口两端各留 10°
# X–Y：A-BSC-SFU 16x10 + 1:1 同步带（A-PUL-HTD 3M-20-15 两只）+ 400 W 伺服（D-MOT-PMSM，建议编号）
Ph = 0.010             # 导程 m
d0, dr = 0.016, 0.016 - 0.003175   # 公称直径、近似底径
rho, E = 7850.0, 206e9
Jm, Tr_rated, Tr_peak, n_rated = 0.30e-4, 1.27, 3.8, 3000   # 400 W 伺服典型参数（与第 15 章同）
Jp = 0.5 * (2700 * math.pi * 0.00955 ** 2 * 0.020) * 0.00955 ** 2   # 3M-20 铝带轮 PD 19.1 mm, 宽 20 mm 近似实心
eta, mu, g = 0.9, 0.05, 9.8
AXES = {'X': dict(m=4.0, Ls=0.50), 'Y': dict(m=12.0, Ls=0.40)}
AMAX = {'X': 50.0, 'Y': 40.0}     # 按发热（rms ≤ 额定）定的设计加速度，m/s²
def screw_J(Ls): return math.pi * rho * Ls * d0 ** 4 / 32
def axis_torque(m, Ls, a):
    alpha = a * 2 * math.pi / Ph
    J = Jm + 2 * Jp + screw_J(Ls) + m * (Ph / (2 * math.pi)) ** 2
    Tf = mu * m * g * Ph / (2 * math.pi * eta)
    return J * alpha + Tf, J, Tf
def axis_amax(m, Ls, Tavail):
    # 反解：Tavail = J α + Tf
    _, J, Tf = axis_torque(m, Ls, 0.0)
    return (Tavail - Tf) / J * Ph / (2 * math.pi)
def crit_speed(Ls, lam_=3.927):   # 固定-支承
    I = math.pi * dr ** 4 / 64; A = math.pi * dr ** 2 / 4
    return 60 * lam_ ** 2 / (2 * math.pi * Ls ** 2) * math.sqrt(E * I / (rho * A))

def ps_report():
    e, l, W = window(1.5)
    Wu = W - MARGIN
    print('== PS 窗口  t=1.5 mm: 入布 %.1f°, 出布 %.1f°, W = %.1f°, 实用 Wu = %.1f°' % (e, l, W, Wu))
    print('   S 形：C = %.3f, Cv = %.3f, rms 形状 = %.3f' % (C_S, Cv_S, RMS_S))
    n = 1600; s = 3.0
    dt = Wu / (6 * n)
    a = C_S * s / 1000 / dt ** 2; vpk = Cv_S * s / 1000 / dt
    print('   n=%d: Δt = %.2f ms; s=3 mm 需 a = %.1f m/s², v_pk = %.3f m/s -> 电机 %.0f r/min' % (n, dt * 1e3, a, vpk, vpk / Ph * 60))
    print('   对照等加速等减速：a = %.1f m/s²' % (4 * s / 1000 / dt ** 2))
    for k, ax in AXES.items():
        T, J, Tf = axis_torque(ax['m'], ax['Ls'], a)
        print('   %s 轴: m=%.0f kg, J_screw=%.3e, J_load=%.3e, Jp=%.2e, J_tot=%.3e, (J-Jm)/Jm=%.2f, T_pk(a=%.1f)=%.2f N·m, Tf=%.4f' % (
            k, ax['m'], screw_J(ax['Ls']), ax['m'] * (Ph / 2 / math.pi) ** 2, Jp, J, (J - Jm) / Jm, a, T, Tf))
        print('      临界转速(固定-支承) L=%.2f m: %.0f r/min' % (ax['Ls'], crit_speed(ax['Ls'])))
        for aa in (AMAX[k], axis_amax(ax['m'], ax['Ls'], 0.8 * Tr_peak)):
            Tpk = axis_torque(ax['m'], ax['Ls'], aa)[0]
            Trms = Tpk * RMS_S * math.sqrt(Wu / 360)
            print('      a=%.1f: T_pk=%.2f, 满窗口 T_rms = %.2f N·m (额定 %.2f)' % (aa, Tpk, Trms, Tr_rated))
        print('      rms=额定 时 a = %.1f' % axis_amax(ax['m'], ax['Ls'], Tr_rated / (RMS_S * math.sqrt(Wu / 360))))
    ax_ = dict(AMAX)
    print('   针距–转速上限（S 形，Wu=%.1f°，机头限 %d，aX=%.0f aY=%.0f）' % (Wu, N_HEAD, ax_['X'], ax_['Y']))
    for s in [1, 2, 3, 4, 5, 6]:
        row = []
        for k in 'XY':
            dt = math.sqrt(C_S * s / 1000 / ax_[k]); row.append(min(N_HEAD, Wu / (6 * dt)))
        dt45 = math.sqrt(C_S * s / math.sqrt(2) / 1000 / ax_['Y'])
        print('     s=%d mm: 沿 X %.0f, 沿 Y %.0f, 45° %.0f r/min' % (s, row[0], row[1], min(N_HEAD, Wu / (6 * dt45))))
    # 刚度对照：丝杠 vs 同步带（第 15 章 82 Hz）
    A = math.pi * dr ** 2 / 4
    for k, ax in AXES.items():
        ks = A * E / ax['Ls']                # 固定-自由最不利
        fn = math.sqrt(ks / ax['m']) / (2 * math.pi)
        print('   %s 丝杠轴向刚度(最不利) %.0f N/μm, fn ≈ %.0f Hz' % (k, ks / 1e6, fn))
    # 插补点数与延迟补偿
    Td = 1.0e-3
    print('   1 ms 插补：每针 %.0f 点；驱动延迟 1 ms 在 2000 r/min = %.1f°, 2500 = %.1f°' % (Wu / (6 * 2000) * 1000, 6 * 2000 * Td, 6 * 2500 * Td))
    # 分辨率
    print('   编码器 10000 计数/转 -> %.1f μm/计数' % (Ph / 10000 * 1e6))
    # 一个 0.1 mm 单位的增量 int8 范围
    print('   int8 增量 0.1 mm -> ±12.7 mm')
    return Wu, ax_

def lookahead(steps, ax_, Wu, dn=300, n_start=400, n_slow=400, k_slow=(2, 2)):
    caps = []
    for (dx, dy) in steps:
        tx = math.sqrt(C_S * abs(dx) / 1000 / ax_['X']) if dx else 0
        ty = math.sqrt(C_S * abs(dy) / 1000 / ax_['Y']) if dy else 0
        t = max(tx, ty)
        caps.append(N_HEAD if t == 0 else min(N_HEAD, Wu / (6 * t)))
    N = len(caps)
    for i in range(min(k_slow[0], N)): caps[i] = min(caps[i], n_slow)
    for i in range(max(0, N - k_slow[1]), N): caps[i] = min(caps[i], n_slow)
    c = caps[:]
    for i in range(N - 2, -1, -1): c[i] = min(c[i], c[i + 1] + dn)
    n = [0] * N; n[0] = min(c[0], n_start)
    for i in range(1, N): n[i] = min(c[i], n[i - 1] + dn)
    return caps, n

# ---------------------------------------------------------------- 横机原型 FK
FK = dict(E=5, N=60, vmax=0.6, a=10.0, c=40.0, Lk=80.0, Tr=1.5, J=0.3, Tctrl=1.0, fpga=False,
          res=0.01, seg=8, mode='rt', Lf=0.9, trev=0.10)
def pitch(P): return 25.4 / P['E']
def stroke(P): return 2 * P['c'] + P['N'] * pitch(P) + P['Lk']      # mm
def kin(P):
    """返回 (D m, 实际峰值速度, t_acc, t_cruise, t_total)"""
    D = stroke(P) / 1000; a = P['a']; v = P['vmax']
    if D <= v * v / a:
        vp = math.sqrt(a * D); ta = vp / a; return D, vp, ta, 0.0, 2 * ta
    ta = v / a; tc = (D - v * v / a) / v; return D, v, ta, tc, 2 * ta + tc
def x_of_t(P, t):
    D, vp, ta, tc, T = kin(P); a = P['a']
    if t <= 0: return 0.0
    if t <= ta: return 0.5 * a * t * t * 1000
    if t <= ta + tc: return (0.5 * a * ta * ta + vp * (t - ta)) * 1000
    if t <= T: td = t - ta - tc; return (0.5 * a * ta * ta + vp * tc + vp * td - 0.5 * a * td * td) * 1000
    return D * 1000
def v_of_t(P, t):
    D, vp, ta, tc, T = kin(P); a = P['a']
    if t <= 0: return 0.0
    if t <= ta: return a * t
    if t <= ta + tc: return vp
    if t <= T: return max(0.0, vp - a * (t - ta - tc))
    return 0.0
def t_of_x(P, x):
    """x_of_t 的解析反函数（x 以 mm 计）"""
    D, vp, ta, tc, T = kin(P); a = P['a']; x = x / 1000
    xa = 0.5 * a * ta * ta
    if x <= 0: return 0.0
    if x <= xa: return math.sqrt(2 * x / a)
    if x <= xa + vp * tc: return ta + (x - xa) / vp
    if x >= D: return T
    r = x - xa - vp * tc                      # 减速段：r = vp td - a td²/2
    disc = max(0.0, vp * vp - 2 * a * r)
    return ta + tc + (vp - math.sqrt(disc)) / a
def needle_x(P, i): return P['c'] + (i + 0.5) * pitch(P)     # 从起点量的位置，mm
def qtime(P, u):
    """触发量化（时间，s）：MCU 为控制周期；FPGA 为走过一个编码器计数的时间"""
    if P['fpga']: return (P['res'] / 1000) / max(u, 1e-4)
    return P['Tctrl'] / 1000
def lead_mm(P, u):
    q = qtime(P, u)
    if P['mode'] == 'rt': return u * (P['Tr'] / 1000 + q / 2) * 1000
    if P['mode'] == 'fixed': return P['Lf']
    return 0.0
def needle_err(P, i, qf, jf):
    """qf ∈ [0,1] 触发量化所占比例；jf ∈ [-1,1] 响应抖动比例。返回误差 mm（正 = 滞后）"""
    xi = needle_x(P, i)
    # 迭代求命令点：实时补偿时用到达命令点时的速度
    xc = xi
    for _ in range(4):
        tc_ = t_of_x(P, max(0.0, xc)); u = v_of_t(P, tc_)
        xc = xi - lead_mm(P, u)
    tc_ = t_of_x(P, max(0.0, xc)); u = v_of_t(P, tc_)
    q = qtime(P, max(u, 1e-3))
    tf = tc_ + qf * q
    tact = tf + P['Tr'] / 1000 + jf * P['J'] / 1000
    return x_of_t(P, tact) - xi, u
def needle_bounds(P, i):
    es = [needle_err(P, i, qf, jf)[0] for qf in (0.0, 1.0) for jf in (-1.0, 1.0)]
    return min(es), max(es)
def seg_ok(P, i):
    u = v_of_t(P, t_of_x(P, needle_x(P, i)))
    return P['seg'] * pitch(P) / 1000 / max(u, 1e-6) >= 2 * P['Tr'] / 1000
def fk_eval(P):
    p = pitch(P); worst = 0.0; bad_acc = 0
    for i in range(P['N']):
        lo, hi = needle_bounds(P, i)
        w = max(abs(lo), abs(hi)); worst = max(worst, w)
        if w > 0.1 * p or not seg_ok(P, i): bad_acc += 1
    D, vp, ta, tc, T = kin(P)
    trow = T + P['trev']
    return dict(p=p, worst=worst, worst_p=worst / p, bad_acc=bad_acc, trow=trow, rph=3600 / trow, vp=vp, D=D)
def fk_vmax(P, crit=0.1):
    lo, hi = 0.05, 4.0
    for _ in range(40):
        mid = (lo + hi) / 2; Q = dict(P, vmax=mid)
        if fk_eval(Q)['bad_acc'] == 0: lo = mid
        else: hi = mid
    return lo

def fk_report():
    P = dict(FK); p = pitch(P)
    print('== FK 基准：E%d p=%.2f mm, 针床宽 %.1f mm, 行程 D=%.1f mm' % (P['E'], p, P['N'] * p, stroke(P)))
    v = P['vmax']
    print('   t_n = p/v = %.2f ms；每段 %d 针一次：%.1f ms ≥ 选针器周期 %.1f ms' % (p / v, P['seg'], P['seg'] * p / v, 2 * P['Tr']))
    print('   提前量 v(Tr+Tc/2) = %.2f mm = %.3f p' % (v * (P['Tr'] + P['Tctrl'] / 2), v * (P['Tr'] + P['Tctrl'] / 2) / p))
    print('   预算：量化 ±%.2f mm，抖动 ±%.2f mm，合计 %.2f mm = %.3f p' % (v * P['Tctrl'] / 2, v * P['J'], v * (P['Tctrl'] / 2 + P['J']), v * (P['Tctrl'] / 2 + P['J']) / p))
    r = fk_eval(P)
    print('   模型最坏误差 %.3f mm = %.3f p；超验收 %d；一行 %.3f s；%.0f 行/h' % (r['worst'], r['worst_p'], r['bad_acc'], r['trow'], r['rph']))
    print('   不补偿时滞后 v(Tr+Tc/2)= %.3f p' % (v * (P['Tr'] + P['Tctrl']/2) / p))
    vm = fk_vmax(P); print('   任务1 MCU 1 ms: v_max = %.3f m/s；解析 %.3f' % (vm, 0.1 * p / (P['Tctrl'] / 2 + P['J'])))
    r1 = fk_eval(dict(P, vmax=vm)); print('       该速度一行 %.3f s, %.0f 行/h' % (r1['trow'], r1['rph']))
    print('       不错选（0.25p）上限解析 %.3f m/s' % (0.25 * p / (P['Tctrl'] / 2 + P['J'])))
    for tc in (0.5, 0.25):
        print('       MCU %.2f ms: v_max = %.3f' % (tc, fk_vmax(dict(P, Tctrl=tc))))
    Pf = dict(P, fpga=True); vf = fk_vmax(Pf)
    print('   任务2 FPGA: v_max = %.3f m/s；解析 %.3f' % (vf, (0.1 * p - P['res'] / 2) / P['J']))
    r2 = fk_eval(dict(Pf, vmax=vf)); print('       一行 %.3f s, %.0f 行/h，峰值 %.3f；比 MCU 多 %.0f%%' % (r2['trow'], r2['rph'], r2['vp'], (r2['rph'] / r1['rph'] - 1) * 100))
    print('       单段选针器 E5 上限 p/(2Tr) = %.2f m/s' % (p / 1000 / (2 * P['Tr'] / 1000)))
    # E7
    P7 = dict(Pf, E=7); p7 = pitch(P7)
    print('   E7: p=%.3f, FPGA 实时 v_max = %.3f' % (p7, fk_vmax(P7)))
    print('       E7 MCU 1ms 实时 v_max = %.3f' % fk_vmax(dict(P7, fpga=False)))
    P7f = dict(P7, mode='fixed', vmax=1.0)
    best = None
    for c in (20, 30, 40, 50, 60, 70):
        for Lf10 in range(10, 25):
            Lf = Lf10 / 10; r = fk_eval(dict(P7f, c=c, Lf=Lf))
            if r['bad_acc'] == 0 and best is None: best = (c, Lf, r)
    for c in (40, 46, 50, 60):
        r = fk_eval(dict(P7f, c=c, Lf=1.5)); print('       E7 FPGA 固定 Lf=1.5 v=1.0 c=%d: worst %.3f p, 超验收 %d, 行 %.3f s' % (c, r['worst_p'], r['bad_acc'], r['trow']))
    for Lf in (1.3, 1.4, 1.45, 1.5, 1.55, 1.6):
        r = fk_eval(dict(P7f, c=50, Lf=Lf)); print('       c=50 Lf=%.2f: worst %.3f p, 超验收 %d' % (Lf, r['worst_p'], r['bad_acc']))
    print('       最小 c 组合：', best[:2], round(best[2]['trow'], 3))
    print('       解析：Lf=1.5 时需 u ≥ %.3f m/s -> c ≥ %.1f mm' % (1.147 / 1.2, (1.147 / 1.2) ** 2 / 20 * 1000))
    # 不补偿 / 固定提前量 E5 MCU
    for mode in ('none', 'fixed'):
        r = fk_eval(dict(P, mode=mode, Lf=0.9)); print('   E5 MCU 模式 %s: worst %.3f p, 超验收 %d' % (mode, r['worst_p'], r['bad_acc']))
    # 伺服选型（机头）
    m, Fcam, mu_c = 2.5, 15.0, 0.1
    rp = 31.831 / 2 / 1000
    F = m * P['a'] + mu_c * m * g + Fcam
    Jm2 = 0.18e-4; Jpul = 0.5 * (2700 * math.pi * 0.0159 ** 2 * 0.02) * 0.0159 ** 2
    T = F * rp + (Jm2 + 2 * Jpul) * P['a'] / rp
    Tc = (mu_c * m * g + Fcam) * rp
    print('   机头驱动：F=%.1f N, T_pk=%.3f N·m, 匀速 %.3f N·m, 2 m/s -> %.0f r/min, %.3f mm/计数' % (F, T, Tc, 2 / (2 * math.pi * rp) * 60, 2 * math.pi * rp * 1000 / 10000))
    # 带伸长
    k = 150e3 / 0.3 + 150e3 / 0.5
    print('   带弹性：k=%.0f N/mm, 加速段伸长 %.3f mm' % (k / 1000, m * P['a'] / k * 1000))
    # 制动距离
    print('   急停（20 m/s²）从 1.6 m/s: %.0f mm' % (1.6 ** 2 / 40 * 1000))
    # 20 行样片
    r = fk_eval(P); print('   20 行样片（0.6 m/s）：%.1f s' % (20 * r['trow']))
    # 统计错选
    random.seed(1); bad = 0; rows = 1000
    Pm = dict(P, vmax=1.2)
    for _ in range(rows):
        for i in range(P['N']):
            e, u = needle_err(Pm, i, random.random(), random.uniform(-1, 1))
            if abs(e) > 0.25 * p: bad += 1
    print('   v=1.2 MCU 1 ms：1000 行错选 %d 针 (%.3f%%)' % (bad, bad / rows / P['N'] * 100))

if __name__ == '__main__':
    Wu, ax_ = ps_report()
    steps = [(2.0, 0)] * 4 + [(0, 6.0)] + [(2.0, 0)] * 3
    caps, n = lookahead(steps, ax_, Wu, k_slow=(0, 0), n_start=N_HEAD)
    print('   前瞻X2/Y6：caps', [round(c) for c in caps]); print('         n', [round(x) for x in n])
    import sys
    if 'ps' not in sys.argv: fk_report()
