"""问渠零件与机器人库 · 临时样例（第 4 轮）.

The real library is built by the digital factory (factory round 2: `library/`, published to Releases and Spaces).
Until it is online, the learning platform develops against this small stand-in with the SAME layout
(docs/方案/数字工厂资源接口约定.md):

    <root>/library/latest.json                     {"version", "index"}
    <root>/library/<version>/index.json            one row per spec
    <root>/library/<version>/<id>/entry.json       entry.yaml as JSON + joints (R2, R4, R5)
    <root>/library/<version>/<id>/<spec>.glb       one node per link, node name = link name (R4)
    <root>/library/<version>/<id>/<spec>.svg       2-D drawing / kinematic sketch (R3)
    <root>/library/<version>/<id>/motion.csv       mechanisms: input angle -> joint values (R5)

Everything here is our own simple geometry (license Apache-2.0); ids use the `-S` suffix ("sample") so they never
collide with the real library's entries. Kinematics are Z-up in metres; the glTF has one root node `zup` that turns
Z-up into glTF's Y-up, below it the link tree.
"""
from __future__ import annotations

import csv
import io
import json
import math
from pathlib import Path

import numpy as np

VERSION = "sample-2026.09.30b"
LICENSE = "Apache-2.0"
ATTRIB = "问渠零件与机器人库 · 临时样例（自建简化几何，正式库上线后替换）"
STEEL, BLUE, ORANGE, DARK, GREY, YELLOW = "#9aa7b0", "#3b82c4", "#e8913a", "#2b3238", "#c9d1d6", "#f2c14e"


# --- small kinematics ------------------------------------------------------------------------------------------------

