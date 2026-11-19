"""23.2 节的图：标定错一点点，在远处放大成多少。

图 23.2.1：（a）三种标定残差各自折成的地面定位误差随距离怎么长（双对数，看得出幂次）；
（b）折成看得懂的单位——50 m 处差几个车身、几个车道宽，以及一个像素在远处值多少米。
"""
import numpy as np

from _ch23 import CAM, ground_to_pixel, pixel_to_ground
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

D_PITCH, D_HEIGHT, D_YAW = 0.3, 0.02, 0.3        # ° / m / °
DIST = np.linspace(5, 80, 160)
LAT = 1.75

u_t, v_t = ground_to_pixel(DIST, np.full_like(DIST, LAT), CAM["pitch"], CAM["height"])
cases = {
    "pitch": (CAM["pitch"] + np.radians(D_PITCH), CAM["height"], 0.0),
    "height": (CAM["pitch"], CAM["height"] + D_HEIGHT, 0.0),
    "yaw": (CAM["pitch"], CAM["height"], np.radians(D_YAW)),
}
err = {}
for tag, (p, h, yw) in cases.items():
    Xe, Ye = pixel_to_ground(u_t, v_t, p, h, yaw=yw)
    err[tag] = (np.abs(Xe - DIST), np.abs(Ye - LAT))

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 双对数：误差随距离的幂次
a.loglog(DIST, err["pitch"][0], color=C["x"], lw=2.2,
         label=T(f"俯仰角差 {D_PITCH}° → 纵向误差", f"pitch off by {D_PITCH}° → longitudinal"))
a.loglog(DIST, err["height"][0], color=C["y"], lw=2.2,
         label=T(f"安装高度差 {D_HEIGHT * 100:.0f} cm → 纵向误差",
                 f"height off by {D_HEIGHT * 100:.0f} cm → longitudinal"))
a.loglog(DIST, err["yaw"][1], color=C["z"], lw=2.2, ls="--",
         label=T(f"偏航角差 {D_YAW}° → 横向误差", f"yaw off by {D_YAW}° → lateral"))
ref = DIST ** 2 / 50.0 ** 2 * err["pitch"][0][-1] * (50.0 / 80.0) ** 2
a.loglog(DIST, ref, color=C["muted"], lw=1.1, ls=":",
         label=T("参照：按距离平方", "reference: $\\propto$ distance$^2$"))
for x0 in (10.0, 50.0):
    a.axvline(x0, color=C["muted"], lw=0.8, ls=":")
i10 = int(np.argmin(np.abs(DIST - 10)))
i50 = int(np.argmin(np.abs(DIST - 50)))
a.annotate(T(f"10 m：{err['pitch'][0][i10]:.2f} m", f"10 m: {err['pitch'][0][i10]:.2f} m"),
           xy=(10, err["pitch"][0][i10]), xytext=(10, -26), textcoords="offset points",
           fontsize=8.5, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))
a.annotate(T(f"50 m：{err['pitch'][0][i50]:.1f} m", f"50 m: {err['pitch'][0][i50]:.1f} m"),
           xy=(50, err["pitch"][0][i50]), xytext=(-64, 16), textcoords="offset points",
           fontsize=8.5, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))
a.annotate(T(f"俯仰角那一条：50 m 的误差是 10 m 的 "
             f"{err['pitch'][0][i50] / err['pitch'][0][i10]:.0f} 倍（≈ 距离平方）",
             f"pitch curve: the error at 50 m is "
             f"{err['pitch'][0][i50] / err['pitch'][0][i10]:.0f}$\\times$ that at 10 m "
             f"($\\approx$ distance$^2$)"),
           xy=(0.97, 0.04), xycoords="axes fraction", ha="right", va="bottom",
           fontsize=8.5, color=C["accent"])
a.set_xlabel(T("目标距离（m）", "target distance (m)"))
a.set_ylabel(T("地面定位误差（m）", "ground localization error (m)"))
a.set_title(T("(a) 同样的标定残差，远处的误差大一两个量级",
              "(a) the same residual, one or two orders worse far away"), fontsize=10)
a.legend(fontsize=8, loc="upper left", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5, which="both")

# ---------------- (b) 折成看得懂的单位
shown = np.array([10.0, 20.0, 30.0, 50.0, 70.0])
idx = [int(np.argmin(np.abs(DIST - s))) for s in shown]
cars = np.array([err["pitch"][0][i] for i in idx]) / 4.8
lanes = np.array([err["yaw"][1][i] for i in idx]) / 3.5
xs = np.arange(len(shown))
b.bar(xs - 0.19, cars, 0.36, color=C["x"],
      label=T("纵向误差（折成车身数，车长 4.8 m）",
              "longitudinal error (in car lengths, 4.8 m)"))
b.bar(xs + 0.19, lanes, 0.36, color=C["z"],
      label=T("横向误差（折成车道宽，3.5 m）", "lateral error (in lane widths, 3.5 m)"))
for i, (cv, lv) in enumerate(zip(cars, lanes)):
    b.annotate(f"{cv:.2f}", xy=(i - 0.19, cv), xytext=(0, 3), textcoords="offset points",
               ha="center", fontsize=8, color=C["x"])
    b.annotate(f"{lv:.2f}", xy=(i + 0.19, lv), xytext=(0, 3), textcoords="offset points",
               ha="center", fontsize=8, color=C["z"])
b.axhline(1.0, color=C["accent"], lw=1.2, ls="--")
b.annotate(T("1 个车身 / 1 个车道", "one car length / one lane"),
           xy=(len(shown) - 0.5, 1.0), xytext=(-4, 8), textcoords="offset points", va="bottom",
           ha="right", fontsize=8.5, color=C["accent"])
b.set_xticks(xs)
b.set_xticklabels([f"{s:.0f} m" for s in shown], fontsize=9)
b.set_ylabel(T("误差（折成车身 / 车道）", "error (car lengths / lane widths)"))
b.set_ylim(0, max(cars.max(), 1.0) * 1.32)
b.set_title(T("(b) 近处标得准，不说明远处标得准",
              "(b) accurate up close says nothing about far away"), fontsize=10)
b.legend(fontsize=8, loc="upper left", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5, axis="y")

fig.tight_layout()
figure(fig, "fig23_2_1")
