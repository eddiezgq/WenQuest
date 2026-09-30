"""WenQuest voice service (round 4, step 5): speech synthesis and speech recognition, on this server.

Open-source models run locally (no cloud service, no key, nothing leaves the server):
  - speech synthesis: Kokoro-82M v1.0 (Apache-2.0), int8, through sherpa-onnx (Apache-2.0) — Chinese and English voices;
  - speech recognition: SenseVoice-Small (FunASR model licence) with the Silero VAD (MIT) to cut long recordings into
    sentences with start and end times.

GET  /voices                       the voices [{id, lang, gender, zh, en}]
POST /tts   {text, voice, speed}   one sentence or a short paragraph → {ok, audio (WAV base64, 24 kHz mono), seconds}
POST /asr   (multipart: file = 16 kHz mono 16-bit WAV)  → {ok, segments: [{start, end, text}], seconds}

One synthesis and one recognition run at a time (CPU bound). Models are baked into the image (see Dockerfile) under
VOICE_MODELS (default /models).
"""
from __future__ import annotations

import asyncio
import base64
import io
import os
import time
import wave

import numpy as np
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel, Field

MODELS = os.environ.get("VOICE_MODELS", "/models")
THREADS = int(os.environ.get("VOICE_THREADS", "2"))
TTS_DIR = f"{MODELS}/kokoro-int8-multi-lang-v1_0/"
ASR_DIR = f"{MODELS}/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09/"
VAD = f"{MODELS}/silero_vad.onnx"

# Kokoro v1.0 speaker ids (order of voices.bin). Only the Chinese and English voices are offered.
VOICES = [
    {"id": "zf_xiaobei", "sid": 45, "lang": "zh", "gender": "f", "zh": "晓贝（女）", "en": "Xiaobei (female)"},
    {"id": "zf_xiaoni", "sid": 46, "lang": "zh", "gender": "f", "zh": "晓妮（女）", "en": "Xiaoni (female)"},
    {"id": "zf_xiaoxiao", "sid": 47, "lang": "zh", "gender": "f", "zh": "晓晓（女）", "en": "Xiaoxiao (female)"},
    {"id": "zf_xiaoyi", "sid": 48, "lang": "zh", "gender": "f", "zh": "晓伊（女）", "en": "Xiaoyi (female)"},
    {"id": "zm_yunjian", "sid": 49, "lang": "zh", "gender": "m", "zh": "云健（男）", "en": "Yunjian (male)"},
    {"id": "zm_yunxi", "sid": 50, "lang": "zh", "gender": "m", "zh": "云希（男）", "en": "Yunxi (male)"},
    {"id": "zm_yunxia", "sid": 51, "lang": "zh", "gender": "m", "zh": "云夏（男）", "en": "Yunxia (male)"},
    {"id": "zm_yunyang", "sid": 52, "lang": "zh", "gender": "m", "zh": "云扬（男）", "en": "Yunyang (male)"},
    {"id": "af_heart", "sid": 3, "lang": "en", "gender": "f", "zh": "Heart（美式女声）", "en": "Heart (US female)"},
    {"id": "af_bella", "sid": 2, "lang": "en", "gender": "f", "zh": "Bella（美式女声）", "en": "Bella (US female)"},
    {"id": "af_nicole", "sid": 6, "lang": "en", "gender": "f", "zh": "Nicole（美式女声）", "en": "Nicole (US female)"},
    {"id": "am_michael", "sid": 16, "lang": "en", "gender": "m", "zh": "Michael（美式男声）", "en": "Michael (US male)"},
    {"id": "am_fenrir", "sid": 14, "lang": "en", "gender": "m", "zh": "Fenrir（美式男声）", "en": "Fenrir (US male)"},
    {"id": "am_puck", "sid": 18, "lang": "en", "gender": "m", "zh": "Puck（美式男声）", "en": "Puck (US male)"},
    {"id": "bf_emma", "sid": 21, "lang": "en", "gender": "f", "zh": "Emma（英式女声）", "en": "Emma (UK female)"},
    {"id": "bm_george", "sid": 26, "lang": "en", "gender": "m", "zh": "George（英式男声）", "en": "George (UK male)"},
]
BY_ID = {v["id"]: v for v in VOICES}

app = FastAPI(title="WenQuest voice")
TTS_LOCK = asyncio.Lock()
ASR_LOCK = asyncio.Lock()
_tts = None
_asr = None


def tts_engine():
    global _tts
    if _tts is None:
        import sherpa_onnx as so
        d = TTS_DIR
        cfg = so.OfflineTtsConfig(
            model=so.OfflineTtsModelConfig(
                kokoro=so.OfflineTtsKokoroModelConfig(
                    model=d + "model.int8.onnx", voices=d + "voices.bin", tokens=d + "tokens.txt",
                    data_dir=d + "espeak-ng-data", dict_dir=d + "dict",
                    lexicon=d + "lexicon-us-en.txt," + d + "lexicon-zh.txt"),
                num_threads=THREADS),
            rule_fsts=d + "date-zh.fst," + d + "number-zh.fst," + d + "phone-zh.fst",
            max_num_sentences=1)
        _tts = so.OfflineTts(cfg)
    return _tts


