# -*- coding: utf-8 -*-
"""Chapter 20 data figures (zh + en). Run from /home/claude/sm: python3 figsrc/ch20_plots.py"""
import math, statistics as st, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from ch20_model import *
from ch20_ol import opt
ROOT = '/home/claude/sm'
BG = '#faf9f5'; INK = '#1b2430'; MU = '#5a6570'; BL = '#2a5fb8'; OR = '#d9622b'; GR = '#1e8449'; RD = '#c0392b'; YE = '#b7791f'; TE = '#0f6e74'
plt.rcParams.update({'font.family': ['Noto Sans CJK SC', 'DejaVu Sans'], 'font.size': 12, 'axes.edgecolor': '#9aa4ae',
                     'axes.labelcolor': INK, 'xtick.color': MU, 'ytick.color': MU, 'figure.facecolor': BG, 'axes.facecolor': BG,
                     'savefig.facecolor': BG, 'axes.spines.top': False, 'axes.spines.right': False})
def out(fig, name, lang):
    p = f'{ROOT}/img/fig_c20_{name}.png' if lang == 'zh' else f'{ROOT}/img/en/fig_c20_{name}.png'
    fig.savefig(p, dpi=150); plt.close(fig); print('ok', p)
def head(fig, t, s):
    fig.text(0.03, 0.965, t, fontsize=18, fontweight='bold', color=INK, va='top')
    fig.text(0.03, 0.915, s, fontsize=12, color=MU, va='top')
