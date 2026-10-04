# -*- coding: utf-8 -*-
"""第 16 轮：流体分析 → 温度场的对流行；AI 一句话填表和结果解释（规则部分，不需要 OpenFOAM）"""
from hub import cfd_ai
from hub.cfd_api import thermal_rows


FACES = [{"id": 1, "area_mm2": 45006, "p_pa": 12.3, "h_w_m2k": 16.9, "heat_w": 30.0},
         {"id": 2, "area_mm2": 123017, "p_pa": -8.1, "h_w_m2k": 20.1, "heat_w": 111.0},
         {"id": 4, "area_mm2": 123017, "p_pa": -9.1, "h_w_m2k": 20.2, "heat_w": 112.0},
         {"id": 5, "area_mm2": 61500, "p_pa": 0.1, "h_w_m2k": 3.0, "heat_w": 5.0},
         {"id": 7, "area_mm2": 900, "p_pa": 0.0, "h_w_m2k": None, "heat_w": None}]


def test_thermal_rows_merge_and_skip():
    ex = {"thermal": [{"type": "heat_flux", "faces": [9], "q_w_m2": 100.0}, {"type": "convection", "faces": [1], "h_w_m2k": 17.45}],
          "groups": {"bottom": [5], "inner": [9]}}
    rows = thermal_rows(FACES, 25.0, ex)
    assert rows[0]["type"] == "heat_flux"                       # 示例的发热保留，查表的对流行不保留
    conv = [r for r in rows if r["type"] == "convection"]
    assert all(r["source"] == "cfd" and r["t_inf_c"] == 25.0 for r in conv)
    assert [r["faces"] for r in conv] == [[2, 4], [1]]          # 20.1 和 20.2 都取 20.0，合成一行；底面 5、没有 h 的 7 跳过
    assert conv[0]["h_w_m2k"] == 20.0 and conv[1]["h_w_m2k"] == 17.0
    assert [r["faces"] for r in thermal_rows(FACES, 20.0)] == [[2, 4], [1], [5]]   # 一般零件：每个有 h 的面都给对流


def test_ai_setup_rules():
    r = cfd_ai.rules_setup("轴端风扇 5 m/s 沿长边吹，空气 25 ℃，箱体表面 70 ℃，放在机座上", bbox=[0, 0, 0, 150, 410, 300])
    f = r["form"]
    assert f == {"velocity_ms": 5.0, "air_t_c": 25.0, "wall_t_c": 70.0, "heat": True, "ground": True, "direction": "+y"}
    assert not r["unmatched"]
    r = cfd_ai.rules_setup("36 km/h 从下往上，只算阻力")
    assert r["form"]["velocity_ms"] == 10.0 and r["form"]["direction"] == "+z" and r["form"]["heat"] is False
    assert cfd_ai.rules_setup("风量 30 CFM")["unmatched"]           # 看不懂的带数字的话交给模型（没有模型就提示学生）


def test_ai_explain_rules():
    st = {"velocity_ms": 5, "direction": "+x", "L_char_mm": 410, "Re": 131271, "turbulence": "kOmegaSST", "drag_n": 0.683,
          "drag_pressure_n": 0.689, "drag_friction_n": -0.006, "Cd": 1.03, "frontal_m2": 0.045, "q_dyn_pa": 14.8,
          "heat_w": 357.6, "h_mean": 20.0, "wall_t_c": 70, "air_t_c": 25, "converged": False}
    t = cfd_ai.explain(None, st, FACES)
    assert t["engine"] == "rules"
    assert "湍流" in t["text"] and "压差阻力" in t["text"] and "面 4" in t["text"] and "面 5" in t["text"] and "收敛" in t["text"]


def test_h_rad():
    from hub.cfd_api import h_rad
    assert abs(h_rad(70, 25) - 6.76) < 0.05                    # 涂漆铸铁 70 ℃ 对 25 ℃ 空气
    assert h_rad(70, 25, eps=0.1) < 1
