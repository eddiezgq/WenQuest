# GPU 实验 22.1 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 22.1　光伏功率预测，以及用两种口径验收它
# 训练只是这个实验的一半。另一半——**也是更要紧的一半**——是回答三个问题：
#
# 1. 它比最笨的基线强多少（打不赢持续法与气候法的模型不要上线）；
# 2. **换一种天气型还准不准**（在晴天上训、到阴天上测）；
# 3. 把误差**折成钱**是多少（同样的均方根误差，两个方向的代价差几倍）。
#
# **先把口径说清楚**：
#
# * 公开气象数据是**再分析值，不是预报值**。用它当输入等于假设“气象预报完全准确”，
#   所以这里的误差是**下界**，真实业务里要更大；
# * 辐照折成功率那一步是**本书的折算**（容量、温度系数、逆变器效率都是显式假设）；
# * 所有误差只在**白天的点**上算——把夜里的零值算进去会把均方根误差压低一大截。
# %%
import sys; sys.path.insert(0, "..")
import time

import numpy as np
import wqgpu
env = wqgpu.check(("gpu", "torch"))

import torch
print(torch.cuda.get_device_name(0), torch.__version__)
wqgpu.sh(f"{sys.executable} -m pip install -q requests", timeout=1800)

# %% [markdown]
# ## 1. 数据：公开气象再分析，折成光伏出力（任务 2）
# 取一段公开的逐小时再分析数据（短波辐照、云量、气温）：Open-Meteo 的 /v1/archive 接口，
# 非商业使用不需要密钥，数据来自 ERA5 再分析（官方文档说辐照是**前一小时的平均值**，
# 云量是瞬时值，数据有约 5 天延迟）。取不到就退回合成数据，实验照样能做，结果里会注明来源。
#
# **显式假设**：装机容量 400 kW、温度系数 −0.4%/℃（以 25 ℃ 为基准）、逆变器效率 0.96。
# %%
import requests

LAT, LON = 31.23, 121.47          # 上海附近；换成你们厂的经纬度也可以
START, END = "2023-03-01", "2023-08-31"
CAP_KW, TEMP_COEF, INV_EFF = 400.0, -0.004, 0.96
URL = ("https://archive-api.open-meteo.com/v1/archive"
       f"?latitude={LAT}&longitude={LON}&start_date={START}&end_date={END}"
       "&hourly=shortwave_radiation,cloud_cover,temperature_2m&timezone=Asia%2FShanghai")

source = "open-meteo /v1/archive（ERA5 再分析）"
try:
    r = requests.get(URL, timeout=90)
    r.raise_for_status()
    h = r.json()["hourly"]
    ghi = np.asarray(h["shortwave_radiation"], dtype=np.float64)
    cloud = np.asarray(h["cloud_cover"], dtype=np.float64) / 100.0
    temp = np.asarray(h["temperature_2m"], dtype=np.float64)
    hours = np.arange(len(ghi)) % 24
    ok = np.isfinite(ghi) & np.isfinite(cloud) & np.isfinite(temp)
    ghi, cloud, temp, hours = ghi[ok], cloud[ok], temp[ok], hours[ok]
except Exception as e:                       # noqa: BLE001  取不到就合成
    source = f"合成（{type(e).__name__}）"
    print(f"  取公开数据失败（{type(e).__name__}），用合成数据代替")
    n = 24 * 184
    g = np.random.default_rng(0)
    hours = np.arange(n) % 24
    clear = 900.0 * np.clip(np.cos((hours - 12.0) / 12.0 * np.pi), 0, None)
    slow = np.convolve(g.normal(0, 1, n + 48), np.ones(48) / 48, "same")[:n]
    cloud = np.clip(0.5 + 0.9 * slow, 0, 1)
    ghi = clear * (1.0 - 0.75 * cloud)
    temp = 24.0 + 7.0 * np.cos((hours - 15.0) / 12.0 * np.pi) + 3.0 * slow

cell_t = temp + ghi / 800.0 * 25.0           # 组件温度的粗略折算（本书的假设）
pv = CAP_KW * (ghi / 1000.0) * (1.0 + TEMP_COEF * (cell_t - 25.0)) * INV_EFF
pv = np.maximum(pv, 0.0)
day = pv > 1.0
n_hours = int(len(pv))
print(f"数据来源：{source}，共 {n_hours} 小时，其中白天 {int(day.sum())} 小时")
print(f"出力最大 {pv.max():.0f} kW，白天平均 {pv[day].mean():.0f} kW")

