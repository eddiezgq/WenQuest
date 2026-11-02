"""第 56 章的示意图与表格（数据取自 std/SH-101_part.yaml、SH-101_route.yaml、SH-301_process.yaml 和 route_methods.yaml）：
图 56.1.3 原始资料、56.2.5 工艺审查意见单、56.2.6 SH-101 与 SH-301 的对比、56.3.4 选择毛坯要考虑的因素、56.4.1 基准重合与不重合、56.4.4 互为基准、
56.4.5 自为基准、56.5.1 粗基准的选择原则、56.6.2 孔、平面、齿面的方案链、56.6.3 各种加工方法的经济精度、56.7.3 粗加工后残余应力重新分布、
56.8.1 工序分散与集中的零件流、56.8.3 一批零件的流转、56.9.1 热处理在路线中的位置、56.9.2 辅助工序、56.9.4 SH-301 与 SH-101 的路线。"""
import _mfg as M
from bookout import T, figure, out, style

R = M.route()
P = M.part101()
ref = M.route101()
s301 = M.plan()
plt = style()
INK, MU = M.INK, M.MUTED


def box(ax, x, y, w, h, t, c=M.ACCENT, fs=7, a=0.13):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=c, alpha=a, ec=c, lw=0.9))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs)


def arrow(ax, p, q, c=INK, lw=0.8, rad=0.0):
    ax.annotate("", q, p, arrowprops={"arrowstyle": "->", "lw": lw, "color": c, "connectionstyle": f"arc3,rad={rad}"})


# ---- 图 56.2.5：工艺审查意见单（SH-101 A 版）
rows = [
    [T("1", "1"), T("轴承位与轴肩相接处", "bearing seat at the shoulder"), T("没有砂轮越程槽，也没有注圆角：淬硬后要磨，砂轮磨不到根部", "no grinding relief"),
     T("加 GB/T 6403.5 越程槽 b = 2，或注 R0.4 并允许砂轮修圆", "add a relief groove"), T("采纳", "accepted")],
    [T("2", "2"), T("密封轴颈 Ø24", "seal journal"), T("Ra 0.8 是油封所需；尺寸 h8 合理，不必提高", "Ra 0.8 needed by the seal"),
     T("保留；注明“磨削纹理不得有螺旋纹”", "keep; no lead on the ground surface"), T("采纳", "accepted")],
    [T("3", "3"), T("键槽与齿轮", "keyway vs gear"), T("键槽在渗碳淬火前铣出，槽底也会渗碳、淬硬", "keyway is carburized"),
     T("键槽区不要求软：确认可以淬硬，图上注“键槽允许渗碳”", "confirm a hardened keyway is acceptable"), T("采纳", "accepted")],
    [T("4", "4"), T("中心孔", "centre holes"), T("A 型中心孔热处理后易碰伤", "type A easily damaged"),
     T("改 B 型（带护锥），注“保留，热处理后修研”", "type B, keep, lap after hardening"), T("采纳", "accepted")],
    [T("5", "5"), T("齿轮精度 8 级", "gear grade 8"), T("滚齿 7 级 + 渗碳淬火降一级可以达到；若要 7 级就得磨齿，本厂没有磨齿机", "grade 7 would need gear grinding"),
     T("保持 8 级", "keep grade 8"), T("设计确认", "confirmed")],
]
M.table_fig(plt, [T("序号", "No."), T("部位", "feature"), T("问题", "problem"), T("建议", "proposal"), T("设计答复", "reply")], rows,
            [0.06, 0.17, 0.36, 0.30, 0.11], "fig56_2_5", fontsize=6.8)

