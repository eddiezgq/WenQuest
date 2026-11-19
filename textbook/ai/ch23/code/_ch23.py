"""第 23 章（自动驾驶）共用的玩具模型。

全章纪律与第 22 章同：**只用 numpy 与标准库，不依赖深度学习框架、不联网、不下载任何数据**。
本章要讲清的几件事——标定错一点点在远处放大成多少、融合为什么会被一个坏传感器拖垮、
预测的平均误差为什么不够用、规划权重调快一点点就不安全了、端到端为什么“更准却不敢用”、
加数据该怎么挑、时延花在哪里——都是**几何与控制问题**，在合成场景上能算到底，
而且每一条都有可核对的参照（真值由场景自己生成，不是另一个模型的输出）。

场景：一条双车道直道。自车在右车道跟着一辆前车走，路侧有若干静态目标（锥桶、立柱）。
相机内参、安装高度、俯仰角、噪声水平、动力学时延都是**显式假设**，写在用它们的算例里。

本章一切“安全”“准确”的结论都只在这套合成场景里成立。真车上的标定误差、传感器失效模式、
时延分布都与此不同——每个算例末尾都会写它回答不了什么。
"""
from __future__ import annotations

import math

import numpy as np

# ================================================================ 一、场景与几何（23.2 节）

SCENE = {
    "lane_w": 3.5,          # 车道宽（m）
    "veh_len": 4.8,         # 车长（m）
    "v_set": 22.0,          # 自车巡航目标车速（m/s，约 79 km/h）
    "d0": 5.0,              # 停车间距（m）
    "t_headway": 1.4,       # 期望车头时距（s）
    "t_safe": 0.6,          # 最小安全时距（s）——低于它算侵犯
    "d_safe0": 3.0,         # 最小安全间距的常数项（m）
    "a_hard": -3.0,         # 低于这个减速度算一次急刹（m/s²）
    "a_min": -6.0, "a_max": 2.5,
}

# 前视相机：内参与安装位姿都是**标称值**，真值与它差多少由算例自己给
CAM = {
    "f": 1200.0,            # 焦距（像素）
    "cx": 960.0, "cy": 540.0,
    "w": 1920, "h": 1080,
    "pitch": 0.040,         # 俯视角（rad，约 2.3°）
    "height": 1.42,         # 安装高度（m）
}


def ground_to_pixel(X, Y, pitch: float, height: float, cam: dict = CAM,
                    yaw: float = 0.0):
    """地面点（车体坐标 X 前、Y 左，单位 m）投到像素（u 右、v 下）。

    小孔模型：相机装在 (0, 0, height)，光轴向下俯 `pitch`、水平偏 `yaw`（正号向左）。
    相机三轴在车体系里的方向：
    前 = (cos p·cos ψ, cos p·sin ψ, −sin p)，下 = (−sin p·cos ψ, −sin p·sin ψ, −cos p)，
    右 = (sin ψ, −cos ψ, 0)。
    """
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    sp, cp = math.sin(pitch), math.cos(pitch)
    sy, cy_ = math.sin(yaw), math.cos(yaw)
    z_c = X * cp * cy_ + Y * cp * sy + height * sp        # 沿光轴的深度
    y_c = -X * sp * cy_ - Y * sp * sy + height * cp       # 像平面的“下”分量
    x_c = X * sy - Y * cy_
    u = cam["cx"] + cam["f"] * x_c / z_c
    v = cam["cy"] + cam["f"] * y_c / z_c
    return u, v


def pixel_to_ground(u, v, pitch: float, height: float, cam: dict = CAM,
                    yaw: float = 0.0):
    """像素反投到地面（**假设地面是平的**）。标定参数错了，这一步就错。

    射线方向 d = a·右 + b·下 + 前，其中 a=(u−cx)/f、b=(v−cy)/f；
    与 Z=0 的交点在 t = height / (b·cos p + sin p) 处。
    """
    u = np.asarray(u, dtype=float)
    v = np.asarray(v, dtype=float)
    sp, cp = math.sin(pitch), math.cos(pitch)
    sy, cy_ = math.sin(yaw), math.cos(yaw)
    a = (u - cam["cx"]) / cam["f"]
    b = (v - cam["cy"]) / cam["f"]
    denom = b * cp + sp                   # 趋于 0 就是“看到地平线”，反投会跑到无穷远
    denom = np.where(np.abs(denom) < 1e-6, np.nan, denom)
    t = height / denom
    X = t * (a * sy - b * sp * cy_ + cp * cy_)
    Y = t * (-a * cy_ - b * sp * sy + cp * sy)
    return X, Y


