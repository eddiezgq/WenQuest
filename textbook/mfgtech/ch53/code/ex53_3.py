"""53.3 节：概率法。算例 53.3.1 SH-301 齿轮位长度 60：工序 40 总长按 ±0.3 控制时，极值法、概率法、蒙特卡罗的结果；
各种分布（正态、均匀、偏态）的影响；图 53.3.1 蒙特卡罗直方图与极值、概率法界限。"""
import copy

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

TL = M.tol()
p = M.plan()
tc = copy.deepcopy(p["tolerance_chart"])
for c in tc["cuts"]:
    if c["seq"] == 40.3:                     # 假设总长按 ±0.3 控制（第 50 章初稿的值）
        c["es"], c["ei"] = 0.3, -0.3
ch = TL.chart_from_plan(tc)["chart"]
links = ch.chain("S2", "S3")
ext = TL.extreme(links)
st = TL.statistical(links)
uni = TL.statistical_general(links, ["uniform"] * len(links))
mc = TL.monte_carlo(links, n=40_000, dist="normal", seed=3)
mcu = TL.monte_carlo(links, n=40_000, dist="uniform", seed=4)
vals = np.array(mc.detail["values"])
tol = 0.3
frac_out = float(np.mean(np.abs(vals - 60) > tol))
frac_out_u = float(np.mean(np.abs(np.array(mcu.detail["values"]) - 60) > tol))
# 偏态：精车端面时操作工习惯“宁长勿短”，总长偏长。跟踪图里这一环是 R→L 的工序尺寸 −167（负值），总长偏长就是它偏向下限（e = −0.26）
sk = TL.statistical_general(links, ["normal" if "总长" not in l.name else "skew_in" for l in links])

plt = style()
fig, ax = plt.subplots(figsize=(5.6, 2.8))
ax.hist(vals - 60, bins=80, color=M.ACCENT, alpha=0.6, density=True)
for x, col, lab in ((ext.es, M.RED, T("极值法", "worst case")), (st.es, M.WARM, T("概率法", "statistical")), (tol, M.INK, T("图纸 ±0.3", "drawing ±0.3"))):
    ax.axvline(x, color=col, lw=1.2, ls="--" if col != M.INK else "-")
    ax.axvline(-x, color=col, lw=1.2, ls="--" if col != M.INK else "-")
    ax.text(x, ax.get_ylim()[1] * 0.92, lab, fontsize=7, color=col, rotation=90, ha="right", va="top")
ax.set_xlabel(T("齿轮位长度 − 60 / mm", "gear-seat length − 60 / mm"), fontsize=8.5)
ax.set_yticks([])
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
figure(fig, "fig53_3_1")
out(n=len(links), ext_es=ext.es, st_es=st.es, uni_es=uni.es, mc_sd=mc.detail["sd"], mc_3s=3 * mc.detail["sd"], frac_out=frac_out,
    frac_out_u=frac_out_u, mc_max=mc.detail["max"] - 60, sk_mid=sk.detail["mid"], sk_es=sk.es, sk_ei=sk.ei, ratio=ext.T / st.T)

# 实验 53.3 的场景数据与工艺规程、尺寸链数据一致（中间偏差）
from pathlib import Path  # noqa: E402
lab = (Path(__file__).resolve().parents[1] / "lab" / "lab53_3.js").read_text(encoding="utf-8")
H = p["chains"][0]["links"][0]
assert f"mid: {(H['es'] + H['ei']) / 2:g}" in lab