# %% [markdown]
# ## 2. 两个笨基线（任务 3）
# 持续法：明天的这个钟点和今天一样。气候法：历史上这个钟点的平均。
# **打不赢它们的模型不要上线。**
# %%
def rmse(a, b, m):
    return float(np.sqrt(np.mean((np.asarray(a)[m] - np.asarray(b)[m]) ** 2)))


persist = np.concatenate([np.zeros(24), pv[:-24]])
clim = np.zeros_like(pv)
for hh in range(24):
    m = hours == hh
    clim[m] = pv[m].mean()
rmse_persist = rmse(persist, pv, day)
rmse_clim = rmse(clim, pv, day)
print(f"持续法：{rmse_persist:.2f} kW　气候法：{rmse_clim:.2f} kW（都只在白天的点上算）")

# %% [markdown]
# ## 3. 两种划分口径，各训一遍（任务 4）
# 特征：辐照、云量、气温、钟点的正余弦、前一小时与前三小时的出力（**都只用过去的值**）。
#
# * **按时间划分**：前 75% 训、后 25% 测，中间**留一天的间隔**；
# * **按天气型划分**：在**晴天**（日均云量低的那些天）上训，到**阴天**上测。
# %%
def lag(x, k):
    return np.concatenate([np.zeros(k), x[:-k]])


X = np.column_stack([ghi / 1000.0, cloud, temp / 40.0,
                     np.sin(hours / 24.0 * 2 * np.pi), np.cos(hours / 24.0 * 2 * np.pi),
                     lag(pv, 1) / CAP_KW, lag(pv, 3) / CAP_KW]).astype(np.float32)
y = (pv / CAP_KW).astype(np.float32)
n = len(y)

n_days = n // 24
day_cloud = np.array([cloud[d * 24:(d + 1) * 24].mean() for d in range(n_days)])
clear_days = np.argsort(day_cloud)[:int(n_days * 0.7)]          # 云最少的七成天
cloudy_days = np.argsort(day_cloud)[int(n_days * 0.7):]
mask_clear = np.zeros(n, dtype=bool)
for d in clear_days:
    mask_clear[d * 24:(d + 1) * 24] = True
mask_cloudy = np.zeros(n, dtype=bool)
for d in cloudy_days:
    mask_cloudy[d * 24:(d + 1) * 24] = True

cut = int(n * 0.75)
splits = {
    "time": (np.arange(0, cut - 24), np.arange(cut, n)),        # 留 24 小时的间隔
    "regime": (np.where(mask_clear)[0], np.where(mask_cloudy)[0]),
}

dev = "cuda"


def train(tr, te, seed=0, epochs=400, quantile=None):
    torch.manual_seed(seed)
    Xtr = torch.tensor(X[tr], device=dev)
    ytr = torch.tensor(y[tr], device=dev)
    Xte = torch.tensor(X[te], device=dev)
    net = torch.nn.Sequential(torch.nn.Linear(X.shape[1], 64), torch.nn.ReLU(),
                              torch.nn.Linear(64, 64), torch.nn.ReLU(),
                              torch.nn.Linear(64, 1)).to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=3e-3)
    t0 = time.perf_counter()
    for _ in range(epochs):
        opt.zero_grad()
        p = net(Xtr).squeeze(1)
        if quantile is None:
            loss = ((p - ytr) ** 2).mean()
        else:                                   # 弹球损失：直接拟合分位数
            d = ytr - p
            loss = torch.maximum(quantile * d, (quantile - 1) * d).mean()
        loss.backward()
        opt.step()
    wall = time.perf_counter() - t0
    with torch.no_grad():
        pred = net(Xte).squeeze(1).clamp(min=0).cpu().numpy() * CAP_KW
    return pred, wall


res = {}
for how in ("time", "regime"):
    tr, te = splits[how]
    pred, wall = train(tr, te)
    m = day[te]
    res[how] = (rmse(pred, pv[te], m), wall)
    name = "按时间划分" if how == "time" else "按天气型划分（晴天训、阴天测）"
    print(f"{name:>28}：均方根误差 {res[how][0]:6.2f} kW　训练 {wall:5.1f} 秒")

