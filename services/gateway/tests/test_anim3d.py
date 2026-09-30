"""Round 4 · step 3: 3D animation — templates, the self-contained scene page, the 3D opener joined to the video."""
import json
import re
import shutil
import subprocess

import pytest

from app import main
from app import studio as st
from app.production import anim, library_sample as L, scene3d as S
from tests.test_materials import login
from tests.test_studio import _write_first_lesson, client, settle  # noqa: F401 - the fixture

need_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="needs ffmpeg")


@pytest.fixture(scope="module")
def models(tmp_path_factory):
    root = L.build(tmp_path_factory.mktemp("lib"))
    return S.load_models(root / L.VERSION, ["B-ARM-6R-S", "B-MOB-DIFF-S", "C-LNK-4BAR-S"])


def test_templates_make_scripts(models):
    sc = S.build({"template": "showcase", "items": [{"id": "B-ARM-6R-S", "name": ["臂", "Arm"], "line": ["一", "one"]},
                                                   {"id": "B-MOB-DIFF-S", "name": ["车", "Base"], "line": ["二", "two"]}]}, models)
    assert [a["model"] for a in sc["actors"]] == ["B-ARM-6R-S", "B-MOB-DIFF-S"] and sc["duration"] > 9
    assert any(s["joint"].startswith("wheel") for s in sc["spin"])      # continuous joints spin
    j = S.joints("B-ARM-6R-S", models, [{"shoulder_pan": 1.0, "nonsense": 3}])
    assert {t["joint"] for t in j["tracks"]} >= {"shoulder_pan"} and "nonsense" not in {t["joint"] for t in j["tracks"]}
    assert j["traces"] and j["frames"]
    assert S.build({"template": "mechanism", "item": "C-LNK-4BAR-S"}, models)["motion"]
    with pytest.raises(S.Render3DError):
        S.build({"template": "joints", "item": "B-NOPE"}, {})


def test_the_page_is_self_contained(models):
    sc = S.build({"template": "joints", "item": "B-ARM-6R-S"}, models)
    html = S.page(sc, models)
    assert "WQ3D.player" in html and "B-ARM-6R-S" in html
    assert not re.search(r"""(src|href)=["']https?://""", html)       # nothing loaded from the network
    assert "C-LNK-4BAR-S" not in html                                 # only the models the scene uses


def test_plans_are_cleaned(models):
    p = st.normalize_plan3d({"template": "joints", "item": "B-ARM-6R-S",
                             "poses": [{"values": [{"joint": "elbow", "value": 99}, {"joint": "x", "value": 1}]}],
                             "captions": [{"from": 0, "to": 3, "text": ["看", "Look"]}]}, models)
    assert p["poses"] == [{"elbow": 2.8}] and p["captions"] == [[0.0, 3.0, ["看", "Look"]]]
    assert st.normalize_plan3d({"template": "hack", "item": "zzz"}, models)["template"] == "joints"


def _clip(path, seconds, color):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c={color}:s=1280x720:d={seconds}:r=30",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path.read_bytes()


@need_ffmpeg
def test_the_3d_opener_is_joined_to_the_lesson_video(client, monkeypatch, tmp_path):
    three = _clip(tmp_path / "a.mp4", 2, "blue")
    manim = _clip(tmp_path / "b.mp4", 3, "red")
    calls = []

    async def render3d(url, page_html, duration, **kw):
        calls.append(page_html)
        return three, b"\xff\xd8\xff", 2.0, [b"\xff\xd8\xff"]

    async def render(url, code, timeout=600.0):
        from PIL import Image
        import io
        b = io.BytesIO()
        Image.new("RGB", (64, 36), "#0f1419").save(b, "PNG")
        return manim, b.getvalue(), 3.0, [b.getvalue()]

    monkeypatch.setattr(S, "render", render3d)
    monkeypatch.setattr(anim, "render", render)
    monkeypatch.setattr(main.state.settings, "animator_url", "http://animator.test")
    monkeypatch.setattr(main.state.settings, "labcheck_url", "http://labcheck.test")
    from app.production import labs

    async def trial_run(url, page_html, lab, timeout=150.0):
        return {"ok": True, "problems": [], "tasks": {}, "screenshot": b"", "seconds": 1.0}
    monkeypatch.setattr(labs, "trial_run", trial_run)
    h = login(client)
    pid, p = _write_first_lesson(client, h)
    les = p["outline"]["chapters"][0]["lessons"][0]
    assert len(calls) == 1 and "WQ3D.player" in calls[0]
    video = next(f for f in les["files"] if f["kind"] == "animation")
    assert video["seconds"] == 5.0
    d = main._studio().lesson_dir(main._studio().projects.load(pid), les)
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(d / video["name"])], capture_output=True, text=True).stdout
    assert abs(float(out) - 5.0) < 0.3
    note = next(c for c in les["checklist"] if c["key"] == "animation")["note"]
    assert "三维动画" in note
