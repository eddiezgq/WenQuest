"""21.99 节“公开发表的数字”那张表里的每个数。

数据全部来自 `conventions/mfg_facts.py`（只收论文正文、官方标准文本、官方指南或官方数据集
说明给出的原始值）。这个程序基本不做计算，只把数交给正文——表里没有一个手打的数字。

算出来的只有两类，而且都在同一口径内：
1. 公开数据集内部的比例（训练集占比、缺陷类型的平均个数）；
2. 由标准系数直接推出的量（三倍标准差控制限的虚发警报间隔）。
"""
from mfg_facts import BEARING, CFR_820_30, CMAPSS, CWRU, MVTEC, PCCP, QMSR, SPC, check
from bookout import out

check()          # 口径断言：错一处就不让构建过去

v = {
    # ---------- 公开振动数据
    "cwru_hp": CWRU["motor_hp"],
    "cwru_fs": CWRU["fs_all_hz"],
    "cwru_fs_de": CWRU["fs_drive_end_hz"],
    "cwru_d_min": CWRU["fault_diameters_mil"][0],
    "cwru_d_max": CWRU["fault_diameters_mil"][-1],
    "cwru_n_d": len(CWRU["fault_diameters_mil"]),
    "cwru_load_min": CWRU["loads_hp"][0],
    "cwru_load_max": CWRU["loads_hp"][-1],
    "cwru_rpm_hi": CWRU["rpms"][0],
    "cwru_rpm_lo": CWRU["rpms"][-1],
    "cwru_rpm_span": CWRU["rpms"][0] - CWRU["rpms"][-1],
    "balls": BEARING["n_balls"],
    "d_ball": BEARING["d_ball_mm"],
    "d_pitch": BEARING["d_pitch_mm"],
    # ---------- 剩余寿命数据
    "cm_fd1_train": CMAPSS["subsets"]["FD001"]["train"],
    "cm_fd1_test": CMAPSS["subsets"]["FD001"]["test"],
    "cm_fd2_train": CMAPSS["subsets"]["FD002"]["train"],
    "cm_fd2_test": CMAPSS["subsets"]["FD002"]["test"],
    "cm_fd4_train": CMAPSS["subsets"]["FD004"]["train"],
    "cm_fd4_test": CMAPSS["subsets"]["FD004"]["test"],
    "cm_cond_max": max(s["conditions"] for s in CMAPSS["subsets"].values()),
    "cm_mode_max": max(s["modes"] for s in CMAPSS["subsets"].values()),
    # ---------- 视觉缺陷数据
    "mv_images": MVTEC["n_images"],
    "mv_cats": MVTEC["n_categories"],
    "mv_tex": MVTEC["n_textures"],
    "mv_obj": MVTEC["n_objects"],
    "mv_defects": MVTEC["n_defect_types"],
    "mv_train": MVTEC["n_train"],
    "mv_test": MVTEC["n_test"],
    "mv_res_min": MVTEC["res_min"],
    "mv_res_max": MVTEC["res_max"],
    # ---------- 受监管行业
    "cfr_n_sub": len(CFR_820_30["subsections"]),
    "qmsr_effective": QMSR["effective"],
    "qmsr_published": QMSR["published"],
    "qmsr_standard": QMSR["incorporates"],
    "pccp_vol": PCCP["fr_volume"],
    "pccp_num": PCCP["fr_number"],
    "pccp_pages": PCCP["fr_pages"],
    "pccp_date": PCCP["date"],
    "pccp_docket": PCCP["docket"],
    "pccp_parts": "；".join(PCCP["three_parts"]),
    # ---------- 统计过程控制
    "a2_5": SPC["a2"][5],
    "d2_5": SPC["d2"][5],
    "d4_5": SPC["d4"][5],
    "false_alarm_p": SPC["three_sigma_false_alarm"],
    "arl0_theory": SPC["arl0_theory"],
}

# 两类算出来的量
v["mv_train_share"] = v["mv_train"] / v["mv_images"] * 100
v["mv_defect_per_cat"] = v["mv_defects"] / v["mv_cats"]
v["arl0_from_p"] = 1.0 / v["false_alarm_p"]
v["cm_fd4_over_fd1"] = v["cm_fd4_train"] / v["cm_fd1_train"]

print(f"公开轴承数据：{v['cwru_hp']} 马力电机，{v['cwru_n_d']} 档人为故障直径"
      f"（{v['cwru_d_min']}—{v['cwru_d_max']} 密耳，电火花加工），"
      f"采样 {v['cwru_fs']:,} Hz（驱动端另有 {v['cwru_fs_de']:,} Hz）；"
      f"负载 {v['cwru_load_min']}—{v['cwru_load_max']} 马力对应转速 "
      f"{v['cwru_rpm_hi']}—{v['cwru_rpm_lo']} r/min（差 {v['cwru_rpm_span']}）")
print(f"剩余寿命数据：最简单的子集 {v['cm_fd1_train']}/{v['cm_fd1_test']} 台，"
      f"最复杂的 {v['cm_fd4_train']}/{v['cm_fd4_test']} 台，"
      f"工况最多 {v['cm_cond_max']} 种、故障模式最多 {v['cm_mode_max']} 种")
print(f"视觉缺陷数据：{v['mv_images']:,} 张、{v['mv_cats']} 类、{v['mv_defects']} 种缺陷"
      f"（平均每类 {v['mv_defect_per_cat']:.1f} 种），"
      f"训练集占 {v['mv_train_share']:.0f}% 且**只有好件**")
print(f"受监管行业：设计控制 {v['cfr_n_sub']} 个小节；质量管理体系法规 {v['qmsr_effective']} 生效，"
      f"纳入 {v['qmsr_standard']}；预定变更控制计划终稿 {v['pccp_date']}"
      f"（联邦公报 {v['pccp_vol']} 卷 {v['pccp_num']} 号，{v['pccp_pages']} 页）")
print(f"统计过程控制：子组大小 5 时 A₂={v['a2_5']}、d₂={v['d2_5']}、D₄={v['d4_5']}；"
      f"三倍标准差控制限的虚发概率 {v['false_alarm_p']}，即平均每 {v['arl0_from_p']:.0f} 个子组一次")

out(**v)
