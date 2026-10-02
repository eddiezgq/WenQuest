# -*- coding: utf-8 -*-
"""第 25 章算例：时效与孔位漂移、工序尺寸链、磨削几何、谐波加速度误差。运行即打印正文里用到的数。"""
import math
import numpy as np
from ch25_model import *

# ---------------- 25.3 时效：残余应力释放引起的针杆孔漂移（悬臂梁示意）
E_CI = 120e9                 # 灰铸铁弹性模量 Pa（示意）
B, H, T = 0.060, 0.070, 0.007  # 机臂截面：前后宽 60、高 70、壁厚 7 mm（箱形，示意）
LC = 0.250                   # 立柱到机头（针杆孔）的悬臂长度
SKIN = 0.002                 # 表层厚 2 mm
def arm_I_vertical_axis():   # 绕竖直轴（前后弯曲）
    return (H * B**3 - (H - 2*T) * (B - 2*T)**3) / 12
def tip_drift(sigma_unbal, released):
    F = sigma_unbal * SKIN * H                       # 前壁（或后壁）表层的不平衡残余应力合力
    M = F * (B / 2 - SKIN / 2)
    kappa = M / (E_CI * arm_I_vertical_axis())
    return kappa * LC**2 / 2 * released              # 悬臂端部位移 m
TAU = 3.0      # 月，常温下应力松弛的时间常数（示意）
F_INF = 0.5    # 常温下最终释放的比例（示意）
def drift_curve(sig0, months):
    return tip_drift(sig0, F_INF * (1 - np.exp(-months / TAU)))
SIG_RAW, SIG_AGED = 40e6, 10e6   # 不时效 / 人工时效后的不平衡残余应力（示意）

# ---------------- 25.4 工序尺寸链：下轴孔轴线到底板上平面 H0 = 32 ± 0.03
H0, TH0 = 32.0, 0.03
A1, TA1 = 115.0, 0.02        # 工序尺寸：底面 → 底板上平面（铣）
def chain():
    A2 = A1 - H0
    T2_ext = TH0 - TA1                       # 极值法：T0 = T1 + T2
    T2_rss = math.sqrt(TH0**2 - TA1**2)      # 统计法：T0² = T1² + T2²
    return A2, T2_ext, T2_rss
def chain_mc(T2, n=200000, seed=1):
    rng = np.random.default_rng(seed)
    a1 = rng.normal(A1, TA1/3, n); a2 = rng.normal(A1 - H0, T2/3, n)
    h = a1 - a2
    return np.mean(np.abs(h - H0) <= TH0)

# ---------------- 25.7 磨削几何：砂轮中心轨迹与磨削点
def grind_geometry(c, law, Rg):
    nm = nominal(c, law)
    psi = np.pi/2 - PHI                     # 从动件相对凸轮的方位（凸轮逆时针转 φ）
    Rp = nm['Rp']
    x, y = Rp*np.cos(psi), Rp*np.sin(psi)
    dx, dy = deriv(x), deriv(y)
    L = np.hypot(dx, dy)
    nx, ny = dy/L, -dx/L
    sgn = np.sign(nx*x + ny*y); nx, ny = nx*sgn, ny*sgn
    Px, Py = x - c['rr']*nx, y - c['rr']*ny        # 实际廓线
    Wx, Wy = Px + Rg*nx, Py + Rg*ny               # 砂轮中心（凸轮坐标）
    X = np.hypot(Wx, Wy)
    gam = np.arctan2(Wx*ny - Wy*nx, Wx*nx + Wy*ny)    # 法线与中心连线的夹角
    lagP = np.arctan2(Px*Wy - Py*Wx, Px*Wx + Py*Wy)   # 磨削点相对中心连线的方位角（从凸轮中心看）
    thW = np.unwrap(np.arctan2(Wy, Wx))
    return dict(X=X, gam=gam, lag=lagP, th=thW, Px=Px, Py=Py, nx=nx, ny=ny)

if __name__ == '__main__':
    print('I =', arm_I_vertical_axis())
    for s in (SIG_RAW, SIG_AGED):
        print('sigma %.0f MPa: full release %.1f um, natural 12 months %.1f um' % (s/1e6, tip_drift(s, 1)*1e6, drift_curve(s, 12)*1e6))
    A2, te, tr = chain()
    print('A2 = %.3f, ext ±%.3f, rss ±%.4f' % (A2, te, tr))
    print('MC pass ext %.4f rss %.4f' % (chain_mc(te), chain_mc(tr)))
    print('MC pass if A2 tol ±0.03 (wrong) %.4f' % chain_mc(0.03))
    c = CAMS['looper']
    for Rg in (200, 100, 50):
        g = grind_geometry(c, 'mtrap', Rg)
        print('Rg', Rg, 'X range %.3f' % (g['X'].max()-g['X'].min()), 'gam max %.2f deg' % np.degrees(np.abs(g['gam']).max()),
              'lag max %.2f deg' % np.degrees(np.abs(g['lag']).max()),
              'err for d=0.05 mm moved-in: %.3f um' % (0.05e3*(1-np.cos(g['gam'])).max()))
    w = omega(6000)
    print('omega', w)
    for k in (1, 2, 3, 6, 12, 24, 36):
        print('k', k, 'a per um = %.2f m/s2' % (1e-6*(k*w)**2))
    print('a_lim looper', a_limit(c))
    e = error_curve(c, 'mtrap', k=24, ek=2.0)
    print('chatter n allow before/after', n_allow(c, 'mtrap', e), n_allow(c, 'mtrap', compensate(e)))

def index_coax(dc_um, dtheta_arcsec, L_mm):
    """调头镗孔的同轴度估算：2×回转中心找正误差 + 分度误差×距离（μm）"""
    return 2 * dc_um + math.radians(dtheta_arcsec / 3600) * L_mm * 1000

def thermal_fit(d_mm, a1, a2, dT):
    return d_mm * (a1 - a2) * dT * 1000   # μm

if __name__ == '__main__':
    print('index coax 5um 5" 150mm =', index_coax(5, 5, 150))
    print('ex6 4um 4" 200mm =', index_coax(4, 4, 200))
    print('thermal Al-steel 20mm 30K =', thermal_fit(20, 23e-6, 11.5e-6, 30))
    w = omega(5000); a = 1.5e-6 * (18 * w) ** 2
    print('ex4 a=%.1f n100=%.0f' % (a, 5000 * math.sqrt(100 / a)))
    print('ex3 25MPa full %.1f half %.1f' % (tip_drift(25e6, 1) * 1e6, tip_drift(25e6, .5) * 1e6))
    print('ex2 rss', math.sqrt(0.025**2 - 0.015**2))
    print('ex5', 30 * (1 / math.cos(math.radians(9)) - 1))
    c = CAMS['looper']; nm = nominal(c, 'mtrap'); print('alpha max', np.degrees(nm['alpha'].max()))
    for law in LAWS:
        e = error_curve(c, law); r = evaluate(c, law, e, 6000); print(law, r['pv'], r['aemax'], r['sig'].max())
