// 白板课编辑器（第 35 轮）：左边讲稿分段，中间 Excalidraw 画板。打开方式：learn.…/wb-editor/?id=<白板课编号>
// 接口在网关 /api/v1/whiteboards/<id>（GET 读、PUT 存、compile 预览、revoice 重新配音、redo 请 AI 重排、upload 换录音或
// 上传视频、mp4 出视频、media 可插入的素材）。登录凭据与平台网页端相同（同一个网址下的 wq.token）。
import React, { useEffect, useMemo, useRef, useState, useCallback } from "react";
import { createRoot } from "react-dom/client";
import { Excalidraw, convertToExcalidrawElements, MainMenu } from "@excalidraw/excalidraw";
import "@excalidraw/excalidraw/index.css";

const W = 1920, H = 1080;
const ID = new URLSearchParams(location.search).get("id") || "";
const API = "/api/v1/whiteboards/" + encodeURIComponent(ID);
const BACK = "/pages/whiteboard/whiteboard";
const ERR = { busy: "这节课正在处理，请等这一步做完再试", forbidden: "这不是你的白板课", not_found: "找不到这节白板课",
  not_ready: "这节课还没做好", teacher_recording: "这节课用的是你的录音，要改声音请换录音", mp4_unavailable: "平台还没有开出视频的服务",
  too_large: "文件太大", bad_file: "文件类型不对", ai_unavailable: "平台还没有配置 AI 模型", link_expired: "链接过期了，请刷新页面" };
const fmt = (s) => Math.floor(s / 60) + ":" + String(Math.floor(s % 60)).padStart(2, "0");

function token() {
  try {
    const raw = localStorage.getItem("wq.token") || "";
    try { const v = JSON.parse(raw); return (v && typeof v === "object" ? v.data : v) || ""; } catch { return raw; }
  } catch { return ""; }
}

async function call(path, opts = {}) {
  const headers = { Authorization: "Bearer " + token(), ...(opts.json !== undefined ? { "content-type": "application/json" } : {}) };
  const r = await fetch(API + path, { method: opts.method || (opts.json !== undefined || opts.body ? "POST" : "GET"), headers,
    body: opts.json !== undefined ? JSON.stringify(opts.json) : opts.body });
  if (r.status === 401) { location.href = "/pages/login/login"; throw new Error("请先登录"); }
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(ERR[d && d.error] || (d && (d.detail || d.error)) || ("出错了 " + r.status));
  return d;
}

// chunked upload (≤ 60 MB a piece), like the platform's recording upload
async function uploadFile(kind, file, onPart) {
  const CH = 60 * 1024 * 1024, total = Math.max(1, Math.ceil(file.size / CH));
  const up = Array.from(crypto.getRandomValues(new Uint8Array(8))).map((b) => b.toString(16).padStart(2, "0")).join("");
  let last;
  for (let i = 0; i < total; i++) {
    onPart && onPart(i, total);
    const q = `?kind=${kind}&upload=${up}&index=${i}&total=${total}&name=${encodeURIComponent(file.name)}`;
    last = await call("/upload" + q, { body: file.slice(i * CH, (i + 1) * CH), method: "POST" });
  }
  return last;
}

// effective segment of every element: its own customData.wq_at, else the previous element's (same rule as the compiler)
function bindings(elements) {
  const out = {};
  let at = 0;
  for (const e of elements) {
    if (e.isDeleted || e.type === "frame") continue;
    const v = e.customData && e.customData.wq_at;
    if (Number.isInteger(v)) at = v;
    out[e.id] = at;
  }
  return out;
}

