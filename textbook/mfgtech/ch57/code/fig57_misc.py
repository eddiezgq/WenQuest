"""第 57 章的示意图与表格（数据取自 std/SH-101_process.yaml、SH-101_part.yaml）：
图 57.0.1 路线与工艺规程的差别、57.1.1 工序余量与总余量、57.1.5 确定余量的三种方法、57.2.3 入体原则、57.2.4 磨削余量与磨削时间、
57.3.3 SH-101 的轴向尺寸与跟踪图的面、57.4.1 各工序的设备与工装、57.4.3 选机床与工装的考虑、57.4.4 检验用量具、
57.5.1 确定切削用量的次序、57.6.3 时间定额的组成、57.6.4 SH-101 的时间定额表、57.6.5 产能与年产量、57.7.2 工艺成本的组成、
57.9.1 评审、试切与发布的流程、57.10.1 两种 CAPP、57.10.2 AI 工艺评审员的规则、57.10.3 评审员能做与不能做的。"""
import math

import _mfg as M
from bookout import T, figure, out, style

P = M.plan101()
PART = M.part101()
RT = M.route()
plt = style()
INK, MU = M.INK, M.MUTED


def box(ax, x, y, w, h, t, c=M.ACCENT, fs=7, a=0.13):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=c, alpha=a, ec=c, lw=0.9))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs)


def arrow(ax, p, q, c=INK, lw=0.8):
    ax.annotate("", q, p, arrowprops={"arrowstyle": "->", "lw": lw, "color": c})


# ---- 图 57.0.1：路线与工艺规程
rows = [[T("工序、顺序、工作中心", "ops, order, machines"), T("有", "yes"), T("有", "yes")],
        [T("定位基准、热处理与辅助工序", "datums, heat, aux"), T("有", "yes"), T("有，并画在工序简图上", "yes, on the sketch")],
        [T("各道的工序尺寸与公差", "op sizes & tolerances"), T("只有主要外圆，凭经验", "main diameters only"), T("每个面都有：由余量推算，轴向用跟踪图", "every surface, calculated")],
        [T("切削用量（ap、f、vc、n）", "cutting data"), T("没有", "no"), T("每个工步都有，并校核功率、粗糙度、刀具寿命", "every step, checked")],
        [T("工步、刀具、量具", "steps, tools, gauges"), T("没有", "no"), T("工步表、刀具卡、检验卡", "step list, tool & inspection cards")],
        [T("时间定额", "time standards"), T("粗估（每道一个数）", "rough guess"), T("机动 + 辅助 + 布置休息 + 准备终结，核算产能", "calculated")],
        [T("车间拿到的文件", "documents"), T("ERP 里的工序表", "ERP routing"), T("过程卡、工序卡、检验卡、刀具卡", "full card set")]]
M.table_fig(plt, [T("内容", "content"), T("第 56 章的工艺路线", "Ch. 56 route"), T("第 57 章的工艺规程", "Ch. 57 process plan")], rows,
            [0.28, 0.3, 0.42], "fig57_0_1", fontsize=7, width_in=6.6)

# ---- 图 57.1.1：工序余量与总余量（外圆，上半剖面；各层厚度放大画出，不按比例）
fig, ax = plt.subplots(figsize=(6.4, 2.4))
ds = [(30, T("棒料 Ø60", "bar Ø60")), (20, T("粗车 A₁ = Ø26.5", "rough Ø26.5")), (15.5, T("半精车 A₂ = Ø25.4", "semi Ø25.4")), (12, T("磨削 Ø25 k6", "ground Ø25 k6"))]
cols = [MU, "#8aa4bd", M.ACCENT, M.WARM]
for i, (r, lab) in enumerate(ds):
    ax.add_patch(plt.Rectangle((0, 0), 12 - i * 0.0, r, fc=cols[i], alpha=0.35 + 0.12 * i, ec=INK, lw=0.5))
    ax.text(12.4, r - 0.8, lab, va="top", fontsize=6.8)
for (a, b, lab, x) in ((30, 20, T("粗车余量 Z₁", "Z₁ rough"), 6), (20, 15.5, T("半精车余量 Z₂", "Z₂ semi"), 6), (15.5, 12, T("磨削余量 Z₃", "Z₃ grind"), 6)):
    ax.annotate("", (x, a), (x, b), arrowprops={"arrowstyle": "<->", "lw": 0.7})
    ax.text(x + 0.3, (a + b) / 2, lab, fontsize=6.6, va="center")
