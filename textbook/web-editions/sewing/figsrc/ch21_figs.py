# -*- coding: utf-8 -*-
"""第 21 章数据图（中英两版）：python3 figsrc/ch21_figs.py
输出 img/fig_c21_*.png 与 img/en/fig_c21_*.png。模型与参数见 ch21_calc.py。"""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import ch21_calc as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = '#faf9f5'
COL = dict(ink='#1b2430', mute='#5a6570', b='#2a6fdb', o='#e0662f', g='#2e9e5b', p='#8a5cc7', r='#c0392b', t='#14797f', y='#c48a17', grid='#d8dde1')
plt.rcParams.update({'font.family': ['Noto Sans CJK SC', 'DejaVu Sans'], 'axes.unicode_minus': False,
                     'figure.facecolor': BG, 'axes.facecolor': BG, 'savefig.facecolor': BG,
                     'axes.edgecolor': COL['mute'], 'axes.labelcolor': COL['ink'], 'xtick.color': COL['mute'],
                     'ytick.color': COL['mute'], 'font.size': 11, 'axes.grid': True, 'grid.color': COL['grid'],
                     'grid.linewidth': 0.6, 'axes.spines.top': False, 'axes.spines.right': False})

def T(lang, zh, en): return zh if lang == 'zh' else en
def save(fig, name, lang):
    d = os.path.join(ROOT, 'img') if lang == 'zh' else os.path.join(ROOT, 'img', 'en')
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    fig.savefig(p, dpi=200); plt.close(fig); print('ok', p)

# ------------------------------------------------------------ 图 21-2 窗口→时间→加速度→转速上限
def fig_ps_budget(lang):
    e, l, W = C.window(1.5); Wu = W - C.MARGIN
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.3), gridspec_kw=dict(width_ratios=[1.25, 1]))
    ph = np.linspace(0, 720, 1441)
    h = np.array([C.TIP - C.xN(math.radians(p % 360)) for p in ph])
    a1.plot(ph, h, color=COL['b'], lw=2, label=T(lang, '针尖高度 h(φ)', 'needle-tip height h(φ)'))
    a1.axhline(1.5, color=COL['mute'], lw=1, ls='--')
    BB = dict(fc=BG, ec='none', alpha=0.9, pad=1.5)
    a1.text(8, 2.6, T(lang, '布 + 下模板 t = 1.5 mm', 'fabric + lower template t = 1.5 mm'), color=COL['mute'], fontsize=9, bbox=BB)
    for k in (0, 360):
        a1.axvspan(e + k, l + k, color=COL['r'], alpha=0.10, lw=0)
    a1.text(e + 360 + 4, -7.5, T(lang, '针在布中\n%.1f°–%.1f°' % (e, l), 'needle in\nfabric\n%.1f°–%.1f°' % (e, l)), color=COL['r'], fontsize=9, bbox=BB)
    s0 = l + C.MARGIN / 2; s1 = s0 + Wu
    a1.axvspan(s0, s1, color=COL['g'], alpha=0.12, lw=0)
    a1.text(s0 + 4, -7.5, T(lang, '实用窗口\n%.1f°' % Wu, 'usable\nwindow\n%.1f°' % Wu), color=COL['g'], fontsize=9, bbox=BB)
    a1.set_xlim(0, 720); a1.set_ylim(-14, 19); a1.set_xticks(range(0, 721, 90))
    a1.set_xlabel(T(lang, '主轴转角 φ（°）', 'spindle angle φ (°)')); a1.set_ylabel(T(lang, '针尖离针板高度（mm）', 'tip above throat plate (mm)'))
    ax2 = a1.twinx(); ax2.grid(False); ax2.spines['right'].set_visible(True)
    xs = []
    for p in ph:
        tau = (p - s0) / Wu
        xs.append(3.0 * C.s_pos(min(max(tau, 0), 1)))
    ax2.plot(ph, xs, color=COL['o'], lw=2)
    ax2.set_ylim(-0.2, 7.5); ax2.set_ylabel(T(lang, 'X 位移（mm，S 形，一针 3 mm）', 'X travel (mm, S-curve, 3 mm stitch)'), color=COL['o'])
    a1.set_title(T(lang, '(a) 模板只在实用窗口内移动（n = 1600 r/min 时 19.1 ms）', '(a) The clamp moves only inside the usable window (19.1 ms at 1600 r/min)'), fontsize=11, loc='left')
    # (b)
    s = np.linspace(0.5, 8, 200)
    def ncap(s, a): return np.minimum(C.N_HEAD, Wu / (6 * np.sqrt(C.C_S * s / 1000 / a)))
    a2.plot(s, ncap(s, C.AMAX['X']), color=COL['o'], lw=2, label=T(lang, '沿 X（a = 50 m/s²）', 'along X (a = 50 m/s²)'))
    a2.plot(s, ncap(s, C.AMAX['Y']), color=COL['g'], lw=2, label=T(lang, '沿 Y（a = 40 m/s²）', 'along Y (a = 40 m/s²)'))
    n45 = np.minimum(C.N_HEAD, Wu / (6 * np.sqrt(C.C_S * s / math.sqrt(2) / 1000 / C.AMAX['Y'])))
    a2.plot(s, n45, color=COL['p'], lw=1.6, ls='--', label=T(lang, '45° 斜向（受 Y 限制）', '45° diagonal (Y-limited)'))
    n3 = float(ncap(np.array([3.0]), C.AMAX['X'])[0])
    a2.plot([3], [n3], 'o', color=COL['o']); a2.annotate('%.0f r/min' % n3, (3, n3), (3.6, n3 + 280), fontsize=9.5, arrowprops=dict(arrowstyle='-', color=COL['mute']))
    a2.axhline(C.N_HEAD, color=COL['mute'], lw=1, ls=':')
    a2.text(5.2, C.N_HEAD + 40, T(lang, '机头限速 2500', 'head limit 2500'), color=COL['mute'], fontsize=9)
    a2.set_xlim(0.5, 8); a2.set_ylim(600, 2700)
    a2.set_xlabel(T(lang, '针距 s（mm）', 'stitch length s (mm)')); a2.set_ylabel(T(lang, '主轴转速上限（r/min）', 'spindle speed limit (r/min)'))
    a2.legend(fontsize=9, frameon=False, loc='upper right', bbox_to_anchor=(1, 0.93))
    a2.set_title(T(lang, '(b) 针距–转速上限（S 形，布厚 1.5 mm）', '(b) Stitch length vs speed limit (S-curve, 1.5 mm)'), fontsize=11, loc='left')
    fig.tight_layout(); save(fig, 'fig_c21_ps_budget.png', lang)

