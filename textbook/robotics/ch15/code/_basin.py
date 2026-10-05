"""15.5 节共用：UR5e 初值平面上的吸引域（成批迭代）。ex15_5.py 和 fig15_5.py 都用它。以下划线开头，构建时不单独运行。

初值平面：θ = (θ₁, θ₂*, θ₃, θ₄*, θ₅*, θ₆*)，θ₁、θ₃ 各在 [−180°, 180°) 内取 n 个值，其余四个关节取 θ* 的值，
所以平面经过 θ* 本身（θ₁ = 30°、θ₃ = 90°）。目标位姿同算例 15.1.2。四种做法：
  "nr"    牛顿-拉夫森（式 (15.1.8)），至多 60 次；
  "step"  限步长的牛顿-拉夫森：每步各关节转角不超过 STEP（式 (15.5.3)）；
  "lm"    按增益比调整阻尼的 LM 法（15.3.4 节），加权 L_c = 0.1 m；
  "cont"  延拓法（式 (15.5.4)）：目标从起点的位姿沿 T₀ e^{s[V₀]} 分 NC 段移到 T_d，每段用牛顿-拉夫森法从上一段的解出发。
"""
import numpy as np

from _nik import TH_STAR, _inv_b, _log_b, ur_batch, ur_err_batch, ur_labels, ur_solution_index, ur_table, ur_target, wrap

STEP = 0.5              # rad
NC = 10
TOL = 1e-10
LC = 0.1
WV = np.array([1, 1, 1, 1 / LC, 1 / LC, 1 / LC])


def grid(n):
    a = np.radians(np.linspace(-180, 180, n, endpoint=False))
    A1, A3 = np.meshgrid(a, a)                       # 行：θ₃，列：θ₁
    th = np.tile(TH_STAR, (n * n, 1))
    th[:, 0], th[:, 2] = A1.ravel(), A3.ravel()
    return a, th


def _conv(V):
    return (np.linalg.norm(V[:, :3], axis=1) < TOL) & (np.linalg.norm(V[:, 3:], axis=1) < TOL)


def newton(th, Td, iters=60, step=None, tol_mask=None):
    """成批的牛顿-拉夫森；step 不为 None 时限步长。返回 (θ, 是否收敛, 迭代次数)。"""
    th = th.copy()
    B = len(th)
    done = np.zeros(B, bool)
    dead = np.zeros(B, bool)
    its = np.full(B, iters)
    for k in range(iters + 1):
        V, J = ur_err_batch(th, Td)
        c = _conv(V) & ~dead
        newly = c & ~done
        its[newly] = k
        done |= c
        act = ~done & ~dead
        if not act.any() or k == iters:
            break
        Ja = J[act]
        ok = np.abs(np.linalg.det(Ja)) > 1e-14
        idx = np.where(act)[0]
        dead[idx[~ok]] = True
        idx = idx[ok]
        d = np.linalg.solve(J[idx], V[idx][:, :, None])[:, :, 0]
        if step is not None:
            m = np.abs(d).max(axis=1)
            sc = np.minimum(1.0, step / np.maximum(m, 1e-300))
            d *= sc[:, None]
        bad = ~np.isfinite(d).all(axis=1) | (np.abs(d).max(axis=1) > 1e3)
        dead[idx[bad]] = True
        th[idx[~bad]] += d[~bad]
    return th, done, its


def lm(th, Td, iters=200, tau=1e-3):
    """成批的 LM 法（增益比调整阻尼 μ = λ²，8.5.4 节）。残差 r = −W V_b，W = diag(1, 1, 1, 1/L_c, 1/L_c, 1/L_c)。"""
    th = th.copy()
    B = len(th)
    V, J = ur_err_batch(th, Td)
    F = 0.5 * np.sum((WV * V) ** 2, axis=1)
    mu = None
    nu = np.full(B, 2.0)
    done = _conv(V)
    its = np.where(done, 0, iters)
    for k in range(1, iters + 1):
        act = ~done
        if not act.any():
            break
        Jw = WV[None, :, None] * J
        A = np.transpose(Jw, (0, 2, 1)) @ Jw
        g = -np.einsum("bji,bj->bi", Jw, WV * V)
        if mu is None:
            mu = tau * np.max(np.diagonal(A, axis1=1, axis2=2), axis=1)
        d = -np.linalg.solve(A + mu[:, None, None] * np.eye(6), g[:, :, None])[:, :, 0]
        pred = 0.5 * np.einsum("bi,bi->b", d, mu[:, None] * d - g)
        thn = th + d
        Vn, Jn = ur_err_batch(thn, Td)
        Fn = 0.5 * np.sum((WV * Vn) ** 2, axis=1)
        rho = np.where(pred > 0, (F - Fn) / np.maximum(pred, 1e-300), -1.0)
        acc = act & (rho > 0)
        rej = act & ~acc
        mu = np.where(acc, mu * np.maximum(1 / 3, 1 - (2 * rho - 1) ** 3), mu)
        nu = np.where(acc, 2.0, nu)
        mu = np.where(rej, mu * nu, mu)
        nu = np.where(rej, nu * 2, nu)
        th[acc], V[acc], J[acc], F[acc] = thn[acc], Vn[acc], Jn[acc], Fn[acc]
        c = _conv(V) & ~done
        its[c] = k
        done |= c
        mu = np.minimum(mu, 1e12)
    return th, done, its


def continuation(th, Td, nc=NC, inner=8, final=40):
    """成批的延拓法：第 j 段的目标 T₀ e^{(j/nc)[V₀]}，V₀ = log(T₀⁻¹T_d)；中间各段至多 inner 次牛顿迭代，最后一段至多 final 次。"""
    T0, _ = ur_batch(th)
    V0 = _log_b(_inv_b(T0) @ Td)
    cur = th.copy()
    alive = np.ones(len(th), bool)
    total = np.zeros(len(th), int)
    for j in range(1, nc + 1):
        s = j / nc
        Tj = np.array([T @ _exp6v(s * v) for T, v in zip(T0, V0)])
        it = final if j == nc else inner
        new, ok, k = newton(cur, Tj, iters=it)
        total += k
        if j < nc:
            Vj, _ = ur_err_batch(new, Tj)
            ok = np.linalg.norm(Vj, axis=1) < 1e-6
        alive &= ok
        cur = new
    return cur, alive, total


def _exp6v(V):
    from _nik import exp_twist
    return exp_twist(V)


def classify(th, ok, table):
    """每个收敛的终点在表 14.5.1 中的编号（1–8）；不收敛记 0。"""
    idx = np.zeros(len(th), int)
    for i in np.where(ok)[0]:
        idx[i] = ur_solution_index(th[i], table, 1e-6)
    return idx


def run_all(n):
    """四种做法在 n × n 个初值上的结果：{名称: (编号数组 n×n, 收敛标志, 迭代次数)}，以及初值。"""
    Td = ur_target()
    table = ur_table()
    a, th0 = grid(n)
    res = {}
    for name in ("nr", "step", "lm", "cont"):
        if name == "nr":
            th, ok, its = newton(th0, Td)
        elif name == "step":
            th, ok, its = newton(th0, Td, iters=200, step=STEP)
        elif name == "lm":
            th, ok, its = lm(th0, Td)
        else:
            th, ok, its = continuation(th0, Td)
        res[name] = (classify(th, ok, table).reshape(n, n), ok.reshape(n, n), its.reshape(n, n))
    return a, th0, res
