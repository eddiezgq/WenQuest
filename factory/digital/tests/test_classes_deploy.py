"""班级工厂的“清单”字段（第 45 轮）：classes.yaml 一行写 plant，那座厂就按那份清单起（机器人厂）。"""
import os
import subprocess
import sys

import pytest
import yaml

DIG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAC = os.path.dirname(DIG)
DEPLOY = os.path.join(FAC, "deploy")
sys.path[:0] = [DEPLOY, FAC]

import classes as C  # noqa: E402


def test_robot_class_uses_robot_plant():
    cls = {c["id"]: c for c in C.load(os.path.join(DEPLOY, "classes.yaml"))}
    assert "robot" in cls and cls["robot"]["plant"] == "wenquest-robot"
    pi = cls["robot"]["plant_info"]
    assert pi["file"] == "/app/plants/wenquest-robot.yaml" and pi["abbr"] == "WQRB"
    assert cls["pilot"]["plant_info"] is None               # 不写 = 减速器厂，配置照旧
    svc = C.compose(list(cls.values()))["services"]
    assert svc["hub-c-robot"]["environment"]["WQ_PLANT_FILE"] == pi["file"]
    assert svc["sim-c-robot"]["environment"]["WQ_PLANT_FILE"] == pi["file"]
    br = svc["bridge-c-robot"]["environment"]
    assert br["WQ_ERP_ABBR"] == "WQRB" and br["WQ_ERP_COMPANY"] == pi["company"]
    assert "WQ_PLANT_FILE" not in svc["hub-c-pilot"]["environment"] and svc["bridge-c-pilot"]["environment"]["WQ_ERP_ABBR"] == "WQ"
    assert "robot" in svc["hub"]["environment"]["WQ_CLASS_IDS"].split()


def test_plant_file_is_valid_and_in_image():
    """清单在仓库的 factory/plants 里（镜像 COPY plants/ plants/），并且通过校验"""
    from factory import plant
    p = plant.load(os.path.join(FAC, "plants", "wenquest-robot.yaml"))
    assert p["PRODUCTS"] and "WQR-105" in p["ITEMS"]
    assert "COPY plants/ plants/" in open(os.path.join(DIG, "Dockerfile"), encoding="utf-8").read()


def test_plants_listing_for_setup_script():
    out = subprocess.run([sys.executable, os.path.join(DEPLOY, "classes.py"), os.path.join(DEPLOY, "classes.yaml"), "--plants"],
                         capture_output=True, text=True, check=True).stdout.strip().splitlines()
    rows = [r.split("\t") for r in out]
    assert [r[0] for r in rows] == ["robot"]
    assert rows[0][1:4] == ["/app/plants/wenquest-robot.yaml", "问渠机器人厂 WenQuest Robotics (Demo)", "WQRB"]


@pytest.mark.parametrize("plant, msg", [("no-such-plant", "找不到清单"), ("../etc", "不合规"), ("wenquest-gearbox", None)])
def test_bad_plant_rejected(tmp_path, plant, msg):
    f = tmp_path / "c.yaml"
    f.write_text(yaml.safe_dump({"classes": [{"id": "abc", "name": "x", "plant": plant}]}, allow_unicode=True), encoding="utf-8")
    if msg is None:                          # 演示清单本身也能用（产品齐全）
        assert C.load(str(f))[0]["plant_info"]["abbr"] == "WQ"
        return
    with pytest.raises(SystemExit) as ei:
        C.load(str(f))
    assert msg in str(ei.value)


def test_sewing_plant_accepted(tmp_path):
    f = tmp_path / "c.yaml"
    f.write_text(yaml.safe_dump({"classes": [{"id": "abc", "name": "x", "plant": "example-sewing"}]}, allow_unicode=True), encoding="utf-8")
    assert C.load(str(f))[0]["plant_info"]["abbr"]           # 缝纫机厂补了产品（第 45 轮），能用