# ------------------------------------------------------------ 图 21-4 同步验证记录
def servo_sim(n_rpm, steps, Td, predict, wn, zeta, ka):
    """X 轴跟随仿真（示意）：参考位置 = 电子凸轮按（预测）角查表，经总延迟 T_d 到达驱动；
    驱动为二阶位置跟随，带速度前馈（100%）与加速度前馈（ka）。"""
    e, l, W = C.window(1.5); Wu = W - C.MARGIN
    s0 = l + C.MARGIN / 2
    w = n_rpm * 6.0      # °/s
    dt = 2e-5
    total = (len(steps) + 0.6) * 360 / w
    def cam(phi_deg):
        pos = 0.0
        for j, s in enumerate(steps):
            pos += s * C.s_pos((phi_deg - (s0 + 360 * j)) / Wu)
        return pos
    def ref(t):
        return cam(w * (t - Td) + (w * Td if predict else 0.0))
    h = 2e-5
    x = v = 0.0
    out_phi, out_cmd, out_x, out_err = [], [], [], []
    for k in range(int(total / dt)):
        t = k * dt
        r0, rp, rm = ref(t), ref(t + h), ref(t - h)
        vff = (rp - rm) / (2 * h) / 1000; aff = (rp - 2 * r0 + rm) / h ** 2 / 1000   # m/s, m/s²
        e_ = (r0 - x) / 1000
        acc = wn * wn * e_ + 2 * zeta * wn * (vff - v) + ka * aff
        v += acc * dt; x += v * dt * 1000
        if k % 10 == 0:
            out_phi.append(w * t); out_cmd.append(cam(w * t)); out_x.append(x); out_err.append(r0 - x)
    return np.array(out_phi), np.array(out_cmd), np.array(out_x), np.array(out_err)

