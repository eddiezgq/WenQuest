# -*- coding: utf-8 -*-
"""第 7 轮：ERPNext 单点登录——授权码一次性、回调地址与密钥校验、老师/学生身份与角色、没登录先去学习平台。"""
import importlib
import urllib.parse

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

ERP = "https://erp.example.com"
CB = ERP + "/api/method/frappe.integrations.oauth2_logins.custom/wenquest"


class _Resp:
    def __init__(self, code, body):
        self.status_code, self._b = code, body

    def json(self):
        return self._b


def _hub(monkeypatch, auth):
    for k, v in {"WQ_HUB_NO_START": "1", "WQ_SECRET": "s", "WQ_AUTH": auth, "WQ_ERPNEXT_URL": ERP,
                 "WQ_ERPNEXT_API": "http://erp-frontend:8080", "WQ_ERP_API_KEY": "k", "WQ_ERP_API_SECRET": "x",
                 "WQ_ERP_OAUTH_SECRET": "oauth-secret", "WQ_SSO_URL": "https://learn.example.com/api/v1/auth/sso",
                 "WQ_LOGIN_URL": "https://learn.example.com/pages/login/login"}.items():
        monkeypatch.setenv(k, v)
    import hub.app as app_mod
    app_mod = importlib.reload(app_mod)
    made = []
    monkeypatch.setattr(app_mod.erp_sso, "provision", lambda ident, session=None: made.append(ident))
    return app_mod, made


def _authorize(c, **extra):
    q = {"client_id": "wenquest-erp", "redirect_uri": CB, "state": "st1", "response_type": "code", **extra}
    return c.get("/api/oauth/authorize", params=q, follow_redirects=False)


def _code(r):
    loc = urllib.parse.urlsplit(r.headers["location"])
    assert loc.scheme + "://" + loc.netloc + loc.path == CB
    q = dict(urllib.parse.parse_qsl(loc.query))
    assert q["state"] == "st1"
    return q["code"]


def test_full_flow_local(monkeypatch):
    app_mod, made = _hub(monkeypatch, "local")
    c = TestClient(app_mod.app)
    tok = app_mod._sign({"name": "李老师", "role": "manager", "mode": "teach", "teacher": True})
    r = _authorize(c, wq_token=tok)
    assert r.status_code == 302
    code = _code(r)
    assert made[0]["email"].endswith("@users.example.com") and "Manufacturing Manager" in made[0]["roles"]
    form = {"grant_type": "authorization_code", "code": code, "redirect_uri": CB, "client_id": "wenquest-erp",
            "client_secret": "oauth-secret"}
    t = c.post("/api/oauth/token", data=form).json()["access_token"]
    info = c.get("/api/oauth/userinfo", headers={"Authorization": "Bearer " + t}).json()
    assert info["email"] == made[0]["email"] and info["given_name"] == "李老师" and info["email_verified"]
    assert c.post("/api/oauth/token", data=form).status_code == 400                     # 授权码只能用一次
    assert c.get("/api/oauth/userinfo", headers={"Authorization": "Bearer x.y"}).status_code == 401


def test_rejects_bad_requests(monkeypatch):
    app_mod, made = _hub(monkeypatch, "local")
    c = TestClient(app_mod.app)
    tok = app_mod._sign({"name": "a", "role": "manager", "mode": "teach", "teacher": True})
    assert _authorize(c, wq_token=tok, redirect_uri="https://evil.example.com/cb").status_code == 400
    assert _authorize(c, wq_token=tok, client_id="other").status_code == 400
    assert _authorize(c).status_code == 401                                              # 本地版没带凭证
    code = _code(_authorize(c, wq_token=tok))
    bad = {"grant_type": "authorization_code", "code": code, "redirect_uri": CB, "client_id": "wenquest-erp",
           "client_secret": "wrong"}
    assert c.post("/api/oauth/token", data=bad).status_code == 401
    other_cb = dict(bad, client_secret="oauth-secret", redirect_uri=ERP + "/x")
    assert c.post("/api/oauth/token", data=other_cb).status_code == 400                 # 回调地址必须和授权时一致


def test_code_expires():
    from hub import erp_sso
    codes = erp_sso.Codes()
    c = codes.issue({"email": "a"}, CB, now=1000)
    assert codes.take(c, CB, now=1000 + erp_sso.CODE_TTL + 1) is None
    key = b"k"
    assert erp_sso.read_token(erp_sso.sign_token({"a": 1}, key, now=0), key, now=erp_sso.TOKEN_TTL + 1) is None


def test_wenquest_student_and_login_redirect(monkeypatch):
    app_mod, made = _hub(monkeypatch, "wenquest")
    import httpx

    def fake_get(url, cookies=None, timeout=None):
        if (cookies or {}).get("wq_sso") == "stu":
            return _Resp(200, {"user": {"id": 101, "fullname": "王小明", "username": "xm", "can_create_courses": False}})
        return _Resp(401, {})
    monkeypatch.setattr(httpx, "get", fake_get)
    c = TestClient(app_mod.app)
    r = _authorize(c)                                                                    # 没登录学习平台
    assert r.status_code == 302 and r.headers["location"].startswith("https://learn.example.com/pages/login/login?back=")
    assert "oauth%2Fauthorize" in r.headers["location"] and made == []
    c.cookies.set("wq_sso", "stu")
    _code(_authorize(c))
    assert made[0]["email"] == "wq101@users.example.com" and made[0]["roles"] == [app_mod.erp_sso.STUDENT_ROLE]
