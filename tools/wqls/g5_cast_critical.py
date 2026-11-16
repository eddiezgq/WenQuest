"""G8.0：凝固仿真结果里，关键部位（轴承座孔、轴套座孔、电机止口等）有没有落在孤立液相区里。

    python3 tools/wqls/g5_cast_critical.py <cast_upper_vN.npz> [输出 json]

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


def main():
    src = Path(sys.argv[1])
    d = np.load(src)
    mat, cast, feeder, o, dx = d["mat"], d["cast"], d["feeder"], d["o"], float(d["dx"])
    met = mat == C.METAL
    f_pro = C.MATERIALS["HT250"]["f_pro"]
    zones = {k: zone_mask(o, dx, mat.shape, v) & cast for k, v in ZONES.items()}
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
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
