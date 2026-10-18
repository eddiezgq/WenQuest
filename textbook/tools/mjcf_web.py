"""网页版机器人 MJCF（第 41 轮）：由 MuJoCo Menagerie 的模型生成浏览器物理仿真实验用的精简模型。

    python3 mjcf_web.py <menagerie 目录>        # 写到 textbook/robotics/models/mjcf/

做了什么（物理参数一个不改）：
- 去掉全部网格（原版 UR5e 32 MB、FR3 57 MB，网页装不下）：可视几何删掉，外观用零件库的 glTF（节点名 = MJCF 的 body 名）；
- 网格做的碰撞几何换成胶囊：在原模型编译后的几何坐标系里，按顶点的主方向拟合（包住全部顶点）；原来就是简单形体的保留；
- 质量、惯量、关节、阻尼、执行器、关键帧照原样（各 body 都有显式 <inertial>，碰撞几何不计质量）；
- 留三个占位注释给实验拼模型：<!--OPTION-->（compiler 之后）、<!--WORLD-->（worldbody 末尾）、<!--TOOL-->（末端连杆里）、<!--ACTUATOR-->。
来源与许可证写在文件头；许可证原文一起复制。生成后检查：同一组关节角下，网页版与原版的重力项 qfrc_bias 逐位相同。
"""
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "textbook" / "robotics" / "models" / "mjcf"
COMMIT = "4d038b3feae26ec82b46a4d586379114012a8ac7"     # 与零件库 library/vendor/menagerie.yaml 相同
MODELS = {
    # 名字: (Menagerie 文件夹, 文件, 末端连杆, 许可证, 碰撞几何颜色)
    "ur5e": ("universal_robots_ur5e", "ur5e.xml", "wrist_3_link", "BSD-3-Clause（Copyright 2018 ROS Industrial Consortium）", "0.72 0.80 0.86 1"),
    "fr3": ("franka_fr3", "fr3.xml", "fr3_link7", "Apache-2.0（Franka Robotics GmbH）", "0.90 0.90 0.90 1"),
}


