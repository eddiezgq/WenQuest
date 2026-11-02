"""23.6 节：UR5e 的运动学标定。“真实”机器人的 24 个 DH 参数与名义值相差 1 mm、1 mrad 量级（_ur5e.py）；
激光跟踪仪在 N 个随机位姿下测法兰中心的位置（噪声 0.05 mm）。
(1) 列文伯格–马夸特法，每步用截断 SVD（保留 18 个奇异值）解线性化方程：残差每步的变化；
(2) 在另外 30 个位姿上验证（与真实位置比较）：标定前后的位置误差的均方根和最大值；
(3) 可辨识的参数（大臂、小臂长度 a₂、a₃ 等）的估计误差；
(4) 位姿个数 N = 10、20、50、100 与测量噪声 0.01、0.05、0.2 mm 对验证误差的影响（各取 5 组随机位姿与噪声的平均），与 σ√(18/3N) 比较；
(5) 可观测性：J 的第 18 个奇异值随位姿个数的变化。"""
import numpy as np

from _num import sci
from _ur5e import NOMINAL, TEXNAMES, fk_all, jac, measure, poses, true_params
from bookout import out

pt = true_params()


def calibrate(Q, y, rank=18, it=8):
    p = NOMINAL.copy()
    hist = [float(np.sqrt(np.mean((y - fk_all(p, Q)) ** 2)))]
    mu = 1e-3
    for _ in range(it):
        J = jac(p, Q)
        r = y - fk_all(p, Q)
        U, s, Vt = np.linalg.svd(J, full_matrices=False)
        k = rank
        f = s[:k] / (s[:k] ** 2 + mu * s[0] ** 2)                 # 列文伯格–马夸特的阻尼（对奇异值的滤波）
        dp = Vt[:k].T @ (f * (U[:, :k].T @ r))
        pn = p + dp
        rn = float(np.sqrt(np.mean((y - fk_all(pn, Q)) ** 2)))
        if rn < hist[-1]:
            p, mu = pn, mu / 10
            hist.append(rn)
        else:
            mu *= 10
            hist.append(hist[-1])
    return p, hist


Q = poses(50)
y = measure(pt, Q)
p_est, hist = calibrate(Q, y)
out(hist=", ".join(f"{1000 * h:.4f}" for h in hist[:5]))
Qv = poses(30, seed=23064)
yv = fk_all(pt, Qv)                                  # 验证用真实位置（相当于用精度高得多的测量）
ev = lambda p: (float(np.sqrt(np.mean((fk_all(p, Qv) - yv) ** 2)) * 1000),
                float(np.max(np.linalg.norm((fk_all(p, Qv) - yv).reshape(-1, 3), axis=1)) * 1000))
b_rms, b_max = ev(NOMINAL)
a_rms, a_max = ev(p_est)
out(v_before=b_rms, v_before_max=b_max, v_after=a_rms, v_after_max=a_max)
# 可辨识参数的估计误差（只看大臂、小臂长度和第 1 关节高度）
for i in (12 + 1, 12 + 2, 6 + 0):
    out(**{f"par_{i}": TEXNAMES[i], f"par_{i}_dev": float((pt[i] - NOMINAL[i]) * 1000), f"par_{i}_err": float((p_est[i] - pt[i]) * 1000)})
# (4) 位姿个数与噪声：每种情形取 5 组不同的位姿与噪声，验证误差与 σ₁₈ 取平均
TRIALS = 5
for N in (10, 20, 50, 100):
    vs, ss = [], []
    for tr in range(TRIALS):
        Qn = poses(N, seed=23070 + N + 1000 * tr)
        yn = measure(pt, Qn, seed=23080 + N + 1000 * tr)
        pn, _ = calibrate(Qn, yn)
        vs.append(ev(pn)[0])
        ss.append(np.linalg.svd(jac(NOMINAL, Qn), compute_uv=False)[17])
    out(**{f"N{N}_v": float(np.mean(vs)), f"N{N}_s18": float(np.mean(ss)), f"N{N}_ref": float(0.05 * np.sqrt(18 / (3 * N)))})
for sig in (1e-5, 5e-5, 2e-4):
    vs = []
    for tr in range(TRIALS):
        Qn = poses(50, seed=23090 + 1000 * tr)
        vs.append(ev(calibrate(Qn, measure(pt, Qn, sigma=sig, seed=23091 + 1000 * tr))[0])[0])
    out(**{f"sig{int(sig * 1e6)}_v": float(np.mean(vs)), f"sig{int(sig * 1e6)}_ref": float(sig * 1000 * np.sqrt(18 / 150))})
