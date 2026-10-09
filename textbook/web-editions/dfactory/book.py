# -*- coding: utf-8 -*-
"""《数字工厂实训》网页版的篇章（第 29 轮）：一讲一章，12 章。课程大纲见 docs/课程体系/数字工厂实训/大纲.md。"""
TITLE = {"zh": "数字工厂实训", "en": "Digital Factory Practicum"}
SUBTITLE = {"zh": "智能工厂运营与决策", "en": "Operating a Smart Factory: Decisions with Data"}

PARTS = [
    # (zh numeral, zh name, en name, [chapter numbers])
    ("第一篇", "全景", "Part I · The Big Picture", [1, 2]),
    ("第二篇", "方法", "Part II · The Method", [3]),
    ("第三篇", "七个领域", "Part III · Seven Domains", [4, 5, 6, 7, 8, 9, 10]),
    ("第四篇", "AI 与综合", "Part IV · AI and Integration", [11, 12]),
]

# n: (zh title, en title, zh summary, en summary)
CH = {
 1: ("数字工厂与工业软件全景", "The Digital Factory and Its Software", "ERP、MES、PLM、QMS、EAM、数字孪生，统一数据总线", "ERP, MES, PLM, QMS, EAM, digital twins and a unified data bus"),
 2: ("订单到交付：ERP 与 MES 闭环", "Order to Delivery: Closing the ERP–MES Loop", "BOM、MRP、工单、报工、OEE、标准成本", "BOM, MRP, work orders, reporting, OEE, standard cost"),
 3: ("厂情中枢：异常、追因与推演", "The Factory Hub: Exceptions, Root Causes and What-ifs", "规则与异常、因果链、影响面、仿真推演、方案比较", "Rules and exceptions, causal chains, impact, simulation, comparing options"),
 4: ("客户与服务：追溯与召回", "Customers and Service: Traceability and Recall", "数字主线、批次追溯、召回范围、服务排班", "Digital thread, batch tracing, recall scope, service scheduling"),
 5: ("安全环保", "Safety and Environment", "危险源辨识、风险矩阵、挂牌上锁、作业许可", "Hazard identification, risk matrix, lockout–tagout, permits to work"),
 6: ("设备维护与可靠性", "Maintenance and Reliability", "威布尔分布、条件故障概率、预期损失、保养时机与最优周期、MTBF", "Weibull model, conditional failure probability, expected loss, PM timing and interval, MTBF"),
 7: ("人员与排班", "People and Shifts", "技能矩阵、单点依赖、排班缺口、加班成本", "Skills matrix, single points of dependency, shift gaps, overtime cost"),
 8: ("供应链与来料质量", "Supply Chain and Incoming Quality", "提前期、安全库存、抽样检验、供应商评分", "Lead time, safety stock, acceptance sampling, supplier scoring"),
 9: ("能源与碳", "Energy and Carbon", "分时电价、空转、需量、单件碳足迹", "Time-of-use tariffs, idling, demand charges, carbon per unit"),
 10: ("经营：毛利、应收与现金", "Business: Margin, Receivables and Cash", "订单毛利分解、应收账龄、DSO、现金流预测", "Order margin, receivables ageing, DSO, cash forecasting"),
 11: ("AI 代理与决策", "AI Agents and Decisions", "工具调用、引用与数字核对、比对模式、人机分工", "Tool use, citations and number checks, comparison mode, human–AI roles"),
 12: ("全厂综合与课程设计导论", "The Whole Plant and the Course Project", "跨领域因果、复盘、决策记录、两周情景", "Cross-domain causes, reviews, decision records, the two-week scenario"),
}

# 第 29 轮的样板讲（先做完整），其余各讲在样板满意后铺开
SAMPLE = [3, 6, 10]


def part_of(n):
    for p in PARTS:
        if n in p[3]:
            return p


NEW = []
