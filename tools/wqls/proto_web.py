"""第 172b 轮：WQ-LS 整机虚拟样机和说明书互动块用的数据 → factory/digital/web/public/wqls/proto.json。

全部从设计计算来，网页只读不算（挑线虚拟实验除外：网页按同一公式重算，test_wqls_spec.py 核对和这里一致）：
  - 每 1° 的曲线（3 mm 正缝、5000 r/min）：针尖、针眼上沿、梭尖、送布牙齿顶（3 / 5 / 倒缝 5）、挑线供线（三维线路）
  - 挑线机构：新（G8.1）旧（G4）两套四连杆、三种布厚的耗线、判据和 Python 算的余量 / 欠线
  - 驱动力矩各分量（G2 dyn.py，惯性部分按转速平方缩放）、各零件惯性力（g81_kin 的每 1° 质心加速度 × 实体质量）
  - 控制器固件在 Renode 里跑的工作周期（第 159 轮 sim_sew.json：转速、轴角、电流、电机力矩、负载力矩、状态、电磁铁）

    python3 tools/wqls/proto_web.py <整机目录（s3、放下、TE，含 parts.json、kin_1deg.json）> <装配检查结果 json（g81_assembly.py 的输出）>
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE)]
import g81_kin as K  # noqa: E402
import g81_takeup as TU  # noqa: E402  （导入时给 g4_takeup 换上 G8.1 的判据）

ROOT = HERE.parents[1]
OUT = ROOT / "factory" / "digital" / "web" / "public" / "wqls" / "proto.json"
GM, T, S = K.GM, K.T, K.S
r1 = lambda a, n=3: [round(float(x), n) for x in a]  # noqa: E731


def curves():
    GM.FP = K.feed_pose(3.0, False)
    fr = GM.frames(step=1, nd=None)
    Mx = {k: np.array([np.array(f["M"][k]).reshape(4, 4) for f in fr]) for k in ("hook",)}
    tip = np.array([f["tip_z"] for f in fr])
    ha = math.radians(K.HOOK_A0)
    p0 = np.array([K.HOOK_FACE, K.HOOK_R * math.cos(ha), S.ZH + K.HOOK_R * math.sin(ha), 1.0])
    hook = np.array([m @ p0 for m in Mx["hook"]])[:, :3]
    th = np.array([f["thread"] for f in fr])
    own = fr[0]["thread_own"]
    ia, ib = own.index("A"), own.index("B")
    Lp = np.sum(np.linalg.norm(np.diff(th[:, ia:ib + 1], axis=1), axis=2), axis=1)
    supply = Lp.max() - Lp
    dogs = {}
    for key, s, rev in (("s3", 3.0, False), ("s5", 5.0, False), ("r5", 5.0, True)):
        d = np.array(K.feed_pose(s, rev)["dog"])
        dogs[key] = dict(y=r1(d[:, 0]), z=r1(d[:, 1]))
    return dict(tip=r1(tip), eye_top=r1(tip + K.EYE), hook_y=r1(hook[:, 1]), hook_z=r1(hook[:, 2] - S.ZH), supply=r1(supply)), dogs


def takeup():
    old = json.loads((T.OUT / "挑线机构.json").read_text())["previous_G4"]
    new = json.loads((T.OUT / "挑线机构.json").read_text())["lk"]
    py = {}
    for name, lk in (("new", new), ("old", old)):
        L = dict(lk, A=tuple(lk["A"]), B=tuple(lk["B"]))
        py[name] = {f: {k: round(TU.takeup3d(L, t)[k], 3) for k in ("margin", "neg", "pre", "Smax")} | {"top": TU.takeup3d(L, t)["top"]}
                    for f, t in TU.FABS.items()}
        py[name]["mu"] = [round(x, 2) for x in TU.takeup3d(L, 1.5)["mu"]]
    fin = {f: int(np.argmax(TU._XN >= TU._EYE_TDC - t)) for f, t in TU.FABS.items()}
    return dict(new=new, old=old, XA=TU.XA, XE=TU.XE, XB=TU.XB, fabrics=TU.FABS, s_ref=TU.S_REF, phc=T.PHC, fin=fin,
                demand={f: r1(TU._DRAW[t], 4) for f, t in TU.FABS.items()}, margin_min=1.0, margin_max=T.MARGIN_MAX, neg_max=1.0,
                pre_max=10.0, mu_lim=[40.0, TU.MU_MAX], m_top=TU.M_TOP, python=py)


def dynamics(bdir: Path):
    import dyn
    R = dyn.Machine().run()
    pick = lambda a: r1(np.asarray(a)[::2], 4)  # noqa: E731   0.5° → 1°
    inertial = np.asarray(R["T_bar"]) + R["T_rod"] + R["T_tk"] + R["T_fd"]
    rest = np.asarray(R["T"]) - inertial
    parts = json.loads((bdir / "parts.json").read_text())["parts"]
    kin = json.loads((bdir / "kin_1deg.json").read_text())["parts"]
    force = {}
    for k in ("needle_bar", "lever", "rod", "crank", "nb_link", "rocker", "feed_bar"):
        if k in kin:
            a = np.linalg.norm(np.array(kin[k]["a"]), axis=1)
            force[k] = r1(parts[k]["mass_kg"] * a, 1)
    return dict(rpm=5000, T_inertial=pick(inertial), T_rest=pick(rest), T_total=pick(R["T"]), F_inertia=force,
                mass_g={k: round(parts[k]["mass_kg"] * 1000, 1) for k in force})


def cycle():
    d = json.loads((ROOT / "factory" / "designs" / "ctrl-ls" / "fw" / "out" / "sim_sew.json").read_text())
    out = {}
    for sc in d["scenarios"]:
        if sc["id"] not in ("cycle", "seam"):
            continue
        s = sc["series"]
        out[sc["id"]] = dict(name=sc["name"], en=sc.get("en", ""), desc=sc.get("desc", ""), solenoids=sc.get("solenoids"),
                             t=r1(s["t"], 4), rpm=r1(s["rpm"], 1), ang=r1(s["ang"], 2), iq=r1(s["iq"], 3), tm=r1(s["tm"], 4), tl=r1(s["tl"], 4),
                             state=s["state"], sol=s["sol"], pedal=s["pedal"])
    return dict(states=d["states"], scenarios=out, disclaimer=d["disclaimer"], params=d["params"])


def assembly(asm_json: Path | None):
    """G8.1 装配顺序（g81_assembly.SEQ 的路径）和检查结果（各步用的主轴转角、是否走通）"""
    import g81_assembly as A
    res = json.loads(asm_json.read_text()) if asm_json and asm_json.exists() else []
    out = []
    for i, (name, parts, path, phi, _slide, _swing, note) in enumerate(A.SEQ):
        r = res[i] if i < len(res) else {}
        out.append(dict(step=name, parts=parts, path=[[float(x) for x in w[:3]] for w in path], phi=r.get("phi", phi if phi != "auto" else 0),
                        ok=r.get("ok"), note=note))
    return out


def dyn41(bdir: Path):
    """G8.1 4.1 整机多体动力学（g81_dyn.py 的每 1° 结果）：驱动力矩三种算法、刺布挑线这一段各运动副的力和铰点位置"""
    p = bdir / "dyn_1deg.json"
    if not p.exists():
        return None
    import g81_dyn as GD
    d = json.loads(p.read_text())
    _, _, pts, _ = GD.kinematics()
    keys = ["brg_front", "brg_rear", "rod", "c_rodnb", "lever", "c_levrck", "rocker", "nb"]
    lps = [GD.GM.MK.link_pose(f, GD.GM.MK.LK0) for f in range(360)]
    eye = np.array([GD.GM.w(q["E"]) for q in lps])
    P = {k: [r1(v[:, 0], 2), r1(v[:, 1], 2)] for k, v in dict(C=pts["C"], B=pts["B"], M=pts["M"], Q=pts["Q"], E=eye).items()}
    return dict(rpm=5000, drive=r1(d["drive"], 4), power=r1(d["power"], 4), g2=r1(d["dyn"], 4), F={k: d["F"][k] for k in keys},
                names={k: d["names"][k] for k in keys}, pts=P, zu=S.ZU, summary=json.loads((K.OUT / "G8.1_动力学.json").read_text()))


def main():
    bdir = Path(sys.argv[1])
    kj = json.loads((K.OUT / "G8.1_运动学.json").read_text())
    c, dogs = curves()
    res = dict(note="WQ-LS 整机虚拟样机的数据，tools/wqls/proto_web.py 由设计计算生成，不手写", rpm=5000, curves=c, dog=dogs,
               timing=kj["timing"], catch=kj["catch"], peaks=kj["peaks"][:8], takeup=takeup(), dyn=dynamics(bdir), cycle=cycle(),
               fabric_t=TU.FABS, assembly=assembly(Path(sys.argv[2]) if len(sys.argv) > 2 else None), dyn41=dyn41(bdir))
    OUT.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")))
    print(f"{OUT.relative_to(ROOT)}  {OUT.stat().st_size / 1e3:.0f} KB")


if __name__ == "__main__":
    main()
