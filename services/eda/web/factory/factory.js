// 问渠贴片 · 新产品导入（第 112 轮 P5）。不用框架。判定都在服务器的确定性代码里；这里上传、显示、编辑问题单。
"use strict";
const T = {
  zh: {brand: "问渠贴片", desk: "新产品导入", toDesk: "起草台", help: "帮助", view: "网页审图", title: "客户的资料包，进厂前先查一遍",
    lede: "上传光绘、钻孔、物料清单和坐标，按本厂的工艺能力查：资料对不对得上、板子做不做得出、好不好贴。查出的问题由 AI 起草成给客户的问题单，你改完、确认后才导出。文件算完就删，不存服务器。",
    factory: "按哪家工厂的工艺能力查", gerber: "光绘和钻孔（一个 zip，或多个文件）", bom: "物料清单（CSV）", cpl: "贴片坐标（CSV）",
    demo: "用演示资料包", go: "检查", scope: "演示工厂都是虚构的，工艺能力是示例值。演示资料包是驱动板 A 版，故意漏了一个物料编号。",
    board: "板图", top: "顶面", bottom: "底面", boardHint: "点检查结果的一行，问题位置在板图上标出来。",
    qty: "数量统计（报价依据，只算量）", results: "检查结果", maps: "列映射与层（认错了在这里改，再点“检查”）",
    issues: "工程问题单", issuesHint: "AI 只拿到没通过的检查结果，不拿你的文件；每条问题必须引用一条检查结果。",
    draft: "AI 起草问题单", add: "加一条", confirm: "我已逐条看过，确认这份问题单", dlY: "下载问题单（YAML，给设计端）",
    dlM: "下载问题单（Markdown，给客户）", pass: "通过", fail: "不通过", pending: "待核对", unknown: "未知",
    checking: "检查中……（读光绘、查资料、出板图，十几秒）", drafting: "AI 起草中……", needFiles: "请选光绘和钻孔文件，或点“用演示资料包”",
    item: "项", result: "结论", value: "量到 / 限值", note: "说明", name: "统计", count: "数量",
    question: "问题", options: "建议选项（一行一个）", reply: "需要客户回复", del: "删掉", cites: "依据",
    rejected: "被代码退回的条目（引用不存在或已通过）", none: "没有没通过的项，不用发问题单。", pick: "引用哪条检查结果",
    limit: "限", login: "AI 起草要先登录问渠账号", loginLink: "去登录", confirmFirst: "先勾选确认", fictional: "（虚构）",
    col: "列", file: "文件", layer: "认成", mapBom: "物料清单的列", mapCpl: "坐标的列", unset: "（没有）",
    keys: {refs: "位号", qty: "数量", value: "数值", package: "封装", item: "物料编号", ref: "位号", x: "X", y: "Y", rot: "角度", side: "面"},
    layersNeeded: "认不出哪个文件是哪一层：请在下面逐个指定，再点“检查”。", newIssue: "新问题"},
  en: {brand: "WenQuest PCBA", desk: "New product introduction", toDesk: "Drafting desk", help: "Help", view: "Web review", title: "Check the customer's data pack before it reaches the line",
    lede: "Upload the Gerber, drill, BOM and placement files and check them against this factory's capability: do the files agree, can the board be made, can it be assembled. AI drafts the findings into an engineering query; you edit and confirm before export. Files are deleted after the check and never stored.",
    factory: "Factory capability table", gerber: "Gerber and drill (one zip or several files)", bom: "BOM (CSV)", cpl: "Placement (CSV)",
    demo: "Use the demo pack", go: "Check", scope: "Demo factories are fictional with example values. The demo pack is drive board A with one part number left out on purpose.",
    board: "Board", top: "Top", bottom: "Bottom", boardHint: "Click a result row to mark its locations on the board.",
    qty: "Quantities (basis for quoting; counts only)", results: "Check results", maps: "Column and layer mapping (fix here, then Check again)",
    issues: "Engineering query", issuesHint: "AI sees only the open check results, never your files; every question must cite a result.",
    draft: "Draft the query with AI", add: "Add one", confirm: "I have read every item and confirm this query", dlY: "Download query (YAML, for design)",
    dlM: "Download query (Markdown, for the customer)", pass: "pass", fail: "fail", pending: "pending", unknown: "unknown",
    checking: "Checking… (reading Gerbers, checking, drawing the board; a few seconds)", drafting: "Drafting…", needFiles: "Choose the Gerber and drill files, or use the demo pack",
    item: "Item", result: "Result", value: "Measured / limit", note: "Note", name: "Count", count: "Value",
    question: "Question", options: "Options (one per line)", reply: "Reply required", del: "Delete", cites: "Based on",
    rejected: "Items rejected by the code (unknown or passed results cited)", none: "Nothing open, no query needed.", pick: "Cite which result",
    limit: "limit", login: "Sign in to use AI drafting", loginLink: "Sign in", confirmFirst: "Tick the confirmation first", fictional: " (fictional)",
    col: "Column", file: "File", layer: "Read as", mapBom: "BOM columns", mapCpl: "Placement columns", unset: "(none)",
    keys: {refs: "designators", qty: "quantity", value: "value", package: "package", item: "part number", ref: "designator", x: "X", y: "Y", rot: "rotation", side: "side"},
    layersNeeded: "Could not tell which file is which layer: assign each file below and Check again.", newIssue: "New question"},
};
let lang = (localGet("eda.lang") || (location.hostname.endsWith("wenquestech.online") ? "zh" : "en")) === "en" ? "en" : "zh";   // 美国站默认英文（第 129 轮）
let FACT = null, S = null, side = "top", sel = null, layersFix = null, demoMode = false;
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
function localGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function localSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* 不记也行 */ } }
const t = k => T[lang][k];
const OPEN = ["fail", "unknown", "pending"];