def horizon_v(pitch: float, cam: dict = CAM) -> float:
    """地平线所在的像素行：b·cos p + sin p = 0，即 v = cy - f·tan p。"""
    return cam["cy"] - cam["f"] * math.tan(pitch)


# ---- 鸟瞰图（BEV）网格：车体坐标 ↔ 俯视网格

BEV = {"x_min": 0.0, "x_max": 80.0, "y_min": -10.0, "y_max": 10.0, "res": 0.2}


def vehicle_to_grid(X, Y, bev: dict = BEV):
    """车体坐标（m）→ 俯视网格的行列号（行 = 纵向格，列 = 横向格）。"""
    row = np.floor((np.asarray(X, float) - bev["x_min"]) / bev["res"]).astype(int)
    col = np.floor((np.asarray(Y, float) - bev["y_min"]) / bev["res"]).astype(int)
    return row, col


def grid_to_vehicle(row, col, bev: dict = BEV):
    """俯视网格的行列号 → 格心的车体坐标（m）。"""
    X = bev["x_min"] + (np.asarray(row, float) + 0.5) * bev["res"]
    Y = bev["y_min"] + (np.asarray(col, float) + 0.5) * bev["res"]
    return X, Y


def grid_shape(bev: dict = BEV) -> tuple[int, int]:
    return (int(round((bev["x_max"] - bev["x_min"]) / bev["res"])),
            int(round((bev["y_max"] - bev["y_min"]) / bev["res"])))


def static_targets() -> np.ndarray:
    """路侧静态目标（锥桶与立柱）的真实位置，车体坐标 (X, Y)。"""
    xs = np.array([8.0, 14.0, 21.0, 30.0, 42.0, 55.0, 68.0])
    ys = np.array([-5.2, 5.4, -5.2, 5.4, -5.2, 5.4, -5.2])
    return np.column_stack([xs, ys])


# ================================================================ 二、前车与观测（23.2、23.3 节）

DT = 0.05                   # 控制周期 50 ms（20 Hz），显式假设


def lead_speed(n: int, dt: float = DT, seed: int = 0, v0: float = 22.0) -> np.ndarray:
    """前车车速（m/s）：巡航 + 几次刹车 + 慢漂移。**刹车是本章一切“最坏情形”的来源。**"""
    g = np.random.default_rng(seed + 17)
    v = np.full(n, v0)
    t = np.arange(n) * dt
    v += 1.2 * np.sin(2 * math.pi * t / 23.0 + g.uniform(0, 6.28))
    n_brake = max(1, int(n * dt / 18.0))
    for _ in range(n_brake):
        k = int(g.integers(int(0.1 * n), int(0.92 * n)))
        dur = int(g.integers(int(1.2 / dt), int(3.5 / dt)))
        depth = float(g.uniform(3.0, 8.5))
        ramp = np.sin(np.linspace(0, math.pi, dur))
        v[k:k + dur] -= depth * ramp[:len(v[k:k + dur])]
    return np.maximum(v, 1.0)


def lead_track(n: int, dt: float = DT, seed: int = 0, s0: float = 40.0,
               v0: float = 22.0) -> tuple[np.ndarray, np.ndarray]:
    """前车的位置（m）与车速（m/s）。位置由车速积出来，所以两者永远自洽。"""
    v = lead_speed(n, dt, seed, v0)
    s = s0 + np.cumsum(v) * dt
    return s, v


def radar_range(x_true: np.ndarray, rng: np.random.Generator,
                sigma: float = 0.45) -> np.ndarray:
    """毫米波式测距：噪声与距离无关，但没有横向分辨力（本章只用它的纵向值）。"""
    return x_true + sigma * rng.normal(0.0, 1.0, len(x_true))


def camera_range(x_true: np.ndarray, rng: np.random.Generator, rel_sigma: float = 0.022,
                 outlier_p: float = 0.0, outlier_m: float = 14.0,
                 stuck: tuple[int, int] | None = None) -> np.ndarray:
    """相机式测距：由目标在像平面的高度反算距离，所以**噪声随距离成比例长大**。

    `outlier_p` 是野值概率（误检到更远的目标上）；`stuck` 是一段“卡死”区间
    （跟踪器锁在上一帧的值上不动）——这两种才是真实的失效样子，不是高斯噪声。
    """
    z = x_true * (1.0 + rel_sigma * rng.normal(0.0, 1.0, len(x_true)))
    if outlier_p > 0:
        hit = rng.random(len(x_true)) < outlier_p
        z = np.where(hit, z + outlier_m, z)
    if stuck is not None:
        a, b = stuck
        z[a:b] = z[a]
    return z


