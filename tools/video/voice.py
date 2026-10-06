"""配音（第 22 轮）：把讲稿的每一句合成为 WAV（24 kHz 单声道），按 “声音 + 语速 + 文字” 缓存，改一句只重合成这一句。

后端：
  estimate  不发声，按字数估计时长（中文每秒 4.3 字，英文每秒 2.55 词），用于排版、试渲染；
  kokoro    服务器上已有的开源 Kokoro（sherpa-onnx，离线），模型目录 $WQ_TTS_MODELS（同 services/voice）；
  clone     Eddie 本人声音克隆（tools/video/clone.py，在 GPU 机器上运行），按句读入它生成的 WAV。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import wave
from pathlib import Path

import numpy as np

RATE = 24000
KOKORO = {"zh": ("zm_yunyang", 52), "en": ("am_michael", 16)}   # 样片的占位声音；定稿用 clone


def zh_numbers(s: str) -> str:
    """Spoken form for Chinese TTS: 0.94 → 零点九四, 2000 → 两千, 147° → 147 度, −0.8 → 负零点八."""
    digits = "零一二三四五六七八九"

    def int_cn(n: int) -> str:
        if n == 0:
            return "零"
        units = ["", "十", "百", "千"]
        out, s4 = [], []
        big = ["", "万", "亿"]
        parts = []
        k = 0
        while n:
            parts.append((n % 10000, big[k]))
            n //= 10000
            k += 1
        res = ""
        for idx, (p, b) in enumerate(reversed(parts)):
            if p == 0:
                if res and not res.endswith("零"):
                    res += "零"
                continue
            seg = ""
            ds = f"{p:04d}" if idx else str(p)
            zero = False
            for i, ch in enumerate(ds):
                d = int(ch)
                u = units[len(ds) - 1 - i]
                if d == 0:
                    zero = bool(seg)
                    continue
                if zero:
                    seg += "零"
                    zero = False
                seg += digits[d] + u
            res += seg + b
        res = res.rstrip("零")
        if res.startswith("一十"):
            res = res[1:]
        res = re.sub(r"(^|零)二(千|百|万|亿)", lambda m: m.group(1) + "两" + m.group(2), res)
        return res

    def num(m):
        sign, ip, fp = m.group(1), m.group(2), m.group(3)
        t = ("负" if sign else "") + int_cn(int(ip))
        if fp:
            t += "点" + "".join(digits[int(c)] for c in fp)
        return t

    s = s.replace("°", " 度").replace("×", "乘").replace("≈", "约等于")
    return re.sub(r"([−-])?(\d+)(?:\.(\d+))?", num, s)


def en_spoken(s: str) -> str:
    s = s.replace("°", " degrees").replace("−", "minus ").replace("×", " times ")
    return s


def estimate_seconds(text: str, lang: str) -> float:
    if lang == "zh":
        n = len(re.sub(r"[\s，。、；：？！“”（）,.;:?!]", "", text))
        return max(0.8, n / 4.3)
    return max(0.8, len(text.split()) / 2.55)


def _wav_write(path: Path, a: np.ndarray, rate: int = RATE):
    pcm = (np.clip(a, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())


def wav_read(path: Path) -> np.ndarray:
    with wave.open(str(path)) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
        rate, ch = w.getframerate(), w.getnchannels()
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    if rate != RATE:
        x = np.linspace(0, len(a) - 1, int(len(a) * RATE / rate))
        a = np.interp(x, np.arange(len(a)), a).astype(np.float32)
    return a


def _trim(a: np.ndarray) -> np.ndarray:
    loud = np.nonzero(np.abs(a) > 0.01)[0]
    if not len(loud):
        return a
    lo, hi = max(0, loud[0] - int(0.03 * RATE)), min(len(a), loud[-1] + int(0.08 * RATE))
    return a[lo:hi]


class Voice:
    def __init__(self, backend: str, lang: str, cache: Path, speed: float = 1.0):
        self.backend, self.lang, self.speed = backend, lang, speed
        self.cache = cache / backend / lang
        self.cache.mkdir(parents=True, exist_ok=True)
        self._tts = None

    def spoken(self, text: str) -> str:
        return zh_numbers(text) if self.lang == "zh" else en_spoken(text)

    def key(self, text: str) -> str:
        who = {"kokoro": KOKORO[self.lang][0], "clone": os.environ.get("WQ_CLONE_ID", "eddie")}.get(self.backend, "")
        return hashlib.sha1(f"{self.backend}|{who}|{self.speed}|{text}".encode()).hexdigest()[:16]

    def kokoro(self):
        if self._tts is None:
            import sherpa_onnx as so
            d = os.environ.get("WQ_TTS_MODELS", "/models").rstrip("/") + "/kokoro-int8-multi-lang-v1_0/"
            cfg = so.OfflineTtsConfig(
                model=so.OfflineTtsModelConfig(
                    kokoro=so.OfflineTtsKokoroModelConfig(
                        model=d + "model.int8.onnx", voices=d + "voices.bin", tokens=d + "tokens.txt",
                        data_dir=d + "espeak-ng-data", dict_dir=d + "dict",
                        lexicon=d + "lexicon-us-en.txt," + d + "lexicon-zh.txt"),
                    num_threads=int(os.environ.get("WQ_TTS_THREADS", "2"))),
                rule_fsts=d + "date-zh.fst," + d + "number-zh.fst," + d + "phone-zh.fst", max_num_sentences=1)
            self._tts = so.OfflineTts(cfg)
        return self._tts

    def say(self, text: str) -> tuple[Path, float]:
        """WAV path and seconds for one sentence (spoken form already applied by the caller)."""
        p = self.cache / f"{self.key(text)}.wav"
        if not p.exists():
            if self.backend == "estimate":
                a = np.zeros(int(estimate_seconds(text, self.lang) * RATE), np.float32)
            elif self.backend == "kokoro":
                g = self.kokoro().generate(text.replace("“", "").replace("”", ""), sid=KOKORO[self.lang][1], speed=self.speed)
                a = _trim(np.asarray(g.samples, np.float32))
                if g.sample_rate != RATE:
                    x = np.linspace(0, len(a) - 1, int(len(a) * RATE / g.sample_rate))
                    a = np.interp(x, np.arange(len(a)), a).astype(np.float32)
            elif self.backend == "clone":
                src = Path(os.environ["WQ_CLONE_DIR"]) / self.lang / f"{self.key(text)}.wav"
                if not src.exists():
                    raise FileNotFoundError(f"克隆配音缺这一句（先在 GPU 机器上运行 clone.py）：{text[:30]}")
                a = _trim(wav_read(src))
            else:
                raise ValueError(f"unknown voice backend {self.backend}")
            _wav_write(p, a)
        with wave.open(str(p)) as w:
            return p, w.getnframes() / w.getframerate()


def clone_jobs(lec, lang: str, cache: Path) -> list[dict]:
    """The sentences clone.py has to speak: [{key, text}] (keys match Voice('clone').key)."""
    v = Voice("clone", lang, cache)
    return [{"key": v.key(v.spoken(ln.spoken)), "text": v.spoken(ln.spoken)}
            for s in lec.shots for ln in s.lines[lang]]


if __name__ == "__main__":
    for t in ["0.94 毫米", "2000 和 1000", "5764 和 24097", "−0.8", "147°", "10 牛", "37° 左右", "3 公斤", "0.4 米", "105"]:
        print(t, "→", zh_numbers(t))
