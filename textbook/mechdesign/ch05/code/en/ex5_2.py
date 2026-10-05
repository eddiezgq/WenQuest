"""Section 5.2 Steel: properties of GB test pieces (25 mm blanks) compared with design values (digital-factory material library,
taken by the section size of the part): hardenability and the size effect (Example 5.2.1, Figure 5.2.1)."""
import _ch5 as H
from bookout import T, figure, out, style

rows = []
for g in H.steel_grades():
    if g["grade"] == "Q235":
        continue
    m = H.lib(g["lib_id"])
    rows.append((g["grade"], g["treatment"], g["Rm"], g["ReL"], m["sb"], m["sy"], m["note"], g["blank_mm"]))

plt = style()
fig, ax = plt.subplots(figsize=(6.4, 2.8))
w = 0.2
for k, (gr, tr, Rm, ReL, sb, sy, note, blank) in enumerate(rows):
    ax.bar(k - 1.5 * w, Rm, w, color="#1f77b4", label=T("试样 Rm", "test piece Rm") if k == 0 else None)
    ax.bar(k - 0.5 * w, sb, w, color="#9ecae1", label=T("设计用 σb", "design σb") if k == 0 else None)
    ax.bar(k + 0.5 * w, ReL, w, color="#d62728", label=T("试样 ReL", "test piece ReL") if k == 0 else None)
    ax.bar(k + 1.5 * w, sy, w, color="#fcae91", label=T("设计用 σs", "design σs") if k == 0 else None)
ax.set_xticks(range(len(rows)))
ax.set_xticklabels([f"{r[0]}\n" + T(f"试样毛坯 {r[7]} mm", f"blank {r[7]} mm") for r in rows], fontsize=6.6)
ax.set_ylabel("MPa", fontsize=7.5)
ax.tick_params(labelsize=6.5)
ax.legend(fontsize=6.4, frameon=False, ncol=4, loc="upper left")
ax.set_ylim(0, 1300)
ax.set_title(T("国标试样（45 钢为正火态）与设计用值（调质，按零件截面尺寸，数字工厂材料库）", "GB test pieces (1045 normalized) versus design values (Q&T, by section size, factory library)"), fontsize=7.6)
fig.tight_layout()
figure(fig, "fig5_2_1")

r = {x[0]: x for x in rows}
c40 = r["40Cr"]
c45 = r["45"]
out(Rm40=c40[2], ReL40=c40[3], sb40=c40[4], sy40=c40[5], drop40_b=100 * (1 - c40[4] / c40[2]), drop40_y=100 * (1 - c40[5] / c40[3]),
    Rm45=c45[2], ReL45=c45[3], sb45=c45[4], sy45=c45[5],
    Rm20=r["20CrMnTi"][2], ReL20=r["20CrMnTi"][3], sb20=r["20CrMnTi"][4], sy20=r["20CrMnTi"][5])