ax.annotate("", (24, 30), (24, 12), arrowprops={"arrowstyle": "<->", "lw": 0.9, "color": M.RED})
ax.text(24.4, 21, T("总余量 Z = Z₁ + Z₂ + Z₃\n（直径上为 2Z）", "total Z (2Z on diameter)"), fontsize=6.8, color=M.RED, va="center")
ax.plot([-1, 34], [0, 0], color=INK, lw=0.5, ls=(0, (8, 2, 1, 2)))
ax.text(0, -2.2, T("轴线（上半剖面；各层厚度放大画出，不按比例）", "axis (upper half; not to scale)"), fontsize=6.3, color=MU)
ax.set_xlim(-1, 36); ax.set_ylim(-4, 32); ax.axis("off")
figure(fig, "fig57_1_1")

# ---- 图 57.1.5：确定余量的三种方法
rows = [[T("经验估计法", "experience"), T("工艺员凭经验", "planner's judgement"), T("单件小批；为保险常偏大", "one-off, small batch")],
        [T("查表修正法", "tables"), T("工艺手册的余量表，按实际修正", "handbook tables, corrected"), T("工厂里最常用", "most common")],
        [T("分析计算法", "analysis"), T("按式 (57.1.3) 逐项算 Rz、Hₐ、ρ、ε", "Eq. (57.1.3) term by term"), T("大批大量、贵重材料、重要零件；要可靠的数据", "large volume, costly parts")]]
M.table_fig(plt, [T("方法", "method"), T("怎样定", "how"), T("用在哪里", "where")], rows, [0.2, 0.42, 0.38], "fig57_1_5", fontsize=7, width_in=6.4)

# ---- 图 57.2.3：入体原则
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.4, 2.0))
for ax, kind in ((a1, "shaft"), (a2, "hole")):
    ax.add_patch(plt.Rectangle((0, 0), 4, 1, fc=MU, alpha=0.25, ec=INK, lw=0.6))
    ax.plot([0, 4], [1, 1], color=INK, lw=1.0)
    if kind == "shaft":
        ax.add_patch(plt.Rectangle((1.2, 0.72), 1.6, 0.28, fc=M.ACCENT, alpha=0.6))
        ax.text(2, 1.18, T("外圆：A₀⁻ᵀ（上偏差 0，公差向体内）", "shaft: upper deviation 0"), ha="center", fontsize=6.8)
        ax.text(2, 0.35, T("材料（工件）", "material"), ha="center", fontsize=6.5, color=MU)
    else:
        ax.add_patch(plt.Rectangle((1.2, 1.0), 1.6, 0.28, fc=M.WARM, alpha=0.6))
        ax.text(2, 1.48, T("孔：A₀⁺ᵀ（下偏差 0，公差向体内）", "hole: lower deviation 0"), ha="center", fontsize=6.8)
        ax.text(2, 0.35, T("材料（孔壁）", "material"), ha="center", fontsize=6.5, color=MU)
    ax.text(4.1, 1.0, T("公称尺寸", "nominal"), fontsize=6.3, va="center")
    ax.set_xlim(-0.2, 5.2); ax.set_ylim(0, 1.7); ax.axis("off")
figure(fig, "fig57_2_3")

# ---- 图 57.2.4：磨削余量与磨削时间（SH-101 轴承位，粗磨横进给 0.002 mm/行程，精磨留 0.04、横进给 0.0015 + 光磨 2）
g = next(o for o in P["operations"] if o["seq"] == 70)["grinding"]
fig, ax = plt.subplots(figsize=(5.6, 2.4))
zs = [0.1 + 0.02 * i for i in range(26)]
t_pass = 0.035                                         # 一个行程的时间（min，示意：轴承位长 17、工作台速度按纵磨）
fin = 0.04
tt = [((z - fin) / 2 / g["passes"][0]["ap"] + fin / 2 / g["passes"][1]["ap"] + 2) * t_pass for z in zs]
ax.plot(zs, tt, color=M.ACCENT, lw=1.4)
ax.axvspan(0.335, 0.398, color=M.GREEN, alpha=0.15); ax.text(0.366, max(tt) * 0.92, T("SH-101\n0.335–0.398", "SH-101"), ha="center", fontsize=6.8, color=M.GREEN)
ax.axvspan(0.1, 0.3, color=M.RED, alpha=0.06); ax.text(0.2, max(tt) * 0.55, T("太小：磨不掉\n热处理变形与氧化层", "too small"), ha="center", fontsize=6.6, color=M.RED)
ax.text(0.52, max(tt) * 0.35, T("太大：工时长，\n磨掉硬化层、易烧伤", "too large"), ha="center", fontsize=6.6, color=M.WARM)
ax.set_xlabel(T("磨削余量（直径上）/ mm", "grinding stock on diameter / mm")); ax.set_ylabel(T("一处轴承位的磨削时间 / min（示意）", "grinding time / min (illustr.)"))
ax.grid(lw=0.3, alpha=0.4)
figure(fig, "fig57_2_4")

