"""本章共用：把数写成 LaTeX 的科学记数法。以下划线开头，构建时不单独运行。"""


def sci(x, d=2):
    """3.34e+10 → 3.34\\times10^{10}；d 为小数位数。"""
    m, e = f"{x:.{d}e}".split("e")
    return rf"{m}\times10^{{{int(e)}}}"


def fix_sign(V):
    """特征向量的符号约定（符号约定第七节第 4 条）：每一列第一个绝对值最大的分量为正。"""
    import numpy as np
    V = np.array(V, dtype=float, copy=True)
    for j in range(V.shape[1]):
        a = np.abs(V[:, j]); i = int(np.argmax(a >= a.max() - 1e-9))
        if V[i, j] < 0:
            V[:, j] = -V[:, j]
    return V
