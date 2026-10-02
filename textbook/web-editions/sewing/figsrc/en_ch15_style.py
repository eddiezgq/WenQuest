# Shared matplotlib style for the English chapter-15 data charts (w_*.png).
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BG = '#faf9f5'
BLUE = '#2a78d6'; ORANGE = '#eb6834'; GREEN = '#1baf7a'; GREY = '#c3c2b7'
INK = '#0b0b0b'; MUTED = '#52514e'; GRID = '#e3e3e1'; AXIS = '#c3c2b7'
WIN = '#e9f1fb'; STILL = '#ebebe9'; FABRIC = '#e0d2b1'

plt.rcParams.update({
    'font.family': ['DejaVu Sans'], 'font.size': 10.5,
    'axes.edgecolor': AXIS, 'axes.labelcolor': MUTED,
    'xtick.color': MUTED, 'ytick.color': MUTED,
    'xtick.labelsize': 10.5, 'ytick.labelsize': 10.5,
    'figure.facecolor': BG, 'axes.facecolor': BG, 'savefig.facecolor': BG,
})

DPI = 150
W_IN = 13.44  # -> 2016 px


def figure(h_ratio):
    """h_ratio = original height / original width."""
    return plt.figure(figsize=(W_IN, W_IN * h_ratio), dpi=DPI)


def header(fig, title, sub, y0=0.955, dy=0.045):
    fig.text(0.032, y0, title, fontsize=14.5, fontweight='bold', color=INK, va='top')
    if sub:
        fig.text(0.032, y0 - dy, sub, fontsize=10.5, color=MUTED, va='top')


def foot(fig, lines, y0, dy=0.035):
    for i, t in enumerate(lines):
        fig.text(0.032, y0 - i * dy, t, fontsize=10.5, color=MUTED, va='top')


def ylabel(fig, ax, name, unit, yfrac=0.62):
    bb = ax.get_position()
    y = bb.y0 + yfrac * bb.height
    fig.text(0.032, y, name, fontsize=11, fontweight='bold', color=INK, va='bottom')
    if unit:
        fig.text(0.032, y - 0.008, unit, fontsize=10.5, color=MUTED, va='top')


def clean(ax, bottom=True):
    for s in ('top', 'right', 'left'):
        ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_visible(bottom)
    ax.spines['bottom'].set_color(AXIS)
    ax.tick_params(length=0, pad=8)
    ax.grid(axis='y', color=GRID, lw=1)
    ax.set_axisbelow(True)


def save(fig, name):
    out = f'/home/claude/sm/img/en/{name}.png'
    fig.savefig(out, dpi=DPI)
    print('saved', out)
