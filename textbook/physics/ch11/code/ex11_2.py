"""11.2 节的计算：

算例 11.2.1  空间机器人：漂浮的基座连同机械臂共 400 kg，机械臂把 10 kg 的卫星部件以相对基座 0.50 m/s 的速度推出。
            推出后部件和基座相对太空的速度各是多少？基座推出前静止。
算例 11.2.2  轮子可以自由滚动的移动机器人（120 kg）把 2.0 kg 的球以 6.0 m/s、仰角 30° 抛出（相对地面）。
            机器人后退多快？竖直方向的动量为什么不守恒？
"""
import math

from bookout import out

M, m, u = 400.0, 10.0, 0.50
v_base = -m * u / (M + m)                                       # m(v_b + u) + M v_b = 0
v_part = v_base + u
assert abs(m * v_part + M * v_base) < 1e-12
out(M=M, m=m, u=u, v_base=-v_base * 1000, v_part=v_part, naive=m * u / M * 1000)

Mr, mb, vb, th = 120.0, 2.0, 6.0, math.radians(30.0)
v_rob = -mb * vb * math.cos(th) / Mr
out(Mr=Mr, mb=mb, vb=vb, px=mb * vb * math.cos(th), py=mb * vb * math.sin(th), v_rob=-v_rob)
