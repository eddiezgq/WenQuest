"""AI 样片：讲稿和画板是 AI 按 whiteboard/ai.py 的提示写出的（script.json、boards.json），程序检查修正、配音、编译。"""
import json, sys
from pathlib import Path
import numpy as np, soundfile as sf
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "services" / "gateway"))
from app.production.whiteboard import ai as wai
here = Path(__file__).resolve().parent
script = json.load(open(here / "script.json"))
# 配音（平台的语音服务用同一套 Kokoro 模型）
import sherpa_onnx as so
d = sys.argv[1].rstrip("/") + "/"
tts = so.OfflineTts(so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(kokoro=so.OfflineTtsKokoroModelConfig(
    model=d + "model.int8.onnx", voices=d + "voices.bin", tokens=d + "tokens.txt", data_dir=d + "espeak-ng-data", dict_dir=d + "dict",
    lexicon=d + "lexicon-us-en.txt," + d + "lexicon-zh.txt"), num_threads=4),
    rule_fsts=d + "date-zh.fst," + d + "number-zh.fst," + d + "phone-zh.fst", max_num_sentences=1))
t, parts, segs = 0.8, [], []
sr = 24000
for s in script["segments"]:
    a = tts.generate(s["zh"], sid=49, speed=0.98); sr = a.sample_rate; x = np.array(a.samples, dtype=np.float32)
    if not parts: parts.append(np.zeros(int(sr * 0.8), np.float32))
    segs.append(dict(s, t0=round(t, 2), t1=round(t + len(x) / sr, 2)))
    parts += [x, np.zeros(int(sr * 0.45), np.float32)]; t += len(x) / sr + 0.45
parts.append(np.zeros(int(sr * 1.5), np.float32)); t += 1.5
sf.write(here / "配音.wav", np.concatenate(parts), sr)
boards, notes = wai.fix_boards(json.load(open(here / "boards.json"))["boards"], len(segs))
print("\n".join(notes) or "layout: no repairs needed")
lesson = wai.to_lesson(script["title"], segs, boards, audio="配音.wav", duration=round(t, 2))
json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
print(len(segs), "segments", len(boards), "boards", round(t, 1), "s")
