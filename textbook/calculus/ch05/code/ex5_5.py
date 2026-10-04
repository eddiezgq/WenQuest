"""5.5 节：二分法——关节阶跃响应首次到达 95% 的时刻 t₉₅；步数的事先估计；
浮点数下区间缩不到零；三种失效：不变号、多个根、间断点。"""
import math

from bookout import out

zeta, wn = 0.6, 10.0                     # 阻尼比、固有频率 / (rad/s)
wd = wn * math.sqrt(1 - zeta * zeta)
q = lambda t: 1 - math.exp(-zeta * wn * t) * (math.cos(wd * t) + zeta / math.sqrt(1 - zeta * zeta) * math.sin(wd * t))
tp = math.pi / wd                        # 峰值时刻，在 [0, tp] 上 q 单调递增
f = lambda t: q(t) - 0.95
out(zeta=zeta, wn=wn, tp=tp, overshoot=(q(tp) - 1) * 100, f0=f(0.0), ftp=f(tp))


def bisect(g, a, b, tol=0.0, nmax=200, log=None):
    fa = g(a)
    n = 0
    while n < nmax:
        m = (a + b) / 2
        if m in (a, b) or b - a <= tol:          # 浮点数下再也分不开，或已达到容差
            break
        fm = g(m)
        if log is not None:
            log.append((n + 1, a, b, m, fm))
        if (fm > 0) == (fa > 0):
            a, fa = m, fm
        else:
            b = m
        n += 1
    return (a + b) / 2, n, b - a


log = []
t95, n6, w6 = bisect(f, 0.0, tp, tol=1e-6, log=log)
out(t95=t95, n6=n6, n6_pred=math.ceil(math.log2(tp / 1e-6)), w6=w6)
out(bis_tab="\n".join(f"| {k} | {a:.6f} | {b:.6f} | {m:.6f} | {fm:+.2e} |" for k, a, b, m, fm in log[:8]))
_, nfull, wfull = bisect(f, 0.0, tp)
out(n_full=nfull, w_full=wfull, ulp_t95=math.ulp(t95))

# 失效 1：(x − 1)² 在 [0, 3] 两端同号，二分法无从下手
out(sq0=(0 - 1) ** 2, sq3=(3 - 1) ** 2)
# 失效 2：x³ − x 在 [−2, 1.5] 上有三个根，二分法只找到其中一个
c, _, _ = bisect(lambda x: x ** 3 - x, -2.0, 1.5, tol=1e-12)
out(cubic_root=c)
# 失效 3：tan x 在 [1, 2] 两端异号，但区间里没有根，二分法收敛到间断点 π/2
c, _, _ = bisect(math.tan, 1.0, 2.0, tol=1e-12)
out(tan_c=c, tan_pi2=math.pi / 2, tan_val=math.tan(c))
