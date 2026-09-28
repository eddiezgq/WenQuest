"""AI course workshop (智能课件工坊): brief -> outline -> lessons -> a real course.

Texts are carried as {"zh": ..., "en": ...} with one or both keys, depending on the course
languages. On publish, bilingual texts become Moodle multi-language markup, which both the
WenQuest app and Moodle's classic view display in the reader's chosen language.
"""
from __future__ import annotations

import html
import re
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

Languages = Literal["zh", "en", "both"]


def lang_keys(languages: str) -> list[str]:
    return ["zh", "en"] if languages == "both" else [languages]


# --- request models -------------------------------------------------------------------

class Brief(BaseModel):
    topic: str = Field(min_length=2, max_length=300)
    audience: str = Field(default="", max_length=300)
    level: str = Field(default="", max_length=100)
    sections: int = Field(default=4, ge=1, le=16)
    lessons_per_section: int = Field(default=2, ge=1, le=5)
    assignments: bool = True
    languages: Languages = "zh"
    notes: str = Field(default="", max_length=30000, description="Syllabus, outline or material pasted by the teacher")


class LessonRequest(BaseModel):
    import_id: str = ""
    sources: list[str] = Field(default_factory=list, max_length=8)
    course_title: str = Field(max_length=300)
    section_title: str = Field(max_length=300)
    lesson_title: str = Field(max_length=300)
    goal: str = Field(default="", max_length=1000)
    audience: str = Field(default="", max_length=300)
    level: str = Field(default="", max_length=100)
    languages: Languages = "zh"
    notes: str = Field(default="", max_length=30000)


class Text(BaseModel):
    zh: str = ""
    en: str = ""


class DraftLesson(BaseModel):
    title: Text
    content: Text = Text()
    sources: list[str] = Field(default_factory=list)


class DraftAssignment(BaseModel):
    title: Text
    brief: Text = Text()


class DraftSection(BaseModel):
    title: Text
    summary: Text = Text()
    lessons: list[DraftLesson] = Field(default_factory=list, max_length=12)
    assignment: DraftAssignment | None = None
    files: list[str] = Field(default_factory=list, max_length=60)


class Draft(BaseModel):
    title: Text
    summary: Text = Text()
    languages: Languages = "zh"
    import_id: str = ""
    sections: list[DraftSection] = Field(min_length=1, max_length=20)


# --- JSON schemas the model must follow --------------------------------------------------

def _text_schema(languages: str, what: str) -> dict:
    keys = lang_keys(languages)
    names = {"zh": "Simplified Chinese", "en": "English"}
    return {
        "type": "object",
        "properties": {k: {"type": "string", "description": f"{what} in {names[k]}"} for k in keys},
        "required": keys,
    }


def outline_schema(languages: str, with_assignment: bool) -> dict:
    t = lambda what: _text_schema(languages, what)  # noqa: E731
    section = {
        "type": "object",
        "properties": {
            "title": t("Section title, e.g. 'Chapter 1 ...'"),
            "summary": t("One sentence: what students will be able to do after this section"),
            "lessons": {"type": "array", "items": {
                "type": "object",
                "properties": {"title": t("Lesson title"), "goal": t("Learning goal of the lesson, one sentence")},
                "required": ["title", "goal"],
            }},
        },
        "required": ["title", "summary", "lessons"],
    }
    if with_assignment:
        section["properties"]["assignment"] = {
            "type": "object",
            "properties": {"title": t("Assignment title"),
                           "brief": t("What students must do and hand in, 2-4 sentences")},
            "required": ["title", "brief"],
        }
        section["required"].append("assignment")
    return {
        "type": "object",
        "properties": {
            "title": t("Course title"),
            "summary": t("Course description for students, 2-3 sentences"),
            "sections": {"type": "array", "items": section},
        },
        "required": ["title", "summary", "sections"],
    }


def lesson_schema(languages: str) -> dict:
    return {
        "type": "object",
        "properties": {"content": _text_schema(languages, "Lesson content as HTML")},
        "required": ["content"],
    }


# --- prompts ---------------------------------------------------------------------------

SYSTEM = (
    "You are the course designer of WenQuest (问渠), an AI-native teaching platform. "
    "You design clear, well-sequenced courses that a real teacher can publish after a quick review. "
    "Principles: every lesson has one concrete learning goal; build from intuition to formalism; "
    "use worked examples and checks for understanding; prefer the teacher's own material and wording "
    "when provided, and never contradict it; do not invent citations, statistics or quotes. "
    "When writing both Chinese and English, write each natively rather than translating word for word."
)