lab = lambda a: f'{a%360:.0f}°'
# ------------------------------------------------------------------ events
def fig_events(lang):
    zh = lang == 'zh'
    M = monte(400, n=300, seed=3)
    tr = Trace(300)
    fig = plt.figure(figsize=(13.4, 7.4))
    head(fig, '剪线事件表与实际动作（平缝机原型，剪线 300 r/min）' if zh else 'Trim event table vs. actual motion (lockstitch prototype, trim at 300 r/min)',
         '算例：电磁铁 24 V ±10%、线圈 8–9.5 Ω（冷/热）、主轴转速波动 ±2%，400 次随机；窗口取自第 14 章（示意值）' if zh else
         'Worked example: solenoid 24 V ±10%, coil 8–9.5 Ω (cold/hot), spindle speed ±2%, 400 random runs; windows from Chapter 14 (illustrative)')
    ax = fig.add_axes([0.13, 0.1, 0.62, 0.74]); ax2 = fig.add_axes([0.79, 0.1, 0.18, 0.74])
    rows = {'knife': 5, 'cut': 4, 'rel': 3, 'spd': 1.6}
    names = ['TRIM 剪线：发令', 'TRIM 动刀进刀 / 剪断', 'TREL 松线', '主轴转速'] if zh else ['TRIM command', 'TRIM knife in / cut', 'TREL release', 'spindle speed']
    ax.set_xlim(260, 445); ax.set_ylim(0.6, 5.9); ax.set_yticks([5, 4, 3, 1.6]); ax.set_yticklabels(names)
    xt = list(range(270, 446, 15)); ax.set_xticks(xt); ax.set_xticklabels([lab(x) for x in xt])
    ax.grid(axis='x', color='#e3e7ea'); ax.tick_params(axis='y', length=0)
    ev = STD_EVENTS
    # command bars
    ax.add_patch(Rectangle((ev['trim_on'], 4.85), ev['trim_off']-ev['trim_on'], 0.3, color=OR, alpha=.85))
    ax.text(ev['trim_on'], 5.25, ('通电 %d° → 断电 %s（下一转）' if zh else 'on %d° → off %s (next rev)') % (ev['trim_on'], lab(ev['trim_off'])), fontsize=11, color=OR)
    # knife window & entries
    ax.add_patch(Rectangle((KNIFE[0], 3.7), KNIFE[1]-KNIFE[0], 0.6, color=GR, alpha=.15))
    ax.add_patch(Rectangle((CUT[0], 3.7), CUT[1]-CUT[0], 0.6, color=GR, alpha=.15))
    e = [m['entry'] for m in M]; c = [m['cut'] for m in M]
    ax.add_patch(Rectangle((min(e), 3.85), max(e)-min(e), 0.3, color=RD, alpha=.8))
    ax.add_patch(Rectangle((min(c), 3.85), max(c)-min(c)+0.4, 0.3, color=YE, alpha=.9))
    ax.text(KNIFE[0], 4.36, ('进刀窗口 300°–330°；实际 %.0f°–%.0f°' if zh else 'entry window 300°–330°; actual %.0f°–%.0f°') % (min(e), max(e)), fontsize=10.5, color=RD, va='bottom')
    ax.text(CUT[1], 4.36, ('剪断窗口 45°–65°；实际 %.0f°' if zh else 'cut 45°–65°; actual %.0f°') % (st.mean(c)-360), fontsize=10.5, color=YE, va='bottom', ha='right')
    # release
    ax.add_patch(Rectangle((ev['trel_on'], 2.95), TARGET-ev['trel_on'], 0.1, color=TE, alpha=.6))
    ro = [m['ropen'] for m in M]
    ax.add_patch(Rectangle((max(ro), 2.75), TARGET+2-max(ro), 0.2, color=TE, alpha=.25))
    ax.add_patch(Rectangle((min(ro), 2.75), max(ro)-min(ro), 0.2, color=TE, alpha=.8))
    ax.plot([REL[0], REL[1]], [3.25, 3.25], color=INK, lw=1.5); ax.text(REL[0], 3.32, '需要：335°–55°' if zh else 'needed: 335°–55°', fontsize=10)
    ax.text(ev['trel_on'], 2.55, ('发令 %d°，%.0f°–%.0f° 打开；保持到停稳' if zh else 'command %d°, open at %.0f°–%.0f°; held until stopped') % (ev['trel_on'], min(ro), max(ro)), fontsize=10.5, color=TE, va='top')
    # speed
    ts = [i*1e-4 for i in range(0, int(tr.tstop*1e4)+300)]
    xs = [tr.ang(t) for t in ts]; ys = [300 if t <= tr.tA else tr.res[min(len(tr.res)-1, int((t-tr.tA)/1e-4))][2] for t in ts]
    ax.plot(xs, [0.9+1.2*y/300 for y in ys], color=BL, lw=2)
    ax.axvline(ENGAGE, color=BL, ls=':', lw=1); ax.text(ENGAGE+1, 2.15, '切入位置环 25°' if zh else 'position loop 25°', color=BL, fontsize=10)
    ax.axvline(NEEDLE_IN-5, color=RD, ls='--', lw=1)
    ax.plot([TARGET], [0.9], 'o', color=BL, ms=9); ax.text(TARGET-2, 0.75, ('目标上针位 70°，停稳 %.0f ms' if zh else 'target needle-up 70°, settled %.0f ms') % ((tr.tstop-tr.tA)*1e3) , color=BL, fontsize=10.5, ha='right')
    ax.text(270, 2.2, '300 r/min', color=BL, fontsize=10); ax.text(270, 0.95, '0', color=BL, fontsize=10)
    for x, t in ((206, ''), (341, '线环脱出' if zh else 'loop leaves'), (415, '挑线杆最高' if zh else 'take-up top')):
        if x > 260: ax.text(x, 5.75, t, fontsize=10, color=MU, ha='center'); ax.plot([x, x], [5.55, 5.7], color=MU)
    # post-stop panel
    ax2.set_xlim(0, 160); ax2.set_ylim(0.6, 5.9); ax2.set_yticks([4.5, 3.0]); ax2.set_yticklabels(['WIPE', 'PFL']); ax2.tick_params(axis='y', length=0)
    ax2.add_patch(Rectangle((ev['wipe_on'], 4.35), ev['wipe_len'], 0.3, color=MU)); ax2.add_patch(Rectangle((ev['wipe_on']+ev['wipe_len'], 4.35), WIPE_RET*1e3, 0.3, color=MU, alpha=.35))
    ax2.add_patch(Rectangle((ev['pfl_on'], 2.85), 80, 0.3, color=GR))
    ax2.text(0, 4.8, '拨线 40 ms + 复位 15 ms' if zh else 'wipe 40 ms + return 15 ms', fontsize=10)
    ax2.text(ev['pfl_on'], 3.3, '抬压脚 ≥ 55 ms' if zh else 'lift foot ≥ 55 ms', fontsize=10, ha='left')
    ax2.set_xlabel('停稳后（ms）' if zh else 'after "stopped" (ms)'); ax2.grid(axis='x', color='#e3e7ea')
    out(fig, 'events', lang)
