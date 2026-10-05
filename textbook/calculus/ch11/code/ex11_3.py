"""11.3 节：运动规划——关节在速度、加速度、加加速度限制下的最短时间运动：梯形速度曲线（含三角形情形）与 S 形速度曲线；
与满足同样限制的五次多项式比较；三个关节的同步；AGV 沿换道路径的速度规划（前向、后向两遍扫描）。"""
import math

from _motion import scurve_plan
from _path import A_LAT, curvature, lane
from bookout import out

V, A, J = 180.0, 400.0, 4000.0          # °/s（UR5e 手册），°/s²、°/s³（教学用的假设值）


def trap_T(D, V, A):
    if D >= V * V / A:
        return D / V + V / A, V
    return 2 * math.sqrt(D / A), math.sqrt(A * D)


def scurve_T(D, V, A, J):
    """对称 S 形曲线的最短时间（达不到 V 或 A 时自动降低，见 _motion.scurve_plan）。"""
    Vr, Ar, tj, ta, tv = scurve_plan(D, V, A, J)
    return 2 * (2 * tj + ta) + tv, Vr


rows = []
for D in (10.0, 30.0, 90.0, 180.0):
    T, vp = trap_T(D, V, A)
    kind = "梯形" if D >= V * V / A else "三角形"
    rows.append(f"| {D:.0f} | {kind} | {T:.3f} | {vp:.1f} |")
out(V=V, A=A, J=J, D_crit=V * V / A, trap_tab="\n".join(rows))
D = 90.0
Tt, _ = trap_T(D, V, A)
Ts, Vs = scurve_T(D, V, A, J)
D120 = 120.0
Ts120, _ = scurve_T(D120, V, A, J)
Tt120, _ = trap_T(D120, V, A)
# 五次多项式：峰值速度 15D/(8T) ≤ V，峰值加速度 10D/(√3 T²) ≤ A
Tq = max(15 * D / (8 * V), math.sqrt(10 * D / (math.sqrt(3) * A)))
out(Tt=Tt, Ts=Ts, Vs=Vs, Ts_pct=(Ts / Tt - 1) * 100, s_need=V * (V / A + A / J), Ts120=Ts120, Tt120=Tt120, Tq=Tq, q_jerk=60 * D / Tq ** 3)

# 三个关节同步：各自的最短时间，取最大者，其余关节按比例降低速度与加速度
Ds = (90.0, 45.0, 120.0)
Ti = [trap_T(d, V, A)[0] for d in Ds]
Tsync = max(Ti)
out(sync_T=", ".join(f"{t:.3f}" for t in Ti), sync_Tmax=Tsync)

# AGV：先直行 6 m，再五次多项式换道（d = 1 m、L = 4 m），再直行 6 m；限速 2 m/s，纵向加减速 0.5 m/s²，侧向 1 m/s²
VMAX, ALONG, S0 = 2.0, 0.5, 6.0
y, yp, ypp = lane("quintic", 1.0, 4.0)
yy = lambda x: 0.0 if x <= 0 else (1.0 if x >= 4 else y(x))
N = 3200
xs = [-S0 + (4 + 2 * S0) * k / N for k in range(N + 1)]
ds = [math.hypot(xs[k + 1] - xs[k], yy(xs[k + 1]) - yy(xs[k])) for k in range(N)]
kap = [curvature(yp, ypp, x) if 0 < x < 4 else 0.0 for x in xs]
vlim = [min(VMAX, math.sqrt(A_LAT / k)) if k > 1e-12 else VMAX for k in kap]
v = vlim[:]
v[0] = 0.0
for k in range(N):                       # 前向：从起点加速的能力
    v[k + 1] = min(v[k + 1], math.sqrt(v[k] ** 2 + 2 * ALONG * ds[k]))
v[N] = 0.0
for k in range(N - 1, -1, -1):           # 后向：到终点停下的能力
    v[k] = min(v[k], math.sqrt(v[k + 1] ** 2 + 2 * ALONG * ds[k]))
T_plan = sum(2 * ds[k] / (v[k] + v[k + 1]) for k in range(N))
# 对比：全程不超过换道段允许的最高车速（恒定限速 √(a/κ_max)）
vc = math.sqrt(A_LAT / max(kap))
w = [min(vc, x) for x in v]
w2 = [vc] * (N + 1)
w2[0] = 0.0
for k in range(N):
    w2[k + 1] = min(w2[k + 1], math.sqrt(w2[k] ** 2 + 2 * ALONG * ds[k]))
w2[N] = 0.0
for k in range(N - 1, -1, -1):
    w2[k] = min(w2[k], math.sqrt(w2[k + 1] ** 2 + 2 * ALONG * ds[k]))
T_const = sum(2 * ds[k] / (w2[k] + w2[k + 1]) for k in range(N))
i0, i1 = int(S0 / (4 + 2 * S0) * N), int((S0 + 4) / (4 + 2 * S0) * N)
out(agv_len=sum(ds), agv_vmin=min(v[i0:i1 + 1]), agv_vc=vc, agv_T=T_plan, agv_Tc=T_const)
