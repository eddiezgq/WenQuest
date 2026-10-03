"""图 1.1.1 用的数（与 ex1_1.py 相同的算法），由 fig1_1.py 导入；作为程序运行时只交出一个核对值。"""
import json
from pathlib import Path

from bookout import out

MODELS = Path(__file__).resolve().parents[2] / "models"
js = {j["name"]: j for j in json.loads((MODELS / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))["robot"]["joints"]}
L = js["elbow_joint"]["origin"]["xyz"][2] + js["wrist_1_joint"]["origin"]["xyz"][2]
t1, t2 = 1.0 * 9.80665 * L, 2.0 * 9.80665 * L
if __name__ == "__main__":
    out(check=t1)