def infab_disp(phi, x):
    e, l, W = C.window(1.5); res = []
    for k in range(0, int(phi[-1] // 360) + 1):
        m = (phi >= e + 360 * k) & (phi <= l + 360 * k)
        if m.sum() > 2: res.append(x[m].max() - x[m].min())
    return res

def fig_ps_sync(lang):
    e, l, W = C.window(1.5)
    steps = [3.0, 3.0, 3.0]
    n = 1600; Td = 1.5e-3
    res = {}
    res[False] = servo_sim(n, steps, Td, False, 2 * math.pi * 40, 0.8, 0.5)     # P0：初调
    res[True] = servo_sim(n, steps, Td, True, 2 * math.pi * 100, 0.9, 0.95)     # 调好后
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 5.6), sharex=True, gridspec_kw=dict(height_ratios=[1.6, 1]))
    for ax in (a1, a2):
        for k in range(0, 4):
            ax.axvspan(e + 360 * k, l + 360 * k, color=COL['r'], alpha=0.09, lw=0)
    ph, cmd, x0, err0 = res[False]; _, _, x1, err1 = res[True]
    a1.plot(ph, cmd, color=COL['mute'], lw=1.2, ls='--', label=T(lang, '电子凸轮理想位置 x(φ)', 'ideal cam position x(φ)'))
    a1.plot(ph, x0, color=COL['o'], lw=1.8, label=T(lang, '初调：40 Hz，前馈 50%，无延迟补偿', 'first tune: 40 Hz, 50 % acc. FF, no delay comp.'))
    a1.plot(ph, x1, color=COL['b'], lw=1.8, label=T(lang, '调好后：100 Hz，前馈 95%，按 φ + ω·T_d 查表', 'tuned: 100 Hz, 95 % acc. FF, table read at φ + ω·T_d'))
    a1.set_ylabel(T(lang, 'X 位置（mm）', 'X position (mm)')); a1.set_ylim(-0.3, 9.8)
    a1.legend(fontsize=9, frameon=False, loc='upper left')
    d0 = infab_disp(ph, x0); d1 = infab_disp(ph, x1)
    a1.text(e + 360 + 6, 8.2, T(lang, '红底：针在布中\n初调：布中位移 %.3f mm\n调好后：%.4f mm' % (max(d0), max(d1)),
                                 'red: needle in fabric\nfirst tune: %.3f mm moved\ntuned: %.4f mm' % (max(d0), max(d1))), fontsize=9, color=COL['ink'], va='top')
    a2.plot(ph, err0, color=COL['o'], lw=1.4)
    a2.plot(ph, err1, color=COL['b'], lw=1.4)
    a2.axhline(0.05, color=COL['g'], lw=1, ls='--'); a2.axhline(-0.05, color=COL['g'], lw=1, ls='--')
    a2.text(6, 0.058, T(lang, '跟随误差判据 ±0.05 mm', 'following-error limit ±0.05 mm'), color=COL['g'], fontsize=9)
    a2.set_ylim(-0.45, 0.45); a2.set_ylabel(T(lang, '跟随误差（mm）', 'following error (mm)'))
    a2.set_xlabel(T(lang, '主轴转角 φ（°，连续三针）', 'spindle angle φ (°, three stitches)'))
    a2.set_xlim(0, 1150); a2.set_xticks(range(0, 1081, 90))
    fig.suptitle(T(lang, '同步验证记录（仿真示意）：n = 1600 r/min，连续 3 mm 针距，总延迟 T_d = 1.5 ms',
                   'Sync-verification record (simulated): n = 1600 r/min, 3 mm stitches, total delay T_d = 1.5 ms'), fontsize=10.5, x=0.01, ha='left')
    fig.tight_layout(); save(fig, 'fig_c21_ps_sync.png', lang)
    print('   sync: in-fabric disp no-comp', [round(v, 4) for v in d0], 'comp', [round(v, 5) for v in d1],
          'max |err| comp %.4f no-comp %.4f' % (abs(err1).max(), abs(err0).max()))

