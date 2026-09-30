"""The teacher's textbook is an instruction; scanned textbooks are read by text recognition (OCR)."""
import io
import shutil

import pytest
from PIL import Image, ImageDraw, ImageFont

from app import main
from app import materials as mt
from app import studio as st
from tests.test_materials import docx_bytes, login
from tests.test_studio import client, settle  # noqa: F401 - the fixture


def scanned_pdf(pages: list[list[str]]) -> bytes:
    """A PDF whose pages are pictures of text (like a scanned book)."""
    font = None
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf"):
        try:
            font = ImageFont.truetype(path, 34)
            break
        except OSError:
            continue
    imgs = []
    for lines in pages:
        im = Image.new("RGB", (1240, 1754), "white")
        d = ImageDraw.Draw(im)
        for i, ln in enumerate(lines):
            d.text((120, 140 + i * 70), ln, fill="black", font=font or ImageFont.load_default())
        imgs.append(im)
    buf = io.BytesIO()
    imgs[0].save(buf, "PDF", save_all=True, append_images=imgs[1:], resolution=150)
    return buf.getvalue()


def new_project(c, h, text):
    return c.post("/api/v1/studio/projects", headers=h, json={"description": text}).json()["id"]


def put(c, h, pid, path, data):
    r = c.post(f"/api/v1/studio/projects/{pid}/files", headers=h, data={"path": path},
               files={"file": (path.rsplit("/", 1)[-1], data, "application/octet-stream")})
    assert r.status_code == 200, r.text
    return r.json()


def test_named_textbooks_and_matching():
    assert st.named_textbooks(["教材用《机器人学导论》第4版", "参考《现代机器人学》"]) == ["机器人学导论", "现代机器人学"]
    assert st.named_textbooks(["The textbook is Craig"]) == ["Craig"]
    assert st.named_textbooks(["请按《教学大纲》来"]) == []
    a = mt.Material(id="a" * 32, name="Craig 机器人学导论 第4版.pdf", path="x", size=9, ext=".pdf", pages=400)
    b = mt.Material(id="b" * 32, name="第1章 讲义.docx", path="y", size=1, ext=".docx")
    best, score = st.match_textbook(["机器人学导论"], [b, a], {}, lambda fid: "")
    assert best == a.id and score == 1.0


def test_the_named_textbook_wins_over_the_librarians_guess(client):
    h = login(client)
    pid = new_project(client, h, "机器人学，本科高年级专业课，教材用《机器人学导论》")
    put(client, h, pid, "资料/Introduction to Robotics 讲义.docx", docx_bytes(["第1章 空间描述和变换"]))
    put(client, h, pid, "资料/机器人学导论（第4版）.docx", docx_bytes(["机器人学导论", "目录", "第1章 概述"]))
    client.post(f"/api/v1/studio/projects/{pid}/start", headers=h)
    p = settle(client, h, pid)
    tb = p["materials"]["textbook"]
    assert next(f for f in p["files"] if f["id"] == tb)["name"] == "机器人学导论（第4版）.docx"
    assert "按你的要求，主教材定为《机器人学导论》" in p["messages"][-1]["text"]


def test_a_named_textbook_that_is_missing_is_asked_for_not_guessed(client):
    h = login(client)
    pid = new_project(client, h, "机器人学，教材用《现代机器人学》")
    put(client, h, pid, "资料/第1章 讲义.docx", docx_bytes(["第1章 空间描述"]))
    put(client, h, pid, "资料/book.docx", docx_bytes(["Robot Modeling and Control", "Contents"]))
    client.post(f"/api/v1/studio/projects/{pid}/start", headers=h)
    p = settle(client, h, pid)
    q = next(q for q in p["questions"] if q.get("kind") == "textbook")
    assert "没有在资料里找到你指定的教材《现代机器人学》" in q["text"] and "book.docx" in q["options"]
    assert "没有在资料里找到" in p["messages"][-1]["text"]
    # the teacher picks the file: it becomes the main textbook
    p = client.post(f"/api/v1/studio/projects/{pid}/questions/{q['id']}", headers=h, json={"answer": "book.docx"}).json()
    assert next(f for f in p["files"] if f["id"] == p["materials"]["textbook"])["name"] == "book.docx"


@pytest.mark.skipif(not shutil.which("tesseract"), reason="needs Tesseract (text recognition)")
def test_a_scanned_textbook_is_read_by_text_recognition(client):
    h = login(client)
    pid = new_project(client, h, "Robotics, textbook: Introduction to Robotics")
    pages = [["Introduction to Robotics", "Mechanics and Control"], ["Contents"] + [f"{i} Chapter title {i} ........ {i * 3}" for i in range(1, 6)],
             ["Preface"], ["Chapter 1 Spatial descriptions", "A robot arm is described by frames."]]
    m = put(client, h, pid, "book/Introduction to Robotics.pdf", scanned_pdf(pages))
    assert m["error"] == "scanned" and m["pages"] == 4
    client.post(f"/api/v1/studio/projects/{pid}/start", headers=h)
    p = settle(client, h, pid, timeout=120)
    f = next(x for x in p["files"] if x["name"] == "Introduction to Robotics.pdf")
    assert not f["error"]
    studio = main._studio()
    text = studio.text(studio.projects.load(pid), f["id"])
    assert "[第2页]" in text and "Contents" in text and "robot arm" in text.lower()