def asr_engine():
    global _asr
    if _asr is None:
        import sherpa_onnx as so
        rec = so.OfflineRecognizer.from_sense_voice(model=ASR_DIR + "model.int8.onnx", tokens=ASR_DIR + "tokens.txt",
                                                    use_itn=True, num_threads=THREADS, language="auto")
        vc = so.VadModelConfig()
        vc.silero_vad.model = VAD
        vc.silero_vad.min_silence_duration = 0.35
        vc.silero_vad.min_speech_duration = 0.25
        vc.silero_vad.max_speech_duration = 12.0
        vc.sample_rate = 16000
        _asr = (rec, vc)
    return _asr


def wav_bytes(samples: np.ndarray, rate: int) -> bytes:
    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2")
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
    return b.getvalue()


def read_wav(data: bytes) -> tuple[np.ndarray, int]:
    with wave.open(io.BytesIO(data)) as w:
        if w.getsampwidth() != 2:
            raise ValueError("need 16-bit PCM WAV")
        ch, rate = w.getnchannels(), w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    return a, rate


@app.get("/health")
def health():
    return {"ok": True, "models": os.path.isdir(TTS_DIR) and os.path.isdir(ASR_DIR)}


@app.get("/voices")
def voices():
    return {"voices": [{k: v[k] for k in ("id", "lang", "gender", "zh", "en")} for v in VOICES]}


class TtsIn(BaseModel):
    text: str = Field(..., max_length=2000)
    voice: str = "zf_xiaobei"
    speed: float = Field(1.0, ge=0.6, le=1.6)


def synth(text: str, voice: str, speed: float) -> tuple[bytes, float]:
    v = BY_ID.get(voice) or VOICES[0]
    a = tts_engine().generate(text, sid=v["sid"], speed=speed)
    samples = np.asarray(a.samples, dtype=np.float32)
    # trim leading/trailing near-silence so sentences join tightly; the caller adds its own pauses
    loud = np.nonzero(np.abs(samples) > 0.01)[0]
    if len(loud):
        pad = int(0.05 * a.sample_rate)
        samples = samples[max(0, loud[0] - pad): loud[-1] + pad]
    return wav_bytes(samples, a.sample_rate), len(samples) / a.sample_rate


@app.post("/tts")
async def tts(body: TtsIn):
    text = " ".join(body.text.split())
    if not text:
        return {"ok": False, "error": "empty text"}
    t = time.time()
    async with TTS_LOCK:
        try:
            audio, secs = await asyncio.to_thread(synth, text, body.voice, body.speed)
        except Exception as e:  # noqa: BLE001 - reported to the caller
            return {"ok": False, "error": f"{type(e).__name__}: {e}"[:500]}
    return {"ok": True, "audio": base64.b64encode(audio).decode(), "seconds": round(secs, 3), "took": round(time.time() - t, 2)}


def recognise(samples: np.ndarray, rate: int) -> list[dict]:
    import sherpa_onnx as so
    rec, vc = asr_engine()
    if rate != 16000:   # simple linear resample (the gateway already sends 16 kHz)
        n = int(len(samples) * 16000 / rate)
        samples = np.interp(np.linspace(0, len(samples) - 1, n), np.arange(len(samples)), samples).astype(np.float32)
    vad = so.VoiceActivityDetector(vc, buffer_size_in_seconds=60)
    win = vc.silero_vad.window_size
    out = []

    def drain():
        while not vad.empty():
            seg = vad.front
            s = rec.create_stream()
            s.accept_waveform(16000, np.asarray(seg.samples, dtype=np.float32))
            rec.decode_stream(s)
            text = s.result.text.strip()
            if text:
                start = seg.start / 16000
                out.append({"start": round(start, 2), "end": round(start + len(seg.samples) / 16000, 2), "text": text})
            vad.pop()

    for i in range(0, len(samples), win):
        vad.accept_waveform(samples[i:i + win])
        drain()
    vad.flush()
    drain()
    return out


@app.post("/asr")
async def asr(file: UploadFile = File(...)):
    t = time.time()
    try:
        samples, rate = read_wav(await file.read())
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"not a 16-bit WAV: {e}"[:300]}
    async with ASR_LOCK:
        try:
            segs = await asyncio.to_thread(recognise, samples, rate)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": f"{type(e).__name__}: {e}"[:500]}
    return {"ok": True, "segments": segs, "seconds": round(len(samples) / rate, 2), "took": round(time.time() - t, 2)}
