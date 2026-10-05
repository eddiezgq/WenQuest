"""Section 3.10 Drawing management: reading the items and BOMs of the digital factory; multilevel explosion of WQR-105, quantity summary, "where is BRG-6207 used" (where-used);
the BOM differences of SA-300 from version A to version B, and the engineering change process (Example 3.10.1, Figure 3.10.1)."""
from collections import defaultdict

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import _ch3 as H
from bookout import T, figure, out, style

F = H.F
KIND = {"raw": T("原材料", "raw material"), "buy": T("外购件", "bought-out"), "make": T("自制件", "made part"),
        "sub": T("部件", "sub-assembly"), "fg": T("成品", "finished product")}


def explode(item, qty=1.0, level=0, out_=None):
    """Multilevel explosion: [(level, item, quantity at this level, cumulative quantity)]"""
    out_ = [] if out_ is None else out_
    for code, q in (F.BOMS.get(item) or (None, []))[1]:
        out_.append((level + 1, code, q, qty * q))
        explode(code, qty * q, level + 1, out_)
    return out_


def where_used(code):
    """Where-used: which BOMs use it directly, traced all the way up to the finished product"""
    parents = [p for p, (_, comps) in F.BOMS.items() if any(c == code for c, _ in comps)]
    chains = []
    for p in parents:
        up = where_used(p)
        chains += [[p] + u for u in up] if up else [[p]]
    return chains


tree = explode("WQR-105")
total = defaultdict(float)
for lvl, code, q, qq in tree:
    if code not in F.BOMS:                       # Lowest level (purchased parts, raw materials)
        total[code] += qq
levels = max(t[0] for t in tree)
n_codes = len({t[1] for t in tree})
kinds = defaultdict(int)
for c in {t[1] for t in tree}:
    kinds[F.ITEMS[c][1]] += 1
wu = where_used("BRG-6207")
bolts = sum(qq for lvl, c, q, qq in tree if c.startswith("BOLT-"))
n_brg = sum(qq for lvl, c, q, qq in tree if c.startswith("BRG-"))

# ---- SA-300: differences between version A (current BOM) and version B (after the engineering change of Chapter 33)
rows_b = H.sa300_rows()
a_codes = {c: q for c, q in F.BOMS["SA-300"][1]}
diff = []
for r in rows_b:
    if r.get("old"):
        diff.append((T("换料号", "new code"), f"{r['old']} → {r['code']}", T("联轴器键加长，改 C 型（开口键槽，第 33.2 节）", "longer type C coupling key, open keyseat (Sec. 33.2)")))
    elif r.get("chg"):
        diff.append((T("新增", "added"), T("套筒（待分配编号）", "sleeve (code to be assigned)"), T("左轴承轴向定位", "locates the left bearing")))
diff = [(T("升版", "new rev."), "SH-301 A → B", T("结构改版，材料改为 40Cr（第 33 章）", "redesign, material to 40Cr (Ch. 33)")),
        (T("升版", "new rev."), "GR-302 A → B", T("改为带毂锻件，毂宽 55", "hub forging, 55 mm hub"))] + diff
unchanged = [c for c in a_codes if c not in ("SH-301", "GR-302") and any(r["code"] == c for r in rows_b)]

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.3), gridspec_kw={"width_ratios": [1.0, 1.25]})
# (a) Engineering change process and the systems of the digital factory
steps = [(T("工程更改申请\nECR", "Change request\nECR"), "PLM"), (T("评审\n（设计、工艺、质量、采购）", "Review\n(design, process, quality, purchasing)"), "PLM"),
         (T("批准，发布新版本\nECO", "Approve, release\nECO"), "PLM"), (T("BOM 新版本、物料版本\n生效日期、旧料处理", "New BOM version, item rev.\neffectivity, old stock"), "ERP"),
         (T("工单用新版本\n检验模板随之改", "Work orders use the new rev.\ninspection template updated"), "MES / QMS")]
for i, (t, sysn) in enumerate(steps):
    y = 4 - i
    a0.add_patch(FancyBboxPatch((0.05, y - 0.36), 0.62, 0.72, boxstyle="round,pad=0.02,rounding_size=0.06", fc="#e8eef7", ec=H.INK, lw=0.7))
    a0.text(0.36, y, t, ha="center", va="center", fontsize=6.6)
    a0.text(0.74, y, sysn, ha="left", va="center", fontsize=6.8, color="#2c6fbb", weight="bold")
    if i < len(steps) - 1:
        a0.add_patch(FancyArrowPatch((0.36, y - 0.38), (0.36, y - 0.62), arrowstyle="-|>", mutation_scale=8, lw=0.8, color=H.INK))
a0.set_xlim(0, 1.05)
a0.set_ylim(-0.5, 4.5)
a0.axis("off")
a0.set_title(T("(a) 工程更改的流程", "(a) Engineering change process"), fontsize=8)
# (b) BOM differences of SA-300
a1.axis("off")
hdr = [T("变化", "Change"), T("物料", "Item"), T("原因", "Reason")]
xs = [0.0, 0.17, 0.55]
yy = 0.92
for x, h in zip(xs, hdr):
    a1.text(x, yy, h, fontsize=7, weight="bold", va="center")
for k, (c, item, why) in enumerate(diff):
    y = yy - 0.13 * (k + 1)
    for x, t in zip(xs, (c, item, why)):
        a1.text(x, y, t, fontsize=6.6, va="center")
y = yy - 0.13 * (len(diff) + 1)
a1.text(0, y, T("不变：", "Unchanged: ") + T("、", ", ").join(unchanged), fontsize=6.6, va="center", color=H.MUTED)
a1.plot([0, 1], [yy - 0.065, yy - 0.065], color=H.INK, lw=0.6)
a1.set_xlim(0, 1)
a1.set_ylim(0, 1)
a1.set_title(T("(b) SA-300 输出轴组件：A 版 → B 版的 BOM 差异", "(b) SA-300 output shaft assy: BOM changes, rev. A → B"), fontsize=8)
fig.tight_layout()
figure(fig, "fig3_10_1")

out(n_codes=n_codes, levels=levels, n_lines=len(tree), n_make=kinds["make"], n_buy=kinds["buy"], n_raw=kinds["raw"], n_sub=kinds["sub"],
    bolts=bolts, n_brg=n_brg, wu_brg=" → ".join(wu[0] + []) if wu else "", n_wu=len(wu), n_diff=len(diff), n_same=len(unchanged))
