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
