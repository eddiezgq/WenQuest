"""第 138 轮 G5.1 第 10 步：机壳工艺的网页三维数据（render/process.html 读 d/proc.json）。

    python3 tools/wqls/g5_web.py <模型目录（g46 / g6）> <输出目录 d/>

内容（坐标同整机 mm）：
  cast_<part>：铸件毛坯（STL 网格）；gate_<part>：浇注系统和冒口；chill_<part>：冷铁（由凝固仿真的体素做等值面）；
  liq_<part>_<t>：t 秒时还没凝固完（固相分数 < 0.99）的区域；
  fixture：上件卧加夹具 FX-HSG-U-20；part_upper：上件成品；path_<程序>：刀具中心轨迹（切削段），已从各面的工件坐标系换回整机坐标。
网格打包成 base64 Float32（每个三角形 9 个数），与 render/stl2json.py 同一格式。
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage
from skimage import measure

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "factory" / "digital"), str(HERE)]
from cae import casting as C  # noqa: E402

TIMES = (10, 20, 30, 45, 60, 90, 120)


def pack(tris):
    return base64.b64encode(np.asarray(tris, np.float32).reshape(-1).tobytes()).decode()


def iso(mask, o, dx, step=1, smooth=0.8):
    if not mask.any():
        return np.zeros((0, 3, 3))
    f = ndimage.gaussian_filter(mask.astype(np.float32), smooth)
    f = np.pad(f, 1)
    v, fc, _, _ = measure.marching_cubes(f, 0.5, step_size=step)
    v = (v - 1) * dx + np.asarray(o) + dx / 2
    return v[fc]


def main():
    mdir, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    g6 = mdir
    P, info = {}, {}
    for part, var in (("upper", 3), ("lower", 2)):
        P[f"cast_{part}"] = pack(C.read_stl(g6 / f"blank_{part}.stl"))
        d = np.load(g6 / "sim" / f"cast_{part}_v{var}.npz")
        mat, cast, feeder = d["mat"], d["cast"], d["feeder"]
        o, dx = d["o"], float(d["dx"])
        P[f"gate_{part}"] = pack(iso(feeder, o, dx, step=2, smooth=1.0))
        P[f"chill_{part}"] = pack(iso(mat == 3, o, dx, smooth=0.5))
        met = mat == 1
        st, snaps = d["snap_t"], d["snaps"]
        tl = []
        for t in TIMES:
            j = int(np.argmin(np.abs(st - t)))
            fs = np.ones(mat.shape, np.float32)
            fs[met] = snaps[j].astype(np.float32)
            liq = met & (fs < 0.99) & cast                     # 只看铸件本身（冒口、浇道另外画成半透明）
            P[f"liq_{part}_{t}"] = pack(iso(liq, o, dx, step=2, smooth=1.0))
            tl.append(dict(t=t, frac=round(float(liq.sum()) / max(int(cast.sum()), 1), 3)))
        res = json.loads((g6 / "sim" / f"cast_{part}_v{var}.json").read_text())
        info[part] = dict(times=tl, mass_casting=res["mass_casting_kg"], mass_poured=res["mass_poured_kg"], yield_pct=res["yield_pct"],
                          t_total=res["t_solid_total_s"], gating=res["gating"])
    # 夹具、成品、刀路
    import g5_drawings as DW
    import build123d as bd
    fx = None
    for n, code, name, q, m, s in DW.fixture_model():
        fx = s if fx is None else fx + s
    bd.export_stl(fx, str(out / "_fx.stl"), tolerance=0.2)
    P["fixture"] = pack(C.read_stl(out / "_fx.stl"))
    (out / "_fx.stl").unlink()
    P["part_upper"] = pack(C.read_stl(g6 / "part_upper.stl"))
    import g5_cam as GC
    from cae import cam_sim
    paths = {}
    for num in (1202, 1205):
        title, part, seq, machine, fn = GC.PROGRAMS[num]
        segs = []
        for opx in fn():
            if opx.get("kind") == "linebar":
                continue
            n, ex, ey, p0 = (np.asarray(v, float) for v in GC.FRAMES[opx["frame"]])
            prog = dict(machine=machine, title="x", number=1, ops=[{k: v for k, v in opx.items() if k not in ("frame", "kind", "b")}])
            from cae import cam_post
            pr = cam_sim.parse(cam_post.post(prog), machine)
            for mv in pr["moves"]:
                if mv["t"] != "feed":
                    continue
                for q in (mv["a"], mv["b"]):
                    segs.append(p0 + ex * q[0] + ey * q[1] + n * q[2])
        paths[f"path_{num}"] = pack(np.asarray(segs).reshape(-1, 2, 3))   # 线段：每段 6 个数
    P.update(paths)
    P["_info"] = info
    # 网页托管单个文件 ≤ 16 MB：凝固过程的网格按件分开放
    for part in ("upper", "lower"):
        sub = {k: P.pop(k) for k in [k for k in P if k.startswith(f"liq_{part}_")]}
        (out / f"proc_{part}.json").write_text(json.dumps(sub))
    (out / "proc.json").write_text(json.dumps(P))
    for f in ("proc.json", "proc_upper.json", "proc_lower.json"):
        print(f, (out / f).stat().st_size // 1024, "KB")
    print(json.dumps(info, ensure_ascii=False)[:400])


if __name__ == "__main__":
    main()
