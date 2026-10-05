"""第 4 章共用：把导线切成小段的 RC 网络，求 Elmore 延时和阶跃响应（数值解）。

网络用一棵树表示：节点 0 是驱动器输出，每个节点有一个父节点、一段电阻（到父节点）和一个对地电容。
驱动器是电阻 Rd 接到阶跃电源（0 → VDD）。阶跃响应用后向欧拉法解 C·dV/dt = −G·V + b。
"""
import numpy as np


class Tree:
    def __init__(self, Rd, C0):
        self.parent, self.R, self.C = [-1], [Rd], [C0]

    def add(self, parent, R, C):
        self.parent.append(parent); self.R.append(R); self.C.append(C)
        return len(self.parent) - 1

    def wire(self, start, Rtot, Ctot, n):
        """从节点 start 接出一段均匀 RC 线，切成 n 段（π 形：每段电阻 R/n，节点电容 C/n），返回末端节点。"""
        node = start
        self.C[start] += Ctot / (2 * n)
        for i in range(n):
            c = Ctot / n if i < n - 1 else Ctot / (2 * n)
            node = self.add(node, Rtot / n, c)
        return node

    def elmore(self):
        """每个节点的 Elmore 延时 Σ_k R(公共路径)·C_k。"""
        n = len(self.parent)
        down = list(self.C)                              # 每个节点下游（含自己）的总电容
        for i in range(n - 1, 0, -1):
            down[self.parent[i]] += down[i]
        t = [0.0] * n
        t[0] = self.R[0] * down[0]
        for i in range(1, n):
            t[i] = t[self.parent[i]] + self.R[i] * down[i]
        return t

    def step(self, vdd, t_end, steps=4000):
        n = len(self.parent)
        G = np.zeros((n, n))
        for i in range(1, n):
            g = 1 / self.R[i]; p = self.parent[i]
            G[i, i] += g; G[p, p] += g; G[i, p] -= g; G[p, i] -= g
        G[0, 0] += 1 / self.R[0]
        b = np.zeros(n); b[0] = vdd / self.R[0]
        C = np.diag(self.C)
        dt = t_end / steps
        A = C / dt + G
        Ainv = np.linalg.inv(A)
        v = np.zeros(n)
        out = [v.copy()]
        for _ in range(steps):
            v = Ainv @ (C / dt @ v + b)
            out.append(v.copy())
        return np.linspace(0, t_end, steps + 1), np.array(out)


def t50(ts, v, vdd):
    k = int(np.argmax(v >= vdd / 2))
    return ts[k - 1] + (ts[k] - ts[k - 1]) * (vdd / 2 - v[k - 1]) / (v[k] - v[k - 1])
