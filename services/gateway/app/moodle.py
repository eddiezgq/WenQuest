"""Teaching-engine adapter for Moodle.

Everything the gateway knows about Moodle lives here, so another engine
(for example Canvas) can be added later by writing a second adapter.
"""
from __future__ import annotations

from typing import Any
from urllib.parse import urlencode, urlsplit

import httpx

from .multilang import moodle_lang


class EngineError(Exception):
    """A Moodle error, mapped to a stable code the frontend can translate."""

    def __init__(self, code: str, message: str = "", status: int = 400):
        super().__init__(message or code)
        self.code = code
        self.message = message
        self.status = status


# Moodle error codes -> (our code, http status)
_ERRORS = {
    "invalidlogin": ("invalid_login", 401),
    "invalidtoken": ("session_expired", 401),
    "usernotfullysetup": ("account_incomplete", 403),
    "sitemaintenance": ("maintenance", 503),
    "restrictedcontextexception": ("forbidden", 403),
    "requireloginerror": ("forbidden", 403),
    "nopermissions": ("forbidden", 403),
    "invalidrecord": ("not_found", 404),
    "invalidrecordunknown": ("not_found", 404),
    "invalidcoursemodule": ("not_found", 404),
    "enablewsdescription": ("engine_misconfigured", 503),
    "accessexception": ("engine_misconfigured", 503),
    "servicenotavailable": ("engine_misconfigured", 503),
}


def _raise_for(payload: Any) -> None:
    if isinstance(payload, dict) and ("exception" in payload or "errorcode" in payload or "error" in payload):
        mcode = payload.get("errorcode") or ""
        code, status = _ERRORS.get(mcode, ("engine_error", 502))
        raise EngineError(code, payload.get("message") or payload.get("error") or mcode, status)


def _flatten(params: dict[str, Any], prefix: str = "") -> list[tuple[str, str]]:
    """Moodle REST wants nested params as courseids[0]=2&options[0][name]=x."""
    out: list[tuple[str, str]] = []
    for key, value in params.items():
        name = f"{prefix}[{key}]" if prefix else str(key)
        if isinstance(value, dict):
            out += _flatten(value, name)
        elif isinstance(value, (list, tuple)):
            out += _flatten({i: v for i, v in enumerate(value)}, name)
        elif isinstance(value, bool):
            out.append((name, "1" if value else "0"))
        elif value is not None:
            out.append((name, str(value)))
    return out


