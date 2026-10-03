"""《人工智能》第 14 轮 2.5：GPU 执行模拟器的 JS 版（平台实验工具包 kit.js 的 GPU 模块）与 Python 参考版
（textbook/ai/ch03/code/_gpusim.py）在同一组情形下结果完全相同；书中的算例数字由 Python 版算出。"""
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
KIT = ROOT / "services" / "gateway" / "app" / "production" / "labkit" / "kit.js"
spec = importlib.util.spec_from_file_location("gpusim", ROOT / "textbook" / "ai" / "ch03" / "code" / "_gpusim.py")
sim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim)

SCHED = [dict(warps=w, schedulers=s, latency=L, k=k, gap=g, policy=pol, cycles=4000, trace=60)
         for w, s, L, k, g, pol in [(1, 1, 600, 4, 0, "gto"), (16, 1, 600, 4, 0, "gto"), (16, 1, 600, 40, 0, "lrr"),
                                    (8, 4, 100, 8, 0, "gto"), (64, 4, 600, 4, 40, "gto"), (13, 3, 37, 5, 11, "lrr"),
                                    (5, 2, 12, 2, 3, "gto")]]
DIV = [dict(cond=c, warps=w, pre=a, then=b, other=o, post=d, p=p, seed=sd)
       for c, w, a, b, o, d, p, sd in [("none", 1, 2, 4, 4, 2, 0.5, 1), ("odd", 2, 2, 4, 4, 2, 0.5, 1), ("half", 1, 0, 3, 5, 0, 0.5, 1),
                                       ("warp", 4, 1, 4, 4, 1, 0.5, 1), ("data", 4, 2, 6, 2, 2, 0.9, 7), ("data", 8, 0, 4, 4, 0, 0.1, 123)]]


def test_js_and_python_agree():
    if not shutil.which("node"):
        pytest.skip("node is not installed")
    kit = KIT.read_text(encoding="utf-8")
    gpu = kit[kit.index("const GPU = {"):kit.index("// ---------- tasks & progress")]
    script = gpu + f"""
const S = {json.dumps(SCHED)}, D = {json.dumps(DIV)};
const r = GPU.rng(42), xs = Array.from({{ length: 5 }}, () => r());
console.log(JSON.stringify({{ s: S.map((o) => GPU.schedule(o)), d: D.map((o) => GPU.diverge(o)), xs }}));
"""
    js = json.loads(subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout)
    r = sim.rng(42)
    assert js["xs"] == [r() for _ in range(5)]
    for o, got in zip(SCHED, js["s"]):
        want = sim.schedule(**o)
        assert got["issued"] == want["issued"] and got["rounds"] == want["rounds"] and got["trace"] == want["trace"], o
    for o, got in zip(DIV, js["d"]):
        want = sim.diverge(**o)
        assert {k: got[k] for k in ("warps", "issued", "active", "steps")} == {k: want[k] for k in ("warps", "issued", "active", "steps")}, o


def test_hand_computed_cases():
    assert sim.diverge(cond="odd", pre=0, post=0)["eff"] == 0.5                     # 两路等长：一半算力空转
    assert sim.diverge(cond="half", pre=0, post=0, then=3, other=5)["eff"] == 0.5
    assert sim.diverge(cond="warp", warps=4)["eff"] == 1.0                          # 按线程束整齐分支：没有浪费
    assert sim.diverge(cond="none")["issued"] == 2 + 4 + 2
    d = sim.diverge(cond="odd", pre=2, then=4, other=4, post=2)
    assert d["issued"] == 12 and d["active"] == 32 * 8
    for n, k, L, g in [(1, 4, 600, 0), (4, 4, 600, 0), (16, 4, 600, 0), (16, 40, 600, 0), (16, 8, 100, 0), (16, 20, 600, 40), (16, 4, 600, 40)]:
        u = sim.schedule(warps=n, latency=L, k=k, gap=g)["util"]
        assert abs(u - sim.little(n, k, L, g)) < 0.04 * sim.little(n, k, L, g) + 1e-3, (n, k, L, g, u)
    lrr = sim.schedule(warps=16, latency=600, k=40, policy="lrr")["util"]
    assert lrr < 0.6                                                                # 松散轮转使线程束同步，延迟藏不住
