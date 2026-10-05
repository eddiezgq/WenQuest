"""第 17 轮附三 6e：用 ngspice + SKY130（tt，27 °C）测第 3 章的触发器时序参数。

被测电路：传输门主从 D 触发器（上升沿触发）。主锁存器在 CLK = 0 时透明，从锁存器在 CLK = 1 时透明；
所有反相器取参考尺寸（Wn = 0.42 μm、Wp = r·Wn），传输门的 NMOS、PMOS 也取参考尺寸。数据和时钟都经反相器整形，
输出 Q 带一个 FO4 负载。
1. tcq：数据早到时，时钟上升沿到 Q 的 50 % 延时（上升、下降取平均）；
2. 建立时间 tsu：数据上升沿越来越靠近时钟沿，tcq 比早到时大 10 % 的那个间隔；
3. 保持时间 th：数据在时钟沿之后才变走，要采到原值且 tcq 不超过 1.1 倍时，数据至少要保持多久（可以为负）；
4. 亚稳态：二分法找到采样结果翻转的临界间隔 Δc，在 Δc 附近测 tcq = a − τm·ln(Δ − Δc)，拟合 τm；
   以 tcq 回到早到值的间隔 Δref 定义窗口 T0 = 2·Δref（数据上升、下降两侧）。
同一仿真里测参考反相器的 FO4 延时，所有结果以 FO4 为单位存进 params.json 的 ff_sim（与门参数的做法一致）。
运行：SKY130_LIB=… 或 SKY130_INCLUDE=… python calib_ff.py；--check 只与仓库比较（镜像验收用，相差 > 10 % 报错）。
"""
import json
import math
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import calib  # noqa: E402

OUT = Path(os.environ.get("CALIB_OUT", HERE))
PARAMS = HERE.parents[3] / "labs/micro/kit/models/params.json"
P = json.loads(PARAMS.read_text(encoding="utf-8"))
WN = P["Wmin"]
WP = round(P["kn"] / P["kp"] * WN, 3)
nmos, pmos = calib.nmos, calib.pmos


def inv(name, a, y):
    return nmos(name + "n", y, a, "0", WN) + pmos(name + "p", y, a, "vdd", WP)


def tg(name, a, b, gn, gp):
    """传输门：NMOS 栅接 gn、PMOS 栅接 gp。"""
    return nmos(name + "n", a, gn, b, WN) + pmos(name + "p", a, gp, b, WP)


def dff():
    s = inv("C1", "clk_in", "clkb") + inv("C2", "clkb", "clk")       # 本地时钟与反相时钟
    s += tg("T1", "d", "m1", "clkb", "clk")                          # 主锁存器输入：CLK = 0 时导通
    s += inv("M1", "m1", "m2") + inv("M2", "m2", "m3") + tg("T2", "m3", "m1", "clk", "clkb")
    s += tg("T3", "m2", "s1", "clk", "clkb")                         # 从锁存器输入：CLK = 1 时导通
    s += inv("S1", "s1", "q") + inv("S2", "q", "s3") + tg("T4", "s3", "s1", "clkb", "clk")
    for k in range(4):
        s += inv(f"L{k}", "q", f"z{k}")
    return s


T_CLK = 1.0e-9          # 被测时钟上升沿（中点）时刻：clk_in 在 1 ns 处由 0 变 1（经两级反相器后才到触发器内部）
# 0.3 ns 处先给一个时钟脉冲（0.3–0.45 ns 为高），把数据的初值打进触发器，使 Q 有确定的初始状态
CLK_PWL = (f"PWL(0 0 0.29n 0 0.31n 1.8 0.44n 1.8 0.46n 0 {T_CLK - 10e-12} 0 {T_CLK + 10e-12} 1.8)")


def run(d_edge, d_rise=True, prev=None, t_end=3.0e-9, step=1e-12):
    """数据在 d_edge 时刻（相对 1 ns 的时钟输入沿）跳变。返回 (tcq, q_final)。prev：先给的数据值。"""
    v0, v1 = (0, 1.8) if d_rise else (1.8, 0)
    td = T_CLK + d_edge
    body = "Vdd vdd 0 1.8\n"
    body += f"Vck clk_in 0 {CLK_PWL}\n"
    body += f"Vd din 0 PWL(0 {v0} {td - 10e-12} {v0} {td + 10e-12} {v1})\n"
    body += inv("D1", "din", "db") + inv("D2", "db", "d") + dff()
    ctl = (f"tran {step} {t_end}\n"
           f"meas tran tq trig v(clk_in) val=0.9 td=0.8n rise=1 targ v(q) val=0.9 td=0.8n {'rise' if d_rise else 'fall'}=1\n"
           f"meas tran qf find v(q) at={t_end * 0.98}")
    out, _ = calib.run(body, ctl)
    m = re.search(r"tq\s*=\s*([-\d.e+]+)", out)
    qf = float(re.search(r"qf\s*=\s*([-\d.e+]+)", out).group(1))
    return (float(m.group(1)) if m else None), qf


