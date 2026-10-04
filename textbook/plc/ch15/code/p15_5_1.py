"""程序 15.5.1 的测试：15.3、15.4 节的全部用例照样通过（回归测试），再加三个异常用例。"""
from bookout import out
from plcbook import read, run
from _press import fault_tests, mode_tests

prog = read("p15_5_1.st")
tests = [t for t in mode_tests() if t["id"] != "home_mid"]
r = run(prog, plant="press", tests=tests + fault_tests(), review=True,
        scenario={"steps": fault_tests()[0]["steps"], "faults": {"clampWire": True}, "trace": ["S_Hand1", "Y_Clamp", "B_Clamped", "H_Fault"]})
assert not [x for x in r["review"] if x["level"] == "error"]
tr = r["scenario"]["trace"]
hand = next(t for t, v in zip(tr["t"], tr["v"][0]) if v)
flt = next(t for t, v in zip(tr["t"], tr["v"][3]) if v)
out(passed=r["passed"], total=r["total"], regression=len(tests), new=len(fault_tests()), fault_after_s=round((flt - hand) / 1000, 2))
