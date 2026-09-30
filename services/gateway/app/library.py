"""问渠零件与机器人库 · 读取与取用 (round 4, docs/方案/数字工厂资源接口约定.md).

The library is built and published by the digital factory. The learning platform only reads it:
`latest.json` → `index.json` → `entry.json` and model files, by id + version. When a course uses an entry, a copy
(entry, model, drawing, licence) goes into the course project, so a later library change never breaks a published
lesson. Until the real library is online, `WQ_LIBRARY_URL` is empty and a built-in sample library (the same layout,
production/library_sample.py) is generated into the data folder.
"""
from __future__ import annotations

import json
import re
import shutil
import time
from pathlib import Path

import httpx

ID = re.compile(r"^[A-Z]-[A-Z0-9]{2,4}(-[A-Z0-9]+)+$")


class LibraryError(Exception):
    pass


class Library:
    def __init__(self, url: str, data_dir: str, http: httpx.AsyncClient | None = None):
        self.url = (url or "").rstrip("/")
        self.data = Path(data_dir)
        self.http = http
        self._index: dict | None = None
        self._at = 0.0

    # --- where it lives --------------------------------------------------------------------------------------------
    @property
    def builtin(self) -> bool:
        return not self.url

    def _sample_root(self) -> Path:
        from .production import library_sample
        root = self.data / "library-sample"
        if not (root / "library" / library_sample.VERSION / "index.json").exists():
            library_sample.build(root)
        return root / "library"

    async def _get(self, rel: str) -> bytes:
        if self.builtin:
            p = (self._sample_root() / rel).resolve()
            if not str(p).startswith(str(self._sample_root().resolve())) or not p.exists():
                raise LibraryError(f"not in the library: {rel}")
            return p.read_bytes()
        try:
            async with httpx.AsyncClient(timeout=60, follow_redirects=True) if self.http is None else _nullctx(self.http) as c:
                r = await c.get(f"{self.url}/library/{rel}")
        except httpx.HTTPError as e:
            raise LibraryError(f"library unreachable: {type(e).__name__}") from e
        if r.status_code != 200:
            raise LibraryError(f"library answered {r.status_code} for {rel}")
        return r.content

    # --- reading ---------------------------------------------------------------------------------------------------
    async def index(self) -> dict:
        """{version, items: [...]} — cached for 10 minutes."""
        if self._index and time.time() - self._at < 600:
            return self._index
        latest = json.loads(await self._get("latest.json"))
        idx = json.loads(await self._get(latest.get("index") or f"{latest['version']}/index.json"))
        idx.setdefault("version", latest["version"])
        self._index, self._at = idx, time.time()
        return idx

    async def entry(self, eid: str, version: str | None = None) -> dict:
        if not ID.match(eid or ""):
            raise LibraryError(f"bad id {eid!r}")
        version = version or (await self.index())["version"]
        return json.loads(await self._get(f"{version}/{eid}/entry.json"))

    async def entries(self) -> dict[str, dict]:
        """One row per entry (the default spec), by id."""
        out: dict[str, dict] = {}
        for row in (await self.index()).get("items") or []:
            out.setdefault(row["id"], row)
        return out

    async def catalog_text(self, words: str = "", limit: int = 40) -> str:
        """A short listing for the AI team: id | name | category | tags | principle; entries matching `words` first."""
        rows = list((await self.entries()).values())
        toks = [t for t in re.split(r"[\s,，、/（）()]+", words.lower()) if len(t) > 1]

        def score(r):
            hay = " ".join([r["id"], r["name"].get("zh", ""), r["name"].get("en", ""), " ".join(r.get("tags") or [])]).lower()
            return -sum(1 for t in toks if t in hay)
        rows.sort(key=score)
        lines = [f"{r['id']} | {r['name'].get('zh', '')} / {r['name'].get('en', '')} | {r.get('category', '')} | "
                 f"{', '.join((r.get('tags') or [])[:6])} | {r.get('principle', '')[:80]}" for r in rows[:limit]]
        return "\n".join(lines)

    # --- taking a copy into a course -----------------------------------------------------------------------------
    async def copy_into(self, folder: Path, eid: str) -> dict:
        """Copy one entry (entry.json, default spec's model and drawing, motion table, licence) into `folder/<id>/`.
        Returns the asset record kept in the project."""
        idx = await self.index()
        version = idx["version"]
        rows = [r for r in idx.get("items") or [] if r["id"] == eid]
        if not rows:
            raise LibraryError(f"{eid} is not in the library")
        entry = await self.entry(eid, version)
        spec = entry.get("default") or rows[0].get("spec") or "default"
        spec = spec if any(r.get("spec") == spec for r in rows) else rows[0].get("spec", "default")
        dest = folder / eid
        tmp = folder / f".{eid}.part"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        (tmp / "entry.json").write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")
        files = ["entry.json"]
        for name in (f"{spec}.glb", f"{spec}.svg", f"{spec}.png", "motion.csv"):
            try:
                (tmp / name).write_bytes(await self._get(f"{version}/{eid}/{name}"))
                files.append(name)
            except LibraryError:
                continue
        src = entry.get("source") or {}
        (tmp / "LICENSE-ATTRIBUTION.txt").write_text(
            f"{entry['name'].get('zh', '')} / {entry['name'].get('en', '')}\n编号 {eid} · 版本 {version}\n"
            f"许可 License: {src.get('license', '')}\n署名 Attribution: {src.get('attribution', '')}\n", encoding="utf-8")
        shutil.rmtree(dest, ignore_errors=True)
        tmp.replace(dest)
        return {"id": eid, "version": version, "spec": spec, "name": entry["name"], "kind": entry.get("kind", ""),
                "category": entry.get("category", ""), "license": src.get("license", ""),
                "attribution": src.get("attribution", ""), "files": files, "added": int(time.time())}


class _nullctx:
    def __init__(self, c):
        self.c = c

    async def __aenter__(self):
        return self.c

    async def __aexit__(self, *a):
        return False
