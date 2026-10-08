"""Make teacher-authored HTML safe to show in the WenQuest frontend."""
from __future__ import annotations

import re
from typing import Callable

import nh3

TAGS = {
    "p", "br", "hr", "div", "span", "section", "article", "blockquote", "pre", "code", "kbd", "samp",
    "strong", "b", "em", "i", "u", "s", "sub", "sup", "small", "mark", "abbr",
    "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "dl", "dt", "dd",
    "table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption", "colgroup", "col",
    "a", "img", "figure", "figcaption", "video", "audio", "source", "track", "iframe",
}
ATTRS = {
    "*": {"title", "lang", "dir"},
    "a": {"href", "target"},
    "img": {"src", "alt", "width", "height"},
    "video": {"src", "controls", "width", "height", "poster", "preload"},
    "audio": {"src", "controls", "preload"},
    "source": {"src", "type"},
    "track": {"src", "kind", "srclang", "label"},
    "iframe": {"src", "width", "height", "allowfullscreen", "title"},
    "td": {"colspan", "rowspan"}, "th": {"colspan", "rowspan", "scope"},
    "ol": {"start", "type"}, "col": {"span"},
}
FORCED = {
    "iframe": {"sandbox": "allow-scripts allow-same-origin allow-popups allow-forms", "loading": "lazy"},
    "a": {"rel": "noopener noreferrer"},
}

_URL_ATTR = re.compile(r'(\s(?:src|href|poster)=")([^"]+)(")', re.I)


def clean(html: str, moodle_base: str, sign: Callable[[str], str]) -> str:
    """Sanitize HTML and route Moodle file links through the gateway's file proxy."""
    safe = nh3.clean(
        html or "",
        tags=TAGS,
        attributes=ATTRS,
        set_tag_attribute_values=FORCED,
        allowed_classes={"div": {"wq-fig"}, "p": {"wq-cap"}, "a": {"wq-factory"}},   # figures; the live factory workshop
        url_schemes={"http", "https", "mailto"},
        link_rel=None,
    )
    base = moodle_base.rstrip("/")

    def swap(m: re.Match) -> str:
        url = m.group(2).replace("&amp;", "&")
        if url.startswith(base + "/pluginfile.php/"):
            url = url.replace("/pluginfile.php/", "/webservice/pluginfile.php/", 1)
        if url.startswith(base + "/webservice/pluginfile.php/"):
            return m.group(1) + sign(url) + m.group(3)
        return m.group(0)

    return _URL_ATTR.sub(swap, safe)


KINDS = {
    "video": {"mp4", "webm", "mov", "m4v", "ogv"},
    "pdf": {"pdf"},
    "slides": {"ppt", "pptx", "pps", "ppsx", "key", "odp"},
    "lab": {"html", "htm"},
    "doc": {"doc", "docx", "odt", "rtf", "txt", "md"},
    "sheet": {"xls", "xlsx", "csv", "ods"},
    "image": {"png", "jpg", "jpeg", "gif", "svg", "webp"},
    "audio": {"mp3", "wav", "m4a", "ogg"},
}


_YT = re.compile(r"^https?://(?:www\.|m\.)?(?:youtube\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/|live/)|youtu\.be/)([A-Za-z0-9_-]{11})")
_BILI = re.compile(r"^https?://(?:www\.|m\.)?bilibili\.com/video/(BV[0-9A-Za-z]{10})")


def video_link(url: str | None) -> dict | None:
    """A B 站 or YouTube page link -> the provider's own embeddable player (第 25 轮：讲课视频). Anything else -> None."""
    u = (url or "").strip()
    m = _YT.match(u)
    if m:
        return {"provider": "youtube", "id": m.group(1), "page": f"https://www.youtube.com/watch?v={m.group(1)}",
                "embed": f"https://www.youtube-nocookie.com/embed/{m.group(1)}?rel=0&autoplay=1"}
    m = _BILI.match(u)
    if m:
        p = re.search(r"[?&]p=(\d+)", u)
        page = f"&page={p.group(1)}" if p else ""
        return {"provider": "bilibili", "id": m.group(1), "page": f"https://www.bilibili.com/video/{m.group(1)}",
                "embed": f"https://player.bilibili.com/player.html?bvid={m.group(1)}{page}&high_quality=1&danmaku=0&autoplay=1"}
    return None


def file_kind(filename: str | None, mimetype: str | None = None) -> str:
    """What the frontend should do with a file: play it, show it, run it, or offer it for download."""
    ext = (filename or "").rsplit(".", 1)[-1].lower() if "." in (filename or "") else ""
    if ext in ("html", "htm") and re.search(r"课件|slides", filename or "", re.I):
        return "deck"   # 网页互动课件（第 24 轮）：放映，和实验页一样在隔离框里运行
    for kind, exts in KINDS.items():
        if ext in exts:
            return kind
    mt = (mimetype or "").lower()
    for prefix, kind in (("video/", "video"), ("image/", "image"), ("audio/", "audio")):
        if mt.startswith(prefix):
            return kind
    if mt == "application/pdf":
        return "pdf"
    return "file"
