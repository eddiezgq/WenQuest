"""20.99 节“公开发表的数字”那几张表里的每个数。

数据全部来自 `conventions/mat_facts.py`（只收论文正文、官方文档或官方公告的原始数字）。
这个程序基本不做计算，只把数交给正文——表里没有一个手打的数字，改一处只改数据那一处。

算出来的只有三类，而且每一类都是**同一口径内**的对照：
1. 公告承诺的贡献数与数据库实际收录数之比（同一个数据库、同一件事）；
2. 同一篇文章里正文与编辑摘要的差、以及独立复核把成功率改判了多少（同一批样品）；
3. 两种重稀土氧化物的价格之比与一年的涨跌（同一个来源、同一口径的离岸价）。

**不做的对照**：不同论文之间的绝对值比较、跨口径的"稳定材料个数"相加、
把矿山产量占比说成分离或磁体制造占比——这些在资料卡里逐条标了不可比。
"""
from mat_facts import (ALAB, ALAB_REVIEW, GNOME, GNOME_REVIEW, HEAVY_RE, M3GNET_SCREEN,
                       MAGNET_ML, METASTABLE, MLIP_LIMITS, MP_INTAKE, NDFEB, RE_FREE,
                       THRESHOLDS, check)
from bookout import out

check()          # 口径断言：错一处就不让构建过去

