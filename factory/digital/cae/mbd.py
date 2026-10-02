# -*- coding: utf-8 -*-
"""运动与动力分析（第 12 轮 D1、D4、D5）：MuJoCo 多体动力学。

设置 setup：
  duration_s: 仿真时长（≤ 60）
  gravity: true / false
  initial: {关节名: 初值（rad 或 m）}           没给的用模型的 home 关键帧，再没有就 0
  drives: [                                    驱动（一个关节一个）
    {"joint": "crank", "kind": "speed", "value": 6.283},                         匀速（rad/s 或 m/s）
    {"joint": "j1", "kind": "move", "to": 1.2, "t0": 0, "t1": 2, "accel": 0.25},  梯形速度点到点（加减速各占 25%）
    {"joint": "j2", "kind": "sine", "amp": 0.3, "freq": 0.5},                    正弦（围绕初值）
    {"joint": "j3", "kind": "hold"},                                             保持初值
    {"joint": "j4", "kind": "torque", "value": 2.0},                             给定力矩 / 力（N·m 或 N）
  ]
  payloads: [{"body": "wrist_3_link", "mass": 3.0, "pos": [0, 0.1, 0]}]       末端负载（质点，挂在构件上）
  forces: [{"body": "slider", "force": [-200, 0, 0], "pos": [0, 0, 0]}]          外力（世界坐标，作用点在构件上，恒定）
  friction: {关节名: {"damping": N·m·s/rad, "frictionloss": N·m}}
  points: [{"body": "coupler", "pos": [0.06, 0, 0], "name": "P"}]                要记录轨迹的点
  sample_hz: 记录频率（≤ 200）

给定运动的驱动用“刚性伺服 + 前馈”实现：先跑一遍取得所需力矩，第二遍把它当前馈，跟踪误差一般 < 0.01°；
记录的驱动力矩就是这次实际运动所需的力矩（与 ADAMS 的“运动副驱动”同义）。
关节反力：每个构件从父构件受到的力和力矩（世界坐标，力矩对关节中心），由 MuJoCo 的 cfrc_int 换算。
"""
import math

import numpy as np

MAX_DURATION_S = 60.0
MAX_SAMPLE_HZ = 200
ANIM_HZ = 50


class SetupError(ValueError):
    pass


# ---------------------------------------------------------------- 载入
def load_spec(path=None, xml=None, assets=None, urdf=False):
    import mujoco
    if path:
        return mujoco.MjSpec.from_file(str(path))
    if xml is None:
        raise SetupError("没有模型")
    return mujoco.MjSpec.from_string(xml, assets=assets or {})


def _visual_group(spec_model):
    """可视几何所在的组：Menagerie 习惯是 2（3 是碰撞）；没有分组就全部"""
    groups = set(int(g) for g in spec_model.geom_group)
    return 2 if 2 in groups else None


def info(model):
    """模型清单：构件、关节、点（网页设置用）"""
    import mujoco
    bodies = []
    for b in range(1, model.nbody):
        bodies.append({"name": mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, b) or "body{}".format(b),
                       "parent": mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, int(model.body_parentid[b])) or "world",
                       "mass_kg": round(float(model.body_mass[b]), 4)})
    joints = []
    for j in range(model.njnt):
        t = int(model.jnt_type[j])
        if t not in (2, 3):                     # 只列转动、移动关节（自由关节、球关节不驱动）
            continue
        rng = model.jnt_range[j] if model.jnt_limited[j] else None
        joints.append({"name": mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, j) or "joint{}".format(j),
                       "type": "hinge" if t == 3 else "slide",
                       "body": mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, int(model.jnt_bodyid[j])),
                       "range": [round(float(x), 5) for x in rng] if rng is not None else None,
                       "unit": "rad" if t == 3 else "m"})
    sites = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_SITE, s) for s in range(model.nsite)]
    home = None
    for k in range(model.nkey):
        if (mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_KEY, k) or "") == "home":
            home = {jn["name"]: float(model.key_qpos[k][model.jnt_qposadr[_jid(model, jn["name"])]]) for jn in joints}
    return {"bodies": bodies, "joints": joints, "sites": [s for s in sites if s], "home": home,
            "total_mass_kg": round(float(sum(model.body_mass[1:])), 4), "equalities": int(model.neq)}


