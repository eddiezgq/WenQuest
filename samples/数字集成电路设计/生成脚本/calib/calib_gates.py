"""第 17 轮附三 6c：用 ngspice + SKY130（tt，27 °C）测第 2 章的门参数。

1. 逻辑努力 g 与寄生延时 p。门按“等效反相器”定尺寸（参考反相器 Wn = 0.42 μm、Wp = r·Wn，r 取第 1 章的 k′n/k′p）：
   n 输入与非门 NMOS 各 n·Wn、PMOS 各 r·Wn；n 输入或非门 NMOS 各 Wn、PMOS 各 n·r·Wn。
   前级反相器整形输入 → 被测门的某个输入 → h 个同样的门的同一个输入（h = 1、2、4、8），其余输入接非控制值。
   平均延时 d(h) = (tPHL + tPLH)/2 对 h 线性拟合：斜率 / 反相器的斜率 = g，截距 / 反相器的斜率 = p（以 τ 为单位）。
   每个门测两个输入：靠近输出的 A 和靠近电源轨的 B。比值只依赖仿真器内部的相对关系，本地和镜像里的模型文件稍有不同时也基本不变。
2. 伪 NMOS 或非门（PMOS 负载常通）：一个输入为高时的输出低电平与静态电流；PMOS 负载取最小宽度，下拉 NMOS 取它的 1、2、4 倍。
3. NMOS 传输管与传输门：输入 1.8 V、栅 1.8 V，给 10 fF 电容充电，10 ns 后的输出电压（高电平损失）。
结果写 calib/gates.json（CALIB_OUT 指定目录时写到那里），要点写进 params.json 的 gates_sim 一节；--check 只与仓库比较（镜像验收用）。运行：SKY130_LIB=… 或 SKY130_INCLUDE=… python calib_gates.py
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import calib  # noqa: E402  共用 run()、nmos()、pmos() 与模型来源

OUT = Path(os.environ.get("CALIB_OUT", HERE))
P = json.loads((HERE.parents[3] / "labs/micro/kit/models/params.json").read_text(encoding="utf-8"))
WN, VDD = P["Wmin"], P["VDD"]
R = P["kn"] / P["kp"]
WP = round(R * WN, 3)
nmos, pmos = calib.nmos, calib.pmos


def gate(kind: str, n: int, name: str, ins: list[str], y: str) -> str:
    """kind = inv / nand / nor；ins[0] 为靠近输出的输入（A），ins[-1] 靠近电源轨。"""
    s = ""
    if kind == "inv":
        return nmos(name + "n", y, ins[0], "0", WN) + pmos(name + "p", y, ins[0], "vdd", WP)
    if kind == "nand":
        wn = round(n * WN, 3)
        nodes = [y] + [f"{name}_s{k}" for k in range(1, n)] + ["0"]
        for k in range(n):                                   # 串联 NMOS：输入 k 在第 k 个位置（0 = 靠近输出）
            s += nmos(f"{name}n{k}", nodes[k], ins[k], nodes[k + 1], wn)
            s += pmos(f"{name}p{k}", y, ins[k], "vdd", WP)
        return s
    if kind == "nor":
        wp = round(n * WP, 3)
        nodes = [y] + [f"{name}_s{k}" for k in range(1, n)] + ["vdd"]
        for k in range(n):                                   # 串联 PMOS：输入 k 在第 k 个位置（0 = 靠近输出）
            s += pmos(f"{name}p{k}", nodes[k], ins[k], nodes[k + 1], wp)
            s += nmos(f"{name}n{k}", y, ins[k], "0", WN)
        return s
    raise ValueError(kind)


def delay(kind: str, n: int, pin: int, h: int) -> tuple[float, float]:
    other = "vdd" if kind == "nand" else "0"                   # 非控制值
    ins = lambda sig: [sig if k == pin else other for k in range(max(n, 1))]  # noqa: E731
    body = "Vdd vdd 0 1.8\nVin in 0 PULSE(0 1.8 100p 20p 20p 1n 2n)\n"
    body += gate("inv", 1, "S", ["in"], "a")                   # 整形
    body += gate(kind, n, "D", ins("a"), "y")                  # 被测门
    for k in range(h):
        body += gate(kind, n, f"L{k}", ins("y"), f"z{k}")      # h 个同样的门作负载
        body += gate("inv", 1, f"M{k}", [f"z{k}"], f"w{k}")    # 负载门再带一级，边沿真实
    ctl = ("tran 1p 4n\n"
           "meas tran tf trig v(a) val=0.9 rise=2 targ v(y) val=0.9 fall=2\n"
           "meas tran tr trig v(a) val=0.9 fall=2 targ v(y) val=0.9 rise=2")
    out, _ = calib.run(body, ctl)
    tf = float(re.search(r"tf\s*=\s*([-\d.e+]+)", out).group(1))
    tr = float(re.search(r"tr\s*=\s*([-\d.e+]+)", out).group(1))
    return tf, tr


def fit(kind, n, pin):
    hs = [1, 2, 4, 8]
    pts = {h: delay(kind, n, pin, h) for h in hs}
    d = {h: sum(pts[h]) / 2 for h in hs}
    mx = sum(hs) / 4; my = sum(d.values()) / 4
    slope = sum((h - mx) * (d[h] - my) for h in hs) / sum((h - mx) ** 2 for h in hs)
    return slope, my - slope * mx, {str(h): pts[h] for h in hs}


def pseudo_nmos(ratio: float) -> dict:
    """PMOS 负载取最小宽度（器件模型不允许更窄），NMOS 下拉宽为它的 ratio 倍。"""
    wn = round(WN * ratio, 3)
    body = ("Vdd vdd 0 1.8\nVa a 0 1.8\nVb b 0 0\n" + nmos("NA", "y", "a", "0", wn) + nmos("NB", "y", "b", "0", wn) +
            pmos("PL", "y", "0", "vdd", WN))
    out, _ = calib.run(body, "op\nprint v(y) i(Vdd)")
    vol = float(re.search(r"v\(y\) = ([-\d.e+]+)", out).group(1))
    i = -float(re.search(r"i\(vdd\) = ([-\d.e+]+)", out).group(1))
    return {"wn_over_wp": ratio, "VOL": vol, "I": i}


def pass_high() -> dict:
    res = {}
    for kind in ("nmos", "tgate"):
        body = "Vdd vdd 0 1.8\nVin in 0 PULSE(0 1.8 100p 50p 50p 20n 40n)\nCl y 0 10f\n" + nmos("N", "y", "vdd", "in", WN)
        if kind == "tgate":
            body += pmos("P", "y", "0", "in", WP)
        out, _ = calib.run(body, "tran 10p 10n\nmeas tran v10 find v(y) at=10n\nmeas tran t50 trig v(in) val=0.9 rise=1 targ v(y) val=0.9 rise=1")
        res[kind] = {"V_high": float(re.search(r"v10\s*=\s*([-\d.e+]+)", out).group(1)),
                     "t50": float(re.search(r"t50\s*=\s*([-\d.e+]+)", out).group(1))}
    return res


def main():
    s_inv, b_inv, raw_inv = fit("inv", 1, 0)
    res = {"r": R, "Wn": WN, "Wp": WP, "tau": s_inv, "p_inv": b_inv / s_inv, "raw": {"inv": raw_inv}, "gates": {}}
    for kind in ("nand", "nor"):
        for n in (2, 3):
            for pin, tag in ((0, "A"), (n - 1, "B")):
                s, b, raw = fit(kind, n, pin)
                key = f"{kind}{n}_{tag}"
                res["gates"][key] = {"g": s / s_inv, "p": b / s_inv}
                res["raw"][key] = raw
    res["pseudo_nmos"] = [pseudo_nmos(x) for x in (1.0, 2.0, 4.0)]
    res["pass"] = pass_high()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gates.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    keep = {"_note": "SKY130 门参数仿真值（samples/数字集成电路设计/生成脚本/calib/calib_gates.py）：g、p 以同一仿真里参考反相器的 τ 为单位；"
                     "A 为靠近输出的输入，B 为靠近电源轨的输入；pseudo_nmos 为 PMOS 负载取最小宽度时的输出低电平与静态电流；"
                     "pass 为 10 fF 负载充电 10 ns 后的输出高电平",
            "p_inv": round(res["p_inv"], 3), "gates": {k: {"g": round(v["g"], 3), "p": round(v["p"], 3)} for k, v in res["gates"].items()},
            "pseudo_nmos": [{"wn_over_wp": v["wn_over_wp"], "VOL": round(v["VOL"], 4), "I": float(f"{v['I']:.3g}")} for v in res["pseudo_nmos"]],
            "pass": {k: round(v["V_high"], 3) for k, v in res["pass"].items()}}
    print(f"tau {s_inv*1e12:.2f} ps, p_inv {b_inv/s_inv:.2f}")
    for k, v in res["gates"].items():
        print(f"{k}: g {v['g']:.2f}  p {v['p']:.2f}")
    for v in res["pseudo_nmos"]:
        print(f"pseudo-NMOS Wn/Wp {v['wn_over_wp']}: VOL {v['VOL']:.3f} V, I {v['I']*1e6:.0f} μA")
    print("pass:", {k: round(v["V_high"], 3) for k, v in res["pass"].items()})
    params_path = HERE.parents[3] / "labs/micro/kit/models/params.json"
    params = json.loads(params_path.read_text(encoding="utf-8"))
    if "--check" in sys.argv:                                   # 镜像验收：与仓库里的值比较，g、p 相差超过 5 % 报错
        old = params.get("gates_sim", {}).get("gates", {})
        bad = [f"{k}.{q}: {old.get(k, {}).get(q)} → {v[q]}" for k, v in keep["gates"].items() for q in ("g", "p")
               if abs((old.get(k, {}).get(q) or 0) - v[q]) > 0.05 * abs(v[q])]
        print("门参数与仓库一致" if not bad else "门参数不一致：" + "；".join(bad))
        if bad:
            sys.exit(1)
    else:
        params["gates_sim"] = keep
        params_path.write_text(json.dumps(params, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
