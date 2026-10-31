"""第 30 章共用：机器人总体设计。以下划线开头，构建时不单独运行。

本章的主角仍是问渠机器人厂的 WQ-CR5（零件库 B-ARM-WQCR5）：几何、关节模组、质量都直接读机器人厂的原件
factory/digital/cae/wqcr5.py（第 58 轮），尺寸综合与模组选择用它的 design()（第 63 轮，与数字工厂“参数配置器”的协作臂模板同一段代码）。
选型案例的数据取自：减速器厂的物料清单与毛坯（factory/factory/data.py）、机器人厂的清单与价格（factory/plants/wenquest-robot.yaml）、
零件库各机械臂的厂商参数（library/catalog/B/*/vendor.yaml）。全部数值中，WQ-CR5 与两座工厂的数据是示例值。
"""
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BOOK = HERE.parents[1]
G0 = 9.81                                  # 𝔤，m/s²（符号约定第九节）


def wqcr5():
    """机器人厂的原件模块（与零件库、问渠 CAE、配置器同一份）"""
    p = str(ROOT / "factory" / "digital" / "cae")
    if p not in sys.path:
        sys.path.insert(0, p)
    import wqcr5 as W                    # noqa: E402
    return W


def motors():
    p = str(ROOT / "factory" / "digital" / "cae")
    if p not in sys.path:
        sys.path.insert(0, p)
    import motors as MT                  # noqa: E402
    return MT


# ---------------------------------------------------------------- 正运动学（标准 DH，第 13 章）
def dh_T(a, alpha, d, theta):
    c, s, ca, sa = math.cos(theta), math.sin(theta), math.cos(alpha), math.sin(alpha)
    return np.array([[c, -s * ca, s * sa, a * c], [s, c * ca, -c * sa, a * s], [0, sa, ca, d], [0, 0, 0, 1.0]])


def fk(q, dh, tool=0.0):
    """各关节坐标系原点与 TCP（法兰沿 z 再走 tool）"""
    T = np.eye(4)
    pts = [T[:3, 3].copy()]
    for qi, p in zip(q, dh):
        T = T @ dh_T(p["a"], p["alpha"], p["d"], qi)
        pts.append(T[:3, 3].copy())
    tcp = T @ np.array([0, 0, tool, 1.0])
    return T, pts, tcp[:3]


def cr_dh(a2=None, a3=None):
    W = wqcr5()
    dh = [dict(p) for p in W.DH]
    if a2 is not None:
        dh[1]["a"] = -a2
    if a3 is not None:
        dh[2]["a"] = -a3
    return dh


# ---------------------------------------------------------------- 工具朝下时够不够得着（30.3 节式 (30.3.1)～(30.3.3)）
TOOL = 0.15                                # 夹爪：TCP 距法兰 0.15 m（与第 5、22 章相同）


def wrist_points(r, z, dh, tool=TOOL):
    """工具竖直朝下、TCP 在离 J1 轴 r、高 z 处：关节 4 轴上那一点 P4 在手臂平面里的两种位置（手腕朝外 / 朝里），
    相对肩关节 J2 的水平、竖直距离。偏置腕：手臂平面离 TCP 偏 d4，所以平面内的距离是 √(r² − d4²)"""
    d1, d4, d5, d6 = dh[0]["d"], dh[3]["d"], dh[4]["d"], dh[5]["d"]
    if r < d4:
        return []
    rp = math.sqrt(r * r - d4 * d4)
    h = z + tool + d6 - d1
    return [(rp - d5, h), (rp + d5, h)]


def reach_margin(r, z, dh, tool=TOOL):
    """够得着的裕量：P4 到 J2 的距离 ρ 在 [|a2 − a3|, a2 + a3] 里时，返回离两端较近的那一端的相对裕量（> 0 才够得着）；
    两种手腕取好的那个"""
    a2, a3 = abs(dh[1]["a"]), abs(dh[2]["a"])
    best = -math.inf
    for x, y in wrist_points(r, z, dh, tool):
        rho = math.hypot(x, y)
        best = max(best, min((a2 + a3 - rho) / (a2 + a3), (rho - abs(a2 - a3)) / (a2 + a3)))
    return best


def ik_down(r, z, dh, tool=TOOL, outward=True, elbow_up=True):
    """工具朝下时的关节角（θ1 = 0，手臂伸向 −x）：平面两连杆求 θ2、θ3，θ4 使 θ2 + θ3 + θ4 = −90°，θ5 = ∓90°。供核对用"""
    a2, a3 = abs(dh[1]["a"]), abs(dh[2]["a"])
    pts = wrist_points(r, z, dh, tool)
    if not pts:
        return None
    x, y = pts[0] if outward else pts[1]
    rho2 = x * x + y * y
    c3 = (rho2 - a2 * a2 - a3 * a3) / (2 * a2 * a3)
    if abs(c3) > 1:
        return None
    s3 = math.sqrt(1 - c3 * c3) * (1 if elbow_up else -1)
    t3 = math.atan2(s3, c3)
    t2 = math.atan2(y, x) - math.atan2(a3 * s3, a2 + a3 * c3)
    if outward:
        return np.array([0.0, -t2, -t3, -math.pi / 2 + t2 + t3, -math.pi / 2, 0.0])
    return np.array([0.0, -t2, -t3, math.pi / 2 + t2 + t3, math.pi / 2, 0.0])


