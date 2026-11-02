"""算例 18.7.1—18.7.4：案例——预测出来的结构，哪几段能信、能拿去做什么（18.7 节）。

实际问题：一个酶在反应釜里不够耐热，要改造它。手上只有一个**预测**的结构和一张逐残基的
自评分数图。要回答三件事：
（1）分数与真实误差的关系有多紧？自评 90 分以上到底意味着什么？
（2）按官方的四档分，各档的误差是什么样？"高分也会错"的那一撮有多大？
（3）能不能拿预测结构直接挑"改哪个位点最稳"？（公开实验给的相关性只有 −0.17，本例把这个
    相关性能买回多少算出来。）
（4）结论怎么写：哪些用途可以，哪些不可以。
"""
import numpy as np

from _ch18 import band_stats, protein_regions
from bio_facts import ESMFOLD, LIMITS, MUTATION, PLDDT
from bookout import out

R_IN = 0.68          # 按整条蛋白算出来的相关系数约 0.76，与论文那条拟合一致（见下面的断言）
N_CORE, N_LINK, N_TAIL = 150, 40, 30
BAD = 2.0            # 本例把"误差大于 2 Å"当作"这一段不能用来看细节"

v = {"n_core": N_CORE, "n_link": N_LINK, "n_tail": N_TAIL,
     "n_res": N_CORE + N_LINK + N_TAIL, "bad_cut": BAD}

score, err, region = protein_regions(N_CORE, N_LINK, N_TAIL, R_IN, seed=0)
v["corr_measured"] = round(float(np.corrcoef(score, -np.log(err))[0, 1]), 3)
v["corr_paper"] = PLDDT["fit_r"]
assert abs(v["corr_measured"] - PLDDT["fit_r"]) < 0.05, \
    "本例的相关系数照论文那条拟合取 0.76——下面所有结论都是'在这个相关性下'的结论"

# ---------- （1）（2）四档各是什么样
v["bands"] = []
for lo, hi, tag in ((90, 101, "90"), (70, 90, "70"), (50, 70, "50"), (0, 50, "0")):
    n, med, bad = band_stats(score, err, lo, hi, BAD)
    v["bands"].append((lo, min(hi, 100), n, round(med, 2), round(bad, 1)))
    v[f"n_{tag}"], v[f"med_{tag}"], v[f"bad_{tag}"] = n, round(med, 2), round(bad, 1)

assert v["med_90"] < 1.0, "最高档的中位误差在一埃以内——这一档确实可以用来看细节"
assert 0 < v["bad_90"] < 15, \
    "**但最高档里仍然有一撮误差大于 2 Å**——这就是 r = 0.76 的含义，不是'对的概率'"
assert v["med_0"] > 4 * v["med_90"], "最低档与最高档差着好几倍"
v["bad_90_count"] = int(round(v["n_90"] * v["bad_90"] / 100))

# ---------- （3）三段各自什么样
v["regions"] = []
for k, name in enumerate(("核心域", "连接段", "末端尾巴")):
    sel = region == k
    v["regions"].append((name, int(sel.sum()), round(float(np.median(score[sel])), 1),
                         round(float(np.median(err[sel])), 2)))
    tag = ("core", "link", "tail")[k]
    v[f"{tag}_score"] = round(float(np.median(score[sel])), 1)
    v[f"{tag}_err"] = round(float(np.median(err[sel])), 2)
assert v["core_score"] > 80 > v["link_score"] > v["tail_score"], \
    "核心域分数高、连接段与尾巴低——这与官方说的'低分常是无序区'对得上"
v["disorder_quote"] = PLDDT["quotes"]["disorder"]
v["not_always_quote"] = PLDDT["quotes"]["not_always_disorder"]
v["genuine_quote"] = PLDDT["quotes"]["genuine_failure"]
v["user_quote"] = PLDDT["quotes"]["user_judges"]

# ---------- （4）能不能拿它挑突变位点
# 公开实验：ΔpLDDT 与 ΔΔG 的相关系数只有 −0.17（Pak 等 2023）。
# 这里算的是："只有这么点相关性，按它排序挑前 10 个，能比随便挑好多少。"
v["mut_corr"] = MUTATION["corr_dplddt_ddg"]
v["mut_n"], v["mut_proteins"] = MUTATION["n_mutations"], MUTATION["n_proteins"]
v["mut_conclusion"] = MUTATION["conclusion"]

g = np.random.default_rng(7)
N_MUT, TOP, TRIALS = 200, 10, 4000
good_frac = 0.15                     # 真正能提高稳定性的突变只占一成半——这是经验上的常态
rho = abs(MUTATION["corr_dplddt_ddg"])
hits, rand_hits = [], []
for _ in range(TRIALS):
    truth = g.normal(size=N_MUT)
    signal = rho * truth + np.sqrt(1 - rho ** 2) * g.normal(size=N_MUT)
    cut = np.quantile(truth, 1 - good_frac)
    good = truth > cut
    hits.append(good[np.argsort(-signal)[:TOP]].mean())
    rand_hits.append(good[g.permutation(N_MUT)[:TOP]].mean())
v["mut_top_pct"] = round(float(np.mean(hits)) * 100, 1)
v["mut_rand_pct"] = round(float(np.mean(rand_hits)) * 100, 1)
v["mut_lift"] = round(v["mut_top_pct"] / v["mut_rand_pct"], 2)
v["mut_n_candidates"], v["mut_top"] = N_MUT, TOP
v["mut_miss_pct"] = round(100 - v["mut_top_pct"], 1)
assert v["mut_lift"] < 2.0, \
    "相关系数 −0.17 换算下来，按它排序挑前十个只比随便挑好六成左右——离'能当判据'差得远"
assert v["mut_top_pct"] > v["mut_rand_pct"], "也不是完全没用，只是远不够当判据"
assert v["mut_miss_pct"] > 70, \
    "挑出来的前十个里仍有七成以上不是稳定化突变——湿实验照做不误"

# ---------- （5）这一章的工具在这个案例里要花多久
v["esm_sec"], v["esm_len"] = ESMFOLD["sec_384res_v100"], ESMFOLD["ref_len"]
v["esm_gpu"] = ESMFOLD["ref_gpu"]
v["esm_speedup"], v["esm_speedup_max"] = ESMFOLD["speedup_typical"], ESMFOLD["speedup_max"]
v["msa_min"] = ESMFOLD["msa_search_min_high"]
v["cameo_esmfold"], v["cameo_af2"] = ESMFOLD["cameo_esmfold"], ESMFOLD["cameo_af2"]
v["casp14_esmfold"], v["casp14_af2"] = ESMFOLD["casp14_esmfold"], ESMFOLD["casp14_af2"]
v["same_input"] = ESMFOLD["same_input"]
assert not v["same_input"], \
    "AF2 那两列是'带 MSA 与模板'的设置，与 ESMFold 的单序列不是同一个输入条件"
v["needs_experiment"] = LIMITS["needs_experiment"]

out(**v)
