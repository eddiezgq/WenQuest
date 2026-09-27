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
