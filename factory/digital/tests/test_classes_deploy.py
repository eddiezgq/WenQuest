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
    assert [r[0] for r in rows] == ["robot", "pcb", "chip", "sensor", "motor", "sewing"]   # 第 85 轮：加了电路板厂；第 103 轮：芯片厂；第 125 轮：传感器厂；第 131 轮：电机厂；第 133 轮：缝纫机厂
    assert rows[0][1:4] == ["/app/plants/wenquest-robot.yaml", "问渠机器人厂 WenQuest Robotics (Demo)", "WQRB"]
    assert rows[1][1:4] == ["/app/plants/wenquest-pcb.yaml", "问渠电路板厂 WenQuest Electronics (Demo)", "WQEL"]
    assert rows[2][1:4] == ["/app/plants/wenquest-chip.yaml", "问渠芯片封测厂 WenQuest Semiconductor (Demo)", "WQSC"]
    assert rows[3][1:4] == ["/app/plants/wenquest-sensor.yaml", "问渠传感器厂 WenQuest Sensors (Demo)", "WQSN"]
    assert rows[4][1:4] == ["/app/plants/wenquest-motor.yaml", "问渠电机厂 WenQuest Motors (Demo)", "WQMT"]
    assert rows[5][1:4] == ["/app/plants/wenquest-sewing.yaml", "问渠缝纫机厂 WenQuest Sewing Machines (Demo)", "WQSW"]   # 第 134 轮


def test_park_peers_between_class_plants():
    """第 85 轮：接入工业园的班级工厂互相认得——按清单 id 下单、按班级编号回传发货；公共工厂认得所有接入的班级工厂"""
    cls = C.load(os.path.join(DEPLOY, "classes.yaml"))
    svc = C.compose(cls)["services"]
    peers = lambda s: dict(x.split("=", 1) for x in svc[s]["environment"]["WQ_PARK_PEERS"].split())    # noqa: E731
    assert peers("hub-c-robot") == {"wenquest-gearbox": "http://hub:8100", "wenquest-pcb": "http://hub-c-pcb:8100", "pcb": "http://hub-c-pcb:8100",
                                    "wenquest-chip": "http://hub-c-chip:8100", "chip": "http://hub-c-chip:8100",      # 第 103 轮：芯片厂
                                    "wenquest-sensor": "http://hub-c-sensor:8100", "sensor": "http://hub-c-sensor:8100",   # 第 125 轮：传感器厂
                                    "wenquest-motor": "http://hub-c-motor:8100", "motor": "http://hub-c-motor:8100"}       # 第 131 轮：电机厂
    assert peers("hub-c-pcb")["robot"] == "http://hub-c-robot:8100" and peers("hub-c-pcb")["wenquest-gearbox"] == "http://hub:8100"
    assert peers("hub") == {"robot": "http://hub-c-robot:8100", "pcb": "http://hub-c-pcb:8100", "chip": "http://hub-c-chip:8100",
                            "sensor": "http://hub-c-sensor:8100", "motor": "http://hub-c-motor:8100"}
    assert peers("hub-c-sensor")["wenquest-pcb"] == "http://hub-c-pcb:8100"                        # 第 125 轮：读头板向电路板厂买
    assert svc["hub-c-pcb"]["environment"]["WQ_PLANT_FILE"] == "/app/plants/wenquest-pcb.yaml"


@pytest.mark.parametrize("plant, msg", [("no-such-plant", "找不到清单"), ("../etc", "不合规"), ("wenquest-gearbox", None),
                                       ("example-sewing", "没有产品")])
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
    f.write_text(yaml.safe_dump({"classes": [{"id": "abc", "name": "x", "plant": "example-sewing-products"}]}, allow_unicode=True), encoding="utf-8")
    assert C.load(str(f))[0]["plant_info"]["abbr"]           # 写了产品的缝纫机厂清单（第 45 轮）能用
