# -*- coding: utf-8 -*-
"""第 25 章数据图（中英两版）：python3 ch25_figs.py → img/fig_25_*.png、img/en/fig_25_*.png"""
import os, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ch25_model import *
from ch25_calc import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = '#faf9f5'; INK = '#1b2430'; MUTED = '#5a6570'; GRID = '#d8dde1'
BLUE = '#2a6fdb'; ORANGE = '#e0662f'; GREEN = '#2e9e5b'; RED = '#c0392b'; PURPLE = '#8a5cc7'; TEAL = '#14797f'; GOLD = '#c48a17'
plt.rcParams.update({'font.family': ['Noto Sans CJK SC', 'DejaVu Sans'], 'font.size': 11, 'axes.edgecolor': GRID,
                     'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.titleweight': 'bold',
                     'axes.titlesize': 12.5, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8,
                     'figure.facecolor': BG, 'axes.facecolor': 'white', 'savefig.facecolor': BG, 'axes.unicode_minus': False})

def fig(w, h, title, sub, lang):
    f = plt.figure(figsize=(w, h))
    f.text(0.02, 0.965, title[lang], fontsize=17, fontweight='bold', color=INK, va='top')
    f.text(0.02, 0.905, sub[lang], fontsize=11.5, color=MUTED, va='top')
    return f

def save(f, name, lang):
    d = os.path.join(ROOT, 'img') if lang == 'zh' else os.path.join(ROOT, 'img', 'en')
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f'fig_25_{name}.png')
    f.savefig(p, dpi=200); plt.close(f); print(p)

Z = lambda zh, en: {'zh': zh, 'en': en}

# ------------------------------------------------------------------ 图 25-3 时效与孔位漂移
def f_ageing(lang):
    f = fig(10.5, 4.6, Z('时效不能省：残余应力慢慢释放，针杆孔跟着漂移', 'Why ageing cannot be skipped: residual stress relaxes and the needle-bar bore drifts'),
            Z('算例（示意值）：机臂按箱形悬臂梁，长 250 mm、截面 60×70 mm、壁厚 7 mm、E = 120 GPa；前壁 2 mm 表层有不平衡残余应力，常温下最终释放一半',
              'Worked example (illustrative): box cantilever arm 250 mm long, 60×70 mm, 7 mm wall, E = 120 GPa; unbalanced stress in a 2 mm front-wall skin, half relaxes at room temperature'), lang)
    ax = f.add_axes([0.07, 0.14, 0.52, 0.66]); bx = f.add_axes([0.68, 0.14, 0.29, 0.66])
    m = np.linspace(0, 24, 200)
    r = drift_curve(SIG_RAW, m) * 1e6; a = drift_curve(SIG_AGED, m) * 1e6
    ax.axhspan(0, 30, color=GREEN, alpha=0.07)
    ax.plot(m, r, color=RED, lw=2.4, label=Z('不时效（40 MPa）', 'No ageing (40 MPa)')[lang])
    ax.plot(m, a, color=GREEN, lw=2.4, label=Z('人工时效后（10 MPa）', 'After thermal ageing (10 MPa)')[lang])
    ax.axhline(30, color=GOLD, ls='--', lw=1.2)
    ax.text(0.4, 31.2, Z('梭尖间隙允许偏离 ±0.03 mm（第 23 章）', 'Hook-point clearance band ±0.03 mm (Chapter 23)')[lang], color=GOLD, fontsize=10)
    for y, col in ((r, RED), (a, GREEN)):
        ax.plot([12], [np.interp(12, m, y)], 'o', color=col, ms=7)
        ax.annotate(f'{np.interp(12, m, y):.0f} μm', (12, np.interp(12, m, y)), xytext=(8, -14), textcoords='offset points', color=col, fontweight='bold')
    ax.set_xlim(0, 24); ax.set_ylim(0, 36)
    ax.set_xlabel(Z('机加工以后的时间（月）', 'Months after machining')[lang]); ax.set_ylabel(Z('针杆孔前后漂移（μm）', 'Needle-bar bore drift, front–back (μm)')[lang])
    ax.set_title(Z('a　加工完的孔位随时间漂移', 'a   Bore position drifts after machining')[lang])
    ax.legend(loc='center right', frameon=False, fontsize=10)
    s = np.linspace(0, 50, 50)
    bx.plot(s, tip_drift(s * 1e6, 1) * 1e6, color=INK, lw=2, label=Z('全部释放', 'all released')[lang])
    bx.plot(s, tip_drift(s * 1e6, F_INF) * 1e6, color=BLUE, lw=2, ls='--', label=Z('释放一半', 'half released')[lang])
    for sv, col in ((40, RED), (10, GREEN)):
        bx.plot([sv], [tip_drift(sv * 1e6, 1) * 1e6], 'o', color=col, ms=7)
    bx.set_xlabel(Z('不平衡残余应力（MPa）', 'Unbalanced residual stress (MPa)')[lang]); bx.set_ylabel(Z('漂移（μm）', 'Drift (μm)')[lang])
    bx.set_title(Z('b　漂移与残余应力成正比', 'b   Drift is proportional to stress')[lang]); bx.legend(frameon=False, fontsize=10)
    save(f, 'ageing', lang)

