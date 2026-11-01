"""第 17 章共用的玩具模型：pass@k 的估计量、采样温度、仓库上下文的选法、
智能体循环的误差累积、多智能体与自洽多采样的对照、工具选择，以及案例的产线数据。

**为什么全是玩具**：这一章讲的东西——"多采几次会不会好"、"每步出错率怎样累积"、
"多一个复核角色值不值"——都是**概率问题**，不是模型问题。真模型上这些量测不准，
因为每一次都混着模型能力、提示、脚手架、随机性好几件事。退到玩具上，每一条都能
**解析地算出来**，再用蒙特卡洛核对一遍。真模型上的对照数字见资料卡与两个云端实验。

仓库里不放任何真实生产数据；案例的产线数据由程序按规则生成。
"""
from __future__ import annotations

from math import log

import numpy as np

# ================================================================ 一、pass@k（17.1 节）


def pass_at_k(n: int, c: int, k: int) -> float:
    """Codex 论文的无偏估计量：一道题采了 n 个样本、其中 c 个通过，则这道题的 pass@k 是
    1 − C(n−c, k) / C(n, k)。直接按这个式子算在 n 大时数值不稳，论文给了逐项相乘的写法。"""
    if n - c < k:
        return 1.0
    p = 1.0
    for i in range(n - c + 1, n + 1):      # 论文 Figure 3 的数值稳定实现
        p *= 1.0 - k / i
    return 1.0 - p


def pass_at_k_naive(p_hat: float, k: int) -> float:
    """常见的错写法：用经验 pass@1 去算 1 − (1 − p̂)^k。论文明说它是**有偏**的。"""
    return 1.0 - (1.0 - p_hat) ** k


def sample_pass_at_k(p_true: float, n: int, k: int, trials: int, g: np.random.Generator):
    """蒙特卡洛：每道题真实通过率是 p_true，采 n 个样本，用上面的估计量算一次 pass@k。
    返回 (估计量的均值, 真值 1−(1−p)^k)。两者应当一致——这就是"无偏"的含义。"""
    cs = g.binomial(n, p_true, size=trials)
    est = np.array([pass_at_k(n, int(c), k) for c in cs])
    return float(est.mean()), 1.0 - (1.0 - p_true) ** k


# ---------------------------------------------------------------- 温度与 k（17.1 节）
# 机制：每道题有若干条"路子"，只有一条对。模型给每条路子一个分数，按温度做 softmax 采样。
# 温度趋于 0 → 永远选分最高的那条（pass@1 与 pass@100 一样）；温度大 → 接近均匀
# （pass@1 低，但多采几次总能碰上对的那条）。Codex 论文观察到的"k 越大最优温度越高"，
# 在这个玩具上是算得出来的，不用训模型。

N_PROBLEMS, N_WAYS = 400, 200


def problem_logits(seed: int = 0, skill: float = 2.6):
    """每道题 N_WAYS 条路子，只有一条对；模型给每条一个分数。
    对的那条平均高 `skill` 分（模型的"水平"），但不总是最高——所以温度一调，结果就变。
    路子多（200 条）这一点很要紧：温度调得很高时，采样会掉进那一大堆没用的路子里，
    于是 pass@k 对每个 k 都有一个**内点**最优温度，而不是越高越好。"""
    g = np.random.default_rng(1700 + seed)
    logits = g.normal(0, 1.0, (N_PROBLEMS, N_WAYS))
    right = g.integers(N_WAYS, size=N_PROBLEMS)
    logits[np.arange(N_PROBLEMS), right] += skill
    return logits, right


def p_correct(logits, right, T: float) -> np.ndarray:
    """给定温度，每道题采一个样本采对的概率。T → 0 时退化成"取最大值"。"""
    if T < 1e-6:
        return (np.argmax(logits, 1) == right).astype(float)
    z = logits / T
    z = z - z.max(1, keepdims=True)
    p = np.exp(z)
    p /= p.sum(1, keepdims=True)
    return p[np.arange(len(right)), right]


def pass_curve(logits, right, T: float, ks=(1, 10, 100)) -> dict[int, float]:
    """这个温度下的 pass@k（按定义直接算期望，不用采样）。"""
    p = p_correct(logits, right, T)
    return {k: float(np.mean(1.0 - (1.0 - p) ** k)) for k in ks}


