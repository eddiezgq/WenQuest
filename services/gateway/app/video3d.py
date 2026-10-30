"""三维仿真视频服务（第 38 轮）：老师和开通的企业账号在平台里一句话出一段工程级三维仿真视频。

一段视频 = 一个场景文件 scene.yaml（只有数据，格式见 tools/blender/场景格式.md）+ 对话记录 + 出片结果。
- AI 写场景、按意见改场景（国内 DeepSeek、美国 Claude，走 ai.py）；写完先过 check()，不合格让 AI 重写；
- 关键画面：blender 容器（POST /stills，自己服务器，约 1 分钟）；
- 小样、高清：临时租一台 Lambda 机器（带 GPU 和约 30 个 CPU 核），经 JupyterLab 传渲染器包、场景和 run.sh，
  在后台运行；网关每 15 秒读一次 status.json，完成后取回视频，马上关机。每次开机都记账（runs 表），
  免费的也记（收费 11 月做）。
AI 只在已有模型上做：模型清单见 USES。"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import logging
import re
import secrets
import shutil
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import yaml

log = logging.getLogger("wenquest.video3d")

USES = {"gen:arm6", "gen:conveyor", "gen:seam", "box", "cyl", "item", "weblab:sewing/proto-lockstitch",
        "gen:sewdesign"}        # 第 56 轮：缝纫机设计软件里这一台设计（只由缝纫机软件自动写，参数锁定）
ANGLE_MODELS = ("weblab:", "gen:sewdesign")
DRIVES = {"pick_place", "weblab"}
EFFECTS = {"xray", "cutaway", "blur", "flash"}
COLORS = {"body", "joint", "accent", "part", "table", "belt", "frame", "floor", "motor", "gear", "needle", "takeup", "hook",
          "feed", "steel", "shell", "wood", "thread", "bobbin", "dark", "chrome"}
MAX_SECONDS = 120
MAX_SCENE = 40_000
LIVE = ("queued", "starting", "rendering", "stopping")
QUALITY = {"draft": "小样", "hd": "高清"}


def now() -> int:
    return int(time.time())


# ---------------------------------------------------------------- 场景检查

def _num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _span(v, dur: float) -> bool:
    return (isinstance(v, list) and len(v) == 2 and all(_num(x) for x in v) and v[0] <= v[1]
            and v[0] >= -3 and v[1] <= dur + 3)


def check(text: str) -> tuple[dict | None, list[str]]:
    """(场景, []) 合格；(None 或场景, [问题…]) 不合格。问题用中文写，直接交给 AI 改。"""
    errs: list[str] = []
    if len(text) > MAX_SCENE:
        return None, [f"场景文件太长（{len(text)} 字符，最多 {MAX_SCENE}）"]
    try:
        s = yaml.safe_load(text)
    except yaml.YAMLError as e:
        return None, [f"不是合法的 YAML：{str(e)[:200]}"]
    if not isinstance(s, dict):
        return None, ["场景文件顶层要是一个字典（name、title、duration、models……）"]
    dur = s.get("duration")
    if not _num(dur) or not 2 <= dur <= MAX_SECONDS:
        errs.append(f"duration 要是 2–{MAX_SECONDS} 之间的秒数")
        dur = MAX_SECONDS
    t = s.get("title")
    if not (isinstance(t, dict) and isinstance(t.get("zh"), str) and isinstance(t.get("en"), str)):
        errs.append("title 要写成 {zh: 中文标题, en: English title}")
    if "stills" in s and not (isinstance(s["stills"], list) and 1 <= len(s["stills"]) <= 6 and all(_num(x) for x in s["stills"])):
        errs.append("stills（可选）是 1–6 个秒数：关键画面取在这几秒")
    if s.get("lang") not in (None, "both", "zh", "en"):
        errs.append("lang 只能是 both（默认，中英两行）、zh 或 en（只出一种文字）")
    if s.get("style") not in (None, "engineering", "cinematic"):
        errs.append("style 只能是 engineering（默认）或 cinematic")
    if "fps" in s and not (_num(s["fps"]) and 10 <= s["fps"] <= 60):
        errs.append("fps 要在 10–60 之间")
    models = s.get("models")
    ids: dict[str, str] = {}
    if not isinstance(models, list) or not models:
        errs.append("models 要是非空列表")
        models = []
    if len(models) > 24:
        errs.append("models 最多 24 个")
    for i, mo in enumerate(models):
        if not isinstance(mo, dict):
            errs.append(f"models 第 {i + 1} 项要是字典")
            continue
        mid, use = mo.get("id"), mo.get("use")
        if not (isinstance(mid, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,23}", mid)):
            errs.append(f"models 第 {i + 1} 项的 id 要是英文字母开头的短名字")
            continue
        if mid in ids:
            errs.append(f"model id 重复：{mid}")
        if use not in USES:
            errs.append(f"model {mid} 的 use={use!r} 不是已有模型；只能用 {', '.join(sorted(USES))}")
        ids[mid] = use
        for k in ("at", "start"):
            if k in mo and not (isinstance(mo[k], list) and len(mo[k]) in (2, 3) and all(_num(x) for x in mo[k])):
                errs.append(f"model {mid} 的 {k} 要是 [x, y] 或 [x, y, z]（米）")
        for k, v in (mo.get("colors") or {}).items() if isinstance(mo.get("colors"), dict) else []:
            if v not in COLORS:
                errs.append(f"model {mid} 的颜色 {k}: {v} 不在颜色名表里")
        if "color" in mo and mo["color"] not in COLORS:
            errs.append(f"model {mid} 的 color={mo['color']!r} 不在颜色名表里")
        if use == "gen:sewdesign":
            if mo.get("machine") not in ("lockstitch", "overlock"):
                errs.append(f"model {mid}（gen:sewdesign）的 machine 只能是 lockstitch 或 overlock")
            if not isinstance(mo.get("params", {}), dict) or len(mo.get("params") or {}) > 80:
                errs.append(f"model {mid}（gen:sewdesign）的 params 要是设计参数字典")
        if use == "item":
            for k in ("pick", "drop"):
                if not _num(mo.get(k)):
                    errs.append(f"item {mid} 要写 {k}（秒）")
            if mo.get("arm") and ids.get(mo["arm"], "gen:arm6") != "gen:arm6":
                errs.append(f"item {mid} 的 arm 要指向一个 gen:arm6")
    for mo in models:      # item 引用的机械臂可能写在它后面
        if isinstance(mo, dict) and mo.get("use") == "item":
            if mo.get("arm") not in ids:
                errs.append(f"item {mo.get('id')} 的 arm={mo.get('arm')!r} 没有这个模型")
            if mo.get("belt") and mo["belt"] not in ids:
                errs.append(f"item {mo.get('id')} 的 belt={mo['belt']!r} 没有这个模型")
    for i, d in enumerate(s.get("motion") or []):
        if not isinstance(d, dict) or d.get("drive") not in DRIVES:
            errs.append(f"motion 第 {i + 1} 项的 drive 只能是 {' / '.join(sorted(DRIVES))}")
            continue
        mid = d.get("model")
        if mid not in ids:
            errs.append(f"motion 第 {i + 1} 项的 model={mid!r} 没有这个模型")
            continue
        if d["drive"] == "weblab":
            if not str(ids[mid]).startswith(ANGLE_MODELS):
                errs.append(f"drive: weblab 要配 weblab: 或 gen:sewdesign 模型（{mid} 是 {ids[mid]}）")
            ang = d.get("angle")
            if not (isinstance(ang, list) and ang and all(isinstance(p, list) and len(p) == 2 and all(_num(x) for x in p) for p in ang)):
                errs.append("weblab 的 angle 要写成 [[秒, 主轴累计转角°], …]")
            elif any(b[0] < a[0] for a, b in zip(ang, ang[1:])) or ang[-1][0] > dur + 3:
                errs.append("weblab 的 angle 时间要从小到大、不超过 duration")
        else:
            if ids[mid] != "gen:arm6":
                errs.append(f"drive: pick_place 要配 gen:arm6（{mid} 是 {ids[mid]}）")
            pts = s.get("points") or {}
            for j, st in enumerate(d.get("steps") or []):
                if not isinstance(st, dict) or not _span(st.get("t"), dur):
                    errs.append(f"pick_place 第 {j + 1} 步的 t 要是 [起, 止] 秒")
                    continue
                for k in ("at", "from", "to"):
                    if k in st and st[k] not in pts:
                        errs.append(f"pick_place 第 {j + 1} 步的 {k}={st[k]!r} 不在 points 里")
    cam = s.get("camera")
    if not isinstance(cam, list) or not cam:
        errs.append("camera 要至少一个关键点")
        cam = []
    for i, k in enumerate(cam):
        if not (isinstance(k, dict) and _num(k.get("t")) and isinstance(k.get("look"), list) and len(k["look"]) == 3
                and all(_num(x) for x in k["look"]) and _num(k.get("az")) and _num(k.get("el")) and _num(k.get("dist"))
                and k["dist"] > 0):
            errs.append(f"camera 第 {i + 1} 个关键点要有 t、look [x,y,z]、az、el、dist（>0）")
        elif not -1 <= k["t"] <= dur + 1:
            errs.append(f"camera 第 {i + 1} 个关键点的 t={k['t']} 超出视频长度")
    if cam and all(isinstance(k, dict) and _num(k.get("t")) for k in cam):
        if any(b["t"] < a["t"] for a, b in zip(cam, cam[1:])):
            errs.append("camera 关键点的 t 要从小到大")
    groups_ok = lambda g: isinstance(g, str) and g.split(".", 1)[0] in ids  # noqa: E731
    for i, e in enumerate(s.get("effects") or []):
        if not isinstance(e, dict) or e.get("kind") not in EFFECTS:
            errs.append(f"effects 第 {i + 1} 项的 kind 只能是 {' / '.join(sorted(EFFECTS))}")
            continue
        if not _span(e.get("t"), dur):
            errs.append(f"effects 第 {i + 1} 项的 t 要是 [起, 止] 秒")
        for k in ("top", "hide", "show"):
            for g in e.get(k) or []:
                if not groups_ok(g):
                    errs.append(f"effects 第 {i + 1} 项 {k} 里的 {g!r} 要写成 <模型id>.<组名>")
    for i, lb in enumerate(s.get("labels") or []):
        if not (isinstance(lb, dict) and _span(lb.get("t"), dur) and isinstance(lb.get("zh"), str) and isinstance(lb.get("en"), str)):
            errs.append(f"labels 第 {i + 1} 条要有 t [起, 止]、zh、en")
            continue
        if len(lb["zh"]) > 46 or len(lb["en"]) > 120:
            errs.append(f"labels 第 {i + 1} 条太长（中文最多 46 字、英文 120 字符），会出框：{lb['zh'][:20]}…")
        if "phi" in lb and not (isinstance(lb["phi"], list) and len(lb["phi"]) == 2 and all(_num(x) for x in lb["phi"])):
            errs.append(f"labels 第 {i + 1} 条的 phi 要是 [起, 止]（度）")
        if lb.get("tone") not in (None, "bad", "warn"):
            errs.append(f"labels 第 {i + 1} 条的 tone 只能是 bad（红）或 warn（黄）")
    p = s.get("panel")
    if p is not None and not (isinstance(p, dict) and p.get("kind") in ("joints", "readouts")):
        errs.append("panel 的 kind 只能是 joints 或 readouts")
    return s, errs


def apply_lock(text: str, lock: dict | None) -> str:
    """缝纫机软件写的讲解片（第 56 轮）：AI 或人改场景时，设计模型的机型和参数改回原样——只许改镜头、节奏、字"""
    if not lock:
        return text
    try:
        s = yaml.safe_load(text)
    except yaml.YAMLError:
        return text
    if not isinstance(s, dict):
        return text
    changed = False
    for mo in s.get("models") or []:
        if isinstance(mo, dict) and mo.get("use") == "gen:sewdesign":
            if mo.get("machine") != lock["machine"] or mo.get("params") != lock["params"]:
                mo["machine"], mo["params"] = lock["machine"], dict(lock["params"])
                changed = True
    return yaml.safe_dump(s, allow_unicode=True, sort_keys=False, width=200) if changed else text


NUM_RE = re.compile(r"\d+(?:\.\d+)?")


def label_numbers(spec: dict) -> set[str]:
    """标题、字幕里出现的数（讲解片锁定用）"""
    out: set[str] = set()
    texts = [spec.get("title") or {}] + [x for x in spec.get("labels") or [] if isinstance(x, dict)]
    for x in texts:
        for k in ("zh", "en"):
            out |= set(NUM_RE.findall(str(x.get(k) or "")))
    return out


def lock_errors(spec: dict, lock: dict | None) -> list[str]:
    """缝纫机软件写的讲解片：设计模型不能删、不能换成别的模型；字幕里的数只能是计算核心给的那些（AI 只改镜头、节奏、字）"""
    if not lock:
        return []
    errs = []
    models = [mo for mo in spec.get("models") or [] if isinstance(mo, dict)]
    if not any(mo.get("id") == lock["model"] and mo.get("use") == "gen:sewdesign" for mo in models):
        errs.append(f"这是缝纫机设计软件的讲解片：模型 {lock['model']}（gen:sewdesign）不能删、不能换")
    other = sorted({str(mo.get("use")) for mo in models if mo.get("use") not in ("gen:sewdesign", "box", "cyl")})
    if other or sum(mo.get("use") == "gen:sewdesign" for mo in models) > 1:
        errs.append("这是缝纫机设计软件的讲解片：除了这台设计，只能加 box、cyl 做标示，不能加别的模型（" + "、".join(other) + "）")
    allowed = set(lock.get("numbers") or [])
    if allowed:
        bad = sorted(label_numbers(spec) - allowed)
        if bad:
            errs.append("这是缝纫机设计软件的讲解片：字幕、标题里的数只能用计算核心给的（原字幕里有的），不能写 " + "、".join(bad[:6]))
    return errs


def normalized(text: str) -> str:
    """出片前统一文件名（成片按 name 命名）。"""
    s = yaml.safe_load(text)
    s["name"] = "video"
    s.pop("slug", None)
    return yaml.safe_dump(s, allow_unicode=True, sort_keys=False, width=200)


def still_times(spec: dict, n: int = 6) -> list[float]:
    """关键画面取在哪几秒：场景写了 stills 就用它（第 56 轮：讲解片要停在出问题的转角）；
    否则镜头关键点之间的中点和整段均分点合起来，挑 n 个。"""
    dur = float(spec.get("duration") or 10)
    own = spec.get("stills")
    if isinstance(own, list) and own and all(_num(x) for x in own):
        return sorted({round(min(max(float(x), 0.2), dur - 0.2), 1) for x in own})[:n]
    cand = [dur * (k + 0.5) / n for k in range(n)]
    keys = sorted({float(k["t"]) for k in spec.get("camera") or [] if isinstance(k, dict) and _num(k.get("t"))})
    mids = [(a + b) / 2 for a, b in zip(keys, keys[1:]) if b - a > 1.5]
    if len(mids) >= n:
        step = len(mids) / n
        cand = [mids[int(i * step)] for i in range(n)]
    return [round(min(max(t, 0.2), dur - 0.2), 1) for t in cand]


# ---------------------------------------------------------------- blender 容器

class Blender:
    def __init__(self, url: str, transport: httpx.AsyncBaseTransport | None = None):
        self.url = url.rstrip("/")
        self.transport = transport
        self._cache: dict[str, Any] = {}

    def client(self, timeout: float) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=timeout, trust_env=False, transport=self.transport)

    @property
    def on(self) -> bool:
        return bool(self.url)

    async def _get(self, path: str) -> Any:
        if path not in self._cache:
            async with self.client(60) as c:
                r = await c.get(self.url + path)
                r.raise_for_status()
                self._cache[path] = r.json() if path != "/bundle" and path != "/run.sh" else r.content
        return self._cache[path]

    async def samples(self) -> list[dict]:
        if not self.on:
            return []
        try:
            return (await self._get("/samples"))["samples"]
        except Exception:  # noqa: BLE001
            log.exception("blender /samples")
            return []

    async def format(self) -> str:
        try:
            return (await self._get("/format"))["text"]
        except Exception:  # noqa: BLE001
            return ""

    async def bundle(self) -> bytes:
        return await self._get("/bundle")

    async def run_sh(self) -> bytes:
        return await self._get("/run.sh")

    async def stills(self, scene: str, times: list[float]) -> dict:
        async with self.client(900) as c:
            r = await c.post(self.url + "/stills", json={"scene": scene, "times": times})
            r.raise_for_status()
            return r.json()


# ---------------------------------------------------------------- 租机（Lambda）与机器上的 JupyterLab

class NoCapacity(Exception):
    """现在没有空闲机器（稍后再试）。"""


class Jupyter:
    """租来的机器上的 JupyterLab：传文件、读文件、取文件、在后台运行一条命令。"""

    def __init__(self, http: httpx.AsyncClient, url: str, token: str):
        self.http, self.url, self.token = http, url.rstrip("/"), token
        self.head = {"Authorization": f"token {token}"}

    async def put(self, path: str, data: bytes | str) -> None:
        parts = path.split("/")
        for i in range(1, len(parts)):
            r = await self.http.put(f"{self.url}/api/contents/{'/'.join(parts[:i])}", headers=self.head,
                                    json={"type": "directory"}, timeout=60)
            if r.status_code >= 400 and r.status_code != 409:
                r.raise_for_status()
        body = ({"type": "file", "format": "base64", "content": base64.b64encode(data).decode()} if isinstance(data, bytes)
                else {"type": "file", "format": "text", "content": data})
        r = await self.http.put(f"{self.url}/api/contents/{path}", headers=self.head, json=body, timeout=300)
        r.raise_for_status()

    async def read_text(self, path: str) -> str | None:
        r = await self.http.get(f"{self.url}/api/contents/{path}", headers=self.head, params={"content": 1, "format": "text"}, timeout=60)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json().get("content")

    async def download(self, path: str, dest: Path) -> None:
        tmp = dest.with_suffix(dest.suffix + ".part")
        async with self.http.stream("GET", f"{self.url}/files/{path}", headers=self.head, timeout=600) as r:
            r.raise_for_status()
            with tmp.open("wb") as f:
                async for chunk in r.aiter_bytes():
                    f.write(chunk)
        tmp.replace(dest)

    async def run(self, code: str) -> None:
        """在新开的内核里执行一段 Python（只用来在后台启动 run.sh）。"""
        import websockets
        r = await self.http.post(f"{self.url}/api/kernels", headers=self.head, json={"name": "python3"}, timeout=120)
        r.raise_for_status()
        kid = r.json()["id"]
        ws_url = re.sub(r"^http", "ws", self.url) + f"/api/kernels/{kid}/channels?token={self.token}"
        mid, sess = uuid.uuid4().hex, uuid.uuid4().hex
        msg = {"header": {"msg_id": mid, "username": "wq", "session": sess, "msg_type": "execute_request", "version": "5.3",
                          "date": datetime.now(timezone.utc).isoformat()},
               "parent_header": {}, "metadata": {}, "channel": "shell", "buffers": [],
               "content": {"code": code, "silent": False, "store_history": False, "user_expressions": {}, "allow_stdin": False,
                           "stop_on_error": True}}
        async with websockets.connect(ws_url, additional_headers=self.head, max_size=None, open_timeout=60) as ws:
            await ws.send(json.dumps(msg))
            end = time.time() + 120
            while time.time() < end:
                m = json.loads(await asyncio.wait_for(ws.recv(), timeout=max(1.0, end - time.time())))
                if (m.get("parent_header") or {}).get("msg_id") == mid and m.get("msg_type") == "execute_reply":
                    if (m.get("content") or {}).get("status") != "ok":
                        raise RuntimeError("kernel: " + json.dumps(m.get("content"))[:300])
                    return
        raise RuntimeError("kernel: no reply")


START_CODE = ("import subprocess, os\n"
              "os.chmod('wq3d/run.sh', 0o755)\n"
              "subprocess.Popen(['bash', 'wq3d/run.sh'], stdout=open('wq3d/run.log', 'w'), stderr=subprocess.STDOUT,"
              " start_new_session=True)\n")


class Lambda:
    """Lambda Cloud API v1。按 types 的顺序挑现在有空的机型和地区；没有就 NoCapacity。"""
    name = "lambda"
    KEY_NAME = "wenquest-video3d"

    def __init__(self, http: httpx.AsyncClient, key: str, url: str, types: str):
        self.http, self.key, self.url = http, key, url.rstrip("/")
        self.types = [t.strip() for t in types.split(",") if t.strip()]

    async def _call(self, method: str, path: str, **kw) -> Any:
        r = await self.http.request(method, self.url + path, headers={"Authorization": f"Bearer {self.key}"}, timeout=60, **kw)
        if r.status_code >= 400:
            raise RuntimeError(f"Lambda {r.status_code}: {r.text[:300]}")
        return r.json().get("data")

    async def _ssh_key(self) -> str:
        """Lambda 开机必须带一把 SSH 公钥；没有就让 Lambda 生成一把（私钥不要，平台只走 JupyterLab）。"""
        keys = await self._call("GET", "/ssh-keys") or []
        if not any(k.get("name") == self.KEY_NAME for k in keys):
            await self._call("POST", "/ssh-keys", json={"name": self.KEY_NAME})
        return self.KEY_NAME

    async def launch(self, label: str) -> dict:
        avail = await self._call("GET", "/instance-types") or {}
        for t in self.types:
            info = avail.get(t) or {}
            regions = [r.get("name") for r in info.get("regions_with_capacity_available") or []]
            if not regions:
                continue
            region = next((r for r in regions if r.startswith("us-")), regions[0])
            price = float(((info.get("instance_type") or {}).get("price_cents_per_hour") or 0)) / 100
            key = await self._ssh_key()
            try:
                data = await self._call("POST", "/instance-operations/launch", json={
                    "region_name": region, "instance_type_name": t, "ssh_key_names": [key], "name": label[:60], "quantity": 1})
            except RuntimeError as e:
                if "capacity" in str(e).lower():
                    continue
                raise
            return {"pid": str((data.get("instance_ids") or [""])[0]), "kind": t, "region": region, "price_hour": price}
        raise NoCapacity()

    async def status(self, pid: str) -> dict:
        inst = await self._call("GET", f"/instances/{pid}") or {}
        st = inst.get("status")
        state = {"active": "running", "booting": "starting", "terminated": "stopped", "terminating": "stopped",
                 "unhealthy": "failed"}.get(st, "starting")
        out = {"state": state}
        if state == "running":
            out.update(url=str(inst.get("jupyter_url") or "").split("?", 1)[0].rstrip("/"), token=inst.get("jupyter_token") or "")
            if not out["url"]:
                out["state"] = "starting"
        return out

    async def stop(self, pid: str) -> None:
        await self._call("POST", "/instance-operations/terminate", json={"instance_ids": [pid]})

    def jupyter(self, url: str, token: str) -> Jupyter:
        return Jupyter(self.http, url, token)


class MockJupyter:
    """测试用：run 之后几次读状态就“出完”，文件是几个字节。"""

    def __init__(self, box: dict):
        self.box = box

    async def put(self, path, data):
        self.box.setdefault("files", {})[path] = data

    async def run(self, code):
        self.box["started"] = True
        self.box["polls"] = 0

    async def read_text(self, path):
        if path != "wq3d/status.json" or not self.box.get("started"):
            return None
        self.box["polls"] += 1
        if self.box.get("fail"):
            return json.dumps({"stage": "error", "done": 0, "total": 0, "msg": "boom", "files": []})
        if self.box["polls"] < 2:
            return json.dumps({"stage": "render", "done": 5, "total": 10, "msg": "", "files": []})
        q = json.loads(self.box["files"]["wq3d/job/job.json"])["quality"]
        files = ["video_小样.mp4"] if q == "draft" else ["video.mp4", "video.webm"]
        return json.dumps({"stage": "done", "done": 10, "total": 10, "msg": "", "files": files})

    async def download(self, path, dest: Path):
        dest.write_bytes(b"\x00\x00\x00\x18ftypmp42 mock " + path.encode())


class Mock:
    name = "mock"

    def __init__(self, capacity: bool = True, delay: int = 1):
        self.capacity, self.delay = capacity, delay
        self.machines: dict[str, dict] = {}
        self.box: dict = {}

    async def launch(self, label: str) -> dict:
        if not self.capacity:
            raise NoCapacity()
        pid = f"mock-{len(self.machines) + 1}"
        self.machines[pid] = {"on": True, "calls": 0, "label": label}
        return {"pid": pid, "kind": "gpu_1x_a10", "region": "us-east-1", "price_hour": 0.86}

    async def status(self, pid: str) -> dict:
        mm = self.machines.get(pid)
        if not mm or not mm["on"]:
            return {"state": "stopped"}
        mm["calls"] += 1
        if mm["calls"] <= self.delay:
            return {"state": "starting"}
        return {"state": "running", "url": "http://jupyter.mock", "token": "t"}

    async def stop(self, pid: str) -> None:
        if pid in self.machines:
            self.machines[pid]["on"] = False

    def jupyter(self, url: str, token: str) -> MockJupyter:
        return MockJupyter(self.box)



# ---------------------------------------------------------------- 存储与记账

class Store:
    """data_dir/video3d/: videos/<id>/(meta.json, scene.yaml, stills/, out/)；video3d.db（开通名单、用机记录）。"""

    def __init__(self, root: Path):
        self.root = Path(root)
        (self.root / "videos").mkdir(parents=True, exist_ok=True)
        self.db = self.root / "video3d.db"
        self.lock = threading.Lock()
        with self._con() as c:
            c.executescript("""
            create table if not exists grant_(user_id integer primary key, username text, note text, by integer, at integer);
            create table if not exists run(id text primary key, video text, user_id integer, quality text, provider text,
                kind text, region text, pid text, state text, price_hour real, queued_at integer, launched_at integer,
                ended_at integer, end_reason text, cost real, seconds integer, msg text, url text, token text, final text,
                errors integer default 0);
            """)

    def _con(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.db, timeout=30)
        c.row_factory = sqlite3.Row
        return c

    # 开通名单（企业账号）
    def granted(self, uid: int) -> bool:
        with self._con() as c:
            return c.execute("select 1 from grant_ where user_id=?", (uid,)).fetchone() is not None

    def grants(self) -> list[dict]:
        with self._con() as c:
            return [dict(r) for r in c.execute("select * from grant_ order by at desc")]

    def grant(self, uid: int, username: str, note: str, by: int) -> None:
        with self.lock, self._con() as c:
            c.execute("insert or replace into grant_ values(?,?,?,?,?)", (uid, username, note, by, now()))

    def revoke(self, uid: int) -> None:
        with self.lock, self._con() as c:
            c.execute("delete from grant_ where user_id=?", (uid,))

    # 用机记录
    def add_run(self, **kw) -> None:
        cols = ",".join(kw)
        with self.lock, self._con() as c:
            c.execute(f"insert into run({cols}) values({','.join('?' * len(kw))})", tuple(kw.values()))

    def update_run(self, rid: str, **kw) -> None:
        with self.lock, self._con() as c:
            c.execute(f"update run set {','.join(k + '=?' for k in kw)} where id=?", (*kw.values(), rid))

    def run(self, rid: str) -> dict | None:
        with self._con() as c:
            r = c.execute("select * from run where id=?", (rid,)).fetchone()
            return dict(r) if r else None

    def live_runs(self) -> list[dict]:
        with self._con() as c:
            return [dict(r) for r in c.execute(f"select * from run where state in ({','.join('?' * len(LIVE))}) order by queued_at", LIVE)]

    def runs(self, limit: int = 200) -> list[dict]:
        with self._con() as c:
            return [dict(r) for r in c.execute("select * from run order by queued_at desc limit ?", (limit,))]

    # 视频
    def vdir(self, vid: str) -> Path:
        if not re.fullmatch(r"[a-f0-9]{12}", vid or ""):
            raise KeyError(vid)
        return self.root / "videos" / vid

    def load(self, vid: str) -> dict:
        p = self.vdir(vid) / "meta.json"
        if not p.exists():
            raise KeyError(vid)
        return json.loads(p.read_text(encoding="utf-8"))

    def save(self, V: dict) -> None:
        d = self.vdir(V["id"])
        d.mkdir(parents=True, exist_ok=True)
        V["updated"] = now()
        tmp = d / "meta.json.tmp"
        tmp.write_text(json.dumps(V, ensure_ascii=False), encoding="utf-8")
        tmp.replace(d / "meta.json")

    def scene(self, vid: str) -> str:
        p = self.vdir(vid) / "scene.yaml"
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def set_scene(self, V: dict, text: str) -> None:
        (self.vdir(V["id"]) / "scene.yaml").write_text(text, encoding="utf-8")
        V["version"] = int(V.get("version") or 0) + 1

    def list(self, uid: int | None) -> list[dict]:
        out = []
        for p in (self.root / "videos").glob("*/meta.json"):
            try:
                V = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if uid is None or V.get("owner") == uid:
                out.append(V)
        return sorted(out, key=lambda v: -int(v.get("updated") or 0))

    def delete(self, vid: str) -> None:
        shutil.rmtree(self.vdir(vid), ignore_errors=True)


# ---------------------------------------------------------------- AI 写场景

SYSTEM = """你是问渠的三维仿真视频编导。用户用一句话说要什么视频，你写出场景文件 scene.yaml（只写数据，不写程序），
平台照着用 Blender 渲染出工程级讲解视频。

