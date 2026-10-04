"""15.2 节：一次合格件压装循环的时序图（图 15.2.1，程序 15.3.1 在虚拟压装工位上运行的记录）和状态转换图（图 15.2.2）。"""
from bookout import T, figure, out
from plcbook import read, run
from _draw15 import state_diagram, timing
from _press import cycle, first_rise

names = ["S_Hand1", "Y_Clamp", "B_Clamped", "Y_PressDown", "B_PressDown", "Y_PressUp", "B_PressUp", "B_Unclamped", "H_OK", "force"]
r = run(read("p15_3_1.st"), plant="press", scenario={"steps": cycle({"until": {"B_PressDown": True}, "within": 5000}), "trace": names})
tr = r["scenario"]["trace"]
t0 = first_rise(tr, "S_Hand1")
k = tr["names"].index("force")
f_end = max(tr["v"][k])
rows = [("S_Hand1", "S_Hand1/2", "bool"), ("Y_Clamp", "Y_Clamp", "bool"), ("B_Clamped", "B_Clamped", "bool"),
        ("Y_PressDown", "Y_PressDown", "bool"), ("force", T("压装力", "force"), ("analog", "kN", 6.0)), ("B_PressDown", "B_PressDown", "bool"),
        ("Y_PressUp", "Y_PressUp", "bool"), ("B_PressUp", "B_PressUp", "bool"), ("B_Unclamped", "B_Unclamped", "bool"), ("H_OK", "H_OK", "bool")]
marks = [(t0, "①"), (first_rise(tr, "B_Clamped", t0), "②"), (first_rise(tr, "B_PressDown", t0), "③"),
         (first_rise(tr, "B_PressUp", first_rise(tr, "B_PressDown", t0)), "④")]
figure(timing(tr, rows, t0=t0 / 1000 - 0.3, t1=t0 / 1000 + 5.0, marks=marks), "fig15_2_1")

S = {"IDLE": (0, 2.2, T("IDLE\n等待", "IDLE\nwaiting"), "init"),
     "CLAMPING": (4.6, 2.2, T("CLAMPING\n夹紧", "CLAMPING\nclamping"), ""),
     "PRESSING": (4.6, 0, T("PRESSING\n压装", "PRESSING\npressing"), ""),
     "RETURNING": (0, 0, T("RETURNING\n回程", "RETURNING\nreturning"), ""),
     "UNCLAMPING": (-3.8, 1.1, T("UNCLAMPING\n松开", "UNCLAMPING\nunclamping"), "")}
E_ = [("IDLE", "CLAMPING", T("有工件∧在原点∧双手启动", "part ∧ home ∧ two-hand start"), 0.0),
      ("CLAMPING", "PRESSING", "B_Clamped", 0.0),
      ("PRESSING", "RETURNING", T("压到底 / 过载 / 松手或挡光", "bottom / overload / hands off or curtain"), 0.0),
      ("RETURNING", "UNCLAMPING", "B_PressUp", -0.25),
      ("UNCLAMPING", "IDLE", "B_Unclamped", -0.25)]
figure(state_diagram(S, E_, size=(9.2, 4.6)), "fig15_2_2")
out(f_end=round(f_end, 1), t_clamp=round((first_rise(tr, "B_Clamped", t0) - t0) / 1000, 2))
