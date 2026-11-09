// 问渠电子 · 起草台（第 105 轮 P3）。不用框架：一页、几个接口。判定都在服务器的确定性代码里，这里只显示和收集人改的数。
"use strict";
const T = {
  zh: {brand: "问渠电子", desk: "起草台", help: "帮助", pcba: "问渠贴片", view: "网页审图", title: "把需求写成一块电路板",
    lede: "写一句话或一段需求。AI 起草规格和功能块参数，每个数都标来源；代码马上展开电路、跑计算和仿真。你改、你定，确认后下载设计描述。",
    reqLabel: "需求", go: "AI 起草", scope: "本版只做三相电机驱动板（九种功能单元、拓扑固定）；板子层沿用驱动板模板。示例设计，不能直接投产。",
    spec: "规格", units: "功能块参数", unitsHint: "只列 AI 可以改的参数；其余沿用模板。改完点“按改过的数重算”。",
    again: "按改过的数重算", confirm: "我已看过标成“AI 假设”的数，确认这份草稿", download: "下载设计描述（YAML）",
    book: "计算书", downloadMd: "下载计算书（Markdown）",
    ex: [["原需求", "给 400 W、48 V 的机器人关节伺服电机做一块驱动板，额定相电流 8.5 A，峰值 30 A，带 2500 线增量编码器和 CAN。"],
         ["改成 24 V", "24 V 母线的关节驱动板，电机额定电流 8.5 A、峰值 30 A，增量编码器 2500 线，最高 3000 r/min。"],
         ["不给电压", "给一台 400 W 的伺服电机做驱动板，要能接编码器和 CAN。"]],
    drafting: "AI 起草中……（模型起草 + 代码展开、计算、仿真，约半分钟）", computing: "重新计算中……",
    rounds: n => `起草 ${n} 轮`, model: "模型", pass: "通过", fail: "不通过", pending: "待核对", unknown: "未知",
    questions: "要你回答的问题", unsupported: "目录里做不了的", rejected: "被代码退回的数（没进设计）",
    missing: k => `缺必须有的规格：${k}。需求里没给，AI 不许猜——请在下面填上再重算。`,
    field: "项", value: "值", source: "来源", src: {requirement: "需求原文", rule: "规则推出", assumption: "AI 假设",
      person: "人填", template: "模板默认"},
    fails: "不通过的判定", none: "无", login: "请先登录问渠账号", loginLink: "去登录",
    noDesign: "还缺必须有的规格，没法展开电路。", confirmFirst: "先勾选确认",
    board: "板子检查", boardHint: "用驱动板模板的板子（不重新布线），按这份草稿的规格查工艺、布局约束和热。",
    boardItem: "项", boardRes: "结论", boardVal: "量到 / 限值", boardNote: "说明", boardAll: "通过的 {n} 项",
    heat: (s, t, w) => `热：${s}。板上最高约 ${t} ℃，总损耗 ${w} W（简化平板模型，只作布局阶段估算）。`,
    tj: "结温", limit: "限", detailLang: ""},
  en: {brand: "WenQuest Electronics", desk: "Drafting desk", help: "Help", pcba: "PCBA (factory)", view: "Web review", title: "Turn a requirement into a circuit board",
    lede: "Write a sentence or a short requirement. AI drafts the specification and block parameters, each number with its source; code then expands the circuit and runs the calculations and simulations. You change and decide, then download the design description.",
    reqLabel: "Requirement", go: "Draft with AI", scope: "This version covers one board family: a three-phase motor drive (nine block types, fixed topology); the board layer follows the drive-board template. Example design, not for production.",
    spec: "Specification", units: "Block parameters", unitsHint: "Only the parameters AI may change are listed; the rest follow the template. Press “Recalculate” after editing.",
    again: "Recalculate", confirm: "I have looked at every value marked “AI assumption” and accept this draft", download: "Download design description (YAML)",
    book: "Calculation sheet", downloadMd: "Download calculation sheet (Markdown)",
    ex: [["Drive board", "Design a drive board for a 400 W, 48 V robot joint servo motor: rated phase current 8.5 A, peak 30 A, 2500-line incremental encoder and CAN."],
         ["24 V", "A joint drive board on a 24 V bus; motor rated 8.5 A, peak 30 A; 2500-line incremental encoder; up to 3000 r/min."],
         ["No voltage", "Make a drive board for a 400 W servo motor with an encoder input and CAN."]],
    drafting: "Drafting… (model draft + code expansion, calculations and simulation, about half a minute)", computing: "Recalculating…",
    rounds: n => `${n} drafting round(s)`, model: "model", pass: "pass", fail: "fail", pending: "pending check", unknown: "unknown",
    questions: "Questions for you", unsupported: "Not possible with this catalog", rejected: "Values rejected by the code (not in the design)",
    missing: k => `Required specification missing: ${k}. The requirement does not give it and AI may not guess — fill it in below and recalculate.`,
    field: "Item", value: "Value", source: "Source", src: {requirement: "requirement", rule: "derived", assumption: "AI assumption",
      person: "entered", template: "template"},
    fails: "Failed checks", none: "none", login: "Please sign in with your WenQuest account", loginLink: "Sign in",
    noDesign: "Required specification is missing, so no circuit can be expanded.", confirmFirst: "Tick the confirmation first",
    board: "Board checks", boardHint: "The drive-board template's board (not re-routed), checked against this draft's specification: process, layout constraints and thermal.",
    boardItem: "Item", boardRes: "Result", boardVal: "Measured / limit", boardNote: "Note", boardAll: "{n} passing items",
    heat: (s, t, w) => `Thermal: ${s}. Board peak about ${t} °C, total loss ${w} W (simplified plate model, a layout-stage estimate only).`,
    tj: "junction", limit: "limit", detailLang: "Item names and notes are in Chinese for now."},
};
let lang = (localGet("eda.lang") || (location.hostname.endsWith("wenquestech.online") ? "zh" : "en")) === "en" ? "en" : "zh";   // 美国站默认英文（第 129 轮）
let CAT = null, state = null;           // state = {requirement, report, result, runs}
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));

function localGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function localSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* 私密窗口等：不记也行 */ } }
const t = k => T[lang][k];
const nm = o => (lang === "en" ? o.name_en : o.name) || o.name;

function applyLang() {
  document.documentElement.lang = lang === "en" ? "en" : "zh-CN";
  document.querySelectorAll("[data-t]").forEach(el => { el.textContent = t(el.dataset.t); });
  $("#lang").textContent = lang === "en" ? "中文" : "EN";
  document.title = `${t("brand")} · ${t("desk")}`;
  $("#examples").innerHTML = t("ex").map((e, i) => `<button type="button" data-i="${i}">${esc(e[0])}</button>`).join("");
  if (state) render();
}

async function api(path, body) {
  const r = await fetch(path, body ? {method: "POST", headers: {"content-type": "application/json"}, credentials: "include",
    body: JSON.stringify(body)} : {credentials: "include"});
  let j = {};
  try { j = await r.json(); } catch (e) { /* 空回答 */ }
  if (!r.ok) {
    const d = j.detail || {};
    const err = new Error(typeof d === "string" ? d : (d[lang] || d.zh || d.en || r.statusText));
    err.status = r.status;
    throw err;
  }
  return j;
}

function status(msg, isErr) {
  const s = $("#status");
  s.className = "status" + (isErr ? " err" : "");
  s.innerHTML = msg;
}

function srcChip(e) {
  const src = e ? e.source : "template";
  return `<span class="src ${src}">${esc(t("src")[src] || src)}</span>` +
    (e && e.quote ? `<span class="why">“${esc(e.quote)}”</span>` : "") +
    (e && e.why ? `<span class="why">${esc(e.why)}</span>` : "");
}

function input(meta, value, id) {
  if (meta.kind === "choice") {
    return `<select id="${id}">` + meta.allowed.map(o => `<option value="${esc(JSON.stringify(o))}"${o === value ? " selected" : ""}>${esc(o)}</option>`).join("") +
      `${value === null || value === undefined ? '<option value="null" selected>—</option>' : ""}</select>`;
  }
  const v = value === null || value === undefined ? "" : value;
  if (meta.kind === "text") return `<input id="${id}" type="text" value="${esc(v)}" maxlength="200">`;
  const [lo, hi] = meta.allowed;
  return `<input id="${id}" type="number" step="any" min="${lo}" max="${hi}" value="${esc(v)}" placeholder="${lo}–${hi}">`;
}

// 退回项的位置写成人看得懂的名字（单元名 · 参数名 / 规格名）
function where(r) {
  const u = CAT.units.find(x => x.type === r.where);
  if (u) { const p = u.params.find(x => x.key === r.key); return nm(u) + (p ? " · " + nm(p) : r.key ? " · " + r.key : ""); }
  const s = CAT.spec.find(x => x.key === r.key);
  return s ? nm(s) : [r.where, r.key].filter(Boolean).join(" ");
}