def rpy_matrix(r: float, p: float, y: float) -> np.ndarray:
    cr, sr, cp, sp, cy, sy = math.cos(r), math.sin(r), math.cos(p), math.sin(p), math.cos(y), math.sin(y)
    return np.array([[cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
                     [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
                     [-sp, cp * sr, cp * cr]])


def tf(xyz=(0, 0, 0), rpy=(0, 0, 0)) -> np.ndarray:
    t = np.eye(4)
    t[:3, :3] = rpy_matrix(*rpy)
    t[:3, 3] = xyz
    return t


def axis_angle(axis, q: float) -> np.ndarray:
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    k = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    t = np.eye(4)
    t[:3, :3] = np.eye(3) + math.sin(q) * k + (1 - math.cos(q)) * k @ k
    return t


def joint_motion(j: dict, q: float) -> np.ndarray:
    if j["type"] == "prismatic":
        t = np.eye(4)
        t[:3, 3] = np.asarray(j["axis"], float) * q
        return t
    return axis_angle(j["axis"], q)


def fk(robot: dict, q: dict[str, float] | None = None) -> dict[str, np.ndarray]:
    """World pose of every link (joint values by joint name; missing = 0)."""
    q = q or {}
    poses = {robot["root"]: np.eye(4)}
    todo = list(robot["joints"])
    while todo:
        for j in list(todo):
            if j["parent"] in poses:
                poses[j["child"]] = poses[j["parent"]] @ tf(j["xyz"], j["rpy"]) @ joint_motion(j, q.get(j["name"], 0.0))
                todo.remove(j)
    return poses


def J(name, parent, child, xyz, axis, kind="revolute", lower=-math.pi, upper=math.pi, rpy=(0, 0, 0)):
    return {"name": name, "type": kind, "parent": parent, "child": child, "xyz": list(xyz), "rpy": list(rpy),
            "axis": list(axis), "lower": lower, "upper": upper}


# shapes: ("box", extents, xyz, color) | ("cyl", radius, height, axis, xyz, color) | ("sph", radius, xyz, color)
#         | ("ring", r_in, r_out, height, axis, xyz, color)

def cyl_between(a, b, r, color):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return ("seg", r, list(a), list(b), color)


# --- the sample robots, parts and mechanisms ------------------------------------------------------------------------

def arm6() -> dict:
    """六轴机械臂（教学样例）: proportions of a common 5 kg collaborative arm (d1 0.1625, a2 0.425, a3 0.392 m)."""
    L = {
        "base": [("cyl", 0.075, 0.09, "z", (0, 0, 0.045), DARK)],
        "shoulder": [("cyl", 0.062, 0.14, "z", (0, 0, 0), BLUE), ("cyl", 0.062, 0.13, "y", (0, 0.07, 0), BLUE)],
        "upper_arm": [cyl_between((0, 0, 0), (0.425, 0, 0), 0.05, GREY), ("cyl", 0.058, 0.12, "y", (0, 0, 0), BLUE),
                      ("cyl", 0.055, 0.11, "y", (0.425, 0, 0), BLUE)],
        "forearm": [cyl_between((0, 0, 0), (0.392, 0, 0), 0.04, GREY)],
        "wrist1": [("cyl", 0.045, 0.1, "y", (0, 0, 0), BLUE)],
        "wrist2": [("cyl", 0.045, 0.1, "z", (0, 0, 0), BLUE)],
        "wrist3": [("cyl", 0.045, 0.06, "y", (0, 0, 0), BLUE), ("cyl", 0.032, 0.02, "y", (0, 0.04, 0), DARK)],
    }
    joints = [
        J("shoulder_pan", "base", "shoulder", (0, 0, 0.1625), (0, 0, 1)),
        J("shoulder_lift", "shoulder", "upper_arm", (0, 0.138, 0), (0, 1, 0)),
        J("elbow", "upper_arm", "forearm", (0.425, -0.131, 0), (0, 1, 0), lower=-2.8, upper=2.8),
        J("wrist_1", "forearm", "wrist1", (0.392, 0.127, 0), (0, 1, 0)),
        J("wrist_2", "wrist1", "wrist2", (0, 0.0, -0.1), (0, 0, 1)),
        J("wrist_3", "wrist2", "wrist3", (0, 0.0, -0.1), (0, 1, 0)),
    ]
    return {"id": "B-ARM-6R-S", "kind": "robot", "category": "ARM", "root": "base", "links": L, "joints": joints,
            "name": {"zh": "六轴协作机械臂（教学样例）", "en": "6-axis collaborative arm (teaching sample)"},
            "tags": ["机械臂", "六轴", "协作机器人", "串联", "6R", "cobot"], "view": "xz",
            "robot": {"type": "arm", "dof": 6, "payload_kg": 5, "reach_mm": 850,
                      "kinematics": "UR 类构型：d1=0.1625 m，a2=0.425 m，a3=0.392 m，腕部三轴"},
            "tool": ["wrist3", (0, 0.05, 0)],
            "rest": {"shoulder_lift": -1.2, "elbow": 1.5, "wrist_1": -1.9, "wrist_2": 0.0},
            "demo": {"shoulder_pan": [0, 1.2], "shoulder_lift": [-1.2, -0.6], "elbow": [1.5, 0.9], "wrist_1": [-1.9, -1.2],
                     "wrist_2": [0, 1.0], "wrist_3": [0, 1.5]},
            "teaching": {"principle": "六个转动关节串联：前三个关节决定末端位置，腕部三个关节决定末端姿态。",
                         "uses": ["装配", "上下料", "人机协作"],
                         "courses": [{"course": "现代机器人学", "chapter": "正运动学"}, {"course": "现代机器人学", "chapter": "逆运动学"}],
                         "labs": ["拖动关节看末端轨迹", "正逆运动学"]}}


def scara() -> dict:
    L = {"base": [("cyl", 0.09, 0.35, "z", (0, 0, 0.175), DARK)],
         "arm1": [cyl_between((0, 0, 0), (0.35, 0, 0), 0.045, GREY), ("cyl", 0.06, 0.08, "z", (0, 0, 0), BLUE)],
         "arm2": [cyl_between((0, 0, 0), (0.3, 0, 0), 0.04, GREY), ("cyl", 0.055, 0.07, "z", (0, 0, 0), BLUE),
                  ("cyl", 0.045, 0.1, "z", (0.3, 0, 0), BLUE)],
         "quill": [("cyl", 0.015, 0.3, "z", (0, 0, -0.1), STEEL)],
         "tool": [("cyl", 0.03, 0.03, "z", (0, 0, -0.26), ORANGE)]}
    joints = [J("j1", "base", "arm1", (0, 0, 0.39), (0, 0, 1), lower=-2.5, upper=2.5),
              J("j2", "arm1", "arm2", (0.35, 0, 0.06), (0, 0, 1), lower=-2.5, upper=2.5),
              J("j3", "arm2", "quill", (0.3, 0, 0), (0, 0, -1), "prismatic", 0.0, 0.15),
              J("j4", "quill", "tool", (0, 0, 0), (0, 0, 1))]
    return {"id": "B-SCA-4-S", "kind": "robot", "category": "SCA", "root": "base", "links": L, "joints": joints,
            "name": {"zh": "SCARA 平面关节机器人（教学样例）", "en": "SCARA robot (teaching sample)"},
            "tags": ["SCARA", "平面关节", "装配", "四轴"], "view": "xz",
            "robot": {"type": "scara", "dof": 4, "payload_kg": 3, "reach_mm": 650, "kinematics": "两个水平转动 + 竖直移动 + 末端转动"},
            "tool": ["tool", (0, 0, -0.28)],
            "demo": {"j1": [0, 1.2], "j2": [0, -1.4], "j3": [0, 0.12], "j4": [0, 3.0]},
            "teaching": {"principle": "两个竖直轴的转动关节在水平面内定位，竖直移动关节负责升降，适合平面内的快速取放。",
                         "uses": ["电子装配", "分拣"], "courses": [{"course": "现代机器人学", "chapter": "机器人分类与构型"}],
                         "labs": ["工作空间"]}}


def gantry() -> dict:
    L = {"frame": [("box", (1.2, 0.05, 0.05), (0.6, -0.4, 0.8), GREY), ("box", (1.2, 0.05, 0.05), (0.6, 0.4, 0.8), GREY),
                   ("box", (0.05, 0.05, 0.8), (0, -0.4, 0.4), DARK), ("box", (0.05, 0.05, 0.8), (0, 0.4, 0.4), DARK),
                   ("box", (0.05, 0.05, 0.8), (1.2, -0.4, 0.4), DARK), ("box", (0.05, 0.05, 0.8), (1.2, 0.4, 0.4), DARK)],
         "x_carriage": [("box", (0.08, 0.86, 0.06), (0, 0, 0), BLUE)],
         "y_carriage": [("box", (0.12, 0.1, 0.1), (0, 0, 0), ORANGE)],
         "z_ram": [("box", (0.04, 0.04, 0.45), (0, 0, -0.2), STEEL), ("cyl", 0.03, 0.04, "z", (0, 0, -0.44), DARK)]}
    joints = [J("x", "frame", "x_carriage", (0.1, 0, 0.84), (1, 0, 0), "prismatic", 0, 1.0),
              J("y", "x_carriage", "y_carriage", (0, -0.35, 0), (0, 1, 0), "prismatic", 0, 0.7),
              J("z", "y_carriage", "z_ram", (0, 0, 0), (0, 0, -1), "prismatic", 0, 0.3)]
    return {"id": "B-CRT-3-S", "kind": "robot", "category": "CRT", "root": "frame", "links": L, "joints": joints,
            "name": {"zh": "直角坐标（龙门）机器人（教学样例）", "en": "Cartesian gantry robot (teaching sample)"},
            "tags": ["直角坐标", "龙门", "三轴", "移动关节"], "view": "xz",
            "robot": {"type": "cartesian", "dof": 3, "payload_kg": 10, "reach_mm": 1000, "kinematics": "三个互相垂直的移动关节"},
            "tool": ["z_ram", (0, 0, -0.46)],
            "demo": {"x": [0, 0.8], "y": [0, 0.6], "z": [0, 0.25]},
            "teaching": {"principle": "三个互相垂直的移动关节分别对应 x、y、z，关节量就是末端坐标，运动学最简单。",
                         "uses": ["搬运", "3D 打印", "数控加工"], "courses": [{"course": "现代机器人学", "chapter": "机器人分类与构型"}],
                         "labs": ["关节空间与任务空间"]}}


def mobile() -> dict:
    L = {"chassis": [("cyl", 0.17, 0.08, "z", (0, 0, 0.09), BLUE), ("box", (0.06, 0.12, 0.03), (0.13, 0, 0.14), YELLOW),
                     ("sph", 0.025, (-0.13, 0, 0.025), DARK), ("cyl", 0.04, 0.05, "z", (0.05, 0, 0.155), DARK)],
         "wheel_left": [("cyl", 0.05, 0.025, "y", (0, 0, 0), DARK)],
         "wheel_right": [("cyl", 0.05, 0.025, "y", (0, 0, 0), DARK)]}
    joints = [J("wheel_left", "chassis", "wheel_left", (0, 0.16, 0.05), (0, 1, 0), "continuous"),
              J("wheel_right", "chassis", "wheel_right", (0, -0.16, 0.05), (0, 1, 0), "continuous")]
    return {"id": "B-MOB-DIFF-S", "kind": "robot", "category": "MOB", "root": "chassis", "links": L, "joints": joints,
            "name": {"zh": "差速移动机器人（教学样例）", "en": "Differential-drive mobile robot (teaching sample)"},
            "tags": ["移动机器人", "差速", "轮式", "AGV", "激光雷达"], "view": "xy",
            "robot": {"type": "mobile", "dof": 2, "payload_kg": 5, "reach_mm": 0,
                      "kinematics": "轮距 0.32 m，轮半径 0.05 m；v=(r/2)(ωr+ωl)，ω=(r/L)(ωr−ωl)"},
            "demo": {"wheel_left": [0, 12.0], "wheel_right": [0, 12.0]},
            "teaching": {"principle": "左右两轮转速相同则直行，不同则转弯；机器人不能横着走（非完整约束）。",
                         "uses": ["仓储 AGV", "服务机器人", "巡检"],
                         "courses": [{"course": "现代机器人学", "chapter": "轮式移动机器人"}], "labs": ["差速运动学", "路径跟踪"]}}


def quadruped() -> dict:
    L = {"trunk": [("box", (0.5, 0.22, 0.12), (0, 0, 0), BLUE), ("box", (0.08, 0.14, 0.06), (0.27, 0, 0.02), DARK)]}
    joints = []
    for leg, (x, y) in {"fl": (0.2, 0.11), "fr": (0.2, -0.11), "hl": (-0.2, 0.11), "hr": (-0.2, -0.11)}.items():
        L[f"{leg}_hip"] = [("cyl", 0.04, 0.06, "x", (0, 0, 0), DARK)]
        L[f"{leg}_thigh"] = [cyl_between((0, 0, 0), (0, 0, -0.2), 0.025, GREY), ("cyl", 0.035, 0.05, "y", (0, 0, 0), DARK)]
        L[f"{leg}_calf"] = [cyl_between((0, 0, 0), (0, 0, -0.2), 0.018, STEEL), ("sph", 0.025, (0, 0, -0.2), DARK)]
        side = 1 if y > 0 else -1
        joints += [J(f"{leg}_hip_abd", "trunk", f"{leg}_hip", (x, y, -0.02), (1, 0, 0), lower=-0.8, upper=0.8),
                   J(f"{leg}_hip_flex", f"{leg}_hip", f"{leg}_thigh", (0, side * 0.06, 0), (0, 1, 0), lower=-1.5, upper=1.5),
                   J(f"{leg}_knee", f"{leg}_thigh", f"{leg}_calf", (0, 0, -0.2), (0, 1, 0), lower=-2.6, upper=-0.3)]
    demo = {}
    for leg in ("fl", "fr", "hl", "hr"):
        demo[f"{leg}_hip_flex"] = [0.6, 0.9]
        demo[f"{leg}_knee"] = [-1.2, -1.6]
    return {"id": "B-LEG-4-S", "kind": "robot", "category": "LEG", "root": "trunk", "links": L, "joints": joints,
            "name": {"zh": "四足机器人（教学样例）", "en": "Quadruped robot (teaching sample)"},
            "tags": ["四足", "足式", "机器狗", "12 自由度"], "view": "xz",
            "robot": {"type": "quadruped", "dof": 12, "payload_kg": 5, "reach_mm": 0, "kinematics": "每条腿 3 个关节：髋侧摆、髋前摆、膝"},
            "rest": {f"{leg}_{j}": v for leg in ("fl", "fr", "hl", "hr") for j, v in (("hip_flex", 0.6), ("knee", -1.2))},
            "demo": demo,
            "teaching": {"principle": "每条腿是一条三自由度的串联链，四条腿交替支撑和摆动来行走。",
                         "uses": ["巡检", "救援", "野外运输"],
                         "courses": [{"course": "现代机器人学", "chapter": "机器人分类与构型"}], "labs": ["单腿运动学"]}}


def humanoid() -> dict:
    L = {"pelvis": [("box", (0.16, 0.26, 0.1), (0, 0, 0), DARK)],
         "torso": [("box", (0.18, 0.34, 0.36), (0, 0, 0.2), BLUE), ("sph", 0.09, (0, 0, 0.48), GREY),
                   ("box", (0.02, 0.12, 0.04), (0.085, 0, 0.49), DARK)]}
    joints = [J("waist", "pelvis", "torso", (0, 0, 0.06), (0, 0, 1), lower=-1.0, upper=1.0)]
    for side, s in (("l", 1), ("r", -1)):
        L[f"{side}_upper_arm"] = [("sph", 0.045, (0, 0, 0), DARK), cyl_between((0, 0, 0), (0, 0, -0.26), 0.035, GREY)]
        L[f"{side}_forearm"] = [cyl_between((0, 0, 0), (0, 0, -0.24), 0.03, STEEL), ("sph", 0.04, (0, 0, -0.26), DARK)]
        L[f"{side}_thigh"] = [("sph", 0.05, (0, 0, 0), DARK), cyl_between((0, 0, 0), (0, 0, -0.38), 0.05, GREY)]
        L[f"{side}_shin"] = [cyl_between((0, 0, 0), (0, 0, -0.38), 0.042, STEEL)]
        L[f"{side}_foot"] = [("box", (0.2, 0.09, 0.04), (0.04, 0, -0.02), DARK)]
        joints += [J(f"{side}_shoulder_pitch", "torso", f"{side}_upper_arm", (0, s * 0.22, 0.34), (0, 1, 0))]
        joints += [J(f"{side}_elbow", f"{side}_upper_arm", f"{side}_forearm", (0, 0, -0.26), (0, 1, 0), lower=-2.4, upper=0),
                   J(f"{side}_hip_pitch", "pelvis", f"{side}_thigh", (0, s * 0.09, -0.06), (0, 1, 0), lower=-1.6, upper=1.0),
                   J(f"{side}_knee", f"{side}_thigh", f"{side}_shin", (0, 0, -0.38), (0, 1, 0), lower=0, upper=2.2),
                   J(f"{side}_ankle", f"{side}_shin", f"{side}_foot", (0, 0, -0.38), (0, 1, 0), lower=-0.8, upper=0.8)]
    return {"id": "B-HUM-S", "kind": "robot", "category": "HUM", "root": "pelvis", "links": L, "joints": joints,
            "name": {"zh": "人形机器人（教学样例）", "en": "Humanoid robot (teaching sample)"},
            "tags": ["人形", "双足", "仿人"], "view": "xz",
            "robot": {"type": "humanoid", "dof": len(joints), "payload_kg": 3, "reach_mm": 0, "kinematics": "腰 1 + 每臂 2 + 每腿 3（简化）"},
            "demo": {"l_shoulder_pitch": [0, -1.2], "r_shoulder_pitch": [0, 0.6], "l_elbow": [0, -1.2], "r_elbow": [0, -0.6],
                     "l_hip_pitch": [0, -0.5], "l_knee": [0, 0.9], "l_ankle": [0, -0.4], "waist": [0, 0.3]},
            "teaching": {"principle": "多条串联链（腿、臂）挂在躯干上，靠控制重心和足底接触保持平衡。",
                         "uses": ["服务", "研究", "人机共处环境"], "courses": [{"course": "现代机器人学", "chapter": "机器人分类与构型"}],
                         "labs": ["平衡与重心"]}}


def drone() -> dict:
    L = {"body": [("box", (0.16, 0.16, 0.05), (0, 0, 0), DARK), ("box", (0.5, 0.03, 0.02), (0, 0, 0), GREY, 45),
                  ("box", (0.5, 0.03, 0.02), (0, 0, 0), GREY, -45)]}
    joints = []
    for i, (x, y) in enumerate(((0.177, 0.177), (-0.177, 0.177), (-0.177, -0.177), (0.177, -0.177))):
        L[f"prop{i + 1}"] = [("box", (0.2, 0.02, 0.004), (0, 0, 0), ORANGE if i < 2 else BLUE), ("cyl", 0.012, 0.02, "z", (0, 0, -0.01), DARK)]
        joints.append(J(f"prop{i + 1}", "body", f"prop{i + 1}", (x, y, 0.03), (0, 0, 1 if i % 2 == 0 else -1), "continuous"))
    return {"id": "B-UAV-QUAD-S", "kind": "robot", "category": "UAV", "root": "body", "links": L, "joints": joints,
            "name": {"zh": "四旋翼无人机（教学样例）", "en": "Quadrotor drone (teaching sample)"},
            "tags": ["无人机", "四旋翼", "飞行机器人"], "view": "xy",
            "robot": {"type": "uav", "dof": 6, "payload_kg": 0.5, "reach_mm": 0, "kinematics": "四个旋翼，相邻两个转向相反，靠转速差控制姿态"},
            "demo": {f"prop{i}": [0, 40.0] for i in range(1, 5)},
            "teaching": {"principle": "四个旋翼转速的组合产生升力和三个方向的力矩，改变转速就能控制姿态和飞行方向。",
                         "uses": ["航拍", "巡检", "物流"], "courses": [{"course": "现代机器人学", "chapter": "机器人分类与构型"}],
                         "labs": ["推力与姿态"]}}


def four_bar(a=0.04, b=0.12, c=0.09, d=0.11) -> dict:
    L = {"ground": [("box", (d + 0.04, 0.02, 0.01), (d / 2, 0, -0.012), GREY), ("cyl", 0.008, 0.02, "z", (0, 0, 0), DARK),
                    ("cyl", 0.008, 0.02, "z", (d, 0, 0), DARK)],
         "crank": [cyl_between((0, 0, 0), (a, 0, 0), 0.005, ORANGE)],
         "coupler": [cyl_between((0, 0, 0), (b, 0, 0), 0.004, BLUE)],
         "rocker": [cyl_between((0, 0, 0), (c, 0, 0), 0.005, GREY)]}
    joints = [J("crank", "ground", "crank", (0, 0, 0.005), (0, 0, 1), "continuous"),
              J("coupler", "crank", "coupler", (a, 0, 0.004), (0, 0, 1)),
              J("rocker", "ground", "rocker", (d, 0, 0.012), (0, 0, 1))]
    rows = []
    for k in range(0, 361, 5):
        t2 = math.radians(k)
        bx, by = a * math.cos(t2), a * math.sin(t2)                      # crank pin
        dx, dy = d - bx, -by
        e = math.hypot(dx, dy)
        cos_g = (b * b + e * e - c * c) / (2 * b * e)
        g = math.acos(max(-1, min(1, cos_g)))
        t3 = math.atan2(dy, dx) + g                                       # coupler absolute angle (open branch)
        cx, cy = bx + b * math.cos(t3), by + b * math.sin(t3)
        t4 = math.atan2(cy, cx - d)
        rows.append({"input_deg": k, "crank": round(t2, 6), "coupler": round(t3 - t2, 6), "rocker": round(t4, 6)})
    return {"id": "C-LNK-4BAR-S", "kind": "mechanism", "category": "LNK", "root": "ground", "links": L, "joints": joints,
            "name": {"zh": "曲柄摇杆机构（教学样例）", "en": "Crank-rocker four-bar linkage (teaching sample)"},
            "tags": ["四杆机构", "平面连杆", "格拉肖夫"], "view": "xy",
            "params": [{"key": "a_mm", "zh": "曲柄长", "en": "Crank", "role": "key"}, {"key": "b_mm", "zh": "连杆长", "en": "Coupler", "role": "key"},
                       {"key": "c_mm", "zh": "摇杆长", "en": "Rocker", "role": "key"}, {"key": "d_mm", "zh": "机架长", "en": "Ground", "role": "key"}],
            "defaults": {"a_mm": a * 1000, "b_mm": b * 1000, "c_mm": c * 1000, "d_mm": d * 1000},
            "ranges": {"a_mm": [10, 100], "b_mm": [40, 300], "c_mm": [30, 250], "d_mm": [40, 300]},
            "mechanism": {"dof": 1, "input": "曲柄", "output": "摇杆"}, "motion": rows,
            "rest": {"coupler": rows[0]["coupler"], "rocker": rows[0]["rocker"]},
            "teaching": {"principle": "最短杆与最长杆之和不大于另两杆之和、且最短杆为曲柄时，曲柄能整周转动，摇杆往复摆动（格拉肖夫条件）。",
                         "uses": ["雨刷", "缝纫机踏板", "颚式破碎机"], "courses": [{"course": "机械原理", "chapter": "平面连杆机构"}],
                         "labs": ["改杆长看能否整周转", "急回特性与传动角"]}}


BEARINGS = {"6205": (25, 52, 15), "6206": (30, 62, 16), "6207": (35, 72, 17)}


def bearing(size="6207") -> dict:
    d, D, B = (v / 1000 for v in BEARINGS[size])
    pitch = (d + D) / 4
    ball = (D - d) / 2 * 0.55
    L = {"outer": [("ring", pitch + ball * 0.35, D / 2, B, "z", (0, 0, 0), STEEL)],
         "inner": [("ring", d / 2, pitch - ball * 0.35, B, "z", (0, 0, 0), STEEL)],
         "balls": [("sph", ball / 2, (pitch * math.cos(2 * math.pi * k / 9), pitch * math.sin(2 * math.pi * k / 9), 0), GREY)
                   for k in range(9)]}
    joints = [J("inner", "outer", "inner", (0, 0, 0), (0, 0, 1), "continuous"),
              J("cage", "outer", "balls", (0, 0, 0), (0, 0, 1), "continuous")]
    return {"id": "A-BRG-DG-S", "spec": size, "kind": "family", "category": "BRG", "root": "outer", "links": L, "joints": joints,
            "name": {"zh": "深沟球轴承（教学样例）", "en": "Deep groove ball bearing (teaching sample)"},
            "tags": ["滚动轴承", "深沟球轴承", "62系列", "ball bearing"], "view": "bearing",
            "standards": [{"code": "GB/T 276-2013", "title": "滚动轴承 深沟球轴承 外形尺寸"}],
            "params": [{"key": "d_mm", "zh": "内径", "en": "Bore", "role": "key"}, {"key": "D_mm", "zh": "外径", "en": "Outside diameter", "role": "key"},
                       {"key": "B_mm", "zh": "宽度", "en": "Width", "role": "key"}],
            "specs": [{"size": s, "d_mm": v[0], "D_mm": v[1], "B_mm": v[2]} for s, v in BEARINGS.items()],
            "default": "6207",
            "demo": {"inner": [0, 12.0], "cage": [0, 5.0]},
            "teaching": {"principle": "钢球在内外圈滚道间滚动，以滚动摩擦代替滑动摩擦，主要承受径向载荷。",
                         "uses": ["减速器、电机转轴支承", "机器人关节"],
                         "courses": [{"course": "机械设计基础", "chapter": "滚动轴承"}, {"course": "现代机器人学", "chapter": "关节传动与支承"}],
                         "labs": ["拆装动画"]},
            "factory": {"erp_items": [{"item_code": f"BRG-{s}", "size": s} for s in BEARINGS]}}


def catalog() -> list[dict]:
    return [arm6(), scara(), gantry(), mobile(), quadruped(), humanoid(), drone(), four_bar(), bearing()]


# --- glTF ----------------------------------------------------------------------------------------------------------

def _hex(c: str) -> list[int]:
    c = c.lstrip("#")
    return [int(c[i:i + 2], 16) for i in (0, 2, 4)] + [255]


def _mesh(shape):
    import trimesh
    kind = shape[0]
    if kind == "box":
        m = trimesh.creation.box(extents=shape[1])
        if len(shape) > 4:
            m.apply_transform(axis_angle((0, 0, 1), math.radians(shape[4])))
        m.apply_translation(shape[2])
        color = shape[3]
    elif kind == "cyl":
        _, r, h, ax, xyz, color = shape
        m = trimesh.creation.cylinder(radius=r, height=h, sections=32)
        if ax == "x":
            m.apply_transform(axis_angle((0, 1, 0), math.pi / 2))
        elif ax == "y":
            m.apply_transform(axis_angle((1, 0, 0), math.pi / 2))
        m.apply_translation(xyz)
    elif kind == "sph":
        _, r, xyz, color = shape
        m = trimesh.creation.icosphere(subdivisions=2, radius=r)
        m.apply_translation(xyz)
    elif kind == "seg":
        _, r, a, b, color = shape
        a, b = np.asarray(a), np.asarray(b)
        m = trimesh.creation.cylinder(radius=r, segment=[a, b], sections=24)
    elif kind == "ring":
        _, ri, ro, h, ax, xyz, color = shape
        m = trimesh.creation.annulus(r_min=ri, r_max=ro, height=h, sections=48)
        m.apply_translation(xyz)
    else:
        raise ValueError(kind)
    # one material colour per part (no per-face colours: those need scipy to convert and make files bigger)
    m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
        baseColorFactor=_hex(color), metallicFactor=0.2, roughnessFactor=0.6))
    return m


