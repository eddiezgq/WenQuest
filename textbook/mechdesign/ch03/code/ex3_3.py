"""3.3 尺寸标注的原则：SH-301 B 版轴向尺寸的三种注法——链式、坐标式、综合式（按功能），
未注公差按 GB/T 1804-m 时，四个功能尺寸的误差累积（极值法与统计法），图 3.3.1。"""
import math
from collections import deque

import numpy as np

import _ch3 as H
import _shaft as S
import mdstd
from bookout import T, figure, out, style

lay, LEN = S.LAY_B, S.LEN_B
faces = sorted({0.0} | {z1 for _, z1, *_ in lay})            # 各端面、台阶面的轴向位置（从左端面算）
FUN = {                                                        # 功能尺寸：哪两个面之间的距离要紧、为什么
    "gear": (90.0, 115.0, T("齿轮定位面—右轴承轴肩", "gear face to right-bearing shoulder")),
    "seat": (37.0, 90.0, T("齿轮位长（要比毂短 2 mm）", "gear seat (2 mm shorter than the hub)")),
    "ext": (172.0, 240.0, T("外伸段长（要比联轴器毂短 2 mm）", "extension (2 mm shorter than the coupling hub)")),
    "total": (0.0, 240.0, T("总长", "overall length")),
}
SCHEMES = {
    "chain": [(faces[i], faces[i + 1]) for i in range(len(faces) - 1)],
    "base": [(0.0, f) for f in faces[1:]],
    "func": [(0.0, 240.0), (37.0, 90.0), (90.0, 100.0), (90.0, 115.0), (115.0, 132.0), (115.0, 172.0), (172.0, 240.0)],
}
NAMES = {"chain": T("链式", "chain"), "base": T("坐标式（以左端面为基准）", "baseline (from the left end)"), "func": T("综合式（按功能）", "functional")}


def tol(a, b):
    return mdstd.general_tol(abs(b - a), "m")


def path_tol(dims, a, b):
    """尺寸 a—b 由图上哪些尺寸决定（图是一棵树：尺寸不封闭），返回 (极值法 ±, 统计法 ±, 经过几个尺寸)"""
    adj = {f: [] for f in faces}
    for u, v in dims:
        adj[u].append((v, tol(u, v)))
        adj[v].append((u, tol(u, v)))
    prev = {a: None}
    q = deque([a])
    while q:
        u = q.popleft()
        for v, t in adj[u]:
            if v not in prev:
                prev[v] = (u, t)
                q.append(v)
    ts, x = [], b
    while prev[x] is not None:
        u, t = prev[x]
        ts.append(t)
        x = u
    return sum(ts), math.sqrt(sum(t * t for t in ts)), len(ts)


for k, dims in SCHEMES.items():                               # 每种注法都不封闭：尺寸个数 = 面数 − 1，且全部连通
    assert len(dims) == len(faces) - 1
res = {k: {f: path_tol(d, *FUN[f][:2]) for f in FUN} for k, d in SCHEMES.items()}

plt = style()
fig = plt.figure(figsize=(7.4, 6.2))
gs = fig.add_gridspec(3, 2, width_ratios=[2.25, 1], hspace=0.25, wspace=0.08)
outline = H.project(H.sh301b(), "front")[0]
R = 24.0
for row, k in enumerate(("chain", "base", "func")):
    ax = fig.add_subplot(gs[row, 0])
    sh = H.Sheet(ax)
    sh.polys(outline, "thick")
    sh.line((-4, 0), (LEN + 4, 0), "center")
    dims = SCHEMES[k]
    levels = []                                               # 尺寸线分层：互相重叠的放到外面一层
    for a, b in sorted(dims, key=lambda d: (d[1] - d[0])):
        lv = 0
        while any(not (b <= a2 or a >= b2) and l == lv for a2, b2, l in levels):
            lv += 1
        levels.append((a, b, lv))
    deep = {}
    for a, b, lv in levels:
        y = -R - 7 - 7 * lv
        sh.dim((a, y), (b, y), 0.0, f"{b - a:g}", size=5.6, ext=False)
        for z in (a, b):
            deep[z] = min(deep.get(z, 0.0), y)
    for z, y in deep.items():                                 # 尺寸界线：从轮廓（台阶的大径一侧）引到最外一层尺寸线外 2 mm
        r = max(d for z0, z1, d, *_ in lay if z0 - 1e-6 <= z <= z1 + 1e-6) / 2
        sh.raw_line((z, -r - 1), (z, y - 2))
    ax.set_title(NAMES[k], fontsize=8, loc="left")
    ax.set_xlim(-8, LEN + 8)                                   # 三种注法用同一比例
    ax.set_ylim(-R - 7 - 7 * (len(faces) - 2) - 5, R + 4)
# 右边：四个功能尺寸的累积公差
ax = fig.add_subplot(gs[:, 1])
keys = list(FUN)
yy = np.arange(len(keys))
cols = {"chain": "#b8860b", "base": "#7a868d", "func": "#2c6fbb"}
for j, k in enumerate(("chain", "base", "func")):
    ax.barh(yy + (j - 1) * 0.26, [res[k][f][0] for f in keys], height=0.24, color=cols[k], label=NAMES[k].split("（")[0])
    for y_, f in zip(yy, keys):
        ax.text(res[k][f][0] + 0.03, y_ + (j - 1) * 0.26, f"±{res[k][f][0]:.1f}", va="center", fontsize=6.5)
ax.set_yticks(yy)
ax.set_yticklabels([FUN[f][2] for f in keys], fontsize=7)
ax.invert_yaxis()
ax.set_xlabel(T("累积的极限偏差 ±/mm（GB/T 1804-m，极值法）", "accumulated limit ± / mm (GB/T 1804-m, worst case)"), fontsize=7)
ax.set_xlim(0, max(res[k][f][0] for k in res for f in keys) * 1.35)
ax.legend(fontsize=6.5, frameon=False, loc="upper right")
ax.tick_params(labelsize=7)
ax.yaxis.tick_right()
for s_ in ("top", "left"):
    ax.spines[s_].set_visible(False)
figure(fig, "fig3_3_1")

out(n_faces=len(faces), n_dims=len(faces) - 1,
    gear_chain=res["chain"]["gear"][0], gear_base=res["base"]["gear"][0], gear_func=res["func"]["gear"][0],
    seat_chain=res["chain"]["seat"][0], seat_base=res["base"]["seat"][0], seat_func=res["func"]["seat"][0],
    ext_chain=res["chain"]["ext"][0], ext_base=res["base"]["ext"][0], ext_func=res["func"]["ext"][0],
    tot_chain=res["chain"]["total"][0], tot_chain_rss=res["chain"]["total"][1], tot_base=res["base"]["total"][0], tot_func=res["func"]["total"][0],
    n_chain_tot=res["chain"]["total"][2], tol_25=tol(90, 115), tol_240=tol(0, 240), tol_53=tol(37, 90),
    margin_hub=S.HUB_GEAR - 53, margin_cpl=S.HUB_CPL - 68)
