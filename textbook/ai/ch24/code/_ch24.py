"""第 24 章（机器人与具身智能）共用的玩具模型。

全章纪律：**不依赖深度学习框架、不装仿真器、不联网**。本章要讲清的几件事
——行为克隆的误差为什么会累积、域随机化的范围为什么有个最佳值、动作分箱的代价、
奖励塑形怎么把机器人教成“刷奖励”、抓取位姿怎么用几何打分、并行环境数换来什么——
都是**策略与评测问题**，在一台平面机械臂的玩具上能算到底，而且每一条都有可核对的参照
（专家策略给出“应该怎么走”，显式几何阈值给出“算不算成功”）。

这台机械臂是第 21 章那座减速器厂工位上的简化版：**平面二连杆 + 一个只管夹爪朝向的腕关节**，
桌面上放一个待抓的工件。几何尺寸、阈值、真机与仿真的参数差都是**显式假设**，写在下面的字典里。

**本章第一号纪律**：仿真成功率不是真机成功率。本模块因此有两套世界参数
（`SIM` 与 `REAL`），任何评测函数都要求调用者说清自己评的是哪一套；算例一律两列并排报。

抓取成功的判据用**显式几何双阈值**（位置 2 cm、姿态 0.4 rad）。这两个数**是本书的显式假设**，
取值与资料卡里 TriFinger 那篇的双阈值口径一致（`conventions/robot_facts.py` 的
`SIM2REAL_TRIFINGER`），但本章的机械臂、任务、物体都与那篇无关，**不与那篇的成功率作任何比较**。
"""
from __future__ import annotations

import math

import numpy as np

# ================================================================ 一、机械臂与任务（算例 24.1 起处处用）

ARM = {
    "q_min": np.array([-2.60, -2.50, -2.20]),   # 三个关节的下限（rad），显式假设
    "q_max": np.array([2.60, 2.50, 2.20]),      # 上限
    "v_max": np.array([1.6, 1.6, 2.2]),         # 关节最大角速度（rad/s）
    "dt": 0.05,                                 # 控制周期（s），20 Hz
    "q_home": np.array([0.55, 0.95, -0.30]),    # 收工位姿
}

# 抓取成功的显式双阈值（**本书的显式假设**，口径同 robot_facts.SIM2REAL_TRIFINGER）
GRASP_TOL = {"pos_m": 0.02, "rot_rad": 0.4}

# 两套世界参数：**仿真不是真机**，四样各差一点
SIM = {
    "l1": 0.35, "l2": 0.30,      # 连杆长度（m）
    "friction": 0.04,            # 关节摩擦：实际走到的角速度要打折扣
    "obs_noise": 0.0,            # 关节角观测噪声（rad，标准差）
    "delay": 0,                  # 执行延迟（控制周期数）
    "name": "仿真",
}
REAL = {
    "l1": 0.363, "l2": 0.288,    # 真机连杆比标称长/短一点（装配与标定误差）
    "friction": 0.11,            # 真机摩擦大得多
    "obs_noise": 0.004,          # 编码器与标定噪声
    "delay": 1,                  # 真机的指令要晚一个周期才生效
    "name": "真机",
}


def fk(q: np.ndarray, world: dict) -> tuple[float, float, float]:
    """正运动学：给关节角，算夹爪中心的位置与朝向。

    返回 (x, y, 朝向)。朝向是三个关节角之和——腕关节只管朝向，不改位置。
    """
    l1, l2 = world["l1"], world["l2"]
    x = l1 * math.cos(q[0]) + l2 * math.cos(q[0] + q[1])
    y = l1 * math.sin(q[0]) + l2 * math.sin(q[0] + q[1])
    return x, y, float(q[0] + q[1] + q[2])


