"""15.7 节：回程中途断电 0.5 s 再来电。状态变量保持（程序 15.7.1）时，来电后压头自己向上走；
状态不保持、上电进 INIT（程序 15.5.1）时，压头不动，等人按复位。"""
from bookout import out
from plcbook import read, run
from _press import HANDS, HOME, LOAD

steps = [{"set": {"S_Auto": True}}] + HOME + [LOAD, {"wait": 200}, HANDS, {"until": {"B_PressDown": True}, "within": 5000},
                                              {"wait": 600}, {"power": 500}]
safe = {"id": "power", "steps": steps + [{"never": {"Y_PressUp": True}, "during": 2000}, {"expect": {"H_Ready": False}}]}
names = ["Y_PressUp", "B_PressUp", "z"]
good = run(read("p15_5_1.st"), plant="press", tests=[safe])
bad = run(read("p15_7_1.st"), plant="press", tests=[safe], must_pass=False,
          scenario={"steps": steps + [{"wait": 2500}], "trace": ["Y_PressUp", "B_PressUp", "Main.state"]})
assert good["passed"] == 1 and bad["passed"] == 0
tr = bad["scenario"]["trace"]
t_on = next(t for t, kind, _ in bad["scenario"]["log"] if kind == "power")            # 来电的时刻
t_rise = next(t for t, v in zip(tr["t"], tr["v"][0]) if v and t > t_on)          # 来电后压头上行阀第一次得电
out(good=good["passed"], bad_fail=bad["tests"][0]["failures"][0].split("：", 1)[1].split(" / ")[0], restart_delay_ms=t_rise - t_on)