# ------------------------------------------------------------------ 图 25-6 磨削几何
def f_grind(lang):
    c = CAMS['looper']; law = 'mtrap'
    f = fig(11, 4.9, Z('数控凸轮磨削：磨削点随凸轮转角移动，砂轮半径要随修整更新', 'CNC cam grinding: the grinding point moves; update the wheel radius after dressing'),
            Z('算例：弯针凸轮（基圆 20 mm、滚子 6 mm、行程 6 mm、推程 150°、修正梯形）；C 轴转凸轮，X 轴进退砂轮', 'Looper cam (base radius 20, roller 6, lift 6 mm, 150° rise, modified trapezoid); C axis turns the cam, X axis moves the wheel'), lang)
    ax = f.add_axes([0.02, 0.07, 0.30, 0.76]); bx = f.add_axes([0.39, 0.14, 0.27, 0.66]); cx = f.add_axes([0.73, 0.14, 0.25, 0.66])
    # a: geometry, wheel R=50 drawn (示意), at cam angle where pressure angle is largest
    Rg = 50.0
    g = grind_geometry(c, law, Rg)
    nm = nominal(c, law)
    i = int(np.argmax(nm['alpha']))
    th = -np.arctan2(g['Px'][i] + Rg * g['nx'][i], 0) * 0  # placeholder
    W = np.array([g['Px'][i] + Rg * g['nx'][i], g['Py'][i] + Rg * g['ny'][i]])
    rot = -math.atan2(W[1], W[0])            # 把砂轮中心转到 +X 轴上
    Rm = np.array([[math.cos(rot), -math.sin(rot)], [math.sin(rot), math.cos(rot)]])
    P = Rm @ np.vstack([g['Px'], g['Py']]); Wc = Rm @ W; Pi = P[:, i]
    ax.fill(P[0], P[1], color='#e9f0fc', ec=BLUE, lw=1.8)
    ax.plot(0, 0, '+', color=INK, ms=10)
    t = np.linspace(math.pi - 0.75, math.pi + 0.75, 100)
    ax.plot(Wc[0] + Rg * np.cos(t), Wc[1] + Rg * np.sin(t), color=ORANGE, lw=2)
    ax.plot([0, Wc[0] - Rg + 4], [0, 0], color=MUTED, ls='--', lw=1)
    ax.plot([Pi[0], Pi[0] + (Wc[0] - Pi[0]) * 0.45], [Pi[1], Pi[1] + (Wc[1] - Pi[1]) * 0.45], color=RED, lw=1.5)
    ax.plot([0, Pi[0]], [0, Pi[1]], color=GREEN, lw=1.2)
    ax.plot(*Pi, 'o', color=RED, ms=6)
    ax.text(Pi[0] - 2, Pi[1] - 7,  Z('磨削点', 'grinding point')[lang], color=RED, fontsize=10, ha='right')
    ax.text(-2, 3, Z('中心连线（X 轴）', 'line of centres (X axis)')[lang], color=MUTED, fontsize=9.5)
    ax.text(-25, -32, Z('凸轮（C 轴）', 'cam (C axis)')[lang], color=BLUE, fontsize=10)
    ax.text(Wc[0] - Rg - 2, 28, Z('砂轮（画成 R 50，示意）', 'wheel (drawn R 50, schematic)')[lang], color=ORANGE, fontsize=9.5, ha='right')
    lag = math.degrees(math.atan2(Pi[1], Pi[0]))
    ax.text(8, Pi[1] * 0.5 - 4.5, f'{abs(lag):.1f}°', color=GREEN, fontsize=10, fontweight='bold')
    ax.set_xlim(-34, 40); ax.set_ylim(-36, 36); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(Z('a　磨削点不在中心连线上', 'a   Grinding point off the line of centres')[lang], y=0.98)
    deg = np.degrees(PHI)
    for Rg_, col in ((200, BLUE), (100, PURPLE), (50, ORANGE)):
        gg = grind_geometry(c, law, Rg_)
        thd = np.degrees(gg['th']); thd = (thd - thd[0]) % 360
        o = np.argsort(thd)
        bx.plot(thd[o], np.degrees(gg['lag'][o]), color=col, lw=1.8, label=f'R = {Rg_} mm')
    bx.set_xlim(0, 360); bx.set_xticks(range(0, 361, 90))
    bx.set_xlabel(Z('凸轮转角（°）', 'Cam angle (°)')[lang]); bx.set_ylabel(Z('磨削点偏离中心连线的角度（°）', 'Offset from line of centres (°)')[lang])
    bx.set_title(Z('b　磨削点随转角来回移动', 'b   The grinding point moves')[lang]); bx.legend(frameon=False, fontsize=9.5)
    # c: un-updated radius
    for d, col in ((0.05, BLUE), (0.2, RED)):
        e = d * 1e3 / np.cos(nm['alpha'])
        cx.plot(deg, e, color=col, lw=2, label=Z(f'少修正 {d*1000:.0f} μm', f'{d*1000:.0f} μm not updated')[lang])
        cx.text(200, e.max() + 4, Z(f'尺寸 +{e.mean():.0f}，形状 {e.max()-e.min():.1f} μm', f'size +{e.mean():.0f}, shape {e.max()-e.min():.1f} μm')[lang], color=col, fontsize=9.5, ha='center')
    cx.set_xlim(0, 360); cx.set_xticks(range(0, 361, 90)); cx.set_ylim(0, 240)
    cx.set_xlabel(Z('凸轮转角（°）', 'Cam angle (°)')[lang]); cx.set_ylabel(Z('升程误差（μm）', 'Lift error (μm)')[lang])
    cx.set_title(Z('c　修整后没更新砂轮半径', 'c   Radius not updated after dressing')[lang]); cx.legend(frameon=False, fontsize=9.5, loc='center right')
    save(f, 'grind', lang)

