"""Section 4.9 Measurement and inspection: CMM inspection records for a batch of SH-301 generated with the measurement model of the digital factory (sim/errors.py, wheel wear and dressing as in sim/engine.py);
process capability calculated (with the same function as the quality module of the digital factory, hub/spc.py); conformity decided according to ISO 14253-1 taking measurement uncertainty into account;
then the data after the teacher injects "dressing interval too long" (Examples 4.9.1, 4.9.2, Figure 4.9.1)."""
import math
import statistics as st

import _ch4 as H
from bookout import T, figure, out, style

N = 84                                   # Three wheel-dressing cycles (dressed every 28 parts)
rows = H.inspect_batch(N, seed=4)
rows_bad = H.inspect_batch(N, seed=4, problems={"dressing_interval": None})
CH = H.CHARS
ONE_SIDED = {"runout_bearing", "keyway_sym"}          # Characteristics with an upper limit only (run-out, symmetry): use Cpu


def column(rs, code):
    i = [c[0] for c in CH].index(code)
    return [r[i][5] for r in rs]


def cap(code, rs):
    _, name, nom, lo, hi = CH[[c[0] for c in CH].index(code)]
    v = column(rs, code)
    c = H.spc.capability(v, lo, hi)
    if code in ONE_SIDED:
        c["Cpk"] = (hi - c["mean"]) / (3 * c["sigma_within"])
        c["Ppk"] = (hi - c["mean"]) / (3 * c["s"])
        c["Cp"] = c["Pp"] = None
    c["n_out"] = sum(1 for x in v if not lo <= x <= hi)
    return c


caps = {c[0]: cap(c[0], rows) for c in CH}

# ---------------------------------------------------------------- Measurement uncertainty (Ø35 diameter, coordinate measuring machine)
L_MM = 35.0
MPE = 1.8 + L_MM / 300                   # Maximum permissible error of length measurement MPE_E0 = (1.8 + L/300) μm (the specification this book sets for the workshop CMM, written as in ISO 10360-2)
u_mpe = MPE / math.sqrt(3)               # Converted to a standard uncertainty assuming a uniform distribution
u_rep = 0.5                              # Standard deviation of repeated measurements, μm (repeatability from measurement system analysis, set by this book)
# Temperature: workpiece at 22 °C (2 K from 20 °C, corrected to 20 °C for thermal expansion), uncertainty of the thermometer 0.5 K, expansion coefficient of steel 11.5×10⁻⁶/K with an uncertainty of 1×10⁻⁶/K
u_temp = L_MM * 1e3 * math.sqrt((11.5e-6 * 0.5) ** 2 + (1.0e-6 * 2.0) ** 2)
u_c = math.sqrt(u_mpe ** 2 + u_rep ** 2 + u_temp ** 2)
U = 2 * u_c                              # Expanded uncertainty, k = 2
U_mm = math.ceil(U * 2) / 2 / 1000       # Rounded up to 0.5 μm for the decision (conservative)
_, _, nom35, lo35, hi35 = CH[0]
TU = (hi35 - lo35) * 1000 / U
acc = (lo35 + U_mm, hi35 - U_mm)         # Acceptance zone for proving conformity by the supplier (ISO 14253-1: the tolerance zone reduced by U at each side)
v = column(rows, "bearing_seat_d35") + column(rows, "bearing_seat_d35_r")
n_conform = sum(1 for x in v if acc[0] <= x <= acc[1])
n_inzone = sum(1 for x in v if lo35 <= x <= hi35 and not acc[0] <= x <= acc[1])
n_out = sum(1 for x in v if not lo35 <= x <= hi35)
n_reject_proven = sum(1 for x in v if x > hi35 + U_mm or x < lo35 - U_mm)

# In the normal state the out-of-tolerance parts are all among the last few before dressing: how short must the dressing interval be for the upper limit of the diameter (mean + 3σ) not to exceed the acceptance limit?
# The first part after dressing is already near the lower acceptance limit, so both ends matter: drift + 6σ must not exceed the width of the acceptance zone, and the start after dressing is set at "lower acceptance limit + 3σ"
w_max = ((acc[1] - acc[0]) - 6 * H.SD_D35) / H.SLOPE            # Allowable wheel wear
n_dress = math.floor(w_max / H.GRD_WEAR + 1e-9) + 1              # Maximum number of parts ground in one dressing cycle
base_new = acc[0] + 3 * H.SD_D35                                # Starting diameter to be set after dressing
first_low = H.BASE_D35 - 3 * H.SD_D35                           # Current lower limit (mean - 3σ) of the first part after dressing
n_dress_now = len(H.wear_sequence(200)[:H.wear_sequence(200).index(0.0, 1)])
drift_um = H.SLOPE * max(H.wear_sequence(n_dress_now)) * 1000          # Drift of the diameter in one dressing cycle
spread_um = drift_um + 6 * H.SD_D35 * 1000
out_pos = [i % n_dress_now + 1 for i, x in enumerate(column(rows, "bearing_seat_d35")) if x > hi35]

