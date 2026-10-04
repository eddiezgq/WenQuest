"""采用镜像里的校准结果（第 17 轮附 3.4：校准以镜像中的完整 SKY130 模型为准）。

镜像验收工作流把 out/calib/result.json 以 gzip+base64 写成运行注释“校准结果 result.json”。
用法：python adopt.py <注释内容>
  → 写 calib/result.json，按其重新拟合（calib.py --fit-only）得到 params.sky130.json，
    再把拟合出的器件参数（VTn、VTp、kn、kp、Cg、Cd）和说明写进 labs/micro/kit/models/params.json（题目参数不动）。
之后运行 ../regen_ch1.sh 重新生成第 1 章全部资料。
"""
import base64
import gzip
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
res = json.loads(gzip.decompress(base64.b64decode(sys.argv[1].strip())))
(HERE / "result.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
subprocess.run([sys.executable, str(HERE / "calib.py"), "--fit-only"], check=True, env={"CALIB_OUT": str(HERE), "PATH": "/usr/bin:/bin"})
new = json.loads((HERE / "params.sky130.json").read_text(encoding="utf-8"))
pf = ROOT / "labs/micro/kit/models/params.json"
p = json.loads(pf.read_text(encoding="utf-8"))
old = {k: p[k] for k in ("VTn", "VTp", "kn", "kp", "Cg", "Cd")}
for k in old:
    p[k] = new[k]
p["_note"] = new["_note"]
pf.write_text(json.dumps(p, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
for k, v in old.items():
    print(f"{k}: {v} → {p[k]}")
