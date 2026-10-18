# -*- coding: utf-8 -*-
"""机型登记（第 40 轮）：平缝机、包缝机、绷缝机。网关、计算书、FreeCAD 都按 machine 键找到对应的计算模块。"""
from . import cover, design, overlock

MACHINES = {"lockstitch": design, "overlock": overlock, "cover": cover}
ORDER = ["lockstitch", "overlock", "cover"]


def get(machine):
    return MACHINES.get(machine or "lockstitch") or design
