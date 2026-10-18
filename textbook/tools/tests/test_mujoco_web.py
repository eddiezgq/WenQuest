"""第 41 轮：浏览器 MuJoCo（npm @mujoco/mujoco，物理仿真实验用）与教材程序用的 Python 版 mujoco 版本相同、结果逐位一致。
书里的数字由 Python 程序算出，学生在网页实验里看到的必须是同一个结果。"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
PKG = TOOLS / "node_modules" / "@mujoco" / "mujoco"
XML = """<mujoco><option timestep="0.001" integrator="RK4" gravity="0 0 0"><flag energy="enable"/></option>
<worldbody><body name="box" pos="0 0 0.8"><freejoint/><geom type="box" size="0.2 0.12 0.05" mass="6"/></body>
<body name="link" pos="0 1 1"><joint name="j" type="hinge" axis="0 1 0"/><geom type="capsule" fromto="0 0 0 0.5 0 0" size="0.03" mass="1"/></body>
</worldbody></mujoco>"""
STEPS = 5000


def test_browser_build_matches_python():
    mujoco = pytest.importorskip("mujoco")
    if not (PKG / "mujoco.js").exists() or not shutil.which("node"):
        pytest.skip("npm ci in textbook/tools first")
    js = f"""import load from {json.dumps((PKG / 'mujoco.js').as_uri())};
const mj = await load(); const m = mj.MjModel.from_xml_string({json.dumps(XML)}); const d = new mj.MjData(m);
d.qvel[3] = 0.08; d.qvel[4] = 8; d.qvel[5] = 0.08;
for (let i = 0; i < {STEPS}; i++) mj.mj_step(m, d);
console.log(JSON.stringify({{v: mj.mj_version(), qpos: Array.from(d.qpos), qvel: Array.from(d.qvel), e: Array.from(d.energy)}}));"""
    out = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True, timeout=120, check=True).stdout
    web = json.loads(out.strip().splitlines()[-1])
    m = mujoco.MjModel.from_xml_string(XML)
    d = mujoco.MjData(m)
    d.qvel[3:6] = [0.08, 8, 0.08]
    for _ in range(STEPS):
        mujoco.mj_step(m, d)
    assert web["v"] == mujoco.mj_version(), "the npm package and the Python package must be the same MuJoCo version"
    assert web["qpos"] == list(d.qpos) and web["qvel"] == list(d.qvel) and web["e"] == list(d.energy)


def test_book_ur5e_gravity_terms_match_python():
    """The book's web UR5e (models/mjcf/ur5e.xml): the browser's gravity torques equal Python's at a lab pose."""
    mujoco = pytest.importorskip("mujoco")
    if not (PKG / "mujoco.js").exists() or not shutil.which("node"):
        pytest.skip("npm ci in textbook/tools first")
    text = (TOOLS.parent / "robotics" / "models" / "mjcf" / "ur5e.xml").read_text(encoding="utf-8")
    tool = '<body name="payload" pos="0 0.15 0"><geom type="box" size="0.05 0.05 0.05" mass="5"/></body>'
    xml = text.replace("<!--TOOL-->", tool).replace("<!--OPTION-->", "").replace("<!--WORLD-->", "").replace("<!--ACTUATOR-->", "")
    q = [0.3, -0.7, 1.1, -1.5708, 0.4, 0.0]
    js = f"""import load from {json.dumps((PKG / 'mujoco.js').as_uri())};
const mj = await load(); const m = mj.MjModel.from_xml_string({json.dumps(xml)}); const d = new mj.MjData(m);
{json.dumps(q)}.forEach((v, i) => {{ d.qpos[i] = v; }}); mj.mj_forward(m, d);
console.log(JSON.stringify(Array.from(d.qfrc_bias)));"""
    out = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True, timeout=120, check=True).stdout
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    d.qpos[:6] = q
    mujoco.mj_forward(m, d)
    assert json.loads(out.strip().splitlines()[-1]) == list(d.qfrc_bias)
