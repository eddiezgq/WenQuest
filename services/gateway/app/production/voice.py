"""Client of the voice service (services/voice): speech synthesis and recognition on our own server."""
from __future__ import annotations

import base64
from pathlib import Path

import httpx


class VoiceError(Exception):
    def __init__(self, message: str, stage: str = "voice"):
        super().__init__(message)
        self.stage = stage


async def voices(url: str) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=20, trust_env=False) as c:
            r = await c.get(url.rstrip("/") + "/voices")
    except httpx.HTTPError as e:
        raise VoiceError(f"voice service unreachable: {type(e).__name__}", "service") from e
    if r.status_code != 200:
        raise VoiceError(f"voice service answered {r.status_code}", "service")
    return r.json().get("voices") or []


async def tts(url: str, text: str, voice: str, speed: float = 1.0, timeout: float = 300.0) -> tuple[bytes, float]:
    """(WAV bytes, seconds) for one sentence."""
    try:
        async with httpx.AsyncClient(timeout=timeout, trust_env=False) as c:
            r = await c.post(url.rstrip("/") + "/tts", json={"text": text, "voice": voice, "speed": speed})
    except httpx.HTTPError as e:
        raise VoiceError(f"voice service unreachable: {type(e).__name__}", "service") from e
    if r.status_code != 200:
        raise VoiceError(f"voice service answered {r.status_code}", "service")
    d = r.json()
    if not d.get("ok"):
        raise VoiceError(str(d.get("error") or "synthesis failed")[:300], "tts")
    return base64.b64decode(d["audio"]), float(d["seconds"])


async def asr(url: str, wav: Path, timeout: float = 3600.0) -> list[dict]:
    """[{start, end, text}] for a 16 kHz mono WAV."""
    try:
        async with httpx.AsyncClient(timeout=timeout, trust_env=False) as c:
            with wav.open("rb") as f:
                r = await c.post(url.rstrip("/") + "/asr", files={"file": ("audio.wav", f, "audio/wav")})
    except httpx.HTTPError as e:
        raise VoiceError(f"voice service unreachable: {type(e).__name__}", "service") from e
    if r.status_code != 200:
        raise VoiceError(f"voice service answered {r.status_code}", "service")
    d = r.json()
    if not d.get("ok"):
        raise VoiceError(str(d.get("error") or "recognition failed")[:300], "asr")
    return d.get("segments") or []
