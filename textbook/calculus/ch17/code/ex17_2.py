"""17.2 节：液体的压力——清洁机器人水箱侧壁（矩形）上的总压力与压力中心；水下机器人（ROV）圆形观察窗在 50 m 深处受的力
与压力中心；梯形闸门（坝面）上的总压力。"""
import math

from scipy import integrate

from bookout import out

g = 9.81
# 水箱侧壁：宽 0.3 m，水深 0.25 m（淡水）
rho, w, H = 1000.0, 0.3, 0.25
F_wall = integrate.quad(lambda y: rho * g * y * w, 0, H)[0]           # y：水面以下的深度
yc = integrate.quad(lambda y: y * rho * g * y * w, 0, H)[0] / F_wall
out(F_wall=F_wall, F_wall_ex=rho * g * w * H * H / 2, yc_wall=yc, yc_ratio=yc / H)
# ROV 观察窗：半径 0.1 m，竖直安装，中心在 50 m 深处（海水 1025 kg/m³）
rho_s, r, hc = 1025.0, 0.1, 50.0
F_win = integrate.quad(lambda s: rho_s * g * (hc + s) * 2 * math.sqrt(r * r - s * s), -r, r)[0]   # s：相对中心向下
cp = integrate.quad(lambda s: s * rho_s * g * (hc + s) * 2 * math.sqrt(r * r - s * s), -r, r)[0] / F_win
out(F_win=F_win / 1000, F_win_ex=rho_s * g * hc * math.pi * r * r / 1000, cp_win_mm=cp * 1000, cp_win_ex_mm=r * r / (4 * hc) * 1000,
    p_win=rho_s * g * hc / 1e6, m_equiv=F_win / g / 1000)
# 梯形闸门：顶宽 6 m（在水面），底宽 4 m，高 5 m
Wt, Wb, Hg = 6.0, 4.0, 5.0
wd = lambda y: Wt - (Wt - Wb) * y / Hg
F_gate = integrate.quad(lambda y: rho * g * y * wd(y), 0, Hg)[0]
out(F_gate=F_gate / 1000)
