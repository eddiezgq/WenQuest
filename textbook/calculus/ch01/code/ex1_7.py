"""1.7 节：贯穿全书的 UR5e 的几个数（由零件库模型读出）。"""
import json
from pathlib import Path

from bookout import out

e = json.loads((Path(__file__).resolve().parents[2] / "models" / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
js = {j["name"]: j for j in e["robot"]["joints"]}
ds = e["datasheet"]["values"]
out(version=e.get("version", ""), l1=js["elbow_joint"]["origin"]["xyz"][2], l2=js["wrist_1_joint"]["origin"]["xyz"][2],
    reach=ds["reach_mm"], l12=js["elbow_joint"]["origin"]["xyz"][2] + js["wrist_1_joint"]["origin"]["xyz"][2], payload=ds["payload_kg"], dof=ds["dof"], n_joints=len(e["robot"]["joints"]))
