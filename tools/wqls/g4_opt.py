"""第 138 轮 G4 第一步：机壳优化——铸件最轻，前后摆 ≥ 125 Hz、上下 ≥ 210 Hz（HT250）。

    python3 tools/wqls/g4_opt.py <试算次数> <输出目录>
每一次试算：FreeCAD 按参数建简化模型（不倒外圆角）→ 数字工厂 CAE 算前三阶 → 记下质量和频率。用数字工厂的优化工具 optuna（TPE）。
结果一行一个写进 <输出目录>/trials.jsonl，可以中途停、接着跑。
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import optuna

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FC = os.environ.get("WQ_FREECAD", "/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/mm/fc/bin/freecadcmd")
F1, F2 = 125.0, 210.0
N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/wqls_opt")
OUT.mkdir(parents=True, exist_ok=True)
LOG = OUT / "trials.jsonl"


def evaluate(p: dict) -> dict:
    env = {**os.environ, "LANG": "C.UTF-8", "WQ_NOEDGE": "1", "WQ_VARIANT": "B", "WQ_OUT": str(OUT / "cur"),
           "WQ_WALL": f"{p['wall']:.2f}", "WQ_ROOTWALL": f"{p['root']:.2f}", "WQ_ROOTX": f"{p['root_x']:.0f}",
           "WQ_BEDWALL": f"{p['bed']:.2f}", "WQ_BEDRIB": f"{p['bedrib']:.0f}", "WQ_HEADWALL": f"{p['head']:.2f}",
           "WQ_PY0": f"{-p['pil_d'] * 0.42:.1f}", "WQ_PY1": f"{p['pil_d'] * 0.58:.1f}",
           "WQ_AY0": f"{-p['arm_d'] * 0.40:.1f}", "WQ_AY1": f"{p['arm_d'] * 0.60:.1f}",
           "WQ_RIBX": ",".join(str(round(75 + i * 150 / max(p['ribs'] - 1, 1))) for i in range(p['ribs'])) if p['ribs'] else ""}
    r = subprocess.run([FC, "-c", f"exec(open('{ROOT}/tools/wqls/cad/housing.py').read())"], capture_output=True, text=True,
                       env=env, timeout=1500, cwd=ROOT)
    m = re.search(r'"mass_kg_ht250": ([0-9.]+)', r.stdout)
    if not m:
        return dict(ok=False, why="build " + (r.stdout + r.stderr)[-200:])
    mass = float(m.group(1))
    for h in ("14", "12", "16"):
        rr = subprocess.run([sys.executable, str(HERE / "g3_modal.py"), str(OUT / "cur" / "housing.step"), str(OUT / "cur" / "modal.json"), h],
                            capture_output=True, text=True, timeout=3000,
                            env={**os.environ, "WQ_NMODES": "3", "WQ_CURV": "10", "WQ_HOO": "0", "WQ_CAE_MAX_ELEMENTS": "400000",
                                 "WQ_CAE_TIME_LIMIT_S": "2500"})
        hz = re.findall(r'"hz": ([0-9.]+)', rr.stdout)
        if len(hz) >= 2:
            return dict(ok=True, mass=mass, f1=float(hz[0]), f2=float(hz[1]), mesh=h)
    return dict(ok=False, mass=mass, why="mesh " + (rr.stdout + rr.stderr)[-200:])


def objective(trial):
    p = dict(wall=trial.suggest_float("wall", 5.5, 7.0), root=trial.suggest_float("root", 6.0, 11.0),
             root_x=trial.suggest_float("root_x", 180, 290), bed=trial.suggest_float("bed", 5.0, 7.0),
             bedrib=trial.suggest_float("bedrib", 0, 40), head=trial.suggest_float("head", 4.5, 6.0),
             pil_d=trial.suggest_float("pil_d", 130, 170), arm_d=trial.suggest_float("arm_d", 96, 126),
             ribs=trial.suggest_int("ribs", 0, 4))
    t0 = time.time()
    r = evaluate(p)
    rec = dict(n=trial.number, p=p, r=r, s=round(time.time() - t0))
    with LOG.open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    if not r.get("ok"):
        return 60.0
    pen = max(0, F1 - r["f1"]) / F1 + max(0, F2 - r["f2"]) / F2
    return r["mass"] * (1 + 8 * pen)


study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=138, n_startup_trials=8))
if LOG.exists():                                          # 接着上次跑
    for line in LOG.read_text().splitlines():
        rec = json.loads(line)
        r = rec["r"]
        v = 60.0 if not r.get("ok") else r["mass"] * (1 + 8 * (max(0, F1 - r["f1"]) / F1 + max(0, F2 - r["f2"]) / F2))
        study.add_trial(optuna.trial.create_trial(
            params=rec["p"], value=v,
            distributions={"wall": optuna.distributions.FloatDistribution(5.5, 7.0), "root": optuna.distributions.FloatDistribution(6.0, 11.0),
                           "root_x": optuna.distributions.FloatDistribution(180, 290), "bed": optuna.distributions.FloatDistribution(5.0, 7.0),
                           "bedrib": optuna.distributions.FloatDistribution(0, 40), "head": optuna.distributions.FloatDistribution(4.5, 6.0),
                           "pil_d": optuna.distributions.FloatDistribution(130, 170), "arm_d": optuna.distributions.FloatDistribution(96, 126),
                           "ribs": optuna.distributions.IntDistribution(0, 4)}))
optuna.logging.set_verbosity(optuna.logging.WARNING)
study.optimize(objective, n_trials=N)
best = [json.loads(x) for x in LOG.read_text().splitlines()]
ok = [b for b in best if b["r"].get("ok") and b["r"]["f1"] >= F1 and b["r"]["f2"] >= F2]
ok.sort(key=lambda b: b["r"]["mass"])
print(json.dumps(ok[:3], ensure_ascii=False, indent=1))