# ---- 图 57.3.3：SH-101 的轴向尺寸与跟踪图上的面
fig, ax = plt.subplots(figsize=(7.0, 2.3))
x = 0
for d, L, n in PART["part"]["segments"]:
    ax.add_patch(plt.Rectangle((x, -d / 2), L, d, fc="#f6ead9", ec=INK, lw=0.7))
    x += L
xs = {"L": 0, "S1": 36, "S2": 56, "S3": 73, "S4": 81, "S5": 111, "S6": 119, "R": 136}
for k, xv in xs.items():
    ax.text(xv, 30, k, ha="center", fontsize=7, color=M.ACCENT)
    ax.plot([xv, xv], [27.5, 26], color=M.ACCENT, lw=0.6)
for a, b, t, yy in (("L", "S1", "36", -33), ("S1", "S2", "20", -33), ("S2", "S3", "17", -33), ("S3", "S4", "8 ± 0.1", -40), ("S4", "S5", "30", -33),
                    ("S5", "S6", "8", -33), ("L", "R", "136", -48)):
    ax.annotate("", (xs[a], yy), (xs[b], yy), arrowprops={"arrowstyle": "<->", "lw": 0.6, "color": M.RED if "±" in t else INK})
    ax.text((xs[a] + xs[b]) / 2 + (12 if "±" in t else 0), yy + 1.2 if "±" not in t else yy - 1.4, t, ha="center", fontsize=6.6, color=M.RED if "±" in t else INK)
ax.plot([-5, 141], [0, 0], color=INK, lw=0.4, ls=(0, (8, 2, 1, 2)))
ax.set_xlim(-6, 142); ax.set_ylim(-50, 34); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig57_3_3")

# ---- 图 57.4.1：各工序的设备与工装（取自工艺规程）
rows = []
for o in P["operations"]:
    rows.append([str(o["seq"]), o["operation"].split(" ")[0], o["workstation"], o.get("fixture") or o.get("clamping") or "—",
                 "、".join(t["id"] for t in P["tool_list"] if o["seq"] in t["ops"]) or "—"])
M.table_fig(plt, [T("工序", "op"), T("名称", "name"), T("设备", "machine"), T("夹具", "fixture"), T("刀具（刀具卡）", "tools")], rows,
            [0.07, 0.11, 0.2, 0.47, 0.15], "fig57_4_1", fontsize=6.8)

# ---- 图 57.4.3：选机床与工装要考虑的
rows = [[T("规格", "size"), T("加工范围（最大回转直径、中心距、模数）与零件相配", "work envelope fits the part")],
        [T("精度", "accuracy"), T("机床精度与工序公差相适应：粗加工用精度一般、刚度好的，精加工用精度高的", "machine accuracy fits the op")],
        [T("生产率", "productivity"), T("按批量：大批用数控、专用或复合设备，小批用通用设备", "by volume")],
        [T("现有条件", "what we have"), T("优先用工厂现有设备；新购要做技术经济分析（57.7 节）", "existing first")],
        [T("工装", "tooling"), T("通用夹具、可调夹具、专用夹具；刀具按材料与工序；量具的精度约为公差的 1/10–1/5", "fixtures, tools, gauges")]]
M.table_fig(plt, [T("考虑", "factor"), T("要点", "notes")], rows, [0.16, 0.84], "fig57_4_3", fontsize=7, width_in=6.6)

# ---- 图 57.4.4：检验用量具（与公差相配）
rows = [[c["id"], c["name"], c.get("spec", "")[:28], next((i["gauge"] for o in P["operations"] if o.get("final_inspection") for i in o["inspect"] if i["char"] == c["id"]), "")]
        for c in P["characteristics"][:9]]
