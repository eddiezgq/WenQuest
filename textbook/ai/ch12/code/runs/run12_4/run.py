"""程序 12.4.1（实测）：开源语音识别模型的字错率与实时率（12.4 节）。A10。
模型：Whisper 的 tiny、base、small 三档（开源权重，MIT 许可）。音频：公开数据集 LibriSpeech 的
几条测试样例（由 Hugging Face 的 datasets 下载，不进仓库）。对每一档测：
  - 词错率（WER）：识别结果与参考文本的编辑距离 ÷ 参考词数（文本先统一成小写、去标点）；
  - 实时率（RTF）：处理时间 ÷ 音频时长，以及"比实时快多少倍"；
  - 噪声下的词错率：把同一段音频按 10 dB、5 dB、0 dB 叠加噪声后再识别（噪声由程序合成，与书中 _ch12 一致）。
结果写进 out.json（第 14 轮附 4.4 节）。"""
import json
import re
import time

import numpy as np
import torch

import prep

prep.ensure()                                               # 装好依赖（transformers、datasets、soundfile）

from datasets import load_dataset                           # noqa: E402
from transformers import WhisperForConditionalGeneration, WhisperProcessor   # noqa: E402

SR = 16000
dev = "cuda"
N_CLIP = 8


try:                                                        # Whisper 官方评测用的归一化（会把数字拼写出来、统一缩写）
    from transformers.models.whisper.english_normalizer import EnglishTextNormalizer
    _norm = EnglishTextNormalizer({})
    NORM_NAME = "EnglishTextNormalizer"
except Exception:                                           # noqa: BLE001  退路：小写、去标点，但数字拼写不处理
    _norm = None
    NORM_NAME = "lowercase+strip-punct"


def norm(s):
    if _norm is not None:
        return _norm(s).split()
    return re.sub(r"[^a-z0-9' ]+", " ", s.lower()).split()


def edit_distance(a, b):
    dp = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, y in enumerate(b, 1):
            prev, dp[j] = dp[j], min(dp[j] + 1, dp[j - 1] + 1, prev + (x != y))
    return dp[-1]


def noise_like(n, seed=0):
    """1/f 谱的车间噪声，做法与书中 _ch12.workshop_noise 相同（这里重写一遍，是因为云端这台机器上
    只放 runs/ 这个目录，不带教材的 code/；两处的公式一致，但随机种子与采样率不同，
    所以这里的噪声波形与书中算例的不是同一段，只能比较趋势，不能比较具体数值。）"""
    rng = np.random.default_rng(1200 + seed + 301)
    white = rng.normal(0, 1, n)
    f = np.fft.rfftfreq(n, 1 / SR)
    y = np.fft.irfft(np.fft.rfft(white) / np.sqrt(np.maximum(f, 1.0)), n)
    return (y / (np.abs(y).max() + 1e-9)).astype(np.float32)


ds = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
clips = [(np.asarray(ds[i]["audio"]["array"], dtype=np.float32), ds[i]["text"]) for i in range(min(N_CLIP, len(ds)))]
import transformers                                        # noqa: E402  记下版本，数字才可比
out = {"torch": torch.__version__, "transformers": transformers.__version__, "normalizer": NORM_NAME,
       "n_clip": len(clips), "audio_s": float(sum(len(a) for a, _ in clips) / SR)}

for size in ("tiny", "base", "small"):
    name = f"openai/whisper-{size}"
    proc = WhisperProcessor.from_pretrained(name)
    model = WhisperForConditionalGeneration.from_pretrained(name, torch_dtype=torch.float16).to(dev).eval()
    model.generation_config.forced_decoder_ids = None
    errs = words = 0
    warm = proc(clips[0][0], sampling_rate=SR, return_tensors="pt").input_features.to(dev, torch.float16)
    with torch.no_grad():                                   # 预热：第一次调用含 CUDA 上下文与算法选型的开销
        model.generate(warm, language="en", task="transcribe", max_new_tokens=8)
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for audio, ref in clips:
        feats = proc(audio, sampling_rate=SR, return_tensors="pt").input_features.to(dev, torch.float16)
        with torch.no_grad():
            ids = model.generate(feats, language="en", task="transcribe", max_new_tokens=200)
        hyp = norm(proc.batch_decode(ids, skip_special_tokens=True)[0])
        r = norm(ref)
        errs += edit_distance(r, hyp)
        words += len(r)
    torch.cuda.synchronize()
    secs = time.perf_counter() - t0
    out[size + "_wer"] = errs / max(words, 1) * 100
    out[size + "_s"] = secs
    out[size + "_rtf"] = secs / out["audio_s"]
    out[size + "_speed"] = out["audio_s"] / secs
    out[size + "_params_M"] = sum(p.numel() for p in model.parameters()) / 1e6
    if size == "small":                                      # 只在最大的一档上做噪声试验
        for snr in (10, 5, 0):
            errs2 = words2 = 0
            for i, (audio, ref) in enumerate(clips):
                nz = noise_like(len(audio), i)
                k = np.sqrt(np.mean(audio ** 2) / (np.mean(nz ** 2) * 10 ** (snr / 10)))
                y = audio + k * nz
                feats = proc(y, sampling_rate=SR, return_tensors="pt").input_features.to(dev, torch.float16)
                with torch.no_grad():
                    ids = model.generate(feats, language="en", task="transcribe", max_new_tokens=200)
                hyp = norm(proc.batch_decode(ids, skip_special_tokens=True)[0])
                r = norm(ref)
                errs2 += edit_distance(r, hyp)
                words2 += len(r)
            out[f"small_wer_snr{snr}"] = errs2 / max(words2, 1) * 100
    del model
    torch.cuda.empty_cache()

out["wer_gain"] = out["tiny_wer"] - out["small_wer"]
out["speed_ratio"] = out["tiny_speed"] / out["small_speed"]
json.dump(out, open("out.json", "w"), ensure_ascii=False)
print(out)
