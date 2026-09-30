"""Voice service: synthesis in both languages, recognition of what was synthesised (needs the models: fetch_models.sh)."""
import base64
import io
import os
import wave

import numpy as np
import pytest
from fastapi.testclient import TestClient

import app as V

pytestmark = pytest.mark.skipif(not os.path.isdir(V.TTS_DIR), reason="models not downloaded (fetch_models.sh)")
c = TestClient(V.app)


def _to16k(wav: bytes) -> bytes:
    a, rate = V.read_wav(wav)
    n = int(len(a) * 16000 / rate)
    a = np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)
    silence = np.zeros(8000, dtype=np.float32)
    return V.wav_bytes(np.concatenate([silence, a, silence, a, silence]), 16000)


def test_voices_and_tts_both_languages():
    vs = c.get("/voices").json()["voices"]
    assert {v["lang"] for v in vs} == {"zh", "en"}
    zh = c.post("/tts", json={"text": "机械臂有6个关节。", "voice": "zf_xiaobei"}).json()
    en = c.post("/tts", json={"text": "This arm has six joints.", "voice": "af_heart", "speed": 1.1}).json()
    assert zh["ok"] and en["ok"] and 0.8 < zh["seconds"] < 6 and 0.8 < en["seconds"] < 6
    with wave.open(io.BytesIO(base64.b64decode(zh["audio"]))) as w:
        assert w.getframerate() == 24000 and w.getnchannels() == 1


def test_asr_finds_two_sentences_with_times():
    zh = base64.b64decode(c.post("/tts", json={"text": "这台机械臂有六个关节。", "voice": "zm_yunxi"}).json()["audio"])
    r = c.post("/asr", files={"file": ("a.wav", _to16k(zh), "audio/wav")}).json()
    assert r["ok"] and len(r["segments"]) == 2, r
    s0, s1 = r["segments"]
    assert "关节" in s0["text"] and 0.2 < s0["start"] < 0.8 and s0["end"] < s1["start"]


def test_bad_input():
    assert not c.post("/asr", files={"file": ("a.wav", b"nope", "audio/wav")}).json()["ok"]
    assert not c.post("/tts", json={"text": "   "}).json()["ok"]
