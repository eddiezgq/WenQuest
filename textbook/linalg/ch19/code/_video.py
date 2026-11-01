"""本章共用：车间顶棚固定相机拍的一段视频（模拟数据，48×64 像素、80 帧）。以下划线开头，构建时不单独运行。

背景：地面的明暗渐变、两台机床和一条地面标线；整体照明随时间缓慢变暗，窗边一块区域的亮度随云彩起伏
（背景的秩为 2）。前景：一辆 AGV（深色矩形，带一个亮的货盘）从左向右穿过画面。每个像素再加 0.01 的随机误差。
"""
import numpy as np

H, W, NF = 48, 64, 80


def video(seed=11):
    y, x = np.mgrid[0:H, 0:W].astype(float)
    bg = 0.55 + 0.15 * x / W + 0.05 * y / H
    bg[6:18, 6:22] = 0.30                     # 机床 1
    bg[30:44, 44:60] = 0.25                   # 机床 2
    bg[22:25, :] = 0.85                       # 地面标线
    win = np.exp(-((x - 56) ** 2 + (y - 8) ** 2) / 120.0)     # 窗边
    t = np.arange(NF)
    light = 1.0 - 0.15 * t / NF
    cloud = 0.12 * np.sin(2 * np.pi * t / 37) + 0.06 * np.sin(2 * np.pi * t / 11)
    B = np.outer(bg.ravel(), light) + np.outer(win.ravel(), cloud)           # 背景：像素 × 帧，秩 2
    F = np.zeros_like(B)
    mask = np.zeros(B.shape, bool)
    for k in range(NF):
        x0 = int(round(-14 + (W + 14) * k / (NF - 1)))
        img = np.zeros((H, W))
        m = np.zeros((H, W), bool)
        xs = slice(max(x0, 0), max(min(x0 + 14, W), 0))
        m[26:36, xs] = True
        img[26:36, xs] = 0.15
        xp = slice(max(x0 + 4, 0), max(min(x0 + 10, W), 0))
        img[28:34, xp] = 0.95                                  # 货盘
        Bk = B[:, k].reshape(H, W)
        F[:, k] = np.where(m, img - Bk, 0).ravel()             # 前景 = 被遮住处“新像素 − 背景”
        mask[:, k] = m.ravel()
    rng = np.random.default_rng(seed)
    M = B + F + 0.01 * rng.standard_normal(B.shape)
    return M, B, F, mask


def pcp(M, lam=None, tol=1e-7, maxit=500):
    """主成分追踪：min ‖L‖* + λ‖E‖₁，L + E = M（正文记稀疏部分为 E，程序里的变量名为 S）（非精确增广拉格朗日法，即交替方向乘子法）。"""
    m, n = M.shape
    lam = lam or 1 / np.sqrt(max(m, n))
    normM = np.linalg.norm(M)
    Y = M / max(np.linalg.norm(M, 2), np.abs(M).max() / lam)
    mu = 1.25 / np.linalg.norm(M, 2)
    L = np.zeros_like(M)
    S = np.zeros_like(M)
    for it in range(maxit):
        U, sig, Vt = np.linalg.svd(M - S + Y / mu, full_matrices=False)
        sig = np.maximum(sig - 1 / mu, 0)                      # 奇异值收缩
        r = int(np.sum(sig > 0))
        L = (U[:, :r] * sig[:r]) @ Vt[:r]
        T = M - L + Y / mu
        S = np.sign(T) * np.maximum(np.abs(T) - lam / mu, 0)   # 软阈值
        Z = M - L - S
        Y = Y + mu * Z
        mu = min(mu * 1.5, 1e7)
        if np.linalg.norm(Z) / normM < tol:
            break
    return L, S, r, it + 1
