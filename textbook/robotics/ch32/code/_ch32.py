"""第 32 章共用：传动与减速器。以下划线开头，构建时不单独运行。

主角仍是问渠机器人厂的 WQ-CR5（factory/digital/cae/wqcr5.py）；齿轮传动的实物是减速器厂的 WQR-105（factory/factory/data.py 的齿轮、
工序检验的公法线偏差；效率取问渠 CAE 热分析示例的同一组数 factory/digital/cae/thermal_parts.py）。
谐波减速器的寿命用问渠“运动与动力分析”的同一段程序（factory/digital/twin/robot.py 的 joint_life）。
减速器的厂商参数读零件库：D-RDC-HD-CSF（Harmonic Drive）、D-RDC-NABTESCO-RVN（Nabtesco）、D-RDC-NEUGART-PLE（Neugart）。
WQ-CR5、两座工厂的数都是示例值。
"""
import csv
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DIGITAL = ROOT / "factory" / "digital"
G0 = 9.81
ARCMIN = math.pi / 180 / 60


def _path(p):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def wqcr5():
    _path(DIGITAL / "cae")
    import wqcr5 as W                    # noqa: E402
    return W


def joint_life():
    """问渠“运动与动力分析”算谐波减速器寿命的函数（twin/robot.py），返回 (函数, 额定寿命 h, 额定输入转速 r/min)"""
    _path(DIGITAL)
    from twin import robot as RB         # noqa: E402
    return RB.joint_life, RB.L_RATED_H, RB.N_RATED_RPM


def gearbox():
    """减速器厂 WQR-105 的齿轮、输入转速（factory/factory/data.py）与效率（thermal_parts.WQR105）"""
    _path(ROOT / "factory")
    from factory import data as D        # noqa: E402
    _path(DIGITAL)
    from cae import thermal_parts as TP  # noqa: E402
    return D, TP.WQR105


def library(eid):
    """零件库条目的规格表：[{列: 值}]"""
    for f in (ROOT / "library" / "catalog").glob(f"*/{eid}/specs.csv"):
        with f.open(encoding="utf-8") as fh:
            return list(csv.DictReader(fh))
    raise FileNotFoundError(eid)


def runin_series(payload_kg=5.0, dt=0.002, accel_scale=1.0):
    """负载跑合台的标准动作（第 29 章）：t、各关节力矩 τ（逆动力学，含转子惯量，无摩擦）、角速度 θ̇。
    accel_scale > 1 表示动作更快：时间按 1/√k 缩短，速度乘 √k，加速度乘 k"""
    import mujoco
    W = wqcr5()
    m = mujoco.MjModel.from_xml_string(W.mjcf(friction=False, payload_kg=payload_kg))
    m.opt.disableflags |= int(mujoco.mjtDisableBit.mjDSBL_CONTACT) | int(mujoco.mjtDisableBit.mjDSBL_LIMIT)
    d = mujoco.MjData(m)
    k = math.sqrt(accel_scale)
    T = W.runin_duration()
    ts = np.arange(0.0, T + 1e-9, dt)
    tau, qd = [], []
    for x in ts:
        q, v, a = W.runin_ref(x)
        d.qpos[:6], d.qvel[:6], d.qacc[:6] = q, v * k, a * k * k
        mujoco.mj_inverse(m, d)
        tau.append(d.qfrc_inverse[:6].copy())
        qd.append(v * k)
    return ts / k, np.array(tau), np.array(qd)
