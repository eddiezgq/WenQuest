"""贯通项目步骤一起始文件：在 SKY130 模型上测 MOSFET 曲线，提取后面设计要用的参数（第 17 轮附二 5a）。

测量对象：sky130_fd_pr__nfet_01v8 / pfet_01v8，W = 0.42 μm（最小宽度）、L = 0.15 μm，tt 工艺角、27 °C。
  1. 转移特性 ID–VGS：|VDS| = 0.05 V（线性区）和 1.8 V（饱和区）；
  2. 输出特性 ID–VDS：|VGS| = 0.6、0.9、1.2、1.5、1.8 V；
  3. 提取：阈值电压 VT（线性区最大跨导外推法）、饱和电流 IDSAT（|VGS| = |VDS| = 1.8 V，并换算成每微米）、
     亚阈值摆幅 S（mV/dec）、关态电流 IOFF（VGS = 0、|VDS| = 1.8 V）、迁移率比（IDSAT,n / IDSAT,p，同宽度）；
  4. 与第 1 章校准用的有效参数比较（labs/micro/kit/models/params.json）：外推 VT 比有效 VT 大，
     这是“短沟道器件用平方律”的结果，报告里要解释。
输出：out/curves.json、out/params.json（提取值）、out/*.csv；装有 matplotlib 时另出 out/*.png。

模型：镜像里自动用 $PDKPATH/libs.tech/combined/sky130.lib.spice（或 ngspice/ 下的同名文件）的 tt 段；
也可用环境变量 SKY130_LIB（.lib 文件）或 SKY130_INCLUDE（可直接 .include 的模型文件）指定。
用法：python3 device_curves.py [--out 目录]
"""
import argparse
import glob
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

VDD, L, W = 1.8, 0.15, 0.42
NF, PF = "sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"
VGS_STEPS = (0.6, 0.9, 1.2, 1.5, 1.8)


def models() -> str:
    lib, inc = os.environ.get("SKY130_LIB"), os.environ.get("SKY130_INCLUDE")
    if not lib and not inc:
        pdk = os.environ.get("PDKPATH") or f"{os.environ.get('PDK_ROOT', '/foss/pdks')}/{os.environ.get('PDK', 'sky130A')}"
        found = sorted(glob.glob(f"{pdk}/libs.tech/combined/sky130.lib.spice") + glob.glob(f"{pdk}/libs.tech/ngspice/sky130.lib.spice"))
        lib = found[0] if found else None
    if lib:
        return f".param mc_mm_switch=0\n.param mc_pr_switch=0\n.lib {lib} tt\n"
    if inc:
        return f".include {inc}\n"
    sys.exit("SKY130 models not found: set SKY130_LIB or SKY130_INCLUDE")


def sweep(body: str, control: str) -> list[list[float]]:
    with tempfile.TemporaryDirectory() as d:
        Path(d, ".spiceinit").write_text("set ngbehavior=hsa\nset skywaterpdk\nset ng_nomodcheck\n")
        Path(d, "c.sp").write_text(f"* WenQuest capstone step 1\n{models()}{body}\n.control\n{control}\n.endc\n.end\n")
        p = subprocess.run(["ngspice", "-b", "c.sp"], cwd=d, capture_output=True, text=True, timeout=600)
        f = Path(d, "o.dat")
        if not f.exists():
            raise RuntimeError((p.stdout + p.stderr)[-3000:])
        rows = []
        for ln in f.read_text().splitlines():
            try:
                rows.append([float(x) for x in ln.split()])
            except ValueError:
                pass
        return rows


def transfer(kind: str, vds: float) -> list[tuple[float, float]]:
    """|ID| against |VGS| at |VDS| = vds."""
    if kind == "n":
        body = f"Vd d 0 {vds}\nVg g 0 0\nXM d g 0 0 {NF} W={W} L={L} nf=1\n"
        rows = sweep(body, "dc Vg 0 1.8 0.005\nwrdata o.dat -i(Vd)")
        return [(r[0], abs(r[1])) for r in rows]
    body = f"Vs s 0 {VDD}\nVd d 0 {VDD - vds}\nVg g 0 {VDD}\nXM d g s s {PF} W={W} L={L} nf=1\n"
    rows = sweep(body, "dc Vg 1.8 0 -0.005\nwrdata o.dat i(Vd)")
    return [(round(VDD - r[0], 4), abs(r[1])) for r in rows]


def output(kind: str, vgs: float) -> list[tuple[float, float]]:
    """|ID| against |VDS| at |VGS| = vgs."""
    if kind == "n":
        body = f"Vd d 0 0\nVg g 0 {vgs}\nXM d g 0 0 {NF} W={W} L={L} nf=1\n"
        rows = sweep(body, "dc Vd 0 1.8 0.01\nwrdata o.dat -i(Vd)")
        return [(r[0], abs(r[1])) for r in rows]
    body = f"Vs s 0 {VDD}\nVd d 0 {VDD}\nVg g 0 {VDD - vgs}\nXM d g s s {PF} W={W} L={L} nf=1\n"
    rows = sweep(body, "dc Vd 1.8 0 -0.01\nwrdata o.dat i(Vd)")
    return [(round(VDD - r[0], 4), abs(r[1])) for r in rows]


