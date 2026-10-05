"""本章 8.6 节用的最小自动微分：前向模式的对偶数 Dual，反向模式的 Var（记录计算图，反向传播）。以下划线开头，构建时不单独运行。"""
import math


class Dual:
    """a + b·ε，ε² = 0：a 是函数值，b 是导数值。"""

    def __init__(self, a, b=0.0):
        self.a, self.b = a, b

    def __add__(self, o):
        o = o if isinstance(o, Dual) else Dual(o)
        return Dual(self.a + o.a, self.b + o.b)

    __radd__ = __add__

    def __sub__(self, o):
        o = o if isinstance(o, Dual) else Dual(o)
        return Dual(self.a - o.a, self.b - o.b)

    def __rsub__(self, o):
        return Dual(o) - self

    def __mul__(self, o):
        o = o if isinstance(o, Dual) else Dual(o)
        return Dual(self.a * o.a, self.a * o.b + self.b * o.a)

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = o if isinstance(o, Dual) else Dual(o)
        return Dual(self.a / o.a, (self.b * o.a - self.a * o.b) / (o.a * o.a))

    def __rtruediv__(self, o):
        return Dual(o) / self


def dsin(x):
    return Dual(math.sin(x.a), math.cos(x.a) * x.b)


def dcos(x):
    return Dual(math.cos(x.a), -math.sin(x.a) * x.b)


def dsqrt(x):
    s = math.sqrt(x.a)
    return Dual(s, x.b / (2 * s))


class Var:
    """反向模式：每个节点记住它的父节点与局部导数；backward() 从输出往回累加 ∂输出/∂节点。"""
    count = 0

    def __init__(self, v, parents=()):
        self.v, self.parents, self.g = v, parents, 0.0
        Var.count += 1

    def __add__(self, o):
        o = o if isinstance(o, Var) else Var(o)
        return Var(self.v + o.v, ((self, 1.0), (o, 1.0)))

    __radd__ = __add__

    def __sub__(self, o):
        o = o if isinstance(o, Var) else Var(o)
        return Var(self.v - o.v, ((self, 1.0), (o, -1.0)))

    def __mul__(self, o):
        o = o if isinstance(o, Var) else Var(o)
        return Var(self.v * o.v, ((self, o.v), (o, self.v)))

    __rmul__ = __mul__

    def backward(self):
        order, seen = [], set()

        def topo(n):
            if id(n) not in seen:
                seen.add(id(n))
                for p, _ in n.parents:
                    topo(p)
                order.append(n)
        topo(self)
        self.g = 1.0
        for n in reversed(order):
            for p, d in n.parents:
                p.g += d * n.g


def vsin(x):
    return Var(math.sin(x.v), ((x, math.cos(x.v)),))


def vcos(x):
    return Var(math.cos(x.v), ((x, -math.sin(x.v)),))