def _jid(model, name):
    import mujoco
    j = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
    if j < 0:
        raise SetupError("模型里没有关节“{}”".format(name))
    return j


def _bid(model, name):
    import mujoco
    b = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, name)
    if b < 0:
        raise SetupError("模型里没有构件“{}”".format(name))
    return b


# ---------------------------------------------------------------- 驱动曲线
def profile(d, q0):
    """返回 f(t) → (q, qd)；给定运动的驱动用"""
    k = d["kind"]
    if k == "hold":
        return lambda t: (q0, 0.0)
    if k == "speed":
        w = float(d["value"])
        return lambda t: (q0 + w * t, w)
    if k == "sine":
        a, f = float(d.get("amp", 0)), float(d.get("freq", 1))
        w = 2 * math.pi * f
        return lambda t: (q0 + a * math.sin(w * t), a * w * math.cos(w * t))
    if k == "move":
        q1 = float(d["to"])
        t0, t1 = float(d.get("t0", 0)), float(d["t1"])
        ra = min(max(float(d.get("accel", 0.25)), 0.01), 0.5)
        T = t1 - t0
        if T <= 0:
            raise SetupError("关节“{}”的运动时间要大于 0".format(d["joint"]))
        ta = ra * T
        vmax = (q1 - q0) / (T - ta)                       # 梯形：加速 ta、匀速 T−2ta、减速 ta
        acc = vmax / ta

        def f(t):
            s = t - t0
            if s <= 0:
                return q0, 0.0
            if s >= T:
                return q1, 0.0
            if s < ta:
                return q0 + 0.5 * acc * s * s, acc * s
            if s < T - ta:
                return q0 + 0.5 * acc * ta * ta + vmax * (s - ta), vmax
            r = T - s
            return q1 - 0.5 * acc * r * r, acc * r
        return f
    raise SetupError("不认识的驱动方式“{}”".format(k))


# ---------------------------------------------------------------- 组装
def build(spec, setup):
    """按设置改模型：去掉模型自带的执行器，加驱动、负载、摩擦、重力。返回 (model, 驱动表)"""
    import mujoco
    for a in list(spec.actuators):
        spec.delete(a)
    spec.option.gravity = [0, 0, -9.81] if setup.get("gravity", True) else [0, 0, 0]
    spec.option.integrator = mujoco.mjtIntegrator.mjINT_IMPLICITFAST
    if not setup.get("contact"):
        spec.option.disableflags |= mujoco.mjtDisableBit.mjDSBL_CONTACT       # 机构、机械臂：默认不算碰撞
    for name, fr in (setup.get("friction") or {}).items():
        j = spec.joint(name)
        if j is None:
            raise SetupError("模型里没有关节“{}”".format(name))
        if "damping" in fr:
            j.damping = float(fr["damping"])
        if "frictionloss" in fr:
            j.frictionloss = float(fr["frictionloss"])
    for i, p in enumerate(setup.get("payloads") or []):
        b = spec.body(p["body"])
        if b is None:
            raise SetupError("模型里没有构件“{}”".format(p["body"]))
        m = float(p["mass"])
        if not 0 < m <= 1000:
            raise SetupError("负载质量要在 0–1000 kg 之间")
        pb = b.add_body(name="wq_payload_{}".format(i), pos=list(p.get("pos") or [0, 0, 0]))
        pb.mass = m
        pb.inertia = [1e-6, 1e-6, 1e-6]
        pb.explicitinertial = True
        pb.add_geom(type=mujoco.mjtGeom.mjGEOM_SPHERE, size=[max(0.01, 0.02 * m ** (1 / 3)), 0, 0], rgba=[0.9, 0.5, 0.1, 1],
                    contype=0, conaffinity=0, group=2, mass=0)
    for i, pt in enumerate(setup.get("points") or []):
        b = spec.body(pt["body"])
        if b is None:
            raise SetupError("模型里没有构件“{}”".format(pt["body"]))
        b.add_site(name="wq_pt_{}".format(i), pos=list(pt.get("pos") or [0, 0, 0]))
    drives = []
    seen = set()
    for d in setup.get("drives") or []:
        jn = d["joint"]
        if jn in seen:
            raise SetupError("关节“{}”有两个驱动".format(jn))
        seen.add(jn)
        if spec.joint(jn) is None:
            raise SetupError("模型里没有关节“{}”".format(jn))
        if d["kind"] == "torque":
            spec.add_actuator(name="wq_m_" + jn, target=jn, trntype=mujoco.mjtTrn.mjTRN_JOINT,
                              gaintype=mujoco.mjtGain.mjGAIN_FIXED, gainprm=[1] + [0] * 9, biastype=mujoco.mjtBias.mjBIAS_NONE)
            drives.append(dict(d, mode="torque"))
        else:
            # 伺服（增益随后按等效惯量设）+ 前馈电机
            spec.add_actuator(name="wq_s_" + jn, target=jn, trntype=mujoco.mjtTrn.mjTRN_JOINT,
                              gaintype=mujoco.mjtGain.mjGAIN_FIXED, gainprm=[1] + [0] * 9,
                              biastype=mujoco.mjtBias.mjBIAS_AFFINE, biasprm=[0, -1, -1] + [0] * 7)
            spec.add_actuator(name="wq_f_" + jn, target=jn, trntype=mujoco.mjtTrn.mjTRN_JOINT,
                              gaintype=mujoco.mjtGain.mjGAIN_FIXED, gainprm=[1] + [0] * 9, biastype=mujoco.mjtBias.mjBIAS_NONE)
            drives.append(dict(d, mode="motion"))
    for key in spec.keys:                    # 关键帧里的执行器控制量按新的执行器个数重置
        key.ctrl = [0.0] * len(spec.actuators)
    try:
        model = spec.compile()
    except Exception as e:  # noqa: BLE001
        raise SetupError("模型编译失败：{}".format(str(e)[:200])) from None
    return model, drives


