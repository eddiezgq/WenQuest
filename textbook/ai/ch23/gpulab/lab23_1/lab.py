# GPU 实验 23.1 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 23.1　在仿真里训车道保持，再换光照与路面验收它
# 训练只是这个实验的一半。另一半——**也是更要紧的一半**——是回答三个问题：
#
# 1. 它比最笨的基线强多少（打不赢“方向盘不动”和一个线性模型的，不要往下走）；
# 2. **换了光照与路面还准不准**（训练时的车道线检测又稳又准，验收时噪声大一倍半、还系统性偏一侧）；
# 3. **罕见情形（急弯）上准不准**——平均误差最会骗人的地方就在这里。
#
# **先把口径说清楚**：
#
# * 本实验的数据**全是合成的**（不联网、不下载）：车道几何、车道线的像素观测、专家方向盘角
#   都由一套**显式假设**生成，与教材第 23 章的算例同一套；
# * “换光照与路面”在这里只折成**两件事**：车道线检测的像素噪声变大、并且系统性偏一侧。
#   真实的光照与路面变化远不止这两样（见本实验的“注意”）；
# * **两种口径的误差不能平均**，也不能只报好看的那一个：它们回答两个不同的问题。
# %%
import sys; sys.path.insert(0, "..")
import time

import numpy as np
import wqgpu
env = wqgpu.check(("gpu", "torch"))

import torch
dev = "cuda"
print(torch.cuda.get_device_name(0), torch.__version__)

# %% [markdown]
# ## 1. 合成一段车道保持数据（任务 2）
# 场景的三个状态量：横向偏差 e（m）、航向偏差 psi（rad）、曲率 kappa（1/m）。
# 车道中心线在前视距离 X 处的横向位置 Y = e + psi·X + kappa·X²/2，
# 再按小孔模型投到**像素横坐标**上——噪声加在像素上，所以远处那一列折回地面时误差被放大。
#
# **显式假设**：焦距 1200 像素、主点 960、安装高度 1.42 m、俯视角 0.04 rad；
# 前视三个距离 8 / 16 / 28 m；专家方向盘角 = (0.16·e + 0.95·psi + atan(12·kappa)) 折成度数再乘转向比。
# %%
F, CX, PITCH, HEIGHT = 1200.0, 960.0, 0.04, 1.42
XS = np.array([8.0, 16.0, 28.0])
KE, KPSI, KKAPPA, LOOK, RATIO = 0.16, 0.95, 1.0, 12.0, 15.0


def lane_scene(n, seed, kappa_max=0.004, e_sigma=0.35):
    g = np.random.default_rng(seed)
    kappa = g.uniform(-kappa_max, kappa_max, n)
    e = g.normal(0.0, e_sigma, n)
    psi = g.normal(0.0, 0.025, n) - 0.4 * kappa * LOOK
    return {"e": e, "psi": psi, "kappa": kappa}


def observe(sc, seed, pix_sigma=1.6, pix_bias=0.0):
    """车道线在三个前视距离上的像素横坐标。pix_sigma 是检测噪声，pix_bias 是系统性偏置。"""
    g = np.random.default_rng(seed + 907)
    cols = []
    sp, cp = np.sin(PITCH), np.cos(PITCH)
    for X in XS:
        Y = sc["e"] + sc["psi"] * X + 0.5 * sc["kappa"] * X ** 2
        z_c = X * cp + HEIGHT * sp
        u = CX + F * (-Y) / z_c
        cols.append(u + pix_bias + pix_sigma * g.normal(0.0, 1.0, len(Y)))
    return np.column_stack(cols)


def expert(sc):
    """“专家”方向盘角（deg）。这是本实验的真值——不是另一个模型的输出。"""
    d = KE * sc["e"] + KPSI * sc["psi"] + KKAPPA * np.arctan(LOOK * sc["kappa"])
    return np.degrees(d) * RATIO / 10.0


def make(n, seed, kappa_max=0.004, e_sigma=0.35, pix_sigma=1.6, pix_bias=0.0):
    sc = lane_scene(n, seed, kappa_max, e_sigma)
    U = observe(sc, seed, pix_sigma, pix_bias)
    X = ((U - CX) / 100.0).astype(np.float32)
    return X, expert(sc).astype(np.float32)


N_TRAIN, N_TEST = 20000, 5000
PIX_TRAIN = 1.6                    # 训练与同分布测试：标定好的检测
PIX_SHIFT, BIAS_SHIFT = 4.0, 3.0   # 换光照与路面：噪声 2.5 倍、系统性偏 3 像素（显式假设）
KAPPA_CURVE = 0.012                # 罕见情形：急弯，曲率上限是训练时的 3 倍

X_tr, y_tr = make(N_TRAIN, 11, pix_sigma=PIX_TRAIN)
X_id, y_id = make(N_TEST, 22, pix_sigma=PIX_TRAIN)
X_sh, y_sh = make(N_TEST, 33, pix_sigma=PIX_SHIFT, pix_bias=BIAS_SHIFT)
X_cv, y_cv = make(N_TEST, 44, kappa_max=KAPPA_CURVE, e_sigma=0.35, pix_sigma=PIX_TRAIN)
n_train = int(len(y_tr))
print(f"训练 {n_train} 条，三个测试集各 {N_TEST} 条")
print(f"方向盘角的量级：训练集标准差 {y_tr.std():.3f}°，急弯集标准差 {y_cv.std():.3f}°")

