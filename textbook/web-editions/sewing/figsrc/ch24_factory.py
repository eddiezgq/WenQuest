# -*- coding: utf-8 -*-
"""第 24 章 24.8 节：机针车间与旋梭车间的主数据（按问渠数字工厂 factory/data.py 的写法，示意值）。
运行：python3 figsrc/ch24_factory.py  → 打印每件占用的工作中心时间、单班产能（找瓶颈）和工序成本。"""

# 工作中心：名称: (台数/容量, (折旧, 人工, 能耗) 美元/小时)
WORKSTATIONS = {
    "切断机 NDL-CUT":        (1, (6, 10, 2)),
    "减径成形机 NDL-RED":    (4, (12, 8, 4)),
    "冲压机 NDL-PRS":        (2, (10, 8, 3)),
    "冲孔机 NDL-EYE":        (3, (12, 10, 3)),
    "针尖磨床 NDL-PT":       (2, (12, 8, 4)),
    "热处理线 NDL-HT":       (1, (14, 10, 12)),
    "校直机 NDL-STR":        (1, (6, 10, 2)),
    "抛光线 NDL-POL":        (1, (8, 8, 6)),
    "电镀线 NDL-PLT":        (1, (12, 10, 10)),
    "视觉检测 NDL-AOI":      (1, (14, 6, 2)),
    "包装机 NDL-PCK":        (1, (4, 10, 1)),
    "数控车床 HK-CNC":       (3, (18, 24, 6)),
    "五轴加工中心 HK-5AX":   (4, (40, 26, 10)),
    "热处理炉 HK-HT":        (40, (10, 12, 12)),   # 一炉 40 件，分钟数为分摊到每件的炉时
    "梭道磨床 HK-GRD":       (2, (24, 26, 6)),
    "研磨工位 HK-LAP":       (3, (4, 30, 1)),
    "涂层炉 HK-PVD":         (60, (30, 12, 20)),   # 一炉 60 件
    "选配站 HK-MATCH":       (1, (10, 28, 2)),
    "跑合噪声台 HK-RUN":     (2, (8, 16, 4)),
    "检验站 QC-01":          (1, (8, 30, 2)),
}
OPERATIONS = {
    "切断 Cut-off": "切断机 NDL-CUT",
    "针身减径 Blade reducing": "减径成形机 NDL-RED",
    "冲槽与凹口 Groove & scarf pressing": "冲压机 NDL-PRS",
    "冲针孔 Eye punching": "冲孔机 NDL-EYE",
    "磨针尖 Point grinding": "针尖磨床 NDL-PT",
    "淬火回火 Harden & temper": "热处理线 NDL-HT",
    "校直 Straightening": "校直机 NDL-STR",
    "抛光 Polishing": "抛光线 NDL-POL",
    "镀铬 Chrome plating": "电镀线 NDL-PLT",
    "视觉检测 Vision inspection": "视觉检测 NDL-AOI",
    "包装 Packing": "包装机 NDL-PCK",
    "粗车 Rough turning": "数控车床 HK-CNC",
    "精车 Finish turning": "数控车床 HK-CNC",
    "铣梭尖与梭道 Point & race milling": "五轴加工中心 HK-5AX",
    "铣梭床轮廓 Basket milling": "五轴加工中心 HK-5AX",
    "渗碳淬火 Carburising": "热处理炉 HK-HT",
    "整体淬火 Through hardening": "热处理炉 HK-HT",
    "磨梭道 Race grinding": "梭道磨床 HK-GRD",
    "磨导轨 Rib grinding": "梭道磨床 HK-GRD",
    "研磨梭尖 Point lapping": "研磨工位 HK-LAP",
    "DLC 涂层 DLC coating": "涂层炉 HK-PVD",
    "测量分组 Gauging & grading": "选配站 HK-MATCH",
    "选配装配 Selective fitting": "选配站 HK-MATCH",
    "跑合与噪声 Run-in & noise": "跑合噪声台 HK-RUN",
    "零件检验 Part inspection": "检验站 QC-01",
    "出厂检验 Final inspection": "检验站 QC-01",
}
# 工艺路线：名称: [(工序, 分钟)]；机针按每千支计，旋梭按每件计
ROUTINGS = {
    "RT-机针 Needle (per 1000)": [
        ("切断 Cut-off", 2), ("针身减径 Blade reducing", 12), ("冲槽与凹口 Groove & scarf pressing", 8),
        ("冲针孔 Eye punching", 10), ("磨针尖 Point grinding", 8), ("淬火回火 Harden & temper", 6),
        ("校直 Straightening", 5), ("抛光 Polishing", 6), ("镀铬 Chrome plating", 5),
        ("视觉检测 Vision inspection", 4), ("包装 Packing", 3)],
    "RT-旋梭体 Hook body": [
        ("粗车 Rough turning", 6), ("精车 Finish turning", 5), ("铣梭尖与梭道 Point & race milling", 12),
        ("渗碳淬火 Carburising", 4), ("磨梭道 Race grinding", 8), ("研磨梭尖 Point lapping", 6),
        ("DLC 涂层 DLC coating", 3), ("零件检验 Part inspection", 2)],
    "RT-梭床 Basket": [
        ("粗车 Rough turning", 4), ("精车 Finish turning", 3), ("铣梭床轮廓 Basket milling", 8),
        ("整体淬火 Through hardening", 3), ("磨导轨 Rib grinding", 6), ("DLC 涂层 DLC coating", 3),
        ("零件检验 Part inspection", 2)],
    "RT-旋梭组件 Hook assembly": [
        ("测量分组 Gauging & grading", 1), ("选配装配 Selective fitting", 2),
        ("跑合与噪声 Run-in & noise", 5), ("出厂检验 Final inspection", 2)],
}
BOMS = {
    "ND-DB1-90": ("RT-机针 Needle (per 1000)", [("RM-WIRE-162", 1.1)]),        # 千支耗丝约 1.1 kg（示意）
    "HK-BODY": ("RT-旋梭体 Hook body", [("RM-FORG-HK", 1)]),
    "HK-BASKET": ("RT-梭床 Basket", [("RM-BAR-BRG", 0.06)]),
    "HK-ASM": ("RT-旋梭组件 Hook assembly", [("HK-BODY", 1), ("HK-BASKET", 1), ("HK-GIB", 1), ("SCR-M3", 2)]),
}

if __name__ == "__main__":
    SHIFT = 480
    for prod, rts in (("机针（每千支）", ["RT-机针 Needle (per 1000)"]),
                      ("旋梭（每套）", ["RT-旋梭体 Hook body", "RT-梭床 Basket", "RT-旋梭组件 Hook assembly"])):
        use = {}
        cost = 0.0
        for rt in rts:
            for op, m in ROUTINGS[rt]:
                wc = OPERATIONS[op]
                use[wc] = use.get(wc, 0) + m
                cost += m / 60 * sum(WORKSTATIONS[wc][1])
        print("==", prod, "总工时 %d 分钟，工序成本 %.2f 美元" % (sum(use.values()), cost))
        rows = sorted(use.items(), key=lambda kv: SHIFT * WORKSTATIONS[kv[0]][0] / kv[1])
        for wc, m in rows:
            cap = WORKSTATIONS[wc][0]
            print("| %s | %d | %d | %.1f |" % (wc, m, cap, SHIFT * cap / m))