class MoodleClient:
    """`base_url` is Moodle's public address (its wwwroot). `connect_url`, if given, is
    where the gateway actually connects (e.g. http://moodle inside docker); requests then
    carry the public Host header, because Moodle refuses requests for any other host."""

    def __init__(self, base_url: str, service: str, client: httpx.AsyncClient, connect_url: str = ""):
        self.base = base_url.rstrip("/")
        self.connect = (connect_url or base_url).rstrip("/")
        self.service = service
        self.http = client
        pub = urlsplit(self.base)
        self.headers: dict[str, str] = {}
        if self.connect != self.base:
            self.headers = {"Host": pub.netloc, "X-Forwarded-Proto": pub.scheme, "X-Forwarded-Host": pub.netloc}

    def _url(self, path_or_public_url: str) -> str:
        if path_or_public_url.startswith(self.base + "/"):
            return self.connect + path_or_public_url[len(self.base):]
        return self.connect + path_or_public_url

    async def login(self, username: str, password: str) -> str:
        try:
            r = await self.http.post(
                self._url("/login/token.php"),
                data={"username": username, "password": password, "service": self.service},
                headers=self.headers,
            )
        except httpx.HTTPError as exc:
            raise EngineError("engine_unreachable", str(exc), 503) from exc
        data = _json(r)
        _raise_for(data)
        token = data.get("token") if isinstance(data, dict) else None
        if not token:
            raise EngineError("invalid_login", "no token", 401)
        return token

    async def call(self, token: str, function: str, lang: str | None = None, **params: Any) -> Any:
        query = [("wstoken", token), ("wsfunction", function), ("moodlewsrestformat", "json")]
        if lang:
            query.append(("moodlewssettinglang", moodle_lang(lang)))
        # Ask for raw text (file links still rewritten) and resolve languages in the
        # gateway: Moodle strips multilang tags from names when its filter is not
        # applied, which would leave both languages glued together.
        query.append(("moodlewssettingraw", "true"))
        query.append(("moodlewssettingfilter", "false"))
        query.append(("moodlewssettingfileurl", "true"))
        try:
            r = await self.http.post(
                self._url("/webservice/rest/server.php"), params=query,
                content=urlencode(_flatten(params)),
                headers={**self.headers, "Content-Type": "application/x-www-form-urlencoded"},
            )
        except httpx.HTTPError as exc:
            raise EngineError("engine_unreachable", str(exc), 503) from exc
        data = _json(r)
        _raise_for(data)
        return data

    async def fetch_file(self, token: str, url: str) -> httpx.Response:
        """Download a Moodle file URL on the user's behalf (only URLs on our Moodle)."""
        if not url.startswith(self.base + "/"):
            raise EngineError("forbidden", "foreign file url", 403)
        sep = "&" if "?" in url else "?"
        try:
            r = await self.http.get(f"{self._url(url)}{sep}token={token}", headers=self.headers)
        except httpx.HTTPError as exc:
            raise EngineError("engine_unreachable", str(exc), 503) from exc
        if r.status_code == 404:
            raise EngineError("not_found", "file", 404)
        if "application/json" in r.headers.get("content-type", ""):
            _raise_for(_json(r))
        return r

    async def upload(self, token: str, filename: str, data: bytes) -> int:
        """Put a file in the user's draft area; returns the draft item id for a resource."""
        try:
            r = await self.http.post(self._url("/webservice/upload.php"), headers=self.headers,
                                     data={"token": token, "filearea": "draft", "itemid": "0"},
                                     files={"file_1": (filename, data, "application/octet-stream")})
        except httpx.HTTPError as exc:
            raise EngineError("engine_unreachable", str(exc), 503) from exc
        payload = _json(r)
        _raise_for(payload)
        if not isinstance(payload, list) or not payload:
            raise EngineError("engine_error", "upload failed", 502)
        return int(payload[0]["itemid"])

    # --- typed helpers -------------------------------------------------
    async def site_info(self, token: str, lang: str | None = None) -> dict:
        return await self.call(token, "core_webservice_get_site_info", lang)

    async def user_courses(self, token: str, userid: int, lang: str | None = None) -> list[dict]:
        return await self.call(token, "core_enrol_get_users_courses", lang, userid=userid, returnusercount=0)

    async def course_contents(self, token: str, courseid: int, lang: str | None = None) -> list[dict]:
        return await self.call(token, "core_course_get_contents", lang, courseid=courseid)

    async def course_module(self, token: str, cmid: int, lang: str | None = None) -> dict:
        return (await self.call(token, "core_course_get_course_module", lang, cmid=cmid))["cm"]

    async def pages(self, token: str, courseid: int, lang: str | None = None) -> list[dict]:
        return (await self.call(token, "mod_page_get_pages_by_courses", lang, courseids=[courseid]))["pages"]

    async def urls(self, token: str, courseid: int, lang: str | None = None) -> list[dict]:
        return (await self.call(token, "mod_url_get_urls_by_courses", lang, courseids=[courseid]))["urls"]

    async def assignments(self, token: str, courseid: int, lang: str | None = None) -> list[dict]:
        data = await self.call(token, "mod_assign_get_assignments", lang, courseids=[courseid])
        courses = data.get("courses") or []
        return courses[0]["assignments"] if courses else []

    async def view_page(self, token: str, pageid: int) -> None:
        """Record the view so completion and logs work as in Moodle's own UI."""
        await self.call(token, "mod_page_view_page", None, pageid=pageid)


def _json(r: httpx.Response) -> Any:
    try:
        return r.json()
    except ValueError as exc:
        raise EngineError("engine_error", f"non-JSON response ({r.status_code})", 502) from exc
