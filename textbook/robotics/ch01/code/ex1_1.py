"""算例 1.1.1：AGV 靠传感器发现前方障碍后停车，需要多远的探测距离。

停车距离 = 反应期间匀速走过的距离 + 匀减速刹停的距离，式 (1.1.4)：d = v·t_d + v²/(2a)。
用两种方法计算：公式；按小时间步逐步推进运动（数值仿真）。两者必须一致。
"""
from _ch1 import AGV_SPEED, STOP_A, STOP_TC, STOP_TP, stop_distance
from bookout import out

v = AGV_SPEED          # 数字工厂 AGV 的行驶速度，m/s
T_c = STOP_TC          # 控制周期，s（假设：控制器每 20 ms 读一次传感器）
t_p = STOP_TP          # 识别障碍、发出指令到制动器起作用的时间，s（假设）
t_d = T_c + t_p        # 反应时间，s
a = STOP_A             # 制动减速度，m/s²（假设：满载小车平稳刹车，货物不滑动）


stop_formula = stop_distance        # 式 (1.1.4)


def stop_sim(v, t_d, a, h=1e-5):
    """逐步推进：反应期间匀速，之后每一步速度减小 a·h，直到速度为零。"""
    x, t, u = 0.0, 0.0, v
    while u > 0:
        if t < t_d:
            x += u * h
        else:
            u_new = max(0.0, u - a * h)
            x += 0.5 * (u + u_new) * h          # 一步内速度线性变化，走过的距离取平均速度乘步长
            u = u_new
        t += h
    return x, t


d = stop_formula(v, t_d, a)
d_sim, t_sim = stop_sim(v, t_d, a)
assert abs(d - d_sim) < 1e-4                    # 公式与逐步推进一致
t_stop = t_d + v / a                            # 从发现障碍到停住的时间
assert abs(t_stop - t_sim) < 1e-3

d_react, d_brake = v * t_d, v * v / (2 * a)
# 速度提高一半：刹车距离按速度的平方增长
v2 = 1.5 * v
d2 = stop_formula(v2, t_d, a)
assert abs(d2 - (v2 * t_d + v2 ** 2 / (2 * a))) < 1e-12
# 开环（不看传感器）的小车：按程序走完 5 m，若障碍在 3 m 处，必然相撞
L_prog, x_obs = 5.0, 3.0

out(v=v, T_c=T_c, t_p=t_p, t_d=t_d, a=a, d=d, d_sim=d_sim, d_react=d_react, d_brake=d_brake, t_stop=t_stop,
    v2=v2, d2=d2, ratio_brake=(v2 ** 2 / (2 * a)) / d_brake, L_prog=L_prog, x_obs=x_obs,
    d_margin=1.5 * d)
