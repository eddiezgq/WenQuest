"""33.10 协作机器人肩关节空心轴 RJ-201：载荷（数字工厂动力学）→ 谐波减速器选型核对（零件库）→ 按刚度定直径 →
钢与铝合金比较 → 有限元核对扭转角和应力 → 按力矩记录算疲劳寿命 → 急停时的静强度（算例 33.10.1–33.10.4，图 33.10.1–33.10.3）。"""
import math

import numpy as np

import _draw as D
import _fea  # noqa: F401 —— 设好 CalculiX 求解器
import _rj as R
from bookout import T, figure, out, style
import mdstd

t, Tq, F, W = R.cycle()                          # N·m、N、rad/s
Tabs = np.abs(Tq)
T_peak, T_min = float(Tabs.max()), float(Tabs.min())
T_rms = float(np.sqrt(np.mean(Tq ** 2)))
F_peak = float(F.max())
w_max = float(np.max(np.abs(W)))                 # rad/s（关节）

# ---- 谐波减速器（零件库 D-RDC-HD-CSF）：平均负载转矩按转速加权的立方平均（样本里的常用算法）
nw = np.abs(W)
T_av = float((np.sum(nw * Tabs ** 3) / max(np.sum(nw), 1e-12)) ** (1 / 3))
hd = R.harmonic("25-100")
n_in_max = w_max * hd["ratio"] * 60 / (2 * math.pi)
hd_ok = T_peak <= hd["repeat"] and T_av <= hd["avg"] and n_in_max <= hd["n_max"]

# ---- 材料
st, al = mdstd.material("40Cr-QT"), mdstd.material("7075-T6")
G = lambda m: m["E"] / (2 * (1 + m["mu"]))      # noqa: E731

# ---- 按刚度定直径：末端偏移 = 扭转角 × 工作半径 ≤ 预算
rows = []
for seat, bore, brg_ in R.CANDIDATES:
    sg = R.segments(seat)
    th = R.twist(T_peak * 1e3, sg, G(st), bore)
    rows.append({"seat": seat, "bore": bore, "brg": brg_, "theta": th, "delta": th * R.REACH_MM,
                 "mass": R.mass(sg, st["density"], bore), "ok": th * R.REACH_MM * R.HAND_MARGIN <= R.DEFLECT_BUDGET_MM})
pick = min((r for r in rows if r["ok"]), key=lambda r: r["mass"])          # 满足刚度的方案里最轻的
assert (pick["seat"], pick["bore"]) == (R.SEAT, R.BORE)
segs = R.segments(R.SEAT)
brg = R.bearing(R.BEARING)

# ---- 钢与铝：同一尺寸；同一刚度（外径放大到同样的末端偏移，内孔不变）
th_st = R.twist(T_peak * 1e3, segs, G(st))
th_al = R.twist(T_peak * 1e3, segs, G(al))
m_st, m_al = R.mass(segs, st["density"]), R.mass(segs, al["density"])
k = 1.0
while R.twist(T_peak * 1e3, [(D_ * k if i else D_ * k, L, n) for i, (D_, L, n) in enumerate(segs)], G(al)) > th_st and k < 3:
    k += 0.002
segs_al = [(D_ * k, L, n) for D_, L, n in segs]
m_al_same = R.mass(segs_al, al["density"])
# 同样的大外径做成薄壁钢管：内孔加大到扭转角与 Ø50/30 钢轴相同——看减重到底来自材料还是来自直径
bore_big = R.BORE
while R.twist(T_peak * 1e3, segs_al, G(st), bore_big + 0.1) <= th_st and bore_big < segs_al[4][0] - 4:
    bore_big += 0.1
m_st_big = R.mass(segs_al, st["density"], bore_big)
wall_big = (R.SEAT * k - bore_big) / 2
# 只看两法兰之间的“管身”（决定扭转刚度的部分）：法兰要装螺钉，壁厚不由刚度定
m_al_body = R.mass(segs_al[1:-1], al["density"])
m_big_body = R.mass(segs_al[1:-1], st["density"], bore_big)
m_al_fl = m_al_same - m_al_body
m_big_fl = m_st_big - m_big_body

# ---- 强度：扭转 + 外侧轴承处的弯曲（剪力 × 力臂）
M_b = F_peak * R.ARM_OFFSET                       # N·mm
sig = M_b / R.W_hollow(R.SEAT)
tau = T_peak * 1e3 / (2 * R.W_hollow(R.SEAT))
s_vm = math.sqrt(sig ** 2 + 3 * tau ** 2)
S_static = st["sigma_s"] / s_vm
# 急停：减速器瞬时允许最大转矩（零件库）作用在轴上，轴不能先坏
tau_stop = hd["momentary"] * 1e3 / (2 * R.W_hollow(R.SEAT))
S_stop = st["sigma_s"] / (math.sqrt(3) * tau_stop)

