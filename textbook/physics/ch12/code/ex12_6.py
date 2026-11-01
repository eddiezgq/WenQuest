"""12.6 节的计算：

算例 12.6.1  冲床的飞轮：转动惯量 20 kg·m²，冲压前转速 300 r/min，每冲一次从飞轮取走 2.0 kJ。冲完转速降到多少？
            电机要在 2.0 s 内把飞轮补回原转速，平均功率至少多少？没有飞轮，冲压的 0.050 s 内电机要提供多大的功率？
算例 12.6.2  直径 1.2 m 的转台（转动惯量 18 kg·m²）以 30 r/min 转动，制动器在 1.5 圈内把它停下。制动力矩多大？吸收多少能量？
"""
import math

from bookout import out

J, n0, Ep = 20.0, 300.0, 2000.0
w0 = n0 * 2 * math.pi / 60
K0 = 0.5 * J * w0 ** 2
w1 = math.sqrt(2 * (K0 - Ep) / J)
out(Jf=J, n0=n0, w0=w0, K0_kJ=K0 / 1e3, w1=w1, n1=w1 * 60 / (2 * math.pi), drop=1 - w1 / w0, P_motor=Ep / 2.0, P_punch=Ep / 0.050)

Jt, nt, turns = 18.0, 30.0, 1.5
wt = nt * 2 * math.pi / 60
Kt = 0.5 * Jt * wt ** 2
th = turns * 2 * math.pi
Mb = Kt / th
out(Jt=Jt, nt=nt, wt=wt, Kt=Kt, th=th, Mb=Mb, t_stop=wt / (Mb / Jt))
