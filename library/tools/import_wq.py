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


def K(key, zh, en, unit="m"):
    return P(key, zh, en, unit)


LINK = [K("link_width_m", "杆宽", "Link width"), K("link_thickness_m", "杆厚", "Link thickness")]
MECHS = {
    "C-LNK-4BAR": {"name": {"zh": "曲柄摇杆机构（铰链四杆）", "en": "Crank-rocker four-bar linkage"}, "category": "LNK",
                   "engine": "four_bar", "tags": ["四杆机构", "曲柄摇杆", "连杆机构", "平面机构", "four-bar"],
                   "params": [K("crank_m", "曲柄长 a", "Crank a"), K("coupler_m", "连杆长 b", "Coupler b"),
                              K("rocker_m", "摇杆长 c", "Rocker c"), K("ground_m", "机架长 d", "Ground d")] + LINK,
                   "defaults": {"crank_m": 0.04, "coupler_m": 0.12, "rocker_m": 0.08, "ground_m": 0.10, "link_width_m": 0.012, "link_thickness_m": 0.006},
                   "ranges": {"crank_m": [0.02, 0.08], "coupler_m": [0.06, 0.2], "rocker_m": [0.04, 0.15], "ground_m": [0.06, 0.2]},
                   "principle": "四根杆用四个转动副连成封闭环：最短杆 + 最长杆 ≤ 另两杆之和（格拉霍夫条件）且最短杆是曲柄时，曲柄整周转动、摇杆往复摆动。连杆上的点画出各种连杆曲线，可用来实现给定轨迹。",
                   "uses": ["雨刷、缝纫机踏板", "颚式破碎机", "搅拌机、步行机构"], "chapter": "平面连杆机构"},
    "C-LNK-SLIDER": {"name": {"zh": "曲柄滑块机构", "en": "Slider-crank mechanism"}, "category": "LNK",
                     "engine": "slider_crank", "tags": ["曲柄滑块", "连杆机构", "活塞", "平面机构", "slider-crank"],
                     "params": [K("crank_m", "曲柄长 r", "Crank r"), K("rod_m", "连杆长 l", "Rod l"), K("offset_m", "偏距 e", "Offset e")] + LINK,
                     "defaults": {"crank_m": 0.04, "rod_m": 0.14, "offset_m": 0.0, "link_width_m": 0.012, "link_thickness_m": 0.006},
                     "ranges": {"crank_m": [0.02, 0.08], "rod_m": [0.08, 0.3], "offset_m": [0, 0.03]},
                     "principle": "曲柄整周转动，经连杆推动滑块沿导路往复移动（或反过来：活塞推动曲轴转动）。对心时滑块行程等于两倍曲柄长；有偏距时出现急回特性。",
                     "uses": ["内燃机、空压机", "冲床", "往复泵"], "chapter": "平面连杆机构"},
    "C-CAM-DISC": {"name": {"zh": "盘形凸轮机构（直动滚子从动件）", "en": "Disc cam with translating roller follower"}, "category": "CAM",
                   "engine": "cam", "tags": ["凸轮", "盘形凸轮", "从动件", "简谐运动", "cam"],
                   "params": [K("base_radius_m", "基圆半径 r0", "Base radius"), K("roller_radius_m", "滚子半径", "Roller radius"),
                              K("lift_m", "行程 h", "Lift h"), K("rise_deg", "推程角", "Rise angle", "deg"),
                              K("far_dwell_deg", "远休止角", "Far dwell", "deg"), K("return_deg", "回程角", "Return angle", "deg"),
                              K("thickness_m", "凸轮厚", "Cam thickness")],
                   "defaults": {"base_radius_m": 0.04, "roller_radius_m": 0.008, "lift_m": 0.02, "rise_deg": 120, "far_dwell_deg": 60,
                                "return_deg": 120, "thickness_m": 0.01},
                   "ranges": {"base_radius_m": [0.025, 0.08], "lift_m": [0.005, 0.04]},
                   "principle": "凸轮转一圈，轮廓推动从动件按规定的规律升起、停留、回落、停留。先定从动件运动规律（这里推程、回程都用余弦加速度规律），再按“反转法”求出凸轮轮廓：理论轮廓是滚子中心的轨迹，实际轮廓向内偏移一个滚子半径。",
                   "uses": ["内燃机配气机构", "自动机床送料", "纺织机械"], "chapter": "凸轮机构"},
    "C-GER-TRAIN": {"name": {"zh": "两级定轴齿轮系", "en": "Two-stage fixed-axis gear train"}, "category": "GER",
                    "engine": "gear_train", "tags": ["齿轮系", "定轴轮系", "传动比", "渐开线齿轮", "gear train"],
                    "params": [K("module1_mm", "第一级模数", "Module, stage 1", "mm"), K("z1", "齿数 z1", "z1", None), K("z2", "齿数 z2", "z2", None),
                               K("face1_mm", "第一级齿宽", "Face width 1", "mm"), K("module2_mm", "第二级模数", "Module, stage 2", "mm"),
                               K("z3", "齿数 z3", "z3", None), K("z4", "齿数 z4", "z4", None), K("face2_mm", "第二级齿宽", "Face width 2", "mm")],
                    "defaults": {"module1_mm": 2, "z1": 20, "z2": 40, "face1_mm": 12, "module2_mm": 2.5, "z3": 18, "z4": 54, "face2_mm": 16},
                    "ranges": {"z1": [12, 40], "z2": [20, 120], "z3": [12, 40], "z4": [20, 120]},
                    "principle": "两对外啮合直齿轮串联：总传动比等于各级从动轮齿数积除以主动轮齿数积，i = (z2·z4)/(z1·z3)；每经过一对外啮合转向反一次。齿形是渐开线，中心距 a = m(z1 + z2)/2。",
                    "uses": ["减速器", "机床主轴箱", "钟表"], "chapter": "齿轮系及其传动比"},
    "C-RED-WQR105": {"name": {"zh": "WQR-105 二级圆柱齿轮减速器（传动机构）", "en": "WQR-105 two-stage gear reducer (gear mechanism)"},
                     "category": "RED", "engine": "gear_train",
                     "tags": ["减速器", "WQR-105", "二级圆柱齿轮减速器", "问渠虚拟工厂", "gear reducer"],
                     "params": [K("module1_mm", "第一级模数", "Module, stage 1", "mm"), K("z1", "输入齿轮轴 SH-101 齿数", "z1 (SH-101)", None),
                                K("z2", "第一级大齿轮 GR-202 齿数", "z2 (GR-202)", None), K("face1_mm", "第一级齿宽", "Face width 1", "mm"),
                                K("module2_mm", "第二级模数", "Module, stage 2", "mm"), K("z3", "第二级小齿轮 GR-203 齿数", "z3 (GR-203)", None),
                                K("z4", "第二级大齿轮 GR-302 齿数", "z4 (GR-302)", None), K("face2_mm", "第二级齿宽", "Face width 2", "mm")],
                     "defaults": {"module1_mm": 2, "z1": 24, "z2": 72, "face1_mm": 30, "module2_mm": 3, "z3": 20, "z4": 70, "face2_mm": 40},
                     "ranges": {},
                     "names": {"ground": "箱座（轴承座示意）", "shaft1": "输入齿轮轴 SH-101（z = 24）",
                               "shaft2": "中间轴（GR-202 z = 72、GR-203 z = 20）", "shaft3": "输出轴（GR-302 z = 70）"},
                     "erp": ["WQR-105"],                       # 成品物料 ↔ 本机构（齿轮 SH-101、GR-202、GR-203、GR-302 写在构件名里）
                     "principle": "问渠虚拟工厂的产品：电机 1450 r/min 输入，第一级 24:72（i = 3），第二级 20:70（i = 3.5），总传动比 10.5，输出约 138 r/min。齿数、模数取自工厂主数据（factory/factory/data.py），与 ERPNext 物料、检验计划一致。",
                     "uses": ["课程设计（减速器设计）", "数字工厂虚拟产线的产品", "装配与检验实验"], "chapter": "减速器（课程设计）"},
    "C-WRM-WORM": {"name": {"zh": "蜗杆蜗轮机构", "en": "Worm and worm wheel"}, "category": "WRM",
                   "engine": "worm", "tags": ["蜗杆", "蜗轮", "交错轴", "自锁", "worm gear"],
                   "params": [K("module_mm", "模数", "Module", "mm"), K("worm_starts", "蜗杆头数 z1", "Worm starts", None),
                              K("wheel_teeth", "蜗轮齿数 z2", "Wheel teeth", None), K("diameter_factor", "直径系数 q", "Diameter factor q", None),
                              K("wheel_face_mm", "蜗轮齿宽", "Wheel face width", "mm")],
                   "defaults": {"module_mm": 2, "worm_starts": 1, "wheel_teeth": 30, "diameter_factor": 10, "wheel_face_mm": 14},
                   "ranges": {"worm_starts": [1, 4], "wheel_teeth": [20, 80]},
                   "principle": "蜗杆像一根螺杆，转一圈推动蜗轮转过 z1 个齿，单级就能得到很大的传动比 i = z2/z1，两轴在空间垂直交错。导程角很小时（tanγ = z1/q），蜗轮推不动蜗杆，具有自锁性。",
                   "uses": ["起重机、电梯曳引", "分度机构", "转台、阀门执行器"], "chapter": "蜗杆传动"},
    "C-BLT-BELT": {"name": {"zh": "开口带传动", "en": "Open belt drive"}, "category": "BLT",
                   "engine": "belt", "tags": ["带传动", "平带", "V 带", "包角", "belt drive"],
                   "params": [K("d1_m", "小带轮直径 D1", "Small pulley D1"), K("d2_m", "大带轮直径 D2", "Large pulley D2"),
                              K("center_m", "中心距 a", "Center distance a"), K("width_m", "带宽", "Belt width")],
                   "defaults": {"d1_m": 0.06, "d2_m": 0.12, "center_m": 0.25, "width_m": 0.02},
                   "ranges": {"d1_m": [0.03, 0.15], "d2_m": [0.05, 0.3], "center_m": [0.15, 0.6]},
                   "principle": "带套在两个带轮上，靠带与轮面的摩擦传递运动，传动比约为 D2/D1（有弹性滑动，略大）。小轮包角越大能传的力越大，一般要求不小于 120°；带长按两段切线加两段圆弧计算。",
                   "uses": ["电机到风机、水泵的传动", "机床主传动", "农机"], "chapter": "带传动"},
    "C-RAT-RATCHET": {"name": {"zh": "棘轮机构", "en": "Ratchet mechanism"}, "category": "RAT",
                      "engine": "ratchet", "tags": ["棘轮", "棘爪", "间歇运动", "止回", "ratchet"],
                      "params": [K("teeth", "棘轮齿数", "Teeth", None), K("wheel_radius_m", "棘轮半径", "Wheel radius"),
                                 K("swing_deg", "摇杆摆角", "Rocker swing", "deg"), K("thickness_m", "厚度", "Thickness")],
                      "defaults": {"teeth": 12, "wheel_radius_m": 0.05, "swing_deg": 40, "thickness_m": 0.008},
                      "ranges": {"teeth": [8, 36], "swing_deg": [20, 90]},
                      "principle": "摇杆往复摆动：推程时驱动棘爪推着棘轮转过一个齿（摆角大于一个齿距，多出的是空程），回程时棘爪在齿背上滑过，止回棘爪顶住棘轮不让倒转。把连续的往复摆动变成单向的间歇转动。",
                      "uses": ["牛头刨床进给", "千斤顶、扳手", "卷扬机止回"], "chapter": "间歇运动机构"},
    "C-GNV-GENEVA": {"name": {"zh": "外槽轮机构（日内瓦机构）", "en": "External Geneva mechanism"}, "category": "GNV",
                     "engine": "geneva", "tags": ["槽轮", "日内瓦机构", "间歇运动", "分度", "Geneva"],
                     "params": [K("slots", "槽数 n", "Slots", None), K("crank_m", "拨销回转半径 R", "Crank radius R"),
                                K("thickness_m", "厚度", "Thickness")],
                     "defaults": {"slots": 4, "crank_m": 0.05, "thickness_m": 0.008},
                     "ranges": {"slots": [3, 8]},
                     "principle": "拨盘匀速转动，拨销进入槽轮的径向槽时带着槽轮转过 360°/n，拨销离开后，拨盘上的锁止弧卡住槽轮让它停住。中心距 C = R / sin(π/n)，拨销进出槽时方向沿槽，没有刚性冲击；运动时间只占一圈的 (n − 2)/(2n)。",
                     "uses": ["转塔刀架、自动机床分度", "电影放映机输片", "包装机转盘"], "chapter": "间歇运动机构"},
    "C-SCN-LEAD": {"name": {"zh": "丝杠螺母机构（梯形螺纹）", "en": "Lead screw and nut (trapezoidal thread)"}, "category": "SCN",
                   "engine": "lead_screw", "tags": ["丝杠", "螺母", "螺旋传动", "梯形螺纹", "lead screw"],
                   "params": [K("diameter_mm", "公称直径 d", "Nominal diameter", "mm"), K("lead_mm", "导程 Ph", "Lead", "mm"),
                              K("screw_length_m", "丝杠长", "Screw length"), K("nut_length_m", "螺母长", "Nut length")],
                   "defaults": {"diameter_mm": 16, "lead_mm": 4, "screw_length_m": 0.3, "nut_length_m": 0.04},
                   "ranges": {"diameter_mm": [8, 40], "lead_mm": [1.5, 10]},
                   "principle": "丝杠转动、螺母（滑台）不转只沿导轨移动，丝杠每转一圈螺母移动一个导程：把旋转变成直线移动。梯形螺纹的导程角小于当量摩擦角时能自锁（推螺母转不动丝杠），所以常用于需要停住的升降、调节。",
                   "uses": ["机床手动进给、台钳", "升降台、千斤顶", "直线模组（与滚珠丝杠对比）"], "chapter": "螺旋传动"},
}


