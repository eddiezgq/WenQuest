"""第 175 轮：软件测试版授权码——登录才能领；领到的码软件端（tools/wqlicense/wq_license.py，纯 Python）验得过；
再领一次给同一个码（不往后延）；过期的、改过的、别的密钥签的都验不过；公钥接口给的就是验码用的那把。"""
import sys
import time
from pathlib import Path

from app import license as L
from tests.test_course_pack import client  # noqa: F401
from tests.test_materials import login
from tests.test_sewing_api import sc  # noqa: F401

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "wqlicense"))
import wq_license as C


def test_needs_login_and_token_verifies_on_client(sc):  # noqa: F811
    c = sc
    assert c.post("/api/v1/license/beta").status_code in (401, 422)        # 没登录：领不到
    h = login(c, "s")
    a = c.post("/api/v1/license/beta", headers=h).json()
    assert a["new"] and a["token"].startswith("WQ1.") and abs(a["exp"] - time.time() - 365 * 86400) < 120
    b = c.post("/api/v1/license/beta", headers=h).json()
    assert not b["new"] and b["token"] == a["token"]                       # 再领：同一个码
    assert c.get("/api/v1/license/me", headers=h).json()["token"] == a["token"]
    pk = c.get("/api/v1/license/public-key").json()
    st = C.check(a["token"], {pk["region"]: pk["key"]})
    assert st["ok"] and st["days_left"] in (364, 365)


def test_client_rejects_expired_tampered_and_foreign():
    keys = {"us": L.public_key_b64("k-us"), "cn": L.public_key_b64("k-cn")}
    assert C.check(L.issue("k-cn", 3, "cn"), keys)["ok"]                   # 国内发的码，美国版软件也认
    assert C.check(L.issue("k-other", 3, "us"), keys)["reason"] == "signature"
    old = L.issue("k-us", 3, "us", now=time.time() - 366 * 86400)
    assert C.check(old, keys)["reason"] == "expired"
    tok = L.issue("k-us", 3, "us")
    head, body, sig = tok.split(".")
    forged = L.b64u(L.unb64u(body).replace(b'"u":3', b'"u":4'))
    assert C.check(f"{head}.{forged}.{sig}", keys)["reason"] == "signature"
    assert C.check("hello", keys)["reason"] == "format"
