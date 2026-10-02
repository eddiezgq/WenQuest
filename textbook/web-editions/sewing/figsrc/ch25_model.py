# -*- coding: utf-8 -*-
"""第 25 章共用模型：凸轮升程、压力角、廓线误差（谐波）、补偿磨削、加速度误差、接触应力。
虚拟实验 labs/cam.html 用同一组公式和参数（示意值）。"""
import math
import numpy as np

N = 720                       # 每转采样点（0.5°）
KMAX = 50                     # 评定用谐波上限（1–50 阶，类似圆度测量的 50 UPR 滤波）
PHI = np.arange(N) * 2 * np.pi / N

# 凸轮类型（示意值）：r0 基圆半径(实际廓线) mm，rr 滚子半径，h 行程，各段角度 deg，nmax 最高转速 r/min，
# m 折算到从动件的质量 kg，Fw 工作载荷 N，L 凸轮厚 mm，law 默认运动规律
CAMS = {
    'looper': dict(zh='弯针凸轮（链缝/绷缝机，示意）', en='Looper cam (chainstitch/coverstitch, illustrative)',
                   r0=20.0, rr=6.0, h=6.0, rise=150, dwell=30, ret=150, nmax=6000, m=0.06, Fw=20.0, L=8.0, law='mtrap'),
    'takeup': dict(zh='挑线凸轮（凸轮式挑线，中低速机）', en='Take-up cam (cam take-up, medium/low speed)',
                   r0=22.0, rr=5.0, h=10.0, rise=110, dwell=30, ret=150, nmax=2500, m=0.03, Fw=15.0, L=8.0, law='mtrap'),
    'feed':   dict(zh='抬牙凸轮（送布，示意）', en='Feed-lift cam (feed, illustrative)',
                   r0=15.0, rr=5.0, h=2.2, rise=180, dwell=0, ret=180, nmax=5000, m=0.05, Fw=20.0, L=8.0, law='harm'),
}
LAWS = {'harm': ('简谐', 'Simple harmonic'), 'cyc': ('摆线', 'Cycloidal'), 'mtrap': ('修正梯形', 'Modified trapezoid')}

def law_unit(law, T):
    """归一化位移 S(T)、T∈[0,1]，S(0)=0, S(1)=1"""
    T = np.clip(T, 0, 1)
    if law == 'harm':
        return (1 - np.cos(np.pi * T)) / 2
    if law == 'cyc':
        return T - np.sin(2 * np.pi * T) / (2 * np.pi)
    # 修正梯形：加速度分段（1/8 正弦升、1/4 常值、1/4 余弦过零、1/4 常值、1/8 正弦回零），数值积分后归一化
    return _mtrap(T)

_MT = None
def _mtrap(T):
    global _MT
    if _MT is None:
        n = 8000
        t = (np.arange(n) + 0.5) / n
        a = np.where(t < 1/8, np.sin(4*np.pi*t),
            np.where(t < 3/8, 1.0,
            np.where(t < 5/8, np.cos(4*np.pi*(t-3/8)),
            np.where(t < 7/8, -1.0, -np.sin(4*np.pi*(1-t))))))
        v = np.concatenate([[0], np.cumsum(a)]) / n
        s = np.concatenate([[0], np.cumsum((v[1:] + v[:-1]) / 2)]) / n
        _MT = (np.linspace(0, 1, n + 1), s / s[-1])
    return np.interp(T, _MT[0], _MT[1])

def lift(c, law, phi):
    """从动件升程 s(φ)（mm），推程—远休止—回程—近休止"""
    f = np.degrees(phi) % 360
    r1, d1, r2, h = c['rise'], c['dwell'], c['ret'], c['h']
    s = np.zeros_like(f)
    m1 = f < r1; s[m1] = h * law_unit(law, f[m1] / r1)
    m2 = (f >= r1) & (f < r1 + d1); s[m2] = h
    m3 = (f >= r1 + d1) & (f < r1 + d1 + r2); s[m3] = h * (1 - law_unit(law, (f[m3] - r1 - d1) / r2))
    return s

def deriv(y, k=1):
    """周期函数对 φ 的数值导数（谱方法）"""
    Y = np.fft.rfft(y); kk = np.arange(len(Y))
    return np.fft.irfft(Y * (1j * kk) ** k, n=len(y))

def nominal(c, law):
    s = lift(c, law, PHI)
    s1, s2 = deriv(s, 1), deriv(s, 2)                       # mm/rad, mm/rad²
    Rp = c['r0'] + c['rr'] + s                              # 滚子中心（理论廓线）半径
    alpha = np.arctan2(s1, Rp)                              # 压力角（对心直动滚子）
    rho_p = (Rp**2 + s1**2)**1.5 / (Rp**2 + 2*s1**2 - Rp*s2)  # 理论廓线曲率半径
    rho_c = rho_p - c['rr']                                 # 实际廓线曲率半径（凸为正）
    return dict(s=s, s1=s1, s2=s2, Rp=Rp, alpha=alpha, rho_c=rho_c)

def omega(n_rpm):
    return 2 * np.pi * n_rpm / 60

def a_nom_peak(c, law, n):
    nm = nominal(c, law)
    return np.max(np.abs(nm['s2'])) * 1e-3 * omega(n) ** 2   # m/s²

