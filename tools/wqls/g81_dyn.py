"""G8.1 第四步 4.1：整机刚体多体动力学（MuJoCo）。

整机三维的运动件按刚性连接合成 13 个刚体，质量、质心、转动惯量取 FreeCAD 实体（parts.json）；
运动副的位置从整机运动（g4_mech.frames，每 1°）里取：上轴、下轴、旋梭轴、摇杆、送布摆轴、抬牙摆轴绕固定轴转，
连杆、挑线杆、送布连杆、抬牙连杆、牙架用铰链挂在上一级，针杆、调节器滑块沿直线滑，闭环用 connect 约束，
同步带 1 : 1、齿轮 1 : 2 用关节等式约束，上轴按 5000 r/min 匀速驱动（关节等式，每步更新角度）。
MuJoCo 正向积分两转（步长 1 µs），取第二转每 1°：
  - 驱动力矩（驱动等式约束的约束力），与 G2 解析法 dyn.py 逐点对照（惯性 + 重力，不加缝纫阻力）；
  - 每个运动副的约束力（树上关节用 cfrc_int 换到铰点，闭环用 connect 的约束力；同步带、齿轮是传递的力矩）；
  - 上轴两个轴承的支反力（上轴整体的约束力和力矩按两支承分开，支点位置同 G2）。
压脚组（没有布时被送布牙顶起）、油泵柱塞（0.4 mm 行程）、同步带质量不进模型，第 4.3 节按工况另算。

    python3 tools/wqls/g81_dyn.py <整机目录（s3、放下、TE：parts.json）>
      → docs/设计/WQ-LS/G8/G8.1_动力学.json、G8.1_动力学.png；<整机目录>/dyn_1deg.json（每 1° 全部结果）
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE)]
os.environ.setdefault("WQ_FEED", "s3")
import g81_kin as K  # noqa: E402

GM, S = K.GM, K.S
ROOT = HERE.parents[1]
OUT = ROOT / "docs" / "设计" / "WQ-LS" / "G8"
DEG = math.pi / 180
N_RPM = 5000.0
W = N_RPM * 2 * math.pi / 60

BODIES = {
    "upper": ["shaft", "crank", "crank_pin", "crank_screws", "rotor", "rotor_magnets", "encoder_disc", "handwheel", "handwheel_ring", "pulley_upper", "feed_ecc"],
    "rod": ["rod", "cage_rod"],
    "nb": ["needle_bar", "needle_clamp", "needle", "nb_link", "slide_block", "clamp_screw", "link_screws"],
    "lever": ["lever", "cage_lever", "pin_M"],
    "rocker": ["rocker"],
    "lower": ["pulley_lower", "lower_shaft", "gear_lower", "lift_ecc", "oil_ecc"],
    "hook": ["gear_hook", "hook_shaft", "hook"],
    "frod": ["feed_rod"], "rsl": ["reg_slider"], "flink": ["feed_link"], "frock": ["feed_rock"], "fbar": ["feed_bar"],
    "llink": ["lift_link"], "lrock": ["lift_rock"],
}
NAME = dict(upper="上轴组（曲柄、平衡块、转子、手轮）", rod="针杆连杆", nb="针杆组（针杆、连接块、滑块、针夹、机针）", lever="挑线杆", rocker="挑线摇杆",
            lower="下轴组", hook="旋梭轴组", frod="送布连杆", rsl="调节器滑块", flink="送布水平连杆", frock="送布摆轴", fbar="牙架（含送布牙）",
            llink="抬牙连杆", lrock="抬牙摆轴")


def combine(parts, names):
    """几个零件合成一个刚体：质量、质心、绕 x 的转动惯量（平行轴），y、z 的近似"""
    m = sum(parts[k]["mass_kg"] for k in names)
    c = sum(parts[k]["mass_kg"] * np.array(parts[k]["com"]) for k in names) / m
    I = np.zeros(3)
    for k in names:
        p = parts[k]
        d = np.array(p["com"]) - c
        mm = p["mass_kg"]
        I += np.array([p["Ixx_kgmm2"], p["Iyy_kgmm2"], p["Izz_kgmm2"]]) + mm * np.array([d[1] ** 2 + d[2] ** 2, d[0] ** 2 + d[2] ** 2, d[0] ** 2 + d[1] ** 2])
    return m, c, I


def angle_of(Mx):
    return math.atan2(Mx[2, 1], Mx[1, 1])


def unwrap_deg(a):
    return np.unwrap(np.array(a))


def kinematics():
    """每 1°：各刚体的转角 / 位移、各铰点位置（整机坐标 mm）"""
    GM.FP = K.feed_pose(3.0, False)
    fr = GM.frames(step=1, nd=None)
    Mx = {k: np.array([np.array(f["M"][k]).reshape(4, 4) for f in fr]) for k in fr[0]["M"]}
    FP = GM.FP
    lk = GM.TK
    pts, ang = {}, {}
    q = np.arange(360) * DEG
    pts["C"] = np.c_[-GM.R * np.sin(q), S.ZU + GM.R * np.cos(q)]          # 曲柄销（连杆大头、挑线杆）
    Bv = np.array([GM.pose(f)[1] for f in range(360)])
    pts["B"] = np.c_[np.zeros(360), S.ZU + Bv]                             # 连杆小头（针杆连接销）
    lps = [GM.MK.link_pose(f, GM.MK.LK0) for f in range(360)]
    pts["M"] = np.array([GM.w(p_["M"]) for p_ in lps])
    pts["Q"] = np.array([GM.w((lk["Qz"], lk["Qy"]))] * 360)
    for k in ("E", "P", "C", "T", "D", "K", "EL", "dog"):
        pts["f" + k] = np.array(FP[k], float)
    for b, names in BODIES.items():
        ang[b] = unwrap_deg([angle_of(Mx[names[0]][i]) for i in range(360)])
    ang["nb_z"] = Bv - Bv[0]
    return fr, Mx, pts, ang


def build(parts, pts, ang):
    """MJCF：树 + 闭环 connect + 关节等式"""
    import mujoco
    g = K.FEED["geo"]
    X = S.MECH_X
    body = {b: combine(parts, n) for b, n in BODIES.items()}
    P0 = {k: v[0] for k, v in pts.items()}
    u_slot = np.array(K.feed_pose(3.0, False)["P"][1]) - np.array(K.feed_pose(3.0, False)["P"][0])
    dP = pts["fP"] - pts["fP"][0]
    u_slot = dP[np.argmax(np.linalg.norm(dP, axis=1))]
    u_slot = u_slot / np.linalg.norm(u_slot)
    bar_dir0 = (P0["fK"] - P0["fT"]) / np.linalg.norm(P0["fK"] - P0["fT"])
    xm = lambda b: body[b][1][0]  # noqa: E731   每个刚体的质心 x：铰点、connect 都放在这个 x 上（平面机构）
    v3 = lambda x, yz: f"{x:.4f} {yz[0]:.4f} {yz[1]:.4f}"  # noqa: E731

    def inertial(b, origin):
        m, c, I = body[b]
        rel = (c - np.asarray(origin)) / 1000.0
        return f'<inertial pos="{rel[0]:.6f} {rel[1]:.6f} {rel[2]:.6f}" mass="{m:.6f}" diaginertia="{I[0] * 1e-6:.4e} {I[1] * 1e-6:.4e} {I[2] * 1e-6:.4e}"/>'

    def p3(x, yz):
        return np.array([x, yz[0], yz[1]], float)

    def bodyxml(b, origin, joint, children="", sites=""):
        o = origin / 1000.0
        return f'<body name="{b}" pos="{o[0]:.6f} {o[1]:.6f} {o[2]:.6f}">{joint}{inertial(b, origin)}{sites}{children}</body>'

    def rel(child_o, parent_o):
        return child_o - parent_o

    def site(name, at, origin):
        r = (at - origin) / 1000.0
        return f'<site name="{name}" pos="{r[0]:.6f} {r[1]:.6f} {r[2]:.6f}" size="0.002"/>'
    hx = lambda n: f'<joint name="{n}" type="hinge" axis="1 0 0" damping="0" armature="0"/>'  # noqa: E731
    sl = lambda n, a: f'<joint name="{n}" type="slide" axis="{a[0]:.6f} {a[1]:.6f} {a[2]:.6f}"/>'  # noqa: E731

    # 绝对位置（世界）——子体的 pos 写成相对父体
    O = dict(upper=p3(xm("upper"), (0, S.ZU)), lower=p3(xm("lower"), (S.YL, S.ZL)), hook=p3(xm("hook"), (0, S.ZH)),
             rocker=p3(xm("rocker"), P0["Q"]), frock=p3(xm("frock"), g["Fr"]), lrock=p3(xm("lrock"), g["Lr"]),
             nb=p3(xm("nb"), P0["B"]), rsl=p3(xm("rsl"), P0["fP"]))
    O.update(rod=p3(xm("rod"), P0["C"]), lever=p3(xm("lever"), P0["C"]), frod=p3(xm("frod"), P0["fE"]), llink=p3(xm("llink"), P0["fEL"]),
             flink=p3(xm("flink"), P0["fP"]), fbar=p3(xm("fbar"), P0["fT"]))

    def child(b, parent, joint, kids="", sites=""):
        o = rel(O[b], O[parent]) / 1000.0
        return f'<body name="{b}" pos="{o[0]:.6f} {o[1]:.6f} {o[2]:.6f}">{joint}{inertial(b, O[b])}{sites}{kids}</body>'

    def root(b, joint, kids="", sites=""):
        o = O[b] / 1000.0
        return f'<body name="{b}" pos="{o[0]:.6f} {o[1]:.6f} {o[2]:.6f}">{joint}{inertial(b, O[b])}{sites}{kids}</body>'

    K0 = P0["fK"]
    ksl_o = p3(xm("fbar"), K0)
    ksl = (f'<body name="ksl" pos="{(ksl_o - O["fbar"])[0] / 1000:.6f} {(ksl_o - O["fbar"])[1] / 1000:.6f} {(ksl_o - O["fbar"])[2] / 1000:.6f}">'
           f'{sl("j_ksl", (0, bar_dir0[0], bar_dir0[1]))}<inertial pos="0 0 0" mass="1e-5" diaginertia="1e-10 1e-10 1e-10"/>'
           f'<site name="ksl_pin" pos="0 0 0" size="0.002"/></body>')
    world = (
        root("upper", hx("j_upper"), child("rod", "upper", hx("j_rod"), sites=site("rod_B", p3(xm("rod"), P0["B"]), O["rod"]))
             + child("lever", "upper", hx("j_lever"), sites=site("lev_M", p3(xm("lever"), P0["M"]), O["lever"]))
             + child("frod", "upper", hx("j_frod"), sites=site("frod_P", p3(xm("frod"), P0["fP"]), O["frod"])))
        + root("nb", sl("j_nb", (0, 0, 1)), sites=site("nb_B", p3(xm("rod"), P0["B"]), O["nb"]))
        + root("rocker", hx("j_rocker"), sites=site("rck_M", p3(xm("lever"), P0["M"]), O["rocker"]))
        + root("lower", hx("j_lower"), child("llink", "lower", hx("j_llink"), sites=site("ll_D", p3(xm("llink"), P0["fD"]), O["llink"])))
        + root("hook", hx("j_hook"))
        + root("rsl", sl("j_rsl", (0, u_slot[0], u_slot[1])), child("flink", "rsl", hx("j_flink"), sites=site("fl_C", p3(xm("flink"), P0["fC"]), O["flink"])),
               sites=site("rsl_P", p3(xm("frod"), P0["fP"]), O["rsl"]))
        + root("frock", hx("j_frock"), child("fbar", "frock", hx("j_fbar"), ksl), sites=site("fr_C", p3(xm("flink"), P0["fC"]), O["frock"]))
        + root("lrock", hx("j_lrock"), sites=site("lr_D", p3(xm("llink"), P0["fD"]), O["lrock"]) + site("lr_K", p3(xm("fbar"), K0), O["lrock"]))
    )
    sr = 'solref="0.00002 1" solimp="0.999 0.9999 0.0001"'
    eq = (f'<connect name="c_rodnb" site1="rod_B" site2="nb_B" {sr}/>'
          f'<connect name="c_levrck" site1="lev_M" site2="rck_M" {sr}/>'
          f'<connect name="c_frodP" site1="frod_P" site2="rsl_P" {sr}/>'
          f'<connect name="c_flinkC" site1="fl_C" site2="fr_C" {sr}/>'
          f'<connect name="c_llinkD" site1="ll_D" site2="lr_D" {sr}/>'
          f'<connect name="c_fork" site1="ksl_pin" site2="lr_K" {sr}/>'
          f'<joint name="belt" joint1="j_lower" joint2="j_upper" polycoef="0 1 0 0 0" {sr}/>'
          f'<joint name="gear" joint1="j_hook" joint2="j_lower" polycoef="0 -2 0 0 0" {sr}/>'
          f'<joint name="drive" joint1="j_upper" polycoef="0 0 0 0 0" {sr}/>')
    xml = (f'<mujoco><compiler angle="radian"/><option timestep="1e-6" gravity="0 0 -9.81" integrator="implicitfast"><flag contact="disable"/></option>'
           f'<worldbody>{world}</worldbody><equality>{eq}</equality></mujoco>')
    model = mujoco.MjModel.from_xml_string(xml)
    return model, xml, body, O, u_slot, bar_dir0


def joint_state(ang, pts, u_slot, bar_dir0):
    """每 1° 的关节坐标（相对 φ = 0 的装配位置）"""
    a = {b: ang[b] - ang[b][0] for b in BODIES}
    qs = dict(j_upper=a["upper"], j_rod=a["rod"] - a["upper"], j_lever=a["lever"] - a["upper"], j_frod=a["frod"] - a["upper"],
              j_nb=ang["nb_z"] / 1000.0, j_rocker=a["rocker"], j_lower=a["lower"], j_llink=a["llink"] - a["lower"], j_hook=a["hook"],
              j_rsl=((pts["fP"] - pts["fP"][0]) @ u_slot) / 1000.0, j_flink=a["flink"], j_frock=a["frock"], j_fbar=a["fbar"] - a["frock"], j_lrock=a["lrock"])
    bd = np.c_[np.cos(a["fbar"]), np.sin(a["fbar"])] @ np.array([[bar_dir0[0], bar_dir0[1]], [-bar_dir0[1], bar_dir0[0]]])
    sk = np.einsum("ij,ij->i", pts["fK"] - pts["fT"], bd)
    qs["j_ksl"] = (sk - sk[0]) / 1000.0
    return qs


def simulate(model, qs, revs=2):
    import mujoco
    d = mujoco.MjData(model)
    jid = {model.joint(i).name: i for i in range(model.njnt)}
    for n, arr in qs.items():
        adr = model.jnt_qposadr[jid[n]]
        d.qpos[adr] = arr[0]
        full = {"j_upper": 1.0, "j_lower": 1.0, "j_hook": -2.0}         # 整周转的：转速已知
        # 挂在整周转的轴上的杆：相对转角每转少 2π，φ = −1° 处的值是 arr[359] + 2π；其余周期的直接中心差分
        wrap = 2 * math.pi if n in ("j_rod", "j_lever", "j_frod", "j_llink") else 0.0
        d.qvel[model.jnt_dofadr[jid[n]]] = full[n] * W if n in full else (arr[1] - arr[-1] - wrap) / (2 * DEG) * W
    mujoco.mj_forward(model, d)
    eid = {model.equality(i).name: i for i in range(model.neq)}
    dt = model.opt.timestep
    steps = int(round(revs * 2 * math.pi / W / dt))
    rec = []
    next_deg = 360.0                    # 第二转起每 1° 记一次
    for _ in range(steps):
        model.eq_data[eid["drive"]][0] = W * (d.time + dt)
        mujoco.mj_step(model, d)
        phi_deg = math.degrees(d.qpos[model.jnt_qposadr[jid["j_upper"]]])
        if phi_deg >= next_deg - 1e-9:
            mujoco.mj_rnePostConstraint(model, d)
            ef = {}
            for i in range(d.nefc):
                if d.efc_type[i] == mujoco.mjtConstraint.mjCNSTR_EQUALITY:
                    ef.setdefault(model.equality(d.efc_id[i]).name, []).append(float(d.efc_force[i]))
            rec.append(dict(phi=phi_deg - 360.0, ef=ef, cfrc=d.cfrc_int.copy(), subcom=d.subtree_com.copy(), xpos=d.xpos.copy(),
                            site={model.site(i).name: d.site_xpos[i].copy() for i in range(model.nsite)},
                            viol=float(np.max(np.abs(d.efc_pos[:d.nefc]))) if d.nefc else 0.0))
            next_deg += 1.0
            if next_deg >= 720.0:
                break
    return rec


def joint_forces(model, rec, O):
    """每 1° 各运动副的力（N，作用在子体上，世界坐标 y、z）、驱动力矩"""
    import mujoco  # noqa: F401
    bid = {model.body(i).name: i for i in range(model.nbody)}
    root_of = {model.body(i).name: model.body_rootid[i] for i in range(model.nbody)}
    tree_joint_pt = dict(upper="上轴轴承（合力）", rod="曲柄销—连杆大头", lever="曲柄销—挑线杆", frod="送布偏心—送布连杆", nb="针杆—导套（侧向力）",
                         rocker="摇杆支点销 Q", lower="下轴轴承（合力）", llink="抬牙偏心—抬牙连杆", hook="旋梭轴轴承（合力）", rsl="调节器滑槽（侧向力）",
                         flink="调节器滑块—送布水平连杆", frock="送布摆轴轴承", fbar="送布摆杆销 T—牙架", lrock="抬牙摆轴轴承")
    out = {k: [] for k in tree_joint_pt}
    conn = dict(c_rodnb="连杆小头—针杆连接销", c_levrck="挑线杆—摇杆铰点 M", c_frodP="送布连杆—调节器滑块 P", c_flinkC="送布水平连杆—摆轴曲柄销 C",
                c_llinkD="抬牙连杆—抬牙摆轴曲柄销 D", c_fork="牙架—抬牙叉子 K")
    for k in conn:
        out[k] = []
    drive, belt, gear, viol = [], [], [], []
    X1, X2 = 45.0, 380.0                     # 上轴两支承（前轴承 6203、后轴承 6201，同 G2）；中间含油轴套的分担在 4.7 用轴的梁模型算
    out["brg_front"], out["brg_rear"] = [], []
    names_extra = dict(brg_front="上轴前轴承 6203（两支承分开）", brg_rear="上轴后轴承 6201（两支承分开）")
    # 上轴两支承：上轴组自身的质心（平衡块使它偏离轴线）× 向心加速度、重力，加上连杆、挑线杆、送布连杆在曲柄销、偏心上的反作用，
    # 按两支承分开（力和绕前轴承的力矩平衡；上轴组绕 y、z 的惯性积不计）
    m_u, c_u0, _ = UPPER_MC
    for r in rec:
        q = math.radians(r["phi"])
        cy, cz = c_u0[1], c_u0[2] - 200.0
        cu = np.array([c_u0[0], cy * math.cos(q) - cz * math.sin(q), 200.0 + cy * math.sin(q) + cz * math.cos(q)])
        a_u = -W ** 2 * np.array([0.0, cu[1], cu[2] - 200.0]) / 1000.0
        Fsum = m_u * a_u - np.array([0.0, 0.0, -9.81 * m_u])
        Msum = np.cross(cu - np.array([X1, 0, 200.0]), m_u * a_u - np.array([0.0, 0.0, -9.81 * m_u]))
        for ch, pt in (("rod", "C"), ("lever", "C"), ("frod", "fE")):
            fch = np.r_[0.0, r["cfrc"][bid[ch]][4:]]                     # 上轴给子杆的力（平面机构：只取 y、z；x 分量是 MuJoCo 内力换算的数值噪声，不用）
            yz = PTS[pt][int(round(r["phi"])) % 360]
            p = np.array([BODY_X[ch], yz[0], yz[1]])
            Fsum = Fsum + fch                                           # 上轴要给出去的，轴承都得补上
            Msum = Msum + np.cross(p - np.array([X1, 0, 200.0]), fch)
        f2y, f2z = Msum[2] / (X2 - X1), -Msum[1] / (X2 - X1)
        out["brg_rear"].append([float(f2y), float(f2z)])
        out["brg_front"].append([float(Fsum[1] - f2y), float(Fsum[2] - f2z)])
    for r in rec:
        for b in tree_joint_pt:
            i = bid[b]
            c = r["subcom"][root_of[b]]
            f = r["cfrc"][i][3:]
            out[b].append([float(f[1]), float(f[2])])
        for k in conn:
            v = r["ef"].get(k, [0, 0, 0])
            out[k].append([float(v[1]), float(v[2])])
        drive.append(float(r["ef"]["drive"][0]))
        belt.append(float(r["ef"]["belt"][0]))
        gear.append(float(r["ef"]["gear"][0]))
        viol.append(r["viol"])
    names = {**tree_joint_pt, **conn, **names_extra}
    return out, names, np.array(drive), np.array(belt), np.array(gear), np.array(viol)


def main():
    bdir = Path(sys.argv[1])
    parts = json.loads((bdir / "parts.json").read_text())["parts"]
    fix = bdir / "inertia_fix.json"                       # 多实体零件的转动惯量（cad/inertia_fix.py）
    if fix.exists():
        for k, v in json.loads(fix.read_text()).items():
            parts[k].update(v)
    fr, Mx, pts, ang = kinematics()
    model, xml, body, O, u_slot, bar_dir0 = build(parts, pts, ang)
    (bdir / "dyn_model.xml").write_text(xml)
    qs = joint_state(ang, pts, u_slot, bar_dir0)
    rec = simulate(model, qs)
    global UPPER_MC, PTS, BODY_X
    UPPER_MC = combine(parts, BODIES["upper"])
    PTS = pts
    BODY_X = {b: combine(parts, n)[1][0] for b, n in BODIES.items()}
    F, names, drive, belt, gear, viol = joint_forces(model, rec, O)
    phi = np.array([r["phi"] for r in rec])
    # 同一质量模型的功率法（不经过 MuJoCo）：T·ω = Σ m a·v + Σ I_xx θ̇ θ̈ + Σ m g ż，各刚体的质心、转角取整机运动每 1°
    body = {b: combine(parts, n) for b, n in BODIES.items()}
    Te = np.zeros(360)
    for b, bparts in BODIES.items():
        m, c, I = body[b]
        Mb = Mx[bparts[0]]
        pc = np.array([Mb[i] @ np.r_[c, 1.0] for i in range(360)])[:, :3] / 1000.0
        d1 = (np.roll(pc, -1, 0) - np.roll(pc, 1, 0)) / (2 * DEG)
        d2 = (np.roll(pc, -1, 0) - 2 * pc + np.roll(pc, 1, 0)) / DEG ** 2
        th = ang[b]
        t1 = (np.roll(th, -1) - np.roll(th, 1)) / (2 * DEG)
        t2 = (np.roll(th, -1) - 2 * th + np.roll(th, 1)) / DEG ** 2
        span = th[-1] - th[0]
        if abs(span) > math.pi:                                   # 整周转的：差分要跨过 0°
            slope = round(span / (2 * math.pi) * 360 / 359)
            t1[0] = (th[1] - th[-1] + slope * 2 * math.pi) / (2 * DEG); t1[-1] = (th[0] + slope * 2 * math.pi - th[-2]) / (2 * DEG)
            t2[0] = (th[1] - 2 * th[0] + th[-1] - slope * 2 * math.pi) / DEG ** 2; t2[-1] = (th[0] + slope * 2 * math.pi - 2 * th[-1] + th[-2]) / DEG ** 2
        Te += m * np.einsum("ij,ij->i", d1, d2) * W ** 2 + I[0] * 1e-6 * t1 * t2 * W ** 2 + m * 9.81 * d1[:, 2]
    t_pow = np.interp(phi, np.arange(360), Te, period=360)
    # G2 解析法：同一转速、不加缝纫阻力（惯性 + 重力）
    import dyn
    R = dyn.Machine(resist={k: 0.0 for k in dyn.RESIST}).run()
    t_ref = np.interp(phi, R["phi"], np.asarray(R["T_bar"]) + R["T_rod"] + R["T_tk"] + R["T_fd"] + R["T_grav"])
    sgn = 1.0 if np.dot(drive, t_pow) >= 0 else -1.0
    drive = sgn * drive
    diff = drive - t_pow                                         # 判据：MuJoCo 与同一质量模型的功率法
    rel = float(np.max(np.abs(diff)) / np.max(np.abs(t_pow)))
    rel_g2 = float(np.max(np.abs(drive - t_ref)) / np.max(np.abs(t_ref)))
    peaks = sorted(((k, float(np.max(np.linalg.norm(np.array(v), axis=1)))) for k, v in F.items()), key=lambda x: -x[1])
    res = dict(rpm=N_RPM, bodies={b: dict(name=NAME[b], mass_g=round(body[b][0] * 1000, 1), parts=BODIES[b]) for b in BODIES},
               drive=dict(T_max=round(float(drive.max()), 3), T_min=round(float(drive.min()), 3), T_rms=round(float(np.sqrt(np.mean(drive ** 2))), 3),
                          power_T_max=round(float(t_pow.max()), 3), power_T_min=round(float(t_pow.min()), 3), max_abs_diff=round(float(np.max(np.abs(diff))), 4),
                          rel_diff=round(rel, 4), ok=rel <= 0.05,
                          g2_T_max=round(float(t_ref.max()), 3), g2_T_min=round(float(t_ref.min()), 3), rel_diff_g2=round(rel_g2, 4)),
               joints=[dict(key=k, name=names[k], F_max=round(v, 1)) for k, v in peaks],
               belt_torque_max=round(float(np.max(np.abs(belt))), 3), gear_torque_max=round(float(np.max(np.abs(gear))), 3),
               constraint_violation_max_m=float(viol.max()), points=len(rec),
               omitted="压脚组（没有布时被送布牙顶起，4.3 按弹簧压在布上算）、油泵柱塞、同步带质量")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "G8.1_动力学.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    figs(phi, drive, t_pow, t_ref, F, names, OUT / "G8.1_动力学.png")
    (bdir / "dyn_1deg.json").write_text(json.dumps(dict(phi=phi.tolist(), drive=drive.tolist(), power=t_pow.tolist(), dyn=t_ref.tolist(), belt=belt.tolist(), gear=gear.tolist(),
                                                         F={k: np.round(np.array(v), 3).tolist() for k, v in F.items()}, names=names)))
    print(json.dumps({k: res[k] for k in ("drive", "joints", "belt_torque_max", "gear_torque_max", "constraint_violation_max_m", "points")}, ensure_ascii=False, indent=1))


def figs(phi, drive, t_pow, t_ref, F, names, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    f_ = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    if Path(f_).exists():
        font_manager.fontManager.addfont(f_)
    plt.rcParams.update({"font.family": ["Noto Sans CJK JP", "DejaVu Sans"], "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    fig = plt.figure(figsize=(13, 4.4))
    a1 = fig.add_subplot(1, 3, 1)
    a1.plot(phi, drive, color="#2a5fb8", lw=2, label="MuJoCo 整机（13 个刚体）")
    a1.plot(phi, t_pow, color="#e0a33b", lw=1, ls="--", label="同一质量的功率法")
    a1.plot(phi, t_ref, color="#7a8794", lw=1, ls=":", label="G2 解析法（估计质量）")
    a1.set_title("驱动力矩（5000 r/min，惯性 + 重力）", loc="left"); a1.set_xlabel("上轴转角 φ（°）"); a1.set_ylabel("N·m"); a1.set_xticks(range(0, 361, 60))
    a1.legend(fontsize=7.5, frameon=False)
    a2 = fig.add_subplot(1, 3, 2, aspect="equal")
    for k, c in (("brg_front", "#c4531d"), ("brg_rear", "#2e9e6a"), ("rod", "#2a5fb8"), ("c_rodnb", "#7a5cc9")):
        v = np.array(F[k])
        a2.plot(v[:, 0], v[:, 1], color=c, lw=1.4, label=f"{names[k]}（最大 {np.max(np.linalg.norm(v, axis=1)):.0f} N）")
    a2.axhline(0, color="#999", lw=0.5); a2.axvline(0, color="#999", lw=0.5)
    a2.set_title("一转里力的走向（端视 y–z，N）", loc="left"); a2.legend(fontsize=7, frameon=False, loc="lower left")
    a3 = fig.add_subplot(1, 3, 3)
    pk = sorted(((names[k], float(np.max(np.linalg.norm(np.array(v), axis=1)))) for k, v in F.items() if k != "upper"), key=lambda x: x[1])[-12:]
    a3.barh([p_[0] for p_ in pk], [p_[1] for p_ in pk], color="#2a5fb8")
    for i, (_, v) in enumerate(pk):
        a3.text(v, i, f" {v:.0f}", va="center", fontsize=7.5)
    a3.set_title("各运动副最大约束力（N）", loc="left"); a3.tick_params(axis="y", labelsize=7.5)
    fig.tight_layout(); fig.savefig(path, dpi=170); plt.close(fig)


if __name__ == "__main__":
    main()
