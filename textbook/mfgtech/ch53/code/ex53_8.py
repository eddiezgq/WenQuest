"""53.8 节：尺寸链的计算机求解与蒙特卡罗模拟。算例 53.8.1 SH-301 键槽深度 d − t₁：各环按实际可能的分布抽样
（铣削 H 和磨削都因“到公差内就停手”而偏向上限，精车正态），与极值法、概率法比较；估计超差率。图 53.8.1。"""
import numpy as np

import _mfg as M
from bookout import T, figure, out, style

TL = M.tol()
p = M.plan()
ch = p["chains"][0]
links = [M.link(l["name"], l["nominal"], l["es"], l["ei"], l["sense"]) for l in ch["links"]]
c5 = next(c for c in p["characteristics"] if c["id"] == ch["char"])
lo, hi = c5["nominal"] + c5["ei"], c5["nominal"] + c5["es"]
ext = TL.extreme(links)
st = TL.statistical(links)
dists = ["skew_out", "normal", "skew_out"]         # 假设改用试切法：H 分层往下铣、到公差内就停，槽偏浅，H 偏向上限；磨削“宁大勿小”，也偏向上限
gen = TL.statistical_general(links, dists)
mcn = TL.monte_carlo(links, n=40_000, dist="normal", seed=5)
mcs = TL.monte_carlo(links, n=40_000, dist=dists, seed=6)
vn, vs = np.array(mcn.detail["values"]), np.array(mcs.detail["values"])
out_n = float(np.mean((vn < lo) | (vn > hi)))
out_s = float(np.mean((vs < lo) | (vs > hi)))
plt = style()
fig, ax = plt.subplots(figsize=(5.6, 2.8))
ax.hist(vn - 35, bins=70, color=M.ACCENT, alpha=0.5, density=True, label=T("各环正态", "all normal"))
ax.hist(vs - 35, bins=70, color=M.WARM, alpha=0.5, density=True, label=T("按实际分布", "realistic distributions"))
for x, col in ((ext.ei, M.RED), (ext.es, M.RED), (c5["ei"], M.INK), (c5["es"], M.INK)):
    ax.axvline(x, color=col, lw=1.0, ls="--" if col == M.RED else "-")
ax.set_xlabel(T("d − t₁ − 35 / mm（黑线：图纸公差；红虚线：极值法）", "d − t₁ − 35 / mm (black: drawing; red dashed: worst case)"), fontsize=8)
ax.set_yticks([]); ax.legend(fontsize=7.5, frameon=False)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
figure(fig, "fig53_8_1")
out(ext_es=ext.es, ext_ei=ext.ei, st_es=st.es, st_ei=st.ei, gen_es=gen.es, gen_ei=gen.ei, gen_mid=gen.detail["mid"],
    mcn_mean=mcn.detail["mean"] - 35, mcn_sd=mcn.detail["sd"], mcs_mean=mcs.detail["mean"] - 35, mcs_sd=mcs.detail["sd"],
    out_n=out_n, out_s=out_s, n=40_000)
