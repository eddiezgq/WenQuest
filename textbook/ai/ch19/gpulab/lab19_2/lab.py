# GPU 实验 19.2 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 19.2　跑一次全球预报，亲手量它越推越平
# 19.2 节用一个谱玩具说明了一件事：**均方误差最优的一步预测，就是把每个波数乘上它自己的
# 相关系数 ρ_k < 1**；自回归推 n 步之后振幅是 ρ_k^n，高波数掉得最快。所以"越推越平"是最优解
# 本身，不是实现上的毛病。
#
# 这个实验把同一件事放到真模型上量一遍：用公开权重的 AIFS（权重 CC BY 4.0、代码 Apache 2.0）
# 从真实初值推十天，逐个时效量锐度与功率谱，再与同一时刻的分析场比 RMSE。
#
# **口径先说清楚**（这一条比结果重要）：
#
# * 本实验**不与任何业务模式比分数**。官方自己指出 AIFS 第 1 天**对分析场**比业务模式差、
#   **对探空观测**却不差——两边用的真值不是同一个；官方也只说改进"of the order of 10%"，
#   **没有公开成对的绝对 RMSE 数值**。
# * 官方明说 GPU 的非确定性使用户**无法精确复现**官方 AIFS 预报。你的数与别人的会有末位差别。
# * 能比的只有两件事：**同一个真值下、不同时效之间**的变化，以及锐度与 RMSE 这两者的方向。
# %%
import sys; sys.path.insert(0, "..")
import time

import numpy as np
import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
# anemoi-inference 是官方推理栈；它自带一个从开放数据取初值的输入插件，所以初值不用自己拼。
wqgpu.sh(f"{sys.executable} -m pip install -q 'anemoi-inference[huggingface]' "
         f"ecmwf-opendata earthkit-data cfgrib xarray netcdf4", timeout=3600)
print(torch.cuda.get_device_name(0), torch.__version__)

# %% [markdown]
# ## 1. 模型权重（任务 1）
# AIFS Single：欧洲中期天气预报中心的机器学习预报模式，2025 年 2 月 25 日起业务运行，每天 4 次。
# 分辨率官方公告说约 28 km、模型卡说 31 km（**两个数都在，本书两个都印**），13 层，6 小时一步。
# 权重几个 GB，第一次下载要等几分钟。
# %%
from huggingface_hub import hf_hub_download

CKPT = hf_hub_download(repo_id="ecmwf/aifs-single-1.0", filename="aifs-single-mse-1.0.ckpt")
print("权重：", CKPT)

# %% [markdown]
# ## 2. 配置一次预报（任务 2）
# anemoi-inference 用一个配置文件说清楚四件事：用哪个权重、从哪个时刻起报、推多久、初值哪里来。
# `input: ecmwf-open-data` 就是官方那个取开放数据的插件——它自己去取 AIFS 要的全部变量，
# 包括地形、陆海掩码那几个常量场。
#
# **开放数据只保留最近一段时间**，所以这里往回取两天。想换时刻，改 `DATE` 一处就行。
# %%
import datetime
import pathlib

DATE = (datetime.datetime.now(datetime.timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=2))
LEAD_H = 240
OUT = pathlib.Path("aifs_fc.nc")
print("起报时刻（UTC）：", DATE.strftime("%Y-%m-%d %H:%M"))

CONFIG = f"""
checkpoint: {CKPT}
date: {DATE.strftime('%Y-%m-%dT%H:%M:%S')}
lead_time: {LEAD_H}
device: cuda
input:
  ecmwf-open-data:
    namer: default
output:
  netcdf:
    path: {OUT}
"""
pathlib.Path("aifs.yaml").write_text(CONFIG)
print(CONFIG)
# 配置项的名字随 anemoi-inference 的版本有过改动。若这一格报"unknown key"，
# 用 `anemoi-inference config --help` 看当下版本的写法，只改这一格，后面各节不用动。

# %% [markdown]
# ## 3. 推十天（任务 3）
# 6 小时一步，十天就是 40 步。官方给的时间口径是**十天预报约 2 分 30 秒、单块 A100（含输入输出）**，
# 按这一条估自己的用时。第一次运行还要把初值下载下来，所以墙钟时间会更长。
# %%
t0 = time.perf_counter()
wqgpu.sh("anemoi-inference run aifs.yaml", timeout=7200)
wall = time.perf_counter() - t0
n_step = LEAD_H // 6
print(f"\n全程 {wall / 60:.1f} 分钟，{n_step} 步，平均每步 {wall / n_step:.2f} s"
      f"（含下载初值，比纯推理慢）")

# %% [markdown]
# ## 4. 锐度与功率谱（任务 4）
# **锐度**取相邻格点差的均方根：场越平这个数越小。
# **功率谱**把每条纬带做一次傅里叶变换，看高波数那一头还剩多少能量——19.2 节那条 ρ_k^n 就该在这里露面。
#
# 输出已经是规则经纬网格，**各时效共用同一套格点**，所以跨时效可比。锐度随分辨率变，
# 换了插值或换了分辨率就不能跨行比。
# %%
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import xarray as xr

ds = xr.open_dataset(OUT)
VAR = "2t" if "2t" in ds else [v for v in ds.data_vars if ds[v].ndim >= 3][0]
da = ds[VAR]
print(f"用来量锐度的变量：{VAR}，维度 {dict(da.sizes)}")
TDIM = [d for d in da.dims if d in ("time", "valid_time", "step")][0]
LATN = [d for d in da.dims if "lat" in d][0]
lat_vals = np.asarray(ds[LATN], dtype=float)


