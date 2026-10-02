"""尺寸链与定位误差计算库（第 13 轮 7.3（4）N4）：教材第 51、53、57、59–69 章的算例和 AI 工艺评审员共用。

尺寸链
- `Link`：组成环（基本尺寸、上下偏差、增环 +1 / 减环 −1）；
- `extreme(links)`：极值法求封闭环（完全互换）；
- `statistical(links, k=1.0)`：概率法（各环正态、对称分布于公差带中点时 k = 1；偏态时 k > 1）；
- `monte_carlo(links, n, dist)`：蒙特卡罗模拟核对；
- `solve_link(links, closing, unknown)`：已知封闭环要求，反求一个组成环（工序尺寸换算、“中间计算”）。

工艺尺寸跟踪图（tolerance chart）
- `ToleranceChart`：按工序顺序登记每一刀“以哪个面为基准、加工哪个面、工序尺寸多少”，程序把每个面在各工序的“版本”连成一棵树；
  任两个面（例如图纸尺寸的两端、某面相邻两次加工的版本）之间的路径就是尺寸链，自动求出图纸尺寸能否保证、每次加工的余量最小最大值。

定位误差
- V 形块、心轴（定位销）、一面两销、顶尖与中心孔，以及基准不重合误差；`v_block_mc` 用蒙特卡罗核对公式。

单位：mm；角度：度。
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field


# ---------------------------------------------------------------- 尺寸链
@dataclass
class Link:
    name: str
    nominal: float
    es: float = 0.0
    ei: float = 0.0
    sense: int = +1           # +1 增环，−1 减环

    @property
    def T(self):
        return self.es - self.ei

    @property
    def mid(self):            # 中间偏差
        return (self.es + self.ei) / 2

    @property
    def max(self):
        return self.nominal + self.es

    @property
    def min(self):
        return self.nominal + self.ei


@dataclass
class Result:
    nominal: float
    es: float
    ei: float
    method: str
    detail: dict = field(default_factory=dict)

    @property
    def T(self):
        return self.es - self.ei

    @property
    def max(self):
        return self.nominal + self.es

    @property
    def min(self):
        return self.nominal + self.ei

    def text(self, nd=3):
        def s(x):
            return "0" if abs(x) < 10 ** -(nd + 1) else f"{x:+.{nd}f}".rstrip("0").rstrip(".")
        return f"{self.nominal:g}（{s(self.es)}/{s(self.ei)}）"


def extreme(links) -> Result:
    """极值法：A0 = Σ增 − Σ减；ES0 = Σ增ES − Σ减EI；EI0 = Σ增EI − Σ减ES；T0 = ΣTi。"""
    A0 = sum(l.sense * l.nominal for l in links)
    es = sum(l.es if l.sense > 0 else -l.ei for l in links)
    ei = sum(l.ei if l.sense > 0 else -l.es for l in links)
    return Result(A0, es, ei, "极值法", {"T_sum": sum(l.T for l in links)})


def statistical(links, k=1.0) -> Result:
    """概率法：封闭环中间偏差 Δ0 = Σ(±Δi)，公差 T0 = k·√ΣTi²（各环正态、公差带 = ±3σ 时 k = 1）。"""
    A0 = sum(l.sense * l.nominal for l in links)
    d0 = sum(l.sense * l.mid for l in links)
    T0 = k * math.sqrt(sum(l.T ** 2 for l in links))
    return Result(A0, d0 + T0 / 2, d0 - T0 / 2, "概率法", {"k": k, "mid": d0})


def monte_carlo(links, n=200_000, dist="normal", seed=1) -> Result:
    """蒙特卡罗：各环按正态（公差带 = ±3σ，截尾于公差带）或均匀分布抽样，返回封闭环的 ±3σ 区间与实际极值。"""
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        s = 0.0
        for l in links:
            if dist == "uniform":
                x = rng.uniform(l.min, l.max)
            else:
                while True:
                    x = rng.gauss(l.nominal + l.mid, l.T / 6)
                    if l.min <= x <= l.max:
                        break
            s += l.sense * x
        vals.append(s)
    A0 = sum(l.sense * l.nominal for l in links)
    mu = sum(vals) / n
    sd = math.sqrt(sum((v - mu) ** 2 for v in vals) / (n - 1))
    return Result(A0, mu - A0 + 3 * sd, mu - A0 - 3 * sd, "蒙特卡罗",
                  {"n": n, "dist": dist, "mean": mu, "sd": sd, "min": min(vals), "max": max(vals)})


def solve_link(links, closing: tuple, unknown: str, sense: int = +1) -> Link:
    """反计算：已知封闭环 (A0, ES0, EI0) 和其余组成环，求名为 unknown 的组成环（极值法）。

    unknown 在 links 里可以不出现；sense 是它作为增环（+1）还是减环（−1）。"""
    A0, ES0, EI0 = closing
    others = [l for l in links if l.name != unknown]
    a = sum(l.sense * l.nominal for l in others)
    es_o = sum(l.es if l.sense > 0 else -l.ei for l in others)
    ei_o = sum(l.ei if l.sense > 0 else -l.es for l in others)
    nom = sense * (A0 - a)
    if sense > 0:
        es, ei = ES0 - es_o, EI0 - ei_o
    else:
        es, ei = -(EI0 - ei_o), -(ES0 - es_o)
    if es < ei - 1e-12:
        raise ValueError(f"封闭环公差 {ES0 - EI0:.4f} 小于其余组成环公差之和 {es_o - ei_o:.4f}：极值法下无解，要压缩其他环的公差或改用概率法")
    return Link(unknown, nom, es, ei, sense)


# ---------------------------------------------------------------- 工艺尺寸跟踪图
@dataclass
class Cut:
    seq: int                  # 工序号（或工序号.工步号）
    ref: str                  # 工序基准面（测量起点）
    surf: str                 # 本工序加工的面
    nominal: float            # 工序尺寸（从 ref 到 surf，沿坐标正向为正）
    es: float = 0.0
    ei: float = 0.0
    label: str = ""


class ToleranceChart:
    """一维（轴向）工艺尺寸跟踪图。

    每个面在毛坯上有一个初始版本（surf@0）；每次加工产生新版本（surf@seq），并通过这一刀的工序尺寸连到当时的基准面版本。
    所有版本组成一棵树（毛坯面之间由毛坯尺寸相连），任两个版本之间的路径就是一条尺寸链。
    坐标：面的位置 x 沿轴向；工序尺寸 = x(surf) − x(ref)。
    """

    def __init__(self, blank: list[tuple]):
        """blank: [(面A, 面B, 基本尺寸 x(B)−x(A), es, ei)]，毛坯上各面之间的尺寸（构成树）。"""
        self.edges = {}       # 版本 → [(邻接版本, Link 方向)]
        self.cur = {}         # 面 → 当前版本
        self.cuts = []
        for a, b, nom, es, ei in blank:
            va, vb = self._ver(a, 0), self._ver(b, 0)
            self._edge(va, vb, nom, es, ei, f"毛坯 {a}–{b}")

    def _ver(self, s, k):
        v = f"{s}@{k}"
        self.edges.setdefault(v, [])
        self.cur.setdefault(s, v)
        return v

    def _edge(self, va, vb, nom, es, ei, label):
        self.edges[va].append((vb, (nom, es, ei, label, +1)))
        self.edges[vb].append((va, (nom, es, ei, label, -1)))

    def cut(self, c: Cut):
        ref = self.cur[c.ref]
        v = f"{c.surf}@{c.seq}"
        self.edges.setdefault(v, [])
        prev = self.cur.get(c.surf)
        self._edge(ref, v, c.nominal, c.es, c.ei, c.label or f"工序 {c.seq} {c.ref}→{c.surf}")
        self.cur[c.surf] = v
        self.cuts.append((c, prev, v))
        return self

    def _path(self, va, vb):
        """树上 va → vb 的路径（BFS），返回 [(nom, es, ei, label, 方向)]，方向 +1 表示沿 x 正向累加。"""
        from collections import deque
        prev = {va: None}
        dq = deque([va])
        while dq:
            u = dq.popleft()
            if u == vb:
                break
            for w, e in self.edges[u]:
                if w not in prev:
                    prev[w] = (u, e)
                    dq.append(w)
        if vb not in prev:
            raise ValueError(f"{va} 与 {vb} 之间没有尺寸联系")
        out, u = [], vb
        while prev[u]:
            p, e = prev[u]
            out.append(e)
            u = p
        return list(reversed(out))

    def chain(self, a: str, b: str, version_a=None, version_b=None) -> list[Link]:
        """面 a（当前或指定版本）到面 b 的尺寸链：x(b) − x(a) = Σ(±组成环)。"""
        va = version_a or self.cur[a]
        vb = version_b or self.cur[b]
        return [Link(lab, nom, es, ei, d) for nom, es, ei, lab, d in self._path(va, vb)]

    def resultant(self, a, b, method="extreme") -> Result:
        links = self.chain(a, b)
        return extreme(links) if method == "extreme" else statistical(links)

    def allowances(self) -> list[dict]:
        """每次加工的余量（沿 x 的切除厚度，取正值）：上一版本到新版本之间的尺寸链。"""
        out = []
        for c, prev, v in self.cuts:
            if not prev:
                continue
            links = [Link(lab, nom, es, ei, d) for nom, es, ei, lab, d in self._path(prev, v)]
            r = extreme(links)
            sign = -1 if r.nominal < 0 else 1          # 切除厚度的方向：面向哪边移动
            zmin, zmax = sorted((sign * r.min, sign * r.max))
            out.append({"seq": c.seq, "surface": c.surf, "nominal": abs(r.nominal), "min": zmin, "max": zmax,
                        "links": [l.name for l in links]})
        return out


# ---------------------------------------------------------------- 定位误差
def v_block(Td: float, alpha_deg: float = 90.0, measure: str = "center") -> float:
    """外圆在 V 形块上定位，工件直径公差 Td 引起的定位误差（工序尺寸方向垂直于 V 形块对称面……竖直方向）。

    measure：工序基准是轴心 "center"、上母线 "top"、下母线 "bottom"。
    ΔY（轴心）= Td / (2 sin(α/2))；上母线 = ΔY + Td/2；下母线 = ΔY − Td/2。"""
    s = math.sin(math.radians(alpha_deg) / 2)
    dy = Td / (2 * s)
    return {"center": dy, "top": dy + Td / 2, "bottom": dy - Td / 2}[measure]


def v_block_mc(d_nom, es, ei, alpha_deg=90.0, measure="center", n=100_000, seed=2):
    """蒙特卡罗核对 V 形块公式：工件直径在公差带内均匀抽样，求工序基准的竖直位置变动范围。"""
    rng = random.Random(seed)
    s = math.sin(math.radians(alpha_deg) / 2)
    ys = []
    for _ in range(n):
        d = rng.uniform(d_nom + ei, d_nom + es)
        yc = (d / 2) / s                          # 轴心到 V 形块交点的距离
        y = {"center": yc, "top": yc + d / 2, "bottom": yc - d / 2}[measure]
        ys.append(y)
    return max(ys) - min(ys)


def pin_clearance(D: tuple, d: tuple, contact: str = "any") -> float:
    """孔套在心轴或定位销上（间隙配合）的基准位移误差。D = (孔基本尺寸, ES, EI)，d = (销, es, ei)。

    contact="any"：间隙方向任意（工件可在任意方向靠紧），ΔY = Xmax = Dmax − dmin；
    contact="one"：工件总靠向同一侧（如重力或夹紧力单向），ΔY = (TD + Td)/2。"""
    TD, Td = D[1] - D[2], d[1] - d[2]
    if contact == "one":
        return (TD + Td) / 2
    return (D[0] + D[1]) - (d[0] + d[2])


def two_pins(L: float, hole1: tuple, pin1: tuple, hole2: tuple, pin2_width_clear: float) -> dict:
    """一面两销（圆柱销 + 削边销）的定位误差。

    hole/pin = (基本尺寸, 上偏差, 下偏差)；pin2_width_clear：削边销方向上的最大间隙 X2max（削边销只在两孔连线的垂直方向起作用）。
    返回：圆柱销处的移动误差 X1max，以及最大转角误差 Δθ = arctan((X1max + X2max) / (2L))（两孔偏向相反时）。"""
    X1 = pin_clearance(hole1, pin1)
    th = math.degrees(math.atan((X1 + pin2_width_clear) / (2 * L)))
    return {"X1max": X1, "X2max": pin2_width_clear, "rot_deg": th, "rot_mm_per_100": math.tan(math.radians(th)) * 100}


def center_hole_axial(dD: float, cone_deg: float = 60.0) -> float:
    """两顶尖装夹：中心孔锥面直径的变动 dD 引起的工件轴向位移（锥角 60° 时 Δz = dD / (2 tan 30°)）。"""
    return dD / (2 * math.tan(math.radians(cone_deg) / 2))


def datum_mismatch(links) -> float:
    """基准不重合误差 ΔB：联系设计基准与定位基准的尺寸的公差之和（极值法）。"""
    return sum(l.T for l in links)


def locate_error(dB: float, dY: float, same_dir: bool = True) -> float:
    """定位误差 ΔD = ΔB ± ΔY：两者引起的工序基准位移同向时相加，反向时相减（取绝对值）。"""
    return dB + dY if same_dir else abs(dB - dY)


def ok_against(tol: float, error: float, fraction: float = 1 / 3) -> bool:
    """经验判据：定位误差不超过工序公差的 1/3（留出加工与测量误差的空间）。"""
    return error <= tol * fraction + 1e-12
