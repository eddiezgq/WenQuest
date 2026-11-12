"""三维故事互动扮演（第 163 轮第 1 步：单人版）。

    WQ_TTS_MODELS=<kokoro 模型目录> python3 tools/whiteboard/play.py <故事目录> [--voice kokoro|estimate] [--snap]

读 <故事目录>/play.yaml（演员、场景取自 base 指向的 story.yaml；节点可引用 story.yaml 的镜头或自己写镜头；
choice 决定点、ending 结局卡），输出 <故事目录>/out/play.html：选角色 → 演到自己的台词时停下（录下自己念的，或用 AI 声音）
→ 决定点自己选 → 不同结局 → 复盘页。每个镜头单独计时，每句配音单独一段，换成学生自己的录音时只换这一句。
--check 把所有分支路径走一遍（不配音），检查每个 next 都有着落、每条路都走到结局。
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from story import TTS, RATE, WB, compile_story, font_css, all_text  # noqa: E402


def load(d: Path):
    P = yaml.safe_load((d / "play.yaml").read_text(encoding="utf-8"))
    B = yaml.safe_load((d / P["base"]).read_text(encoding="utf-8"))
    base_shots = {s["id"]: s for s in B["shots"] if "id" in s}
    return P, B, base_shots


def paths(P):
    """All paths from start to an ending (list of node ids)."""
    nodes = {n["id"]: n for n in P["nodes"]}
    out = []

    def walk(nid, path):
        if nid not in nodes:
            raise SystemExit(f"节点 {path[-1] if path else '?'} 指向不存在的 {nid}")
        if nid in path:
            raise SystemExit(f"死循环：{' → '.join(path + [nid])}")
        n, path = nodes[nid], path + [nid]
        if "ending" in n:
            out.append(path); return
        if "choice" in n:
            for o in n["choice"]["options"]:
                walk(o["next"], path)
        elif "next" in n:
            walk(n["next"], path)
        else:
            raise SystemExit(f"节点 {nid} 既没有 next / choice，也不是结局")
    walk(P["start"], [])
    return out


def mp3_b64(a: np.ndarray) -> str:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "wav", "-i", "-", "-b:a", "80k", "-f", "mp3", "-"], input=buf.getvalue(), capture_output=True, check=True)
    return base64.b64encode(r.stdout).decode()


def build(d: Path, voice: str, snap: bool):
    d = d.resolve()
    P, B, base_shots = load(d)
    ps = paths(P)
    print(f"{len(ps)} 条路径：")
    for p in ps:
        print("  " + " → ".join(p))
    tts = TTS(voice, d / "out" / "voice" / voice)
    nodes, cache = {}, {}
    for n in P["nodes"]:
        nd = {"id": n["id"]}
        if "ending" in n:
            nd["ending"] = n["ending"]
            nd["shot"] = {"t0": 0, "t1": 4.5, "title": {"zh": n["ending"]["title"], "sub": n["ending"].get("text", ""), "note": B.get("note", "")}}
        else:
            src = base_shots[n["use"]] if "use" in n else n["shot"]
            key = n.get("use") or n["id"]
            if key not in cache:
                if src.get("title"):
                    cache[key] = ({"t0": 0, "t1": src.get("dur", 3), "title": {"zh": B["title"], "sub": "互动版 · " + B.get("sub", ""), "note": B.get("note", "")}}, [])
                else:
                    info = []
                    S = dict(B, shots=[src])
                    story, _ = compile_story(S, tts, end_card=False, clip_info=info)
                    cache[key] = (story["shots"][0], [{"t": round(c["t"], 3), "dur": round(c["dur"], 3), "who": c["who"], "text": c["text"], "src": mp3_b64(c["a"])} for c in info])
            nd["shot"], nd["clips"] = cache[key]
        for k in ("next", "choice"):
            if k in n:
                nd[k] = n[k]
        nodes[n["id"]] = nd
    story = {"size": B.get("size", [1280, 720]), "cast": {k: v.get("look", {}) for k, v in B["cast"].items()}, "scenes": B["scenes"], "watermark": "问渠 WenQuest · 原创故事"}
    game = {"title": P.get("title", B["title"]), "roles": P["roles"], "start": P["start"], "lessons": P.get("lessons", []), "nodes": nodes,
            "looks": {r: B["cast"][r].get("look", {}) for r in P["roles"]}}
    out = d / "out"
    out.mkdir(exist_ok=True)
    fonts = font_css(all_text(B) + all_text(P) + "轮到你了如果你是你会怎么选你来决定录音念出来停止用声音继续跳过只看不演选择角色开始再来一次换个角色复盘你的选择结局道理这一路")
    page = PAGE.replace("%TITLE%", game["title"]).replace("%FONTS%", fonts).replace("%W%", str(story["size"][0])).replace("%H%", str(story["size"][1]))
    page = page.replace("%ROUGH%", (WB / "rough.js").read_text()).replace("%SCENE%", (WB / "scene3d.js").read_text())
    page = page.replace("%STORY%", json.dumps(story, ensure_ascii=False)).replace("%GAME%", json.dumps(game, ensure_ascii=False))
    (out / "play.html").write_text(page, encoding="utf-8")
    print(f"→ {out / 'play.html'}（{(out / 'play.html').stat().st_size / 1e6:.1f} MB）")
    if snap:
        shoot(out / "play.html", out)


def shoot(html: Path, out: Path):
    """Walk one path in a browser: role screen, a paused own line, a choice, the recap."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        for vp, tag in (({"width": 1280, "height": 860}, "pc"), ({"width": 390, "height": 844}, "phone")):
            pg = b.new_page(viewport=vp)
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(html.as_uri())
            pg.wait_for_function("document.fonts.status==='loaded'")
            pg.screenshot(path=str(out / f"play_{tag}_1_roles.png"))
            pg.click("text=老马")
            pg.click("#go")
            pg.evaluate("TEST.skipTo('s2', G.nodes.s2.clips.find(c=>c.who==='老马').t)")   # 老马's own line in the phone shot
            pg.wait_for_timeout(500)
            pg.screenshot(path=str(out / f"play_{tag}_2_myline.png"))
            pg.evaluate("TEST.skipTo('s4b', 999)")
            pg.wait_for_timeout(500)
            pg.screenshot(path=str(out / f"play_{tag}_3_choice.png"))
            pg.click(".opt >> nth=1")
            pg.evaluate("TEST.skipTo('s6bad', 999)")
            pg.wait_for_timeout(300)
            pg.evaluate("TEST.skipTo('end_trust', 999)")
            pg.wait_for_timeout(500)
            pg.screenshot(path=str(out / f"play_{tag}_4_recap.png"))
            if errs:
                print("页面错误：", errs)
            pg.close()
        b.close()


