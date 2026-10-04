"""15.6 节：自动门（图 15.6.1）与三层电梯（图 15.6.2）的状态转换图。"""
from bookout import T, figure, out
from _draw15 import state_diagram

door = {"CLOSED": (0, 1.6, T("CLOSED\n关闭", "CLOSED"), "init"), "OPENING": (4.2, 1.6, T("OPENING\n开门中", "OPENING"), ""),
        "OPEN": (4.2, -0.4, T("OPEN\n开着", "OPEN"), ""), "CLOSING": (0, -0.4, T("CLOSING\n关门中", "CLOSING"), "")}
de = [("CLOSED", "OPENING", T("有人", "person"), 0.0), ("OPENING", "OPEN", T("开到位", "fully open"), 0.0),
      ("OPEN", "CLOSING", T("无人 ∧ 停留 3 s", "nobody ∧ 3 s"), 0.0), ("CLOSING", "CLOSED", T("关到位", "fully closed"), 0.0),
      ("CLOSING", "OPENING", T("有人 / 遇阻", "person / obstacle"), 0.3)]
figure(state_diagram(door, de, size=(8, 4.2)), "fig15_6_1")
lift = {"DOOR_OPEN": (0, 1.6, T("DOOR_OPEN\n停层开门", "DOOR_OPEN"), "init"), "CLOSING": (4.4, 1.6, T("CLOSING\n关门", "CLOSING"), ""),
        "MOVING": (2.2, -0.6, T("MOVING\n运行", "MOVING"), "")}
le = [("DOOR_OPEN", "CLOSING", T("有呼梯 ∧ 门开到位", "call ∧ door open"), -0.12), ("CLOSING", "MOVING", T("关到位", "door closed"), 0.0),
      ("CLOSING", "DOOR_OPEN", T("关门超时 4 s", "close timeout 4 s"), -0.5), ("MOVING", "DOOR_OPEN", T("到目标层", "at target"), 0.0)]
figure(state_diagram(lift, le, size=(8, 4.4)), "fig15_6_2")
out(door=len(door), lift=len(lift))
