"""同一节 AI 样片，用 Eddie 的声音合成（ZipVoice 零样本声音克隆：以他原录音里 7.8 秒的一句话做参考）。"""
import json, re, sys
from pathlib import Path
import numpy as np, soundfile as sf, sherpa_onnx as so
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "services" / "gateway"))
from app.production.whiteboard import ai as wai
here = Path(__file__).resolve().parent
Z = Path(sys.argv[1]); M = Z / "sherpa-onnx-zipvoice-distill-int8-zh-en-emilia"
tts = so.OfflineTts(so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(zipvoice=so.OfflineTtsZipvoiceModelConfig(
    tokens=str(M / "tokens.txt"), encoder=str(M / "encoder.int8.onnx"), decoder=str(M / "decoder.int8.onnx"),
    vocoder=str(Z / "vocos_24khz.onnx"), data_dir=str(M / "espeak-ng-data"), lexicon=str(M / "lexicon.txt")), num_threads=4),
    max_num_sentences=1))
p, psr = sf.read(Z / "prompt.wav", dtype="float32")
ptext = "物理学是自然科学的一个分支。自然科学包括生命科学、地球科学和物质科学。"
SAY = {"τ": "tau", "·": "", "×": "乘以", "≈": "约等于", "°": "度"}
script = json.load(open(here / "script.json"))
t, parts, segs, sr = 0.8, [], [], 24000
for s in script["segments"]:
    say = "".join(SAY.get(ch, ch) for ch in s["zh"])
    a = tts.generate(say, ptext, p.tolist(), psr, speed=1.0, num_steps=4)
    sr = a.sample_rate; x = np.array(a.samples, dtype=np.float32)
    if not parts: parts.append(np.zeros(int(sr * 0.8), np.float32))
    segs.append(dict(s, t0=round(t, 2), t1=round(t + len(x) / sr, 2)))
    parts += [x, np.zeros(int(sr * 0.45), np.float32)]; t += len(x) / sr + 0.45
    print(round(t, 1), s["zh"][:20], flush=True)
parts.append(np.zeros(int(sr * 1.5), np.float32)); t += 1.5
sf.write(here / "配音_Eddie.wav", np.concatenate(parts), sr)
boards, notes = wai.fix_boards(json.load(open(here / "boards.json"))["boards"], len(segs))
lesson = wai.to_lesson(script["title"], segs, boards, audio="配音_Eddie.wav", duration=round(t, 2))
json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
print(len(segs), "segments", round(t, 1), "s")
