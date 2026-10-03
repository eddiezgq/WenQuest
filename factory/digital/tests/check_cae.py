# -*- coding: utf-8 -*-
"""服务器演练（第 11 轮）：经枢纽在真镜像里走一遍有限元——读入 SH-301 → 示范题工况 → 排队计算 → 取结果。
用法：python tests/check_cae.py --hub http://localhost:8100"""
import argparse
import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--hub", default="http://localhost:8100")
ap.add_argument("--erp", default="", help="给了就核对 ERPNext 物料上附了数控程序（第 13 轮）")
ap.add_argument("--erp-key", default="")
ap.add_argument("--erp-secret", default="")
A = ap.parse_args()


def call(method, path, body=None, token=None, raw=False):
    req = urllib.request.Request(A.hub + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json", **({"x-wq-token": token} if token else {})})
    with urllib.request.urlopen(req, timeout=180) as r:
        b = r.read()
        return b if raw else json.loads(b.decode())


h = call("GET", "/api/cae/health")
assert h["ok"], h
tok = call("POST", "/api/login", {"name": "仿真检查", "role": "engineer", "mode": "teach"})["token"]
mats = call("GET", "/api/cae/materials", token=tok)["materials"]
assert len(mats) == 12 and all(m["sources"] for m in mats)
assert "SH-301" in [i["item"] for i in call("GET", "/api/cae/parts", token=tok)["items"]]
g = call("POST", "/api/cae/geometry/item/SH-301", token=tok)
assert call("GET", g["model_url"], raw=True)[:4] == b"glTF"
F = g["faces"]
ax = {"origin": [0, 0, 0], "dir": [0, 0, 1]}
brg = sorted([f["id"] for f in F if f.get("radius_mm") == 17.5])
out = max((f for f in F if f.get("radius_mm") == 15.0), key=lambda f: f["center"][2])["id"]
wall = next(f["id"] for f in F if f["kind"] == "plane" and f.get("normal") and abs(abs(f["normal"][0]) - 1) < 1e-3)
setup = {"material_id": "45-QT", "mesh": {"size_mm": 5}, "loads": [
    {"type": "cyl_support", "faces": [brg[0]], "axis": ax, "dofs": ["radial", "axial"]},
    {"type": "cyl_support", "faces": [brg[1]], "axis": ax, "dofs": ["radial"]},
    {"type": "cyl_support", "faces": [out], "axis": ax, "dofs": ["tangential"]},
    {"type": "torque", "faces": [wall], "value_nmm": 350e3, "axis": ax}]}
j = call("POST", "/api/cae/jobs", {"step_sha": g["sha"], "setup": setup, "item": "SH-301", "title": "演练"}, token=tok)
t0 = time.time()
while j["status"] not in ("done", "failed") and time.time() - t0 < 400:
    time.sleep(2)
    j = call("GET", "/api/cae/jobs/" + j["id"], token=tok)
print(json.dumps(j.get("stats") or j.get("error"), ensure_ascii=False))
assert j["status"] == "done", j.get("error")
st = j["stats"]
assert abs(st["vm_max_at"][1] - 15) < 0.5 and 52 < st["vm_max_at"][2] < 112, "最大应力不在键槽根部"
assert 0.3 < st["safety_factor"] < 5
assert call("GET", "/api/cae/jobs/{}/surface.bin".format(j["id"]), token=tok, raw=True)[:4] == b"WQS1"
assert j["id"] in [x["id"] for x in call("GET", "/api/cae/jobs", token=tok)["jobs"]]
# 本地登录方式下人人都按老师算，“只能看自己的任务”在线上（问渠账号）才生效
print("有限元演练通过：{} 个单元，{} 秒，最大应力 {} MPa，安全系数 {}".format(
    st["elements"], st["seconds"], st["vm_max_mpa"], st["safety_factor"]))

# 第 12 轮：运动与动力分析——UR5e 保持一个姿态，驱动力矩等于重力矩
info = call("POST", "/api/mbd/models/load", {"source": "library", "id": "B-ARM-UR5E"}, token=tok)
assert call("GET", info["model_url"], raw=True)[:4] == b"glTF" and len(info["joints"]) == 6
pose = {"shoulder_lift_joint": -1.2, "elbow_joint": 1.0}
j = call("POST", "/api/mbd/jobs", {"model": {"source": "library", "id": "B-ARM-UR5E"}, "title": "演练",
                                   "setup": {"duration_s": 0.5, "initial": pose,
                                             "drives": [{"joint": x["name"], "kind": "hold"} for x in info["joints"]]}}, token=tok)
t0 = time.time()
while j["status"] not in ("done", "failed") and time.time() - t0 < 300:
    time.sleep(2)
    j = call("GET", "/api/mbd/jobs/" + j["id"], token=tok)
assert j["status"] == "done", j.get("error")
peak = {d["joint"]: d["peak"] for d in j["stats"]["drives"]}
assert 20 < peak["shoulder_lift_joint"] < 100, peak
assert call("GET", "/api/mbd/jobs/{}/series.bin".format(j["id"]), token=tok, raw=True)[:4] == b"WQC1"
print("动力学演练通过：肩部重力矩 {:.1f} N·m，用时 {} 秒".format(peak["shoulder_lift_joint"], j["stats"]["seconds"]))

# 第 14 轮：温度场——WQR-105 简化箱体热平衡，与教材公式比
g = call("POST", "/api/cae/geometry/example/housing", {"params": {}}, token=tok)
ex = g["example"]
j = call("POST", "/api/cae/jobs", {"step_sha": g["sha"], "item": None, "title": "演练 箱体热平衡", "setup": {
    "analysis": "thermal", "material_id": ex["material_id"], "mesh": {"size_mm": ex["mesh_mm"]}, "thermal": ex["thermal"],
    "formula": ex["formula"]}}, token=tok)
t0 = time.time()
while j["status"] not in ("done", "failed") and time.time() - t0 < 400:
    time.sleep(2)
    j = call("GET", "/api/cae/jobs/" + j["id"], token=tok)
assert j["status"] == "done", j.get("error")
assert abs(j["stats"]["film_groups"][0]["mean_c"] - ex["formula"]["t_oil_c"]) < 0.5, j["stats"]
assert call("POST", "/api/cae/jobs/{}/report".format(j["id"]), {"images": []}, token=tok, raw=True)[:2] == b"PK"
print("温度场演练通过：箱体外表面平均 {:.1f} ℃，公式 {} ℃".format(j["stats"]["film_groups"][0]["mean_c"], ex["formula"]["t_oil_c"]))

# 第 14 轮：拓扑优化——MBB 梁（经典算例，柔度约 203），拉伸成板件交给有限元
j = call("POST", "/api/opt/topo", {"spec": {"preset": "mbb"}}, token=tok)
t0 = time.time()
while j["status"] not in ("done", "failed") and time.time() - t0 < 200:
    time.sleep(1)
    j = call("GET", "/api/opt/jobs/" + j["id"], token=tok)
assert j["status"] == "done", j.get("error")
assert abs(j["stats"]["compliance"] - 203) < 5, j["stats"]
f = call("POST", "/api/opt/topo/{}/to-fea".format(j["id"]), {}, token=tok)
assert f["geometry"]["solid"]["solids"] == 1 and len(f["rows"]) == 3, f["rows"]
print("拓扑优化演练通过：MBB 梁柔度 {}，{} 次迭代".format(j["stats"]["compliance"], j["stats"]["iterations"]))

# 第 13 轮：数控编程——SH-301 粗车工序（工艺规程 20）→ 编程单 → 生成、仿真；示例平板铣削
ops = call("GET", "/api/cam/ops?item=SH-301", token=tok)
assert [o["seq"] for o in ops["ops"] if o["cam"]] == [20, 40, 50], ops
spec = call("POST", "/api/cam/spec", {"item": "SH-301", "seq": 20}, token=tok)
assert spec["mode"] == "rough" and spec["cut"]["ap"] == 2.5
j = call("POST", "/api/cam/jobs", {"spec": spec, "title": "演练"}, token=tok)
assert j["status"] == "done", j.get("error")
n_rough = len(j["programs"])
for k, p in enumerate(j["programs"]):
    assert not [c for c in p["checks"] if c["level"] == "error"], p["checks"]
    assert abs(p["sim"]["dev_min"]) <= 0.01 and p["sim"]["dev_max"] <= 0.01
    assert call("GET", "/api/cam/jobs/{}/{}.nc".format(j["id"], k), token=tok, raw=True).startswith(b"%\nO")
# 下发：挂到工艺规程粗车工序 → 提交 → 另一个人批准 → 程序随工艺规程生效下发（design.gcode → ERPNext 附件、派工、3D 回放）
r = call("POST", "/api/cam/jobs/{}/submit".format(j["id"]), {"note": "演练"}, token=tok)
assert r["status"] == "pending", r
boss = call("POST", "/api/login", {"name": "演练老师", "role": "manager", "mode": "teach"})["token"]
for c in r["comments"]:
    call("POST", "/api/process/submissions/{}/comments/{}".format(r["submission"], c["id"]), {"resolved": True}, token=boss)
a = call("POST", "/api/process/submissions/{}/decision".format(r["submission"]), {"decision": "approve", "note": "演练"}, token=boss)
assert a["status"] == "approved" and a["programs_released"] >= 2, a      # 这一版挂着的全部程序（重复演练时还有上次的精车程序）
gc = [g for g in call("GET", "/api/design/SH-301", token=tok)["gcode"] if g.get("process_revision") == a["revision"]
      and g["operation"].startswith("粗车")]
assert sorted(g["program"] for g in gc) == [1201, 1202] and all(g["machine"] == "cnc-l01-a" for g in gc), gc
if A.erp:
    import base64
    hdr = {"Authorization": "token {}:{}".format(A.erp_key, A.erp_secret)}
    t0 = time.time()
    names = []
    while time.time() - t0 < 60:
        q = urllib.request.Request(A.erp + "/api/resource/File?fields=" + urllib.parse.quote('["file_name"]') + "&filters="
                                   + urllib.parse.quote('[["attached_to_name","=","SH-301"]]') + "&limit_page_length=500", headers=hdr)
        names = [f["file_name"] for f in json.loads(urllib.request.urlopen(q, timeout=30).read().decode())["data"]]
        if any("O1201" in n for n in names) and any("O1202" in n for n in names):
            break
        time.sleep(2)
    assert any("O1201" in n for n in names) and any("O1202" in n for n in names), names[-6:]
    print("ERPNext：SH-301 附上了粗车程序 O1201、O1202")
print("数控程序随工艺规程第 {} 版生效下发：{} 个".format(a["revision"], a["programs_released"]))
ex = call("POST", "/api/cam/examples/WQ-PLATE", token=tok)
spec = call("POST", "/api/cam/spec/geometry", {"sha": ex["sha"], "kind": "mill", "material": "6061", "name": "WQ-PLATE"}, token=tok)
j = call("POST", "/api/cam/jobs", {"spec": spec, "title": "演练"}, token=tok)
assert j["status"] == "done" and j["programs"][0]["sim"]["over"] == 0, j.get("error") or j["programs"][0]["checks"]
assert len(call("GET", "/api/cam/jobs/{}/h0.bin".format(j["id"]), token=tok, raw=True)) == 4 * j["programs"][0]["sim"]["nx"] * j["programs"][0]["sim"]["ny"]
print("数控编程演练通过：SH-301 粗车 {} 个程序，平板铣削 {:.1f} 分钟".format(n_rough, j["compare"]["program_minutes"]))
