"""50.1 节：SH-301 现行工艺路线（数字工厂）一览——工序数、单件工时合计；图 50.1.1 工艺规程设计的步骤。"""
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import _mfg as M
from bookout import T, figure, out, style

p = M.plan()
ops = p["operations"]
total = sum(o["minutes"] for o in ops)
rt = M.F.BOMS["SH-301"][0]
assert [o["operation"] for o in ops] == [op for op, _ in M.F.ROUTINGS[rt]]        # 与工厂数据的工艺路线一致
assert total == sum(m for _, m in M.F.ROUTINGS[rt])
mach = [o for o in ops if M.stage(o["operation"]) in ("rough", "finish", "keyway", "grind")]
out(n_ops=len(ops), total_min=total, n_mach=len(mach), routing=rt.split(" ")[0])

# ---- 图 50.1.1：工艺规程设计的步骤（左列为步骤，右列为每一步用到的资料与工具）
steps = [("零件的工艺分析", "Manufacturability analysis", "图纸、技术要求、生产纲领", "drawing, requirements, volume"),
         ("确定毛坯", "Choose the blank", "材料、批量、毛坯制造能力", "material, volume, blank supply"),
         ("选择定位基准", "Choose datums", "基准选择原则", "datum principles"),
         ("拟定工艺路线", "Plan the route", "经济精度、加工阶段、工序顺序", "economic accuracy, stages, order"),
         ("确定余量与工序尺寸", "Allowances & op. dimensions", "余量标准、尺寸链", "allowance standards, chains"),
         ("选设备、工装、切削用量", "Machines, tooling, cutting data", "工作中心、刀具、切削数据", "work centers, tools, cutting data"),
         ("计算时间定额", "Time standards", "基本时间 + 辅助时间 …", "machining + handling time …"),
         ("技术经济分析", "Techno-economic analysis", "费率、批量、成本", "rates, batch size, cost"),
         ("编写工艺文件、评审、发布", "Write, review, release", "工艺卡、评审、ERP 工艺路线", "route sheets, review, ERP routing")]
plt = style()
fig, ax = plt.subplots(figsize=(6.8, 6.2))
n = len(steps)
for i, (a, ae, b, be) in enumerate(steps):
    y = n - 1 - i
    ax.add_patch(FancyBboxPatch((0, y - 0.35), 3.4, 0.7, boxstyle="round,pad=0.02,rounding_size=0.12", fc="#e6eef7", ec=M.INK, lw=1))
    ax.text(0.12, y, f"{i + 1}", fontsize=11, color="#3a7dc9", va="center", weight="bold")
    ax.text(1.85, y, T(a, ae), fontsize=10.5, ha="center", va="center", color=M.INK)
    ax.text(3.65, y, T(b, be), fontsize=9.5, va="center", color=M.MUTED)
    if i < n - 1:
        ax.add_patch(FancyArrowPatch((1.75, y - 0.36), (1.75, y - 0.64), arrowstyle="-|>", mutation_scale=10, color=M.INK, lw=1))
ax.add_patch(FancyArrowPatch((-0.1, -0.1), (-0.1, n - 1.4), connectionstyle="arc3,rad=-0.25", arrowstyle="-|>", mutation_scale=12,
                             color="#b5443b", lw=1.2, ls="--"))
ax.text(-0.55, n / 2 - 0.8, T("评审退回、\n批量变化时\n返回修改", "revise after\nreview or a\nvolume change"), fontsize=9, color="#b5443b", ha="center", va="center")
ax.set_xlim(-1.2, 7.4); ax.set_ylim(-0.6, n - 0.4); ax.axis("off")
figure(fig, "fig50_1_1")
