# -*- coding: utf-8 -*-
"""问渠缝纫机工作台连问渠（第 49 轮）：AI 助手、本单位零件库。不依赖图形界面，命令行里也能测。

钥匙：网页版“零件库 → FreeCAD 钥匙”生成，每人一把；存在 FreeCAD 的用户设置里（只在本机）。
服务器：默认 https://learn.wenquestrobotics.com；国内部署或本地测试时在设置里改。
"""
import json
import os
import ssl
import urllib.error
import urllib.request

DEFAULT_SERVER = "https://learn.wenquestrobotics.com"
PREF = "User parameter:BaseApp/Preferences/Mod/WenQuestSewing"


def settings():
    try:
        import FreeCAD as App
        g = App.ParamGet(PREF)
        return {"server": g.GetString("Server", DEFAULT_SERVER) or DEFAULT_SERVER, "key": g.GetString("Key", "")}
    except Exception:  # noqa: BLE001
        return {"server": os.environ.get("WQ_SEWING_SERVER", DEFAULT_SERVER), "key": os.environ.get("WQ_SEWING_KEY", "")}


def save_settings(server, key):
    import FreeCAD as App
    g = App.ParamGet(PREF)
    g.SetString("Server", (server or DEFAULT_SERVER).strip().rstrip("/"))
    g.SetString("Key", (key or "").strip())


class NetError(Exception):
    pass


ERR = {"bad_key": "钥匙不对：请在网页版“零件库 → FreeCAD 钥匙”重新生成，再在这里填一次。",
       "not_licensed": "这个账号还没开通企业版。", "quota": "今天的 AI 次数用完了，明天再来。",
       "not_found": "没有找到。", "rate_limited": "太频繁了，等一分钟。"}


class Client:
    def __init__(self, server=None, key=None, timeout=120):
        s = settings()
        self.server = (server or s["server"]).rstrip("/")
        self.key = key if key is not None else s["key"]
        self.timeout = timeout

    def _req(self, method, path, body=None, raw=False):
        if not self.key:
            raise NetError("还没填钥匙：先点“AI 助手”或“插入本单位零件”里的“设置钥匙”。")
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(self.server + path, data=data, method=method,
                                     headers={"X-WQ-Key": self.key, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=ssl.create_default_context()) as r:
                out = r.read()
        except urllib.error.HTTPError as e:
            try:
                code = json.loads(e.read().decode("utf-8")).get("error", "")
            except Exception:  # noqa: BLE001
                code = ""
            raise NetError(ERR.get(code) or "服务器返回错误（{} {}）".format(e.code, code)) from e
        except urllib.error.URLError as e:
            raise NetError("连不上问渠服务器（{}）：检查网络，或在设置里改服务器地址。".format(e.reason)) from e
        return out if raw else json.loads(out.decode("utf-8"))

    # AI 助手：kind = draft / explain / describe
    def ai(self, kind, machine, params, sentence=""):
        return self._req("POST", "/api/v1/sewing/ai/" + kind, {"machine": machine, "params": params, "sentence": sentence})

    def parts(self, q="", cat="", status="ok"):
        from urllib.parse import urlencode
        return self._req("GET", "/api/v1/sewing/parts?" + urlencode({"q": q, "cat": cat, "status": status}))

    def part(self, pid, machine=""):
        return self._req("GET", "/api/v1/sewing/parts/{}?machine={}".format(int(pid), machine))

    def step(self, pid):
        return self._req("GET", "/api/v1/sewing/parts/{}/step".format(int(pid)), raw=True)


def cache_dir():
    d = os.path.join(os.path.expanduser("~"), ".wenquest", "sewing-parts")
    os.makedirs(d, exist_ok=True)
    return d
