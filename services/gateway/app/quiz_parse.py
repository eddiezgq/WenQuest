"""Turn Moodle's rendered quiz questions into plain data WenQuest draws itself (web and mini program).

Supported: single / multiple choice, true-false, fill-in (short answer) and numerical questions. Other
question types keep a read-only copy of their HTML so the page can at least show them.
"""
from __future__ import annotations

import re
from typing import Any, Callable

from bs4 import BeautifulSoup, Tag

BLANK = "＿＿＿＿"


def _inner(el: Tag | None) -> str:
    return el.decode_contents().strip() if el else ""


def _classes(el: Tag) -> list[str]:
    c = el.get("class") or []
    return c if isinstance(c, list) else str(c).split()


def _state(el: Tag) -> str:
    cls = _classes(el)
    for s in ("correct", "partiallycorrect", "incorrect"):
        if s in cls:
            return s
    return ""


def parse_question(q: dict, clean: Callable[[str], str]) -> dict[str, Any]:
    """One question from mod_quiz_get_attempt_data / get_attempt_review."""
    html = (q.get("html") or "").split("<script")[0]
    soup = BeautifulSoup(html, "html.parser")
    root = soup.find("div", class_="que") or soup
    qtype = q.get("type") or ""
    out: dict[str, Any] = {
        "slot": q.get("slot"), "number": q.get("questionnumber") or q.get("number"), "type": qtype,
        "status": q.get("status") or "", "state": q.get("state") or "", "flagged": bool(q.get("flagged")),
        "mark": q.get("mark"), "maxmark": q.get("maxmark"), "sequence": None, "kind": "unsupported",
        "input": "", "options": [], "value": "", "feedback": "", "rightanswer": "", "result": _state(root),
    }
    seq = root.find("input", attrs={"name": re.compile(r":sequencecheck$")})
    if seq:
        out["sequence"] = {"name": seq["name"], "value": seq.get("value", "")}

    qtext = root.find("div", class_="qtext")
    fb = root.find("div", class_="feedback")
    if fb:
        ra = fb.find("div", class_="rightanswer")
        if ra:
            right = re.sub(r"^\s*(The correct answers? (is|are)[:：]?|正确答案是[:：]?)\s*", "", _inner(ra))
            if qtype == "truefalse":
                right = "true" if re.search(r"true|正确|对", right, re.I) else "false"
            out["rightanswer"] = clean(right.strip().strip("'\"‘’“”").rstrip("."))
            ra.extract()
        out["feedback"] = clean(_inner(fb))

    if qtype == "multichoice" or qtype == "truefalse":
        rows = root.select("div.answer > div")
        opts = []
        multi = False
        for row in rows:
            inp = row.find("input", attrs={"type": ["radio", "checkbox"]})
            if not inp or inp.get("value") == "-1":
                continue
            multi = multi or inp.get("type") == "checkbox"
            label = row.find(attrs={"data-region": "answer-label"})
            if label:
                num = label.find("span", class_="answernumber")
                if num:
                    num.extract()
                text = _inner(label.find("div", class_="flex-fill") or label)
            else:
                lab = row.find("label")
                text = _inner(lab)
            spec = row.find("div", class_="specificfeedback")
            opts.append({"name": inp.get("name"), "value": inp.get("value"), "label": clean(text),
                         "checked": inp.has_attr("checked"), "result": _state(row),
                         "feedback": clean(_inner(spec)) if spec else ""})
        if qtype == "truefalse":
            for o in opts:
                o["label"] = {"1": "true", "0": "false"}.get(o["value"], o["label"])
        out["kind"] = "multi" if multi else "choice"
        out["options"] = opts
        if not multi and opts:
            out["input"] = opts[0]["name"]
            out["value"] = next((o["value"] for o in opts if o["checked"]), "")
    elif qtype in ("shortanswer", "numerical"):
        inp = root.find("input", attrs={"type": "text", "name": re.compile(r"_answer$")})
        if inp:
            out["kind"] = "text"
            out["input"] = inp["name"]
            out["value"] = inp.get("value", "")
            out["result"] = _state(inp) or out["result"]
            out["numeric"] = qtype == "numerical"
            if qtext and qtext.find("input", attrs={"name": inp["name"]}):
                # A fill-in-the-blank: the box sits inside the sentence.
                blank = qtext.find("input", attrs={"name": inp["name"]})
                for sib in blank.find_next_siblings("i"):
                    sib.extract()
                blank.replace_with(BLANK)
                out["inline"] = True
    for lab in (qtext.find_all("label", class_="visually-hidden") if qtext else []):
        lab.extract()
    out["text"] = clean(_inner(qtext))
    if out["kind"] == "unsupported":
        body = root.find("div", class_="formulation") or root
        out["html"] = clean(_inner(body))
    return out


def form_data(questions: list[dict], answers: dict[str, Any]) -> list[dict[str, str]]:
    """Moodle's form fields for these answers: {slot: value | [values]} -> [{name, value}, ...]."""
    data: list[dict[str, str]] = []
    for q in questions:
        a = answers.get(str(q["slot"]))
        if q.get("sequence"):
            data.append(q["sequence"])
        if a is None or q["kind"] == "unsupported":
            continue
        if q["kind"] == "multi":
            chosen = {str(x) for x in (a if isinstance(a, list) else [a])}
            for o in q["options"]:
                data.append({"name": o["name"], "value": "1" if o["name"] in chosen else "0"})
        elif q["kind"] in ("choice", "text"):
            if str(a) != "":
                data.append({"name": q["input"], "value": str(a)[:1000]})
    return data
