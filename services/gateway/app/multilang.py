"""Resolve Moodle multi-language markup to one language.

Teachers write bilingual text as adjacent spans:
    <span lang="zh_cn" class="multilang">中文</span><span lang="en" class="multilang">English</span>
and also the {mlang xx}...{mlang} form used by the popular multilang2 filter.
We resolve it in the gateway so the result does not depend on Moodle's filter
settings, and so nested <span> tags inside a translation are handled correctly.
"""
from __future__ import annotations

import re

LANG_ALIASES = {"zh": "zh_cn", "zh_cn": "zh_cn", "zh-cn": "zh_cn", "en": "en", "en_us": "en"}

_OPEN = re.compile(
    r'<span(?=[^>]*\bclass\s*=\s*["\']multilang["\'])(?=[^>]*\blang\s*=\s*["\']([A-Za-z0-9_-]+)["\'])[^>]*>',
    re.I,
)
_ANY_SPAN = re.compile(r"<span\b[^>]*>|</span\s*>", re.I)
_MLANG = re.compile(r"\{mlang\s+([A-Za-z0-9_,-]+)\s*\}(.*?)\{mlang\}", re.I | re.S)


def moodle_lang(lang: str | None) -> str:
    """Map a client language code (zh / en) to Moodle's (zh_cn / en)."""
    return LANG_ALIASES.get((lang or "").lower(), "en")


def _norm(code: str) -> str:
    return LANG_ALIASES.get(code.lower().replace("-", "_"), code.lower().replace("-", "_"))


def _match_close(text: str, start: int) -> int | None:
    """Given the index just after an opening <span>, return index just after its matching </span>."""
    depth = 1
    for m in _ANY_SPAN.finditer(text, start):
        if m.group(0).startswith("</"):
            depth -= 1
            if depth == 0:
                return m.end()
        else:
            depth += 1
    return None


def _pick(options: list[tuple[str, str]], want: str) -> str:
    for code, body in options:
        if _norm(code) == want:
            return body
    for code, body in options:
        if _norm(code) == "en":
            return body
    return options[0][1] if options else ""


def _resolve_spans(text: str, want: str) -> str:
    out: list[str] = []
    pos = 0
    while True:
        m = _OPEN.search(text, pos)
        if not m:
            out.append(text[pos:])
            break
        out.append(text[pos:m.start()])
        group: list[tuple[str, str]] = []
        cur = m
        end = m.start()
        while cur:
            close = _match_close(text, cur.end())
            if close is None:
                break
            inner = text[cur.end():close]
            inner = inner[: inner.lower().rfind("</span")]
            group.append((cur.group(1), inner))
            end = close
            # Next span belongs to the same group only if separated by whitespace.
            nxt = _OPEN.match(text, end + (len(text[end:]) - len(text[end:].lstrip())))
            cur = nxt
        if not group:  # malformed: keep the text as it is
            out.append(text[m.start():m.end()])
            pos = m.end()
            continue
        out.append(_resolve_spans(_pick(group, want), want))
        pos = end
    return "".join(out)


def _resolve_mlang(text: str, want: str) -> str:
    # Collect consecutive {mlang} blocks and pick one per run.
    result: list[str] = []
    pos = 0
    matches = list(_MLANG.finditer(text))
    i = 0
    while i < len(matches):
        run = [matches[i]]
        j = i + 1
        while j < len(matches) and text[run[-1].end():matches[j].start()].strip() == "":
            run.append(matches[j])
            j += 1
        result.append(text[pos:run[0].start()])
        options: list[tuple[str, str]] = []
        for m in run:
            for code in m.group(1).split(","):
                options.append((code, m.group(2)))
        other = [o for o in options if _norm(o[0]) != "other"]
        chosen = None
        for code, body in other:
            if _norm(code) == want:
                chosen = body
                break
        if chosen is None:
            fallback = [b for c, b in options if _norm(c) == "other"]
            chosen = fallback[0] if fallback else _pick(other, want)
        result.append(chosen)
        pos = run[-1].end()
        i = j
    result.append(text[pos:])
    return "".join(result)


def resolve(text: str | None, lang: str | None) -> str:
    """Return `text` with every multilang group reduced to the requested language."""
    if not text:
        return text or ""
    want = moodle_lang(lang)
    if "multilang" in text:
        text = _resolve_spans(text, want)
    if "{mlang" in text:
        text = _resolve_mlang(text, want)
    return text


_TAG = re.compile(r"<[^>]+>")


def plain(text: str | None, lang: str | None) -> str:
    """Resolve and strip tags: for titles and short summaries."""
    s = _TAG.sub("", resolve(text, lang))
    return re.sub(r"\s+", " ", s.replace("&nbsp;", " ")).strip()
