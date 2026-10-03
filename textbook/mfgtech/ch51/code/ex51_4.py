"""51.4 节：用自由度分析判断四个定位方案：完全定位、不完全定位、欠定位、过定位（算例 51.4.1）。"""
import _mfg as M
from bookout import out

TL = M.tol()
ALL = set(TL.DOF)
cases = {
    # 1 铣长方体上一个不通的槽：六个都要限制
    "blind_slot": ([("底面支承板", {"z", "rx", "ry"}), ("侧面两个支承钉", {"y", "rz"}), ("端面一个支承钉", {"x"})], ALL),
    # 2 铣通槽：沿槽长方向的移动不影响加工
    "through_slot": ([("底面支承板", {"z", "rx", "ry"}), ("侧面两个支承钉", {"y", "rz"})], {"z", "rx", "ry", "y", "rz"}),
    # 3 SH-301 铣键槽只用 V 形块，忘了轴向挡销：键槽长度方向的位置保证不了
    "keyway_no_stop": ([("两个短 V 形块", {"y", "z", "ry", "rz"})], {"x", "y", "z", "ry", "rz"}),
    # 4 SH-301 键槽夹具：V 形块 + 轴向挡销（绕轴线转动由键槽对中决定，不必限制）
    "keyway": ([("两个短 V 形块", {"y", "z", "ry", "rz"}), ("轴向挡销", {"x"})], {"x", "y", "z", "ry", "rz"}),
    # 5 一夹一顶，卡盘长夹持：卡盘 4 个 + 顶尖 2 个，y、z 方向的转动被重复限制
    "long_chuck": ([("卡盘长夹持", {"y", "z", "ry", "rz"}), ("后顶尖", {"ry", "rz"}), ("卡爪端面", {"x"})], {"x", "y", "z", "ry", "rz"}),
    # 6 一夹一顶，卡盘短夹持：卡盘 2 个 + 端面 1 个 + 顶尖 2 个
    "short_chuck": ([("卡盘短夹持", {"y", "z"}), ("卡爪端面", {"x"}), ("后顶尖", {"ry", "rz"})], {"x", "y", "z", "ry", "rz"}),
}
res = {k: TL.dof_analysis(loc, req) for k, (loc, req) in cases.items()}
vals = {}
for k, r in res.items():
    vals[k] = r["verdict"]
    vals[k + "_n"] = r["n"]
    vals[k + "_rep"] = "、".join(TL.DOF_ZH[d] for d in r["repeated"]) or "无"
    vals[k + "_miss"] = "、".join(TL.DOF_ZH[d] for d in r["missing"]) or "无"
out(**vals)