def outline_prompt(b: Brief) -> str:
    langs = {"zh": "Simplified Chinese only", "en": "English only", "both": "both Simplified Chinese and English"}[b.languages]
    parts = [
        f"Design a course outline.\nTopic: {b.topic}",
        f"Students: {b.audience or 'not specified'}",
        f"Level: {b.level or 'not specified'}",
        f"Structure: exactly {b.sections} sections, each with exactly {b.lessons_per_section} lessons"
        + (", and one practical assignment per section." if b.assignments else ", no assignments."),
        f"Write every text in {langs}.",
    ]
    if b.notes.strip():
        parts.append("The teacher's material (follow its scope, order and terminology):\n<<<\n"
                     + b.notes.strip() + "\n>>>")
    return "\n".join(parts)


def lesson_prompt(r: LessonRequest, sources: str = "") -> str:
    langs = {"zh": "Simplified Chinese only", "en": "English only", "both": "both Simplified Chinese and English (one full version each)"}[r.languages]
    parts = [
        f"Write the full content of one lesson.\nCourse: {r.course_title}\nSection: {r.section_title}\n"
        f"Lesson: {r.lesson_title}\nLearning goal: {r.goal or 'derive from the title'}",
        f"Students: {r.audience or 'not specified'}; level: {r.level or 'not specified'}",
        f"Language: {langs}.",
        "Length: about 500-900 words (or 800-1400 Chinese characters) per language.",
        "Structure: a one-line goal; an intuitive explanation; key concepts with at least one worked example; "
        "a short summary; 2-3 check-your-understanding questions (no answers).",
        "Format: HTML using only h3, h4, p, ul, ol, li, strong, em, code, pre, blockquote, table, tr, th, td. "
        "No h1/h2, no inline styles, no scripts, no images. Write formulas as plain text, e.g. u = Kp·e.",
    ]
    if sources:
        parts.append("Write the lesson FROM the teacher's own files below: keep their scope, notation, examples and "
                     "terminology, reorganise and explain rather than invent. After each paragraph or example that "
                     "comes from a file, cite it inline in brackets, e.g. （参考：1-质点运动学讲义.pdf 第2页）. "
                     "Only cover what belongs to this lesson title.\n" + sources)
    elif r.notes.strip():
        parts.append("The teacher's material (stay consistent with it):\n<<<\n" + r.notes.strip()[:12000] + "\n>>>")
    return "\n".join(parts)


# --- fake provider output (tests, offline demos) --------------------------------------

def fake_outline(b: Brief) -> dict:
    keys = lang_keys(b.languages)

    def t(zh: str, en: str) -> dict:
        return {k: (zh if k == "zh" else en) for k in keys}

    sections = []
    for i in range(1, b.sections + 1):
        s = {
            "title": t(f"第 {i} 章 {b.topic}（{i}）", f"Chapter {i}: {b.topic} ({i})"),
            "summary": t(f"学完本章，你能说明{b.topic}的第 {i} 个核心概念。",
                         f"After this chapter you can explain core idea {i} of {b.topic}."),
            "lessons": [{"title": t(f"{i}.{j} 第 {j} 课", f"{i}.{j} Lesson {j}"),
                         "goal": t(f"理解第 {i}.{j} 个要点", f"Understand point {i}.{j}")}
                        for j in range(1, b.lessons_per_section + 1)],
        }
        if b.assignments:
            s["assignment"] = {"title": t(f"作业 {i}", f"Assignment {i}"),
                               "brief": t("完成练习并提交说明。", "Complete the exercise and submit a short write-up.")}
        sections.append(s)
    return {"title": t(b.topic, b.topic), "summary": t(f"一门关于{b.topic}的课程。", f"A course on {b.topic}."),
            "sections": sections}


def fake_lesson(r: LessonRequest, source: tuple[str, str] | None = None) -> dict:
    keys = lang_keys(r.languages)
    if source:  # offline mode with materials: quote the start of the first source and cite it
        name, text = source
        para = html.escape(" ".join(text.split())[:300])
        body = f"<h3>学习目标</h3><p>{html.escape(r.goal or r.lesson_title)}</p><h3>讲解</h3><p>{para}（参考：{html.escape(name)}）</p>"
        return {"content": {k: body for k in keys}}
    body = {
        "zh": f"<h3>学习目标</h3><p>{html.escape(r.goal or r.lesson_title)}</p><h3>讲解</h3><p>这是《{html.escape(r.lesson_title)}》的示例内容。</p>"
              "<h3>小结</h3><ul><li>要点一</li><li>要点二</li></ul>",
        "en": f"<h3>Goal</h3><p>{html.escape(r.goal or r.lesson_title)}</p><h3>Explanation</h3><p>Sample content for {html.escape(r.lesson_title)}.</p>"
              "<h3>Summary</h3><ul><li>Point one</li><li>Point two</li></ul>",
    }
    return {"content": {k: body[k] for k in keys}}


