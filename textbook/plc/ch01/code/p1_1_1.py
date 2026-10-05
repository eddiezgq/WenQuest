"""程序 1.1.1 的测试：上料输送线的五条要求（送到末端停、停止、急停、卡料报警、过载）全部通过；
再用一次完整的运行记录画时序图（图 1.1.2），算出料从入口到末端的时间和按下启动到接触器得电的时间。"""
from bookout import figure, out, T
from plcbook import read, run
from _draw01 import timing

START = [{"set": {"S1_Start": True}}, {"wait": 300}, {"set": {"S1_Start": False}}]
tests = [
    {"id": "run", "steps": [{"wait": 500}, *START, {"until": {"B2_End": True}, "within": 15000}, {"wait": 50},
                            {"expect": {"KM1_Run": False, "H2_Fault": False}}]},
    {"id": "stop", "steps": [*START, {"wait": 2000}, {"set": {"S2_Stop": False}}, {"wait": 20}, {"expect": {"KM1_Run": False}},
                             {"set": {"S2_Stop": True}}, {"never": {"KM1_Run": True}, "during": 1000}]},
    {"id": "estop", "steps": [*START, {"wait": 2000}, {"set": {"S0_EStop": False}}, {"wait": 20}, {"expect": {"KM1_Run": False}}]},
    {"id": "jam", "faults": {"jam": True}, "steps": [*START, {"never": {"H2_Fault": True}, "during": 19000}, {"until": {"H2_Fault": True}, "within": 2000},
                                                    {"wait": 20}, {"expect": {"KM1_Run": False}}]},
    {"id": "overload", "faults": {"overload": True}, "steps": [*START, {"wait": 50}, {"expect": {"KM1_Run": False, "H2_Fault": True}}]},
]
names = ["S1_Start", "KM1_Run", "B1_Entry", "B2_End", "H1_Run"]
r = run(read("p1_1_1.st"), plant="conveyor", tests=tests, review=True,
        scenario={"steps": tests[0]["steps"] + [{"wait": 1500}], "trace": names})
assert not [x for x in r["review"] if x["level"] == "error"], r["review"]
tr = r["scenario"]["trace"]


def rise(name, after=0):
    k = tr["names"].index(name)
    return next(t for t, v in zip(tr["t"], tr["v"][k]) if v and t >= after)


def fall(name, after=0):
    k = tr["names"].index(name)
    return next(t for t, v in zip(tr["t"], tr["v"][k]) if not v and t >= after)


t_s1 = rise("S1_Start")
t_km = rise("KM1_Run")
t_entry_free = fall("B1_Entry", t_km)
t_end = rise("B2_End")
t_stop = fall("KM1_Run", t_km)
figure(timing(tr, [("S1_Start", "S1_Start"), ("KM1_Run", "KM1_Run"), ("B1_Entry", "B1_Entry"), ("B2_End", "B2_End"), ("H1_Run", "H1_Run")],
              marks=[(t_s1, T("按启动", "Start")), (t_end, T("料到末端", "bar at the end"))]), "fig1_1_2")
out(passed=r["passed"], total=r["total"], cycle_ms=10, travel_s=round((t_end - t_km) / 1000, 1),
    leave_s=round((t_entry_free - t_km) / 1000, 1))
