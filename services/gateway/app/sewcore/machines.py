# -*- coding: utf-8 -*-
"""机型登记（第 40 轮；第 42 轮加电子花样机、多头刺绣机）。网关、计算书、FreeCAD 都按 machine 键找到对应的计算模块。"""
from . import cover, design, embroid, overlock, pattern

MACHINES = {"lockstitch": design, "overlock": overlock, "cover": cover, "pattern": pattern, "embroid": embroid}
ORDER = ["lockstitch", "overlock", "cover", "pattern", "embroid"]


def get(machine):
    return MACHINES.get(machine or "lockstitch") or design
