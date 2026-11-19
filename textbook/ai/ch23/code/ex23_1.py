"""算例 23.2.1：鸟瞰图坐标变换，以及标定错一点点在远处放大成多少（23.2 节）。

一件事：**鸟瞰图是靠“地面是平的 + 相机位姿已知”算出来的，不是拍出来的。**
所以俯仰角与安装高度各错一点点，折到地面上就是定位误差；而这个误差**随距离平方长大**：
近处看不出来，远处差出几个车身。

俯仰角差 0.3°、安装高度差 2 cm，都是标定里完全正常的残差——本算例把它们折成米。
"""
import numpy as np

from _ch23 import CAM, BEV, ground_to_pixel, pixel_to_ground, grid_shape, static_targets, \
    vehicle_to_grid, grid_to_vehicle, horizon_v
from bookout import out

v = {}

# ---------- 零、先确认正反投影自己是自洽的（没有这一步，后面的误差分不清是谁的）
XS = np.array([10.0, 20.0, 30.0, 50.0, 70.0])
YS = np.array([1.6, -1.6, 1.6, -1.6, 1.6])
u, vv = ground_to_pixel(XS, YS, CAM["pitch"], CAM["height"])
X_back, Y_back = pixel_to_ground(u, vv, CAM["pitch"], CAM["height"])
v["roundtrip_max_err_m"] = float(np.max(np.abs(X_back - XS)))
assert v["roundtrip_max_err_m"] < 1e-9, "正反投影必须完全互逆，否则后面量的不是标定误差"
print(f"正反投影自洽：往返最大误差 {v['roundtrip_max_err_m']:.2e} m")

v["cam_f_px"], v["cam_w"], v["cam_h"] = CAM["f"], CAM["w"], CAM["h"]
v["pitch_deg"] = np.degrees(CAM["pitch"])
v["height_m"] = CAM["height"]
v["horizon_row"] = horizon_v(CAM["pitch"])
print(f"标称外参：俯视角 {v['pitch_deg']:.2f}°、安装高度 {v['height_m']:.2f} m，"
      f"地平线在第 {v['horizon_row']:.0f} 行（共 {CAM['h']} 行）")

# ---------- 一、鸟瞰图网格：一个格子在地面上有多大，像平面上又占多少像素
rows, cols = grid_shape()
v["bev_rows"], v["bev_cols"], v["bev_res_m"] = rows, cols, BEV["res"]
v["bev_range_m"] = BEV["x_max"]
print(f"\n鸟瞰图网格 {rows}×{cols} 格，每格 {BEV['res']:.2f} m，看到 {BEV['x_max']:.0f} m")

tg = static_targets()
r_t, c_t = vehicle_to_grid(tg[:, 0], tg[:, 1])
Xc, Yc = grid_to_vehicle(r_t, c_t)
v["grid_quant_max_m"] = float(np.max(np.abs(np.column_stack([Xc, Yc]) - tg)))
assert v["grid_quant_max_m"] <= BEV["res"], "落格误差不该超过一个格子"
print(f"{len(tg)} 个路侧目标落格，最大落格误差 {v['grid_quant_max_m']:.2f} m（≤ 一格）")

# 同样一个 0.2 m 的格子，在像平面上占多少像素——远处的“一格”根本不到一个像素
for X in (10.0, 30.0, 50.0):
    u1, _ = ground_to_pixel(np.array([X]), np.array([0.0]), CAM["pitch"], CAM["height"])
    u2, _ = ground_to_pixel(np.array([X]), np.array([BEV["res"]]), CAM["pitch"], CAM["height"])
    v[f"px_per_cell_{int(X)}m"] = float(abs(u2[0] - u1[0]))
    print(f"  {X:.0f} m 处，一个 {BEV['res']:.1f} m 的格子横向只占 "
          f"{v[f'px_per_cell_{int(X)}m']:.2f} 像素")
assert v["px_per_cell_50m"] < v["px_per_cell_10m"], "远处同样的格子占的像素必然更少"
v["px_cell_ratio_10_50"] = v["px_per_cell_10m"] / v["px_per_cell_50m"]
print(f"**10 m 与 50 m 差 {v['px_cell_ratio_10_50']:.0f} 倍**——"
      f"鸟瞰图里远处那一片，信息量根本不够填满它")

