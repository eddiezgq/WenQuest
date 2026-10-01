# -*- coding: utf-8 -*-
"""问渠自建机器人与机构的条目（第 5 轮第 6 步，P9）：参数、默认值、范围、教学说明 → catalog/<部分>/<编号>/entry.yaml。
SCARA、Delta、差速小车（第 5 轮 P12）的条目是手写的，不在这里。
用法：python3 tools/import_wq.py
"""
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from wqlib import CATALOG  # noqa: E402

ON = "2026-10-01"


def P(key, zh, en, unit="m"):
    return {"key": key, "zh": zh, "en": en, "role": "key", **({"unit": unit} if unit else {})}


ROBOTS = {
    "B-CRT-WQ3": {
        "name": {"zh": "直角坐标机器人（龙门，问渠）", "en": "Cartesian gantry robot (WenQuest)"}, "category": "CRT",
        "tags": ["直角坐标机器人", "龙门", "桁架机器人", "笛卡尔", "自建", "cartesian", "gantry"],
        "engine": "cartesian", "type": "cartesian",
        "params": [P("stroke_x_m", "X 行程", "X stroke"), P("stroke_y_m", "Y 行程", "Y stroke"), P("stroke_z_m", "Z 行程", "Z stroke"),
                   P("frame_height_m", "立柱高", "Frame height"), P("beam_m", "梁截面边长", "Beam section")],
        "defaults": {"stroke_x_m": 0.6, "stroke_y_m": 0.4, "stroke_z_m": 0.25, "frame_height_m": 0.5, "beam_m": 0.04},
        "ranges": {"stroke_x_m": [0.2, 2.0], "stroke_y_m": [0.2, 1.5], "stroke_z_m": [0.1, 0.6]},
        "principle": "三个互相垂直的移动关节，每个关节只管一个坐标方向：关节值直接就是末端的 x、y、z，运动学最简单，刚度好、精度高，但占地大。",
        "uses": ["码垛与上下料（桁架机械手）", "3D 打印机、数控雕刻", "点胶、检测"], "chapter": "直角坐标机器人与运动学入门"},
    "B-EDU-2R": {
        "name": {"zh": "两连杆平面臂（问渠）", "en": "Two-link planar arm (WenQuest)"}, "category": "EDU",
        "tags": ["两连杆", "平面机械臂", "2R", "运动学", "教学模型", "自建", "planar arm"],
        "engine": "planar_2r", "type": "planar_2r",
        "params": [P("link1_m", "连杆 1 长", "Link 1 length"), P("link2_m", "连杆 2 长", "Link 2 length"),
                   P("base_height_m", "底座高", "Base height"), P("link_radius_m", "连杆截面（半）", "Link half-width")],
        "defaults": {"link1_m": 0.3, "link2_m": 0.25, "base_height_m": 0.12, "link_radius_m": 0.018},
        "ranges": {"link1_m": [0.1, 0.6], "link2_m": [0.1, 0.6]},
        "principle": "竖直平面内两个转动关节串联：末端位置由两个关节角唯一确定（正运动学），反过来给定末端位置一般有“肘上”“肘下”两组关节角（逆运动学），是学习运动学、雅可比和奇异位形的最小例子。",
        "uses": ["正逆运动学入门", "雅可比与奇异位形", "轨迹规划与 PID 控制实验"], "chapter": "平面机械臂运动学"},
    "B-EDU-CARTPOLE": {
        "name": {"zh": "倒立摆小车（问渠）", "en": "Cart-pole inverted pendulum (WenQuest)"}, "category": "EDU",
        "tags": ["倒立摆", "小车倒立摆", "控制", "LQR", "教学模型", "自建", "cart-pole"],
        "engine": "cart_pole", "type": "cart_pole",
        "params": [P("rail_length_m", "导轨长", "Rail length"), P("pole_length_m", "摆杆长", "Pole length"),
                   P("rail_height_m", "导轨高", "Rail height"), P("cart_mass_kg", "小车质量", "Cart mass", "kg"),
                   P("pole_mass_kg", "摆杆质量", "Pole mass", "kg")],
        "defaults": {"rail_length_m": 1.0, "pole_length_m": 0.5, "rail_height_m": 0.08, "cart_mass_kg": 1.0, "pole_mass_kg": 0.1},
        "ranges": {"pole_length_m": [0.2, 1.0], "cart_mass_kg": [0.3, 5.0], "pole_mass_kg": [0.05, 1.0]},
        "principle": "小车只能沿导轨左右移动，摆杆靠铰链立在小车上，竖直向上是不稳定平衡：摆杆一倒，就要把小车往同一侧推。条目给出非线性方程和在竖直位置的线性化模型（A、B 矩阵），可直接做极点配置、LQR 等控制实验。",
        "uses": ["状态反馈与 LQR 控制", "PID 与模糊控制对比", "强化学习的经典环境"], "chapter": "欠驱动系统与倒立摆控制"},
    "B-PAR-STEWART": {
        "name": {"zh": "Stewart 六自由度平台（问渠）", "en": "Stewart platform (WenQuest)"}, "category": "PAR",
        "tags": ["Stewart", "六自由度平台", "并联机器人", "运动模拟", "自建", "hexapod"],
        "engine": "stewart", "type": "stewart",
        "params": [P("base_radius_m", "基座铰点圆半径", "Base joint radius"), P("platform_radius_m", "平台铰点圆半径", "Platform joint radius"),
                   P("base_half_angle_deg", "基座每组两点半夹角", "Base pair half-angle", "deg"),
                   P("platform_half_angle_deg", "平台每组两点半夹角", "Platform pair half-angle", "deg"),
                   P("home_height_m", "原位高度", "Home height"), P("leg_stroke_m", "腿伸缩行程", "Leg stroke"),
                   P("demo_amplitude_m", "演示运动幅度", "Demo amplitude"), P("demo_tilt_deg", "演示倾角", "Demo tilt", "deg")],
        "defaults": {"base_radius_m": 0.25, "platform_radius_m": 0.15, "base_half_angle_deg": 12, "platform_half_angle_deg": 12,
                     "home_height_m": 0.32, "leg_stroke_m": 0.12, "demo_amplitude_m": 0.03, "demo_tilt_deg": 6},
        "ranges": {"home_height_m": [0.2, 0.6], "leg_stroke_m": [0.05, 0.3]},
        "principle": "六根可伸缩的腿把动平台连到基座，改变六根腿的长度就能让平台在空间里平移和转动（六个自由度）。由平台位姿求腿长（逆解）只要算两点距离，由腿长求位姿（正解）要解非线性方程组——和串联机械臂正好相反。",
        "uses": ["飞行与驾驶模拟器", "精密定位与对接", "振动台"], "chapter": "并联机器人运动学"},
}