function applyLang() {
  document.documentElement.lang = lang === "en" ? "en" : "zh-CN";
  document.querySelectorAll("[data-t]").forEach(el => { el.textContent = t(el.dataset.t); });
  $("#lang").textContent = lang === "en" ? "中文" : "EN";
  document.title = `${t("brand")} · ${t("desk")}`;
  if (FACT) $("#factory").innerHTML = FACT.factories.map(f => `<option value="${esc(f.key)}">${esc(f.factory)}</option>`).join("");
  if (S) render();
}

function status(msg, isErr) { const s = $("#status"); s.className = "status" + (isErr ? " err" : ""); s.innerHTML = msg; }

function loginUrl() {
  const host = location.hostname.replace(/^www\./, "");
  const local = host === "localhost" || host === "127.0.0.1";
  return (local ? "http://localhost:8088" : location.protocol + "//learn." + host) + "/pages/login/login?back=" + encodeURIComponent(location.href);
}

async function call(path, opts) {
  const r = await fetch(path, Object.assign({credentials: "include"}, opts));
  let j = {};
  try { j = await r.json(); } catch (e) { /* 空 */ }
  if (!r.ok) {
    const d = j.detail || {};
    const err = new Error(typeof d === "string" ? d : (d[lang] || d.zh || d.en || r.statusText));
    err.status = r.status; err.detail = d;
    throw err;
  }
  return j;
}

function failed(e) {
  if (e.status === 401) status(`${esc(t("login"))} · <a href="${esc(loginUrl())}">${esc(t("loginLink"))}</a>`, true);
  else if (e.status === 422 && e.detail && e.detail.files) { layersFix = Object.fromEntries(e.detail.files.map(f => [f, "ignore"])); renderLayerFix(e.detail); status(esc(t("layersNeeded")), true); }
  else status(esc(e.message), true);
}

