"""第 56 轮：按设计尺寸一键出三维讲解片——网关自动写场景（全绿 / 有红灯）、过检查、参数锁定；
接口要开通缝纫机设计软件；开通的单位只能看、改自己的讲解片，不能拿“三维视频”另起别的片子。"""
import yaml

from app import sewcore
from app import sewing_video as SV
from app import video3d as v3
from app.sewcore import cad
from tests.test_materials import login
from tests.test_video3d import CALLS, settle, v3c  # noqa: F401


def test_scene_all_green_lockstitch():
    text, meta = SV.scene("lockstitch", {})
    spec, errs = v3.check(text)
    assert errs == [] and "&id" not in text
    assert meta["bad"] == 0 and meta["problems"] == [] and 35 <= meta["duration"] <= 60
    m = spec["models"][0]
    assert m["use"] == "gen:sewdesign" and m["machine"] == "lockstitch" and m["params"]["n"] == sewcore.get("lockstitch").clean({})["n"]
    # 主轴角单调不减（慢放靠两点之间转得慢），一路转到片尾
    ang = spec["motion"][0]["angle"]
    assert all(b[0] >= a[0] and b[1] >= a[1] for a, b in zip(ang, ang[1:])) and ang[-1][0] == spec["duration"]
    assert any("全部" in lb["zh"] and "合格" in lb["zh"] for lb in spec["labels"])
    assert v3.still_times(spec)


def test_scene_with_red_checks_slows_down_at_the_problem_angle():
    text, meta = SV.scene("lockstitch", {"n": 6000})
    spec, errs = v3.check(text)
    R = sewcore.get("lockstitch").analyze(sewcore.get("lockstitch").clean({"n": 6000}), trial=False)
    bad = [c["key"] for c in R["checks"] if c["state"] == "bad"]
    assert errs == [] and meta["bad"] == len(bad) >= 1 and meta["problems"][0] in bad
    assert meta["duration"] > SV.scene("lockstitch", {})[1]["duration"]
    # 下止点惯性力：那一段在 180° 附近慢放（每秒转的度数比整机那段小得多）
    ang = spec["motion"][0]["angle"]
    rates = [((b[1] - a[1]) / (b[0] - a[0]), a[1] % 360, b[1] % 360) for a, b in zip(ang, ang[1:]) if b[0] > a[0]]
    whole = rates[0][0]
    assert any(r < whole / 4 and (lo <= 180 <= hi or abs(lo - 180) < 30) for r, lo, hi in rates)
    # 关键画面里有一张正好停在 180°（场景自己写 stills）
    def phi_at(x):
        i = max(k for k in range(len(ang)) if ang[k][0] <= x)
        a, b = ang[i], ang[min(i + 1, len(ang) - 1)]
        return (a[1] + (b[1] - a[1]) * (x - a[0]) / max(1e-9, b[0] - a[0])) % 360
    times = v3.still_times(spec)
    assert len(times) == 6 and times == sorted(spec["stills"]) and any(abs(phi_at(x) - 180) < 1 for x in times[1:])
    # 字幕里的数就是计算核心的数，而且不截断（941 N 不能变成 94…）
    v = next(c for c in R["checks"] if c["key"] == "needle_force")["value"]["zh"]
    assert sum(v in lb["zh"] for lb in spec["labels"]) >= 2 and not any("…" in lb["zh"] or "…" in lb["en"] for lb in spec["labels"])
    # 红灯标题标红
    assert any(lb.get("tone") == "bad" and "不合格" in lb["zh"] for lb in spec["labels"])


def test_overlock_and_language():
    text, meta = SV.scene("overlock", {}, "en")
    spec, errs = v3.check(text)
    assert errs == [] and spec["lang"] == "en" and spec["models"][0]["machine"] == "overlock"
    assert spec["panel"]["head"] == "Readouts" and all(it["en"] == "" for it in spec["panel"]["items"])
    _, errs = v3.check(text.replace("lang: en", "lang: fr"))
    assert any("lang" in e for e in errs)


