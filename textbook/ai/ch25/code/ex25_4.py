"""算例 25.4.1—25.4.4：排队论估算对离散事件仿真——**估算什么时候开始不准**（25.7 节）。

车间的搬运系统：任务陆续来，k 台搬运车按先到先服务做。两种算法：

* **估算**：用 M/M/k 的 Erlang C 公式算平均停留时间 W，再用**利特尔法则** L = λW
  折成在制品数。一张纸就能算完；
* **仿真**：自己写一个事件队列（不引任何仿真库）跑几十万个任务，直接量 W 与 L。

利特尔法则本身是**恒等式**，仿真里也验得到（它不会错）。会错的是**喂给它的 W**：
1961 年那篇论文的摘要把适用条件写死了三条（原话见 `logi_facts.LITTLES_LAW`，
程序开头照原话打出来），三条里有一条不成立，前面那个 W 就不再是这个系统的 W。
本算例把两种失效方式分别算出来：服务时间方差比假设大（模型不对），
以及到达率按班次来回变（不平稳）。
"""
import numpy as np
from logi_facts import LITTLES_LAW

from _ch25 import erlang_c_wait, littles_law, simulate_queue, simulate_queue_shift
from bookout import out

K = 3                    # 三台搬运车
MU = 2.0                 # 每台每小时做 2 个任务（平均 30 分钟一个）
N_JOBS = 200000
SEEDS = (0, 1, 2)
LOADS = (0.4, 0.6, 0.8, 0.9, 0.95)
CV2 = (1.0, 3.0)         # 平方变异系数：1 = 指数分布（与假设一致）；3 = 方差比假设大得多
v = {"k": K, "mu": MU, "n_jobs": N_JOBS, "n_seeds": len(SEEDS),
     "loads": str(list(LOADS)), "cv2": str(list(CV2))}
print(f"{K} 台搬运车，每台平均 {60 / MU:.0f} 分钟做完一个任务；"
      f"每个点跑 {N_JOBS} 个任务、{len(SEEDS)} 个随机种子取平均")
print("（车数、服务时间、到达率都是**显式假设**，不取自任何厂家样本）")
print(f"利特尔法则 {LITTLES_LAW['formula']}，适用条件照论文摘要原话三条：")
for i, cond in enumerate(LITTLES_LAW["conditions"], 1):
    print(f"  ({i}) {cond}")
v["littles_formula"] = LITTLES_LAW["formula"]
v["littles_n_conditions"] = len(LITTLES_LAW["conditions"])
# 第 175 轮补：正文两张表的行标签（利用率）与行文里提到的那两档
for _i, _r in enumerate(LOADS, 1):
    v[f"rho_{_i}"] = _r
v["rho_high"], v["rho_second_high"] = LOADS[-1], LOADS[-2]


def sweep(cv2: float) -> list:
    rows = []
    for rho in LOADS:
        lam = rho * K * MU
        w_est = erlang_c_wait(lam, MU, K) + 1.0 / MU
        l_est = littles_law(lam, w_est)
        ws, ls, ids = [], [], []
        for sd in SEEDS:
            s = simulate_queue(lam, MU, K, n_jobs=N_JOBS, cv2=cv2, seed=sd)
            ws.append(s["w"])
            ls.append(s["l"])
            ids.append(s["l"] / (lam * s["w"]))
        rows.append({"rho": rho, "lam": lam, "w_est": w_est, "l_est": l_est,
                     "w_sim": float(np.mean(ws)), "l_sim": float(np.mean(ls)),
                     "identity": float(np.mean(ids))})
        rows[-1]["err_w"] = (rows[-1]["w_est"] / rows[-1]["w_sim"] - 1) * 100
        rows[-1]["err_l"] = (rows[-1]["l_est"] / rows[-1]["l_sim"] - 1) * 100
    return rows


# ---------- 一、服务时间正好符合假设（cv² = 1）
base = sweep(1.0)
print("\n① 服务时间正好是指数分布（**模型假设成立**）：")
print("利用率   W 估算   W 仿真   误差      L 估算   L 仿真   误差    L/(λW) 恒等式")
for r in base:
    print(f" {r['rho']:.2f}    {r['w_est']:6.3f}  {r['w_sim']:6.3f}  "
          f"{r['err_w']:+6.1f}%   {r['l_est']:6.2f}  {r['l_sim']:6.2f}  "
          f"{r['err_l']:+6.1f}%     {r['identity']:.3f}")
    v[f"err_w_cv1_rho{int(r['rho'] * 100)}"] = r["err_w"]
    v[f"l_sim_cv1_rho{int(r['rho'] * 100)}"] = r["l_sim"]
    v[f"identity_rho{int(r['rho'] * 100)}"] = r["identity"]
v["err_w_cv1_low"] = base[0]["err_w"]
v["err_w_cv1_high"] = base[-2]["err_w"]
assert abs(v["err_w_cv1_low"]) < 15.0, "低负载、假设成立时，估算与仿真必须接近"
assert all(abs(r["identity"] - 1.0) < 0.02 for r in base), \
    "利特尔法则是恒等式：仿真里 L 必须等于 λW，差 2% 以内"
