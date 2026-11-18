"""第 172b 轮第二批：说明书互动块 3、4、5、9、10、12、13 用的数据 → factory/digital/web/public/wqls/labs.json、fea.bin、cast.bin。

全部从设计计算结果来，网页只读、只做线性组合（平衡率、转速），test_wqls_spec.py 核对和设计文件一致：
  mech    机构简图：曲柄半径、连杆长（G2 dyn.py 的 S.SEW），旋梭半径和梭尖起始角（g81_kin）
  torque  G2 dyn.py（现在的模型：G8.1 第三步换了挑线机构，峰值和 G2 计算书 11-15 那次差约 2 %，两个数都给）5000 r/min 一转（每 1°）各项力矩；整机振动力、曲柄销力在平衡率 k = 0 时的值和 k 每加 1 的增量（两者对 k 是线性的）
  fea     G2 上轴有限元表面（G2/有限元_表面.npz）→ fea.bin：顶点 Float32×3、三角形 Uint16×3、等效应力 Float32、位移 Float32×3
  cast    G5 凝固仿真（上件、下件）每个铸件 / 冒口体素（2×2×2 合并成 5 mm）的凝固时刻 → cast.bin：Int16×3 格点 + Uint16 0.1 s
  nc      G5 数控程序逐段（cae.cam_sim 读，和 G5 的仿真核对同一个读法）：快移 / 切削、刀号、分度 B、加工时间
  bom     G7 物料清单 8 个变型
  clash   G8.1 运动干涉：每一对零件一转里的最近距离和那个角度
  inertia G8.1 每 1° 运动学（kin_1deg.json）：各运动件质量、质心（静止位置）和加速度 → 惯性力 −m·a

    python3 tools/wqls/labs_web.py <整机目录（s3、放下、TE，含 parts.json、kin_1deg.json）> <凝固仿真目录（cast_upper_v12.npz、cast_lower_v8.npz）>
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital")]
SRC = ROOT / "docs" / "设计" / "WQ-LS"
OUT = ROOT / "factory" / "digital" / "web" / "public" / "wqls"
r1 = lambda a, n=3: [round(float(x), n) for x in a]  # noqa: E731


def mech():
    import dyn
    import g81_kin as K
    m = dyn.Machine()
    return dict(r=m.p["r"], l=m.p["l"], hook_r=K.HOOK_R, hook_a0=K.HOOK_A0)


def torque():
    import dyn
    m0, m1 = dyn.Machine(k=0.0), dyn.Machine(k=1.0)
    R0, R1 = m0.run(), m1.run()
    pick = lambda a, n=4: r1(np.asarray(a)[::2], n)  # noqa: E731   0.5° → 1°
    keys = ("T_bar", "T_rod", "T_tk", "T_fd", "T_grav", "T_needle", "T_thread", "T_feed", "T_fric", "T")
    sh0, dsh = R0["F_shake"], R1["F_shake"] - R0["F_shake"]
    cr0, dcr = R0["F_crank"], R1["F_crank"] - R0["F_crank"]
    g2 = json.loads((SRC / "G2" / "结果.json").read_text(encoding="utf-8"))
    return dict(rpm=R0["n"], inertial=["T_bar", "T_rod", "T_tk", "T_fd"], **{k: pick(R0[k]) for k in keys},
                shake0=[pick(sh0[:, 0], 2), pick(sh0[:, 1], 2)], dshake=[pick(dsh[:, 0], 2), pick(dsh[:, 1], 2)],
                crank0=[pick(cr0[:, 0], 2), pick(cr0[:, 1], 2)], dcrank=[pick(dcr[:, 0], 2), pick(dcr[:, 1], 2)],
                k_design=g2["k_best"], g2_doc=dict(T_max=round(g2["torque"]["T_max"], 3), T_min=round(g2["torque"]["T_min"], 3)), balance=[dict(k=r["k"], Fmax=round(r["Fmax"], 1), Fcrank=round(r["Fcrank"], 1)) for r in g2["balance"]["rows"]],
                P_mean=round(float(np.mean(R0["T"])) * R0["w"], 1))


def fea():
    z = np.load(SRC / "G2" / "有限元_表面.npz")
    j = json.loads((SRC / "G2" / "有限元.json").read_text(encoding="utf-8"))
    pos, tri, vm, u = (z[k] for k in ("positions", "triangles", "vm", "u"))
    assert len(pos) < 65536
    buf = (pos.astype("<f4").tobytes() + tri.astype("<u2").tobytes() + vm.astype("<f4").tobytes() + u.astype("<f4").tobytes())
    (OUT / "fea.bin").write_bytes(buf)
    s = j["stats"]
    i = int(np.argmax(vm))
    return dict(nv=len(pos), nt=len(tri), phi=j["phi"], M_I=round(j["M_I"], 1), vm_surf=round(float(vm.max()), 3), vm_surf_at=r1(pos[i], 2),
                vm_max=s["vm_max_mpa"], vm_max_at=s["vm_max_at"], vm_peak=s["vm_peak_all_mpa"], vm_peak_at=s["vm_peak_all_at"], u_max=round(float(np.linalg.norm(u, axis=1).max()), 5), u_max_report=s["u_max_mm"],
                strength=s["strength_mpa"], sf=s["safety_factor"], nodes=s["nodes"], elements=s["elements"], mesh=s["mesh_size_mm"])


def cast(cdir: Path):
    out, buf, n0 = {}, bytearray(), 0
    for part, zh in (("upper", "上件"), ("lower", "下件")):
        js = json.loads((SRC / "G5" / f"凝固仿真_{zh}.json").read_text(encoding="utf-8"))
        z = np.load(cdir / f"cast_{part}_v{js['variant']}.npz")
        keep = (z["cast"] | z["feeder"]) & np.isfinite(z["t_sol"])
        tmax = float(np.nanmax(np.where(z["cast"], z["t_sol"], np.nan)))
        assert abs(tmax - js["t_solid_total_s"]) < 0.06, (part, tmax, js["t_solid_total_s"])
        sh = [s - s % 2 for s in keep.shape]
        k2 = keep[:sh[0], :sh[1], :sh[2]].reshape(sh[0] // 2, 2, sh[1] // 2, 2, sh[2] // 2, 2)
        t2 = np.where(keep, z["t_sol"], -1.0)[:sh[0], :sh[1], :sh[2]].reshape(k2.shape).max(axis=(1, 3, 5))   # 2×2×2 里最晚凝固的
        f2 = (z["feeder"] & ~z["cast"])[:sh[0], :sh[1], :sh[2]].reshape(k2.shape).any(axis=(1, 3, 5))
        idx = np.argwhere(t2 >= 0)
        tt = t2[t2 >= 0]
        fl = f2[t2 >= 0]
        dx = float(z["dx"]) * 2
        c = (np.asarray(z["o"]) + (idx + 0.5) * dx).round().astype("<i2")
        t16 = np.clip(np.round(tt * 10), 0, 65000).astype("<u2") | 0
        buf += c.tobytes() + t16.tobytes() + fl.astype("u1").tobytes()
        out[part] = dict(off=n0, n=len(idx), dx=dx, t_end=round(tmax, 1), t_end_all=round(float(tt.max()), 1), mass_kg=js["mass_casting_kg"],
                         poured_kg=js["mass_poured_kg"], yield_pct=js["yield_pct"], pour_c=js["t_pour_c"], variant=js["variant"],
                         risers=js["layout"].get("risers"), chills=js["layout"].get("chills"))
        n0 += len(idx)
    (OUT / "cast.bin").write_bytes(bytes(buf))
    return out


def nc():
    from cae import cam_sim
    progs = {}
    for f in sorted((SRC / "G5" / "数控程序").glob("O*.nc")):
        text = f.read_text(encoding="utf-8")
        mach = "HMC-01" if "卧式" in text[:400] else "VMC-01"
        p = cam_sim.parse(text, mach)
        title = re.search(r"^O\d+ \((.*)\)", text, flags=re.M)
        tools = {}
        for m in re.finditer(r"^\(T(\d+) (.+?) D([\d.]+)\)", text, flags=re.M):
            tools[int(m.group(1))] = dict(name=m.group(2), d=float(m.group(3)))
        mv, tsum = [], 0.0
        for m in p["moves"]:
            dt = cam_sim.move_time(m, mach, False)
            tsum += dt
            mv.append([0 if m["t"] == "rapid" else 1, m["tool"] or 0, int(m.get("B") or 0), *r1(m["b"], 2), round(tsum, 2), m["line"]])
        start = r1(p["moves"][0]["a"], 2) if p["moves"] else [0, 0, 0]
        progs[f.stem] = dict(title=title.group(1) if title else f.stem, machine=mach, tools=tools, start=start, moves=mv, t_total=round(tsum, 1),
                             lines=text.count("\n"), b=sorted({x[2] for x in mv}), src=text.splitlines())
    return progs


def bom():
    b = json.loads((SRC / "G7" / "物料清单.json").read_text(encoding="utf-8"))["variants"]
    return {v: dict(price=d["price"], options=d["options"], lines=[dict(code=x["code"], qty=x["qty"], parts=x["parts"], kind=x["kind"], name=x["name"],
                                                                         mass_g=x.get("mass_g")) for x in d["lines"]]) for v, d in b.items()}


def clash():
    d = json.loads((SRC / "G8" / "G8.1_运动干涉.json").read_text(encoding="utf-8"))
    rows = sorted(([*p[0].split(" | "), round(p[1], 2), p[2], p[3]] for p in d["pairs"]), key=lambda r: r[2])
    return dict(pairs=rows, too_close=[[c, *p[0].split(" | "), p[1], p[2]] for c, p in d["too_close"]])


def inertia(bdir: Path):
    parts = json.loads((bdir / "parts.json").read_text())["parts"]
    kin = json.loads((bdir / "kin_1deg.json").read_text())
    out = {}
    for k, v in kin["parts"].items():
        if k not in parts or not parts[k].get("valid", True):
            continue
        a = np.array(v["a"])
        F = parts[k]["mass_kg"] * np.linalg.norm(a, axis=1)
        if F.max() < 5:                                        # 不到 5 N 的不画（转动件质心在轴上，基本是 0）
            continue
        out[k] = dict(m_g=round(parts[k]["mass_kg"] * 1000, 1), com=r1(parts[k]["com"], 2), a=[r1(x, 0) for x in a[::2]], Fmax=round(float(F.max()), 1),
                      at=int(np.argmax(F)))
    return dict(rpm=kin["rpm"], step=2, parts=out)


def main():
    bdir, cdir = Path(sys.argv[1]), Path(sys.argv[2])
    L = dict(note="WQ-LS 设计说明书互动块的数据，tools/wqls/labs_web.py 由设计计算结果生成，不手写",
             mech=mech(), torque=torque(), fea=fea(), cast=cast(cdir), nc=nc(), bom=bom(), clash=clash(), inertia=inertia(bdir))
    (OUT / "labs.json").write_text(json.dumps(L, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for f in ("labs.json", "fea.bin", "cast.bin"):
        print(f, round((OUT / f).stat().st_size / 1024), "KB")
    print({p: (v["n"], v["t_end"]) for p, v in L["cast"].items()}, {k: v["t_total"] for k, v in L["nc"].items()}, len(L["inertia"]["parts"]))


if __name__ == "__main__":
    main()
