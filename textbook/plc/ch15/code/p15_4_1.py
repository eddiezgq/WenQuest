"""程序 15.4.1 的测试：上电不动、回原点（含从行程中间回原点）、自动循环五条、单步按五次走完一个循环、点动受光幕约束。"""
from bookout import out
from plcbook import read, run
from _press import mode_tests

prog = read("p15_4_1.st")
tests = mode_tests()
r = run(prog, plant="press", tests=[t for t in tests if t["id"] != "home_mid"], review=True)
# 从行程中间回原点：上电时压头停在 60 mm 处、夹具夹着
mid = run(prog, plant="press", plant_opts={"ram0": 0.06, "clamp0": 1}, tests=[t for t in tests if t["id"] == "home_mid"],
          scenario={"steps": [t for t in tests if t["id"] == "home_mid"][0]["steps"], "trace": ["B_PressUp", "B_Unclamped", "H_Ready"]})
errors = [x for x in r["review"] if x["level"] == "error"]
assert not errors, errors
tr = mid["scenario"]["trace"]
t_ready = next(t for t, v in zip(tr["t"], tr["v"][2]) if v)
out(passed=r["passed"] + mid["passed"], total=r["total"] + mid["total"], home_mid_s=round((t_ready - 100) / 1000, 2))   # 复位按钮在 0.1 s 时按下