v = {
    # ---------- 一、大规模发现：论文自己怎么说
    "gnome_m": GNOME["n_structures_m"],
    "gnome_new_k": GNOME["n_new_hull_k"],
    "gnome_total_k": GNOME["n_total_stable_k"],
    "gnome_al_mev": GNOME["active_learning_mev"],
    "gnome_r2scan_bt": GNOME["r2scan_binary_ternary_pct"],
    "gnome_r2scan_q": GNOME["r2scan_quaternary_pct"],
    "gnome_realized": GNOME["n_already_realized"],
    "gnome_new_since": GNOME["n_new_since_project"],
    "gnome_hit": GNOME["hit_rate_pct"],
    "gnome_promised_k": GNOME["announced_contribution_k"],
    # ---------- 二、数据库实际收录
    "mp_2024_12": MP_INTAKE["v2024_12_18_added"],
    "mp_2026_04": MP_INTAKE["v2026_04_13_added_r2scan"],
    "mp_deprecated": MP_INTAKE["v2024_11_14_deprecated"],
    # ---------- 三、独立复核（结构）
    "rev_sampled": GNOME_REVIEW["n_sampled_stable"],
    "rev_in_icsd": GNOME_REVIEW["n_found_in_icsd"],
    "rev_same_sg": GNOME_REVIEW["n_same_space_group"],
    "rev_first_n": GNOME_REVIEW["n_first_entries_examined"],
    "rev_explorer": GNOME_REVIEW["n_gnome_explorer"],
    "rev_stable_db": GNOME_REVIEW["n_stable_db"],
    "rev_radioactive": GNOME_REVIEW["n_radioactive"],
    "rev_top4_sg": GNOME_REVIEW["top4_space_group_pct"],
    # ---------- 四、自主实验室与它的复核
    "alab_days": ALAB["days"],
    "alab_made": ALAB["n_realized_body"],
    "alab_targets": ALAB["n_targets_body"],
    "alab_made_ed": ALAB["n_realized_editorial"],
    "alab_targets_ed": ALAB["n_targets_editorial"],
    "alab_exp": ALAB["n_experiments"],
    "alab_recipe_pct": ALAB["recipe_success_pct"],
    "alab_thr_mev": ALAB["target_hull_mev"],
    "alab_failed": ALAB["n_failed"],
    "alab_failed_kin": ALAB["n_failed_kinetics"],
    "rev2_examined": ALAB_REVIEW["n_examined"],
    "rev2_issues": ALAB_REVIEW["n_with_issues"],
    "rev2_opposite": ALAB_REVIEW["n_opposite_conclusion"],
    "rev2_made": ALAB_REVIEW["revised_success"],
    "rev2_total": ALAB_REVIEW["revised_total"],
    "rev2_pct": ALAB_REVIEW["revised_pct"],
    "rev2_known": ALAB_REVIEW["n_revised_already_known"],
    "rev2_no_order": ALAB_REVIEW["n_no_cation_order"],
    # ---------- 五、亚稳程度（"稳定"这个词的地基）
    "meta_median": METASTABLE["median_mev"],
    "meta_median_err": METASTABLE["median_err"],
    "meta_p90": METASTABLE["p90_mev"],
    "meta_p90_err": METASTABLE["p90_err"],
    "meta_nitride_median": METASTABLE["nitride_median_mev"],
    "meta_nitride_p90": METASTABLE["nitride_p90_mev"],
    "meta_oxide_p90": METASTABLE["binary_oxide_p90_mev"],
    "meta_n": METASTABLE["n_entries"],
    "meta_pct": METASTABLE["metastable_pct"],
    "meta_pct_err": METASTABLE["metastable_pct_err"],
    "meta_range": METASTABLE["observed_range_mev"],
    # 三个工程阈值（口径互不相同，不能混用）
    "thr_alab": THRESHOLDS["alab_target_mev"],
    "thr_gnome": THRESHOLDS["gnome_active_learning_mev"],
    "thr_matbench": THRESHOLDS["matbench_classify_mev"],
    # 另一次大规模筛选
    "m3_gen": M3GNET_SCREEN["n_generated"],
    "m3_below": M3GNET_SCREEN["n_below_1mev"],
    "m3_dft": M3GNET_SCREEN["n_dft_checked"],
    "m3_ok": M3GNET_SCREEN["n_dft_confirmed"],
    # ---------- 六、机器学习势自己承认的局限
    "chgnet_moment": MLIP_LIMITS["chgnet_moment_mae_ub"],
    # ---------- 七、永磁与重稀土
    "ndfeb_ha": NDFEB["anisotropy_field_t"],
    "ndfeb_ms": NDFEB["saturation_t"],
    "ndfeb_tc": NDFEB["curie_c"],
    "ndfeb_bh": NDFEB["n50_bhmax_kj_m3"],
    "ndfeb_hc160": NDFEB["hc_at_160c_t"],
    "motor_t": NDFEB["motor_op_temp_c"],
    "beta_dyfree": NDFEB["beta_hc_dy_free"],
    "beta_ndcu": NDFEB["beta_hc_ndcu"],
    "beta_tb": NDFEB["beta_hc_tb"],
    "beta_ce": NDFEB["beta_hc_ce"],
    "gbd_cap": NDFEB["gbd_dy_free_max_t"],
    "gbd_dy_wt": NDFEB["gbd_dy_wt_pct"],
    "gbd_from": NDFEB["gbd_from_t"],
    "gbd_to": NDFEB["gbd_to_t"],
    "us_reliance": HEAVY_RE["us_import_reliance_pct"],
    "cn_tb": HEAVY_RE["from_china_pct"]["terbium"],
    "cn_ho": HEAVY_RE["from_china_pct"]["holmium"],
    "cn_lu": HEAVY_RE["from_china_pct"]["lutetium"],
    "cn_yb": HEAVY_RE["from_china_pct"]["ytterbium"],
    "cn_er": HEAVY_RE["from_china_pct"]["erbium"],
    "dy_price": HEAVY_RE["dy_oxide_usd_kg_2025e"],
    "dy_price_prev": HEAVY_RE["dy_oxide_usd_kg_2024"],
    "tb_price": HEAVY_RE["tb_oxide_usd_kg_2025e"],
    "tb_price_prev": HEAVY_RE["tb_oxide_usd_kg_2024"],
    "nd_price": HEAVY_RE["nd_oxide_usd_kg_2025e"],
    "world_mine": HEAVY_RE["world_mine_production_t_2025e"],
    "cn_mine": HEAVY_RE["china_mine_production_t_2025e"],
    "cn_mine_share": HEAVY_RE["china_mine_share_pct_derived"],
    # 无稀土路线（只收综述写出条件的实验值）
    "fe16n2_ms": RE_FREE["fe16n2_ms_emu_cm3"],
    "fe16n2_hc_ball": RE_FREE["fe16n2_hc_oe_ballmill"],
    "fe16n2_hc_foil": RE_FREE["fe16n2_hc_oe_foil"],
    "fe16n2_bh_calc": RE_FREE["fe16n2_bhmax_mgoe_calculated"],
    # 用机器学习筛永磁：是表格回归，不是势、也不是图网络
    "mag_n_exp": MAGNET_ML["n_experimental"],
    "mag_n_sim": MAGNET_ML["n_micromagnetic"],
    "mag_r2": MAGNET_ML["xgb_r2"],
    "mag_mse": MAGNET_ML["xgb_mse"],
    "mag_ann_r2": MAGNET_ML["ann_r2"],
}