# ---------- 二、标定错一点点：折到地面上是多少米
D_PITCH_DEG = 0.3          # 俯仰角标定残差（°），显式假设
D_HEIGHT_M = 0.02          # 安装高度标定残差（m），显式假设
D_YAW_DEG = 0.3            # 偏航角标定残差（°），显式假设
v["d_pitch_deg"], v["d_height_m"], v["d_yaw_deg"] = D_PITCH_DEG, D_HEIGHT_M, D_YAW_DEG

DIST = np.array([5.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0])
LAT = 1.75                 # 取车道中心线上的点

u_t, v_t = ground_to_pixel(DIST, np.full_like(DIST, LAT), CAM["pitch"], CAM["height"])

cases = {
    "pitch": (CAM["pitch"] + np.radians(D_PITCH_DEG), CAM["height"], 0.0),
    "height": (CAM["pitch"], CAM["height"] + D_HEIGHT_M, 0.0),
    "yaw": (CAM["pitch"], CAM["height"], np.radians(D_YAW_DEG)),
    "both": (CAM["pitch"] + np.radians(D_PITCH_DEG), CAM["height"] + D_HEIGHT_M,
             np.radians(D_YAW_DEG)),
}
err = {}
print(f"\n标定残差：俯视角 +{D_PITCH_DEG}°、安装高度 +{D_HEIGHT_M * 100:.0f} cm、"
      f"偏航角 +{D_YAW_DEG}°")
print("距离(m)  只俯仰角(纵向 m)  只高度(纵向 m)  只偏航角(横向 m)  三个都错(纵向/横向 m)")
for tag, (p, h, yw) in cases.items():
    Xe, Ye = pixel_to_ground(u_t, v_t, p, h, yaw=yw)
    err[tag] = (np.abs(Xe - DIST), np.abs(Ye - LAT))
for i, d in enumerate(DIST):
    print(f"{d:6.0f}  {err['pitch'][0][i]:15.3f}  {err['height'][0][i]:13.3f}  "
          f"{err['yaw'][1][i]:15.3f}  {err['both'][0][i]:9.3f} / {err['both'][1][i]:.3f}")

for tag in cases:
    for i, d in enumerate(DIST):
        if d in (10.0, 30.0, 50.0, 80.0):
            v[f"lon_{tag}_{int(d)}m"] = float(err[tag][0][i])
            v[f"lat_{tag}_{int(d)}m"] = float(err[tag][1][i])

v["lon_amp_50_over_10"] = v["lon_both_50m"] / v["lon_both_10m"]
v["lat_amp_50_over_10"] = v["lat_yaw_50m"] / v["lat_yaw_10m"]
print(f"\n50 m 处的纵向误差是 10 m 处的 {v['lon_amp_50_over_10']:.1f} 倍"
      f"（三项都错）；横向误差（只偏航角错）是 {v['lat_amp_50_over_10']:.1f} 倍")
assert v["lon_amp_50_over_10"] >= 5.0, \
    "标定误差折到地面上随距离平方长大，50 m 比 10 m 至少大 5 倍"
assert v["lat_amp_50_over_10"] >= 4.0, "横向误差随距离一次方长大，50 m 比 10 m 至少大 4 倍"

# **一个要照实写的意外**：三项残差凑在一起时，横向误差在这条车道上几乎互相抵消了
v["lat_both_50m_vs_yaw"] = v["lat_both_50m"] / v["lat_yaw_50m"]
print(f"但三项一起错时，50 m 处的横向误差只有 {v['lat_both_50m']:.3f} m，"
      f"是单独偏航角错的 {v['lat_both_50m_vs_yaw']:.2f} 倍——"
      f"俯仰角错把距离算远了、把横向按比例缩小，正好与偏航角错的方向相反")
print("**这不是好消息，是最坏的消息**：标定残差可以在某一个距离、某一条车道上互相抵消，"
      "于是在那一处验收全是绿的。所以标定验收必须沿整条距离、整个横向范围逐点报，"
      "不能只在一个点上看。")

# 平方律：误差 ≈ 常数 × 距离²，用对数斜率量出来
mask = DIST >= 10.0
slope = np.polyfit(np.log(DIST[mask]), np.log(err["pitch"][0][mask]), 1)[0]
v["lon_power_law"] = float(slope)
print(f"只俯仰角错的那一列，误差对距离的幂次是 {v['lon_power_law']:.2f}"
      f"（≈2，就是平方律）")
