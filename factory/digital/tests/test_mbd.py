# -*- coding: utf-8 -*-
"""第 12 轮 运动与动力分析：标准题（单摆周期、机械臂重力矩、动态力矩与逆动力学互核）、计算服务的动力学任务。
机器人模型要 Menagerie（WQ_MENAGERIE，CI 用 deploy/fetch_menagerie.sh 取）；没有就跳过机器人的几项。"""
import math
import os
import re
import time
from pathlib import Path

import numpy as np
import pytest

mujoco = pytest.importorskip("mujoco")

from cae import mbd  # noqa: E402
from cae import mbd_models as MM  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
HAS_MEN = os.path.exists(os.path.join(MM.MENAGERIE, MM.ROBOTS["B-ARM-UR5E"][0]))
need_men = pytest.mark.skipif(not HAS_MEN, reason="没有 Menagerie 模型（WQ_MENAGERIE）")

PENDULUM = """<mujoco><worldbody><body name="rod"><joint name="pivot" type="hinge" axis="0 1 0"/>
<inertial pos="0 0 -0.5" mass="1" diaginertia="0.08333333 0.08333333 1e-6"/>
<geom type="capsule" fromto="0 0 0 0 0 -1" size="0.01" mass="0"/></body></worldbody></mujoco>"""
POSE = {"shoulder_pan_joint": 0.3, "shoulder_lift_joint": -1.2, "elbow_joint": 1.0, "wrist_1_joint": -0.6,
        "wrist_2_joint": 0.4, "wrist_3_joint": 0.0}


def test_pendulum_period():
    amp = 0.05
    s, ch, an = mbd.simulate(mbd.load_spec(xml=PENDULUM), {"duration_s": 10, "initial": {"pivot": amp}, "sample_hz": 200, "dt": 1e-4})
    q, t = ch["q.pivot"], ch["t"]
    z = [t[i] - q[i] * (t[i + 1] - t[i]) / (q[i + 1] - q[i]) for i in range(len(q) - 1) if q[i] > 0 >= q[i + 1]]
    T = float(np.mean(np.diff(z)))
    theory = 2 * math.pi * math.sqrt((1 / 3) / (9.81 * 0.5)) * (1 + amp ** 2 / 16)
    assert abs(T - theory) / theory < 0.01
    assert an["pos"].shape[1] == 1 and len(an["t"]) > 400
    # 铰点反力：静止下垂时 ≈ m·g（摆动很小）
    assert abs(ch["rf.rod.abs"][0] - 9.81) / 9.81 < 0.01


def test_setup_errors():
    with pytest.raises(mbd.SetupError, match="没有关节"):
        mbd.simulate(mbd.load_spec(xml=PENDULUM), {"drives": [{"joint": "nope", "kind": "hold"}]})
    with pytest.raises(mbd.SetupError, match="最多"):
        mbd.simulate(mbd.load_spec(xml=PENDULUM), {"duration_s": 120})
    with pytest.raises(mbd.SetupError, match="两个驱动"):
        mbd.simulate(mbd.load_spec(xml=PENDULUM), {"drives": [{"joint": "pivot", "kind": "hold"}, {"joint": "pivot", "kind": "hold"}]})


def test_menagerie_pin_matches_library():
    pin = (REPO / "library" / "vendor" / "menagerie.yaml").read_text(encoding="utf-8")
    assert MM.MENAGERIE_COMMIT in pin
    sh = (REPO / "factory" / "deploy" / "fetch_menagerie.sh").read_text(encoding="utf-8")
    assert MM.MENAGERIE_COMMIT in sh
    assert sorted(re.search(r'DIRS="([^"]+)"', sh).group(1).split()) == MM.MENAGERIE_DIRS


@need_men
def test_ur5e_gravity_torque_matches_hand_calc():
    pay = [{"body": "wrist_3_link", "mass": 3, "pos": [0, 0.1, 0]}]
    s, ch, _ = mbd.simulate(mbd.load_spec(path=MM.robot_path("B-ARM-UR5E")),
                            {"duration_s": 1.0, "initial": POSE, "payloads": pay, "drives": [{"joint": j, "kind": "hold"} for j in POSE]})
    model, _ = mbd.build(mbd.load_spec(path=MM.robot_path("B-ARM-UR5E")), {"payloads": pay})
    qp = np.zeros(model.nq)
    for j, v in POSE.items():
        qp[model.jnt_qposadr[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, j)]] = v
    g = mbd.gravity_torques(model, qp)
    for j in ("shoulder_lift_joint", "elbow_joint", "wrist_1_joint"):
        assert abs(ch["drive." + j][-1] + g[j]) / abs(g[j]) < 0.02
    assert s["tracking_error_max"] < math.radians(0.05)


