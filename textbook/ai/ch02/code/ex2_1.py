"""算例 2.1.1：梯度下降在一维二次损失上的行为。

L(w) = ½ a (w − w*)²，梯度 a (w − w*)。式 (2.1.5)：w ← w − η ∇L。
误差 e_k = w_k − w* 满足 e_{k+1} = (1 − η a) e_k（式 (2.1.6)），|1 − η a| < 1 即 0 < η < 2/a 时收敛。
"""
from bookout import out

a, w_star, w0 = 4.0, 3.0, 0.0


def run(eta, steps=60):
    w, ws = w0, [w0]
    for _ in range(steps):
        w = w - eta * a * (w - w_star)
        ws.append(w)
    return ws


etas = [0.1, 0.25, 0.45, 0.55]
res = {eta: run(eta) for eta in etas}
for eta, ws in res.items():                       # 与闭式解 e_k = (1 − ηa)^k e_0 比较
    for k, w in enumerate(ws):
        assert abs((w - w_star) - (1 - eta * a) ** k * (w0 - w_star)) < 1e-9 * (1 + abs(w))


def steps_to(eta, tol=1e-3):
    for k, w in enumerate(res[eta]):
        if abs(w - w_star) < tol:
            return k
    return None


out(a=a, eta_max=2 / a, eta_best=1 / a, r01=1 - 0.1 * a, r045=1 - 0.45 * a, r055=1 - 0.55 * a,
    k01=steps_to(0.1), k025=steps_to(0.25), k045=steps_to(0.45), w055_10=res[0.55][10], err055_10=abs(res[0.55][10] - w_star))