def field(day):
    """第 day 天的场，取成二维（纬度 × 经度）。"""
    g = np.asarray(da.isel({TDIM: day * 4}).squeeze(), dtype=float)
    return g if g.ndim == 2 else g[0]


def sharpness(g):
    """相邻格点差的均方根（东西、南北各算一遍再合）。"""
    dx = np.diff(g, axis=1); dy = np.diff(g, axis=0)
    return float(np.sqrt((np.mean(dx ** 2) + np.mean(dy ** 2)) / 2))


def spectrum(g):
    """纬向功率谱，按 cos(纬度) 给纬带加权——高纬的格点在球面上代表的面积小。"""
    w = np.cos(np.deg2rad(lat_vals))
    f = np.abs(np.fft.rfft(g - g.mean(axis=1, keepdims=True), axis=1)) ** 2
    return (f * w[:, None]).sum(0) / w.sum()


DAYS = [0, 1, 2, 5, 10]
DAYS = [d for d in DAYS if d * 4 < da.sizes[TDIM]]
g0 = field(0)
sp0 = spectrum(g0)
HI = slice(len(sp0) // 3, None)                     # 高波数那一头
s0 = sharpness(g0)
rows = []
for d in DAYS:
    g = field(d)
    sp = spectrum(g)
    rows.append((d, sharpness(g), sharpness(g) / s0, float(sp[HI].sum() / sp.sum())))
    print(f"第 {d:2d} 天　锐度 {rows[-1][1]:.4f}　占初值 {rows[-1][2]:.3f}　"
          f"高波数能量占比 {rows[-1][3]:.5f}")

hi_drop = (1 - rows[-1][3] / rows[0][3]) * 100
print(f"\n**高波数能量掉了 {hi_drop:.1f}%** —— 这就是 ρ_k^n 在真模型上的样子")

fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4))
for d in DAYS:
    a.loglog(np.arange(1, len(sp0)), spectrum(field(d))[1:], label=f"第 {d} 天")
a.set_xlabel("纬向波数"); a.set_ylabel("能量"); a.legend(); a.set_title("谱：高波数先掉")
b.plot([r[0] for r in rows], [r[2] for r in rows], "o-")
b.set_xlabel("时效（天）"); b.set_ylabel("锐度 / 初值锐度"); b.set_ylim(0, 1.05)
b.set_title("锐度随时效怎么掉")
fig.tight_layout(); fig.savefig("sharpness.png", dpi=120)
print("图已存成 sharpness.png")

# %% [markdown]
# ## 5. 与分析场比 RMSE，顺便数极端（任务 5）
# 真值用**同一时刻的分析场**：开放数据里 `type="an"` 的那一份，用同一个变量、插到同一套格点上。
# 这里只比"同一个真值下、不同时效之间"的变化：RMSE 一路涨是意料之中的，要看的是
# **锐度掉得比 RMSE 涨得还明显**，以及极端格点抓住了几成。
# %%
from ecmwf.opendata import Client

client = Client(source="ecmwf")
PARAM = {"2t": "2t"}.get(VAR, VAR)
lon_vals = np.asarray(ds[[d for d in da.dims if "lon" in d][0]], dtype=float)


def analysis(day):
    """取 DATE + day 天那一时刻的分析场，最近邻插到预报的格点上。"""
    when = DATE + datetime.timedelta(days=day)
    path = f"an_{day}.grib"
    try:
        client.retrieve(date=when.strftime("%Y-%m-%d"), time=when.hour, type="an",
                        param=PARAM, target=path)
    except Exception as e:                       # 保留期有限、或这个变量没有分析场
        print(f"  第 {day} 天取不到分析场：{e}")
        return None
    a = xr.open_dataset(path, engine="cfgrib")
    v = list(a.data_vars)[0]
    return a[v].interp(latitude=lat_vals, longitude=lon_vals,
                       method="nearest").to_numpy().astype(float)


Q = 0.95
rmse_rows = []
for d in [x for x in (1, 2, 5, 10) if x in DAYS]:
    truth = analysis(d)
    if truth is None:
        continue
    f = field(d)
    rmse = float(np.sqrt(np.mean((f - truth) ** 2)))
    th = float(np.quantile(truth, Q))            # 两边用同一个门限，免得被预报自己的分布糊弄过去
    n_ev = int((truth > th).sum())
    hit = float(((f > th) & (truth > th)).sum() / max(1, n_ev) * 100)
    rmse_rows.append((d, rmse, sharpness(f), hit))
    print(f"第 {d:2d} 天　RMSE {rmse:6.3f}　锐度 {sharpness(f):.4f}　极端格点抓住 {hit:5.1f}%")

if rmse_rows:
    print("\n把几栏并排看：RMSE 在涨，锐度在掉，极端抓住的比例也在掉——"
          "**RMSE 这一把尺子看不出后面两件事**")
else:
    print("\n分析场一个也没取到：第 4 节的结论照样成立（它只用预报自己），表 2 这一次留空。")

# %% [markdown]
# ## 回传结果
# %%
def pick(day, col):
    for r in rows:
        if r[0] == day:
            return r[col]
    return float("nan")


def pick_rmse(day):
    for r in rmse_rows:
        if r[0] == day:
            return r[1]
    return float("nan")


wqgpu.submit(lead_days=max(DAYS),
             sec_per_step=wall / n_step,
             sharp_day0=pick(0, 1), sharp_day2=pick(2, 1), sharp_day10=pick(10, 1),
             sharp_ratio=pick(10, 2), hi_energy_drop_pct=hi_drop,
             rmse_day2=pick_rmse(2), rmse_day5=pick_rmse(5),
             extreme_share_pct=(rmse_rows[-1][3] if rmse_rows else float("nan")))