# ------------------------------------------------------------------ 图 25-7 廓线误差与加速度误差
def f_error(lang):
    c = CAMS['looper']; law = 'mtrap'; deg = np.degrees(PHI)
    f = fig(11.5, 4.9, Z('廓线误差：低阶影响升程，高阶影响加速度', 'Profile error: low orders affect lift, high orders affect acceleration'),
            Z('算例：弯针凸轮，最高 6000 r/min；渗碳淬火变形 2、3 阶各 20、8 μm，精磨一次（复映系数 0.25）；机床误差 6 阶 3 μm；补偿磨削一轮', 'Looper cam, 6000 r/min; carburising distortion 20/8 μm (orders 2/3), one finish pass (replication 0.25); machine error 3 μm at order 6'), lang)
    ax = f.add_axes([0.06, 0.14, 0.27, 0.66]); bx = f.add_axes([0.40, 0.14, 0.26, 0.66]); cx = f.add_axes([0.73, 0.14, 0.25, 0.66])
    e = error_curve(c, law); r0 = evaluate(c, law, e, 6000); e1 = compensate(e); r1 = evaluate(c, law, e1, 6000)
    ax.axhspan(-5, 5, color=GREEN, alpha=0.08)
    ax.plot(deg, r0['shape'], color=RED, lw=2, label=Z(f'磨后 P-V {r0["pv"]:.1f} μm', f'as ground P-V {r0["pv"]:.1f} μm')[lang])
    ax.plot(deg, r1['shape'], color=GREEN, lw=2, label=Z(f'补偿一轮 P-V {r1["pv"]:.1f} μm', f'after 1 round P-V {r1["pv"]:.1f} μm')[lang])
    ax.set_xlim(0, 360); ax.set_xticks(range(0, 361, 90)); ax.set_ylim(-12, 14)
    ax.set_xlabel(Z('凸轮转角（°）', 'Cam angle (°)')[lang]); ax.set_ylabel(Z('升程形状误差（μm，已去掉平均值）', 'Lift shape error (μm, mean removed)')[lang])
    ax.set_title(Z('a　升程误差：限值 P-V 10 μm', 'a   Lift error: limit 10 μm P-V')[lang]); ax.legend(frameon=False, fontsize=9.5, loc='upper right')
    k = np.arange(1, 41)
    for n, col in ((6000, RED), (3000, BLUE)):
        bx.semilogy(k, 1e-6 * (k * omega(n)) ** 2, 'o-', color=col, ms=3, lw=1.5, label=f'{n} r/min')
    bx.axhline(a_limit(c), color=GOLD, ls='--'); bx.text(1.5, a_limit(c) * 1.25, Z(f'限值 {a_limit(c):.0f} m/s²', f'limit {a_limit(c):.0f} m/s²')[lang], color=GOLD, fontsize=9.5)
    bx.set_xlabel(Z('谐波阶次 k', 'Harmonic order k')[lang]); bx.set_ylabel(Z('1 μm 误差引起的加速度误差（m/s²）', 'Acceleration error per 1 μm (m/s²)')[lang])
    bx.set_title(Z('b　e·(kω)²：阶次加倍，影响变四倍', 'b   e·(kω)²: 2× order, 4× effect')[lang], fontsize=11.5); bx.legend(frameon=False, fontsize=9.5)
    ec = error_curve(c, law, k=24, ek=2.0); ec1 = compensate(ec)
    n = np.linspace(1000, 7000, 200)
    for ee, col, lab in ((e, GREEN, Z('6 阶 3 μm（默认）', 'order 6, 3 μm (default)')), (ec, RED, Z('24 阶振纹 2 μm', 'order-24 chatter 2 μm')), (ec1, PURPLE, Z('振纹，补偿一轮后', 'chatter, after 1 round'))):
        a6 = evaluate(c, law, ee, 6000)['aemax']
        cx.plot(n, a6 * (n / 6000) ** 2, color=col, lw=2, label=lab[lang])
    cx.axhline(a_limit(c), color=GOLD, ls='--')
    for ee, col in ((ec, RED), (ec1, PURPLE)):
        na = n_allow(c, law, ee); cx.plot([na], [a_limit(c)], 'o', color=col, ms=6)
        cx.annotate(f'{na:.0f}', (na, a_limit(c)), xytext=(-12, 8) if col == RED else (10, -16), textcoords='offset points', color=col, fontsize=9.5, fontweight='bold', ha='right' if col == RED else 'left')
    cx.set_xlim(1000, 7000); cx.set_ylim(0, 600)
    cx.set_xlabel(Z('转速（r/min）', 'Speed (r/min)')[lang]); cx.set_ylabel(Z('加速度误差峰值（m/s²）', 'Peak acceleration error (m/s²)')[lang])
    cx.set_title(Z('c　加速度误差随转速平方增长', 'c   Error grows with speed²')[lang]); cx.legend(frameon=False, fontsize=9.2, loc='upper left')
    save(f, 'error', lang)
    return r0, r1

