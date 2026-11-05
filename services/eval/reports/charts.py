"""第 83 轮补充（Eddie 11-05：“缺乏图片和各种统计分析图，报告干巴巴的……应该是彩色的”）：评价与校情的统计图。

全部由流水线结果画出（matplotlib，PNG 2x），同一批图既放演示页，也嵌进网页版和 Word 版报告。
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
PAL = {"blue": "#2563eb", "teal": "#0d9488", "amber": "#f59e0b", "red": "#e11d48", "violet": "#7c3aed", "green": "#16a34a",
       "slate": "#475569", "sky": "#0ea5e9", "pink": "#db2777", "ink": "#0f172a", "grid": "#e2e8f0"}
GRADE_COL = {"A": "#16a34a", "B+": "#22c55e", "B": "#84cc16", "C+": "#f59e0b", "C": "#fb923c", "D": "#f43f5e", "F": "#be123c"}
TIER_COL = {"未掌握": "#f43f5e", "基本掌握": "#f59e0b", "熟练": "#22c55e", "精通": "#0d9488"}


def _font():
    have = {f.name for f in font_manager.fontManager.ttflist}
    for n in ("Noto Sans CJK SC", "Noto Sans CJK TC", "Noto Sans CJK JP", "Noto Serif CJK SC", "WenQuanYi Zen Hei", "Microsoft YaHei"):
        if n in have:
            return n
    return "DejaVu Sans"


plt.rcParams.update({"font.family": [_font(), "DejaVu Sans"], "axes.unicode_minus": False, "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#94a3b8",
                     "axes.titleweight": "bold", "axes.titlesize": 13, "figure.dpi": 100})


def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=180, facecolor="white")
    plt.close(fig)
    return path.name


def course_charts(c, run_lp, stu, kp_names, out: Path):
    """课程层：返回 {图名: 文件名}"""
    figs = {}
    # 1 成绩分布
    g = c["grades"]
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ks = list(g)
    ax.bar(ks, [g[k] for k in ks], color=[GRADE_COL.get(k, PAL["slate"]) for k in ks], width=0.65)
    for i, k in enumerate(ks):
        ax.text(i, g[k] + 0.2, str(g[k]), ha="center", fontsize=11, fontweight="bold")
    ax.set_title(f"成绩分布（{c['n']} 人，总评平均 {c['mean']}）")
    ax.set_ylabel("人数")
    ax.grid(axis="y", color=PAL["grid"])
    figs["grades"] = _save(fig, out / "fig_grades.png")
    # 2 课程目标达成度：直接 / 间接 + 阈值
    o = c["objectives"]
    cos = list(o)
    x = np.arange(len(cos))
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    d = [o[k]["direct"] for k in cos]
    ax.bar(x - 0.18, d, 0.36, label="直接评价", color=[PAL["teal"] if o[k]["achieved"] else PAL["red"] for k in cos])
    ax.bar(x + 0.18, [o[k]["indirect"] for k in cos], 0.36, label="间接评价（学生自评）", color=PAL["sky"], alpha=0.55)
    ax.axhline(c["threshold"], color=PAL["amber"], lw=2, ls="--")
    ax.text(0.55, c["threshold"] + 0.015, f"达成阈值 {c['threshold']:.2f}", ha="left", color="#b45309", fontsize=10)
    for i, v in enumerate(d):
        ax.text(i - 0.18, v + 0.012, f"{v:.3f}", ha="center", fontsize=9.5, fontweight="bold")
    ax.set_xticks(x, cos)
    ax.set_ylim(0, 1.12)
    ax.set_title("课程目标达成度")
    ax.legend(frameon=False, loc="upper center", ncol=2, fontsize=9.5, bbox_to_anchor=(0.5, 1.0))
    figs["co"] = _save(fig, out / "fig_co.png")
    # 3 考核环节得分率（热力）
    rows = [(co, comp["name"], comp["rate"], comp["weight"]) for co in cos for comp in o[co]["components"]]
    fig, ax = plt.subplots(figsize=(6.8, 0.42 * len(rows) + 1.0))
    cmap = plt.get_cmap("RdYlGn")
    for i, (co, n, r, w) in enumerate(rows[::-1]):
        ax.barh(i, r, color=cmap((r - 0.3) / 0.65), height=0.7)
        ax.text(r + 0.01, i, f"{r:.2f}（权重 {w:.1f}）", va="center", fontsize=9.5)
    ax.set_yticks(range(len(rows)), [f"{co} {n}" for co, n, _, _ in rows[::-1]], fontsize=9.5)
    ax.set_xlim(0, 1.15)
    ax.axvline(0.6, color=PAL["slate"], lw=1, ls=":")
    ax.set_title("各考核环节得分率（越红越弱）")
    figs["components"] = _save(fig, out / "fig_components.png")
    # 4 知识点掌握结构（期末）
    tiers = ["未掌握", "基本掌握", "熟练", "精通"]
    kps = list(stu[0]["kp_map"])
    cnt = {t: [sum(1 for s in stu if s["kp_map"][k]["tier"] == t) for k in kps] for t in tiers}
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    left = np.zeros(len(kps))
    for t in tiers:
        ax.barh(range(len(kps)), cnt[t], left=left, color=TIER_COL[t], label=t, height=0.7)
        left += np.array(cnt[t])
    ax.set_yticks(range(len(kps)), [kp_names.get(k, k) for k in kps], fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlabel("学生人数")
    ax.set_title("期末各知识点掌握结构（自适应考试）")
    ax.legend(ncol=4, frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.28), fontsize=9.5)
    figs["kp"] = _save(fig, out / "fig_kp.png")
    # 5 学习增值 + AI 推荐对随机
    lp = run_lp["练习对比"]
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.6), gridspec_kw={"width_ratios": [1, 1.4]})
    ga = c["gain"]
    axs[0].bar(["期初", "期末"], [ga["pre_mean"], ga["post_mean"]], color=[PAL["slate"], PAL["violet"]], width=0.55)
    for i, v in enumerate([ga["pre_mean"], ga["post_mean"]]):
        axs[0].text(i, v + 0.01, f"{v:.2f}", ha="center", fontweight="bold")
    axs[0].set_ylim(0, 0.8)
    axs[0].set_title(f"平均掌握概率 +{ga['gain']:.2f}")
    keys = ["全章平均掌握概率提升", "两个卡点平均提升"]
    xx = np.arange(len(keys))
    axs[1].bar(xx - 0.18, [lp["推荐"][k] for k in keys], 0.36, label="AI 学习路径", color=PAL["violet"])
    axs[1].bar(xx + 0.18, [lp["随机"][k] for k in keys], 0.36, label="随机练习", color="#cbd5e1")
    for i, k in enumerate(keys):
        axs[1].text(i - 0.18, lp["推荐"][k] + 0.004, f"{lp['推荐'][k]:.3f}", ha="center", fontsize=9)
        axs[1].text(i + 0.18, lp["随机"][k] + 0.004, f"{lp['随机'][k]:.3f}", ha="center", fontsize=9)
    axs[1].set_xticks(xx, ["全章平均提升", "两个卡点提升"])
    axs[1].set_title("AI 学习路径 vs 随机练习")
    axs[1].legend(frameon=False, fontsize=9)
    figs["gain"] = _save(fig, out / "fig_gain.png")
    # 6 知识 × 实践 散点：照抄型被拦下
    copiers = set(c["review"]["暂缓发布成绩单"])
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    k_hot = 0
    for s in stu:
        hot = s["id"] in copiers
        ax.scatter(s["A"], s["B"], s=90 if hot else 55, color=GRADE_COL.get(s["grade"], PAL["slate"]),
                   edgecolor=PAL["red"] if hot else "white", linewidth=2.2 if hot else 0.8, zorder=3)
        if hot:
            ax.annotate(s["id"], (s["A"], s["B"]), xytext=[(8, 8), (8, -16), (8, -4)][k_hot % 3], textcoords="offset points",
                        color=PAL["red"], fontsize=10, fontweight="bold")
            k_hot += 1
    ax.plot([40, 100], [40, 100], color=PAL["grid"], lw=1, zorder=1)
    ax.set_xlabel("知识（闭卷、自适应考试）")
    ax.set_ylabel("实践（虚拟实验过程 + 报告）")
    ax.set_title("知识 vs 实践：红圈是终审暂缓的学生")
    figs["scatter"] = _save(fig, out / "fig_scatter.png")
    # 7 能力画像雷达（三个样例学生）
    sample = [next(s for s in stu if s["id"] == "S006"), max(stu, key=lambda s: s["total"]), min(stu, key=lambda s: s["total"])]
    labels = list(sample[0]["profile"])
    ang = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    fig = plt.figure(figsize=(5.4, 4.6))
    ax = fig.add_subplot(111, polar=True)
    for s, col in zip(sample, (PAL["red"], PAL["teal"], PAL["amber"])):
        v = [s["profile"][k] for k in labels]
        ax.plot(ang + ang[:1], v + v[:1], color=col, lw=2, label=f"{s['id']}（{s['grade']}）")
        ax.fill(ang + ang[:1], v + v[:1], color=col, alpha=0.12)
    ax.set_xticks(ang, labels)
    ax.set_ylim(0, 100)
    ax.set_title("能力画像", pad=18)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22), ncol=3, frameon=False, fontsize=9.5)
    figs["radar"] = _save(fig, out / "fig_radar.png")
    # 8 终审队列 + 评教主题
    rs = {k: v for k, v in c["review"]["按原因"].items() if v}
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.8), gridspec_kw={"width_ratios": [1, 1.25]})
    cols = [PAL["violet"], PAL["sky"], PAL["amber"], PAL["pink"], PAL["teal"], PAL["slate"]]
    axs[0].pie(rs.values(), labels=[f"{k}\n{v}" for k, v in rs.items()], colors=cols[:len(rs)], startangle=90,
               wedgeprops={"width": 0.42, "edgecolor": "white"}, textprops={"fontsize": 9})
    axs[0].set_title(f"终审队列 {c['review']['总数']} 例")
    th = c["themes"]
    axs[1].barh(range(len(th)), [t["count"] for t in th], color=[PAL["green"] if t["tone"] == "正面" else PAL["red"] for t in th], height=0.55)
    axs[1].set_yticks(range(len(th)), [t["theme"] for t in th], fontsize=9.5)
    axs[1].invert_yaxis()
    axs[1].set_xlabel("人次")
    axs[1].set_title("评教：学生说了什么（绿正面，红负面）")
    figs["review"] = _save(fig, out / "fig_review.png")
    return figs


NAMES = {"1.2": "1.2 工程知识", "2.1": "2.1 问题分析", "3.1": "3.1 设计/开发", "4.2": "4.2 研究", "5.1": "5.1 现代工具", "10.1": "10.1 沟通"}


def school_charts(pts, sch, out: Path, thr=0.70):
    figs = {}
    progs = [(col["name"], p) for col in sch["colleges"] for p in col["programs"]]
    # 1 热力图：专业 × 指标点
    labels = sorted({x["id"].split(" ")[0].split("（")[0] for _, p in progs for x in p["points"]}, key=lambda s: [float(t) for t in s.split(".")])
    M = np.full((len(progs), len(labels)), np.nan)
    for i, (_, p) in enumerate(progs):
        for x in p["points"]:
            M[i, labels.index(x["id"].split(" ")[0].split("（")[0])] = x["v"]
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    im = ax.imshow(M, cmap="RdYlGn", vmin=0.6, vmax=0.86, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if np.isnan(M[i, j]):
                ax.text(j, i, "—", ha="center", va="center", fontsize=9, color="#94a3b8")
            else:
                ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=9.5, color="#0f172a",
                        fontweight="bold" if M[i, j] < thr else "normal")
    ax.set_xticks(range(len(labels)), [NAMES.get(l, l) for l in labels], fontsize=9)
    ax.set_yticks(range(len(progs)), [p["name"] + ("" if p["real"] else "（模拟）") for _, p in progs], fontsize=9.5)
    ax.set_title("全校毕业要求达成热力图（低于 0.70 加粗）")
    fig.colorbar(im, ax=ax, fraction=0.03)
    for s in ax.spines.values():
        s.set_visible(False)
    figs["heat"] = _save(fig, out / "fig_heat.png")
    # 2 机器人工程：指标点雷达 + 阈值
    lab = [p["id"].replace("（示例指标点）", "") for p in pts]
    v = [p["weighted"] for p in pts]
    ang = np.linspace(0, 2 * np.pi, len(lab), endpoint=False).tolist()
    fig = plt.figure(figsize=(5.4, 4.6))
    ax = fig.add_subplot(111, polar=True)
    ax.plot(ang + ang[:1], v + v[:1], color=PAL["blue"], lw=2.2, label="加权和法")
    ax.fill(ang + ang[:1], v + v[:1], color=PAL["blue"], alpha=0.15)
    ax.plot(ang + ang[:1], [thr] * (len(v) + 1), color=PAL["red"], lw=1.6, ls="--", label="达成阈值 0.70")
    ax.set_xticks(ang, lab, fontsize=9.5)
    ax.set_ylim(0.5, 0.9)
    ax.set_yticks([0.6, 0.7, 0.8], ["0.6", "0.7", "0.8"], fontsize=8.5, color="#64748b")
    ax.set_rlabel_position(22)
    ax.set_title("机器人工程 · 毕业要求指标点", pad=18)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False, fontsize=9.5)
    figs["radar"] = _save(fig, out / "fig_grad_radar.png")
    # 3 支撑课程贡献（堆叠）
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    cols = [PAL["violet"], PAL["sky"], PAL["teal"], PAL["amber"]]
    for i, p in enumerate(pts):
        left = 0
        for k, s in enumerate(p["support"]):
            w = s["w"] * s["v"]
            ax.barh(i, w, left=left, color=cols[k % 4] if not s["example"] else cols[k % 4], alpha=1 if not s["example"] else 0.45,
                    edgecolor="white", height=0.6)
            ax.text(left + w / 2, i, s["course"] if w > 0.12 else "", ha="center", va="center", fontsize=8.5, color="white" if not s["example"] else PAL["ink"])
            left += w
    ax.axvline(thr, color=PAL["red"], ls="--", lw=1.6)
    ax.set_yticks(range(len(pts)), lab, fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 0.9)
    ax.set_title("各指标点由哪些课程撑起来（深色 = 真算，浅色 = 示例课程）")
    figs["support"] = _save(fig, out / "fig_support.png")
    # 4 学业预警与未达成指标点（按专业）
    fig, ax1 = plt.subplots(figsize=(7.6, 3.6))
    names = [p["name"] for _, p in progs]
    x = np.arange(len(names))
    ax1.bar(x - 0.2, [p["risk"] for _, p in progs], 0.4, color=PAL["amber"], label="学业预警（人）")
    ax2 = ax1.twinx()
    ax2.bar(x + 0.2, [p["low"] for _, p in progs], 0.4, color=PAL["red"], label="未达成指标点（个）")
    ax1.set_xticks(x, names, fontsize=9, rotation=12)
    ax1.set_title("各专业：学业预警与未达成指标点")
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, frameon=False, fontsize=9, loc="upper left")
    ax2.spines["right"].set_visible(True)
    figs["risk"] = _save(fig, out / "fig_risk.png")
    return figs


def kp_names():
    b = json.loads((HERE / "ch1_bank.json").read_text(encoding="utf-8"))
    return {k["id"]: k["name_zh"] for k in b["knowledge_points"]}