def test_lock_resets_the_design_and_keeps_the_numbers():
    text, meta = SV.scene("lockstitch", {"n": 6000})
    lock = {"model": "d", "machine": "lockstitch", "params": yaml.safe_load(text)["models"][0]["params"], "numbers": meta["numbers"]}
    hacked = text.replace("machine: lockstitch", "machine: overlock").replace("n: 6000", "n: 3000")
    out = yaml.safe_load(v3.apply_lock(hacked, lock))
    assert out["models"][0]["machine"] == "lockstitch" and out["models"][0]["params"]["n"] == 6000
    _, errs = v3.check(text.replace("machine: lockstitch", "machine: flatknit"))
    assert errs
    spec, _ = v3.check(text)
    assert v3.lock_errors(spec, lock) == []
    # 改字幕的数、换模型、加别的模型：都不行；改措辞、加 box 标示可以
    forged = yaml.safe_load(text)
    forged["labels"][-1]["zh"] = "全部 21 项校核合格，惯性力只有 500 N"
    assert any("500" in e for e in v3.lock_errors(forged, lock))
    swapped = yaml.safe_load(text)
    swapped["models"] = [{"id": "d", "use": "weblab:sewing/proto-lockstitch"}]
    assert len(v3.lock_errors(swapped, lock)) == 2
    ok = yaml.safe_load(text)
    ok["labels"][0]["zh"] = "我们这台平缝机：6000 r/min"
    ok["models"].append({"id": "m1", "use": "box", "size": [0.01, 0.01, 0.01], "at": [0, 0, 0]})
    assert v3.lock_errors(ok, lock) == []


def test_extent_counts_radius_so_the_hook_is_not_framed_too_close():
    c, d = SV._extent("lockstitch", {}, SV._names_in("lockstitch", {}, ["hook"]))
    hook = next(p for p in cad.parts3d({}, 0, "lockstitch")["parts"] if p["name"] == "RotaryHook")
    assert d >= 2 * max(c_[2] for c_ in hook["circles"]) * 0.001


def test_endpoint_needs_a_license_and_opens_only_sewing_videos(v3c):  # noqa: F811
    s, t = login(v3c, "s"), login(v3c, "t")
    body = {"machine": "lockstitch", "params": {"n": 6000}, "project": "LS-6000", "lang": "zh"}
    assert v3c.post("/api/v1/sewing/video", json=body, headers=s).status_code == 403
    assert v3c.post("/api/v1/sewing/video", json=dict(body, machine="flatknit"), headers=t).status_code == 422
    assert v3c.post("/api/v1/admin/sewing/licenses", json={"username": "s", "org": "甲缝纫机厂"}, headers=t).status_code == 200
    r = v3c.post("/api/v1/sewing/video", json=body, headers=s).json()
    assert r["problems"] and r["duration"] > 40
    d = settle(v3c, s, r["id"], lambda d: d["stills"].get("state") == "done")
    assert d["title"]["zh"].startswith("LS-6000") and "/stills" in CALLS and len(d["stills"]["urls"]) >= 4
    a = v3c.get("/api/v1/video3d/access", headers=s).json()
    assert a["allowed"] and a["sewing"] and not a["general"]
    # 开通缝纫机设计软件的单位：能看、改自己的讲解片；不能另起别的三维视频
    assert v3c.post("/api/v1/video3d", headers=s, json={"sample": "缝纫机一针"}).status_code == 403
    sc = d["scene"].replace("n: 6000", "n: 1000")
    d2 = v3c.put(f"/api/v1/video3d/{r['id']}/scene", headers=s, json={"scene": sc}).json()
    assert "n: 6000" in d2["scene"]                                  # 参数锁定：改不了
    arm = d["scene"].replace("\nmotion:", "\n- {id: arm, use: gen:arm6}\nmotion:", 1)    # 加一台机械臂另出别的片：不行
    x = v3c.put(f"/api/v1/video3d/{r['id']}/scene", headers=s, json={"scene": arm})
    assert x.status_code == 422 and "讲解片" in x.text
    idx = v3c.get("/api/v1/video3d", headers=s).json()
    assert idx["general"] is False and idx["samples"] == [] and [v["id"] for v in idx["videos"]] == [r["id"]]
    other = v3c.post("/api/v1/video3d", headers=t, json={"sample": "缝纫机一针"}).json()["id"]
    assert v3c.get(f"/api/v1/video3d/{other}", headers=s).status_code == 403