def best_temperature(logits, right, k: int, temps=None) -> tuple[float, float]:
    temps = temps if temps is not None else np.round(np.arange(0.0, 2.01, 0.05), 2)
    vals = [(float(t), pass_curve(logits, right, float(t), (k,))[k]) for t in temps]
    return max(vals, key=lambda x: x[1])


# ---------------------------------------------------------------- 污染（17.1 节）
# 两个"模型"：一个把见过的题连答案一起背下来，一个真会解题。它们在原题上分不开，
# 在改写过的题上立刻分开——这就是为什么评测集被训练数据污染之后分数会虚高。

def contamination(n_problems: int = 400, seen_frac: float = 0.3, solver_skill: float = 0.55,
                  memo_recall: float = 0.98, seed: int = 0):
    """返回两个模型在（原题 / 改写题）上的正确率，以及"看见过的题"与"没看见过的题"的落差。"""
    g = np.random.default_rng(1800 + seed)
    seen = g.random(n_problems) < seen_frac
    # 背题的：见过的题几乎全对，没见过的题只能瞎蒙
    memo_orig = np.where(seen, g.random(n_problems) < memo_recall, g.random(n_problems) < 0.12)
    # 改写之后，背下来的那份对不上了（只剩一点点），真会解的不受影响
    memo_para = np.where(seen, g.random(n_problems) < 0.18, g.random(n_problems) < 0.12)
    solver_orig = g.random(n_problems) < solver_skill
    solver_para = g.random(n_problems) < solver_skill
    out = {
        "memo_orig": float(memo_orig.mean()), "memo_para": float(memo_para.mean()),
        "solver_orig": float(solver_orig.mean()), "solver_para": float(solver_para.mean()),
        "memo_seen": float(memo_orig[seen].mean()), "memo_unseen": float(memo_orig[~seen].mean()),
        "solver_seen": float(solver_orig[seen].mean()), "solver_unseen": float(solver_orig[~seen].mean()),
        "seen_frac": float(seen.mean()),
    }
    return out


# ================================================================ 二、仓库上下文（17.2 节）
# 一个玩具仓库：每个文件有若干"符号"，任务要改的那几个文件由若干符号串起来。
# 三种选法：按最近编辑、按词面检索、按符号图扩展。量命中率与词元账。

def make_repo(n_files: int = 3000, n_symbols: int = 9000, seed: int = 0):
    g = np.random.default_rng(1900 + seed)
    # 每个文件定义 1—3 个符号，引用 0—5 个别的符号
    defines = [g.choice(n_symbols, size=int(g.integers(1, 4)), replace=False) for _ in range(n_files)]
    uses = [g.choice(n_symbols, size=int(g.integers(0, 6)), replace=False) for _ in range(n_files)]
    tokens = g.integers(200, 3000, size=n_files)         # 每个文件多少词元
    edited = g.permutation(n_files)                      # 最近编辑顺序（0 是最近改过的）
    return {"defines": defines, "uses": uses, "tokens": tokens, "edited": edited,
            "n_files": n_files, "n_symbols": n_symbols}


def make_task(repo, seed: int = 0):
    """一个任务，照真实 issue 的样子造：提到一个符号 s。
    改 s 的定义处（文件 A）不够——还要跟着改用到 s 的文件 B，以及用到 B 里那个符号的文件 C。
    **三个文件是被符号串起来的**，这一点决定了哪种选法找得到它们："""
    g = np.random.default_rng(2000 + seed)
    a = int(g.integers(repo["n_files"]))
    sym_s = int(g.choice(repo["defines"][a]))
    # 造一个用到 s 的文件 B，B 自己定义 t
    b = int(g.integers(repo["n_files"]))
    while b == a:
        b = int(g.integers(repo["n_files"]))
    repo["uses"][b] = np.unique(np.append(repo["uses"][b], sym_s))
    sym_t = int(repo["defines"][b][0])
    # 再造一个用到 t 的文件 C
    c = int(g.integers(repo["n_files"]))
    while c in (a, b):
        c = int(g.integers(repo["n_files"]))
    repo["uses"][c] = np.unique(np.append(repo["uses"][c], sym_t))
    return {"target": [a, b, c], "mentioned": [sym_s], "chain": (sym_s, sym_t)}