assert 1.7 < v["lon_power_law"] < 2.4, "俯仰角错折成纵向误差应近似平方律"

# ---------- 三、折成“够不够用”：50 m 外还认不认得出在哪条车道
v["lane_w"] = 3.5
v["lat_err_50m_in_lanes"] = v["lat_yaw_50m"] / v["lane_w"]
v["lon_err_50m_in_cars"] = v["lon_both_50m"] / 4.8
print(f"\n折成看得懂的单位：50 m 处纵向差 {v['lon_both_50m']:.2f} m = "
      f"{v['lon_err_50m_in_cars']:.2f} 个车身；只偏航角错时横向差 {v['lat_yaw_50m']:.2f} m = "
      f"{v['lat_err_50m_in_lanes']:.2f} 个车道宽")
print(f"而 10 m 处纵向只差 {v['lon_both_10m']:.2f} m——"
      f"**近处标得准，不说明远处标得准**")
v["lat_yaw_power_law"] = float(np.polyfit(np.log(DIST[mask]),
                                          np.log(err["yaw"][1][mask]), 1)[0])
print(f"\n三项残差的分工：俯仰角与高度错，主要折成**纵向**误差"
      f"（50 m 处 {v['lon_pitch_50m']:.2f} m）；偏航角错折成**横向**误差，"
      f"幂次 {v['lat_yaw_power_law']:.2f}（≈1，一次方）")
assert 0.8 < v["lat_yaw_power_law"] < 1.3, "偏航角错折成横向误差应近似一次方"

# 俯仰角错也会带来横向误差，但它**与目标的横向偏置成正比**：正对着看的目标不受影响
u0, v0 = ground_to_pixel(DIST, np.zeros_like(DIST), CAM["pitch"], CAM["height"])
_, Y_axis = pixel_to_ground(u0, v0, CAM["pitch"] + np.radians(D_PITCH_DEG), CAM["height"])
v["lat_pitch_onaxis_50m"] = float(np.abs(Y_axis[i50_ := int(np.where(DIST == 50.0)[0][0])]))
print(f"同样的俯仰角残差，正对车道中心（横向 0）的目标横向误差只有 "
      f"{v['lat_pitch_onaxis_50m']:.2e} m，而横向偏 {LAT:.2f} m 的目标差 "
      f"{v['lat_pitch_50m']:.2f} m——**俯仰角错带来的横向误差与横向偏置成正比**")
assert v["lat_pitch_onaxis_50m"] < 1e-9, "正对着看的目标，俯仰角错不产生横向误差"

# 折成“多大的偏航角残差会把车判到隔壁车道”：这是能直接写进验收单的数
v["yaw_half_lane_deg"] = float(np.degrees(np.arctan(3.5 / 2 / 50.0)))
print(f"反过来算验收门槛：要让 50 m 处的横向误差超过半个车道（{3.5 / 2:.2f} m），"
      f"偏航角只需错 {v['yaw_half_lane_deg']:.2f}°——标定验收的偏航角残差必须比这个小一个量级")

# ---------- 四、一个像素值多少米：鸟瞰图的分辨率极限
for X in (10.0, 50.0):
    u0, v0 = ground_to_pixel(np.array([X]), np.array([0.0]), CAM["pitch"], CAM["height"])
    X1, _ = pixel_to_ground(u0, v0 + 1.0, CAM["pitch"], CAM["height"])
    v[f"m_per_px_{int(X)}m"] = float(abs(X1[0] - X))
    print(f"{X:.0f} m 处，像平面上差一行（1 像素）就是 {v[f'm_per_px_{int(X)}m']:.3f} m")
v["px_value_ratio"] = v["m_per_px_50m"] / v["m_per_px_10m"]
assert v["px_value_ratio"] > 10, "一个像素在远处值多少米，差一个量级以上"
print(f"**差 {v['px_value_ratio']:.0f} 倍**：所以远处的格子不是“看不清”，是“一个像素都没有”")

print("\n这个算例回答不了什么：真路面不是平的（上下坡、路拱），本算例假设地面是平面；"
      "真标定残差不是常数偏置（会随温度、载重、颠簸变）；真系统还有激光雷达与高精地图"
      "来兜住远处——但那几路也各有自己的标定误差，叠起来不会比这里小。")

out(**v)
