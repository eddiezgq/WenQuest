"""图 1.2.1：PLC 发展大事记（年份见 1.2 节与章末参考文献）。"""
from bookout import figure
from _draw01 import timeline

EVENTS = [
    (1968, "通用汽车提出\n“标准机器控制器”规格", "GM issues the 'standard\nmachine controller' spec", 0, 0),
    (1969, "Modicon 084\n交付通用汽车", "Modicon 084\ndelivered to GM", 0, 1),
    (1979, "西门子 SIMATIC S5", "Siemens SIMATIC S5", 0, 0),
    (1994, "CODESYS 发布\n（编程软件与运行时）", "CODESYS released\n(IDE and runtime)", 0, 0),
    (2010, "震网病毒攻击 PLC\n被公开", "Stuxnet attack on\nPLCs made public", 0, 0),
    (1992, "PLCopen 成立", "PLCopen founded", 1, 0),
    (1993, "IEC 61131-3 第 1 版", "IEC 61131-3 ed. 1", 1, 1),
    (2000, "ISA-95 第 1 部分", "ISA-95 Part 1", 1, 0),
    (2003, "IEC 61131-3 第 2 版\n（修订版）", "IEC 61131-3 ed. 2\n(revision)", 1, 2),
    (2005, "IEC 61499\n分布式控制", "IEC 61499\ndistributed control", 1, 0),
    (2006, "OPC UA 规范 1.0", "OPC UA 1.0", 1, 1),
    (2013, "IEC 61131-3 第 3 版\n（面向对象）", "IEC 61131-3 ed. 3\n(object-oriented)", 1, 0),
    (2025, "IEC 61131-3 第 4 版\n（删去指令表）", "IEC 61131-3 ed. 4\n(IL removed)", 1, 1),
]
figure(timeline(EVENTS), "fig1_2_1")
