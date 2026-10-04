"""GPU 执行模拟器的 Python 参考版（第 14 轮细则 2.5 节：① 线程束执行、② 线程束分化、③ 合并访问、④ 存储体冲突）。
全书共用（conventions/ 在程序的搜索路径上）。

平台实验工具包里的 `gpu` 模块（services/gateway/app/production/labkit/kit.js，`const GPU = {`）与本文件逐行对应；
textbook/tools/tests/test_gpusim.py 用 node 运行 JS 版，核对两者在同一组情形下给出完全相同的结果。

这是教学模型，不是真实 GPU 的仿真：只有一个流多处理器（SM）；指令只有“读显存”和“算术”两种；
读显存的延迟是固定值；算术指令之间没有依赖延迟，可以逐周期连发（真实 GPU 上互相依赖的乘加之间约 4 个周期）；
不模拟缓存、双发射、寄存器存储体。分化部分只统计发射的指令与活动线程，不逐周期模拟。周期数用来比较不同写法，不代表某块显卡的实际耗时。
"""
import math

M32 = 0xFFFFFFFF


def _imul(a, b):
    return (a * b) & M32


def rng(seed):
    """mulberry32 伪随机数（与 JS 版逐位相同），返回 [0, 1) 的函数。"""
    state = [seed & M32]

    def nxt():
        state[0] = (state[0] + 0x6D2B79F5) & M32
        a = state[0]
        t = _imul(a ^ (a >> 15), 1 | a)
        t = ((t + _imul(t ^ (t >> 7), 61 | t)) & M32) ^ t
        return ((t ^ (t >> 14)) & M32) / 4294967296
    return nxt


def schedule(warps=8, schedulers=1, latency=700, k=4, cycles=20000, gap=0, policy="gto", trace=0):
    """部分 ①：线程束调度与延迟隐藏。

    每个线程束不停地重复“读一次显存，再做 k 条依赖这次读取的算术指令”，共模拟 cycles 个周期。线程束 w 归调度器 w % schedulers 管。
    每个周期，每个调度器发射一个“准备好”的线程束的一条指令。挑哪一个由 policy 决定：
      'gto'（贪心后取最老，默认）：上一周期发射的线程束若仍准备好就继续发它，否则取编号最小（最早进入）的准备好的线程束；
      'lrr'（松散轮转）：从上次发射的线程束的下一个开始轮流查找。
    指令能否发射：
      - 读显存：若 gap > 0，同一调度器两次读显存至少相隔 gap 个周期（代表显存带宽的上限）；
      - 算术：要等这次读取的数据到达，即读指令发出后 latency 个周期。
    返回后一半周期里的发射槽利用率（稳态，开头所有线程束都在等第一次读取的阶段不计）与每个线程束完成的轮数；trace > 0 时另给出前 trace 个周期每个线程束的状态：
      'I' 发射，'M' 等显存，'R' 准备好但没轮到，'B' 等带宽。
    """
    assert policy in ("gto", "lrr") and warps >= 1 and schedulers >= 1 and k >= 1 and cycles >= 2 and latency >= 1
    pc = [0] * warps          # 0 = 下一条是读显存，1..k = 第几条算术
    it = [0] * warps          # 完成的轮数
    ready = [0] * warps       # 数据到达的周期
    group = [[w for w in range(warps) if w % schedulers == s] for s in range(schedulers)]
    rr = [0] * schedulers
    last_mem = [-(10 ** 9)] * schedulers
    half = cycles // 2
    issued = 0
    rows = [[] for _ in range(warps)] if trace else None

    def can(w, s, c):
        if pc[w] == 0:
            return gap <= 0 or c - last_mem[s] >= gap
        return c >= ready[w]
    for c in range(cycles):
        for s in range(schedulers):
            g = group[s]
            if not g:
                continue
            pick = -1
            start = rr[s] if policy == "lrr" else 0
            if policy == "gto" and can(g[rr[s]], s, c):
                pick = rr[s]
            else:
                for j in range(len(g)):
                    if can(g[(start + j) % len(g)], s, c):
                        pick = (start + j) % len(g)
                        break
            if trace and c < trace:
                for j, w in enumerate(g):
                    if pick == j:
                        st = "I"
                    elif pc[w] == 0:
                        st = "R" if gap <= 0 or c - last_mem[s] >= gap else "B"
                    else:
                        st = "R" if c >= ready[w] else "M"
                    rows[w].append(st)
            if pick < 0:
                continue
            w = g[pick]
            rr[s] = (pick + 1) % len(g) if policy == "lrr" else pick
            if c >= half:
                issued += 1
            if pc[w] == 0:
                ready[w] = c + latency
                last_mem[s] = c
                pc[w] = 1
            else:
                pc[w] += 1
                if pc[w] > k:
                    pc[w] = 0
                    it[w] += 1
    res = {"issued": issued, "util": issued / (schedulers * (cycles - half)), "rounds": it}
    if trace:
        res["trace"] = ["".join(r) for r in rows]
    return res