def capsule(verts: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Endpoints and radius of a capsule along the points' main direction that contains every point."""
    c = verts.mean(axis=0)
    _, _, vt = np.linalg.svd(verts - c, full_matrices=False)
    ax = vt[0]
    t = (verts - c) @ ax
    perp = np.linalg.norm((verts - c) - np.outer(t, ax), axis=1)
    r = float(perp.max())
    # shrink the segment so the end caps still contain the extreme points
    lo = min((t[i] + np.sqrt(max(r * r - perp[i] ** 2, 0.0))) for i in range(len(t)))
    hi = max((t[i] - np.sqrt(max(r * r - perp[i] ** 2, 0.0))) for i in range(len(t)))
    if hi < lo:
        lo = hi = (lo + hi) / 2
    return c + lo * ax, c + hi * ax, r


def mat(q: np.ndarray) -> np.ndarray:
    m = np.zeros(9)
    mujoco.mju_quat2Mat(m, q)
    return m.reshape(3, 3)


def build(name: str, men: Path) -> str:
    folder, file, tool, lic, rgba = MODELS[name]
    src = men / folder / file
    m = mujoco.MjModel.from_xml_path(str(src))
    tree = ET.parse(src)
    root = tree.getroot()
    asset = root.find("asset")
    if asset is not None:
        for e in list(asset):
            if e.tag == "mesh":
                asset.remove(e)
    world = root.find("worldbody")
    for light in world.iter("light"):
        pass
    for parent in list(world.iter()):
        for ch in list(parent):
            if ch.tag == "light":
                parent.remove(ch)
    # bodies whose mass came from their (visual) meshes get the compiled inertia written out, so nothing changes
    for body in world.iter("body"):
        if body.find("inertial") is None:
            bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, body.get("name"))
            if bid > 0 and m.body_mass[bid] > 0:
                ine = ET.Element("inertial", {"pos": " ".join(repr(float(x)) for x in m.body_ipos[bid]),
                                              "quat": " ".join(repr(float(x)) for x in m.body_iquat[bid]),
                                              "mass": repr(float(m.body_mass[bid])),
                                              "diaginertia": " ".join(repr(float(x)) for x in m.body_inertia[bid])})
                body.insert(0, ine)
    # compiled geom ids follow the document order of <geom> elements
    gid = 0
    for body in world.iter("body"):
        for g in [x for x in list(body) if x.tag == "geom"]:
            cls = g.get("class", "")
            is_mesh = g.get("mesh") is not None
            visual = cls == "visual" or (is_mesh and int(m.geom_contype[gid]) == 0 and int(m.geom_conaffinity[gid]) == 0)
            if visual:
                body.remove(g)
            elif is_mesh:
                mid = int(m.geom_dataid[gid])
                v0, nv = int(m.mesh_vertadr[mid]), int(m.mesh_vertnum[mid])
                verts = m.mesh_vert[v0:v0 + nv]                          # in the geom frame
                a, b, r = capsule(np.asarray(verts, dtype=float))
                R, p = mat(m.geom_quat[gid]), m.geom_pos[gid]
                A, B = R @ a + p, R @ b + p                               # in the body frame
                for k in ("mesh", "pos", "quat", "material"):
                    g.attrib.pop(k, None)
                g.set("type", "capsule")
                g.set("fromto", " ".join(f"{x:.5f}" for x in (*A, *B)))
                g.set("size", f"{r:.5f}")
                g.set("rgba", rgba)
            else:
                g.attrib.pop("material", None)
                g.set("rgba", rgba)
            gid += 1
    # visual default classes may set type="mesh": keep them harmless (no geom uses them now)
    for d in root.iter("default"):
        if d.get("class") == "visual":
            for g in d.findall("geom"):
                g.set("type", "sphere")
    for b in world.iter("body"):
        if b.get("name") == tool:
            b.append(ET.Comment("TOOL"))
    world.append(ET.Comment("WORLD"))
    act = root.find("actuator")
    if act is not None:
        act.append(ET.Comment("ACTUATOR"))
    else:
        root.append(ET.Comment("ACTUATOR"))
    comp = root.find("compiler")
    comp.attrib.pop("meshdir", None)
    idx = list(root).index(comp)
    root.insert(idx + 1, ET.Comment("OPTION"))
    ET.indent(tree, space="  ")
    body = ET.tostring(root, encoding="unicode")
    head = (f"<!-- 问渠《机器人学》网页物理仿真用的精简模型（textbook/tools/mjcf_web.py 生成，不要手改）。\n"
            f"     来源：MuJoCo Menagerie（Google DeepMind）{folder}/{file}，提交 {COMMIT}；许可证 {lic}，原文见同目录 LICENSE-{name}。\n"
            f"     改动：去掉网格与可视几何（外观用零件库 glTF）；网格碰撞几何换成包住它的胶囊；质量、惯量、关节、执行器不变。 -->\n")
    return head + body + "\n"


def check(name: str, men: Path, text: str) -> None:
    """Same masses, inertias and gravity terms as the original at a few joint configurations."""
    folder, file, *_ = MODELS[name]
    a = mujoco.MjModel.from_xml_path(str(men / folder / file))
    b = mujoco.MjModel.from_xml_string(text)
    assert a.nq == b.nq and a.nbody == b.nbody and a.nu == b.nu
    assert np.array_equal(a.body_mass, b.body_mass) and np.array_equal(a.body_inertia, b.body_inertia)
    da, db = mujoco.MjData(a), mujoco.MjData(b)
    rng = np.random.default_rng(41)
    for _ in range(5):
        q = rng.uniform(-1.5, 1.5, a.nq)
        da.qpos[:] = q
        db.qpos[:] = q
        mujoco.mj_forward(a, da)
        mujoco.mj_forward(b, db)
        assert np.array_equal(da.qfrc_bias, db.qfrc_bias), name


def main(men: Path) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (folder, *_rest) in MODELS.items():
        text = build(name, men)
        check(name, men, text)
        (OUT / f"{name}.xml").write_text(text, encoding="utf-8")
        shutil.copyfile(men / folder / "LICENSE", OUT / f"LICENSE-{name}")
        print(f"{name}: {len(text)} bytes")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
