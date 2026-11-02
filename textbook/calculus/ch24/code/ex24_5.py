"""24.5 节：欧拉公式。
(1) e^{iπ} + 1 的数值；e^{iθ} 的级数在 θ = π 的部分和；cosh x = cos(ix)；
(2) 差速驱动机器人的里程计：航向用单位复数 z = e^{iθ} 表示，每步乘以 e^{iωΔt}；与“欧拉法更新 z”（|z| 漂移）
    及按圆弧精确积分比较 60 s 后的位置误差；
(3) 复步长求导（8.5 节）：f(x + ih) 的虚部除以 h。"""
import cmath
import math

from bookout import out

out(e_ipi_re=(cmath.exp(1j * math.pi) + 1).real, e_ipi_im=(cmath.exp(1j * math.pi) + 1).imag)
th, n, S, t = math.pi, 0, 0j, 1 + 0j
while abs(S - (-1)) > 1e-12:
    S += t
    n += 1
    t *= 1j * th / n
out(eu_pi_terms=n, cosh_check=abs(math.cosh(1.3) - cmath.cos(1.3j).real))
# (2) 里程计：v = 0.5 m/s，ω = 0.5 rad/s，Δt = 10 ms，60 s；准确轨迹是半径 1 m 的圆
v, w, dt, Tt = 0.5, 0.5, 0.01, 60.0
N = round(Tt / dt)
exact = v / (1j * w) * (cmath.exp(1j * w * Tt) - 1)          # 从原点、航向 0 出发
res = {}
# a. 欧拉法更新航向：z ← z + iωΔt·z，位置 p ← p + vΔt·z
z, p = 1 + 0j, 0j
for _ in range(N):
    p += v * dt * z
    z += 1j * w * dt * z
res["eu"] = (abs(p - exact), abs(z))
# b. 乘单位复数：z ← z·e^{iωΔt}，位置仍用 p ← p + vΔt·z
z, p = 1 + 0j, 0j
r = cmath.exp(1j * w * dt)
for _ in range(N):
    p += v * dt * z
    z *= r
res["rot"] = (abs(p - exact), abs(z))
# c. 按圆弧精确积分一步：p ← p + v (e^{iωΔt} − 1)/(iω) · z
z, p = 1 + 0j, 0j
arc = v * (r - 1) / (1j * w)
for _ in range(N):
    p += arc * z
    z *= r
res["arc"] = (abs(p - exact), abs(z))
for k, (e, m) in res.items():
    out(**{f"od_{k}_err": e, f"od_{k}_mod": m})
out(od_eu_mod_formula=(1 + (w * dt) ** 2) ** (N / 2))
# (3) 复步长求导
f = lambda x: cmath.exp(x) * cmath.sin(x)
x0 = 1.5
d_exact = math.exp(x0) * (math.sin(x0) + math.cos(x0))
out(cs_err=abs((f(x0 + 1e-20j)).imag / 1e-20 - d_exact) / abs(d_exact),
    fd_err=min(abs((f(x0 + h).real - f(x0 - h).real) / (2 * h) - d_exact) / abs(d_exact) for h in [10.0 ** -k for k in range(2, 12)]))
