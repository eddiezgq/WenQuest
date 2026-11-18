"""算例 22.6.1—22.6.4：机房冷却——约束下的连续控制与安全层（22.3 节）。

机房冷却是本章"系统不能停"的典型：**省电的办法人人都知道（让温度贴着上限走），
难的是贴着上限走而不越界**。本算例做四件事：

（1）把"省电"与"越界"两件事分开报——**只报电耗，排名是反的**；
（2）在仿真里搜一套贴着上限的参数，看它在仿真里有多省；
（3）把同一套参数放到**与仿真有偏差的真设备**上（制冷量比标称少一成），看越界冒出来；
（4）加一层**写死的安全层**（预测下一步要越界就把制冷量顶到最大），
    算出它花了多少电、挡掉了多少次越界。

全章的那条线在这里是：**安全不能靠学出来，要靠外面那层兜底**。
"""
import numpy as np

from _ch22 import HALL, cop, learned_policy, run_hall
from bookout import out

N_DAYS = 10
GAIN_REAL = 0.90             # 真设备的制冷量只有标称的九成（显式假设）
v = {"n_days": N_DAYS, "t_max": HALL["t_max"], "c_th": HALL["c_th"],
     "cool_max": HALL["cool_max"], "gain_real": GAIN_REAL}

print(f"机房：热容 {HALL['c_th']:.0f} kWh/℃，冷机最大制冷量 {HALL['cool_max']:.0f} kW，"
      f"冷通道温度上限 {HALL['t_max']:.0f} ℃")
v["cop_20c"] = float(cop(20.0))
v["cop_30c"] = float(cop(30.0))
print(f"冷机能效比：室外 20 ℃ 时 {v['cop_20c']:.2f}，30 ℃ 时 {v['cop_30c']:.2f}——"
      f"**省电的空间就在这里：热的时候少制冷、凉的时候多存点冷量**")

# ---------- 一、保守的规则控制（基线）
base = run_hall(learned_policy(23.0, 240.0, 0.0), N_DAYS, seed=0)
v["kwh_safe_rule"] = base["kwh"]
v["viol_safe_rule"] = base["viol"]
v["tmax_safe_rule"] = float(base["temps"].max())
print(f"\n保守规则（盯住 23 ℃）：{N_DAYS} 天耗电 {v['kwh_safe_rule']:,.0f} kWh，"
      f"越界 {v['viol_safe_rule']} 次，最高温度 {v['tmax_safe_rule']:.2f} ℃")

# ---------- 二、在仿真里搜一套贴着上限的参数
best = None
for sp in np.arange(23.0, 26.96, 0.05):
    for lead in (0.0, -30.0, -60.0, -90.0):
        r = run_hall(learned_policy(float(sp), 240.0, float(lead)), N_DAYS, seed=0)
        if r["viol"] == 0 and (best is None or r["kwh"] < best[0]["kwh"]):
            best = (r, float(sp), float(lead))
r_sim, SP, LEAD = best
v["setpoint"], v["lead"] = SP, LEAD
v["kwh_sim"], v["viol_sim"] = r_sim["kwh"], r_sim["viol"]
v["tmax_sim"] = float(r_sim["temps"].max())
v["save_sim_pct"] = (1 - v["kwh_sim"] / v["kwh_safe_rule"]) * 100
print(f"\n在仿真里搜出来的参数：设定 {SP:.1f} ℃、借室外温度提前动 {LEAD:.0f}")
print(f"仿真里：耗电 {v['kwh_sim']:,.0f} kWh（比保守规则省 {v['save_sim_pct']:.1f}%），"
      f"越界 {v['viol_sim']} 次，最高 {v['tmax_sim']:.2f} ℃")
assert v["viol_sim"] == 0 and v["kwh_sim"] < v["kwh_safe_rule"], "仿真里它该是又省又不越界"
v["margin_sim"] = HALL["t_max"] - v["tmax_sim"]
print(f"注意搜出来的参数**一直顶到墙边**：离上限只剩 {v['margin_sim']:.2f} ℃。"
      "这不是偶然——在仿真里越界为零，优化就会一直往上推，"
      "**把余量全部吃掉，恰好停在仿真误差最要命的地方**")

# ---------- 三、放到真设备上
r_real = run_hall(learned_policy(SP, 240.0, LEAD), N_DAYS, seed=0, gain=GAIN_REAL)
v["kwh_real"], v["viol_real"] = r_real["kwh"], r_real["viol"]
v["over_real"] = r_real["over_degh"]
v["tmax_real"] = float(r_real["temps"].max())
print(f"\n同一套参数，放到制冷量少一成的真设备上：耗电 {v['kwh_real']:,.0f} kWh，"
      f"**越界 {v['viol_real']} 次**（累计超温 {v['over_real']:.2f} ℃·h），"
      f"最高 {v['tmax_real']:.2f} ℃")
assert v["viol_real"] > 0, "仿真到现实的那一点偏差，正是要在这里露出来"
r_rule_real = run_hall(learned_policy(23.0, 240.0, 0.0), N_DAYS, seed=0, gain=GAIN_REAL)
v["kwh_rule_real"], v["viol_rule_real"] = r_rule_real["kwh"], r_rule_real["viol"]
print(f"保守规则在同一台真设备上：耗电 {v['kwh_rule_real']:,.0f} kWh，"
      f"越界 {v['viol_rule_real']} 次")
v["save_real_pct"] = (1 - v["kwh_real"] / v["kwh_rule_real"]) * 100
print(f"**只报电耗，学出来的策略省 {v['save_real_pct']:.1f}%，排第一；"
      f"把越界一起报，它根本不该上线**")

# ---------- 四、加一层安全层
r_safe = run_hall(learned_policy(SP, 240.0, LEAD), N_DAYS, seed=0,
                  gain=GAIN_REAL, safety=True)
v["kwh_safed"], v["viol_safed"] = r_safe["kwh"], r_safe["viol"]
v["over_safed"] = r_safe["over_degh"]
v["tmax_safed"] = float(r_safe["temps"].max())
v["safety_cost_pct"] = (v["kwh_safed"] / v["kwh_real"] - 1) * 100
v["still_save_pct"] = (1 - v["kwh_safed"] / v["kwh_rule_real"]) * 100
print(f"\n加安全层后：耗电 {v['kwh_safed']:,.0f} kWh，越界 {v['viol_safed']} 次，"
      f"最高 {v['tmax_safed']:.2f} ℃")
assert v["viol_safed"] == 0, "安全层的职责就是把越界清零"
print(f"**安全层的价钱：多花 {v['safety_cost_pct']:.2f}% 的电，"
      f"把 {v['viol_real']} 次越界变成 0 次**；"
      f"扣掉这笔钱，相对保守规则仍省 {v['still_save_pct']:.1f}%")
print("这一条值得记住：**安全层不是给模型打补丁，是把“绝对不许发生的事”从学习里拿出来、"
      "写成代码**。它花多少钱是可以算的，而且通常很便宜")

# ---------- 五、把安全层挪到仿真里会怎样
r_sim_safe = run_hall(learned_policy(SP, 240.0, LEAD), N_DAYS, seed=0, safety=True)
v["kwh_sim_safed"] = r_sim_safe["kwh"]
v["sim_safety_cost_pct"] = (v["kwh_sim_safed"] / v["kwh_sim"] - 1) * 100
print(f"\n在仿真里，安全层几乎不花钱（多 {v['sim_safety_cost_pct']:.2f}%）——"
      "因为仿真里本来就不越界")
print("**所以安全层的价钱只能在真设备上算**；在仿真里算出来的那个数，会低估它")

out(**v)
