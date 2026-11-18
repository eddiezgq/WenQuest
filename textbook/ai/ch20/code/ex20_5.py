"""算例 20.5.1—20.5.2：训练集的划分口径（20.4 节）。

机器学习势的训练数据多来自**结构松弛的轨迹**：同一个结构的几十帧只差一点点。于是

* **按帧随机划分**：测试集里每一帧，在训练集里都有一个几乎相同的孪生兄弟；
* **按体系划分**：整条轨迹要么全训练、要么全测试；
* **按成分划分**：整个成分（含它下面所有体系）要么全训练、要么全测试。

三种口径量出来的误差差几倍，而论文里印的往往只说"测试集 MAE"。这是第 18.5 节骨架划分、
第 19.5 节区块划分之后，同一件事的**第三次**露面。
"""
import numpy as np

from _ch20 import (BASIS, basis_centers, energy_mae, featurize, featurize_forces,
                   force_mae, make_trajectories, split_frames)
from bookout import out

L, N = 12.0, 10
CENTERS, WIDTH = basis_centers(), BASIS["width"]
N_SYS, N_FRAMES = 10, 36       # “少体系、多帧”：结构松弛轨迹数据集最常见的形状

v = {"n_sys": N_SYS, "n_frames": N_FRAMES, "n_atoms": N}
systems = make_trajectories(N_SYS, N, L, seed=0, n_frames=N_FRAMES)
v["n_comp"] = len({s["comp"] for s in systems})
v["n_total_frames"] = sum(len(s["frames"]) for s in systems)
print(f"{v['n_sys']} 个体系、{v['n_comp']} 个成分、共 {v['n_total_frames']} 帧")

# 同一条轨迹上相邻两帧有多像——这是泄漏的来源，先量出来
near = []
for s in systems:
    for a, b in zip(s["frames"][:-1], s["frames"][1:]):
        near.append(float(np.abs(a["x"] - b["x"]).max()))
far = []
for i in range(len(systems) - 1):
    far.append(float(np.abs(systems[i]["frames"][0]["x"]
                            - systems[i + 1]["frames"][0]["x"]).max()))
v["gap_within_traj"] = float(np.mean(near))
v["gap_across_sys"] = float(np.mean(far))
v["gap_ratio"] = v["gap_across_sys"] / v["gap_within_traj"]
print(f"同一条轨迹相邻帧的坐标差 {v['gap_within_traj']:.4f}，"
      f"不同体系之间 {v['gap_across_sys']:.4f}（差 {v['gap_ratio']:.0f} 倍）")


def fit_rows(rows):
    A, b = [], []
    for _, _, fr in rows:
        A.append(featurize(fr["x"], L, CENTERS, WIDTH)[None, :])
        b.append([fr["e"]])
        A.append(0.1 * featurize_forces(fr["x"], L, CENTERS, WIDTH))
        b.append(0.1 * fr["f"])
    A = np.vstack(A)
    b = np.concatenate([np.atleast_1d(t) for t in b])
    return np.linalg.solve(A.T @ A + 1e-8 * np.eye(A.shape[1]), A.T @ b)


# ---------- 一、三种口径，在"少体系、多帧"的数据上（实践中最常见的那一种）
N_SEED = 12
for how in ("frame", "system", "composition"):
    es, fs = [], []
    for seed in range(N_SEED):
        train, test = split_frames(systems, how, seed=seed)
        w = fit_rows(train)
        es.append(energy_mae(w, test, L, CENTERS, WIDTH))
        fs.append(force_mae(w, test, L, CENTERS, WIDTH))
    # 用**中位数**作代表：折与折之间能差几十倍，平均数会被一折带跑
    v[f"e_{how}"] = float(np.median(es))
    v[f"e_{how}_lo"] = float(np.min(es))
    v[f"e_{how}_hi"] = float(np.max(es))
    v[f"f_{how}"] = float(np.median(fs))
    print(f"{how:>12}：能量误差/原子 中位数 {v[f'e_{how}']:.3e}"
          f"（{N_SEED} 折最好 {v[f'e_{how}_lo']:.1e}、最差 {v[f'e_{how}_hi']:.1e}）　"
          f"力误差 {v[f'f_{how}']:.3e}")

