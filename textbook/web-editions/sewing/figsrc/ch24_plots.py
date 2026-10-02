# -*- coding: utf-8 -*-
"""第 24 章数据图（中英两版）：fig_c24_cpk、fig_c24_select。运行：python3 figsrc/ch24_plots.py"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ch24_model import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG, INK, MUTED, RULE = '#faf9f5', '#1b2430', '#5a6570', '#d8dde1'
BLUE, ORANGE, RED, GREEN = '#2a5fb8', '#d9622b', '#c0392b', '#1e8449'
plt.rcParams.update({'font.family': ['Noto Sans CJK SC', 'DejaVu Sans'], 'font.size': 11,
                     'axes.edgecolor': MUTED, 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
                     'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': BG,
                     'axes.facecolor': BG, 'savefig.facecolor': BG, 'axes.unicode_minus': False})

T = {
 'zh': dict(
  cpk_t='针孔宽度：工序能力与控制图（Nm 90，算例，示意值）',
  hist='前 25 组 × 5 支的针孔宽度分布', width='针孔宽度（mm）', count='支数',
  xbar='均值控制图（每组 5 支；第 26 组起注入 +1σ 漂移）', grp='子组序号', mean='子组均值（mm）',
  lsl='LSL', usl='USL', cl='中心线', ucl='UCL', lcl='LCL', alarm='第 {} 组报警', drift='漂移开始',
  capk='Cp = {:.2f}\nCpk = {:.2f}\n超差约 {:.1f} ppm',
  sel_t='旋梭选配：2000 套的直径间隙分布（算例，示意值）',
  a='(a) 完全互换，两零件 σ = 5 μm', b='(b) 完全互换，两零件 σ = 2.6 μm', c='(c) 分 3 组选配，σ = 5 μm',
  d='(d) 分 3 组：梭道均值偏 +4 μm 时各组件数', gap='直径间隙（μm）', sets='套数',
  res='合格 {:.1f}%\n每套 {:.1f} 元', res2='合格 {:.1f}%，剩余 {:.1f}%\n每套 {:.1f} 元',
  g=['第 1 组（小）', '第 2 组', '第 3 组（大）'], D='旋梭体（梭道）', dd='梭床（导轨）', nparts='件数',
  shifted='深色：梭床未跟随，剩余 {:.0f}%', ok='浅色：梭床目标也 +4 μm，剩余 {:.1f}%', spec='允许 10–30 μm'),
 'en': dict(
  cpk_t='Eye width: process capability and control chart (Nm 90, worked example, illustrative)',
  hist='Eye width, first 25 subgroups × 5 needles', width='Eye width (mm)', count='Needles',
  xbar='Chart of subgroup means (5 needles each; +1σ drift from subgroup 26)', grp='Subgroup', mean='Subgroup mean (mm)',
  lsl='LSL', usl='USL', cl='Centre line', ucl='UCL', lcl='LCL', alarm='alarm at subgroup {}', drift='drift starts',
  capk='Cp = {:.2f}\nCpk = {:.2f}\nout of spec ≈ {:.1f} ppm',
  sel_t='Selective assembly of rotary hooks: diametral clearance of 2000 sets (worked example, illustrative)',
  a='(a) Full interchangeability, σ = 5 μm', b='(b) Full interchangeability, σ = 2.6 μm', c='(c) 3-group selective fit, σ = 5 μm',
  d='(d) 3 groups: part counts when race mean shifts +4 μm', gap='Diametral clearance (μm)', sets='Sets',
  res='in spec {:.1f}%\n{:.1f} yuan per set', res2='in spec {:.1f}%, left over {:.1f}%\n{:.1f} yuan per set',
  g=['Group 1 (small)', 'Group 2', 'Group 3 (large)'], D='Hook body (race)', dd='Basket (rib)', nparts='Parts',
  shifted='dark: basket not re-targeted, {:.0f}% left over', ok='light: basket target also +4 μm, {:.1f}% left over',
  spec='allowed 10–30 μm'),
}


def fig_cpk(lang):
    L = T[lang]
    S = spc(**dict(STD2, drift=1.0))
    fig = plt.figure(figsize=(13.3, 5.4), dpi=150)
    fig.suptitle(L['cpk_t'], x=0.012, ha='left', fontsize=14, fontweight='bold', color=INK)
    ax = fig.add_axes([0.06, 0.13, 0.28, 0.70])
    vals = [v for s in S['raw'][:NBASE] for v in s]
    ax.hist(vals, bins=[0.338 + 0.002 * i for i in range(23)], color=BLUE, edgecolor=BG, linewidth=1.5)
    for x, lab in ((LSL, L['lsl']), (USL, L['usl'])):
        ax.axvline(x, color=RED, lw=1.6, ls='--')
        ax.text(x, ax.get_ylim()[1] * 0.97, lab, color=RED, ha='center', va='top', fontsize=10,
                bbox=dict(fc=BG, ec='none', pad=1))
    ax.text(0.05, 0.62, L['capk'].format(S['cp'], S['cpk'], S['ppm']), transform=ax.transAxes, fontsize=10.5, color=INK, bbox=dict(fc=BG, ec=RULE, pad=4))
    ax.set_xlabel(L['width']); ax.set_ylabel(L['count']); ax.set_title(L['hist'], fontsize=11.5, loc='left', color=INK)
    ax.set_xlim(0.336, 0.384)
    ax2 = fig.add_axes([0.42, 0.13, 0.56, 0.70])
    g = list(range(1, NTOT + 1))
    ax2.plot(g, S['xb'], color=INK, lw=1.6, marker='o', ms=5, mfc=BLUE, mec=BG, zorder=3)
    for y, lab, col, ls in ((S['ucl'], L['ucl'], RED, '--'), (S['lcl'], L['lcl'], RED, '--'), (S['xbb'], L['cl'], MUTED, '-')):
        ax2.axhline(y, color=col, lw=1.3, ls=ls)
        ax2.text(NTOT + 1.0, y + 0.0002, '%s %.4f' % (lab, y), va='bottom', fontsize=9.5, color=col)
    ax2.axvspan(NBASE + 0.5, NTOT + 0.5, color=ORANGE, alpha=0.08)
    ax2.text(NBASE + 1, S['lcl'] - 0.0016, L['drift'] + ' →', color=ORANGE, fontsize=10)
    if S['alarm']:
        a = S['alarm']
        ax2.plot([a], [S['xb'][a - 1]], 'o', ms=13, mfc='none', mec=RED, mew=2)
        ax2.annotate(L['alarm'].format(a), (a, S['xb'][a - 1]), (a + 3, S['ucl'] + 0.0022), color=RED, fontsize=10.5,
                     arrowprops=dict(arrowstyle='->', color=RED))
    ax2.set_xlim(0, NTOT + 9); ax2.set_ylim(S['lcl'] - 0.0025, S['ucl'] + 0.0035)
    ax2.set_xlabel(L['grp']); ax2.set_ylabel(L['mean']); ax2.set_title(L['xbar'], fontsize=11.5, loc='left', color=INK)
    out = os.path.join(ROOT, 'img', ('en/' if lang == 'en' else '') + 'fig_c24_cpk.png')
    fig.savefig(out); plt.close(fig); print(out)


def fig_select(lang):
    L = T[lang]
    fig, axs = plt.subplots(2, 2, figsize=(13.3, 8.6), dpi=150)
    fig.suptitle(L['sel_t'], x=0.012, ha='left', fontsize=14, fontweight='bold', color=INK)
    fig.subplots_adjust(left=0.065, right=0.985, top=0.89, bottom=0.08, hspace=0.42, wspace=0.18)
    cases = [(axs[0][0], L['a'], dict(STD)), (axs[0][1], L['b'], dict(STD, sD=2.6, sd=2.6)), (axs[1][0], L['c'], dict(STD, k=3))]
    bins = [i for i in range(-6, 47, 2)]
    for ax, title, p in cases:
        R = simulate(keep=True, **p)
        ok = [c for c in R['cs'] if CMIN <= c <= CMAX]
        bad = [c for c in R['cs'] if not (CMIN <= c <= CMAX)]
        ax.axvspan(CMIN, CMAX, color=GREEN, alpha=0.08)
        ax.hist([ok, bad], bins=bins, stacked=True, color=[BLUE, RED], edgecolor=BG, linewidth=1.2)
        ax.set_title(title, fontsize=11.5, loc='left', color=INK)
        ax.set_xlabel(L['gap']); ax.set_ylabel(L['sets']); ax.set_xlim(-6, 46); ax.set_ylim(0, 640)
        txt = L['res'].format(R['pass_rate'] * 100, R['cost']) if p['k'] == 1 else \
            L['res2'].format(R['pass_rate'] * 100, R['left_rate'] * 100, R['cost'])
        ax.text(0.98, 0.95, txt, transform=ax.transAxes, ha='right', va='top', fontsize=10.5, color=INK)
        ax.text(20, 610, L['spec'], color=GREEN, ha='center', fontsize=9.5)
    ax = axs[1][1]
    R1 = simulate(**dict(STD, k=3, muD=4.0))
    R2 = simulate(**dict(STD, k=3, muD=4.0, mud=4.0))
    import numpy as np
    x = np.arange(3)
    w = 0.2
    ax.bar(x - 1.5 * w, [a for a, b in R1['per']], w, color=BLUE, label=L['D'])
    ax.bar(x - 0.5 * w, [b for a, b in R1['per']], w, color=ORANGE, label=L['dd'])
    ax.bar(x + 0.5 * w + 0.04, [a for a, b in R2['per']], w, color=BLUE, alpha=0.45)
    ax.bar(x + 1.5 * w + 0.04, [b for a, b in R2['per']], w, color=ORANGE, alpha=0.45)
    ax.set_xticks(x); ax.set_xticklabels(L['g'])
    ax.set_ylabel(L['nparts']); ax.set_title(L['d'], fontsize=11.5, loc='left', color=INK)
    ax.legend(frameon=False, loc='upper left', fontsize=10)
    ax.set_ylim(0, 1750)
    ax.text(0.98, 0.95, L['shifted'].format(R1['left_rate'] * 100) + '\n' + L['ok'].format(R2['left_rate'] * 100),
            transform=ax.transAxes, ha='right', va='top', fontsize=10, color=INK)
    out = os.path.join(ROOT, 'img', ('en/' if lang == 'en' else '') + 'fig_c24_select.png')
    fig.savefig(out); plt.close(fig); print(out)


if __name__ == '__main__':
    os.makedirs(os.path.join(ROOT, 'img', 'en'), exist_ok=True)
    for lang in ('zh', 'en'):
        fig_cpk(lang)
        fig_select(lang)
