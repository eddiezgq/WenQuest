"""Make the "outline only" example (round 179): the feed-lift cam of examples/sewing-feed.json drawn as a CAD file
would be — the outline as a SPLINE through fit points, turned 30° on the drawing, with a bore, centre lines and a
note — and the project that imports it. Run from services/cam:  python tools/make_outline_example.py
"""

import io
import json
import math
import sys
from pathlib import Path

import ezdxf
import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from camkit import disk as D  # noqa: E402
from camkit import inverse as IV  # noqa: E402
from camkit.analyze import mechanism  # noqa: E402
from camkit.program import Program  # noqa: E402

src = json.loads((HERE / "examples" / "sewing-feed.json").read_text(encoding="utf-8"))
geo = D.analyse(mechanism(src["mechanism"]), Program.from_dict(src["program"]), 3600)
P = np.asarray(geo["profile"])[:, ::5]  # 720 fit points, every 0.5°
turn = math.radians(30)
c, s = math.cos(turn), math.sin(turn)
P = np.stack([c * P[0] - s * P[1], s * P[0] + c * P[1]])

doc = ezdxf.new("R2010", setup=True)
msp = doc.modelspace()
pts = [(float(x), float(y)) for x, y in P.T] + [(float(P[0, 0]), float(P[1, 0]))]
msp.add_spline(fit_points=pts, dxfattribs={"layer": "OUTLINE"}).closed = False
msp.add_circle((0, 0), 4.0, dxfattribs={"layer": "OUTLINE"})  # the bore
for a, b in (((-22, 0), (22, 0)), ((0, -22), (0, 22))):
    msp.add_line(a, b, dxfattribs={"layer": "CENTER", "linetype": "CENTER"})
msp.add_text("FEED-LIFT CAM (FICTIONAL)", dxfattribs={"height": 1.5, "insert": (-14, -20)})
buf = io.StringIO()
doc.write(buf)
text = buf.getvalue()
(HERE / "examples" / "sewing-feed-outline.dxf").write_text(text, encoding="utf-8")

mech = dict(src["mechanism"])
outline = {"format": "dxf", "name": "sewing-feed-outline.dxf", "data": text, "cx": 0, "cy": 0, "zero": "rise",
           "smooth": 1}
res = IV.import_outline({"mechanism": mech, "outline": {**outline, "center": [0, 0]}})
outline["report"] = res["report"]
outline["used"] = ""  # the web app fills it in from the mechanism when it opens the project
proj = {
    "title": {"zh": "示例：只有廓线图的送布抬牙凸轮（导入 DXF，参数为虚构）",
              "en": "Example: a feed-lift cam from its drawing only (imported DXF, fictional numbers)"},
    "program": res["program"],
    "mechanism": res["mechanism"],
    "loads": src.get("loads", {}),
    "material": src.get("material", {}),
    "limits": src.get("limits", {}),
    "outline": outline,
}
(HERE / "examples" / "sewing-feed-outline.json").write_text(json.dumps(proj, ensure_ascii=False, indent=1) + "\n",
                                                            encoding="utf-8")
r = res["report"]
print(f"rb {r['rb']:.5f}  lift {r['lift']:.5f}  zero turned {r['shift_deg']}°",
      f"check {r['check']['max_dev'] * 1e3:.2f} µm  source {r['source']}")