v["e_ratio_sys"] = v["e_system"] / v["e_frame"]
v["e_ratio_comp"] = v["e_composition"] / v["e_frame"]
v["spread_frame"] = v["e_frame_hi"] / v["e_frame_lo"]
v["spread_comp"] = v["e_composition_hi"] / v["e_composition_lo"]
print(f"\n按体系划分是按帧划分的 {v['e_ratio_sys']:.1f} 倍，按成分划分是 {v['e_ratio_comp']:.1f} 倍")
print(f"抖动完全不同：按帧划分最好与最差只差 {v['spread_frame']:.1f} 倍，"
      f"按成分划分差 {v['spread_comp']:.0f} 倍")
print("**所以按成分划分必须跑多折、报中位数与范围**；只跑一折，想要什么数都能“要”到")
assert v["e_system"] > v["e_frame"], "按帧随机划分应当给出偏乐观的成绩"
assert v["spread_comp"] > v["spread_frame"] * 3, "按成分划分的折间抖动应当大得多"

# ---------- 二、泄漏有多严重，取决于数据里到底有多少个互不相同的体系
# 总帧数固定在 360 左右，把它分成"少体系多帧"到"多体系少帧"几档。
# 这一段是本算例真正的结论：**同一个划分动作，在不同形状的数据上后果差一个量级**。
print("\n总帧数固定，看“体系数 × 每体系帧数”这个形状怎么影响泄漏：")
for n_sys, n_fr in ((5, 72), (10, 36), (30, 12), (60, 6)):
    sysx = make_trajectories(n_sys, N, L, seed=5, n_frames=n_fr)
    got = {}
    for how in ("frame", "system"):
        es = []
        for seed in range(8):
            tr, te = split_frames(sysx, how, seed=seed)
            if not tr or not te:
                continue
            w = fit_rows(tr)
            es.append(energy_mae(w, te, L, CENTERS, WIDTH))
        got[how] = float(np.median(es))
    ratio = got["system"] / got["frame"]
    v[f"shape_{n_sys}x{n_fr}_frame"] = got["frame"]
    v[f"shape_{n_sys}x{n_fr}_system"] = got["system"]
    v[f"shape_{n_sys}x{n_fr}_ratio"] = ratio
    print(f"  {n_sys:>2d} 个体系 × 每个 {n_fr:>2d} 帧：按帧 {got['frame']:.3e}　"
          f"按体系 {got['system']:.3e}　**差 {ratio:>6.1f} 倍**")

v["ratio_few_systems"] = v["shape_5x72_ratio"]
v["ratio_many_systems"] = v["shape_60x6_ratio"]
assert v["ratio_few_systems"] > v["ratio_many_systems"] * 3, \
    "体系越少、每个体系帧越多，按帧随机划分高估得越厉害"
print(f"\n**少体系多帧（{v['ratio_few_systems']:.0f} 倍）比多体系少帧（"
      f"{v['ratio_many_systems']:.1f} 倍）严重得多**——而“少体系多帧”恰恰是"
      f"结构松弛轨迹数据集最常见的形状")

# ---------- 三、每条轨迹只取一帧：泄漏就没了
thin = [{"sys": s["sys"], "comp": s["comp"], "frames": s["frames"][:1]} for s in systems]
es = []
for seed in range(N_SEED):
    train, test = split_frames(thin, "frame", seed=seed)
    if not train or not test:
        continue
    w = fit_rows(train)
    es.append(energy_mae(w, test, L, CENTERS, WIDTH))
v["e_frame_thinned"] = float(np.median(es))
v["thin_ratio"] = v["e_frame_thinned"] / v["e_frame"]
print(f"\n每条轨迹只留一帧再按帧随机划分：误差 {v['e_frame_thinned']:.3e}，"
      f"是原来的 {v['thin_ratio']:.1f} 倍")
print("**所以不是“按帧划分”这个动作本身错，是轨迹里的帧彼此太像**——"
      "去掉冗余帧，按帧划分也能给出诚实的数")
assert v["e_frame_thinned"] > v["e_frame"], "去掉冗余帧之后，按帧划分的成绩应当变诚实（变差）"

out(**v)
