"""13.6 节：复特征值与旋转。
旋转–伸缩矩阵 C = [[a, −b], [b, a]] 的特征值 a ± bi = r e^{±iθ}：乘以 C 就是转 θ、伸缩 r 倍。
实矩阵的复特征值成对共轭出现；特征向量 v = u + iw 时，A 在基 (u, −w) 下就是旋转–伸缩：A = X C X⁻¹，X = [u, −w]。
机器人：13.5 节的采样 PD 控制（K_p = 100，K_d = 10）特征值 0.75 ± 0.433i = 0.866 e^{±i30°}：每步转 30°、缩小到 0.866 倍，
状态在相平面上沿螺线收敛，每 12 步振荡一周（0.6 s）。
旋转矩阵 R 的复特征向量：实部与虚部张成垂直于转轴的平面。"""
import numpy as np

from _num import sci
from bookout import out, tex, vec

T, kp, kd = 0.05, 100.0, 10.0
A = np.array([[1, T], [-kp * T, 1 - kd * T]])
w, V = np.linalg.eig(A)
k = int(np.argmax(w.imag)); lam = w[k]; v = V[:, k]
v = v / v[0]                                  # 第一个分量取 1
u, ww = v.real, v.imag
X = np.column_stack([u, -ww])                 # 取 v = u + iw，A[u, −w] = [u, −w] C
C = np.linalg.solve(X, A @ X)
r, th = abs(lam), np.degrees(np.angle(lam))
out(A=r"\begin{pmatrix} 1 & 0.05 \\ -5 & 0.5 \end{pmatrix}", Achk=float(np.abs(A - [[1, 0.05], [-5, 0.5]]).max()), lam=f"{lam.real:.3f} + {lam.imag:.3f}\\mathrm i", r=float(r), th=float(th), period=float(360 / th), periodT=float(360 / th * T),
    v=f"(1,\\ {v[1].real:.3f} {'+' if v[1].imag > 0 else '-'} {abs(v[1].imag):.3f}\\mathrm i)^{{\\mathsf T}}", u=vec(u, 3), w=vec(-ww, 3),
    C=tex(C, 3), Cchk=sci(float(np.abs(C - np.array([[lam.real, -lam.imag], [lam.imag, lam.real]])).max()) + 1e-30, 0))
x = np.array([1.0, 0]); pts = [x]
for _ in range(36):
    x = A @ x; pts.append(x)
pts = np.array(pts)
out(x12=vec(pts[12], 4), x12a=float(pts[12][0]), r12=float(r ** 12), sign_changes=int(np.sum(np.diff(np.sign(pts[:25, 0])) != 0)))
# 三维旋转的复特征向量
R = np.array([[0.0, 0, 1], [1, 0, 0], [0, 1, 0]])
wR, VR = np.linalg.eig(R)
k = int(np.argmax(wR.imag)); z = VR[:, k] / VR[0, k]
a, b = z.real, z.imag
def cfmt(t):
    re, im = round(t.real, 9) + 0.0, round(t.imag, 9) + 0.0
    sre = "1" if abs(re - 1) < 1e-9 else f"{re:.3f}"
    return sre if abs(im) < 1e-9 else f"{sre} {'+' if im > 0 else '-'} {abs(im):.3f}\\mathrm i"
out(zR=",\\ ".join(cfmt(t) for t in z), a_dot=sci(abs(float(a @ np.ones(3))) + 1e-30, 0), b_dot=sci(abs(float(b @ np.ones(3))) + 1e-30, 0),
    ab=sci(abs(float(a @ b)) + 1e-30, 0), na=float(np.linalg.norm(a)), nb=float(np.linalg.norm(b)))
