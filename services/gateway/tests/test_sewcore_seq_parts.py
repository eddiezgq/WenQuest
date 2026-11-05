"""第 89 轮：花样机、刺绣机、横机的三维零件（讲解片用）——进度角每 360° 一针 / 一趟，位置和样机数据（第 81 轮 proto）、计算核心一致。"""
import base64
import math

from app.sewcore import cad
from app.sewcore import cad_seq as C
from app.sewcore import emb_samples as SMP
from app.sewcore import flatknit as F
from app.sewcore import pattern as P

LOGO = base64.b64encode(SMP.logo_dst()).decode()


def _part(m, name):
    return next(q for q in m["parts"] if q["name"] == name)


def _shape(m):
    """零件清单的“形状”：名字、类型、管子点数——每帧都得一样（渲染器只在第一帧建物体，之后只挪）"""
    return [(q["name"], q["type"], len(q.get("pts", []))) for q in m["parts"]]


def test_pattern_needle_and_template_follow_the_design():
    p = {"pat": "star", "n": 2600}
    D, pp = C.cfg_of("pattern", p)
    xs, ys = [q[0] for q in D["pts"]], [q[1] for q in D["pts"]]
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    shape0 = _shape(cad.parts3d(p, 0.0, "pattern"))
    for k in (1, 7, D["n"] // 2, D["n"] - 1):
        m = cad.parts3d(p, k * 360 + 180, "pattern")                # 针在布中：模板静止，第 k 针在针下
        assert _shape(m) == shape0
        assert math.isclose(m["px"], D["pts"][k][0] - cx, abs_tol=1e-9) and math.isclose(m["py"], D["pts"][k][1] - cy, abs_tol=1e-9)
        assert m["inF"] and m["sp"] == D["sp"][k] and m["idx"] == D["idx"][k] + 1
        assert math.isclose(m["needle"], P.TIP - P.xN(180))
        seam = _part(m, "PT_Seam")["pts"]
        assert math.isclose(seam[-1][0], 0, abs_tol=1e-6) and math.isclose(seam[-1][1], 0, abs_tol=1e-6)   # 针迹末端就在针下
        tip = _part(m, "PT_Needle")["base"]
        assert tip[0] == 0 and tip[1] == 0
    # 出布以后在移动窗口里走到下一针，入布前走完（移动转角 = 样机的 mv）
    k = 5
    a = k * 360 + D["f2"] + D["mg"] + D["mv"][k + 1] + 0.5
    m = cad.parts3d(p, a, "pattern")
    assert math.isclose(m["px"], D["pts"][k + 1][0] - cx, abs_tol=1e-6)
    mid = cad.parts3d(p, k * 360 + D["f2"] + D["mg"] + D["mv"][k + 1] / 2, "pattern")
    assert not math.isclose(mid["px"], m["px"], abs_tol=1e-3) or D["pts"][k][0] == D["pts"][k + 1][0]


def test_embroid_hoop_colours_heads_and_jumps():
    p = {"src": "file", "dst": LOGO, "H": 12}
    D, pp = C.cfg_of("embroid", p)
    assert D["H"] == 12
    m0 = cad.parts3d(p, 0.0, "embroid")
    assert m0["heads"] == 4 and m0["H"] == 12                          # 最多画 4 个头（Q3）
    assert sum(1 for q in m0["parts"] if q["name"].startswith("EM_Needle")) == 4
    seams = [q for q in m0["parts"] if q["name"].startswith("EM_Seam1_")]
    assert len({q["color"] for q in seams}) == len({c % len(C.PAL) for c in D["col"][1:]} & {C.PAL.index(q["color"]) for q in seams})
    shape0 = _shape(m0)
    W = D["W"]
    for k in range(1, D["n"], max(1, D["n"] // 9)):
        m = cad.parts3d(p, k * 360 + 180, "embroid")
        assert _shape(m) == shape0
        assert m["idx"] == D["idx"][k] + 1 and m["col"] == D["col"][k] + 1 and m["sp"] == D["sp"][k]
        if D["kind"][k] in "jc":
            assert m["needle"] == 18 and not m["inF"]                  # 跳步、换色：针杆停在上面
        elif D["acc"][k] <= 1:                                          # 走得完：针扎下时绷架已在第 k 针
            assert m["inF"] and math.isclose(m["px"], D["pts"][k][0], abs_tol=1e-6)
    j = D["worst"]
    late = cad.parts3d({"src": "hand", "s": 12, "n": 1200}, 2 * 360 + 135, "embroid")
    assert late["late"] and late["acc"] > 1                             # 手填长针、高速：针扎下后绷架还在动
    assert j >= 0 and W > 0


def test_flatknit_carriage_follows_each_pass():
    p = {"sys": 2, "xfer": 4, "rack": 2}
    D, pp = C.cfg_of("flatknit", p)
    m0 = cad.parts3d(p, 0.0, "flatknit")
    assert m0["sys"] == 2 and sum(1 for q in m0["parts"] if q["name"].startswith("FK_CamPlateF")) == 2
    assert sum(1 for q in m0["parts"] if q["name"].startswith("FK_NeedleF")) == C.FK_N
    shape0 = _shape(m0)
    for j in (0, 1, D["widest"], D["first_x"]):
        tj = D["t"][j] / D["kw"]
        for fr in (0.1, 0.5, 0.95):
            m = cad.parts3d(p, j * 360 + fr * 360, "flatknit")
            assert _shape(m) == shape0
            s_, v_ = C.pass_pos(D, j, fr * tj)
            assert math.isclose(m["v"], v_) and v_ <= D["v"][j] + 1e-9
            assert m["kind"] == D["kind"][j] and m["idx"] == D["idx"][j] + 1
            assert (m["rack"] > 0) == (D["kind"][j] == "x")
    # 一趟走完：机头停在行程另一端（换向停顿），速度为 0；行程按 F.profile 的时间
    j = D["widest"]
    vp, ta, tc, tm = F.profile(D["D"][j], D["v"][j], D["a"])
    assert tm < D["t"][j] / D["kw"] and math.isclose(C.pass_top(D, j), vp)
    m = cad.parts3d(p, j * 360 + 359.9, "flatknit")
    assert m["v"] == 0 and math.isclose(m["x"], D["D"][j], abs_tol=1e-6)
    m = cad.parts3d(p, j * 360 + 360 * (ta + tc / 2) / (D["t"][j] / D["kw"]), "flatknit")
    assert math.isclose(m["v"], vp)                                     # 匀速段：机头在最高速度
    car = [q for q in m["parts"] if q["name"] == "FK_Bridge"][0]
    car0 = [q for q in cad.parts3d(p, j * 360, "flatknit")["parts"] if q["name"] == "FK_Bridge"][0]
    assert abs(car["base"][0] - car0["base"][0]) > 100                 # 机头真的从一端走到了另一端


def test_groups_and_no_cad_exports():
    assert cad.group_of("PT_NeedleBar") == "needle" and cad.group_of("PT_XSlide") == "x" and cad.group_of("PT_Seam") == "stitch"
    assert cad.group_of("EM_Hoop2") == "hoop" and cad.group_of("EM_Seam3_2") == "stitch" and cad.group_of("FK_CamF1") == "carriage"
    assert cad.group_of("FK_NeedleB12") == "needles" and cad.group_of("FK_Fabric") == "fabric"
    for m in C.MACHINES:                                               # 每个零件都分到了机构里（不落到默认的 frame，台板、机架除外）
        for q in cad.parts3d({}, 0.0, m)["parts"]:
            g = cad.group_of(q["name"])
            assert g != "frame" or any(k in q["name"] for k in ("Table", "Control", "Bed", "Plate", "Rail", "LowerShaft", "Wall")), q["name"]
    from app import sewing
    assert {"pattern", "embroid", "flatknit"} <= set(sewing.NO_CAD)     # 零件尺寸是示意：仍不出 STEP、宏、DXF
