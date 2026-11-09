// 网页审图（第 113 轮 P6）：KiCanvas 看图；问题来自服务器上已生成的报告；自己的文件只在浏览器里读，不上传
"use strict";
const T = {
  zh: {brand: "问渠电子", desk: "网页审图", toDesk: "起草台", pcba: "问渠贴片", help: "帮助",
    title: "不装软件，看原理图和板子", lede: "选一块示例板子，旁边列出它报告里没通过的项，点一条，板子上就跳到那个位置。也可以打开自己电脑上的 KiCad 文件：文件只在浏览器里打开，不上传。",
    design: "示例设计", local: "打开自己的 KiCad 文件（原理图、板子，可多选）", board: "板子", sch: "原理图",
    kicanvas: "看图用的是 KiCanvas（开源，MIT 许可）。滚轮缩放，拖动平移。", issues: "报告里没通过的项",
    noReport: "自己的文件这里不做检查：要检查，请用问渠贴片上传资料包，或在 KiCad 插件里跑。",
    pass: "通过", fail: "不通过", pending: "待核对", unknown: "未知", loading: "读文件……", localOpen: "已在浏览器里打开 {n} 个文件（没有上传）",
    noBoard: "没有板子文件", noSch: "没有原理图文件", limit: "限", none: "没有没通过的项", notFound: "板子上没找到 {r}"},
  en: {brand: "WenQuest Electronics", desk: "Web review", toDesk: "Drafting desk", pcba: "PCBA (factory)", help: "Help",
    title: "Review schematics and boards without installing anything", lede: "Pick an example board; the open items from its report are listed beside it, and clicking one jumps to its place on the board. You can also open KiCad files from your computer: they are opened in your browser and never uploaded.",
    design: "Example design", local: "Open your own KiCad files (schematics, board; several at once)", board: "Board", sch: "Schematic",
    kicanvas: "Viewer: KiCanvas (open source, MIT). Scroll to zoom, drag to pan.", issues: "Open items in the report",
    noReport: "Your own files are not checked here: upload a data pack to WenQuest PCBA, or run the KiCad plugin.",
    pass: "pass", fail: "fail", pending: "pending", unknown: "unknown", loading: "Loading…", localOpen: "{n} files opened in your browser (nothing uploaded)",
    noBoard: "No board file", noSch: "No schematic file", limit: "limit", none: "Nothing open", notFound: "{r} is not on the board"},
};
let lang = (localGet("eda.lang") || (location.hostname.endsWith("wenquestech.online") ? "zh" : "en")) === "en" ? "en" : "zh";   // 美国站默认英文（第 129 轮）
let DESIGNS = [], REPORT = null, sel = null;
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
function localGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function localSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* 不记也行 */ } }
const t = k => T[lang][k];

function applyLang() {
  document.documentElement.lang = lang === "en" ? "en" : "zh-CN";
  document.querySelectorAll("[data-t]").forEach(el => { el.textContent = t(el.dataset.t); });
  $("#lang").textContent = lang === "en" ? "中文" : "EN";
  document.title = `${t("brand")} · ${t("desk")}`;
  if (REPORT) renderIssues();
}

function status(msg) { $("#status").textContent = msg || ""; }

// 一个 KiCanvas 查看器：urls = 服务器上的文件；files = 浏览器里读到的 {name, text}（不上传）
function mount(paneId, urls, files) {
  const pane = $("#" + paneId);
  pane.innerHTML = "";
  if (!urls.length && !files.length) { pane.innerHTML = `<p class="hint" style="color:#ccc;padding:12px">${esc(t(paneId === "pcb" ? "noBoard" : "noSch"))}</p>`; return; }
  const k = document.createElement("kicanvas-embed");
  k.setAttribute("controls", "full");
  urls.forEach(u => { const s = document.createElement("kicanvas-source"); s.setAttribute("src", u); k.appendChild(s); });
  files.forEach(f => { const s = document.createElement("kicanvas-source"); s.setAttribute("name", f.name); s.textContent = f.text; k.appendChild(s); });
  pane.appendChild(k);
}

function tab(name) {
  document.querySelectorAll(".tabs button").forEach(b => b.classList.toggle("on", b.dataset.tab === name));
  $("#pcb").hidden = name !== "pcb"; $("#sch").hidden = name !== "sch";
}

async function loadDesign(key) {
  const d = DESIGNS.find(x => x.key === key);
  if (!d) return;
  const url = n => `../api/view/file/${encodeURIComponent(key)}/${encodeURIComponent(n)}`;
  mount("pcb", d.files.filter(f => f.endsWith(".kicad_pcb")).map(url), []);
  mount("sch", d.files.filter(f => !f.endsWith(".kicad_pcb")).map(url), []);
  $("#noReport").hidden = true;
  try {
    const r = await fetch(`../api/view/report/${encodeURIComponent(key)}`);
    REPORT = r.ok ? await r.json() : null;
  } catch (e) { REPORT = null; }
  sel = null;
  renderIssues();
}

