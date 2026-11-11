"""第 138 轮 G4.1 一键：刺布与挑线机构的零件 → 运动 → 干涉检查 → 质量回填 → 网页三维的文件。

    python3 tools/wqls/g4_parts.py <工作目录> [<机壳 housing.step>]

步骤：
 1. FreeCAD 跑 cad/mech.py：按 spec.py 和 G4/挑线机构.json 画零件（φ = 0 位置），按平衡率定平衡块，导出 STEP/STL 和质量特性；
 2. g4_mech.py：一转每 2° 的零件变换（设计软件运动学）；
 3. FreeCAD 跑 cad/mech_check.py：每 2° 零件两两之间、零件与机壳之间的最小距离；导出机头网格；
 4. 写回仓库：docs/设计/WQ-LS/G4/零件质量.json（dyn.py 用它替换估计质量）、G4/干涉检查.json。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FC = os.environ.get("WQ_FREECAD", "/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/mm/fc/bin/freecadcmd")
G4 = ROOT / "docs" / "设计" / "WQ-LS" / "G4"


def fc(script, env):
    r = subprocess.run([FC, "-c", f"exec(open('{ROOT / 'tools' / 'wqls' / 'cad' / script}').read())"], cwd=ROOT, text=True,
                       capture_output=True, env={**os.environ, "LANG": "C.UTF-8", **env}, timeout=7200)
    tail = [ln for ln in r.stdout.splitlines() if ln.lstrip().startswith("{") or "{\"" in ln]
    if r.returncode or not tail:
        raise SystemExit(f"{script} 失败：\n{(r.stdout + r.stderr)[-1500:]}")
    return json.loads(tail[-1][tail[-1].index("{"):])


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/wqls_mech")
    housing = sys.argv[2] if len(sys.argv) > 2 else None
    out.mkdir(parents=True, exist_ok=True)
    print("1 零件", fc("mech.py", {"WQ_OUT": str(out)})["balance"])
    subprocess.run([sys.executable, str(HERE / "g4_mech.py"), str(out)], check=True)
    info = json.loads((out / "parts.json").read_text())
    if housing:
        chk = fc("mech_check.py", {"WQ_MECH": str(out), "WQ_HOUSING": housing, "WQ_STEP": os.environ.get("WQ_STEP", "2")})
        full = json.loads((out / "clearance.json").read_text())
        (G4 / "干涉检查.json").write_text(json.dumps(full, ensure_ascii=False, indent=1))
        print("3 干涉", "太近：", chk["too_close"], "最近：", chk["closest"][:5])
    # 质量回填 dyn.py
    P = info["parts"]
    sys.path[:0] = [str(HERE)]
    import g4_takeup as T
    import spec as S
    lk = json.loads((G4 / "挑线机构.json").read_text())["lk"]
    m = T.Mech2(r=S.SEW["r"], l=S.SEW["l"], lk=lk)
    p0 = m.link_pose(0, m.LK0)
    Pw = (-p0["P"][0], S.ZU + p0["P"][1])
    Ew = (-p0["E"][0], S.ZU + p0["E"][1])
    c = P["lever"]["com"]
    pe = (Ew[0] - Pw[0], Ew[1] - Pw[1])
    g_tk = ((c[1] - Pw[0]) * pe[0] + (c[2] - Pw[1]) * pe[1]) / (pe[0] ** 2 + pe[1] ** 2)
    bal = info["balance"]
    dyn_mass = dict(m_bar=round(sum(P[k]["mass_kg"] for k in ("needle_bar", "needle_clamp", "needle", "nb_link")), 4),
                    m_rod=P["rod"]["mass_kg"], g_rod=round(bal["g_rod_mm"] / S.SEW["l"], 3), I_rod=round(P["rod"]["Ixx_kgmm2"] * 1e-6, 8),
                    m_pin=round(P["crank_pin"]["mass_kg"] + 0.010, 4), m_tk=P["lever"]["mass_kg"], g_tk=round(g_tk, 3))
    res = dict(dyn_mass=dyn_mass, balance=bal, parts={k: dict(mass_g=round(v["mass_kg"] * 1000, 1), material=v["material"]) for k, v in P.items()},
               note="质量按钢 7.85 g/cm³ 从 FreeCAD 实体算；滚针轴承 2 只约 10 g 计入曲柄销；平衡块按平衡率 k 定（cad/mech.py）。")
    (G4 / "零件质量.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print("4 质量", dyn_mass, "平衡块折算到曲柄半径", bal["equiv_at_r_g"], "g")


if __name__ == "__main__":
    main()