def select_recent(repo, task, budget_tokens: int):
    order = np.argsort(repo["edited"])
    return _take(repo, order, budget_tokens)


def select_lexical(repo, task, budget_tokens: int):
    """词面检索：文件里出现了提示词提到的符号就算相关（命中的定义排在引用前面）。"""
    score = np.zeros(repo["n_files"])
    for s in task["mentioned"]:
        for i in range(repo["n_files"]):
            if s in repo["defines"][i]:
                score[i] += 2.0
            elif s in repo["uses"][i]:
                score[i] += 1.0
    order = np.argsort(-score, kind="stable")
    return _take(repo, order, budget_tokens)


def select_symbol_graph(repo, task, budget_tokens: int, hops: int = 2):
    """符号图扩展：从提示词提到的符号出发，把**定义它的文件**与**用到它的文件**拉进来；
    这些文件自己定义的符号再进入下一跳。一跳只能找到"定义处 + 直接调用方"，
    两跳才跟得上"调用方自己又被谁用了"这条链——而真实的改动往往就是这么一条链。"""
    frontier = set(task["mentioned"])
    picked, seen_sym = [], set()
    for _ in range(hops):
        new_sym: set[int] = set()
        for i in range(repo["n_files"]):
            if i in picked:
                continue
            d, u = set(repo["defines"][i].tolist()), set(repo["uses"][i].tolist())
            if frontier & d or frontier & u:
                picked.append(i)
                new_sym |= d                   # 这个文件定义的符号，进入下一跳
        seen_sym |= frontier
        frontier = new_sym - seen_sym
        if not frontier:
            break
    rest = [i for i in np.argsort(repo["edited"]) if i not in set(picked)]
    return _take(repo, picked + list(rest), budget_tokens)


def _take(repo, order, budget_tokens: int):
    out, used = [], 0
    for i in order:
        t = int(repo["tokens"][i])
        if used + t > budget_tokens:
            continue
        out.append(int(i))
        used += t
        if used > budget_tokens * 0.98:
            break
    return out, used


def recall(selected, task) -> float:
    s = set(selected)
    return sum(1 for t in task["target"] if t in s) / len(task["target"])


# ================================================================ 三、智能体循环（17.3 节）
# 一个任务要走 n 步，每步有 p 的概率出错。什么都不做时，成功率是 (1−p)^n——
# 这是个恒等式，不是经验规律。下面三种救法各买回多少，也都算得出来。


def plain(p: float, n: int) -> float:
    """什么都不做：n 步全对的概率。"""
    return (1 - p) ** n


def with_retry(p: float, n: int, tries: int) -> float:
    """整件事失败就从头再来，最多 tries 次。注意：这要求失败看得出来，而且能重来。"""
    s = plain(p, n)
    return 1 - (1 - s) ** tries


def with_check(p: float, n: int, detect: float, retries: int = 1) -> float:
    """每一步之后自检：查出错误的概率是 detect，查出来就重做这一步（最多 retries 次）。
    单步成功率从 (1−p) 变成 1 − p·(1 − detect·(1−p))^... ——下面按几何级数展开。"""
    q = p
    for _ in range(retries):
        q = q * (1 - detect * (1 - p))     # 错了但没查出来，或查出来重做又错了
    return (1 - q) ** n


def with_verifier(p: float, n: int, tpr: float, fpr: float, tries: int = 3) -> float:
    """末端校验：整件事做完之后用一个校验器判对错，判错就重做（最多 tries 次）。
    校验器本身会误判：真错被查出的概率是 tpr，真对被误判为错的概率是 fpr。
    返回"交付出去的结果是对的"的概率——注意误判为错会把对的结果扔掉。"""
    s = plain(p, n)
    ok = 0.0
    alive = 1.0
    for _ in range(tries):
        ok += alive * s * (1 - fpr)        # 这一轮做对了，而且校验器放行
        alive = alive * (s * fpr + (1 - s) * tpr)   # 被打回：对的被误判，或错的被查出
    ok += alive * s                        # 最后一次无论如何都交付
    return ok


def simulate_agent(p: float, n: int, trials: int, seed: int = 0) -> float:
    """蒙特卡洛核对 (1−p)^n。"""
    g = np.random.default_rng(2100 + seed)
    return float(np.mean((g.random((trials, n)) > p).all(1)))


