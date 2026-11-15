"""第 167b 轮：软件公司案例 C——20 柜云平台的容量规划。
计算机厂案例 C 的 20 柜机房（16 柜计算 + 4 柜存储，两个可用区）：三年能卖多少份云订阅（100 vCPU·月）、超分比与内存、坏一整柜的余量、
接口网关几台、租户可用性、多久回本。订阅增长预测；虚拟机在线装箱仿真（三年开通、退订）算碎片；网关 Erlang C 公式对照离散事件仿真；
全年 8 760 小时负载看高峰；坏服务器、坏柜、可用区事故的蒙特卡洛算租户月度停机；软件公司开通 24 份订阅验收，
再演一次“吵闹的邻居”：注入后验收不合格，下发“隔离租户”措施后合格。

    python3 tools/cases/software_c.py

服务器配置、虚拟机规格分布、请求量、故障率、电价、人工都是示例值。输出到 factory/cases/software/C/。
"""
from __future__ import annotations

import heapq
import json
import math
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-software.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402
import yaml  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402

TOOLS = {
    "softops": ("发布与服务", "Releases & services", "/software-ops"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "quality": ("质量", "Quality", "/work/quality"),
    "energy": ("能源与环境", "Energy & environment", "/energy"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("software", "C", "完整", "20 柜云平台的容量规划", "Capacity planning for a 20-rack cloud", "WQ-Cloud 机房与订阅",
              "计算机厂 20 柜机房上的云平台：16 柜计算、4 柜存储、两个可用区。比较超分比和内存配置，选 1.5 倍超分 + 768 GB 内存；留一整柜余量；"
              "三年订阅预测与可卖容量对照；虚拟机在线装箱仿真算碎片；接口网关 Erlang C 与离散事件仿真对照；全年 8 760 小时看高峰 CPU；"
              "坏服务器、坏柜、可用区事故的蒙特卡洛算租户停机；回本时间；开通 24 份订阅验收，演一次“吵闹的邻居”从发现到隔离。",
              "A cloud on the computer plant's 20-rack hall: 16 compute racks, 4 storage racks, two availability zones. Overcommit ratio and memory compared, "
              "1.5× overcommit with 768 GB chosen; one rack per zone held in reserve; three-year subscription forecast against sellable capacity; online VM bin-packing "
              "simulation for fragmentation; API gateways by Erlang C and discrete-event simulation; 8,760-hour peak CPU; Monte Carlo of server, rack and zone failures "
              "for tenant downtime; payback; 24 subscriptions accepted and a noisy-neighbour incident caught and isolated.",
              "tools/cases/software_c.py")

# ---------------------------------------------------------------- 任务（示例值）
N_RACK, SV_PER = 20, 16
N_STORE = 4                                   # 存储柜（案例 B）
N_COMP_RACK = N_RACK - N_STORE
N_SV = N_COMP_RACK * SV_PER                   # 计算服务器
N_CTRL = 8                                    # 控制面（元数据、调度、监控、网关）占的服务器，两区各 4 台
N_HOST = N_SV - N_CTRL
THREADS = 128                                 # 每台 2 × 32 核 × 2 线程（WQ-SV2U，示例配置）
HOST_RAM = 32                                 # 宿主机自己留的内存 GB
GB_PER_VCPU = 4.0                             # 通用型虚拟机 1 vCPU : 4 GB
SUB_VCPU = 100                                # 一份订阅 = 100 vCPU·月（软件公司清单 SUB-CLOUD）
PRICE = 2400.0                                # 每份每月 USD（软件公司价目）
VM_UTIL = 0.35                                # 虚拟机平均 CPU 利用率（通用业务的常见量级）
CPU_PEAK_MAX = 0.85                           # 高峰小时物理 CPU 利用率上限
MONTHS = 36
K_SUB, R_SUB, T0_SUB = 400, 0.15, 20          # 订阅增长（逻辑斯谛）：上限、增速、拐点月
REQ_PER_SUB = 15.0                            # 每份订阅平均接口请求 / s
SVC_MS = 2.0                                  # 网关每个请求平均处理时间（一个核）
GW_CORES = 32                                 # 一台网关虚拟机的核数
GW_P99 = 20.0                                 # 网关 p99 预算 ms（服务延迟 p99 ≤ 50 ms 的一部分）
SLA = 99.9                                    # 月可用性承诺 %
AFR_SV, RACK_RATE, AZ_RATE = 0.04, 0.2, 0.1   # 服务器年故障率；每柜每年断电 / 断网次数；每可用区每年事故次数
T_SV, T_RACK, T_AZ, T_FAILOVER = 5.0, 15.0, 60.0, 2.0   # 停机分钟：服务器坏（虚拟机在别处重启）、整柜、可用区事故（单区租户）、跨区切换

plant_c = json.loads((ROOT / "factory" / "cases" / "computer" / "C" / "case.json").read_text(encoding="utf-8"))
PUE = float(next(f["value"] for s in plant_c["steps"] for f in s["facts"] if f["name"] == "年 PUE"))
comp = yaml.safe_load((ROOT / "factory" / "plants" / "wenquest-computer.yaml").read_text(encoding="utf-8"))
RACK_PRICE = float(next(p["price"] for p in comp["products"] if p["item"] == "WQ-RACK42"))
P_RACK_KW = 10.8                              # 每柜满载功率（计算机厂案例 C）
ELEC = 0.09                                   # 电价 USD/kWh
STAFF = 6 * 150_000.0                         # 运维 6 人一年
RAM_PRICE = 2.5                               # 加内存 USD/GB


def subs(m):
    return K_SUB / (1 + math.exp(-R_SUB * (m - T0_SUB)))


brief = f"""# 设计任务书：20 柜云平台的容量规划

**用在哪**　软件公司向计算机厂买了 {N_RACK} 台整机柜 WQ-RACK42（计算机厂案例 C 的机房，每柜 {SV_PER} 台 WQ-SV2U），建云平台 WQ-Cloud：
{N_COMP_RACK} 柜计算（{N_SV} 台服务器）、{N_STORE} 柜存储（本厂案例 B）。两个可用区，各一半，供电、网络分开。
卖的是订阅 SUB-CLOUD：**一份 = {SUB_VCPU} vCPU·月，{PRICE:,.0f} 美元**（软件公司价目）。

| 项目 | 要求 | 出处 |
|---|---|---|
| 三年订阅预测 | 逻辑斯谛增长，上限 {K_SUB} 份，第 36 个月约 {subs(36):.0f} 份 | 市场预测（示例） |
| 容量 | 第 36 个月的订阅装得下，**每个可用区留一整柜**（坏一柜虚拟机有地方重启） | 运维规程 |
| 高峰物理 CPU | 高峰小时 ≤ {CPU_PEAK_MAX * 100:.0f} %（超分后不能挤爆） | 运维规程 |
| 服务延迟 p99 | ≤ 50 ms（软件公司清单 cl_p99）；其中网关 ≤ {GW_P99:g} ms，一个可用区全断时也满足 | 服务验收 |
| 月可用性 | ≥ {SLA} %（软件公司清单 cl_avail 的日指标 ≥ 99.9 %） | 订阅合同 |
| 回本 | 36 个月内 | 投资要求 |

服务器配置、虚拟机规格分布、请求量、故障率、电价、人工都是示例值。整机柜价格 {RACK_PRICE:,.0f} 美元取计算机厂价目，PUE {PUE} 取计算机厂案例 C。
"""
case.step("brief", f"{N_SV} 台计算服务器、两个可用区；第 36 个月约 {subs(36):.0f} 份订阅；留一整柜；网关 p99 ≤ {GW_P99:g} ms；月可用性 ≥ {SLA} %；36 个月回本。",
          f"{N_SV} compute servers in two zones; about {subs(36):.0f} subscriptions by month 36; one rack in reserve; gateway p99 ≤ {GW_P99:g} ms; "
          f"monthly availability ≥ {SLA} %; payback within 36 months.",
          md=case.text("1_任务书.md", brief),
          facts=[("计算服务器", "Compute servers", N_SV, ""), ("36 个月订阅", "Subscriptions at month 36", round(subs(36)), ""), ("单价", "Price", f"{PRICE:,.0f}", "USD/月")])

# ================================================================ 2 方案：超分比与内存
# 全年 8 760 小时负载（第 36 个月的规模）：日周期 + 工作日 / 周末 + 噪声；请求量和虚拟机 CPU 利用率跟着走
rng = random.Random(1676)
hours = np.arange(8760)
day = 1 + 0.75 * np.sin((hours % 24 - 8) / 24 * 2 * np.pi) ** 1 * ((hours % 24 >= 8) & (hours % 24 <= 20)) - 0.25 * ((hours % 24 < 7) | (hours % 24 > 22))
week = np.where(((hours // 24) % 7) >= 5, 0.7, 1.0)
noise = np.array([rng.lognormvariate(0, 0.08) for _ in hours])
shape = day * week * noise
shape = shape / shape.mean()
peak_factor = float(np.quantile(shape, 0.999))
BASE = 0.6                                    # 虚拟机 CPU 的六成是跟请求量无关的底子（系统、后台、批处理），四成跟着请求量走
cpu_mult = BASE + (1 - BASE) * shape           # 每小时虚拟机 CPU 利用率 = 平均 × cpu_mult
CPU_PEAK_MULT = float(cpu_mult.max())
RESERVE = 1 / (N_COMP_RACK / 2)               # 每区 8 柜留 1 柜
PACK_ASSUMED = 0.92                           # 装箱效率（碎片），第 4 步仿真核对


def sellable(oc, ram):
    per = min(THREADS * oc, (ram - HOST_RAM) / GB_PER_VCPU)
    return per, N_HOST * per * (1 - RESERVE) * PACK_ASSUMED


OPTS = [("不超分，512 GB", 1.0, 512, 0.0), ("1.5 倍超分，512 GB", 1.5, 512, 0.0), ("不超分，768 GB", 1.0, 768, 256), ("1.5 倍超分，768 GB", 1.5, 768, 256),
        ("2 倍超分，1 TB", 2.0, 1024, 512)]
need36 = subs(36) * SUB_VCPU
orow = []
for name, oc, ram, add in OPTS:
    per, cap = sellable(oc, ram)
    peak = VM_UTIL * CPU_PEAK_MULT * oc * min(1.0, per / (THREADS * oc))   # 高峰物理 CPU = 虚拟机平均利用率 × 全年最高小时系数 × 实际超分（卖满时）
    orow.append(dict(name=name, oc=oc, ram=ram, per=per, cap=cap, subs=cap / SUB_VCPU, add=add, cost=add * RAM_PRICE * N_HOST, peak=peak))
SEL = 3
sel = orow[SEL]
conmd = f"""# 方案：超分比与内存

一台服务器能卖多少 vCPU = min(线程数 {THREADS} × 超分比，(内存 − 宿主机 {HOST_RAM} GB) ÷ {GB_PER_VCPU:g} GB)。
全平台可卖 = {N_HOST} 台（{N_SV} 台减控制面 {N_CTRL} 台）× 每台可卖 × (1 − 留一柜 {RESERVE * 100:.1f} %) × 装箱效率 {PACK_ASSUMED}。

{L.md_table(["方案", "每台可卖 vCPU", "全平台可卖 vCPU", "能卖订阅", "第 36 个月要", "加内存投入", "高峰物理 CPU（估）", ""],
            [[o["name"], f"{o['per']:.0f}", f"{o['cap']:,.0f}", f"{o['subs']:.0f}", f"{subs(36):.0f}", f"{o['cost']:,.0f} USD", f"{o['peak'] * 100:.0f} %",
              ("✓ 选定" if i == SEL else ("✗ 装不下" if o["subs"] < subs(36) else ("✗ CPU 挤爆" if o["peak"] > CPU_PEAK_MAX else "")))] for i, o in enumerate(orow)])}

- **超分不加内存没用**：512 GB 时每台只能卖 {orow[1]['per']:.0f} vCPU，**内存先用完**，CPU 超分了也卖不出去。
- **1.5 倍超分 + 768 GB**：虚拟机平均只用 {VM_UTIL * 100:.0f} % 的 CPU（全年最忙的小时是平均的 {CPU_PEAK_MULT:.2f} 倍，第 4 步的 8 760 小时负载），
  超分 1.5 倍、卖满时高峰物理 CPU 约 {sel['peak'] * 100:.0f} %；内存 768 GB 刚好配上 {sel['per']:.0f} vCPU。
- **2 倍超分**：容量多，但高峰 CPU 会超 {CPU_PEAK_MAX * 100:.0f} %，租户之间抢 CPU（“吵闹的邻居”）——不选。
- 超分以后必须给每个租户设 CPU 限额，不然一个租户能把整台机器占满——第 7 步就演这个故障。
- 加内存向计算机厂下单（每台多 256 GB），整机柜不用换。
- **余量很薄**：第 36 个月正好卖满（{sel['subs']:.1f} 份对 {subs(36):.1f} 份）。所以每月容量评审在分配率 75 % 时（第 {next(m for m in range(1, 61) if subs(m) >= 0.75 * sel['subs'])} 个月）
  就向计算机厂下整机柜订单，第四年的增长靠扩容，不靠再提超分。
"""
case.step("concept", f"选 1.5 倍超分 + 768 GB：每台卖 {sel['per']:.0f} vCPU，全平台 {sel['subs']:.0f} 份订阅 ≥ 第 36 个月 {subs(36):.0f} 份；512 GB 时内存先用完。",
          f"1.5× overcommit with 768 GB: {sel['per']:.0f} vCPU per server, {sel['subs']:.0f} subscriptions ≥ {subs(36):.0f} needed at month 36; with 512 GB memory runs out first.",
          md=case.text("2_方案.md", conmd),
          facts=[("每台可卖", "Sellable per server", round(sel["per"]), "vCPU"), ("能卖订阅", "Sellable subscriptions", round(sel["subs"]), ""),
                 ("加内存投入", "Memory upgrade", f"{sel['cost']:,.0f}", "USD")])
case.check("concept", "可卖订阅 ≥ 第 36 个月预测", "Sellable subscriptions ≥ month-36 forecast", round(sel["subs"]), ">=", round(subs(36)), "份", "任务书")


# ================================================================ 3 计算：网关排队、可用性、回本
def erlang_c(c, a):
    """Erlang C：c 个服务台、到达强度 a = λ/μ 时要排队的概率"""
    s, term = 0.0, 1.0
    for k in range(c):
        if k:
            term *= a / k
        s += term
    term *= a / c if c else 1.0
    last = term * c / (c - a)
    return last / (s + last)


def p99_resp(c, lam, mu, q=0.99):
    """M/M/c 响应时间（排队 + 处理）的 q 分位，秒。R = S + W：要排队（概率 Pw）时 W ~ Exp(cμ − λ)；S ~ Exp(μ)"""
    pw = erlang_c(c, lam / mu)
    a = c * mu - lam

    def tail(t):
        hyp = (a * math.exp(-mu * t) - mu * math.exp(-a * t)) / (a - mu) if abs(a - mu) > 1e-9 else (1 + mu * t) * math.exp(-mu * t)
        return (1 - pw) * math.exp(-mu * t) + pw * hyp
    lo, hi = 0.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tail(mid) > 1 - q else (lo, mid)
    return hi, pw


lam_avg = subs(36) * REQ_PER_SUB
lam_peak = lam_avg * peak_factor
cpu_hour = VM_UTIL * cpu_mult * sel["oc"] * (sel["per"] / (THREADS * sel["oc"]))   # 卖满时的物理 CPU 利用率（最坏：可卖的都卖了）
cpu_peak = float(cpu_hour.max())
mu = 1000.0 / SVC_MS
gw_rows, n_gw = [], None
for n in range(1, 7):
    c_all = n * GW_CORES
    if lam_peak >= c_all * mu:
        gw_rows.append([n, "过载", "—", "—"])
        continue
    r99, pw = p99_resp(c_all, lam_peak, mu)
    gw_rows.append([n, f"{lam_peak / (c_all * mu) * 100:.0f} %", f"{pw:.3f}", f"{r99 * 1000:.1f} ms"])
    if n_gw is None and r99 * 1000 <= GW_P99:
        n_gw = n
GW_PER_AZ = max(n_gw, 2)                          # 一个可用区全断时，剩下那个区的网关要扛全部；每区至少 2 台（区内坏一台还有一台）
r99_one_az, _ = p99_resp(GW_PER_AZ * GW_CORES, lam_peak, mu)

# 可用性（解析）：单区租户一年停机分钟期望 = 服务器坏 + 整柜 + 可用区事故；两区租户可用区事故只停切换时间
down_1az = AFR_SV * T_SV + RACK_RATE * T_RACK + AZ_RATE * T_AZ
down_2az = AFR_SV * T_SV + RACK_RATE * T_RACK + AZ_RATE * T_FAILOVER
avail_1az = 100 * (1 - down_1az / (365 * 1440))
avail_2az = 100 * (1 - down_2az / (365 * 1440))

# 回本：每月现金流（收入 − 电费 − 人工 − 其他），期初投资 = 整机柜 + 加内存 + 网络
CAPEX = N_RACK * RACK_PRICE + sel["cost"] + 150_000
power_kw = N_RACK * P_RACK_KW * PUE
elec_month = power_kw * 730 * ELEC
staff_month = STAFF / 12
cum, pay_m, cash = -CAPEX, None, []
for m in range(1, 61):
    rev = subs(m) * PRICE
    cum += rev - elec_month - staff_month - 0.08 * rev            # 其他：带宽、软件授权、销售 8 %
    cash.append(cum)
    if pay_m is None and cum >= 0:
        pay_m = m

calcmd = f"""# 计算

## 1. 网关：Erlang C

第 36 个月 {subs(36):.0f} 份订阅，每份平均 {REQ_PER_SUB:g} 个请求 / s，平均 {lam_avg:,.0f} 个 / s；全年 8 760 小时负载（第 4 步）的 99.9 分位是平均的 {peak_factor:.2f} 倍，
**高峰 {lam_peak:,.0f} 个 / s**。每个请求在网关一个核上平均处理 {SVC_MS:g} ms（μ = {mu:.0f} / s），一台网关 {GW_CORES} 核。

M/M/c 排队：要排队的概率 Pw = Erlang C；响应时间 R = 处理 + 排队，排队时等待 ~ 指数(cμ − λ)。按 R 的 99 分位：

{L.md_table(["网关台数（一个区扛全部）", "利用率", "要排队的概率", "响应 p99"], gw_rows)}

利用率不高时 p99 几乎全是处理时间自己的尾巴（指数分布：{SVC_MS:g} ms × ln 100 = {SVC_MS * math.log(100):.1f} ms），台数再加也降不下来；要再降只能缩短处理时间。

一个可用区全断时剩下的区要扛全部：算出 {n_gw} 台就够；区内还要能坏一台，所以**每个区放 {GW_PER_AZ} 台**（共 {2 * GW_PER_AZ} 台）：单区扛全部时 p99 {r99_one_az * 1000:.1f} ms ≤ {GW_P99:g} ms。
平时两区分担，利用率只有一半。

## 2. 租户可用性

| 事件 | 频率 | 停多久（单区租户 / 两区租户） | 一年停机期望 |
|---|---|---|---|
| 服务器坏 | 每台 {AFR_SV * 100:.0f} % / 年 | 虚拟机在别的服务器重启 {T_SV:g} 分钟 | {AFR_SV * T_SV:.1f} 分钟 |
| 整柜断电 / 断网 | 每柜 {RACK_RATE:g} 次 / 年 | {T_RACK:g} 分钟（留的那一柜接住） | {RACK_RATE * T_RACK:.1f} 分钟 |
| 可用区事故 | 每区 {AZ_RATE:g} 次 / 年 | {T_AZ:g} 分钟 / 两区租户切换 {T_FAILOVER:g} 分钟 | {AZ_RATE * T_AZ:.1f} / {AZ_RATE * T_FAILOVER:.1f} 分钟 |

一年停机期望：单区租户 {down_1az:.1f} 分钟（{avail_1az:.4f} %），两区租户 {down_2az:.1f} 分钟（{avail_2az:.4f} %）。平均都远好于 {SLA} %，
但**月度**承诺要看坏的那个月：一次 {T_AZ:g} 分钟的可用区事故就超过一个月允许的 {0.001 * 30 * 1440:.0f} 分钟——第 4 步用蒙特卡洛算有多少个月会违约。

## 3. 回本

| 项目 | 金额 |
|---|---|
| 期初投资 | 整机柜 {N_RACK} × {RACK_PRICE:,.0f} + 加内存 {sel['cost']:,.0f} + 网络 150,000 = **{CAPEX:,.0f} USD** |
| 电费 | {N_RACK} 柜 × {P_RACK_KW:g} kW × PUE {PUE} × {ELEC:g} USD/kWh = {elec_month:,.0f} USD / 月 |
| 人工 | 运维 6 人，{staff_month:,.0f} USD / 月 |
| 其他 | 带宽、授权、销售，收入的 8 % |
| 收入 | 订阅数（逻辑斯谛预测）× {PRICE:,.0f} USD / 月 |

累计现金流第 **{pay_m}** 个月转正（≤ 36）。
"""
case.step("calc", f"网关每区 {GW_PER_AZ} 台（单区扛全部 p99 {r99_one_az * 1000:.1f} ms）；租户一年停机期望 {down_1az:.1f} / {down_2az:.1f} 分钟（单区 / 两区）；第 {pay_m} 个月回本。",
          f"{GW_PER_AZ} gateways per zone (p99 {r99_one_az * 1000:.1f} ms with one zone carrying all); expected downtime {down_1az:.1f} / {down_2az:.1f} min a year "
          f"(single / dual zone); payback in month {pay_m}.",
          md=case.text("3_计算.md", calcmd),
          facts=[("网关", "Gateways", f"2×{GW_PER_AZ}", ""), ("期初投资", "Capex", f"{CAPEX / 1e6:.2f}", "M USD"), ("回本", "Payback", pay_m, "月")])
case.check("calc", "一个可用区全断时网关 p99", "Gateway p99 with one zone down", round(r99_one_az * 1000, 1), "<=", GW_P99, "ms", "任务书")
case.check("calc", "回本月数", "Payback (months)", pay_m, "<=", MONTHS, "月", "任务书")


# ================================================================ 4 仿真
# 4.1 虚拟机在线装箱：三年里租户开通、扩缩、退订，虚拟机随来随放（最佳适应），看最后的碎片
VM_MIX = [((2, 8), 0.24), ((4, 16), 0.24), ((8, 32), 0.15), ((16, 64), 0.08), ((32, 128), 0.04),     # 通用型 1:4
          ((4, 8), 0.08), ((8, 16), 0.05),                                                       # 计算型 1:2
          ((4, 32), 0.07), ((8, 64), 0.05)]                                                      # 内存型 1:8


def pack_sim(seed=1677):
    rs = random.Random(seed)
    cap_cpu, cap_ram = sel["per"], sel["ram"] - HOST_RAM
    hosts = [[cap_cpu, cap_ram] for _ in range(int(N_HOST * (1 - RESERVE)))]
    vms = {}
    vid = 0
    alloc = 0
    rejected = 0
    hist = []
    sizes, w = zip(*VM_MIX)
    for m in range(1, MONTHS + 1):
        target = subs(m) * SUB_VCPU
        # 每月约 3 % 的虚拟机退订（腾出空洞）
        for k in [k for k in vms if rs.random() < 0.03]:
            h, c, r = vms.pop(k)
            hosts[h][0] += c
            hosts[h][1] += r
            alloc -= c
        while alloc < target:
            c, r = rs.choices(sizes, w)[0]
            best, bi = None, -1
            for i, (fc, fr) in enumerate(hosts):            # 最佳适应：放进剩余 CPU 最少、又放得下的那台
                if fc >= c and fr >= r and (best is None or fc < best):
                    best, bi = fc, i
            if bi < 0:
                rejected += 1
                break
            hosts[bi][0] -= c
            hosts[bi][1] -= r
            vms[vid] = (bi, c, r)
            vid += 1
            alloc += c
        free = sum(fc for fc, _ in hosts)
        hist.append((m, alloc, free))
    # 三年后接着随机开虚拟机（放不下的跳过），直到一台常见的 8 vCPU / 32 GB 都放不下：这时的分配率就是“装满时能用到多少”（剩下的是碎片）
    at36 = alloc
    while any(fc >= 8 and fr >= 32 for fc, fr in hosts):
        c, r = rs.choices(sizes, w)[0]
        cand = [i for i, (fc, fr) in enumerate(hosts) if fc >= c and fr >= r]
        if not cand:
            continue
        bi = min(cand, key=lambda i: hosts[i][0])
        hosts[bi][0] -= c
        hosts[bi][1] -= r
        alloc += c
    total = cap_cpu * len(hosts)
    return alloc / total, rejected, hist, at36, total


pack_eff, pack_rej, pack_hist, pack_alloc, pack_total = pack_sim()


# 4.2 网关离散事件仿真：M/M/c，高峰时刻 λ，一个可用区扛全部
def gw_sim(c, lam, mu, n=300_000, seed=1678):
    rs = random.Random(seed)
    free_at = [0.0] * c
    heapq.heapify(free_at)
    t = 0.0
    out = []
    for _ in range(n):
        t += rs.expovariate(lam)
        f = heapq.heappop(free_at)
        start = max(t, f)
        end = start + rs.expovariate(mu)
        heapq.heappush(free_at, end)
        out.append(end - t)
    out = sorted(out[n // 10:])
    return out[int(0.99 * len(out))]


sim_r99 = gw_sim(GW_PER_AZ * GW_CORES, lam_peak, mu)
d_gw = (sim_r99 / r99_one_az - 1) * 100


# 4.3 可用性蒙特卡洛：一个租户一年按分钟算，单区、两区；统计月度违约（月停机 > 0.1 % × 30 天）
def avail_mc(two_az, years=200_000, seed=1679):
    rs = random.Random(seed)
    lim = 0.001 * 30 * 1440
    bad_months, total_down = 0, 0.0
    for _ in range(years):
        month = [0.0] * 12
        for rate, dur in ((AFR_SV, T_SV), (RACK_RATE, T_RACK), (AZ_RATE, T_FAILOVER if two_az else T_AZ)):
            t = rs.expovariate(rate)
            while t < 1.0:
                month[min(11, int(t * 12))] += dur * (rs.uniform(0.5, 1.5))
                t += rs.expovariate(rate)
        total_down += sum(month)
        bad_months += sum(1 for d in month if d > lim)
    return total_down / years, bad_months / (years * 12) * 100


mc1_down, mc1_bad = avail_mc(False)
mc2_down, mc2_bad = avail_mc(True, seed=1680)
d_av = max(abs(mc1_down / down_1az - 1), abs(mc2_down / down_2az - 1)) * 100

fig, axs = plt.subplots(2, 2, figsize=(12, 7.5))
mm = np.arange(1, MONTHS + 1)
axs[0, 0].plot(mm, [subs(m) for m in mm], label="订阅预测")
axs[0, 0].axhline(sel["subs"], color="#2f9e44", ls="--", label=f"可卖（1.5 倍 + 768 GB）{sel['subs']:.0f}")
axs[0, 0].axhline(orow[0]["subs"], color="#c92a2a", ls=":", label=f"不超分 512 GB {orow[0]['subs']:.0f}")
axs[0, 0].set_xlabel("月")
axs[0, 0].set_ylabel("订阅份数")
axs[0, 0].legend(fontsize=8)
axs[0, 0].set_title("三年订阅与可卖容量", fontsize=10)
wk = slice(24 * 7 * 10, 24 * 7 * 12)
axs[0, 1].plot(hours[wk] - hours[wk][0], cpu_hour[wk] * 100, lw=0.8)
axs[0, 1].axhline(CPU_PEAK_MAX * 100, color="#c92a2a", lw=1)
axs[0, 1].set_xlabel("小时（第 11–12 周）")
axs[0, 1].set_ylabel("物理 CPU 利用率 %")
axs[0, 1].set_title(f"卖满时的物理 CPU：全年最高 {cpu_peak * 100:.0f} %（红线 {CPU_PEAK_MAX * 100:.0f} %）", fontsize=10)
xs = np.linspace(0.0005, 0.03, 200)
axs[1, 0].set_title("网关响应时间分布（单区扛全部，高峰）", fontsize=10)
c_all = GW_PER_AZ * GW_CORES
pw = erlang_c(c_all, lam_peak / mu)
a_ = c_all * mu - lam_peak
tail = [(1 - pw) * math.exp(-mu * t) + pw * ((a_ * math.exp(-mu * t) - mu * math.exp(-a_ * t)) / (a_ - mu)) for t in xs]
axs[1, 0].semilogy(xs * 1000, tail, label="Erlang C 公式")
axs[1, 0].axvline(sim_r99 * 1000, color="#e8590c", ls="--", label=f"仿真 p99 {sim_r99 * 1000:.1f} ms")
axs[1, 0].axhline(0.01, color="k", lw=0.5)
axs[1, 0].set_xlabel("响应时间 / ms")
axs[1, 0].set_ylabel("P(响应 > t)")
axs[1, 0].legend(fontsize=8)
axs[1, 1].plot(range(1, 61), [c / 1e6 for c in cash])
axs[1, 1].axhline(0, color="k", lw=0.6)
axs[1, 1].axvline(pay_m, color="#2f9e44", ls="--")
axs[1, 1].set_xlabel("月")
axs[1, 1].set_ylabel("累计现金流 / 百万 USD")
axs[1, 1].set_title(f"第 {pay_m} 个月回本", fontsize=10)
fig.tight_layout()
case.fig(fig, "4_容量仿真.png")
simmd = f"""# 仿真

## 1. 虚拟机在线装箱（三年）

虚拟机规格按 {', '.join(f'{c} vCPU/{r} GB {p * 100:.0f} %' for (c, r), p in VM_MIX)} 随机（通用型 1:4、计算型 1:2、内存型 1:8）；每月按订阅预测开通，每月约 3 % 退订（留下空洞），
新虚拟机用“最佳适应”放（放进剩余最少、又放得下的那台）。第 36 个月已分配 {pack_alloc:,.0f} vCPU（总 {pack_total:,.0f}），三年里放不下而被拒 {pack_rej} 次。
然后接着随机开虚拟机（放不下的跳过），直到连一台 8 vCPU / 32 GB 的都放不下——这时的 vCPU 分配率就是**装满时能用到多少：{pack_eff * 100:.1f} %**（第 2 步假设 {PACK_ASSUMED * 100:.0f} %），剩下的是碎片：计算型、内存型虚拟机的 CPU 和内存比例和宿主机不一样，一台机器常常 CPU 还剩、内存先满（或反过来）。

## 2. 全年 8 760 小时

日周期（白天高、夜里低）、周末 0.7 倍、每小时随机波动。按第 36 个月的规模：网关请求高峰（99.9 分位）是平均的 {peak_factor:.2f} 倍；
虚拟机 CPU 六成是跟请求量无关的底子、四成跟着请求量走，全年最忙的小时是平均的 {CPU_PEAK_MULT:.2f} 倍；
卖满时物理 CPU 利用率（{VM_UTIL * 100:.0f} % × 超分 × 这个系数）全年最高 **{cpu_peak * 100:.0f} %** ≤ {CPU_PEAK_MAX * 100:.0f} %。

## 3. 网关排队：公式对仿真

离散事件仿真 M/M/c（{GW_PER_AZ * GW_CORES} 个核、高峰 {lam_peak:,.0f} 个 / s、30 万个请求，去掉前 10 % 预热）：p99 {sim_r99 * 1000:.2f} ms，
Erlang C 公式 {r99_one_az * 1000:.2f} ms，相差 {d_gw:+.1f} %。

## 4. 租户可用性蒙特卡洛（20 万租户·年）

| 租户 | 一年停机（公式） | 一年停机（蒙特卡洛） | 违约月份占比（月停机 > {0.001 * 30 * 1440:.0f} 分钟） |
|---|---|---|---|
| 单可用区 | {down_1az:.2f} 分钟 | {mc1_down:.2f} 分钟 | {mc1_bad:.2f} % |
| 两可用区 | {down_2az:.2f} 分钟 | {mc2_down:.2f} 分钟 | {mc2_bad:.3f} % |

单区租户每 100 个月约有 {mc1_bad:.1f} 个月违约——几乎全是可用区事故。所以合同写：**99.9 % 月可用性只承诺给跨两区部署的租户**；
单区租户承诺 99.5 %，控制台开通时默认跨两区。
"""
case.step("sim", f"装箱效率 {pack_eff * 100:.1f} %（假设 {PACK_ASSUMED * 100:.0f} %）；高峰物理 CPU {cpu_peak * 100:.0f} %；网关仿真与公式相差 {d_gw:+.1f} %；两区租户违约月份 {mc2_bad:.3f} %。",
          f"Packing efficiency {pack_eff * 100:.1f} % (assumed {PACK_ASSUMED * 100:.0f} %); peak physical CPU {cpu_peak * 100:.0f} %; gateway sim vs formula {d_gw:+.1f} %; "
          f"dual-zone tenants miss the SLA in {mc2_bad:.3f} % of months.",
          md=case.text("4_仿真.md", simmd), figs=[("4_容量仿真.png", "订阅与容量、CPU、网关、现金流", "Subscriptions vs capacity, CPU, gateway, cash flow")],
          facts=[("装箱效率", "Packing efficiency", round(pack_eff * 100, 1), "%"), ("高峰物理 CPU", "Peak physical CPU", round(cpu_peak * 100), "%"),
                 ("两区违约月份", "Dual-zone SLA-miss months", round(mc2_bad, 3), "%")])
case.check("sim", "装箱效率 ≥ 第 2 步假设", "Packing efficiency ≥ assumption", round(pack_eff * 100, 1), ">=", PACK_ASSUMED * 100, "%", "第 2 步")
case.check("sim", "三年内放不下被拒的虚拟机", "VMs rejected over three years", pack_rej, "==", 0, "", "任务书")
case.check("sim", "高峰物理 CPU 利用率", "Peak physical CPU utilization", round(cpu_peak * 100, 1), "<=", CPU_PEAK_MAX * 100, "%", "任务书")
case.check("sim", "网关 p99：仿真与 Erlang C 相差", "Gateway p99: simulation vs Erlang C", round(abs(d_gw), 1), "<=", 5.0, "%", "核对公式")
case.check("sim", "可用性：蒙特卡洛与公式相差（最大）", "Availability: Monte Carlo vs formula (max)", round(d_av, 1), "<=", 5.0, "%", "核对公式")
case.check("sim", "两区租户违约月份占比", "Dual-zone tenants: share of months below SLA", round(mc2_bad, 3), "<=", 0.1, "%", "订阅合同")

# ================================================================ 5 图纸：机房分区与网络
fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.8), gridspec_kw=dict(width_ratios=[1.3, 1]))
ax = axs[0]
ax.set_axis_off()
ax.set_xlim(-0.3, 10.3)
ax.set_ylim(-0.8, 5.2)
for row, (az, y) in enumerate((("可用区 A", 3.0), ("可用区 B", 0.4))):
    ax.text(-0.2, y + 1.85, az + f"（供电 {'1' if row == 0 else '2'} 路、核心交换各一对）", fontsize=9)
    for k in range(10):
        is_store = k >= 8
        is_res = k == 7
        lab = (f"S{row * 2 + k - 7}" if is_store else f"C{row * 8 + k + 1}")
        fc = "#e7f5ff" if is_store else ("#fff4e6" if is_res else "#eef3f8")
        ax.add_patch(plt.Rectangle((k * 1.0, y), 0.9, 1.6, fc=fc, ec="#2c6fbb"))
        ax.text(k * 1.0 + 0.45, y + 1.0, lab, ha="center", fontsize=8.5)
        ax.text(k * 1.0 + 0.45, y + 0.45, "存储" if is_store else ("余量" if is_res else "计算"), ha="center", fontsize=7, color="#7b8794")
    ax.add_patch(plt.Rectangle((0.0, y - 0.25), 0.9, 0.18, fc="#f3f0ff", ec="#7048e8"))
    ax.text(1.0, y - 0.24, f"控制面 {N_CTRL // 2} 台 + 网关 {GW_PER_AZ} 台（在 C{row * 8 + 1} 柜）", fontsize=7)
ax.set_title("机房分区：两个可用区，各 8 柜计算（1 柜余量）+ 2 柜存储", fontsize=10)
ax = axs[1]
ax.set_axis_off()
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
for (x, y, w, h, t, c) in [(0.3, 8.4, 9.4, 1.2, "互联网 / 园区专线 → 负载均衡（两区各一对）", "#eef3f8"),
                           (0.3, 6.5, 4.4, 1.4, f"接口网关 A × {GW_PER_AZ}\n（{GW_CORES} 核 / 台）", "#f3f0ff"),
                           (5.3, 6.5, 4.4, 1.4, f"接口网关 B × {GW_PER_AZ}", "#f3f0ff"),
                           (0.3, 4.5, 9.4, 1.4, "调度与元数据（三节点共识，跨两区 + 仲裁）", "#ebfbee"),
                           (0.3, 2.2, 4.4, 1.8, f"计算 A：{N_HOST // 2} 台\n1.5 倍超分、每租户 CPU 限额", "#e7f5ff"),
                           (5.3, 2.2, 4.4, 1.8, f"计算 B：{N_HOST // 2} 台", "#e7f5ff"),
                           (0.3, 0.3, 9.4, 1.4, "对象存储（案例 B：热三副本 + 温冷 RS(6,3)）", "#fff4e6")]:
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=c, ec="#2c6fbb"))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=8.5)
ax.set_title("平台架构（两区对称，任一区全断另一区扛全部）", fontsize=10)
case.fig(fig, "5_机房分区与架构.png")
cadmd = f"""# 图纸：机房分区与平台架构

软件没有三维零件（机房三维在计算机厂案例 C），这一步出**机房分区图**和**平台架构图**，写进云平台的区域配置：

| 区 | 计算柜 | 余量柜 | 存储柜 | 控制面 | 网关 |
|---|---|---|---|---|---|
| A | C1–C7 | C8 | S1、S2 | {N_CTRL // 2} 台（C1） | {GW_PER_AZ} 台 |
| B | C9–C15 | C16 | S3、S4 | {N_CTRL // 2} 台（C9） | {GW_PER_AZ} 台 |

- 余量柜平时也开机跑虚拟机，但调度器只放“可被打断”的批处理虚拟机；坏一柜时把它们停掉，给要重启的虚拟机腾地方；
- 每台宿主机给每个租户设 CPU 限额（超分的前提）；
- 订阅开通时默认跨两区（控制台勾选）。
"""
case.step("cad", f"两区对称：各 7 柜计算 + 1 柜余量 + 2 柜存储，控制面 {N_CTRL // 2} 台、网关 {GW_PER_AZ} 台；租户 CPU 限额；默认跨两区。",
          f"Two symmetric zones: 7 compute racks + 1 reserve + 2 storage each, {N_CTRL // 2} control-plane servers and {GW_PER_AZ} gateways; per-tenant CPU limits; dual-zone by default.",
          md=case.text("5_机房分区与架构.md", cadmd), figs=[("5_机房分区与架构.png", "机房分区与平台架构", "Hall zoning and platform architecture")])

# ================================================================ 6 工艺
from factory import data as F  # noqa: E402

rts = F.ROUTINGS[F.BOMS["SUB-CLOUD"][0]]
procmd = f"""# 工艺：订阅开通与容量管理

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rts)])}

- **资源开通**：按订阅建租户、配额（100 vCPU、400 GB）、CPU 限额、两区网络；
- **服务验收 24 小时**：每分钟的延迟 p99、错误率、可用性（cl_p99 ≤ 50 ms、cl_err ≤ 0.1 %、cl_avail ≥ 99.9 %）；不合格不交付，查宿主机和配置；
- **容量评审每月一次**：已分配 / 可卖 > 75 % 时向计算机厂下整机柜订单（交货加上架约 2 个月），按第 4 步装箱效率核可卖容量；
- **高峰物理 CPU** > {CPU_PEAK_MAX * 100:.0f} % 的宿主机，调度器不再往上放新虚拟机。
"""
case.step("process", f"订阅 {len(rts)} 道：资源开通 → 24 小时服务验收；每月容量评审，分配率过 75 % 向计算机厂下单。",
          f"Subscription in {len(rts)} steps: provisioning, then 24-hour acceptance; monthly capacity review, order racks from the computer plant above 75 % allocation.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer", "planner"), facts=[("工序", "Operations", len(rts), "")])

# ================================================================ 7 制造：24 份订阅 + 吵闹的邻居
OP_PROV = rts[0][0]                           # 订阅开在哪台宿主机由“资源开通”这道定
sh0 = L.run_shop("SUB-CLOUD", 24, "WO-CASE-SW-C1", seed=1681)
rows0, cpk0, fails0, st0 = L.shop_table(sh0["measurements"])
sh1 = L.run_shop("SUB-CLOUD", 6, "WO-CASE-SW-C2", seed=1682, problems=[("noisy_nb", None)], units={OP_PROV: "cl-a2"})
rows1, _, fails1, st1 = L.shop_table(sh1["measurements"])
sh2 = L.run_shop("SUB-CLOUD", 6, "WO-CASE-SW-C3", seed=1683, problems=[("noisy_nb", None)], fixes=["isolate_tenant"], units={OP_PROV: "cl-a2"})
rows2, cpk2, fails2, st2 = L.shop_table(sh2["measurements"])
bad_parts = len({m["part_serial"] for m in sh1["measurements"] if m["result"] != "pass"})
makemd = f"""# 制造：订阅开通与验收

## 1. 24 份订阅（宿主机 cl-a1，{sh0['hours']:.1f} 小时）

{L.md_table(["特性", "规格", "份数", "均值", "标准差", "Cpk"], rows0)}

不合格 **{fails0}**，最低 Cpk {cpk0:.2f}。

## 2. 吵闹的邻居（宿主机 cl-a2）

超分的风险：同一台宿主机上有个租户没设 CPU 限额，把机器占满。在仿真车间注入“A 区 2 号宿主机被吵闹的邻居占满”（sim/errors.py 的 noisy_nb），
在 cl-a2 上开 6 份订阅：

{L.md_table(["特性", "规格", "份数", "均值", "标准差", "Cpk"], rows1)}

**{bad_parts} 份验收不合格**（服务延迟 p99 平均 {st1['cl_p99']['mean']:.1f} ms）——验收把问题拦在交付前。
下发措施“隔离租户”（isolate_tenant：把占满的租户迁走、加 CPU 限额，和“质量 → 8D”下发措施同一个入口），再开 6 份：

{L.md_table(["特性", "规格", "份数", "均值", "标准差", "Cpk"], rows2)}

不合格 **{fails2}**，延迟回到 {st2['cl_p99']['mean']:.1f} ms。第 5 步“每租户 CPU 限额”就是这条措施的长效版。
"""
case.step("make", f"24 份订阅不合格 {fails0}；注入吵闹的邻居后 cl-a2 上 {bad_parts} / 6 份不合格（p99 {st1['cl_p99']['mean']:.0f} ms）；隔离租户后 0 份。",
          f"24 subscriptions, {fails0} failures; with a noisy neighbour {bad_parts} of 6 on cl-a2 fail (p99 {st1['cl_p99']['mean']:.0f} ms); none after isolating the tenant.",
          md=case.text("7_订阅验收.md", makemd), tools=tools("softops", "planner", "quality"),
          facts=[("不合格", "Failures", fails0, ""), ("最低 Cpk", "Lowest Cpk", round(cpk0, 2), ""), ("故障拦下", "Caught by acceptance", f"{bad_parts}/6", "")])
case.check("make", "24 份订阅不合格", "Failures in 24 subscriptions", fails0, "==", 0, "", "服务验收")
case.check("make", "24 份订阅最低 Cpk", "Lowest Cpk over 24 subscriptions", round(cpk0, 2), ">=", 1.33, "", "常用要求")
case.check("make", "吵闹的邻居：验收拦下的订阅", "Noisy neighbour: subscriptions caught at acceptance", bad_parts, ">", 0, "份", "服务验收")
case.check("make", "隔离租户后不合格", "Failures after isolating the tenant", fails2, "==", 0, "", "纠正措施")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **云的容量先看内存**：CPU 能超分、内存不能，512 GB 时超分白超；配 768 GB 后 1.5 倍超分，可卖从 {orow[0]['subs']:.0f} 份到 {sel['subs']:.0f} 份。
2. **余量是按故障域留的**：每区留一整柜，坏一柜虚拟机有地方重启；网关按“一个区全断”算台数。
3. **平均可用性很好看，违约看坏月份**：单区租户一年平均才停 {down_1az:.0f} 分钟，可一次可用区事故就超一个月的额度——所以 99.9 % 只承诺给跨两区的租户。
4. **超分的代价是吵闹的邻居**：验收能拦下，长效办法是每租户 CPU 限额。

## 留给学生的问题

1. 订阅增长快一倍（上限 800 份），哪个月要向计算机厂下整机柜订单？（交货加上架 2 个月，分配率 75 % 触发。）
2. 网关处理时间从 2 ms 优化到 1.5 ms，能少几台？省多少钱？
3. 电价涨到 0.15 USD/kWh，回本推迟几个月？把机房换成计算机厂案例 C 里 PUE 1.38 的方案呢？

相关：软件公司帮助“云平台”；计算机厂案例 C（20 柜机房）；本厂案例 B（存储）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；1.5 倍超分 + 768 GB，{sel['subs']:.0f} 份可卖，网关 2 × {GW_PER_AZ}，第 {pay_m} 个月回本。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; 1.5× overcommit with 768 GB, {sel['subs']:.0f} sellable, 2 × {GW_PER_AZ} gateways, payback in month {pay_m}.",
          md=case.text("8_总结.md", review), tools=tools("softops", "quality", "energy"))
case.write()
print("ok", round(sel["subs"]), round(subs(36)), round(pack_eff, 4), pack_rej, round(cpu_peak, 3), round(peak_factor, 2), GW_PER_AZ, round(r99_one_az * 1000, 2),
      round(sim_r99 * 1000, 2), round(d_gw, 1), round(down_1az, 2), round(mc1_down, 2), round(mc1_bad, 2), round(mc2_bad, 4), pay_m, fails0, bad_parts, fails2, PUE, RACK_PRICE)
