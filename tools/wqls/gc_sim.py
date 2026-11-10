"""第 138 轮 GC：主轴伺服的控制仿真——起动、5000 r/min 缝纫、减速剪线、停针，负载用 G2 的一转力矩。

    python3 tools/wqls/gc_sim.py      # 写到 docs/设计/WQ-LS/GC/

模型（教材《缝纫机设计与制造》第 13、14 章的结构）：
  电流环：一阶滞后，带宽 2 kHz（PWM 16 kHz、每 0.1 ms 算一次，教材第 18 章），力矩限幅 ±峰值；
  速度环：PI，带宽 f_s（扫 20–400 Hz），速度反馈来自编码器差分（12 位，每 0.1 ms）；可选“按转角查表的负载力矩前馈”；
  位置环：停针时 P 控制，接速度环；
  负载：J = 转子与手轮 + 负载侧惯量（G2）；负载力矩 = 惯性部分 ×(ω/ω5000)² + 缝纫阻力（剪线那一针另加剪线力矩，示例）。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402

for _f in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",):
    if Path(_f).exists():
        font_manager.fontManager.addfont(_f)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import dyn  # noqa: E402

OUT = ROOT / "docs" / "设计" / "WQ-LS" / "GC"
plt.rcParams.update({"font.family": ["Noto Sans CJK JP", "DejaVu Sans"], "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False})
INK, MUTE, ACC, GRN, BLU, ORG = "#1d2733", "#7a8794", "#c8102e", "#2e9e6a", "#1f5fa8", "#d98a1f"

R = dyn.Machine().run(N=720)
W5 = R["w"]
T_IN = R["T_bar"] + R["T_rod"] + R["T_tk"] + R["T_fd"]          # 惯性部分（∝ ω²）
T_RS = R["T_needle"] + R["T_thread"] + R["T_feed"] + R["T_fric"] + R["T_grav"]
PHI = R["phi"]
J_LOAD = 1.24e-4
DT = 1e-4
CPR = 4096                                                         # 编码器每转计数（12 位）
T_PEAK = 3.2


def load(phi_deg, w, trim=False):
    i = int(round((phi_deg % 360) / 0.5)) % 720
    T = T_IN[i] * (w / W5) ** 2 + (T_RS[i] if w > 1 else 0.0)
    if trim and 200 <= phi_deg % 360 <= 330:                       # 剪线动刀切线（示例 0.15 N·m）
        T += 0.15
    return T


def simulate(profile, f_s=40.0, J_rotor=4e-4, ff=0.0, stop_at=None, t_end=1.0, trim_window=None):
    """profile(t) → 目标转速 rad/s；stop_at=(t0, 目标角°) 时从 t0 起转为位置控制停针。"""
    J = J_rotor + J_LOAD
    wc = 2 * math.pi * f_s
    kp, ti = J * wc, 4 / wc                                        # PI：比例按惯量，积分时间 4/ωc
    tau_i = 1 / (2 * math.pi * 2000)
    n = int(t_end / DT)
    th, w, Tm, integ, cnt_prev = 0.0, 0.0, 0.0, 0.0, 0
    w_est = 0.0
    log = np.zeros((n, 6))
    pos_mode = False
    w_ref_prev = 0.0
    for k in range(n):
        t = k * DT
        cnt = int(math.floor(th / (2 * math.pi) * CPR))
        w_est = 0.7 * w_est + 0.3 * (cnt - cnt_prev) * 2 * math.pi / CPR / DT
        cnt_prev = cnt
        trim = trim_window is not None and trim_window[0] <= t <= trim_window[1]
        if stop_at and t >= stop_at[0]:
            pos_mode = True
        if pos_mode:
            # 停针：目标角在当前圈之后最近的那个位置；位置环 P，限速 300 r/min
            tgt = stop_at[1] * math.pi / 180
            rev = math.floor((th - tgt) / (2 * math.pi)) + 1
            err = tgt + 2 * math.pi * rev - th
            if err > 2 * math.pi - 0.02:
                err -= 2 * math.pi
            kpos = 2 * math.pi * f_s / 4
            w_ref = max(-300 * math.pi / 30, min(300 * math.pi / 30, kpos * err))
        else:
            w_ref = profile(t)
        e = w_ref - w_est
        a_ref = (w_ref - w_ref_prev) / DT if k else 0.0             # 加速度前馈：J·dω/dt（按目标曲线，标准做法）
        w_ref_prev = w_ref
        T_ff = (ff * load(math.degrees(th), w_ref) if w_ref > 50 else 0.0) + (J * a_ref if not pos_mode else 0.0)
        integ += e * DT
        T_cmd = kp * (e + integ / ti) + T_ff
        if abs(T_cmd) > T_PEAK:
            integ -= e * DT                                        # 限幅时停止积分
            T_cmd = max(-T_PEAK, min(T_PEAK, T_cmd))
        Tm += (T_cmd - Tm) * (1 - math.exp(-DT / tau_i))
        TL = load(math.degrees(th), w, trim)
        if w < 1e-3 and abs(Tm) <= abs(TL) and not pos_mode and w_ref == 0:
            acc = 0.0
        else:
            acc = (Tm - TL) / J
        w += acc * DT
        th += w * DT
        log[k] = (t, w * 30 / math.pi, Tm, math.degrees(th) % 360, w_ref * 30 / math.pi, TL)
    return log


def ramp(t0, t1, n0, n1):
    return lambda t: (n0 + (n1 - n0) * min(1, max(0, (t - t0) / (t1 - t0)))) * math.pi / 30


def cycle():
    """一个完整的工作周期（教材第 14 章）：0.1 s 起动到 5000 → 缝 0.4 s → 0.12 s 减到剪线转速 300 → 剪线一针 → 停在上针位（70°）。"""
    W = 5000

    def prof(t):
        if t < 0.10:
            return ramp(0, 0.10, 0, W)(t)
        if t < 0.50:
            return W * math.pi / 30
        if t < 0.62:
            return ramp(0.50, 0.62, W, 300)(t)
        return 300 * math.pi / 30
    return prof


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = {}
    # 1 速度环带宽扫描（5000 r/min 稳态）：转速波动、电机力矩均方根
    rows = []
    const = lambda t: ramp(0, 0.1, 0, 5000)(t)  # noqa: E731
    for f_s in (20, 40, 80, 160, 400):
        for ff in (0.0, 0.5):
            lg = simulate(const, f_s=f_s, ff=ff, t_end=0.5)
            ss = lg[lg[:, 0] > 0.3]
            rows.append(dict(f_s=f_s, ff=ff, ripple=float((ss[:, 1].max() - ss[:, 1].min()) / 2 / 5000 * 100),
                             T_rms=float(np.sqrt(np.mean(ss[:, 2] ** 2))), T_peak=float(np.max(np.abs(ss[:, 2])))))
    res["bandwidth"] = rows
    # 2 完整周期（推荐参数）
    f_rec = 40.0
    t_trim = 0.62 + 60 / 300 * 1.0                                 # 剪线转速下转一针
    lg = simulate(cycle(), f_s=f_rec, ff=0.0, stop_at=(t_trim, 70.0), t_end=t_trim + 0.25, trim_window=(0.62, t_trim))
    t, rpm, Tm, ang = lg[:, 0], lg[:, 1], lg[:, 2], lg[:, 3]
    stop_k = np.where((t > t_trim) & (np.abs(rpm) < 1))[0]
    settle = None
    if len(stop_k):
        # 停稳：之后 20 ms 内转速都 < 1 r/min
        for k in stop_k:
            if np.all(np.abs(rpm[k:k + 200]) < 1):
                settle = float(t[k])
                break
    final = float(ang[-1])
    err = (final - 70 + 180) % 360 - 180
    t50 = float(t[np.argmax(rpm >= 0.98 * 5000)])
    res["cycle"] = dict(f_s=f_rec, ff=0.0, t_reach_5000=t50, stop_angle=final, stop_error_deg=err,
                        t_settle=settle, t_from_release=None if settle is None else settle - 0.50,
                        T_peak=float(np.max(np.abs(Tm))), T_rms_cycle=float(np.sqrt(np.mean(Tm ** 2))))
    fig, axs = plt.subplots(3, 1, figsize=(8.6, 7.2), sharex=True, gridspec_kw=dict(hspace=0.1))
    axs[0].plot(t, lg[:, 4], color=MUTE, lw=1, ls="--", label="目标")
    axs[0].plot(t, rpm, color=INK, lw=1.4, label="主轴转速")
    axs[0].set_ylabel("r/min")
    axs[0].legend(frameon=False, fontsize=8)
    for i_, (x0, x1, nm) in enumerate(((0, 0.10, "起动"), (0.10, 0.50, "缝纫 5000 r/min"), (0.50, 0.62, "减速"),
                                       (0.62, t_trim, "剪线一针 300 r/min"), (t_trim, t[-1], "停针（上针位 70°）"))):
        axs[0].axvspan(x0, x1, color=["#eef1f4", "#ffffff"][i_ % 2], lw=0)
        axs[0].text((x0 + x1) / 2, 5400, nm, ha="center", fontsize=7.5, color=MUTE)
    axs[0].set_ylim(-200, 5800)
    axs[1].plot(t, Tm, color=BLU, lw=0.8)
    axs[1].axhline(T_PEAK, color=ACC, lw=0.6, ls=":")
    axs[1].axhline(-T_PEAK, color=ACC, lw=0.6, ls=":")
    axs[1].set_ylabel("电机力矩 N·m")
    axs[2].plot(t, ang, color=GRN, lw=0.6)
    axs[2].axhline(70, color=ACC, lw=0.6, ls=":")
    axs[2].set_ylabel("主轴转角 °")
    axs[2].set_xlabel("时间 / s")
    fig.suptitle(f"WQ-LS 主轴伺服：一个工作周期（速度环 {f_rec:.0f} Hz、不加前馈；停针误差 {err:+.2f}°）",
                 x=0.06, ha="left", fontsize=10.5)
    fig.savefig(OUT / "1_工作周期.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    # 3 带宽图
    fig, a = plt.subplots(1, 2, figsize=(9.6, 3.6))
    for ff, ls in ((0.0, "-"), (0.5, "--")):
        rr = [r for r in rows if r["ff"] == ff]
        a[0].plot([r["f_s"] for r in rr], [r["ripple"] for r in rr], ls, marker="o", color=INK, label=f"前馈 {ff:.0%}")
        a[1].plot([r["f_s"] for r in rr], [r["T_rms"] for r in rr], ls, marker="o", color=BLU, label=f"前馈 {ff:.0%}")
    a[1].axhline(1.05, color=ACC, lw=0.8, ls=":")
    a[1].text(22, 1.1, "550 W 电机额定 1.05 N·m", color=ACC, fontsize=7.5)
    for x, yl in ((a[0], "转速波动 ±% （5000 r/min）"), (a[1], "电机力矩均方根 N·m")):
        x.set_xscale("log")
        x.set_xlabel("速度环带宽 / Hz")
        x.set_ylabel(yl)
        x.legend(frameon=False, fontsize=8)
        x.grid(color="#eef0f2", lw=0.6)
    fig.suptitle("速度环带宽：硬了电机发热，软了转速波动（二倍频 167 Hz）", x=0.06, ha="left", fontsize=10.5)
    fig.tight_layout()
    fig.savefig(OUT / "2_速度环带宽.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    (OUT / "仿真结果.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows:
        print(r["f_s"], r["ff"], round(r["ripple"], 2), round(r["T_rms"], 2), round(r["T_peak"], 2))
    print(json.dumps(res["cycle"], ensure_ascii=False))


if __name__ == "__main__":
    main()
