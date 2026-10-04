"""算例 4.6.1、4.6.2：一个线程束的一次读取要搬几个 32 字节扇区（GPU 执行模拟器部分 ③，conventions/gpusim.py）；
结构体数组与数组结构体。式 (4.6.1)：有效带宽比 = 请求的字节 / 搬运的字节。"""
from bookout import out
from gpusim import addresses, coalesce

cases = {"cont": dict(kind="contiguous"), "off4": dict(kind="offset", offset=4), "s2": dict(kind="stride", k=2),
         "s4": dict(kind="stride", k=4), "s8": dict(kind="stride", k=8), "s32": dict(kind="stride", k=32),
         "rand": dict(kind="random", k=64, seed=3)}
res = {k: coalesce(addresses(**v)) for k, v in cases.items()}
vec4 = coalesce(addresses(kind="contiguous", size=16), 16)       # 每个线程读一个 float4
# 结构体数组：粒子 (x, y, z, vx, vy, vz) 6 个单精度，每个 24 字节；只读 x
aos = coalesce(addresses(kind="aos", struct=24))
soa = coalesce(addresses(kind="contiguous"))
assert res["cont"]["sectors"] == 4 and res["s2"]["sectors"] == 8 and res["s32"]["sectors"] == 32
out(**{f"{k}_sec": v["sectors"] for k, v in res.items()}, **{f"{k}_eff": v["eff"] * 100 for k, v in res.items()},
    vec4_sec=vec4["sectors"], vec4_eff=vec4["eff"] * 100, aos_sec=aos["sectors"], aos_eff=aos["eff"] * 100,
    soa_sec=soa["sectors"])
