"""Outgoing email for sign-up codes, teacher approval and course notices.

Sends through the SMTP server in the settings (on DigitalOcean: a mail service's port 2525).
Without SMTP settings nothing is sent and the message is written to the log instead, so the
sign-up flow can still be tried locally.
"""
from __future__ import annotations

import asyncio
import html
import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr, make_msgid

log = logging.getLogger("wenquest.mail")


class Mailer:
    def __init__(self, host: str, port: int, secure: str, user: str, password: str, sender: str, sender_name: str):
        self.host, self.port, self.secure = host, port, (secure or "tls").lower()
        self.user, self.password = user, password
        self.sender, self.sender_name = sender, sender_name
        self.outbox: list[dict] = []  # the last messages, for tests and the local log

    @property
    def configured(self) -> bool:
        return bool(self.host and self.sender)

    async def send(self, to: str, subject: str, text: str, html_body: str | None = None) -> bool:
        self.outbox = (self.outbox + [{"to": to, "subject": subject, "text": text}])[-50:]
        if not self.configured:
            log.warning("[mail not configured] to %s: %s\n%s", to, subject, text)
            return True
        msg = EmailMessage()
        msg["From"] = formataddr((self.sender_name, self.sender))
        msg["To"] = to
        msg["Subject"] = subject
        msg["Message-ID"] = make_msgid(domain=self.sender.split("@")[-1])
        msg.set_content(text)
        msg.add_alternative(html_body or wrap_html(text), subtype="html")
        try:
            await asyncio.to_thread(self._send, msg)
            return True
        except (OSError, smtplib.SMTPException) as exc:
            log.error("mail to %s failed: %s", to, exc)
            return False

    def _send(self, msg: EmailMessage) -> None:
        ctx = ssl.create_default_context()
        if self.secure == "ssl":
            server: smtplib.SMTP = smtplib.SMTP_SSL(self.host, self.port, timeout=20, context=ctx)
        else:
            server = smtplib.SMTP(self.host, self.port, timeout=20)
        with server:
            if self.secure == "tls":
                server.starttls(context=ctx)
            if self.user:
                server.login(self.user, self.password)
            server.send_message(msg)


def wrap_html(text: str) -> str:
    """A plain, readable HTML version of a text email (links clickable, the code large)."""
    import re
    parts = []
    for para in text.strip().split("\n\n"):
        p = html.escape(para).replace("\n", "<br>")
        p = re.sub(r"(https?://[^\s<]+)", r'<a href="\1" style="color:#0b6e8a">\1</a>', p)
        if re.fullmatch(r"\d{6}", para.strip()):
            p = f'<span style="font-size:28px;font-weight:700;letter-spacing:6px;color:#0f2b3a">{p}</span>'
        parts.append(f'<p style="margin:0 0 14px">{p}</p>')
    return ('<div style="font-family:-apple-system,Segoe UI,PingFang SC,Microsoft YaHei,sans-serif;'
            'font-size:15px;line-height:1.7;color:#1d2b33;max-width:560px">'
            '<div style="font-weight:700;font-size:17px;color:#0f2b3a;margin-bottom:16px">问渠机器人学院 · WenQuest</div>'
            + "".join(parts) + '</div>')