# %% [markdown]
# ## 2. 两个笨基线（任务 3）
# 一是**方向盘不动**（一律输出 0），二是**线性最小二乘**（同样三列像素，只拟一次项）。
# **打不赢它们的模型不要往下走**——这一条在第 22 章立过，这里再用一次。
# %%
def rmse(pred, truth):
    return float(np.sqrt(np.mean((np.asarray(pred, dtype=np.float64)
                                  - np.asarray(truth, dtype=np.float64)) ** 2)))


rmse_zero = rmse(np.zeros_like(y_id), y_id)
A = np.column_stack([np.ones(len(X_tr)), X_tr])
coef = np.linalg.lstsq(A, y_tr, rcond=None)[0]
lin_id = np.column_stack([np.ones(len(X_id)), X_id]) @ coef
rmse_base = rmse(lin_id, y_id)
print(f"方向盘不动：{rmse_zero:.4f}°　线性最小二乘：{rmse_base:.4f}°（都在同分布测试集上）")

# %% [markdown]
# ## 3. 训一个小网络（任务 4）
# 三列像素进去，一个方向盘角出来。网络很小（两层 64），因为本实验要量的不是模型大小，
# 是**两种验收口径差多少**。训练用时一并记下来。
# %%
def train(epochs=600, seed=0):
    torch.manual_seed(seed)
    xt = torch.tensor(X_tr, device=dev)
    yt = torch.tensor(y_tr, device=dev)
    net = torch.nn.Sequential(torch.nn.Linear(X_tr.shape[1], 64), torch.nn.ReLU(),
                              torch.nn.Linear(64, 64), torch.nn.ReLU(),
                              torch.nn.Linear(64, 1)).to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=3e-3)
    t0 = time.perf_counter()
    for _ in range(epochs):
        opt.zero_grad()
        loss = ((net(xt).squeeze(1) - yt) ** 2).mean()
        loss.backward()
        opt.step()
    torch.cuda.synchronize()
    return net, time.perf_counter() - t0


net, train_s = train()
train_s = float(train_s)


def predict(X):
    with torch.no_grad():
        return net(torch.tensor(X, device=dev)).squeeze(1).cpu().numpy()


rmse_id = rmse(predict(X_id), y_id)
print(f"同分布测试：{rmse_id:.4f}°　训练用时 {train_s:.1f} 秒")
print(f"与线性基线比：{rmse_base:.4f}° → {rmse_id:.4f}°（提高 "
      f"{(1 - rmse_id / rmse_base) * 100:.1f}%）")
print("本实验的映射**接近线性**，所以小网络大体只是与线性基线打平——"
      "这正是“先打赢笨基线”这一条的用处：它会告诉你这一处用不上神经网络。"
      "照实报这个数，不要把“打平”写成“达到基线水平”。")
if rmse_id >= min(rmse_zero, rmse_base):
    print("**模型没打赢笨基线**——先查训练轮数与特征，不要急着换更大的模型")

# %% [markdown]
# ## 4. 换光照与路面，再验收一遍（任务 5）
# 同一个模型，一个字都不改，只把测试集换成“光照与路面变了”的那一套：
# 车道线检测的噪声 2.5 倍、而且系统性偏 3 个像素。
#
# **这两行不能平均，也不能只报一个。** 第一行回答“仿真里训得准不准”，
# 第二行回答“条件变了还准不准”。
# %%
rmse_shift = rmse(predict(X_sh), y_sh)
shift_ratio = rmse_shift / max(rmse_id, 1e-9)
lin_sh = np.column_stack([np.ones(len(X_sh)), X_sh]) @ coef
print(f"同分布测试：      {rmse_id:.4f}°")
print(f"换光照与路面：    {rmse_shift:.4f}°　**差 {shift_ratio:.2f} 倍**")
print(f"同一条件下的线性基线：{rmse(lin_sh, y_sh):.4f}°（看看退化是不是模型独有的）")
print("\n两行分开报，不平均：第一行是“仿真里训得准不准”，第二行是“条件变了还准不准”。")

# %% [markdown]
# ## 5. 罕见情形：急弯（任务 6）
# 把曲率上限放到训练时的 3 倍（急弯），光照与路面不变。平均误差最会骗人的地方就在这里：
# 同分布那一行好看，是因为**急弯在训练分布里几乎不出现**。
# %%
rmse_curve = rmse(predict(X_cv), y_cv)
curve_ratio = rmse_curve / max(rmse_id, 1e-9)
print(f"急弯测试：{rmse_curve:.4f}°，是同分布的 {curve_ratio:.2f} 倍")
print("把三行并排看一遍：")
print(f"  同分布       {rmse_id:.4f}°")
print(f"  换光照与路面 {rmse_shift:.4f}°")
print(f"  急弯         {rmse_curve:.4f}°")
print("\n**仿真里跑通不等于路上能跑**：这三行里最差的那一行，才是上车之前要回答的问题。")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(n_train=n_train, rmse_zero=rmse_zero, rmse_base=rmse_base, rmse_id=rmse_id,
             rmse_shift=rmse_shift, shift_ratio=shift_ratio, rmse_curve=rmse_curve,
             curve_ratio=curve_ratio, train_s=train_s)