PAGE = r"""<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%TITLE%</title><style>%FONTS%
:root{--ink:#1d2329;--paper:#fbf8f2;--gold:#f0b14a;--muted:#5f6b76}
html,body{margin:0;background:#2b2f35;color:var(--ink);font-family:WQHand,sans-serif}
#wrap{max-width:calc((100vh - 24px)*16/9);margin:0 auto;padding:12px 0;box-sizing:border-box}
#stage{position:relative;width:100%;aspect-ratio:16/9;background:var(--paper);overflow:hidden;border-radius:6px}
#stage svg{width:100%;height:100%;display:block}
.panel{position:absolute;left:50%;transform:translateX(-50%);bottom:4%;width:min(92%,760px);background:#fffdf6;border:2.5px solid var(--ink);border-radius:14px;padding:14px 18px;box-sizing:border-box;box-shadow:0 6px 20px rgba(0,0,0,.25)}
.panel h3{margin:0 0 6px;font-size:clamp(15px,2.2vw,22px);color:#c2410c}
.panel .line{font-size:clamp(18px,3vw,30px);margin:4px 0 10px}
.btns{display:flex;flex-wrap:wrap;gap:8px}
button{font:inherit;font-size:clamp(14px,2vw,19px);border:2px solid var(--ink);background:#fff;border-radius:10px;padding:7px 14px;cursor:pointer}
button.main{background:var(--gold)}
button:disabled{opacity:.5}
.opt{display:block;width:100%;text-align:left;margin:6px 0;font-size:clamp(15px,2.4vw,22px)}
#cover{position:absolute;inset:0;background:var(--paper);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;padding:16px;box-sizing:border-box;text-align:center;overflow:auto}
#cover h1{margin:0;font-size:clamp(24px,5vw,52px)}
#cover p{margin:0;color:var(--muted);font-size:clamp(13px,2vw,18px)}
.roles{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}
.role{border:2.5px solid var(--ink);border-radius:12px;background:#fff;padding:8px 14px;cursor:pointer;min-width:110px}
.role.on{background:var(--gold)}
.role b{display:block;font-size:clamp(18px,3vw,26px)}
.role span{font-size:clamp(12px,1.7vw,15px);color:var(--muted)}
#recap{position:absolute;inset:0;background:var(--paper);padding:3% 5%;box-sizing:border-box;overflow:auto;display:none}
#recap h2{margin:.2em 0;font-size:clamp(20px,3.6vw,36px)}
#recap li{margin:.35em 0;font-size:clamp(14px,2.1vw,20px)}
#bar{display:flex;gap:10px;align-items:center;padding:8px 4px;color:#ddd;font-size:14px}
.rec{color:#c2410c}
@media (max-width:700px),(orientation:portrait){#wrap{padding:0}#stage{border-radius:0;aspect-ratio:auto;overflow:visible;background:#2b2f35}#stage svg{height:auto;background:var(--paper)}.panel{position:static;transform:none;width:100%;border-radius:0;border-width:2px 0}#cover,#recap{position:static;min-height:60vh}.role{min-width:0;flex:1 1 40%}}
</style></head><body><div id="wrap">
<div id="stage"><svg id="svg" viewBox="0 0 %W% %H%" xmlns="http://www.w3.org/2000/svg"></svg>
<div id="cover"><h1>%TITLE%</h1><p>选一个角色：演到你的台词时会停下，你来念；关键时刻，你来决定。</p>
<div class="roles" id="roles"></div><button class="main" id="go">开始</button><p>人物、公司、情节均为虚构 · AI 配音</p></div>
<div id="recap"></div><div id="panel" class="panel" style="display:none"></div></div>
<div id="bar"><button id="pause">暂停</button><span id="where"></span></div></div>
<script>%ROUGH%</script><script>%SCENE%</script>
<script>
const STORY=%STORY%, G=%GAME%;
const svg=document.getElementById('svg'),panel=document.getElementById('panel'),cover=document.getElementById('cover'),recap=document.getElementById('recap');
const DESC={'老马':'销售副总：要给客户一个答复','周敏':'技术负责人：老板不在，谁来拍板','小陈':'测试工程师：第一个发现问题'};
let role=null,node=null,t=0,last=0,playing=false,hold=false,path=[],choices=[],asked={},mine={},audios={},recorder=null,chunks=[];
const roles=document.getElementById('roles');
[...G.roles,'只看不演'].forEach(r=>{const b=document.createElement('div');b.className='role';b.innerHTML=`<b>${r}</b><span>${DESC[r]||'看完整个故事，决定点照样由你选'}</span>`;b.onclick=()=>{[...roles.children].forEach(x=>x.classList.remove('on'));b.classList.add('on');role=r==='只看不演'?'':r;};roles.appendChild(b);});
roles.children[0].click();
function one(n){return Object.assign({},STORY,{shots:[n.shot]});}
function draw(){if(node)svg.innerHTML=WQScene3D.render(one(node),Math.min(t,node.shot.t1-0.001));document.getElementById('where').textContent=role?('你演：'+role):'旁观';}
function stopAudio(){Object.values(audios).forEach(a=>{try{a.pause();}catch(e){}});}
function clipAudio(i){const k=node.id+'#'+i;if(!audios[k]){const c=node.clips[i];const own=mine[c.text];audios[k]=new Audio(own||('data:audio/mpeg;base64,'+c.src));audios[k].own=!!own;}return audios[k];}
function enter(id){stopAudio();audios={};node=G.nodes[id];path.push(id);t=0;last=performance.now();asked={};
  if(node.ending){playing=true;loop();return;}
  playing=true;loop();}
function loop(){if(!playing)return;const now=performance.now();let dt=Math.min(0.1,(now-last)/1000);last=now;
  if(!hold){
    // own line coming up: stop and let the player read it
    (node.clips||[]).forEach((c,i)=>{if(role&&c.who===role&&!asked[i]&&t+dt>=c.t-0.25){asked[i]=true;dt=0;askLine(c,i);}});
    if(!playing)return;
    t+=dt;
    (node.clips||[]).forEach((c,i)=>{const a=clipAudio(i);if(t>=c.t&&t<c.t+c.dur+0.2&&a.paused&&!a.started){a.started=true;a.currentTime=Math.max(0,t-c.t);a.play().catch(()=>{});}
      // a recording longer than the AI line: hold the picture until it ends
      if(a.own&&a.started&&!a.ended&&!a.paused&&t>c.t+c.dur-0.25)t=c.t+c.dur-0.25;});
  }
  if(t>=node.shot.t1){playing=false;return next();}
  draw();requestAnimationFrame(loop);}
function next(){if(node.ending)return showRecap();if(node.choice)return askChoice();enter(node.next);}
function askLine(c,i){playing=false;stopAudio();draw();
  panel.style.display='block';
  const canRec=!!(navigator.mediaDevices&&window.MediaRecorder);
  panel.innerHTML=`<h3>轮到你了（${role}）</h3><div class="line">${c.text}</div><div class="btns">${canRec?'<button class="main" id="rec">录音：念出来</button>':''}<button id="ai">用 AI 声音</button><button id="skip">我念完了，继续</button></div><div id="rs" class="rec"></div>`;
  const resume=()=>{panel.style.display='none';playing=true;last=performance.now();loop();};
  document.getElementById('ai').onclick=resume;
  document.getElementById('skip').onclick=()=>{const k=node.id+'#'+i;audios[k]=new Audio();audios[k].started=true;resume();};
  if(canRec)document.getElementById('rec').onclick=async(e)=>{const b=e.target;
    if(recorder&&recorder.state==='recording'){recorder.stop();return;}
    try{const st=await navigator.mediaDevices.getUserMedia({audio:true});chunks=[];recorder=new MediaRecorder(st);
      recorder.ondataavailable=ev=>chunks.push(ev.data);
      recorder.onstop=()=>{st.getTracks().forEach(x=>x.stop());const url=URL.createObjectURL(new Blob(chunks,{type:recorder.mimeType}));mine[c.text]=url;const k=node.id+'#'+i;delete audios[k];resume();};
      recorder.start();b.textContent='停止录音';document.getElementById('rs').textContent='正在录音……念完点“停止录音”';}
    catch(err){document.getElementById('rs').textContent='没能打开麦克风，可以用 AI 声音，或自己念完点继续。';}};}
function askChoice(){draw();const ch=node.choice;panel.style.display='block';
  const me=role===ch.who;
  panel.innerHTML=`<h3>${me?'你来决定（'+ch.who+'）':'如果你是'+ch.who+'，你会怎么选？'}</h3><div class="line">${ch.prompt}</div>`+ch.options.map((o,i)=>`<button class="opt" data-i="${i}">${String.fromCharCode(65+i)}　${o.text}</button>`).join('');
  panel.querySelectorAll('.opt').forEach(b=>b.onclick=()=>{const o=ch.options[+b.dataset.i];choices.push({who:ch.who,prompt:ch.prompt,text:o.text,note:o.note});panel.style.display='none';enter(o.next);});}
function showRecap(){stopAudio();const e=node.ending;recap.style.display='block';
  recap.innerHTML=`<h2>${e.title}</h2><p>${e.text}</p><h3>你的选择</h3><ol>${choices.map(c=>`<li><b>${c.who}：</b>${c.text}<br><span style="color:#5f6b76">→ ${c.note}</span></li>`).join('')}</ol><h3>这个故事想说的道理</h3><ul>${G.lessons.map(l=>`<li>${l}</li>`).join('')}</ul><div class="btns"><button class="main" id="again">换个选择，再来一次</button><button id="other">换个角色</button></div>`;
  document.getElementById('again').onclick=()=>start(role);document.getElementById('other').onclick=()=>{recap.style.display='none';cover.style.display='flex';};}
function start(r){role=r;path=[];choices=[];mine={};recap.style.display='none';cover.style.display='none';panel.style.display='none';enter(G.start);}
document.getElementById('go').onclick=()=>start(role);
document.getElementById('pause').onclick=(e)=>{if(!node||panel.style.display==='block')return;if(playing){playing=false;stopAudio();e.target.textContent='继续';}else{playing=true;last=performance.now();e.target.textContent='暂停';Object.values(audios).forEach(a=>{if(a.started&&!a.ended&&a.src)a.play().catch(()=>{});});loop();}};
// for automatic checks: jump into a node at a time
window.TEST={skipTo(id,tt){stopAudio();playing=false;if(!node||node.id!==id){node=G.nodes[id];path.push(id);audios={};asked={};}t=Math.min(tt,node.shot.t1);
  if(t>=node.shot.t1){if(node.ending)return showRecap();if(node.choice)return askChoice();return;}
  const c=(node.clips||[]).findIndex(c=>role&&c.who===role&&c.t>=t-0.3&&c.t<t+0.6);if(c>=0){t=node.clips[c].t-0.25;asked[c]=true;askLine(node.clips[c],c);}else draw();}};
document.fonts.ready.then(()=>{});
</script></body></html>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--voice", default="kokoro", choices=["kokoro", "estimate"])
    ap.add_argument("--snap", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        P, _, _ = load(Path(a.dir))
        ps = paths(P)
        ends = {p[-1] for p in ps}
        print(f"{len(ps)} 条路径，{len(ends)} 个结局：{sorted(ends)}")
    else:
        build(Path(a.dir), a.voice, a.snap)