function render() {
  const {report, result} = state;
  $("#out").hidden = false;
  const c = result ? result.count : null;
  $("#tally").innerHTML = c ? ["pass", "fail", "pending", "unknown"].map(k => `<span class="${k}"><b>${c[k]}</b>${esc(t(k))}</span>`).join("")
    : `<span class="unknown">${esc(t("noDesign"))}</span>`;
  let notes = "";
  if (report.missing && report.missing.length) {
    const names = report.missing.map(k => nm(CAT.spec.find(s => s.key === k))).join("、");
    notes += `<div class="box rej"><h3>${esc(t("missing")(names))}</h3></div>`;
  }
  const list = (title, items, cls) => items && items.length ? `<div class="box ${cls || ""}"><h3>${esc(title)}</h3><ul>${items.map(x => `<li>${x}</li>`).join("")}</ul></div>` : "";
  notes += list(t("questions"), (report.questions || []).map(esc));
  notes += list(t("unsupported"), (report.unsupported || []).map(esc));
  notes += list(t("rejected"), (report.rejected || []).map(r => `${esc(where(r))} = ${esc(JSON.stringify(r.value))}：${esc(r.reason)}`), "rej");
  if (result && result.fails.length) {
    notes += list(t("fails"), result.fails.map(f => `${esc(f.block)} · ${esc(f.name)}：${esc(f.rule)}`), "rej");
  }
  $("#notes").innerHTML = notes;
  $("#specT").innerHTML = `<tr><th>${esc(t("field"))}</th><th>${esc(t("value"))}</th><th>${esc(t("source"))}</th></tr>` +
    CAT.spec.map(s => {
      const e = report.spec[s.key];
      return `<tr class="${e && e.source === "assumption" ? "assume" : ""}"><td>${esc(nm(s))}${s.required ? " *" : ""}</td>` +
        `<td>${input(s, e ? e.value : null, "s-" + s.key)}<span class="unit">${esc(s.unit)}</span></td><td>${e ? srcChip(e) : "—"}</td></tr>`;
    }).join("");
  $("#unitsT").innerHTML = CAT.units.map(u => {
    const got = report.params[u.type] || {};
    const anyAssume = Object.values(got).some(e => e.source === "assumption");
    return `<details class="unit"${Object.keys(got).length ? " open" : ""}><summary>${esc(nm(u))}${anyAssume ? ` <span class="src assumption">${esc(t("src").assumption)}</span>` : ""}</summary>` +
      `<div class="wrap"><table>` + u.params.map(p => {
        const e = got[p.key];
        return `<tr class="${e && e.source === "assumption" ? "assume" : ""}"><td>${esc(nm(p))}</td>` +
          `<td>${input(p, e ? e.value : p.default, `p-${u.type}-${p.key}`)}<span class="unit">${esc(p.unit)}</span></td><td>${srcChip(e)}</td></tr>`;
      }).join("") + `</table></div></details>`;
  }).join("");
  renderBoard(result && result.board);
  $("#ok").checked = false;
  $("#dl").disabled = !result;
  const book = $("#book");
  book.srcdoc = result ? result.html : "";
  $("#dlmd").style.display = result ? "" : "none";
}

// 第 111 轮：板子检查（不通过、未知的排在前面；通过的收在“全部”里）
function renderBoard(b) {
  const box = $("#boardT");
  if (!b) { box.innerHTML = `<p class="hint">${esc(t("noDesign"))}</p>`; return; }
  if (b.skipped) { box.innerHTML = `<p class="hint">${esc(b.skipped[lang] || b.skipped.zh)}</p>`; return; }
  const rank = {fail: 0, unknown: 1, pending: 2, pass: 3};
  const fmt = v => v === null || v === undefined ? "—" : (typeof v === "number" ? +v.toFixed(3) : v);
  const val = r => r.limit === null || r.limit === undefined ? `${fmt(r.value)} ${esc(r.unit || "")}` : `${fmt(r.value)} / ${esc(t("limit"))} ${fmt(r.limit)} ${esc(r.unit || "")}`;
  const row = r => `<tr><td>${esc(r.name)}<small>${esc(r.key)}</small></td><td class="${r.status}"><b>${esc(t(r.status))}</b></td><td>${val(r)}</td><td>${esc(r.detail || r.why || "")}</td></tr>`;
  const head = `<tr><th>${esc(t("boardItem"))}</th><th>${esc(t("boardRes"))}</th><th>${esc(t("boardVal"))}</th><th>${esc(t("boardNote"))}</th></tr>`;
  const rows = b.rows.slice().sort((a, c) => rank[a.status] - rank[c.status]);
  const top = rows.filter(r => r.status !== "pass"), rest = rows.filter(r => r.status === "pass");
  const th = b.thermal || {};
  const fets = (th.rows || []).filter(r => r.model === "mosfet");
  let h = `<div class="tally">` + ["pass", "fail", "pending", "unknown"].map(k => `<span class="${k}"><b>${b.count[k]}</b>${esc(t(k))}</span>`).join("") + `</div>`;
  if (t("detailLang")) h += `<p class="hint">${esc(t("detailLang"))}</p>`;
  if (th.status && th.t_max_c !== undefined && th.t_max_c !== null) {
    h += `<p class="${th.status}">${esc(t("heat")(t(th.status), th.t_max_c, th.total_w))}</p>`;
    if (fets.length) h += `<p class="hint">${fets.map(r => `${esc(r.ref)} ${esc(t("tj"))} ${fmt(r.tj_c)} / ${fmt(r.tj_max_c)} ℃ <span class="${r.status}">${esc(t(r.status))}</span>`).join(" · ")}</p>`;
  } else if (th.detail) h += `<p class="hint">${esc(th.detail)}</p>`;
  if (top.length) h += `<div class="wrap"><table>${head}${top.map(row).join("")}</table></div>`;
  h += `<details class="unit"><summary>${esc(t("boardAll").replace("{n}", rest.length))}</summary><div class="wrap"><table>${head}${rest.map(row).join("")}</table></div></details>`;
  box.innerHTML = h;
}

