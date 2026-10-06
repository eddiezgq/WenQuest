"""Eddie 本人声音的配音（第 22 轮 2.3）：在临时租用的 GPU 机器上用开源 CosyVoice 合成，合成完立即关机。

    python3 tools/video/clone.py audition --out DIR            # 试听：同一段中英文，Fun-CosyVoice3 与 CosyVoice2 各一份
    python3 tools/video/clone.py lectures L1 [L2 …] --out DIR   # 正式：讲稿的每一句（中、英），按 voice.py 的键命名
       [--engine cv3|cv2]

样音：docs/课程视频/声音样本/{zh,en}.*.enc（AES-256 加密，仓库公开所以不放明文），密码在环境变量 VOICE_KEY
（GitHub 仓库密钥）。只有中文样音时，英文用跨语种克隆。样音在 GPU 机器上切出 8–15 秒最干净的一段作提示音，
文字由 Whisper 识别；整段样音与合成结果用完即删，机器最后一定关机（与 GPU 实测同一套 Lambda 账号，textbook/tools/gpurun.py）。

模型：CosyVoice 代码 Apache-2.0（固定提交 COSYVOICE_COMMIT）；权重 Fun-CosyVoice3-0.5B-2512、CosyVoice2-0.5B 从 Hugging Face
下载，日志里打印模型自带的许可证说明备查。不调用任何语音合成 API。
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "textbook" / "tools"))
SAMPLES = ROOT / "docs" / "课程视频" / "声音样本"
COSYVOICE_COMMIT = "074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc"
MODELS = {"cv3": "FunAudioLLM/Fun-CosyVoice3-0.5B-2512", "cv2": "FunAudioLLM/CosyVoice2-0.5B"}
GPU = "gpu_1x_a10"

AUDITION = {
    "zh": ["同学们好，欢迎来到问渠的线性代数课。这一讲是第十四章第二节，谱定理。",
           "机械臂握着砂轮磨削工件，工具压在工件上，工件也在反推工具，末端就会被顶开一点点。",
           "用 eigh 一算，两个主刚度是五千七百六十四和两万四千零九十七牛每米，相差四倍多。"],
    "en": ["Hi everyone, and welcome to Linear Algebra at WenQuest. This is Chapter 14, Section 2, the spectral theorem.",
           "A robot arm holds a grinding wheel. The tool presses on the part, the part pushes back, and the tip of the arm gives way a little.",
           "Running eigh, the principal stiffnesses are 5764 and 24097 newtons per metre, more than four times apart."],
}

SETUP = f"""set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq && sudo apt-get install -y -qq sox libsox-dev ffmpeg > /dev/null
if [ ! -d CosyVoice ]; then
  git init -q CosyVoice && cd CosyVoice && git remote add origin https://github.com/FunAudioLLM/CosyVoice.git
  git fetch -q --depth 1 origin {COSYVOICE_COMMIT} && git checkout -q FETCH_HEAD && git submodule update -q --init --recursive --depth 1
  cd ..