def glb(item: dict, q: dict | None = None) -> bytes:
    """One node per link (node name = link name), nested along the joints; root node `zup` turns Z-up into Y-up.
    Exported at the ZERO pose (joint values 0): each node's transform is just its joint origin, so a viewer that
    sets joint q gets origin · R(axis, q). The rest pose (entry `rest`) is applied by the viewer, never baked in."""
    import trimesh
    scene = trimesh.Scene()
    scene.graph.update(frame_from=scene.graph.base_frame, frame_to="zup", matrix=axis_angle((1, 0, 0), -math.pi / 2))
    scene.graph.update(frame_from="zup", frame_to=item["root"], matrix=np.eye(4))
    q = q or {}
    for j in item["joints"]:
        scene.graph.update(frame_from=j["parent"], frame_to=j["child"],
                           matrix=tf(j["xyz"], j["rpy"]) @ joint_motion(j, q.get(j["name"], 0.0)))
    for link, shapes in item["links"].items():
        for i, sh in enumerate(shapes):
            scene.add_geometry(_mesh(sh), node_name=f"{link}.g{i}", geom_name=f"{link}.g{i}", parent_node_name=link)
    return scene.export(file_type="glb")


# --- SVG drawings -------------------------------------------------------------------------------------------------

def _svg_frame(title_zh: str, title_en: str, body: str, w=640, h=440, note="") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="Noto Sans CJK SC, Noto Sans SC, sans-serif">'
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>{body}'
            f'<g transform="translate({w - 250},{h - 58})"><rect width="240" height="48" fill="none" stroke="#2b3238"/>'
            f'<text x="8" y="19" font-size="13" fill="#2b3238">{title_zh}</text>'
            f'<text x="8" y="37" font-size="11" fill="#5b6770">{title_en}</text></g>'
            + (f'<text x="12" y="{h - 12}" font-size="10" fill="#8a949b">{note}</text>' if note else "")
            + "</svg>")