# ------------------------------------------------------------ 图 21-6 选针时序预算
def fig_fk_timing(lang):
    P = dict(C.FK); p = C.pitch(P); v = P['vmax']
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.4), gridspec_kw=dict(width_ratios=[1.05, 1]))
    # (a) 一枚针的时序（以机头位置为横轴，单位 mm，针位为 0）
    Tr, J, Tc = P['Tr'], P['J'], P['Tctrl']
    lead = v * (Tr + Tc / 2)
    y = dict(win=4.2, cmd=3.2, fire=2.2, act=1.2)
    a1.axvspan(-0.25 * p, 0.25 * p, ymin=0.02, ymax=0.98, color=COL['y'], alpha=0.13, lw=0)
    a1.axvspan(-0.1 * p, 0.1 * p, ymin=0.02, ymax=0.98, color=COL['g'], alpha=0.16, lw=0)
    a1.axvline(0, color=COL['ink'], lw=1)
    a1.text(0.06, 4.75, T(lang, '针位 x_i', 'needle x_i'), fontsize=9)
    a1.text(-0.25 * p + 0.05, 0.38, T(lang, '允许窗口 ±0.25p', 'window ±0.25p'), fontsize=8.5, color=COL['y'])
    a1.text(-0.1 * p + 0.04, 0.05, T(lang, '验收 ±0.1p', 'accept ±0.1p'), fontsize=8.5, color=COL['g'])
    a1.annotate('', xy=(0, y['cmd']), xytext=(-lead, y['cmd']), arrowprops=dict(arrowstyle='<->', color=COL['b']))
    a1.text(-1.7, y['cmd'] + 0.3, T(lang, '命令点 x_i − v(T_r + T_c/2) = −%.2f mm' % lead, 'command x_i − v(T_r + T_c/2) = −%.2f mm' % lead), fontsize=9, color=COL['b'])
    a1.add_patch(plt.Rectangle((-lead, y['fire'] - 0.18), v * Tc, 0.36, color=COL['p'], alpha=0.35, lw=0))
    a1.text(-lead, y['fire'] + 0.28, T(lang, '触发落在下一个控制周期：0 ~ v·T_c = %.2f mm' % (v * Tc), 'fires at the next control tick: 0 … v·T_c = %.2f mm' % (v * Tc)), fontsize=9, color=COL['p'])
    lo = -v * (Tc / 2 + J); hi = v * (Tc / 2 + J)
    a1.add_patch(plt.Rectangle((lo, y['act'] - 0.18), hi - lo, 0.36, color=COL['o'], alpha=0.45, lw=0))
    a1.text(lo - 0.3, y['act'] - 0.62, T(lang, '衔铁动作位置 ±%.2f mm = ±%.3f p' % (hi, hi / p), 'armature acts at ±%.2f mm = ±%.3f p' % (hi, hi / p)), fontsize=9, color=COL['o'])
    a1.annotate('', xy=(-lead + v * Tc / 2, y['act'] + 0.2), xytext=(-lead + v * Tc / 2, y['fire'] - 0.2), arrowprops=dict(arrowstyle='->', color=COL['mute']))
    a1.text(-lead + v * Tc / 2 - 0.05, (y['act'] + y['fire']) / 2 - 0.05, 'T_r = %.1f ± %.1f ms' % (Tr, J), fontsize=8.5, color=COL['mute'], ha='right')
    a1.set_xlim(-1.75, 1.6); a1.set_ylim(0, 5.1); a1.set_yticks([])
    a1.set_xlabel(T(lang, '机头位置相对针位（mm）', 'carriage position relative to needle (mm)'))
    a1.set_title(T(lang, '(a) 一枚针的时序预算（E5，v = 0.6 m/s，MCU 1 ms）', '(a) Timing budget of one needle (E5, v = 0.6 m/s, MCU 1 ms)'), fontsize=10.5, loc='left')
    # (b) 最坏误差 vs 速度
    vs = np.linspace(0.1, 2.4, 70)
    cfgs = [(dict(E=5, fpga=False, Tctrl=1.0), COL['o'], '-', T(lang, 'E5，MCU 1 ms', 'E5, MCU 1 ms')),
            (dict(E=5, fpga=False, Tctrl=0.25), COL['p'], '-', T(lang, 'E5，MCU 0.25 ms', 'E5, MCU 0.25 ms')),
            (dict(E=5, fpga=True), COL['b'], '-', T(lang, 'E5，FPGA', 'E5, FPGA')),
            (dict(E=7, fpga=False, Tctrl=1.0), COL['o'], '--', T(lang, 'E7，MCU 1 ms', 'E7, MCU 1 ms')),
            (dict(E=7, fpga=True), COL['b'], '--', T(lang, 'E7，FPGA', 'E7, FPGA'))]
    for cfg, col, ls, lab in cfgs:
        ys = [C.fk_eval(dict(P, vmax=vv, **cfg))['worst_p'] for vv in vs]
        a2.plot(vs, ys, color=col, ls=ls, lw=1.8, label=lab)
    a2.axhline(0.1, color=COL['g'], lw=1.2); a2.axhline(0.25, color=COL['y'], lw=1.2)
    a2.text(2.42, 0.1, T(lang, ' 验收\n 0.1p', ' accept\n 0.1p'), color=COL['g'], fontsize=9, va='center')
    a2.text(2.42, 0.25, T(lang, ' 错选\n 0.25p', ' mis-select\n 0.25p'), color=COL['y'], fontsize=9, va='center')
    for cfg, lab in ((dict(E=5, fpga=False, Tctrl=1.0), '0.64'), (dict(E=5, fpga=True), '1.66')):
        vm = C.fk_vmax(dict(P, **cfg)); a2.plot([vm], [0.1], 'o', color=COL['ink'], ms=5)
        a2.annotate('%.3f m/s' % vm, (vm, 0.1), (vm + 0.05, 0.035), fontsize=9)
    a2.set_xlim(0, 2.4); a2.set_ylim(0, 0.4)
    a2.set_xlabel(T(lang, '机头最高速度 v（m/s）', 'carriage top speed v (m/s)')); a2.set_ylabel(T(lang, '一行中最坏选针误差（针距 p）', 'worst selection error in a row (pitches)'))
    a2.legend(fontsize=8.5, frameon=False, loc='upper left')
    a2.set_title(T(lang, '(b) 最坏误差与机头速度（T_r = 1.5 ± 0.3 ms，实时提前量）', '(b) Worst error vs speed (T_r = 1.5 ± 0.3 ms, real-time lead)'), fontsize=10.5, loc='left')
    fig.tight_layout(); save(fig, 'fig_c21_fk_timing.png', lang)