def steps_for(p: float, target: float) -> float:
    """要让成功率不低于 target，每步出错率 p 时最多能走几步（解出来的，不是试出来的）。"""
    if p <= 0:
        return float("inf")
    return log(target) / log(1 - p)


# ---------------------------------------------------------------- 记忆的三层账（17.3 节）
def memory_cost(turns: int, tokens_per_turn: int, tools_tokens: int, system_tokens: int,
                cache_write: float = 1.25, cache_read: float = 0.1):
    """一个 n 轮的智能体对话，每轮都要把前面所有内容重新送一遍（官方原话：请求里的一切都算上下文）。
    返回 (不缓存的总输入词元, 缓存前缀后的相对价格)。
    相对价格是折算：前缀写一次 1.25 倍、读 n−1 次 0.1 倍，与"每次全价"比。"""
    prefix = system_tokens + tools_tokens
    total = sum(prefix + tokens_per_turn * t for t in range(1, turns + 1))
    full_price = total
    cached = (cache_write * prefix + sum(cache_read * prefix for _ in range(turns - 1))
              + sum(tokens_per_turn * t for t in range(1, turns + 1)))
    return total, cached / full_price


# ================================================================ 四、多智能体（17.4 节）
# 同样的预算（一共调 N 次模型），两种花法：
#   （甲）自洽多采样：独立采 N 次，投票；
#   （乙）提议—复核：一个角色提议、一个角色复核，一轮两次调用，共 N/2 轮。
# 哪种更准，取决于三个数：单次正确率 p、错误答案会不会撞在一起、复核者的查错能力。


def self_consistency(p: float, n_calls: int, n_wrong: int = 4, trials: int = 20000, seed: int = 0):
    """独立采 n_calls 次投票。错的时候从 n_wrong 个错误答案里随机挑一个——
    n_wrong 越小，错误越容易撞在一起，投票就越不管用。"""
    g = np.random.default_rng(2200 + seed)
    ok = 0
    for _ in range(trials):
        votes: dict[int, int] = {}
        for _ in range(n_calls):
            a = 0 if g.random() < p else int(1 + g.integers(n_wrong))
            votes[a] = votes.get(a, 0) + 1
        best = max(votes.items(), key=lambda kv: (kv[1], -kv[0]))[0]
        ok += int(best == 0)
    return ok / trials


