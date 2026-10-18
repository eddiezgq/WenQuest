# -*- coding: utf-8 -*-
"""问渠缝纫机设计软件的计算核心（第 39 轮）。网关的网页版与 FreeCAD 工作台共用。"""
from .design import (CHOICES, DEFAULTS, GROUPS, PARAMS, VERSION, adjust_card, analyze, chain, clean, mech_of, parts,  # noqa: F401
                     proto_cfg)
from .kit import Mech  # noqa: F401
