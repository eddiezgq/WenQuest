"""Course materials: store uploads, extract their text, classify them, plan a course from them.

A teacher drops a folder of files (syllabus, lesson plans, notes, slides, homework, quizzes,
lab guides, media). Each file is stored in the teacher's import session, its text extracted,
then classified by category and chapter. Classification uses filename and content rules and,
when a model is available, an AI pass for anything the rules cannot place. The teacher
reviews the table before a course is built.
"""
from __future__ import annotations

import io
import json
import re
import shutil
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

MAX_FILE = 50 * 1024 * 1024
MAX_TEXT = 60_000          # characters kept per file
SESSION_TTL = 24 * 3600

CATEGORIES = {
    "syllabus": "教学大纲",
    "calendar": "教学日历",
    "lesson_plan": "教案",
    "notes": "教材/讲义",
    "slides": "课件",
    "homework": "作业/习题",
    "quiz": "测验/试卷",
    "answer_key": "参考答案",
    "lab": "实验指导",
    "rubric": "评分标准",
    "media": "素材",
    "other": "其他",
}
# Files students should not see; they are attached hidden (teachers only).
TEACHER_ONLY = {"lesson_plan", "answer_key"}
TEXT_EXT = {".txt", ".md", ".csv"}
MEDIA_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".mp4", ".mov", ".mp3", ".wav"}


@dataclass
class Material:
    id: str
    name: str
    path: str                  # relative path inside the uploaded folder, e.g. "第1章/习题1.docx"
    size: int
    ext: str
    chars: int = 0
    pages: int = 0
    excerpt: str = ""
    category: str = "other"
    chapter: int | None = None  # None = whole course
    confidence: str = "rule"   # rule | ai | teacher
    error: str = ""
    headings: list[str] = field(default_factory=list)

    def public(self) -> dict:
        d = asdict(self)
        d["category_label"] = CATEGORIES.get(self.category, "其他")
        d["teacher_only"] = self.category in TEACHER_ONLY
        return d


# --- storage ---------------------------------------------------------------------------

class Store:
    """One directory per import session: <root>/<session>/{meta.json, <id>.bin, <id>.txt}."""

    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def new_session(self, user_id: int) -> str:
        self.cleanup()
        sid = uuid.uuid4().hex
        d = self.root / sid
        d.mkdir()
        (d / "meta.json").write_text(json.dumps({"user": user_id, "created": time.time(), "files": []}))
        return sid

    def _meta_path(self, sid: str) -> Path:
        if not re.fullmatch(r"[0-9a-f]{32}", sid or ""):
            raise KeyError("bad session")
        p = self.root / sid / "meta.json"
        if not p.exists():
            raise KeyError("no session")
        return p

    def load(self, sid: str, user_id: int) -> dict:
        meta = json.loads(self._meta_path(sid).read_text())
        if meta["user"] != user_id:
            raise PermissionError("not your session")
        return meta

    def save(self, sid: str, meta: dict) -> None:
        self._meta_path(sid).write_text(json.dumps(meta, ensure_ascii=False))

    def add(self, sid: str, user_id: int, m: Material, data: bytes, text: str) -> None:
        meta = self.load(sid, user_id)
        (self.root / sid / f"{m.id}.bin").write_bytes(data)
        (self.root / sid / f"{m.id}.txt").write_text(text)
        meta["files"] = [f for f in meta["files"] if f["path"] != m.path] + [asdict(m)]
        self.save(sid, meta)

    def materials(self, sid: str, user_id: int) -> list[Material]:
        return [Material(**f) for f in self.load(sid, user_id)["files"]]

    def put_materials(self, sid: str, user_id: int, items: list[Material]) -> None:
        meta = self.load(sid, user_id)
        meta["files"] = [asdict(m) for m in items]
        self.save(sid, meta)

    def text(self, sid: str, fid: str) -> str:
        p = self.root / sid / f"{fid}.txt"
        return p.read_text() if p.exists() and re.fullmatch(r"[0-9a-f]{32}", fid) else ""

    def data(self, sid: str, fid: str) -> bytes:
        p = self.root / sid / f"{fid}.bin"
        if not re.fullmatch(r"[0-9a-f]{32}", fid) or not p.exists():
            raise KeyError("no file")
        return p.read_bytes()

    def cleanup(self) -> None:
        now = time.time()
        for d in self.root.iterdir():
            try:
                meta = json.loads((d / "meta.json").read_text())
                if now - meta.get("created", 0) > SESSION_TTL:
                    shutil.rmtree(d, ignore_errors=True)
            except (OSError, ValueError):
                continue


