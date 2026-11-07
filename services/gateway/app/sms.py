"""Text messages through Alibaba Cloud SMS (阿里云短信服务, SendSms), round 108.

No SDK: one signed GET (RPC signature version 1.0, HMAC-SHA1) with the httpx client the gateway already has.
Without settings nothing is sent and the message is written to the log, so the flows can be tried locally.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import uuid
from datetime import datetime, timezone
from urllib.parse import quote

import httpx

log = logging.getLogger("wenquest.sms")


def pct(s: str) -> str:
    """Alibaba Cloud's percent-encoding (RFC 3986: only A-Z a-z 0-9 - _ . ~ stay)."""
    return quote(str(s), safe="-_.~")


def signature(params: dict[str, str], secret: str, method: str = "GET") -> str:
    canon = "&".join(f"{pct(k)}={pct(v)}" for k, v in sorted(params.items()))
    to_sign = f"{method}&{pct('/')}&{pct(canon)}"
    mac = hmac.new((secret + "&").encode(), to_sign.encode(), hashlib.sha1).digest()
    return base64.b64encode(mac).decode()


class Sms:
    def __init__(self, key_id: str, secret: str, sign: str, template: str, endpoint: str, http: httpx.AsyncClient | None):
        self.key_id, self.secret, self.sign, self.template = key_id, secret, sign, template
        self.endpoint, self.http = endpoint, http
        self.outbox: list[dict] = []   # the last messages, for tests and the local log

    @property
    def configured(self) -> bool:
        return bool(self.key_id and self.secret and self.sign and self.template)

    def params(self, phone: str, code: str, now: datetime | None = None, nonce: str | None = None) -> dict[str, str]:
        p = {
            "AccessKeyId": self.key_id, "Action": "SendSms", "Format": "JSON", "PhoneNumbers": phone,
            "RegionId": "cn-hangzhou", "SignName": self.sign, "SignatureMethod": "HMAC-SHA1",
            "SignatureNonce": nonce or uuid.uuid4().hex, "SignatureVersion": "1.0", "TemplateCode": self.template,
            "TemplateParam": json.dumps({"code": code}),
            "Timestamp": (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ"), "Version": "2017-05-25",
        }
        p["Signature"] = signature(p, self.secret)
        return p

    async def send_code(self, phone: str, code: str) -> bool:
        self.outbox = (self.outbox + [{"to": phone, "code": code}])[-50:]
        if not self.configured:
            log.warning("[sms not configured] to %s: code %s", phone, code)
            return True
        try:
            assert self.http is not None
            r = await self.http.get(self.endpoint, params=self.params(phone, code), timeout=15)
            body = r.json()
        except (httpx.HTTPError, ValueError, AssertionError) as exc:
            log.error("sms to %s failed: %s", phone, exc)
            return False
        if body.get("Code") != "OK":
            log.error("sms to %s refused: %s %s", phone, body.get("Code"), body.get("Message"))
            return False
        return True
