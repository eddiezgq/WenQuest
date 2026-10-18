"""What the digital factory's CAE is asked to compute for a cam system (round 39, step 4d), and how its answers are
compared with this kernel. Plain code: builds models and setups, reads results; the calls themselves are made by the
cam service (cae_bridge.py), never from here.

Multibody dynamics (MuJoCo, digital factory `cae/mbd.py`): one body per moving member, each on its own joint —
  camshaft: hinge about x, driven by a trapezoidal "move" (start, run, brake as camkit.system.motion_time);
  every cam output: a hinge (angle) or a slide (stroke, m), coupled to the camshaft by a table (the cam's motion
  program; `cae/mech_mjcf.table_fn`), with its inertia, mass and gravity.
  A translating output given as a lever (an angle program with "radius"): a slide along z moving radius·ψ.
The camshaft's drive torque from MuJoCo is compared with camkit.system's rigid model.

Finite elements (Gmsh + CalculiX): the tool-changer arm from camkit.atc_arm; the bore fixed; on each gripper's fork the
tool's inertia force (tangential m·α·R, centrifugal m·ω²·R) and weight at the instant of the largest force in the
cycle; fatigue: one tool change = one block, the force over the cycle scaled to that instant.
"""

from __future__ import annotations

import math

import numpy as np

from camkit import system as S


class CaeSetupError(ValueError):
    pass


def _inertial(mass, J, axis):
    """Inertia J about the joint's axis; the other two (which do not move) half of it."""
    d = [J / 2, J / 2, J / 2]
    d["xyz".index(axis)] = J
    return f'<inertial pos="0 0 0" mass="{mass:.6g}" diaginertia="{d[0]:.6g} {d[1]:.6g} {d[2]:.6g}"/>'


def mbd_model(system: dict) -> tuple[str, dict, dict]:
    """(MJCF xml, MBD setup, notes) for a cam system."""
    r = S.analyse(system)
    cs = system.get("camshaft") or {}
    a1, a2 = float(cs.get("start_deg") or 0), float(cs.get("stop_deg") or 0)
    if abs(a1 - a2) > 1e-9:
        raise CaeSetupError("the dynamics model needs the same starting and braking angle")
    T = float(r["cycle"])
    w = float(np.max(r["thd"]))
    ta = 2 * math.radians(a1) / w if a1 > 0 else 0.0
    J_cs = max(float(cs.get("J") or 0), 1e-4)
    bodies = [f'<body name="camshaft" pos="0 0 0">{_inertial(1.0, J_cs, "x")}'
              '<joint name="camshaft" type="hinge" axis="1 0 0" damping="0"/>'
              '<geom type="cylinder" size="0.02 0.15" euler="0 90 0" mass="0" rgba="0.6 0.6 0.65 1"/></body>']
    couplings = []
    notes = {"outputs": []}
    deg = np.arange(0, 360, 0.5)
    for k, c in enumerate(system.get("cams") or []):
        cam = next(p for p in r["cams"] if p["id"] == c["id"])
        prog = cam["program"]
        o = c.get("output") or {}
        s_tab = prog.eval(np.radians(deg))[0]
        x = 0.4 * (k + 1)
        if prog.unit == "rad" and o.get("radius") and o.get("m"):
            # a lever moving a mass up and down: a slide along z, stroke = −radius·ψ (a rise pulls down)
            m = float(o["m"])
            R = float(o["radius"]) * 1e-3
            bodies.append(f'<body name="{c["id"]}" pos="{x} 0 0"><inertial pos="0 0 0" mass="{m:.6g}" '
                          f'diaginertia="0.01 0.01 0.01"/><joint name="{c["id"]}" type="slide" axis="0 0 1"/>'
                          f'<geom type="box" size="0.04 0.04 0.04" mass="0" rgba="0.9 0.7 0.1 1"/></body>')
            couplings.append({"driver": "camshaft", "follower": c["id"], "fn": "table",
                              "params": {"deg": deg.tolist(), "value": (-R * s_tab).tolist(),
                                         "advance": -R * prog.advance}})
            notes["outputs"].append({"id": c["id"], "joint": "slide", "mass": m, "radius_m": R})
        elif prog.unit == "rad":
            J = float(o.get("J") or 0)
            if not J > 0:
                raise CaeSetupError(f"cam {c['id']}: give the inertia of what it turns")
            bodies.append(f'<body name="{c["id"]}" pos="{x} 0 0">{_inertial(1e-3, J, "z")}'
                          f'<joint name="{c["id"]}" type="hinge" axis="0 0 1"/>'
                          f'<geom type="box" size="0.15 0.02 0.01" mass="0" rgba="0.2 0.5 0.8 1"/></body>')
            couplings.append({"driver": "camshaft", "follower": c["id"], "fn": "table",
                              "params": {"deg": deg.tolist(), "value": s_tab.tolist(), "advance": prog.advance}})
            notes["outputs"].append({"id": c["id"], "joint": "hinge", "J": J})
        else:
            m = float(o.get("m") or 0)
            bodies.append(f'<body name="{c["id"]}" pos="{x} 0 0"><inertial pos="0 0 0" mass="{m:.6g}" '
                          f'diaginertia="0.01 0.01 0.01"/><joint name="{c["id"]}" type="slide" axis="0 0 1"/>'
                          f'<geom type="box" size="0.03 0.03 0.03" mass="0"/></body>')
            couplings.append({"driver": "camshaft", "follower": c["id"], "fn": "table",
                              "params": {"deg": deg.tolist(), "value": (s_tab * 1e-3).tolist(),
                                         "advance": prog.advance * 1e-3}})
            notes["outputs"].append({"id": c["id"], "joint": "slide", "mass": m})
    xml = ('<mujoco model="wenquest-cam-system"><compiler angle="radian"/>'
           '<option timestep="0.0005" gravity="0 0 -9.81" integrator="implicitfast"/>'
           '<worldbody><light pos="0 0 3"/>' + "".join(bodies) + "</worldbody></mujoco>")
    setup = {"duration_s": T, "gravity": True, "sample_hz": 200,
             "drives": [{"joint": "camshaft", "kind": "move", "to": 2 * math.pi, "t0": 0, "t1": T,
                         "accel": max(0.01, min(0.5, ta / T)) if ta > 0 else 0.01}],
             "couplings": couplings}
    notes.update(cycle_s=T, run_rad_s=w)
    return xml, setup, notes


