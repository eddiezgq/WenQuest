"""图 7.5.1：减速器试验台的六次试验，五个频率处的振动幅值。试验 4、5、6 分别等于试验 1+2、2+3、1+2+3（叠加原理），
是“多余的”记录；秩为 3。"""
import numpy as np

from _fig import BLUE, GREEN, MUTED, RED, T, figure, plt
from _rec import FREQS, FREQS_EN, RECORDS

fig, ax = plt.subplots(figsize=(9.6, 3.8))
x = np.arange(5)
cols = [BLUE, GREEN, RED, "#8a8a8a", "#a8a8a8", "#c8c8c8"]
names = [T("试验 1：齿轮啮合", "run 1: gear mesh"), T("试验 2：轴承", "run 2: bearing"), T("试验 3：不平衡", "run 3: unbalance"),
         T("试验 4 = 1 + 2", "run 4 = 1 + 2"), T("试验 5 = 2 + 3", "run 5 = 2 + 3"), T("试验 6 = 1 + 2 + 3", "run 6 = 1 + 2 + 3")]
for i in range(6):
    ax.bar(x + (i - 2.5) * 0.13, RECORDS[i], width=0.13, color=cols[i], label=names[i], edgecolor="white")
ax.set_xticks(x)
ax.set_xticklabels([T(a, b) for a, b in zip(FREQS, FREQS_EN)])
ax.set_ylabel(T("振动幅值 / (mm/s)", "amplitude / (mm/s)"))
ax.legend(frameon=False, fontsize=8, ncol=2)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig7_5_1")