# ---------- 第 76 轮：绷缝机讲解片 ----------
def _phi_at(spec, x):
    ang = spec["motion"][0]["angle"]
    i = max(k for k in range(len(ang)) if ang[k][0] <= x)
    a, b = ang[i], ang[min(i + 1, len(ang) - 1)]
    return (a[1] + (b[1] - a[1]) * (x - a[0]) / max(1e-9, b[0] - a[0])) % 360


def test_cover_parts_follow_the_calculation():
    """针尖、弯针尖每个转角都和 cover.py 一致；针数、撑线器随线迹；不出 STEP 的零件名都带 CV_ 前缀"""
    from app.sewcore import cover as C
    for st, n, spread in (("401", 1, False), ("406", 2, False), ("407", 3, False), ("602", 2, True), ("605", 3, True)):
        m = cad.parts3d({"stitch": st, "g": 5.6}, 214, "cover")
        names = [p["name"] for p in m["parts"]]
        assert sum(x.startswith("CV_Needle") and x[9:].isdigit() for x in names) == n
        assert ("CV_SpArm" in names) == spread and ("CV_ThreadCover" in names) == spread
        assert all(x.startswith("CV_") for x in names) and {cad.group_of(x) for x in names} >= {"needle", "looper", "thread", "feed", "frame"}
    for prm in ({}, {"dphi": -6, "dz": 0.5, "rr": 4}):
        E = C.evaluate({k: C.clean(prm)[k] for k in ("dphi", "dz", "e", "gap", "rr")})
        for f in range(0, 360, 7):
            m = cad.parts3d(prm, f, "cover")
            assert abs(m["z_tip"] - C.ztip(f)) < 1e-9 and abs(m["lx"] - E["looper"](f)[0]) < 1e-9 and m["zb"] == E["zb"]
            tip = next(p for p in m["parts"] if p["name"] == "CV_Needle2")["base"][2]
            assert abs(tip - C.ztip(f)) < 1e-9
            blade = next(p for p in m["parts"] if p["name"] == "CV_Looper")["pts"][0]
            lx, ly = E["looper"](f)
            assert abs(blade[0] - lx) < 1e-9 and abs(blade[1] - ly) < 1e-9 and blade[2] == E["zb"]   # 模型 10-1 的 −y，Y 反向后是 +y
    # 线环：针回升时在钩线角附近张开，针在上面时没有
    loop = lambda f: next(p for p in cad.parts3d({}, f, "cover")["parts"] if p["name"] == "CV_Thread1")["pts"][4]   # noqa: E731
    assert abs(loop(214)[1]) > 1.0 and abs(loop(0)[1]) < 1.0


