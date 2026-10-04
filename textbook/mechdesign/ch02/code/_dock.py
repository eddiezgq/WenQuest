"""第 2 章共用：Go2 四足机器人自动充电桩的对接机构——功能分解、形态矩阵、四个方案与评价准则（2.2、2.4 节；任务单 TS-2-1）。
功能和解法是本书按对接问题整理的；Go2 的重量、外形取自零件库 B-LEG-GO2。"""
# 分功能：(中文, English, [(解法中文, 解法英文), ...])
FUNCS = [
    ("走到桩前", "approach the dock", [("视觉标记导航", "visual-marker navigation"), ("红外信标", "infrared beacon"), ("地面导引条", "floor guide strip")]),
    ("消除位置误差", "absorb position error", [("V 形导槽", "V-shaped guide"), ("浮动接触板", "floating contact plate"), ("锥销定位", "taper-pin locating"), ("磁力自对中", "magnetic self-centring")]),
    ("接通电流", "make electrical contact", [("弹簧顶针", "spring pins"), ("刀片触点", "blade contacts"), ("无线感应", "inductive (wireless)"), ("插头插座", "plug and socket")]),
    ("保持接触", "hold contact", [("机身自重", "own weight"), ("永磁吸合", "permanent magnet"), ("机械卡扣", "mechanical latch")]),
    ("保护触点", "protect the contacts", [("翻盖", "flip cover"), ("毛刷", "brushes"), ("不设防护", "none")]),
]
# 不相容的组合（分功能序号, 解法序号）对：插头插座要求插入前的定位误差很小，只有锥销一类的精确定位配得上，
# V 形导槽、浮动板、磁力自对中都不够。（无线感应 + 机械卡扣只是多余，不算不相容。）
INCOMPATIBLE = [((2, 3), (1, 0)), ((2, 3), (1, 1)), ((2, 3), (1, 3))]
# 四个方案：每个分功能选哪个解法
CONCEPTS = {
    "A": ("趴下式弹簧顶针", "lie-down spring pins", [0, 0, 0, 0, 1]),
    "B": ("浮动板刀片触点", "floating plate, blade contacts", [0, 1, 1, 1, 0]),
    "C": ("无线感应垫", "inductive pad", [1, 3, 2, 0, 2]),
    "D": ("锥销插头", "taper pin and plug", [2, 2, 3, 2, 0]),
}
# 评价准则：(中文, English, 权重)
CRITERIA = [("对接成功率（容许位置误差）", "docking success (tolerance to position error)", 0.25), ("充电效率与发热", "charging efficiency and heat", 0.15),
            ("成本", "cost", 0.20), ("可靠性与寿命（磨损、粘污）", "reliability and life (wear, dirt)", 0.20),
            ("安全（裸露带电）", "safety (exposed live parts)", 0.10), ("对机器人改装量", "changes to the robot", 0.10)]
# 普氏矩阵：以 A 为基准，其余方案逐项 +1 / 0 / −1（评审小组的判断，示意）
PUGH = {"B": [1, 0, 0, 0, 0, -1], "C": [1, -1, -1, 1, 1, -1], "D": [-1, 1, -1, -1, 0, -1]}
# 加权评分：1–5 分（评审小组的打分，示意）
SCORES = {"A": [3, 4, 5, 3, 3, 4], "B": [4, 4, 4, 3, 3, 3], "C": [5, 2, 2, 5, 5, 2], "D": [2, 5, 3, 2, 3, 2]}
