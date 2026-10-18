"""Read camkit's STEP files back with OpenCASCADE (round 39, step 3): a local check, not a CI test.

    pip install cadquery-ocp && python tools/crosscheck_step_occ.py packaging-plate out.step

Write the STEP first (web app, or camkit.step.solid). Prints, for every planar edge of the solid, the largest distance
to the dense design curve; checks that the solid is valid and gives its volume from a fine mesh.
"""

import json
import sys
from pathlib import Path

import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.GProp import GProp_GProps
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from camkit import mfg, step  # noqa: E402


def main(example: str, path: str) -> None:
    p = json.loads((HERE / "examples" / f"{example}.json").read_text(encoding="utf-8"))
    _, _, surfaces, _ = mfg.design(p)
    reader = STEPControl_Reader()
    reader.ReadFile(path)
    reader.TransferRoots()
    shape = reader.OneShape()
    ex = TopExp_Explorer(shape, TopAbs_EDGE)
    while ex.More():
        c = BRepAdaptor_Curve(TopoDS.Edge(ex.Current()))
        u = np.linspace(c.FirstParameter(), c.LastParameter(), 4001)
        P = np.array([[c.Value(x).X(), c.Value(x).Y(), c.Value(x).Z()] for x in u])
        ex.Next()
        if np.ptp(P[:, 2]) > 1e-6:
            continue  # seam lines
        r = np.hypot(P[:, 0], P[:, 1])
        if np.ptp(r) < 1e-9:
            print(f"edge z={P[0, 2]:.2f} circle r={r[0]:.4f}")
            continue
        best = min(step._seg_dist(sf.P, P[:, :2].T, cKDTree(sf.P.T).query(P[:, :2])[1]).max() for sf in surfaces)
        print(f"edge z={P[0, 2]:.2f} max distance to the design {best:.2e} mm")
    BRepMesh_IncrementalMesh(shape, 0.0005, False, 0.05, True)
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, g, True, False, True)
    print("valid solid:", BRepCheck_Analyzer(shape).IsValid(), " volume (mesh):", g.Mass())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