# --- text extraction -------------------------------------------------------------------

def extract(name: str, data: bytes) -> tuple[str, int]:
    """Return (text, pages). Raises ValueError for unreadable files."""
    ext = Path(name).suffix.lower()
    if ext == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        pages = [(p.extract_text() or "").strip() for p in reader.pages]
        # Keep page markers so lessons can cite "p. N".
        return "\n\n".join(f"[第{i}页]\n{t}" for i, t in enumerate(pages, 1) if t), len(pages)
    if ext == ".docx":
        import docx
        doc = docx.Document(io.BytesIO(data))
        lines = []
        for block in doc.element.body.iterchildren():
            tag = block.tag.rsplit("}", 1)[-1]
            if tag == "p":
                t = "".join(n.text or "" for n in block.iter() if n.tag.endswith("}t")).strip()
                if t:
                    lines.append(t)
            elif tag == "tbl":
                for row in block.iter():
                    if row.tag.endswith("}tr"):
                        cells = ["".join(n.text or "" for n in c.iter() if n.tag.endswith("}t")).strip()
                                 for c in row.iter() if c.tag.endswith("}tc")]
                        lines.append(" | ".join(cells))
        return "\n".join(lines), 0
    if ext == ".pptx":
        from pptx import Presentation
        prs = Presentation(io.BytesIO(data))
        out = []
        for i, slide in enumerate(prs.slides, 1):
            texts = [sh.text_frame.text.strip() for sh in slide.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
            notes = slide.notes_slide.notes_text_frame.text.strip() if slide.has_notes_slide else ""
            out.append(f"[幻灯片{i}]\n" + "\n".join(texts) + (f"\n（讲者备注：{notes}）" if notes else ""))
        return "\n\n".join(out), len(prs.slides)
    if ext == ".xlsx":
        from openpyxl import load_workbook
        wb = load_workbook(io.BytesIO(data), data_only=True, read_only=True)
        out = []
        for ws in wb.worksheets:
            out.append(f"[工作表 {ws.title}]")
            for row in ws.iter_rows(values_only=True):
                vals = [str(v) for v in row if v not in (None, "")]
                if vals:
                    out.append(" | ".join(vals))
        return "\n".join(out), 0
    if ext in TEXT_EXT:
        for enc in ("utf-8", "gb18030"):
            try:
                return data.decode(enc), 0
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", "replace"), 0
    if ext in MEDIA_EXT:
        return "", 0
    raise ValueError("unsupported")


HEADING = re.compile(r"^\s*(\d+\.\d+(?:\.\d+)?)\s+(\S.{1,40})$")


def headings(text: str) -> list[str]:
    """Numbered section headings such as '1.3  抛体运动' (used to split chapters into lessons)."""
    seen, out = set(), []
    for line in text.splitlines():
        m = HEADING.match(line)
        if m and m.group(1).count(".") == 1 and m.group(1) not in seen:
            seen.add(m.group(1))
            out.append(f"{m.group(1)} {m.group(2).strip()}")
    return out


# --- rule-based classification ---------------------------------------------------------

CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
_RULES = [  # order matters: first match wins
    ("answer_key", r"答案|解答|参考答案|answer|solution"),
    ("rubric", r"评分标准|评分量规|量规|rubric|grading"),
    ("syllabus", r"大纲|syllabus|课程标准"),
    ("calendar", r"日历|进度表|教学进度|calendar|schedule"),
    ("lesson_plan", r"教案|教学设计|lesson\s*plan"),
    ("quiz", r"测验|试卷|考试|期中|期末|quiz|exam|test"),
    ("lab", r"实验|lab"),
    ("homework", r"作业|习题|练习|homework|assignment|exercise|problem"),
    ("slides", r"课件|幻灯|slides?|ppt"),
    ("notes", r"讲义|教材|笔记|notes|lecture|chapter|textbook"),
]


def chapter_of(path: str) -> int | None:
    for pat in (r"第\s*(\d+)\s*章", r"第\s*([一二三四五六七八九十])\s*章", r"\bch(?:apter)?\s*_?(\d+)", r"^(\d+)\s*[-_、.]"):
        for part in reversed(Path(path).parts):
            m = re.search(pat, part, re.I)
            if m:
                v = m.group(1)
                return CN_NUM.get(v) or int(v)
    m = re.search(r"(?:习题|作业|练习|homework)\s*(\d+)", Path(path).stem, re.I)
    return int(m.group(1)) if m else None


def classify_rule(m: Material) -> None:
    ext, stem = m.ext, Path(m.path).stem
    haystack = stem + " " + Path(m.path).parent.name
    cat = None
    for c, pat in _RULES:
        if re.search(pat, stem, re.I):
            cat = c
            break
    if cat is None and ext in MEDIA_EXT:
        cat = "media"
    if cat is None and ext == ".pptx":
        cat = "slides"
    if cat is None:
        for c, pat in _RULES:
            if re.search(pat, haystack, re.I):
                cat = c
                break
    # Content hints for files with vague names ("新建文本文档.txt").
    if cat is None and m.excerpt:
        head = m.excerpt[:400]
        for c, pat in (("syllabus", r"教学大纲|课程目标"), ("lesson_plan", r"教学目标.*教学重点|教学过程"),
                       ("homework", r"^\s*1[.、]"), ("notes", r"本章|第\s*\d+\s*章")):
            if re.search(pat, head, re.S | re.M):
                cat = c
                break
    m.category = cat or "other"
    m.chapter = chapter_of(m.path) if m.category not in ("syllabus", "calendar", "rubric") else None
    if m.category == "media" and m.chapter is None:
        m.chapter = None
    m.confidence = "rule" if cat else "unsure"


# --- AI classification -----------------------------------------------------------------

def classify_schema() -> dict:
    return {
        "type": "object",
        "properties": {"files": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "category": {"type": "string", "enum": list(CATEGORIES)},
                "chapter": {"type": ["integer", "null"], "description": "Chapter number, or null for whole-course files"},
            },
            "required": ["id", "category", "chapter"],
        }}},
        "required": ["files"],
    }