def a_limit(c):
    """加速度误差限值：最高转速下名义峰值加速度（修正梯形/默认规律）的 10%（示意）"""
    return 0.10 * a_nom_peak(c, c['law'], c['nmax'])

# 误差源（μm）
HT = {'carb': dict(zh='渗碳淬火', en='Carburise & quench', d2=20.0, d3=8.0),
      'ind':  dict(zh='感应淬火', en='Induction hardening', d2=8.0, d3=3.0)}
EPS = 0.25          # 误差复映系数：每一次精磨走刀把上一次的形状误差缩小到 25%（示意）
E1 = 1.0            # 工件主轴/装夹偏心造成的一阶误差（μm，固定）
PH = dict(p1=60, p2=30, p3=100, pk=0)   # 各谐波相位（deg，示意）
R_PROG = 200.0      # 控制器里的砂轮半径（mm）
D_RES = 0.002       # 更新半径后的残余（测量）误差，mm

def eta(k):
    """一轮补偿磨削对第 k 阶误差的修正率（示意）：低阶约 85%，阶次越高越难修正"""
    return 0.85 * np.exp(-(np.asarray(k, float) / 20.0) ** 2)

def error_curve(c, law, ht='carb', passes=1, k=6, ek=3.0, R_act=200.0, rcomp=True):
    """磨削后的升程误差 e(φ)（μm），未经补偿"""
    nm = nominal(c, law)
    h = HT[ht]; r = EPS ** passes
    d = math.radians
    e = (E1 * np.cos(PHI + d(PH['p1']))
         + r * h['d2'] * np.cos(2 * PHI + d(PH['p2']))
         + r * h['d3'] * np.cos(3 * PHI + d(PH['p3']))
         + ek * np.cos(k * PHI + d(PH['pk'])))
    dw = D_RES if rcomp else (R_PROG - R_act)          # 砂轮比控制器里的值小 dw：工件处处多留 dw（法向）
    e = e + dw * 1e3 / np.cos(nm['alpha'])
    return e

def spectrum(e):
    C = np.fft.rfft(e) / len(e)       # e = C0 + 2 Re Σ C_k e^{ikφ}
    return C

def filt(e, kmax=KMAX):
    C = np.fft.rfft(e); C[kmax + 1:] = 0
    return np.fft.irfft(C, n=len(e))

def compensate(e, rounds=1):
    C = np.fft.rfft(e); kk = np.arange(len(C))
    C = C * (1 - eta(kk)) ** rounds
    return np.fft.irfft(C, n=len(e))

def evaluate(c, law, e, n):
    """返回：尺寸偏差 μm、形状误差 P-V μm、加速度误差峰值 m/s²（转速 n）、加速度误差曲线、接触应力曲线 MPa"""
    ef = filt(e)
    size = ef.mean()
    shape = ef - size
    pv = shape.max() - shape.min()
    ae = deriv(shape, 2) * 1e-6 * omega(n) ** 2           # m/s²
    nm = nominal(c, law)
    an = nm['s2'] * 1e-3 * omega(n) ** 2
    sig = contact_stress(c, nm, an + ae)
    return dict(size=size, shape=shape, pv=pv, ae=ae, aemax=np.max(np.abs(ae)), an=an, sig=sig)

E_STAR = 210e9 / (2 * (1 - 0.3 ** 2))   # 钢对钢的当量弹性模量

def contact_stress(c, nm, a):
    F = c['Fw'] + c['m'] * np.abs(a)                       # 沟槽凸轮：惯性力由一侧或另一侧承受，加工作载荷
    inv = 1 / (nm['rho_c'] * 1e-3) + 1 / (c['rr'] * 1e-3)
    return np.sqrt(F * E_STAR * inv / (np.pi * c['L'] * 1e-3)) / 1e6

def n_allow(c, law, e, n_ref=None):
    n_ref = n_ref or c['nmax']
    r = evaluate(c, law, e, n_ref)
    return n_ref * math.sqrt(a_limit(c) / r['aemax'])

if __name__ == '__main__':
    for key, c in CAMS.items():
        for law in LAWS:
            nm = nominal(c, law)
            print(key, law, 'a_nom@nmax=%.0f' % a_nom_peak(c, law, c['nmax']), 'alpha_max=%.1f' % np.degrees(np.abs(nm['alpha']).max()),
                  'rho_min=%.1f' % nm['rho_c'].min(), 'sig_max=%.0f' % evaluate(c, law, np.zeros(N), c['nmax'])['sig'].max())
        print('  a_lim', round(a_limit(c), 1))
    c = CAMS['looper']; law = 'mtrap'
    for label, kw in [('default', {}), ('pass2', dict(passes=2)), ('ind', dict(ht='ind')),
                      ('wheel199.8', dict(R_act=199.8, rcomp=False)), ('wheel199.8comp', dict(R_act=199.8)),
                      ('chatter24', dict(k=24, ek=2.0))]:
        e = error_curve(c, law, **kw)
        r0 = evaluate(c, law, e, 6000); r1 = evaluate(c, law, compensate(e), 6000)
        print(label, 'before size %.1f pv %.1f ae %.0f sig %.0f | after size %.1f pv %.1f ae %.0f | nallow %.0f %.0f' % (
            r0['size'], r0['pv'], r0['aemax'], r0['sig'].max(), r1['size'], r1['pv'], r1['aemax'], n_allow(c, law, e), n_allow(c, law, compensate(e))))