function App() {
  const [api, setApi] = useState(null);
  const [lesson, setLesson] = useState(null);
  const [segs, setSegs] = useState([]);
  const [cur, setCur] = useState(0);
  const [tick, setTick] = useState(0);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState("");
  const [preview, setPreview] = useState(null);
  const [panel, setPanel] = useState("");      // "", "media", "redo"
  const [failed, setFailed] = useState("");
  const curRef = useRef(0);
  curRef.current = cur;
  const dirty = useRef(false);
  const sig = useRef("");

  // open the lesson; while the platform is still making it, show its progress
  const open = useCallback(async () => {
    try {
      const L = await call("");
      setLesson(L);
      if (L.job || L.state === "making" || L.state === "waiting") return;
      setSegs(L.segments);
    } catch (e) { setFailed(e.message); }
  }, []);
  useEffect(() => { if (!ID) setFailed("没有指定白板课"); else open(); }, [open]);
  useEffect(() => { fetch("/api/v1/whiteboards/assets/pen.svg").then((r) => (r.ok ? r.text() : "")).then((t) => { if (t) window.WB_PEN = t; }).catch(() => {}); }, []);
  const fitted = useRef(false);
  useEffect(() => {
    if (!lesson || !(lesson.job && !lesson.scene)) return;
    const t = setTimeout(open, 2500);
    return () => clearTimeout(t);
  }, [lesson, open]);
  useEffect(() => {
    const warn = (e) => { if (dirty.current) { e.preventDefault(); e.returnValue = ""; } };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, []);

  const elements = () => (api ? api.getSceneElements() : []);
  const bind = useMemo(() => bindings(api ? api.getSceneElementsIncludingDeleted() : (lesson && lesson.scene ? lesson.scene.elements : [])), [api, lesson, tick]);
  const counts = useMemo(() => { const c = {}; Object.values(bind).forEach((a) => { c[a] = (c[a] || 0) + 1; }); return c; }, [bind]);

  // new elements: draw them during the segment that is selected on the left
  const onChange = useCallback((els) => {
    if (!api) return;
    if (!fitted.current && els.length) {     // show the first board whole when the editor opens
      fitted.current = true;
      const f = els.find((e) => e.type === "frame" && !e.isDeleted);
      if (f) setTimeout(() => api.scrollToContent([f], { fitToViewport: true, viewportZoomFactor: 0.9 }), 60);
    }
    const fresh = els.filter((e) => !e.isDeleted && e.type !== "frame" && !(e.customData && Number.isInteger(e.customData.wq_at)));
    if (fresh.length) {
      const ids = new Set(fresh.map((e) => e.id));
      api.updateScene({ elements: els.map((e) => (ids.has(e.id) ? { ...e, customData: { ...(e.customData || {}), wq_at: curRef.current } } : e)) });
    }
    // Excalidraw calls onChange on every pointer move: refresh the counts only when the drawing itself changed
    let v = 0;
    for (const e of els) v += e.version;
    const s = els.length + ":" + v;
    if (s !== sig.current) { if (sig.current) dirty.current = true; sig.current = s; setTick((t) => t + 1); }
  }, [api]);

  const picked = useRef("");
  function pick(i) {
    setCur(i);
    if (!api) return;
    // the teacher selected something on the board by hand: keep it, so it can be moved to the segment just clicked
    const sel = api.getAppState().selectedElementIds || {};
    const selNow = Object.keys(sel).filter((k) => sel[k]).sort().join(",");
    if (selNow && selNow !== picked.current) {
      setMsg(`选中的 ${selNow.split(",").length} 样还在——点下面的按钮把它们放到第 ${i + 1} 段`);
      return;
    }
    const b = bindings(api.getSceneElementsIncludingDeleted());
    const mine = elements().filter((e) => b[e.id] === i);
    if (mine.length) {
      api.updateScene({ appState: { selectedElementIds: Object.fromEntries(mine.map((e) => [e.id, true])) } });
      picked.current = mine.map((e) => e.id).sort().join(",");
      const frame = elements().find((e) => e.id === mine[0].frameId);
      api.scrollToContent(frame ? [frame] : mine, { fitToViewport: true, viewportZoomFactor: 0.9, animate: true });
    } else {
      api.updateScene({ appState: { selectedElementIds: {} } });
      picked.current = "";
    }
  }

  function moveSelected() {
    const sel = api.getAppState().selectedElementIds;
    const ids = Object.keys(sel).filter((k) => sel[k]);
    if (!ids.length) { setMsg("先在画板上选中要放到这一段的东西"); return; }
    const set = new Set(ids);
    // also fix the element after each moved one, so elements that inherited the old segment keep it
    const all = api.getSceneElementsIncludingDeleted();
    const before = bindings(all);
    api.updateScene({ elements: all.map((e) => {
      if (e.type === "frame") return e;
      if (set.has(e.id)) return { ...e, customData: { ...(e.customData || {}), wq_at: cur } };
      return { ...e, customData: { ...(e.customData || {}), wq_at: before[e.id] ?? 0 } };
    }) });
    setMsg(`已把 ${ids.length} 样东西放到第 ${cur + 1} 段`);
    picked.current = ids.sort().join(",");
    setTick((t) => t + 1);
  }

  // the board the selected segment draws on (for “请 AI 重排这张” and for inserting)
  function currentFrame() {
    const b = bindings(api.getSceneElementsIncludingDeleted());
    const mine = elements().filter((e) => b[e.id] === cur && e.frameId);
    const frames = elements().filter((e) => e.type === "frame");
    if (mine.length) return frames.find((f) => f.id === mine[0].frameId) || null;
    // nothing drawn in this segment: the board of the nearest earlier segment
    let best = null, bestAt = -1;
    for (const e of elements()) { if (e.frameId && b[e.id] <= cur && b[e.id] > bestAt) { bestAt = b[e.id]; best = e.frameId; } }
    return frames.find((f) => f.id === best) || frames[0] || null;
  }

  function addBoard() {
    const frames = elements().filter((e) => e.type === "frame");
    const x = frames.length ? Math.max(...frames.map((f) => f.x)) + 2200 : 0;
    const f = convertToExcalidrawElements([{ type: "frame", x, y: 0, width: W, height: H, name: `画板 ${frames.length + 1}`, children: [] }]);
    api.updateScene({ elements: [...api.getSceneElementsIncludingDeleted(), ...f] });
    api.scrollToContent(f, { fitToViewport: true, viewportZoomFactor: 0.9, animate: true });
  }

  function insertMedia(m) {
    const f = currentFrame();
    const fx = f ? f.x : 0, fy = f ? f.y : 0;
    const box = convertToExcalidrawElements([
      { type: "rectangle", x: fx + 980, y: fy + 330, width: 800, height: 450, strokeColor: "#5f6b76", strokeWidth: 2, roughness: 1,
        customData: { wq_at: cur, wq_media: { src: m.src, label: m.title } } },
      { type: "text", x: fx + 980, y: fy + 270, text: (m.kind || "") + "：" + m.title.slice(0, 24), fontSize: 28, strokeColor: "#5f6b76",
        customData: { wq_at: cur } },
    ]).map((e) => (f ? { ...e, frameId: f.id } : e));
    api.updateScene({ elements: [...api.getSceneElementsIncludingDeleted(), ...box] });
    api.scrollToContent(f ? [f] : box, { fitToViewport: true, viewportZoomFactor: 0.9, animate: true });
    setPanel("");
    setMsg(`已插入“${m.title}”，讲到第 ${cur + 1} 段时开始播放；拖动框可以改位置和大小`);
  }

  const scene = () => ({ type: "excalidraw", version: 2, elements: api.getSceneElementsIncludingDeleted().filter((e) => !e.isDeleted),
    appState: { viewBackgroundColor: "#fdfcf8" }, files: api.getFiles() });

  async function save(quiet) {
    if (!quiet) setBusy("保存中…");
    try {
      const L = await call("", { method: "PUT", json: { title: lesson.title.zh, segments: segs.map((s) => ({ zh: s.zh })), scene: scene() } });
      dirty.current = false;
      setLesson((x) => ({ ...x, ...L, scene: x.scene }));
      if (!quiet) setMsg(L.voice_stale ? "已保存。讲稿改过了，点“重新配音”让声音跟上" : "已保存");
      return L;
    } catch (e) { setMsg("保存没成功：" + e.message); throw e; }
    finally { if (!quiet) setBusy(""); }
  }

  async function doPreview() {
    setBusy("准备预览…");
    try {
      const data = await call("/compile", { json: { segments: segs.map((s) => ({ zh: s.zh })), scene: scene() } });
      setPreview({ data, from: segs[cur] ? Math.max(0, segs[cur].t0 - 0.3) : 0 });
    } catch (e) { setMsg("预览没成功：" + e.message); }
    setBusy("");
  }

  // a background job on the server (revoice, redo, new recording, MP4): wait for it, then reload what changed
  async function follow(start, label, after) {
    try {
      let L = await start();
      while (L.job) {
        setBusy(L.job.label + (L.job.progress ? ` ${L.job.progress}%` : "") + "…");
        await new Promise((ok) => setTimeout(ok, 2500));
        L = await call("");
      }
      setBusy("");
      if (L.error) { setMsg(L.error); return; }
      after && after(L);
      setLesson(L);
    } catch (e) { setBusy(""); setMsg(label + "没成功：" + e.message); }
  }

  const reloadScene = (L) => {
    setSegs(L.segments);
    api.updateScene({ elements: L.scene.elements });
    dirty.current = false;
    setTick((t) => t + 1);
  };

  async function revoice() {
    await save(true);
    follow(() => call("/revoice", { json: {} }), "重新配音", (L) => { setSegs(L.segments); setMsg("配音好了：时间按新的声音排好了"); });
  }

  async function redo(note, whole) {
    setPanel("");
    if (dirty.current) await save(true);
    const f = whole ? null : currentFrame();
    follow(() => call("/redo", { json: { note, frame: f ? f.id : "" } }), "AI 重排",
      (L) => { reloadScene(L); setMsg(whole ? "AI 重排了整节课的画板" : "AI 重排了这张画板"); });
  }

  async function render() {
    if (dirty.current) await save(true);
    follow(() => call("/mp4", { json: {} }), "出视频", (L) => setMsg(<span>视频好了：<a href={L.video} download>下载 MP4</a></span>));
  }

  async function uploadAudio(ev) {
    const f = ev.target.files[0];
    ev.target.value = "";
    if (!f) return;
    if (dirty.current) await save(true);
    follow(() => uploadFile("recording", f, (i, n) => setBusy(`上传录音 ${i + 1}/${n}…`)), "换录音",
      (L) => { reloadScene(L); setMsg(`新录音切成了 ${L.segments.length} 段，画板按文字对上了新时间；请校对左边的文字`); });
  }

  if (failed) return <div className="loading">打不开这节白板课：{failed} <a href={BACK}>回到白板课</a></div>;
  if (!lesson) return <div className="loading">正在打开白板课…</div>;
  if (!lesson.scene) return (
    <div className="loading">
      <h2>{lesson.title.zh}</h2>
      {lesson.state === "waiting" ? <p>等你上传讲课录音（在白板课列表里新建时上传）。</p>
        : lesson.error ? <p className="err">{lesson.error}</p>
        : <p>平台正在做这节课：{lesson.job ? lesson.job.label : "排队中"}{lesson.job && lesson.job.progress ? ` ${lesson.job.progress}%` : ""}……做好后这里自动打开。</p>}
      <a href={BACK}>← 回到白板课</a>
    </div>
  );
  const changedText = lesson.segments && segs.some((s, i) => lesson.segments[i] && s.zh !== lesson.segments[i].zh);
  return (
    <div className="wb">
      <header>
        <a className="back" href={BACK} title="回到白板课列表">←</a>
        <input className="title" value={lesson.title.zh} onChange={(e) => { dirty.current = true; setLesson({ ...lesson, title: { ...lesson.title, zh: e.target.value } }); }} />
        <span className="msg">{busy || msg}</span>
        <button className="btn ghost" onClick={() => setPanel(panel === "media" ? "" : "media")}>插入</button>
        <button className="btn ghost" onClick={() => setPanel(panel === "redo" ? "" : "redo")}>请 AI 重排</button>
        <label className="btn ghost">换录音<input type="file" accept="audio/*,video/mp4,.m4a,.mp3,.wav" onChange={uploadAudio} hidden /></label>
        <button className="btn ghost" onClick={doPreview}>▶ 预览</button>
        {lesson.play && <a className="btn ghost" href={lesson.play} target="_blank" rel="noopener">网页版</a>}
        <button className="btn ghost" onClick={render} disabled={!!busy}>出视频</button>
        {lesson.video && <a className="btn ghost" href={lesson.video} download>下载 MP4</a>}
        <button className="btn" onClick={() => save(false)} disabled={!!busy}>保存</button>
      </header>
      <div className="body">
        <aside>
          <div className="aside-head">讲稿 · {segs.length} 段<small>点一段：画板跳过去，选中这段要画的东西</small></div>
          <ol>
            {segs.map((s, i) => (
              <li key={i} className={i === cur ? "on" : ""} onClick={() => pick(i)}>
                <span className="t">{fmt(s.t0)}</span>
                <textarea rows={Math.min(4, Math.ceil(s.zh.length / 16))} value={s.zh}
                  onChange={(e) => { dirty.current = true; setSegs(segs.map((x, j) => (j === i ? { ...x, zh: e.target.value } : x))); }} />
                <span className={"n" + (counts[i] ? "" : " zero")} title="这段要画几样">{counts[i] || 0}</span>
              </li>
            ))}
          </ol>
          <div className="aside-foot">
            <button className="btn" onClick={moveSelected}>把选中的放到第 {cur + 1} 段</button>
            <button className="btn ghost" onClick={addBoard}>＋ 新画板</button>
            {lesson.audio_kind !== "teacher" && (changedText || lesson.voice_stale) &&
              <button className="btn gold" onClick={revoice} disabled={!!busy}>重新配音</button>}
            <small>新画的东西自动放到当前选中的这段{lesson.moves ? `；AI 加的 ${lesson.moves} 个动作跟着元素走` : ""}</small>
          </div>
        </aside>
        <main>
          <Excalidraw excalidrawAPI={(a) => { window.WBAPI = a; setApi(a); }}
            initialData={{ elements: lesson.scene.elements, files: lesson.scene.files || {}, appState: { viewBackgroundColor: "#fdfcf8", currentItemFontFamily: 5 }, scrollToContent: true }}
            langCode="zh-CN" onChange={onChange}>
            <MainMenu><MainMenu.DefaultItems.ToggleTheme /><MainMenu.DefaultItems.ChangeCanvasBackground /></MainMenu>
          </Excalidraw>
          {panel === "media" && <MediaPanel seg={cur} onPick={insertMedia} onClose={() => setPanel("")} setBusy={setBusy} />}
          {panel === "redo" && <RedoPanel seg={cur} onRedo={redo} onClose={() => setPanel("")} />}
        </main>
      </div>
      {preview && <Preview data={preview.data} from={preview.from} audio={lesson.audio} onClose={() => setPreview(null)} />}
    </div>
  );
}

function MediaPanel({ seg, onPick, onClose, setBusy }) {
  const [list, setList] = useState(null);
  const [err, setErr] = useState("");
  const [q, setQ] = useState("");
  const load = () => call("/media").then((d) => setList(d.media)).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);
  async function upload(ev) {
    const f = ev.target.files[0];
    ev.target.value = "";
    if (!f) return;
    try {
      const r = await uploadFile("video", f, (i, n) => setBusy(`上传视频 ${i + 1}/${n}…`));
      setBusy("");
      onPick({ src: r.src, title: r.title, kind: "视频" });
    } catch (e) { setBusy(""); setErr("上传没成功：" + e.message); }
  }
  return (
    <div className="panel">
      <div className="ph"><b>插入到第 {seg + 1} 段</b><button className="x" onClick={onClose}>×</button></div>
      <p className="hint">先画一个框，讲到这一段时框里开始播放；虚拟实验在网页版里可以当场操作。</p>
      <label className="btn ghost">上传一段视频（mp4）<input type="file" accept="video/mp4,video/webm" onChange={upload} hidden /></label>
      {err && <p className="err">{err}</p>}
      <input className="search" placeholder="搜索实验、动画（按名字）" value={q} onChange={(e) => setQ(e.target.value)} />
      {!list ? <p className="hint">正在列出……</p> : !list.length ? <p className="hint">还没有可插入的实验和动画。</p> : (
        <ul>{list.filter((m) => !q || (m.title + m.from + m.kind).toLowerCase().includes(q.toLowerCase())).slice(0, 120).map((m) =>
          <li key={m.src} onClick={() => onPick(m)}><span className="k">{m.kind}</span>{m.title}<small>{m.from}</small></li>)}</ul>
      )}
    </div>
  );
}

