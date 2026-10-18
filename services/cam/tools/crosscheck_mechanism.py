"""Cross-check camkit against the open-source `mechanism` package (round 39, step 2).

    pip install mechanism && python tools/crosscheck_mechanism.py

`mechanism` (MIT) has harmonic and cycloidal rise / dwell / fall and the profile of an in-line knife-edge
follower (r = r_b + s). This is not a CI test (the package pulls in matplotlib); the result is recorded in
the round 39 plan. Run from services/cam.
"""
import sys
from pathlib import Path

import numpy as np
from mechanism import Cam

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from camkit.disk import Mechanism, analyse  # noqa: E402
from camkit.program import Program  # noqa: E402

H, RB, OMEGA = 20.0, 40.0, 2 * np.pi * 5  # mm, mm, rad/s (300 r/min)
worst = 0.0
for law in ("harmonic", "cycloidal"):
    ref = Cam(motion=[("Rise", H, 100), ("Dwell", 80), ("Fall", H, 120), ("Dwell", 60)], degrees=True, omega=OMEGA)
    obj = getattr(ref, law)
    th = ref.thetas
    prog = Program.from_dict({"unit": "mm", "segments": [
        {"kind": "rise", "deg": 100, "h": H, "law": law}, {"kind": "dwell", "deg": 80},
        {"kind": "return", "deg": 120, "h": H, "law": law}, {"kind": "dwell", "deg": 60}]})
    s, s1, s2, _ = prog.eval(th)
    rows = [("s", s, obj.S, 1.0), ("v", s1 * OMEGA, obj.V, OMEGA), ("a", s2 * OMEGA**2, obj.A, OMEGA**2)]
    for name, mine, theirs, scale in rows:
        err = np.max(np.abs(mine - theirs)) / (H * scale)
        worst = max(worst, err)
        print(f"{law:10s} {name}: max |camkit - mechanism| / scale = {err:.2e}")
    # profile of an in-line knife-edge follower: radius at each cam-frame angle
    res = analyse(Mechanism(follower="translating", contact="knife", rb=RB), prog, n=3600)
    x, y = res["profile"]
    xr, yr = obj.get_profile(RB, ref.thetas_r)
    # compare the radius at the same polar angle of the cam frame; the tools put the follower on different axes
    # (camkit on +y, mechanism on +x) and may mirror, so take the best of the four quarter turns and two senses
    ang, r_mine = np.mod(np.arctan2(y, x), 2 * np.pi), np.hypot(x, y)
    order = np.argsort(ang)
    ang_t, r_theirs = np.mod(np.arctan2(yr, xr), 2 * np.pi), np.hypot(xr, yr)
    best = min(np.max(np.abs(np.interp(np.mod(sg * ang_t + q, 2 * np.pi), ang[order], r_mine[order], period=2 * np.pi)
                             - r_theirs)) for sg in (1, -1) for q in np.arange(4) * np.pi / 2)
    worst = max(worst, best / H)
    print(f"{law:10s} profile: max radius difference at the same angle = {best:.2e} mm")
print("worst", f"{worst:.2e}", "OK" if worst < 1e-3 else "DIFFERENT")
