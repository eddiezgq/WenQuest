"""图 1.4.1：自动化金字塔与 ISA-95 的五层，以及问渠数字工厂里对应的部分。"""
from bookout import figure
from _draw01 import pyramid

LEVELS = [
    ("0", "现场：传感器与执行器", "Field: sensors, actuators", "输送线的光电开关、压装工位的气缸和光幕", "photo sensors, cylinders, light curtains", "ms"),
    ("1", "控制：PLC 与运动控制器", "Control: PLCs, motion controllers", "虚拟 PLC、各台设备的控制器", "virtual PLC, machine controllers", "1–100 ms"),
    ("2", "监控：HMI 与 SCADA", "Supervision: HMI, SCADA", "看板、3D 车间", "dashboards, 3D shop floor", "s"),
    ("3", "制造执行：MES", "Manufacturing execution: MES", "派工、作业卡、检验、班次记录", "dispatch, job cards, inspection, shifts", "min–h"),
    ("4", "企业：ERP", "Enterprise: ERP", "ERPNext：订单、工单、物料、成本", "ERPNext: orders, work orders, stock, cost", "d"),
]
figure(pyramid(LEVELS), "fig1_4_1")
