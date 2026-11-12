"""第 161 轮：设计制造全过程案例的共用代码。

一个案例 = factory/cases/<工厂>/<案例号>/ 下的 case.json（八步、校核一览）+ 每步的 md、图、模型、程序。
网页（数字工厂“设计案例”页）只读 case.json 和这些文件。生成脚本：tools/cases/<工厂>_<案例号>.py。
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIGITAL = ROOT / "factory" / "digital"
CASES = ROOT / "factory" / "cases"
for _f in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"):
    if Path(_f).exists():
        font_manager.fontManager.addfont(_f)
plt.rcParams.update({"font.family": ["Noto Sans CJK JP", "DejaVu Sans"], "axes.unicode_minus": False, "font.size": 9.5,
                     "axes.spines.top": False, "axes.spines.right": False})

# 八步（全部案例同一套；简单案例某一步可以很短，但不跳）
STEPS = [
    ("brief", "任务书", "Design brief"),
    ("concept", "方案", "Concept"),
    ("calc", "计算", "Calculation"),
    ("sim", "仿真", "Simulation"),
    ("cad", "三维与图纸", "3D model & drawing"),
    ("process", "工艺", "Process planning"),
    ("make", "制造", "Manufacturing"),
    ("review", "总结", "Review"),
]
INK, MUTED, ACCENT, OK, BAD = "#1f2933", "#7b8794", "#2c6fbb", "#2f9e44", "#c92a2a"


def fmt(v, digits=3):
    if isinstance(v, str):
        return v
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "∞"
    if abs(v) >= 1000:
        return f"{v:,.0f}"
    return f"{v:.{digits}g}"


class Case:
    def __init__(self, plant, cid, level, title, title_en, item, summary, summary_en, script):
        self.dir = CASES / plant / cid
        if self.dir.exists():
            shutil.rmtree(self.dir)
        self.dir.mkdir(parents=True)
        self.meta = dict(plant=plant, id=cid, level=level, title=title, title_en=title_en, item=item, summary=summary,
                         summary_en=summary_en, script=script, generated=dt.date.today().isoformat(),
                         honest="示例设计：经计算和仿真校核，没有实物试制；数值为示例值。",
                         honest_en="Example design: checked by calculation and simulation, not built and tested; all values are examples.")
        self.steps = {}
        self.checks = []

    # ------------------------------------------------------------ 文件
    def text(self, name, body):
        (self.dir / name).write_text(body, encoding="utf-8")
        return name

    def fig(self, fig, name, dpi=150):
        fig.savefig(self.dir / name, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        return name

    def raw(self, name, data: bytes):
        (self.dir / name).write_bytes(data)
        return name

    def path(self, name):
        return self.dir / name

    # ------------------------------------------------------------ 步骤与校核
    def step(self, key, summary, summary_en, md=None, figs=(), files=(), tools=(), facts=()):
        """figs：[(文件, 说明, 英文)]；files：[(文件, 说明, 英文)] 供下载；tools：[(按钮文字, 英文, 路由)]；
        facts：[(名称, 英文, 值, 单位)] 关键数（单位写中英通用的，如 h、N·m、×）"""
        title, title_en = next((t, e) for k, t, e in STEPS if k == key)
        self.steps[key] = dict(key=key, title=title, title_en=title_en, summary=summary, summary_en=summary_en, md=md,
                               figs=[dict(file=f, caption=c, caption_en=e) for f, c, e in figs],
                               files=[dict(file=f, label=c, label_en=e) for f, c, e in files],
                               tools=[dict(label=a, label_en=b, route=r) for a, b, r in tools],
                               facts=[dict(name=n, name_en=ne, value=fmt(v) if not isinstance(v, str) else v, unit=u) for n, ne, v, u in facts])

    def check(self, step, what, what_en, value, op, limit, unit="", src=""):
        ok = {">=": value >= limit, "<=": value <= limit, "==": value == limit}[op]
        self.checks.append(dict(step=step, what=what, what_en=what_en, value=fmt(value), op=op, limit=fmt(limit), unit=unit, ok=bool(ok), src=src))
        return ok

    def write(self):
        missing = [k for k, *_ in STEPS if k not in self.steps]
        if missing:
            raise SystemExit("案例缺步骤：" + "、".join(missing))
        files = sorted(p.name for p in self.dir.iterdir())
        for s in self.steps.values():
            for f in [x["file"] for x in s["figs"] + s["files"]] + ([s["md"]] if s["md"] else []):
                if f not in files:
                    raise SystemExit(f"步骤 {s['key']} 引用的文件不存在：{f}")
        out = dict(self.meta, steps=[self.steps[k] for k, *_ in STEPS], checks=self.checks,
                   all_ok=all(c["ok"] for c in self.checks), files=files)
        (self.dir / "case.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        bad = [c for c in self.checks if not c["ok"]]
        print(f"{self.meta['plant']}/{self.meta['id']}：{len(self.checks)} 项校核，{'全部通过' if not bad else '不通过 ' + str(len(bad))}；文件 {len(files)} 个")
        return out


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out)


# ---------------------------------------------------------------- 轴类零件图（SVG）
def shaft_drawing(segs, keyways, fillets, *, item, title, material, rev, tech, chamfer=1.5, runout=(), datums=(), scale=3.0):
    """阶梯轴零件图。
    segs：[(d, L, 名称, 公差带, Ra)]；keyways：[(z0, z1, d, b, t, 公差带宽, 型式)]；fillets：{z: r}；
    runout：[(段号, 值, 'radial'|'face')]；datums：[(段号, 字母)]；tech：技术要求文字列表。"""
    sys.path.insert(0, str(ROOT / "textbook" / "mechdesign" / "conventions"))
    import mdstd
    total = sum(s[1] for s in segs)
    dmax = max(s[0] for s in segs)
    W, H = 1120, 700
    s = scale
    x0 = 70
    yc = 250
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         'font-family="Noto Sans CJK SC, Noto Sans SC, sans-serif" font-size="12">',
         '<defs><marker id="a" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         '<path d="M0 2 L10 5 L0 8 z"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         f'<rect x="8" y="8" width="{W - 16}" height="{H - 16}" fill="none" stroke="#000" stroke-width="1.6"/>']
    X = lambda z: x0 + z * s  # noqa: E731
    o.append(f'<line x1="{X(0) - 18}" y1="{yc}" x2="{X(total) + 18}" y2="{yc}" stroke="#000" stroke-dasharray="14 3 2 3" stroke-width="0.6"/>')
    # 外形：上下母线 + 台阶
    z = 0.0
    prev = None
    lay = []
    for d, L, *_ in segs:
        lay.append((z, z + L, d))
        z += L
    path = []
    for i, (za, zb, d) in enumerate(lay):
        r = d / 2 * s
        c = chamfer * s if i == 0 else 0
        c2 = chamfer * s if i == len(lay) - 1 else 0
        path.append(f'<path d="M{X(za) + c:.1f} {yc - r:.1f} L{X(zb) - c2:.1f} {yc - r:.1f} M{X(za) + c:.1f} {yc + r:.1f} L{X(zb) - c2:.1f} {yc + r:.1f}" '
                    'stroke="#000" stroke-width="1.5" fill="none"/>')
        if i == 0:
            path.append(f'<path d="M{X(za) + c:.1f} {yc - r:.1f} L{X(za):.1f} {yc - r + c:.1f} L{X(za):.1f} {yc + r - c:.1f} L{X(za) + c:.1f} {yc + r:.1f}" stroke="#000" stroke-width="1.5" fill="none"/>')
        if i == len(lay) - 1:
            path.append(f'<path d="M{X(zb) - c2:.1f} {yc - r:.1f} L{X(zb):.1f} {yc - r + c2:.1f} L{X(zb):.1f} {yc + r - c2:.1f} L{X(zb) - c2:.1f} {yc + r:.1f}" stroke="#000" stroke-width="1.5" fill="none"/>')
        if prev is not None:
            rr = max(prev, d) / 2 * s
            path.append(f'<line x1="{X(za):.1f}" y1="{yc - rr:.1f}" x2="{X(za):.1f}" y2="{yc + rr:.1f}" stroke="#000" stroke-width="1.5"/>')
        prev = d
    o += path
    # 键槽（主视图上方画槽底线）与断面图
    sec_x = 120
    for k, (z0, z1, d, b, t, tolb, kind) in enumerate(keyways):
        top = yc - d / 2 * s
        o.append(f'<rect x="{X(z0):.1f}" y="{top:.1f}" width="{(z1 - z0) * s:.1f}" height="{t * s:.1f}" fill="#e9ecef" stroke="#000" stroke-width="1"/>')
        lab = "CDEF"[k]
        o.append(f'<text x="{X((z0 + z1) / 2):.1f}" y="{top - 30:.1f}" text-anchor="middle">{lab}</text>'
                 f'<line x1="{X((z0 + z1) / 2):.1f}" y1="{top - 26:.1f}" x2="{X((z0 + z1) / 2):.1f}" y2="{top - 8:.1f}" stroke="#000" stroke-width="1.2" marker-end="url(#a)"/>')
        o.append(f'<text x="{X((z0 + z1) / 2):.1f}" y="{top - 46:.1f}" text-anchor="middle" font-size="11">键槽长 {z1 - z0:g}{"（开到轴端）" if kind == "C" else ""}</text>')
        # 断面图
        cx, cy, R = sec_x + k * 230, 588, d / 2 * 2.2
        lo, hi = mdstd.fit_limits(b, tolb)
        o.append(f'<text x="{cx}" y="{cy - R - 22}" text-anchor="middle" font-size="13">{lab}–{lab}</text>')
        yb = d / 2 - t                      # 槽底到轴心
        sx = b / 2 * 2.2
        ytop = cy - math.sqrt(R ** 2 - sx ** 2)
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{R:.1f}" fill="url(#h)" stroke="#000" stroke-width="1.3"/>'
                 f'<rect x="{cx - sx:.1f}" y="{cy - R - 2:.1f}" width="{2 * sx:.1f}" height="{R + 2 - yb * 2.2:.1f}" fill="#fff"/>'
                 f'<path d="M{cx - sx:.1f} {ytop:.1f} L{cx - sx:.1f} {cy - yb * 2.2:.1f} L{cx + sx:.1f} {cy - yb * 2.2:.1f} L{cx + sx:.1f} {ytop:.1f}" '
                 'stroke="#000" stroke-width="1.3" fill="none"/>'
                 f'<line x1="{cx - R - 8:.1f}" y1="{cy}" x2="{cx + R + 8:.1f}" y2="{cy}" stroke="#000" stroke-dasharray="10 3 2 3" stroke-width="0.5"/>'
                 f'<line x1="{cx}" y1="{cy - R - 8:.1f}" x2="{cx}" y2="{cy + R + 8:.1f}" stroke="#000" stroke-dasharray="10 3 2 3" stroke-width="0.5"/>')
        o.append(f'<text x="{cx}" y="{cy + R + 18}" text-anchor="middle" font-size="11">{b:g} {tolb}（{(lo - b) * 1000:+.0f}/{(hi - b) * 1000:+.0f} μm）</text>')
        o.append(f'<text x="{cx}" y="{cy + R + 34}" text-anchor="middle" font-size="11">d − t = {d - t:g}（0/−0.2）</text>')
    o.insert(2, '<defs><pattern id="h" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                '<line x1="0" y1="0" x2="0" y2="6" stroke="#666" stroke-width="0.7"/></pattern></defs>')
    # 圆角
    for zz, r in fillets.items():
        d_small = min(dd for za, zb, dd in lay if abs(za - zz) < 1e-6 or abs(zb - zz) < 1e-6)
        o.append(f'<text x="{X(zz) + 3:.1f}" y="{yc + d_small / 2 * s + 14:.1f}" font-size="10" fill="#444">R{r:g}</text>')
    # 直径标注（带公差带与极限偏差）
    for i, ((za, zb, d), seg) in enumerate(zip(lay, segs)):
        tol = seg[3] if len(seg) > 3 else ""
        txt = f"Ø{d:g}"
        if tol:
            lo, hi = mdstd.fit_limits(d, tol)
            txt += f" {tol}"
            sub = f"({(hi - d) * 1000:+.0f}/{(lo - d) * 1000:+.0f} μm)"
        else:
            sub = ""
        xm = X((za + zb) / 2)
        o.append(f'<text x="{xm:.1f}" y="{yc - 4:.1f}" text-anchor="middle" font-size="11.5">{txt}</text>')
        if sub:
            o.append(f'<text x="{xm:.1f}" y="{yc + 12:.1f}" text-anchor="middle" font-size="9.5">{sub}</text>')
        ra = seg[4] if len(seg) > 4 else None
        if ra:
            yt = yc + d / 2 * s
            o.append(f'<path d="M{xm - 6:.1f} {yt + 4:.1f} L{xm:.1f} {yt + 13:.1f} L{xm + 12:.1f} {yt - 6:.1f}" stroke="#000" fill="none" stroke-width="0.9"/>'
                     f'<text x="{xm + 13:.1f}" y="{yt - 6:.1f}" font-size="10">Ra {ra:g}</text>')
    # 长度：链式尺寸
    yd = yc + dmax / 2 * s + 38
    for za, zb, d in lay:
        o.append(f'<line x1="{X(za):.1f}" y1="{yd}" x2="{X(zb):.1f}" y2="{yd}" stroke="#000" stroke-width="0.6" marker-start="url(#a)" marker-end="url(#a)"/>'
                 f'<text x="{X((za + zb) / 2):.1f}" y="{yd - 4}" text-anchor="middle" font-size="11">{zb - za:g}</text>')
        o.append(f'<line x1="{X(za):.1f}" y1="{yc + d / 2 * s + 3:.1f}" x2="{X(za):.1f}" y2="{yd + 26}" stroke="#000" stroke-width="0.4"/>')
    o.append(f'<line x1="{X(total):.1f}" y1="{yc + lay[-1][2] / 2 * s + 3:.1f}" x2="{X(total):.1f}" y2="{yd + 26}" stroke="#000" stroke-width="0.4"/>')
    o.append(f'<line x1="{X(0):.1f}" y1="{yd + 22}" x2="{X(total):.1f}" y2="{yd + 22}" stroke="#000" stroke-width="0.6" marker-start="url(#a)" marker-end="url(#a)"/>'
             f'<text x="{X(total / 2):.1f}" y="{yd + 18}" text-anchor="middle" font-size="11.5">{total:g} ± 0.5</text>')
    # 基准与跳动
    for i, letter in datums:
        za, zb, d = lay[i]
        xm, yt = X((za + zb) / 2), yc - d / 2 * s
        o.append(f'<line x1="{xm:.1f}" y1="{yt:.1f}" x2="{xm:.1f}" y2="{yt - 70:.1f}" stroke="#000" stroke-width="0.8"/>'
                 f'<path d="M{xm - 5:.1f} {yt:.1f} L{xm + 5:.1f} {yt:.1f} L{xm:.1f} {yt - 7:.1f} z" fill="#000"/>'
                 f'<rect x="{xm - 9:.1f}" y="{yt - 88:.1f}" width="18" height="18" fill="#fff" stroke="#000"/>'
                 f'<text x="{xm:.1f}" y="{yt - 74:.1f}" text-anchor="middle" font-size="12">{letter}</text>')
    ref = "–".join(letter for _, letter in datums) or "A"
    for j, (i, val, kind) in enumerate(runout):
        za, zb, d = lay[i]
        if kind == "face":                  # 端面圆跳动：指引线指在这一段左端面（齿轮、轴承靠的轴肩）
            xm, yb = X(za), yc + (d / 2 - 2) * s
        else:
            xm, yb = X((za + zb) / 2), yc + d / 2 * s
        by = yd + 50 + j * 26
        o.append(f'<line x1="{xm:.1f}" y1="{yb:.1f}" x2="{xm:.1f}" y2="{by:.1f}" stroke="#000" stroke-width="0.6" marker-start="url(#a)"/>')
        bx = xm - 46
        o.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="92" height="18" fill="#fff" stroke="#000" stroke-width="0.8"/>'
                 f'<line x1="{bx + 20:.1f}" y1="{by:.1f}" x2="{bx + 20:.1f}" y2="{by + 18:.1f}" stroke="#000" stroke-width="0.8"/>'
                 f'<line x1="{bx + 62:.1f}" y1="{by:.1f}" x2="{bx + 62:.1f}" y2="{by + 18:.1f}" stroke="#000" stroke-width="0.8"/>'
                 f'<text x="{bx + 10:.1f}" y="{by + 13:.1f}" text-anchor="middle" font-size="11">↗</text>'
                 f'<text x="{bx + 41:.1f}" y="{by + 13:.1f}" text-anchor="middle" font-size="11">{val:g}</text>'
                 f'<text x="{bx + 77:.1f}" y="{by + 13:.1f}" text-anchor="middle" font-size="11">{ref}</text>')
    # 技术要求
    tx, ty = 600, 470
    o.append(f'<text x="{tx}" y="{ty}" font-size="13" font-weight="bold">技术要求</text>')
    for i, line in enumerate(tech):
        o.append(f'<text x="{tx}" y="{ty + 20 + i * 18}" font-size="11.5">{i + 1}. {line}</text>')
    # 标题栏
    bx, by, bw, bh = W - 430, 30, 410, 92
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="none" stroke="#000" stroke-width="1.2"/>')
    rows = [("名称", title), ("图号 / 物料", item), ("版本", rev), ("材料", material),
            ("单位", "问渠减速器厂（示例设计）"), ("日期", dt.date.today().isoformat()), ("比例", f"{scale:g} 像素 / mm"), ("生成", "tools/cases")]
    for i, (k, v) in enumerate(rows):
        cx, cy = bx + (i % 2) * bw / 2, by + (i // 2) * bh / 4
        o.append(f'<rect x="{cx:.0f}" y="{cy:.0f}" width="{bw / 2:.0f}" height="{bh / 4:.0f}" fill="none" stroke="#000" stroke-width="0.5"/>'
                 f'<text x="{cx + 6:.0f}" y="{cy + 16:.0f}" font-size="11">{k}：{v}</text>')
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- 三维效果图
def render_solid(solid, path, elev=30, azim=-72, color=(0.80, 0.84, 0.88), size=(9, 3.4)):
    """build123d 实体 → 简单明暗的三维效果图（matplotlib）。"""
    import numpy as np
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    verts, faces = solid.tessellate(0.05, 0.3)
    V = np.array([[v.X, v.Y, v.Z] for v in verts])
    F = np.array(faces)
    tri = V[F]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
    light = np.array([0.4, -0.6, 0.7])
    light /= np.linalg.norm(light)
    sh = 0.55 + 0.45 * np.abs(n @ light)
    cols = np.clip(np.outer(sh, color), 0, 1)
    # 轴线沿 z：画图时换成水平
    tri = tri[:, :, [2, 0, 1]]
    fig = plt.figure(figsize=size)
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(tri, facecolors=cols, edgecolors="none", linewidths=0))
    lo, hi = tri.reshape(-1, 3).min(0), tri.reshape(-1, 3).max(0)
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])
    ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(hi - lo)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    fig.savefig(path, dpi=170, bbox_inches="tight", pad_inches=0.02, transparent=False, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- 仿真车间
def run_shop(item, qty, wo, seed=7, fixes=()):
    """数字工厂仿真车间（sim/engine.py，和线上同一份代码）按现行工艺路线加工 qty 件。
    → dict(hours, measurements, events, cycle)：measurements 是 quality.measurement 的 data 列表。"""
    sys.path[:0] = [str(DIGITAL), str(ROOT / "factory")]
    from sim.engine import OP_UNITS, Engine, routing_for

    class Clock:
        t = 0.0

        def now(self):
            return self.t

    out = []
    clock = Clock()
    eng = Engine(lambda tp, ty, src, data, corr: out.append((tp, ty, data)), clock, mode="teach", auto_start=True, seed=seed, status_every_s=1e9)
    for f in fixes:                       # 改进措施（sim/errors.py 的 FIXES，和“质量 → 8D”下发措施同一个入口）
        eng.errors.apply_fix(f)
    ops = routing_for(item)
    for op, _ in ops:
        ok, why = eng.command(OP_UNITS[op][0], {"command": "dispatch", "work_order": wo, "operation": op, "qty": qty, "item": item, "routing": ops}, wo)
        if not ok:
            raise RuntimeError(why)
    while eng.q and clock.t < 7 * 86400:
        clock.t = max(clock.t, eng.next_event_time())
        eng.run_due()
    meas = [d for _, ty, d in out if ty == "quality.measurement" and d.get("item") == item]
    ev = [d for _, ty, d in out if ty == "machine.event"]
    return dict(hours=clock.t / 3600, measurements=meas, events=ev, routing=ops)


def cpk(values, lo, hi, one_sided=False):
    """→ (均值, 标准差, Cpk)。one_sided：只有上限有意义（跳动、对称度、粗糙度，下限 0 是自然界限），用 Cpu"""
    import statistics
    m = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    if sd <= 0:
        return m, sd, math.inf
    return m, sd, ((hi - m) if one_sided else min(hi - m, m - lo)) / (3 * sd)


def shop_table(meas):
    """测量值 → (表格行, 最低 Cpk, 不合格数, 各特性)。属性特性（上下限都是 0，如“磨削烧伤 0 无 1 有”）只数不合格，不算 Cpk。"""
    by = {}
    for m in meas:
        by.setdefault((m["characteristic"], m["name"], m["lower_tol_mm"], m["upper_tol_mm"]), []).append(m["value_mm"])
    rows, low, stats = [], math.inf, {}
    fails = sum(1 for m in meas if m["result"] != "pass")
    for (cid, name, lo, hi), vals in by.items():
        if lo == hi:
            bad = sum(1 for v in vals if v != lo)
            rows.append([name, f"{lo:g}", len(vals), f"不合格 {bad} 件", "—", "—（属性特性）"])
            continue
        one = lo == 0
        mu, sd, c = cpk(vals, lo, hi, one)
        low = min(low, c)
        stats[cid] = dict(name=name, mean=mu, sd=sd, cpk=c, lo=lo, hi=hi)
        unit = "μm" if "Ra" in name else "mm"
        sd_s = f"{sd:.3f} μm" if unit == "μm" else f"{sd * 1000:.1f} μm"
        rows.append([name, f"{lo:g}–{hi:g}" if not one else f"≤ {hi:g}", len(vals), f"{mu:.4f}", sd_s, f"{c:.2f}{'（单边）' if one else ''}"])
    return rows, low, fails, stats
