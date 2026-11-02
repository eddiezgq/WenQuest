"""第 17 轮附三 6h：用 ngspice + SKY130（tt，27 °C）测第 7 章的 SRAM 参数。

器件：nfet_01v8 / pfet_01v8，L = 0.15 μm。6 管单元：存取管 Wpg = 0.42 μm，下拉管 Wpd = CR·Wpg，上拉管 Wpu = PR·Wpg。
1. 蝴蝶曲线与静态噪声容限 SNM（Seevinck 法：把两条传输特性旋转 45°，两瓣里最大的差除以 √2，取两瓣的小者）：
   半边单元的传输特性用 DC 扫描得到——保持：字线 = 0；读出：字线 = VDD、位线 = VDD（存取管把位线接到输出端）。
   单元对称，两条曲线互为镜像。CR = 1、1.25、1.5、2、2.5、3，PR = 1；另测 CR = 2 时 VDD = 0.9、1.2、1.5、1.8 V 的读出与保持 SNM。
2. 写入裕量：整个单元，Q 初始为 1，BLB = VDD、字线 = VDD，BL 从 VDD 往 0 扫，Q 跌过 VDD/2 时 BL 的电压（越高越容易写）。
   PR = 1、1.5、2、3，CR = 2。
3. 读电流：CR = 2、PR = 1，Q = 0，字线、两条位线都为 VDD 时从 BL 流进单元的电流。
4. 位线（存取管接位线一端给出扩散区面积与周长，见 DIFF_L）：一条位线挂 N = 64、128、256 个单元（只有一个被选中、存 0，其余字线 = 0、存 1），位线预充到 VDD 后打开字线，
   位线掉 100 mV 的时间 t；对 N 线性拟合，斜率 × I / ΔV 是每个单元给位线添的电容（I 为第 3 项的读电流；仿真里没有导线），
   截距 t_bl0 是与行数无关的起步时间（从字线斜坡过半到存取管导通、Q 被抬起）。
5. 灵敏放大器：锁存型（交叉耦合反相器 Wn = 0.84、Wp = 0.84 μm，尾管 Wn = 1.68 μm，每个输出另挂 2 fF），两个输出初值
   VDD 与 VDD − ΔV，使能上升（20 ps）后两个输出之差达到 VDD/2 的时间，ΔV = 25、50、100、200 mV。
结果写 calib/sram.json，要点写进 params.json 的 sram_sim；--check 只与仓库比较（镜像验收用，相差 > 15 % 报错）。
运行：SKY130_LIB=… 或 SKY130_INCLUDE=… python calib_sram.py（约 1 分钟）
"""
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import calib  # noqa: E402

