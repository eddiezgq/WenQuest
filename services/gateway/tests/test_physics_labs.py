"""第 41 轮：物理仿真实验页（view: "physics"）带三维引擎、书中机器人的 MJCF，安全策略只放开本站的 MuJoCo 文件。"""
from app.production import labs

PHYS = (labs.KIT / "demo_physics_ur5e.js").read_text(encoding="utf-8")
PLAIN = labs.physics_example()


def test_physics_page_embeds_engine_robot_and_its_policy():
    page = labs.page([("41.2", PHYS)], course=["c", "c"], chapter=["第41章", "Chapter 41"],
                     models={"B-ARM-UR5E": {"entry": {}, "glb": "", "motion": []}, "B-ARM-PANDA": {"entry": {}, "glb": "", "motion": []}},
                     mjcf={"ur5e": "<mujoco><!--TOOL--></mujoco>", "fr3": "<mujoco/>"})
    assert 'data-physics="1"' in page and "WQ3D" in page
    assert "window.WQ_MJCF" in page and '"ur5e"' in page and '"fr3"' not in page.split("window.WQ_MJCF", 1)[1][:200]
    assert labs.PHYSICS_CSP in page and labs.csp_for(page) == labs.PHYSICS_CSP
    assert "'wasm-unsafe-eval'" in labs.PHYSICS_CSP and "connect-src 'self' https://wq.local" in labs.PHYSICS_CSP
    assert '"B-ARM-PANDA"' not in page          # only the models the lab names


def test_ordinary_labs_keep_the_closed_policy():
    page = labs.page([("2.1", PLAIN)], course=["c", "c"], chapter=["第2章", "Chapter 2"])
    assert 'data-physics' not in page and labs.csp_for(page) == labs.CSP and "connect-src 'none'" in labs.CSP


def test_physics_lab_code_passes_the_static_check():
    assert labs.static_problems(PHYS) == []
    assert labs.static_problems((labs.KIT / "demo_physics.js").read_text(encoding="utf-8")) == []
