"""第 17 轮附三 6g：第 6 章算术电路的综合数据（Yosys + ABC，按 SKY130 标准单元库 sky130_fd_sc_hd 的 tt_025C_1v80 映射）。

程序生成各结构的门级 Verilog（只用与、或、异或、非和二选一，结构写死）。Yosys 只做展开和逐门映射（不调用 synth，
synth 里的 ABC 会把进位选择这类结构按逻辑等价改写成行波进位），ABC 做“结构哈希 → 映射 → 插缓冲 → 调整单元尺寸”（追求延时），不做全局重构，
所以比较的是结构本身。记录面积（μm²，单元库面积之和）、ABC 按单元库估算的最长延时（ps）与单元数；
另按“只求面积最小”（map -a，最小尺寸单元，不插缓冲）再映射一次，记录 area_min 与对应的 delay_amin；
书中算例的位宽再按时间预算（tgt_…，ABC 以预算为目标映射、调尺寸）综合一次。
  加法器（n = 8、16、32）：rca 行波进位；cla 四位一组超前进位（组内传播先算好，组进位只经一级与门和或门）、组间行波；csel 四位一组进位选择；bk Brent–Kung；ks Kogge–Stone。
  乘法器（无符号，n = 8、16）：array 进位保留阵列 + 行波进位；dadda 部分积按 Dadda 方案逐层压缩（全加器/半加器树）+ Kogge–Stone；
                               booth 基 4 Booth 编码（部分积约减半）+ 同样的压缩树与加法器。
  其他（16 位）：shift 对数移位器（左移 0–15 位）；cmp_rc 行波比较器（a < b）；cmp_ks 前缀比较器。
每个结构先用 Icarus Verilog 测试边界数（全 1 加 1 等）与 2000 组随机数（--verify 时），再综合。结果写 calib/arith.json，要点写进 params.json 的 arith_syn；
--check 只与仓库比较（镜像验收用，相差 > 10 % 报错）。
运行：SKY130_HD_LIB=<sky130_fd_sc_hd__tt_025C_1v80.lib> python arith.py [--verify] [--check]
"""
import json
import os
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("CALIB_OUT", HERE))
PARAMS = HERE.parents[3] / "labs/micro/kit/models/params.json"


class Net:
    """极简门级网表：每个门一条 assign。"""

    def __init__(self):
        self.lines, self.k = [], 0

    def w(self, expr):
        self.k += 1
        name = f"n{self.k}"
        self.lines.append(f"  wire {name} = {expr};")
        return name

    def AND(self, a, b): return self.w(f"{a} & {b}")
    def OR(self, a, b): return self.w(f"{a} | {b}")
    def XOR(self, a, b): return self.w(f"{a} ^ {b}")
    def NOT(self, a): return self.w(f"~{a}")
    def MUX(self, s, a0, a1): return self.w(f"{s} ? {a1} : {a0}")

    def FA(self, a, b, c):
        t = self.XOR(a, b)
        return self.XOR(t, c), self.OR(self.AND(a, b), self.AND(t, c))

    def HA(self, a, b):
        return self.XOR(a, b), self.AND(a, b)