gmap = {g["id"]: g["name"] for g in P["gauges"]}
rows = [r[:3] + [gmap.get(r[3], r[3])] for r in rows]
M.table_fig(plt, [T("特性", "char"), T("名称", "name"), T("要求", "spec"), T("量检具", "gauge")], rows, [0.07, 0.27, 0.33, 0.33], "fig57_4_4", fontsize=6.6)

# ---- 图 57.5.1：确定切削用量的次序
fig, ax = plt.subplots(figsize=(6.8, 1.7))
steps = [(T("背吃刀量 ap\n按余量，尽量一刀", "ap: by stock"), M.ACCENT), (T("进给量 f\n粗加工按力与功率\n精加工按 Ra", "f: force / Ra"), M.WARM),
         (T("切削速度 vc\n按刀具寿命", "vc: tool life"), M.RED), (T("校核\n功率、刚度、\nRa、寿命", "check"), M.GREEN), (T("算 n、t_b\n写进工序卡", "n, t_b to card"), MU)]
for i, (t, c) in enumerate(steps):
    box(ax, i * 1.35, 0.2, 1.15, 1.0, t, c=c, fs=6.6)
    if i:
        arrow(ax, (i * 1.35 - 0.2, 0.7), (i * 1.35, 0.7))
ax.set_xlim(-0.1, 6.8); ax.set_ylim(0, 1.4); ax.axis("off")
figure(fig, "fig57_5_1")

# ---- 图 57.6.3：时间定额的组成
fig, ax = plt.subplots(figsize=(6.6, 1.9))
parts = [(T("机动时间 t_b", "machining t_b"), 4.7, M.ACCENT), (T("辅助时间 t_a", "handling t_a"), 2.9, M.WARM),
         (T("布置工作地 α、休息与生理 β", "servicing α, rest β"), 0.61, MU)]
x = 0
for lab, w, c in parts:
    ax.barh(1, w, left=x, color=c, height=0.45)
    ax.text(x + w / 2 if w > 1 else x + w, 1.38 if w > 1 else 1.62, lab, ha="center" if w > 1 else "right", fontsize=6.4)
    x += w
ax.annotate("", (0, 0.55), (4.7 + 2.9, 0.55), arrowprops={"arrowstyle": "<->", "lw": 0.6})
ax.text(3.8, 0.38, T("作业时间 t_b + t_a", "operating time"), ha="center", fontsize=6.6)
ax.annotate("", (0, 0.15), (x, 0.15), arrowprops={"arrowstyle": "<->", "lw": 0.6, "color": M.RED})
ax.text(x / 2, -0.03, T("单件时间 t_d = (t_b + t_a)(1 + (α + β)/100)；单件计算时间 t_c = t_d + T_z/n", "t_d and t_c"), ha="center", fontsize=6.6, color=M.RED)
ax.set_xlim(-0.2, 8.6); ax.set_ylim(-0.25, 1.8); ax.axis("off")
figure(fig, "fig57_6_3")

# ---- 图 57.6.5：产能与年产量
cost = RT.route_cost(P["operations"], P["batch"])
fig, ax = plt.subplots(figsize=(5.6, 2.4))
Ns = [2000 + 500 * i for i in range(57)]
ax.plot([n / 1000 for n in Ns], [M.FE_MIN / n for n in Ns], color=M.RED, lw=1.3, label=T("需求节拍 Fe/N", "demand takt"))
for k, v in sorted(cost["load"].items(), key=lambda kv: -kv[1])[:2]:
    ax.axhline(v, lw=1.0, color={0: M.ACCENT}.get(0) if k.startswith("外圆") else MU, ls="-" if k.startswith("外圆") else "--")
    ax.text(29.5, v + 0.4, k.split(" ")[0] + f" {v:.1f}", fontsize=6.6, ha="right")
cap = M.FE_MIN / cost["takt"]
ax.axvline(cap / 1000, color=M.ACCENT, ls=":", lw=0.8); ax.text(cap / 1000 + 0.3, 30, T(f"产能约 {cap:.0f} 件/年", f"capacity ≈ {cap:.0f}/yr"), fontsize=6.8, color=M.ACCENT)
ax.set_ylim(0, 40); ax.set_xlim(2, 30)
ax.set_xlabel(T("年产量 / 千件", "annual volume / 1000")); ax.set_ylabel(T("min / 件", "min per part")); ax.legend(fontsize=7, loc="upper right"); ax.grid(lw=0.3, alpha=0.4)
figure(fig, "fig57_6_5")

