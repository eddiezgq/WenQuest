"""G8.0：凝固仿真结果里，关键部位（轴承座孔、轴套座孔、电机止口等）有没有落在孤立液相区里。

    python3 tools/wqls/g5_cast_critical.py <cast_upper_vN.npz> [输出 json] [--machined <machined.stl>] [--zones none]

--machined：再把所有加工面（housing.py 的 machined_faces 导出的 machined.stl / machined_lower.stl）往里 1 格的金属都当关键部位查，
按孤立区分组列出（位置、体积、碰到的加工面格数）。

g5_cast 只给出每个孤立区的外包框和最大模数；外包框大（整段机臂薄壁一起被切断）时看不出关键部位在不在里面。
这里按存下的每 2 s 快照逐个重查：快照时刻固相分数 < f_pro（共晶开始前，要补缩）的金属格，按 6 邻接连通，
不与冒口、浇注系统连通的就是孤立液相；再看关键部位的格子有没有落在里面。"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[1] / "factory" / "digital")]
from cae import casting as C  # noqa: E402

ZU = 200.0
# 关键部位（上件）：机加工的支承孔一圈（孔面往外 6 mm 的材料，即镗孔后留下的座壁）
ZONES = {
    "前轴承孔 Ø40（6203）": ("ring_x", 39.0, 51.0, 20.0 - 2.5, 26.0),
    "中间轴套孔 Ø35": ("ring_x", 162.5, 187.5, 17.5 - 2.5, 23.5),
    "后轴承孔 Ø32（6201）": ("ring_x", 375.0, 385.0, 16.0 - 2.5, 22.0),
    "电机止口 Ø52": ("ring_x", 390.0, 411.0, 26.0, 32.0),
}


def zone_mask(o, dx, shape, z):
    xs, ys, zs = (o[i] + (np.arange(shape[i]) + 0.5) * dx for i in range(3))
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    _, x0, x1, r0, r1 = z
    r = np.hypot(Y, Z - ZU)
    return (X >= x0) & (X <= x1) & (r >= r0) & (r <= r1)


def machined_mask(stl, o, dx, shape, cast):
    tris = C.read_stl(stl)
    pts = []
    for t in tris:
        a, b, c = t
        n = int(max(np.linalg.norm(b - a), np.linalg.norm(c - a), np.linalg.norm(c - b)) / (dx / 2)) + 1
        u, v = np.meshgrid(np.linspace(0, 1, n + 1), np.linspace(0, 1, n + 1))
        k = (u + v) <= 1
        pts.append(a + np.outer(u[k], b - a) + np.outer(v[k], c - a))
    P = np.concatenate(pts)
    idx = np.floor((P - o) / dx).astype(int)
    ok = np.all((idx >= 0) & (idx < np.array(shape)), axis=1)
    m = np.zeros(shape, bool)
    m[tuple(idx[ok].T)] = True
    return ndimage.binary_dilation(m, iterations=1) & cast


def main():
    args = [a for a in sys.argv[1:]]
    mach = None
    if "--machined" in args:
        i = args.index("--machined"); mach = Path(args[i + 1]); del args[i:i + 2]
    use_zones = True
    if "--zones" in args:
        i = args.index("--zones"); use_zones = args[i + 1] != "none"; del args[i:i + 2]
    sys.argv = [sys.argv[0]] + args
    src = Path(sys.argv[1])
    d = np.load(src)
    mat, cast, feeder, o, dx = d["mat"], d["cast"], d["feeder"], d["o"], float(d["dx"])
    met = mat == C.METAL
    f_pro = C.MATERIALS["HT250"]["f_pro"]
    zones = {k: zone_mask(o, dx, mat.shape, v) & cast for k, v in ZONES.items()} if use_zones else {}
    mm = machined_mask(mach, o, dx, mat.shape, cast) if mach else None
    mach_hits = {}
    out = {k: dict(cells=int(m.sum()), isolated_cells=0, first_t=None, max_vol_cm3=0.0) for k, m in zones.items()}
    fs = np.ones(mat.shape, np.float32)
    for t, s in zip(d["snap_t"], d["snaps"]):
        fs[met] = s.astype(np.float32)
        liq = met & (fs < f_pro)
        lab, n = ndimage.label(liq)
        if n == 0:
            continue
        fed = np.unique(lab[feeder & liq])
        iso = liq & ~np.isin(lab, fed)
        if mm is not None:
            hit = iso & mm
            for lid in np.unique(lab[hit]):
                reg = lab == lid
                cells = int((hit & reg).sum())
                ii = np.argwhere(hit & reg).mean(axis=0)
                cen = tuple(int(round(float(o[j] + (ii[j] + 0.5) * dx) / 5) * 5) for j in range(3))
                vol = round(float(reg.sum() * dx ** 3 / 1000), 1)
                r = mach_hits.setdefault(cen, dict(center_mm=list(cen), first_t=round(float(t), 1), cells=0, vol_cm3=0.0))
                r["cells"], r["vol_cm3"] = max(r["cells"], cells), max(r["vol_cm3"], vol)
        for k, m in zones.items():
            hit = iso & m
            if hit.any():
                ids = np.unique(lab[hit])
                vol = float(np.isin(lab, ids).sum() * dx ** 3 / 1000)
                r = out[k]
                r["isolated_cells"] = max(r["isolated_cells"], int(hit.sum()))
                r["first_t"] = r["first_t"] if r["first_t"] is not None else round(float(t), 1)
                r["max_vol_cm3"] = max(r["max_vol_cm3"], round(vol, 1))
    for k, r in out.items():
        print(f"{k}：{r['cells']} 格；孤立 {r['isolated_cells']} 格" + (f"（{r['first_t']} s 起，所在孤立区最大 {r['max_vol_cm3']} cm³）" if r["first_t"] else ""))
    if mm is not None:
        out["加工面"] = sorted(mach_hits.values(), key=lambda r: -r["cells"])
        print(f"加工面附近金属 {int(mm.sum())} 格；落在孤立液相区里的：{len(mach_hits)} 处")
        for r in out["加工面"][:20]:
            print("  ", r)
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
