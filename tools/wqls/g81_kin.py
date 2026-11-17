"""G8.1 第三步 运动学：从整机三维的运动（每 1°）量出时序、钩线、刺布与送布、挑线和各运动件的速度、加速度。

    python3 tools/wqls/g81_kin.py <零件目录>     → docs/设计/WQ-LS/G8/G8.1_运动学.json、G8.1_时序图.png、G8.1_惯性力.png
                                                 <零件目录>/kin_1deg.json（每个运动件每 1° 的质心速度、加速度、角速度、角加速度，给第四步动力学）

<零件目录> 是 cad/mech.py 建好的整机（要 parts.json：每个零件 φ = 0 时的质量、质心）。
零件的变换用 g4_mech.frames(step=1)（和三维动画、干涉检查同一套）；送布组换成每 1° 重算的位置（g4_feed.kin）。
点的取法：针尖、针眼上沿（针尖上 2.0，DB×1 Nm 90）、挑线杆线眼、梭尖（cad/hook.py：r 13.5，φ = 0 时方向角 142.2°，梭面 x 0.53）、
送布牙齿顶（g4_feed 的 dog 点）。合格标准见 G8.1 方案第三节。
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "services" / "gateway"), str(HERE)]
os.environ.setdefault("WQ_FEED", "s3")
import g4_feed as GF  # noqa: E402
import g4_mech as GM  # noqa: E402
import g4_takeup as T  # noqa: E402
import spec as S  # noqa: E402
from app.sewcore.kit import Mech  # noqa: E402

# 布厚：任务书面料“轻薄到中厚：衬里、衬衫、棉布、轻牛仔（两到四层）”。衬里、棉布取 sewcore 的 0.4、1.5；轻牛仔四层按每层约 0.75 取 3.0
# （sewcore 的 denim 4.0 是厚牛仔，超出任务书，只作参考不判）
FT = dict(lining=0.4, cotton=1.5, light_denim_x4=3.0)
FT_REF = dict(denim=4.0)
OUT = ROOT / "docs" / "设计" / "WQ-LS" / "G8"
DEG = math.pi / 180
PRESSER = ("presser_bar", "presser_collar", "presser_foot", "lift_bracket")
N_RPM = S.SEW["n"]
W = N_RPM * 2 * math.pi / 60                      # 上轴角速度 rad/s
DT = DEG / W                                      # 1° 的时间
EYE = 2.0                                         # 针眼上沿到针尖（sewcore Mech.EYE）
R_NEEDLE = 0.45                                   # Nm 90
HOOK_R, HOOK_A0, HOOK_FACE = 13.5, 142.2, 0.53    # cad/hook.py
FEED = json.loads((ROOT / "docs" / "设计" / "WQ-LS" / "G4" / "送布机构.json").read_text())
TKL = json.loads((ROOT / "docs" / "设计" / "WQ-LS" / "G4" / "挑线机构.json").read_text())["lk"]
G1 = json.loads((ROOT / "docs" / "设计" / "WQ-LS" / "G1" / "校核.json").read_text())["timing"]


def feed_pose(s, rev):
    """每 1° 的送布组位置（和 g4_feed.main 给三维的 poses 同样的键）"""
    a = math.radians(next(x["alpha_deg"] for x in FEED["settings"] if x["s"] == s and x["reverse"] == rev))
    GF.PHI = np.arange(360) * 1.0
    k = GF.kin(FEED["params"], a, full=True)
    P = {n: [list(map(float, v)) for v in k[n]] for n in ("E", "P", "C", "T", "D", "K", "EL", "dog")}
    P.update(beta=[float(v) for v in k["beta"]], gam=[float(v) for v in k["gam"]])
    return P


def cross(phi, y, level, up):
    """y 穿过 level 的角度（up：往上穿），线性插值；一转可能有多次，全给"""
    out = []
    for i in range(len(phi)):
        j = (i + 1) % len(phi)
        a, b = y[i] - level, y[j] - level
        if (a < 0 <= b) if up else (a >= 0 > b):
            out.append((phi[i] + (0 - a) / (b - a)) % 360)
    return out


def rotvec(Rm):
    c = max(-1.0, min(1.0, (np.trace(Rm) - 1) / 2))
    th = math.acos(c)
    if th < 1e-12:
        return np.zeros(3)
    v = np.array([Rm[2, 1] - Rm[1, 2], Rm[0, 2] - Rm[2, 0], Rm[1, 0] - Rm[0, 1]])
    return v / (2 * math.sin(th)) * th


def main():
    d = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/wqls_mech")
    parts = json.loads((d / "parts.json").read_text())["parts"]
    GM.FP = feed_pose(3.0, False)
    fr = GM.frames(step=1, nd=None)
    phi = np.array([f["phi"] for f in fr], float)
    Mx = {k: np.array([np.array(f["M"][k]).reshape(4, 4) for f in fr]) for k in fr[0]["M"]}

    def track(k, p0):
        p = np.r_[np.asarray(p0, float), 1.0]
        return np.array([m @ p for m in Mx[k]])[:, :3]

    # ---------- 1 时序（3 mm 正缝、布厚 1.5） ----------
    tip = np.array([f["tip_z"] for f in fr])
    eye_top = tip + EYE
    ha = math.radians(HOOK_A0)
    hook = track("hook", (HOOK_FACE, HOOK_R * math.cos(ha), S.ZH + HOOK_R * math.sin(ha)))
    dog = np.array(GM.FP["dog"])                       # (y, z)，z 是牙齿顶高出针板
    th = np.array([f["thread"] for f in fr])           # 面线折线
    own = fr[0]["thread_own"]
    ia, ib = own.index("A"), own.index("B")
    Lp = np.sum(np.linalg.norm(np.diff(th[:, ia:ib + 1], axis=1), axis=2), axis=1)     # 过线点 A → 线眼 → B 的线长（三维）
    supply = Lp.max() - Lp                               # 挑线杆放出的线（0 = 挑线杆最高、收线最紧）
    Lp2 = np.sum(np.linalg.norm(np.diff(th[:, ia:ib + 1, 1:], axis=1), axis=2), axis=1)  # 只看端视（G4 综合挑线机构时的算法）
    supply2 = Lp2.max() - Lp2
    up_hook = [a for a in cross(phi, hook[:, 1], 0.0, False) if hook[int(round(a)) % 360, 2] > S.ZH]   # 梭尖在上半圈经过针
    up_hook += [a for a in cross(phi, hook[:, 1], 0.0, True) if hook[int(round(a)) % 360, 2] > S.ZH]
    fc = min(up_hook, key=lambda a: abs(a - 206))
    i_fc = int(round(fc)) % 360

    def at(arr, a):
        return float(np.interp(a, np.r_[phi, 360], np.r_[arr, arr[0]]))
    t_fab = FT["cotton"]
    timing = dict(
        needle_tdc=float(phi[np.argmax(tip)]), needle_bdc=float(phi[np.argmin(tip)]),
        tip_in_plate=cross(phi, tip, 0.0, False)[0], tip_out_plate=cross(phi, tip, 0.0, True)[0],
        eye_in_fabric=cross(phi, eye_top, t_fab, False)[0],
        hook_catch=round(fc, 2),
        takeup_top=float(phi[np.argmin(supply)]), takeup_bottom=float(phi[np.argmax(supply)]),
        dog_rise=cross(phi, dog[:, 1], 0.0, True)[0], dog_drop=cross(phi, dog[:, 1], 0.0, False)[0],
    )
    # 对照：设计值。钩线、针眼入布取 G1；送布牙、挑线杆在 G4 换了机构（G4.6 连杆送布、G4 挑线杆共用曲柄销），取 G4 的机构值，G1 理想值并列
    f3 = next(x["check"] for x in FEED["settings"] if x["s"] == 3.0 and not x["reverse"])
    tk_top = T.Mech2(r=S.SEW["r"], l=S.SEW["l"], lk=TKL).takeup(t=t_fab, s=3.0, phc=206, lk=TKL)["top"]
    ref = dict(hook_catch=(G1["fc"], "G1", G1["fc"]), eye_in_fabric=(G1["fin"], "G1", G1["fin"]),
               dog_rise=(f3["rise"], "G4.6", G1["rise"]), dog_drop=(f3["drop"], "G4.6", G1["drop"]), takeup_top=(tk_top, "G4", G1["takeup_top"]))
    timing_cmp = {k: dict(three_d=round(timing[k], 2), design=round(v, 2), source=src, diff=round(timing[k] - v, 2), g1_ideal=round(g, 2))
                  for k, (v, src, g) in ref.items()}

    # ---------- 2 钩线 ----------
    rise = at(tip, fc) - tip.min()
    above = at(hook[:, 2], fc) - at(eye_top, fc)
    gap = HOOK_FACE - R_NEEDLE                            # 梭面到针表面（针不沿 x 动，梭尖在梭面上）
    catch = dict(angle=round(fc, 2), needle_rise=round(rise, 3), point_gap=round(gap, 3), point_above_eye=round(above, 3),
                 ok=dict(rise=abs(rise - 2.0) <= 0.3, gap=0.05 <= gap <= 0.10, above=0.5 <= above <= 1.5))

    # ---------- 3 刺布与送布：牙齿在针板上面（真正推布）的时候针尖要在布面上面 ----------
    feed = []
    for rev in (False, True):
        for s in S.STITCH_RANGE:
            P = GM.FP if (s == 3.0 and not rev) else feed_pose(s, rev)
            dg = np.array(P["dog"])
            dy = np.roll(dg[:, 0], -1) - dg[:, 0]
            on = (dg[:, 1] > 0) & (np.roll(dg[:, 1], -1) > 0)
            row = dict(s=s, reverse=rev, net=round(float(np.sum(dy[on])), 3))
            for fab, t in FT.items():
                infab = (tip <= t) | (np.roll(tip, -1) <= t)
                row[f"drag_{fab}"] = round(float(np.sum(np.abs(dy[on & infab]))), 4)
            for fab, t in FT_REF.items():
                infab = (tip <= t) | (np.roll(tip, -1) <= t)
                row[f"ref_drag_{fab}"] = round(float(np.sum(np.abs(dy[on & infab]))), 4)
            row["ok"] = all(row[f"drag_{f}"] <= 0.05 for f in FT)
            feed.append(row)

    # ---------- 4 挑线：三维线路量出的挑线量（供线），对 sewcore 的耗线模型 ----------
    m = Mech(r=S.SEW["r"], l=S.SEW["l"])
    takeup = []
    for path, sup in (("3d", supply), ("end_view", supply2)):
      for fab, t in FT.items():
        for s in S.STITCH_RANGE:
            top = int(np.argmin(sup))
            phc = int(round(fc))
            c = s + t
            D = np.array([c if i < top else m.demand(i, t, s, phc) for i in range(360)])
            sl = sup - D
            fin = int(np.argmax(eye_top <= t)) if np.any(eye_top <= t) else 180
            margin = float(min(sl[i] for i in range(phc, min(359, phc + 135) + 1)))
            neg = float(max([0.0] + [-sl[i] for i in range(fin, phc)]))
            takeup.append(dict(path=path, fabric=fab, t=t, s=s, takeup=round(float(sup.max()), 2), demand_max=round(float(D.max()), 2),
                               consumption=round(c, 2), margin=round(margin, 2), shortfall=round(neg, 2),
                               ok=bool(sup.max() >= D.max() and margin >= 1.0 and neg <= 1.0)))

    # ---------- 5 速度、加速度（质心，有限差分；针杆和 sewcore 精确式对照） ----------
    kin, peaks = {}, []
    for k in Mx:
        if k not in parts:
            continue
        p = track(k, parts[k]["com"]) / 1000.0                   # m
        v = (np.roll(p, -1, 0) - np.roll(p, 1, 0)) / (2 * DT)
        a = (np.roll(p, -1, 0) - 2 * p + np.roll(p, 1, 0)) / DT ** 2
        Rm = Mx[k][:, :3, :3]
        om = np.array([rotvec(Rm[(i + 1) % 360] @ Rm[i - 1].T) / (2 * DT) for i in range(360)])
        al = (np.roll(om, -1, 0) - np.roll(om, 1, 0)) / (2 * DT)
        vm, am, wm, alm = (np.linalg.norm(x, axis=1) for x in (v, a, om, al))
        if am.max() < 1e-6 and wm.max() < 1e-6:
            continue                                                  # 这一状态不动（剪线件平时不动）
        if k in PRESSER:
            continue      # 压脚组：没有布时被送布牙顶起 max(0, 牙高)，速度在牙出针板时跳变，加速度是假尖峰；第四步按弹簧接触算
        kin[k] = dict(v=np.round(v, 4).tolist(), a=np.round(a, 2).tolist(), w=np.round(om, 3).tolist(), alpha=np.round(al, 1).tolist())
        peaks.append(dict(part=k, mass_kg=parts[k]["mass_kg"], v_max=round(float(vm.max()), 3), a_max=round(float(am.max()), 1),
                          a_at=int(phi[np.argmax(am)]), w_max=round(float(wm.max()), 1), alpha_max=round(float(alm.max()), 0),
                          F_inertia_max=round(float(parts[k]["mass_kg"] * am.max()), 1)))
    peaks.sort(key=lambda r: -r["F_inertia_max"])
    nb = np.array(kin["needle_bar"]["a"])[:, 2]
    ref = np.array([-m.acc(f, N_RPM) for f in phi])                 # sewcore：向下为正的针杆位移 → 加速度取反
    nb_err = float(np.max(np.abs(nb - ref)) / np.max(np.abs(ref)))

    res = dict(rpm=N_RPM, step_deg=1, fabric_t_timing=t_fab, timing=timing, timing_vs_G1=timing_cmp, catch=catch, feed=feed,
               takeup=takeup, peaks=peaks, needle_bar_vs_exact=dict(rel_err=round(nb_err, 5), a_max_exact=round(float(np.abs(ref).max()), 1)),
               all_ok=bool(all(catch["ok"].values()) and all(r["ok"] for r in feed) and all(r["ok"] for r in takeup if r["path"] == "3d")
                           and all(abs(x["diff"]) <= 1.0 for x in timing_cmp.values()) and nb_err <= 0.01))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "G8.1_运动学.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    (d / "kin_1deg.json").write_text(json.dumps(dict(rpm=N_RPM, phi=phi.tolist(), parts=kin)))
    figs(phi, tip, eye_top, hook, dog, supply, timing, res)
    print(json.dumps({k: res[k] for k in ("timing", "timing_vs_G1", "catch", "needle_bar_vs_exact", "all_ok")}, ensure_ascii=False, indent=1, default=lambda o: o.item()))
    for r in feed:
        print(r)
    for r in takeup:
        print(r)
    for r in peaks[:12]:
        print(r)


def figs(phi, tip, eye_top, hook, dog, supply, tm, res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for f_ in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",):
        if Path(f_).exists():
            font_manager.fontManager.addfont(f_)
    plt.rcParams.update({"font.family": ["Noto Sans CJK JP", "DejaVu Sans"], "font.size": 9,
                         "axes.spines.top": False, "axes.spines.right": False})
    INK, MUTE, C1, C2, C3, C4 = "#1d2733", "#7a8794", "#1f5fa8", "#c8102e", "#2e9e6a", "#b8860b"
    fig, ax = plt.subplots(4, 1, figsize=(9, 8.5), sharex=True)
    ax[0].plot(phi, tip, color=C1, lw=1.6, label="针尖 needle tip")
    ax[0].plot(phi, eye_top, color=C1, lw=1, ls="--", label="针眼上沿 eye top")
    ax[0].axhline(0, color=MUTE, lw=0.8)
    ax[0].axhline(FT["cotton"], color=MUTE, lw=0.6, ls=":")
    ax[0].set_ylabel("高出针板 mm")
    ax[1].plot(phi, hook[:, 2], color=C2, lw=1.6, label="梭尖高度 hook point z")
    ax[1].plot(phi, eye_top, color=C1, lw=1, ls="--", label="针眼上沿")
    ax[1].set_ylim(-16, 6)
    ax[1].set_ylabel("mm")
    ax[2].plot(phi, supply, color=C3, lw=1.6, label="挑线杆放出的线 take-up supply")
    ax[2].set_ylabel("mm")
    ax[3].plot(phi, dog[:, 1], color=C4, lw=1.6, label="牙齿顶高出针板 dog height")
    ax3 = ax[3].twinx()
    ax3.plot(phi, dog[:, 0] - dog[:, 0].mean(), color=C4, lw=1, ls="--", label="牙前后 dog y")
    ax3.spines["top"].set_visible(False)
    ax3.set_ylabel("前后 mm", color=MUTE)
    ax[3].axhline(0, color=MUTE, lw=0.8)
    ax[3].set_ylabel("mm")
    ax[3].set_xlabel("上轴转角 φ（°）")
    ax[3].set_xticks(range(0, 361, 30))
    marks = [("hook_catch", "钩线"), ("eye_in_fabric", "针眼入布"), ("tip_out_plate", "针尖出针板"), ("takeup_top", "挑线最高"),
             ("dog_rise", "牙出针板"), ("dog_drop", "牙落下")]
    for k, lab in marks:
        for a in ax:
            a.axvline(tm[k], color=MUTE, lw=0.6, ls=":")
        ax[0].annotate(f"{lab} {tm[k]:.1f}°", (tm[k], ax[0].get_ylim()[1]), rotation=90, va="top", ha="right", fontsize=7, color=INK)
    for a in ax:
        a.legend(loc="lower right", fontsize=7, frameon=False)
    ax[0].set_title("WQ-LS 整机时序（三维运动每 1° 量出；3 mm 正缝，布厚 1.5）", loc="left", color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "G8.1_时序图.png", dpi=180)
    plt.close(fig)

    pk = res["peaks"][:15]
    fig, ax = plt.subplots(figsize=(8, 5))
    names = [p["part"] for p in pk][::-1]
    ax.barh(names, [p["F_inertia_max"] for p in pk][::-1], color=C1, height=0.6)
    for i, p in enumerate(pk[::-1]):
        ax.text(p["F_inertia_max"], i, f"  {p['F_inertia_max']:.0f} N（a {p['a_max'] / 1000:.1f} km/s²）", va="center", fontsize=7, color=INK)
    ax.set_xlabel("质心最大惯性力 m·a（N），5000 r/min")
    ax.set_title("各运动件的最大惯性力（前 15）", loc="left", color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "G8.1_惯性力.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
