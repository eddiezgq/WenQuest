"""英文版的检查（第 8 轮 2.2）。

The English edition is the same book in another language: numbers, formulas, numbering, figures, animations and
labs come from the same sources; only the words are written twice. A section ``NN-M.en.md`` sits next to its Chinese
``NN-M.md``; these checks make sure the two cannot drift apart:

- parity     the same equation tags, directives (figures, programs, animations, labs, tables), numbered items
             (definitions, theorems, examples …), exercises, subsections and placeholders, in the same order;
- terms      every bold term is an English glossary entry, and every glossary term bolded in Chinese is bolded in
             English too;
- refs       Eq. (x.y.z), Figure/Example/Lab … x.y.z, Section x.y, Chapter n point at something that exists;
- code       the English copy of a program (code/en/NAME.py) differs from the Chinese one only in comments and
             docstrings, so it cannot compute anything else;
- values     a program run for the English edition (WQ_LANG=en, so figure labels and text values are English)
             hands over the same numbers as the Chinese run.
"""
from __future__ import annotations

import ast
import math
import re
from pathlib import Path

KINDS = {"Program": "程序", "Animation": "动画", "Lab": "实验", "Figure": "图", "Table": "表", "Task": "任务"}
LABEL = {v: k for k, v in KINDS.items()}
ITEMS = {"Definition": "定义", "Law": "定律", "Theorem": "定理", "Lemma": "引理", "Corollary": "推论", "Example": "算例"}
REFS = {**ITEMS, **KINDS, "Fig.": "图", "Exercise": "习题"}
LABELS = {"engineer's notes", "engineer’s notes", "exercises", "proof", "references", "summary", "note", "notes", "hint",
          "historical notes", "everyday example", "chapter references", "section references", "quick reference", "worked example"}

TAG = re.compile(r"\\tag\{([^}]+)\}")
FENCE = re.compile(r"^```.*?^```", re.S | re.M)
PLACE = re.compile(r"\{\{\s*(\w+)\.(\w+)\s*(?::[^}]+)?\}\}")
ZH_DIR = re.compile(r"^:::[ \t]*(程序|动画|实验|图|表)[ \t]+([\d.]+)", re.M)
EN_DIR = re.compile(r"^:::[ \t]*(" + "|".join(KINDS) + r")[ \t]+([\d.]+)", re.M)
ZH_ITEM = re.compile(r"\*\*(定义|定律|定理|引理|推论|算例) (\d+\.\d+\.\d+)")
EN_ITEM = re.compile(r"\*\*(" + "|".join(ITEMS) + r") (\d+\.\d+\.\d+)")
EXERCISE = re.compile(r"(?m)^(\d+\.\d+\.\d+)\s")
SUBSEC = re.compile(r"(?m)^#{3,4}\s+(\d+\.\d+\.\d+)\s")
ZH_TERM = re.compile(r"\*\*([\u4e00-\u9fff][\u4e00-\u9fff·\-–]{1,11})\*\*(?![：:])")
EN_TERM = re.compile(r"\*\*([A-Za-z][A-Za-z'’\-– ]{0,48}[A-Za-z])\*\*(?![:：])")
CJK = re.compile(r"[\u4e00-\u9fff]")


def structure(text: str, lang: str) -> dict:
    text = FENCE.sub("", text)
    if lang == "en":
        dirs = [(KINDS[k], n) for k, n in EN_DIR.findall(text)]
        items = [(ITEMS[k], n) for k, n in EN_ITEM.findall(text)]
    else:
        dirs = ZH_DIR.findall(text)
        items = ZH_ITEM.findall(text)
    return {"公式编号": TAG.findall(text), "图、程序、动画、实验、表": dirs, "定义、定理、算例": items,
            "习题": EXERCISE.findall(text), "小节": SUBSEC.findall(text),
            "占位符": sorted(set(PLACE.findall(text)))}


def parity(zh: str, en: str) -> list[str]:
    a, b = structure(zh, "zh"), structure(en, "en")
    out = []
    for k in a:
        if a[k] != b[k]:
            miss = [x for x in a[k] if x not in b[k]]
            extra = [x for x in b[k] if x not in a[k]]
            what = []
            if miss:
                what.append("英文版缺少 " + "、".join(map(_show, miss[:6])))
            if extra:
                what.append("英文版多出 " + "、".join(map(_show, extra[:6])))
            if not what:
                what.append("次序与中文版不同")
            out.append(f"{k}与中文版不一致：" + "；".join(what))
    return out


def _show(x) -> str:
    return " ".join(x) if isinstance(x, tuple) else str(x)


# ---------------------------------------------------------------- terms

def _norm(t: str) -> str:
    t = re.sub(r"\([^)]*\)", "", t.lower().replace("’", "'"))
    t = re.sub(r"[\s\-–]+", " ", t).strip()
    return re.sub(r"^(the|a|an) ", "", t)