# ------------------------------------------------------------------ Z calibration
Rr, Ll = 15.5, 55.0; lam = Rr/Ll
X = lambda f: Rr*(1-math.cos(f*D))-Ll*(1-math.sqrt(1-(lam*math.sin(f*D))**2))
def fig_zcal(lang):
    zh = lang == 'zh'
    fig = plt.figure(figsize=(13.4, 5.6))
    head(fig, '上止点怎样找：对称两点法' if zh else 'Finding top dead centre: the symmetric two-point method',
         '算例：第 3、8 章的针杆曲柄滑块（r = 15.5 mm，l = 55 mm），百分表分辨率 0.01 mm' if zh else 'Worked example: the needle-bar slider-crank of Chapters 3 and 8 (r = 15.5 mm, l = 55 mm), dial gauge resolution 0.01 mm')
    a1 = fig.add_axes([0.07, 0.13, 0.52, 0.66]); a2 = fig.add_axes([0.68, 0.13, 0.29, 0.66])
    f = [i*0.5 for i in range(-120, 841)]
    a1.plot(f, [X(x) for x in f], color=INK, lw=2); a1.invert_yaxis()
    h = 12.0
    # find symmetric angles
    lo = next(x for x in [i*0.01 for i in range(0, 18000)] if X(x) >= h); hi = 360-lo
    for x in (lo, hi): a1.plot([x], [h], 'o', color=OR, ms=9)
    a1.axhline(h, color=OR, ls='--', lw=1)
    a1.annotate('', xy=(hi-3, h+3), xytext=(lo+3, h+3), arrowprops=dict(arrowstyle='<->', color=OR))
    a1.text(180, h+7.5, ('r₁ = %.1f°，r₂ = %.1f°\n下止点 = (r₁+r₂)/2' if zh else 'r₁ = %.1f°, r₂ = %.1f°\nBDC = (r₁+r₂)/2') % (lo, hi), ha='center', va='center', color=OR, fontsize=11)
    a1.set_xlim(-60, 420); a1.set_xticks(range(-45, 421, 45)); a1.set_xticklabels([f'{x%360}°' for x in range(-45, 421, 45)])
    a1.set_ylabel('针杆离上止点（mm）' if zh else 'needle bar below TDC (mm)'); a1.set_xlabel('主轴转角' if zh else 'spindle angle')
    slope = (X(lo+0.01)-X(lo))/0.01
    a1.text(-55, 27, ('此处斜率 %.2f mm/°\n0.01 mm ↔ %.2f°' if zh else 'slope here %.2f mm/°\n0.01 mm ↔ %.2f°') % (slope, 0.01/slope), color=OR, fontsize=10.5, ha='left')
    # zoom TDC
    g = [i*0.05 for i in range(-80, 81)]
    a2.plot(g, [X(x)*1000 for x in g], color=INK, lw=2); a2.invert_yaxis()
    ftd = math.sqrt(2*0.01/(Rr*(1+lam)))/D
    a2.axhspan(0, 10, color=RD, alpha=.12); a2.axvspan(-ftd, ftd, color=RD, alpha=.08)
    a2.text(0, 13.5, ('百分表读不出变化：±%.1f°' if zh else 'gauge shows no change: ±%.1f°') % ftd, ha='center', color=RD, fontsize=11)
    a2.set_xlabel('上止点附近的转角（°）' if zh else 'angle near TDC (°)'); a2.set_ylabel('μm')
    a2.set_ylim(25, -1)
    out(fig, 'zcal', lang)
    return lo, hi, slope, ftd
