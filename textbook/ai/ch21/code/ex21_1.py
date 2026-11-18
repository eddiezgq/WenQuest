"""算例 21.1.1—21.1.3：数据在哪一层丢掉（21.1 节）。

车间的数据有三层：传感器（毫秒级）、制造执行系统（工序级，靠人扫码）、
企业资源计划（订单级，按天）。三层各自有时钟，而且越往上记录越稀。

本算例把三件事算出来：
（1）**同一个批次，三层给出的"加工用了多久"不是一个数**，差多少；
（2）**时钟差多大就开始出错**：两台服务器差几十秒，工位的占用率就能算反；
（3）**记录粒度决定了你能回答什么问题**：按天记的那一层，连"哪台机床慢"都问不出来。
"""
import numpy as np

from _ch21 import STATIONS, busy_share, cycle_time, make_batch
from bookout import out

N_PARTS = 40
v = {"n_parts": N_PARTS, "n_stations": len(STATIONS)}

# ---------- 一、三层各自给出的数
b = make_batch(N_PARTS, seed=0, drift_s=0.0, mes_round_s=60.0)
v["mes_round_s"] = 60.0

sensor_total = sum(r["end"] - r["start"] for r in b["sensor"])
mes_total = sum(r["end"] - r["start"] for r in b["mes"])
erp_days = b["erp"]["end_day"] - b["erp"]["start_day"]
v["sensor_hours"] = sensor_total / 3600.0
v["mes_hours"] = mes_total / 3600.0
v["erp_days"] = erp_days
v["mes_over_sensor"] = mes_total / sensor_total
print(f"传感器层：这一批的净加工 {v['sensor_hours']:.2f} 小时")
print(f"制造执行系统（扫码取整到 {v['mes_round_s']:.0f} 秒）：{v['mes_hours']:.2f} 小时，"
      f"是前者的 {v['mes_over_sensor']:.2f} 倍")
print(f"企业资源计划：只知道这批走了 {v['erp_days']:.0f} 天")
assert v["mes_hours"] > v["sensor_hours"], "取整只会把时长记长，不会记短"

# 取整带来的偏差有多大，与工序本身的长短有关：短工序被放大得最厉害
rows = []
for st in STATIONS:
    cs, cm = cycle_time(b["sensor"], st), cycle_time(b["mes"], st)
    rows.append((st, cs, cm, cm / cs))
rows.sort(key=lambda r: r[3], reverse=True)
v["worst_station"] = rows[0][0]
v["worst_ratio"] = rows[0][3]
v["worst_sensor_s"] = rows[0][1]
v["best_station"] = rows[-1][0]
v["best_ratio"] = rows[-1][3]
v["best_sensor_s"] = rows[-1][1]
print(f"\n取整放大得最厉害的是 {v['worst_station']}（真实 {v['worst_sensor_s']:.0f} 秒，"
      f"记成 {v['worst_ratio']:.1f} 倍）；最轻的是 {v['best_station']}"
      f"（真实 {v['best_sensor_s']:.0f} 秒，{v['best_ratio']:.2f} 倍）")
assert v["worst_ratio"] > v["best_ratio"], "工序越短，取整的相对影响越大"
print("**所以拿制造执行系统的工时去算节拍，短工序一定偏长**——"
      "这不是系统有毛病，是记录粒度决定的")

# ---------- 二、时钟差
# 两台服务器差 drift_s 秒。传感器层的真实时刻不变，只是制造执行系统整体偏移。
base_busy = {st: busy_share(b["sensor"], st) for st in STATIONS}
for drift in (0.0, 30.0, 90.0, 300.0):
    bb = make_batch(N_PARTS, seed=0, drift_s=drift, mes_round_s=60.0)
    err = [abs(busy_share(bb["mes"], st) - base_busy[st]) for st in STATIONS]
    v[f"busy_err_{int(drift)}"] = float(np.mean(err))
    print(f"时钟差 {drift:>5.0f} 秒：工位占用率平均算错 {v[f'busy_err_{int(drift)}']:.4f}")
print("注意这一组数：**整体平移不改变时长，所以占用率几乎不受影响**——"
      "时钟差真正害人的地方在下一段")

# 害人的地方：拿两层的时刻去**对齐**（例如"这个零件加工时主轴电流是多少"）
# 时钟差 drift 秒，就会把 drift 秒之前/之后的信号安到这个零件头上。
for drift in (0.0, 30.0, 90.0, 300.0):
    wrong = 0
    bb = make_batch(N_PARTS, seed=0, drift_s=drift, mes_round_s=60.0)
    for s_row, m_row in zip(b["sensor"], bb["mes"]):
        # 分析的人**不知道**时钟差多少，只会照制造执行系统的时刻去截信号
        mid = (m_row["start"] + m_row["end"]) / 2.0
        if not (s_row["start"] <= mid <= s_row["end"]):
            wrong += 1
    v[f"align_wrong_{int(drift)}"] = wrong / len(b["sensor"]) * 100
    print(f"时钟差 {drift:>5.0f} 秒：按工序时刻去截传感器信号，"
          f"{v[f'align_wrong_{int(drift)}']:.1f}% 的零件截到了别的时间段")
assert v["align_wrong_300"] > v["align_wrong_0"], "时钟差越大，对齐错得越多"
v["align_jump"] = v["align_wrong_300"] - v["align_wrong_0"]
print(f"从 0 到 300 秒，错配比例涨了 {v['align_jump']:.1f} 个百分点。"
      f"**这就是“数据链”这三个字的实际含义：时间戳对不齐，后面所有分析都是空的**")

# ---------- 三、粒度决定能问什么
v["sensor_rows"] = len(b["sensor"])
v["mes_rows"] = len(b["mes"])
v["erp_rows"] = 2
v["rows_ratio"] = v["sensor_rows"] / v["erp_rows"]
print(f"\n三层的记录条数：传感器 {v['sensor_rows']}、制造执行系统 {v['mes_rows']}、"
      f"企业资源计划 {v['erp_rows']}（差 {v['rows_ratio']:.0f} 倍）")
print("能回答的问题也差这么多：按天记的那一层，连“哪台机床慢”都问不出来——"
      "**不是模型不行，是数据里没有这个问题的答案**")

out(**v)