# ---------------------------------------------------------------- 减速器厂部件装配工位（30.1、30.4 节的案例；布置为示例）
# 机器人装在工作台上（底座在台面，z = 0），目标点：方位角 φ（度）、离 J1 轴 r（m）、高 z（m）；每个点还要能从上方 0.1 m 处接近
STATION = [
    ("轴料架（取轴）", "shaft rack", -90, 0.55, 0.20),
    ("轴承料盘", "bearing tray", -45, 0.45, 0.02),
    ("压装工装", "press fixture", 0, 0.50, 0.10),
    ("齿轮料架", "gear rack", 45, 0.60, 0.05),
    ("AGV 料箱（台面下）", "AGV tote (below the bench)", 90, 0.70, -0.30),
    ("检具", "gauge", 150, 0.35, 0.05),
]
APPROACH = 0.10


def station_points():
    """(名称, 英文名, r, z)：每个目标点和它上方的接近点"""
    out = []
    for zh, en, phi, r, z in STATION:
        out.append((zh, en, r, z))
        out.append((zh + "上方", en + " (approach)", r, z + APPROACH))
    return out


def factory_data():
    """factory/factory/data.py：减速器厂的物料清单（与工厂仿真同一份数据）"""
    p = str(ROOT / "factory")
    if p not in sys.path:
        sys.path.insert(0, p)
    from factory import data            # noqa: E402
    return data


RHO_STEEL = 7850.0


def station_parts():
    """部件装配工位要搬的零件与毛坯质量（上限：成品比毛坯轻）。棒料按物料清单的耗料 kg；锻坯按尺寸 Ø×厚算"""
    F = factory_data()
    out = []
    for item in ("SH-101", "SH-201", "SH-301", "GR-202", "GR-203", "GR-302"):
        rm, q = F.BOMS[item][1][0]
        if F.ITEMS[rm][2] == "Kg":
            m = float(q)
        else:                                            # 锻坯：名称里有 Ø×厚
            import re
            dia, th = map(float, re.search(r"Ø(\d+)×(\d+)", F.ITEMS[rm][0]).groups())
            m = RHO_STEEL * math.pi * (dia / 2000) ** 2 * th / 1000
        out.append({"item": item, "name": F.ITEMS[item][0], "blank": rm, "blank_kg": m})
    return out


GRIPPER_KG = 1.0                           # 夹爪（与第 5 章算例相同的假设）


# ---------------------------------------------------------------- 零件库：机械臂的厂商参数
def library_arms():
    """零件库 B 部分各机械臂的厂商参数（vendor.yaml 的 datasheet.values），加上 WQ-CR5 自己的数"""
    import yaml
    out = []
    for f in sorted((ROOT / "library" / "catalog" / "B").glob("B-ARM-*/vendor.yaml")):
        v = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        d = (v.get("datasheet") or {}).get("values") or {}
        out.append({"id": f.parent.name, "vendor": ((v.get("vendor") or {}).get("name") or {}).get("zh", ""),
                    "model": (v.get("datasheet") or {}).get("model", ""), **{k: d.get(k) for k in
                    ("payload_kg", "reach_mm", "dof", "repeatability_mm", "weight_kg")}})
    W = wqcr5()
    s = W.summary()
    out.append({"id": "B-ARM-WQCR5", "vendor": "问渠机器人厂", "model": "WQ-CR5", "payload_kg": s["payload_kg"], "reach_mm": s["reach_mm"],
                "dof": 6, "repeatability_mm": 0.03, "weight_kg": s["mass_kg"]})
    return out


# 协作机器人（可与人同场工作，功率与力限制）：按厂商的产品定位
COBOTS = {"B-ARM-WQCR5", "B-ARM-UR5E", "B-ARM-UR10E", "B-ARM-GOFA", "B-ARM-HC10", "B-ARM-CRX10IAL", "B-ARM-CR7IA",
          "B-ARM-FR3", "B-ARM-PANDA", "B-ARM-IIWA14", "B-ARM-GEN3", "B-ARM-Z1"}


# ---------------------------------------------------------------- 机器人厂：清单、价格、工艺路线
def robot_plant():
    import yaml
    return yaml.safe_load((ROOT / "factory" / "plants" / "wenquest-robot.yaml").read_text(encoding="utf-8"))


def bom_rollup(item):
    """按清单把一台 item 的材料与外购件费用逐层加起来（只算材料，不含工时），返回 {直接下级: 金额}、合计"""
    P = robot_plant()
    price = {it["code"]: it.get("price") for it in P["items"]}
    boms = {b["item"]: b["components"] for b in P["boms"]}

    def cost(code):
        if code in boms:
            return sum(q * cost(c) for c, q in boms[code])
        return float(price.get(code) or 0.0)
    parts = {c: q * cost(c) for c, q in boms[item]}
    return parts, sum(parts.values())


# ---------------------------------------------------------------- 节拍：梯形速度的点到点运动
def move_time(dist, vmax, amax):
    """走 dist（rad 或 m）：先以 amax 加速到 vmax、匀速、再减速；距离短时只加速、减速（三角形）"""
    if dist <= vmax * vmax / amax:
        return 2 * math.sqrt(dist / amax)
    return dist / vmax + vmax / amax
