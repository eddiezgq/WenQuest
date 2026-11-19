"""问渠软件授权码检查（第 175 轮，测试版）：软件端用，不依赖任何第三方库（FreeCAD 自带的 Python 就能跑）。

授权码 WQ1.<内容>.<签名> 由学习平台发（services/gateway/app/license.py），Ed25519 签名；这里内置美国、国内两把公钥，两边发的都认。
用法：
    import wq_license
    st = wq_license.status()          # {"ok": bool, "reason": ..., "exp": ..., "days_left": ...}
    wq_license.save(token)            # 用户粘贴的授权码存到本机
放在：%APPDATA%\\WenQuest\\license.txt（Windows），~/.config/WenQuest/license.txt（其他）。
版本检查：check_update(product, current) 读下载中心的 versions.json（3 秒超时，没网就跳过）。
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import time
from pathlib import Path

# 美国、国内学习平台的公钥（GET /api/v1/license/public-key）。换了服务器的 WQ_SECRET_KEY 要更新这里。
KEYS = {
    "us": "FoaROOa3yuG2wbCh1gZj1ufQ69PgNDb_qCkBLMWohCs",
    "cn": "",
}
DOWNLOAD = {"us": "https://wenquestrobotics.com/download/", "cn": "https://wenquestech.online/download/"}

# ---------------- Ed25519 验签（RFC 8032 的参考算法，纯 Python）
_q = 2 ** 255 - 19
_l = 2 ** 252 + 27742317777372353535851937790883648493
_d = -121665 * pow(121666, _q - 2, _q) % _q
_I = pow(2, (_q - 1) // 4, _q)


def _xrecover(y):
    xx = (y * y - 1) * pow(_d * y * y + 1, _q - 2, _q)
    x = pow(xx, (_q + 3) // 8, _q)
    if (x * x - xx) % _q != 0:
        x = (x * _I) % _q
    if x % 2 != 0:
        x = _q - x
    return x


_By = 4 * pow(5, _q - 2, _q) % _q
_B = (_xrecover(_By) % _q, _By % _q, 1, _xrecover(_By) * _By % _q)


def _add(P, Q):
    A = (P[1] - P[0]) * (Q[1] - Q[0]) % _q
    B = (P[1] + P[0]) * (Q[1] + Q[0]) % _q
    C = 2 * P[3] * Q[3] * _d % _q
    D = 2 * P[2] * Q[2] % _q
    E, F, G, H = B - A, D - C, D + C, B + A
    return (E * F % _q, G * H % _q, F * G % _q, E * H % _q)


def _mul(s, P):
    Q = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            Q = _add(Q, P)
        P = _add(P, P)
        s >>= 1
    return Q


def _eq(P, Q):
    return (P[0] * Q[2] - Q[0] * P[2]) % _q == 0 and (P[1] * Q[2] - Q[1] * P[2]) % _q == 0


def _decode(b):
    y = int.from_bytes(b, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    if y >= _q:
        return None
    x = _xrecover(y)
    if (x * x * _d * y * y + 1 - y * y - x * x) % _q != 0 and (-x * x + y * y - 1 - _d * x * x * y * y) % _q != 0:
        return None
    if (x & 1) != sign:
        x = _q - x
    return (x, y, 1, x * y % _q)


def verify(pub: bytes, msg: bytes, sig: bytes) -> bool:
    if len(pub) != 32 or len(sig) != 64:
        return False
    A, R = _decode(pub), _decode(sig[:32])
    if A is None or R is None:
        return False
    s = int.from_bytes(sig[32:], "little")
    if s >= _l:
        return False
    h = int.from_bytes(hashlib.sha512(sig[:32] + pub + msg).digest(), "little") % _l
    return _eq(_mul(s, _B), _add(R, _mul(h, A)))


# ---------------- 授权码
def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def check(token: str, keys: dict | None = None, now: float | None = None) -> dict:
    keys = KEYS if keys is None else keys
    token = (token or "").strip()
    parts = token.split(".")
    if len(parts) != 3 or parts[0] != "WQ1":
        return {"ok": False, "reason": "format"}
    try:
        body = json.loads(_unb64(parts[1]))
        sig = _unb64(parts[2])
    except Exception:  # noqa: BLE001
        return {"ok": False, "reason": "format"}
    key = keys.get(body.get("r", ""))
    if not key or not verify(_unb64(key), (parts[0] + "." + parts[1]).encode(), sig):
        return {"ok": False, "reason": "signature"}
    now = time.time() if now is None else now
    left = (body["exp"] - now) / 86400
    out = {"ok": left > 0, "reason": "ok" if left > 0 else "expired", "exp": body["exp"], "days_left": int(left) if left > 0 else 0,
           "region": body["r"], "user": body["u"]}
    return out


def path() -> Path:
    base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".config")
    return Path(base) / "WenQuest" / "license.txt"


def save(token: str) -> dict:
    st = check(token)
    if st["ok"]:
        p = path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(token.strip(), encoding="ascii")
    return st


def status() -> dict:
    p = path()
    if not p.exists():
        return {"ok": False, "reason": "missing"}
    return check(p.read_text(encoding="ascii", errors="ignore"))


def check_update(product: str, current: str, region: str = "us", timeout: float = 3.0) -> dict | None:
    """下载中心 versions.json：{"产品": {"version": "...", "url": "...", "notes": "..."}}；有新版返回那一项，否则 None"""
    import urllib.request
    try:
        with urllib.request.urlopen(DOWNLOAD.get(region, DOWNLOAD["us"]) + "versions.json", timeout=timeout) as r:
            v = json.loads(r.read().decode("utf-8")).get(product)
    except Exception:  # noqa: BLE001 —— 没网、超时：不提示
        return None
    if not v:
        return None

    def key(s):
        return [int(x) if x.isdigit() else x for x in str(s).replace("-", ".").split(".")]
    try:
        return v if key(v["version"]) > key(current) else None
    except TypeError:
        return v if str(v["version"]) != str(current) else None