def _esc(t: str) -> str:
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(item: dict) -> str:
    name = item["name"]
    if item["view"] == "bearing":
        d, D, B = BEARINGS[item.get("spec", "6207")]
        s = 3.2
        cx, cy = 190, 210
        body = (f'<circle cx="{cx}" cy="{cy}" r="{D / 2 * s}" fill="#eef1f3" stroke="#2b3238" stroke-width="2"/>'
                f'<circle cx="{cx}" cy="{cy}" r="{d / 2 * s}" fill="#fff" stroke="#2b3238" stroke-width="2"/>'
                + "".join(f'<circle cx="{cx + (d + D) / 4 * s * math.cos(2 * math.pi * k / 9):.1f}" '
                          f'cy="{cy + (d + D) / 4 * s * math.sin(2 * math.pi * k / 9):.1f}" r="{(D - d) / 4 * s * 0.55:.1f}" '
                          f'fill="#c9d1d6" stroke="#2b3238"/>' for k in range(9))
                + f'<line x1="{cx - D / 2 * s}" y1="{cy + D / 2 * s + 22}" x2="{cx + D / 2 * s}" y2="{cy + D / 2 * s + 22}" stroke="#c0392b"/>'
                f'<text x="{cx}" y="{cy + D / 2 * s + 38}" font-size="13" text-anchor="middle" fill="#c0392b">D = {D} mm</text>'
                f'<text x="{cx}" y="{cy + 5}" font-size="13" text-anchor="middle" fill="#c0392b">d = {d} mm</text>'
                f'<rect x="{420}" y="{cy - D / 2 * s}" width="{B * s}" height="{D * s}" fill="#eef1f3" stroke="#2b3238" stroke-width="2"/>'
                f'<rect x="{420}" y="{cy - d / 2 * s}" width="{B * s}" height="{d * s}" fill="#fff" stroke="#2b3238"/>'
                f'<text x="{420 + B * s / 2}" y="{cy - D / 2 * s - 10}" font-size="13" text-anchor="middle" fill="#c0392b">B = {B} mm</text>')
        return _svg_frame(f"{name['zh']} {item.get('spec', '')}", name["en"], body, note="GB/T 276 外形尺寸（样例图）")
    # kinematic sketch: part outlines + links + joints at a drawing pose, projected on the chosen plane
    pose = dict(item.get("rest", {}))
    if item.get("motion"):
        row = min(item["motion"], key=lambda r: abs(r["input_deg"] - 60))
        pose = {k: row[k] for k in ("crank", "coupler", "rocker")}
    poses = fk(item, pose)
    plane = (0, 2) if item["view"] == "xz" else (0, 1)
    depth = 1 if item["view"] == "xz" else 2

    def proj(T, p):
        w = T @ np.array([p[0], p[1], p[2], 1.0])
        return w[plane[0]], w[plane[1]], w[depth]

    shapes = []   # (depth, kind, data)
    for link, shs in item["links"].items():
        T = poses[link]
        for sh in shs:
            k = sh[0]
            if k == "seg":
                (x1, y1, z1), (x2, y2, z2) = proj(T, sh[2]), proj(T, sh[3])
                shapes.append(((z1 + z2) / 2, "seg", (x1, y1, x2, y2, sh[1])))
            elif k in ("sph", "cyl", "box", "ring"):
                c = sh[2] if k == "sph" else sh[4] if k == "cyl" else sh[2] if k == "box" else sh[5]
                x, y, z = proj(T, c)
                if k == "sph":
                    shapes.append((z, "circ", (x, y, sh[1])))
                elif k == "ring":
                    shapes.append((z, "circ", (x, y, sh[2])))
                elif k == "box":
                    ext = sh[1]
                    shapes.append((z, "rect", (x, y, ext[plane[0]], ext[plane[1]])))
                else:
                    r, hgt, ax = sh[1], sh[2], sh[3]
                    local = {"x": np.array([1.0, 0, 0]), "y": np.array([0, 1.0, 0]), "z": np.array([0, 0, 1.0])}[ax]
                    wa = T[:3, :3] @ local
                    along = abs(wa[depth])
                    if along > 0.9:
                        shapes.append((z, "circ", (x, y, r)))
                    else:
                        e = wa * hgt / 2
                        shapes.append((z, "seg", (x - e[plane[0]], y - e[plane[1]], x + e[plane[0]], y + e[plane[1]], r)))
    pts = {k: (v[plane[0], 3], v[plane[1], 3]) for k, v in poses.items()}
    xs = [p[0] for p in pts.values()] + [d[0] for _, kd, d in shapes] + [d[2] for _, kd, d in shapes if kd == "seg"]
    ys = [p[1] for p in pts.values()] + [d[1] for _, kd, d in shapes] + [d[3] for _, kd, d in shapes if kd == "seg"]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 0.1) * 1.15
    sc = 300 / span
    ox, oy = 300 - (max(xs) + min(xs)) / 2 * sc, 200 + (max(ys) + min(ys)) / 2 * sc
    P = lambda x, y: (ox + x * sc, oy - y * sc)  # noqa: E731
    body = '<g fill="#e7ecef" stroke="#9aa7b0" stroke-width="1">'
    for _, kd, d in sorted(shapes, key=lambda t: t[0] if item["view"] == "xz" else t[0]):
        if kd == "circ":
            x, y = P(d[0], d[1])
            body += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(d[2] * sc, 1.5):.1f}"/>'
        elif kd == "rect":
            x, y = P(d[0], d[1])
            w, h = d[2] * sc, d[3] * sc
            body += f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{max(w, 1):.1f}" height="{max(h, 1):.1f}"/>'
        else:
            (x1, y1), (x2, y2) = P(d[0], d[1]), P(d[2], d[3])
            body += (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#c9d1d6" '
                     f'stroke-width="{max(d[4] * 2 * sc, 2):.1f}" stroke-linecap="round"/>')
    body += '</g><g stroke="#2b3238" stroke-width="2.5" fill="none">'
    for j in item["joints"]:
        (x1, y1), (x2, y2) = P(*pts[j["parent"]]), P(*pts[j["child"]])
        body += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
    if item.get("motion"):   # the coupler and rocker meet at a pin that is not a joint of the tree
        cpin = poses["coupler"] @ np.array([item["defaults"]["b_mm"] / 1000, 0, 0, 1])
        for link in ("coupler", "rocker"):
            (x1, y1), (x2, y2) = P(*pts[link]), P(cpin[0], cpin[1])
            body += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
        x, y = P(cpin[0], cpin[1])
        body += f'</g><circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="#fff" stroke="#3b82c4" stroke-width="2"/><g>'
    body += "</g>"
    placed: list[tuple[float, float, list[str]]] = []
    for i, j in enumerate(item["joints"], 1):
        x, y = P(*pts[j["child"]])
        near = next((p for p in placed if abs(p[0] - x) < 9 and abs(p[1] - y) < 9), None)
        if near:
            near[2].append(f"J{i}")
            continue
        placed.append((x, y, [f"J{i}"]))
        if j["type"] == "prismatic":
            body += f'<rect x="{x - 7:.1f}" y="{y - 7:.1f}" width="14" height="14" fill="#fff" stroke="#3b82c4" stroke-width="2"/>'
        else:
            body += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="#fff" stroke="#3b82c4" stroke-width="2"/>'
    for x, y, names in placed:
        body += f'<text x="{x + 10:.1f}" y="{y - 9:.1f}" font-size="12" fill="#3b82c4">{"/".join(names)}</text>'
    bx, by = P(*pts[item["root"]])
    if item["view"] == "xz" or item.get("motion"):
        body += (f'<path d="M{bx - 22:.1f},{by + 10:.1f} L{bx + 22:.1f},{by + 10:.1f}" stroke="#2b3238" stroke-width="3"/>'
                 + "".join(f'<line x1="{bx - 22 + 8 * k:.1f}" y1="{by + 10:.1f}" x2="{bx - 30 + 8 * k:.1f}" y2="{by + 18:.1f}" stroke="#2b3238"/>'
                           for k in range(6)))
    body += (f'<g transform="translate(40,380)"><line x1="0" y1="0" x2="40" y2="0" stroke="#c0392b" stroke-width="2"/>'
             f'<line x1="0" y1="0" x2="0" y2="-40" stroke="#27ae60" stroke-width="2"/>'
             f'<text x="44" y="4" font-size="12" fill="#c0392b">x</text>'
             f'<text x="-4" y="-44" font-size="12" fill="#27ae60">{"z" if item["view"] == "xz" else "y"}</text></g>')
    what = "侧视" if item["view"] == "xz" else "俯视"
    return _svg_frame(_esc(name["zh"]), _esc(name["en"]), body,
                      note=f"机构简图（{what}） · ○ 转动关节 revolute  □ 移动关节 prismatic")


