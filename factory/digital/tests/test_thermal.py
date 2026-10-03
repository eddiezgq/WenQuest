# -*- coding: utf-8 -*-
"""第 14 轮 热分析：标准题与解析解对比（平壁导热、圆柱肋片、集总参数冷却、热应力、热伸长），计算服务的热分析任务。"""
import math
import os
import tempfile
import time

import numpy as np
import pytest

pytest.importorskip("gmsh")
bd = pytest.importorskip("build123d")
import shutil  # noqa: E402

if not shutil.which(os.environ.get("WQ_CCX", "ccx")):
    pytest.skip("没有 CalculiX（ccx）", allow_module_level=True)

from cae import geometry as G  # noqa: E402
from cae import materials as M  # noqa: E402
from cae import thermal as TH  # noqa: E402


def step(shape):
    f = tempfile.mktemp(suffix=".step")
    bd.export_step(shape, f)
    data = open(f, "rb").read()
    os.remove(f)
    return data


def planes_at(faces, axis, val):
    return [f["id"] for f in faces if f["kind"] == "plane" and abs(f["center"][axis] - val) < 1e-6]


@pytest.fixture(scope="module")
def bar():
    s = step(bd.Box(100, 10, 10, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)))
    return s, G.faces(s)[0]


def test_materials_have_thermal_properties():
    for m in M.public():
        assert m["k_w_mk"] > 0 and m["c_j_kgk"] > 0 and m["alpha_1e6"] > 0 and any("热物性" in x for x in m["sources"])
    assert M.get("45-QT")["k_w_mk"] == pytest.approx(49.8) and M.FILM[0]["h"] == pytest.approx(8.15)


def test_plane_wall_conduction(bar):
    """一维导热：一端面输入 10 W（热流 10⁵ W/m²），另一端 20 ℃：T = 20 + q·L/k"""
    s, F = bar
    st, surf, _ = TH.solve(s, {"material": M.get("45-QT"), "mesh": {"size_mm": 3}, "thermal": [
        {"type": "heat_flux", "faces": planes_at(F, 0, 0), "power_w": 10},
        {"type": "temperature", "faces": planes_at(F, 0, 100), "value_c": 20}]})
    assert st["t_max_c"] == pytest.approx(20 + 1e5 * 0.1 / 49.8, rel=0.01)
    assert len(surf["temp"]) == len(surf["positions"])


def test_pin_fin():
    """圆柱肋片 Ø10×100（45 钢），根部 100 ℃，其余表面 h = 25、20 ℃：散热量与肋片公式（端部对流）比"""
    s = step(bd.Cylinder(5, 100, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)))
    F = G.faces(s)[0]
    st, _, _ = TH.solve(s, {"material": M.get("45-QT"), "mesh": {"size_mm": 3}, "thermal": [
        {"type": "temperature", "faces": planes_at(F, 2, 0), "value_c": 100},
        {"type": "convection", "faces": "rest", "h_w_m2k": 25, "t_inf_c": 20}]})
    h, k, D, L = 25, 49.8, 0.01, 0.1
    P, A = math.pi * D, math.pi * D * D / 4
    m = math.sqrt(h * P / (k * A))
    r = h / (m * k)
    Q = math.sqrt(h * P * k * A) * 80 * (math.sinh(m * L) + r * math.cosh(m * L)) / (math.cosh(m * L) + r * math.sinh(m * L))
    assert st["heat_out_convection_w"] == pytest.approx(Q, rel=0.03)


def test_lumped_cooling():
    """10 mm 铝块从 120 ℃ 在 20 ℃ 空气里冷却（h = 50，Bi ≈ 0.003）：θ = θ₀·exp(−t/τ)，τ = ρcV/(hA)"""
    s = step(bd.Box(10, 10, 10))
    al = M.get("6061-T6")
    st, _, _ = TH.solve(s, {"material": al, "mesh": {"size_mm": 3}, "transient": {"duration_s": 300, "steps": 30, "t0_c": 120},
                            "thermal": [{"type": "convection", "faces": "rest", "h_w_m2k": 50, "t_inf_c": 20}]})
    tau = al["density"] * 1000 * al["c_j_kgk"] * (0.01 / 6) / 50
    ser = st["series"]
    assert ser[0] == [0.0, 120.0, 120.0] and ser[-1][0] == pytest.approx(300)
    for t, _, tm in ser[1:]:                       # 误差按初始温差算：后向欧拉每步 1.5 s，偏差 < 1% θ₀
        assert abs((tm - 20) - 100 * math.exp(-t / tau)) < 1.0
    t, _, tm = min(ser, key=lambda r: abs(r[0] - tau))    # 一个时间常数处：θ/θ₀ = e⁻¹，相对误差 < 3%
    assert (tm - 20) == pytest.approx(100 * math.exp(-t / tau), rel=0.03)