def test_cover_scene_green_and_red():
    from app.sewcore import cover as C
    text, meta = SV.scene("cover", {})
    spec, errs = v3.check(text)
    assert errs == [] and meta["bad"] == 0 and 40 <= meta["duration"] <= 75 and spec["models"][0]["machine"] == "cover"
    heads = [lb["zh"] for lb in spec["labels"] if lb["zh"][:1] in "①②③④⑤"]
    assert [h[0] for h in heads] == list("①②③④") and "撑线器" not in "".join(heads)          # 406 没有撑线器那段，段号不跳
    assert "撑线器" in "".join(lb["zh"] for lb in yaml.safe_load(SV.scene("cover", {"stitch": "605"})[0])["labels"])
    # 钩线段停在钩线角（关键画面里有一张）
    E = C.evaluate({"dphi": 0, "dz": 0, "e": 1.0, "gap": 0.03, "rr": 3.2})
    assert any(abs(_phi_at(spec, x) - E["fc"]) < 1 for x in spec["stills"])
    assert not any("STEP" in lb["zh"] for lb in spec["labels"]) and any("示意" in lb["zh"] for lb in spec["labels"])
    # 弯针定时 −6°：三项红灯；“针下行时让开弯针”在针下到弯针平面的转角慢放，字幕的数取自 analyze
    text, meta = SV.scene("cover", {"dphi": -6})
    spec, errs = v3.check(text)
    R = C.analyze(C.clean({"dphi": -6}))
    assert errs == [] and meta["bad"] == 3 and "descend" in meta["problems"]
    fd = C.evaluate({"dphi": -6, "dz": 0, "e": 1.0, "gap": 0.03, "rr": 3.2})["fd"]
    assert any(abs(_phi_at(spec, x) - fd) < 1 for x in spec["stills"])
    v = next(c for c in R["checks"] if c["key"] == "descend")["value"]["zh"]
    assert any(v in lb["zh"] for lb in spec["labels"]) and any(lb.get("tone") == "bad" for lb in spec["labels"])
    assert spec["panel"]["plot"]["key"] == "needle" and [it["key"] for it in spec["panel"]["items"]] == ["phi", "needle", "looper"]


def test_cover_endpoint(v3c):  # noqa: F811
    t = login(v3c, "t")
    assert v3c.post("/api/v1/admin/sewing/licenses", json={"username": "t", "org": "乙缝纫机厂"}, headers=t).status_code == 200
    r = v3c.post("/api/v1/sewing/video", json={"machine": "cover", "params": {"stitch": "605"}, "lang": "en"}, headers=t).json()
    assert r["duration"] > 40 and r["problems"] == []


def test_cover_loops_are_caught_one_after_another_and_odd_cases():
    """标准定时、605：弯针越过一根针以后，那根针的线环挂在弯针身上（环顶在弯针平面附近）；左边的针晚一些"""
    from app.sewcore import cover as C
    p = {"stitch": "605"}
    E = C.evaluate({"dphi": 0, "dz": 0, "e": 1.0, "gap": 0.03, "rr": 3.2})

    def top_z(f, i):
        th = next(q for q in cad.parts3d(p, f, "cover")["parts"] if q["name"] == f"CV_Thread{i}")
        return th["pts"][4][2]
    caught = lambda f, i: abs(top_z(f, i) - (E["zb"] + 0.6)) < 1e-9   # noqa: E731
    assert caught(E["fc"] + 1, 3) and not caught(E["fc"] + 1, 1)          # 最右一根先钩，最左一根还没到
    assert all(caught(E["fu"] + 10, i) for i in (1, 2, 3))                # 三根都挂在弯针上
    # 不合格时线环不挂上去（钩不住）
    E14 = C.evaluate({"dphi": 14, "dz": 0, "e": 1.0, "gap": 0.03, "rr": 3.2})
    th = next(q for q in cad.parts3d({"stitch": "605", "dphi": 14}, E14["fc"] + 1, "cover")["parts"] if q["name"] == "CV_Thread3")
    assert abs(th["pts"][4][2] - (E14["zb"] + 0.6)) > 0.1
    # 没有定时窗口：字幕照原话，不拼成“可行没有可行的定时”
    spec = yaml.safe_load(SV.scene("cover", {"gap": -0.05})[0])
    assert not any("可行没有" in lb["zh"] or "workable no" in lb["en"] for lb in spec["labels"])
    # 后侧相碰（gap 为负）：慢放到针回升时间隙最小的那一刻，而不是针下行时
    ang = SV._avoid_angle(C, C.clean({"gap": -0.05}))
    assert 180 <= ang <= E["fu"]
    _, meta = SV.scene("cover", {"gap": -0.05})
    assert "avoid" in meta["problems"]