# ---------------------------------------------------------------- 计算
def _initial(model, data, setup, drives):
    import mujoco
    home = info(model)["home"] or {}
    for name, v in list(home.items()) + list((setup.get("initial") or {}).items()):
        data.qpos[model.jnt_qposadr[_jid(model, name)]] = float(v)
    mujoco.mj_forward(model, data)


def _ids(model, drives):
    import mujoco
    out = []
    for d in drives:
        j = _jid(model, d["joint"])
        if model.jnt_type[j] not in (2, 3):
            raise SetupError("关节“{}”不是转动或移动关节，不能驱动".format(d["joint"]))
        a = {k: mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, "wq_{}_{}".format(k, d["joint"])) for k in ("m", "s", "f")}
        out.append({"d": d, "j": j, "qadr": int(model.jnt_qposadr[j]), "dadr": int(model.jnt_dofadr[j]), "a": a})
    return out


def _tune(model, data, ids, dt):
    """伺服增益：按关节等效惯量取固有频率 ω（≤ 0.15/dt），临界阻尼"""
    import mujoco
    M = np.zeros((model.nv, model.nv))
    mujoco.mj_fullM(model, data, M)
    w = min(2 * math.pi * 60, 0.15 / dt)
    for x in ids:
        if x["d"]["mode"] != "motion":
            continue
        inertia = max(float(M[x["dadr"], x["dadr"]]), 1e-6)
        kp, kv = inertia * w * w, 2 * inertia * w
        s = x["a"]["s"]
        model.actuator_gainprm[s, 0] = kp
        model.actuator_biasprm[s, 1] = -kp
        model.actuator_biasprm[s, 2] = -kv
        x["kp"], x["kv"] = kp, kv