function renderIssues() {
  const ol = $("#issues");
  if (!REPORT) { $("#tally").innerHTML = ""; ol.innerHTML = ""; return; }
  const c = REPORT.count || {};
  $("#tally").innerHTML = ["pass", "fail", "pending", "unknown"].map(k => `<span class="${k}"><b>${c[k] || 0}</b>${esc(t(k))}</span>`).join("");
  if (!REPORT.issues.length) { ol.innerHTML = `<li>${esc(t("none"))}</li>`; return; }
  const f = v => v === null || v === undefined ? "—" : (typeof v === "number" ? +v.toFixed(2) : v);
  ol.innerHTML = REPORT.issues.map((x, i) => `<li tabindex="0" data-i="${i}" class="${sel === i ? "on" : ""}">` +
    `<span class="st ${x.status}">${esc(t(x.status))}</span>${esc(x.name)}` +
    `<small>${x.value !== null && x.value !== undefined ? `${f(x.value)}${x.limit !== null && x.limit !== undefined ? ` / ${esc(t("limit"))} ${f(x.limit)}` : ""} ${esc(x.unit)} · ` : ""}${esc(x.detail || x.why)}</small></li>`).join("");
}

// KiCanvas 的板子查看器在两层 shadow DOM 里；它的 select(位号) 和 zoom_to_selection() 是我们要用的
function boardViewer() {
  const walk = n => {
    if (!n) return null;
    if (n.tagName === "KC-BOARD-VIEWER") return n.viewer || null;
    for (const c of [n.shadowRoot, ...(n.children || [])]) { const v = c && walk(c); if (v) return v; }
    return null;
  };
  return walk($("#pcb"));
}

function jump(i) {
  sel = i; renderIssues(); tab("pcb");
  const x = REPORT.issues[i];
  const v = boardViewer();
  if (!v || !v.board) return;
  const ref = (x.refs || []).find(r => v.board.find_footprint && v.board.find_footprint(r));
  if (ref) { v.select(ref); v.zoom_to_selection(); status(""); return; }
  if (x.points && x.points.length) {
    const fp = (v.board.footprints || [])[0];
    const BBox = fp && fp.bbox && fp.bbox.constructor;
    if (BBox) {
      const xs = x.points.map(p => p[0]), ys = x.points.map(p => p[1]);
      const x0 = Math.min(...xs), y0 = Math.min(...ys);
      v.select(new BBox(x0 - 1, y0 - 1, Math.max(...xs) - x0 + 2, Math.max(...ys) - y0 + 2));
      v.zoom_to_selection(); status(""); return;
    }
  }
  status(t("notFound").replace("{r}", (x.refs || []).join(" ")));
}

async function openLocal(list) {
  status(t("loading"));
  const files = await Promise.all([...list].map(async f => ({name: f.name, text: await f.text()})));
  mount("pcb", [], files.filter(f => f.name.endsWith(".kicad_pcb")));
  mount("sch", [], files.filter(f => !f.name.endsWith(".kicad_pcb")));
  REPORT = null; renderIssues(); $("#noReport").hidden = false;
  tab(files.some(f => f.name.endsWith(".kicad_pcb")) ? "pcb" : "sch");
  status(t("localOpen").replace("{n}", files.length));
}

$("#design").addEventListener("change", e => { status(""); loadDesign(e.target.value); });
$("#files").addEventListener("change", e => { if (e.target.files.length) openLocal(e.target.files); });
document.querySelector(".tabs").addEventListener("click", e => { const b = e.target.closest("button"); if (b) tab(b.dataset.tab); });
$("#issues").addEventListener("click", e => { const li = e.target.closest("li[data-i]"); if (li) jump(+li.dataset.i); });
$("#issues").addEventListener("keydown", e => { if (e.key === "Enter") { const li = e.target.closest("li[data-i]"); if (li) jump(+li.dataset.i); } });
$("#lang").addEventListener("click", () => { lang = lang === "en" ? "zh" : "en"; localSet("eda.lang", lang); applyLang(); });

applyLang();
fetch("../api/view/designs").then(r => r.json()).then(j => {
  DESIGNS = j.designs;
  $("#design").innerHTML = DESIGNS.map(d => `<option value="${esc(d.key)}">${esc(d.title)}</option>`).join("");
  if (DESIGNS.length) loadDesign(DESIGNS[0].key);
});
