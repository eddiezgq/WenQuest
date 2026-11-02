"""算例 18.3.1—18.3.2：复合物难在界面，不难在单链（18.3 节）。

（1）把 18.1 节那个"两个域"换个身份读：它就是一个两条链的复合物。每条链各自预测得很好，
    中心位置也对，只是第二条链**拿错了面**朝向对方——这时单链指标一点看不出来，界面全塌。
（2）DockQ 的四档分界（照抄官方定义，本书不自造 DockQ 的具体数值）。
"""
import numpy as np

from _ch18 import (chain_quality, fnat, gdt_ts, interface, jitter, lddt,
                   rotate_chain, two_domain)
from bio_facts import DOCKQ_BANDS, LIMITS, PAE
from bookout import out

v = {}
ref = two_domain()
SPLIT = len(ref) // 2
v["n_res"], v["n_chain"] = len(ref), SPLIT
v["n_interface"] = len(interface(ref, SPLIT))
assert v["n_interface"] > 5, "两个域之间有一小撮界面接触"

# ---------- （1）界面错了，单链指标看不出来
v["rows"] = []
for ang in (0, 30, 60, 90, 120):
    m = rotate_chain(ref, ang)
    la, lb = chain_quality(m, ref, SPLIT)
    row = (ang, round(la, 3), round(lb, 3), round(lddt(m, ref), 3),
           round(gdt_ts(m, ref), 1), round(fnat(m, ref, SPLIT), 3))
    v["rows"].append(row)
    v[f"a{ang}_chain"], v[f"a{ang}_all"] = round(min(la, lb), 3), round(lddt(m, ref), 3)
    v[f"a{ang}_gdt"], v[f"a{ang}_fnat"] = round(gdt_ts(m, ref), 1), round(fnat(m, ref, SPLIT), 3)

assert v["a60_chain"] > 0.99, "每条链自己一点没动——单链指标当然满分"
assert v["a60_fnat"] < 0.05, "而界面接触一对都没对上"
assert v["a60_all"] > 0.95, \
    "整体 lDDT 也看不出来（域间的对只占 15 Å 之内那些对的百分之一点几）——所以复合物必须单独评界面"

# 对照：每条链自己也抖一点，这是另一种错
mj = jitter(ref, 1.0)
la, lb = chain_quality(mj, ref, SPLIT)
v["jit_chain"], v["jit_fnat"] = round(min(la, lb), 3), round(fnat(mj, ref, SPLIT), 3)
assert v["jit_chain"] < 0.75, "链自己乱了，单链指标立刻反映出来"

# ---------- （2）DockQ 的分档（只收官方定义）
v["bands"] = [(lo, hi, name) for lo, hi, name in DOCKQ_BANDS]
v["band_incorrect_hi"] = DOCKQ_BANDS[0][1]
v["band_acceptable_hi"] = DOCKQ_BANDS[1][1]
v["band_medium_hi"] = DOCKQ_BANDS[2][1]
v["n_bands"] = len(DOCKQ_BANDS)

# ---------- （3）口径：为什么这一节不印 AF3 的分数
v["pae_what"] = PAE["what"]
v["pae_division"] = PAE["division_of_labour"]
v["pae_unit_known"] = PAE["unit"] is not None
assert not v["pae_unit_known"], "PAE 的单位本书核不到官方文字，正文写'未核到'"
v["hetero_quote"] = LIMITS["hetero_complex"]
v["bridging"] = LIMITS["bridging_domains"]

out(**v)