# ------------------------------------------------------------------ 图 25-8 SPC
def spc_data():
    rng = np.random.default_rng(7)
    nom = 0.0; sig = 0.004
    means = []; ranges = []; data = []
    for g in range(25):
        drift = 0.0 if g < 16 else 0.0028 * (g - 15)      # 第 17 组起夹具定位销磨损，均值慢慢偏移（示意）
        x = rng.normal(nom + drift, sig, 5); data.append(x)
        means.append(x.mean()); ranges.append(x.max() - x.min())
    return np.array(data), np.array(means), np.array(ranges)

def spc_limits(means, ranges, ng=15):
    A2_, D3, D4, d2 = 0.577, 0.0, 2.114, 2.326
    xb = means[:ng].mean(); rb = ranges[:ng].mean()
    return xb, rb, xb + A2_ * rb, xb - A2_ * rb, D4 * rb, rb / d2

def f_spc(lang):
    data, means, ranges = spc_data(); xb, rb, ucl, lcl, uclr, sig = spc_limits(means, ranges)
    tol = 0.02
    cpk = min(tol - xb, xb + tol) / (3 * sig)
    f = fig(11, 5.0, Z('三坐标数据进历史库：均值–极差控制图发现夹具磨损', 'CMM data in the historian: an X̄–R chart catches fixture wear'),
            Z(f'示意数据：上轴孔到下轴孔的中心距偏差（名义值 ±0.02 mm），每 5 件一组；前 15 组定控制限，Cpk ≈ {cpk:.2f}；第 17 组起定位销磨损',
              f'Illustrative: upper-to-lower bore centre-distance deviation (±0.02 mm), subgroups of 5; limits from groups 1–15, Cpk ≈ {cpk:.2f}; pin wears from group 17'), lang)
    ax = f.add_axes([0.07, 0.47, 0.90, 0.33]); bx = f.add_axes([0.07, 0.10, 0.90, 0.26])
    g = np.arange(1, 26)
    ax.plot(g, means * 1000, 'o-', color=BLUE, lw=1.5, ms=5)
    for y, col, lab in ((ucl, RED, 'UCL'), (xb, MUTED, 'X̄'), (lcl, RED, 'LCL')):
        ax.axhline(y * 1000, color=col, ls='--' if lab != 'X̄' else '-', lw=1)
        ax.text(25.7, y * 1000, f'{lab} {y*1000:.1f}', color=col, fontsize=9.5, va='center', bbox=dict(fc=BG if False else 'white', ec='none', pad=1))
    ax.axhline(20, color=GOLD, lw=1); ax.text(1, 21, Z('公差上限 +20 μm', 'upper tolerance +20 μm')[lang], color=GOLD, fontsize=9.5)
    out = np.where(means > ucl)[0]
    ax.plot(g[out], means[out] * 1000, 'o', color=RED, ms=9, mfc='none', mew=2)
    run = None
    for i in range(6, 25):
        if all(means[j] > xb for j in range(i - 6, i + 1)):
            run = i; break
    i0 = out[0]
    ax.annotate(Z(f'第 {g[i0]} 组超出控制上限：报警，此时零件还在公差内', f'Group {g[i0]} exceeds the UCL: alarm while parts are still in tolerance')[lang],
                (g[i0], means[i0] * 1000), xytext=(g[i0] - 12, 14), color=RED, fontsize=10, arrowprops=dict(arrowstyle='->', color=RED))
    j0 = int(np.argmax(means > tol))
    ax.annotate(Z(f'第 {g[j0]} 组均值超差', f'group {g[j0]} mean out of tolerance')[lang], (g[j0], means[j0] * 1000), xytext=(g[j0] - 5.5, -11), color=GOLD, fontsize=10, arrowprops=dict(arrowstyle='->', color=GOLD))
    ax.set_xlim(0.5, 27.5); ax.set_ylim(-14, 24); ax.set_ylabel(Z('组均值（μm）', 'Subgroup mean (μm)')[lang]); ax.set_xticks(g)
    ax.set_xticklabels([])
    bx.bar(g, ranges * 1000, color=TEAL, alpha=0.75, width=0.6)
    bx.axhline(uclr * 1000, color=RED, ls='--', lw=1); bx.text(25.7, uclr * 1000, f'UCL {uclr*1000:.1f}', color=RED, fontsize=9.5, va='center', bbox=dict(fc='white', ec='none', pad=1))
    bx.axhline(rb * 1000, color=MUTED, lw=1); bx.text(25.7, rb * 1000, f'R̄ {rb*1000:.1f}', color=MUTED, fontsize=9.5, va='center', bbox=dict(fc='white', ec='none', pad=1))
    bx.set_xlim(0.5, 27.5); bx.set_xticks(g); bx.set_ylabel(Z('组极差（μm）', 'Range (μm)')[lang]); bx.set_xlabel(Z('子组序号', 'Subgroup')[lang])
    save(f, 'spc', lang)
    return xb, rb, ucl, lcl, uclr, cpk, run, out

if __name__ == '__main__':
    for L in ('zh', 'en'):
        f_ageing(L); f_grind(L); print(f_error(L)[0]['pv']); print(f_spc(L))