function readValues() {
  const val = (el, meta) => {
    if (!el) return null;
    if (meta.kind === "choice") return JSON.parse(el.value);
    if (meta.kind === "text") return el.value.trim() || null;
    return el.value === "" ? null : Number(el.value);
  };
  const spec = {};
  CAT.spec.forEach(s => { const v = val($("#s-" + s.key), s); if (v !== null && !Number.isNaN(v)) spec[s.key] = v; });
  const params = {};
  CAT.units.forEach(u => u.params.forEach(p => {
    const v = val(document.getElementById(`p-${u.type}-${p.key}`), p);
    if (v !== null && !Number.isNaN(v)) (params[u.type] = params[u.type] || {})[p.key] = v;
  }));
  return {spec, params};
}

// 全站登录页在学习平台上，登录后回到这里（同凸轮、site/auth.js）
function loginUrl() {
  const host = location.hostname.replace(/^www\./, "");
  const local = host === "localhost" || host === "127.0.0.1";
  const learn = local ? "http://localhost:8088" : location.protocol + "//learn." + host;
  return learn + "/pages/login/login?back=" + encodeURIComponent(location.href);
}

function failed(e) {
  if (e.status === 401) {
    status(`${esc(t("login"))} · <a href="${esc(loginUrl())}">${esc(t("loginLink"))}</a>`, true);
  } else status(esc(e.message), true);
}

async function draft() {
  const requirement = $("#req").value.trim();
  if (requirement.length < 4) { $("#req").focus(); return; }
  $("#go").disabled = true;
  status(esc(t("drafting")));
  try {
    const r = await api("api/draft", {requirement, lang});
    state = {requirement, report: r.report, result: r.result, runs: r.rounds.map(x => x.run).filter(Boolean)};
    render();
    status(esc(t("rounds")(r.rounds.length)));
  } catch (e) { failed(e); } finally { $("#go").disabled = false; }
}

async function again() {
  if (!state) return;
  status(esc(t("computing")));
  try {
    const r = await api("api/evaluate", {requirement: state.requirement, report: state.report, values: readValues(), runs: state.runs});
    state.report = r.report; state.result = r.result;
    render();
    status("");
  } catch (e) { failed(e); }
}

function save(name, text, type) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], {type}));
  a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
}

$("#go").addEventListener("click", draft);
$("#again").addEventListener("click", again);
$("#lang").addEventListener("click", () => { lang = lang === "en" ? "zh" : "en"; localSet("eda.lang", lang); applyLang(); });
$("#examples").addEventListener("click", ev => { const b = ev.target.closest("button"); if (b) $("#req").value = t("ex")[+b.dataset.i][1]; });
$("#ok").addEventListener("change", () => { $("#dl").disabled = !(state && state.result); });
$("#dl").addEventListener("click", () => {
  if (!$("#ok").checked) { status(esc(t("confirmFirst")), true); $("#ok").focus(); return; }
  save("design.yaml", state.result.yaml, "text/yaml");
});
$("#dlmd").addEventListener("click", ev => { ev.preventDefault(); if (state && state.result) save("calc.md", state.result.markdown, "text/markdown"); });

api("api/catalog").then(c => { CAT = c; applyLang(); }).catch(e => failed(e));