# ---------------------------------------------------------------- The same characteristic after the problem is injected
cb = cap("bearing_seat_d35", rows_bad)
vb = column(rows_bad, "bearing_seat_d35")
first_out = next((i + 1 for i, x in enumerate(vb) if x > hi35), None)

# ---------------------------------------------------------------- Figure
plt = style()
fig, (a0, a1) = plt.subplots(2, 1, figsize=(7.4, 4.4), sharex=True)
for ax, vals, ttl in ((a0, column(rows, "bearing_seat_d35"), T("(a) 正常状态：砂轮磨损使直径逐件变大，每 28 件修整砂轮", "(a) Normal: wheel wear makes the diameter grow; the wheel is dressed every 28 parts")),
                      (a1, vb, T("(b) 老师注入“砂轮修整间隔过长”：磨损引起的漂移变为约 2.5 倍", "(b) Teacher injects “dressing interval too long”: the drift is about 2.5 times larger"))):
    ax.plot(range(1, N + 1), [(x - nom35) * 1000 for x in vals], "o-", ms=2.2, lw=0.6, color=H.INK)
    for y, ls, c in (((lo35 - nom35) * 1000, "-", "#d62728"), ((hi35 - nom35) * 1000, "-", "#d62728"),
                     ((acc[0] - nom35) * 1000, "--", "#1f77b4"), ((acc[1] - nom35) * 1000, "--", "#1f77b4")):
        ax.axhline(y, ls=ls, color=c, lw=0.8)
    ax.set_ylabel(T("Ø35 偏离 35.010 / μm", "Ø35 minus 35.010 / μm"), fontsize=7)
    ax.tick_params(labelsize=6.5)
    ax.set_title(ttl, fontsize=7.8)
a0.text(N + 0.5, (hi35 - nom35) * 1000, T("上限", "USL"), fontsize=6.4, color="#d62728", va="center")
a0.text(N + 0.5, (acc[1] - nom35) * 1000, T("接收限", "acceptance"), fontsize=6.4, color="#1f77b4", va="center")
a1.set_xlabel(T("零件序号", "Part number"), fontsize=7.5)
a1.set_ylim(-12, 40)
fig.tight_layout()
figure(fig, "fig4_9_1")

c35, c35r, c40, ckw, cro, csy = (caps[k] for k in ("bearing_seat_d35", "bearing_seat_d35_r", "gear_seat_d40", "keyway_width_12", "runout_bearing", "keyway_sym"))
lim = {c[0]: (f"{c[3]:.3f}–{c[4]:.3f}" if c[3] > 0 else f"{c[4]:.3f}") for c in CH}
out(N=N, n_chars=len(CH), lim_d35=lim["bearing_seat_d35"], lim_d40=lim["gear_seat_d40"], lim_kw=lim["keyway_width_12"],
    lim_ro=lim["runout_bearing"], lim_sy=lim["keyway_sym"],
    Cp35=c35["Cp"], Cpk35=c35["Cpk"], Pp35=c35["Pp"], Ppk35=c35["Ppk"], mean35=c35["mean"], sw35=c35["sigma_within"] * 1000, s35=c35["s"] * 1000,
    Cp35r=c35r["Cp"], Cpk35r=c35r["Cpk"], Ppk35r=c35r["Ppk"],
    Cp40=c40["Cp"], Cpk40=c40["Cpk"], Ppk40=c40["Ppk"], Cpkw=ckw["Cpk"], Cpw=ckw["Cp"], Ppkw=ckw["Ppk"],
    Cpk_ro=cro["Cpk"], Ppk_ro=cro["Ppk"], Cpk_sy=csy["Cpk"], Ppk_sy=csy["Ppk"],
    n_out_all=sum(c["n_out"] for c in caps.values()),
    mpe=MPE, u_mpe=u_mpe, u_rep=u_rep, u_temp=u_temp, u_c=u_c, U=U, U_um=U_mm * 1000, n_dress=n_dress, base_new=base_new, base_now=H.BASE_D35, first_low=first_low, n_dress_now=n_dress_now, drift_um=drift_um, spread_um=spread_um, tol35_um=(hi35 - lo35) * 1000, out_pos=T("、", ", ").join(str(k) for k in out_pos), TU=TU, acc_lo=acc[0], acc_hi=acc[1],
    n_meas=len(v), n_conform=n_conform, n_inzone=n_inzone, n_out35=n_out, n_reject_proven=n_reject_proven,
    Cpk_bad=cb["Cpk"], Ppk_bad=cb["Ppk"], n_out_bad=cb["n_out"], first_out=first_out, max_bad=max(vb))
