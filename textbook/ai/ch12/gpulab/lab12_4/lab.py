# GPU 实验 12.4 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 12.4　用开源模型转写录音并算词错率
# %%
import sys; sys.path.insert(0, "..")
import re, time
import numpy as np
import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
wqgpu.sh(f"{sys.executable} -m pip install -q transformers datasets soundfile librosa", timeout=1800)
from datasets import load_dataset
from transformers import WhisperForConditionalGeneration, WhisperProcessor
dev, SR = "cuda", 16000
print(torch.cuda.get_device_name(0))
# %% [markdown]
# ## 1. 数据与指标（任务 1）
# 用公开数据集 LibriSpeech 的几条测试样例。词错率 = 编辑距离 ÷ 参考词数；比较前先统一成小写、去标点，
# 否则标点和大小写会把错误率抬高好几个点——**报告词错率一定要说清归一化规则**。
# %%
ds = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
clips = [(np.asarray(ds[i]["audio"]["array"], dtype=np.float32), ds[i]["text"]) for i in range(min(8, len(ds)))]
audio_s = sum(len(a) for a, _ in clips) / SR
print(f"{len(clips)} 条，共 {audio_s:.1f} 秒")

try:   # Whisper 官方评测用的归一化：会把数字拼写出来、统一缩写；没有就退回小写去标点
    from transformers.models.whisper.english_normalizer import EnglishTextNormalizer
    _n = EnglishTextNormalizer({}); norm = lambda s: _n(s).split()
except Exception:
    norm = lambda s: re.sub(r"[^a-z0-9' ]+", " ", s.lower()).split()
def ed(a, b):
    dp = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, y in enumerate(b, 1):
            prev, dp[j] = dp[j], min(dp[j] + 1, dp[j - 1] + 1, prev + (x != y))
    return dp[-1]
# %% [markdown]
# ## 2. 三档模型（任务 2）
# tiny、base、small 的参数量相差约十倍。词错率降多少？实时率（处理时间 ÷ 音频时长）差多少？
# %%
res = {}
for size in ("tiny", "base", "small"):
    proc = WhisperProcessor.from_pretrained(f"openai/whisper-{size}")
    model = WhisperForConditionalGeneration.from_pretrained(f"openai/whisper-{size}", torch_dtype=torch.float16).to(dev).eval()
    model.generation_config.forced_decoder_ids = None
    errs = words = 0
    with torch.no_grad():                                 # 预热一次再计时
        model.generate(proc(clips[0][0], sampling_rate=SR, return_tensors="pt").input_features.to(dev, torch.float16),
                       language="en", task="transcribe", max_new_tokens=8)
    torch.cuda.synchronize(); t0 = time.perf_counter()
    for audio, ref in clips:
        feats = proc(audio, sampling_rate=SR, return_tensors="pt").input_features.to(dev, torch.float16)
        with torch.no_grad():
            ids = model.generate(feats, language="en", task="transcribe", max_new_tokens=200)
        hyp = norm(proc.batch_decode(ids, skip_special_tokens=True)[0]); r = norm(ref)
        errs += ed(r, hyp); words += len(r)
    torch.cuda.synchronize(); secs = time.perf_counter() - t0
    res[size] = (errs / max(words, 1) * 100, secs, audio_s / secs, sum(p.numel() for p in model.parameters()) / 1e6)
    print(f"{size:6s} 词错率 {res[size][0]:5.1f}%　{res[size][3]:5.0f} M 参数　比实时快 {res[size][2]:5.1f} 倍")
    del model; torch.cuda.empty_cache()
# %% [markdown]
# ## 3. 加上车间噪声（任务 3）
# 按 10、5、0 dB 叠加 1/f 噪声（与书中 `_ch12.workshop_noise` 同样的做法），看 small 的词错率怎样变。
# %%
def noise_like(n, seed=0):
    rng = np.random.default_rng(1200 + seed + 301)
    f = np.fft.rfftfreq(n, 1 / SR)
    y = np.fft.irfft(np.fft.rfft(rng.normal(0, 1, n)) / np.sqrt(np.maximum(f, 1.0)), n)
    return (y / (np.abs(y).max() + 1e-9)).astype(np.float32)

proc = WhisperProcessor.from_pretrained("openai/whisper-small")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small", torch_dtype=torch.float16).to(dev).eval()
model.generation_config.forced_decoder_ids = None
noisy = {}
for snr in (10, 5, 0):
    errs = words = 0
    for i, (audio, ref) in enumerate(clips):
        nz = noise_like(len(audio), i)
        k = np.sqrt(np.mean(audio ** 2) / (np.mean(nz ** 2) * 10 ** (snr / 10)))
        feats = proc(audio + k * nz, sampling_rate=SR, return_tensors="pt").input_features.to(dev, torch.float16)
        with torch.no_grad():
            ids = model.generate(feats, language="en", task="transcribe", max_new_tokens=200)
        hyp = norm(proc.batch_decode(ids, skip_special_tokens=True)[0]); r = norm(ref)
        errs += ed(r, hyp); words += len(r)
    noisy[snr] = errs / max(words, 1) * 100
    print(f"信噪比 {snr:3d} dB：词错率 {noisy[snr]:5.1f}%")
# %% [markdown]
# ## 4. 改一改（任务 4）
# 换一条自己念的录音（上传 wav，16 kHz 单声道）试试；或者把 `max_new_tokens` 调小，看截断对词错率的影响。
# %%
# 在这里试
# %% [markdown]
# ## 5. 回传结果
# %%
wqgpu.submit(tiny_wer=res["tiny"][0], base_wer=res["base"][0], small_wer=res["small"][0],
             small_speed=res["small"][2], wer_snr10=noisy[10], wer_snr0=noisy[0])