# ---- 图 56.2.6：SH-101 与 SH-301
rows = [[T("材料与热处理", "material, heat"), T("45 钢调质 217–255 HB", "45, Q&T"), T("20CrMnTi 渗碳淬火 58–62 HRC", "20CrMnTi carburized")],
        [T("最精的外圆", "finest diameter"), "Ø35 k6（IT6）Ra 0.8", "Ø25 k6（IT6）Ra 0.8；Ø20 j6（IT6）"],
        [T("齿轮", "gear"), T("无（装大齿轮 GR-302）", "none"), "m2 z24，8 级"],
        [T("热处理后还能车吗", "turnable after heat?"), T("能（调质后 255 HB 以下）", "yes"), T("不能（58–62 HRC，只能磨）", "no — grind only")],
        [T("键槽", "keyway"), "12 N9，齿轮位", "6 N9，轴伸"],
        [T("毛坯", "blank"), "Ø50 × 182 圆钢", "Ø60 × 142 圆钢（或模锻件）"]]
M.table_fig(plt, ["", "SH-301", "SH-101"], rows, [0.24, 0.34, 0.42], "fig56_2_6", fontsize=7)

# ---- 图 56.1.3：原始资料在数字工厂里的位置
rows = [[T("零件图与装配图", "drawings"), T("SH-101 零件图要求：std/SH-101_part.yaml；工艺规程页选 SH-101 后显示；WQR-105 减速器三维模型", "std/SH-101_part.yaml; process-plan page; WQR-105 3D model")],
        [T("生产纲领与批量", "volume, batch"), T(f"年产 {P['annual_volume']} 件、每批 {P['batch']} 件（零件文件）；ERP 的物料 SH-101", f"{P['annual_volume']}/yr, batch {P['batch']}; ERP item")],
        [T("毛坯与材料", "blank, material"), T("物料 RM-20CR-D60（Ø60 圆钢，单价）；材料库 20CrMnTi", "item RM-20CR-D60; material library")],
        [T("现场设备", "equipment"), T("工作中心：台数、小时费率（数控车床、滚齿机、键槽铣床、热处理炉、外圆磨床、检验站）", "work centres: count, hourly rate")],
        [T("标准与工艺资料", "standards, data"), T("std/it_grades.yaml（标准公差）、econ_accuracy.yaml（经济精度）、route_methods.yaml（加工方法表）", "IT grades, economic accuracy, methods")],
        [T("同类零件的工艺", "similar parts"), T("SH-301 工艺规程（std/SH-301_process.yaml）；ERP 里 SH-101 的现行工序（RT-齿轮轴）", "SH-301 plan; current ERP routing")],
        [T("质量要求", "quality"), T("检验特性 C1–C16（零件文件）；QMS 的检验模板与历史数据", "characteristics C1–C16; QMS")]]
M.table_fig(plt, [T("原始资料", "input"), T("在数字工厂里的位置", "where in the digital factory")], rows, [0.2, 0.8], "fig56_1_3", fontsize=7, width_in=6.6)

# ---- 图 56.3.4：选毛坯要考虑的因素
rows = [[T("零件材料与性能", "material"), T("铸铁、铸铝只能铸；受力大、要求纤维连续的钢件用锻件；一般阶梯轴可用圆钢", "")],
        [T("形状与尺寸", "shape, size"), T("各段直径相差大的轴用锻件省料；形状复杂的箱体用铸件", "")],
        [T("生产纲领", "volume"), T("批量大，模锻、精密铸造的模具费摊得开；批量小用圆钢、自由锻", "")],
        [T("本厂与协作厂的条件", "shop capability"), T("有没有锻压设备、铸造车间或可靠的毛坯供应商", "")],
        [T("新工艺新材料", "new processes"), T("精锻、冷挤压、粉末冶金可以接近成品形状，少切削或不切削", "")]]
M.table_fig(plt, [T("因素", "factor"), T("要点", "notes")], rows, [0.24, 0.76], "fig56_3_4", fontsize=7, width_in=6.4)