def little(warps_per_scheduler, k, latency, gap=0):
    """利特尔定律给出的每个调度器发射利用率的估计：
    一个线程束一轮发 k + 1 条指令、用 latency + k 个周期，n 个线程束轮流就是 n(k+1)/(latency+k)；
    带宽限制 gap 时每 gap 个周期至多一轮，利用率不超过 (k+1)/gap；再不超过 1。"""
    u = min(1.0, warps_per_scheduler * (k + 1) / (latency + k))
    if gap > 0:
        u = min(u, (k + 1) / gap)
    return u


def diverge(cond="odd", warps=1, pre=2, then=4, other=4, post=2, p=0.5, seed=1):
    """部分 ②：线程束分化。线程 t（全线程块编号）先执行 pre 条指令，再按条件 cond 分支：
    条件成立的线程执行 then 条指令，不成立的执行 other 条；最后汇合，再执行 post 条。
    一个线程束里两种线程都有时，两条路径依次执行，执行一条路径时另一类线程空转（活动掩码为 0）。
    cond: 'none' 全部成立；'half' t % 32 < 16；'odd' t 为奇数；'warp' 线程束编号为奇数（同一线程束内一致）；
          'data' 每个线程以概率 p 成立（mulberry32，种子 seed）。
    返回每个线程束的掩码与发射的指令、总的 SIMT 效率 = 活动线程·指令 ÷ (32 × 发射的指令)，以及执行步骤。"""
    r = rng(seed)
    out, issued, active, steps = [], 0, 0, []
    for w in range(warps):
        mask = []
        for lane in range(32):
            t = 32 * w + lane
            if cond == "none":
                b = True
            elif cond == "half":
                b = lane < 16
            elif cond == "odd":
                b = t % 2 == 1
            elif cond == "warp":
                b = w % 2 == 1
            elif cond == "data":
                b = r() < p
            else:
                raise ValueError(cond)
            mask.append(b)
        n_t = sum(mask)
        n_f = 32 - n_t
        seq = [("pre", 32)] * pre
        if n_t:
            seq += [("then", n_t)] * then
        if n_f:
            seq += [("else", n_f)] * other
        seq += [("post", 32)] * post
        wi = len(seq)
        wa = sum(a for _, a in seq)
        issued += wi
        active += wa
        steps.append([kind for kind, _ in seq])
        out.append({"mask": "".join("1" if b else "0" for b in mask), "issued": wi, "active": wa})
    return {"warps": out, "issued": issued, "active": active, "eff": active / (32 * issued), "steps": steps}


def addresses(kind="contiguous", size=4, k=1, offset=0, struct=16, seed=1, base=0):
    """部分 ③：一个线程束 32 个线程各读一个元素的字节地址。
    kind: 'contiguous' 第 i 个线程读第 i 个元素；'stride' 读第 k·i 个；'offset' 整体错开 offset 字节；
          'aos' 结构体数组（每个结构体 struct 字节，读同一字段）；'random' 在 32·k 个元素里随机读（mulberry32，种子 seed）。"""
    r = rng(seed)
    out = []
    for i in range(32):
        if kind == "contiguous":
            a = i * size
        elif kind == "stride":
            a = i * k * size
        elif kind == "offset":
            a = i * size + offset
        elif kind == "aos":
            a = i * struct
        elif kind == "random":
            a = int(r() * 32 * k) * size
        else:
            raise ValueError(kind)
        out.append(base + a)
    return out


def coalesce(addrs, size=4):
    """一个线程束的一次读：每个地址读 size 字节。显存按 32 字节扇区搬运，按 128 字节缓存行组织。
    返回扇区数、缓存行数、请求的字节、搬运的字节与有效带宽比（请求 ÷ 搬运）。"""
    sectors, lines = set(), set()
    for a in addrs:
        for sct in range(a // 32, (a + size - 1) // 32 + 1):      # 这次读用到的每个扇区
            sectors.add(sct)
            lines.add(sct // 4)
    req = len(addrs) * size
    moved = len(sectors) * 32
    return {"sectors": len(sectors), "lines": len(lines), "requested": req, "moved": moved, "eff": req / moved,
            "sector_list": sorted(sectors)}


def bank_words(kind="stride", k=1, pad=0, col=0, seed=1):
    """部分 ④：一个线程束 32 个线程访问共享内存的 4 字节字地址（字的序号）。
    kind: 'stride' 第 i 个线程访问第 k·i 个字；'column' 读 32×(32+pad) 的二维数组的第 col 列（第 i 个线程读第 i 行）；
          'same' 全部读同一个字（广播）；'random' 在 1024 个字里随机。"""
    r = rng(seed)
    out = []
    for i in range(32):
        if kind == "stride":
            w = i * k
        elif kind == "column":
            w = i * (32 + pad) + col
        elif kind == "same":
            w = col
        elif kind == "random":
            w = int(r() * 1024)
        else:
            raise ValueError(kind)
        out.append(w)
    return out


def banks(words, nbanks=32):
    """共享内存 nbanks 个存储体，字 w 在存储体 w % nbanks。同一存储体的不同字要分几次读，同一个字广播（只算一次）。
    返回冲突路数 ways（= 读完要几次）、每个存储体被访问的不同字数。"""
    per = [set() for _ in range(nbanks)]
    for w in words:
        per[w % nbanks].add(w)
    load = [len(s) for s in per]
    return {"ways": max(load), "load": load}