# ------------------------------------------------------------ 图 21-8 选针时序标定：两速扫描提前量
def fig_fk_calib(lang):
    P = dict(C.FK); p = C.pitch(P)
    Tr_nom = 1.2       # 固件里的初值（ms），真值 1.5
    random.seed(7)
    fig, ax = plt.subplots(figsize=(9.6, 4.0))
    centers = []
    for v, col in ((0.3, COL['g']), (0.9, COL['b'])):
        ds = np.arange(-1.6, 1.81, 0.02)
        rate = []
        for d in ds:
            # 固件按 Tr_nom 算提前量，再加偏置 d（mm）；用真实模型测“选中率”
            Q = dict(P, vmax=v, mode='fixed', Lf=v * (Tr_nom + P['Tctrl'] / 2) + d, c=80)
            ok = 0; tot = 0
            for r in range(30):
                for i in range(P['N']):
                    e, u = C.needle_err(Q, i, random.random(), random.uniform(-1, 1))
                    tot += 1; ok += abs(e) <= 0.25 * p
            rate.append(ok / tot * 100)
        rate = np.array(rate)
        good = ds[rate >= 99.9]
        lo, hi = good.min(), good.max(); c = (lo + hi) / 2; centers.append((v, c))
        ax.plot(ds, rate, color=col, lw=2, label=T(lang, 'v = %.1f m/s：通过带 %.2f ~ %.2f mm，中点 %.2f' % (v, lo, hi, c), 'v = %.1f m/s: pass band %.2f … %.2f mm, centre %.2f' % (v, lo, hi, c)))
        ax.axvline(c, color=col, lw=1, ls=':')
    slope = (centers[1][1] - centers[0][1]) / (centers[1][0] - centers[0][0])
    ax.set_xlabel(T(lang, '提前量偏置 δ（mm，加在固件按 T_r = 1.2 ms 算出的提前量上）', 'lead offset δ (mm, added to the lead computed with T_r = 1.2 ms)'))
    ax.set_ylabel(T(lang, '选针正确率（%，30 行 × 60 针）', 'correct selections (%, 30 rows × 60 needles)'))
    ax.set_ylim(-3, 105); ax.set_xlim(-1.6, 1.8)
    ax.legend(fontsize=9, frameon=True, facecolor=BG, edgecolor='none', framealpha=0.95, loc='lower center')
    ax.text(-0.4, 50, T(lang, '中点随速度移动：\nΔδ/Δv = %.2f ms\n→ T_r 应改为 1.2 + %.2f = %.2f ms' % (slope, slope, 1.2 + slope),
                        'centre shifts with speed:\nΔδ/Δv = %.2f ms\n→ set T_r = 1.2 + %.2f = %.2f ms' % (slope, slope, 1.2 + slope)), fontsize=9.5)
    ax.set_title(T(lang, '选针时序标定（仿真示意）：两种速度下扫描提前量，取通过带中点', 'Selection-timing calibration (simulated): sweep the lead at two speeds, take the centre of the pass band'), fontsize=10.5, loc='left')
    fig.tight_layout(); save(fig, 'fig_c21_fk_calib.png', lang)
    print('   calib centers', centers, 'slope ms', slope)

if __name__ == '__main__':
    which = sys.argv[1:] or ['budget', 'sync', 'timing', 'calib']
    for lang in ('zh', 'en'):
        if 'budget' in which: fig_ps_budget(lang)
        if 'sync' in which: fig_ps_sync(lang)
        if 'timing' in which: fig_fk_timing(lang)
        if 'calib' in which: fig_fk_calib(lang)
