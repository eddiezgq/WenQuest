"""算例 2.5.1、程序 2.5.1：一个最小的反向模式自动微分引擎，与手算的反向传播和有限差分比较。

计算图：z = w·x + b，p = σ(z)，L = (p − y)²。
每个节点记录它的值、它由哪些节点经什么运算得到，以及“局部导数”；反向时按拓扑序的逆序，把上游梯度乘以局部导数
累加到输入节点上（式 (2.5.2)）。
"""
import math

from bookout import out


class Value:
    """标量节点：data 是值，grad 是 ∂L/∂(本节点)，_back 把本节点的 grad 传给输入节点。"""

    def __init__(self, data, parents=(), op=""):
        self.data, self.grad = float(data), 0.0
        self._parents, self._op = parents, op
        self._back = lambda: None

    def __add__(self, o):
        o = o if isinstance(o, Value) else Value(o)
        r = Value(self.data + o.data, (self, o), "+")

        def back():
            self.grad += r.grad
            o.grad += r.grad
        r._back = back
        return r

    def __mul__(self, o):
        o = o if isinstance(o, Value) else Value(o)
        r = Value(self.data * o.data, (self, o), "×")

        def back():
            self.grad += o.data * r.grad
            o.grad += self.data * r.grad
        r._back = back
        return r

    def __sub__(self, o):
        return self + (o * -1 if isinstance(o, Value) else Value(-o))

    def sigmoid(self):
        s = 1 / (1 + math.exp(-self.data))
        r = Value(s, (self,), "σ")

        def back():
            self.grad += s * (1 - s) * r.grad
        r._back = back
        return r

    def square(self):
        r = Value(self.data ** 2, (self,), "²")

        def back():
            self.grad += 2 * self.data * r.grad
        r._back = back
        return r

    def backward(self):
        order, seen = [], set()

        def visit(v):                       # 拓扑排序：先访问输入，再记录自己
            if id(v) not in seen:
                seen.add(id(v))
                for p in v._parents:
                    visit(p)
                order.append(v)
        visit(self)
        self.grad = 1.0
        for v in reversed(order):
            v._back()
        return order


def forward(x, w, b, y):
    z = w * x + b
    p = z.sigmoid()
    return z, p, (p - y).square()


xv, wv, bv, yv = 1.5, 0.8, -0.3, 1.0
x, w, b = Value(xv), Value(wv), Value(bv)
z, p, L = forward(x, w, b, yv)
order = L.backward()

# 手算（式 (2.5.1)）
z_ = wv * xv + bv
p_ = 1 / (1 + math.exp(-z_))
dL_dp = 2 * (p_ - yv)
dp_dz = p_ * (1 - p_)
dL_dz = dL_dp * dp_dz
dL_dw, dL_db, dL_dx = dL_dz * xv, dL_dz, dL_dz * wv
assert abs(w.grad - dL_dw) < 1e-12 and abs(b.grad - dL_db) < 1e-12 and abs(x.grad - dL_dx) < 1e-12


def Lnum(wv_, bv_):
    s = 1 / (1 + math.exp(-(wv_ * xv + bv_)))
    return (s - yv) ** 2


eps = 1e-6
fd_w = (Lnum(wv + eps, bv) - Lnum(wv - eps, bv)) / (2 * eps)
fd_b = (Lnum(wv, bv + eps) - Lnum(wv, bv - eps)) / (2 * eps)
assert abs(fd_w - dL_dw) < 1e-8 and abs(fd_b - dL_db) < 1e-8

# 梯度消失：sigmoid 的导数至多 1/4，连乘 L 层
vanish10 = 0.25 ** 10
vanish30 = 0.25 ** 30

out(x=xv, w=wv, b=bv, y=yv, z=z_, p=p_, L=L.data, dL_dp=dL_dp, dp_dz=dp_dz, dL_dz=dL_dz, dL_dw=dL_dw, dL_db=dL_db,
    dL_dx=dL_dx, fd_w=fd_w, fd_err=abs(fd_w - dL_dw), n_nodes=len(order), vanish10=vanish10, vanish30=vanish30)
