"""第 94 轮：红黄灯 → 出问题的部件、停的地方（计算核心 sewcore/hotspot.py，网页版讲解片和 FreeCAD 工作台共用）；
讲解片接口认 FreeCAD 钥匙。"""
import yaml

from app import sewcore
from app import sewing_video as SV
from app.sewcore import cad_seq as CS
from app.sewcore import hotspot as HS
from tests.test_materials import login
from tests.test_video3d import v3c  # noqa: F401

BAD = {"lockstitch": {"n": 6000}, "overlock": {"n": 9000}, "cover": {"dphi": 40}, "pattern": {"n": 3000},
       "embroid": {"n": 1400}, "flatknit": {"sys": 2, "xfer": 4, "rack": 4, "dwell": 0.01}}


def test_every_red_and_yellow_has_parts():
    for m, p in BAD.items():
        R = sewcore.get(m).analyze(sewcore.get(m).clean(p))
        hs = HS.hotspots(m, p, R)
        assert [h["key"] for h in hs] == [c["key"] for c in R["checks"] if c["state"] == "bad"] + \
            [c["key"] for c in R["checks"] if c["state"] == "warn"]
        assert any(h["state"] == "bad" for h in hs) or m == "overlock"
        names = {q["name"] for q in sewcore.cad.parts3d(p, 0.0, m)["parts"]}
        for h in hs:
            assert h["names"] and set(h["names"]) <= names, (m, h["key"])
            assert h["phi"] is None or h["phi"] >= 0
    assert HS.hotspots("lockstitch", {}) == []


def test_spindle_machines_stop_where_the_video_slows_down():
    hs = {h["key"]: h for h in HS.hotspots("lockstitch", BAD["lockstitch"])}
    assert hs["needle_force"]["phi"] == 180 and hs["frame_res"]["phi"] is None
    p = sewcore.get("cover").clean(BAD["cover"])
    catch, fd = HS.catch_fd("cover", p)
    for h in HS.hotspots("cover", p):
        assert h["phi"] == SV.problem_target("cover", h["key"], catch, fd, SV._avoid_angle(sewcore.get("cover"), p))[1]
        assert h["phi"] == catch                                    # 钩线三项都停在钩线角


def test_seq_machines_stop_on_the_same_stitch_as_the_video():
    """FreeCAD 用全部针（不抽样），讲解片用抽样后的轨迹：停的是同一针；进度角在讲解片慢放那一段的正中"""
    for m in ("pattern", "embroid", "flatknit"):
        p = sewcore.get(m).clean(BAD[m])
        full = CS.cfg_of(m, p)[0]
        thin = CS.video_track(m, full)
        R = sewcore.get(m).analyze(p)
        text, _ = SV.scene(m, p, "zh")
        angles = [a for _, a in yaml.safe_load(text)["motion"][0]["angle"]]
        for c in [c for c in R["checks"] if c["state"] != "ok"][:3]:
            grp, how = HS.seq_how(m, c)
            kt = HS.seq_target(m, thin, how)
            h = next(h for h in HS.hotspots(m, p, R) if h["key"] == c["key"])
            if kt is None:
                assert h["index"] is None and h["phi"] is None
                continue
            lo = 1 if m != "flatknit" else 0
            kt = max(lo, kt)
            assert thin["idx"][kt] == h["index"]                    # 同一针 / 同一趟
            start, span = HS.seq_slow(m, thin)
            assert any(abs(a - start(kt)) < 0.2 for a in angles)     # 讲解片从这里慢放
            assert abs(HS.seq_stop(m, thin, kt) - (start(kt) + span / 2)) < 0.11


def test_video_endpoint_takes_a_freecad_key(v3c):  # noqa: F811
    t, s_ = login(v3c, "t"), login(v3c, "s")
    body = {"machine": "pattern", "params": BAD["pattern"], "project": "PT-3000", "lang": "zh", "voice": False}
    assert v3c.post("/api/v1/admin/sewing/licenses", json={"username": "s", "org": "乙缝纫机厂"}, headers=t).status_code == 200
    kr = v3c.post("/api/v1/sewing/keys", headers=s_)
    assert kr.status_code == 200, kr.text
    key = kr.json()["key"]
    v3c.cookies.clear()                                                                 # 下面只凭钥匙（登录留下的 cookie 不算）
    assert v3c.post("/api/v1/sewing/video", json=body, headers={"X-WQ-Key": "nope"}).status_code == 401
    assert v3c.post("/api/v1/sewing/video", json=body).status_code == 401              # 没登录、没钥匙
    r = v3c.post("/api/v1/sewing/video", json=body, headers={"X-WQ-Key": key})
    assert r.status_code == 200, r.text
    t = login(v3c, "s")
    vid = r.json()["id"]
    assert r.json()["problems"]
    mine = [v["id"] for v in v3c.get("/api/v1/video3d", headers=t).json()["videos"]]
    assert vid in mine                                                                  # 记在钥匙主人名下，网页上找得到
    d = v3c.get(f"/api/v1/video3d/{vid}", headers=t).json()
    assert d["title"]["zh"].startswith("PT-3000")


def test_workbench_zip_has_everything_the_core_needs(tmp_path):
    """安装包里的计算核心单独拿出来（不连网关）也能出六种机型的零件、标红"""
    import io
    import subprocess
    import sys
    import zipfile
    from app.sewing import workbench_zip
    zipfile.ZipFile(io.BytesIO(workbench_zip())).extractall(tmp_path)
    mod = tmp_path / "Mod" / "WenQuestSewing"
    code = ("import sys; sys.path.insert(0, sys.argv[1]); from sewcore import cad, hotspot\n"
            "for m, p in [('lockstitch', {'n': 6000}), ('overlock', {}), ('cover', {'dphi': 40}), ('pattern', {'n': 3000}),"
            " ('embroid', {'n': 1400}), ('flatknit', {'sys': 2, 'xfer': 4, 'rack': 4, 'dwell': 0.01})]:\n"
            "    assert cad.parts3d(p, 400.0, m)['parts'] and hotspot.hotspots(m, p), m\n"
            "print('ok')")
    r = subprocess.run([sys.executable, "-I", "-c", code, str(mod)], capture_output=True, text=True, cwd=tmp_path)
    assert r.stdout.strip() == "ok", r.stderr[-2000:]
