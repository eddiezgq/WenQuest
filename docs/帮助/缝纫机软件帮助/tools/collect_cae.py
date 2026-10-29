"""帮助里 CAE 一节用到的真实计算结果（第 49 轮）：在本地完整环境（tools/local + 数字工厂 cae、hub）里，
用网页版同一个接口算一遍平缝机教材算例的针杆曲柄有限元 + 疲劳、刺布机构动力学、主轴电机选型，存成 data/web_cae.json。
用法：python3 collect_cae.py [网关地址] [账号] [密码]"""
import json
import sys
import time
import urllib.request
from pathlib import Path

B = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8090"
U, P = (sys.argv[2], sys.argv[3]) if len(sys.argv) > 3 else ("teacher1", "Test#2026")


def req(m, p, b=None, t=None):
    r = urllib.request.Request(B + p, data=json.dumps(b).encode() if b is not None else None, method=m,
                               headers={"content-type": "application/json", **({"authorization": "Bearer " + t} if t else {})})
    return json.load(urllib.request.urlopen(r, timeout=300))


t = req("POST", "/api/v1/auth/login", {"username": U, "password": P})["token"]
a = req("POST", "/api/v1/sewing/cae/fea", {"machine": "lockstitch", "params": {}, "part": "NeedleCrank"}, t)
b = req("POST", "/api/v1/sewing/cae/mbd", {"machine": "lockstitch", "params": {}}, t)
motor = req("POST", "/api/v1/sewing/cae/motor", {"machine": "lockstitch", "params": {}}, t)
for _ in range(120):
    ja, jb = req("GET", f"/api/v1/sewing/cae/jobs/{a['id']}", t=t), req("GET", f"/api/v1/sewing/cae/jobs/{b['id']}", t=t)
    if ja["status"] in ("done", "failed") and jb["status"] in ("done", "failed"):
        break
    time.sleep(5)
fr, mr = ja.get("result") or {}, jb.get("result") or {}
out = {"date": time.strftime("%Y-%m-%d"),
       "fea": {k: fr.get(k) for k in ("vm_max_mpa", "safety_factor", "u_max_mm", "elements", "infinite")},
       "fatigue": {k: (fr.get("fatigue") or {}).get(k) for k in ("S_D", "cycles_per_block", "block_seconds")},
       "mbd": {k: mr.get(k) for k in ("torque_peak_mbd", "torque_peak_formula", "diff", "series", "formula")},
       "motor": {"peak_nm": motor["peak_nm"], "rms_nm": motor["rms_nm"], "power_w": motor["power_w"],
                 "pick": (motor.get("pick") or {}).get("name"), "safety": motor["safety"]}}
Path(__file__).resolve().parent.parent.joinpath("data", "web_cae.json").write_text(json.dumps(out, ensure_ascii=False))
print(json.dumps({k: v for k, v in out.items() if k != "mbd"}, ensure_ascii=False), out["mbd"]["torque_peak_mbd"], out["mbd"]["diff"])