async function check(ev) {
  if (ev) ev.preventDefault();
  const fd = new FormData();
  fd.append("factory", $("#factory").value);
  if (demoMode) fd.append("demo", "1");
  else {
    const g = $("#gerber").files;
    if (!g.length) { status(esc(t("needFiles")), true); return; }
    for (const f of g) fd.append("gerber", f);
    if ($("#bom").files[0]) fd.append("bom", $("#bom").files[0]);
    if ($("#cpl").files[0]) fd.append("cpl", $("#cpl").files[0]);
  }
  if (layersFix) fd.append("layers", JSON.stringify(layersFix));
  if (S && S.maps) { if (S.maps.bom) fd.append("bom_map", JSON.stringify(S.maps.bom)); if (S.maps.cpl) fd.append("cpl_map", JSON.stringify(S.maps.cpl)); }
  $("#go").disabled = true; status(esc(t("checking")));
  try {
    const keepMaps = S && S.maps;
    S = await call("../api/factory/check", {method: "POST", body: fd});
    if (keepMaps) S.maps = Object.assign({}, S.maps, keepMaps);
    S.issues = null; sel = null;
    render(); status("");
  } catch (e) { failed(e); } finally { $("#go").disabled = false; }
}

function val(r) {
  const f = v => v === null || v === undefined ? "—" : (typeof v === "number" ? +v.toFixed(3) : v);
  return r.limit === null || r.limit === undefined ? `${f(r.value)} ${esc(r.unit || "")}` : `${f(r.value)} / ${esc(t("limit"))} ${f(r.limit)} ${esc(r.unit || "")}`;
}

function render() {
  $("#out").hidden = false;
  const c = S.counts;
  $("#tally").innerHTML = ["pass", "fail", "pending", "unknown"].map(k => `<span class="${k}"><b>${c[k] || 0}</b>${esc(t(k))}</span>`).join("") +
    `<span class="unknown">${esc(S.factory)}</span>`;
  $("#notes").innerHTML = S.notes.length ? `<div class="box"><ul>${S.notes.map(n => `<li>${esc(n)}</li>`).join("")}</ul></div>` : "";
  const rank = {fail: 0, unknown: 1, pending: 2, pass: 3};
  const rows = S.results.slice().sort((a, b) => rank[a.status] - rank[b.status] || +a.id.slice(1) - +b.id.slice(1));
  $("#res").innerHTML = `<tr><th>${esc(t("item"))}</th><th>${esc(t("result"))}</th><th>${esc(t("value"))}</th><th>${esc(t("note"))}</th></tr>` +
    rows.map(r => `<tr data-id="${esc(r.id)}" class="${sel === r.id ? "sel" : ""}" tabindex="0"><td>${esc(r.name)}<small>${esc(r.id)} · ${esc(r.key)}</small></td>` +
      `<td class="${r.status}"><b>${esc(t(r.status))}</b></td><td>${val(r)}</td><td>${esc(r.detail || r.why || "")}` +
      `${r.refs && r.refs.length ? `<small>${esc(r.refs.slice(0, 20).join(" "))}</small>` : ""}</td></tr>`).join("");
  $("#qty").innerHTML = `<tr><th>${esc(t("name"))}</th><th>${esc(t("count"))}</th><th>${esc(t("note"))}</th></tr>` +
    S.quantity.rows.map(r => `<tr><td>${esc(r.name)}</td><td><b>${esc(r.value ?? "—")}</b></td><td>${esc(r.note)}</td></tr>`).join("");
  drawBoard();
  renderMaps();
  renderIssues();
}

// 板图：服务器给的 SVG（gerbonara 画的）；标记点用和铜层同一个坐标变换
function drawBoard() {
  const box = $("#svg");
  box.innerHTML = S.svg[side] || "";
  const svg = box.querySelector("svg");
  if (!svg) return;
  svg.removeAttribute("width"); svg.removeAttribute("height");
  const cu = svg.querySelector(`[id^="l-${side}-copper"]`) || svg.querySelector("g[transform*='scale']");
  const tr = cu ? cu.getAttribute("transform") : "";
  const r = S.results.find(x => x.id === sel);
  if (!r) return;
  const pts = r.marks || [];
  const ns = "http://www.w3.org/2000/svg";
  const g = document.createElementNS(ns, "g");
  g.setAttribute("id", "marks");
  if (tr) g.setAttribute("transform", tr);
  pts.forEach(a => {
    const c = document.createElementNS(ns, "circle");
    c.setAttribute("cx", a[0]); c.setAttribute("cy", a[1]); c.setAttribute("r", 1.6);
    c.setAttribute("fill", "none"); c.setAttribute("stroke", "#ff9b4a"); c.setAttribute("stroke-width", 0.5);
    g.appendChild(c);
  });
  svg.appendChild(g);
}

