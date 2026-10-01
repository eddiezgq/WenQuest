"""第 39 章共用：力传感器测量链的参数与模型（应变片 → 全桥 → 仪表放大器 → 12 位 ADC），以及数字工厂的磨削检测模型。
以下划线开头，构建时不单独运行。所有数值例子都从这里取，正文与实验一致。
"""
import math

import numpy as np

# ---------------------------------------------------------------- 测力传感器（S 型或平行梁式称重传感器）
F_FS = 100.0          # 量程 N
GF = 2.0              # 应变片灵敏系数
R_G = 350.0           # 应变片电阻 Ω
V_EX = 5.0            # 激励电压 V
RO = 2.0e-3           # 额定输出 2 mV/V
EPS_FS = RO / GF      # 满量程时全桥的“等效应变”（四片应变片 ±ε 各一半贡献）：V/Vex = GF·ε → ε = 1000 µε

# 仪表放大器（三运放结构，增益 G = 1 + 2R/R_g；以 AD620 一类为例 49.4 kΩ/R_g）
R_IA = 24.7e3         # 内部反馈电阻 R（每个），2R = 49.4 kΩ
RG_SEL = 200.0        # 选用的增益电阻 Ω（E96 系列中不小于理想值、使满量程不溢出的一档）
GAIN = 1 + 2 * R_IA / RG_SEL

# 模数转换器
ADC_BITS = 12
V_REF = 2.5


def bridge_full(eps, v_ex=V_EX, gf=GF):
    """全桥（四臂均为应变片，两拉两压）：Vout = Vex·GF·ε，与 ε 成正比。"""
    return v_ex * gf * eps


def bridge_half(eps, v_ex=V_EX, gf=GF):
    """半桥（相邻两臂，一拉一压）：Vout = Vex·GF·ε/2。"""
    return v_ex * gf * eps / 2


def bridge_quarter(eps, v_ex=V_EX, gf=GF):
    """单臂电桥（一片应变片）：Vout = Vex·x/(4 + 2x)，x = GF·ε；小应变时 ≈ Vex·GF·ε/4。"""
    x = gf * eps
    return v_ex * x / (4 + 2 * x)


def adc(v, bits=ADC_BITS, vref=V_REF):
    """理想 ADC：0 … Vref 均匀量化，返回码值（截断到范围内）。"""
    code = np.floor(np.asarray(v) / vref * 2 ** bits)
    return np.clip(code, 0, 2 ** bits - 1)


# ---------------------------------------------------------------- 数字工厂：SH-301 轴承位直径（factory/digital/sim/engine.py 的同一模型）
SPEC_LO, SPEC_HI, NOMINAL = 35.002, 35.018, 35.010        # Ø35 k6，mm
WEAR_PER_PART = 1 / 30                                     # 砂轮每磨一件的磨损
DRESS_AT = 0.08                                            # 剩余寿命低于此值时修整


def bearing_seat(n_parts, seed=39, dress_every=None):
    """按数字工厂的磨削模型生成 n 件的直径：均值 35.0065 + 0.0125·磨损，标准差 0.0012 mm。
    砂轮修整：默认按工厂的做法，剩余寿命低于 0.08 时修整（约每 28 件一次）；给出 dress_every 则每磨这么多件修整一次。"""
    rng = np.random.default_rng(seed)
    life, out, wear_log = 1.0, [], []
    for i in range(n_parts):
        wear = 1 - life
        out.append(round(float(rng.normal(35.0065 + 0.0125 * wear, 0.0012)), 4))
        wear_log.append(wear)
        life = max(0.0, life - WEAR_PER_PART)
        if (dress_every is None and life < DRESS_AT) or (dress_every is not None and (i + 1) % dress_every == 0):
            life = 1.0
    return np.array(out), np.array(wear_log)


# 控制图常数（子组容量 n = 5）
A2, D3, D4, D2 = 0.577, 0.0, 2.114, 2.326
