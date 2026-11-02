"""21.3 节：常系数线性方程组。几个 2×2 系数矩阵的迹、行列式、特征值与平衡点类型；
x′ = Ax 的解 e^{At}x0 与特征向量展开、数值解的比较；双节点热模型的两个时间常数与模态。"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from bookout import T, out

mats = [("[[-2, 0], [0, -0.5]]", np.array([[-2.0, 0], [0, -0.5]]), T("稳定结点", "stable node")),
        ("[[1, 0], [0, -1]]", np.array([[1.0, 0], [0, -1]]), T("鞍点", "saddle")),
        ("[[-0.5, 2], [-2, -0.5]]", np.array([[-0.5, 2], [-2, -0.5]]), T("稳定焦点", "stable focus")),
        ("[[0, 1], [-4, 0]]", np.array([[0.0, 1], [-4, 0]]), T("中心", "centre")),
        ("[[0.2, 1], [-1, 0.2]]", np.array([[0.2, 1], [-1, 0.2]]), T("不稳定焦点", "unstable focus"))]
rows = []
for name, A, kind in mats:
    ev = np.linalg.eigvals(A)
    fe = lambda z: f"{z.real:.2f}" if abs(z.imag) < 1e-12 else f"{z.real:.2f} ± {abs(z.imag):.2f}i"
    evs = fe(ev[0]) if abs(ev[0].imag) > 1e-12 else f"{min(ev.real):.2f}, {max(ev.real):.2f}"
    pm = r"\begin{pmatrix}" + r"\\".join("&".join(f"{v:g}" for v in row) for row in A) + r"\end{pmatrix}"
    rows.append(f"| ${pm}$ | {np.trace(A):.2f} | {np.linalg.det(A):.2f} | {evs} | {kind} |")
out(cls_tab="\n".join(rows))

# e^{At}x0：A = [[-0.5, 2], [-2, -0.5]]，x0 = (1, 0)，t = 1
A = np.array([[-0.5, 2], [-2, -0.5]])
x0 = np.array([1.0, 0.0])
x_expm = expm(A) @ x0
x_formula = np.exp(-0.5) * np.array([np.cos(2.0), -np.sin(2.0)])
s = solve_ivp(lambda t, x: A @ x, (0, 1), x0, rtol=1e-12, atol=1e-14)
out(ex_x1=float(x_expm[0]), ex_x2=float(x_expm[1]), ex_f1=float(x_formula[0]), ex_f2=float(x_formula[1]),
    ex_err=float(np.max(np.abs(s.y[:, -1] - x_expm))))

# 双节点热模型：特征向量（模态）
R1, R2 = 4.65, 1.93
Cw, Ch = 41.5 / R2, 809.0 / R1
At = np.array([[-1 / (R2 * Cw), 1 / (R2 * Cw)], [1 / (R2 * Ch), -1 / (R2 * Ch) - 1 / (R1 * Ch)]])
ev, V = np.linalg.eig(At)
i = np.argsort(ev)
ev, V = ev[i].real, V[:, i].real
V = V / V[0]                                    # 绕组分量归一为 1
out(tm_fast=float(-1 / ev[0]), tm_slow=float(-1 / ev[1]), tm_v_fast=float(V[1, 0]), tm_v_slow=float(V[1, 1]),
    tm_tr=float(np.trace(At)), tm_det=float(np.linalg.det(At)))
