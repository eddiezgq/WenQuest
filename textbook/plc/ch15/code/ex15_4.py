"""15.4 节：加上 INIT（上电）与 HOMING（回原点）后的状态转换图（图 15.4.1）。"""
from bookout import T, figure, out
from _draw15 import state_diagram

S = {"INIT": (-4.6, 3.6, T("INIT\n上电·位置未知", "INIT\npower-up"), "init"),
     "HOMING": (0, 3.6, T("HOMING\n回原点", "HOMING\nhoming"), ""),
     "IDLE": (0, 1.8, T("IDLE\n在原点", "IDLE\nat home"), ""),
     "CLAMPING": (4.6, 1.8, T("CLAMPING\n夹紧", "CLAMPING"), ""),
     "PRESSING": (4.6, 0, T("PRESSING\n压装", "PRESSING"), ""),
     "RETURNING": (0, 0, T("RETURNING\n回程", "RETURNING"), ""),
     "UNCLAMPING": (-4.6, 0.9, T("UNCLAMPING\n松开", "UNCLAMPING"), "")}
E_ = [("INIT", "HOMING", T("复位", "reset"), 0.0),
      ("HOMING", "IDLE", T("上位∧松开", "up ∧ unclamped"), -0.45),
      ("IDLE", "HOMING", T("复位", "reset"), -0.45),
      ("IDLE", "CLAMPING", T("自动：双手启动\n手动：单步", "auto: two-hand\nmanual: step"), 0.0),
      ("CLAMPING", "PRESSING", T("夹紧到位 ∧ go", "clamped ∧ go"), 0.0),
      ("PRESSING", "RETURNING", T("压到底 ∧ go / 过载", "bottom ∧ go / overload"), 0.0),
      ("RETURNING", "UNCLAMPING", T("上位 ∧ go", "up ∧ go"), -0.25),
      ("UNCLAMPING", "IDLE", T("松开 ∧ go", "unclamped ∧ go"), -0.25)]
figure(state_diagram(S, E_, size=(10, 5.6)), "fig15_4_1")
out(states=len(S))