# ---- 图 56.4.1：基准重合与不重合（齿轮左端面的轴向位置）
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 3.8))
for ax, title, mode in ((a1, T("(a) 基准不重合：程序从左端面编，8 由 81 与 73 间接得到", "(a) programmed from the left end"), 0),
                        (a2, T("(b) 基准重合：从轴肩（设计基准）直接控制 8", "(b) from the shoulder (design datum)"), 1)):
    x = 0
    for d, L, n in P["part"]["segments"]:
        ax.add_patch(plt.Rectangle((x, -d / 2), L, d, fc="#f6ead9", ec=INK, lw=0.7))
        x += L
    if mode == 0:
        ax.plot([0, 0], [11, 50], color=INK, lw=0.6); ax.plot([81, 81], [27, 50], color=INK, lw=0.6); ax.plot([73, 73], [16, 40], color=M.RED, lw=1.0)
        ax.annotate("", (81, 47), (0, 47), arrowprops={"arrowstyle": "<|-|>", "lw": 0.6, "mutation_scale": 6}); ax.text(40, 49, "81 ± 0.1", ha="center", fontsize=7)
        ax.annotate("", (73, 37), (0, 37), arrowprops={"arrowstyle": "<|-|>", "lw": 0.6, "mutation_scale": 6}); ax.text(36, 39, "73 ± 0.1", ha="center", fontsize=7)
    else:
        ax.plot([73, 73], [16, 40], color=M.RED, lw=1.0); ax.plot([81, 81], [27, 40], color=INK, lw=0.6)
        ax.plot([73, 81], [37, 37], color=M.GREEN, lw=0.8); ax.plot([66, 73], [37, 37], color=M.GREEN, lw=0.4); ax.plot([81, 88], [37, 37], color=M.GREEN, lw=0.4)
        ax.text(77, 40, "8 ± 0.1", ha="center", fontsize=7, color=M.GREEN)
    ax.text(73, -36, T("轴承定位轴肩（设计基准）", "bearing shoulder (design datum)"), fontsize=6.5, ha="center", color=M.RED)
    ax.set_title(title, fontsize=7.5, loc="left"); ax.set_xlim(-6, 142); ax.set_ylim(-40, 54); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig56_4_1")

# ---- 图 56.4.4：互为基准（渗碳淬火的齿轮 GR-203：以齿面定位磨孔，再以孔定位磨齿）
fig, axs = plt.subplots(1, 2, figsize=(6.0, 2.4))
for ax, t, which in ((axs[0], T("① 以齿面（节圆夹具）定位磨孔", "① grind the bore located on the flanks"), "bore"),
                     (axs[1], T("② 以磨好的孔定位磨齿", "② grind the flanks located on the bore"), "teeth")):
    import numpy as np
    th = np.linspace(0, 2 * np.pi, 400)
    r = 30 + 2.2 * np.sign(np.sin(20 * th)) * 0.5 + 1.1
    ax.plot(r * np.cos(th), r * np.sin(th), color=M.RED if which == "teeth" else INK, lw=1.2 if which == "teeth" else 0.7)
    ax.add_patch(plt.Circle((0, 0), 12, fc="white", ec=M.RED if which == "bore" else INK, lw=1.4 if which == "bore" else 0.7))
    for a in np.linspace(0, 2 * np.pi, 3, endpoint=False) + 0.3:
        if which == "bore":
            ax.plot(33.5 * np.cos(a), 33.5 * np.sin(a), "o", color=M.ACCENT, ms=6)
        else:
            ax.plot(11 * np.cos(a), 11 * np.sin(a), "^", color=M.ACCENT, ms=6)
    ax.text(0, -44, t, ha="center", fontsize=7)
    ax.set_xlim(-40, 40); ax.set_ylim(-48, 38); ax.set_aspect("equal"); ax.axis("off")
axs[0].text(0, 36, T("蓝点：定位元件　红色：本工序加工的表面", "blue: locators  red: surface machined"), ha="center", fontsize=6.5, color=MU)
figure(fig, "fig56_4_4")