# --- normalising model output ------------------------------------------------------------

def norm_text(value, keys: list[str]) -> dict:
    """Accept {zh, en} objects or bare strings; keep only the course languages."""
    if isinstance(value, str):
        value = {keys[0]: value}
    if not isinstance(value, dict):
        value = {}
    return {k: str(value.get(k) or "").strip() for k in keys}


def norm_outline(data: dict, b: Brief) -> dict:
    keys = lang_keys(b.languages)
    sections = []
    for s in (data.get("sections") or [])[:16]:
        sec = {
            "title": norm_text(s.get("title"), keys),
            "summary": norm_text(s.get("summary"), keys),
            "lessons": [{"title": norm_text(l.get("title"), keys), "goal": norm_text(l.get("goal"), keys),
                         "content": {k: "" for k in keys}}
                        for l in (s.get("lessons") or [])[:5] if isinstance(l, dict)],
            "assignment": None,
        }
        a = s.get("assignment")
        if b.assignments and isinstance(a, dict):
            sec["assignment"] = {"title": norm_text(a.get("title"), keys), "brief": norm_text(a.get("brief"), keys)}
        sections.append(sec)
    return {"title": norm_text(data.get("title"), keys), "summary": norm_text(data.get("summary"), keys),
            "languages": b.languages, "sections": sections}


# --- draft -> Moodle -------------------------------------------------------------------

def ml(t: Text, languages: str, is_html: bool = False) -> str:
    """One string for Moodle: plain for one language; two languages as multilang markup.

    Names use <span lang class="multilang"> (Moodle keeps it in plain-text fields). HTML uses
    {mlang xx}...{mlang}, because Moodle's HTML cleaner moves block tags such as <p> out of
    inline spans and would glue the languages together. The multilang2 filter renders it in
    the classic view; the gateway resolves both forms itself."""
    keys = lang_keys(languages)
    vals = {k: getattr(t, k).strip() for k in keys}
    present = [k for k in keys if vals[k]]
    if not present:
        return ""
    if len(present) == 1:
        return vals[present[0]]
    code = {"zh": "zh_cn", "en": "en"}
    if is_html:
        return "".join(f"{{mlang {code[k]}}}{vals[k]}{{mlang}}" for k in present)
    return "".join(f'<span lang="{code[k]}" class="multilang">{vals[k]}</span>' for k in present)


def paragraphs(text: str) -> str:
    """Plain text (assignment briefs, summaries) -> safe HTML paragraphs."""
    return "".join(f"<p>{html.escape(p.strip())}</p>" for p in re.split(r"\n\s*\n|\n", text) if p.strip())


def shortname_for(d: Draft) -> str:
    en = d.title.en.strip()
    if en:
        words = [w for w in re.findall(r"[A-Za-z0-9]+", en) if w.lower() not in {"to", "of", "and", "the", "a", "an", "for", "in"}]
        initials = "".join(w[0].upper() for w in words)[:8]
        if initials:
            return f"{initials}-{date.today():%Y%m}"
    return f"WQ-{date.today():%Y%m%d}"


def to_moodle(d: Draft, clean_html) -> dict:
    """Build the local_wenquest_create_course payload. `clean_html` sanitizes lesson HTML."""
    lg = d.languages

    def html_text(t: Text, plain: bool) -> str:
        conv = Text(**{k: (paragraphs(getattr(t, k)) if plain else clean_html(getattr(t, k)))
                       for k in ("zh", "en")})
        return ml(conv, lg, is_html=True)

    sections = []
    for s in d.sections:
        acts = [{"type": "page", "name": ml(l.title, lg), "content": html_text(l.content, plain=False)}
                for l in s.lessons if ml(l.title, lg)]
        if s.assignment and ml(s.assignment.title, lg):
            acts.append({"type": "assign", "name": ml(s.assignment.title, lg),
                         "intro": html_text(s.assignment.brief, plain=True)})
        sections.append({"name": ml(s.title, lg) or "—", "summary": html_text(s.summary, plain=True),
                         "activities": acts})
    return {"fullname": ml(d.title, lg) or "Untitled course", "shortname": shortname_for(d),
            "summary": html_text(d.summary, plain=True), "sections": sections}
