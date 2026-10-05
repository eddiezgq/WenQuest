"""Synthesize every narration sentence with the local Kokoro model (sherpa-onnx) → <work>/tts/sNN_MM.wav + durations.json.
Usage: python3 tts.py <work dir>   (skips sentences already synthesized with the same text)"""
import json, os, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.environ.get("VOICE_MODELS", "/home/claude/local/voice-models")
work = sys.argv[1]
os.makedirs(f"{work}/tts", exist_ok=True)
N = json.load(open(f"{HERE}/narration.json", encoding="utf-8"))
dur_path = f"{work}/tts/durations.json"
done = json.load(open(dur_path)) if os.path.exists(dur_path) else {}
_t = None
def engine():
    global _t
    if _t is None:
        import sherpa_onnx as so
        d = f"{MODELS}/kokoro-int8-multi-lang-v1_0/"
        cfg = so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(kokoro=so.OfflineTtsKokoroModelConfig(
            model=d + "model.int8.onnx", voices=d + "voices.bin", tokens=d + "tokens.txt", data_dir=d + "espeak-ng-data",
            dict_dir=d + "dict", lexicon=d + "lexicon-us-en.txt," + d + "lexicon-zh.txt"), num_threads=os.cpu_count() or 2),
            rule_fsts=d + "date-zh.fst," + d + "number-zh.fst," + d + "phone-zh.fst", max_num_sentences=1)
        _t = so.OfflineTts(cfg)
    return _t
for seg in N["segments"]:
    for j, s in enumerate(seg["sentences"]):
        key = f"s{seg['id']:02d}_{j:02d}"
        say = s.get("say", s["text"])
        if key in done and done[key]["say"] == say and done[key].get("speed") == N["speed"] and done[key].get("sid") == N["voice_sid"] and os.path.exists(f"{work}/tts/{key}.wav"):
            continue
        a = engine().generate(say, sid=N["voice_sid"], speed=N["speed"])
        x = np.array(a.samples, dtype=np.float32)
        # trim leading/trailing near-silence
        idx = np.where(np.abs(x) > 0.006)[0]
        if len(idx):
            x = x[max(0, idx[0] - int(0.06 * a.sample_rate)): idx[-1] + int(0.10 * a.sample_rate)]
        with wave.open(f"{work}/tts/{key}.wav", "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(a.sample_rate)
            w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
        done[key] = {"say": say, "speed": N["speed"], "sid": N["voice_sid"], "seconds": len(x) / a.sample_rate, "rate": a.sample_rate}
        json.dump(done, open(dur_path, "w"), ensure_ascii=False, indent=1)
        print(key, round(done[key]["seconds"], 2), flush=True)