# ---- 图 56.4.5：自为基准（以加工面本身为基准：浮动铰刀、无心磨、导轨磨削找正）
fig, axs = plt.subplots(1, 3, figsize=(6.6, 2.0))
a = axs[0]
a.add_patch(plt.Rectangle((-20, -12), 40, 24, fc="#f6ead9", ec=INK)); a.add_patch(plt.Rectangle((-20, -6), 40, 12, fc="white", ec=INK))
a.add_patch(plt.Rectangle((-28, -5), 50, 10, fc=M.ACCENT, alpha=0.3, ec=M.ACCENT)); a.text(0, -20, T("浮动铰刀：跟着孔走", "floating reamer"), ha="center", fontsize=7)
a.annotate("", (-34, 0), (-28, 0), arrowprops={"arrowstyle": "<->", "lw": 0.6, "color": M.RED})
a = axs[1]
a.add_patch(plt.Circle((-16, 4), 13, fc="#c9d3dc", ec=INK)); a.add_patch(plt.Circle((15, 2), 9, fc="#c9d3dc", ec=INK)); a.add_patch(plt.Circle((0, -2), 6, fc="#f6ead9", ec=M.RED, lw=1.2))
a.add_patch(plt.Rectangle((-3, -14), 6, 6, fc=MU, ec=INK)); a.text(0, -20, T("无心磨：以外圆本身定位", "centreless grinding"), ha="center", fontsize=7)
a = axs[2]
a.add_patch(plt.Rectangle((-24, -6), 48, 10, fc="#f6ead9", ec=INK)); a.plot([-24, 24], [4.2, 4.6], color=M.RED, lw=1.4)
a.plot([12, 12], [5, 13], color=INK, lw=0.6); a.plot(12, 13, "o", color=M.ACCENT, ms=5)
a.text(0, -20, T("磨导轨：先用表找正导轨面", "grind a slideway after indicating it"), ha="center", fontsize=7)
for a in axs:
    a.set_xlim(-36, 30); a.set_ylim(-24, 18); a.set_aspect("equal"); a.axis("off")
figure(fig, "fig56_4_5")

# ---- 图 56.5.1：粗基准的选择原则
fig, axs = plt.subplots(1, 4, figsize=(7.0, 1.9))
tt = [T("① 保证不加工面与加工面的位置", "① position of unmachined surfaces"), T("② 保证重要表面余量均匀", "② even stock on key surfaces"),
      T("③ 粗基准只用一次", "③ use a rough datum once"), T("④ 选平整光洁、无飞边浇口的面", "④ a clean, flat surface")]
for a, t in zip(axs, tt):
    a.axis("off"); a.set_xlim(0, 10); a.set_ylim(0, 8)
    a.text(5, 0.4, M.wrap(t, 11), ha="center", fontsize=6.8, va="bottom")
a = axs[0]; a.set_aspect("equal"); a.add_patch(plt.Circle((5, 5), 2.6, fc="#b9aa98", ec=INK)); a.add_patch(plt.Circle((5.4, 5), 1.3, fc="white", ec=M.RED)); a.plot([2.2, 2.2], [3.5, 6.5], color=M.ACCENT, lw=2)
a = axs[1]; a.add_patch(plt.Rectangle((1.5, 3.8), 7, 2.6, fc="#b9aa98", ec=INK)); a.plot([1.5, 8.5], [6.0, 6.0], color=M.RED, lw=1.2, ls="--"); a.plot([1.5, 8.5], [3.8, 3.8], color=M.ACCENT, lw=2.4)
a.text(5, 6.6, T("导轨面", "slideway"), ha="center", fontsize=6.5, color=M.RED)
a = axs[2]; a.add_patch(plt.Rectangle((1.5, 4), 7, 2, fc="#b9aa98", ec=INK)); a.text(5, 6.6, T("第二次用毛面 → 位置误差", "2nd use → error"), ha="center", fontsize=6.3, color=M.RED)
a = axs[3]; a.add_patch(plt.Rectangle((1.5, 4), 7, 2.2, fc="#b9aa98", ec=INK)); a.add_patch(plt.Rectangle((4.4, 6.2), 1.2, 0.8, fc="#8e7f6c", ec=INK))
a.text(5, 7.3, T("浇口", "gate"), ha="center", fontsize=6.3)
figure(fig, "fig56_5_1")