function renderMaps() {
  const block = (kind, title) => {
    const heads = (S.headers || {})[kind];
    if (!heads) return "";
    const m = (S.maps || {})[kind] || {};
    return `<h3>${esc(title)}</h3><div class="wrap"><table>` + Object.keys(t("keys")).filter(k => (kind === "bom" ? ["refs", "qty", "value", "package", "item"] : ["ref", "x", "y", "rot", "side"]).includes(k))
      .map(k => `<tr><td>${esc(t("keys")[k])}</td><td><select data-kind="${kind}" data-k="${k}"><option value="">${esc(t("unset"))}</option>` +
        heads.map(h => `<option${m[k] === h ? " selected" : ""}>${esc(h)}</option>`).join("") + `</select></td></tr>`).join("") + `</table></div>`;
  };
  const lay = S.layers || {};
  $("#maps").innerHTML = block("bom", t("mapBom")) + block("cpl", t("mapCpl")) +
    `<h3>${esc(t("layer"))}</h3><div class="wrap"><table>` + Object.entries(lay).map(([f, l]) =>
      `<tr><td>${esc(f)}</td><td>${layerSelect(f, l)}</td></tr>`).join("") + `</table></div>`;
}

function layerSelect(f, cur) {
  return `<select data-file="${esc(f)}">` + (FACT ? FACT.layers : []).map(l => `<option${l === cur ? " selected" : ""}>${esc(l)}</option>`).join("") + `</select>`;
}

function renderLayerFix(d) {
  $("#out").hidden = false;
  S = S || {results: [], quantity: {rows: []}, notes: [], counts: {}, svg: {}, layers: {}, headers: {}, maps: {}, factory: ""};
  S.layers = layersFix;
  renderMaps();
  $("#mapBox").open = true;
}

// 问题单：AI 起草的草稿 → 人改 → 确认 → 服务器校验后下载
async function draftIssues() {
  status(esc(t("drafting")));
  try {
    const r = await call("../api/factory/issues", {method: "POST", headers: {"content-type": "application/json"},
      body: JSON.stringify({results: S.results, factory: S.factory, package: demoMode ? "demo" : "", lang})});
    S.issues = r.issues; S.rejected = r.rejected;
    renderIssues(); status("");
  } catch (e) { failed(e); }
}

function renderIssues() {
  const box = $("#issues");
  const open = S.results.filter(r => OPEN.includes(r.status));
  if (!open.length) { box.innerHTML = `<p class="hint">${esc(t("none"))}</p>`; $("#draft").disabled = true; $("#issueActions").hidden = true; return; }
  $("#draft").disabled = false;
  if (!S.issues) { box.innerHTML = ""; $("#issueActions").hidden = true; return; }
  const name = id => { const r = S.results.find(x => x.id === id); return r ? `${id} ${r.name}` : id; };
  box.innerHTML = S.issues.issues.map((it, i) => `<div class="issue" data-i="${i}">` +
    `<div class="meta">${esc(it.id)} · ${esc(t("cites"))}：${esc(it.cites.map(name).join("；"))}${it.refs.length ? " · " + esc(it.refs.join(" ")) : ""}</div>` +
    `<label>${esc(t("question"))}<textarea data-f="question" rows="3">${esc(it.question)}</textarea></label>` +
    `<label>${esc(t("options"))}<textarea data-f="options" rows="3">${esc(it.options.join("\n"))}</textarea></label>` +
    `<div class="row"><label class="confirm"><input type="checkbox" data-f="reply"${it.reply_required ? " checked" : ""}> ${esc(t("reply"))}</label>` +
    `<button type="button" data-del="${i}">${esc(t("del"))}</button></div></div>`).join("") +
    (S.rejected && S.rejected.length ? `<div class="box rej"><h3>${esc(t("rejected"))}</h3><ul>${S.rejected.map(r => `<li>${esc(r.reason)}：${esc((r.item || {}).question || "")}</li>`).join("")}</ul></div>` : "");
  $("#issueActions").hidden = false;
  $("#pick").innerHTML = open.map(r => `<option value="${esc(r.id)}">${esc(r.id)} ${esc(r.name)}</option>`).join("");
  $("#ok").checked = false; $("#dlY").disabled = $("#dlM").disabled = true;
}

