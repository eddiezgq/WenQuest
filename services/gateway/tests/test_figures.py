"""Round 4 · step 2: the illustrator's figures (graph, chart, drawing, scene), checks and failures."""
import shutil

import pytest

from app import main
from app.production import figures as F
from tests.test_materials import login
from tests.test_studio import _write_first_lesson, client, settle  # noqa: F401 - the fixture

need_dot = pytest.mark.skipif(not shutil.which("dot"), reason="needs Graphviz")


def test_labels_follow_the_course_language():
    assert F.text_of(["机器人", "Robot"], "zh") == "机器人"
    assert F.text_of(["机器人", "Robot"], "en") == "Robot"
    assert F.text_of(["机器人", "Robot"], "both") == "机器人\nRobot"
    assert F.text_of(["同", "同"], "both") == "同"


def test_graph_file_is_written_by_us_and_escapes_labels():
    dot = F.graph_dot({"nodes": [{"id": "a", "label": ['引号"x"', "quote"]}, {"id": "b", "label": ["b", "b"]}],
                       "edges": [{"from": "a", "to": "b"}, {"from": "a", "to": "zzz"}]}, "zh")
    assert '\\"x\\"' in dot and "n_zzz" not in dot and "system" not in dot


@need_dot
def test_graph_and_chart_render(tmp_path):
    g = F.render_graph({"direction": "LR", "nodes": [{"id": "a", "label": ["正运动学", "FK"]}, {"id": "b", "label": ["末端位姿", "Pose"]}],
                        "edges": [{"from": "a", "to": "b"}]}, "both", tmp_path / "g")
    assert F.png_ok(tmp_path / g["png"]) and (tmp_path / g["svg"]).read_text().startswith("<?xml")
    c = F.render_chart({"type": "line", "x_label": ["t", "t"], "y_label": ["θ", "θ"],
                        "series": [{"x": [0, 1, 2], "y": [0, 1, 4]}]}, "zh", tmp_path / "c")
    assert F.png_ok(tmp_path / c["png"])
    with pytest.raises(F.FigureError):
        F.render_chart({"series": []}, "zh", tmp_path / "x")


@need_dot
def test_a_figure_that_misses_its_purpose_is_left_out_and_said(client, monkeypatch):
    ai = main.state.ai
    orig = ai.json
    seen = []

    async def spy(**kw):
        if "relevance check" in kw.get("system", "") and "概念图" in kw.get("prompt", ""):
            seen.append(kw.get("images"))
            return {"on_topic": False, "reason": "图里是另一门课的内容", "fix": "画本课的概念"}
        return await orig(**kw)
    monkeypatch.setattr(ai, "json", spy)
    h = login(client)
    _, p = _write_first_lesson(client, h)
    les = p["outline"]["chapters"][0]["lessons"][0]
    assert len(seen) == 2 and seen[0] and seen[0][0][0] == "image/png"     # the reviewer saw the picture, twice
    figs = [f for f in les["files"] if f["kind"] == "figure"]
    assert len(figs) == 1                                                    # the drawing passed, the concept map did not
    item = next(c for c in les["checklist"] if c["key"] == "figures")
    assert item["ok"] is False and "1/2" in item["note"] and "本课概念图" in item["note"]