# ------------------------------------------------------------------ 加法器（返回 n 位和与进位）
def adder(net, kind, a, b, cin):
    n = len(a)
    g = [net.AND(a[i], b[i]) for i in range(n)]
    p = [net.XOR(a[i], b[i]) for i in range(n)]
    c = [cin]
    if kind == "rca":
        for i in range(n):
            c.append(net.OR(g[i], net.AND(p[i], c[i])))
    elif kind == "cla":
        for blk in range(0, n, 4):
            c0 = c[blk]
            for i in range(blk, min(blk + 4, n)):
                term = g[i]
                for j in range(i - 1, blk - 1, -1):          # g_j·p_{j+1}…p_i（不经过 c0）
                    t = g[j]
                    for k in range(j + 1, i + 1):
                        t = net.AND(t, p[k])
                    term = net.OR(term, t)
                pg = p[blk]                                  # 组内传播 p_blk…p_i，先算好，c0 最后才进来
                for k in range(blk + 1, i + 1):
                    pg = net.AND(pg, p[k])
                c.append(net.OR(term, net.AND(pg, c0)))
    elif kind == "csel":
        s = []
        for blk in range(0, n, 4):
            hi = min(blk + 4, n)
            if blk == 0:
                cc = cin
                for i in range(blk, hi):
                    s.append(net.XOR(p[i], cc)); cc = net.OR(g[i], net.AND(p[i], cc))
                cprev = cc
                continue
            res = []
            for cv in ("1'b0", "1'b1"):
                cc, ss = cv, []
                for i in range(blk, hi):
                    ss.append(net.XOR(p[i], cc)); cc = net.OR(g[i], net.AND(p[i], cc))
                res.append((ss, cc))
            s += [net.MUX(cprev, res[0][0][k], res[1][0][k]) for k in range(hi - blk)]
            cprev = net.MUX(cprev, res[0][1], res[1][1])
        return s, cprev
    elif kind in ("ks", "bk"):
        G = list(g); P = list(p)
        G[0] = net.OR(g[0], net.AND(p[0], cin))        # 把进位输入并进第 0 位
        if kind == "ks":
            d = 1
            while d < n:
                G2, P2 = list(G), list(P)
                for i in range(d, n):
                    G2[i] = net.OR(G[i], net.AND(P[i], G[i - d]))
                    P2[i] = net.AND(P[i], P[i - d])
                G, P = G2, P2
                d *= 2
        else:                                            # Brent–Kung：上扫 + 下扫
            d = 1
            while d < n:
                for i in range(2 * d - 1, n, 2 * d):
                    G[i] = net.OR(G[i], net.AND(P[i], G[i - d])); P[i] = net.AND(P[i], P[i - d])
                d *= 2
            d //= 2
            while d >= 1:
                for i in range(3 * d - 1, n, 2 * d):
                    G[i] = net.OR(G[i], net.AND(P[i], G[i - d])); P[i] = net.AND(P[i], P[i - d])
                d //= 2
        c += G
    else:
        raise ValueError(kind)
    s = [net.XOR(p[i], c[i]) for i in range(n)]
    return s, c[n]


def make_adder(kind, n):
    net = Net()
    a = [f"a[{i}]" for i in range(n)]; b = [f"b[{i}]" for i in range(n)]
    s, co = adder(net, kind, a, b, "cin")
    body = "\n".join(net.lines) + "\n" + "\n".join(f"  assign s[{i}] = {s[i]};" for i in range(n)) + f"\n  assign cout = {co};"
    return f"module top(input [{n - 1}:0] a, b, input cin, output [{n - 1}:0] s, output cout);\n{body}\nendmodule\n"


