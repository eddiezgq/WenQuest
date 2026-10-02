# -*- coding: utf-8 -*-
"""
第 27 章 · 缝纫机整机厂（示意）的主数据草稿：工业平缝机 WQ-LS 系列。

仿照问渠数字工厂 factory/factory/data.py（减速器 WQR-105）的结构写成：
ITEMS / WORKSTATIONS / OPERATIONS / ROUTINGS / BOMS / inspection_templates() / LIBRARY_REFS。
这是**方案（待建）**：问渠数字工厂里目前只有减速器厂；本文件是 27.10 节学生项目的起点。
所有数值都是教学用的示意值，不代表任何企业。

本书第 27 章正文表 27-5（工作中心负荷）由 ch27_model.py 调用本文件计算。
"""

# ---------------------------------------------------------------- 配置选项（机型 × 选项）
# 选项码: (中文, 英文, 增加的物料, 去掉的物料)
OPTIONS = {
    "T": ("自动剪线", "Automatic thread trimming",
          [("SA-TRIM", 1)], []),
    "E": ("电子针距", "Electronic stitch length",
          [("SA-EFEED", 1)], [("SA-MFEED", 1)]),
    "D": ("少油旋梭（DLC）", "Micro-oil hook (DLC)",
          [("SA-HOOK-D", 1)], [("SA-HOOK", 1)]),
}


def variants():
    """8 种配置：WQ-LS、WQ-LS-T、WQ-LS-E……WQ-LS-TED。"""
    import itertools
    out = []
    for n in range(0, 4):
        for c in itertools.combinations("TED", n):
            out.append("WQ-LS" + ("-" + "".join(c) if c else ""))
    return out


# ---------------------------------------------------------------- 物料
# 代号: (名称, 类别 raw/buy/make/sub/fg/fw, 单位, 供应商键或 None, 检验模板, 备注)
ITEMS = {
    # 原材料
    "RM-HT250-LS":  ("机壳铸件 HT250 Housing casting", "raw", "Nos", "castings", "进货检验-铸件", "按炉号（熔炼批）管理，时效后交货（第 25 章）"),
    "RM-20CRMO-D40": ("20CrMo 圆钢 Ø40 Steel bar", "raw", "Kg", "steel", None, "旋梭毛坯（第 24 章）"),
    "RM-GCR15-D30": ("GCr15 圆钢 Ø30 Bearing steel bar", "raw", "Kg", "steel", None, "凸轮、轴"),
    # 外购件
    "NDL-DB1-14":  ("机针 DB×1 14# Needle", "buy", "Nos", "needles", "进货检验-机针", "外购，按批次（第 24 章）"),
    "MOT-LS-SV":   ("直驱伺服电机 Direct-drive servo motor", "buy", "Nos", "motors", "进货检验-电机", "建议零件库编号 D-MOT-PMSM，计划入库"),
    "CTL-WQSC-LS": ("电控箱 WQ-SC/LS Control box", "buy", "Nos", "electronics", "进货检验-电控箱", "按本厂规格外协制造；出厂测试时烧录本厂固件"),
    "SOL-TRIM":    ("剪线电磁铁 Trimming solenoid", "buy", "Nos", "electronics", None, "建议编号 D-SOL-PUSH，计划入库"),
    "SOL-WIPE":    ("拨线电磁铁 Wiper solenoid", "buy", "Nos", "electronics", None, "建议编号 D-SOL-PUSH，计划入库"),
    "STP-FEED":    ("送布步进电机（闭环） Closed-loop stepper", "buy", "Nos", "electronics", None, "建议编号 D-MOT-STEP，计划入库"),
    "BRG-6000":    ("深沟球轴承 6000 Ball bearing", "buy", "Nos", "bearings", None, "零件库 A-BRG-DG"),
    "BRG-6201":    ("深沟球轴承 6201 Ball bearing", "buy", "Nos", "bearings", None, "零件库 A-BRG-DG"),
    "BELT-HTD":    ("上下轴同步带 Timing belt", "buy", "Nos", "hardware", None, "零件库 C-BLT-BELT"),
    "PUL-HTD":     ("同步带轮 Timing pulley", "buy", "Nos", "hardware", None, "零件库 A-PUL-HTD"),
    "BOBBIN-CASE": ("梭壳 Bobbin case", "buy", "Nos", "hooks", None, "与旋梭选配（第 24 章）"),
    "SCR-SET":     ("螺钉包 Screw kit", "buy", "Set", "hardware", None, "零件库 A-SCR-SHC 等"),
    # 自制零件
    "HSG-LS01":   ("机壳 Housing", "make", "Nos", None, "零件检验-机壳", "一次装夹镗孔（第 25 章）"),
    "HK-LS01":    ("旋梭 Rotary hook", "make", "Nos", None, "零件检验-旋梭", "渗碳、梭道磨削、梭尖研磨（第 24 章）"),
    "HK-LS01D":   ("少油旋梭（DLC）Micro-oil hook", "make", "Nos", None, "零件检验-旋梭", "在 HK-LS01 上加 DLC 外协工序"),
    "CAM-LS01":   ("抬牙凸轮 Feed-lift cam", "make", "Nos", None, "零件检验-凸轮", "廓线磨削（第 25 章）"),
    "CAM-LS02":   ("剪线凸轮 Trimmer cam", "make", "Nos", None, "零件检验-凸轮", "只用于 T 选项"),
    "SH-LS01":    ("上轴 Arm shaft", "make", "Nos", None, None, ""),
    "SH-LS02":    ("下轴 Hook shaft", "make", "Nos", None, None, ""),
    # 部件
    "SA-HSG":    ("机壳组件 Housing assembly", "sub", "Nos", None, None, ""),
    "SA-ARM":    ("上轴与针杆组件 Arm-shaft & needle-bar assy", "sub", "Nos", None, None, ""),
    "SA-HOOK":   ("下轴与旋梭组件 Hook-shaft & hook assy", "sub", "Nos", None, None, ""),
    "SA-HOOK-D": ("下轴与少油旋梭组件 Hook assy, micro-oil", "sub", "Nos", None, None, "D 选项"),
    "SA-MFEED":  ("机械针距送布组件 Mechanical feed assy", "sub", "Nos", None, None, ""),
    "SA-EFEED":  ("电子针距送布组件 Electronic feed assy", "sub", "Nos", None, None, "E 选项"),
    "SA-TRIM":   ("剪线组件 Trimmer assy", "sub", "Nos", None, None, "T 选项"),
    # 固件也是物料：有版本，由出厂测试台烧录并核对
    "FW-WQSC-LS": ("WQ-SC/LS 主控固件 Firmware", "fw", "Nos", None, None, "版本号随序列号记录；参数表、事件表另有版本"),
    # 成品（模板 + 8 个变型，见 variants()）
    "WQ-LS":     ("工业平缝机 WQ-LS Industrial lockstitch machine", "fg", "Nos", None, "出厂检验-平缝机", "物料模板，按选项生成变型"),
}

