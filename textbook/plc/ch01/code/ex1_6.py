"""图 1.6.1：一个自动化项目从报价到交付的过程（V 形：左边写设计文件，右边逐层验证）。"""
from bookout import figure
from _draw01 import lifecycle

PHASES = [
    ("需求与报价", "Requirements and quote", "技术协议", "technical agreement", "L", 0),
    ("功能规格书", "Functional specification", "控制要求说明、I/O 表", "control requirements, I/O list", "L", 1),
    ("详细设计", "Detailed design", "电气图、选型、软件结构", "drawings, selection, software design", "L", 2),
    ("编程与仿真", "Programming and simulation", "PLC 程序、HMI、测试用例", "PLC program, HMI, test cases", "B", 3),
    ("自动化测试", "Automated testing", "测试报告（虚拟调试）", "test report (virtual commissioning)", "R", 2),
    ("工厂验收 FAT", "Factory acceptance (FAT)", "FAT 记录、问题清单", "FAT record, issue list", "R", 1),
    ("现场调试与 SAT", "Commissioning and SAT", "调试记录、SAT 记录、操作维护说明", "commissioning and SAT records, manuals", "R", 0),
]
figure(lifecycle(PHASES), "fig1_6_1")
