"""15.5 节：完整的状态转换图，加上 FAULT 与 ESTOP（图 15.5.1）。虚线框里的任何状态都可能转入故障或急停。"""
from bookout import T, figure, out
from _draw15 import state_diagram

S = {"INIT": (-4.6, 3.8, "INIT", "init"),
     "HOMING": (0, 3.8, "HOMING", ""),
     "IDLE": (0, 1.8, "IDLE", ""),
     "CLAMPING": (4.4, 1.8, "CLAMPING", ""),
     "PRESSING": (4.4, 0, "PRESSING", ""),
     "RETURNING": (0, 0, "RETURNING", ""),
     "UNCLAMPING": (-4.4, 0.9, "UNCLAMPING", ""),
     "FAULT": (9.8, 2.2, T("FAULT 故障\n复位 → HOMING", "FAULT\nreset → HOMING"), "fault"),
     "ESTOP": (9.8, -0.2, T("ESTOP 急停\n松开、复位 → HOMING", "ESTOP\nrelease, reset → HOMING"), "fault")}
E_ = [("INIT", "HOMING", T("复位", "reset"), 0.0), ("HOMING", "IDLE", "", -0.3),
      ("IDLE", "CLAMPING", "", 0.0), ("CLAMPING", "PRESSING", "", 0.0), ("PRESSING", "RETURNING", "", 0.0),
      ("RETURNING", "UNCLAMPING", "", -0.25), ("UNCLAMPING", "IDLE", "", -0.25),
      ("*", "FAULT", T("超时 / 传感器冲突", "timeout / sensor conflict"), 0),
      ("*", "ESTOP", T("急停按下", "e-stop pressed"), 0)]
figure(state_diagram(S, E_, size=(11.5, 5.8), group=(-5.9, -0.7, 6.0, 2.6, T("工作中的状态（含 HOMING）", "working states (and HOMING)"))), "fig15_5_1")
out(states=len(S))
