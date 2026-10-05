"""Section 6.7 Design for assembly (Boothroyd–Dewhurst method): DFA analysis of the rear cover assembly of a robot joint, original
and improved designs; minimum part count of the output-shaft assembly SA-300 of the WQR-105 (digital-factory BOM).
Examples 6.7.1 and 6.7.2, Figure 6.7.1.

Manual assembly time = handling time + insertion (placing, fastening) time, estimated from typical values of the Boothroyd–Dewhurst
manual assembly tables (values taken by this book, yet to be verified). Design efficiency E = 3 s × theoretical minimum number of
parts / total assembly time (3 s being the assembly time of an ideal part). Theoretical minimum number of parts: ask three
questions of each part: does it move relative to the parts already assembled when the product works? must it be of a different
material (or isolated from them)? must it be separate so that other parts can be assembled or removed? One "yes" makes it essential."""
import _ch6 as H
from bookout import T, figure, out, style

F = H.F

# typical times (s): (handling, insertion)
TIMES = {
    "cap": (1.95, 1.5),           # fairly large cap, easy to grasp: place and align
    "oring": (2.25, 5.0),         # O-ring: soft, must be stretched into its groove
    "screw": (1.8, 6.0),          # small screw: pick up, align with hole, tighten with a screwdriver
    "washer": (1.8, 1.5),         # washer: thin and small, awkward to pick up
    "pin": (1.5, 3.0),            # dowel pin: press in
    "holder": (1.5, 2.6),         # magnet holder: press onto the shaft end
    "magnet": (2.6, 4.0),         # magnet: small, magnetic, must be glued
    "gland": (1.95, 8.0),         # cable gland: thread the cable, tighten
    "label": (2.0, 3.0),          # nameplate: peel and stick
    "snapcap": (1.95, 2.5),       # snap-fit cap: align, twist in until it snaps
    "magsub": (1.5, 2.6),         # magnet assembly (holder with magnet glued in by the supplier)
}
# (name, quantity, time class, essential? (three questions), reason)
ORIG = [
    (T("端盖", "cap"), 1, "cap", True, T("要能拆下来维修编码器", "must come off to service the encoder")),
    (T("O 形圈", "O-ring"), 1, "oring", True, T("材料不同（橡胶）", "different material (rubber)")),
    (T("M3 螺钉", "M3 screw"), 6, "screw", False, T("紧固件", "fastener")),
    (T("垫圈", "washer"), 6, "washer", False, T("紧固件", "fastener")),
    (T("定位销", "dowel pin"), 2, "pin", False, T("只为对准，可做成盖上的止口", "only for alignment; a spigot on the cap can do it")),
    (T("磁铁座", "magnet holder"), 1, "holder", True, T("随轴转，相对端盖运动", "turns with the shaft")),
    (T("磁铁", "magnet"), 1, "magnet", True, T("材料不同", "different material")),
    (T("电缆密封接头", "cable gland"), 1, "gland", False, T("可做成盖上的密封套", "can be a sleeve molded on the cap")),
    (T("铭牌", "label"), 1, "label", False, T("可激光打标在盖上", "can be laser-marked on the cap")),
]
NEW = [
    (T("卡扣式端盖（止口、密封套一体）", "snap-fit cap (spigot, cable sleeve integral)"), 1, "snapcap", True, ""),
    (T("O 形圈", "O-ring"), 1, "oring", True, ""),
    (T("M3 螺钉（防松）", "M3 screw (anti-loosening)"), 2, "screw", False, ""),
    (T("磁铁组件（供应商粘好）", "magnet assembly (bonded by supplier)"), 1, "magsub", True, ""),
]


def analyze(parts):
    n = sum(q for _, q, *_ in parts)
    nmin = sum(q for _, q, _, ess, _ in parts if ess)
    tt = sum(q * sum(TIMES[k]) for _, q, k, _, _ in parts)
    rows = [(nm, q, q * sum(TIMES[k])) for nm, q, k, _, _ in parts]
    return n, nmin, tt, 3 * nmin / tt, rows


n0, nmin0, t0, e0, rows0 = analyze(ORIG)
n1, nmin1, t1, e1, rows1 = analyze(NEW)
LABOR = sum(F.WORKSTATIONS["装配工位 ASM-01"][1])          # rate of the digital factory's assembly station, USD/hour
c0, c1 = t0 / 3600 * LABOR, t1 / 3600 * LABOR
Q_YEAR = 20000                                               # annual output for task sheet TS-6-1 (set by this book)

# Example 6.7.2: SA-300 (digital-factory BOM)
ESS = {"SH-301": (True, T("基体零件", "base part")),
       "GR-302": (False, T("三个“否”：40Cr 与 45 钢都是钢，原理上可做成齿轮轴", "three noes: both steels; could be one gear shaft")),
       "BRG-6207": (True, T("内外圈相对转动", "rings rotate relative to each other"))}
sa = []
for code, q in F.BOMS["SA-300"][1]:
    ess, why = ESS.get(code, (False, T("键：可用过盈或花键代替（要另算强度）", "key: interference or spline could replace it (check strength)")))
    sa.append((code, F.ITEMS[code][0].split(" ")[0], int(q), ess, why))
n_sa = sum(r[2] for r in sa)
nmin_sa = sum(r[2] for r in sa if r[3])

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.25, 1.0]})
for ax, rows, ttl in ((a0, rows0, T(f"(a) 原设计：{n0} 个零件，{t0:.0f} s，E = {e0:.0%}", f"(a) Original: {n0} parts, {t0:.0f} s, E = {e0:.0%}")),
                      (a1, rows1, T(f"(b) 改进设计：{n1} 个零件，{t1:.0f} s，E = {e1:.0%}", f"(b) Redesign: {n1} parts, {t1:.0f} s, E = {e1:.0%}"))):
    y = range(len(rows))
    ax.barh(list(y), [r[2] for r in rows], color=H.C_MILL)
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{r[0]} × {r[1]}" for r in rows], fontsize=6.2)
    ax.invert_yaxis()
    ax.set_xlim(0, max(r[2] for r in rows0) * 1.1)
    ax.set_xlabel(T("装配时间 / s", "Assembly time / s"), fontsize=7.2)
    ax.tick_params(labelsize=6.3)
    ax.set_title(ttl, fontsize=7.4)
fig.tight_layout()
figure(fig, "fig6_7_1")

out(n0=n0, nmin0=nmin0, t0=t0, e0=100 * e0, n1=n1, nmin1=nmin1, t1=t1, e1=100 * e1, t_saved=100 * (1 - t1 / t0),
    labour=LABOR, c0=c0, c1=c1, t_screw=sum(TIMES["screw"]), t_screws0=6 * sum(TIMES["screw"]) + 6 * sum(TIMES["washer"]),
    share_fast0=100 * (6 * sum(TIMES["screw"]) + 6 * sum(TIMES["washer"])) / t0,
    n_sa=n_sa, nmin_sa=nmin_sa, n_kinds_sa=len(sa), q_year=Q_YEAR, save_year=(c0 - c1) * Q_YEAR, save_h=(t0 - t1) * Q_YEAR / 3600)