# ---- 两状态卡尔曼滤波（距离、相对速度）

def kalman_fuse(meas: list[tuple[np.ndarray, float]], dt: float = DT,
                q_a: float = 1.8, x0: float | None = None,
                gate: float | None = None, max_miss: int = 20
                ) -> tuple[np.ndarray, int]:
    """匀加速模型下融合若干路测距。返回距离估计与**被门限挡掉的观测次数**。

    `meas` 是 [(观测序列, 观测标准差), ...]；`gate` 是新息门限（倍标准差），
    `None` 表示朴素融合——来什么都吃。门限就是本节要教的那一行代码。

    `max_miss` 是**防锁死的那一条**：连续 `max_miss` 帧**一路观测都没采信**，就认错——
    把协方差放大、强行采信第一路，重新张开。没有这一条，门限一紧，滤波器会把所有观测
    都当野值、自己飘走再也回不来（算例 23.2 把这个数算出来了）。注意它只在**全被挡**时
    才触发：某一路长期被挡，那是这一路坏了，正确的做法是继续不信它，不是强行采信。
    """
    n = len(meas[0][0])
    x = np.array([meas[0][0][0] if x0 is None else x0, 0.0])
    P = np.diag([4.0, 9.0])
    F = np.array([[1.0, dt], [0.0, 1.0]])
    Q = q_a ** 2 * np.array([[dt ** 4 / 4, dt ** 3 / 2], [dt ** 3 / 2, dt ** 2]])
    H = np.array([[1.0, 0.0]])
    est = np.empty(n)
    rejected = 0
    blind = 0

    def update(z: float, sigma: float) -> None:
        nonlocal x, P
        r = z - float((H @ x)[0])
        S = float((H @ P @ H.T)[0, 0]) + sigma ** 2
        K = (P @ H.T / S).ravel()
        x = x + K * r
        P = (np.eye(2) - np.outer(K, H)) @ P

    for k in range(n):
        x = F @ x
        P = F @ P @ F.T + Q
        used = False
        for z_seq, sigma in meas:
            z = float(z_seq[k])
            r = z - float((H @ x)[0])
            S = float((H @ P @ H.T)[0, 0]) + sigma ** 2
            if gate is not None and abs(r) > gate * math.sqrt(S):
                rejected += 1
                continue                       # **这一帧不信它**
            update(z, sigma)
            used = True
        blind = 0 if used else blind + 1
        if blind > max_miss:                   # 全被挡太久：认错，张开协方差重新收敛
            P = P * 16.0
            update(float(meas[0][0][k]), meas[0][1])
            blind = 0
        est[k] = x[0]
    return est, rejected


# ================================================================ 三、轨迹预测（23.3 节）

def predict_const_vel(s: np.ndarray, v: np.ndarray, horizon: int) -> np.ndarray:
    """常速预测：第 k 步往后看 `horizon` 步，就是 s + v·T。最笨的基线，先打赢它。"""
    return s + v * (horizon * DT)


def pred_features(s: np.ndarray, v: np.ndarray, dt: float = DT) -> np.ndarray:
    """可学模型的特征：当前车速、最近的加速度、再往前一拍的加速度（够它看出“在刹车”）。"""
    a = np.gradient(v, dt)
    a_prev = np.concatenate([[a[0]], a[:-1]])
    return np.column_stack([np.ones_like(v), v, a, a_prev, v * a])


def fit_ls(X: np.ndarray, y: np.ndarray, lam: float = 1e-6) -> np.ndarray:
    return np.linalg.solve(X.T @ X + lam * np.eye(X.shape[1]), X.T @ y)


# ================================================================ 四、跟车动力学与规划（23.4、23.6 节）

