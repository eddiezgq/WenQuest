"""程序 4.6.1 的测试：一拍延迟、双线圈、顺序（扫描周期 10 ms）。按下 S1，看 H1_Copy、H2_Late、H3_First、H4_Same 各在哪一次扫描后变化。"""
from bookout import out
from plcbook import read, run

IO = [{"name": "S1_In", "addr": "%IX0.0", "dir": "in", "comment": ["输入 S1", "Input S1"]},
      {"name": "S2_In", "addr": "%IX0.1", "dir": "in", "comment": ["输入 S2", "Input S2"]},
      {"name": "H1_Copy", "addr": "%QX0.0", "dir": "out", "comment": ["H1", "H1"]},
      {"name": "H2_Late", "addr": "%QX0.1", "dir": "out", "comment": ["H2", "H2"]},
      {"name": "Y1_Out", "addr": "%QX0.2", "dir": "out", "comment": ["Y1", "Y1"]},
      {"name": "H3_First", "addr": "%QX0.3", "dir": "out", "comment": ["H3", "H3"]},
      {"name": "H4_Same", "addr": "%QX0.4", "dir": "out", "comment": ["H4", "H4"]}]
tests = [
    {"id": "late", "steps": [{"wait": 30}, {"set": {"S1_In": True}}, {"wait": 10}, {"expect": {"H1_Copy": True, "H2_Late": False, "H3_First": True, "H4_Same": True}},
                             {"wait": 10}, {"expect": {"H2_Late": True}}]},
    {"id": "double", "steps": [{"set": {"S1_In": True, "S2_In": False}}, {"wait": 30}, {"expect": {"Y1_Out": False}},
                               {"set": {"S1_In": False, "S2_In": True}}, {"wait": 30}, {"expect": {"Y1_Out": True}}]},
]
r = run(read("p4_6_1.st"), io=IO, tests=tests, review=True)
dbl = [x for x in r["review"] if x["rule"] == "double-coil"]
assert dbl, r["review"]
out(passed=r["passed"], total=r["total"], review_line=dbl[0]["line"])
