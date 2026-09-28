"""Build the 大学物理 sample course locally through the gateway's upload-materials flow."""
import json, pathlib, sys, httpx
G = "http://localhost:8090"
ROOT = pathlib.Path("/home/claude/wenquest/samples/大学物理/课程资料")
c = httpx.Client(timeout=300)
tok = c.post(f"{G}/api/v1/auth/login", json={"username": "teacher1", "password": "Test#2026"}).json()["token"]
H = {"Authorization": f"Bearer {tok}"}
iid = c.post(f"{G}/api/v1/imports", headers=H).json()["import_id"]
files = [p for p in sorted(ROOT.rglob("*")) if p.is_file()]
for p in files:
    rel = "大学物理（上）课程资料/" + str(p.relative_to(ROOT))
    r = c.post(f"{G}/api/v1/imports/{iid}/files", headers=H, files={"file": (p.name, p.read_bytes())}, data={"path": rel})
    if r.status_code != 200: print("upload fail", p.name, r.status_code, r.text[:200])
cls = c.post(f"{G}/api/v1/imports/{iid}/classify", headers=H, json={}).json()
unsure = [f["name"] for f in cls["files"] if f["confidence"] not in ("rule", "ai", "teacher")]
print("files", len(cls["files"]), "categories", {f["category"] for f in cls["files"]})
outline = c.post(f"{G}/api/v1/imports/{iid}/outline", headers=H, json={"languages": "zh"}).json()
print("sections", [s["title"] for s in outline["sections"]])
for s in outline["sections"]:
    for l in s["lessons"]:
        body = {"import_id": iid, "sources": l.get("sources", [])[:6], "course_title": outline["title"].get("zh", ""),
                "section_title": s["title"].get("zh", ""), "lesson_title": l["title"].get("zh", ""), "languages": "zh"}
        r = c.post(f"{G}/api/v1/ai/lesson", headers=H, json=body)
        l["content"] = r.json()["content"] if r.status_code == 200 else {"zh": "<p>(内容生成失败)</p>"}
pub = c.post(f"{G}/api/v1/courses", headers=H, json=outline)
print("publish", pub.status_code, pub.text[:300])
