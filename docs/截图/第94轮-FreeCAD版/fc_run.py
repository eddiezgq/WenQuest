import sys, time, os
MOD = sys.argv[-2] if len(sys.argv) > 2 else os.environ["WQMOD"]
OUT = os.environ["WQOUT"]
sys.path.insert(0, MOD)
import FreeCAD as App
import wqsew_feature as F
BAD = {"lockstitch": {"n": 6000}, "overlock": {"n": 9000}, "cover": {"dphi": 40}, "pattern": {"n": 3000},
       "embroid": {"n": 1400}, "flatknit": {"sys": 2, "xfer": 4, "rack": 4, "dwell": 0.01}}
for m, p in BAD.items():
    doc = App.newDocument("T_" + m)
    t0 = time.time()
    o = F.add_design(doc, params=p, machine=m)
    t1 = time.time()
    bad = [x for x in o.Parts if not x.Shape.isValid() or x.Shape.Volume <= 0]
    hs = F.hotspots(o)
    pp = o.Proxy.params(o)
    t2 = time.time()
    for i in range(10):
        o.Proxy.update_parts(o, pp, (i + 1) * (6 if m not in F.SEQ else 36))
    t3 = time.time()
    h = next((h for h in hs if h["phi"] is not None), None)
    if h:
        o.Proxy.update_parts(o, pp, h["phi"])
    F.export_step(o, os.path.join(OUT, m + ".step"))
    print(m, "parts", len(o.Parts), "invalid", len(bad), "hot", ascii([(x["key"], x["phi"], x["index"]) for x in hs][:3]),
          "build %.1fs  10 steps %.2fs" % (t1 - t0, t3 - t2), "progress", ascii(getattr(o, "Progress", "-")),
          "step KB", os.path.getsize(os.path.join(OUT, m + ".step")) // 1024)
    doc.saveAs(os.path.join(OUT, m + ".FCStd"))
print("DONE")
import sys; sys.stdout.flush(); os._exit(0)