def classify_prompt(items: list[Material]) -> str:
    cats = "; ".join(f"{k} = {v}" for k, v in CATEGORIES.items())
    lines = [f"Classify each file of a teacher's course folder. Categories: {cats}.",
             "Also give the chapter number the file belongs to, or null if it covers the whole course "
             "(syllabus, calendar, rubric) or is unrelated to teaching content (use category 'other').",
             "Files (id | path | first lines of text):"]
    for m in items:
        lines.append(f"- {m.id} | {m.path} | {m.excerpt[:500].replace(chr(10), ' ')}")
    return "\n".join(lines)


def apply_ai(items: list[Material], data: dict) -> None:
    by_id = {m.id: m for m in items}
    for f in data.get("files") or []:
        m = by_id.get(str(f.get("id")))
        if not m or f.get("category") not in CATEGORIES:
            continue
        if m.confidence in ("unsure", "rule"):
            if m.confidence == "unsure" or m.category == "other":
                m.category = f["category"]
                m.confidence = "ai"
            ch = f.get("chapter")
            if m.chapter is None and isinstance(ch, int) and ch > 0:
                m.chapter = ch


# --- planning a course from materials ---------------------------------------------------

def chapters(items: list[Material]) -> list[int]:
    return sorted({m.chapter for m in items if m.chapter and m.category not in ("other",)})


def section_title_for(ch: int, items: list[Material], store_text) -> str:
    """Take the chapter title from a notes/slides file ("第1章  质点运动学") or the folder name."""
    for m in items:
        if m.chapter == ch and m.category in ("notes", "slides", "lesson_plan"):
            t = store_text(m.id)
            mm = re.search(rf"第\s*{ch}\s*章\s+([^\n，,。]{{2,30}})", t)
            if mm:
                return f"第{ch}章 {mm.group(1).strip()}"
    for m in items:
        if m.chapter == ch:
            folder = Path(m.path).parent.name
            if re.search(r"第\s*\d+\s*章", folder):
                return folder
    return f"第{ch}章"