# ------------------------------------------------------------------ acceptance
def fig_accept(lang):
    zh = lang == 'zh'
    M = monte(1000, n=300, calib=0.1, seed=7)
    MB = monte(1000, n=300, calib=0.7, seed=7)
    cases = [(300, STD_EVENTS, 24.0, 0.1), (300, STD_EVENTS, 20.0, 0.1), (700, STD_EVENTS, 24.0, 0.1), (700, dict(STD_EVENTS, trim_on=285.0, trel_on=290.0), 24.0, 0.1), (300, STD_EVENTS, 24.0, 0.7)]
    rates = []
    for (n, ev, V, cal) in cases:
        R = monte(300, ev=ev, n=n, calib=cal, seed=11, Vmu=V); rates.append(100*sum(m['all'] for m in R)/len(R))
    fig = plt.figure(figsize=(13.4, 5.8))
    head(fig, '验收测试的一组算例结果（软件在环，同一模型）' if zh else 'A set of worked acceptance results (software-in-the-loop, same model)',
         '左、中：标准事件表、剪线 300 r/min、标定残差 0.1°，1000 次；右：五种工况各 300 次的剪线周期合格率（剪断、松线、停针都合格）' if zh else
         'Left, centre: standard event table, trim at 300 r/min, calibration residual 0.1°, 1000 runs; right: trim-cycle pass rate (cut, release and stop all good), 300 runs per case')
    a1 = fig.add_axes([0.06, 0.14, 0.27, 0.64]); a2 = fig.add_axes([0.39, 0.14, 0.25, 0.64]); a3 = fig.add_axes([0.73, 0.14, 0.25, 0.64])
    e = [m['entry'] for m in M]
    a1.hist(e, bins=30, color=RD, alpha=.8); a1.axvspan(*KNIFE, color=GR, alpha=.12); a1.set_xlim(295, 335)
    a1.set_xlabel('动刀进刀角（°）' if zh else 'knife entry angle (°)'); a1.set_ylabel('次数' if zh else 'count')
    a1.text(301, a1.get_ylim()[1]*0.9, '窗口 300°–330°' if zh else 'window 300°–330°', color=GR)
    s = [m['stop']-TARGET for m in M]; sb = [m['stop']-TARGET for m in MB]
    a2.hist(s, bins=20, color=BL, alpha=.85, label='残差 0.1°' if zh else 'residual 0.1°'); a2.hist(sb, bins=20, color=OR, alpha=.6, label='残差 0.7°' if zh else 'residual 0.7°')
    a2.axvspan(-1, 1, color=GR, alpha=.08); a2.axvline(-1, color=GR, ls='--'); a2.set_xlim(-1.6, 0.6)
    a2.set_xlabel('停针误差（°，停稳标志时）' if zh else 'stop error (°, at "stopped" flag)'); a2.legend(frameon=False, fontsize=10, loc='upper right')
    labs = (['300 r/min\n标准', '300 r/min\n20 V', '700 r/min\n标准表', '700 r/min\n重编表', '300 r/min\n残差 0.7°'] if zh else
            ['300 r/min\nstandard', '300 r/min\n20 V', '700 r/min\nstd table', '700 r/min\nretuned', '300 r/min\nresidual 0.7°'])
    col = [GR if r >= 99.5 else RD for r in rates]
    a3.bar(range(5), rates, color=col); a3.set_xticks(range(5)); a3.set_xticklabels(labs, fontsize=9.5); a3.set_ylim(0, 108)
    for i, r in enumerate(rates): a3.text(i, r+1.5, f'{r:.1f}%', ha='center', fontsize=10)
    a3.axhline(99.5, color=GR, ls='--', lw=1); a3.set_ylabel('剪线成功率（%）' if zh else 'trim success (%)')
    out(fig, 'accept', lang)
    return dict(e=(min(e), max(e), st.mean(e)), s=(min(s), max(s), st.mean(s), st.pstdev(s)), sb=(min(sb), max(sb)), rates=rates,
                okb=sum(m['all'] for m in MB))