硬规则：
1. 只用已有模型（下面格式说明里的 use 清单）；不能编造新的 use、零件名、组名或颜色名。没有合适模型时，用已有模型做最接近的讲解，并在 reply 里说明缺什么。
2. 运动由程序算：机械臂用 pick_place，缝纫机用 drive: weblab 的 angle；不要手写关键帧坐标。
3. 中英标注成对（zh、en），标题栏中文不超过 30 字、英文不超过 90 字符；一条标注讲一件事。
4. 时长一般 20–60 秒；镜头要交代全景 → 关键部位特写 → 收尾全景；慢放、剖开、透视按讲解需要用。
5. 坐标单位米，z 向上；缝纫机的针在 x≈−0.017、y=0，针板面 z=0，旋梭在针板下约 21 mm。
6. 默认工程图风格；用户明确要“震撼、电影感、宣传片”才用 style: cinematic。
7. scene 字段里放完整的 YAML 文本（不要加 ``` 包裹）；reply 用中文一两句话告诉用户这段视频怎么安排的。"""


def scene_schema() -> dict:
    return {"type": "object", "properties": {
        "scene": {"type": "string"}, "reply": {"type": "string"}}, "required": ["scene", "reply"]}


def fake_scene(samples: list[dict], prompt: str) -> dict:
    """测试与没有 AI 时：拿最接近的样片当底稿。"""
    pick = next((s for s in samples if "缝" in prompt and "缝纫机一针" == s["id"]), None) or (samples[0] if samples else None)
    if pick:
        return {"scene": pick["scene"], "reply": f"先用样片“{pick['id']}”做底稿。"}
    return {"scene": BUILTIN, "reply": "先用一段机械臂的底稿。"}


BUILTIN = """name: demo
title: {zh: 六轴机械臂搬运, en: A six-axis arm moves a part}
duration: 12
models:
  - {id: arm, use: "gen:arm6"}
  - {id: base, use: box, size: [0.4, 0.4, 0.4], at: [0.6, 0, 0.2], color: table}
camera:
  - {t: 0, look: [0.3, 0, 0.5], az: -30, el: 20, dist: 2.6}
  - {t: 12, look: [0.3, 0, 0.5], az: 20, el: 25, dist: 2.4}
labels:
  - {t: [0, 12], zh: 六轴机械臂, en: Six-axis arm}
"""


# ---------------------------------------------------------------- 服务

OUT_NAMES = {"draft": {"video_小样.mp4": "draft.mp4"}, "hd": {"video.mp4": "hd.mp4", "video.webm": "hd.webm"}}


class Service:
    def __init__(self, root: Path, ai, blender: Blender, provider, *, max_machines: int = 2, max_hours: float = 3.0,
                 wait_minutes: int = 60):
        self.store = Store(root)
        self.ai, self.blender, self.provider = ai, blender, provider
        self.max_machines, self.max_hours, self.wait = max_machines, max_hours, wait_minutes
        self.tick_lock = asyncio.Lock()
        self.tasks: set[asyncio.Task] = set()

    @property
    def render_on(self) -> bool:
        return self.provider is not None

    def spawn(self, coro) -> None:
        t = asyncio.create_task(coro)
        self.tasks.add(t)
        t.add_done_callback(self.tasks.discard)

    # ---- 新建、AI 写和改
    async def create(self, owner: int, owner_name: str, prompt: str, sample: str) -> dict:
        vid = secrets.token_hex(6)
        V = {"id": vid, "owner": owner, "owner_name": owner_name, "prompt": prompt, "created": now(), "version": 0,
             "title": {"zh": "新视频", "en": "New video"}, "chat": [], "busy": "", "ai_error": "", "from_sample": sample,
             "stills": {}, "renders": {}}
        self.store.vdir(vid).mkdir(parents=True, exist_ok=True)
        if sample:
            smp = next((x for x in await self.blender.samples() if x["id"] == sample), None)
            if not smp:
                raise KeyError(sample)
            self.store.set_scene(V, smp["scene"])
            V["title"] = dict(smp.get("title") or V["title"])
            V["chat"].append({"who": "ai", "text": f"已复制样片“{sample}”。可以直接出关键画面，或者告诉我要改什么。", "at": now()})
        if prompt:
            V["chat"].append({"who": "me", "text": prompt, "at": now()})
            V["busy"] = "ai"
        self.store.save(V)
        if prompt:
            self.spawn(self.write(vid, prompt))
        return V

    async def say(self, V: dict, text: str) -> dict:
        V["chat"].append({"who": "me", "text": text, "at": now()})
        V["busy"], V["ai_error"] = "ai", ""
        self.store.save(V)
        self.spawn(self.write(V["id"], text))
        return V

    async def write(self, vid: str, instruction: str) -> None:
        try:
            samples = await self.blender.samples()
            fmt = await self.blender.format()
            V = self.store.load(vid)
            cur = self.store.scene(vid)
            refs = [x for x in samples if x["id"] in ("旋梭钩线_整机", "机械臂抓取")][:2]
            hist = "\n".join(f"{'用户' if c['who'] == 'me' else '你'}：{c['text']}" for c in V["chat"][-8:-1])
            base = ("## 场景格式说明\n" + (fmt or "（见样板）") + "\n\n## 样板场景\n"
                    + "\n\n".join(f"### {x['id']}\n{x['scene']}" for x in refs)
                    + ("\n\n## 当前场景（在它上面改）\n" + cur if cur else "")
                    + ("\n\n## 之前的对话\n" + hist if hist else "")
                    + ("\n\n## 注意\n这是缝纫机设计软件按企业的设计自动写的讲解片：模型 " + V["lock"]["model"]
                       + "（gen:sewdesign）的 machine、params 不能改，不能删、不能加别的模型（只能加 box、cyl 做标示）；"
                       "字幕、标题里的数只能用原字幕里已有的数。只改镜头、节奏、透视剖开、字幕措辞。" if V.get("lock") else "")
                    + "\n\n## 这次的要求\n" + instruction)
            prompt, last_errs = base, []
            for _ in range(3):
                res = await self.ai.json(system=SYSTEM, prompt=prompt, schema=scene_schema(), max_tokens=8000,
                                         fake=lambda: fake_scene(samples, instruction) if not cur else {"scene": cur, "reply": "好的，已按你的意见改了。"})
                text = re.sub(r"^```(?:yaml)?\s*|\s*```\s*$", "", str(res.get("scene") or "").strip())
                text = apply_lock(text, V.get("lock"))
                spec, errs = check(text)
                errs = errs or lock_errors(spec, V.get("lock"))
                if not errs:
                    V = self.store.load(vid)
                    self.store.set_scene(V, text)
                    t = spec.get("title") or {}
                    V["title"] = {"zh": str(t.get("zh") or V["title"]["zh"])[:60], "en": str(t.get("en") or V["title"]["en"])[:120]}
                    V["chat"].append({"who": "ai", "text": str(res.get("reply") or "写好了。")[:1000], "at": now()})
                    V["busy"], V["ai_error"] = "", ""
                    self.store.save(V)
                    return
                last_errs = errs
                prompt = base + "\n\n## 上一稿没通过检查，请改正后重写完整场景\n" + "\n".join("- " + e for e in errs[:20]) + "\n\n上一稿：\n" + text[:MAX_SCENE]
            V = self.store.load(vid)
            V["busy"], V["ai_error"] = "", "AI 写的场景三次都没通过检查：" + "；".join(last_errs[:3])
            V["chat"].append({"who": "ai", "text": "这次没写成，请换个说法再试，或者从样片开始改。", "at": now()})
            self.store.save(V)
        except Exception as e:  # noqa: BLE001
            log.exception("video3d write %s", vid)
            try:
                V = self.store.load(vid)
                V["busy"], V["ai_error"] = "", f"AI 出错：{type(e).__name__}"
                self.store.save(V)
            except KeyError:
                pass

    def set_scene(self, V: dict, text: str) -> list[str]:
        text = apply_lock(text, V.get("lock"))
        spec, errs = check(text)
        errs = errs or lock_errors(spec, V.get("lock"))
        if errs:
            return errs
        self.store.set_scene(V, text)
        t = spec.get("title") or {}
        V["title"] = {"zh": str(t.get("zh") or "")[:60], "en": str(t.get("en") or "")[:120]}
        self.store.save(V)
        return []

    # ---- 关键画面（blender 容器）
    async def stills(self, vid: str) -> None:
        V = self.store.load(vid)
        text = self.store.scene(vid)
        spec, errs = check(text)
        times = still_times(spec or {})
        V["stills"] = {"state": "running", "version": V.get("version"), "times": times, "n": 0, "error": "", "at": now()}
        self.store.save(V)
        try:
            r = await self.blender.stills(normalized(text), times)
            d = self.store.vdir(vid) / "stills"
            shutil.rmtree(d, ignore_errors=True)
            d.mkdir()
            if r.get("ok"):
                for i, b in enumerate(r["stills"]):
                    (d / f"{i}.png").write_bytes(base64.b64decode(b))
            V = self.store.load(vid)
            V["stills"].update(state="done" if r.get("ok") else "failed", n=len(r.get("stills") or []),
                               error=str(r.get("error") or "")[-1500:], seconds=r.get("seconds"))
        except Exception as e:  # noqa: BLE001
            log.exception("video3d stills %s", vid)
            V = self.store.load(vid)
            V["stills"].update(state="failed", error=f"关键画面服务出错：{type(e).__name__}")
        self.store.save(V)

    # ---- 小样、高清（租机）
    def request_render(self, V: dict, quality: str, uid: int) -> str:
        rid = secrets.token_hex(6)
        text = normalized(self.store.scene(V["id"]))
        (self.store.vdir(V["id"]) / f"run_{rid}.yaml").write_text(text, encoding="utf-8")
        self.store.add_run(id=rid, video=V["id"], user_id=uid, quality=quality, provider=getattr(self.provider, "name", ""),
                           state="queued", queued_at=now(), price_hour=0.0)
        V.setdefault("renders", {})[quality] = {"state": "queued", "run": rid, "version": V.get("version"), "stage": "",
                                                 "done": 0, "total": 0, "error": "", "at": now()}
        self.store.save(V)
        return rid

    def cancel(self, V: dict, quality: str) -> None:
        R = (V.get("renders") or {}).get(quality) or {}
        run = self.store.run(R.get("run") or "")
        if run and run["state"] in LIVE and run["state"] != "stopping":
            self._end(run, "cancelled", "cancelled", "")

    def _view(self, vid: str, quality: str, **kw) -> None:
        try:
            V = self.store.load(vid)
        except KeyError:
            return
        R = (V.get("renders") or {}).get(quality)
        if R is not None:
            R.update(kw)
            self.store.save(V)

    def _end(self, run: dict, final: str, reason: str, msg: str) -> None:
        """结束一次出片：先记下结果，机器关掉以后才算完（关机失败下一轮再关）。"""
        t = now()
        secs = (t - run["launched_at"]) if run.get("launched_at") else 0
        self.store.update_run(run["id"], state="stopping" if run.get("pid") else final, final=final, end_reason=reason,
                              msg=msg[:2000], ended_at=t, seconds=secs, cost=round(secs / 3600 * (run.get("price_hour") or 0), 4))
        self._view(run["video"], run["quality"], state=final, error=msg[:1500] if final == "failed" else "", at=t)

    async def tick(self) -> None:
        if self.provider is None:
            return
        async with self.tick_lock:
            for run in self.store.live_runs():
                try:
                    await self._advance(run)
                except Exception as e:  # noqa: BLE001
                    log.exception("video3d run %s", run["id"])
                    n = int(run.get("errors") or 0) + 1
                    self.store.update_run(run["id"], errors=n)
                    if n >= 40 and run["state"] != "stopping":       # 连续约 10 分钟出错
                        self._end(run, "failed", "error", f"{type(e).__name__}: {e}")

    async def _advance(self, run: dict) -> None:
        t, st = now(), run["state"]
        if st == "stopping":
            try:
                await self.provider.stop(run["pid"])
            except Exception as e:  # noqa: BLE001
                if "not found" not in str(e).lower():
                    raise
            self.store.update_run(run["id"], state=run.get("final") or "done")
            return
        try:
            self.store.load(run["video"])
        except KeyError:
            self._end(run, "cancelled", "deleted", "")
            return
        if run.get("launched_at") and t - run["launched_at"] > self.max_hours * 3600:
            self._end(run, "failed", "time_limit", f"超过 {self.max_hours} 小时还没出完，已关机")
            return
        if st == "queued":
            busy = sum(1 for r in self.store.live_runs() if r["state"] in ("starting", "rendering"))
            if busy >= self.max_machines:
                self._view(run["video"], run["quality"], stage="waiting_machine")
                return
            try:
                m = await self.provider.launch(f"wq-video3d-{run['id']}")
            except NoCapacity:
                if t - run["queued_at"] > self.wait * 60:
                    self._end(run, "failed", "no_machine", f"等了 {self.wait} 分钟还没有空闲机器，请稍后再出")
                else:
                    self._view(run["video"], run["quality"], stage="waiting_machine")
                return
            self.store.update_run(run["id"], state="starting", pid=m["pid"], kind=m["kind"], region=m["region"],
                                  price_hour=m["price_hour"], launched_at=now(), errors=0)
            self._view(run["video"], run["quality"], state="starting", stage="booting")
            return
        if st == "starting":
            s = await self.provider.status(run["pid"])
            if s["state"] in ("stopped", "failed"):
                self._end(run, "failed", "machine_failed", "租的机器没有开起来，请重出")
                return
            if s["state"] != "running":
                if t - run["launched_at"] > 20 * 60:
                    self._end(run, "failed", "boot_timeout", "租的机器 20 分钟还没开好，已关机，请重出")
                return
            jup = self.provider.jupyter(s["url"], s["token"])
            q = run["quality"]
            await jup.put("wq3d/bundle.tgz", await self.blender.bundle())
            await jup.put("wq3d/run.sh", (await self.blender.run_sh()).decode("utf-8"))
            await jup.put("wq3d/job/scene.yaml", (self.store.vdir(run["video"]) / f"run_{run['id']}.yaml").read_text(encoding="utf-8"))
            await jup.put("wq3d/job/job.json", json.dumps({"quality": q}))
            await jup.run(START_CODE)
            self.store.update_run(run["id"], state="rendering", url=s["url"], token=s["token"], errors=0)
            self._view(run["video"], q, state="rendering", stage="setup")
            return
        if st == "rendering":
            jup = self.provider.jupyter(run["url"], run["token"])
            raw = await jup.read_text("wq3d/status.json")
            self.store.update_run(run["id"], errors=0)
            if not raw:
                return
            s = json.loads(raw)
            if s.get("stage") == "error":
                self._end(run, "failed", "render_error", "出片出错：" + str(s.get("msg") or "")[-1200:])
                return
            if s.get("stage") != "done":
                self._view(run["video"], run["quality"], stage=s.get("stage", ""), done=s.get("done", 0), total=s.get("total", 0))
                return
            out = self.store.vdir(run["video"]) / "out"
            out.mkdir(exist_ok=True)
            got = []
            for src, dst in OUT_NAMES[run["quality"]].items():
                if src in (s.get("files") or []):
                    await jup.download(f"wq3d/out/{src}", out / dst)
                    got.append(dst)
            if not got:
                self._end(run, "failed", "no_file", "机器上没有找到出好的视频")
                return
            self._view(run["video"], run["quality"], files=got, done=s.get("total", 0), total=s.get("total", 0))
            self._end(self.store.run(run["id"]) or run, "done", "done", "")
