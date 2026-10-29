"""Demo requests from the China website 问渠科技 (第 48 轮)."""
from tests.test_course_pack import client  # noqa: F401  (the fixture: fake Moodle, temporary data_dir)
from tests.test_materials import login

GOOD = {"org": "某某缝纫机有限公司", "name": "王工", "phone": "138 0013 8000", "email": "Wang@Example.cn", "industry": "缝制机械",
        "products": ["问渠质量 ERP", "缝纫机设计与制造软件", "不存在的产品"], "note": "想看质量体系怎么自查", "consent": True}


def test_submit_validate_and_export(client):  # noqa: F811
    assert client.post("/api/v1/public/demo-request", json=GOOD).json() == {"ok": True}
    for bad, code in (({"consent": False}, "consent_required"), ({"phone": "12345"}, "bad_phone"), ({"org": " "}, "bad_org"),
                      ({"name": ""}, "bad_name"), ({"email": "nope"}, "bad_email")):
        r = client.post("/api/v1/public/demo-request", json={**GOOD, **bad})
        assert r.status_code == 400 and r.json()["error"] == code and r.json()["detail"]
    assert client.post("/api/v1/public/demo-request", json={**GOOD, "phone": "021-12345678", "email": ""}).json() == {"ok": True}
    # a bot fills the honeypot: answered politely, not stored
    assert client.post("/api/v1/public/demo-request", json={**GOOD, "website": "http://spam"}).json() == {"ok": True}
    assert client.get("/api/v1/admin/demo-request", headers=login(client, "s")).status_code == 403
    h = login(client)
    r = client.get("/api/v1/admin/demo-request", headers=h).json()
    assert r["count"] == 2
    row = r["rows"][1]
    assert row["phone"] == "13800138000" and row["email"] == "wang@example.cn" and row["products"] == "问渠质量 ERP、缝纫机设计与制造软件"
    csv = client.get("/api/v1/admin/demo-request?format=csv", headers=h)
    assert csv.headers["content-type"].startswith("text/csv") and "某某缝纫机有限公司" in csv.text
    # round 50: a request for online trial accounts
    assert client.post("/api/v1/public/demo-request", json={**GOOD, "trial": True, "seats": 3,
                                                           "products": ["学习系统", "虚拟实验开发"]}).json() == {"ok": True}
    row = client.get("/api/v1/admin/demo-request", headers=h).json()["rows"][0]
    assert row["trial"] == 1 and row["seats"] == 3 and row["products"] == "学习系统、虚拟实验开发"
    assert client.post("/api/v1/public/demo-request", json={**GOOD, "trial": True, "seats": 9}).status_code == 422


def test_rate_limit(client):  # noqa: F811
    codes = [client.post("/api/v1/public/demo-request", json=GOOD, headers={"X-Forwarded-For": "10.8.8.8"}).status_code for _ in range(8)]
    assert codes[:6] == [200] * 6 and codes[6] == 429


def test_site_info_by_region(client):  # noqa: F811
    assert client.get("/api/v1/public/site").json() == {"region": "us"}
    from app import main
    s = main.state.settings
    old = (s.region, s.company, s.icp)
    try:
        s.region, s.company, s.icp = "cn", "某某问渠科技有限公司", "沪ICP备0000000号-1"
        r = client.get("/api/v1/public/site").json()
        assert r["region"] == "cn" and r["brand"] == "问渠科技" and r["company"] == "某某问渠科技有限公司" and r["icp"].startswith("沪ICP")
        assert r["ai_label"] is True and r["ai_model"] == "DeepSeek"
    finally:
        s.region, s.company, s.icp = old