# ---------------------------------------------------------------- 工作中心
# 名称: (台数, 每天开动班数, 单位/小时费率示意)
WORKSTATIONS = {
    "立式加工中心 VMC-H":   (5, 2, 60),
    "卧式加工中心 HMC-H":   (5, 2, 75),
    "数控车床 CNC-S":       (8, 2, 45),
    "热处理线 HT-01":       (1, 2, 40),   # 连续式，按每件分摊的炉时计
    "外圆磨床 GRD-S":       (3, 2, 50),
    "梭道磨床 GRD-H":       (2, 2, 55),
    "梭尖研磨机 LAP-H":     (2, 2, 40),
    "凸轮磨床 GRD-C":       (2, 2, 60),
    "三坐标 CMM-01":        (1, 2, 45),
    "检验站 QC-01":         (2, 2, 40),
    "总装线 ASM-L1":        (1, 1, 30),   # 一条线，节拍 2.4 min → 25 台/h
    "调试工位 ADJ":         (5, 1, 35),   # 旋梭定时、针杆高度、梭尖间隙
    "跑合台 RUN":           (15, 1, 10),
    "出厂测试台 EOL":       (3, 1, 40),   # 第 22 章
}

# 工艺路线：名称: [(工序, 工作中心, 每件分钟)]
ROUTINGS = {
    "RT-机壳 Housing": [
        ("铣基准面 Datum milling", "立式加工中心 VMC-H", 6),
        ("一次装夹镗孔 Single-setup boring", "卧式加工中心 HMC-H", 16),
        ("钻攻 Drilling & tapping", "立式加工中心 VMC-H", 8),
        ("孔系检验（每 10 件抽 1 件） CMM sampling", "三坐标 CMM-01", 2),
        ("零件检验 Part inspection", "检验站 QC-01", 2)],
    "RT-旋梭 Hook": [
        ("车削 Turning", "数控车床 CNC-S", 7),
        ("渗碳淬火 Carburising", "热处理线 HT-01", 1),
        ("磨梭道 Race grinding", "梭道磨床 GRD-H", 6),
        ("研磨梭尖 Point lapping", "梭尖研磨机 LAP-H", 5),
        ("零件检验 Part inspection", "检验站 QC-01", 1.5)],
    "RT-凸轮 Cam": [
        ("车削 Turning", "数控车床 CNC-S", 4),
        ("淬火 Hardening", "热处理线 HT-01", 0.5),
        ("磨廓线 Profile grinding", "凸轮磨床 GRD-C", 3.5),
        ("零件检验 Part inspection", "检验站 QC-01", 1)],
    "RT-轴 Shaft": [
        ("车削 Turning", "数控车床 CNC-S", 5),
        ("淬火 Hardening", "热处理线 HT-01", 0.5),
        ("磨外圆 Grinding", "外圆磨床 GRD-S", 4)],
    "RT-总装 Final assembly": [
        ("总装 12 工位 Line assembly", "总装线 ASM-L1", 2.4),
        ("调试 Adjustment", "调试工位 ADJ", 9.6),
        ("跑合 Run-in", "跑合台 RUN", 30),
        ("出厂测试 EOL test", "出厂测试台 EOL", 4.8)],
}
# DLC 镀膜是外协工序（不占本厂工作中心，只加交期），见 27.3 节
SUBCONTRACT = {"HK-LS01D": ("DLC 镀膜外协 DLC coating (subcontract)", 5)}   # 交期 5 天（示意）

