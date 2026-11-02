"""算例 18.1.1—18.1.4：问题有多大、CASP 的口径、四个指标各测什么（18.1 节）。

（1）序列与实验结构的差距有多大。
（2）两种完全不同的"错"：整个域摆一下，与每个残基各抖一点。
（3）四个指标在这两种错上给出**方向相反**的结论——这正是"该看哪个指标"要先问清楚的理由。
（4）随机结构对的基线：TM-score 约 0.17、lDDT 约 0.20，核对论文给的值。
"""
import numpy as np

from _ch18 import (gdt_ts, hinge, jitter, lddt, random_chain, rmsd, tm_score,
                   two_domain)
from bio_facts import CASP, CASP14, METRICS, SCALE
from bookout import out

v = {}

# ---------- （1）问题的规模
v["pdb"] = SCALE["pdb_entries"]
v["pdb_as_of"] = SCALE["pdb_as_of"]
v["pdb_w"] = SCALE["pdb_entries"] / 1e4
v["sprot"] = SCALE["uniprot_sprot"]
v["trembl"] = SCALE["uniprot_trembl"]
v["trembl_y"] = SCALE["uniprot_trembl"] / 1e8
v["uniprot_release"] = SCALE["uniprot_release"]
v["gap_ratio"] = SCALE["uniprot_trembl"] / SCALE["pdb_entries"]     # 折算，只能当量级说
v["afdb_y"] = SCALE["afdb_sequences"] / 1e8
v["afdb_as_of"] = SCALE["afdb_as_of"]
v["afdb_unit"] = SCALE["afdb_unit"]
v["human_exp_cov"] = SCALE["human_residue_coverage_exp_pct"]
assert v["gap_ratio"] > 100, "序列比实验结构多两个量级以上——这是本章问题的来由"

# ---------- （2）CASP 的口径（只写官方可核的那几条）
v["casp_cadence"] = CASP["cadence_years"]
v["casp14_targets"], v["casp14_units"] = CASP["casp14_targets"], CASP["casp14_units"]
v["casp15_targets"], v["casp15_units"] = CASP["casp15_targets"], CASP["casp15_units"]
v["casp_ranking"] = CASP["ranking"]
v["z_af2"], v["z_second"] = CASP14["official_z_af2"], CASP14["official_z_second"]
v["z_ratio"] = CASP14["official_z_af2"] / CASP14["official_z_second"]   # 折算
v["af2_median_domain"] = CASP14["af2_median_domain_gdt_ts"]
v["af2_n_domains"] = CASP14["af2_median_n_domains"]
v["gdt90_rmsd"], v["gdt80_rmsd"] = CASP14["gdt90_rmsd_a"], CASP14["gdt80_rmsd_a"]

# ---------- （3）两种错，四个指标
ref = two_domain()
v["n_res"] = len(ref)
v["lddt_radius"] = METRICS["lddt_radius_a"]

# 15 Å 之内的残基对里，域间的占多少——这决定了 lDDT 对域摆动有多不敏感
d = np.linalg.norm(ref[:, None] - ref[None, :], axis=-1)
ii, jj = np.triu_indices(len(ref), k=2)
near = d[ii, jj] < METRICS["lddt_radius_a"]
half = len(ref) // 2
v["inter_frac_pct"] = float(((ii[near] < half) != (jj[near] < half)).mean() * 100)

v["hinge_rows"], v["jit_rows"] = [], []
for ang in (15, 30, 60, 90):
    m = hinge(ref, ang)
    row = (ang, round(rmsd(m, ref), 2), round(gdt_ts(m, ref), 1),
           round(lddt(m, ref), 3), round(tm_score(m, ref), 3))
    v["hinge_rows"].append(row)
    v[f"h{ang}_rmsd"], v[f"h{ang}_gdt"], v[f"h{ang}_lddt"], v[f"h{ang}_tm"] = row[1:]
for s in (0.5, 1.0, 1.5, 2.0):
    m = jitter(ref, s)
    tag = str(s).replace(".", "p")
    row = (s, round(rmsd(m, ref), 2), round(gdt_ts(m, ref), 1),
           round(lddt(m, ref), 3), round(tm_score(m, ref), 3))
    v["jit_rows"].append(row)
    v[f"j{tag}_rmsd"], v[f"j{tag}_gdt"], v[f"j{tag}_lddt"], v[f"j{tag}_tm"] = row[1:]

assert v["h90_lddt"] > 0.95, "整个域摆 90°，lDDT 几乎不扣分——它不做叠合"
assert v["h90_gdt"] < 40, "同一件事上 GDT_TS 塌掉——它要叠合"
assert v["j1p0_lddt"] < 0.75 and v["j1p0_tm"] > 0.8, \
    "反过来：每个残基各抖 1 Å，整体折叠还在（TM 高），局部环境全乱（lDDT 低）"

# 两个指标在两种错上的"排序"正好相反——这是本节最该记住的一张表
v["swap"] = (v["h90_lddt"] > v["j1p0_lddt"]) and (v["h90_gdt"] < v["j1p0_gdt"])
assert v["swap"], "一个说前者好、一个说后者好：拿一个指标做判断必然出错"

# ---------- （4）随机结构的基线
tms, lds = [], []
for sd in range(20):
    r = random_chain(len(ref), seed=100 + sd)
    tms.append(tm_score(r, ref)); lds.append(lddt(r, ref))
v["rand_tm"] = float(np.mean(tms))
v["rand_lddt"] = float(np.mean(lds))
v["tm_random_paper"] = METRICS["tm_random"]
v["lddt_random_paper"] = METRICS["lddt_random"]
assert abs(v["rand_tm"] - METRICS["tm_random"]) < 0.08, "与论文给的 0.17 量级一致"
assert abs(v["rand_lddt"] - METRICS["lddt_random"]) < 0.08, "与论文给的 0.20 量级一致"

v["corr_tm"], v["corr_gdt"] = METRICS["corr_tm"], METRICS["corr_gdt"]
v["tm_d0_300"], v["tm_d0_50"] = METRICS["tm_d0_300"], METRICS["tm_d0_50"]
v["no_conversion"] = METRICS["no_conversion"]
v["tm_fold_threshold_known"] = METRICS["tm_fold_threshold"] is not None
assert not v["tm_fold_threshold_known"], \
    "流传的'TM-score 0.5 以上算同折叠'在原论文里没有——不要印"

out(**v)