# ---- 图 56.6.2：孔、平面、齿面的方案链
fig, ax = plt.subplots(figsize=(7.0, 2.6))
lines = [(T("孔（实心钻出）", "hole from solid"), ["hole_drill", "hole_core_drill", "hole_ream"], 2.1),
         (T("孔（铸、锻出的孔）", "cored hole"), ["hole_rough_bore", "hole_semi_bore", "hole_finish_bore", "hole_grind"], 1.4),
         (T("平面", "plane"), ["plane_rough_mill", "plane_finish_mill"], 0.7),
         (T("齿面", "gear flank"), ["gear_hob", "gear_shave", "gear_grind"], 0.0)]
for lab, ks, y in lines:
    ax.text(-0.1, y + 0.25, lab, fontsize=7, ha="right", va="center")
    for i, k in enumerate(ks):
        m = R.METHODS[k]
        c = M.RED if m["hard_ok"] else M.ACCENT
        box(ax, i * 1.75, y, 1.45, 0.5, T(m["method_zh"], m["method_en"]) + f"\nIT{m['IT_min']}–{m['IT_max']}", c=c, fs=6.6)
        if i:
            arrow(ax, ((i - 1) * 1.75 + 1.45, y + 0.25), (i * 1.75, y + 0.25))
ax.text(6.9, 2.35, T("红框：淬硬后也能加工", "red: works on hardened steel"), fontsize=6.6, color=M.RED, ha="right")
ax.set_xlim(-2.2, 7.0); ax.set_ylim(-0.1, 2.7); ax.axis("off")
figure(fig, "fig56_6_2")

# ---- 图 56.6.3：各种加工方法的经济精度
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ms = [m for m in R.METHODS.values() if m["feature"] in ("外圆", "孔", "平面")]
for i, m in enumerate(ms):
    c = {"外圆": M.ACCENT, "孔": M.WARM, "平面": M.GREEN}[m["feature"]]
    ax.plot([m["IT_min"], m["IT_max"]], [i, i], color=c, lw=5, solid_capstyle="butt")
    ax.text(m["IT_min"] - 0.25, i, f"{m['feature']} · {m['method_zh']}" + ("（淬硬后可用）" if m["hard_ok"] else ""), va="center", fontsize=6.6)
ax.set_xlim(15, 0.5); ax.set_yticks([]); ax.set_xlabel(T("经济精度 IT（向右越精）", "economic grade IT"))
ax.grid(lw=0.3, alpha=0.5, axis="x")
figure(fig, "fig56_6_3")

# ---- 图 56.7.3：粗加工后残余应力重新分布（示意）
fig, axs = plt.subplots(1, 2, figsize=(6.2, 1.8))
import numpy as np
xx = np.linspace(0, 10, 50)
for a, bend, t in ((axs[0], 0, T("粗车前：毛坯内的残余应力自相平衡", "before: stresses in balance")),
                   (axs[1], 0.5, T("粗车切掉表层后：应力重新分布，轴弯了", "after rough turning: the shaft bows"))):
    y = bend * np.sin(np.pi * xx / 10)
    a.fill_between(xx, y - 1, y + 1, color="#f6ead9", ec=INK, lw=0.6)
    a.plot(xx, y, color=M.RED, lw=0.6, ls="--")
    a.text(5, -2.4, t, ha="center", fontsize=6.8); a.set_xlim(-0.5, 10.5); a.set_ylim(-3, 2.2); a.axis("off")
