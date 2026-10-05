"""12.2 节：复向量与埃尔米特内积。
z = (1, i) 的 zᵀz = 0 而 zᴴz = 2；u = (1, i)、v = (i, 1) 在埃尔米特内积下正交；埃尔米特矩阵的特征值为实数；
复矩阵 A = (1, i)ᵀ 的 AᵀA = 0、AᴴA = 2（秩只能用 AᴴA 保持）；4 点离散傅里叶变换矩阵 F 满足 FᴴF = 4I，帕塞瓦尔等式。
机器人：伺服电机三相电流的克拉克变换（功率不变形式）是正交矩阵；合成的复数空间矢量模长不变、匀速旋转；
功率 p = v_a i_a + v_b i_b + v_c i_c = Re(v̄_s i_s)（埃尔米特内积的实部）。"""
import numpy as np

from _num import sci
from bookout import out, tex

def ctex(z):
    """复数写成 a + bi（整数或两位小数）。"""
    z = complex(z)
    a, b = round(z.real, 10), round(z.imag, 10)
    fa = lambda x: str(int(x)) if abs(x - round(x)) < 1e-9 else f"{x:.2f}"
    if b == 0:
        return fa(a)
    sb = "" if abs(abs(b) - 1) < 1e-12 else fa(abs(b))
    if a == 0:
        return ("-" if b < 0 else "") + sb + r"\mathrm i"
    return fa(a) + (" - " if b < 0 else " + ") + sb + r"\mathrm i"

def cmat(M):
    M = np.atleast_2d(M)
    return r"\begin{pmatrix} " + r" \\ ".join(" & ".join(ctex(x) for x in r) for r in M) + r" \end{pmatrix}"

z = np.array([1, 1j])
out(zTz=ctex(z @ z), zHz=ctex(np.vdot(z, z)))
u, v = np.array([1, 1j]), np.array([1j, 1])
out(uHv=ctex(np.vdot(u, v)), uTv=ctex(u @ v))
A = np.array([[2, 1 - 1j], [1 + 1j, 3]])
out(H=cmat(A), Heig=", ".join(f"{x:.0f}" for x in np.linalg.eigvalsh(A)))
B = np.array([[1], [1j]])
out(BTB=ctex((B.T @ B)[0, 0]), BHB=ctex((B.conj().T @ B)[0, 0]))
# 4 点 DFT
N = 4
w = np.exp(-2j * np.pi / N)
F = np.array([[w ** (j * k) for k in range(N)] for j in range(N)])
x = np.array([1.0, 2, 0, -1])
X = F @ x
out(F=cmat(F), FHF=cmat(F.conj().T @ F), X=r"(" + r",\ ".join(ctex(t) for t in X) + r")^{\mathsf T}", nX2=float(np.vdot(X, X).real), nx2=float(x @ x),
    fft_ok=sci(float(np.abs(X - np.fft.fft(x)).max()) + 1e-30, 0))
# 克拉克变换（功率不变）
s3 = np.sqrt(3)
C = np.sqrt(2 / 3) * np.array([[1, -0.5, -0.5], [0, s3 / 2, -s3 / 2], [1 / np.sqrt(2)] * 3])
out(CCT=sci(float(np.abs(C @ C.T - np.eye(3)).max()) + 1e-30, 0))
I0, V0, phi, f = 2.0, 24.0, np.radians(30), 50.0
t = np.linspace(0, 0.02, 9)
th = 2 * np.pi * f * t
ia = I0 * np.cos(th[:, None] - np.array([0, 2 * np.pi / 3, -2 * np.pi / 3]))
va = V0 * np.cos(th[:, None] + phi - np.array([0, 2 * np.pi / 3, -2 * np.pi / 3]))
iab, vab = ia @ C.T, va @ C.T
i_s, v_s = iab[:, 0] + 1j * iab[:, 1], vab[:, 0] + 1j * vab[:, 1]
p_abc = (va * ia).sum(1)
p_c = (np.conj(v_s) * i_s).real
out(I0=I0, V0=V0, phi_deg=30, is_mag=float(np.abs(i_s).mean()), is_mag_spread=sci(float(np.ptp(np.abs(i_s))) + 1e-30, 0), is_mag_th=float(np.sqrt(1.5) * I0),
    p_abc=float(p_abc.mean()), p_spread=sci(float(np.ptp(p_abc)) + 1e-30, 0), p_diff=sci(float(np.abs(p_abc - p_c).max()) + 1e-30, 0), p_th=float(1.5 * V0 * I0 * np.cos(phi)),
    i0=sci(float(np.abs(iab[:, 2]).max()) + 1e-30, 0))
