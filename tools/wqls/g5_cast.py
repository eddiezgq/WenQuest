"""第 138 轮 G5.1 第 1、2 步：机壳两件的铸造工艺（浇注系统、冒口、冷铁）和凝固仿真。

    python3 tools/wqls/g5_cast.py <毛坯目录> <输出目录> [upper|lower] [--dx 2.5] [--variant N]

毛坯来自 cad/blank.py（blank_<part>.stl / .json）。坐标同整机（mm）；“上”是浇注位置的上方：上件 +y（分型面 y = 0），
下件 −z（分型面在机座底面）。

工艺原则：灰铸铁薄壁件按“同时凝固”设计——内浇道开在薄壁上、分散进铁水，厚大的凸台放冷铁，利用灰铁共晶石墨化膨胀自补缩，
只在最高处放出气冒口（兼补液态收缩）。凝固仿真（factory/digital/cae/casting.py）检查孤立液相区（热节）；
有超出限度的，加冷铁或改冒口再算。
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "factory" / "digital"))
from cae import casting as C  # noqa: E402

RHO = 7.2e-6                     # HT250 kg/mm³
T_POUR = 1380.0                  # 浇注温度：薄壁灰铁件 1370–1400 ℃
SAND_MM = 40.0                   # 铸件四周的砂层（凝固时间内砂里的热影响深度约 15 mm，40 mm 够）
POCKET_LIMIT_CM3 = 0.5           # 孤立液相区体积上限：灰铁有石墨化膨胀，再小的孤立区一般不出缩孔（判据见报告）


# ---------------------------------------------------------------- 浇注系统计算（《铸造手册》灰铸铁的常用公式）
def gating(G_cast, H0_cm, P_cm, C_cm, S=1.7, mu=0.42, yield_=0.80, n_gates=4):
    """G_cast 铸件毛坯重 kg；H0 直浇道顶到内浇道的高度；P 内浇道以上的铸件高度；C 铸件在浇注位置的总高（cm）。
    浇注时间 τ = S·√G（S 按壁厚 4.5–6 mm 的灰铁件取 1.7）；平均静压头 Hp = H0 − P²/(2C)；
    阻流截面（内浇道总截面）ΣA = G / (0.31·μ·τ·√Hp)（cm²）；截面比 直:横:内 = 1.4:1.2:1（封闭式，灰铸铁常用）。"""
    G = G_cast / yield_
    tau = S * math.sqrt(G)
    Hp = H0_cm - P_cm ** 2 / (2 * C_cm)
    A_in = G / (0.31 * mu * tau * math.sqrt(Hp))
    return dict(G_pour_kg=round(G, 2), tau_s=round(tau, 1), Hp_cm=round(Hp, 1), mu=mu, S=S,
                A_ingate_cm2=round(A_in, 2), A_runner_cm2=round(1.2 * A_in, 2), A_sprue_cm2=round(1.4 * A_in, 2),
                n_ingates=n_gates, A_each_ingate_cm2=round(A_in / n_gates, 2),
                sprue_d_mm=round(2 * math.sqrt(1.4 * A_in * 100 / math.pi), 1),
                pour_rate_kg_s=round(G / tau, 2))


def box(lo, hi):
    return ("box", np.asarray(lo, float), np.asarray(hi, float))


def cyl(p0, axis, r, L):
    return ("cyl", np.asarray(p0, float), np.asarray(axis, float), float(r), float(L))


# ---------------------------------------------------------------- 两件的工艺方案（mm，整机坐标）
def layout(part, var):
    """返回 dict：up（浇注位置上方）、gate（浇注系统几何）、risers、chills、H0/P/C（cm）。var 是第几次改进"""
    if part == "upper":
        # 分型面 y = 0；横浇道在上型（y 0…25），沿机臂顶面上方 z 266…291；4 个内浇道（x 方向宽 22、y 方向厚 6）在分型面下方，
        # 从横浇道下到机臂顶面（同时凝固：铁水从薄壁进）；直浇道在立柱右边 x = 445，竖直（+y）高 200
        A_each = 1.6                                             # 由 gating() 算出约 1.3–1.6 cm²，取整到模样尺寸
        w = A_each * 100 / 6
        gates = [box((x - w / 2, -6, 254), (x + w / 2, 0, 268)) for x in (40, 115, 190, 265)]
        g = [box((20, 0, 266), (445, 25, 291))] + gates + [cyl((445, 0, 278.5), (0, 1, 0), 17.0, 200)]
        risers = [cyl((350, 112, 140), (0, 1, 0), 15, 80), cyl((-20, 60, 200), (0, 1, 0), 15, 80)]   # 出气冒口（顶出型面）
        chills = []
        if var >= 1:                                             # 第二次：立柱脚 4 个螺钉凸台、两个轴承座外侧放外冷铁
            for x_, y_ in ((322.1, -39.9), (373.9, -39.9), (322.1, 93.9), (373.9, 93.9)):
                chills.append(box((x_ - 16, y_ - 16, -30), (x_ + 16, y_ + 16, -3)))
        return dict(up=(0, 1, 0), gate=g, risers=risers, chills=chills, H0=20.0, P=12.8, C=20.6)
    # 下件：分型面在机座底面（z ≈ −66），整个铸件在下型，机座顶面朝下；横浇道在上型，沿机座前侧；
    # 内浇道在分型面上，从横浇道进机座前壁底边（薄壁）；直浇道在右端 x = 445，竖直（−z）高 150
    A_each = 1.3
    w = A_each * 100 / 6
    gates = [box((x - w / 2, -76, -66), (x + w / 2, -63, -60)) for x in (30, 130, 230, 330)]
    g = [box((10, -100, -91), (445, -76, -66))] + gates + [cyl((445, -88, -66), (0, 0, -1), 15.0, 150)]
    risers = [cyl((30, 30, -66), (0, 0, -1), 15, 70), cyl((360, 30, -66), (0, 0, -1), 15, 70)]
    chills = []
    if var >= 1:
        for x_, y_ in ((322.1, -39.9), (373.9, -39.9), (322.1, 93.9), (373.9, 93.9)):
            chills.append(box((x_ - 14, y_ - 14, -60), (x_ + 14, y_ + 14, -27)))
    return dict(up=(0, 0, -1), gate=g, risers=risers, chills=chills, H0=15.0, P=0.0, C=7.0)


def paint(grid_shape, o, dx, shapes):
    """把几何（box / cyl）画进布尔网格"""
    nx, ny, nz = grid_shape
    X = o[0] + (np.arange(nx) + 0.5) * dx
    Y = o[1] + (np.arange(ny) + 0.5) * dx
    Z = o[2] + (np.arange(nz) + 0.5) * dx
    out = np.zeros(grid_shape, bool)
    for s in shapes:
        if s[0] == "box":
            lo, hi = s[1], s[2]
            out[np.ix_((X >= lo[0]) & (X <= hi[0]), (Y >= lo[1]) & (Y <= hi[1]), (Z >= lo[2]) & (Z <= hi[2]))] = True
        else:
            p0, ax, r, L = s[1], s[2] / np.linalg.norm(s[2]), s[3], s[4]
            lo = np.minimum(p0, p0 + ax * L) - r
            hi = np.maximum(p0, p0 + ax * L) + r
            ii, jj, kk = [np.nonzero((A >= l - dx) & (A <= h + dx))[0] for A, l, h in zip((X, Y, Z), lo, hi)]
            if not len(ii) or not len(jj) or not len(kk):
                continue
            PX, PY, PZ = np.meshgrid(X[ii], Y[jj], Z[kk], indexing="ij")
            d = np.stack([PX - p0[0], PY - p0[1], PZ - p0[2]], -1)
            t = d @ ax
            rr = np.linalg.norm(d - t[..., None] * ax, axis=-1)
            sel = (t >= 0) & (t <= L) & (rr <= r)
            sub = out[np.ix_(ii, jj, kk)]
            sub |= sel
            out[np.ix_(ii, jj, kk)] = sub
    return out


def bounds(shapes):
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    for s in shapes:
        if s[0] == "box":
            lo, hi = np.minimum(lo, s[1]), np.maximum(hi, s[2])
        else:
            a, b = s[1], s[1] + s[2] / np.linalg.norm(s[2]) * s[4]
            lo, hi = np.minimum(lo, np.minimum(a, b) - s[3]), np.maximum(hi, np.maximum(a, b) + s[3])
    return lo, hi


def run(blank_dir: Path, out: Path, part: str, dx=2.5, var=0):
    out.mkdir(parents=True, exist_ok=True)
    info = json.loads((blank_dir / f"blank_{part}.json").read_text())
    tris = C.read_stl(blank_dir / f"blank_{part}.stl")
    L = layout(part, var)
    extra = L["gate"] + L["risers"] + L["chills"]
    lo = np.minimum(tris.min((0, 1)), bounds(extra)[0]) - SAND_MM
    hi = np.maximum(tris.max((0, 1)), bounds(extra)[1]) + SAND_MM
    o = np.floor(lo / dx) * dx
    shape = tuple(int(v) for v in np.ceil((hi - o) / dx))
    t0 = time.time()
    cast = C.voxelize(tris, o, dx, shape)
    gate = paint(shape, o, dx, L["gate"])
    rise = paint(shape, o, dx, L["risers"])
    chill = paint(shape, o, dx, L["chills"]) & ~cast
    mat = np.full(shape, C.SAND, np.int8)
    mat[chill] = C.CHILL
    mat[cast | gate | rise] = C.METAL
    feeder = (gate | rise) & ~cast
    vc = dx ** 3
    m_cast = float(cast.sum() * vc * RHO)
    m_pour = float((cast | gate | rise).sum() * vc * RHO)
    g = gating(info["mass_blank_kg"], L["H0"], L["P"], L["C"])
    print(part, "体素", shape, f"{np.prod(shape) / 1e6:.1f} M 格，铸件 {m_cast:.2f} kg，浇注 {m_pour:.2f} kg", f"{time.time() - t0:.0f} s", flush=True)

    def prog(t, left):
        if int(t) % 50 < 5:
            print(f"  t = {t:6.1f} s  未凝固 {left * 100:5.1f} %", flush=True)
    t0 = time.time()
    r = C.solidify(C.Mold(mat=mat, dx=dx / 1000, feeder=feeder, t_pour=T_POUR), snap_every=5.0, progress=prog)
    _, _, B = C.plate_test(20.0, 2.0)
    tc = np.where(cast, r["t_sol"], np.nan)
    M = C.modulus(tc, B)
    pk = []
    for p in r["pockets"]:
        cen = [round(float(o[i] + (p["center"][i] + 0.5) * dx), 1) for i in range(3)]
        box_mm = [[round(float(o[i] + a * dx), 1), round(float(o[i] + b * dx), 1)] for i, (a, b) in enumerate(p["box"])]
        sl = tuple(slice(a, b) for a, b in p["box"])
        incast = bool(cast[sl].any())
        pk.append(dict(volume_cm3=p["volume_cm3"], center_mm=cen, box_mm=box_mm, t_isolated_s=round(p["t_iso"], 1),
                       t_end_s=p["t_end"] and round(p["t_end"], 1), in_casting=incast,
                       modulus_cm=round(float(np.nanmax(M[sl])), 2) if incast and np.isfinite(M[sl]).any() else None))
    bad = [p for p in pk if p["in_casting"] and p["volume_cm3"] >= POCKET_LIMIT_CM3]
    res = dict(part=part, variant=var, dx_mm=dx, grid=list(shape), origin_mm=[float(v) for v in o], t_pour_c=T_POUR,
               mass_casting_kg=round(m_cast, 2), mass_poured_kg=round(m_pour, 2), yield_pct=round(100 * m_cast / m_pour, 1),
               gating=g, layout={k: (v if not isinstance(v, list) else len(v)) for k, v in L.items()},
               chvorinov_B_s_cm2=round(B, 1), t_solid_total_s=round(float(np.nanmax(tc)), 1),
               modulus_max_cm=round(float(np.nanmax(M)), 2), steps=r["steps"], dt_s=round(r["dt"], 4),
               seconds=round(time.time() - t0), pockets=pk[:30], pockets_over_limit=bad, pocket_limit_cm3=POCKET_LIMIT_CM3)
    (out / f"cast_{part}_v{var}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    np.savez_compressed(out / f"cast_{part}_v{var}.npz", mat=mat, cast=cast, feeder=feeder, t_sol=r["t_sol"], o=o, dx=dx,
                        snap_t=np.array([s[0] for s in r["snaps"]]), snaps=np.stack([s[1] for s in r["snaps"]]))
    print(json.dumps({k: res[k] for k in ("mass_casting_kg", "mass_poured_kg", "yield_pct", "t_solid_total_s", "modulus_max_cm", "seconds")},
                     ensure_ascii=False))
    print("孤立液相区（前 8 个）：")
    for p in pk[:8]:
        print("  ", p)
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    dx = float(a[a.index("--dx") + 1]) if "--dx" in a else 2.5
    var = int(a[a.index("--variant") + 1]) if "--variant" in a else 0
    pos = [x for x in a if not x.startswith("--") and not x.replace(".", "").isdigit()]
    parts = [pos[2]] if len(pos) > 2 else ["upper", "lower"]
    for p in parts:
        run(Path(pos[0]), Path(pos[1]), p, dx, var)
