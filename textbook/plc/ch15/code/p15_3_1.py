"""程序 15.3.1 的测试：自动循环的五条要求全部通过；再用一次完整循环的时序记录算出各段时间和节拍。"""
from bookout import out
from plcbook import read, run
from _press import auto_tests, cycle, first_fall, first_rise

prog = read("p15_3_1.st")
names = ["S_Hand1", "Y_Clamp", "B_Clamped", "Y_PressDown", "B_PressDown", "Y_PressUp", "B_PressUp", "B_Unclamped", "H_OK", "force"]
r = run(prog, plant="press", tests=auto_tests(), review=True,
        scenario={"steps": cycle({"until": {"B_PressDown": True}, "within": 5000}), "trace": names})
tr = r["scenario"]["trace"]
t0 = first_rise(tr, "S_Hand1")
t_clamp = first_rise(tr, "B_Clamped", t0)
t_down = first_rise(tr, "B_PressDown", t_clamp)
t_up = first_rise(tr, "B_PressUp", t_down)
t_free = first_rise(tr, "B_Unclamped", t_up)
errors = [x for x in r["review"] if x["level"] == "error"]
assert not errors, errors
out(passed=r["passed"], total=r["total"],
    clamp_s=(t_clamp - t0) / 1000, press_s=(t_down - t_clamp) / 1000, return_s=(t_up - t_down) / 1000, unclamp_s=(t_free - t_up) / 1000,
    cycle_s=(t_free - t0) / 1000, warnings=len([x for x in r["review"] if x["level"] == "warning"]))