# ---- 图 57.7.2：工艺成本的组成
rows = [[T("可变费用 V（元/件）", "variable V"), T("材料、生产工人工资、机床的电费与维护、通用工装与刀具的折旧和刃磨", "material, wages, power, tools")],
        [T("不变费用 S（元/年）", "fixed S"), T("专用机床、专用夹具、模具的折旧与维护，调整工人工资（不随产量变）", "special equipment, dies")],
        [T("年工艺成本", "annual cost"), T("E = V·N + S", "E = V·N + S")],
        [T("单件工艺成本", "unit cost"), T("C = V + S/N：产量越大，不变费用摊得越薄", "C = V + S/N")]]
M.table_fig(plt, [T("项", "item"), T("内容", "content")], rows, [0.24, 0.76], "fig57_7_2", fontsize=7, width_in=6.4)

# ---- 图 57.9.1：评审、试切与发布
fig, ax = plt.subplots(figsize=(7.0, 1.9))
st = [(T("编写\n工艺规程", "write"), M.ACCENT), (T("AI 预检\n逐条处理意见", "AI pre-check"), M.WARM), (T("提交\n待审", "submit"), MU),
      (T("老师/审批人\n批准", "approve"), M.GREEN), (T("生效\n新版本", "release"), M.GREEN), (T("首件试切\n首件检验", "first article"), M.RED), (T("批量生产\n质量反馈", "production"), M.ACCENT)]
for i, (t, c) in enumerate(st):
    box(ax, i * 1.0, 0.45, 0.85, 0.8, t, c=c, fs=6.3)
    if i:
        arrow(ax, (i * 1.0 - 0.15, 0.85), (i * 1.0, 0.85))
ax.annotate("", (1.42, 0.42), (5.42, 0.42), arrowprops={"arrowstyle": "->", "lw": 0.7, "color": M.RED, "connectionstyle": "arc3,rad=-0.25"})
ax.text(3.4, 0.05, T("首件不合格、或现场发现问题：工艺更改单 → 改工艺规程 → 再评审", "change request loops back"), ha="center", fontsize=6.4, color=M.RED)
ax.set_xlim(-0.1, 7.0); ax.set_ylim(-0.05, 1.4); ax.axis("off")
figure(fig, "fig57_9_1")

# ---- 图 57.10.1：两种 CAPP
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.3))
for ax, title, chain in ((a1, T("派生式（变异式）", "variant"), [T("零件编码\n（成组分类）", "part code"), T("检索零件族的\n标准工艺", "family plan"), T("修改\n得到新工艺", "edit")]),
                         (a2, T("创成式", "generative"), [T("零件特征\n与要求", "features"), T("决策规则\n（方法、顺序、\n设备、用量）", "rules"), T("自动生成\n工艺", "generate")])):
    for i, t in enumerate(chain):
        box(ax, 0.15, 2.0 - i * 0.85, 1.7, 0.65, t, c=M.ACCENT if ax is a1 else M.WARM, fs=6.6)
        if i:
            arrow(ax, (1.0, 2.0 - (i - 1) * 0.85), (1.0, 2.0 - i * 0.85 + 0.65))
    ax.text(1.0, 2.85, title, ha="center", fontsize=7.5)
    ax.set_xlim(0, 2.0); ax.set_ylim(0.1, 3.0); ax.axis("off")
figure(fig, "fig57_10_1")

