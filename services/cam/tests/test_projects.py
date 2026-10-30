"""Cloud projects (round 39, step 7): the cam service passes the sign-in on to the gateway and the project through
unchanged; the gateway's refusals become words the page shows, and a save conflict keeps who saved and when."""

import json

import httpx
from fastapi.testclient import TestClient

import cae_bridge as B
from app import app


def standin():
    seen = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append((req.method, req.url.path, req.url.query.decode(), json.loads(req.content or b"null"),
                     req.headers.get("cookie")))
        cookie = req.headers.get("cookie") or ""
        if req.url.path == "/api/v1/industry/me":
            if "wq_sso=a" in cookie:
                return httpx.Response(200, json={"login": True, "licensed": True, "org": "甲厂", "user_id": 5,
                                                 "name": "王工"})
            return httpx.Response(200, json={"login": True, "licensed": False, "org": "", "user_id": 6, "name": "李"})
        if "wq_sso=a" not in cookie:
            return httpx.Response(403, json={"error": "not_licensed"})
        if req.method == "PUT":
            return httpx.Response(409, json={"error": "conflict", "version": 3, "updated": 1761800000,
                                             "updated_name": "张工", "updated_by": 7})
        if req.url.path.endswith("/99"):
            return httpx.Response(404, json={"error": "not_found"})
        return httpx.Response(200, json={"org": "甲厂", "me": "王工", "projects": []})
    return httpx.Client(transport=httpx.MockTransport(handler)), seen


def test_cloud_projects_go_through_the_gateway(monkeypatch):
    cl, seen = standin()
    monkeypatch.setattr(B, "CLIENT", cl)
    c = TestClient(app)
    # not signed in: refused here, nothing sent
    r = c.get("/api/projects")
    assert r.status_code == 401 and "登录" in r.json()["detail"]["zh"] and not seen
    assert c.get("/api/me").json() == {"login": False, "licensed": False, "org": "", "name": "", "reachable": True}

    c.cookies.set("wq_sso", "b")                  # signed in, company not activated
    assert c.get("/api/me").json()["licensed"] is False
    r = c.get("/api/projects")
    assert r.status_code == 403 and "开通" in r.json()["detail"]["zh"]

    c.cookies.set("wq_sso", "a")
    assert c.get("/api/me").json() == {"login": True, "licensed": True, "org": "甲厂", "name": "王工",
                                       "reachable": True}
    body = {"name": "送料凸轮", "kind": "cam", "body": {"title": {"zh": "送料"}, "program": {"segments": []}}}
    assert c.post("/api/projects", json=body).json()["org"] == "甲厂"
    assert seen[-1][:2] == ("POST", "/api/v1/cam/projects") and seen[-1][3] == body   # content passed unchanged
    assert "wq_sso=a" in seen[-1][4]
    c.get("/api/projects/4?version=2")
    assert seen[-1][1:3] == ("/api/v1/cam/projects/4", "version=2")

    r = c.put("/api/projects/4", json={"body": {}, "base": 2})
    assert r.status_code == 409 and r.json()["updated_name"] == "张工" and r.json()["version"] == 3
    r = c.get("/api/projects/99")
    assert r.status_code == 404 and "20 版" in r.json()["detail"]["zh"]
    c.post("/api/projects/4/restore", json={"version": 1, "base": 3})
    c.delete("/api/projects/4")
    assert [s[:2] for s in seen[-2:]] == [("POST", "/api/v1/cam/projects/4/restore"),
                                          ("DELETE", "/api/v1/cam/projects/4")]


def test_gateway_down_is_said_plainly(monkeypatch):
    def down(req):
        raise httpx.ConnectError("no")
    monkeypatch.setattr(B, "CLIENT", httpx.Client(transport=httpx.MockTransport(down)))
    c = TestClient(app)
    c.cookies.set("wq_sso", "a")
    r = c.get("/api/projects")
    assert r.status_code == 503 and "云端" in r.json()["detail"]["zh"]
    assert c.get("/api/me").json()["reachable"] is False