def cost_planner(w_gap: float, w_speed: float = 1.0, w_accel: float = 0.6,
                 scene: dict = SCENE, n_cand: int = 41, horizon_s: float = 2.0):
    """代价函数式规划器：在若干候选加速度里挑代价最低的那一个。

    三项代价：跟车距离偏离期望值、车速偏离巡航目标、舒适（加速度平方）。
    前车按常速外推（**这正是预测误差进入规划的地方**）。
    """
    cands = np.linspace(scene["a_min"], scene["a_max"], n_cand)

    def plan(gap: float, v_ego: float, v_lead: float) -> float:
        T = horizon_s
        gap_des = scene["d0"] + scene["t_headway"] * v_ego
        v_next = np.clip(v_ego + cands * T, 0.0, None)
        ds_ego = (v_ego + v_next) / 2 * T
        gap_next = gap + v_lead * T - ds_ego
        cost = (w_gap * (gap_next - gap_des) ** 2
                + w_speed * (v_next - scene["v_set"]) ** 2
                + w_accel * (cands ** 2) * T)
        cost += np.where(gap_next < scene["d_safe0"], 1e4, 0.0)   # 撞上去的那一档总是最贵
        return float(cands[int(np.argmin(cost))])

    return plan


def follow_sim(plan, n: int = 1200, dt: float = DT, seed: int = 0,
               delay_steps: int = 2, meas_sigma: float = 0.0,
               scene: dict = SCENE, lead_seed: int | None = None) -> dict:
    """把一个规划器放进跟车场景跑一遍，返回车距、车速、急刹次数与侵犯次数。

    `delay_steps` 是**感知到执行的时延**（折成多少个控制周期）：规划器看到的是若干拍以前的
    车距与车速。`meas_sigma` 是车距观测噪声——时延与噪声都会把车距抖大。
    """
    s_l, v_l = lead_track(n, dt, seed if lead_seed is None else lead_seed)
    g = np.random.default_rng(seed + 303)
    s_e, v_e = 0.0, scene["v_set"]
    gaps = np.empty(n)
    vs = np.empty(n)
    accs = np.empty(n)
    hist: list[tuple[float, float, float]] = []
    hard = 0
    viol = 0
    crash = 0
    a = 0.0
    for k in range(n):
        gap = s_l[k] - s_e - scene["veh_len"]
        obs_gap = gap + (meas_sigma * g.normal() if meas_sigma > 0 else 0.0)
        hist.append((obs_gap, v_e, float(v_l[k])))
        j = max(0, len(hist) - 1 - delay_steps)
        a = plan(*hist[j])                      # **看到的是过去，踩下去的是现在**
        a = float(np.clip(a, scene["a_min"], scene["a_max"]))
        v_e = max(0.0, v_e + a * dt)
        s_e += v_e * dt
        gaps[k], vs[k], accs[k] = gap, v_e, a
        if a < scene["a_hard"]:
            hard += 1
        if gap < scene["d_safe0"] + scene["t_safe"] * v_e:
            viol += 1
        if gap <= 0.0:
            crash += 1
    return {"gap": gaps, "v": vs, "a": accs, "v_lead": v_l,
            "gap_mean": float(np.mean(gaps)), "gap_min": float(np.min(gaps)),
            "gap_std": float(np.std(gaps)), "v_mean": float(np.mean(vs)),
            "travel_m": float(np.sum(vs) * dt), "hard": hard, "viol": viol,
            "crash": crash, "jerk_rms": float(np.sqrt(np.mean(np.gradient(accs, dt) ** 2)))}


# ================================================================ 五、车道保持：端到端与分模块（23.5 节）

LANE = {"look": 12.0,       # 前视点距离（m）
        "k_e": 0.16,         # 横向偏差增益
        "k_psi": 0.95,       # 航向偏差增益
        "k_kappa": 1.0,      # 曲率前馈增益
        "ratio": 15.0}       # 方向盘与前轮转角之比


def true_steer(e: np.ndarray, psi: np.ndarray, kappa: np.ndarray,
               lane: dict = LANE) -> np.ndarray:
    """“专家”方向盘角（deg）：横向偏差 + 航向偏差 + 曲率前馈，再乘转向比。

    这是本节的**真值**——不是另一个模型的输出，所以两种做法都能被同一把尺子量。
    """
    delta = lane["k_e"] * e + lane["k_psi"] * psi + lane["k_kappa"] * np.arctan(
        lane["look"] * kappa)
    return np.degrees(delta) * lane["ratio"] / 10.0


def lane_scene(n: int, seed: int = 0, kappa_max: float = 0.004,
               e_sigma: float = 0.35) -> dict:
    """一段车道保持数据：横向偏差 e（m）、航向偏差 psi（rad）、曲率 kappa（1/m）。"""
    g = np.random.default_rng(seed + 71)
    kappa = g.uniform(-kappa_max, kappa_max, n)
    e = g.normal(0.0, e_sigma, n)
    psi = g.normal(0.0, 0.025, n) - 0.4 * kappa * LANE["look"]
    return {"e": e, "psi": psi, "kappa": kappa}


