"""第 167b 轮：软件公司案例 A——关节驱动板实时操作系统（REL-RTOS）的任务调度。
电流环 20 kHz、速度环、EtherCAT 通信、位置环、诊断、日志 6 个任务排在一颗 MCU 上：比较前后台大循环 / 固定优先级 / 最早截止期优先，选固定优先级（截止期单调）；
手算利用率、Liu–Layland 界、精确响应时间分析（含中断延迟、上下文切换、共享缓冲的阻塞）；自己写的离散事件调度仿真跑 1 000 个超周期对照；
软件公司发布流水线做 20 次 REL-RTOS 构建，发布门禁量最坏中断延迟等。

    python3 tools/cases/software_a.py

MCU 主频、各任务执行时间、上下文切换时间都是示例值（量级按 200 MHz 级 Cortex-M7 类 MCU 的伺服驱动器）。输出到 factory/cases/software/A/。
"""
from __future__ import annotations

import math
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-software.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402

TOOLS = {
    "softops": ("发布与服务", "Releases & services", "/software-ops"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间执行", "Shop floor", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("software", "A", "简单", "关节驱动板的实时任务调度", "Real-time task scheduling on the joint drive board", "REL-RTOS 任务与优先级",
              "电流环 20 kHz、速度环、EtherCAT 通信、位置环、诊断、日志 6 个任务排在关节驱动板的一颗 MCU 上：比较前后台大循环、固定优先级、最早截止期优先，选固定优先级（截止期单调）；"
              "手算利用率、Liu–Layland 界和精确响应时间（含中断延迟、上下文切换、共享缓冲阻塞），发现电流环超时、改成无锁双缓冲；离散事件调度仿真 1 000 个超周期对照；"
              "软件公司发布流水线做 20 次构建，发布门禁量最坏中断延迟。",
              "Six tasks (20 kHz current loop, speed loop, EtherCAT, position loop, diagnostics, logging) on the joint drive board's MCU: super-loop, fixed priority and EDF compared, "
              "fixed priority (deadline monotonic) chosen; utilization, Liu–Layland bound and exact response-time analysis (interrupt latency, context switches, blocking on a shared buffer) "
              "show the current loop missing its deadline, fixed with a lock-free double buffer; a discrete-event scheduling simulation over 1,000 hyperperiods cross-checks; "
              "20 release builds through the software company's pipeline, worst-case interrupt latency measured at the release gate.",
              "tools/cases/software_a.py")

# ---------------------------------------------------------------- 任务（示例值）
MCU_MHZ = 200
CS = 0.8              # 一次上下文切换 μs（保存 / 恢复寄存器 + 调度器，示例）
IRQ_SPEC = 8.0        # 最坏中断延迟上限 μs（软件公司清单 rtos_irq 的上限 = 本设计的释放抖动）
CRIT = 6.0            # 共享参数缓冲（设定值、增益、状态字）的临界区最长 μs
HYPER = 100_000.0     # 超周期 μs（各周期的最小公倍数）
N_HYPER = 1000
# 名称、英文、周期 T、最坏执行时间 C、截止期 D（μs）、用不用共享缓冲（初稿）
TASKS = [
    ("电流环（FOC）", "Current loop (FOC)", 50.0, 14.0, 25.0, True),
    ("速度环", "Speed loop", 250.0, 22.0, 250.0, True),
    ("EtherCAT 过程数据", "EtherCAT process data", 1000.0, 150.0, 600.0, True),
    ("位置环与插补", "Position loop & interpolation", 1000.0, 70.0, 1000.0, True),
    ("诊断（编码器、温度、过流）", "Diagnostics", 10_000.0, 900.0, 10_000.0, True),
    ("日志与参数服务", "Logging & parameters", 100_000.0, 6000.0, 100_000.0, False),
]
# 截止期单调：截止期短的优先级高（同周期的 EtherCAT 截止期 600 μs，排在位置环前面）
TASKS.sort(key=lambda t: t[4])

brief = f"""# 设计任务书：关节驱动板的实时任务调度

**用在哪**　电路板厂的关节驱动板 DRV-JOINT（装进机器人厂的协作机器人关节）上跑软件公司的实时操作系统 REL-RTOS，每块板一份授权 LIC-RTOS。
一颗 {MCU_MHZ} MHz 的 MCU 要同时做 6 件事，每件都有周期和截止期：

| 任务 | 周期 | 最坏执行时间 | 截止期 | 为什么 |
|---|---|---|---|---|
""" + "\n".join(f"| {n} | {T:g} μs | {C:g} μs | {D:g} μs | {why} |" for (n, _, T, C, D, _), why in zip(TASKS, [
    "PWM 中心对齐，半个周期内算完才赶得上下一个 PWM 更新",
    "速度环带宽约 400 Hz，周期内算完",
    "EtherCAT 每 1 ms 同步一次，过程数据要在下一个同步信号前 400 μs 备好",
    "位置指令每 1 ms 一个插补点",
    "编码器、温度、过流的慢速检查",
    "写日志、回应上位机读写参数",
])) + f"""

| 项目 | 要求 | 出处 |
|---|---|---|
| 所有任务 | 最坏响应时间 ≤ 截止期（硬实时，一次都不能错过） | 伺服控制 |
| 中断延迟 | ≤ {IRQ_SPEC:g} μs（从 ADC 采样完成到电流环开始） | 软件公司清单 rtos_irq（发布门禁硬件在环 2 万次） |
| 上下文切换 | 每次 {CS:g} μs | REL-RTOS 实测量级（示例） |
| 共享参数缓冲 | 临界区最长 {CRIT:g} μs | 代码走查 |
| CPU 余量 | 利用率 ≤ 85 %（以后加功能） | 常用要求 |

执行时间都是示例值，按同类伺服驱动器的量级取。
"""
case.step("brief", f"一颗 {MCU_MHZ} MHz MCU 上 6 个硬实时任务，电流环 20 kHz、截止期 25 μs；中断延迟 ≤ {IRQ_SPEC:g} μs。",
          f"Six hard real-time tasks on one {MCU_MHZ} MHz MCU; 20 kHz current loop with a 25 μs deadline; interrupt latency ≤ {IRQ_SPEC:g} μs.",
          md=case.text("1_任务书.md", brief),
          facts=[("任务", "Tasks", len(TASKS), ""), ("电流环截止期", "Current-loop deadline", 25, "μs"), ("中断延迟上限", "Interrupt latency limit", IRQ_SPEC, "μs")])


# ================================================================ 2 方案
def util(tasks, cs=CS):
    return sum((C + 2 * cs) / T for _, _, T, C, _, _ in tasks)


U = util(TASKS)
U0 = sum(C / T for _, _, T, C, _, _ in TASKS)
n = len(TASKS)
LL = n * (2 ** (1 / n) - 1)
# 前后台大循环：电流环放 ADC 中断里，其余都在主循环里排队——位置环最坏要等主循环转一整圈（所有任务各跑一次）
loop_worst = sum(C for _, _, T, C, _, _ in TASKS[1:]) + math.ceil(sum(C for _, _, T, C, _, _ in TASKS[1:]) / 50.0) * (TASKS[0][3] + 2 * CS)
conmd = f"""# 方案：三种调度方法

| 方法 | 怎么排 | 最坏情况 | 结论 |
|---|---|---|---|
| 前后台大循环 | 电流环放 ADC 中断，其余 5 个在主循环里轮流跑 | 位置环最坏要等主循环转一整圈：{loop_worst:.0f} μs > 截止期 1 000 μs（被 6 ms 的日志任务挡住） | ✗ 除非把日志切碎，代码难维护 |
| **固定优先级（截止期单调）** | 截止期短的优先级高，可抢占；共享缓冲用优先级天花板协议 | 能用响应时间分析算出每个任务的最坏响应；过载时只有低优先级任务受影响 | ✓ **选这个**：REL-RTOS 本来就是固定优先级内核，安全认证（IEC 61508）常用 |
| 最早截止期优先（EDF） | 每次跑截止期最近的 | 利用率 ≤ 100 % 就排得下，最省 CPU | ✗ 过载时哪个任务超时说不准（可能连电流环一起），内核要改 |

利用率（含每次两次上下文切换）**U = {U * 100:.1f} %**（不含切换 {U0 * 100:.1f} %），≤ 85 % 余量要求。
Liu–Layland 充分条件：{n} 个任务 U ≤ {n}(2^(1/{n}) − 1) = **{LL * 100:.1f} %**——U 超过了这个界，**充分条件判不了**，要用第 3 步的精确响应时间分析。
"""
case.step("concept", f"选固定优先级（截止期单调）+ 优先级天花板；利用率 {U * 100:.1f} % 超过 Liu–Layland 界 {LL * 100:.1f} %，要精确分析。",
          f"Fixed priority (deadline monotonic) with priority ceiling; utilization {U * 100:.1f} % exceeds the Liu–Layland bound {LL * 100:.1f} %, so exact analysis is needed.",
          md=case.text("2_方案.md", conmd),
          facts=[("利用率", "Utilization", round(U * 100, 1), "%"), ("Liu–Layland 界", "Liu–Layland bound", round(LL * 100, 1), "%"),
                 ("大循环最坏", "Super-loop worst", round(loop_worst), "μs")])
case.check("concept", "CPU 利用率（含上下文切换）", "CPU utilization (with context switches)", round(U * 100, 1), "<=", 85.0, "%", "任务书")


# ================================================================ 3 计算：响应时间分析
def rta(tasks, users, jitter=IRQ_SPEC, cs=CS, crit=CRIT):
    """固定优先级精确响应时间分析（Audsley / Tindell，含释放抖动与阻塞）。
    R_i = J_i + w_i，w_i = C_i + B_i + Σ_{j 高优先级} ⌈(w_i + J_j) / T_j⌉ C_j；C 含两次上下文切换。
    B_i：优先级天花板协议下，比 i 低、且用到天花板 ≥ i 的资源的任务的最长临界区。"""
    ceiling = min(i for i, t in enumerate(tasks) if users[i]) if any(users) else len(tasks)
    out = []
    for i, (_, _, T, C, D, _) in enumerate(tasks):
        Ci = C + 2 * cs
        B = crit if (i >= ceiling and any(users[k] for k in range(i + 1, len(tasks)))) else 0.0
        J = jitter if i == 0 else 0.0
        w = Ci + B
        for _ in range(1000):
            nw = Ci + B + sum(math.ceil((w + (jitter if j == 0 else 0.0)) / tasks[j][2]) * (tasks[j][3] + 2 * cs) for j in range(i))
            if abs(nw - w) < 1e-9:
                break
            w = nw
        out.append(dict(R=J + w, B=B, J=J, D=D))
    return out


users0 = [t[5] for t in TASKS]                    # 初稿：电流环也用共享缓冲（读设定值、写状态）
r0 = rta(TASKS, users0)
users1 = [False] + users0[1:]                     # 改：电流环和速度环之间改成无锁双缓冲（写一半、指针一换），电流环不再上锁
r1 = rta(TASKS, users1)
rows = [[t[0], f"{t[2]:g}", f"{t[3] + 2 * CS:g}", f"{a['B']:g}", f"{a['J']:g}", f"{a['R']:.1f}", f"{b['R']:.1f}", f"{t[4]:g}",
         "✓" if b["R"] <= t[4] else "✗"] for t, a, b in zip(TASKS, r0, r1)]
calcmd = f"""# 计算：精确响应时间分析

**公式**（固定优先级、可抢占，Audsley / Tindell 响应时间分析）：

R_i = J_i + w_i，　w_i = C_i + B_i + Σ_(j 比 i 优先) ⌈(w_i + J_j) / T_j⌉ · C_j　（迭代到不变）

- C_i：最坏执行时间 + 2 次上下文切换（{CS:g} μs × 2）；
- J_i：释放抖动——电流环由 ADC 中断启动，中断延迟最坏 {IRQ_SPEC:g} μs（软件公司发布门禁量的 rtos_irq 上限，第 7 步实测）；
- B_i：阻塞——共享参数缓冲用优先级天花板协议，一个任务最多被比它低的任务的一段临界区（{CRIT:g} μs）挡一次。

{L.md_table(["任务", "T / μs", "C（含切换）", "B", "J", "R 初稿", "R 改后", "D", ""], rows)}

**初稿不行**：电流环也锁共享缓冲（读速度环给的电流指令、写状态字），会被低优先级任务的临界区挡 {CRIT:g} μs：
R = {IRQ_SPEC:g} + {CRIT:g} + {TASKS[0][3] + 2 * CS:g} = **{r0[0]['R']:.1f} μs > 25 μs**，偶尔赶不上 PWM 更新。

**改设计**：速度环 → 电流环的指令改成**无锁双缓冲**（速度环写备用的一半，写完一条原子指令换指针；电流环只读当前那一半），电流环不再上锁，B = 0：
R = {r1[0]['R']:.1f} μs ≤ 25 μs。其余任务仍用优先级天花板协议，阻塞 {CRIT:g} μs 已算在里面，全部满足截止期。
最紧的是电流环（余量 {25 - r1[0]['R']:.1f} μs）——中断延迟上限 {IRQ_SPEC:g} μs 就是这条余量的来源，发布门禁每个版本都要量。
"""
worst_margin = min(t[4] - b["R"] for t, b in zip(TASKS, r1))
case.step("calc", f"初稿电流环 R = {r0[0]['R']:.1f} μs > 25 μs（被共享缓冲挡住）；改无锁双缓冲后 {r1[0]['R']:.1f} μs，6 个任务全部满足截止期。",
          f"Draft current loop R = {r0[0]['R']:.1f} μs > 25 μs (blocked on the shared buffer); with a lock-free double buffer {r1[0]['R']:.1f} μs, all six tasks meet their deadlines.",
          md=case.text("3_响应时间分析.md", calcmd),
          facts=[("电流环 R（初稿）", "Current loop R (draft)", round(r0[0]["R"], 1), "μs"), ("电流环 R（改后）", "Current loop R (final)", round(r1[0]["R"], 1), "μs"),
                 ("EtherCAT R", "EtherCAT R", round(r1[1]["R"], 1), "μs")])
for t, b in zip(TASKS, r1):
    case.check("calc", f"{t[0]} 最坏响应", f"{t[1]} worst-case response", round(b["R"], 1), "<=", t[4], "μs", "截止期")


# ================================================================ 4 仿真：离散事件调度
def irq_sample(rng):
    """中断延迟：和软件公司硬件在环模型（sim/softsim.py）同一个分布——基础 3 μs + 对数正态尾巴 + 2 % 的总线争用"""
    return 3.0 + rng.lognormvariate(-0.9, 0.45) + (rng.uniform(0, 1.5) if rng.random() < 0.02 else 0.0)


def simulate(users, n_hyper=N_HYPER, seed=167, overrun=None):
    """固定优先级可抢占调度的离散事件仿真。每个作业的执行时间 = C × U(0.55, 1)（5 % 的作业正好最坏 C），外加两次上下文切换；
    电流环的释放晚一个中断延迟（irq_sample）；用共享缓冲的作业在执行中随机一处进临界区 {CRIT} μs，期间优先级升到天花板。
    → 每个任务的最坏响应（从名义释放时刻算）、错过截止期次数。overrun：(任务号, 倍数) 让某个任务超时运行，看会不会连累别人。"""
    rng = random.Random(seed)
    ntask = len(TASKS)
    ceiling = min(i for i in range(ntask) if users[i])
    horizon = n_hyper * HYPER
    worst = [0.0] * ntask
    miss = [0] * ntask
    # 事件队列：按时间排的释放
    ready = []                              # 作业：[任务号, 名义释放, 剩余执行（临界区前）, 临界区剩余, 临界区后剩余, 实际可运行时刻]
    t = 0.0
    import heapq
    rel = []
    for i in range(ntask):
        heapq.heappush(rel, (0.0 + (irq_sample(rng) if i == 0 else 0.0), i, 0.0))
    while rel and rel[0][0] < horizon or ready:
        # 选当前最高有效优先级的作业（数字小优先）
        if not ready:
            t = max(t, rel[0][0])
        while rel and rel[0][0] <= t + 1e-12:
            _, i, nominal = heapq.heappop(rel)
            T, C = TASKS[i][2], TASKS[i][3]
            e = C if rng.random() < 0.05 else C * rng.uniform(0.55, 1.0)
            if overrun and overrun[0] == i:
                e *= overrun[1]
            e += 2 * CS
            if users[i]:
                pre = rng.uniform(0, max(0.0, e - CRIT))
                ready.append([i, nominal, pre, CRIT, max(0.0, e - CRIT - pre)])
            else:
                ready.append([i, nominal, e, 0.0, 0.0])
            nn = nominal + T
            if nn < horizon:
                heapq.heappush(rel, (nn + (irq_sample(rng) if i == 0 else 0.0), i, nn))
        if not ready:
            continue

        def prio(j):
            return min(j[0], ceiling) if (j[2] <= 1e-12 and j[3] > 1e-12) else j[0]
        job = min(ready, key=lambda j: (prio(j), j[1]))
        seg = 2 if job[2] > 1e-12 else (3 if job[3] > 1e-12 else 4)
        run = job[seg]
        tn = rel[0][0] if rel else math.inf
        dt = min(run, tn - t) if tn > t else run
        if dt <= 0:
            dt = run if tn <= t else dt
        job[seg] -= dt
        t += dt
        if job[2] <= 1e-12 and job[3] <= 1e-12 and job[4] <= 1e-12:
            ready.remove(job)
            i = job[0]
            r = t - job[1]
            worst[i] = max(worst[i], r)
            if r > TASKS[i][4] + 1e-9:
                miss[i] += 1
    return worst, miss


sim0, miss0 = simulate(users0, n_hyper=200, seed=11)
sim1, miss1 = simulate(users1, seed=12)
sim_ov, miss_ov = simulate(users1, n_hyper=100, seed=13, overrun=(5, 3.0))
n_cur = int(N_HYPER * HYPER / TASKS[0][2])
srows = [[t[0], f"{b['R']:.1f}", f"{s:.1f}", f"{s / b['R'] * 100:.0f} %", m, f"{so:.1f}", mo]
         for t, b, s, m, so, mo in zip(TASKS, r1, sim1, miss1, sim_ov, miss_ov)]
simmd = f"""# 仿真：离散事件调度

自己写的固定优先级可抢占调度仿真（脚本里 `simulate`）：

- 每个作业的执行时间在 0.55 C 到 C 之间随机，5 % 的作业正好是最坏 C；每个作业加两次上下文切换；
- 电流环由 ADC 中断启动，晚一个中断延迟——和软件公司硬件在环测试台用的是**同一个分布**（基础 3 μs + 对数正态尾巴 + 2 % 总线争用，`sim/softsim.py`）；
- 用共享缓冲的作业在执行中随机一处进 {CRIT:g} μs 临界区，期间按优先级天花板协议升优先级；
- 跑 {N_HYPER} 个超周期（{N_HYPER * HYPER / 1e6:g} 秒，电流环 {n_cur:,} 次）。

{L.md_table(["任务", "分析 R / μs", "仿真最坏 / μs", "仿真 / 分析", "错过截止期", "日志超时 3 倍：最坏", "错过"], srows)}

1. **仿真最坏都不超过分析值**：分析假设所有最坏情况同时发生，是上界；电流环仿真最坏 {sim1[0]:.1f} μs，离分析值 {r1[0]['R']:.1f} μs 不远（中断延迟尾巴、最坏执行时间都碰上过）。
2. **初稿也仿了 200 个超周期**：电流环最坏 {sim0[0]:.1f} μs、错过截止期 **{miss0[0]}** 次——低优先级任务在临界区里时 ADC 中断来了，电流环被挡。
   次数不多但伺服不允许，和第 3 步的分析一致。
3. **过载隔离**：让日志任务超时跑 3 倍（参数服务卡住），比它优先的 5 个任务一个都没错过截止期——固定优先级的好处，EDF 做不到这一点。
"""


def gantt(ax, users, span=1000.0, seed=5):
    """画前 span μs 的调度时序（单独再跑一遍记录每段谁在跑）"""
    rng = random.Random(seed)
    ntask = len(TASKS)
    ceiling = min(i for i in range(ntask) if users[i])
    segs = []
    import heapq
    rel = [(0.0 + (irq_sample(rng) if i == 0 else 0.0), i, 0.0) for i in range(ntask)]
    heapq.heapify(rel)
    ready, t = [], 0.0
    while t < span:
        if not ready:
            t = max(t, rel[0][0])
        while rel and rel[0][0] <= t + 1e-12:
            _, i, nominal = heapq.heappop(rel)
            e = TASKS[i][3] * rng.uniform(0.7, 1.0) + 2 * CS
            pre = rng.uniform(0, max(0.0, e - CRIT)) if users[i] else e
            ready.append([i, nominal, pre, CRIT if users[i] else 0.0, max(0.0, e - CRIT - pre) if users[i] else 0.0])
            heapq.heappush(rel, (nominal + TASKS[i][2] + (irq_sample(rng) if i == 0 else 0.0), i, nominal + TASKS[i][2]))
        if not ready:
            continue
        job = min(ready, key=lambda j: ((min(j[0], ceiling) if (j[2] <= 1e-12 and j[3] > 1e-12) else j[0]), j[1]))
        seg = 2 if job[2] > 1e-12 else (3 if job[3] > 1e-12 else 4)
        dt = min(job[seg], rel[0][0] - t) if rel[0][0] > t else job[seg]
        segs.append((job[0], t, dt, seg == 3))
        job[seg] -= dt
        t += dt
        if job[2] <= 1e-12 and job[3] <= 1e-12 and job[4] <= 1e-12:
            ready.remove(job)
    cols = ["#c92a2a", "#e8590c", "#2c6fbb", "#2f9e44", "#7048e8", "#7b8794"]
    for i, t0, dt, crit in segs:
        if t0 < span:
            ax.broken_barh([(t0, min(dt, span - t0))], (ntask - 1 - i + 0.1, 0.8), color=cols[i], alpha=0.95 if not crit else 0.55,
                           hatch="///" if crit else None, edgecolor="white" if not crit else "k", linewidth=0.3)
    for i, tk in enumerate(TASKS):
        k = 0
        while k * tk[2] < span:
            ax.plot([k * tk[2]] * 2, [ntask - 1 - i + 0.05, ntask - 1 - i + 0.95], color="k", lw=0.5)
            k += 1
    ax.set_yticks([ntask - 1 - i + 0.5 for i in range(ntask)], [tk[0] for tk in TASKS], fontsize=8)
    ax.set_xlim(0, span)
    ax.set_xlabel("时间 / μs（竖线 = 释放；斜线 = 临界区）")


fig, axs = plt.subplots(1, 2, figsize=(12, 3.8), gridspec_kw=dict(width_ratios=[1.6, 1]))
gantt(axs[0], users1, span=1000.0)
axs[0].set_title("改后前 1 ms 的调度（电流环每 50 μs 一次，总是第一个跑）", fontsize=10)
x = range(len(TASKS))
axs[1].bar([i - 0.2 for i in x], [b["R"] / t[4] * 100 for t, b in zip(TASKS, r1)], 0.4, label="分析 R / D")
axs[1].bar([i + 0.2 for i in x], [s / t[4] * 100 for t, s in zip(TASKS, sim1)], 0.4, label="仿真最坏 / D")
axs[1].axhline(100, color="#c92a2a", lw=1)
axs[1].set_xticks(list(x), [f"T{i + 1}" for i in x])
axs[1].set_ylabel("占截止期 %")
axs[1].legend(fontsize=8)
axs[1].set_title("响应时间：分析与仿真", fontsize=10)
case.fig(fig, "4_调度仿真.png")
case.step("sim", f"{N_HYPER} 个超周期：仿真最坏都不超过分析值（电流环 {sim1[0]:.1f} / {r1[0]['R']:.1f} μs），0 次错过；初稿错过 {miss0[0]} 次；日志超时 3 倍不连累别人。",
          f"{N_HYPER} hyperperiods: simulated worst cases never exceed the analysis (current loop {sim1[0]:.1f} / {r1[0]['R']:.1f} μs), 0 misses; the draft missed {miss0[0]} times; "
          "a 3× logging overrun affects no other task.",
          md=case.text("4_调度仿真.md", simmd), figs=[("4_调度仿真.png", "调度时序与响应时间", "Schedule timeline and response times")],
          facts=[("仿真电流环最坏", "Simulated current-loop worst", round(sim1[0], 1), "μs"), ("错过截止期", "Deadline misses", sum(miss1), ""),
                 ("初稿错过", "Draft misses", miss0[0], "")])
case.check("sim", "仿真最坏 ≤ 分析值（所有任务，最大比值）", "Simulated worst ≤ analysis (max ratio over tasks)", round(max(s / b["R"] for s, b in zip(sim1, r1)), 3), "<=", 1.0, "",
           "响应时间分析是上界")
case.check("sim", "改后错过截止期", "Deadline misses after the fix", sum(miss1), "==", 0, "", "硬实时")
case.check("sim", "日志超时 3 倍时其他任务错过截止期", "Misses of other tasks with a 3× logging overrun", sum(miss_ov[:5]), "==", 0, "", "过载隔离")
case.check("sim", "初稿仿真也能看到电流环超时（次数）", "Draft simulation shows current-loop misses", miss0[0], ">", 0, "", "和分析一致")

# ================================================================ 5 图纸：任务与优先级架构
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.set_axis_off()
ax.set_xlim(0, 11)
ax.set_ylim(0, 4.6)


def box(x, y, w, h, text, fc="#eef3f8", ec="#2c6fbb", fs=8.5):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


box(0.2, 3.5, 2.0, 0.8, "ADC 采样完成\n中断（≤ 8 μs）", fc="#fff4e6", ec="#e8590c")
box(0.2, 2.2, 2.0, 0.8, "EtherCAT SYNC0\n中断（1 ms）", fc="#fff4e6", ec="#e8590c")
box(0.2, 0.9, 2.0, 0.8, "系统节拍\n定时器", fc="#fff4e6", ec="#e8590c")
for k, (tk, b) in enumerate(zip(TASKS, r1)):
    box(2.7, 3.9 - k * 0.7, 4.3, 0.6, f"P{k + 1}  {tk[0]}　T {tk[2]:g} / R {b['R']:.0f} / D {tk[4]:g} μs", fs=7.8)
box(7.4, 3.4, 3.3, 0.9, "无锁双缓冲\n速度环 → 电流环：电流指令", fc="#ebfbee", ec="#2f9e44")
box(7.4, 1.8, 3.3, 1.1, f"共享参数缓冲（互斥锁）\n优先级天花板 = P2\n临界区 ≤ {CRIT:g} μs", fc="#f3f0ff", ec="#7048e8")
box(7.4, 0.4, 3.3, 0.9, "PWM 定时器（中心对齐 20 kHz）\n占空比在下半周期前写入", fc="#eef3f8")
for y0, k in [(3.9, 0), (2.6, 2), (1.3, 4)]:          # ADC → 电流环，SYNC0 → EtherCAT，系统节拍 → 诊断、日志
    ax.annotate("", xy=(2.7, 3.9 - k * 0.7 + 0.3), xytext=(2.2, y0), arrowprops=dict(arrowstyle="->", color="#7b8794"))
ax.annotate("", xy=(7.4, 3.85), xytext=(7.0, 3.85), arrowprops=dict(arrowstyle="<->", color="#2f9e44"))
ax.annotate("", xy=(7.4, 2.35), xytext=(7.0, 2.6), arrowprops=dict(arrowstyle="<->", color="#7048e8"))
ax.annotate("", xy=(7.4, 0.85), xytext=(7.0, 4.05), arrowprops=dict(arrowstyle="->", color="#2c6fbb"))
ax.set_title("REL-RTOS 在关节驱动板上的任务与优先级（P1 最高）", fontsize=11)
case.fig(fig, "5_任务架构.png")
cadmd = f"""# 图纸：任务、优先级与共享数据

软件没有三维零件，这一步出的是**任务架构图**和**调度表**（写进 REL-RTOS 的板级配置，构建时生成任务控制块）：

{L.md_table(["优先级", "任务", "启动方式", "周期 / μs", "栈 / 字节", "用共享缓冲"],
            [[f"P{k + 1}", tk[0], ["ADC 中断", "电流环每 5 次", "SYNC0 中断", "SYNC0 后", "系统节拍", "系统节拍"][k], f"{tk[2]:g}",
              [512, 768, 2048, 1536, 2048, 4096][k], "否（无锁双缓冲）" if k == 0 else ("是" if users1[k] else "否")] for k, tk in enumerate(TASKS)])}

- 电流环、速度环之间：**无锁双缓冲**（两份电流指令，速度环写备用的一份，写完原子地换指针）；
- 其余共享：互斥锁 + 优先级天花板（天花板 = 速度环 P2），临界区代码走查限 {CRIT:g} μs；
- 中断里只做最少的事（记时间戳、放信号），算法都在任务里，中断延迟才能压在 {IRQ_SPEC:g} μs 内。
"""
case.step("cad", "6 个任务 P1–P6；电流环与速度环之间无锁双缓冲；其余共享数据用优先级天花板（P2）；调度表写进板级配置。",
          "Six tasks P1–P6; lock-free double buffer between the current and speed loops; other shared data under priority ceiling (P2); schedule table in the board configuration.",
          md=case.text("5_任务架构.md", cadmd), figs=[("5_任务架构.png", "任务与优先级架构", "Task and priority architecture")])

# ================================================================ 6 工艺：发布流水线
from factory import data as F  # noqa: E402

rt = F.ROUTINGS[F.BOMS["REL-RTOS"][0]]
procmd = f"""# 工艺：软件公司实时 OS 发布流水线

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt)])}

和这个设计有关的：

- **编译与单元测试**：调度表由板级配置生成，单元测试里有一条“调度表与本案例的响应时间分析一致”（任务、优先级、周期不许手改）；
- **硬件在环测试**：测试台接真的关节驱动板，量 2 万次中断延迟取最大值（rtos_irq ≤ {IRQ_SPEC:g} μs）——这是第 3 步电流环余量的来源；
  另外记录 10 分钟内每个任务的最坏响应，和第 3 步的表比；
- **发布门禁**：测试通过率、覆盖率、最坏中断延迟、冷启动时间四项都在规格内才能签名发布。
"""
case.step("process", f"发布流水线 {len(rt)} 道：合并评审 → 编译单元测试 → 集成测试 → 硬件在环（量中断延迟）→ 安全扫描 → 发布门禁 → 签名发布。",
          f"{len(rt)}-step release pipeline: review, build & unit test, integration test, HIL (interrupt latency), security scan, release gate, sign & publish.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("工序", "Operations", len(rt), "")])

# ================================================================ 7 制造：20 次构建
sh = L.run_shop("REL-RTOS", 20, "WO-CASE-SW-A", seed=1671)
meas = sh["measurements"]
rows_q, cpk_min, fails, st = L.shop_table(meas)
irq_max = max(m["value_mm"] for m in meas if m["characteristic"] == "rtos_irq")
r_meas = rta(TASKS, users1, jitter=irq_max)
makemd = f"""# 制造：20 次 REL-RTOS 构建

软件公司仿真车间按现行流水线做 20 次构建（{sh['hours']:.1f} 小时），发布门禁记四项：

{L.md_table(["特性", "规格", "次数", "均值", "标准差", "Cpk"], rows_q)}

不合格 **{fails}**，最低 Cpk {cpk_min:.2f}（测试通过率上限 100 % 是自然界限，只看下限）。
20 次构建里最坏中断延迟最大 **{irq_max:.2f} μs**——用它代替 {IRQ_SPEC:g} μs 再算一次电流环：R = {r_meas[0]['R']:.1f} μs，余量 {25 - r_meas[0]['R']:.1f} μs。
"""
case.step("make", f"20 次构建：最坏中断延迟最大 {irq_max:.2f} μs（≤ {IRQ_SPEC:g}），不合格 {fails}，最低 Cpk {cpk_min:.2f}；实测延迟下电流环 R = {r_meas[0]['R']:.1f} μs。",
          f"20 builds: worst interrupt latency at most {irq_max:.2f} μs (≤ {IRQ_SPEC:g}); {fails} failures, lowest Cpk {cpk_min:.2f}; current loop R = {r_meas[0]['R']:.1f} μs with the measured latency.",
          md=case.text("7_构建与发布门禁.md", makemd), tools=tools("softops", "planner", "quality"),
          facts=[("不合格", "Out of spec", fails, ""), ("最低 Cpk", "Lowest Cpk", round(cpk_min, 2), ""), ("最坏中断延迟", "Worst interrupt latency", round(irq_max, 2), "μs")])
case.check("make", "实测最坏中断延迟 ≤ 设计用的抖动", "Measured worst latency ≤ jitter used in the design", round(irq_max, 2), "<=", IRQ_SPEC, "μs", "第 3 步")
case.check("make", "不合格项", "Failures", fails, "==", 0, "", "发布门禁")
case.check("make", "最低 Cpk", "Lowest Cpk", round(cpk_min, 2), ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **利用率过了 Liu–Layland 界不等于排不下**：U = {U * 100:.1f} % 超过 {LL * 100:.1f} %，充分条件判不了；精确响应时间分析算出每个任务都满足截止期。
2. **最紧的不是 CPU，是电流环的 25 μs**：中断延迟 + 一次阻塞 + 执行时间就超了——改成无锁双缓冲去掉阻塞；仿真也看到了初稿偶尔超时。
3. **工厂的测量就是设计的假设**：发布门禁量的最坏中断延迟（rtos_irq ≤ {IRQ_SPEC:g} μs）是响应时间分析里的抖动；哪个版本超了，这个分析就不成立，所以门禁拦下。

## 留给学生的问题

1. 电流环提到 40 kHz（周期 25 μs、截止期 12.5 μs），这颗 MCU 还够吗？把电流环执行时间降到多少才行？
2. 换成 EDF：利用率能用到多少？让日志任务超时 3 倍，哪些任务会错过截止期？（改 `simulate` 里选作业的那一行。）
3. 发布门禁里中断延迟上限为什么取 8 μs 而不是 10 μs？（提示：看电流环的余量。）

相关：软件公司帮助“发布流水线”；电路板厂的关节驱动板 DRV-JOINT；案例 B（云存储）、案例 C（云平台容量）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；固定优先级、电流环无锁双缓冲，R = {r1[0]['R']:.1f} μs ≤ 25 μs。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; fixed priority, lock-free current loop, R = {r1[0]['R']:.1f} μs ≤ 25 μs.",
          md=case.text("8_总结.md", review), tools=tools("softops", "quality"))
case.write()
print("ok", [round(b["R"], 1) for b in r1], [round(s, 1) for s in sim1], miss0, miss1, miss_ov, irq_max, cpk_min)