print(f"最后一列全是 1.00：**利特尔法则在仿真里是恒等式，它不会错**。"
      f"而且假设成立时，连 {LOADS[-1]:.2f} 的高负载估算也准"
      f"（{base[-1]['err_w']:+.1f}%）——所以“负载高了估算就不准”这句话本身是不对的")

# ---------- 二、服务时间方差比假设大（cv² = 3）
hv = sweep(3.0)
print("\n② 同样的平均服务时间，但**方差是假设的 3 倍**（有的任务特别费时）：")
print("利用率   W 估算   W 仿真   误差      L 估算   L 仿真   误差")
for r in hv:
    print(f" {r['rho']:.2f}    {r['w_est']:6.3f}  {r['w_sim']:6.3f}  "
          f"{r['err_w']:+6.1f}%   {r['l_est']:6.2f}  {r['l_sim']:6.2f}  "
          f"{r['err_l']:+6.1f}%")
    v[f"err_w_cv3_rho{int(r['rho'] * 100)}"] = r["err_w"]
    v[f"l_sim_cv3_rho{int(r['rho'] * 100)}"] = r["l_sim"]
v["err_w_cv3_low"], v["err_w_cv3_high"] = hv[0]["err_w"], hv[-2]["err_w"]
v["wip_underestimate"] = hv[-2]["l_sim"] - hv[-2]["l_est"]
assert abs(v["err_w_cv3_low"]) < 15.0, "低负载下即使方差不对，估算也还凑合"
assert v["err_w_cv3_high"] < -15.0, \
    "高负载 + 方差大：估算必须明显偏低，这是本算例要讲的那条"
assert v["err_w_cv3_high"] < v["err_w_cv3_low"], "误差要随负载变大"
print(f"低负载时还凑合（{v['err_w_cv3_low']:+.1f}%），到 {LOADS[-2]:.2f} 的负载就差"
      f"{v['err_w_cv3_high']:+.1f}%——**估算偏低**，在制品数少算了 "
      f"{v['wip_underestimate']:.1f} 个任务")
print("**所以“什么时候开始不准”的答案是：负载 × 假设偏差。**负载本身不致命，"
      "负载把假设的偏差放大了才致命——这与第 19 章“分布一变，标定就失效”是同一回事")

# ---------- 三、到达不平稳：把第二个条件违反掉
RHO_MEAN = 0.8
lam_mean = RHO_MEAN * K * MU
lam_hi, lam_lo = 1.2 * K * MU, 0.4 * K * MU          # 忙班与闲班各占一半
w_flat = erlang_c_wait(lam_mean, MU, K) + 1.0 / MU
shift = simulate_queue_shift(lam_hi, lam_lo, period=40.0, mu=MU, k=K,
                             n_jobs=N_JOBS, cv2=1.0, seed=0)
v["rho_mean"] = RHO_MEAN
v["lam_hi_rho"], v["lam_lo_rho"] = lam_hi / (K * MU), lam_lo / (K * MU)
v["w_est_flat"] = w_flat
v["w_sim_shift"] = shift["w"]
v["err_w_shift"] = (w_flat / shift["w"] - 1) * 100
v["l_sim_shift"] = shift["l"]
v["l_est_flat"] = littles_law(shift["lam_mean"], w_flat)
v["identity_shift"] = shift["l"] / (shift["lam_mean"] * shift["w"])
print(f"\n③ 平均利用率还是 {RHO_MEAN:.2f}，但任务**按班次来回变**"
      f"（忙班相当于 {v['lam_hi_rho']:.1f} 的利用率、闲班 {v['lam_lo_rho']:.1f}）：")
print(f"   按平均到达率估算 W = {w_flat:.3f} 小时，仿真实测 W = {shift['w']:.3f} 小时"
      f"（估算 {v['err_w_shift']:+.1f}%）")
print(f"   在制品数：估算 {v['l_est_flat']:.2f}，仿真 {v['l_sim_shift']:.2f}；"
      f"而 L/(λW) = {v['identity_shift']:.3f}——**恒等式照样成立，错的是 W**")
assert v["err_w_shift"] < -25.0, \
    "不平稳时，拿平均到达率估出来的 W 必然大幅偏低（忙班排起的队，闲班才还得清）"
assert abs(v["identity_shift"] - 1.0) < 0.05, "利特尔法则在这里仍然是恒等式"
print("   这正是论文摘要里第二个条件的分量：**“严格平稳”不是摆设**。"
      "车间里两班制、早晚高峰、月底冲量，都是这一条不成立的现实版本")

# ---------- 四、该怎么用
print("\n所以本章把这两件工具的分工写死：")
print("  · **利特尔法则**用来做量纲检查与反推（它是恒等式，永远可用）：知道 L 与 λ 就知道 W；")
print("  · **排队公式**只用来估个数量级，并且必须报清假设（指数服务、平稳到达、先到先服务）；")
print(f"  · 要给出能上报表的数，就跑仿真，并且**把方差与班次一起放进去**——"
      f"本算例里这两件事各让估算偏低 {abs(v['err_w_cv3_high']):.0f}% 与 "
      f"{abs(v['err_w_shift']):.0f}%。")

out(**v)
