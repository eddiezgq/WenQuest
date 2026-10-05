"""Interest registration for the physical sewing-machine kits (第 20 轮 5.2)."""
from tests.test_course_pack import client  # noqa: F401  (the fixture: fake Moodle, temporary data_dir)
from tests.test_materials import login

GOOD = {"kits": ["A", "A+"], "machines": ["lockstitch"], "band": "2", "currency": "usd", "who": "school", "country": "United States",
        "qty": 12, "email": "Teacher@School.edu", "note": "for a lab", "lang": "en", "consent": True}


def test_register_validate_and_export(client):  # noqa: F811
    assert client.post("/api/v1/public/kit-interest", json=GOOD).json() == {"ok": True}
    assert client.post("/api/v1/public/kit-interest", json={**GOOD, "consent": False}).status_code == 400
    assert client.post("/api/v1/public/kit-interest", json={**GOOD, "email": "nope"}).status_code == 400
    assert client.post("/api/v1/public/kit-interest", json={**GOOD, "kits": ["Z"]}).status_code == 400
    assert client.post("/api/v1/public/kit-interest", json={**GOOD, "who": "x"}).status_code == 400
    # a bot fills the honeypot: answered politely, not stored
    assert client.post("/api/v1/public/kit-interest", json={**GOOD, "website": "http://spam"}).json() == {"ok": True}
    assert client.get("/api/v1/admin/kit-interest", headers=login(client, "s")).status_code == 403
    h = login(client)
    r = client.get("/api/v1/admin/kit-interest", headers=h).json()
    assert r["count"] == 1 and r["kits"] == {"A": 1, "A+": 1} and r["units"] == {"A": 12, "A+": 12}
    assert r["rows"][0]["email"] == "teacher@school.edu" and r["rows"][0]["currency"] == "USD"
    csv = client.get("/api/v1/admin/kit-interest?format=csv", headers=h)
    assert csv.headers["content-type"].startswith("text/csv") and "teacher@school.edu" in csv.text


def test_rate_limit(client):  # noqa: F811
    codes = [client.post("/api/v1/public/kit-interest", json=GOOD, headers={"X-Forwarded-For": "10.9.9.9"}).status_code for _ in range(10)]
    assert codes[:8] == [200] * 8 and codes[8] == 429