def plan_schema() -> dict:
    t = {"type": "string"}
    return {
        "type": "object",
        "properties": {
            "title": t, "summary": t,
            "sections": {"type": "array", "items": {
                "type": "object",
                "properties": {
                    "chapter": {"type": "integer"},
                    "title": t, "summary": t,
                    "lessons": {"type": "array", "items": {
                        "type": "object", "properties": {"title": t, "goal": t}, "required": ["title", "goal"]}},
                },
                "required": ["chapter", "title", "summary", "lessons"],
            }},
        },
        "required": ["title", "summary", "sections"],
    }


def plan_prompt(items: list[Material], store_text, language: str) -> str:
    lang = "Simplified Chinese" if language == "zh" else "English"
    parts = [f"Plan an online course from the teacher's own materials. Write in {lang}.",
             "One section per chapter found in the materials, in chapter order. Split each chapter into 2-5 lessons "
             "that follow the numbered headings of its lecture notes (or slides / lesson plan when there are no notes). "
             "Lesson goals come from the lesson plan's teaching objectives when available. "
             "Take the course title from the syllabus. Do not add chapters the materials do not cover."]
    for m in items:
        if m.category in ("syllabus", "calendar"):
            parts.append(f"\n## {CATEGORIES[m.category]}: {m.path}\n{store_text(m.id)[:5000]}")
    for ch in chapters(items):
        parts.append(f"\n## Chapter {ch}")
        for m in items:
            if m.chapter == ch and m.category in ("notes", "lesson_plan", "slides"):
                heads = "; ".join(m.headings) if m.headings else ""
                parts.append(f"- {CATEGORIES[m.category]} {m.path}. Headings: {heads}\n{store_text(m.id)[:2500]}")
    return "\n".join(parts)


def rule_plan(items: list[Material], store_text) -> dict:
    """Outline without a model: chapters -> sections, numbered note headings -> lessons."""
    title = "新课程"
    for m in items:
        if m.category == "syllabus":
            mm = re.search(r"《([^》]{2,40})》", store_text(m.id)) or re.search(r"^(.{2,40})$", store_text(m.id), re.M)
            if mm:
                title = mm.group(1).strip().replace("课程教学大纲", "")
            break
    sections = []
    for ch in chapters(items):
        heads: list[str] = []
        for cat in ("notes", "slides", "lesson_plan"):
            for m in items:
                if m.chapter == ch and m.category == cat and m.headings:
                    heads = m.headings
                    break
            if heads:
                break
        lessons = [{"title": h, "goal": ""} for h in heads[:6]] or [{"title": f"{ch}.1 本章内容", "goal": ""}]
        sections.append({"chapter": ch, "title": section_title_for(ch, items, store_text), "summary": "",
                         "lessons": lessons})
    return {"title": title, "summary": "", "sections": sections}


def homework_brief(items: list[Material], ch: int, store_text) -> tuple[str, str] | None:
    for m in items:
        if m.chapter == ch and m.category == "homework":
            text = store_text(m.id).strip()
            title = Path(m.path).stem
            return title, text[:6000]
    return None


def source_ids(items: list[Material], ch: int) -> list[str]:
    """Files a lesson in chapter `ch` is written from, most authoritative first."""
    order = {"notes": 0, "lesson_plan": 1, "slides": 2, "lab": 3}
    picked = [m for m in items if m.chapter == ch and m.category in order and m.chars]
    return [m.id for m in sorted(picked, key=lambda m: order[m.category])]


def attachment_ids(items: list[Material], ch: int | None) -> list[str]:
    """Original files attached to a section (ch) or to the course overview section (None)."""
    keep = {"lesson_plan", "notes", "slides", "homework", "quiz", "answer_key", "lab", "rubric", "media",
            "syllabus", "calendar"}
    return [m.id for m in items if m.chapter == ch and m.category in keep]