axs[1].annotate(T("精加工把它车（磨）直", "finishing makes it straight again"), (5, 1.55), (7.8, 2.0), fontsize=6.5, color=M.GREEN,
                arrowprops={"arrowstyle": "->", "lw": 0.5, "color": M.GREEN})
figure(fig, "fig56_7_3")

# ---- 图 56.8.1：工序分散与工序集中的零件流
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.0, 2.3))
A = [T("锯", "saw"), T("粗车", "rough"), T("精车", "finish"), T("滚齿", "hob"), T("铣键槽", "key"), T("渗碳淬火", "carburize"), T("磨", "grind"), T("检验", "inspect")]
B = [T("锯", "saw"), T("车铣复合：粗车、精车、铣键槽", "turn-mill: rough, finish, keyway"), T("滚齿", "hob"), T("渗碳淬火", "carburize"), T("磨", "grind"), T("检验", "inspect")]
for ax, seq, t in ((a1, A, T("A 工序分散：8 道工序、7 次搬运、7 次装夹", "A dispersed")), (a2, B, T("B 工序集中：6 道工序、5 次搬运、4 次装夹", "B concentrated"))):
    x = 0
    for i, n in enumerate(seq):
        w = 2.6 if "复合" in n or "turn-mill" in n else 0.9
        box(ax, x, 0, w, 0.6, n, c=M.WARM if "复合" in n or "turn-mill" in n else M.ACCENT, fs=6.6)
        if i:
            arrow(ax, (x - 0.25, 0.3), (x, 0.3))
        x += w + 0.25
    ax.text(0, 0.82, t, fontsize=7); ax.set_xlim(-0.1, 9.6); ax.set_ylim(-0.1, 1.05); ax.axis("off")
figure(fig, "fig56_8_1")

# ---- 图 56.8.3：一批零件在两种组织方式下的流转（顺序移动，批量 100，示意按工序时间）
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 2.4), sharex=True)
RT = M.route()
for ax, ops, t in ((a1, ref["operations"], "A"), (a2, None, "B")):
    if ops is None:
        import copy
        ops = [copy.deepcopy(o) for o in ref["operations"] if o["seq"] not in (20, 30, 50)]
        ops.insert(1, {"operation": "车铣复合 Turn-mill", "workstation": "车铣复合中心 TM-01", "minutes": 27.0, "setup_min": 45})
        RT.EXTRA_WS["车铣复合中心 TM-01"] = (95.0, 1)
    t0 = 0
    for i, o in enumerate(ops):
        r, n = RT.rate_per_hour(o["workstation"])
        furn = "热处理" in o["workstation"]
        dur = (o.get("setup_min", 0) + o["minutes"] * 100 / (n if not furn else 1) / (20 if furn else 1)) / 60
        ax.barh(i, dur, left=t0, color=M.RED if furn else M.ACCENT, height=0.6)
        ax.text(t0 + dur + 0.3, i, o["operation"].split(" ")[0], va="center", fontsize=6.3)
        t0 += dur
    ax.invert_yaxis(); ax.set_yticks([]); ax.set_ylabel(t, rotation=0, labelpad=10)
    ax.text(t0, len(ops) - 0.6, T(f"{t0:.0f} h", f"{t0:.0f} h"), fontsize=7, ha="right")
a2.set_xlabel(T("一批 100 件顺序移动的生产周期 / h（不计等待与运输）", "lead time of a batch of 100 / h (no waiting, no transport)"))
figure(fig, "fig56_8_3")

# ---- 图 56.9.1：热处理在路线中的位置
fig, ax = plt.subplots(figsize=(7.0, 2.2))
seq = [(T("毛坯", "blank"), MU), (T("预备热处理\n正火、退火", "preparatory\nnormalize, anneal"), M.RED), (T("粗加工", "roughing"), M.ACCENT),
       (T("调质、时效", "Q&T, ageing"), M.RED), (T("半精加工", "semi-finish"), M.ACCENT), (T("最终热处理\n淬火、渗碳", "final heat\nharden, carburize"), M.RED),
       (T("精加工\n（磨）", "finishing\n(grind)"), M.WARM)]