def _run(model, setup, drives, ff=None, record=False):
    """跑一遍。ff：上一遍每一步的驱动力矩（前馈）。返回 (每一步的驱动力矩表, 记录)"""
    import mujoco
    data = mujoco.MjData(model)
    _initial(model, data, setup, drives)
    ids = _ids(model, drives)
    dt = float(model.opt.timestep)
    for x in ids:
        x["q0"] = float(data.qpos[x["qadr"]])
        if x["d"]["mode"] == "motion":
            x["f"] = profile(x["d"], x["q0"])
            q, qd = x["f"](0.0)
            data.qpos[x["qadr"]] = q
            data.qvel[x["dadr"]] = qd
    mujoco.mj_forward(model, data)
    _tune(model, data, ids, dt)
    nsteps = int(round(min(float(setup.get("duration_s", 2)), MAX_DURATION_S) / dt))
    fbody = []
    for fdef in setup.get("forces") or []:
        fbody.append((_bid(model, fdef["body"]), np.asarray(fdef["force"], float), np.asarray(fdef.get("pos") or [0, 0, 0], float)))
    taus = np.zeros((nsteps, len(ids)))
    rec = Recorder(model, setup, ids) if record else None
    every = max(1, int(round(1 / (min(float(setup.get("sample_hz", 100)), MAX_SAMPLE_HZ) * dt))))
    anim_every = max(1, int(round(1 / (ANIM_HZ * dt))))
    err = 0.0
    for k in range(nsteps):
        t = k * dt
        for x in ids:
            if x["d"]["mode"] == "torque":
                data.ctrl[x["a"]["m"]] = float(x["d"]["value"])
            else:
                q, qd = x["f"](t + dt)
                data.ctrl[x["a"]["s"]] = q + x["kv"] / x["kp"] * qd
                data.ctrl[x["a"]["f"]] = ff[k, ids.index(x)] if ff is not None else 0.0
        data.xfrc_applied[:] = 0
        for b, F, p in fbody:
            # 作用点在构件坐标里：转成对质心的力矩
            pw = data.xpos[b] + data.xmat[b].reshape(3, 3) @ p
            data.xfrc_applied[b, :3] = F
            data.xfrc_applied[b, 3:] = np.cross(pw - data.xipos[b], F)
        if rec and k % every == 0:
            rec.sample(data, t, k % anim_every == 0 or k == 0)
        mujoco.mj_step(model, data)
        if not np.all(np.isfinite(data.qpos)):
            raise SetupError("计算发散（第 {:.3f} 秒）：载荷或速度太大，或者初始位置不满足约束".format(t))
        for i, x in enumerate(ids):
            taus[k, i] = data.qfrc_actuator[x["dadr"]]
            if x["d"]["mode"] == "motion":
                err = max(err, abs(data.qpos[x["qadr"]] - x["f"](t + dt)[0]))
    if rec:
        rec.sample(data, nsteps * dt, True)
    return taus, rec, err


def simulate(spec, setup):
    """返回 (汇总, 曲线通道 {名: 数组}, 动画 {bodies, t, pos, quat})"""
    import time as _t
    t0 = _t.time()
    if float(setup.get("duration_s", 2)) <= 0:
        raise SetupError("仿真时长要大于 0")
    if float(setup.get("duration_s", 2)) > MAX_DURATION_S:
        raise SetupError("教学版仿真时长最多 {:.0f} 秒".format(MAX_DURATION_S))
    model, drives = build(spec, setup)
    model.opt.timestep = float(setup.get("dt") or (2e-4 if model.nv <= 12 and model.neq else 5e-4))
    ff = None
    if any(d["mode"] == "motion" for d in drives):
        ff, _, _ = _run(model, setup, drives)                # 第一遍：取得所需力矩
    _, rec, err = _run(model, setup, drives, ff=ff, record=True)
    ch = rec.channels()
    summ = {"duration_s": float(setup.get("duration_s", 2)), "timestep_s": float(model.opt.timestep),
            "samples": len(ch["t"]), "seconds": round(_t.time() - t0, 2), "tracking_error_max": err,
            "drives": [], "peaks": {}}
    for d in drives:
        j = d["joint"]
        tau, qd = ch["drive." + j], ch["qd." + j]
        p = tau * qd
        summ["drives"].append({"joint": j, "kind": d["kind"], "peak": float(np.max(np.abs(tau))), "rms": float(np.sqrt(np.mean(tau ** 2))),
                               "speed_max": float(np.max(np.abs(qd))), "power_peak": float(np.max(np.abs(p))),
                               "power_mean": float(np.mean(p))})
    for name, v in ch.items():
        if name != "t":
            i = int(np.argmax(np.abs(v)))
            summ["peaks"][name] = {"max_abs": float(abs(v[i])), "at_s": float(ch["t"][i]), "rms": float(np.sqrt(np.mean(v ** 2)))}
    return summ, ch, rec.animation()


