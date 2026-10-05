"""程序 3.5.1 的测试：液位计 4–20 mA 的标定、断线检测与加水阀的两位控制（6 个测试）；
分辨率：16 位（0–27648）与 12 位（0–4095）模拟量输入时，一个数各代表多少毫米、多少微安。"""
from bookout import out
from plcbook import read, run

IO = [{"name": "AI_Level", "addr": "%IW64", "dir": "in", "type": "INT", "comment": ["液位计 4–20 mA（4 mA ↔ 0，20 mA ↔ 27648）", "Level 4–20 mA (4 mA ↔ 0, 20 mA ↔ 27648)"]},
      {"name": "Y1_Fill", "addr": "%QX0.0", "dir": "out", "comment": ["加水电磁阀", "Fill valve"]},
      {"name": "H3_LevelFault", "addr": "%QX0.1", "dir": "out", "comment": ["液位故障灯（黄）", "Level fault lamp (amber)"]}]
FS = 27648


def raw(mm):
    return round(mm / 2000 * FS)


def ma(m):
    return round((m - 4) / 16 * FS)


tests = [
    {"id": "scale", "steps": [{"set": {"AI_Level": ma(12)}}, {"wait": 20}, {"expect": {"level": 1000.0, "current": 12.0}}]},
    {"id": "low", "steps": [{"set": {"AI_Level": raw(500)}}, {"wait": 20}, {"expect": {"Y1_Fill": True, "H3_LevelFault": False}}]},
    {"id": "hyst", "steps": [{"set": {"AI_Level": raw(500)}}, {"wait": 20}, {"set": {"AI_Level": raw(1200)}}, {"wait": 20}, {"expect": {"Y1_Fill": True}},
                             {"set": {"AI_Level": raw(1600)}}, {"wait": 20}, {"expect": {"Y1_Fill": False}},
                             {"set": {"AI_Level": raw(1200)}}, {"wait": 20}, {"expect": {"Y1_Fill": False}}]},
    {"id": "break", "steps": [{"set": {"AI_Level": raw(500)}}, {"wait": 20}, {"set": {"AI_Level": ma(0.0)}}, {"wait": 20},
                              {"expect": {"Y1_Fill": False, "H3_LevelFault": True, "wireBreak": True}}]},
    {"id": "low-but-ok", "steps": [{"set": {"AI_Level": ma(3.8)}}, {"wait": 20}, {"expect": {"wireBreak": False, "Y1_Fill": True}}]},
    {"id": "over", "steps": [{"set": {"AI_Level": ma(21.0)}}, {"wait": 20}, {"expect": {"H3_LevelFault": True, "Y1_Fill": False}}]},
]
r = run(read("p3_5_1.st"), io=IO, tests=tests, review=True)
assert not [x for x in r["review"] if x["level"] == "error"], r["review"]
out(passed=r["passed"], total=r["total"], mm16=round(2000 / FS, 3), ua16=round(16000 / FS, 2), mm12=round(2000 / 4096, 2), ua12=round(16000 / 4096, 1),
    raw_break=ma(3.6), raw_0=ma(0.0))