# --- entry / index / write -----------------------------------------------------------------------------------------

def entry(item: dict) -> dict:
    out = {"schema": 1, "id": item["id"], "kind": item["kind"], "name": item["name"], "category": item["category"],
           "tags": item["tags"], "standards": item.get("standards", []), "params": item.get("params", []),
           "default": item.get("default", "default"),
           "model": {"engine": "generator:wenquest.sample", "formats": ["glb", "svg"], "up": "Z (glTF root node 'zup' turns it to Y-up)",
                     "units": "m"},
           "source": {"origin": "wenquest", "license": LICENSE, "attribution": ATTRIB,
                      "checked": {"by": "Claude", "on": "2026-09-30", "note": "临时样例，自建几何"}},
           "teaching": item["teaching"], "factory": item.get("factory", {"erp_items": [], "suppliers": []}),
           "links": list(item["links"]), "root": item["root"],
           "joints": [{k: j[k] for k in ("name", "type", "parent", "child", "axis", "lower", "upper")}
                      | {"origin": {"xyz": j["xyz"], "rpy": j["rpy"]}} for j in item["joints"]],
           "rest": item.get("rest", {}), "demo": item.get("demo", {})}
    for k in ("robot", "mechanism", "defaults", "ranges", "specs"):
        if k in item:
            out[k] = item[k]
    if "tool" in item:
        out["tool"] = {"link": item["tool"][0], "xyz": list(item["tool"][1])}
    if "motion" in item:
        out["motion"] = "motion.csv"
    return out


