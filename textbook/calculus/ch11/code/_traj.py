"""第 7 章共用：UR5e 的连杆长度（读零件库关节表）与三种“静止到静止”的关节运动规律。以下划线开头，构建时不单独运行。

三种运动规律都让关节在时间 T 内从 θ0 转到 θ0 + Δ，起点和终点的角速度都为零：
  三次多项式  θ = θ0 + Δ(3s² − 2s³)
  五次多项式  θ = θ0 + Δ(10s³ − 15s⁴ + 6s⁵)
  梯形速度    匀加速 ta → 匀速 → 匀减速 ta
其中 s = t/T。函数返回 (θ, ω, α, j)：角度、角速度、角加速度、角加加速度，用公式直接算出（不做数值求导）。
"""
import json
import math
from pathlib import Path

import numpy as np

MODELS = Path(__file__).resolve().parents[2] / "models"


def ur5e_links():
    """UR5e 上臂与前臂的长度（肩关节到肘关节、肘关节到腕关节 1），单位 m，由零件库关节表读出。"""
    js = {j["name"]: j for j in json.loads((MODELS / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))["robot"]["joints"]}
    return js["elbow_joint"]["origin"]["xyz"][2], js["wrist_1_joint"]["origin"]["xyz"][2]


def ur5e_version():
    return json.loads((MODELS / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8")).get("version", "")


def cubic(t, T, delta, th0=0.0):
    s = np.clip(np.asarray(t, float) / T, 0, 1)
    th = th0 + delta * (3 * s**2 - 2 * s**3)
    w = delta / T * (6 * s - 6 * s**2)
    a = delta / T**2 * (6 - 12 * s)
    j = delta / T**3 * (-12 + 0 * s)
    inside = (np.asarray(t) > 0) & (np.asarray(t) < T)
    return th, w * inside, a * inside, j * inside


def quintic(t, T, delta, th0=0.0):
    s = np.clip(np.asarray(t, float) / T, 0, 1)
    th = th0 + delta * (10 * s**3 - 15 * s**4 + 6 * s**5)
    w = delta / T * (30 * s**2 - 60 * s**3 + 30 * s**4)
    a = delta / T**2 * (60 * s - 180 * s**2 + 120 * s**3)
    j = delta / T**3 * (60 - 360 * s + 360 * s**2)
    inside = (np.asarray(t) > 0) & (np.asarray(t) < T)
    return th, w, a, j * inside


def trapezoid(t, T, delta, ta, th0=0.0):
    """匀加速时间 ta（0 < ta ≤ T/2）；巡航角速度 wc = Δ/(T − ta)，角加速度 ±wc/ta。加加速度在折点处是冲激，这里返回 0（另行说明）。"""
    t = np.asarray(t, float)
    wc = delta / (T - ta)
    a0 = wc / ta
    th = np.where(t < ta, 0.5 * a0 * t**2,
         np.where(t < T - ta, 0.5 * a0 * ta**2 + wc * (t - ta),
                  delta - 0.5 * a0 * (T - t).clip(0) ** 2))
    th = np.where(t <= 0, 0, np.where(t >= T, delta, th)) + th0
    w = np.where(t < ta, a0 * t, np.where(t < T - ta, wc, a0 * (T - t)))
    w = np.where((t <= 0) | (t >= T), 0, w)
    a = np.where(t < ta, a0, np.where(t < T - ta, 0.0, -a0))
    a = np.where((t <= 0) | (t >= T), 0, a)
    return th, w, a, np.zeros_like(t)
