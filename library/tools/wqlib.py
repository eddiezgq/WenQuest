# -*- coding: utf-8 -*-
"""零件库公共函数：读条目、读规格表、规格代号转文件名。"""
import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog"
ALLOWED_LICENSES = {"Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "BSD-3-Clause-Clear", "MIT", "Zlib", "ISC",
                    "CC0-1.0", "CC-BY-3.0", "CC-BY-4.0"}


def entry_dirs():
    return sorted(p.parent for p in CATALOG.glob("*/*/entry.yaml"))


def load(d):
    """读条目；同目录有 vendor.yaml（厂商样本数据，第 5 轮 P4）就合并进来：datasheet、dh、vendor，出处追加到 data_sources。
    这样 import_menagerie.py 重写 entry.yaml 时厂商数据不会丢。"""
    d = Path(d)
    e = yaml.safe_load(open(d / "entry.yaml", encoding="utf-8"))
    ov = d / "vendor.yaml"
    if ov.exists():
        v = yaml.safe_load(open(ov, encoding="utf-8")) or {}
        for k in ("datasheet", "dh", "vendor"):
            if k in v:
                e[k] = v[k]
        if v.get("data_sources"):
            src = e.setdefault("source", {})
            src["data_sources"] = list(src.get("data_sources") or []) + v["data_sources"]
        if v.get("tags"):
            e["tags"] = list(dict.fromkeys(list(e.get("tags") or []) + v["tags"]))
    e["_dir"] = d
    return e


def entries(only=None):
    out = [load(d) for d in entry_dirs()]
    if only:
        out = [e for e in out if e["id"] in only or any(e["id"].startswith(o) for o in only)]
    return out


def _num(v):
    if v is None or v == "":
        return None
    try:
        f = float(v)
    except ValueError:
        return v
    return int(f) if f == int(f) else f


def specs(e):
    """规格表的每一行（数值已转成数）；robot/mechanism/case 只有一行 default。"""
    if e.get("specs"):
        with open(e["_dir"] / e["specs"], encoding="utf-8") as f:
            return [{k: (_num(v) if k != "size" else v) for k, v in r.items()} for r in csv.DictReader(f)]
    return [dict({"size": "default"}, **(e.get("defaults") or {}))]


def file_code(size):
    return str(size).replace("/", "_").replace("×", "x").replace(" ", "")


def ref(e, size):
    return "{}/{}".format(e["id"], size)


# 类别词表（附录 B.2）：部分 → 代号 → 名称；validate.py 校验、index.json 带上给网页和学习平台用
CATEGORY_NAMES = {
    "A": {"BLT": ("螺栓", "Bolts"), "SCR": ("螺钉", "Screws"), "NUT": ("螺母", "Nuts"), "WSH": ("垫圈", "Washers"),
          "PIN": ("销", "Pins"), "KEY": ("键", "Keys"), "RNG": ("挡圈", "Retaining rings"), "BRG": ("滚动轴承", "Rolling bearings"),
          "BSC": ("滚珠丝杠", "Ball screws"), "LGD": ("直线导轨", "Linear guides"), "PUL": ("同步带轮", "Timing pulleys"),
          "SPK": ("链轮", "Sprockets"), "CPL": ("联轴器", "Couplings"), "SPR": ("弹簧", "Springs"), "SEL": ("密封件", "Seals"),
          "PLG": ("螺塞", "Plugs")},
    "B": {"ARM": ("机械臂", "Arms"), "MOB": ("移动机器人", "Mobile robots"), "LEG": ("足式机器人", "Legged robots"),
          "HUM": ("人形机器人", "Humanoids"), "EEF": ("末端执行器", "End effectors"), "UAV": ("无人机", "Drones"),
          "CRT": ("直角坐标", "Cartesian"), "SCA": ("SCARA", "SCARA"), "PAR": ("并联", "Parallel"),
          "EDU": ("教学模型", "Teaching models"), "MAN": ("移动操作", "Mobile manipulators"), "SEN": ("其他", "Other")},
    "D": {"MOT": ("伺服电机", "Servo motors"), "RDC": ("精密减速器", "Precision reducers"), "DRV": ("驱动器", "Drives"),
          "ENC": ("编码器", "Encoders"), "FTS": ("力/力矩传感器", "Force/torque sensors"), "IMU": ("惯性测量单元", "IMUs"),
          "LDR": ("激光雷达", "Lidars"), "CAM": ("相机", "Cameras"), "CTL": ("控制器", "Controllers"),
          "BAT": ("电池", "Batteries"), "ACT": ("执行器模组", "Actuator modules"), "GRP": ("夹爪", "Grippers")},
    "C": {"LNK": ("连杆机构", "Linkages"), "CAM": ("凸轮", "Cams"), "GER": ("齿轮与齿轮系", "Gears"), "WRM": ("蜗轮蜗杆", "Worm gears"),
          "BLT": ("带传动", "Belt drives"), "RAT": ("棘轮", "Ratchets"), "GNV": ("槽轮", "Geneva drives"),
          "SCN": ("丝杠螺母", "Lead screws"), "RED": ("减速器案例", "Reducer cases")},
}
