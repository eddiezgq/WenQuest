"""第 50 章共用：读数字工厂的数据（工厂数据、SH-301 工艺规程、AI 工艺评审员）和画图的颜色。

书里的算例都落在数字工厂真实的数据上：工艺路线、工作中心费率、物料单价取自 factory/factory/data.py，
SH-301 的工艺规程取自 factory/digital/std/SH-301_process.yaml——工厂的测试和 AI 工艺评审员用的是同一份。
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory", REPO / "factory" / "digital"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from factory import data as F  # noqa: E402

PLAN_FILE = REPO / "factory" / "digital" / "std" / "SH-301_process.yaml"

# 颜色（各阶段）
STAGE_COLOR = {"blank": "#8c8c8c", "rough": "#d98c3a", "qt": "#b5443b", "finish": "#3a7dc9", "keyway": "#7b5fb3",
               "grind": "#2f8f5b", "inspect": "#555555", "harden": "#b5443b", "gear": "#7b5fb3"}
INK = "#1d2327"
MUTED = "#7a868d"
STEEL = "#c9d2d9"


def plan():
    return yaml.safe_load(PLAN_FILE.read_text(encoding="utf-8"))


def review(p):
    from hub import process
    return process.review(p)


def stage(op_name):
    from hub import process
    return process.STAGE.get(op_name)


def rate(workstation):
    """工作中心费率（美元/小时）= 折旧 + 人工 + 能耗（工厂数据，教学示意值）"""
    return float(sum(F.WORKSTATIONS[workstation][1]))


def price(item):
    return float(F.ITEMS[item][3])


def segments():
    """SH-301 的轴段 (直径, 长度) mm，与 FreeCAD 宏 wq_shaft.py 的默认参数相同。"""
    sys.path.insert(0, str(REPO / "factory" / "digital" / "freecad"))
    import wq_shaft
    return list(wq_shaft.PARAMS["segments"]), dict(wq_shaft.PARAMS["keyway"])
