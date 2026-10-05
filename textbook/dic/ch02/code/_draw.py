"""第 2 章示意图共用的配色与晶体管级电路画法（schemdraw）。"""
import schemdraw
import schemdraw.elements as elm

from bookout import COLORS

NMOS = "#1d6fb8"       # NMOS、下拉网络：蓝
PMOS = "#c0392b"       # PMOS、上拉网络：红
MEAN = "#2e8b57"       # 合成结果、最优值：绿
LOAD = "#e67e22"       # 负载、要求、限值：橙
INK = COLORS["ink"]
MUTED = COLORS["muted"]

schemdraw.config(fontsize=11, lw=1.3, font="Noto Sans CJK JP")


def spines(ax):
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)


class Net:
    """在 (x, y) 坐标上摆晶体管：每个管子竖放，长 1.5，栅极在左边 1.37 处。"""

    def __init__(self, d):
        self.d = d

    def line(self, a, b, color=INK):
        self.d.add(elm.Line().at(a).to(b).color(color))

    def dot(self, p, color=INK):
        self.d.add(elm.Dot(radius=0.07).at(p).color(color))

    def text(self, p, s, color=INK, loc="center", size=11):
        self.d.add(elm.Label().at(p).label(s, loc=loc, color=color, fontsize=size))

    def pfet(self, x, ytop, gate, w=None, right=False):
        e = elm.PFet(bulk=False).at((x, ytop)).anchor("source").theta(0)
        e = self.d.add((e if right else e.reverse()).color(PMOS))
        g = e.absanchors["gate"]
        sx = 0.35 if right else -0.35
        self.line(g, (g[0] + sx, g[1]), PMOS)
        if gate:
            self.text((g[0] + sx * 1.3, g[1]), gate, PMOS, loc="right" if right else "left")
        if w:
            self.text((x + 0.25, ytop - 0.75), w, MUTED, loc="right", size=9)
        return ytop - 1.5

    def nfet(self, x, ytop, gate, w=None):
        e = self.d.add(elm.NFet(bulk=False).at((x, ytop)).anchor("drain").theta(0).reverse().color(NMOS))
        g = e.absanchors["gate"]
        self.line(g, (g[0] - 0.35, g[1]), NMOS)
        self.text((g[0] - 0.45, g[1]), gate, NMOS, loc="left")
        if w:
            self.text((x + 0.25, ytop - 0.75), w, MUTED, loc="right", size=9)
        return ytop - 1.5

    def rail(self, x0, x1, y, name):
        self.line((x0, y), (x1, y))
        self.text((x0 - 0.15, y), name, MUTED, loc="left", size=10)

    def ground(self, p):
        self.d.add(elm.Ground().at(p))


def schem_to_ax(d, ax):
    d.draw(canvas=ax, show=False)
    ax.set_aspect("equal")
    ax.axis("off")
