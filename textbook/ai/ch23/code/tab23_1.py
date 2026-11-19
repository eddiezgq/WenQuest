"""第 23 章正文里要印的公开数字，一处定义、处处引用。

数据全部来自 `conventions/drive_facts.py`（只收标准官方页、法规条文、监管机构官方文档、
论文正文与厂家官方规格页的原始值）。这个程序几乎不做计算，只把数交给正文——正文里
没有一个手打的数字。

算出来的只有两类，而且都在同一口径内：
1. 同一份材料内部的对照（两个数据集的标注频率之比、同一家官网两页的算力差）；
2. 本书自己的量纲折算，**逐条标明**（场景时长折成小时一类）。

口径不全的数一律不在这里出现——它们在 `drive_facts.NOT_PRINTED` 里，正文只说"不印"
和"为什么不印"。
"""
from drive_facts import (CA_DISENGAGEMENT, DATASET_NOT_COMPARABLE, DRIVE_ORIN, DRIVE_THOR,
                         ISO_SAE_22736_DEFS, J3016, JETSON_CONFLICT, LATENCY,
                         LEVEL_DESCRIPTORS_202104, LEVEL_DESCRIPTORS_202609, NHTSA_SGO,
                         NUSCENES, SGO_CAVEATS, WAYMO_OPEN, check)
from bookout import out

check()          # 口径断言：错一处就不让构建过去