function RedoPanel({ seg, onRedo, onClose }) {
  const [note, setNote] = useState("");
  return (
    <div className="panel">
      <div className="ph"><b>请 AI 重排</b><button className="x" onClick={onClose}>×</button></div>
      <p className="hint">说说要怎么改，比如“太挤了，分成两张”“这里画受力图”“把实验放大”。不写也行。</p>
      <textarea rows={4} value={note} onChange={(e) => setNote(e.target.value)} placeholder="你的意见（可不填）" />
      <div className="row">
        <button className="btn" onClick={() => onRedo(note, false)}>重排第 {seg + 1} 段所在的这张</button>
        <button className="btn ghost" onClick={() => { if (confirm("整节课的画板都会换成 AI 新排的，你手动改过的地方会丢掉。继续吗？")) onRedo(note, true); }}>重排整节</button>
      </div>
    </div>
  );
}

function Preview({ data, from, audio, onClose }) {
  const host = useRef(null), aud = useRef(null);
  const [t, setT] = useState(from);
  useEffect(() => {
    const svg = host.current;
    svg.innerHTML = window.WB_PEN || "";
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    svg.insertBefore(g, svg.firstChild);
    window.WB.init(g, data);
    const a = aud.current;
    a.currentTime = from;
    let raf;
    const loop = () => { window.WB_PLAYING = !a.paused; window.WB.seek(a.currentTime); setT(a.currentTime); raf = requestAnimationFrame(loop); };
    a.play().catch(() => {});
    loop();
    return () => { cancelAnimationFrame(raf); a.pause(); window.WB_PLAYING = false; const l = document.getElementById("wbmedia"); if (l) l.remove(); };
  }, [data]);
  return (
    <div className="preview" onClick={onClose}>
      <div className="pv" onClick={(e) => e.stopPropagation()}>
        <div id="stage"><svg ref={host} viewBox={`0 0 ${W} ${H}`} /></div>
        <div className="pvbar">
          <button className="btn ghost" onClick={() => { const a = aud.current; a.paused ? a.play() : a.pause(); }}>播放 / 暂停</button>
          <input type="range" min={0} max={data.total} step={0.1} value={t} onChange={(e) => { aud.current.currentTime = +e.target.value; }} />
          <span>{fmt(t)} / {fmt(data.total)}</span>
          <button className="btn" onClick={onClose}>关闭</button>
        </div>
        <audio ref={aud} src={audio} preload="auto" />
      </div>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