rmse_time, train_s = res["time"]
rmse_regime = res["regime"][0]
regime_ratio = rmse_regime / max(rmse_time, 1e-9)
print(f"\n**按天气型划分比按时间划分差 {regime_ratio:.2f} 倍**——"
      f"前者回答“换一种天气还准不准”，后者回答“拿过去预测未来准不准”")
print(f"两个基线：持续法 {rmse_persist:.2f} kW、气候法 {rmse_clim:.2f} kW；"
      f"模型按时间划分 {rmse_time:.2f} kW")
if rmse_time >= min(rmse_persist, rmse_clim):
    print("**注意：模型没打赢笨基线**——先查特征与训练轮数，不要急着换更大的模型")

# %% [markdown]
# ## 4. 分位数与覆盖率（任务 5）
# 调度要的不是“最可能是多少”，是“有多大把握不低于多少”。用弹球损失直接拟三个分位数，
# 然后看 10%—90% 这个**名义 80%** 的区间，实际盖住了多少。
# %%
tr, te = splits["time"]
qpred = {}
for q in (0.1, 0.5, 0.9):
    qpred[q], _ = train(tr, te, quantile=q, epochs=400)
m = day[te]
truth = pv[te]
lo, hi = qpred[0.1], qpred[0.9]
cover_nominal = 80.0
cover_actual = float(np.mean((truth[m] >= lo[m]) & (truth[m] <= hi[m]))) * 100
width = float(np.mean(hi[m] - lo[m]))
print(f"名义 {cover_nominal:.0f}% 的区间，实际盖住 {cover_actual:.1f}%，平均宽 {width:.1f} kW")
print("**报区间必须报实际覆盖率**：名义值是你要的，实际值才是你有的")

# %% [markdown]
# ## 5. 把误差折成钱（任务 6）
# 显式假设：分时电价（峰 1.05、平 0.62、谷 0.28 元/kWh），**少发按 1.6 倍电价买回来、
# 多发按 0.5 倍贱卖**。同样大小的误差，两个方向的代价差几倍？最省的申报偏置在哪？
# %%
UP, DOWN = 1.6, 0.5
hh = hours[te]
price = np.full(len(te), 0.62)
price[(hh >= 8) & (hh < 11)] = 1.05
price[(hh >= 18) & (hh < 21)] = 1.05
price[(hh < 7) | (hh >= 23)] = 0.28
point = qpred[0.5]


def cost(declared):
    d = truth - declared
    return float(np.sum(np.maximum(-d, 0) * price * UP + np.maximum(d, 0) * price * DOWN))


SHIFT = 20.0
cost_over = cost(np.maximum(point + SHIFT, 0))
cost_under = cost(np.maximum(point - SHIFT, 0))
cost_ratio = cost_over / max(cost_under, 1e-9)
print(f"往高报 {SHIFT:.0f} kW：{cost_over:,.0f} 元　往低报 {SHIFT:.0f} kW：{cost_under:,.0f} 元"
      f"　**差 {cost_ratio:.2f} 倍**")

biases = np.arange(-120, 41, 5.0)
costs = np.array([cost(np.maximum(point + b, 0)) for b in biases])
rmses = np.array([rmse(np.maximum(point + b, 0), truth, m) for b in biases])
best_bias = float(biases[int(np.argmin(costs))])
rmse_bias = float(biases[int(np.argmin(rmses))])
save = (1 - costs.min() / costs[int(np.argmin(rmses))]) * 100
print(f"成本最低的申报偏置 {best_bias:+.0f} kW，均方根误差最低的偏置 {rmse_bias:+.0f} kW，"
      f"照成本调省 {save:.1f}%")
print("**“该报多少”的答案在电价规则里，不在模型里**")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(n_hours=n_hours, source=source, rmse_persist=rmse_persist,
             rmse_time=rmse_time, rmse_regime=rmse_regime, regime_ratio=regime_ratio,
             cover_nominal=cover_nominal, cover_actual=cover_actual,
             cost_ratio=cost_ratio, best_bias=best_bias, train_s=train_s)
