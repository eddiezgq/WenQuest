"""53.9 节：工艺评审中对尺寸链的检查。算例 53.9.1 把 SH-301 的工艺规程改出三种常见错误，看 AI 工艺评审员（hub/process.py）给出什么意见：
(1) 铣键槽误按图纸尺寸控制（H = 35（0/−0.2））；(2) 工序 40 总长放宽到 ±0.3；(3) 轴肩粗车余量减到 0.3。"""
import copy
import sys

import _mfg as M
from bookout import out

sys.path.insert(0, str(M.REPO / "factory" / "digital"))
from hub import process as P  # noqa: E402

p = M.plan()
base = [x for x in P.review(p) if x["rule"] == "尺寸链"]
cases = {}
b1 = copy.deepcopy(p)
b1["chains"][0]["links"][0].update({"nominal": 35, "es": 0, "ei": -0.2})
cases["keyway"] = b1
b2 = copy.deepcopy(p)
next(c for c in b2["tolerance_chart"]["cuts"] if c["seq"] == 40.3).update({"es": 0.3, "ei": -0.3})
cases["total"] = b2
b3 = copy.deepcopy(p)
for c in b3["tolerance_chart"]["cuts"]:
    if str(c["seq"]).startswith("20.") and c["surf"] in ("S1", "S2"):
        c["nominal"] += 0.5                       # 朝左的轴肩：粗车位置右移 0.5，余量从 0.8 减到 0.3
    if str(c["seq"]).startswith("20.") and c["surf"] in ("S3", "S4"):
        c["nominal"] -= 0.5
cases["allow"] = b3
msg = {k: [x["text"] for x in P.review(v) if x["rule"] == "尺寸链"] for k, v in cases.items()}
assert not base and all(msg.values())
out(n_base=len(base), m_keyway=msg["keyway"][0], m_total=msg["total"][0], n_total=len(msg["total"]), m_allow=msg["allow"][0], n_allow=len(msg["allow"]))
