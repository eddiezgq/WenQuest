"""Textbook build and checks (第 7 轮 2.3): the real section 4.1 passes; every kind of mistake is stopped."""
import shutil
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import build  # noqa: E402

ROBOTICS = TOOLS.parent / "robotics"


@pytest.fixture
def book(tmp_path):
    """A copy of the robotics book in a temporary folder, to break on purpose."""
    root = tmp_path / "textbook" / "robotics"
    shutil.copytree(ROBOTICS, root, ignore=shutil.ignore_patterns("__pycache__"))
    return root


def run(root, **kw):
    return build.build("robotics", root=root, **kw)


def kinds(rep):
    return {(p.kind, p.text.split("：")[0]) for p in rep.errors}


def edit(root, old, new, path="ch04/04-1.md"):
    p = root / path
    t = p.read_text(encoding="utf-8")
    assert old in t, old
    p.write_text(t.replace(old, new, 1), encoding="utf-8")


def test_the_real_book_passes_and_is_in_line_with_the_outline(tmp_path):
    out = tmp_path / "out"
    rep = build.build("robotics", out_dir=out)
    assert not rep.errors, "\n".join(map(str, rep.errors))
    frag = (out / "web" / "4.1.html").read_text(encoding="utf-8")
    assert "<svg" in frag and "x_p = 0.123205" in frag and "{{" not in frag   # numbers in formulas are SVG glyphs
    assert "WQMATH" not in frag and "WQTOKEN" not in frag
    idx = (out / "web" / "index.json").read_text(encoding="utf-8")
    assert '"no": 61' in idx


def test_a_number_typed_by_hand_is_stopped(book):
    edit(book, "{{ex4_1_1.x_p}}\\ \\mathrm{m}, \\\\", "0.12322\\ \\mathrm{m}, \\\\")
    rep = run(book)
    assert any(p.kind == "手写数字" and "0.12322" in p.text for p in rep.errors)


def test_placeholders_programs_formulas_numbering_references_terms(book):
    edit(book, "{{ex4_1_1.r}}", "{{ex4_1_1.radius}}")                       # not handed over by the program
    edit(book, "\\tag{4.1.3}", "\\tag{4.1.9}")                              # numbering out of order
    edit(book, "式 (4.1.5) 的 2×2", "式 (4.1.12) 的 2×2")                   # reference to nothing
    edit(book, "R(\\theta) = \\begin{pmatrix} \\cos", "R(\\theta = \\frac{ \\begin{pmatrix} \\cos")  # broken formula
    edit(book, "**主动转动**", "**主动旋转术**")                              # term not in the glossary
    edit(book, "第 5 章作为定理", "第 75 章作为定理")                          # no such chapter
    rep = run(book)
    text = "\n".join(map(str, rep.errors))
    assert "ex4_1_1.radius" in text
    assert "公式编号应从 1 起连续" in text
    assert "式 4.1.12 不存在" in text
    assert any(p.kind == "公式" for p in rep.errors)
    assert "主动旋转术" in text
    assert "第 75 章不存在" in text


def test_a_failing_program_stops_the_build(book):
    p = book / "ch04" / "code" / "ex4_1_1.py"
    p.write_text(p.read_text(encoding="utf-8").replace("theta = math.radians(30)", "theta = math.radians(31)"), encoding="utf-8")
    edit(book, "R(30^\\circ) = \\begin{pmatrix}", "R(30^\\circ) = \\begin{pmatrix}")   # text unchanged
    rep = run(book)
    # the program's own checks still hold at 31°, so it runs; the numbers in the book follow it automatically
    assert not [e for e in rep.errors if e.kind == "程序"]
    frag = (book.parent / "build" / "robotics" / "web" / "4.1.html").read_text(encoding="utf-8")
    assert "x_p = 0.123205" not in frag and "x_p = 0.11" in frag
    p.write_text(p.read_text(encoding="utf-8") + "\nraise SystemExit('核对失败')\n", encoding="utf-8")
    rep = run(book)
    assert any(e.kind == "程序" for e in rep.errors)


def test_section_files_must_match_the_outline(book):
    (book / "ch04" / "04-9.md").write_text("---\nid: \"4.99\"\ntitle: 不存在的节\n---\n正文\n", encoding="utf-8")
    rep = run(book)
    assert any("4.99 不在提纲里" in p.text for p in rep.errors)


def test_significant_digits_keep_trailing_zeros():
    assert build.sig(0.1866025403784) == "0.18660"
    assert build.sig(26.565051177) == "26.565"
    assert build.sig(0.05) == "0.050000"