# ------------------------------------------------------------------ 乘法器
def compress(net, cols):
    """Dadda 压缩：目标高度取序列 2、3、4、6、9、13、19……中小于当前最高列的各项，逐层压到目标。
    每层只用上一层的位作输入（本层产生的和、进位留到下一层），低位列的进位计入高一列的高度。"""
    seq = [2]
    while seq[-1] < max(len(c) for c in cols):
        seq.append(seq[-1] * 3 // 2)
    for target in reversed(seq[:-1]):
        new = [[] for _ in range(len(cols) + 1)]
        for k in range(len(cols)):
            old = list(cols[k])
            while len(old) + len(new[k]) > target:
                if len(old) + len(new[k]) - target >= 2 and len(old) >= 3:
                    s_, c_ = net.FA(old.pop(), old.pop(), old.pop())
                elif len(old) >= 2:
                    s_, c_ = net.HA(old.pop(), old.pop())
                else:
                    break
                new[k].append(s_); new[k + 1].append(c_)
            new[k] += old
        cols = new[:len(cols)]
    return cols


def final_add(net, cols, width, kind):
    a = [cols[k][0] if len(cols[k]) > 0 else "1'b0" for k in range(width)]
    b = [cols[k][1] if len(cols[k]) > 1 else "1'b0" for k in range(width)]
    s, _ = adder(net, kind, a, b, "1'b0")
    return s


def make_mult(kind, n):
    net = Net()
    W = 2 * n
    A = [f"a[{i}]" for i in range(n)]; B = [f"b[{i}]" for i in range(n)]
    cols = [[] for _ in range(W)]
    if kind in ("array", "dadda"):
        rows = [[(i + j, net.AND(A[j], B[i])) for j in range(n)] for i in range(n)]
        if kind == "dadda":
            for r in rows:
                for k, x in r:
                    cols[k].append(x)
            out = final_add(net, compress(net, cols), W, "ks")
        else:                                            # 进位保留阵列：逐行用全加器累加，最后一行行波进位
            S = ["1'b0"] * W; C = ["1'b0"] * W
            for r in rows:
                nS, nC = list(S), ["1'b0"] * W
                for k, x in r:
                    if S[k] == "1'b0" and C[k] == "1'b0":
                        nS[k] = x
                    elif C[k] == "1'b0":
                        nS[k], cc = net.HA(S[k], x); nC[k + 1] = cc
                    else:
                        nS[k], cc = net.FA(S[k], C[k], x); nC[k + 1] = cc
                for k in range(W):                       # 不在本行的列：上一行的进位留到下一行
                    if all(k != kk for kk, _ in r) and C[k] != "1'b0":
                        if nS[k] == "1'b0":
                            nS[k] = C[k]
                        else:
                            nS[k], cc = net.HA(nS[k], C[k]); nC[k + 1] = cc if nC[k + 1] == "1'b0" else net.OR(nC[k + 1], cc)
                S, C = nS, nC
            out = final_add(net, [[S[k], C[k]] for k in range(W)], W, "rca")
    elif kind == "booth":
        Bx = ["1'b0"] + B + ["1'b0", "1'b0"]           # b[-1] = 0，高位补 0（无符号）
        nd = n // 2 + 1
        const = 0
        for i in range(nd):
            b0, b1, b2 = Bx[2 * i], Bx[2 * i + 1], Bx[2 * i + 2]      # b(2i−1), b(2i), b(2i+1)
            one = net.XOR(b1, b0)
            two = net.OR(net.AND(b2, net.AND(net.NOT(b1), net.NOT(b0))), net.AND(net.NOT(b2), net.AND(b1, b0)))
            neg = b2
            Ax = ["1'b0"] + A + ["1'b0", "1'b0"]         # Ax[j] = A[j−1]，高位补 0；部分积取 n + 2 位二进制补码
            for j in range(n + 2):
                bit = net.XOR(net.OR(net.AND(one, Ax[j + 1]), net.AND(two, Ax[j])), neg)
                pos = 2 * i + j
                if j == n + 1:                           # 最高位（符号位）权重为负：放 ~bit，常数里减去 2^pos
                    bit = net.NOT(bit); const -= 1 << pos
                if pos < W:
                    cols[pos].append(bit)
            if 2 * i < W:
                cols[2 * i].append(neg)                  # 取反加 1 的“加 1”
        const %= 1 << W
        for k in range(W):
            if const >> k & 1:
                cols[k].append("1'b1")
        out = final_add(net, compress(net, cols), W, "ks")
    else:
        raise ValueError(kind)
    body = "\n".join(net.lines) + "\n" + "\n".join(f"  assign p[{k}] = {out[k]};" for k in range(W))
    return f"module top(input [{n - 1}:0] a, b, output [{W - 1}:0] p);\n{body}\nendmodule\n"


# ------------------------------------------------------------------ 移位器与比较器
def make_shift(n=16):
    net = Net()
    x = [f"a[{i}]" for i in range(n)]
    for lv in range(4):
        d = 1 << lv
        x = [net.MUX(f"sh[{lv}]", x[i], x[i - d] if i >= d else "1'b0") for i in range(n)]
    body = "\n".join(net.lines) + "\n" + "\n".join(f"  assign y[{i}] = {x[i]};" for i in range(n))
    return f"module top(input [{n - 1}:0] a, input [3:0] sh, output [{n - 1}:0] y);\n{body}\nendmodule\n"


def make_cmp(kind, n=16):
    """a < b ⇔ a + ~b + 1 不产生进位（无符号）。"""
    net = Net()
    a = [f"a[{i}]" for i in range(n)]
    nb = [net.NOT(f"b[{i}]") for i in range(n)]
    _, co = adder(net, kind, a, nb, "1'b1")
    lt = net.NOT(co)
    return f"module top(input [{n - 1}:0] a, b, output lt);\n" + "\n".join(net.lines) + f"\n  assign lt = {lt};\nendmodule\n"


def designs():
    d = {}
    for n in (8, 16, 32):
        for k in ("rca", "cla", "csel", "bk", "ks"):
            d[f"add_{k}_{n}"] = ("add", n, make_adder(k, n))
    for n in (8, 16):
        for k in ("array", "dadda", "booth"):
            d[f"mul_{k}_{n}"] = ("mul", n, make_mult(k, n))
    d["shift_16"] = ("shift", 16, make_shift(16))
    d["cmp_rca_16"] = ("cmp", 16, make_cmp("rca", 16))
    d["cmp_ks_16"] = ("cmp", 16, make_cmp("ks", 16))
    return d


# ------------------------------------------------------------------ 验证与综合
def verify(name, kind, n, src):
    rnd = random.Random(1)
    vecs = []
    m = (1 << n) - 1
    edge = [(m, 1), (m, m), (0, m), (1, m), (m, 0), (0, 0), (1 << (n - 1), 1 << (n - 1)), (m >> 1, 1)]
    for t in range(2000 + len(edge)):
        a, b = edge[t] if t < len(edge) else (rnd.getrandbits(n), rnd.getrandbits(n))
        if kind == "add":
            c = 1 if t < len(edge) else rnd.getrandbits(1); vecs.append((a, b, c, (a + b + c) & ((1 << (n + 1)) - 1)))
        elif kind == "mul":
            vecs.append((a, b, 0, a * b))
        elif kind == "shift":
            s = rnd.getrandbits(4); vecs.append((a, s, 0, (a << s) & ((1 << n) - 1)))
        else:
            vecs.append((a, b, 0, int(a < b)))
    if kind == "add":
        ports = f"reg [{n - 1}:0] a, b; reg cin; wire [{n - 1}:0] s; wire cout; top u(.a(a), .b(b), .cin(cin), .s(s), .cout(cout));"
        chk = lambda a, b, c, r: f"a={a}; b={b}; cin={c}; #1; if ({{cout, s}} !== {r}) begin $display(\"FAIL\"); $finish; end"  # noqa: E731
    elif kind == "mul":
        ports = f"reg [{n - 1}:0] a, b; wire [{2 * n - 1}:0] p; top u(.a(a), .b(b), .p(p));"
        chk = lambda a, b, c, r: f"a={a}; b={b}; #1; if (p !== {r}) begin $display(\"FAIL\"); $finish; end"  # noqa: E731
    elif kind == "shift":
        ports = f"reg [{n - 1}:0] a; reg [3:0] b; wire [{n - 1}:0] y; top u(.a(a), .sh(b), .y(y));"
        chk = lambda a, b, c, r: f"a={a}; b={b}; #1; if (y !== {r}) begin $display(\"FAIL\"); $finish; end"  # noqa: E731
    else:
        ports = f"reg [{n - 1}:0] a, b; wire lt; top u(.a(a), .b(b), .lt(lt));"
        chk = lambda a, b, c, r: f"a={a}; b={b}; #1; if (lt !== {r}) begin $display(\"FAIL\"); $finish; end"  # noqa: E731
    tb = f"module tb; {ports}\ninitial begin\n" + "\n".join(chk(*v) for v in vecs) + '\n$display("PASS"); $finish; end\nendmodule\n'
    with tempfile.TemporaryDirectory() as d:
        Path(d, "dut.v").write_text(src); Path(d, "tb.v").write_text(tb)
        subprocess.run(["iverilog", "-o", "sim", "dut.v", "tb.v"], cwd=d, check=True)
        r = subprocess.run(["vvp", "sim"], cwd=d, capture_output=True, text=True)
        if "PASS" not in r.stdout:
            raise SystemExit(f"{name} 验证失败")


def _run(src, lib, script):
    with tempfile.TemporaryDirectory() as d:
        Path(d, "dut.v").write_text(src)
        cmd = (f"read_verilog dut.v; proc; flatten; techmap; opt_clean; "
               f"abc -liberty {lib} -script {script}; stat -liberty {lib}")
        r = subprocess.run(["yosys", "-p", cmd], cwd=d, capture_output=True, text=True, timeout=1200)
        log = r.stdout + r.stderr
    dl = re.findall(r"Delay =\s*([\d.]+) ps", log)
    ar = re.findall(r"Chip area for module '\\top': ([\d.]+)", log)
    # 单元个数：旧版 Yosys 写“Number of cells: N”，新版（镜像里的）写“N cells”
    nc = re.findall(r"Number of cells:\s+(\d+)", log) or re.findall(r"^\s*(\d+)\s+cells\s*$", log, re.M)
    if not dl or not ar:
        raise SystemExit("综合失败：\n" + log[-2000:])
    return float(dl[-1]), float(ar[-1]), int(nc[-1]) if nc else 0


def synth(src, lib):
    """两种映射：追求延时（插缓冲、调尺寸）与追求面积（map -a，最小尺寸单元）。"""
    d1, a1, c1 = _run(src, lib, "+strash;map;topo;buffer,-p;upsize;dnsize;stime,-p")
    d2, a2, _ = _run(src, lib, "+strash;map,-a;topo;stime,-p")
    return {"area": round(a1, 1), "delay": round(d1, 1), "cells": c1, "area_min": round(a2, 1), "delay_amin": round(d2, 1)}


def budgets():
    """书中两个算例的时间预算（ps）：时钟周期 − 第 3 章触发器的 tcq − tsu（与 textbook/dic/conventions/mos.py 相同的算法）。"""
    sys.path.insert(0, str(HERE.parents[3] / "textbook/dic/conventions"))
    import mos  # noqa: E402
    ff = mos.ff_timing()
    pr = mos.P["problems"]
    b = lambda f: round((1 / (f * 1e6) - ff["tcq"] - ff["tsu"]) * 1e12)  # noqa: E731
    return {"add_32": b(pr["p61"]["f_MHz"]), "mul_16": b(pr["p63"]["f_MHz"])}


def main():
    lib = os.environ.get("SKY130_HD_LIB")
    if not lib:
        sys.exit("set SKY130_HD_LIB")
    res = {}
    for name, (kind, n, src) in designs().items():
        if "--verify" in sys.argv:
            verify(name, kind, n, src)
        res[name] = synth(src, lib)
        r = res[name]
        print(f"{name:14s} 面积 {r['area']:9.1f} μm²  延时 {r['delay']:7.1f} ps  单元 {r['cells']}  |  最小面积 {r['area_min']:9.1f}  延时 {r['delay_amin']:7.1f}")
    # 按预算综合（ABC 以预算为目标映射、调尺寸，满足后回收面积）：书中算例 6.1.2、6.3.1 用
    bud = budgets()
    for name, D in bud.items():
        kind, n = name.split("_"); n = int(n)
        kinds = ("rca", "cla", "csel", "bk", "ks") if kind == "add" else ("array", "dadda", "booth")
        for k in kinds:
            src = make_adder(k, n) if kind == "add" else make_mult(k, n)
            dl, ar, nc = _run(src, lib, f"+strash;map,-D,{D};topo;buffer,-p;upsize,-D,{D};dnsize,-D,{D};stime,-p")
            res[f"tgt_{kind}_{k}_{n}"] = {"area": round(ar, 1), "delay": round(dl, 1), "cells": nc, "area_min": round(ar, 1), "delay_amin": round(dl, 1), "target": D}
            print(f"按预算 {D} ps：{kind}_{k}_{n:<3d} 面积 {ar:9.1f}  延时 {dl:7.1f}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "arith.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    params = json.loads(PARAMS.read_text(encoding="utf-8"))
    keep = {"_note": "第 6 章算术电路按 SKY130 sky130_fd_sc_hd（tt_025C_1v80）综合的面积（μm²）、最长延时（ps，ABC 估算，含插缓冲与尺寸调整）与单元数"
                     "（samples/数字集成电路设计/生成脚本/calib/arith.py）", **res}
    if "--check" in sys.argv:
        old = params.get("arith_syn", {})
        bad = [f"{k}: {old.get(k)} → {v}" for k, v in res.items()
               if k not in old or any(abs(old[k].get(f, 0) - v[f]) > 0.1 * v[f] for f in ("area", "delay", "area_min", "delay_amin"))]
        print("算术电路综合结果与仓库一致" if not bad else "算术电路综合结果不一致：" + "；".join(bad))
        if bad:
            sys.exit(1)
    else:
        params["arith_syn"] = keep
        PARAMS.write_text(json.dumps(params, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
