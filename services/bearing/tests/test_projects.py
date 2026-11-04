"""Cloud projects through the bearing service (round 64, step 7b): sign-in is passed on to the gateway, contents pass
through as they are, conflicts come back with who and when, other errors become Chinese and English words. The gateway
is replaced by a stand-in (no network)."""

import json

import httpx
import pytest
from fastapi.testclient import TestClient

import app as A
import projects_api as P


class Gateway:
    """A stand-in for /api/v1/bearing/projects and /api/v1/industry/me."""

    def __init__(self):
        self.calls, self.store, self.version = [], {}, 0

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.calls.append((request.method, request.url.path, dict(request.url.params), request.headers.get("cookie")))
        if not request.headers.get("cookie") and not request.headers.get("authorization"):
            return httpx.Response(401, json={})
        if "nolicense" in (request.headers.get("cookie") or ""):
            return httpx.Response(403, json={})
        path = request.url.path
        if path == "/api/v1/industry/me":
            return httpx.Response(
                200, json={"login": True, "licensed": True, "org": "甲轴承厂", "user_id": 7, "name": "张工"}
            )
        if request.method == "POST" and path.endswith("/projects"):
            body = json.loads(request.content)
            self.version = 1
            self.store = body
            return httpx.Response(200, json={"id": 1, "version": 1, "kind": body["kind"], "name": body["name"]})
        if request.method == "PUT":
            body = json.loads(request.content)
            if body["base"] != self.version:
                return httpx.Response(409, json={"error": "conflict", "version": self.version, "updated_name": "李工"})
            self.version += 1
            self.store["body"] = body["body"]
            return httpx.Response(200, json={"id": 1, "version": self.version})
        if request.method == "GET" and path.endswith("/projects/1"):
            return httpx.Response(200, json={"id": 1, "version": self.version, "body": self.store.get("body")})
        if request.method == "GET" and path.endswith("/projects"):
            return httpx.Response(200, json={"projects": [], "kind": dict(request.url.params).get("kind")})
        if path.endswith("/projects/9"):
            return httpx.Response(404, json={})
        return httpx.Response(500, json={})


@pytest.fixture
def gw(monkeypatch):
    g = Gateway()
    monkeypatch.setattr(P, "_CLIENT", [httpx.Client(transport=httpx.MockTransport(g))])
    return g


def test_projects_round_trip_conflict_and_words(gw):
    c = TestClient(A.app)
    assert c.get("/api/me").json() == {"login": False, "licensed": False, "org": "", "name": "", "reachable": True}
    c.cookies.set("wq_sso", "tok")
    assert c.get("/api/me").json()["org"] == "甲轴承厂"
    design = json.loads((A.EXAMPLES / "demo-deep-groove.json").read_text(encoding="utf-8"))
    r = c.post("/api/projects", json={"name": "6206", "kind": "design", "body": design})
    assert r.status_code == 200 and r.json()["kind"] == "design" and gw.store["body"] == design  # passed through
    assert gw.calls[-1][3] == "wq_sso=tok"  # the sign-in went on to the gateway
    assert c.get("/api/projects?kind=process").json()["kind"] == "process"
    assert c.get("/api/projects?kind=cam").status_code == 400
    assert c.put("/api/projects/1", json={"body": {"a": 1}, "base": 1}).json()["version"] == 2
    r = c.put("/api/projects/1", json={"body": {"a": 2}, "base": 1})
    assert r.status_code == 409 and r.json()["updated_name"] == "李工"
    assert c.get("/api/projects/1").json()["body"] == {"a": 1}
    r = c.get("/api/projects/9")
    assert r.status_code == 404 and "20" in r.json()["detail"]["zh"]
    c.cookies.set("wq_sso", "nolicense")
    r = c.get("/api/projects")
    assert r.status_code == 403 and r.json()["detail"]["zh"] == "云端项目给已开通的企业账号用，请联系问渠开通"
    c.cookies.clear()
    assert c.get("/api/projects").json()["detail"]["zh"].startswith("请先登录")


def test_gateway_down(monkeypatch):
    def boom(request):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(P, "_CLIENT", [httpx.Client(transport=httpx.MockTransport(boom))])
    c = TestClient(A.app)
    c.cookies.set("wq_sso", "tok")
    r = c.get("/api/projects")
    assert r.status_code == 503 and r.json()["detail"]["zh"] == "暂时连不上云端，请稍后再试"
    assert c.get("/api/me").json()["reachable"] is False