def build(root: str | Path, public: str = "") -> Path:
    """Write the sample library under <root>/library; `public` is the URL prefix put into index.json (may be '')."""
    base = Path(root) / "library"
    ver = base / VERSION
    rows = []
    for item in catalog():
        d = ver / item["id"]
        d.mkdir(parents=True, exist_ok=True)
        specs = [s["size"] for s in item["specs"]] if item.get("specs") else ["default"]
        for spec in specs:
            it = bearing(spec) if item["id"] == "A-BRG-DG-S" else item
            (d / f"{spec}.glb").write_bytes(glb(it))
            (d / f"{spec}.svg").write_text(svg(it), encoding="utf-8")
            href = f"{public.rstrip('/')}/library/{VERSION}/{item['id']}" if public else f"{item['id']}"
            rows.append({"id": item["id"], "spec": spec, "name": item["name"], "category": item["category"], "kind": item["kind"],
                         "tags": item["tags"], "principle": item["teaching"]["principle"],
                         "robot": item.get("robot", {}), "license": LICENSE, "attribution": ATTRIB,
                         "entry": f"{href}/entry.json", "glb": f"{href}/{spec}.glb", "svg": f"{href}/{spec}.svg"})
        (d / "entry.json").write_text(json.dumps(entry(item), ensure_ascii=False, indent=1), encoding="utf-8")
        if "motion" in item:
            buf = io.StringIO()
            w = csv.DictWriter(buf, fieldnames=list(item["motion"][0]))
            w.writeheader()
            w.writerows(item["motion"])
            (d / "motion.csv").write_text(buf.getvalue(), encoding="utf-8")
    (ver / "index.json").write_text(json.dumps({"version": VERSION, "items": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    (base / "latest.json").write_text(json.dumps({"version": VERSION, "index": f"{VERSION}/index.json"}), encoding="utf-8")
    return base


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1] if len(sys.argv) > 1 else "/tmp/wq-library"))
