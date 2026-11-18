# GPU 实验 20.3 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 20.3　机器学习势跑分子动力学，和经典力场比一比
# 20.3 节说过：机器学习势学的是**势能面**，性质要拿这个势跑模拟再算出来。这个实验把它
# 真的跑一遍，在同一个体系上和经典力场逐项比：每步多久、体系一大怎么涨、能量守不守得住、
# 结构像不像。
#
# **口径先说清楚**（这一条比结果重要）：
#
# * 本实验**不排名准确度**。两种势都没有和第一性原理或实验对照——那正是算不起的那一步。
#   能比的只有耗时、增长、能量守恒，以及两者之间差多少。
# * 机器学习势的误差（论文里那些 meV/atom）是**对第一性原理说的**，不是对实验说的。
# * 官方写明的局限照记：MACE-MP-0 的论文说这一组模型**不含磁性或自旋自由度**；
#   CHGNet 显式纳入磁矩、报告磁矩平均绝对误差 0.032 µB，同时承认对**无磁矩离子**推断电荷不准；
#   训练数据 MPtrj **混用 GGA 与 GGA+U**。本实验选**无磁的金属铜**，正是为了避开第一条。
# %%
import sys; sys.path.insert(0, "..")
import time

import numpy as np
import wqgpu
env = wqgpu.check(("gpu", "torch"))