def propose_review(p: float, n_calls: int, tpr: float, fpr: float):
    """提议—复核：一轮用两次调用（提议一次、复核一次）。复核说"不行"就重提。
    与 with_verifier 是同一个结构，这里把轮数换算成调用次数。"""
    rounds = max(1, n_calls // 2)
    return with_verifier(1 - p, 1, tpr, fpr, tries=rounds)


# ================================================================ 五、工具选择（17.5 节）
# 工具一多，两件事同时变坏：工具定义吃掉的词元越来越多；在一堆工具里挑对的那个也越来越难。

def tool_budget(n_tools: int, per_tool_tokens: int, system_overhead: int) -> int:
    """工具定义占的词元（折算：固定开销 + 每个工具的定义）。官方只给固定开销那一项。"""
    return system_overhead + n_tools * per_tool_tokens


def tool_pick_accuracy(n_tools: int, margin: float = 2.5, trials: int = 20000, seed: int = 0):
    """在 n_tools 个工具里挑对的概率：对的那个平均分高 margin，其余都是噪声。
    工具越多，噪声里出现一个比它更高的分就越容易——这是极值统计，不是模型笨。"""
    g = np.random.default_rng(2300 + seed)
    right = g.normal(margin, 1.0, trials)
    others = g.normal(0.0, 1.0, (trials, n_tools - 1))
    return float(np.mean(right > others.max(1)))


# ================================================================ 六、案例：产线日报（17.7 节）
# 三条产线、若干天的节拍、缺陷、停机。智能体要回答一组有标准答案的问题。
# 程序里的"智能体"是一个规则脚手架：取数 → 算指标 → 比对 → 下结论。
# 要量的不是"模型聪不聪明"，是**脚手架与检查**各挡掉了多少错。

LINES = ("一号线", "二号线", "三号线")
DAYS = 28


def factory_data(seed: int = 0):
    """产线数据：每条线每天的产量、节拍、停机分钟、缺陷数。
    第 25 天起二号线悄悄掉产能——**只影响最近 7 天里的后 4 天**，所以"数据只取回一半"
    这种毛病会把它整个盖掉。"""
    g = np.random.default_rng(2400 + seed)
    out = {}
    for li, name in enumerate(LINES):
        base = 480 + 40 * li
        rate = g.normal(base, 12, DAYS)
        down = np.clip(g.gamma(2.0, 18.0, DAYS), 0, 300)
        defect = g.poisson(6 + 2 * li, DAYS)
        if li == 1:                                   # 二号线：第 25 天起节拍变慢
            rate[24:] *= 0.80
            down[24:] += 45
        out[name] = {"rate": rate, "down": down, "defect": defect,
                     "output": np.round(rate * (1 - down / 1440)).astype(int)}
    return out


def truth(data) -> dict:
    """标准答案：这组问题的正确结论是算得出来的。"""
    last7 = {k: v["output"][-7:].mean() for k, v in data.items()}
    prev7 = {k: v["output"][-14:-7].mean() for k, v in data.items()}
    drop = {k: (last7[k] - prev7[k]) / prev7[k] * 100 for k in data}
    worst = min(drop, key=lambda k: drop[k])
    return {
        "worst_line": worst, "worst_drop_pct": drop[worst], "drop": drop,
        "total_last7": sum(last7.values()),
        "most_downtime": max(data, key=lambda k: data[k]["down"][-7:].sum()),
        "most_defect": max(data, key=lambda k: data[k]["defect"][-7:].sum()),
        "defect_rate": {k: data[k]["defect"][-7:].sum() / data[k]["output"][-7:].sum() * 1000
                        for k in data},
    }


# ---- 智能体用的"工具"。三种毛病都是真实系统里会遇到的，而且都**不报错**。
BOX = 12                                              # 一箱 12 件


def tool_fetch(data, line, days=7, fault=None):
    v = data[line]["output"]
    if fault == "stale":                              # 时间窗口写错了，取到的是上一周
        return v[-14:-7].astype(float)
    if fault == "partial":                            # 分页没翻完，只取回前半段
        return v[-days:][:4].astype(float)
    if fault == "mixed" and line == LINES[0]:         # 这一条线的数来自另一个系统，单位是"箱"
        return v[-days:].astype(float) / BOX
    return v[-days:].astype(float)


def agent_report(data, faults=None, checks=()):
    """脚手架：每条线取最近 7 天与前 7 天的平均产量，算变化，挑最差的那条。
    faults 指定哪个工具出毛病；checks 指定开哪些检查。返回 (结论, 报了几个警)。"""
    faults = faults or {}
    f = faults.get("fetch")
    warn = 0
    drop = {}
    for line in data:
        a = tool_fetch(data, line, 7, f)
        b = data[line]["output"][-14:-7].astype(float)
        if "length" in checks and len(a) != 7:        # 检查一：取回来的够不够七天
            warn += 1
            a = data[line]["output"][-7:].astype(float)
        if "range" in checks and not (0.2 < a.mean() / b.mean() < 5):   # 检查二：量级对不对
            warn += 1
            a = data[line]["output"][-7:].astype(float)
        drop[line] = (a.mean() - b.mean()) / b.mean() * 100
    if "cross" in checks:                             # 检查三：换一个口径交叉核对
        alt = {k: (data[k]["rate"][-7:].mean() - data[k]["rate"][-14:-7].mean())
               / data[k]["rate"][-14:-7].mean() * 100 for k in data}
        if min(alt, key=lambda k: alt[k]) != min(drop, key=lambda k: drop[k]):
            warn += 1
            drop = alt
    worst = min(drop, key=lambda k: drop[k])
    return {"worst_line": worst, "worst_drop_pct": drop[worst], "drop": drop}, warn


def report_ok(rep, tru, tol: float = 2.0) -> bool:
    """结论算不算对：挑出的线要对，而且变化幅度不能差太多。"""
    return (rep["worst_line"] == tru["worst_line"]
            and abs(rep["worst_drop_pct"] - tru["worst_drop_pct"]) < tol)
