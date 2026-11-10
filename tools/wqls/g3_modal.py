"""第 138 轮 G3：机壳铸件模态（数字工厂 CAE：Gmsh + CalculiX）。

    python3 tools/wqls/g3_modal.py <housing.step> <结果.json> [网格 mm]
支承：机座底面一圈（装油盘、坐在台板上的那一圈）固定。材料 HT250：E 取 120 GPa（灰铸铁常用值，GB/T 9439 没有给弹性模量，待核），
ν 0.26，密度 7.2 g/cm³。目标（G1 定）：一阶 ≥ 210 Hz，避开 5000 r/min 的二倍频 167 Hz。
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "factory" / "digital"))
from cae import geometry as GEO, materials as MATS, modal as MO  # noqa: E402

_G = GEO._gmsh()
_orig = _G.option.setNumber


def _set(name, val):                       # 带大量圆角的铸件 HXT 有时划不出网格：改用 Delaunay（WQ_ALG3D=1）
    if name == "Mesh.Algorithm3D" and os.environ.get("WQ_ALG3D"):
        val = int(os.environ["WQ_ALG3D"])
    if name == "Mesh.HighOrderOptimize" and os.environ.get("WQ_HOO") is not None:
        val = int(os.environ["WQ_HOO"])            # 二阶网格优化在细圆角处偶尔不收敛：关掉（WQ_HOO=0），
        _orig("Mesh.SecondOrderLinear", 1)          # 同时让中间节点取直，避免雅可比为负
    if name == "Mesh.MeshSizeFromCurvature" and os.environ.get("WQ_CURV"):
        val = int(os.environ["WQ_CURV"])           # 铸件圆角多：曲率加密会让单元数暴涨（内存不够），可调小
    if name == "Mesh.MeshSizeMin" and os.environ.get("WQ_HMIN"):
        val = float(os.environ["WQ_HMIN"])
    return _orig(name, val)


_G.option.setNumber = _set

step = open(sys.argv[1], "rb").read()
size = float(sys.argv[3]) if len(sys.argv) > 3 else 7.0
faces, _, solid = GEO.faces(step)
bottom = [f["id"] for f in faces if f["kind"] == "plane" and abs(f["bbox"][2] + 62) < 0.05 and abs(f["bbox"][5] + 62) < 0.05]
mat = dict(MATS.get("HT200"), id="HT250", name="HT250 灰铸铁", E_mpa=120000, ultimate_mpa=250)
if os.environ.get("WQ_MAT") == "QT450":                    # 球墨铸铁 QT450-10：E 取 169 GPa、密度 7.1（常用值，待核）
    mat = dict(mat, id="QT450", name="QT450-10 球墨铸铁", E_mpa=169000, nu=0.275, density=7.10, ultimate_mpa=450)
os.environ.setdefault("WQ_CAE_TIME_LIMIT_S", "3000")
st, surf = MO.solve(step, {"material": mat, "mesh": {"size_mm": size}, "loads": [{"type": "fixed", "faces": bottom}]}, n_modes=int(os.environ.get("WQ_NMODES", 6)))
res = dict(solid=solid, bottom_faces=bottom, mesh=size, stats=st)
Path(sys.argv[2]).write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
np.savez_compressed(Path(sys.argv[2]).with_suffix(".npz"), **{k: v for k, v in surf.items()})
print(json.dumps(st.get("freqs"), ensure_ascii=False), st.get("seconds"))
