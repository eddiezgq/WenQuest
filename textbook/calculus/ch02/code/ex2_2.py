"""2.2 节：同一个函数的四种表示——UR5e 肩关节 2 s 内由 0 平稳转到 90°（五次多项式，见 7.8 节）的公式、表格与插值；
算例 2.2.1 的定义域；狄利克雷函数在计算机上“画不出来”。"""
from fractions import Fraction

import numpy as np

from bookout import out

T, D = 2.0, 90.0                         # 运动时间 2 s，转角 90°


def theta(t):
    """肩关节角（度）：θ(t) = Δ (10 s³ − 15 s⁴ + 6 s⁵)，s = t/T，0 ≤ t ≤ T。"""
    s = np.clip(np.asarray(t, dtype=float) / T, 0.0, 1.0)
    return D * (10 * s**3 - 15 * s**4 + 6 * s**5)


# 控制器每 0.25 s 记一次（表格表示）
tk = np.arange(0, T + 1e-9, 0.25)
yk = theta(tk)
out(table="\n".join(f"| {t:.2f} | {y:.2f} |" for t, y in zip(tk, yk)), n_rows=tk.size)
out(th_half=float(theta(1.0)), th_q=float(theta(0.5)))

# 表格之间的值：线性插值与真值比较
t_q = 0.6
lin = float(np.interp(t_q, tk, yk))
out(t_q=t_q, interp=lin, true_q=float(theta(t_q)), interp_err=abs(lin - float(theta(t_q))))
# 最大的线性插值误差（在 0–2 s 上密集取点）
tt = np.linspace(0, T, 4001)
err = np.abs(np.interp(tt, tk, yk) - theta(tt))
out(interp_max=float(err.max()), interp_at=float(tt[err.argmax()]))

# 算例 2.2.1：f(x) = √(4 − x²) / ln(x + 1) 的定义域：(−1, 0) ∪ (0, 2]；在网格上逐点核对
xs = np.linspace(-3, 3, 6000)        # 网格不含 −1、0（numpy 在 x = −1 处会把 √3/(−∞) 算成 −0）
with np.errstate(all="ignore"):
    ok = np.isfinite(np.sqrt(4 - xs**2) / np.log(xs + 1))
pred = ((xs > -1) & (xs < 0)) | ((xs > 0) & (xs <= 2))
assert np.array_equal(ok, pred)
out(dom_checked=xs.size)

# 狄利克雷函数：浮点数全是有理数，所以“计算机里的 D(x)”处处等于 1
fs = Fraction(float(np.sqrt(2)))                     # “√2”在计算机里的精确值：分母是 2 的幂
k = fs.denominator.bit_length() - 1
assert fs.denominator == 2**k
out(dir_sqrt2=1, sqrt2_den_pow=k)