def lane_obs(sc: dict, seed: int = 0, pix_sigma: float = 1.6,
             cam: dict = CAM) -> np.ndarray:
    """车道线在三个前视距离上的像素横坐标——这就是“原始观测”。

    车道中心线在 X 处的横向位置 Y = e + psi·X + kappa·X²/2，再按小孔模型投到像素上。
    噪声加在**像素**上，所以远处那一列折回地面时误差被放大——与算例 23.1 同一回事。
    """
    g = np.random.default_rng(seed + 907)
    cols = []
    for X in (8.0, 16.0, 28.0):
        Y = sc["e"] + sc["psi"] * X + 0.5 * sc["kappa"] * X ** 2
        u, _ = ground_to_pixel(np.full_like(Y, X), Y, cam["pitch"], cam["height"], cam)
        cols.append(u + pix_sigma * g.normal(0.0, 1.0, len(Y)))
    return np.column_stack(cols)


def perceive_lane(U: np.ndarray, pitch: float, height: float,
                  cam: dict = CAM) -> dict:
    """分模块做法的第一环：把三列像素反投到地面，再最小二乘拟出 e、psi、kappa。"""
    Xs = np.array([8.0, 16.0, 28.0])
    Ys = np.empty_like(U)
    for j, X in enumerate(Xs):
        _, v_pix = ground_to_pixel(np.full(len(U), X), np.zeros(len(U)), pitch, height, cam)
        Xg, Yg = pixel_to_ground(U[:, j], v_pix, pitch, height, cam)
        Ys[:, j] = Yg
    A = np.column_stack([np.ones_like(Xs), Xs, 0.5 * Xs ** 2])
    coef = np.linalg.lstsq(A, Ys.T, rcond=None)[0]
    return {"e": coef[0], "psi": coef[1], "kappa": coef[2]}


def poly_features(U: np.ndarray) -> np.ndarray:
    """端到端模型的特征：三列像素的一次项与二次项（够它把噪声的相关性都吃掉）。"""
    u = (U - CAM["cx"]) / 100.0
    cols = [np.ones(len(u))]
    cols += [u[:, j] for j in range(u.shape[1])]
    for i in range(u.shape[1]):
        for j in range(i, u.shape[1]):
            cols.append(u[:, i] * u[:, j])
    return np.column_stack(cols)


# ================================================================ 六、数据闭环（23.6 节）

def pool_scene(n: int, seed: int = 0, easy_frac: float = 0.93) -> dict:
    """候选数据池：绝大多数是重复的直道好天气，少数才是弯道、大偏差的难例。

    这是数据闭环真正的样子——**路上跑出来的数据，绝大部分是你已经会的那一种**。
    """
    g = np.random.default_rng(seed + 1301)
    n_easy = int(n * easy_frac)
    easy = lane_scene(n_easy, seed=seed, kappa_max=0.0004, e_sigma=0.10)
    hard = lane_scene(n - n_easy, seed=seed + 5, kappa_max=0.009, e_sigma=1.10)
    sc = {k: np.concatenate([easy[k], hard[k]]) for k in ("e", "psi", "kappa")}
    sc["is_hard"] = np.concatenate([np.zeros(n_easy, bool), np.ones(n - n_easy, bool)])
    idx = g.permutation(n)
    return {k: v[idx] for k, v in sc.items()}


def leverage(X_pool: np.ndarray, X_tr: np.ndarray, lam: float = 1e-3) -> np.ndarray:
    """每个候选样本的“杠杆值” xᵀ(XᵀX+λI)⁻¹x：模型对它越没把握，这个数越大。

    这是本节的“不确定性”——不需要贝叶斯，不需要集成，线性模型自己就给得出。
    """
    A = np.linalg.inv(X_tr.T @ X_tr + lam * np.eye(X_tr.shape[1]))
    return np.einsum("ij,jk,ik->i", X_pool, A, X_pool)


# ================================================================ 七、时延预算（23.7 节）

def latency_to_steps(ms: float, dt: float = DT) -> int:
    """时延（ms）折成多少个控制周期：不足一个周期也要占一个（**向上取整**）。"""
    return int(math.ceil(ms / 1000.0 / dt))
