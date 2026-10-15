// 白板课编辑器（第 35 轮第 2 步）：左边讲稿分段，中间 Excalidraw 画板。
// 后端接口（样板页由 serve.py 提供，接进平台后由网关提供，路径不变）：
//   GET  {API}/lesson   → {title, segments:[{t0,t1,zh}], audio, scene}
//   POST {API}/save     ← {title, segments, scene}
//   POST {API}/compile  ← {segments, scene}            → 播放数据（预览）
//   POST {API}/audio    ← 录音文件                       → {segments}（语音识别切段）
//   POST {API}/render   ← {segments, scene}             → {job}；GET {API}/render/{job} → {state, url}
import React, { useEffect, useMemo, useRef, useState, useCallback } from "react";
import { createRoot } from "react-dom/client";
import { Excalidraw, convertToExcalidrawElements, MainMenu } from "@excalidraw/excalidraw";
import "@excalidraw/excalidraw/index.css";

const API = window.WB_API || "api";
const W = 1920, H = 1080;
const fmt = (s) => Math.floor(s / 60) + ":" + String(Math.floor(s % 60)).padStart(2, "0");

// effective segment of every element: its own customData.wq_at, else the previous element's (same rule as wb.py)
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
  const curRef = useRef(0);
  curRef.current = cur;
  const dirty = useRef(false);
  const sig = useRef("");

  useEffect(() => {
    fetch(API + "/lesson").then((r) => r.json()).then((L) => { setLesson(L); setSegs(L.segments); });
  }, []);

  const elements = () => (api ? api.getSceneElements() : []);
  const bind = useMemo(() => bindings(api ? api.getSceneElementsIncludingDeleted() : (lesson ? lesson.scene.elements : [])), [api, lesson, tick]);
  const counts = useMemo(() => { const c = {}; Object.values(bind).forEach((a) => { c[a] = (c[a] || 0) + 1; }); return c; }, [bind]);

  // new elements: draw them during the segment that is selected on the left
  const onChange = useCallback((els) => {
    if (!api) return;
    const fresh = els.filter((e) => !e.isDeleted && e.type !== "frame" && !(e.customData && Number.isInteger(e.customData.wq_at)));
    if (fresh.length) {
      const ids = new Set(fresh.map((e) => e.id));
      api.updateScene({ elements: els.map((e) => (ids.has(e.id) ? { ...e, customData: { ...(e.customData || {}), wq_at: curRef.current } } : e)) });
    }
    // Excalidraw calls onChange on every pointer move: refresh the counts only when the drawing itself changed
    let v = 0;
    for (const e of els) v += e.version;
    const s = els.length + ":" + v;
    if (s !== sig.current) { sig.current = s; dirty.current = true; setTick((t) => t + 1); }
  }, [api]);

  const picked = useRef("");
  function pick(i) {
    setCur(i);
    if (!api) return;
    // the teacher selected something on the board by hand: keep it, so it can be moved to the segment just clicked
    const selNow = Object.keys(api.getAppState().selectedElementIds || {}).filter((k) => api.getAppState().selectedElementIds[k]).sort().join(",");
    if (selNow && selNow !== picked.current) {
      setMsg(`选中的 ${selNow.split(",").length} 样还在——点下面的按钮把它们放到第 ${i + 1} 段`);
      return;
    }
    const b = bindings(api.getSceneElementsIncludingDeleted());
    const mine = elements().filter((e) => b[e.id] === i);
    if (mine.length) {
      api.updateScene({ appState: { selectedElementIds: Object.fromEntries(mine.map((e) => [e.id, true])) } });
      picked.current = mine.map((e) => e.id).sort().join(",");
      // show the whole board the segment draws on
      const fid = mine[0].frameId;
      const frame = elements().find((e) => e.id === fid);
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
    const next = all.map((e) => {
      if (e.type === "frame") return e;
      if (set.has(e.id)) return { ...e, customData: { ...(e.customData || {}), wq_at: cur } };
      return { ...e, customData: { ...(e.customData || {}), wq_at: before[e.id] ?? 0 } };
    });
    api.updateScene({ elements: next });
    setMsg(`已把 ${ids.length} 样东西放到第 ${cur + 1} 段`);
    picked.current = ids.sort().join(",");
    setTick((t) => t + 1);
  }

  function addBoard() {
    const frames = elements().filter((e) => e.type === "frame");
    const x = frames.length ? Math.max(...frames.map((f) => f.x)) + 2200 : 0;
    const f = convertToExcalidrawElements([{ type: "frame", x, y: 0, width: W, height: H, name: `画板 ${frames.length + 1}`, children: [] }]);
    api.updateScene({ elements: [...api.getSceneElementsIncludingDeleted(), ...f] });
    api.scrollToContent(f, { fitToViewport: true, viewportZoomFactor: 0.9, animate: true });
  }

  const scene = () => ({ type: "excalidraw", version: 2, elements: api.getSceneElementsIncludingDeleted().filter((e) => !e.isDeleted),
    appState: { viewBackgroundColor: "#fdfcf8" }, files: api.getFiles() });

  async function post(path, body) {
    const r = await fetch(API + path, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  }

  async function save() {
    setBusy("保存中…");
    try { await post("/save", { title: lesson.title, segments: segs, scene: scene() }); dirty.current = false; setMsg("已保存"); }
    catch (e) { setMsg("保存没成功：" + e.message); }
    setBusy("");
  }

  async function doPreview() {
    setBusy("准备预览…");
    try { const data = await post("/compile", { segments: segs, scene: scene() }); setPreview({ data, from: segs[cur] ? segs[cur].t0 : 0 }); }
    catch (e) { setMsg("预览没成功：" + e.message); }
    setBusy("");
  }

  async function render() {
    setBusy("排队出视频…");
    try {
      const { job } = await post("/render", { segments: segs, scene: scene() });
      const poll = async () => {
        const s = await (await fetch(API + "/render/" + job)).json();
        if (s.state === "done") { setBusy(""); setMsg(<span>视频好了：<a href={s.url} download>下载 MP4</a></span>); }
        else if (s.state === "failed") { setBusy(""); setMsg("出视频没成功：" + (s.error || "")); }
        else { setBusy(`出视频中… ${s.progress || 0}%`); setTimeout(poll, 3000); }
      };
      poll();
    } catch (e) { setBusy(""); setMsg("出视频没成功：" + e.message); }
  }

  async function uploadAudio(ev) {
    const f = ev.target.files[0];
    if (!f) return;
    setBusy("语音识别中…（大约录音长度的十分之一）");
    try {
      const fd = new FormData(); fd.append("file", f);
      const r = await fetch(API + "/audio", { method: "POST", body: fd });
      if (!r.ok) throw new Error(await r.text());
      const res = await r.json();
      setSegs(res.segments);
      if (res.scene) api.updateScene({ elements: res.scene.elements });
      setLesson((L) => ({ ...L, audio: res.audio }));
      setMsg(`新录音已切成 ${res.segments.length} 段，画板按文字对上了新时间；请校对左边的文字`);
    } catch (e) { setMsg("录音没处理成功：" + e.message); }
    setBusy("");
    ev.target.value = "";
  }

  if (!lesson) return <div className="loading">正在打开白板课…</div>;
  return (
    <div className="wb">
      <header>
        <b className="title">{lesson.title}</b>
        <span className="msg">{busy || msg}</span>
        <label className="btn ghost">换录音<input type="file" accept="audio/*,video/mp4" onChange={uploadAudio} hidden /></label>
        <button className="btn ghost" onClick={doPreview}>▶ 预览</button>
        <button className="btn ghost" onClick={render}>出视频</button>
        <button className="btn" onClick={save}>保存</button>
      </header>
      <div className="body">
        <aside>
          <div className="aside-head">讲稿 · {segs.length} 段<small>点一段：画板跳过去，选中这段要画的东西</small></div>
          <ol>
            {segs.map((s, i) => (
              <li key={i} className={i === cur ? "on" : ""} onClick={() => pick(i)}>
                <span className="t">{fmt(s.t0)}</span>
                <textarea rows={Math.min(4, Math.ceil(s.zh.length / 16))} value={s.zh}
                  onChange={(e) => setSegs(segs.map((x, j) => (j === i ? { ...x, zh: e.target.value } : x)))} />
                <span className={"n" + (counts[i] ? "" : " zero")} title="这段要画几样">{counts[i] || 0}</span>
              </li>
            ))}
          </ol>
          <div className="aside-foot">
            <button className="btn" onClick={moveSelected}>把选中的放到第 {cur + 1} 段</button>
            <button className="btn ghost" onClick={addBoard}>＋ 新画板</button>
            <small>新画的东西自动放到当前选中的这段</small>
          </div>
        </aside>
        <main>
          <Excalidraw excalidrawAPI={(a) => { window.WBAPI = a; setApi(a); }} initialData={{ elements: lesson.scene.elements, appState: { viewBackgroundColor: "#fdfcf8", currentItemFontFamily: 5 }, scrollToContent: true }}
            langCode="zh-CN" onChange={onChange}>
            <MainMenu><MainMenu.DefaultItems.ToggleTheme /><MainMenu.DefaultItems.ChangeCanvasBackground /></MainMenu>
          </Excalidraw>
        </main>
      </div>
      {preview && <Preview data={preview.data} from={preview.from} audio={lesson.audio} onClose={() => setPreview(null)} />}
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
    const loop = () => { window.WB.seek(a.currentTime); setT(a.currentTime); raf = requestAnimationFrame(loop); };
    a.play().catch(() => {});
    loop();
    return () => { cancelAnimationFrame(raf); a.pause(); };
  }, [data]);
  return (
    <div className="preview" onClick={onClose}>
      <div className="pv" onClick={(e) => e.stopPropagation()}>
        <svg ref={host} viewBox={`0 0 ${W} ${H}`} />
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
