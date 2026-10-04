"""本章程序共用：从问渠零件库读 UR5e 的上臂长 l₁、前臂长 l₂。以下划线开头，构建时不单独运行。"""
import json
from pathlib import Path

_e = json.loads((Path(__file__).resolve().parents[2] / "models" / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
_js = {j["name"]: j for j in _e["robot"]["joints"]}
L1 = _js["elbow_joint"]["origin"]["xyz"][2]
L2 = _js["wrist_1_joint"]["origin"]["xyz"][2]
