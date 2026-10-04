"""程序 15.6.1（CASE）与 15.6.2（SFC）：同一台三层电梯、同一组测试。"""
from bookout import out
from plcbook import read, run

call = lambda k: [{"set": {f"S_C{k}": True}}, {"wait": 100}, {"set": {f"S_C{k}": False}}]
tests = [
    {"id": "up", "steps": [{"wait": 2000}, *call(3), {"until": {"floor": 3}, "within": 12000}, {"until": {"B_DoorOpen": True}, "within": 3000},
                           {"expect": {"H_C3": False, "hazard": False}}]},
    {"id": "down", "steps": [{"wait": 2000}, *call(3), {"until": {"B_DoorOpen": True, "floor": 3}, "within": 15000}, *call(2),
                             {"until": {"floor": 2, "B_DoorOpen": True}, "within": 12000}, {"expect": {"hazard": False}}]},
    {"id": "jam", "faults": {"doorJam": True}, "steps": [{"wait": 2000}, *call(2), {"never": {"K_Up": True}, "during": 9000}, {"expect": {"hazard": False}}]},
    {"id": "safe", "steps": [{"wait": 1500}, *call(3), {"wait": 300}, *call(1), {"wait": 300}, *call(2), {"never": {"hazard": True}, "during": 25000}]},
]
rc = run(read("p15_6_1.st"), plant="elevator", tests=tests, review=True)
rs = run(read("p15_6_2.st"), plant="elevator", tests=tests, review=True,
         scenario={"steps": tests[0]["steps"], "trace": ["K_Up", "B_F3", "Y_DoorOpen"]})
for r in (rc, rs):
    assert not [x for x in r["review"] if x["level"] == "error"], r["review"]
tr = rs["scenario"]["trace"]
up = [t for t, v in zip(tr["t"], tr["v"][0]) if v]
out(case_passed=rc["passed"], sfc_passed=rs["passed"], total=len(tests), travel_s=round((up[-1] - up[0]) / 1000, 1))