@need_men
def test_ur5e_move_torque_matches_inverse_dynamics():
    """点到点搬运：驱动力矩与按实际运动做逆动力学（mj_inverse）的结果一致"""
    pay = [{"body": "wrist_3_link", "mass": 3, "pos": [0, 0.1, 0]}]
    drives = [{"joint": "shoulder_pan_joint", "kind": "move", "to": 1.8, "t0": 0.2, "t1": 1.7},
              {"joint": "shoulder_lift_joint", "kind": "move", "to": -0.6, "t0": 0.2, "t1": 1.7}] + \
             [{"joint": j, "kind": "hold"} for j in ("elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint")]
    setup = {"duration_s": 2.0, "initial": POSE, "payloads": pay, "drives": drives, "sample_hz": 200}
    s, ch, an = mbd.simulate(mbd.load_spec(path=MM.robot_path("B-ARM-UR5E")), setup)
    model, _ = mbd.build(mbd.load_spec(path=MM.robot_path("B-ARM-UR5E")), setup)
    data = mujoco.MjData(model)
    names = list(POSE)
    jid = [mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, j) for j in names]
    worst = 0.0
    peak = max(abs(ch["drive.shoulder_lift_joint"]))
    for k in range(5, len(ch["t"]) - 5, 7):
        for j, n in zip(jid, names):
            data.qpos[model.jnt_qposadr[j]] = ch["q." + n][k]
            data.qvel[model.jnt_dofadr[j]] = ch["qd." + n][k]
            data.qacc[model.jnt_dofadr[j]] = ch["qdd." + n][k]
        mujoco.mj_inverse(model, data)
        for j, n in zip(jid, names):
            worst = max(worst, abs(data.qfrc_inverse[model.jnt_dofadr[j]] - ch["drive." + n][k]))
    assert worst / peak < 0.02
    d = {x["joint"]: x for x in s["drives"]}
    assert d["shoulder_pan_joint"]["speed_max"] > 1.0 and d["shoulder_lift_joint"]["peak"] > 40
    assert abs(ch["q.shoulder_pan_joint"][-1] - 1.8) < 1e-3


@need_men
def test_service_runs_dynamics_job(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from cae import service
    monkeypatch.setattr(service, "DATA", str(tmp_path))
    with TestClient(service.app) as c:
        assert "B-ARM-UR5E" in [r["id"] for r in c.get("/mbd/robots").json()["robots"]]
        info = c.post("/mbd/models/load", json={"source": "library", "id": "B-ARM-UR5E"}).json()
        assert len(info["joints"]) == 6 and c.get("/mbd/models/{}/model.glb".format(info["key"])).content[:4] == b"glTF"
        assert c.post("/mbd/jobs", json={"model": {"source": "library", "id": "B-ARM-UR5E"},
                                         "setup": {"drives": [{"joint": "x", "kind": "hold"}]}}).status_code == 400
        j = c.post("/mbd/jobs", json={"model": {"source": "library", "id": "B-ARM-UR5E"}, "owner": "7", "factory": "wq_test",
                                      "setup": {"duration_s": 0.5, "initial": POSE, "drives": [{"joint": n, "kind": "hold"} for n in POSE]}}).json()
        for _ in range(240):
            j = c.get("/jobs/" + j["id"]).json()
            if j["status"] in ("done", "failed"):
                break
            time.sleep(0.5)
        assert j["status"] == "done", j.get("error")
        ser = service.read_series(os.path.join(str(tmp_path), "jobs", j["id"], "series.bin"))
        assert "drive.elbow_joint" in ser and len(ser["t"]) >= 50
        assert c.get("/jobs/{}/anim.bin".format(j["id"])).content[:4] == b"WQA1"
        assert [x["id"] for x in c.get("/jobs", params={"kind": "mbd"}).json()["jobs"]] == [j["id"]]
        assert c.get("/jobs", params={"kind": "fea"}).json()["jobs"] == []
        # 上传：单个 MJCF
        up = c.post("/mbd/models/upload", params={"name": "pend.xml"}, content=PENDULUM.encode()).json()
        assert up["joints"][0]["name"] == "pivot"
        assert c.post("/mbd/models/upload", params={"name": "x.txt"}, content=b"hello").status_code == 422
