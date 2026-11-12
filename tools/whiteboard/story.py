"""白板三维简画讲故事（第 162 轮第 1 步，本机做样片）。

    python3 tools/whiteboard/story.py <故事目录> [--mp4] [--voice kokoro|estimate] [--snap 秒,秒,…]

<故事目录>/story.yaml：演员（外形、声音）、场景（道具清单）、镜头（机位、人物初始站位、每一拍谁说什么、做什么）。
输出到 <故事目录>/out/：story.html（网页版：播放、拖进度、暂停时可拖着转视角）、story.mp4（1280×720，30 帧/秒）、snap_*.png。
配音：kokoro（sherpa-onnx，模型目录 $WQ_TTS_MODELS）；每句按“声音 + 文字”缓存在 out/voice/。
播放器在 services/gateway/app/production/whiteboard/scene3d.js（网页和逐帧出视频同一份）。
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
WB = ROOT / "services/gateway/app/production/whiteboard"
sys.path.insert(0, str(ROOT / "tools/video"))
from voice import zh_numbers, _trim, estimate_seconds  # noqa: E402

RATE = 24000
NARRATOR = "旁白"
LEAD, PRE, GAP, HOLD, WALK = 1.3, 0.2, 0.35, 0.8, 1.05


class TTS:
    def __init__(self, backend, cache: Path):
        self.backend, self.cache, self._tts = backend, cache, None
        cache.mkdir(parents=True, exist_ok=True)

    def say(self, text, sid):
        spoken = zh_numbers(text)
        key = hashlib.sha1(f"{self.backend}|{sid}|{spoken}".encode()).hexdigest()[:16]
        p = self.cache / f"{key}.wav"
        if not p.exists():
            if self.backend == "estimate":
                a = np.zeros(int(estimate_seconds(spoken, "zh") * RATE), np.float32)
            else:
                g = self.kokoro().generate(spoken.replace("“", "").replace("”", ""), sid=sid, speed=1.0)
                a = _trim(np.asarray(g.samples, np.float32))
                if g.sample_rate != RATE:
                    x = np.linspace(0, len(a) - 1, int(len(a) * RATE / g.sample_rate))
                    a = np.interp(x, np.arange(len(a)), a).astype(np.float32)
            with wave.open(str(p), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
                w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
        with wave.open(str(p)) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32767
        return a

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
                    num_threads=4),
                rule_fsts=d + "date-zh.fst," + d + "number-zh.fst," + d + "phone-zh.fst", max_num_sentences=1)
            self._tts = so.OfflineTts(cfg)
        return self._tts


def face_to(src, dst):
    return math.degrees(math.atan2(dst[0] - src[0], dst[1] - src[1]))


def compile_story(S, tts):
    cast = S["cast"]
    shots, clips, t = [], [], 0.0
    for sh in S["shots"]:
        if sh.get("title"):
            shots.append({"t0": t, "t1": t + sh.get("dur", 3), "title": {"zh": S["title"], "sub": S.get("sub", ""), "note": S.get("note", "")}})
            t += sh.get("dur", 3)
            continue
        t0 = t
        pos = {n: list(c["pos"]) for n, c in sh.get("chars", {}).items()}

        def resolve_face(who, v):
            if isinstance(v, str) and v.startswith("@"):
                return face_to(pos[who], pos[v[1:]])
            return v

        chars = {}
        for n, c in sh.get("chars", {}).items():
            k = {"t": t0 - 0.001, "pos": c["pos"], "face": resolve_face(n, c.get("face", 0)), "pose": c.get("pose", "stand"), "expr": c.get("expr", "neutral")}
            if "lookAt" in c:
                k["lookAt"] = c["lookAt"]
            chars[n] = [k]
        props = {pid: [{"t": t0 - 0.001, "set": s}] for pid, s in sh.get("props", {}).items()}
        bubbles, subs, cuts = [], [], []
        cur = t0 + LEAD
        for b in sh["beats"]:
            start = cur + b.get("pre", PRE)
            who = b["say"]
            sid = S.get("narrator", 52) if who == NARRATOR else cast[who]["voice"]
            a = tts.say(b["text"], sid)
            dur = len(a) / RATE
            clips.append((start, a))
            if who == NARRATOR:
                subs.append({"t0": start, "t1": start + dur + 0.2, "text": b["text"]})
            else:
                bb = {"who": who, "t0": start - 0.1, "t1": start + dur + 0.35, "text": b["text"]}
                if b.get("style"):
                    bb.update(style=b["style"], at=b.get("at"), label=b.get("label"))
                bubbles.append(bb)
            cams = b.get("cams") or ([dict(b["cam"], at=0)] if b.get("cam") else [])
            for c in cams:
                spec = {k: v for k, v in c.items() if k != "at"}
                ct = start - 0.12 + c.get("at", 0) * dur
                if spec.get("wide"):
                    spec = {"wide": True}
                cuts.append({"t": ct, "spec": spec})
            for d in sorted(b.get("do", []), key=lambda d: d.get("delay", 0)):
                at = start + d.get("delay", 0)
                if "prop" in d:
                    props.setdefault(d["prop"], []).append({"t": at, "set": d["set"]})
                    continue
                n = d["who"]
                k = {"t": at}
                for key in ("pose", "expr", "lookAt", "show", "mark"):
                    if key in d:
                        k[key] = d[key]
                if "pos" in d:
                    k["pos"] = d["pos"]; pos[n] = list(d["pos"])
                if "face" in d:
                    k["face"] = resolve_face(n, d["face"])
                if "walk" in d:
                    w = d["walk"]; to = w["to"]
                    dist = math.dist(pos[n], to)
                    k["walk"] = {"to": to, "dur": max(0.6, dist / WALK)}
                    if "face" in w:
                        k["walk"]["face"] = resolve_face(n, w["face"])
                    pos[n] = list(to)
                chars[n].append(k)
            cur = start + dur + GAP
        t1 = cur + sh.get("hold", HOLD)
        for n in chars:
            chars[n].sort(key=lambda k: k["t"])
        for p in props:
            props[p].sort(key=lambda k: k["t"])
        cam = [{"t": t0 + c["at"] * (t1 - t0), "pos": c["pos"], "look": c["look"], "fov": c.get("fov", 42)} for c in sh["cam"]]
        cuts = [c for c in sorted(cuts, key=lambda c: c["t"])]
        # a {wide: true} cut returns to the shot's own camera path
        cuts = [c if not c["spec"].get("wide") else {"t": c["t"], "spec": {"wide": True}} for c in cuts]
        shots.append({"t0": t0, "t1": t1, "scene": sh["scene"], "chars": chars, "props": props, "cam": cam, "bubbles": bubbles, "subs": subs,
                      "cuts": cuts, "mood": sh.get("mood")})
        t = t1
    end = 3.2
    shots.append({"t0": t, "t1": t + end, "title": {"zh": "（完）", "sub": S["title"], "note": S.get("note", "")}})
    t += end
    audio = np.zeros(int(t * RATE) + RATE, np.float32)
    for st, a in clips:
        i = int(st * RATE)
        audio[i:i + len(a)] += a[: len(audio) - i]
    story = {"size": S.get("size", [1280, 720]), "cast": {n: c.get("look", {}) for n, c in cast.items()}, "scenes": S["scenes"], "shots": shots,
             "duration": t, "watermark": "问渠 WenQuest · 原创故事"}
    return story, audio


def font_css(text):
    """霞鹜文楷切片里只取用到的字所在的几片，内嵌成 WQHand 字体。"""
    from fontTools.ttLib import TTFont
    need = set(map(ord, text)) | set(range(32, 127))
    css = []
    for f in sorted((WB / "fonts").glob("lxgwwenkai-bold-subset-*.woff2")):
        cm = TTFont(str(f)).getBestCmap()
        if need & set(cm):
            b64 = base64.b64encode(f.read_bytes()).decode()
            rng = ",".join(f"U+{c:X}" for c in sorted(need & set(cm)))
            css.append(f"@font-face{{font-family:WQHand;src:url(data:font/woff2;base64,{b64}) format('woff2');unicode-range:{rng};}}")
    return "\n".join(css)


def all_text(S):
    out = ["（完）问渠 WenQuest · 原创故事菜谱十一月发布关节角度"]

    def walk(x):
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, dict):
            for k, v in x.items():
                walk(k); walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(S)
    return "".join(out)


PAGE = """<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{fonts}
html,body{{margin:0;background:#2b2f35;height:100%}} body{{display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:WQHand,sans-serif}}
#stage{{width:min(100vw,calc((100vh - 56px)*16/9));aspect-ratio:16/9;background:#fbf8f2;position:relative;touch-action:none}}
#stage svg{{width:100%;height:100%;display:block}}
#bar{{width:min(100vw,calc((100vh - 56px)*16/9));display:flex;gap:10px;align-items:center;padding:10px 12px;box-sizing:border-box;color:#e8e8e8}}
#bar button{{font:inherit;font-size:18px;background:#f0b14a;border:0;border-radius:8px;padding:6px 14px;cursor:pointer}}
#bar input{{flex:1}} #hint{{font-size:14px;color:#aab}}
{render_css}</style></head><body>
<div id="stage"><svg id="svg" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"></svg></div>
<div id="bar"><button id="play">▶ 播放</button><input id="seek" type="range" min="0" max="{dur}" step="0.01" value="0"><span id="time">0:00</span><span id="hint">暂停时可拖动画面转视角</span></div>
{audio}
<script>{rough}</script><script>{scene3d}</script>
<script>
const STORY={story};
const svg=document.getElementById('svg'),seek=document.getElementById('seek'),btn=document.getElementById('play'),tm=document.getElementById('time'),au=document.getElementById('au');
let t=0,playing=false,t0=0,w0=0,orbit=null;
function draw(){{svg.innerHTML=WQScene3D.render(STORY,Math.min(t,STORY.duration-0.001),{{orbit}});seek.value=t;tm.textContent=Math.floor(t/60)+':'+String(Math.floor(t%60)).padStart(2,'0');}}
window.SEEK=(x)=>{{t=x;orbit=null;draw();return true;}};
function loop(){{if(!playing)return;t=au&&!au.paused?au.currentTime:w0+(performance.now()-t0)/1000;if(t>=STORY.duration){{t=STORY.duration;playing=false;btn.textContent='▶ 播放';}}draw();requestAnimationFrame(loop);}}
btn.onclick=()=>{{playing=!playing;btn.textContent=playing?'❚❚ 暂停':'▶ 播放';orbit=null;if(playing){{if(t>=STORY.duration)t=0;t0=performance.now();w0=t;if(au){{au.currentTime=t;au.play().catch(()=>{{}});}}loop();}}else if(au)au.pause();}};
seek.oninput=()=>{{t=+seek.value;orbit=null;if(au)au.currentTime=t;t0=performance.now();w0=t;draw();}};
let drag=null;const st=document.getElementById('stage');
st.onpointerdown=(e)=>{{if(playing)return;drag=[e.clientX,e.clientY,orbit?orbit.slice():[0,0]];st.setPointerCapture(e.pointerId);}};
st.onpointermove=(e)=>{{if(!drag)return;orbit=[drag[2][0]-(e.clientX-drag[0])*0.008,drag[2][1]+(e.clientY-drag[1])*0.01];draw();}};
st.onpointerup=()=>{{drag=null;}};
document.fonts.ready.then(draw);draw();
</script></body></html>"""


def build(d: Path, voice: str, mp4: bool, snaps):
    d = d.resolve()
    S = yaml.safe_load((d / "story.yaml").read_text(encoding="utf-8"))
    out = d / "out"
    out.mkdir(exist_ok=True)
    story, audio = compile_story(S, TTS(voice, out / "voice" / voice))
    W, H = story["size"]
    wav = out / "story.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-b:a", "96k", str(out / "story.mp3")], check=True)
    fonts = font_css(all_text(S))
    common = dict(title=S["title"], fonts=fonts, W=W, H=H, dur=round(story["duration"], 2),
                  rough=(WB / "rough.js").read_text(), scene3d=(WB / "scene3d.js").read_text(), story=json.dumps(story, ensure_ascii=False))
    au = base64.b64encode((out / "story.mp3").read_bytes()).decode()
    (out / "story.html").write_text(PAGE.format(**common, render_css="", audio=f'<audio id="au" src="data:audio/mpeg;base64,{au}" preload="auto"></audio>'), encoding="utf-8")
    rend = out / "render.html"
    rend.write_text(PAGE.format(**common, audio="", render_css="#bar{display:none} #stage{width:1280px!important;height:720px} body{display:block}"), encoding="utf-8")
    print(f"时长 {story['duration']:.1f} 秒，{len(story['shots'])} 个镜头 → {out / 'story.html'}")
    if snaps or mp4:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
            pg.on("pageerror", lambda e: print("页面错误:", e))
            pg.goto(rend.as_uri())
            pg.wait_for_function("document.fonts.status==='loaded'")
            pg.wait_for_timeout(300)
            for s in snaps:
                pg.evaluate(f"SEEK({s})")
                pg.wait_for_timeout(30)
                pg.locator("#stage").screenshot(path=str(out / f"snap_{s:06.2f}.png"))
            if mp4:
                fps = 30
                n = int(story["duration"] * fps)
                ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-i", "-", "-i", str(wav),
                                       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "128k",
                                       "-shortest", "-movflags", "+faststart", str(out / "story.mp4")], stdin=subprocess.PIPE)
                import time
                t0 = time.time()
                for i in range(n):
                    pg.evaluate(f"SEEK({i / fps})")
                    ff.stdin.write(pg.locator("#stage").screenshot(type="jpeg", quality=95))
                    if i % 300 == 0:
                        print(f"  帧 {i}/{n}  {time.time() - t0:.0f} 秒", flush=True)
                ff.stdin.close(); ff.wait()
                print(f"MP4 → {out / 'story.mp4'}（{n} 帧，{time.time() - t0:.0f} 秒）")
            b.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--voice", default="kokoro", choices=["kokoro", "estimate"])
    ap.add_argument("--mp4", action="store_true")
    ap.add_argument("--snap", default="")
    a = ap.parse_args()
    build(Path(a.dir), a.voice, a.mp4, [float(x) for x in a.snap.split(",") if x])
