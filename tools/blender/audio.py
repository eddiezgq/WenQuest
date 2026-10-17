"""三维视频的声音（第 37 轮震撼版）：配音（平台本地 AI 声音 Kokoro，中文 zm_yunjian）+ 合成音效（低频铺底、高速段马达声、
冻结时的“嗖—咚”、片尾收音），混成场景目录里的 audio.m4a（小文件，进仓库；出片时 render.py 自动配上）。
    python3 tools/blender/audio.py <场景目录> <kokoro 模型目录>
场景文件里：voice: [{t, zh, en, dur}]；effects 里的 blur 段当作“高速”，flash 处加“嗖—咚”。"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import yaml

DIR = Path(sys.argv[1]).resolve()
SPEC = yaml.safe_load((DIR / "scene.yaml").read_text(encoding="utf-8"))
SR = 24000
T = float(SPEC["duration"])
n = int(T * SR)
t = np.arange(n) / SR
mix = np.zeros(n, np.float32)
rng = np.random.default_rng(7)


def env(a, b, fade=0.2):
    e = np.clip((t - a) / fade, 0, 1) * np.clip((b - t) / fade, 0, 1)
    return e * ((t >= a) & (t < b))


# 铺底：两个低音轻轻起伏，片尾升一点
pad = 0.05 * (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.4 * t) + 0.3 * np.sin(2 * np.pi * 110 * t))
pad *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * t) ** 2
mix += (pad * np.clip(t / 1.5, 0, 1) * np.clip((T - t) / 1.5, 0, 1)).astype(np.float32)
fx = SPEC.get("effects", [])
for e in fx:
    a, b = e["t"]
    if e["kind"] == "blur":            # 高速：马达嗡嗡声（基频随转速，带针击的节拍）
        buzz = np.sign(np.sin(2 * np.pi * 83 * t)) * 0.5 + np.sin(2 * np.pi * 166 * t) * 0.3
        tick = (np.sin(2 * np.pi * 20 * t) > 0.97).astype(np.float32) * rng.normal(0, 1, n)
        mix += (0.10 * buzz + 0.06 * tick) * env(a, b, 0.3)
    if e["kind"] == "flash":           # 嗖（噪声扫频）+ 咚（低频衰减）
        w = (t >= a - 0.6) & (t < a)
        u = (t[w] - (a - 0.6)) / 0.6
        mix[w] += 0.25 * rng.normal(0, 1, w.sum()) * u ** 2 * np.convolve(np.ones(1), [1], "same")[0]
        h = t >= a
        mix[h] += (0.6 * np.sin(2 * np.pi * 48 * (t[h] - a)) * np.exp(-(t[h] - a) * 5)).astype(np.float32)
# 配音
import sherpa_onnx as so  # noqa: E402
from importlib import util as _u  # noqa: E402
spec = _u.spec_from_file_location("speech", Path(__file__).resolve().parents[2] / "services/gateway/app/production/whiteboard/speech.py")
speech = _u.module_from_spec(spec)
spec.loader.exec_module(speech)
m = sys.argv[2].rstrip("/") + "/"
tts = so.OfflineTts(so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(kokoro=so.OfflineTtsKokoroModelConfig(
    model=m + "model.int8.onnx", voices=m + "voices.bin", tokens=m + "tokens.txt", data_dir=m + "espeak-ng-data", dict_dir=m + "dict",
    lexicon=m + "lexicon-us-en.txt," + m + "lexicon-zh.txt"), num_threads=2),
    rule_fsts=m + "date-zh.fst," + m + "number-zh.fst," + m + "phone-zh.fst", max_num_sentences=1))
for v in SPEC.get("voice", []):
    a = tts.generate(speech.speakable(v.get("say", v["zh"])), sid=int(v.get("sid", 49)), speed=float(v.get("speed", 1.1)))
    x = np.array(a.samples, np.float32)
    if a.sample_rate != SR:
        x = np.interp(np.arange(0, len(x), a.sample_rate / SR), np.arange(len(x)), x).astype(np.float32)
    i = int(v["t"] * SR)
    x = x[: max(0, n - i)]
    mix[i:i + len(x)] += 0.9 * x
    print(f"{v['t']:5.1f}s  {len(x) / SR:4.1f}s  {v['zh']}")
mix /= max(1e-6, np.abs(mix).max()) / 0.9
wav = DIR / "_audio.wav"
sf.write(wav, mix, SR)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-c:a", "aac", "-b:a", "128k", str(DIR / "audio.m4a")], check=True)
print("→", DIR / "audio.m4a")
