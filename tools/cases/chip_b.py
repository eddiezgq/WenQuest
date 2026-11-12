"""第 161g 轮：芯片封测厂案例 B——一个数字模块：SSI 绝对值编码器读取（RTL → 逐拍仿真对照参考模型 → 线缆延迟 → 综合）。

    python3 tools/cases/chip_b.py

RTL 和测试平台在 tools/cases/rtl/（wq_ssi.v、tb_ssi.v）；仿真用 Icarus Verilog（芯片设计页同一个工具），综合用 Yosys（pip 的 yowasp-yosys）；
制造用芯片封测厂仿真车间的工程样片路线（老化 + 成品测试）。输出到 factory/cases/chip/B/。
"""
from __future__ import annotations

import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-chip.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402

RTL = HERE / "rtl"
TOOLS = {
    "chip": ("芯片设计（WQ-ENCIF）", "Chip design (WQ-ENCIF)", "/chip-design"),
    "pcb": ("电路板设计：B 版固件", "PCB design: rev-B firmware", "/pcb-design"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731
BITS, HALF, TM, FCLK = 17, 25, 1000, 50e6
F_SSI = FCLK / (2 * HALF)

case = L.Case("chip", "B", "中等", "数字模块：SSI 绝对值编码器读取", "Digital block: SSI absolute-encoder reader", "WQ-SSI（WQ-ENCIF B 版候选模块）",
              "驱动板现在用 MCU 的 SPI 软件读关节输出端的 SSI 编码器；把它做成芯片里的硬件模块：写 RTL，Icarus 逐拍仿真、和 Python 参考模型逐帧对照，"
              "扫线缆延迟找出能用多长的线，发现偶校验抓不住移位错，Yosys 综合看规模；按工程样片路线做一批。",
              "The drive board reads the joint-output SSI encoder with MCU SPI software; this case moves it into hardware on the chip: RTL, cycle-accurate Icarus simulation checked "
              "frame by frame against a Python reference model, a cable-delay sweep to find the usable length (even parity misses shifted frames), Yosys synthesis for size; one engineering-sample lot.",
              "tools/cases/chip_b.py")

# ================================================================ 1 任务书
brief = f"""# 设计任务书：SSI 读取模块

**为什么**　驱动板 B 版的固件用 MCU 的 SPI3 读关节输出端绝对值编码器（SSI，第 107 轮），每次读都占 CPU、还要软件转格雷码、查校验。
芯片厂的 WQ-ENCIF 下一版想把它做成硬件：MCU 只读一个寄存器。

| 项目 | 要求 | 出处 |
|---|---|---|
| 协议 | SSI：主机发时钟串（空闲为高），第一个下降沿编码器锁存位置，之后每个上升沿送一位（高位先）；{BITS} 位格雷码 + 1 位偶校验 | 示例协议（与第 107 轮固件一致的结构） |
| 时钟 | 芯片 {FCLK / 1e6:g} MHz；SSI {F_SSI / 1e6:g} MHz | 芯片时钟；常见 SSI 速率 |
| 帧间 | 等编码器单稳态恢复 {TM / FCLK * 1e6:g} μs | 编码器 |
| 读数率 | ≥ 1 kHz（关节位置环） | 驱动板固件 |
| 线缆 | 关节里约 2 m，留余量 | 机器人关节 |
"""
case.step("brief", f"SSI {BITS} 位格雷码 + 偶校验；芯片 {FCLK / 1e6:g} MHz、SSI {F_SSI / 1e6:g} MHz；帧间 {TM / FCLK * 1e6:g} μs；≥ 1 kHz；线缆 2 m。",
          f"SSI, {BITS}-bit Gray + even parity; {FCLK / 1e6:g} MHz core, {F_SSI / 1e6:g} MHz SSI; {TM / FCLK * 1e6:g} μs between frames; ≥ 1 kHz; 2 m cable.",
          md=case.text("1_任务书.md", brief), tools=tools("pcb"), facts=[("位数", "Bits", BITS, ""), ("SSI 时钟", "SSI clock", F_SSI / 1e6, "MHz")])

# ================================================================ 2 方案
concept = f"""# 方案：状态机 + 移位寄存器

| 部分 | 做法 |
|---|---|
| 状态机 | 空闲 → 移位（发 {BITS + 1} 个时钟、采 {BITS + 1} 位）→ 等待（{TM / FCLK * 1e6:g} μs）→ 空闲 |
| 时钟发生 | 计数器数 {HALF} 拍翻一次：{FCLK / 1e6:g} MHz / {2 * HALF} = {F_SSI / 1e6:g} MHz |
| 采样时刻 | 时钟高电平的最后一拍（编码器在上升沿换数，等了半个周期，数据最稳） |
| 输入同步 | 数据线过两级触发器（编码器和芯片不同时钟，防亚稳态）——代价是采样晚 2 拍 |
| 格雷码 → 二进制 | b[n−1] = g[n−1]，b[i] = b[i+1] ⊕ g[i]：一串异或 |
| 校验 | {BITS + 1} 位全部异或，应为 0 |

RTL：`wq_ssi.v`（参数 BITS、HALF、TM，{sum(1 for _ in (RTL / 'wq_ssi.v').open(encoding='utf-8'))} 行）。
"""
case.raw("wq_ssi.v", (RTL / "wq_ssi.v").read_bytes())
case.raw("tb_ssi.v", (RTL / "tb_ssi.v").read_bytes())
case.step("concept", f"三状态状态机 + {BITS + 1} 位移位寄存器；高电平最后一拍采样；两级同步；格雷码转换与偶校验。",
          f"Three-state FSM + {BITS + 1}-bit shift register; sample in the last cycle of the high phase; two-flop synchroniser; Gray conversion and even parity.",
          md=case.text("2_方案.md", concept), files=[("wq_ssi.v", "RTL（Verilog）", "RTL (Verilog)"), ("tb_ssi.v", "测试平台", "Testbench")], tools=tools("chip"))

# ================================================================ 3 计算：时序预算
t_frame = (BITS + 1) / F_SSI + TM / FCLK
rate = 1 / t_frame
margin = 1 / (2 * F_SSI) - 2 / FCLK - 1 / FCLK          # 半周期 − 同步 2 拍 − 采样拍
V_CABLE = 5e-9                                          # 线缆传播约 5 ns/m（示例）
T_XCVR = 60e-9                                          # 收发器延迟合计（往返，示例）
l_max = (margin - T_XCVR) / (2 * V_CABLE)
calcmd = f"""# 计算：时序预算

- 一帧 = {BITS + 1} 位 / {F_SSI / 1e6:g} MHz + 等待 {TM / FCLK * 1e6:g} μs = **{t_frame * 1e6:.0f} μs** → 最高 {rate / 1000:.1f} 千帧/秒（要求 1 kHz ✓）
- **线缆延迟预算**：编码器在时钟上升沿（编码器那一端）换数；数据回到芯片要经过“时钟去 + 数据回”两趟线缆和收发器。
  芯片在上升沿后半个周期（{1 / (2 * F_SSI) * 1e9:.0f} ns）采样，减去两级同步 + 采样共 3 拍（{3 / FCLK * 1e9:.0f} ns），允许往返延迟约 **{margin * 1e9:.0f} ns**。
- 线缆约 {V_CABLE * 1e9:g} ns/m（示例），收发器往返约 {T_XCVR * 1e9:g} ns（示例）→ 最长约 **{l_max:.0f} m**（关节 2 m 富余很多）。
- 想更快：SSI 提到 4 MHz，预算只剩约 {(1 / (2 * 4e6) - 3 / FCLK) * 1e9:.0f} ns，2 m 线就紧了——这就是长线 SSI 只能低速、或要做延迟补偿的原因。
"""
case.step("calc", f"一帧 {t_frame * 1e6:.0f} μs（{rate / 1000:.1f} 千帧/秒）；往返延迟预算 {margin * 1e9:.0f} ns，约 {l_max:.0f} m 线缆。",
          f"{t_frame * 1e6:.0f} μs per frame ({rate / 1000:.1f} k frames/s); {margin * 1e9:.0f} ns round-trip budget, about {l_max:.0f} m of cable.",
          md=case.text("3_时序预算.md", calcmd), facts=[("帧率", "Frame rate", round(rate / 1000, 1), "kHz"), ("延迟预算", "Delay budget", round(margin * 1e9), "ns")])
case.check("calc", "最高帧率", "Maximum frame rate", round(rate / 1000, 1), ">=", 1.0, "kHz", "任务书")


# ================================================================ 4 仿真：Icarus 逐拍 + Python 参考模型
def g2b(g):
    b = g
    s = g >> 1
    while s:
        b ^= s
        s >>= 1
    return b


def model(p):
    """参考模型：编码器送出 gray(p) + 偶校验位；正确读回应是 p、校验 0"""
    g = p ^ (p >> 1)
    return g2b(g), 0


def sim(positions, delay_ns):
    with tempfile.TemporaryDirectory() as d:
        hx = Path(d) / "pos.hex"
        hx.write_text("".join(f"{p:x}\n" for p in positions))
        vvp = Path(d) / "s.vvp"
        subprocess.run(["iverilog", "-g2012", f"-Ptb.DELAY_NS={delay_ns}", f"-Ptb.NPOS={len(positions)}", "-o", str(vvp), str(RTL / "tb_ssi.v"), str(RTL / "wq_ssi.v")], check=True)
        out = subprocess.run(["vvp", "-n", str(vvp), f"+pos={hx}"], capture_output=True, text=True, check=True).stdout
    fr = [tuple(int(x) for x in m.groups()) for m in re.finditer(r"FRAME (\d+) (\d+) (\d+) (\d+)", out)]
    return fr


rnd = random.Random(1632)
POS = [0, 1, 2 ** BITS - 1, 2 ** (BITS - 1), 0x0AAAA, 0x15555] + [rnd.randrange(2 ** BITS) for _ in range(58)]
fr0 = sim(POS, 0)
ok0 = sum(1 for i, p, r, pe in fr0 if (r, pe) == model(p))
iv_ver = subprocess.run(["iverilog", "-V"], capture_output=True, text=True).stdout.splitlines()[0]
delays = list(range(0, 801, 50))
res = []
for dl in delays:
    f_ = sim(POS[:24], dl)
    good = sum(1 for i, p, r, pe in f_ if r == p and pe == 0)
    bad = [x for x in f_ if x[2] != x[1]]
    caught = sum(1 for x in bad if x[3] == 1)
    res.append((dl, good / len(f_) * 100, len(bad), caught))
d_ok = max(dl for dl, g, nb, c in res if g == 100)
d_fail = min(dl for dl, g, nb, c in res if g < 100)
miss = sum(nb - c for dl, g, nb, c in res)
bad_all = sum(nb for dl, g, nb, c in res)
fig, ax = plt.subplots(figsize=(8, 3.0))
ax.plot([r[0] for r in res], [r[1] for r in res], "o-", color=L.ACCENT, label="读对的帧 %")
ax.plot([r[0] for r in res], [(r[3] / r[2] * 100) if r[2] else np.nan for r in res], "s--", color=L.BAD, label="错帧里被校验抓住的 %")
ax.axvline(margin * 1e9, color=L.MUTED, ls=":", lw=1)
ax.text(margin * 1e9 + 8, 50, f"预算 {margin * 1e9:.0f} ns", fontsize=8, color=L.MUTED)
ax.set_xlabel("线缆往返延迟 / ns")
ax.set_ylabel("%")
ax.legend(fontsize=8)
case.fig(fig, "4_线缆延迟.png")
simmd = f"""# 仿真：Icarus Verilog 逐拍 + Python 参考模型

测试平台 `tb_ssi.v`：编码器（SSI 从机）行为模型 + 一段可调的线缆往返延迟；Python 生成位置、跑 {iv_ver.split('(')[0].strip()}、逐帧和参考模型比。

## 功能：{len(POS)} 个位置（含 0、1、全 1、最高位、交替位和随机），延迟 0

读对 **{ok0} / {len(fr0)}** 帧，校验错 0。

## 线缆延迟扫描（每档 24 帧）

{L.md_table(["往返延迟 ns", "读对 %", "错帧", "其中校验抓住"], [[dl, f"{g:.0f}", nb, c] for dl, g, nb, c in res])}

- 延迟到 **{d_ok} ns** 全对，{d_fail} ns 开始出错——和第 3 步预算的 {margin * 1e9:.0f} ns 吻合（仿真步长 50 ns）。
- **偶校验抓不住移位错**：延迟超了以后，每一位都晚采一位，整帧错位；{bad_all} 个错帧里有 {miss} 个校验照样“通过”——
  错位的数据里 1 的个数是偶数的概率约一半。所以光靠校验不行：**要么保证时序预算，要么连读两次比对、或者加循环冗余校验（CRC）**。
"""
case.step("sim", f"{ok0} / {len(fr0)} 帧与参考模型一致；延迟 ≤ {d_ok} ns 全对、{d_fail} ns 起出错；{bad_all} 个错帧里 {miss} 个校验没抓住。",
          f"{ok0} / {len(fr0)} frames match the reference model; all correct up to {d_ok} ns delay, errors from {d_fail} ns; {miss} of {bad_all} bad frames slip past the parity check.",
          md=case.text("4_逐拍仿真.md", simmd), figs=[("4_线缆延迟.png", "线缆往返延迟扫描", "Cable round-trip delay sweep")], tools=tools("chip"),
          facts=[("对照参考模型", "Frames vs model", f"{ok0}/{len(fr0)}", ""), ("实测延迟上限", "Delay limit (simulated)", d_ok, "ns")])
case.check("sim", "与参考模型一致的帧", "Frames matching the reference model", ok0, "==", len(fr0), "", "逐帧对照")
case.check("sim", "仿真延迟上限与预算相差", "Simulated delay limit vs budget", abs(d_ok - margin * 1e9), "<=", 50, "ns", "仿真步长 50 ns")

# ================================================================ 5 综合
with tempfile.TemporaryDirectory() as d:
    log = subprocess.run(["yowasp-yosys", "-p", f"read_verilog {RTL / 'wq_ssi.v'}; synth -top wq_ssi -noabc; stat"], capture_output=True, text=True, cwd=d).stdout
cells = {m.group(2): int(m.group(1)) for m in re.finditer(r"^\s+(\d+)\s+\$_(\w+)_\s*$", log, re.M)}
n_ff = sum(v for k, v in cells.items() if k.startswith("DFF"))
n_gate = sum(v for k, v in cells.items() if not k.startswith("DFF"))
ver = re.search(r"Yosys [\d.]+", log).group(0)
enc = json.loads((ROOT / "factory" / "designs" / "wq-encif" / "out" / "design.json").read_text(encoding="utf-8"))
std = enc["layout"].get("stdcells")
cadmd = f"""# 综合（{ver}，通用门级）

{L.md_table(["单元", "个数"], [[k, v] for k, v in sorted(cells.items())])}

合计触发器 **{n_ff}**（{BITS + 1} 位移位寄存器、{BITS} 位位置输出、计数器、状态、同步器），组合门 {n_gate}。
现在的 WQ-ENCIF 用 SKY130 标准单元 {std} 个（芯片厂案例 C）——加上这个模块大约多四分之一的逻辑，芯片面积还是由焊盘决定，不用改封装。

（本机综合到通用门；接到 SKY130 标准单元、布局布线要进芯片工作流 `chip.yml` 跑 LibreLane，和 WQ-ENCIF 一样。）
"""
case.raw("综合统计.txt", log[log.find("Printing statistics"):][:2000].encode())
case.step("cad", f"Yosys 综合：触发器 {n_ff}、组合门 {n_gate}；约为现有 WQ-ENCIF 逻辑的四分之一。",
          f"Yosys synthesis: {n_ff} flip-flops, {n_gate} gates; about a quarter of the present WQ-ENCIF logic.",
          md=case.text("5_综合.md", cadmd), files=[("综合统计.txt", "综合统计", "Synthesis statistics")], tools=tools("chip"), facts=[("触发器", "Flip-flops", n_ff, ""), ("组合门", "Gates", n_gate, "")])

# ================================================================ 6 工艺：从 RTL 到样片
from factory import data as F  # noqa: E402

rt = F.ROUTINGS[F.BOMS["WQ-ENCIF-ES"][0]]
procmd = f"""# 工艺：从 RTL 到工程样片

1. 并进 WQ-ENCIF 的 RTL（加寄存器：位置、状态、SSI 速率），回归原有 9 个仿真场景 + 本模块的场景；
2. 芯片工作流跑 LibreLane：综合到 SKY130、布局布线、时序、设计规则、版图与原理图一致性（LVS）；
3. 外协代工流片（晶圆，几个月）；
4. 芯片封测厂：晶圆测试 → 按**工程样片路线**封装（比量产多一道老化，托盘装）：

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt)])}

5. 成品测试加一组 SSI 测试向量：测试机模拟编码器，送本案例仿真里的那些位置，比对读回值（测试平台就是测试向量的来源）。
"""
case.step("process", f"并进 RTL → LibreLane → 流片 → 晶圆测试 → 工程样片路线 {len(rt)} 道（含老化）→ 成品测试加 SSI 向量。",
          f"Merge RTL → LibreLane → tape-out → wafer probe → {len(rt)}-step engineering-sample route (with burn-in) → SSI vectors at final test.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer", "chip"))

# ================================================================ 7 制造：一批工程样片
sh = L.run_shop("WQ-ENCIF-ES", 1, "WO-CASE-CHIP-B", seed=1633)
rows_q, cpk_min, fails, st = L.shop_table([m for m in sh["measurements"] if m["item"] == "WQ-ENCIF-ES"])
makemd = f"""# 制造：一批工程样片（一片晶圆）

芯片封测厂仿真车间按工程样片路线走一批（{sh['hours']:.0f} 小时，键合、老化最长）。成品测试（一批记一条：抽检值、良率、中位数）：

{L.md_table(["特性", "公差", "这一批"], [[r[0], r[1], r[3]] for r in rows_q])}

不合格 {fails}。（一批只有一条记录，算不了 Cpk；量产后按批积累。）真正的 SSI 功能要等这一版流片后才能在样片上测——现在的样片是现有 WQ-ENCIF，这一步演示路线和测试项。
"""
case.step("make", f"工程样片一批（{sh['hours']:.0f} 小时），成品测试不合格 {fails}；本模块要等新一版流片后在样片上测。",
          f"One engineering-sample lot ({sh['hours']:.0f} h), {fails} final-test failures; this block is tested on samples once the new revision is taped out.",
          md=case.text("7_工程样片.md", makemd), tools=tools("planner", "operator", "quality"), facts=[("不合格", "Out of tolerance", fails, "")])
case.check("make", "工程样片成品测试不合格", "Engineering-sample final-test failures", fails, "==", 0, "", "成品测试")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **硬件模块 = 状态机 + 计数器 + 移位寄存器**：{n_ff} 个触发器就把 MCU 软件做的事搬进了芯片。
2. **仿真要有参考模型**：Python 写一份“应该是什么”，逐帧对照，才知道 RTL 对不对。
3. **时序预算先算、再仿真验证**：{margin * 1e9:.0f} ns 的预算和仿真的 {d_ok} ns 对上；超了以后错得悄无声息——**偶校验抓不住移位**。

## 留给学生的问题

1. 把 HALF 改成 6（约 4 MHz），重跑仿真：延迟上限变成多少？
2. 给模块加“连读两次比对”：两次不一样就报错。要多少触发器？
3. 编码器换成 CRC-6 校验，状态机要改哪里？

相关：数字工厂“芯片设计”；驱动板 B 版固件 SSI（第 107 轮）；案例 A（施密特）、C（WQ-ENCIF 整颗）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；{n_ff} 个触发器，延迟上限 {d_ok} ns。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; {n_ff} flip-flops, delay limit {d_ok} ns.", md=case.text("8_总结.md", review), tools=tools("chip"))
case.write()
print("ok", ok0, len(fr0), res, d_ok, margin, n_ff, n_gate, cells, fails)
