"""第 138 轮 G2：上轴 LS-101 B 版的三维有限元（数字工厂 CAE：Gmsh + CalculiX），取一转里截面 I 应力最大的转角。

    python3 tools/wqls/g2_fea.py
三维模型由 FreeCAD 按 spec.UPPER_SEGS 建（加载处的轴段单独分面，便于加力），导出 STEP 后交给 cae.solve。
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital")]
import g2  # noqa: E402
import spec as S  # noqa: E402
import dyn  # noqa: E402

FC = os.environ.get("WQ_FREECAD", "/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/mm/fc/bin/freecadcmd")
OUT = ROOT / "docs" / "设计" / "WQ-LS" / "G2"
BANDS = [(S.X_TAKEUP - 5, S.X_TAKEUP + 5), (S.X_FEED_E - 5, S.X_FEED_E + 5), (S.X_BELT - 5, S.X_BELT + 5), (S.X_ROTOR - 12, S.X_ROTOR + 12)]

FC_SCRIPT = r'''
import Part, FreeCAD as App, json, sys
segs = json.loads(open(sys.argv[-2]).read())
out = sys.argv[-1]
shape = None
for x0, x1, d in segs:
    c = Part.makeCylinder(d / 2, x1 - x0, App.Vector(x0, 0, 0), App.Vector(1, 0, 0))
    shape = c if shape is None else shape.fuse(c)          # 不去分割线：每段是单独的面，便于加载
edges = []
for x in json.loads(open(sys.argv[-2] + ".steps").read()):
    cs = [e for e in shape.Edges if hasattr(e.Curve, "Radius") and abs(e.BoundBox.XMin - x) < 1e-6 and abs(e.BoundBox.XMax - x) < 1e-6]
    if cs:
        edges.append(min(cs, key=lambda e: e.Curve.Radius))   # 凹角那条（小直径）
if edges:
    shape = shape.makeFillet(0.5, edges)
shape.exportStep(out)
print("ok", len(shape.Faces))
'''


def build_step():
    segs = []
    cuts = sorted({x for b in BANDS for x in b})
    for x0, x1, d, _ in S.UPPER_SEGS:
        pts = [x0] + [c for c in cuts if x0 < c < x1] + [x1]
        segs += [(a, b, d) for a, b in zip(pts, pts[1:])]
    steps = [x1 for x0, x1, d, _ in S.UPPER_SEGS[:-1]]         # 直径变化处倒 0.5 圆角（小直径一侧的圆边）
    tmp = tempfile.mkdtemp()
    js = os.path.join(tmp, "segs.json")
    open(js, "w").write(json.dumps(segs))
    open(js + ".steps", "w").write(json.dumps(steps))
    sc = os.path.join(tmp, "build.py")
    open(sc, "w").write(FC_SCRIPT)
    stp = os.path.join(tmp, "LS-101B.step")
    r = subprocess.run([FC, "-c", f"import sys; sys.argv=['x', {js!r}, {stp!r}]; exec(open({sc!r}).read())"],
                       capture_output=True, text=True, env={**os.environ, "LANG": "C.UTF-8"}, timeout=300)
    if not os.path.exists(stp):
        raise RuntimeError(r.stdout[-800:] + r.stderr[-800:])
    return open(stp, "rb").read()


def main():
    from cae import geometry as GEO, materials as MATS, solve as SV
    R = dyn.Machine().run()
    x, xs, reac, Mb, dc = g2.shaft(R)
    j = int(np.argmin(abs(x - 11.0)))
    Mmag = np.hypot(Mb[:, j, 0], Mb[:, j, 1])
    i = int(np.argmax(Mmag))
    phi = float(R["phi"][i])
    step = build_step()
    (OUT / "LS-101B.step").write_bytes(step)
    faces, _, solid = GEO.faces(step)

    def band(x0, x1, rad):
        c = [f for f in faces if f["kind"] == "cylinder" and abs(f["bbox"][0] - x0) < 0.6 and abs(f["bbox"][3] - x1) < 0.6
             and abs((f["bbox"][4] - f["bbox"][1]) / 2 - rad) < 0.2]
        if not c:
            raise RuntimeError(f"no face {x0}-{x1} r{rad}: " + str([(f['kind'], [round(b, 1) for b in f['bbox']]) for f in faces][:40]))
        return [f["id"] for f in c]

    crank = band(-11, 11 - 0.5, 5)            # 曲柄座（到圆角起点）
    seat_f = [f["id"] for f in faces if f["kind"] == "cylinder" and abs((f["bbox"][4] - f["bbox"][1]) / 2 - 6) < 0.1 and f["bbox"][3] < 30]
    seat_r = [f["id"] for f in faces if f["kind"] == "cylinder" and abs((f["bbox"][4] - f["bbox"][1]) / 2 - 6) < 0.1 and f["bbox"][0] > 300]
    tk = band(*BANDS[0], 8)
    fe = band(*BANDS[1], 8)
    belt = band(*BANDS[2], 5)
    rotor = band(*BANDS[3], 5)
    ax = {"origin": [0, 0, 0], "dir": [1, 0, 0]}
    # 力：端视 u（水平）→ 整机 Y；v（铅垂）→ Z
    Fc, Ft = R["F_crank"][i], R["F_tk"][i]
    T_needle = float(R["T_bar"][i] + R["T_rod"][i] + R["T_needle"][i]) * 1000
    T_tk = float(R["T_tk"][i] + R["T_thread"][i]) * 1000
    T_fd = float(R["T_fd"][i] + R["T_feed"][i]) * 1000
    loads = [
        {"type": "cyl_support", "faces": seat_f, "dofs": ["radial", "axial"], "axis": ax, "band_mm": 1},
        {"type": "cyl_support", "faces": seat_r, "dofs": ["radial"], "axis": ax, "band_mm": 1},
        {"type": "cyl_support", "faces": rotor, "dofs": ["tangential"], "axis": ax},
        {"type": "force", "faces": crank, "vector_n": [0, float(Fc[0]), float(Fc[1])]},
        {"type": "force", "faces": tk, "vector_n": [0, float(Ft[0]), float(Ft[1])]},
        {"type": "force", "faces": fe, "vector_n": [0, 0, float(R["F_fe"][i])]},
        {"type": "force", "faces": belt, "vector_n": [0, 0, -S.BELT_N]},
        {"type": "force", "faces": rotor, "vector_n": [0, 0, -0.9 * 9.81]},
    ]
    for fs, T in ((crank, T_needle), (tk, T_tk), (fe, T_fd)):
        if abs(T) > 1:
            loads.append({"type": "torque", "faces": fs, "value_nmm": -T, "axis": ax})
    setup = {"material": MATS.get("45-QT"), "mesh": {"size_mm": 2.5}, "loads": loads}
    stats, surf, _ = SV.solve(step, setup)
    res = dict(phi=phi, M_I=float(Mmag[i]), stats=stats, solid=solid)
    (OUT / "有限元.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    np.savez_compressed(OUT / "有限元_表面.npz", **{k: v for k, v in surf.items()})
    plot(surf, stats, phi)
    print(json.dumps(res, ensure_ascii=False, default=float)[:1500])


def plot(surf, stats, phi):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from matplotlib import font_manager
    for f in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",):
        font_manager.fontManager.addfont(f)
    plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]
    pos, tri, vm = surf["positions"], surf["triangles"], surf["vm"]
    vmax = float(stats["vm_max_mpa"])
    fig, axs = plt.subplots(2, 1, figsize=(10, 5.8), gridspec_kw=dict(height_ratios=[1, 1.5], hspace=0.25))
    cm = plt.get_cmap("turbo")
    for a, (x0, x1), title in ((axs[0], (-12, 412), "整根轴（前视）"), (axs[1], (-12, 45), "前端放大：曲柄座 Ø10 → 前轴颈 Ø12 → 轴身 Ø16")):
        P = pos[tri]
        c = P.mean(axis=1)
        sel = (c[:, 1] < 0) & (c[:, 0] >= x0) & (c[:, 0] <= x1)          # 朝向观察者的半边
        order = np.argsort(c[sel][:, 1])[::-1]
        polys = P[sel][order][:, :, [0, 2]]
        tv = vm[tri[sel][order]].mean(axis=1)
        a.add_collection(PolyCollection(polys, facecolors=cm(np.clip(tv / vmax, 0, 1)), edgecolors="none"))
        a.set_xlim(x0, x1)
        a.set_ylim(-9, 9)
        a.set_aspect("equal")
        a.set_title(title, loc="left", fontsize=9.5)
        a.set_yticks([])
        a.set_xlabel("x / mm")
        for sp in ("left", "right", "top"):
            a.spines[sp].set_visible(False)
    mx = stats["vm_max_at"]
    axs[1].annotate(f"最大 {vmax:.0f} MPa（圆角 R0.5）", (mx[0], mx[2]), (mx[0] + 12, 8.2), fontsize=8.5,
                    arrowprops=dict(arrowstyle="->", lw=0.8))
    sm = plt.cm.ScalarMappable(cmap="turbo", norm=plt.Normalize(0, vmax))
    fig.colorbar(sm, ax=axs, shrink=0.8, label="von Mises 应力 / MPa")
    fig.suptitle(f"上轴 LS-101 B 版有限元（数字工厂 CAE：Gmsh + CalculiX），主轴 φ = {phi:.0f}°（截面 I 弯矩最大的转角）",
                 x=0.04, ha="left", fontsize=10.5)
    fig.savefig(OUT / "6_上轴有限元.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    if sys.argv[1:] == ["--plot"]:
        d = np.load(OUT / "有限元_表面.npz")
        r = json.loads((OUT / "有限元.json").read_text(encoding="utf-8"))
        plot({k: d[k] for k in d.files}, r["stats"], r["phi"])
    else:
        main()