def mech_doc(eid, r):
    doc = robot_doc(eid, dict(r, type=None))
    doc["kind"] = "mechanism"
    doc.pop("robot", None)
    doc["model"] = {"engine": "wqmech:" + r["engine"], "formats": ["glb"],
                    "origin": "机构坐标系：平面机构在竖直 XZ 平面内（转角绕 −Y，从前方看逆时针为正），齿轮轴沿 Y；每个构件一个节点",
                    "note": "参数化自建模型；运动表 motion.csv 按默认参数采样（R5）"}
    doc["source"]["attribution"] = "问渠零件库（参数化生成器 generators/c_mech.py）"
    doc["source"]["checked"]["note"] = "自建；位置分析由测试核对（两种算法互核、闭环约束、传动比）"
    doc["teaching"]["courses"] = [{"course": "机械设计基础", "chapter": r["chapter"]}]
    if r.get("names"):
        doc["mechanism_names"] = r["names"]
    if r.get("erp"):
        doc["factory"]["erp_items"] = [{"item_code": c, "size": "default"} for c in r["erp"]]
    return doc


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
    for eid, r in MECHS.items():
        d = CATALOG / "C" / eid
        d.mkdir(parents=True, exist_ok=True)
        (d / "entry.yaml").write_text("# {} · {}（自建机构，第 5 轮第 6 步）\n".format(eid, r["name"]["zh"])
                                      + yaml.safe_dump(mech_doc(eid, r), allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(eid)
    for eid, r in ROBOTS.items():
        d = CATALOG / "B" / eid
        d.mkdir(parents=True, exist_ok=True)
        (d / "entry.yaml").write_text("# {} · {}（自建，第 5 轮第 6 步）\n".format(eid, r["name"]["zh"])
                                      + yaml.safe_dump(robot_doc(eid, r), allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(eid)


if __name__ == "__main__":
    main()
