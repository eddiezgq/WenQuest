"""算例 21.3.1—21.3.3：轴承故障在振动里长什么样（21.3 节）。

三件事：
（1）**故障特征频率是算出来的，不是学出来的**：由滚动体个数、直径、节圆直径与转速决定，
    本算例按几何算出四个频率，再在合成信号里把它找出来，两边必须对得上；
（2）**直接看频谱看不见它**：局部故障的冲击激起的是高频共振，故障频率只在**包络谱**上出现；
（3）**转速一变，频率全变**：所以拿一个转速下训的模型去判另一个转速，先问它见过没有。

本算例用的几何取公开轴承数据集里常见的那一种（9 个滚动体、滚动体直径 7.94 mm、
节圆直径 39.04 mm），**合成信号是程序造的**，不是任何实测数据。
"""
import numpy as np

from _ch21 import bearing_freqs, bearing_signal, envelope, peak_near, spectrum
from bookout import out

FS, SECONDS = 12000.0, 2.0
N_BALLS, D_BALL, D_PITCH = 9, 7.94, 39.04
RPM = 1797.0
v = {"fs": FS, "seconds": SECONDS, "n_balls": N_BALLS,
     "d_ball": D_BALL, "d_pitch": D_PITCH, "rpm": RPM}

# ---------- 一、按几何算四个特征频率
f = bearing_freqs(N_BALLS, D_BALL, D_PITCH, RPM)
for k in ("fr", "BPFO", "BPFI", "BSF", "FTF"):
    v[k.lower()] = f[k]
print(f"轴频 {f['fr']:.2f} Hz；外圈 BPFO {f['BPFO']:.2f}；内圈 BPFI {f['BPFI']:.2f}；"
      f"滚动体 BSF {f['BSF']:.2f}；保持架 FTF {f['FTF']:.2f} Hz")

# 两条能自查的关系：BPFO + BPFI = 滚动体个数 × 轴频；FTF < fr/2
v["sum_check"] = (f["BPFO"] + f["BPFI"]) / (N_BALLS * f["fr"])
v["bpfo_per_rev"] = f["BPFO"] / f["fr"]
v["bpfi_per_rev"] = f["BPFI"] / f["fr"]
print(f"自查：(BPFO + BPFI) / (n × 轴频) = {v['sum_check']:.6f}（应当正好是 1）；"
      f"外圈每转 {v['bpfo_per_rev']:.3f} 次，内圈每转 {v['bpfi_per_rev']:.3f} 次")
assert abs(v["sum_check"] - 1.0) < 1e-12, "这两个频率的和必须等于滚动体个数乘轴频"
assert f["FTF"] < f["fr"] / 2, "保持架转得比轴慢"

# ---------- 二、频谱上找不到，包络谱上找得到
x = bearing_signal(FS, SECONDS, f["BPFO"], RPM, carrier_hz=3200.0, noise=0.35, seed=0)
fa, X = spectrum(x, FS)
fe, E = spectrum(envelope(x) - np.mean(envelope(x)), FS)

win = 2.0
pk_raw = peak_near(fa, X, f["BPFO"], win)
pk_env = peak_near(fe, E, f["BPFO"], win)
# 本底：故障频率附近 20—300 Hz 这一段的中位幅值
band_raw = np.median(X[(fa > 20) & (fa < 300)])
band_env = np.median(E[(fe > 20) & (fe < 300)])
v["raw_peak_hz"] = pk_raw[0]
v["raw_snr"] = pk_raw[1] / band_raw
v["env_peak_hz"] = pk_env[0]
v["env_snr"] = pk_env[1] / band_env
v["snr_gain"] = v["env_snr"] / v["raw_snr"]
print(f"\n原始频谱：在 {f['BPFO']:.1f} Hz 附近的峰 {v['raw_peak_hz']:.2f} Hz，"
      f"比本底高 {v['raw_snr']:.1f} 倍")
print(f"包络谱　：在 {f['BPFO']:.1f} Hz 附近的峰 {v['env_peak_hz']:.2f} Hz，"
      f"比本底高 {v['env_snr']:.1f} 倍")
print(f"**包络把故障频率的显著程度提高了 {v['snr_gain']:.0f} 倍**——"
      f"冲击激起的是高频共振，故障频率是它的调制频率，不做包络就看不见")
assert v["env_snr"] > 3 * v["raw_snr"], "包络谱应当明显更能看见故障频率"
assert abs(v["env_peak_hz"] - f["BPFO"]) < win, "包络谱上的峰必须落在算出来的频率上"

# 包络谱上还应当有它的谐波
for k in (2, 3):
    hz, amp = peak_near(fe, E, k * f["BPFO"], win)
    v[f"env_harm{k}_hz"] = hz
    v[f"env_harm{k}_snr"] = amp / band_env
    print(f"　二次以上：{k} 倍频 {hz:.2f} Hz（算出来是 {k * f['BPFO']:.2f}），"
          f"比本底高 {v[f'env_harm{k}_snr']:.1f} 倍")
assert v["env_harm2_snr"] > 2.0, "局部故障的包络谱应当有谐波"

# ---------- 三、转速一变，频率全变
rows = []
for rpm in (1730.0, 1750.0, 1772.0, 1797.0):
    ff = bearing_freqs(N_BALLS, D_BALL, D_PITCH, rpm)
    rows.append((rpm, ff["BPFO"], ff["BPFI"]))
    v[f"bpfo_{int(rpm)}"] = ff["BPFO"]
    print(f"转速 {rpm:>6.0f} r/min：BPFO {ff['BPFO']:.2f} Hz，BPFI {ff['BPFI']:.2f} Hz")
v["bpfo_spread_hz"] = rows[-1][1] - rows[0][1]
v["bpfo_spread_pct"] = v["bpfo_spread_hz"] / rows[0][1] * 100
print(f"四档负载（转速差 {rows[-1][0] - rows[0][0]:.0f} r/min）之间，"
      f"外圈频率差 {v['bpfo_spread_hz']:.2f} Hz（{v['bpfo_spread_pct']:.1f}%）")

# 拿一个转速下的"故障频率窗口"去判另一个转速：窗口开窄了就抓不到
narrow = 1.0
hit = 0
for rpm in (1730.0, 1750.0, 1772.0, 1797.0):
    if abs(bearing_freqs(N_BALLS, D_BALL, D_PITCH, rpm)["BPFO"] - f["BPFO"]) <= narrow:
        hit += 1
v["narrow_window_hz"] = narrow
v["narrow_hit"] = hit
print(f"若把判据写死成“{f['BPFO']:.1f} ± {narrow:.0f} Hz 有峰”，"
      f"四档转速里只有 {hit} 档落在窗口里")
assert hit < 4, "写死频率窗口必然在别的转速上失效"
print("**所以转速必须进模型**（或者先按转速归一化成“每转几次”）——"
      "这是本章第一条“换个工况还准不准”的例子")

out(**v)