def _forms(t: str) -> set[str]:
    t = _norm(t)
    out = {t}
    for suf in ("es", "s"):
        if t.endswith(suf):
            out.add(t[: -len(suf)])
    out.add(t + "s")
    return out


def english_names(row_en: str) -> list[str]:
    return [x.strip() for x in re.split(r"[;；]", row_en or "") if x.strip()]


def check_terms(zh: str, en: str, glossary: dict[str, str]) -> list[str]:
    """glossary: 中文 → English (alternatives separated by ';')."""
    out = []
    zh, en = FENCE.sub("", zh), FENCE.sub("", en)
    known: set[str] = set()
    for e in glossary.values():
        for name in english_names(e):
            known |= _forms(name)
    bold = [t for t in dict.fromkeys(EN_TERM.findall(en)) if _norm(t) not in LABELS]
    have: set[str] = set()
    for t in bold:
        f = _forms(t)
        have |= f
        if not f & known:
            out.append(f"英文版加粗的“{t}”不是术语表里的英文名（conventions/术语表.csv 的 English 列）")
    for t in dict.fromkeys(ZH_TERM.findall(zh)):
        names = english_names(glossary.get(t, ""))
        if not names:
            continue
        if not any(_forms(n) & have for n in names):
            out.append(f"中文版加粗的术语“{t}”，英文版没有加粗对应的“{' / '.join(names)}”")
    return out


# ---------------------------------------------------------------- references

EQ_LIST = re.compile(r"Eqs?\.\s*\((\d+\.\d+\.\d+)\)(?:\s*(?:,|and|to|or|–|-)\s*\((\d+\.\d+\.\d+)\))?")
REF = re.compile(r"\b(" + "|".join(re.escape(k) for k in REFS) + r")s?\s+(\d+\.\d+(?:\.\d+)?)")
SEC = re.compile(r"\bSections?\s+(\d+\.\d+(?:\.\d+)?)(?![\d.]*\d)")
CH = re.compile(r"\bChapters?\s+(\d+)")


def refs(text: str) -> tuple[set[str], list[str], list[int]]:
    """(item references in canonical form "式 4.1.2" / "图 4.1.1" …, section ids, chapter numbers)."""
    text = FENCE.sub("", text)
    text = re.sub(r"^:::.*$", "", text, flags=re.M)        # directive headers define, they do not refer
    items = set()
    for m in EQ_LIST.finditer(text):
        items.update(f"式 {x}" for x in m.groups() if x)
    for m in REF.finditer(text):
        items.add(f"{REFS[m.group(1)]} {m.group(2)}")
    return items, [m.group(1) for m in SEC.finditer(text)], [int(m.group(1)) for m in CH.finditer(text)]


# ---------------------------------------------------------------- programs and values

def _strip_docstrings(tree: ast.AST) -> ast.AST:
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                and isinstance(body[0].value.value, str):
            node.body = body[1:] or [ast.Pass()]
    return tree


def same_code(zh: Path, en: Path) -> str:
    """'' when the two programs are the same apart from comments and docstrings, else what is wrong."""
    if not en.exists():
        return f"没有英文注释的程序副本 code/en/{zh.name}"
    try:
        a = ast.dump(_strip_docstrings(ast.parse(zh.read_text(encoding="utf-8"))))
        b = ast.dump(_strip_docstrings(ast.parse(en.read_text(encoding="utf-8"))))
    except SyntaxError as e:
        return f"程序有语法错误：{e}"
    if a != b:
        return f"code/en/{zh.name} 与中文版的代码不同（只能改注释和文档字符串）"
    if CJK.search(_code_text(en)):
        return f"code/en/{zh.name} 的注释里还有中文"
    return ""


def _code_text(p: Path) -> str:
    """Comments and docstrings only (what a reader of the English edition reads besides the code)."""
    src = p.read_text(encoding="utf-8")
    import io
    import tokenize
    out = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            out.append(tok.string)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                and isinstance(body[0].value.value, str):
            out.append(body[0].value.value)
    return "\n".join(out)


def same_values(zh: dict, en: dict, prog: str) -> list[str]:
    out = []
    if set(zh) != set(en):
        out.append(f"{prog}.py 两种语言交出的结果项不同：{sorted(set(zh) ^ set(en))}")
    for k in set(zh) & set(en):
        if not _num_equal(zh[k], en[k]):
            out.append(f"{prog}.py 的 {k} 在英文版运行时数值不同（数字不能随语言变化）")
    return out


def _num_equal(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b or (math.isfinite(a) and math.isfinite(b) and abs(a - b) <= 1e-12 * max(1.0, abs(a)))
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_num_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_num_equal(a[k], b[k]) for k in a)
    if isinstance(a, str) and isinstance(b, str):
        return True          # text may be translated
    return type(a) is type(b)
