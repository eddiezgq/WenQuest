// WenQuest PLC lab (第 18 轮 〔PLC〕): the editor, operator panel, I/O monitor, timing chart and test runner that a lab
// with view: "plc" gets. The engine is WQPLC (plc.js); the kit (kit.js) calls WQPLCUI.setup(L, kit) for such a lab.
//
// A PLC lab supplies, besides the usual title, scenes, tasks and draw():
//   plc:   { io: [{name, addr, dir: "in"|"out", type?, comment: [zh, en]}], lang: "ST"|"LD", cycle, filter,
//            program: {st} or {decls, ladder}   (the starting program the student edits),
//            watch: ["Main.state", ...], tests: [{id, name: [zh, en], steps: [...], faults}], },
//   plant: { reset(s, {faults}), inputs(s) -> {name: value}, step(dt_ms, outputs, s), read(s, name),
//            panel: [{name, kind: "push"|"nc-push"|"switch", label: [zh, en]}], faults: [{id, name: [zh, en]}] }
//   draw(api, s) sees api.plc.io (name -> value), api.plc.plant (the plant state), api.plc.rt (the runtime).
//   A task with test: "<id>" is ticked when that test passes; check(api) may tick others with api.done(id).
(function () {
"use strict";
const ELEMENTS = [
  ["NO", "–| |–", ["常开触点", "Normally open contact"]], ["NC", "–|/|–", ["常闭触点", "Normally closed contact"]],
  ["P", "–|P|–", ["上升沿", "Rising edge"]], ["N", "–|N|–", ["下降沿", "Falling edge"]],
  ["CMP", "–[比较]–", ["比较触点", "Compare contact"]], ["WIRE", "———", ["导线", "Wire"]],
  ["COIL", "–( )–", ["线圈", "Coil"]], ["NCOIL", "–(/)–", ["取反线圈", "Negated coil"]],
  ["SET", "–(S)–", ["置位", "Set"]], ["RST", "–(R)–", ["复位", "Reset"]],
  ["TON", "TON", ["接通延时", "On-delay timer"]], ["TOF", "TOF", ["断开延时", "Off-delay timer"]], ["TP", "TP", ["脉冲定时", "Pulse timer"]],
  ["CTU", "CTU", ["加计数", "Up counter"]], ["CTD", "CTD", ["减计数", "Down counter"]],
  ["ASSIGN", "[ := ]", ["赋值", "Assign"]],
];
const COLS = 8;

function setup(L, K) {
  const { el, biText, T, P, store, KEY } = K;
  const def = L.def, cfg = def.plc, plant = def.plant || {};
  const api = L.api;
  const saveKey = `${KEY}-plc-${L.id}`;
  const saved = store.get(saveKey) || {};
  const lang0 = (saved.lang || cfg.lang || (cfg.program && cfg.program.ladder ? "LD" : "ST")).toUpperCase();
  const S = L.plc = {
    lang: lang0,
    st: saved.st != null ? saved.st : (cfg.program && cfg.program.st) || "PROGRAM Main\n  (* 在这里写程序 / write your program here *)\nEND_PROGRAM\n",
    decls: saved.decls != null ? saved.decls : (cfg.program && cfg.program.decls) || "",
    ladder: saved.ladder || JSON.parse(JSON.stringify((cfg.program && cfg.program.ladder) || [{ cells: [[null, null, null, null, null, null, null, null]], links: [] }])),
    rt: null, ps: {}, panel: {}, faults: {}, acc: 0, speed: 1, err: null, sel: null, results: {},
  };
  const io = cfg.io.map((x) => Object.assign({}, x, { addr: WQPLC.normAddr(x.addr) }));
  api.plc = { io: {}, plant: S.ps, rt: null, faults: S.faults };

  // ---------------------------------------------------------------- DOM
  const box = el("div", "plcbox");
  const head = el("div", "plchead");
  const tabs = {};
  const views = {};
  const TABS = [["prog", ["程序", "Program"]], ["io", ["I/O 与监视", "I/O & watch"]], ["trace", ["时序图", "Timing"]], ["tests", ["测试", "Tests"]]];
  const tabbar = el("div", "plctabs");
  TABS.forEach(([k, name]) => {
    const b = biText(el("button", "btn chip"), name); b.dataset.k = k;
    b.addEventListener("click", () => showTab(k));
    tabbar.appendChild(b); tabs[k] = b;
    views[k] = el("div", "plcview"); views[k].hidden = true;
  });
  const status = el("span", "plcstatus");
  head.append(tabbar, status);
  box.append(head, ...Object.values(views));
  // operator panel goes under the stage (it is part of the machine)
  const panel = el("div", "plcpanel");
  L.dom.sec.querySelector(".stagebox").insertBefore(panel, L.dom.sec.querySelector(".stagebox .stagebar").nextSibling);
  L.dom.sec.querySelector(".stagebox").appendChild(box);
  L.dom.sec.classList.add("plclab");

  function showTab(k) {
    Object.entries(tabs).forEach(([n, b]) => b.setAttribute("aria-pressed", String(n === k)));
    Object.entries(views).forEach(([n, v]) => { v.hidden = n !== k; });
    S.tab = k;
    if (k === "trace") drawTrace();
  }

  // ---- program view: language switch, ST editor or ladder editor, compile button, messages
  const pv = views.prog;
  const langbar = el("div", "row plclang");
  const bST = biText(el("button", "btn chip"), ["结构化文本 ST", "Structured text ST"]);
  const bLD = biText(el("button", "btn chip"), ["梯形图 LD", "Ladder LD"]);
  const bLoad = biText(el("button", "btn primary"), ["编译并下载", "Compile & download"]);
  const bAsSt = biText(el("button", "btn"), ["看等价的 ST", "Show as ST"]);
  const bXml = biText(el("button", "btn"), ["导出 PLCopen XML", "Export PLCopen XML"]);
  const bReset = biText(el("button", "btn"), ["恢复初始程序", "Restore the starting program"]);
  langbar.append(bST, bLD, el("span", "spacer"), bLoad, bAsSt, bXml, bReset);
  const msg = el("div", "plcmsg");
  const stWrap = el("div", "plcst");
  const gutter = el("pre", "gutter");
  const ta = el("textarea"); ta.spellcheck = false; ta.value = S.st; ta.setAttribute("aria-label", "ST");
  stWrap.append(gutter, ta);
  const declLabel = biText(el("div", "plclbl"), ["变量声明（VAR … END_VAR）", "Declarations (VAR … END_VAR)"]);
  const decl = el("textarea", "plcdecl"); decl.spellcheck = false; decl.value = S.decls; decl.rows = 3;
  const ldWrap = el("div", "plcld");
  const ldTools = el("div", "ldtools");
  const ldGrid = el("div", "ldgrid");
  const ldEdit = el("div", "ldedit");
  ldWrap.append(declLabel, decl, ldTools, ldGrid, ldEdit);
  const asSt = el("pre", "plcasst"); asSt.hidden = true;
  pv.append(langbar, msg, stWrap, ldWrap, asSt);

  function paintGutter() {
    const n = ta.value.split("\n").length;
    gutter.textContent = Array.from({ length: n }, (_, k) => k + 1).join("\n");
  }
  ta.addEventListener("input", () => { S.st = ta.value; paintGutter(); persist(); });
  ta.addEventListener("scroll", () => { gutter.scrollTop = ta.scrollTop; });
  ta.addEventListener("keydown", (e) => {
    if (e.key === "Tab") { e.preventDefault(); const s = ta.selectionStart; ta.setRangeText("  ", s, ta.selectionEnd, "end"); S.st = ta.value; persist(); }
  });
  decl.addEventListener("input", () => { S.decls = decl.value; persist(); });
  bST.addEventListener("click", () => setLang("ST"));
  bLD.addEventListener("click", () => setLang("LD"));
  bLoad.addEventListener("click", () => { load(); if (!S.err) say(T("已下载到 PLC，按“运行”开始扫描。", "Downloaded; press Run to start scanning."), "ok"); });
  bAsSt.addEventListener("click", () => {
    asSt.hidden = !asSt.hidden;
    if (!asSt.hidden) asSt.textContent = S.lang === "LD" ? `PROGRAM Main\n${S.decls}\n${WQPLC.ladderToSt(S.ladder).replace(/^/gm, "  ")}\nEND_PROGRAM` : S.st;
  });
  bXml.addEventListener("click", () => {
    try {
      const src = S.lang === "LD" ? `PROGRAM Main\n${S.decls}\n${ldStWithEdges()}\nEND_PROGRAM` : S.st;
      const xml = WQPLC.exportXml(src, { io, name: P(def.title), cycle: cfg.cycle || 10 });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([xml], { type: "application/xml" }));
      a.download = `lab-${L.id}.xml`; document.body.appendChild(a); a.click(); a.remove();
    } catch (e) { say(errText(e), "bad"); }
  });
  bReset.addEventListener("click", () => {
    if (!confirm(T("恢复成实验给的初始程序？你写的会被替换。", "Restore the starting program? Your edits will be replaced."))) return;
    const p0 = cfg.program || {};
    S.st = p0.st || S.st; S.decls = p0.decls || ""; S.ladder = JSON.parse(JSON.stringify(p0.ladder || S.ladder));
    ta.value = S.st; decl.value = S.decls; paintGutter(); paintLadder(); persist(); load();
  });
  function ldStWithEdges() {
    // ladder → ST for export: edge contacts need R_TRIG / F_TRIG instances declared
    const body = WQPLC.ladderToSt(S.ladder);
    const extra = [...new Set((body.match(/_(rt|ft)\d+_\d+_\d+/g) || []))].map((n) => `${n} : ${n.startsWith("_rt") ? "R_TRIG" : "F_TRIG"};`);
    const d = S.decls.trim() ? S.decls.replace(/END_VAR(?![\s\S]*END_VAR)/, extra.join(" ") + " END_VAR") : (extra.length ? `VAR ${extra.join(" ")} END_VAR` : "");
    return d + "\n" + body;
  }
  function setLang(l) {
    S.lang = l; persist();
    bST.setAttribute("aria-pressed", String(l === "ST")); bLD.setAttribute("aria-pressed", String(l === "LD"));
    stWrap.hidden = l !== "ST"; ldWrap.hidden = l !== "LD"; asSt.hidden = true;
    if (l === "LD") paintLadder();
    load();
  }
  function persist() { store.set(saveKey, { lang: S.lang, st: S.st, decls: S.decls, ladder: S.ladder }); }
  function say(text, kind) { msg.textContent = text; msg.className = "plcmsg " + (kind || ""); }
  function errText(e) { return (e.line ? T(`第 ${e.line} 行：`, `Line ${e.line}: `) : "") + (e.message || String(e)); }

  // ---- ladder editor
  ELEMENTS.forEach(([k, sym, name]) => {
    const b = el("button", "btn chip ld-el"); b.textContent = sym; b.title = P(name); b.dataset.k = k;
    b.addEventListener("click", () => placeElement(k));
    ldTools.appendChild(b);
  });
  [["link", "┃", ["竖线（并联）", "Vertical link (parallel)"]], ["del", "✕", ["删除元件", "Delete element"]],
   ["row", "+行", ["加一行（并联分支）", "Add a row (branch)"]], ["rung", "+网络", ["加一个网络", "Add a rung"]],
   ["delrung", "−网络", ["删除这个网络", "Delete this rung"]]].forEach(([k, sym, name]) => {
    const b = el("button", "btn chip ld-act"); b.textContent = sym; b.title = P(name); b.dataset.act = k;
    b.addEventListener("click", () => ladderAction(k));
    ldTools.appendChild(b);
  });
  function cellText(c) {
    if (!c) return "";
    if (c.k === "FB") return `${c.inst}${Object.entries(c.p || {}).map(([k, v]) => `\n${k}:${v}`).join("")}`;
    if (c.k === "CMP") return `[${c.x}]`;
    if (c.k === "ASSIGN") return `${c.v} := ${c.x}`;
    if (c.k === "WIRE") return "";
    return c.v || "?";
  }
  function symbol(c) {
    if (!c) return "";
    const e = ELEMENTS.find((x) => x[0] === (c.k === "FB" ? c.fb : c.k));
    return e ? e[1] : c.k;
  }
  function paintLadder() {
    ldGrid.innerHTML = "";
    const probe = S.rt && S.rt.probe;
    S.ladder.forEach((r, ri) => {
      const rung = el("div", "rung");
      const no = el("div", "rungno", String(ri + 1));
      const cm = el("input", "rungcm"); cm.type = "text"; cm.placeholder = T("网络注释", "Rung comment");
      cm.value = Array.isArray(r.comment) ? P(r.comment) : (r.comment || "");
      cm.addEventListener("input", () => { r.comment = cm.value; persist(); });
      const hd = el("div", "runghead"); hd.append(no, cm);
      const grid = el("div", "rgrid"); grid.style.gridTemplateColumns = `repeat(${COLS}, minmax(0, 1fr))`;
      const links = new Set((r.links || []).map(([a, c]) => a + ":" + c));
      const pr = probe && probe[ri];
      r.cells.forEach((row, i) => {
        for (let j = 0; j < COLS; j++) {
          const c = row[j] || null;
          const cell = el("button", "lcell" + (c ? " has" : "") + (S.sel && S.sel.r === ri && S.sel.i === i && S.sel.j === j ? " sel" : ""));
          const live = pr && pr.edge[i] && (pr.edge[i][j + 1]);
          const inLive = pr && pr.edge[i] && pr.edge[i][j];
          if (c && live) cell.classList.add("on");
          if (c && inLive) cell.classList.add("in");
          if (links.has(i + ":" + j) && j > 0) cell.classList.add("linkL");
          if (links.has(i + ":" + (j + 1))) cell.classList.add("linkR");
          if (j === 0) cell.classList.add("first");
          const sym = el("span", "sym", symbol(c)); const tx = el("span", "tx", cellText(c));
          cell.append(sym, tx);
          cell.addEventListener("click", () => { S.sel = { r: ri, i, j }; paintLadder(); paintCellEditor(); });
          grid.appendChild(cell);
        }
      });
      rung.append(hd, grid);
      ldGrid.appendChild(rung);
    });
  }
  function selCell() { const s = S.sel; return s ? S.ladder[s.r].cells[s.i][s.j] : null; }
  function placeElement(k) {
    const s = S.sel;
    if (!s) { say(T("先点一个格子，再选元件。", "Pick a cell first, then an element."), "bad"); return; }
    const row = S.ladder[s.r].cells[s.i];
    const old = row[s.j] || {};
    let c;
    if (["TON", "TOF", "TP", "CTU", "CTD"].includes(k)) {
      const n = (k.startsWith("T") ? "t" : "c") + (countFb() + 1);
      c = { k: "FB", fb: k, inst: old.inst || n, p: k.startsWith("CT") ? { PV: "10", ...(k === "CTU" ? { R: "FALSE" } : { LD: "FALSE" }) } : { PT: "T#1s" } };
      ensureDecl(c.inst, k);
    } else if (k === "CMP") c = { k, x: old.x || "count >= 10" };
    else if (k === "ASSIGN") c = { k, v: old.v || "count", x: old.x || "0" };
    else if (k === "WIRE") c = { k };
    else c = { k, v: old.v || (io[0] && io[0].name) || "x" };
    row[s.j] = c;
    persist(); paintLadder(); paintCellEditor();
  }
  function countFb() { let n = 0; S.ladder.forEach((r) => r.cells.forEach((row) => row.forEach((c) => { if (c && c.k === "FB") n++; }))); return n; }
  function ensureDecl(inst, type) {
    if (new RegExp(`\\b${inst}\\s*:`, "i").test(S.decls)) return;
    S.decls = S.decls.trim() ? S.decls.replace(/END_VAR(?![\s\S]*END_VAR)/, `  ${inst} : ${type};\nEND_VAR`) : `VAR\n  ${inst} : ${type};\nEND_VAR`;
    decl.value = S.decls;
  }
  function ladderAction(k) {
    const s = S.sel;
    if (k === "rung") { S.ladder.push({ cells: [new Array(COLS).fill(null)], links: [] }); S.sel = { r: S.ladder.length - 1, i: 0, j: 0 }; }
    else if (!s) { say(T("先点一个格子。", "Pick a cell first."), "bad"); return; }
    else if (k === "del") S.ladder[s.r].cells[s.i][s.j] = null;
    else if (k === "row") S.ladder[s.r].cells.push(new Array(COLS).fill(null));
    else if (k === "delrung") { if (S.ladder.length > 1) { S.ladder.splice(s.r, 1); S.sel = null; } }
    else if (k === "link") {
      // toggle a vertical link between this row and the next, at the left edge of the selected column
      const r = S.ladder[s.r];
      if (s.i >= r.cells.length - 1) { say(T("竖线连到下一行：先“+行”，再选上面那一行的格子。", "A link joins this row to the next: add a row, then pick a cell in the upper row."), "bad"); return; }
      const c = Math.max(1, s.j);
      r.links = r.links || [];
      const at = r.links.findIndex(([a, b]) => a === s.i && b === c);
      if (at >= 0) r.links.splice(at, 1); else r.links.push([s.i, c]);
    }
    persist(); paintLadder(); paintCellEditor();
  }
  function paintCellEditor() {
    ldEdit.innerHTML = "";
    const c = selCell();
    if (!c) return;
    const names = io.map((x) => x.name);
    const field = (label, val, set) => {
      const w = el("label", "ldf"); w.append(biText(el("span"), label));
      const inp = el("input"); inp.type = "text"; inp.value = val; inp.setAttribute("list", `plc-names-${L.id}`);
      inp.addEventListener("change", () => { set(inp.value.trim()); persist(); paintLadder(); });
      w.appendChild(inp); ldEdit.appendChild(w);
    };
    if (["NO", "NC", "P", "N", "COIL", "NCOIL", "SET", "RST"].includes(c.k)) field(["变量", "Variable"], c.v, (v) => { c.v = v; });
    if (c.k === "CMP") field(["条件（ST 表达式）", "Condition (ST expression)"], c.x, (v) => { c.x = v; });
    if (c.k === "ASSIGN") { field(["目标", "Target"], c.v, (v) => { c.v = v; }); field(["值（ST 表达式）", "Value (ST expression)"], c.x, (v) => { c.x = v; }); }
    if (c.k === "FB") {
      field(["实例名", "Instance"], c.inst, (v) => { c.inst = v; ensureDecl(v, c.fb); });
      Object.keys(c.p || {}).forEach((k) => field([k, k], c.p[k], (v) => { c.p[k] = v; }));
    }
    let dl = document.getElementById(`plc-names-${L.id}`);
    if (!dl) { dl = el("datalist"); dl.id = `plc-names-${L.id}`; document.body.appendChild(dl); }
    dl.innerHTML = names.map((n) => `<option value="${n}">`).join("");
  }

  // ---- I/O and watch view
  const iov = views.io;
  const iotab = el("table", "plcio");
  const watchIn = el("input"); watchIn.type = "text"; watchIn.placeholder = T("加监视变量，如 Main.state、t1.ET", "Add a watch, e.g. Main.state, t1.ET");
  const watchList = (store.get(saveKey + "-watch") || cfg.watch || []).slice();
  watchIn.addEventListener("change", () => { const v = watchIn.value.trim(); if (v && !watchList.includes(v)) { watchList.push(v); store.set(saveKey + "-watch", watchList); } watchIn.value = ""; paintIo(true); });
  iov.append(iotab, watchIn, biText(el("p", "hint"), ["点 I/O 表里的值可以强制（再点取消强制）。强制会覆盖 PLC 的读写，调试完一定要取消。",
    "Click a value in the I/O table to force it (click again to release). A force overrides the PLC; release it when you are done."]));
  function paintIo(rebuild) {
    if (rebuild || iotab.rows.length !== io.length + watchList.length + 1) {
      iotab.innerHTML = "";
      const h = iotab.insertRow(); [["地址", "Address"], ["符号", "Symbol"], ["说明", "Comment"], ["值", "Value"]].forEach((x) => h.appendChild(biText(el("th"), x)));
      io.forEach((x) => {
        const r = iotab.insertRow(); r.className = x.dir;
        r.insertCell().textContent = x.addr; r.insertCell().textContent = x.name;
        biText(r.insertCell(), x.comment || ["", ""]);
        const v = r.insertCell(); v.className = "v"; v.dataset.name = x.name;
        v.addEventListener("click", () => toggleForce(x));
      });
      watchList.forEach((w) => {
        const r = iotab.insertRow(); r.className = "watch";
        r.insertCell().textContent = "—"; r.insertCell().textContent = w; r.insertCell().textContent = "";
        const v = r.insertCell(); v.className = "v"; v.dataset.watch = w;
        const x = el("button", "btn chip", "✕"); x.addEventListener("click", () => { watchList.splice(watchList.indexOf(w), 1); store.set(saveKey + "-watch", watchList); paintIo(true); });
        r.cells[2].appendChild(x);
      });
    }
    iotab.querySelectorAll("td.v").forEach((td) => {
      let v;
      if (td.dataset.name) { const x = io.find((q) => q.name === td.dataset.name); v = S.rt ? S.rt.read(x.addr) : undefined; td.classList.toggle("forced", !!(S.rt && x.addr in S.rt.forces)); }
      else v = S.rt ? S.rt.watchAny(td.dataset.watch) : undefined;
      td.textContent = show(v);
      td.classList.toggle("hi", v === true);
    });
  }
  function show(v) {
    if (v === undefined) return "—";
    if (typeof v === "boolean") return v ? "1" : "0";
    if (typeof v === "number") return Number.isInteger(v) ? String(v) : v.toFixed(3);
    if (Array.isArray(v)) return "[" + v.slice(0, 8).map(show).join(", ") + (v.length > 8 ? "…" : "") + "]";
    if (v && typeof v === "object") return "{…}";
    return String(v);
  }
  function toggleForce(x) {
    if (!S.rt) return;
    if (x.addr in S.rt.forces) S.rt.force(x.name, null);
    else S.rt.force(x.name, x.addr[2] === "X" ? !S.rt.read(x.addr) : +(prompt(T("强制为：", "Force to:"), "0") || 0));
    paintIo();
  }

  // ---- timing chart
  const tv = views.trace;
  const tcan = el("canvas", "plctrace");
  tv.append(tcan, biText(el("p", "hint"), ["最近 10 秒的 I/O 与监视变量，每格 1 秒。", "The last 10 s of I/O and watched variables, 1 s per division."]));
  function drawTrace() {
    if (!S.rt || !S.rt.trace || tv.hidden) return;
    const tr = S.rt.trace;
    const names = tr.names, n = names.length;
    const w = tcan.clientWidth || 600, rowH = 22, h = n * rowH + 24;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (tcan.width !== w * dpr || tcan.height !== h * dpr) { tcan.width = w * dpr; tcan.height = h * dpr; tcan.style.height = h + "px"; }
    const c = tcan.getContext("2d"); c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, w, h);
    const x0 = 110, span = 10000, tEnd = S.rt.now, tStart = tEnd - span;
    const X = (t) => x0 + (w - x0 - 8) * (t - tStart) / span;
    c.strokeStyle = K.css("--grid"); c.lineWidth = 1;
    for (let s = 0; s <= 10; s++) { const x = x0 + (w - x0 - 8) * s / 10; c.beginPath(); c.moveTo(x, 0); c.lineTo(x, h - 18); c.stroke(); }
    names.forEach((nm, k) => {
      const y = k * rowH + 4;
      c.fillStyle = K.css("--ink"); c.font = `12px ${K.css("--mono")}`; c.textAlign = "left"; c.textBaseline = "middle";
      c.fillText(nm.length > 14 ? nm.slice(0, 13) + "…" : nm, 4, y + rowH / 2 - 2);
      const vs = tr.v[k];
      const nums = vs.filter((v) => typeof v === "number");
      const lo = Math.min(0, ...nums), hi = Math.max(1, ...nums);
      c.strokeStyle = K.css(io.find((q) => q.name === nm && q.dir === "out") ? "--accent" : "--green"); c.lineWidth = 1.6; c.beginPath();
      let first = true;
      tr.t.forEach((t, i) => {
        if (t < tStart) return;
        const v = vs[i];
        const f = typeof v === "boolean" ? (v ? 1 : 0) : typeof v === "number" ? (v - lo) / (hi - lo || 1) : 0;
        const x = X(t), yy = y + rowH - 6 - f * (rowH - 10);
        if (first) { c.moveTo(x, yy); first = false; } else c.lineTo(x, yy);
      });
      c.stroke();
    });
    c.fillStyle = K.css("--muted"); c.textAlign = "center";
    c.fillText(T("现在", "now"), w - 20, h - 8);
    c.fillText("−10 s", x0 + 12, h - 8);
  }

  // ---- tests view
  const testv = views.tests;
  const bRun = biText(el("button", "btn primary"), ["运行全部测试", "Run all tests"]);
  const tlist = el("ul", "plctests");
  testv.append(el("div", "row"), tlist);
  testv.firstChild.append(bRun, biText(el("span", "hint"), ["测试用你现在的程序，在模拟时间里驱动设备，自动判断对不对（含故障）。",
    "Tests run your current program against the machine in simulated time and judge the result (faults included)."]));
  bRun.addEventListener("click", runTests);
  function paintTests() {
    tlist.innerHTML = "";
    (cfg.tests || []).forEach((t) => {
      const r = S.results[t.id];
      const li = el("li", r ? (r.ok ? "ok" : "bad") : "");
      li.append(el("span", "mark", r ? (r.ok ? "✓" : "✗") : "·"), biText(el("span"), t.name));
      if (r && !r.ok) { const ul = el("ul"); r.failures.slice(0, 3).forEach((f) => ul.appendChild(el("li", "", f.msg))); li.appendChild(ul); }
      tlist.appendChild(li);
    });
  }
  function runTests() {
    const rtOpts = rtOptions();
    if (!rtOpts) { showTab("prog"); return; }
    (cfg.tests || []).forEach((t) => {
      try { S.results[t.id] = WQPLC.runTest(rtOpts, plant, t); }
      catch (e) { S.results[t.id] = { ok: false, failures: [{ msg: errText(e) }] }; }
      if (S.results[t.id].ok) def.tasks.filter((k) => k.test === t.id).forEach((k) => api.done(k.id));
    });
    paintTests();
    const n = (cfg.tests || []).length, ok = Object.values(S.results).filter((r) => r.ok).length;
    try { if (window.parent !== window) window.parent.postMessage({ type: "wq-plc-tests", lab: L.id.replace("-", "."), passed: ok, total: n }, "*"); } catch (e) { /* no parent */ }
  }

  // ---- operator panel (push buttons, switches) and fault injection
  function paintPanel() {
    panel.innerHTML = "";
    (plant.panel || []).forEach((p) => {
      const b = biText(el("button", "btn opbtn " + p.kind), p.label);
      if (p.kind === "switch") {
        b.setAttribute("aria-pressed", String(!!S.panel[p.name]));
        b.addEventListener("click", () => { S.panel[p.name] = !S.panel[p.name]; b.setAttribute("aria-pressed", String(S.panel[p.name])); });
      } else {
        const down = () => { S.panel[p.name] = p.kind !== "nc-push"; b.classList.add("down"); };
        const up = () => { S.panel[p.name] = p.kind === "nc-push"; b.classList.remove("down"); };
        b.addEventListener("pointerdown", (e) => { e.preventDefault(); down(); try { b.setPointerCapture(e.pointerId); } catch (x) { /* old browser */ } });
        b.addEventListener("pointerup", up); b.addEventListener("pointercancel", up);
        b.addEventListener("keydown", (e) => { if (e.key === " " || e.key === "Enter") down(); });
        b.addEventListener("keyup", (e) => { if (e.key === " " || e.key === "Enter") up(); });
        up();
      }
      panel.appendChild(b);
    });
    if ((plant.faults || []).length) {
      const f = el("span", "faults");
      f.appendChild(biText(el("span", "lbl"), ["故障：", "Faults: "]));
      plant.faults.forEach((x) => {
        const b = biText(el("button", "btn chip"), x.name); b.setAttribute("aria-pressed", String(!!S.faults[x.id]));
        b.addEventListener("click", () => { S.faults[x.id] = !S.faults[x.id]; b.setAttribute("aria-pressed", String(!!S.faults[x.id])); });
        f.appendChild(b);
      });
      panel.appendChild(f);
    }
  }

  // ---------------------------------------------------------------- runtime
  function rtOptions() {
    const base = { io, cycle: cfg.cycle || 10, filter: cfg.filter || 0, budget: cfg.budget || 100000 };
    try {
      if (S.lang === "LD") { const o = Object.assign(base, { decls: S.decls, ladder: S.ladder }); new WQPLC.Runtime(o); return o; }
      const o = Object.assign(base, { st: S.st }); new WQPLC.Runtime(o); return o;
    } catch (e) { S.err = e; say(errText(e), "bad"); return null; }
  }
  function load() {
    S.err = null;
    const o = rtOptions();
    api.running = false;
    if (!o) { S.rt = null; api.plc.rt = null; paintStatus(); return; }
    S.rt = new WQPLC.Runtime(o);
    S.rt.startTrace(io.map((x) => x.name).concat(watchList).slice(0, 14), 3000);
    api.plc.rt = S.rt;
    S.acc = 0;
    say("", "");
    resetPlant();
    syncIo();
    paintStatus(); paintIo(true);
    if (S.lang === "LD") paintLadder();
  }
  function resetPlant() {
    for (const k of Object.keys(S.ps)) delete S.ps[k];
    if (plant.reset) plant.reset(S.ps, { faults: S.faults, live: true });
  }
  function syncIo() {
    if (!S.rt) return;
    io.forEach((x) => { api.plc.io[x.name] = S.rt.read(x.addr); });
  }
  function scanOnce() {
    const rt = S.rt;
    const fromPlant = plant.inputs ? plant.inputs(S.ps) : {};
    io.forEach((x) => {
      if (x.dir !== "in") return;
      const v = x.name in S.panel ? S.panel[x.name] : x.name in fromPlant ? fromPlant[x.name] : undefined;
      if (v !== undefined) rt.phys[x.addr] = v;
    });
    const ok = rt.scan();
    if (plant.step) plant.step(rt.cycle, rt.outputs(), S.ps);
    if (!ok) { api.running = false; say(T("PLC 停机（STOP）：", "PLC stopped: ") + errText(rt.error), "bad"); }
    return ok;
  }
  function paintStatus() {
    const rt = S.rt;
    const st = !rt ? ["未下载", "No program"] : rt.error ? ["故障 STOP", "FAULT STOP"] : api.running ? ["运行 RUN", "RUN"] : ["停止 STOP", "STOP"];
    status.textContent = P(st) + (rt ? T(` · 扫描 ${rt.scans} 次 · 周期 ${rt.cycle} ms`, ` · ${rt.scans} scans · cycle ${rt.cycle} ms`) : "");
    status.className = "plcstatus " + (!rt || rt.error ? "bad" : api.running ? "run" : "");
  }

  // the kit's hooks
  def.reset = () => { if (S.rt) { const o = rtOptions(); if (o) { S.rt = new WQPLC.Runtime(o); S.rt.startTrace(io.map((x) => x.name).concat(watchList).slice(0, 14), 3000); api.plc.rt = S.rt; } } resetPlant(); syncIo(); paintStatus(); paintIo(); };
  def.start = () => { if (!S.rt || S.rt.error) load(); if (!S.rt) { api.running = false; return; } };
  def.update = (dt) => {
    if (!S.rt) { api.running = false; return; }
    S.acc += dt * 1000 * S.speed;
    let n = 0;
    while (S.acc >= S.rt.cycle && n < 400) { S.acc -= S.rt.cycle; n++; if (!scanOnce()) break; }
    syncIo();
  };
  def.action = (id) => {
    if (id === "stop") { api.running = false; }
    else if (id === "step") { if (!S.rt) load(); if (S.rt) { api.running = false; scanOnce(); syncIo(); } }
    else if (id === "slow") { S.speed = S.speed === 1 ? 0.1 : 1; }
    paintStatus();
  };
  const userReadouts = def.readouts;
  def.readouts = (a, s) => {
    paintStatus();
    if (!document.hidden) { if (S.tab === "io") paintIo(); if (S.tab === "trace") drawTrace(); if (S.tab === "prog" && S.lang === "LD" && S.rt && api.running) paintLadderLive(); }
    if (def.check) def.check(api, S.ps);
    return userReadouts ? userReadouts(a, S.ps) : [];
  };
  let lastLive = 0;
  function paintLadderLive() { const t = performance.now(); if (t - lastLive > 150) { lastLive = t; paintLadder(); } }
  const userDraw = def.draw;
  def.draw = (a) => userDraw(a, S.ps);

  // language switch repaint
  K.onLang(() => { paintTests(); paintStatus(); paintIo(true); if (S.lang === "LD") paintLadder(); });

  // first paint
  ta.value = S.st; paintGutter();
  paintPanel(); paintTests();
  setLang(S.lang);
  showTab("prog");
}

window.WQPLCUI = { setup };
})();
