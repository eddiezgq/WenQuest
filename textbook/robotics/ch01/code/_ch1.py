"""第 1 章共用：读取零件库模型的关节表、按关节表算正运动学、统计自由度，以及数字工厂的车间布置。
以下划线开头，构建时不单独运行。

数据来源：
- textbook/robotics/models/<编号>/entry.json：零件库条目（关节表、连杆质量、厂家参数表 datasheet）；
- 模型的 MJCF 原文件（MuJoCo Menagerie，提交 4d038b3feae26ec82b46a4d586379114012a8ac7）中几项不在关节表里的事实，
  抄在下面的 MJCF 字典里，并注明出处；
- factory/factory/data.py（工艺路线）与 factory/digital/wqbus/layout.py（车间平面、AGV 路线），与数字工厂同一份数据。
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MODELS = HERE.parents[1] / "models"

# 书中五台贯穿机器人，以及零件库里另外三台
FIVE = ["B-ARM-UR5E", "B-ARM-PANDA", "B-LEG-GO2", "B-EDU-DIFF", "B-UAV-X2"]
ALL8 = FIVE[:2] + ["B-SCA-WQ4", "B-PAR-DELTA"] + FIVE[2:3] + ["B-HUM-G1"] + FIVE[3:]

# 关节表之外的模型事实（MJCF 原文件）
MENAGERIE = "https://github.com/google-deepmind/mujoco_menagerie/tree/4d038b3feae26ec82b46a4d586379114012a8ac7"
MJCF = {
    # base：fixed 固定在地面；free 自由刚体（<freejoint/>，6 个自由度）；planar 在地面上运动（差速小车，3 个位姿变量）
    "B-ARM-UR5E": {"base": "fixed", "actuators": 6},                      # ur5e.xml：6 个 general 执行器
    "B-ARM-PANDA": {"base": "fixed", "actuators": 8, "coupled": [("finger_joint1", "finger_joint2")]},
    # panda.xml：7 个关节执行器 + 1 个手爪执行器（tendon "split"）；<equality><joint joint1="finger_joint1" joint2="finger_joint2"/>
    "B-LEG-GO2": {"base": "free", "actuators": 12},                       # go2.xml：<freejoint/>，12 个 motor
    "B-UAV-X2": {"base": "free", "actuators": 4,                          # x2.xml：<freejoint/>，4 个 motor（推力）
                 "thrust_max_N": 13.0,                                    # <motor ctrlrange="0 13"/>
                 "rotor_xyz": [(-0.14, -0.18, 0.05), (-0.14, 0.18, 0.05), (0.14, 0.18, 0.08), (0.14, -0.18, 0.08)],
                 "yaw_gear": [-0.0201, 0.0201, -0.0201, 0.0201],         # gear="0 0 1 0 0 ∓.0201"：反扭矩系数 m
                 "hover_N": 3.2495625},                                   # <key name="hover" ctrl="3.2495625 …"/>
    "B-HUM-G1": {"base": "free", "actuators": 29},
    "B-SCA-WQ4": {"base": "fixed", "actuators": 4},
    "B-PAR-DELTA": {"base": "fixed", "actuators": 3, "closed": True},
    "B-EDU-DIFF": {"base": "planar", "actuators": 2},
}
BASE_DOF = {"fixed": 0, "free": 6, "planar": 3}
G = 9.81                                    # 重力加速度，m/s²


def entry(eid: str) -> dict:
    return json.loads((MODELS / eid / "entry.json").read_text(encoding="utf-8"))


def movable(e: dict) -> list[dict]:
    """关节表中能动的关节（转动、连续转动、移动），即模型的关节变量。"""
    return [j for j in e["robot"]["joints"] if j["type"] in ("revolute", "continuous", "prismatic")]


def dof_summary(eid: str) -> dict:
    """由关节表统计一台机器人的关节变量、基座自由度、执行器数和独立的构型变量数。"""
    e = entry(eid)
    js = movable(e)
    info = MJCF[eid]
    n_rev = sum(j["type"] in ("revolute", "continuous") for j in js)
    n_pri = sum(j["type"] == "prismatic" for j in js)
    n_coupled = len(info.get("coupled", []))            # 每一对联动关节少一个独立变量
    base = BASE_DOF[info["base"]]
    joints_indep = len(js) - n_coupled
    return {"id": eid, "name": e["name"], "type": e["robot"]["type"], "n_joints": len(js), "n_rev": n_rev, "n_pri": n_pri,
            "coupled": n_coupled, "joints_indep": joints_indep, "base": info["base"], "base_dof": base,
            "config_dof": base + joints_indep, "actuators": info["actuators"], "closed": bool(info.get("closed")),
            "mass_model": sum((l.get("mass_kg") or 0.0) for l in e["robot"]["links"]),
            "datasheet": (e.get("datasheet") or {}).get("values", {})}


# ---------------------------------------------------------------- 按关节表做正运动学（URDF 的写法：平移、RPY、绕轴转）

def rot_axis(a, t):
    a = np.asarray(a, float) / np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def rpy(r, p, y):
    cr, sr, cp, sp, cy, sy = math.cos(r), math.sin(r), math.cos(p), math.sin(p), math.cos(y), math.sin(y)
    return np.array([[cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
                     [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
                     [-sp, cp * sr, cp * cr]])


def fk_point(e: dict, q: dict, link: str, xyz=(0, 0, 0)) -> np.ndarray:
    """link 上一点（在 link 自身坐标系中为 xyz）在根连杆坐标系中的位置；q：{关节名: 转角 rad 或位移 m}。"""
    by_child = {j["child"]: j for j in e["robot"]["joints"]}
    chain, n = [], link
    while n in by_child:
        chain.insert(0, by_child[n])
        n = by_child[n]["parent"]
    T = np.eye(4)
    for j in chain:
        o = j.get("origin") or {}
        A = np.eye(4)
        A[:3, :3] = rpy(*o.get("rpy", (0, 0, 0)))
        A[:3, 3] = o.get("xyz", (0, 0, 0))
        M = np.eye(4)
        t = q.get(j["name"], 0.0)
        if j["type"] == "prismatic":
            M[:3, 3] = np.asarray(j["axis"], float) * t
        elif j["type"] in ("revolute", "continuous"):
            M[:3, :3] = rot_axis(j["axis"], t)
        T = T @ A @ M
    return (T @ np.r_[np.asarray(xyz, float), 1.0])[:3]


# ---------------------------------------------------------------- 数字工厂（与工厂仿真同一份数据）

def factory():
    """返回 (data, layout)：工厂数据模块和车间布置模块。"""
    for p in (ROOT / "factory", ROOT / "factory" / "digital"):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    from factory import data            # noqa: E402
    from wqbus import layout            # noqa: E402
    return data, layout


# 工序 → 默认设备（factory/digital/sim/engine.py 的 OP_UNITS 中每道工序的第一台设备）
OP_UNIT = {"下料 Sawing": "saw-01", "粗车 Rough turning": "cnc-l01-a", "精车 Finish turning": "cnc-l01-b",
           "调质 Quench & temper": "ht-01", "渗碳淬火 Carburizing": "ht-01", "铣键槽 Keyway milling": "key-01",
           "滚齿 Gear hobbing": "hob-01", "磨外圆 Cylindrical grinding": "grd-01", "零件检验 Part inspection": "qc-01"}
AGV_SPEED = 1.0          # m/s，工厂仿真的 AGV 速度（engine.py: AGV_SPEED）
LOAD_UNLOAD_S = 30       # s，每次装或卸（engine.py: LOAD_UNLOAD_S）

# 算例 1.1.1 的假设（AGV 停车）
STOP_TC = 0.02           # 控制周期，s
STOP_TP = 0.08           # 识别障碍、发出指令到制动器起作用的时间，s
STOP_A = 0.5             # 制动减速度，m/s²


def stop_distance(v, t_d, a):
    """式 (1.1.4)：d = v·t_d + v²/(2a)。"""
    return v * t_d + v * v / (2 * a)


# ---------------------------------------------------------------- 1.2 节：历史年表与统计数据（出处见 1.2 节和本章参考文献）

# (年份, 中文, English, 线索)。线索：auto 自动机与程序；ctrl 反馈与控制；ind 工业机器人；ai 智能、移动与学习
TIMELINE = [
    (-250, "克特西比乌斯：带浮子调节的水钟", "Ctesibius: water clock with a float regulator", "ctrl"),
    (60, "希罗：绳索与木钉“编程”的自动小车", "Hero: a cart programmed by rope and pegs", "auto"),
    (1088, "苏颂、韩公廉：水运仪象台", "Su Song, Han Gonglian: astronomical clock tower", "auto"),
    (1206, "加扎里：《精巧机械装置知识书》", "al-Jazari: Book of Ingenious Mechanical Devices", "auto"),
    (1739, "沃康松：消化鸭", "Vaucanson: the Digesting Duck", "auto"),
    (1774, "雅克-德罗：书写者（凸轮编程）", "Jaquet-Droz: the Writer (programmed by cams)", "auto"),
    (1788, "瓦特：离心调速器", "Watt: centrifugal governor", "ctrl"),
    (1804, "雅卡尔：穿孔卡片织机", "Jacquard loom controlled by punched cards", "auto"),
    (1868, "麦克斯韦：《论调速器》", "Maxwell: On Governors", "ctrl"),
    (1920, "恰佩克：《罗素姆万能机器人》", "Čapek: R.U.R.", "ind"),
    (1942, "阿西莫夫：机器人三定律", "Asimov: Three Laws of Robotics", "ai"),
    (1948, "维纳：《控制论》；沃尔特：机器乌龟", "Wiener: Cybernetics; Walter: robot tortoises", "ctrl"),
    (1954, "德沃尔：申请“程序控制物件传送”专利", "Devol: files the Programmed Article Transfer patent", "ind"),
    (1955, "德纳维特、哈滕贝格：DH 参数", "Denavit, Hartenberg: DH parameters", "ind"),
    (1961, "第一台 Unimate 在通用汽车投入使用", "First Unimate goes to work at General Motors", "ind"),
    (1966, "斯坦福研究所：Shakey（至 1972 年）", "SRI: Shakey (until 1972)", "ai"),
    (1969, "沙因曼：斯坦福机械臂", "Scheinman: Stanford Arm", "ind"),
    (1973, "早稻田大学 WABOT-1；库卡 FAMULUS", "Waseda WABOT-1; KUKA FAMULUS", "ind"),
    (1974, "ASEA IRB 6：全电动、微处理器控制", "ASEA IRB 6: all-electric, microprocessor control", "ind"),
    (1978, "PUMA；牧野洋：SCARA", "PUMA; Makino: SCARA", "ind"),
    (1984, "布罗克特：指数积公式", "Brockett: product-of-exponentials formula", "ind"),
    (1986, "布鲁克斯：包容式结构", "Brooks: subsumption architecture", "ai"),
    (1996, "本田 P2 仿人机器人", "Honda P2 humanoid", "ai"),
    (1997, "旅居者号火星车", "Sojourner Mars rover", "ai"),
    (2000, "达芬奇手术系统获美国 FDA 批准", "da Vinci surgical system cleared by the US FDA", "ai"),
    (2002, "Roomba 扫地机器人", "Roomba robot vacuum", "ai"),
    (2005, "斯坦福 Stanley 赢得 DARPA 无人车挑战赛", "Stanford's Stanley wins the DARPA Grand Challenge", "ai"),
    (2008, "优傲 UR5：协作机器人进入工厂", "Universal Robots UR5: cobots enter factories", "ind"),
    (2012, "亚马逊收购 Kiva；深度学习兴起", "Amazon buys Kiva; deep learning takes off", "ai"),
    (2023, "视觉-语言-动作模型 RT-2；宇树 Go2", "Vision-language-action model RT-2; Unitree Go2", "ai"),
    (2025, "全球在役工业机器人约 500 万台", "About 5 million industrial robots in operation", "ind"),
]

# IFR World Robotics：工业机器人年安装量（台）与在役量
IFR = {
    "inst_2024": 542076,            # WR 2025（2025-09-25 发布）：2024 年安装 542 076 台
    "stock_2024": 4664000,          # 2024 年末在役 4 664 000 台
    "growth_2025": 0.11,            # WR 2026（2026-09-24 发布）：2025 年安装量增长 11%，“超过 60 万台”
    "stock_2025": 5.0e6,            # 2025 年末在役“创纪录的 500 万台”（增长 9%）
    "fc_2026": 655000, "fc_2029": 806000,       # WR 2026 预测
    # 各国安装量：2024 年（WR 2025），2025 年（WR 2026）
    # 德国 2025 年只公布为“少于 2.5 万台”，表中 25000 是上限，图中标作“<25”
    "upper_2025": ["德国"],
    "country": [("中国", "China", 295000, 354000), ("美国", "USA", 34200, 38500), ("日本", "Japan", 44500, 36219),
                ("韩国", "Rep. of Korea", 30600, 30000), ("德国", "Germany", 26982, 25000)],
}
# IFR WR 2025 服务机器人（2025-10-07 发布）：2024 年专业服务机器人销量（台）
IFR_SERVICE_2024 = [("运输与物流", "Transport & logistics", 102900), ("餐饮酒店", "Hospitality", 42000),
                    ("专业清洁", "Professional cleaning", 25000), ("农业", "Agriculture", 19500),
                    ("医疗", "Medical", 16700), ("搜救与安防", "Search & rescue, security", 3100)]


def glb_tree(eid: str) -> dict:
    """模型 default.glb 的节点树：{节点名: [子节点名…]}（网页三维显示用的就是它；关节表里没有的固定连接也在其中）。"""
    import struct
    b = (MODELS / eid / "default.glb").read_bytes()
    n = struct.unpack("<I", b[12:16])[0]
    js = json.loads(b[20:20 + n])
    return {nd.get("name"): [js["nodes"][c].get("name") for c in nd.get("children", [])] for nd in js["nodes"]}