# ---- 有限元（数字工厂“仿真与分析”的同一套程序）：减速器法兰端面固定，大臂法兰外圆加峰值扭矩
from cae import geometry as GEO, solve as SOL, fatigue as FAT, materials as MATS  # noqa: E402
step = R.step_bytes(segs)
faces, _, _ = GEO.faces(step)
fix = next(f["id"] for f in faces if f["kind"] == "plane" and abs(f["bbox"][2]) < 1e-6 and abs(f["bbox"][5]) < 1e-6)
z_end = sum(L for _, L, _ in segs)
r_fl = segs[-1][0] / 2
tq_face = next(f["id"] for f in faces if f["kind"] == "cylinder" and abs((f["bbox"][3] - f["bbox"][0]) / 2 - r_fl) < 0.05
               and f["bbox"][5] > z_end - 1e-3)
mat_fe = MATS.get("40Cr-QT")
stats, surf, _ = SOL.solve(step, {"material": mat_fe, "mesh": {"size_mm": 3.5}, "loads": [
    {"type": "fixed", "faces": [fix]},
    {"type": "torque", "faces": [tq_face], "value_nmm": T_peak * 1e3, "axis": {"origin": [0, 0, 0], "dir": [0, 0, 1]}}]})
theta_fe = stats["u_max_mm"] / r_fl                               # 大臂法兰外缘的切向位移 / 半径
# 手算对照（固定端面到加载面中点：法兰一半到另一个法兰一半，与 R.twist 同口径）
err_theta = (theta_fe - th_st) / th_st * 100
tau_hand_body = T_peak * 1e3 / R.J_hollow(R.SEAT + 5) * (R.SEAT + 5) / 2
# 疲劳寿命：同一节拍不断重复（pyLife 雨流计数 + Goodman + Miner；数字工厂的 cae.fatigue）
zs = surf["positions"][:, 2]
keep = (zs > 4) & (zs < z_end - 12)                                # 离固定面、加载面远一点（约束和载荷附近的应力不可信）
vm_keep = np.where(keep, surf["vm"], 0.0)
vm_hot = float(vm_keep.max())
_, fs = FAT.compute(vm_keep, T_peak, np.abs(Tq), R.CYCLE_S, mat_fe, surface="fine_turned", size_factor=mdstd.size_factor(R.SEAT))
life_inf = bool(fs["infinite"])

# ---------------------------------------------------------------- 图
plt = style()
fig, axs = plt.subplots(2, 1, figsize=(6.6, 4.4), sharex=True)
axs[0].plot(t, Tq, color=D.TORQUE, lw=1.4)
axs[0].axhline(-hd["rated"], color=D.MUTED, ls="--", lw=0.8)
axs[0].text(t[-1], -hd["rated"], T(" CSF-25-100 额定", " CSF-25-100 rated"), fontsize=8, va="bottom", ha="right", color=D.MUTED)
axs[0].set_ylabel(T("J2 力矩 / N·m", "J2 torque / N·m"))
axs[1].plot(t, F, color=D.FORCE, lw=1.4)
axs[1].set_ylabel(T("传给大臂的力 / N", "force on upper arm / N"))
axs[1].set_xlabel(T("时间 / s（一个搬运节拍）", "time / s (one pick-and-place cycle)"))
for ax in axs:
    for x0 in (0, R.MOVE_S + R.DWELL_S):
        ax.axvspan(x0, x0 + R.MOVE_S, color="#eef3f8", lw=0, zorder=0)
fig.tight_layout()
figure(fig, "fig33_10_1")

fig, ax = plt.subplots(figsize=(6.4, 3.6))
seats = np.linspace(40, 55, 60)
for m_, name, col in ((st, T("40Cr 钢", "40Cr steel"), D.MOMENT), (al, T("7075 铝合金", "7075 aluminium"), D.FORCE)):
    ax.plot(seats, [R.twist(T_peak * 1e3, R.segments(s_), G(m_), 30) * R.REACH_MM for s_ in seats], color=col, lw=1.6, label=name + T("，内孔 Ø30", ", bore Ø30"))
ax.axhline(R.DEFLECT_BUDGET_MM, color=D.INK, ls="--", lw=0.9)
ax.axhline(R.DEFLECT_BUDGET_MM / R.HAND_MARGIN, color=D.INK, ls=":", lw=0.9)
ax.text(40.3, R.DEFLECT_BUDGET_MM * 1.04, T("允许值", "allowed"), fontsize=8)
ax.text(40.3, R.DEFLECT_BUDGET_MM / R.HAND_MARGIN * 0.86, T("手算选型线（留 20% 余量）", "hand-sizing line (20% margin)"), fontsize=8)
for r in rows:
    ax.plot(r["seat"], r["delta"], "o", color=D.MOMENT if r["ok"] else D.MUTED, ms=5)
    ax.annotate("{}/{}".format(r["seat"], r["bore"]), (r["seat"], r["delta"]), textcoords="offset points", xytext=(4, 4), fontsize=7.5)