function readIssues() {
  document.querySelectorAll(".issue").forEach(el => {
    const it = S.issues.issues[+el.dataset.i];
    it.question = el.querySelector("[data-f=question]").value.trim();
    it.options = el.querySelector("[data-f=options]").value.split("\n").map(s => s.trim()).filter(Boolean);
    it.reply_required = el.querySelector("[data-f=reply]").checked;
  });
  const cited = new Set(S.issues.issues.flatMap(i => i.cites));
  S.issues.results = S.results.filter(r => cited.has(r.id)).map(r => ({id: r.id, key: r.key, name: r.name, status: r.status, value: r.value,
    limit: r.limit, unit: r.unit, detail: r.detail, refs: r.refs}));
  S.issues.issues.forEach((it, i) => { it.id = "Q" + (i + 1); });
}

function addIssue() {
  const r = S.results.find(x => x.id === $("#pick").value);
  if (!r) return;
  readIssues();
  S.issues.issues.push({id: "", cites: [r.id], keys: [r.key], refs: r.refs || [], question: t("newIssue"), options: [], reply_required: true});
  readIssues(); renderIssues();
}

async function download(kind) {
  if (!$("#ok").checked) { status(esc(t("confirmFirst")), true); return; }
  readIssues();
  try {
    const r = await call("../api/factory/issues/render", {method: "POST", headers: {"content-type": "application/json"}, body: JSON.stringify({issues: S.issues})});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([kind === "yaml" ? r.yaml : r.markdown], {type: kind === "yaml" ? "text/yaml" : "text/markdown"}));
    a.download = kind === "yaml" ? "issues.yaml" : "issues.md";
    document.body.appendChild(a); a.click(); a.remove();
    status("");
  } catch (e) { failed(e); }
}

$("#up").addEventListener("submit", ev => { demoMode = false; check(ev); });
$("#demo").addEventListener("click", () => { demoMode = true; layersFix = null; S = null; check(); });
$("#lang").addEventListener("click", () => { lang = lang === "en" ? "zh" : "en"; localSet("eda.lang", lang); applyLang(); });
$("#res").addEventListener("click", ev => { const tr = ev.target.closest("tr[data-id]"); if (!tr) return; sel = sel === tr.dataset.id ? null : tr.dataset.id; render(); });
$("#res").addEventListener("keydown", ev => { if (ev.key === "Enter") ev.target.click(); });
document.querySelector(".sides").addEventListener("click", ev => {
  const b = ev.target.closest("button"); if (!b) return;
  side = b.dataset.side; document.querySelectorAll(".sides button").forEach(x => x.classList.toggle("on", x === b)); drawBoard();
});
$("#maps").addEventListener("change", ev => {
  const s = ev.target;
  if (s.dataset.file) { layersFix = Object.assign({}, S.layers, layersFix || {}); layersFix[s.dataset.file] = s.value; return; }
  S.maps = S.maps || {}; S.maps[s.dataset.kind] = S.maps[s.dataset.kind] || {};
  if (s.value) S.maps[s.dataset.kind][s.dataset.k] = s.value; else delete S.maps[s.dataset.kind][s.dataset.k];
});
$("#draft").addEventListener("click", draftIssues);
$("#add").addEventListener("click", addIssue);
$("#issues").addEventListener("click", ev => { const b = ev.target.closest("[data-del]"); if (!b) return; readIssues(); S.issues.issues.splice(+b.dataset.del, 1); readIssues(); renderIssues(); });
$("#ok").addEventListener("change", () => { $("#dlY").disabled = $("#dlM").disabled = !$("#ok").checked; });
$("#dlY").addEventListener("click", () => download("yaml"));
$("#dlM").addEventListener("click", () => download("md"));
["gerber", "bom", "cpl"].forEach(id => $("#" + id).addEventListener("change", () => { demoMode = false; layersFix = null; if (S) S.maps = null; }));

call("../api/factory/factories").then(f => { FACT = f; applyLang(); }).catch(e => failed(e));
applyLang();