def test_thermal_stress_and_expansion():
    """热—结构耦合：两端固定的长杆均匀升温 100 ℃，中段 σ = E·α·ΔT；一端固定时自由伸长 α·L·ΔT"""
    s = step(bd.Box(300, 10, 10, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)))
    F = G.faces(s)[0]
    m = M.get("45-QT")
    ends = planes_at(F, 0, 0) + planes_at(F, 0, 300)
    st, _, aux = TH.solve(s, {"analysis": "thermo_mech", "material": m, "mesh": {"size_mm": 4}, "ref_temp_c": 20,
                              "thermal": [{"type": "temperature", "faces": "rest", "value_c": 120}],
                              "loads": [{"type": "fixed", "faces": ends}]})
    mid = [aux["vm"][n] for n, p in aux["nodes"].items() if abs(p[0] - 150) < 2 and n in aux["vm"]]
    assert np.mean(mid) == pytest.approx(m["E_mpa"] * m["alpha_1e6"] * 1e-6 * 100, rel=0.02)
    assert st["safety_factor"] > 0
    st, _, aux = TH.solve(s, {"analysis": "thermo_mech", "material": m, "mesh": {"size_mm": 4}, "ref_temp_c": 20,
                              "thermal": [{"type": "temperature", "faces": "rest", "value_c": 120}],
                              "loads": [{"type": "fixed", "faces": planes_at(F, 0, 0)}]})
    U, P = aux["U"], aux["nodes"]
    far = np.mean([U[n][0] for n, p in P.items() if abs(p[0] - 300) < 1e-6 and n in U])
    half = np.mean([U[n][0] for n, p in P.items() if abs(p[0] - 150) < 2 and n in U])
    assert far - half == pytest.approx(m["alpha_1e6"] * 1e-6 * 150 * 100, rel=0.01)


def test_errors():
    s = step(bd.Box(10, 10, 10))
    with pytest.raises(ValueError):
        TH.solve(s, {"material": M.get("45-QT"), "thermal": [{"type": "heat_body", "power_w": 5}]})


def test_service_thermal_job(tmp_path, monkeypatch, bar):
    from fastapi.testclient import TestClient
    from cae import service
    monkeypatch.setattr(service, "DATA", str(tmp_path))
    s, _ = bar
    with TestClient(service.app) as c:
        assert c.get("/materials").json()["films"][0]["id"] == "air-still"
        g = c.post("/geometry", content=s).json()
        x0 = planes_at(g["faces"], 0, 0)
        assert c.post("/jobs", json={"step_sha": g["sha"], "setup": {"analysis": "thermal", "material_id": "45-QT",
                                                                    "thermal": [{"type": "heat_body", "power_w": 5}]}}).status_code == 400
        j = c.post("/jobs", json={"step_sha": g["sha"], "factory": "wq_test", "setup": {
            "analysis": "thermal", "material_id": "45-QT", "mesh": {"size_mm": 4},
            "thermal": [{"type": "heat_body", "power_w": 5}, {"type": "temperature", "faces": x0, "value_c": 20}]}}).json()
        for _ in range(240):
            j = c.get("/jobs/" + j["id"]).json()
            if j["status"] in ("done", "failed"):
                break
            time.sleep(0.5)
        assert j["status"] == "done", j.get("error")
        # 体积均匀发热 q、一端定温：T_max = 20 + q·L²/(2k)，q = 5 W / 10⁻⁵ m³
        assert j["stats"]["t_max_c"] == pytest.approx(20 + 5e5 * 0.01 / (2 * 49.8), rel=0.02)
        surf = service.read_surface(os.path.join(str(tmp_path), "jobs", j["id"], "surface.bin"))
        assert surf["temp"].max() == pytest.approx(j["stats"]["t_max_c"], rel=1e-3)