def fo4():
    body = "Vdd vdd 0 1.8\nVin in 0 PULSE(0 1.8 100p 20p 20p 1n 2n)\n" + inv("S", "in", "a") + inv("D", "a", "y")
    for k in range(4):
        body += inv(f"L{k}", "y", f"z{k}") + inv(f"M{k}", f"z{k}", f"w{k}")
    ctl = ("tran 1p 4n\nmeas tran tf trig v(a) val=0.9 rise=2 targ v(y) val=0.9 fall=2\n"
           "meas tran tr trig v(a) val=0.9 fall=2 targ v(y) val=0.9 rise=2")
    out, _ = calib.run(body, ctl)
    tf = float(re.search(r"tf\s*=\s*([-\d.e+]+)", out).group(1))
    tr = float(re.search(r"tr\s*=\s*([-\d.e+]+)", out).group(1))
    return (tf + tr) / 2


def main():
    f4 = fo4()
    # 1. 早到时的 tcq（上升、下降）
    tq_r, _ = run(-500e-12, True)
    tq_f, _ = run(-500e-12, False)
    tcq0 = (tq_r + tq_f) / 2
    # 2. 建立时间（数据上升）：间隔从 -300 ps 向 0 扫描
    def tq_at(dl):
        t, q = run(-dl, True)
        return t if (t is not None and q > 0.9) else None
    su = None
    for k in range(300, -1, -2):
        t = tq_at(k * 1e-12)
        if t is None or t > 1.1 * tq_r:
            su = (k + 2) * 1e-12
            break
    # 3. 保持时间：先给 1（数据早已为 1），时钟沿后 δ 变为 0；δ 从 +200 ps 往下扫，看 Q 仍为 1 且 tcq ≤ 1.1 倍
    def hold_ok(dl):
        vd = T_CLK + dl
        body = "Vdd vdd 0 1.8\n" + f"Vck clk_in 0 {CLK_PWL}\n"
        body += f"Vd din 0 PWL(0 0 0.5n 0 0.52n 1.8 {vd - 10e-12} 1.8 {vd + 10e-12} 0)\n"
        body += inv("D1", "din", "db") + inv("D2", "db", "d") + dff()
        out, _ = calib.run(body, "tran 1p 3n\nmeas tran tq trig v(clk_in) val=0.9 td=0.8n rise=1 targ v(q) val=0.9 td=0.8n rise=1\nmeas tran qf find v(q) at=2.9n")
        m = re.search(r"tq\s*=\s*([-\d.e+]+)", out)
        qf = float(re.search(r"qf\s*=\s*([-\d.e+]+)", out).group(1))
        return m is not None and qf > 0.9 and float(m.group(1)) <= 1.1 * tq_r
    th = None
    for k in range(200, -301, -2):
        if not hold_ok(k * 1e-12):
            th = (k + 2) * 1e-12
            break
    # 4. 亚稳态：二分法找临界间隔（数据上升），步长取 0.1 ps
    lo, hi = 0.0, su                               # lo：采不到 1；hi：采得到
    for _ in range(40):
        mid = (lo + hi) / 2
        t, q = run(-mid, True, t_end=4e-9, step=1e-13)
        if q > 0.9:
            hi = mid
        else:
            lo = mid
    dc = hi
    pts = []
    for e in (1e-15, 1e-14, 1e-13, 1e-12, 3e-12, 1e-11):
        t, q = run(-(dc + e), True, t_end=4e-9, step=1e-13)
        if t is not None and q > 0.9:
            pts.append((math.log(e), t))
    n = len(pts); mx = sum(p[0] for p in pts) / n; my = sum(p[1] for p in pts) / n
    slope = sum((p[0] - mx) * (p[1] - my) for p in pts) / sum((p[0] - mx) ** 2 for p in pts)
    a = my - slope * mx
    tau_m = -slope
    dref = math.exp((a - tq_r) / tau_m)            # tcq 回到早到值时的间隔
    T0 = 2 * dref
    res = {"fo4": f4, "tcq": tcq0, "tcq_rise": tq_r, "tcq_fall": tq_f, "tsu": su, "th": th, "tau_m": tau_m, "T0": T0,
           "delta_c": dc, "meta_pts": pts}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ff.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    keep = {"_note": "SKY130 传输门主从触发器的时序参数（samples/数字集成电路设计/生成脚本/calib/calib_ff.py），以同一仿真中的 FO4 延时为单位："
                     "tcq 时钟到输出、tsu 建立时间、th 保持时间、tau_m 亚稳态时间常数、T0 亚稳态窗口",
            "tcq": round(tcq0 / f4, 3), "tsu": round(su / f4, 3), "th": round(th / f4, 3), "tau_m": round(tau_m / f4, 4), "T0": round(T0 / f4, 4)}
    print(f"FO4 {f4*1e12:.1f} ps; tcq {tcq0*1e12:.1f} ps (r {tq_r*1e12:.1f}, f {tq_f*1e12:.1f}); tsu {su*1e12:.0f} ps; th {th*1e12:.0f} ps; "
          f"tau_m {tau_m*1e12:.2f} ps; T0 {T0*1e12:.2f} ps; Δc {dc*1e12:.2f} ps")
    print("FO4 单位：", {k: v for k, v in keep.items() if k != "_note"})
    params = json.loads(PARAMS.read_text(encoding="utf-8"))
    if "--check" in sys.argv:
        old = params.get("ff_sim", {})
        bad = [f"{k}: {old.get(k)} → {v}" for k, v in keep.items() if k != "_note" and abs((old.get(k) or 0) - v) > 0.1 * abs(v) + 0.02]
        print("触发器参数与仓库一致" if not bad else "触发器参数不一致：" + "；".join(bad))
        if bad:
            sys.exit(1)
    else:
        params["ff_sim"] = keep
        PARAMS.write_text(json.dumps(params, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
