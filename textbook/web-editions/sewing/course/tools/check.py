#!/usr/bin/env python3
"""Check a lesson file of the course pack (format in ../FORMAT.md).  Usage: python3 course/tools/check.py ch13 [ch14 ...] | all"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COURSE = HERE.parent
BOOK = COURSE.parent
LABS = {1: ['stitch'], 2: ['lockstitch', 'model-lockstitch'], 3: ['slidercrank'], 4: ['takeup'], 5: ['hook'], 6: ['feed'],
        7: ['tension'], 8: ['timing'], 9: ['model-overlock', 'difffeed', 'rssr'], 10: ['looper', 'coverstitch'], 11: ['zigzag'],
        12: ['hang', 'tend'], 13: ['solenoid', 'servo'], 14: ['trim'], 15: ['pattern', 'patprog', 'model-pattern'], 16: ['embroid'],
        17: ['knit', 'knitprog', 'fpga', 'model-flatknit'], 18: ['ebox'], 19: ['config'], 20: ['proto-ls'], 21: ['proto-fk'],
        22: ['testbench'], 23: ['tol'], 24: ['hookfit'], 25: ['cam'], 26: ['iot'], 27: ['factory'], 28: ['line21'], 29: ['line'],
        30: ['soft'], 31: ['aiqc']}
CJK = re.compile(r"[一-鿿]")


def check(name: str) -> list[str]:
    errs: list[str] = []
    p = COURSE / "lessons" / f"{name}.json"
    if not p.exists():
        return [f"{p} missing"]
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"not valid JSON: {e}"]
    no = int(name[2:])
    frag = (BOOK / "src" / "zh" / f"ch{no:02d}.html").read_text(encoding="utf-8")
    figs = set(re.findall(r'img/([^"/]+\.png)', frag))

    def pair(x, where, need=True):
        if not (isinstance(x, list) and len(x) == 2 and all(isinstance(s, str) for s in x)):
            errs.append(f"{where}: not a [zh, en] pair"); return
        zh, en = x
        if need and not (zh.strip() and en.strip()):
            errs.append(f"{where}: empty text")
        if CJK.search(en):
            errs.append(f"{where}: Chinese characters in the English text")
        if zh.strip() and not CJK.search(zh) and len(zh) > 12:
            errs.append(f"{where}: the Chinese text has no Chinese")
        if "<" in zh + en and re.search(r"</?[a-z]+[ >]", zh + en):
            errs.append(f"{where}: HTML is not allowed")

    def pairs(xs, where, lo, hi):
        if not isinstance(xs, list) or not (lo <= len(xs) <= hi):
            errs.append(f"{where}: needs {lo}-{hi} items, has {len(xs) if isinstance(xs, list) else '?'}"); return
        for i, x in enumerate(xs):
            pair(x, f"{where}[{i}]")

    def question(q, where):
        t = q.get("type")
        pair(q.get("text"), f"{where}.text"); pair(q.get("feedback"), f"{where}.feedback")
        if t in ("single", "multiple"):
            a = q.get("answers") or []
            for i, x in enumerate(a):
                pair(x.get("text"), f"{where}.answers[{i}]")
            right = sum(1 for x in a if x.get("correct") is True)
            if t == "single" and (len(a) != 4 or right != 1):
                errs.append(f"{where}: single needs 4 options, exactly 1 correct")
            if t == "multiple" and (not 4 <= len(a) <= 5 or not 2 <= right <= 3):
                errs.append(f"{where}: multiple needs 4-5 options, 2-3 correct")
        elif t == "truefalse":
            if not isinstance(q.get("correct"), bool):
                errs.append(f"{where}: truefalse needs correct: true/false")
        elif t == "numerical":
            if not isinstance(q.get("answer"), (int, float)) or not isinstance(q.get("tolerance"), (int, float)):
                errs.append(f"{where}: numerical needs answer and tolerance numbers")
        else:
            errs.append(f"{where}: unknown type {t}")

    if d.get("no") != no:
        errs.append("no does not match the file name")
    pair(d.get("title"), "title")
    if not isinstance(d.get("hours"), int) or not 2 <= d["hours"] <= 6:
        errs.append("hours: 2-6")
    pairs(d.get("goals"), "goals", 3, 5)
    for k in ("title", "text", "question", "answer"):
        pair((d.get("problem") or {}).get(k), f"problem.{k}")
    for sec in ("robot", "life"):
        for k in ("title", "text"):
            pair((d.get(sec) or {}).get(k), f"{sec}.{k}")
    sl = d.get("slides") or []
    if not 10 <= len(sl) <= 16:
        errs.append(f"slides: needs 10-16, has {len(sl)}")
    for i, s in enumerate(sl):
        pair(s.get("title"), f"slides[{i}].title")
        pairs(s.get("points"), f"slides[{i}].points", 2, 5)
        pair(s.get("narration"), f"slides[{i}].narration")
        if s.get("figure") and s["figure"] not in figs:
            errs.append(f"slides[{i}].figure {s['figure']} is not a figure of this chapter")
        if not isinstance(s.get("formula", ""), str):
            errs.append(f"slides[{i}].formula must be a string")
    pairs(d.get("summary"), "summary", 4, 6)
    labs = d.get("labs") or []
    ids = [x.get("id") for x in labs]
    if sorted(ids) != sorted(LABS[no]):
        errs.append(f"labs: must be exactly {LABS[no]}, has {ids}")
    for i, lb in enumerate(labs):
        w = f"labs[{i}]"
        pair(lb.get("title"), f"{w}.title")
        pairs(lb.get("goal"), f"{w}.goal", 2, 4)
        pairs(lb.get("theory"), f"{w}.theory", 2, 5)
        pairs(lb.get("steps"), f"{w}.steps", 5, 10)
        pairs(lb.get("questions"), f"{w}.questions", 2, 4)
        rec = lb.get("record") or {}
        pair(rec.get("caption"), f"{w}.record.caption")
        pairs(rec.get("headers"), f"{w}.record.headers", 2, 8)
        if not isinstance(rec.get("rows"), int):
            errs.append(f"{w}.record.rows must be a number")
        if not (BOOK / "src" / "zh" / "labs" / f"{lb.get('id')}.html").exists():
            errs.append(f"{w}: no lab page {lb.get('id')}")
    a = d.get("assignment") or {}
    pair(a.get("title"), "assignment.title")
    pairs(a.get("tasks"), "assignment.tasks", 2, 4)
    pair(a.get("deliverable"), "assignment.deliverable")
    pairs(a.get("rubric"), "assignment.rubric", 3, 5)
    qz = d.get("quiz") or []
    if not 8 <= len(qz) <= 10:
        errs.append(f"quiz: needs 8-10, has {len(qz)}")
    if sum(1 for q in qz if q.get("type") == "numerical") < 2:
        errs.append("quiz: at least 2 numerical questions")
    for i, q in enumerate(qz):
        question(q, f"quiz[{i}]")
    ex = d.get("exam") or []
    if len(ex) != 5:
        errs.append(f"exam: needs 5, has {len(ex)}")
    for i, q in enumerate(ex):
        question(q, f"exam[{i}]")
    texts = {json.dumps(q.get("text"), ensure_ascii=False) for q in qz}
    if any(json.dumps(q.get("text"), ensure_ascii=False) in texts for q in ex):
        errs.append("exam repeats a quiz question")
    pl = d.get("plan") or {}
    for k in ("key", "difficult", "homework"):
        pair(pl.get(k), f"plan.{k}")
    proc = pl.get("process") or []
    for i, x in enumerate(proc):
        pair(x.get("phase"), f"plan.process[{i}].phase"); pair(x.get("content"), f"plan.process[{i}].content")
    if proc and isinstance(d.get("hours"), int) and sum(int(x.get("minutes", 0)) for x in proc) != d["hours"] * 45:
        errs.append(f"plan.process minutes must add up to hours x 45 = {d.get('hours', 0) * 45}")
    return errs


def main() -> int:
    names = sys.argv[1:] or ["all"]
    if names == ["all"]:
        names = sorted(p.stem for p in (COURSE / "lessons").glob("ch*.json"))
    bad = 0
    for n in names:
        e = check(n)
        print(f"{n}: {'OK' if not e else str(len(e)) + ' error(s)'}")
        for x in e:
            print("   ✗", x)
        bad += len(e)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
