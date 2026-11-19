"""问渠软件测试版授权（第 175 轮）：注册用户登录后自己申请，自动发一年授权码，问渠所有可下载的软件共用。

  POST /api/v1/license/beta        已登录：发授权码（已有且没过期的就原样再给一次，不会一次次往后延）
  GET  /api/v1/license/me          已登录：我的授权码、到期日
  GET  /api/v1/license/public-key  本站的公钥（软件里内置美国、国内两把，两边发的码都认）

授权码：WQ1.<内容>.<签名>，内容是 JSON（v 版本、u 账号号、r 地区、p 产品、iat 发码时间、exp 到期时间），Ed25519 签名。
私钥由本站的 WQ_SECRET_KEY 推出来（不另存密钥）：美国、国内各一把；软件里两把公钥都内置。改了 WQ_SECRET_KEY，旧码失效。
数据：<data_dir>/license.db（SQLite），记谁在什么时候领了码。
"""

import base64
import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Annotated

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from fastapi import Depends

from .session import Session

DAYS = 365
PRODUCT = "beta"


def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def unb64u(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def private_key(secret: str) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"wq-license-v1|" + secret.encode()).digest())


def public_key_b64(secret: str) -> str:
    return b64u(private_key(secret).public_key().public_bytes(Encoding.Raw, PublicFormat.Raw))


def issue(secret: str, uid: int, region: str, now: int | None = None, days: int = DAYS) -> str:
    now = int(now if now is not None else time.time())
    body = json.dumps({"v": 1, "u": uid, "r": region, "p": PRODUCT, "iat": now, "exp": now + days * 86400},
                      separators=(",", ":"), sort_keys=True).encode()
    head = "WQ1." + b64u(body)
    return head + "." + b64u(private_key(secret).sign(head.encode()))


def read(token: str) -> dict:
    """不验签，只读出内容（服务端列表、显示用）"""
    return json.loads(unb64u(token.split(".")[1]))


def register(app, m) -> None:
    state = m.state

    def db() -> sqlite3.Connection:
        d = Path(state.settings.data_dir)
        d.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(d / "license.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("create table if not exists issued(user_id integer primary key, token text, iat integer, exp integer)")
        return c

    def mine(uid: int) -> dict | None:
        with db() as c:
            r = c.execute("select * from issued where user_id=?", (uid,)).fetchone()
        return dict(r) if r else None

    @app.get("/api/v1/license/public-key")
    async def public_key():
        return {"region": state.settings.region, "key": public_key_b64(state.settings.secret_key), "alg": "Ed25519", "format": "WQ1"}

    @app.get("/api/v1/license/me")
    async def me(sess: Annotated[Session, Depends(m.current)]):
        r = mine(sess.user_id)
        if not r:
            return {"token": None}
        return {"token": r["token"], "exp": r["exp"], "expired": r["exp"] < time.time()}

    @app.post("/api/v1/license/beta")
    async def beta(sess: Annotated[Session, Depends(m.current)]):
        r = mine(sess.user_id)
        now = int(time.time())
        if r and r["exp"] > now:
            return {"token": r["token"], "exp": r["exp"], "new": False}
        tok = issue(state.settings.secret_key, sess.user_id, state.settings.region, now)
        with db() as c:
            c.execute("insert or replace into issued(user_id, token, iat, exp) values(?,?,?,?)", (sess.user_id, tok, now, now + DAYS * 86400))
        return {"token": tok, "exp": now + DAYS * 86400, "new": True}