# ---------- 算出来的三类对照（都在同一口径内）

# 1）公告承诺 380,000 条，数据库两版实际收录多少，以及撤回了多少
v["mp_added_total"] = v["mp_2024_12"] + v["mp_2026_04"]
v["promise_over_actual"] = v["gnome_promised_k"] * 1000 / v["mp_added_total"]
# “已被独立实验实现”的 736 个里，真正算新发现的只占多少
v["new_share_of_realized"] = v["gnome_new_since"] / v["gnome_realized"] * 100

# 2）同一篇文章正文与编辑摘要差几个；独立复核把成功率压到几分之一
v["alab_editorial_gap"] = v["alab_made_ed"] - v["alab_made"]
v["alab_body_pct"] = v["alab_made"] / v["alab_targets"] * 100
v["rev2_shrink"] = v["alab_body_pct"] / v["rev2_pct"]
v["rev2_truly_new"] = v["rev2_made"] - v["rev2_known"]

# 3）两种氧化物的价差与一年的涨跌（同一来源、同一口径）
v["tb_over_dy"] = v["tb_price"] / v["dy_price"]
v["tb_over_nd"] = v["tb_price"] / v["nd_price"]
v["dy_yoy_pct"] = (v["dy_price"] - v["dy_price_prev"]) / v["dy_price_prev"] * 100
v["tb_yoy_pct"] = (v["tb_price"] - v["tb_price_prev"]) / v["tb_price_prev"] * 100

# 另外两个一眼能看出分量的比：筛出来的里有多少真去算了，以及算了的里多少过关
v["m3_dft_share"] = v["m3_dft"] / v["m3_below"] * 100
v["m3_ok_pct"] = v["m3_ok"] / v["m3_dft"] * 100

print(f"公告承诺向数据库贡献 {v['gnome_promised_k']},000 条，"
      f"两版实际收录合计 {v['mp_added_total']} 条，差 {v['promise_over_actual']:.0f} 倍；"
      f"同期还撤回 {v['mp_deprecated']} 条")
print(f"{v['gnome_realized']} 个已被独立实验实现，其中项目开始后才有的新发现 "
      f"{v['gnome_new_since']} 个（占 {v['new_share_of_realized']:.0f}%）")
print(f"自主实验室：正文 {v['alab_made']}/{v['alab_targets']}（{v['alab_body_pct']:.0f}%），"
      f"编辑摘要写 {v['alab_made_ed']}/{v['alab_targets_ed']}（差 {v['alab_editorial_gap']} 个）；"
      f"独立复核改判为 {v['rev2_made']}/{v['rev2_total']}（{v['rev2_pct']}%），"
      f"压到原来的 {v['rev2_shrink']:.0f} 分之一，而且这 {v['rev2_made']} 个里只有 "
      f"{v['rev2_truly_new']} 个此前未知")
print(f"亚稳程度：中位 {v['meta_median']} ± {v['meta_median_err']}、"
      f"90 分位 {v['meta_p90']} ± {v['meta_p90_err']} meV/atom；"
      f"氮化物中位就到 {v['meta_nitride_median']}、90 分位 {v['meta_nitride_p90']}")
print(f"三个工程阈值互不相同：选靶 {v['thr_alab']}、主动学习 {v['thr_gnome']}、"
      f"基准分类 {v['thr_matbench']} meV/atom")
print(f"重稀土：美国净进口依赖度 {v['us_reliance']}%；"
      f"铽氧化物 {v['tb_price']} 美元/公斤是镝氧化物的 {v['tb_over_dy']:.1f} 倍、"
      f"钕氧化物的 {v['tb_over_nd']:.0f} 倍；一年里镝 {v['dy_yoy_pct']:+.0f}%、"
      f"铽 {v['tb_yoy_pct']:+.0f}%")

out(**v)