v = {
    # ---------- 分级标准（23.1 节）
    "sae_rev": J3016["current_revision"],
    "sae_rev_date": J3016["current_revision_date"],
    "sae_prev": J3016["previous_revision"],
    "sae_prev_date": J3016["previous_revision_date"],
    "sae_n_rev": len(J3016["all_revisions"]),
    "sae_committee": J3016["committee"],
    "sae_doctype": J3016["document_type"],
    "sae_levels": J3016["n_levels"],
    "desc_2_old": LEVEL_DESCRIPTORS_202104[2],
    "desc_3_old": LEVEL_DESCRIPTORS_202104[3],
    "desc_4_old": LEVEL_DESCRIPTORS_202104[4],
    "desc_3_new": LEVEL_DESCRIPTORS_202609[3],
    "desc_4_new": LEVEL_DESCRIPTORS_202609[4],
    "ddt_subtasks": ISO_SAE_22736_DEFS["ddt_subtasks"],
    "ads_lo": ISO_SAE_22736_DEFS["ads_levels"][0],
    "ads_hi": ISO_SAE_22736_DEFS["ads_levels"][-1],

    # ---------- 加州脱离报告（23.7 节）
    "ca_cite": CA_DISENGAGEMENT["citation"],
    "ca_n_situations": CA_DISENGAGEMENT["n_triggering_situations"],
    "ca_start": CA_DISENGAGEMENT["period_start"],
    "ca_end": CA_DISENGAGEMENT["period_end"],
    "ca_due": CA_DISENGAGEMENT["due_date"],
    "ca_form": CA_DISENGAGEMENT["form"],
    "ca_n_loc": CA_DISENGAGEMENT["n_location_categories"],
    "ca_n_initiator": len(CA_DISENGAGEMENT["initiator_options"]),

    # ---------- 事故上报令（23.7 节）
    "sgo_second": NHTSA_SGO["second_amended_effective"],
    "sgo_third": NHTSA_SGO["third_amended_effective"],
    "sgo_window_s": NHTSA_SGO["engagement_window_s"],
    "sgo_1day": NHTSA_SGO["one_day_deadline_days"],
    "sgo_5day": NHTSA_SGO["five_day_deadline_days"],
    "sgo_monthly_day": NHTSA_SGO["monthly_due_day"],
    "sgo_n_1day_triggers": len(NHTSA_SGO["one_day_trigger"]),
    "sgo_n_5day_triggers": len(NHTSA_SGO["five_day_trigger"]),
    "sgo_n_caveats": len(SGO_CAVEATS["six_bullets"]),
    "sgo_dict_date": NHTSA_SGO["data_dictionary_date"],

    # ---------- 两个公开数据集（23.5 节）
    "nus_scenes": NUSCENES["scenes"],
    "nus_sec": NUSCENES["scene_seconds"],
    "nus_keyframes": NUSCENES["keyframes"],
    "nus_key_hz": NUSCENES["keyframe_hz"],
    "nus_boxes": NUSCENES["boxes_3d"],
    "nus_classes": NUSCENES["classes"],
    "nus_cities": NUSCENES["cities"],
    "nus_cams": NUSCENES["cameras"],
    "nus_radars": NUSCENES["radars"],
    "nus_lidars": NUSCENES["lidars"],
    "nus_rain_pct": NUSCENES["rain_pct"],
    "nus_night_pct": NUSCENES["night_pct"],
    "nus_km": NUSCENES["drive_km"],
    "nus_hours": NUSCENES["drive_hours"],
    "way_scenes": WAYMO_OPEN["scenes"],
    "way_sec": WAYMO_OPEN["scene_seconds"],
    "way_hz": WAYMO_OPEN["sample_hz"],
    "way_boxes3d": WAYMO_OPEN["boxes_3d"],
    "way_classes": WAYMO_OPEN["classes"],
    "way_cities": WAYMO_OPEN["cities"],
    "way_lidars": WAYMO_OPEN["lidars"],
    "way_radars": WAYMO_OPEN["radars"],
    "nus_footnote": DATASET_NOT_COMPARABLE["nuscenes_table1_footnote"],
    "n_reasons_not_comparable": len(DATASET_NOT_COMPARABLE["reasons"]),

    # ---------- 车载算力（23.6 节）
    "orin_int8": DRIVE_ORIN["int8_tops"],
    "orin_dla_int8": DRIVE_ORIN["dla_int8_tops"],
    "orin_fp32": DRIVE_ORIN["fp32_tops"],
    "orin_prec": DRIVE_ORIN["precision_stated"],
    "thor_int8": DRIVE_THOR["int8_tops"],
    "thor_fp4": DRIVE_THOR["fp4_flops"],
    "thor_prec": DRIVE_THOR["precision_stated"],
    "nx_a": JETSON_CONFLICT["orin_nx_tops_page_a"],
    "nx_b": JETSON_CONFLICT["orin_nx_tops_page_b"],
    "nano_a": JETSON_CONFLICT["orin_nano_tops_page_a"],
    "nano_b": JETSON_CONFLICT["orin_nano_tops_page_b"],

    # ---------- 中间件时延（23.6 节）
    "aw_before_ms": LATENCY["autoware_perception_to_decision_before_ms"],
    "aw_after_ms": LATENCY["autoware_perception_to_decision_after_ms"],
    "aw_stack": LATENCY["stack"],
    "aw_excludes": LATENCY["excludes"],
}

# ---------- 同一份材料内部的对照
v["dataset_hz_ratio"] = WAYMO_OPEN["sample_hz"] / NUSCENES["keyframe_hz"]
v["dataset_box_ratio"] = WAYMO_OPEN["boxes_3d"] / NUSCENES["boxes_3d"]
v["nx_conflict_pct"] = 100.0 * (JETSON_CONFLICT["orin_nx_tops_page_b"]
                                / JETSON_CONFLICT["orin_nx_tops_page_a"] - 1.0)
v["nano_conflict_pct"] = 100.0 * (JETSON_CONFLICT["orin_nano_tops_page_b"]
                                  / JETSON_CONFLICT["orin_nano_tops_page_a"] - 1.0)
v["orin_int8_over_fp32"] = DRIVE_ORIN["int8_tops"] / DRIVE_ORIN["fp32_tops"]
v["thor_over_orin_int8"] = DRIVE_THOR["int8_tops"] / DRIVE_ORIN["int8_tops"]
v["aw_cut_pct"] = 100.0 * (1.0 - LATENCY["autoware_perception_to_decision_after_ms"]
                           / LATENCY["autoware_perception_to_decision_before_ms"])

