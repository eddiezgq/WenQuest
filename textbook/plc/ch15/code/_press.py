"""第 15 章共用：压装工位的测试用例和画图的小工具。

测试用例写成数据：给输入、等、检查输出或设备状态。书里的每个压装程序都要通过它该通过的那些用例
（textbook/tools/plcbook.py 用平台的 PLC 引擎和虚拟压装工位运行，与学生实验里的一模一样）。
"""

LOAD = {"set": {"B_Part": True, "S_LC": True, "S_EStop": True}}
HANDS = {"set": {"S_Hand1": True, "S_Hand2": True}}
FREE = {"set": {"S_Hand1": False, "S_Hand2": False}}


def cycle(*middle, within=8000):
    """放工件、双手启动、……、等压头回到上位并松开。"""
    return [LOAD, {"wait": 200}, HANDS, *middle, {"until": {"B_PressUp": True, "Y_Clamp": False}, "within": within}, FREE,
            {"until": {"B_Unclamped": True}, "within": 2000}]


def auto_tests():
    """15.3 节：自动循环应满足的五条要求（每条对应控制要求说明里的一句话）。"""
    return [
        {"id": "good", "steps": cycle({"until": {"B_PressDown": True}, "within": 5000}) + [{"expect": {"H_OK": True, "H_NOK": False}}]},
        {"id": "loose", "faults": {"loose": True}, "steps": cycle() + [{"expect": {"H_OK": False, "H_NOK": True}}]},
        {"id": "tight", "faults": {"tight": True}, "steps": cycle() + [{"expect": {"H_NOK": True}}]},
        {"id": "curtain", "steps": [LOAD, {"wait": 200}, HANDS, {"wait": 1500}, {"set": {"S_LC": False}}, {"wait": 20},
                                     {"expect": {"Y_PressDown": False, "hazard": False}}, {"set": {"S_LC": True}},
                                     {"until": {"B_PressUp": True, "Y_Clamp": False}, "within": 6000}, {"expect": {"H_NOK": True}}]},
        {"id": "twohand", "steps": [LOAD, {"wait": 200}, {"set": {"S_Hand1": True}}, {"wait": 800}, {"set": {"S_Hand2": True}},
                                     {"never": {"Y_Clamp": True}, "during": 1500}, FREE, {"wait": 300}, HANDS,
                                     {"until": {"Y_Clamp": True}, "within": 300}]},   # 两手都松开后重新按，能启动
    ]


def first_rise(trace, name, after=0.0):
    """时序记录里某信号第一次变为 TRUE（或第一次大于 0）的时刻，ms。"""
    k = trace["names"].index(name)
    for t, v in zip(trace["t"], trace["v"][k]):
        if t >= after and v:
            return t
    return None


def first_fall(trace, name, after=0.0):
    k = trace["names"].index(name)
    for t, v in zip(trace["t"], trace["v"][k]):
        if t >= after and not v:
            return t
    return None


HOME = [{"set": {"S_EStop": True, "S_LC": True}}, {"wait": 100}, {"set": {"S_Reset": True}}, {"wait": 50}, {"set": {"S_Reset": False}},
        {"until": {"H_Ready": True}, "within": 6000}]


def press_step(n=1):
    """手动方式下按 n 次“单步”。"""
    out = []
    for _ in range(n):
        out += [{"set": {"S_Step": True}}, {"wait": 50}, {"set": {"S_Step": False}}, {"wait": 50}]
    return out


def mode_tests():
    """15.4 节：上电不动、回原点、自动、单步、点动。"""
    auto = [{"set": {"S_Auto": True}}] + HOME
    return [
        {"id": "powerup", "steps": [{"set": {"S_EStop": True}}, {"never": {"Y_PressUp": True}, "during": 2000}, {"expect": {"H_Ready": False}}]},
        {"id": "home", "steps": HOME + [{"expect": {"B_PressUp": True, "B_Unclamped": True}}]},
        *[dict(t, id="auto_" + t["id"], steps=auto + t["steps"]) for t in auto_tests()],
        {"id": "step", "steps": HOME + [LOAD] + press_step(1) + [{"until": {"B_Clamped": True}, "within": 1000}, {"wait": 500},
            {"expect": {"Y_PressDown": False, "Y_Clamp": True}}] + press_step(1) + [HANDS, {"until": {"B_PressDown": True}, "within": 5000}, {"wait": 500},
            {"expect": {"Y_PressUp": False}}, FREE] + press_step(1) + [{"until": {"B_PressUp": True}, "within": 5000}] + press_step(1)
            + [{"until": {"B_Unclamped": True}, "within": 1000}, {"wait": 300}, {"expect": {"H_Ready": False}}] + press_step(1)
            + [{"wait": 50}, {"expect": {"H_Ready": True, "H_OK": True}}]},
        {"id": "jog", "steps": HOME + [LOAD, {"set": {"S_JogDown": True}}, {"wait": 300}, {"expect": {"Y_PressDown": False}},   # 没夹紧不许下行
            {"set": {"S_JogDown": False, "S_JogClamp": True}}, {"until": {"B_Clamped": True}, "within": 1000},
            {"set": {"S_JogDown": True}}, {"wait": 500}, {"expect": {"Y_PressDown": True, "hazard": False}},
            {"set": {"S_LC": False}}, {"wait": 20}, {"expect": {"Y_PressDown": False}}, {"set": {"S_LC": True, "S_JogDown": False, "S_JogUp": True}},
            {"until": {"B_PressUp": True}, "within": 3000}, {"set": {"S_JogUp": False, "S_JogClamp": False}}, {"wait": 500},
            {"expect": {"H_Ready": False, "hazard": False}}]},   # 点动过，要回原点才就绪
        {"id": "home_mid", "plant": None, "steps": HOME + [{"expect": {"B_PressUp": True}}]},
    ]


def fault_tests():
    """15.5 节：夹紧传感器断线、急停、上位开关粘连（传感器冲突）。"""
    auto = [{"set": {"S_Auto": True}}] + HOME
    return [
        {"id": "clamp_timeout", "faults": {"clampWire": True}, "steps": auto + [LOAD, {"wait": 200}, HANDS,
            {"until": {"H_Fault": True}, "within": 1500}, {"never": {"Y_PressDown": True}, "during": 1000}, FREE,
            {"set": {"S_Reset": True}}, {"wait": 50}, {"set": {"S_Reset": False}}, {"until": {"H_Ready": True}, "within": 3000}]},
        {"id": "estop", "steps": auto + [LOAD, {"wait": 200}, HANDS, {"wait": 1500}, {"set": {"S_EStop": False}}, {"wait": 20},
            {"expect": {"Y_PressDown": False, "Y_PressUp": False, "H_Fault": True, "hazard": False}}, {"wait": 500},
            {"set": {"S_EStop": True}}, {"never": {"Y_PressUp": True}, "during": 1000}, FREE,
            {"set": {"S_Reset": True}}, {"wait": 50}, {"set": {"S_Reset": False}}, {"until": {"H_Ready": True}, "within": 4000},
            {"expect": {"hazard": False}}]},
        {"id": "conflict", "faults": {"upStuck": True}, "steps": auto + [LOAD, {"wait": 200}, HANDS,
            {"until": {"H_Fault": True}, "within": 5000}, {"expect": {"Y_PressDown": False}}, {"never": {"Y_PressUp": True}, "during": 500}]},
    ]