ax.set_yscale("log")
ax.set_xlabel(T("轴承位直径 / mm（标注：外径/内孔）", "bearing-seat diameter / mm (labels: outer/bore)"))
ax.set_ylabel(T("末端偏移 / mm（峰值力矩）", "tool deflection / mm (peak torque)"))
ax.legend(fontsize=8, frameon=False)
fig.tight_layout()
figure(fig, "fig33_10_2")

fig, ax = plt.subplots(figsize=(6.6, 2.9))
lay, z = [], 0.0
for D_, L, n in segs:
    lay.append((z, z + L, D_))
    z += L
D.shaft(ax, lay)
for z0, z1, d_ in lay:
    ax.add_patch(D.Rectangle((z0, -R.BORE / 2), z1 - z0, R.BORE, fc="white", ec=D.INK, lw=0.8, zorder=3))
for zc in (lay[1][0] + 8, lay[3][0] + 8):
    D.bearing(ax, zc, brg["d"], brg["D"], brg["B"])
ax.add_patch(D.Rectangle((-30, -hd["OD"] / 2), 30, hd["OD"], fc="#dfe6ec", ec=D.INK, lw=0.9, zorder=1))
ax.text(-15, 0, T("谐波减速器\nCSF-25", "harmonic drive\nCSF-25"), ha="center", va="center", fontsize=7.5)
ax.add_patch(D.Rectangle((lay[-1][1], -60), 14, 120, fc="#f1e3c8", ec=D.INK, lw=0.9, zorder=1))
ax.text(lay[-1][1] + 18, 52, T("大臂", "upper arm"), fontsize=8)
ax.text(z / 2, -66, T("内孔 Ø30（减重，也可走线）", "Ø30 bore (lighter, room for cables)"), ha="center", fontsize=8)
ax.set_xlim(-40, z + 50)
ax.set_ylim(-75, 70)
ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout()
figure(fig, "fig33_10_3")

out(T_peak=T_peak, T_min=T_min, T_rms=T_rms, T_av=T_av, F_peak=F_peak, w_max_deg=math.degrees(w_max), cycle_s=R.CYCLE_S,
    payload=R.PAYLOAD_KG, reach=R.REACH_MM, budget=R.DEFLECT_BUDGET_MM, life_req=R.LIFE_H,
    hd_rated=hd["rated"], hd_repeat=hd["repeat"], hd_avg=hd["avg"], hd_mom=hd["momentary"], hd_nmax=hd["n_max"], hd_ratio=hd["ratio"],
    hd_od=hd["OD"], n_in_max=n_in_max, hd_ok=hd_ok,
    rows=[{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()} for r in rows],
    d_pick=pick["delta"], m_pick=pick["mass"], d_4525=rows[0]["delta"], m_4525=rows[0]["mass"], d_4530=rows[1]["delta"],
    m_4530=rows[1]["mass"], d_5034=rows[3]["delta"], d_5038=rows[4]["delta"], m_5038=rows[4]["mass"], seat=R.SEAT, bore=R.BORE, brg=R.BEARING, brg_D=brg["D"], brg_B=brg["B"],
    G_st=G(st) / 1000, G_al=G(al) / 1000, rho_st=st["density"], rho_al=al["density"],
    th_st_urad=th_st * 1e6, th_al_urad=th_al * 1e6, d_al=th_al * R.REACH_MM, m_st=m_st, m_al=m_al, k_al=k,
    m_al_same=m_al_same, bore_big=bore_big, m_st_big=m_st_big, wall_big=wall_big, m_al_body=m_al_body, m_big_body=m_big_body, m_al_fl=m_al_fl, m_big_fl=m_big_fl, m_5034=rows[3]["mass"], Gr_st=G(st) / st["density"] / 1000, Gr_al=G(al) / al["density"] / 1000, seat_al=R.SEAT * k, M_b=M_b / 1e3, sig=sig, tau=tau, s_vm=s_vm, S_static=S_static,
    sigma_s=st["sigma_s"], tau_stop=tau_stop, S_stop=S_stop, arm_offset=R.ARM_OFFSET,
    vm_hot=vm_hot, margin=R.HAND_MARGIN, d_fe=theta_fe * R.REACH_MM, n_el=stats["elements"], theta_fe_urad=theta_fe * 1e6, err_theta=err_theta, vm_fe=stats["vm_max_mpa"],
    tau_hand_body=tau_hand_body, life_inf=life_inf, life_h=fs["life_hours"], life_exp=math.floor(math.log10(fs["life_hours"])) if fs["life_hours"] and math.isfinite(fs["life_hours"]) else None, cycles_block=fs["cycles_per_block"], S_D=fs["S_D"],
    total_len=z)
