"""6.3 节：乘法器。

算例 6.3.1  电机电流环的 PI 控制要算 Kp·e（16 位 × 16 位，无符号部分），高速版本的时钟 250 MHz。三种乘法器
            （进位保留阵列 + 行波进位；部分积按列压缩的树 + Kogge–Stone；基 4 Booth 编码 + 同样的树与加法器）按 SKY130 综合的延时与面积，
            哪些满足时间预算，面积最小的是哪个；部分积的行数与压缩的级数。
图 6.3.1    8 位 × 8 位乘法的部分积点图：普通的与门部分积（8 行）与基 4 Booth 编码（5 行）。
"""
from bookout import T, figure, out, style
from mos import P, ff_timing
import _draw as d

S = P["arith_syn"]
q = P["problems"]["p63"]
ff = ff_timing()
budget = 1 / (q["f_MHz"] * 1e6) - ff["tcq"] - ff["tsu"]


def levels(rows):
    """Dadda 序列 2, 3, 4, 6, 9, 13, 19, …：把 rows 行压到 2 行需要的级数。"""
    seq, h = [2], 2
    while h < rows:
        h = h * 3 // 2
        seq.append(h)
    return len(seq) - 1 if seq[-1] >= rows else len(seq)


n = q["bits"]
kinds = ("array", "dadda", "booth")
ok = [k for k in kinds if S[f"tgt_mul_{k}_{n}"]["delay"] * 1e-12 <= budget]
best = min(ok, key=lambda k: S[f"tgt_mul_{k}_{n}"]["area"])
for k in kinds:
    t = S[f"tgt_mul_{k}_{n}"]
    out(**{f"t_{k}_ns": t["delay"] / 1e3, f"t_{k}_a": t["area"]})


def booth_height(n):
    """无符号 n 位基 4 Booth 各列的位数（部分积 n + 2 位、取反加 1 的位、符号处理的常数位），取最高的一列。"""
    W, nd = 2 * n, n // 2 + 1
    cols, const = [0] * W, 0
    for i in range(nd):
        for j in range(n + 2):
            if 2 * i + j < W:
                cols[2 * i + j] += 1
        cols[2 * i] += 1
        const -= 1 << (2 * i + n + 1)
    const %= 1 << W
    for k in range(W):
        cols[k] += const >> k & 1
    return max(cols)


out(bh16=booth_height(16), lvb16=levels(booth_height(16)))
out(bits=n, f_MHz=q["f_MHz"], budget_ns=budget * 1e9, best=best, n_ok=len(ok),
    rows_plain=n, rows_booth=n // 2 + 1, lv_plain=levels(n), lv_booth=levels(n // 2 + 1),
    rows8_booth=8 // 2 + 1, lv8_plain=levels(8), lv8_booth=levels(5))
for k in kinds:
    for w in (8, 16):
        s = S[f"mul_{k}_{w}"]
        out(**{f"{k}{w}_d": s["delay"], f"{k}{w}_ns": s["delay"] / 1e3, f"{k}{w}_a": s["area"], f"{k}{w}_c": s["cells"], f"{k}{w}_am": s["area_min"], f"{k}{w}_dm": s["delay_amin"]})
    out(**{f"{k}_x": S[f"mul_{k}_16"]["delay"] / S[f"mul_{k}_8"]["delay"], f"{k}_ax": S[f"mul_{k}_16"]["area"] / S[f"mul_{k}_8"]["area"]})
out(mul_vs_add=S["mul_dadda_16"]["area"] / S["add_ks_16"]["area"], booth_save_pct=(1 - S["mul_booth_16"]["area"] / S["mul_dadda_16"]["area"]) * 100,
    booth8_more_pct=(S["mul_booth_8"]["area"] / S["mul_dadda_8"]["area"] - 1) * 100)

# ---------------------------------------------------------------- 图 6.3.1
plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.2))
for i in range(8):
    for j in range(8):
        a1.plot(15 - (i + j), -i, "o", color=d.NMOS, ms=5)
a1.set_title(T("(a) 与门部分积：8 行", "(a) AND partial products: 8 rows"), fontsize=10)
for i in range(5):
    for j in range(10):
        pos = 2 * i + j
        if pos < 16:
            last = j == 9 and i < 4
            a2.plot(15 - pos, -i, "s" if last else "o", color=d.PMOS if last else d.NMOS, ms=5)
    if i < 4:                                    # 无符号 8 位时最后一行的数字只取 0 或 1，不取反
        a2.plot(15 - 2 * i, -i - 0.35, "^", color=d.LOAD, ms=5)
a2.set_title(T("(b) 基 4 Booth：5 行（方块：符号位，三角：取反加 1）", "(b) radix-4 Booth: 5 rows (square: sign, triangle: +1 for negation)"), fontsize=10)
for ax in (a1, a2):
    ax.set_xlim(-0.8, 15.8); ax.set_ylim(-8.2, 0.8)
    ax.axis("off")
figure(fig, "fig6_3_1")