class Recorder:
    def __init__(self, model, setup, ids):
        import mujoco
        self.m = model
        self.ids = ids
        self.rows = []
        self.anim_t, self.anim_pos, self.anim_quat = [], [], []
        self.joints = [j for j in range(model.njnt) if model.jnt_type[j] in (2, 3)]
        self.jname = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, j) for j in self.joints]
        self.bodies = list(range(1, model.nbody))
        self.bname = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, b) or "body{}".format(b) for b in self.bodies]
        self.sites = [s for s in range(model.nsite) if (mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_SITE, s) or "").startswith("wq_pt_")]
        self.pnames = [(setup.get("points") or [])[int(mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_SITE, s)[6:])].get("name")
                       or "P{}".format(i + 1) for i, s in enumerate(self.sites)]
        self.drive_j = {x["d"]["joint"]: x["dadr"] for x in ids}
        self.names = None

    def sample(self, data, t, anim):
        import mujoco
        m = self.m
        mujoco.mj_forward(m, data)
        mujoco.mj_rnePostConstraint(m, data)
        row = [t]
        for j in self.joints:
            qa, da = m.jnt_qposadr[j], m.jnt_dofadr[j]
            row += [data.qpos[qa], data.qvel[da], data.qacc[da]]
        for jn, da in self.drive_j.items():
            row.append(data.qfrc_actuator[da])
        for b in self.bodies:
            # cfrc_int：父构件作用在本构件上的力，[力矩; 力]，参考点是所在树根的子树质心
            c = data.subtree_com[m.body_rootid[b]]
            tq, f = data.cfrc_int[b, :3], data.cfrc_int[b, 3:]
            j = m.body_jntadr[b]
            p = data.xanchor[j] if j >= 0 else data.xpos[b]
            mo = tq - np.cross(p - c, f)
            row += [f[0], f[1], f[2], np.linalg.norm(f), mo[0], mo[1], mo[2], np.linalg.norm(mo)]
        for s in self.sites:
            row += list(data.site_xpos[s])
        self.rows.append(row)
        if anim:
            self.anim_t.append(t)
            self.anim_pos.append(np.array(data.xpos[1:], float))
            self.anim_quat.append(np.array(data.xquat[1:], float))

    def channels(self):
        names = ["t"]
        for n in self.jname:
            names += ["q." + n, "qd." + n, "qdd." + n]
        names += ["drive." + n for n in self.drive_j]
        for n in self.bname:
            names += ["rf.{}.{}".format(n, a) for a in ("x", "y", "z", "abs")] + ["rm.{}.{}".format(n, a) for a in ("x", "y", "z", "abs")]
        for n in self.pnames:
            names += ["pt.{}.{}".format(n, a) for a in ("x", "y", "z")]
        arr = np.array(self.rows, float)
        return {n: arr[:, i] for i, n in enumerate(names)}

    def animation(self):
        return {"bodies": self.bname, "t": np.array(self.anim_t, float), "pos": np.array(self.anim_pos, float),
                "quat": np.array(self.anim_quat, float)}


# ---------------------------------------------------------------- 手算对照（测试与报告用）
def gravity_torques(model, qpos, g=9.81):
    """独立于动力学求解的几何算法：每个转动关节的重力矩 τ = Σ_下游构件 (质心 − 关节点) × m·g · 轴向。
    驱动要提供的力矩 = −τ"""
    import mujoco
    data = mujoco.MjData(model)
    data.qpos[:] = qpos
    mujoco.mj_kinematics(model, data)
    mujoco.mj_comPos(model, data)
    out = {}
    for j in range(model.njnt):
        if model.jnt_type[j] != 3:
            continue
        b0 = model.jnt_bodyid[j]
        sub = [b for b in range(model.nbody) if _is_descendant(model, b, b0)]
        p, a = data.xanchor[j], data.xaxis[j]
        tq = sum(np.cross(data.xipos[b] - p, np.array([0, 0, -g]) * model.body_mass[b]) for b in sub)
        out[mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, j)] = float(np.dot(tq, a))
    return out


def _is_descendant(model, b, anc):
    while b > 0:
        if b == anc:
            return True
        b = model.body_parentid[b]
    return anc == 0
