"""算例 3.6.1、3.6.2：线程束分化的代价（GPU 执行模拟器的 Python 参考版 _gpusim.py，部分 ②）。

式 (3.6.1)：一个线程束内两种线程都有时，发射的指令数 = pre + then + else + post；
SIMT 效率 = 活动线程·指令 / (32 × 发射的指令)。
"""
from _gpusim import diverge
from bookout import out

base = dict(pre=2, then=4, other=4, post=2)
odd = diverge("odd", warps=4, **base)
half = diverge("half", warps=4, **base)
warp = diverge("warp", warps=4, **base)
none = diverge("none", warps=4, **base)
assert odd["eff"] == half["eff"]
assert warp["eff"] == 1.0 and none["eff"] == 1.0

# 算例 3.6.2：按数据分支：每个线程以概率 p 走 then；4096 个线程束
data = {p: diverge("data", warps=4096, p=p, seed=7, **base) for p in (0.5, 0.9, 0.99, 0.999)}
# 一个线程束 32 个线程全走同一路的概率：p^32 + (1 − p)^32
uni = {p: p ** 32 + (1 - p) ** 32 for p in data}
frac_uni = {p: sum(1 for w in d["warps"] if w["mask"] in ("0" * 32, "1" * 32)) / len(d["warps"]) for p, d in data.items()}

out(odd_issued=odd["warps"][0]["issued"], none_issued=none["warps"][0]["issued"], odd_eff=odd["eff"] * 100,
    warp_eff=warp["eff"] * 100, ratio_time=odd["issued"] / none["issued"],
    eff50=data[0.5]["eff"] * 100, eff90=data[0.9]["eff"] * 100, eff99=data[0.99]["eff"] * 100, eff999=data[0.999]["eff"] * 100,
    uni90=uni[0.9] * 100, uni99=uni[0.99] * 100, uni999=uni[0.999] * 100, fu90=frac_uni[0.9] * 100, fu99=frac_uni[0.99] * 100,
    fu999=frac_uni[0.999] * 100)
