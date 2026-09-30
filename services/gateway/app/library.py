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
        rel = re.sub(r"^/?library/", "", latest.get("index") or f"{latest['version']}/index.json")
        idx = json.loads(await self._get(rel))
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
            if row["id"] not in out or (row.get("default") and not out[row["id"]].get("default")):
                out[row["id"]] = row
        return out

    async def catalog_text(self, words: str = "", limit: int = 40) -> str:
        """A short listing for the AI team: id | name | category | tags | principle; entries matching `words` first."""
        rows = list((await self.entries()).values())
        toks = [t for t in re.split(r"[\s,，、/（）()]+", words.lower()) if len(t) > 1]

        def score(r):
            hay = " ".join([r["id"], r["name"].get("zh", ""), r["name"].get("en", ""), " ".join(r.get("tags") or [])]).lower()
            return -sum(1 for t in toks if t in hay)
        rows.sort(key=lambda r: (score(r), 0 if r.get("kind") == "robot" or r["id"].startswith("B-") else 1, r["id"]))
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
        entry = normalize_entry(await self.entry(eid, version))
        row = next((r for r in rows if r.get("default")), rows[0])
        spec = row.get("size") or row.get("spec") or entry.get("default") or "default"
        dest = folder / eid
        tmp = folder / f".{eid}.part"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        (tmp / "entry.json").write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")
        files = ["entry.json"]
        wanted = {f"{spec}.glb", f"{spec}.svg", f"{spec}.png", "motion.csv"}
        for name in [Path(v).name for v in (row.get("files") or {}).values()] + sorted(wanted):
            if name in files or not (name in wanted or name.startswith(spec + ".")):
                continue
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


SPIN = re.compile(r"wheel|rotor|prop|caster|spin", re.I)


def normalize_entry(entry: dict) -> dict:
    """Entries of the published library (robot.links / robot.joints with limit{lower, upper}) get the fields the course
    tools use: links, root, joints (lower/upper), tool (end of the longest chain, arms only), rest and demo ranges.
    Entries that already have them (the built-in sample) are left as they are."""
    e = dict(entry)
    if isinstance(e.get("default"), dict):
        e.pop("default")
    rob = e.get("robot") or {}
    if e.get("joints") or not rob.get("joints"):
        return e
    joints = []
    for j in rob["joints"]:
        if j.get("type") not in ("revolute", "continuous", "prismatic") or not j.get("child"):
            continue
        lim = j.get("limit") or {}
        lo, hi = lim.get("lower"), lim.get("upper")
        if j["type"] == "continuous" or lo is None or hi is None:
            lo, hi = (-3.14159, 3.14159) if j["type"] != "prismatic" else (-0.1, 0.1)
        joints.append({"name": j["name"], "type": j["type"], "parent": j.get("parent"), "child": j["child"],
                       "axis": j.get("axis") or [0, 0, 1], "lower": float(lo), "upper": float(hi), "origin": j.get("origin")})
    links = [x["node"] if isinstance(x, dict) else x for x in rob.get("links") or []]
    links = [x.get("name") if isinstance(x, dict) else x for x in links]
    children = {j["child"] for j in joints}
    root = next((x for x in links if x not in children), links[0] if links else "")
    e["links"], e["root"], e["joints"] = links, root, joints
    if rob.get("type") == "arm" and joints:
        kids: dict[str, list[str]] = {}
        for j in joints:
            kids.setdefault(j["parent"], []).append(j["child"])

        node, seen = root, set()
        while len(kids.get(node, [])) == 1 and node not in seen:   # down the arm; stop where a gripper branches
            seen.add(node)
            node = kids[node][0]
        e["tool"] = {"link": node, "xyz": [0, 0, 0]}
    rest, demo = {}, {}
    given = rob.get("rest") or rob.get("home") or {}          # the model's own standing pose, when the library gives one
    posed = {k: float(v) for k, v in given.items() if isinstance(v, (int, float))} or (_arm_rest(e) if e.get("tool") else {})
    for j in joints:
        lo, hi = j["lower"], j["upper"]
        mid = posed.get(j["name"], min(max(0.0, lo), hi))
        rest[j["name"]] = mid
        if j["type"] == "continuous" and SPIN.search(j["name"] + " " + j["child"]):
            demo[j["name"]] = [0.0, 12.566]
        else:
            amp = min(0.9 if j["type"] != "prismatic" else 0.05, (hi - lo) / 4)
            demo[j["name"]] = [max(lo, mid - amp), min(hi, mid + amp)]
    e.setdefault("rest", rest)
    e.setdefault("demo", demo)
    return e


def _tf(xyz, rpy):
    import numpy as np
    r, p, y = rpy
    cx, sx, cy, sy, cz, sz = np.cos(r), np.sin(r), np.cos(p), np.sin(p), np.cos(y), np.sin(y)
    m = np.eye(4)
    m[:3, :3] = [[cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx],
                 [sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx],
                 [-sy, cy * sx, cy * cx]]
    m[:3, 3] = xyz
    return m


def _rot(axis, q):
    import numpy as np
    a = np.asarray(axis, float) / (np.linalg.norm(axis) or 1)
    k = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    m = np.eye(4)
    m[:3, :3] = np.eye(3) + np.sin(q) * k + (1 - np.cos(q)) * k @ k
    return m


def _arm_rest(e: dict) -> dict:
    """A natural-looking rest pose for an arm: shoulder and elbow bent so the tool stands up and forward (every joint
    at zero often leaves an arm lying flat). Forward kinematics from the entry's joint origins and axes."""
    import itertools
    import numpy as np
    chain, node = [], e["tool"]["link"]
    by_child = {j["child"]: j for j in e["joints"]}
    while node in by_child:
        chain.insert(0, by_child[node])
        node = by_child[node]["parent"]
    rev = [j for j in chain if j["type"] == "revolute"]
    if len(rev) < 3 or any(not (j.get("origin") or {}).get("xyz") for j in chain):
        return {}

    def tool(vals):
        m = np.eye(4)
        for j in chain:
            o = j.get("origin") or {}
            m = m @ _tf(o.get("xyz", [0, 0, 0]), o.get("rpy", [0, 0, 0])) @ _rot(j["axis"], vals.get(j["name"], 0.0))
        return m[:3, 3]
    length = sum(float(np.linalg.norm((j.get("origin") or {}).get("xyz", [0, 0, 0]))) for j in chain) or 1.0
    grid = [x * 0.3 for x in range(-6, 7)]
    best, pose = -1e9, {}
    for a, b in itertools.combinations(rev[1:4], 2):     # shoulder and elbow (7-axis arms have a roll joint between)
        for qa, qb in itertools.product(grid, grid):
            if not (a["lower"] <= qa <= a["upper"] and b["lower"] <= qb <= b["upper"]):
                continue
            p = tool({a["name"]: qa, b["name"]: qb})
            reach = float(np.hypot(p[0], p[1]))
            score = p[2] + 0.6 * min(reach, 0.45 * length) - 0.02 * (abs(qa) + abs(qb))
            if p[2] > 0.25 * length and reach > 0.2 * length and score > best:
                best, pose = score, {a["name"]: qa, b["name"]: qb}
    return pose


class _nullctx:
    def __init__(self, c):
        self.c = c

    async def __aenter__(self):
        return self.c

    async def __aexit__(self, *a):
        return False