# 每台整机用到的自制件（模板的平均组合：剪线选项 70%）
MADE_PER_UNIT = {"HSG-LS01": ("RT-机壳 Housing", 1), "HK-LS01": ("RT-旋梭 Hook", 1),
                 "CAM-LS01": ("RT-凸轮 Cam", 1), "CAM-LS02": ("RT-凸轮 Cam", 0.7),
                 "SH-LS01": ("RT-轴 Shaft", 1), "SH-LS02": ("RT-轴 Shaft", 1),
                 "WQ-LS": ("RT-总装 Final assembly", 1)}

# ---------------------------------------------------------------- BOM（EBOM 的一部分，按部件组织）
BOMS = {
    "SA-HSG":    [("HSG-LS01", 1), ("SCR-SET", 1)],
    "SA-ARM":    [("SH-LS01", 1), ("BRG-6201", 2), ("PUL-HTD", 1)],
    "SA-HOOK":   [("SH-LS02", 1), ("HK-LS01", 1), ("BOBBIN-CASE", 1), ("BRG-6000", 2), ("PUL-HTD", 1)],
    "SA-HOOK-D": [("SH-LS02", 1), ("HK-LS01D", 1), ("BOBBIN-CASE", 1), ("BRG-6000", 2), ("PUL-HTD", 1)],
    "SA-MFEED":  [("CAM-LS01", 1)],
    "SA-EFEED":  [("CAM-LS01", 1), ("STP-FEED", 1)],
    "SA-TRIM":   [("CAM-LS02", 1), ("SOL-TRIM", 1), ("SOL-WIPE", 1)],
    "WQ-LS":     [("SA-HSG", 1), ("SA-ARM", 1), ("SA-HOOK", 1), ("SA-MFEED", 1), ("BELT-HTD", 1),
                  ("MOT-LS-SV", 1), ("CTL-WQSC-LS", 1), ("FW-WQSC-LS", 1), ("NDL-DB1-14", 1)],
}

# 标准件在问渠零件库里的编号（已有条目）；电控模块是建议编号、计划入库
LIBRARY_REFS = {"BRG-6000": "A-BRG-DG/6000", "BRG-6201": "A-BRG-DG/6201", "PUL-HTD": "A-PUL-HTD",
                "BELT-HTD": "C-BLT-BELT", "SCR-SET": "A-SCR-SHC", "CAM-LS01": "C-CAM-DISC"}
PROPOSED_REFS = {"MOT-LS-SV": "D-MOT-PMSM", "SOL-TRIM": "D-SOL-PUSH", "SOL-WIPE": "D-SOL-PUSH",
                 "STP-FEED": "D-MOT-STEP", "CTL-WQSC-LS": "D-CTL-WQSC"}


# ---------------------------------------------------------------- 检验计划
def _num(name, lo, hi):
    return {"parameter": name, "numeric": 1, "min": lo, "max": hi}


def _text(name, value):
    return {"parameter": name, "numeric": 0, "value": value}


def inspection_templates():
    return {
        "进货检验-机针": [_text("外观与针尖 Appearance & point", "无弯曲、针尖无毛刺"),
                         _num("针杆直线度 Straightness (mm)", 0, 0.02)],
        "进货检验-铸件": [_text("铸件外观 Casting appearance", "无砂眼、气孔、裂纹"),
                         _num("铸件硬度 Hardness (HB)", 180, 240)],
        "零件检验-机壳": [_num("上下轴孔平行度 Shaft-bore parallelism (mm)", 0, 0.015),
                         _num("针杆套孔位置度 Needle-bar bore position (mm)", 0, 0.03)],
        "零件检验-旋梭": [_num("梭尖到安装基准 Point to datum (mm)", -0.01, 0.01),
                         _num("表面硬度 Surface hardness (HRC)", 58, 64)],
        "零件检验-凸轮": [_num("廓线误差 Profile error (mm)", 0, 0.015),
                         _num("硬度 Hardness (HRC)", 58, 63)],
        "调试检验": [_num("梭尖间隙 Hook-point clearance (mm)", 0.04, 0.10),
                    _num("钩线定时偏差 Hook-timing error (deg)", -1.5, 1.5)],
        "出厂检验-平缝机": [_num("停针定位误差 Needle-up positioning error (deg)", -1, 1),
                           _text("剪线 50 次 Trimming ×50", "全部成功"),
                           _text("固件版本核对 Firmware check", "与工单要求一致")],
    }