import torch
print(torch.cuda.get_device_name(0), torch.__version__,
      f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# mace-torch 自带 MACE-MP-0 的下载入口；ASE 提供体系、积分器与 EMT 经典力场
wqgpu.sh(f"{sys.executable} -m pip install -q mace-torch ase", timeout=3600)

# %% [markdown]
# ## 1. 两个计算器（任务 1）
# * **机器学习势**：MACE-MP-0 的 small 档，权重公开，第一次用会自动下载（几百 MB）。
# * **经典力场**：ASE 自带的 EMT（effective medium theory），几个参数的手写函数形式，
#   对铜这类金属是能用的；它快几个数量级。
#
# 两个计算器在同一个 `Atoms` 对象上调用，接口一模一样——这正是 ASE 的好处：
# **换势就是换一行**，别的都不动。
# %%
from ase.build import bulk
from ase.calculators.emt import EMT
from mace.calculators import mace_mp

DEV = "cuda"
mlip = mace_mp(model="small", device=DEV, default_dtype="float64")
classic = EMT()
print("两个计算器就绪")

# %% [markdown]
# ## 2. 体系（任务 2）
# 铜的面心立方结构，做一个 3×3×3 的超胞。原子数、晶格常数记进表 1 第一行。
# %%
a0 = 3.61                                   # 铜的实验晶格常数，Å（只作为建模的起点）
atoms = bulk("Cu", "fcc", a=a0, cubic=True).repeat((3, 3, 3))
N = len(atoms)
print(f"原子数 {N}，晶格常数 {a0} Å，盒子 {atoms.cell.lengths().round(2)}")

# %% [markdown]
# ## 3. 两种势各跑一段 NVE（任务 3）
# 微正则系综：不接恒温器，总能量应当守恒。**它守不住的程度，就是这个势“不像个势”的程度**
# （或者步长太大）。两边用同一个步长、同一个初速度，才比得了。
#
# 计时**跳过前 5 步**：第一次调用包含编译与显存分配，算进去会把结果带偏。
# %%
from ase import units
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.verlet import VelocityVerlet

DT_FS = 1.0                                  # 步长 1 飞秒，两边一样
N_STEP = 120
T0 = 500                                     # 初温 500 K


def run_nve(calc, n_step=N_STEP, warm=5, system=None):
    at = (system or atoms).copy()
    at.calc = calc
    MaxwellBoltzmannDistribution(at, temperature_K=T0, rng=np.random.default_rng(0))
    dyn = VelocityVerlet(at, DT_FS * units.fs)
    etot = []

    def rec():
        etot.append(at.get_total_energy())

    dyn.attach(rec, interval=1)
    dyn.run(warm)                            # 预热，不计时
    t0 = time.perf_counter()
    dyn.run(n_step)
    wall = time.perf_counter() - t0
    e = np.array(etot[warm:])
    drift = (e[-1] - e[0]) / len(at) * 1000   # meV/atom
    return {"ms_per_step": wall / n_step * 1000, "drift": drift, "atoms": at,
            "etot": e, "n": len(at)}


res_c = run_nve(classic)
res_m = run_nve(mlip)
for name, r in (("经典力场 EMT", res_c), ("机器学习势", res_m)):
    print(f"{name:>12}：每步 {r['ms_per_step']:8.2f} 毫秒　"
          f"跑 1 皮秒（1000 步）要 {r['ms_per_step']:7.2f} 秒　"
          f"总能量漂移 {r['drift']:+8.3f} meV/atom")
ratio = res_m["ms_per_step"] / res_c["ms_per_step"]
print(f"\n机器学习势比经典力场慢 {ratio:.0f} 倍（同一块卡、同一个体系、同一个步长）")

# %% [markdown]
# ## 4. 体系一大，代价怎么涨（任务 4）
# 把超胞依次放大，量每步耗时。两种势的函数形式都是**截断的**，所以理论上耗时应当与原子数
# 成正比（幂次 1）；实际测出来往往不是 1——显卡没喂饱时幂次小于 1，显存不够时又会跳上去。
# 拟出来的幂次填表 2。
# %%
sizes, n_list, ms_m, ms_c = [(2, 2, 2), (3, 3, 3), (4, 4, 4)], [], [], []
for rep in sizes:
    sys_i = bulk("Cu", "fcc", a=a0, cubic=True).repeat(rep)
    rm = run_nve(mlip, n_step=30, system=sys_i)
    rc = run_nve(classic, n_step=30, system=sys_i)
    n_list.append(len(sys_i)); ms_m.append(rm["ms_per_step"]); ms_c.append(rc["ms_per_step"])
    print(f"{rep}　{len(sys_i):>4d} 个原子：机器学习势 {rm['ms_per_step']:8.2f} 毫秒，"
          f"经典力场 {rc['ms_per_step']:7.3f} 毫秒，慢 {rm['ms_per_step'] / rc['ms_per_step']:.0f} 倍")

slope = float(np.polyfit(np.log(n_list), np.log(ms_m), 1)[0])
print(f"\n机器学习势的耗时 ∝ 原子数的 {slope:.2f} 次方")
print("幂次明显小于 1，多半是小体系没把显卡喂饱；明显大于 1，就该查显存与邻居表了")

# %% [markdown]
# ## 5. 两者给出的结构一样吗（任务 5）
# 两件事：
# 1. 在**同一批构型**上比两者给出的力——同一个输入、两个输出，直接相减；
# 2. 各自跑完之后算**径向分布函数**，看第一近邻峰在哪、多高。
#
# 注意第 2 件事比的是“两者之间”，不是“谁更对”。
# %%
from ase.geometry.analysis import Analysis


def forces_on(calc, frames):
    out = []
    for fr in frames:
        at = fr.copy(); at.calc = calc
        out.append(at.get_forces())
    return np.array(out)


frames = []
at = atoms.copy(); at.calc = mlip
MaxwellBoltzmannDistribution(at, temperature_K=T0, rng=np.random.default_rng(1))
dyn = VelocityVerlet(at, DT_FS * units.fs)
for _ in range(6):
    dyn.run(10)
    frames.append(at.copy())

f_m, f_c = forces_on(mlip, frames), forces_on(classic, frames)
f_gap = float(np.sqrt(((f_m - f_c) ** 2).mean()))
print(f"同一批构型上，两者力的均方根差 {f_gap:.4f} eV/Å")
print(f"（机器学习势自己的力均方根 {np.sqrt((f_m ** 2).mean()):.4f}，"
      f"经典力场 {np.sqrt((f_c ** 2).mean()):.4f} eV/Å）")


def rdf_peak(at, rmax=5.0, nbins=120):
    """径向分布函数的第一个峰：峰位（Å）与峰高。"""
    ana = Analysis(at)
    got = ana.get_rdf(rmax=rmax, nbins=nbins, return_dists=True)
    rdf, dists = got[0]                     # Analysis 对每一帧返回一组，这里只有一帧
    i = int(np.argmax(rdf))
    return float(dists[i]), float(rdf[i])


peak_m, high_m = rdf_peak(res_m["atoms"])
peak_c, high_c = rdf_peak(res_c["atoms"])
print(f"第一近邻峰位：机器学习势 {peak_m:.3f} Å（峰高 {high_m:.2f}），"
      f"经典力场 {peak_c:.3f} Å（峰高 {high_c:.2f}），差 {abs(peak_m - peak_c):.3f} Å")
print("这个差要和热涨落的宽度一起看——峰有多宽，去表 3 里记下来")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(n_atoms=N,
             ms_per_step_mlip=res_m["ms_per_step"],
             ms_per_step_classic=res_c["ms_per_step"],
             speed_ratio=ratio,
             scale_exponent=slope,
             drift_mlip=res_m["drift"],
             drift_classic=res_c["drift"],
             rdf_peak_mlip=peak_m,
             rdf_peak_classic=peak_c,
             force_rms_gap=f_gap)