OUT = Path(os.environ.get("CALIB_OUT", HERE))
PARAMS = HERE.parents[3] / "labs/micro/kit/models/params.json"
VDD, WPG = 1.8, 0.42
nmos, pmos = calib.nmos, calib.pmos
CRS = [1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
PRS = [1.0, 1.5, 2.0, 3.0]
NS = [64, 128, 256]
DVS = [0.025, 0.05, 0.1, 0.2]
VDDS = [0.9, 1.2, 1.5, 1.8]


def w(x):
    return round(x * WPG, 3)


# ------------------------------------------------------------------ 1 蝴蝶曲线与 SNM
def half_vtc(cr, pr, mode, vdd=VDD):
    wl = vdd if mode == "read" else 0.0
    body = f"Vdd vdd 0 {vdd}\nVbl bl 0 {vdd}\nVwl wl 0 {wl}\nVin a 0 0\n"
    body += nmos("PD", "y", "a", "0", w(cr)) + pmos("PU", "y", "a", "vdd", w(pr)) + nmos("PG", "bl", "wl", "y", WPG)
    _, f = calib.run(body, f"dc Vin 0 {vdd} 0.002\nwrdata vtc.dat v(y)")
    rows = calib.table(f["vtc.dat"])
    return [r[0] for r in rows], [r[1] for r in rows]


def snm(xs, ys, vdd=VDD):
    """Seevinck：曲线 A 为 (x, f(x))，曲线 B 为它的镜像 (f(y), y)。转 45°：u = (x − y)/√2，v = (x + y)/√2。
    两条曲线在同一 u 上的 v 之差，在 u > 0、u < 0 两侧各取最大，除以 √2 即两瓣里最大正方形的边长；取较小的一瓣。
    （与 textbook/dic/conventions/mos.py 的 sram_snm 同一算法。）"""
    s2 = math.sqrt(2)
    a = sorted(((x - y) / s2, (x + y) / s2) for x, y in zip(xs, ys))
    b = sorted(((y - x) / s2, (y + x) / s2) for x, y in zip(xs, ys))

    def at(c, u):
        if u <= c[0][0] or u >= c[-1][0]:
            return None
        lo, hi = 0, len(c) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if c[m][0] <= u:
                lo = m
            else:
                hi = m
        t = (u - c[lo][0]) / (c[hi][0] - c[lo][0]) if c[hi][0] > c[lo][0] else 0.0
        return c[lo][1] + t * (c[hi][1] - c[lo][1])
    pos = neg = 0.0
    n = 2000
    umax = vdd / s2
    for i in range(1, n):
        u = -umax + 2 * umax * i / n
        va, vb = at(a, u), at(b, u)
        if va is None or vb is None:
            continue
        d = va - vb
        pos, neg = max(pos, d), max(neg, -d)
    return min(pos, neg) / s2


# ------------------------------------------------------------------ 2 写入裕量
# 存取管接位线的那一端的扩散区：位线接触由上下相邻两个单元共用，每个单元约分到 0.27 μm 长（接触孔 0.17 μm 加两侧间距的一半，近似）。
# 其余管子不给扩散区几何（与前几章的校准相同，只影响位线电容这一项）。
DIFF_L = 0.27


def pg(name, bl, wl, q):
    a, pp = round(WPG * DIFF_L, 4), round(2 * DIFF_L + WPG, 3)
    return f"X{name} {bl} {wl} {q} 0 {calib.NF} W={WPG} L={calib.L} nf=1 ad={a} pd={pp}\n"


def cell(name, q, qb, bl, blb, wl, cr, pr):
    return (nmos(name + "D1", q, qb, "0", w(cr)) + pmos(name + "U1", q, qb, "vdd", w(pr)) + pg(name + "G1", bl, wl, q) +
            nmos(name + "D2", qb, q, "0", w(cr)) + pmos(name + "U2", qb, q, "vdd", w(pr)) + pg(name + "G2", blb, wl, qb))


def write_trip(cr, pr):
    body = f"Vdd vdd 0 {VDD}\nVbl bl 0 {VDD}\nVblb blb 0 {VDD}\nVwl wl 0 {VDD}\n" + cell("C", "q", "qb", "bl", "blb", "wl", cr, pr)
    body += f".nodeset v(q)={VDD} v(qb)=0\n"
    _, f = calib.run(body, "dc Vbl 1.8 0 -0.002\nwrdata wt.dat v(q)")
    rows = calib.table(f["wt.dat"])
    for r in rows:
        if r[1] < VDD / 2:
            return r[0]
    return 0.0


# ------------------------------------------------------------------ 3 读电流
def read_current(cr=2.0, pr=1.0):
    body = f"Vdd vdd 0 {VDD}\nVbl bl 0 {VDD}\nVblb blb 0 {VDD}\nVwl wl 0 {VDD}\n" + cell("C", "q", "qb", "bl", "blb", "wl", cr, pr)
    body += f".nodeset v(q)=0 v(qb)={VDD}\n"
    out, _ = calib.run(body, "op\nprint -i(Vbl)")
    import re
    m = re.search(r"-i\(vbl\)\s*=\s*([-\d.e+]+)", out, re.I)
    return float(m.group(1))


# ------------------------------------------------------------------ 4 位线
def bitline(n, cr=2.0, pr=1.0, dv=0.1):
    body = f"Vdd vdd 0 {VDD}\nVblb blb 0 {VDD}\nVwl wl 0 PULSE(0 {VDD} 50p 20p 20p 20n 40n)\nCb0 bl 0 0.1f\n"
    ic = ["v(bl)=1.8"]
    body += cell("S", "q0", "qb0", "bl", "blb", "wl", cr, pr)
    ic += ["v(q0)=0", f"v(qb0)={VDD}"]
    for k in range(1, n):
        body += cell(f"X{k}", f"q{k}", f"qb{k}", "bl", "blb", "0", cr, pr)
        ic += [f"v(q{k})={VDD}", f"v(qb{k})=0"]
    body += ".ic " + " ".join(ic) + "\n"
    out, _ = calib.run(body, f"tran 1p 6n uic\nmeas tran t when v(bl)={VDD - dv} fall=1\nmeas tran t0 when v(wl)=0.9 rise=1")
    t = calib_num(out, "t") - calib_num(out, "t0")
    return t


def calib_num(out, key):
    import re
    m = re.search(rf"^\s*{key}\s*=\s*([-\d.e+]+)", out, re.M)
    return float(m.group(1))


# ------------------------------------------------------------------ 5 灵敏放大器
def sense(dv):
    body = (f"Vdd vdd 0 {VDD}\nVen en 0 PULSE(0 {VDD} 50p 20p 20p 5n 10n)\n"
            + nmos("N1", "o", "ob", "t", 0.84) + pmos("P1", "o", "ob", "vdd", 0.84)
            + nmos("N2", "ob", "o", "t", 0.84) + pmos("P2", "ob", "o", "vdd", 0.84)
            + nmos("T", "t", "en", "0", 1.68) + "Co o 0 2f\nCob ob 0 2f\n"
            + f".ic v(o)={VDD} v(ob)={VDD - dv} v(t)=0\n")
    out, _ = calib.run(body, f"tran 0.5p 3n uic\nmeas tran t0 when v(en)=0.9 rise=1\n"
                             f"let d = v(o) - v(ob)\nmeas tran t1 when d=0.9 rise=1")
    return calib_num(out, "t1") - calib_num(out, "t0")


def main():
    res = {"snm_hold": [], "snm_read": [], "write": [], "curves": {}}
    for cr in CRS:
        xh, yh = half_vtc(cr, 1.0, "hold")
        xr, yr = half_vtc(cr, 1.0, "read")
        res["snm_hold"].append([cr, round(snm(xh, yh), 4)])
        res["snm_read"].append([cr, round(snm(xr, yr), 4)])
        if cr in (1.0, 2.0):
            k = 10   # 每 20 mV 取一点，给实验的“仿真曲线”用
            res["curves"][f"hold_{cr:g}"] = [round(v, 4) for v in yh[::k]]
            res["curves"][f"read_{cr:g}"] = [round(v, 4) for v in yr[::k]]
        print(f"CR {cr}: SNM 保持 {res['snm_hold'][-1][1] * 1e3:.0f} mV，读 {res['snm_read'][-1][1] * 1e3:.0f} mV")
    res["snm_vdd"] = []
    for v in VDDS:
        xh, yh = half_vtc(2.0, 1.0, "hold", v)
        xr, yr = half_vtc(2.0, 1.0, "read", v)
        res["snm_vdd"].append([v, round(snm(xr, yr, v), 4), round(snm(xh, yh, v), 4)])
        print(f"VDD {v} V（CR = 2）：SNM 读 {res['snm_vdd'][-1][1] * 1e3:.0f} mV，保持 {res['snm_vdd'][-1][2] * 1e3:.0f} mV")
    for pr in PRS:
        res["write"].append([pr, round(write_trip(2.0, pr), 4)])
        print(f"PR {pr}: 写入裕量（位线翻转电压） {res['write'][-1][1] * 1e3:.0f} mV")
    i = read_current()
    res["i_read"] = i
    ts = [bitline(n) for n in NS]
    # t = (C0 + N·Cc)·ΔV / I：对 N 线性拟合
    mx, my = sum(NS) / len(NS), sum(ts) / len(ts)
    sl = sum((x - mx) * (y - my) for x, y in zip(NS, ts)) / sum((x - mx) ** 2 for x in NS)
    res["bl_t"] = [[n, t] for n, t in zip(NS, ts)]
    res["c_cell"] = sl * i / 0.1
    res["t_bl0"] = my - sl * mx          # 截距：与行数无关的起步时间（字线斜坡过半到存取管导通、Q 被抬起），不是电容
    print(f"读电流 {i * 1e6:.1f} μA；位线掉 100 mV：" + "，".join(f"{n} 行 {t * 1e12:.0f} ps" for n, t in zip(NS, ts))
          + f"；每单元 {res['c_cell'] * 1e15:.3f} fF")
    res["sa"] = [[dv, sense(dv)] for dv in DVS]
    print("灵敏放大器：" + "，".join(f"{dv * 1e3:.0f} mV {t * 1e12:.0f} ps" for dv, t in res["sa"]))
    (OUT / "sram.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    params = json.loads(PARAMS.read_text(encoding="utf-8"))
    keep = {"_note": "第 7 章 6 管 SRAM 单元按 SKY130 tt、27 °C 仿真（samples/数字集成电路设计/生成脚本/calib/calib_sram.py）："
                     "SNM 与写入裕量（V），读电流（A），每单元位线电容（F，只含存取管漏极，不含导线），位线的起步时间 t_bl0（s），位线掉 100 mV 的时间与灵敏放大器分辨时间（s）",
            "snm_hold": res["snm_hold"], "snm_read": res["snm_read"], "snm_vdd": res["snm_vdd"], "write": res["write"],
            "i_read": float(f"{i:.4g}"), "c_cell": float(f"{res['c_cell']:.4g}"), "t_bl0": float(f"{res['t_bl0']:.4g}"),
            "bl_t": [[n, float(f"{t:.4g}")] for n, t in res["bl_t"]], "sa": [[dv, float(f"{t:.4g}")] for dv, t in res["sa"]],
            "curves": res["curves"]}
    if "--check" in sys.argv:
        old = params.get("sram_sim", {})

        def flat(d, k=""):
            if isinstance(d, (int, float)):
                yield k, float(d)
            elif isinstance(d, list):
                for j, x in enumerate(d):
                    yield from flat(x, f"{k}[{j}]")
            elif isinstance(d, dict):
                for kk, x in d.items():
                    if kk not in ("_note", "curves"):
                        yield from flat(x, f"{k}.{kk}")
        o, n = dict(flat(old)), dict(flat(keep))
        bad = [f"{k}: {o.get(k)} → {v:.4g}" for k, v in n.items() if k not in o or abs(o[k] - v) > 0.15 * max(abs(v), 1e-3 if "snm" in k or "write" in k else 1e-30)]
        print("SRAM 参数与仓库一致" if not bad else "SRAM 参数不一致：" + "；".join(bad))
        if bad:
            sys.exit(1)
    else:
        params["sram_sim"] = keep
        PARAMS.write_text(json.dumps(params, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
