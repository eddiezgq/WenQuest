"""第 33 章示意图共用的画法：阶梯轴、轴承、齿轮、套筒、联轴器、力和弯矩图。长度以 mm 画在数据坐标里。"""
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle

from bookout import COLORS, T

INK = COLORS["ink"]
MUTED = COLORS["muted"]
STEEL = "#b8c4ce"       # 轴
BEARING = "#7f9cb8"     # 轴承
GEAR = "#d9a441"        # 齿轮
SLEEVE = "#9bbf85"      # 套筒、轴环一类定位件
CPL = "#c48ac9"         # 联轴器
FORCE = "#c0392b"
MOMENT = "#2c6fbb"
TORQUE = "#8e44ad"


def shaft(ax, lay, color=STEEL, lw=1.2, keys=(), center=True):
    """阶梯轴的轴向剖面（上下对称）。lay: [(z0, z1, d, ...)]；keys: [(z0, z1, t)] 画在上方的键槽。"""
    for z0, z1, d, *_ in lay:
        ax.add_patch(Rectangle((z0, -d / 2), z1 - z0, d, fc=color, ec=INK, lw=lw, zorder=2))
    for z0, z1, t in keys:
        d = [s[2] for s in lay if s[0] <= (z0 + z1) / 2 <= s[1]][0]
        ax.add_patch(Rectangle((z0, d / 2 - t), z1 - z0, t, fc="white", ec=INK, lw=0.9, zorder=3))
    if center:
        ax.plot([lay[0][0] - 8, lay[-1][1] + 8], [0, 0], color=MUTED, lw=0.7, ls=(0, (8, 3, 2, 3)), zorder=1)


def bearing(ax, zc, d, D, B):
    """深沟球轴承的剖面（上下各一）：内外圈和一个滚珠。"""
    for s in (1, -1):
        y0 = s * d / 2
        h = (D - d) / 2
        ax.add_patch(Rectangle((zc - B / 2, min(y0, y0 + s * h)), B, h, fc=BEARING, ec=INK, lw=1.0, zorder=4))
        from matplotlib.patches import Circle
        ax.add_patch(Circle((zc, s * (d + D) / 4), min(B, h) * 0.32, fc="white", ec=INK, lw=0.9, zorder=5))


def ring(ax, z0, z1, d_in, d_out, color, zorder=4, hatch=None):
    for s in (1, -1):
        ax.add_patch(Rectangle((z0, s * d_in / 2 if s > 0 else -d_out / 2), z1 - z0, (d_out - d_in) / 2,
                               fc=color, ec=INK, lw=1.0, zorder=zorder, hatch=hatch))


def gear(ax, z0, hub, d_bore, d_hub, rim_w, d_root, d_tip):
    """齿轮剖面：轮毂、辐板（简化为实体）、轮缘与齿（齿顶到齿根用斜线表示）。"""
    zc = z0 + hub / 2
    ring(ax, z0, z0 + hub, d_bore, d_hub, GEAR)
    ring(ax, zc - rim_w / 2, zc + rim_w / 2, d_hub, d_root, GEAR)
    ring(ax, zc - rim_w / 2, zc + rim_w / 2, d_root, d_tip, GEAR, hatch="////")


def force(ax, x, y, dx, dy, text="", color=FORCE, size=11, off=(0, 0), lw=2.0):
    ax.add_patch(FancyArrowPatch((x, y), (x + dx, y + dy), arrowstyle="-|>", mutation_scale=13, lw=lw, color=color,
                                 shrinkA=0, shrinkB=0, zorder=7))
    if text:
        ax.text(x + dx + off[0], y + dy + off[1], text, color=color, fontsize=size, ha="center", va="center", zorder=8)


def support(ax, z, y, size=6):
    """简支（三角形）。"""
    ax.add_patch(Polygon([[z, y], [z - size, y - 1.6 * size], [z + size, y - 1.6 * size]], closed=True, fc="white",
                         ec=INK, lw=1.2, zorder=6))
    ax.plot([z - 1.6 * size, z + 1.6 * size], [y - 1.6 * size] * 2, color=INK, lw=1.2)


def dim(ax, z0, z1, y, text, size=9, color=INK):
    """水平尺寸线。"""
    ax.annotate("", (z0, y), (z1, y), arrowprops=dict(arrowstyle="<->", lw=0.8, color=color, shrinkA=0, shrinkB=0))
    ax.text((z0 + z1) / 2, y + 2.2, text, ha="center", va="bottom", fontsize=size, color=color)


def diagram(ax, z, v, color, label, unit, fill=True):
    """弯矩、转矩一类的图：基线、曲线、填色、最大值标注。"""
    ax.plot(z, v, color=color, lw=1.6)
    if fill:
        ax.fill_between(z, 0, v, color=color, alpha=0.18, lw=0)
    ax.axhline(0, color=INK, lw=0.8)
    ax.set_ylabel(f"{label} / {unit}", fontsize=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


__all__ = ["shaft", "bearing", "ring", "gear", "force", "support", "dim", "diagram", "T", "INK", "MUTED", "STEEL",
           "BEARING", "GEAR", "SLEEVE", "CPL", "FORCE", "MOMENT", "TORQUE"]
