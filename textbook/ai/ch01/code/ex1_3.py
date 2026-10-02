"""算例 1.3.1：ImageNet 竞赛（ILSVRC）分类任务的错误率下降有多快。

数据：_ch1.ILSVRC（各年冠军的前五错误率）。相对下降 = (旧 − 新)/旧；年均变化率按式 (1.3.1)：(e_t/e_0)^{1/t} − 1。
"""
from _ch1 import HUMAN_TOP5, ILSVRC, ILSVRC_2012_SECOND, TIMELINE
from bookout import out

e = {y: v for y, v, _ in ILSVRC}
rel_vs_second = (ILSVRC_2012_SECOND - e[2012]) / ILSVRC_2012_SECOND
rel_vs_2011 = (e[2011] - e[2012]) / e[2011]
rel_10_11 = (e[2010] - e[2011]) / e[2010]
factor = e[2010] / e[2015]
years = 2015 - 2010
annual = (e[2015] / e[2010]) ** (1 / years) - 1
first_below_human = min(y for y, v, _ in ILSVRC if v < HUMAN_TOP5)

gap_dartmouth_alexnet = 2012 - 1956
gap_perceptron_alexnet = 2012 - 1958
gap_bp_alexnet = 2012 - 1986
n_events = len(TIMELINE)

out(e2010=e[2010], e2011=e[2011], e2012=e[2012], e2015=e[2015], second=ILSVRC_2012_SECOND,
    rel_vs_second_pct=rel_vs_second * 100, rel_vs_2011_pct=rel_vs_2011 * 100, rel_10_11_pct=rel_10_11 * 100,
    factor=factor, annual_pct=annual * 100, first_below_human=first_below_human, human=HUMAN_TOP5,
    gap_dartmouth_alexnet=gap_dartmouth_alexnet, gap_perceptron_alexnet=gap_perceptron_alexnet,
    gap_bp_alexnet=gap_bp_alexnet, n_events=n_events)
