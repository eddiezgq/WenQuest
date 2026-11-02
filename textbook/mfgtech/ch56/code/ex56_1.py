"""56.1 节：工艺规程的设计步骤（图 56.1.1），生产类型与年产量（图 56.1.2，轻型零件的常用划分，示意），SH-101 的生产类型。
年产量、批量取 std/SH-101_part.yaml（WQR-105 年产 6000 台，教学设定）。"""
import _mfg as M
from bookout import T, figure, out, style

P = M.part101()
N = P["annual_volume"]
# 轻型零件（< 100 kg）按年产量划分生产类型（国内教材常用的划分，示意）
TYPES = [(T("单件生产", "one-off"), 0, 100), (T("小批", "small batch"), 100, 500), (T("中批", "medium batch"), 500, 5000),
         (T("大批", "large batch"), 5000, 50000), (T("大量生产", "mass"), 50000, 500000)]
kind = next(n for n, lo, hi in TYPES if lo <= N < hi)
batches_per_year = N / P["batch"]

plt = style()
# ---- 图 56.1.1：设计步骤
fig, ax = plt.subplots(figsize=(7.4, 2.3))
steps = [(T("① 零件图\n工艺审查", "① review the\ndrawing"), "56.2", M.ACCENT), (T("② 选毛坯", "② blank"), "56.3", M.ACCENT),
         (T("③ 选定位\n基准", "③ datums"), "56.4–56.5", M.ACCENT), (T("④ 拟定\n工艺路线", "④ route"), "56.6–56.10", M.ACCENT),
         (T("⑤ 余量与\n工序尺寸", "⑤ stock &\nsizes"), T("第 57 章", "Ch. 57"), M.MUTED), (T("⑥ 设备工装\n切削用量", "⑥ machines,\ncutting data"), T("第 57 章", "Ch. 57"), M.MUTED),
         (T("⑦ 时间定额", "⑦ times"), T("第 57 章", "Ch. 57"), M.MUTED), (T("⑧ 技术经济\n分析", "⑧ economics"), T("第 57 章", "Ch. 57"), M.MUTED),
         (T("⑨ 工艺文件\n评审发布", "⑨ documents,\nreview"), T("第 50、57 章", "Ch. 50, 57"), M.MUTED)]
w, g = 0.95, 0.32
for i, (t, where, c) in enumerate(steps):
    x = i * (w + g)
    ax.add_patch(plt.Rectangle((x, 0.35), w, 0.9, fc=c, alpha=0.12, ec=c, lw=1.0))
    ax.text(x + w / 2, 0.8, t, ha="center", va="center", fontsize=6.6)
    ax.text(x + w / 2, 0.18, where, ha="center", va="center", fontsize=6.5, color=c)
    if i:
        ax.annotate("", (x, 0.8), (x - g, 0.8), arrowprops={"arrowstyle": "->", "lw": 0.8, "color": M.INK})
x_end = len(steps) * (w + g) - g
ax.annotate("", (w / 2, 1.27), (x_end - w / 2, 1.27), arrowprops={"arrowstyle": "->", "lw": 0.7, "color": M.RED, "connectionstyle": "arc3,rad=0.12"})
ax.text(x_end / 2, 1.62, T("评审不通过，或批量、设备变了：返回前面的步骤", "rejected, or batch / machines changed: go back"), ha="center", fontsize=7, color=M.RED)
ax.set_xlim(-0.1, x_end + 0.1); ax.set_ylim(0, 1.85); ax.axis("off")
figure(fig, "fig56_1_1")

# ---- 图 56.1.2：生产类型
fig, ax = plt.subplots(figsize=(6.0, 1.7))
cols = ["#dfe7ef", "#cddbe8", "#b8cde0", "#a1bcd6", "#86a9cb"]
for (n, lo, hi), c in zip(TYPES, cols):
    lo_ = max(lo, 10)
    ax.axvspan(lo_, hi, color=c)
    ax.text((lo_ * hi) ** 0.5, 0.55, n, ha="center", va="center", fontsize=7.5)
ax.axvline(N, color=M.RED, lw=1.4)
ax.text(N * 1.1, 0.18, T(f"SH-101：年产 {N} 件", f"SH-101: {N}/yr"), fontsize=7.5, color=M.RED)
ax.set_xscale("log"); ax.set_xlim(10, 500000); ax.set_yticks([]); ax.set_ylim(0, 1)
ax.set_xlabel(T("年产量 / 件（轻型零件，< 100 kg；常用划分，示意）", "annual volume (light parts < 100 kg; typical classes)"))
figure(fig, "fig56_1_2")

out(N=N, kind=kind, batch=P["batch"], batches=batches_per_year, mass=P["part"]["mass_kg"])