# ---- 图 57.10.2：AI 工艺评审员的规则（数字工厂 hub/process.py，按本书各章）
rows = [[T("完整、工序与设备", "completeness"), T("第 50 章", "Ch. 50"), T("工序表、工作中心、工序内容、计算书", "")],
        [T("顺序、基准", "order, datums"), T("第 50、56 章", "Ch. 50, 56"), T("先粗后精、热处理位置、粗基准、基准统一", "")],
        [T("精度、余量", "accuracy, stock"), T("第 50、57 章", "Ch. 50, 57"), T("经济精度、末道尺寸与 Ra、相邻工序余量", "")],
        [T("切削用量、工时", "cutting, time"), T("第 57 章", "Ch. 57"), T("功率、基本时间、工步时间与单件工时、产能与需求节拍", "")],
        [T("定位误差、夹具", "locating, fixtures"), T("第 51、52 章", "Ch. 51, 52"), T("V 形块等定位误差、夹紧力、夹具精度预算", "")],
        [T("尺寸链、跟踪图", "chains"), T("第 53 章", "Ch. 53"), T("键槽深等尺寸链、轴向跟踪图的图纸尺寸与余量", "")],
        [T("精度预算、表面", "budget, surface"), T("第 54、55 章", "Ch. 54, 55"), T("系统与随机误差合成、磨削烧伤与粗糙度", "")],
        [T("路线、工序设计", "route, op design"), T("第 56、57 章", "Ch. 56, 57"), T("毛坯、方案链、渗碳件顺序、去毛刺清洗；入体标注", "")]]
M.table_fig(plt, [T("规则组", "rule group"), T("出自", "from"), T("查什么", "what")], rows, [0.22, 0.16, 0.62], "fig57_10_2", fontsize=6.8, width_in=6.6)

# ---- 图 57.10.3：能做与不能做
rows = [[T("能做", "can"), T("按写成规则的标准逐条核算：经济精度、余量、功率、尺寸链、定位误差、烧伤……把意见写成批注，给建议分", "rule-based checks")],
        [T("不能做", "cannot"), T("判断方案是否最好；知道车间设备的实际状态、订单的变化；为没见过的零件想新工艺；替人签字负责", "judgement, accountability")],
        [T("怎样用", "how to use"), T("没意见 ≠ 没问题；有意见 ≠ 一定照改（写明理由可保留）；规则依据的数据要注明出处、定期核对", "use with care")]]
M.table_fig(plt, [T("", ""), T("AI 工艺评审员", "AI reviewer")], rows, [0.14, 0.86], "fig57_10_3", fontsize=7, width_in=6.4)

# ---- 图 57.2.5：SH-301（调质，铣键槽后磨）与 SH-101（渗碳淬火后磨）磨削的最小余量
import _calc57 as C57
z301 = C57.zmin(0.0125, 0.03, 0.03)                      # 第 50 章底稿的企业标准：精车后铣键槽（Rz、Hₐ、ρ）
z101 = C57.zmin(*C57.WQ_PS_01["半精车后渗碳淬火"][:3])
fig, ax = plt.subplots(figsize=(5.2, 1.8))
ax.barh([1, 0], [z301, z101], color=[MU, M.ACCENT], height=0.5)
ax.set_yticks([1, 0]); ax.set_yticklabels([T("SH-301 调质，精车后铣键槽", "SH-301 Q&T"), T("SH-101 半精车后渗碳淬火", "SH-101 carburized")], fontsize=7)
for y, z in ((1, z301), (0, z101)):
    ax.text(z + 0.005, y, f"{z:.3f} mm", va="center", fontsize=7)
ax.set_xlim(0, 0.42); ax.set_xlabel(T("磨削的最小余量（直径上）/ mm", "min grinding stock / mm")); ax.grid(lw=0.3, alpha=0.4, axis="x")
figure(fig, "fig57_2_5")

# ---- 图 57.8.7：工序简图的画法
rows = [[T("画什么", "what"), T("本工序结束时的形状；加工面用粗实线，其余细实线", "state after the op; machined surfaces bold")],
        [T("标什么", "dimensions"), T("本工序的工序尺寸、公差和粗糙度；不标图纸尺寸里与本工序无关的", "this op's sizes, tolerances, Ra")],
        [T("定位夹紧", "locating"), T("GB/T 24740 的定位、夹紧符号，旁注限制的自由度数", "GB/T 24740 symbols with DOF")],
        [T("方位", "orientation"), T("按工件在机床上的装夹位置画", "as held on the machine")],
        [T("数字工厂", "digital factory"), T("hub/sketch.py 按工艺规程的 sketch 字段自动画，与工序卡同一份数据", "drawn from the plan data")]]
M.table_fig(plt, [T("要点", "item"), T("做法", "how")], rows, [0.18, 0.82], "fig57_8_7", fontsize=7, width_in=6.4)

out(z301=z301, z101=z101, t_pass=t_pass, cap=cap, neck=cost["bottleneck"].split(" ")[0])
