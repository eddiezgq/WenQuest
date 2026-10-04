"""Example 1.1.1: how far ahead an AGV must detect an obstacle with its sensor to stop in time.

Stopping distance = distance travelled at constant speed during the reaction time + distance braking at constant
deceleration, Eq. (1.1.4): d = v·t_d + v²/(2a).
Computed two ways: by the formula, and by advancing the motion in small time steps (numerical simulation). The two
must agree.
"""
from _ch1 import AGV_SPEED, STOP_A, STOP_TC, STOP_TP, stop_distance
from bookout import out

v = AGV_SPEED          # travel speed of the digital factory's AGV, m/s
T_c = STOP_TC          # control period, s (assumption: the controller reads the sensor every 20 ms)
t_p = STOP_TP          # time from recognising the obstacle and issuing the command until the brake acts, s (assumption)
t_d = T_c + t_p        # reaction time, s
a = STOP_A             # braking deceleration, m/s² (assumption: fully loaded cart brakes smoothly, the load does not slide)


stop_formula = stop_distance        # Eq. (1.1.4)


def stop_sim(v, t_d, a, h=1e-5):
    """Step by step: constant speed during the reaction time, then the speed drops by a·h each step until it is zero."""
    x, t, u = 0.0, 0.0, v
    while u > 0:
        if t < t_d:
            x += u * h
        else:
            u_new = max(0.0, u - a * h)
            x += 0.5 * (u + u_new) * h          # speed changes linearly within a step: distance = mean speed × step
            u = u_new
        t += h
    return x, t


d = stop_formula(v, t_d, a)
d_sim, t_sim = stop_sim(v, t_d, a)
assert abs(d - d_sim) < 1e-4                    # formula and step-by-step simulation agree
t_stop = t_d + v / a                            # time from detecting the obstacle to standing still
assert abs(t_stop - t_sim) < 1e-3

d_react, d_brake = v * t_d, v * v / (2 * a)
# Speed raised by half: the braking distance grows with the square of the speed
v2 = 1.5 * v
d2 = stop_formula(v2, t_d, a)
assert abs(d2 - (v2 * t_d + v2 ** 2 / (2 * a))) < 1e-12
# Open-loop cart (ignores its sensors): programmed to drive 5 m; with an obstacle at 3 m it must collide
L_prog, x_obs = 5.0, 3.0

out(v=v, T_c=T_c, t_p=t_p, t_d=t_d, a=a, d=d, d_sim=d_sim, d_react=d_react, d_brake=d_brake, t_stop=t_stop,
    v2=v2, d2=d2, ratio_brake=(v2 ** 2 / (2 * a)) / d_brake, L_prog=L_prog, x_obs=x_obs,
    d_margin=1.5 * d)
