"""问渠数字工厂 · 课程接口的客户端 (docs/方案/数字工厂资源接口约定.md §3).

The gateway reads the factory's teaching case (lab7, a gear-reducer workshop) with a read-only key: workshop layout,
products (BOM, routings, quality plans), production data (AGV moves, machine events, measurements, KPIs) and embed
tokens for the live / replay 3D workshop. Nothing personal comes back; every answer has `as_of` (UTC), which the
course shows as "数据来自问渠数字工厂，截至 …". Empty URL or key = no factory (lessons are made without it).
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone

import httpx


class FactoryError(Exception):
    pass


class Factory:
    def __init__(self, url: str, key: str, http: httpx.AsyncClient | None = None):
        self.url = (url or "").rstrip("/")
        self.key = key or ""
        self.http = http
        self._cache: dict[str, tuple[float, dict]] = {}

    @property
    def available(self) -> bool:
        return bool(self.url and self.key)

    async def get(self, path: str, params: dict | None = None, cache: float = 600) -> dict:
        params = params or {}
        if not self.available:
            raise FactoryError("the digital factory is not connected")
        k = path + "?" + json.dumps(params, sort_keys=True)
        hit = self._cache.get(k)
        if hit and time.time() - hit[0] < cache:
            return hit[1]
        try:
            if self.http is not None:
                r = await self.http.get(self.url + path, params=params, headers={"Authorization": f"Bearer {self.key}"})
            else:
                async with httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
                    r = await c.get(self.url + path, params=params, headers={"Authorization": f"Bearer {self.key}"})
        except httpx.HTTPError as e:
            raise FactoryError(f"digital factory unreachable: {type(e).__name__}") from e
        if r.status_code != 200:
            raise FactoryError(f"digital factory answered {r.status_code} for {path}")
        d = r.json()
        self._cache[k] = (time.time(), d)
        return d

    # --- the course interface ----------------------------------------------------------------------------------------
    async def cases(self) -> list[dict]:
        return (await self.get("/api/course/cases")).get("items") or []

    async def layout(self) -> dict:
        return await self.get("/api/course/layout")

    async def products(self) -> list[dict]:
        return (await self.get("/api/course/products")).get("items") or []

    async def product(self, code: str) -> dict:
        return await self.get(f"/api/course/products/{code}")

    async def data(self, kind: str, case: str = "lab7", frm: str = "", to: str = "") -> dict:
        params = {"case": case, "kind": kind}
        if frm:
            params["from"] = frm
        if to:
            params["to"] = to
        return await self.get("/api/course/data", params)

    async def embed_token(self, ttl: int = 1800) -> dict:
        return await self.get("/api/course/embed-token", {"ttl": str(ttl)}, cache=60)

    async def busy_window(self, hours: float = 1.0, case: str = "lab7") -> tuple[str, str, list[dict]]:
        """The latest stretch of `hours` with AGV traffic in the last 7 days: (from, to, agv rows)."""
        rows = (await self.data("agv", case)).get("rows") or []
        if not rows:
            return "", "", []
        end = max(_t(r["ts"]) for r in rows)
        start = end - timedelta(hours=hours)
        sel = [r for r in rows if _t(r["ts"]) >= start]
        return _iso(start), _iso(end), sel

    # --- for the AI team ---------------------------------------------------------------------------------------------
    async def summary(self) -> dict:
        """Facts about the teaching case, short enough for a prompt; plus as_of for the sources line."""
        cases, layout, products = await self.cases(), await self.layout(), await self.products()
        case = cases[0] if cases else {}
        lines = []
        if case:
            lines.append(f"Case {case['id']}: {case['name'].get('zh', '')} / {case['name'].get('en', '')} — {case.get('summary', '')}")
        for p in products[:3]:
            lines.append(f"Product {p['code']}: {p['name'].get('zh', '')} / {p['name'].get('en', '')}; {p.get('summary', '')}; "
                         f"specs {json.dumps(p.get('specs') or {}, ensure_ascii=False)[:300]}")
        units = layout.get("units") or []
        lines.append("Workshop units (x, y in metres): " + "; ".join(
            f"{u['unit']} {u['name'].get('zh', '')}/{u['name'].get('en', '')} ({u['x_m']}, {u['y_m']})" for u in units))
        if layout.get("agv_home"):
            lines.append("AGVs: " + ", ".join(layout["agv_home"]))
        lines.append("The workshop has no robot arms; AGVs carry parts between units.")
        return {"text": "\n".join(lines), "as_of": layout.get("as_of", ""), "case": case.get("id", "lab7"),
                "case_name": case.get("name") or {"zh": "数字工厂", "en": "Digital factory"},
                "products": [p["code"] for p in products]}


def source_record(summary: dict) -> dict:
    """The line in a lesson's sources for factory data."""
    asof = (summary.get("as_of") or "").replace("T", " ").replace("Z", " UTC")
    name = summary.get("case_name") or {}
    return {"id": f"factory:{summary.get('case', 'lab7')}", "version": f"截至 {asof}".strip(),
            "name": {"zh": f"问渠数字工厂 · {name.get('zh', '')}", "en": f"WenQuest Digital Factory · {name.get('en', '')}"},
            "license": "教学数据 Teaching data", "attribution": "数据来自问渠数字工厂（factory.wenquestrobotics.com），不含个人信息"}


def _t(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _iso(d: datetime) -> str:
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