def extract(lin, sat) -> dict:
    """从曲线提取参数。lin、sat 是 [(|VGS|, |ID|), ...]，分别在 |VDS| = 0.05 V 和 1.8 V 下测得，VGS 步长 5 mV。
    返回的键名不要改（wqlab 和实验报告按这些名字取数）。"""
    # ===== 在这里完成 TODO 1：阈值电压 VT —— 线性区最大跨导外推法 =====
    #   gm = dID/dVGS（用相邻点差分）；找 gm 最大的点 (VGS0, ID0)；切线与横轴交点 VGS0 − ID0/gm；再减去 VDS/2。
    vds_lin = 0.05
    gm = [(lin[i + 1][1] - lin[i][1]) / (lin[i + 1][0] - lin[i][0]) for i in range(len(lin) - 1)]
    k = max(range(len(gm)), key=lambda i: gm[i])
    v0 = (lin[k][0] + lin[k + 1][0]) / 2
    i0 = (lin[k][1] + lin[k + 1][1]) / 2
    vt = v0 - i0 / gm[k] - vds_lin / 2
    # ===== 在这里完成 TODO 2：饱和电流 IDSAT（|VGS| = 1.8 V 时 sat 的电流）与关态电流 IOFF（|VGS| = 0）=====
    idsat = min(sat, key=lambda r: abs(r[0] - 1.8))[1]
    ioff = min(sat, key=lambda r: abs(r[0]))[1]
    # ===== 在这里完成 TODO 3：亚阈值摆幅 S —— 亚阈值区里电流每增大 10 倍所需的 ΔVGS（mV/dec），取最小值 =====
    #   在亚阈值区（VGS < VT，且电流远小于 VT 处）逐点算 dVGS/dlog10(ID)，取最小值
    s = float("inf")
    for i in range(len(sat) - 1):
        (va, ia), (vb, ib) = sat[i], sat[i + 1]
        if vb >= vt - 0.1 or ia <= 0 or ib <= ia:
            continue
        s = min(s, (vb - va) / (math.log10(ib) - math.log10(ia)))
    return {"vt": round(vt, 4), "idsat_a": idsat, "idsat_ua_per_um": round(idsat / W * 1e6, 1),
            "ioff_a": ioff, "swing_mv_dec": round(s * 1000, 1), "ion_ioff": round(idsat / ioff, 0) if ioff > 0 else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="step1_out")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    curves, params = {}, {}
    for kind in ("n", "p"):
        lin, sat = transfer(kind, 0.05), transfer(kind, VDD)
        outs = {str(v): output(kind, v) for v in VGS_STEPS}
        curves[kind] = {"transfer_lin": lin, "transfer_sat": sat, "output": outs}
        params[kind] = extract(lin, sat)
        with open(out / f"{kind}mos_transfer.csv", "w") as f:
            f.write("VGS_V,ID_lin_A,ID_sat_A\n" + "".join(f"{v},{x},{y}\n" for (v, x), (_, y) in zip(lin, sat)))
        with open(out / f"{kind}mos_output.csv", "w") as f:
            f.write("VDS_V," + ",".join(f"ID_VGS{v}_A" for v in VGS_STEPS) + "\n")
            for j in range(len(outs[str(VGS_STEPS[0])])):
                f.write(f"{outs[str(VGS_STEPS[0])][j][0]}," + ",".join(str(outs[str(v)][j][1]) for v in VGS_STEPS) + "\n")
    params["mobility_ratio"] = round(params["n"]["idsat_a"] / params["p"]["idsat_a"], 2)
    # compare with chapter 1's effective long-channel parameters
    pj = Path(os.environ.get("WQ_PARAMS", Path(__file__).resolve().parents[2] / "ch1_params.json"))
    if pj.exists():
        p1 = json.loads(pj.read_text(encoding="utf-8"))
        params["ch1_effective"] = {"VT": p1["VTn"], "kn_ua_v2": round(p1["kn"] * 1e6, 1), "kp_ua_v2": round(p1["kp"] * 1e6, 1)}
    (out / "curves.json").write_text(json.dumps(curves), encoding="utf-8")
    (out / "params.json").write_text(json.dumps(params, indent=1, ensure_ascii=False), encoding="utf-8")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        for kind, nm in (("n", "NMOS"), ("p", "PMOS")):
            fig, ax = plt.subplots(1, 2, figsize=(10, 4))
            c = curves[kind]
            ax[0].semilogy([v for v, _ in c["transfer_sat"]], [max(x, 1e-13) for _, x in c["transfer_sat"]], label="|VDS| = 1.8 V")
            ax[0].semilogy([v for v, _ in c["transfer_lin"]], [max(x, 1e-13) for _, x in c["transfer_lin"]], label="|VDS| = 0.05 V")
            ax[0].set_xlabel("|VGS| (V)"); ax[0].set_ylabel("|ID| (A)"); ax[0].legend(); ax[0].set_title(f"{nm} transfer, W/L = 0.42/0.15")
            for v in VGS_STEPS:
                ax[1].plot([x for x, _ in c["output"][str(v)]], [y * 1e6 for _, y in c["output"][str(v)]], label=f"|VGS| = {v} V")
            ax[1].set_xlabel("|VDS| (V)"); ax[1].set_ylabel("|ID| (μA)"); ax[1].legend(fontsize=8); ax[1].set_title(f"{nm} output")
            fig.tight_layout(); fig.savefig(out / f"{kind}mos.png", dpi=120); plt.close(fig)
    except ImportError:
        pass
    print(json.dumps(params, ensure_ascii=False))


if __name__ == "__main__":
    main()