def ik(pose: np.ndarray, world: dict) -> np.ndarray | None:
    """逆运动学：给目标位姿 (x, y, 朝向)，算关节角；够不到就返回 None。

    二连杆取“肘朝上”那一支；腕关节补足朝向。够不到或超出关节限位的一律返回 None——
    **“够不到”要显式返回，不许偷偷夹到边界上**，否则后面的成功率就是假的。
    """
    l1, l2 = world["l1"], world["l2"]
    x, y, th = float(pose[0]), float(pose[1]), float(pose[2])
    r2 = x * x + y * y
    c2 = (r2 - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    if not -1.0 <= c2 <= 1.0:
        return None
    q2 = math.acos(c2)                                   # 肘朝上
    q1 = math.atan2(y, x) - math.atan2(l2 * math.sin(q2), l1 + l2 * math.cos(q2))
    q3 = th - q1 - q2
    q = np.array([q1, q2, q3])
    if np.any(q < ARM["q_min"]) or np.any(q > ARM["q_max"]):
        return None
    return q


def reachable(pose: np.ndarray, world: dict) -> bool:
    """这个位姿在这套世界参数下够不够得到。"""
    return ik(pose, world) is not None


def sample_targets(n: int, seed: int = 0, world: dict = SIM) -> np.ndarray:
    """采 n 个待抓工件的位姿 (x, y, 朝向)，都落在工作空间里（两套世界参数下都够得到）。"""
    g = np.random.default_rng(seed + 20240)
    out = []
    while len(out) < n:
        r = g.uniform(0.30, 0.56)
        a = g.uniform(-0.35, 1.25)
        th = g.uniform(-0.9, 1.9)
        pose = np.array([r * math.cos(a), r * math.sin(a), th])
        if reachable(pose, SIM) and reachable(pose, REAL):
            out.append(pose)
    return np.array(out)


def sample_starts(n: int, seed: int = 0, spread: float = 0.10) -> np.ndarray:
    """采 n 个起始关节角：围着收工位姿散开，`spread` 越大散得越开。

    **演示数据与验收的起始分布可以不一样**——这正是算例 24.1 里行为克隆要栽的那个跟头。
    """
    g = np.random.default_rng(seed + 771)
    q = ARM["q_home"] + spread * g.normal(0, 1, (n, 3))
    return np.clip(q, ARM["q_min"], ARM["q_max"])


# ================================================================ 二、跑一条轨迹（算例 24.1 起处处用）

ACTION_DIM = 4              # (三个关节的角速度指令, 夹爪闭合指令)
STEPS = 60                  # 一回合最多多少步（60 步 × 0.05 s = 3 秒）


def obs_of(q: np.ndarray, pose: np.ndarray, world: dict, g) -> np.ndarray:
    """策略看到的观测：带噪声的关节角 + **量出来的夹爪位姿**（相机给的）+ 工件位姿。

    九维：(q1, q2, q3, 夹爪 x, 夹爪 y, 夹爪朝向, 工件 x, 工件 y, 工件朝向)。
    **策略看不到世界参数**——连杆到底多长、摩擦多大，它只能从观测里推。
    夹爪位姿这三维是本章的关键：只盯关节角的策略必须自己心算一套正运动学
    （于是连杆一变就错），而盯着量出来的夹爪位姿的策略可以“看着误差收”。
    域随机化那个算例（24.2）就是靠这件事起作用的。
    """
    nq = world["obs_noise"] * g.normal(0, 1, 3) if world["obs_noise"] > 0 else np.zeros(3)
    tip = np.array(fk(q, world))
    nt = world["obs_noise"] * g.normal(0, 1, 3) if world["obs_noise"] > 0 else np.zeros(3)
    return np.concatenate([q + nq, tip + nt * np.array([0.6, 0.6, 1.0]), pose])


def grasp_ok(q: np.ndarray, pose: np.ndarray, world: dict) -> tuple[bool, float, float]:
    """按显式双阈值判这一步算不算抓到：位置误差 < 2 cm **且** 姿态误差 < 0.4 rad。"""
    x, y, th = fk(q, world)
    dp = math.hypot(x - pose[0], y - pose[1])
    dth = abs(th - pose[2])
    return (dp < GRASP_TOL["pos_m"] and dth < GRASP_TOL["rot_rad"]), dp, dth


def rollout(policy, pose: np.ndarray, q0: np.ndarray, world: dict, seed: int = 0,
            steps: int = STEPS, bins: int | None = None) -> dict:
    """把一个策略放进世界里跑一回合。

    `policy(obs) -> 四维动作`；前三维是关节角速度指令（单位是 `v_max` 的倍数，截到 ±1），
    第四维 > 0.5 表示闭合夹爪。成功的定义：**夹爪闭合的那一刻正好落在双阈值里**——
    光走到位不闭合不算成功，闭合了但没到位也不算（这是本章的显式判据）。

    `bins` 不是 None 时，把动作每一维**均匀分箱**再执行（算例 24.3 用；口径参照资料卡里
    RT-1/RT-2 的“每维 256 个均匀分箱”）。`world` 的摩擦、连杆长度、观测噪声、执行延迟
    决定这是“仿真”还是“真机”。
    """
    g = np.random.default_rng(seed + 10007)
    q = np.array(q0, dtype=float)
    queue = [np.zeros(ACTION_DIM) for _ in range(world["delay"])]
    traj = np.empty((steps + 1, 3))
    tips = np.empty((steps + 1, 3))
    acts = np.empty((steps, ACTION_DIM))
    traj[0] = q
    tips[0] = fk(q, world)
    success, t_success, closed = False, -1, False
    for t in range(steps):
        a = np.asarray(policy(obs_of(q, pose, world, g)), dtype=float)
        a = np.clip(a, -1.0, 1.0)
        if bins is not None:
            a = quantize(a, bins)
        acts[t] = a
        queue.append(a)
        a_eff = queue.pop(0)                            # 执行延迟
        q = np.clip(q + (1.0 - world["friction"]) * a_eff[:3] * ARM["v_max"] * ARM["dt"],
                    ARM["q_min"], ARM["q_max"])
        traj[t + 1] = q
        tips[t + 1] = fk(q, world)
        if a_eff[3] > 0.5:                              # 夹爪闭合：这一刻定成败，回合结束
            closed = True
            ok, _, _ = grasp_ok(q, pose, world)
            success, t_success = ok, t + 1
            traj[t + 2:] = q
            tips[t + 2:] = tips[t + 1]
            acts[t + 1:] = 0.0
            break
    ok_now, dp, dth = grasp_ok(q, pose, world)
    return {"q": traj, "tip": tips, "act": acts, "success": success, "closed": closed,
            "t_success": t_success, "pos_err": dp, "rot_err": dth, "in_tol_at_end": ok_now,
            "n_steps": steps if t_success < 0 else t_success}


def quantize(a: np.ndarray, bins: int) -> np.ndarray:
    """把 [-1, 1] 的动作每一维**均匀分箱**（口径参照 RT-1/RT-2 的每维 256 个均匀分箱）。"""
    idx = np.round((a + 1.0) / 2.0 * (bins - 1))
    return idx / (bins - 1) * 2.0 - 1.0


# ================================================================ 三、专家策略（算例 24.1）

KP = 5.0                     # 专家的比例增益（显式假设）


def expert(pose: np.ndarray, world: dict):
    """专家策略：**知道真实连杆长度**（特权信息），解逆运动学后按比例往目标关节角收，
    到了双阈值里就闭合夹爪。

    这是本章的“应该怎么走”。学生策略只看得到观测，看不到世界参数——
    这正是模仿学习要跨的那道沟。
    """
    q_goal = ik(pose, world)
    if q_goal is None:                                  # 够不到：原地不动，也不闭合
        return lambda o: np.zeros(ACTION_DIM)

    def f(o):
        q = np.asarray(o[:3], dtype=float)
        a = np.clip(KP * (q_goal - q) / ARM["v_max"], -1.0, 1.0)
        ok, _, _ = grasp_ok(q, pose, world)
        return np.concatenate([a, [1.0 if ok else -1.0]])
    return f


def servo_policy(gain: float = 3.5, l1_hat: float | None = None, l2_hat: float | None = None,
                 close_at: float = 0.012, close_rot: float = 0.2, hover: float = 0.0):
    """雅可比转置伺服：盯着**量出来的**夹爪位姿往工件收，到了触发半径里就闭合夹爪。

    参数的意思：`gain` 增益；`l1_hat`、`l2_hat` 是**它自己以为的连杆长度**（算雅可比用，
    可以不等于真值）；`close_at` 是闭合夹爪的触发半径（**取 0 就是永不闭合**）；
    `hover` 是绕着工件打转的幅度（贴着目标来回转、不闭合——奖励塑形那个算例（24.4）里“刷奖励”的行为就在这里）。

    这个只有几个参数的小策略族是算例 24.4 与 24.6 搜参数用的；它不是学出来的，
    但**它能表达“刷奖励”的行为**，这正是奖励塑形那一节要看的。
    """
    l1_hat = SIM["l1"] if l1_hat is None else l1_hat
    l2_hat = SIM["l2"] if l2_hat is None else l2_hat

    def f(o):
        q = np.asarray(o[:3], dtype=float)
        tip = np.asarray(o[3:6], dtype=float)
        tgt = np.asarray(o[6:9], dtype=float)
        e = tgt[:2] - tip[:2]
        eth = float(tgt[2] - tip[2])
        s1, c1 = math.sin(q[0]), math.cos(q[0])
        s12, c12 = math.sin(q[0] + q[1]), math.cos(q[0] + q[1])
        J = np.array([[-l1_hat * s1 - l2_hat * s12, -l2_hat * s12],
                      [l1_hat * c1 + l2_hat * c12, l2_hat * c12]])
        d = float(np.linalg.norm(e))
        v = e.copy()
        if hover > 0.0 and d > 1e-9:
            v = v + hover * np.array([-e[1], e[0]]) * (math.exp(-(d / 0.03) ** 2))
        a12 = gain * (J.T @ v) / 0.1
        close = 1.0 if (close_at > 0.0 and d < close_at and abs(eth) < close_rot) else -1.0
        return np.clip(np.array([a12[0], a12[1], gain * eth, close]), -1.0, 1.0)
    return f


# ================================================================ 四、策略拟合器（算例 24.1—24.3）

def poly_features(O: np.ndarray, degree: int = 2) -> np.ndarray:
    """多项式特征：常数 + 指定阶数的全部单项式，再加几个按运动学写出来的特征。

    自己写，不引任何机器学习库。额外的那几项——关节角的正余弦、工件的极坐标半径与极角——
    是**把已知的物理结构写进特征**：运动学本来就是三角函数，逆运动学本来就按极坐标算。
    这比堆层数便宜得多，也是工程上最先该做的一步。
    """
    from itertools import combinations_with_replacement
    O = np.atleast_2d(np.asarray(O, dtype=float))
    d = O.shape[1]
    cols = [np.ones(len(O))]
    for k in range(1, max(degree, 1) + 1):
        for idx in combinations_with_replacement(range(d), k):
            col = np.ones(len(O))
            for j in idx:
                col = col * O[:, j]
            cols.append(col)
    for j in range(3):                                   # 三个关节角的正余弦
        cols += [np.sin(O[:, j]), np.cos(O[:, j])]
    if d >= 9:
        r = np.hypot(O[:, 6], O[:, 7])                   # 工件的极坐标：逆运动学按这个算
        a = np.arctan2(O[:, 7], O[:, 6])
        cols += [r, a, r * r, r * a, np.cos(a), np.sin(a),
                 np.cos(O[:, 8]), np.sin(O[:, 8]), r * np.cos(a), r * np.sin(a)]
        e = O[:, 6:9] - O[:, 3:6]                        # **任务空间误差**：工件位姿 − 量出来的夹爪位姿
        for k3 in range(3):
            cols.append(e[:, k3])
            for m in range(k3, 3):
                cols.append(e[:, k3] * e[:, m])
            for j in range(3):
                cols += [e[:, k3] * np.cos(O[:, j]), e[:, k3] * np.sin(O[:, j])]
    return np.column_stack(cols)


def fit_ls(X: np.ndarray, Y: np.ndarray, lam: float = 1e-4) -> np.ndarray:
    """最小二乘（带一点岭正则），自己解正规方程。一次把四维动作一起拟合。"""
    Y = np.atleast_2d(Y)
    if Y.shape[0] != X.shape[0]:
        Y = Y.T
    A = X.T @ X + lam * np.eye(X.shape[1])
    return np.linalg.solve(A, X.T @ Y)


def make_policy(W: np.ndarray, degree: int = 2):
    """把拟合出来的系数包成一个策略函数。"""
    def f(o):
        return (poly_features(np.asarray(o).reshape(1, -1), degree) @ W).ravel()
    return f


def collect(policy_of, poses: np.ndarray, starts: np.ndarray, world: dict,
            seed: int = 0, steps: int = STEPS) -> tuple[np.ndarray, np.ndarray]:
    """跑一批回合，把（观测，专家标注的动作）收下来。

    `policy_of(pose, world)` 给出**跑这一条用的策略**：传专家进去就是演示数据（行为克隆用的）；
    传学生进去，再用专家给标注，就是“带纠正的”（DAgger 玩具版）。
    """
    O, A = [], []
    g = np.random.default_rng(seed + 55)
    for k, (pose, q0) in enumerate(zip(poses, starts)):
        exp = expert(pose, world)
        pol = policy_of(pose, world)
        q = np.array(q0, dtype=float)
        queue = [np.zeros(ACTION_DIM) for _ in range(world["delay"])]
        for t in range(steps):
            o = obs_of(q, pose, world, g)
            O.append(o)
            A.append(exp(o))                            # **标注永远来自专家**
            a = np.clip(np.asarray(pol(o), dtype=float), -1.0, 1.0)
            queue.append(a)
            a_eff = queue.pop(0)
            q = np.clip(q + (1.0 - world["friction"]) * a_eff[:3] * ARM["v_max"] * ARM["dt"],
                        ARM["q_min"], ARM["q_max"])
            if a_eff[3] > 0.5:
                break
    return np.array(O), np.array(A)


def evaluate(policy_of, poses: np.ndarray, starts: np.ndarray, world: dict,
             seed: int = 0, bins: int | None = None) -> dict:
    """在一套世界参数上验收：成功率、试了多少次、平均位置误差、动作抖动。

    **“试了多少次”必须跟着成功率一起报**（本章口径 b）：几十次试验的成功率，
    小数点后那一位没有意义。
    """
    succ, perr, rerr, jit = [], [], [], []
    for k, (pose, q0) in enumerate(zip(poses, starts)):
        r = rollout(policy_of(pose, world), pose, q0, world, seed=seed + k, bins=bins)
        succ.append(r["success"])
        perr.append(r["pos_err"])
        rerr.append(r["rot_err"])
        n = max(r["n_steps"] - 1, 1)
        jit.append(float(np.mean(np.abs(np.diff(r["act"][:n, :3], axis=0)))) if n > 1 else 0.0)
    return {"success_pct": float(np.mean(succ)) * 100, "n_trials": len(succ),
            "pos_err": float(np.mean(perr)), "rot_err": float(np.mean(rerr)),
            "jitter": float(np.mean(jit))}


def deviation_curve(policy_of, poses: np.ndarray, starts: np.ndarray, world: dict,
                    seed: int = 0, steps: int = STEPS) -> np.ndarray:
    """误差随步数怎么累积：每一步上“学生的夹爪位置”离“专家的夹爪位置”有多远（m）。

    专家从**同一个起始状态**出发跑一条参照轨迹，两条逐步相减。这条曲线是算例 24.1 的主角。
    """
    dev = np.zeros(steps + 1)
    for k, (pose, q0) in enumerate(zip(poses, starts)):
        r_s = rollout(policy_of(pose, world), pose, q0, world, seed=seed + k, steps=steps)
        r_e = rollout(expert(pose, world), pose, q0, world, seed=seed + k, steps=steps)
        dev += np.linalg.norm(r_s["tip"][:, :2] - r_e["tip"][:, :2], axis=1)
    return dev / len(poses)


def randomized_world(base: dict, scale: float, g) -> dict:
    """域随机化：在仿真参数上按 `scale` 的相对幅度抖动摩擦、连杆长度、观测噪声、执行延迟。

    `scale = 0` 就是不随机化（只有标称仿真）；`scale` 越大，训练时见过的世界越杂。
    四样一起抖，因为真机与仿真差的从来不止一样。
    """
    w = dict(base)
    w["l1"] = base["l1"] * (1.0 + scale * g.uniform(-1, 1) * 0.10)
    w["l2"] = base["l2"] * (1.0 + scale * g.uniform(-1, 1) * 0.10)
    w["friction"] = float(np.clip(base["friction"] + scale * g.uniform(0, 1) * 0.25, 0.0, 0.9))
    w["obs_noise"] = base["obs_noise"] + scale * g.uniform(0, 1) * 0.008
    w["delay"] = int(g.random() < min(scale, 1.0) * 0.8)
    w["name"] = f"随机化 scale={scale:.2f}"
    return w


DEGREE = 3                   # 本章策略拟合统一用三次多项式特征（显式假设）


def train_policy(n_episodes: int = 160, rounds: int = 4, world_of=None, seed: int = 0,
                 degree: int = DEGREE, spread: float = 0.25) -> np.ndarray:
    """用“带纠正的”方式训一个策略（算例 24.1 证明过它比纯克隆强，后面各算例一律用它）。

    第一轮是专家演示（起始位姿集中在收工位姿附近），后面每轮**在学生自己走出的状态上
    再要专家标注**，然后把所有数据合起来重拟合。`world_of(i, g)` 给出第 i 回合在哪套世界里采
    （域随机化就是从这里进来的）；不给就全在标称仿真里采。
    """
    g = np.random.default_rng(seed + 4242)
    per = max(n_episodes // rounds, 1)
    Os: list[np.ndarray] = []
    As: list[np.ndarray] = []
    W = None
    for rnd in range(rounds):
        poses = sample_targets(per, seed=seed + 100 * rnd)
        starts = sample_starts(per, seed=seed + 100 * rnd, spread=0.05 if rnd == 0 else spread)
        for i in range(per):
            w = SIM if world_of is None else world_of(rnd * per + i, g)
            if W is None:
                pol = (lambda p, wo: expert(p, wo))
            else:
                pol = (lambda p, wo, Wc=W.copy(): make_policy(Wc, degree))
            O, A = collect(pol, poses[i:i + 1], starts[i:i + 1], w, seed=i + rnd * 97)
            Os.append(O)
            As.append(A)
        W = fit_ls(poly_features(np.vstack(Os), degree), np.vstack(As))
    return W


# ================================================================ 五、抓取位姿的几何打分（算例 24.5）

def polygon(kind: str = "L") -> np.ndarray:
    """待抓工件的平面轮廓（m）。默认是一块 L 形连接板——质心不在几何中心，这才有戏。"""
    if kind == "L":
        return np.array([[0.00, 0.00], [0.060, 0.00], [0.060, 0.022],
                         [0.024, 0.022], [0.024, 0.055], [0.00, 0.055]])
    return np.array([[0.0, 0.0], [0.07, 0.0], [0.07, 0.045], [0.0, 0.045]])


def cross2(a: np.ndarray, b: np.ndarray) -> float:
    """平面叉积（标量）：a × b。用它算“点到直线的垂距”。"""
    return float(a[0] * b[1] - a[1] * b[0])


def poly_centroid(P: np.ndarray) -> np.ndarray:
    """多边形质心（按面积算，不是顶点平均）。"""
    x, y = P[:, 0], P[:, 1]
    x2, y2 = np.roll(x, -1), np.roll(y, -1)
    cr = x * y2 - x2 * y
    A = cr.sum() / 2.0
    cx = ((x + x2) * cr).sum() / (6.0 * A)
    cy = ((y + y2) * cr).sum() / (6.0 * A)
    return np.array([cx, cy])


def grasp_line(P: np.ndarray, center: np.ndarray, angle: float) -> dict | None:
    """一个抓取位姿：夹爪沿 `angle` 方向夹在过 `center` 的那条线上。

    求这条线与轮廓的两个交点（夹爪的两个接触点），并给出接触边的外法线。
    交点不足两个就返回 None（这个位姿根本夹不到东西）。
    """
    d = np.array([math.cos(angle), math.sin(angle)])
    hits = []
    n = len(P)
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        e = b - a
        den = d[0] * e[1] - d[1] * e[0]
        if abs(den) < 1e-12:
            continue
        w = a - center
        s = (w[0] * d[1] - w[1] * d[0]) / den            # 边上的参数（0—1 之间才算真交到这条边）
        t = (w[0] * e[1] - w[1] * e[0]) / den            # 线上的参数（用来给交点排序）
        if -1e-9 <= s <= 1 + 1e-9:
            nrm = np.array([e[1], -e[0]])
            nrm = nrm / (np.linalg.norm(nrm) + 1e-12)
            hits.append((t, a + s * e, nrm))
    if len(hits) < 2:
        return None
    hits.sort(key=lambda h: h[0])
    t0, p0, n0 = hits[0]
    t1, p1, n1 = hits[-1]
    return {"p0": p0, "p1": p1, "n0": n0, "n1": n1, "width": float(np.linalg.norm(p1 - p0)),
            "angle": angle, "center": center.copy()}


GRIPPER = {"open_max_m": 0.062, "mu": 0.45}      # 夹爪最大开口与摩擦系数，显式假设


def grasp_score(P: np.ndarray, gl: dict, grip: dict = GRIPPER) -> float:
    """抓取位姿的几何打分（0—1）：三条判据相乘。

    （1）**接触点连线离质心多远**——离得越远，夹住后越容易绕质心转掉；
    （2）**夹爪开口够不够**——夹不下就是 0；
    （3）**摩擦锥近似**——夹紧方向与接触面法线夹角超出 arctan(mu) 就容易滑。

    这是“工程上先用几何筛一遍”的那一层，不是真力学。**它的近似在哪里会错，由算例算出来。**
    """
    if gl is None or gl["width"] > grip["open_max_m"]:
        return 0.0
    c = poly_centroid(P)
    d = np.array([math.cos(gl["angle"]), math.sin(gl["angle"])])
    off = abs(cross2(d, c - gl["p0"]))                 # 质心到抓取线的垂距
    s_center = math.exp(-(off / 0.012) ** 2)
    s_width = 1.0 - gl["width"] / grip["open_max_m"] * 0.5
    cone = math.atan(grip["mu"])
    ang0 = math.acos(min(1.0, abs(float(np.dot(d, gl["n0"])))))
    ang1 = math.acos(min(1.0, abs(float(np.dot(d, gl["n1"])))))
    s_cone = float(np.clip((cone - max(ang0, ang1)) / cone + 0.25, 0.0, 1.0))
    return float(s_center * s_width * s_cone)


def grasp_truth(P: np.ndarray, gl: dict, grip: dict = GRIPPER, seed: int = 0,
                trials: int = 24) -> float:
    """这个位姿**实际**抓成多少（0—1）：抓起来之后扰动一下，看会不会滑脱或转掉。

    “真相”比打分多算两件事：接触点处的真实法线（打分里按抓取线方向近似了）、
    以及抬起时质心偏置产生的力矩。扰动是随机的——所以同一个位姿也不是非 0 非 1。
    """
    if gl is None or gl["width"] > grip["open_max_m"]:
        return 0.0
    g = np.random.default_rng(seed + 919)
    c = poly_centroid(P)
    d = np.array([math.cos(gl["angle"]), math.sin(gl["angle"])])
    off = abs(cross2(d, c - gl["p0"]))
    half = gl["width"] / 2.0 + 1e-6
    ok = 0
    for _ in range(trials):
        jit = 0.0025 * g.normal()                        # 抓取时的定位扰动
        tilt = 0.09 * g.normal()                         # 抬起时的晃动（rad）
        dd = np.array([math.cos(gl["angle"] + tilt), math.sin(gl["angle"] + tilt)])
        slip0 = math.acos(min(1.0, abs(float(np.dot(dd, gl["n0"]))))) > math.atan(grip["mu"])
        slip1 = math.acos(min(1.0, abs(float(np.dot(dd, gl["n1"]))))) > math.atan(grip["mu"])
        torque_ok = (off + abs(jit)) < half * grip["mu"] * 1.9
        if torque_ok and not (slip0 or slip1):
            ok += 1
    return ok / trials


# ================================================================ 六、线性倒立摆（足式运动的简化模型）

LIP = {"g": 9.81, "h": 0.92, "dt": 0.02}      # 质心高度 0.92 m，显式假设


def lip_step(x: float, xd: float, foot: float, lip: dict = LIP) -> tuple[float, float]:
    """线性倒立摆走一步：质心在支撑点上方时加速度正比于偏移。

    足式运动的最简模型：**支撑脚踩在哪里，决定质心往哪倒**。
    """
    xdd = lip["g"] / lip["h"] * (x - foot)
    return x + xd * lip["dt"], xd + xdd * lip["dt"]


def capture_point(x: float, xd: float, lip: dict = LIP) -> float:
    """捕获点：脚踩在这里，质心恰好能停住。足式机器人的“稳定边界”就是这个点能不能踩到。"""
    return x + xd * math.sqrt(lip["h"] / lip["g"])


def lip_stable(x: float, xd: float, step_max: float, lip: dict = LIP) -> bool:
    """这一步还救不救得回来：捕获点落在最大跨步范围里才救得回来。"""
    return abs(capture_point(x, xd, lip) - x) <= step_max