# ------------------------------------------------------------------ overlock tail
def fig_oltail(lang):
    zh = lang == 'zh'
    o = opt(1.25); s = 3.0; N1 = math.ceil(25/s); N2 = math.ceil(40/s)
    fig = plt.figure(figsize=(13.4, 5.6))
    head(fig, '包缝机原型的“布走即停”：要提前多少针开始减速' if zh else 'Overlock "stop when the fabric leaves": how many stitches early to start braking',
         '算例：主轴折算到电机 7.45×10⁻⁴ kg·m²（同步带 1:1.25），减速度取能力的 60%；针距 3 mm，传感器在针前 25 mm，链线 40 mm' if zh else
         'Worked example: inertia at the motor 7.45×10⁻⁴ kg·m² (1:1.25 timing belt), braking at 60% of capability; stitch 3 mm, sensor 25 mm ahead, chain 40 mm')
    a1 = fig.add_axes([0.07, 0.14, 0.42, 0.64]); a2 = fig.add_axes([0.57, 0.14, 0.40, 0.64])
    ns = list(range(1000, 7001, 250)); nb = [o['revs_dec']*(n/7000)**2 for n in ns]
    a1.plot(ns, nb, color=BL, lw=2.2); a1.set_xlabel('缝纫转速（r/min）' if zh else 'sewing speed (r/min)'); a1.set_ylabel('减速到停的针数 N$_b$' if zh else 'stitches to stop N$_b$')
    a1.axhline(N1+N2, color=OR, ls='--'); a1.text(1100, N1+N2+0.6, ('布离开传感器后共要缝 N₁ + N₂ = %d + %d = %d 针' if zh else 'after the fabric leaves: N₁ + N₂ = %d + %d = %d stitches') % (N1, N2, N1+N2), color=OR)
    a1.set_ylim(0, 26)
    # timeline at 7000: speed vs stitch after fabric leaves
    for n, c in ((7000, RD), (4000, BL)):
        Nb = o['revs_dec']*(n/7000)**2; start = N1+N2-Nb
        xs = [0, start] + [start+Nb*k/60 for k in range(1, 61)]; ys = [n, n] + [n*math.sqrt(max(0, 1-k/60)) for k in range(1, 61)]
        a2.plot(xs, ys, color=c, lw=2.2, label=f'{n} r/min: ' + (f'第 {start:.1f} 针开始减速' if zh else f'brake from stitch {start:.1f}'))
        xl = [0, N1+N2] + [N1+N2+Nb*k/60 for k in range(1, 61)]; a2.plot(xl, ys, color=c, lw=1.2, ls=':')
    a2.axvline(N1, color=MU, ls='--', lw=1); a2.text(N1+0.2, 7300, '布尾到针' if zh else 'fabric tail at needle', color=MU, fontsize=10)
    a2.axvline(N1+N2, color=OR, ls='--', lw=1); a2.text(N1+N2+0.2, 7300, '链线够长' if zh else 'chain long enough', color=OR, fontsize=10)
    a2.set_xlabel('布离开传感器后的针数' if zh else 'stitches after the fabric leaves the sensor'); a2.set_ylabel('r/min'); a2.set_ylim(0, 7900); a2.set_xlim(0, 40)
    a2.legend(frameon=False, fontsize=10, loc='upper right', bbox_to_anchor=(1.0, 0.9))
    a2.text(24, 2300, '点线：到点才减速，\n链线多出 N$_b$ 针' if zh else 'dotted: braking only at the end\nadds N$_b$ stitches of chain', fontsize=10, color=MU)
    out(fig, 'oltail', lang)
    return N1, N2, o
if __name__ == '__main__':
    for lang in ('zh', 'en'):
        fig_events(lang); z = fig_zcal(lang); A = fig_accept(lang); O = fig_oltail(lang)
    print('zcal', z); print('accept', A); print('ol', O)