def robot_doc(eid, r):
    return {
        "schema": 1, "id": eid, "kind": "robot", "name": r["name"], "category": r["category"], "tags": r["tags"],
        "standards": [], "params": r["params"], "defaults": r["defaults"], "ranges": r["ranges"],
        "model": {"engine": "wqrobot:" + r["engine"], "formats": ["glb", "urdf"],
                  "origin": "基座坐标系（Z 向上）；每个连杆（构件）一个节点", "note": "参数化自建模型：改参数可重新生成"},
        "robot": {"type": r["type"]},
        "source": {"origin": "wenquest", "license": "Apache-2.0", "attribution": "问渠零件库（参数化生成器 generators/b_wq.py）",
                   "checked": {"by": "Claude", "on": ON, "note": "自建；运动学（与动力学）由测试核对"}},
        "teaching": {"principle": r["principle"], "uses": r["uses"], "courses": [{"course": "机器人技术", "chapter": r["chapter"]}], "labs": []},
        "factory": {"erp_items": [], "suppliers": []},
    }


def main():
    for eid, r in ROBOTS.items():
        d = CATALOG / "B" / eid
        d.mkdir(parents=True, exist_ok=True)
        (d / "entry.yaml").write_text("# {} · {}（自建，第 5 轮第 6 步）\n".format(eid, r["name"]["zh"])
                                      + yaml.safe_dump(robot_doc(eid, r), allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(eid)


if __name__ == "__main__":
    main()