fi
python3 -m venv ~/cv && . ~/cv/bin/activate
pip install -q --upgrade pip
pip install -q -r CosyVoice/requirements.txt
pip install -q huggingface_hub
"""

REMOTE = r'''
import json, os, sys, glob, subprocess
sys.path.insert(0, "CosyVoice"); sys.path.insert(0, "CosyVoice/third_party/Matcha-TTS")
import numpy as np, soundfile as sf, torch, torchaudio
from huggingface_hub import snapshot_download
from cosyvoice.cli.cosyvoice import AutoModel

job = json.load(open("job.json", encoding="utf-8"))
os.makedirs("out", exist_ok=True)

# 1. 提示音：每种语言的样音切出 8–15 秒一段，Whisper 识别文字
import whisper
asr = whisper.load_model("small")
prompts = {}
for src in sorted(glob.glob("sample_*.wav")):
    lang = whisper.detect_language(asr, whisper.log_mel_spectrogram(whisper.pad_or_trim(whisper.load_audio(src)), asr.dims.n_mels).to(asr.device))[1]
    lang = max(lang, key=lang.get)          # 按识别出的语言归类（文件名只是猜测）
    if lang not in ("zh", "en"):
        print(f"{src}: 识别为 {lang}，跳过", flush=True)
        continue
    r = asr.transcribe(src, language=lang, condition_on_previous_text=False)
    segs = [s for s in r["segments"] if s["end"] - s["start"] > 0.8 and s.get("no_speech_prob", 0) < 0.3]
    best = None
    for i in range(len(segs)):
        j, t = i, 0.0
        while j < len(segs) and segs[j]["end"] - segs[i]["start"] < 15.0:
            t = segs[j]["end"] - segs[i]["start"]; j += 1
            if t >= 8.0:
                score = -sum(s.get("avg_logprob", -1) for s in segs[i:j]) / (j - i)
                if best is None or score < best[0]:
                    best = (score, segs[i]["start"], segs[j - 1]["end"], "".join(s["text"] for s in segs[i:j]) if lang == "zh"
                            else " ".join(s["text"].strip() for s in segs[i:j]))
    if not best:
        raise SystemExit(f"样音 {lang} 太短或识别不出连续 8 秒以上的语音")
    _, a, b, text = best
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ss", f"{max(0, a - 0.1):.2f}", "-to", f"{b + 0.15:.2f}",
                    "-ar", "16000", "-ac", "1", f"prompt_{lang}.wav"], check=True)
    prompts[lang] = (f"prompt_{lang}.wav", text.strip())
    print(f"提示音 {lang}: {a:.1f}–{b:.1f} s，{text.strip()}", flush=True)
del asr; torch.cuda.empty_cache()
json.dump({k: v[1] for k, v in prompts.items()}, open("out/prompts.json", "w", encoding="utf-8"), ensure_ascii=False)

# 2. 合成
for engine in job["engines"]:
    mdir = snapshot_download(job["models"][engine], local_dir=f"models/{engine}")
    for f in glob.glob(mdir + "/README*") + glob.glob(mdir + "/LICENSE*"):
        print(f"--- {engine} {os.path.basename(f)} ---\n" + open(f, encoding="utf-8", errors="replace").read()[:1500], flush=True)
    cv = AutoModel(model_dir=mdir, fp16=False)
    os.makedirs(f"out/{engine}", exist_ok=True)
    for item in job["items"]:
        lang, text = item["lang"], item["text"]
        out = f"out/{engine}/{lang}/{item['key']}.wav"
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if os.path.exists(out):
            continue
        if lang in prompts:
            wav, ptext = prompts[lang]
            ptext = ("You are a helpful assistant.<|endofprompt|>" + ptext) if engine == "cv3" else ptext
            gen = cv.inference_zero_shot(text, ptext, wav, stream=False)
        else:   # 只有一种语言的样音：跨语种
            wav = next(iter(prompts.values()))[0]
            t = ("You are a helpful assistant.<|endofprompt|>" + text) if engine == "cv3" else ("<|en|>" + text)
            gen = cv.inference_cross_lingual(t, wav, stream=False)
        parts = [o["tts_speech"].squeeze(0).cpu().numpy() for o in gen]
        a = np.concatenate(parts) if parts else np.zeros(1, np.float32)
        sf.write(out, a, cv.sample_rate, subtype="PCM_16")
    print(f"{engine}: {len(job['items'])} 句完成", flush=True)
    del cv; torch.cuda.empty_cache()
'''


def decrypt_samples(dst: Path) -> list[str]:
    key = os.environ.get("VOICE_KEY")
    if not key:
        raise SystemExit("没有设置 VOICE_KEY（GitHub 仓库密钥），解不开样音")
    langs = []
    for enc in sorted(SAMPLES.glob("*.enc")):
        lang = enc.name.split(".")[0]
        raw = dst / enc.name[:-4]
        subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-iter", "200000", "-in", str(enc), "-out", str(raw),
                        "-pass", "env:VOICE_KEY"], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-ar", "24000", "-ac", "1", str(dst / f"sample_{lang}.wav")], check=True)
        raw.unlink()
        langs.append(lang)
    if not langs:
        raise SystemExit("缺少样音 docs/课程视频/声音样本/*.enc")
    return langs


def encrypt_sample(src: Path, lang: str) -> Path:
    """For Claude's side: put Eddie's recording into the repo, encrypted with VOICE_KEY."""
    SAMPLES.mkdir(parents=True, exist_ok=True)
    out = SAMPLES / f"{lang}{src.suffix.lower()}.enc"
    subprocess.run(["openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2", "-iter", "200000", "-in", str(src), "-out", str(out),
                    "-pass", "env:VOICE_KEY"], check=True)
    return out


def temp_ssh_key(G, work: Path) -> tuple[str, str]:
    """No SSH key in the secrets: make a one-off key pair and register it with Lambda (removed again afterwards)."""
    key = work / "wq_voice_key"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)], check=True)
    name = f"wq-voice-{int(time.time())}"
    kid = G._api("POST", "/ssh-keys", {"name": name, "public_key": (work / "wq_voice_key.pub").read_text().strip()}).get("id", "")
    os.environ["LAMBDA_SSH_KEY_FILE"] = str(key)
    return name, kid


def gpu_session(job: dict, work: Path, out: Path):
    import gpurun as G
    kid = ""
    if os.environ.get("LAMBDA_SSH_KEY_FILE") and os.environ.get("LAMBDA_SSH_KEY_NAME"):
        key_name = os.environ["LAMBDA_SSH_KEY_NAME"]
    else:
        key_name, kid = temp_ssh_key(G, work)
    region = G.pick_region(GPU)
    try:
        iid = G._api("POST", "/instance-operations/launch", {"region_name": region, "instance_type_name": GPU,
                                                             "ssh_key_names": [key_name], "name": "wq-voice"})["instance_ids"][0]
    except Exception:
        if kid:
            G._api("DELETE", f"/ssh-keys/{kid}")
        raise
    t0 = time.time()
    try:
        ip = ""
        for _ in range(120):
            inst = G._api("GET", f"/instances/{iid}")
            if inst.get("status") == "active" and inst.get("ip"):
                ip = inst["ip"]
                break
            time.sleep(10)
        if not ip:
            raise RuntimeError("GPU 机器没有启动")
        time.sleep(20)
        (work / "job.json").write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")
        (work / "remote.py").write_text(REMOTE, encoding="utf-8")
        (work / "setup.sh").write_text(SETUP, encoding="utf-8")
        G._ssh(ip, "mkdir -p wqv")
        for f in ["job.json", "remote.py", "setup.sh", *[p.name for p in work.glob("sample_*.wav")]]:
            G._scp(str(work / f), f"ubuntu@{ip}:wqv/{f}")
        G._ssh(ip, "cd wqv && bash setup.sh && . ~/cv/bin/activate && python remote.py")
        G._scp(f"ubuntu@{ip}:wqv/out/.", str(out))
        G._ssh(ip, "rm -rf wqv/sample_* wqv/prompt_* wqv/out")
    finally:
        G._api("POST", "/instance-operations/terminate", {"instance_ids": [iid]})
        print(f"GPU 机器已关机，用时 {(time.time() - t0) / 60:.0f} 分钟", flush=True)
        if kid:
            try:
                G._api("DELETE", f"/ssh-keys/{kid}")
            except Exception as e:      # the machine is already off; a leftover public key is harmless
                print(f"临时 SSH 公钥没删掉：{e}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("audition")
    a1.add_argument("--out", required=True)
    a2 = sub.add_parser("lectures")
    a2.add_argument("lectures", nargs="+")
    a2.add_argument("--out", required=True)
    a2.add_argument("--engine", default="cv3", choices=sorted(MODELS))
    a3 = sub.add_parser("encrypt")
    a3.add_argument("file")
    a3.add_argument("--lang", required=True, choices=["zh", "en"])
    a = ap.parse_args()
    if a.cmd == "encrypt":
        print(encrypt_sample(Path(a.file), a.lang))
        return
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        decrypt_samples(work)
        if a.cmd == "audition":
            items = [{"lang": lang, "key": f"{lang}_{i + 1}", "text": t} for lang, ts in AUDITION.items() for i, t in enumerate(ts)]
            job = {"engines": ["cv3", "cv2"], "models": MODELS, "items": items}
        else:
            import script as S
            import voice as V
            items, seen = [], set()
            for d in a.lectures:
                lec = S.load(d)
                for lang in ("zh", "en"):
                    for j in V.clone_jobs(lec, lang, Path(td) / "cache"):
                        if j["key"] not in seen:
                            seen.add(j["key"])
                            items.append({"lang": lang, **j})
            job = {"engines": [a.engine], "models": MODELS, "items": items}
        print(f"{len(job['items'])} 句，引擎 {job['engines']}", flush=True)
        gpu_session(job, work, out)


if __name__ == "__main__":
    main()