for i, (t, c) in enumerate(seq):
    box(ax, i * 1.0, 0.5, 0.86, 0.75, t, c=c, fs=6.2)
    if i:
        arrow(ax, (i * 1.0 - 0.14, 0.875), (i * 1.0, 0.875))
ax.text(1.43, 0.2, T("改善切削性、消除锻造应力", "machinability"), ha="center", fontsize=6.2, color=M.RED)
ax.text(3.43, 0.2, T("综合力学性能、消除内应力", "properties, stress relief"), ha="center", fontsize=6.2, color=M.RED)
ax.text(5.43, 0.2, T("表面硬度：之后只能磨", "surface hardness: grind only after"), ha="center", fontsize=6.2, color=M.RED)
ax.text(5.43, 1.45, T("SH-101：渗碳淬火（工序 60）", "SH-101: op 60"), ha="center", fontsize=6.4, color=M.RED)
ax.text(3.43, 1.45, T("SH-301：调质（工序 30）", "SH-301: Q&T (op 30)"), ha="center", fontsize=6.4, color=M.RED)
ax.set_xlim(-0.1, 7.0); ax.set_ylim(0, 1.7); ax.axis("off")
figure(fig, "fig56_9_1")

# ---- 图 56.9.2：辅助工序
rows = [[T("去毛刺、倒棱", "deburr"), T("铣键槽、滚齿之后", "after keyway, hobbing"), T("毛刺划伤定位面和轴承；渗碳时尖角过热、淬裂", "")],
        [T("清洗", "wash"), T("热处理前后、终检之前、装配之前", "before/after heat, before inspection"), T("切削液、磨屑、氧化皮影响测量和装配", "")],
        [T("修研中心孔", "lap centre holes"), T("热处理之后、磨削之前", "after heat, before grinding"), T("中心孔氧化、变形，磨出的跳动保不住", "")],
        [T("退磁", "demagnetize"), T("用电磁吸盘磨削、磁粉探伤之后", "after magnetic chucks, MPI"), T("剩磁吸附铁屑，进入轴承", "")],
        [T("防锈", "rust protection"), T("检验合格以后、工序间存放较久时", "after inspection"), T("渗碳件、磨削表面容易生锈", "")]]
M.table_fig(plt, [T("辅助工序", "auxiliary op"), T("放在哪里", "where"), T("为什么", "why")], rows, [0.2, 0.36, 0.44], "fig56_9_2", fontsize=7, width_in=6.6)

# ---- 图 56.9.4：SH-301 与 SH-101 的路线
r301 = [o["operation"].split(" ")[0] for o in s301["operations"]]
r101 = [o["operation"].split(" ")[0] for o in ref["operations"]]
fig, ax = plt.subplots(figsize=(7.0, 1.7))
for row, (lab, rr) in enumerate(((T("SH-301（45 调质）", "SH-301 (Q&T)"), r301), (T("SH-101（渗碳淬火）", "SH-101 (carburized)"), r101))):
    y = 1.0 - row * 0.9
    ax.text(-0.1, y + 0.25, lab, ha="right", va="center", fontsize=7)
    for i, n in enumerate(rr):
        c = M.RED if n in ("调质", "渗碳淬火") else (M.WARM if n.startswith("磨") else M.ACCENT)
        box(ax, i * 0.95, y, 0.82, 0.5, n, c=c, fs=6.4)
        if i:
            arrow(ax, (i * 0.95 - 0.13, y + 0.25), (i * 0.95, y + 0.25))
ax.set_xlim(-1.9, 8.0); ax.set_ylim(-0.0, 1.6); ax.axis("off")
figure(fig, "fig56_9_4")

out(n_ops_301=len(r301), n_ops_101=len(r101), ops_301="—".join(r301), ops_101="—".join(r101))
