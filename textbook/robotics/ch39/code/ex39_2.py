"""算例 39.2.1–39.2.3：应变片电桥与仪表放大器。

39.2.1 单片应变片 350 Ω、GF = 2、ε = 500 µε：电阻变化只有 0.35 Ω；单臂电桥的精确输出与线性近似之差。
39.2.2 三种接法在同一应变下的输出：单臂、半桥、全桥。
39.2.3 称重传感器（100 N、2 mV/V、5 V 激励）配仪表放大器与 12 位 ADC：增益电阻怎样选，力的分辨率是多少。
"""
import numpy as np

from _meas import (ADC_BITS, EPS_FS, F_FS, GAIN, GF, R_G, R_IA, RG_SEL, RO, V_EX, V_REF, bridge_full, bridge_half,
                   bridge_quarter)
from bookout import out

# 39.2.1
eps = 500e-6
dR = R_G * GF * eps
vq = bridge_quarter(eps)
vq_lin = V_EX * GF * eps / 4
nonlin_q = (vq_lin - vq) / vq * 100                # 线性近似偏大的百分比
assert abs(vq - V_EX * GF * eps / (4 + 2 * GF * eps)) < 1e-15

# 满量程 1000 µε 时单臂电桥的非线性
eps2 = 1000e-6
nonlin_q2 = (V_EX * GF * eps2 / 4 - bridge_quarter(eps2)) / bridge_quarter(eps2) * 100

# 39.2.2
vh, vf = bridge_half(eps), bridge_full(eps)
assert np.isclose(vf, 4 * vq_lin) and np.isclose(vh, 2 * vq_lin)

# 39.2.3
v_fs = RO * V_EX                                   # 满量程电桥输出 10 mV
g_need = V_REF / v_fs                              # 希望满量程正好对应 ADC 参考电压
rg_ideal = 2 * R_IA / (g_need - 1)
v_out_fs = GAIN * v_fs                             # 选 E96 电阻 200 Ω 后的实际满量程输出
assert (1 + 2 * R_IA / 196) * v_fs > V_REF > v_out_fs   # 正文：E96 相邻的 196 Ω 会溢出，200 Ω 不会
lsb = V_REF / 2 ** ADC_BITS
f_res = lsb / (GAIN * RO * V_EX / F_FS)            # 一个码值对应的力
cm = V_EX / 2                                      # 电桥两输出端的共模电压
cmrr_db = 100.0                                    # 仪表放大器的共模抑制比（典型 100 dB，G ≥ 100 时）
cm_rti = cm / 10 ** (cmrr_db / 20)                 # 共模电压折算到输入端的误差（相当于多了这么大的差模信号）
cm_err_N = cm_rti / (RO * V_EX / F_FS)

out(eps_ue=eps * 1e6, dR=dR, vq_mV=vq * 1e3, vq_lin_mV=vq_lin * 1e3, nonlin_q=nonlin_q, nonlin_q2=nonlin_q2,
    vh_mV=vh * 1e3, vf_mV=vf * 1e3, eps_fs_ue=EPS_FS * 1e6, v_fs_mV=v_fs * 1e3, g_need=g_need, rg_ideal=rg_ideal,
    rg_sel=RG_SEL, gain=GAIN, v_out_fs=v_out_fs, lsb_mV=lsb * 1e3, f_res=f_res, cm=cm, cmrr_db=cmrr_db,
    cm_rti_uV=cm_rti * 1e6, cm_err_N=cm_err_N, adc_bits=ADC_BITS)
