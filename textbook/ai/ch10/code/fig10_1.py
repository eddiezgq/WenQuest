"""10.1 节的示意图（数据同 _ch10.py 与程序 10.1.1）。

图 10.1.1：（a）各家加速器在同一张屋顶线图上（对数坐标）：横轴计算强度，纵轴可达算力，每条线的转折点就是屋脊点。
峰值算力相差二十多倍，屋脊点却都在一百多到三百多 FLOP/B，相差约两倍——换一家的加速器，受带宽限制的运算还是受带宽限制。
（b）厂商公布了什么：每条规格里六项（稠密峰值、低精度峰值、显存带宽、卡间互联、功耗、并行单元数）中有几项查不到。
"""
from _ch10 import ACC, missing, roofline
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(12.6, 4.5), gridspec_kw={"width_ratios": [1.25, 1]})

# ---------- (a) 同一张屋顶线图
shown = sorted((k for k in ACC if roofline(ACC[k]) is not None), key=lambda k: -ACC[k]["bf16"])
cols = {"NVIDIA": C["z"], "AMD": C["x"], "Google": C["accent"], "壁仞": C["y"], "天数智芯": C["muted"], "寒武纪": "#8c564b"}
xs = [2 ** i for i in range(-1, 12)]
for i, k in enumerate(shown):
    acc = ACC[k]
    peak, bw, ridge = acc["bf16"], acc["bw"], roofline(acc)
    ys = [min(peak, bw * x) / 1e12 for x in xs]
    col = cols.get(acc["vendor"], C["ink"])
    a.plot(xs, ys, lw=1.6, color=col, alpha=0.9)
    a.plot([ridge], [peak / 1e12], "o", ms=4, color=col)
    a.annotate(T(acc["name"].replace("NVIDIA ", "").replace("Google ", "").replace(" SXM", ""),
                 acc["en"].replace(" SXM", "")),
               (ridge, peak / 1e12), textcoords="offset points", xytext=(7, 5 if i % 2 else -8), fontsize=7.5, color=col)
a.set_xscale("log", base=2)
a.set_yscale("log", base=10)
a.set_xlabel(T("计算强度（FLOP/B）", "arithmetic intensity (FLOP/B)"))
a.set_ylabel(T("可达算力（TFLOP/s，BF16/FP16 稠密）", "attainable (TFLOP/s, dense BF16/FP16)"))
a.set_title(T("(a) 各家加速器的屋顶线", "(a) Roofline of several accelerators"), fontsize=10)
a.set_xlim(0.5, 4096 * 2)
a.grid(alpha=0.25, lw=0.5)

# ---------- (b) 公布了几项、没公布几项
ks = sorted(ACC, key=lambda k: (missing(ACC[k]), ACC[k]["name"]))
y = range(len(ks))
miss = [missing(ACC[k]) for k in ks]
a_pub = [6 - m for m in miss]
b.barh(list(y), a_pub, color=C["z"], alpha=0.65, label=T("已公布", "published"))
b.barh(list(y), miss, left=a_pub, color=C["x"], alpha=0.55, label=T("查不到", "not published"))
b.set_yticks(list(y))
b.set_yticklabels([T(ACC[k]["name"], ACC[k]["en"]) for k in ks], fontsize=7.5)
b.set_xlim(0, 6)
b.set_xticks(range(7))
b.set_xlabel(T("六项规格中的项数", "of the six specifications"))
b.set_title(T("(b) 厂商公布了什么", "(b) What vendors publish"), fontsize=10)
b.legend(fontsize=8, loc="lower right", framealpha=0.9)
b.invert_yaxis()
b.grid(axis="x", alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig10_1_1")
