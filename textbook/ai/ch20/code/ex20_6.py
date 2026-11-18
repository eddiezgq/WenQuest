"""算例 20.6.1—20.6.3："稳定"是对谁而言（20.4 节）。

材料里说一个相"稳定"，意思是它落在**形成能的下凸包**上。这句话里藏着两个条件，
而公开报道常常把它们省掉：

（1）**凸包是对一个参考集算的。** 参考集里多一个相，别人的距离就变——原来落在包上
    （距离 0，"稳定"）的点，可能一下子变成正距离（"不稳定"）。本算例把这件事算出来。
（2）**"稳定"是个阈值判断。** 阈值取 0、25 还是 50 meV/atom，候选数能差好几倍。
    所以"发现了 N 个稳定材料"这个数，不说阈值就没有意义。

另外还要分清：热力学稳定 ≠ 能合成。凸包上的相可能做不出来，包上方的亚稳相可能长期存在。
"""
import numpy as np

from _ch20 import convex_hull_lower, hull_distance, hull_energy_at
from bookout import out

# 一个伪二元体系 A—B：成分 x 是 B 的比例，y 是形成能（eV/atom，负的更稳）
# 这些点是造出来的，不代表任何真实体系。
POINTS = [(0.00, 0.000), (0.10, -0.060), (0.20, -0.150), (0.25, -0.230),
          (0.30, -0.240), (0.33, -0.300), (0.40, -0.250), (0.45, -0.290),
          (0.50, -0.330), (0.55, -0.280), (0.60, -0.240), (0.67, -0.250),
          (0.75, -0.190), (0.80, -0.120), (0.90, -0.055), (1.00, 0.000)]
v = {"n_points": len(POINTS)}

# ---------- 一、谁在包上
d0 = hull_distance(POINTS)
hull0 = convex_hull_lower(POINTS)
stable0 = [p for p, d in d0.items() if d < 1e-12]
v["n_hull_vertices"] = len(hull0)
v["n_stable_0"] = len(stable0)
v["hull_x"] = " ".join(f"{x:.2f}" for x, _ in hull0)
print(f"参考集 {v['n_points']} 个相，下凸包顶点 {v['n_hull_vertices']} 个："
      f"成分 {v['hull_x']}")
print(f"距离为 0（严格意义上“稳定”）的有 {v['n_stable_0']} 个")

# ---------- 二、阈值一改，"稳定"的个数就变
for thr in (0, 10, 25, 50, 100):
    n = sum(1 for d in d0.values() if d <= thr / 1000 + 1e-12)
    v[f"n_within_{thr}"] = n
    print(f"阈值 {thr:>3d} meV/atom 以内：{n:>2d} 个（占 {100 * n / len(POINTS):.0f}%）")
v["thr_ratio_50_over_0"] = v["n_within_50"] / v["n_within_0"]
assert v["n_within_0"] < v["n_within_50"] < v["n_points"] + 1
print(f"阈值从 0 放到 50 meV/atom，个数变成 {v['thr_ratio_50_over_0']:.1f} 倍——"
      f"**不说阈值，“发现了 N 个稳定材料”就没有意义**")

# ---------- 三、参考集里加一个相，原来"稳定"的点变不稳定
NEW = (0.42, -0.420)          # 新算出来（或新合成出来）的一个相，把 0.33—0.50 那一段压下去
d1 = hull_distance(POINTS, extra=[NEW])
flipped = [(p, d0[p], d1[p]) for p in POINTS if d0[p] < 1e-12 and d1[p] > 1e-12]
v["n_flipped"] = len(flipped)
v["new_phase_x"], v["new_phase_y"] = NEW
print(f"\n参考集里加入成分 {NEW[0]:.2f}、形成能 {NEW[1]:.3f} 的一个相之后：")
for p, before, after in flipped:
    print(f"  成分 {p[0]:.2f} 的相：距离从 {before * 1000:.0f} 变成 "
          f"{after * 1000:.0f} meV/atom——**从“稳定”变成“不稳定”**")
v["flip_x"] = " ".join(f"{p[0]:.2f}" for p, _, _ in flipped)
v["flip_after_mev"] = float(max(after for _, _, after in flipped) * 1000) if flipped else 0.0
assert v["n_flipped"] >= 1, "这个构造必须真的把某个原本在包上的相顶下来"
print(f"一共 {v['n_flipped']} 个相翻了号。**它们自己一个数都没变**——"
      f"变的只是参考集")

# ---------- 四、反过来：参考集不全时，会多报多少"稳定"
# 假装我们的数据库里缺了三个相（删掉凸包上的三个顶点），看有多少点被误判成稳定
missing = [p for p in hull0[1:-1]][:3]
partial = [p for p in POINTS if p not in missing]
d_partial = hull_distance(partial)
false_stable = [p for p in partial if d_partial[p] < 1e-12 and d0[p] > 1e-12]
v["n_missing"] = len(missing)
v["n_false_stable"] = len(false_stable)
v["false_stable_x"] = " ".join(f"{p[0]:.2f}" for p in false_stable)
print(f"\n参考集里缺了 {v['n_missing']} 个相（成分 "
      f"{' '.join(f'{p[0]:.2f}' for p in missing)}）：")
print(f"有 {v['n_false_stable']} 个相被误判成“稳定”（成分 {v['false_stable_x']}）")
assert v["n_false_stable"] >= 1, "参考集不全时应当会多报稳定相"
print("**所以“相对哪个数据库”这句话必须跟着那个数一起印**：数据库越不全，"
      "报出来的“新稳定相”越多")

out(**v)