# ---------- 本书自己的量纲折算（标明）
# 两个数据集"公开发表时"的场景时长折成小时：场景数 × 每段秒数 ÷ 3600
v["nus_scene_hours_calc"] = NUSCENES["scenes"] * NUSCENES["scene_seconds"] / 3600.0
v["way_scene_hours_calc"] = WAYMO_OPEN["scenes"] * WAYMO_OPEN["scene_seconds"] / 3600.0
# 自查：nuScenes 的关键帧数应当与"场景数 × 每段秒数 × 关键帧频率"对得上
v["nus_keyframes_calc"] = NUSCENES["scenes"] * NUSCENES["scene_seconds"] * NUSCENES["keyframe_hz"]
assert abs(v["nus_keyframes_calc"] - NUSCENES["keyframes"]) < 1, \
    "论文里这两个数应当自洽：1000 段 × 20 s × 2 Hz = 40 000 个关键帧"

print(f"分级标准：{v['sae_rev']}（{v['sae_rev_date']} 改版，上一版 {v['sae_prev']}）；"
      f"{v['sae_committee']} 制定，文件类型是 {v['sae_doctype']}，不是安全标准")
print(f"  等级简称改了：旧版第 3 级叫“{v['desc_3_old']}”，新版写成“{v['desc_3_new'][:48]}…”")
print(f"  **官方明说那些简称不是定义**；等级定义与 ODD 定义的原文在付费正文里，本次未核到")
print(f"脱离报告：{v['ca_cite']}，{v['ca_n_situations']} 种情形要报，"
      f"周期 {v['ca_start']} 到次年 {v['ca_end']}（**不是自然年**），{v['ca_due']} 前交，表号 {v['ca_form']}")
print(f"事故上报：第二次修订令自 {v['sgo_second']} 起（本书引的就是这一版），"
      f"触发窗口“事发前 {v['sgo_window_s']} 秒”；{v['sgo_n_1day_triggers']} 类要 "
      f"{v['sgo_1day']} 天内报、{v['sgo_n_5day_triggers']} 类 {v['sgo_5day']} 天内报")
print(f"  监管方自己列了 {v['sgo_n_caveats']} 条数据局限（数据字典 {v['sgo_dict_date']}）——"
      f"其中一条就是“别拿不同厂家的事故数据互相比”")
print(f"数据集：nuScenes {v['nus_scenes']:,} 段 × {v['nus_sec']} s（本书折算 "
      f"{v['nus_scene_hours_calc']:.1f} 小时）、关键帧 {v['nus_key_hz']} Hz；"
      f"Waymo Open {v['way_scenes']:,} 段 × {v['way_sec']} s、采样 {v['way_hz']} Hz")
print(f"  标注频率差 {v['dataset_hz_ratio']:.0f} 倍，框数差 {v['dataset_box_ratio']:.1f} 倍——"
      f"**nuScenes 自己的表注就说明了这件事**，所以两个数不能当“谁更大”来比")
print(f"算力：DRIVE AGX Orin {v['orin_int8']} TOPS（{v['orin_prec']}，其中深度学习加速器 "
      f"{v['orin_dla_int8']} TOPS；FP32 只有 {v['orin_fp32']}，差 {v['orin_int8_over_fp32']:.0f} 倍）；"
      f"Thor {v['thor_int8']} TOPS（{v['thor_prec']}）")
print(f"  **同一家官网两页自相矛盾**：Orin NX 一页 {v['nx_a']} TOPS、另一页 {v['nx_b']}"
      f"（差 {v['nx_conflict_pct']:.0f}%），Orin Nano {v['nano_a']} 对 {v['nano_b']}——"
      f"两页都没写精度，稀疏化也没标，所以这几个数本书不印")
print(f"中间件时延：{v['aw_stack']} 上 {v['aw_before_ms']:.1f} → {v['aw_after_ms']:.1f} ms"
      f"（降 {v['aw_cut_pct']:.0f}%），但作者明写 {v['aw_excludes']}——**这不是端到端时延**")

out(**v)