def compare_torque(system: dict, values: list[float], duration_s: float, friction: bool = False) -> dict:
    """MuJoCo's camshaft drive torque against camkit's rigid model over the same time axis."""
    sysd = dict(system)
    if not friction:
        sysd["camshaft"] = dict(system.get("camshaft") or {}, friction=0)
    r = S.analyse(sysd)
    v = np.asarray(values, float)
    t = np.linspace(0, duration_s, len(v))
    mine = np.interp(t, r["t"], r["T_cs"])
    peak = float(np.max(np.abs(mine)))
    diff = v - mine
    return {"t": t.tolist(), "mbd": v.tolist(), "camkit": mine.tolist(), "peak_mbd": float(np.max(np.abs(v))),
            "peak_camkit": peak, "max_diff": float(np.max(np.abs(diff))),
            "rel_rms": float(np.sqrt(np.mean(diff**2)) / max(peak, 1e-12))}


def arm_loads(system: dict, cam_id: str, tool_mass: float, R_tip: float) -> dict:
    """Inertia force of one tool on a gripper over the cycle (arm along x, turning about z): tangential m·α·R and
    centrifugal m·ω²·R; the instant of the largest force."""
    r = S.analyse(system)
    cam = next((p for p in r["cams"] if p["id"] == cam_id), None)
    if cam is None or cam["unit"] != "rad":
        raise CaeSetupError("choose the cam that turns the arm")
    R = R_tip * 1e-3
    w = cam["s1"] * r["thd"]
    alpha = cam["acc"]
    Ft = tool_mass * alpha * R
    Fc = tool_mass * w * w * R
    F = np.hypot(Ft, Fc)
    i = int(np.argmax(F))
    return {"t": r["t"], "F": F, "Ft": Ft, "Fc": Fc, "i": i, "Ft_max": float(Ft[i]), "Fc_max": float(Fc[i]),
            "F_max": float(F[i]), "deg": float(r["deg"][i]), "cycle_s": float(r["cycle"])}


def pick_faces(faces: list[dict], bore: float, r_fork: float, R_tip: float, tol: float = 0.05):
    """The bore (a cylinder of radius `bore` about z through the origin) and the two forks (cylinders of radius
    r_fork about axes at x = ±R_tip). Returns (bore ids, {+1: ids, −1: ids})."""
    def cyl(f, radius):
        return f.get("radius_mm") is not None and abs(f["radius_mm"] - radius) <= tol
    b = [f["id"] for f in faces if cyl(f, bore) and abs(f.get("axis_origin", [9, 9, 9])[0]) < 1
         and abs(f.get("axis_origin", [9, 9, 9])[1]) < 1]
    forks = {1: [], -1: []}
    for f in faces:
        if cyl(f, r_fork):
            x = f.get("axis_origin", [0, 0, 0])[0]
            if abs(abs(x) - R_tip) < 1:
                forks[1 if x > 0 else -1].append(f["id"])
    if not b or not forks[1] or not forks[-1]:
        raise CaeSetupError("could not find the bore and both forks on the arm model")
    return b, forks


def arm_fea_setup(faces: list[dict], arm: dict, loads: dict, tool_mass: float, material_id: str,
                  mesh_mm: float | None = None) -> dict:
    """FEA setup for the arm: bore fixed; on each fork the tool's inertia force and weight at the worst instant.
    Gripper at +x: tangential +y·sign(α), centrifugal +x; at −x: −y·sign(α), −x."""
    b, forks = pick_faces(faces, arm["bore"], arm["r_fork"], arm["R_tip"])
    g = 9.81 * tool_mass
    out = [{"type": "fixed", "faces": b}]
    for sg in (1, -1):
        vec = [sg * loads["Fc_max"], sg * loads["Ft_max"], -g]
        out.append({"type": "force", "faces": forks[sg], "vector_n": [round(v, 3) for v in vec]})
    size = mesh_mm or max(2.0, min(6.0, arm["thickness"] / 6))  # a few elements through the thickness
    return {"material_id": material_id, "loads": out, "mesh": {"size_mm": size}, "analysis": "static"}


def fatigue_body(loads: dict, changes_per_day: float, surface: str = "fine_turned") -> dict:
    """One tool change = one block; the block lasts a day divided by the tool changes per day, so the life in hours
    reads directly. The series is the force over the cycle as a multiple of the computed (worst) instant."""
    if not changes_per_day or changes_per_day <= 0:
        raise CaeSetupError("give the tool changes per day")
    F = np.asarray(loads["F"])
    series = (F / max(loads["F_max"], 1e-12)).tolist()
    series = series[:: max(1, len(series) // 2000)]
    return {"ref_load": 1.0, "series": series + [0.0], "block_seconds": 86400.0 / changes_per_day, "surface": surface,
            "size_factor": 0.85, "kf": 1.0, "haibach": True, "label": "one tool change"}
