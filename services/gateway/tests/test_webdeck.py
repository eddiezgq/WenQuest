"""Round 32 附二: AI-built lessons get the web interactive deck (the 《缝纫机设计与制造》 standard), not PowerPoint."""
import json
from pathlib import Path

from app.production import webdeck
from tests.test_lesson_edit import spec_of, written_lesson
from tests.test_studio import client, moodle  # noqa: F401 - the fixture

ROOT = Path(__file__).resolve().parents[3]


def test_the_engine_is_the_one_the_textbooks_use():
    for name in ("wc_slides.py", "wc_config.py"):
        mine = (ROOT / "services/gateway/app/production" / name).read_text(encoding="utf-8")
        theirs = (ROOT / "textbook/tools/webcourse" / name).read_text(encoding="utf-8")
        assert mine == theirs, f"copy textbook/tools/webcourse/{name} to services/gateway/app/production/ again"


def test_a_written_lesson_has_a_web_deck_and_no_powerpoint_for_students(client):
    h, pid, lid, st = written_lesson(client)
    _, les = spec_of(st, pid, lid)
    slides = [f for f in les["files"] if f["kind"] == "slides"]
    assert len(slides) == 1 and slides[0]["name"].endswith("课件.html")
    assert not any(f["name"].endswith(".pptx") for f in les["files"])
    proj = st.projects.load(pid)
    d = st.lesson_dir(proj, les)
    html = (d / slides[0]["name"]).read_text(encoding="utf-8")
    assert 'id="deck-data"' in html and "讲者" in html and html.count('<div class="slide ') >= 8
    data = json.loads(html.split('id="deck-data">', 1)[1].split("</script>", 1)[0].replace("<\\/", "</"))
    assert data["presenter"] and data["clips"]
    deck = json.loads((d / "deck.json").read_text(encoding="utf-8"))["slides"]
    assert deck[0]["layout"] == "cover" and any(s["layout"] == "summary" for s in deck)


def test_designer_pages_are_checked_and_unsafe_drawings_cleaned():
    assets = {"anim": True, "lab": True, "figures": [{"name": "fig-1", "title": ["图", "Fig"]}]}
    good = webdeck.clean_slide({"layout": "split", "title": "标题", "points": [["一", "one"]],
                                "visual": {"svg": "<svg viewBox='0 0 9 9'><script>x()</script><circle r='3' onclick='x()'/></svg>"}}, assets)
    assert good and "script" not in good["visual"]["svg"] and "onclick" not in good["visual"]["svg"]
    assert webdeck.clean_slide({"layout": "figure", "title": ["a", "b"], "visual": {"fig": "nope"}}, assets) is None
    assert webdeck.clean_slide({"layout": "lab", "title": ["a", "b"], "tasks": []}, {"lab": False}) is None
    assert webdeck.clean_slide({"layout": "nonsense"}, assets) is None
    cover = webdeck.clean_slide({"layout": "cover", "video": "missing", "title": ["t", "T"]}, assets)
    assert cover["video"] == "anim"
