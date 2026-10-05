"""比较：拟合参数下的长沟道模型 与 SKY130 仿真（result.json）。打印各量的相对误差。"""
import json, sys, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent
res = json.loads((HERE / "result.json").read_text())
P = json.loads((HERE / (sys.argv[1] if len(sys.argv) > 1 else "params.sky130.json")).read_text())
spec = importlib.util.spec_from_file_location("wqmodel", HERE.parents[3] / "textbook" / "dic" / "conventions" / "mos.py"); M = importlib.util.module_from_spec(spec)
import types
spec.loader.exec_module(M)
for k in ("VDD", "VTn", "VTp", "kn", "kp", "L", "Wmin", "Cg", "Cd"):
    setattr(M, k, P[k])
rows = []
d = res["device"]
rows.append(("IDSAT n μA/μm", M.idsat_n(1) * 1e6, d["idsat_n_per_um"] * 1e6))
rows.append(("IDSAT p μA/μm", M.idsat_p(1) * 1e6, d["idsat_p_per_um"] * 1e6))
for v in res["vtc"]:
    nm = M.noise_margins(M.Wmin, v["ratio"] * M.Wmin, step=0.001)
    rows.append((f"VM r={v['ratio']}", M.vm(M.Wmin, v["ratio"] * M.Wmin), v["VM"]))
    rows.append((f"NML r={v['ratio']}", nm["NML"], v["NML"]))
    rows.append((f"NMH r={v['ratio']}", nm["NMH"], v["NMH"]))
for k, v in res["delay"].items():
    r = float(k)
    for n in ("1", "4", "8"):
        a, b = M.delays(M.Wmin, r * M.Wmin, int(n) * M.cin(M.Wmin, r * M.Wmin))
        rows.append((f"tPHL r={k} FO{n} ps", a * 1e12, v[n][0] * 1e12))
        rows.append((f"tPLH r={k} FO{n} ps", b * 1e12, v[n][1] * 1e12))
w = max(len(r[0]) for r in rows)
for name, m, s in rows:
    print(f"{name:<{w}}  model {m:8.3f}  sim {s:8.3f}  err {100*(m-s)/s:+6.1f}%")
