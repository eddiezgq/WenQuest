"""Session tokens.

The browser never sees the Moodle token. It gets an encrypted, expiring
session token that carries the Moodle token inside; only the gateway can read it.
"""
from __future__ import annotations

import base64
import hashlib
import json
import time
from dataclasses import dataclass

from cryptography.fernet import Fernet, InvalidToken


@dataclass
class Session:
    moodle_token: str
    user_id: int
    lang: str


class SessionCodec:
    def __init__(self, secret: str, days: int):
        key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
        self.fernet = Fernet(key)
        self.ttl = days * 86400

    def issue(self, s: Session) -> str:
        body = json.dumps({"t": s.moodle_token, "u": s.user_id, "l": s.lang, "iat": int(time.time())})
        return self.fernet.encrypt(body.encode()).decode()

    def read(self, token: str) -> Session | None:
        try:
            raw = self.fernet.decrypt(token.encode(), ttl=self.ttl)
        except (InvalidToken, ValueError):
            return None
        d = json.loads(raw)
        return Session(moodle_token=d["t"], user_id=int(d["u"]), lang=d.get("l", "zh"))
