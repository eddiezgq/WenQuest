// WenQuest PLC lab (第 18 轮 〔PLC〕): the editor, operator panel, I/O monitor, timing chart and test runner that a lab
// with view: "plc" gets. The engine is WQPLC (plc.js); the kit (kit.js) calls WQPLCUI.setup(L, kit) for such a lab.
//
// A PLC lab supplies, besides the usual title, scenes, tasks and draw():
//   plc:   { io: [{name, addr, dir: "in"|"out", type?, comment: [zh, en]}], lang: "ST"|"LD", cycle, filter, scanModel?, cycleMode?, watchdog?,
//            program: {st} or {decls, ladder}   (the starting program the student edits),
//            watch: ["Main.state", ...], tests: [{id, name: [zh, en], steps: [...], faults}], },
//   plant: { reset(s, {faults}), inputs(s) -> {name: value}, step(dt_ms, outputs, s), read(s, name),
//            panel: [{name, kind: "push"|"nc-push"|"switch"|"estop", label: [zh, en], names?: [..]}] (names: one push button holding several inputs; estop: latching NC), faults: [{id, name: [zh, en]}] }
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
  const p0 = cfg.program || {};
  const lang0 = (saved.lang || cfg.lang || (p0.ladder ? "LD" : p0.sfc ? "SFC" : p0.fbd ? "FBD" : "ST")).toUpperCase();
  const S = L.plc = {
    lang: lang0,
    st: saved.st != null ? saved.st : (cfg.program && cfg.program.st) || "PROGRAM Main\n  (* 在这里写程序 / write your program here *)\nEND_PROGRAM\n",
    decls: saved.decls != null ? saved.decls : (cfg.program && cfg.program.decls) || "",
    sfc: saved.sfc != null ? saved.sfc : p0.sfc || "PROGRAM Main\n  INITIAL_STEP S0: END_STEP\n  STEP S1: END_STEP\n  TRANSITION FROM S0 TO S1 := FALSE; END_TRANSITION\n  TRANSITION FROM S1 TO S0 := FALSE; END_TRANSITION\nEND_PROGRAM\n",
    fbd: saved.fbd || JSON.parse(JSON.stringify(p0.fbd || [{ comment: "", text: "" }])),
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
  const bSFC = biText(el("button", "btn chip"), ["顺序功能图 SFC", "SFC"]);
  const bFBD = biText(el("button", "btn chip"), ["功能块图 FBD", "FBD"]);
  const LANGB = { ST: bST, LD: bLD, SFC: bSFC, FBD: bFBD };
  (cfg.langs || ["ST", "LD", "SFC", "FBD"]).forEach((l) => { LANGB[l].dataset.allowed = "1"; });
  Object.values(LANGB).forEach((b) => { if (!b.dataset.allowed) b.hidden = true; });
  const bLoad = biText(el("button", "btn primary"), ["编译并下载", "Compile & download"]);
  const bAsSt = biText(el("button", "btn"), ["看等价的 ST", "Show as ST"]);
  const bXml = biText(el("button", "btn"), ["导出 PLCopen XML", "Export PLCopen XML"]);
  const bReset = biText(el("button", "btn"), ["恢复初始程序", "Restore the starting program"]);
  langbar.append(bST, bLD, bSFC, bFBD, el("span", "spacer"), bLoad, bAsSt, bXml, bReset);
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
  const sfcDiag = el("div", "sfcdiag");
  const fbdWrap = el("div", "plcfbd");
  const fbdDecl = el("textarea", "plcdecl"); fbdDecl.spellcheck = false; fbdDecl.rows = 3; fbdDecl.value = S.decls;
  const fbdNets = el("div", "fbdnets");
  const fbdAdd = biText(el("button", "btn chip"), ["+ 网络", "+ Network"]);
  fbdWrap.append(biText(el("div", "plclbl"), ["变量声明（VAR … END_VAR）", "Declarations (VAR … END_VAR)"]), fbdDecl, fbdNets, fbdAdd);
  fbdDecl.addEventListener("input", () => { S.decls = fbdDecl.value; decl.value = S.decls; persist(); });
  fbdAdd.addEventListener("click", () => { S.fbd.push({ comment: "", text: "" }); persist(); paintFbd(); });
  pv.append(langbar, msg, stWrap, sfcDiag, ldWrap, fbdWrap, asSt);

  function paintGutter() {
    const n = ta.value.split("\n").length;
    gutter.textContent = Array.from({ length: n }, (_, k) => k + 1).join("\n");
  }
  ta.addEventListener("input", () => { if (S.lang === "SFC") S.sfc = ta.value; else S.st = ta.value; paintGutter(); persist(); });
  ta.addEventListener("scroll", () => { gutter.scrollTop = ta.scrollTop; });
  ta.addEventListener("keydown", (e) => {
    if (e.key === "Tab") { e.preventDefault(); const s = ta.selectionStart; ta.setRangeText("  ", s, ta.selectionEnd, "end"); if (S.lang === "SFC") S.sfc = ta.value; else S.st = ta.value; persist(); }
  });
  decl.addEventListener("input", () => { S.decls = decl.value; fbdDecl.value = S.decls; persist(); });
  bST.addEventListener("click", () => setLang("ST"));
  bLD.addEventListener("click", () => setLang("LD"));
  bSFC.addEventListener("click", () => setLang("SFC"));
  bFBD.addEventListener("click", () => setLang("FBD"));
  bLoad.addEventListener("click", () => { load(); if (!S.err) say(T("已下载到 PLC，按“运行”开始扫描。", "Downloaded; press Run to start scanning."), "ok"); });
  bAsSt.addEventListener("click", () => {
    asSt.hidden = !asSt.hidden;
    if (!asSt.hidden) asSt.textContent = S.lang === "LD" ? `PROGRAM Main\n${S.decls}\n${WQPLC.ladderToSt(S.ladder).replace(/^/gm, "  ")}\nEND_PROGRAM` : source().st;
  });
  bXml.addEventListener("click", () => {
    try {
      if (S.lang === "SFC") { say(T("顺序功能图的 PLCopen XML（图形格式）还没做；先用“看等价的 ST”。", "PLCopen XML for SFC (graphical) is not available yet."), "bad"); return; }
      const src = S.lang === "LD" ? `PROGRAM Main\n${S.decls}\n${ldStWithEdges()}\nEND_PROGRAM` : source().st;
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
    S.sfc = p0.sfc || S.sfc; S.fbd = JSON.parse(JSON.stringify(p0.fbd || S.fbd));
    ta.value = S.lang === "SFC" ? S.sfc : S.st; decl.value = S.decls; fbdDecl.value = S.decls; paintGutter(); paintLadder(); paintFbd(); persist(); load();
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
    Object.entries(LANGB).forEach(([k, b]) => b.setAttribute("aria-pressed", String(k === l)));
    stWrap.hidden = l !== "ST" && l !== "SFC"; ldWrap.hidden = l !== "LD"; fbdWrap.hidden = l !== "FBD"; sfcDiag.hidden = l !== "SFC"; asSt.hidden = true;
    if (l === "ST" || l === "SFC") { ta.value = l === "SFC" ? S.sfc : S.st; paintGutter(); }
    if (l === "LD") paintLadder();
    if (l === "FBD") paintFbd();
    load();
    if (l === "SFC") paintSfc();
  }
  function persist() { store.set(saveKey, { lang: S.lang, st: S.st, decls: S.decls, ladder: S.ladder, sfc: S.sfc, fbd: S.fbd }); }
  function fbdSource() {
    return `PROGRAM Main\n${S.decls}\n` + S.fbd.map((n, k) => `(* 网络 ${k + 1} ${n.comment || ""} *)\n${n.text.trim().replace(/;?$/, ";")}`).filter((x) => !/\n;$/.test(x)).join("\n") + "\nEND_PROGRAM";
  }
  function source() {
    if (S.lang === "LD") return { decls: S.decls, ladder: S.ladder };
    if (S.lang === "SFC") return { st: S.sfc };
    if (S.lang === "FBD") return { st: fbdSource() };
    return { st: S.st };
  }

  // ---- SFC chart: steps by level from the initial step, transitions as bars, parallel branches as double lines
  function paintSfc() {
    let ast;
    try { ast = WQPLC.parse(S.sfc); } catch (e) { return; }
    const u = ast.pous.find((x) => x.sfc);
    if (!u) { sfcDiag.innerHTML = ""; return; }
    const sf = u.sfc;
    const level = {}, col = {};
    const init = sf.steps.filter((x) => x.initial).map((x) => x.name.toUpperCase());
    const queue = init.slice(); init.forEach((n) => { level[n] = 0; });
    const back = new Set();
    while (queue.length) {
      const n = queue.shift();
      sf.transitions.filter((t) => t.from.some((x) => x.toUpperCase() === n)).forEach((t) => t.to.forEach((m) => {
        const k = m.toUpperCase();
        if (level[k] == null) { level[k] = level[n] + 1; queue.push(k); }
      }));
    }
    sf.steps.forEach((x) => { const k = x.name.toUpperCase(); if (level[k] == null) level[k] = 0; });
    const rows = {};
    sf.steps.forEach((x) => { const k = x.name.toUpperCase(); (rows[level[k]] = rows[level[k]] || []).push(k); });
    Object.values(rows).forEach((r) => r.forEach((k, i) => { col[k] = i; }));
    const W = 150, H = 92, BW = 96, BH = 30, X0 = 40;
    const maxCols = Math.max(...Object.values(rows).map((r) => r.length));
    const nLev = Object.keys(rows).length;
    const pos = (k) => [X0 + col[k] * W + (maxCols - rows[level[k]].length) * W / 2, 14 + level[k] * H];
    const live = S.rt ? (k) => S.rt.watchAny(`${u.name}.${k}`) : () => null;
    let svg = "";
    const esc = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;");
    // transitions
    sf.transitions.forEach((t) => {
      const fr = t.from.map((x) => x.toUpperCase()), to = t.to.map((x) => x.toUpperCase());
      const isBack = to.some((k) => level[k] <= Math.max(...fr.map((f) => level[f])));
      const yb = Math.max(...fr.map((k) => pos(k)[1])) + BH + 22;
      const xs = fr.map((k) => pos(k)[0] + BW / 2);
      const xt = to.map((k) => pos(k)[0] + BW / 2);
      fr.forEach((k) => { const [x, y] = pos(k); svg += `<line x1="${x + BW / 2}" y1="${y + BH}" x2="${x + BW / 2}" y2="${yb - (fr.length > 1 ? 6 : 0)}" class="w"/>`; });
      if (fr.length > 1) svg += `<line x1="${Math.min(...xs)}" y1="${yb - 6}" x2="${Math.max(...xs)}" y2="${yb - 6}" class="w"/><line x1="${Math.min(...xs)}" y1="${yb - 9}" x2="${Math.max(...xs)}" y2="${yb - 9}" class="w"/>`;
      const xm = fr.length > 1 ? (Math.min(...xs) + Math.max(...xs)) / 2 : xs[0];
      if (fr.length > 1) svg += `<line x1="${xm}" y1="${yb - 6}" x2="${xm}" y2="${yb}" class="w"/>`;
      svg += `<line x1="${xm - 12}" y1="${yb}" x2="${xm + 12}" y2="${yb}" class="tb"/>`;
      svg += `<text x="${xm + 16}" y="${yb + 4}" class="tc">${esc(WQPLC.exprText(t.cond)).slice(0, 34)}</text>`;
      if (isBack) {
        const xl = 12 + (sf.transitions.indexOf(t) % 3) * 6;
        const [tx, ty] = pos(to[0]);
        svg += `<polyline points="${xm},${yb} ${xm},${yb + 12} ${xl},${yb + 12} ${xl},${ty - 8} ${tx + BW / 2},${ty - 8} ${tx + BW / 2},${ty}" class="w" fill="none"/>`;
        svg += `<polygon points="${tx + BW / 2 - 4},${ty - 6} ${tx + BW / 2 + 4},${ty - 6} ${tx + BW / 2},${ty}" class="ar"/>`;
      } else {
        const yd = yb + (to.length > 1 ? 10 : 0);
        if (to.length > 1) svg += `<line x1="${xm}" y1="${yb}" x2="${xm}" y2="${yd}" class="w"/><line x1="${Math.min(...xt)}" y1="${yd}" x2="${Math.max(...xt)}" y2="${yd}" class="w"/><line x1="${Math.min(...xt)}" y1="${yd + 3}" x2="${Math.max(...xt)}" y2="${yd + 3}" class="w"/>`;
        to.forEach((k) => { const [x, y] = pos(k); svg += `<polyline points="${to.length > 1 ? x + BW / 2 : xm},${to.length > 1 ? yd + 3 : yb} ${x + BW / 2},${to.length > 1 ? yd + 3 : yb + 8} ${x + BW / 2},${y}" class="w" fill="none"/>`; });
      }
    });
    // steps
    sf.steps.forEach((st) => {
      const k = st.name.toUpperCase(), [x, y] = pos(k);
      const v = live(k) || {};
      svg += `<rect x="${x}" y="${y}" width="${BW}" height="${BH}" class="st${v.X ? " on" : ""}"/>`;
      if (st.initial) svg += `<rect x="${x + 3}" y="${y + 3}" width="${BW - 6}" height="${BH - 6}" class="st2${v.X ? " on" : ""}"/>`;
      svg += `<text x="${x + BW / 2}" y="${y + 19}" class="sn">${esc(st.name)}${v.X ? " · " + Math.round((v.T || 0) / 100) / 10 + "s" : ""}</text>`;
      if (st.acts.length) {
        svg += `<line x1="${x + BW}" y1="${y + BH / 2}" x2="${x + BW + 8}" y2="${y + BH / 2}" class="w"/>`;
        svg += `<text x="${x + BW + 10}" y="${y + BH / 2 + 4}" class="ac">${esc(st.acts.map((a) => `${a.q} ${a.name}`).join(" · ")).slice(0, 26)}</text>`;
      }
    });
    const w = X0 + maxCols * W + 120, h = 30 + nLev * H;
    sfcDiag.innerHTML = `<svg viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" role="img" aria-label="SFC">${svg}</svg>`;
  }

  // ---- FBD: one statement per network, drawn as blocks (AND &, OR ≥1, NOT o, compare, arithmetic, functions, FB boxes)
  function fbdBlocks(x) {
    // tree → {w, h, svg(x, y) -> {svg, out:[x,y]}}
    const esc = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;");
    const flat = (e, op) => (e.e === "bin" && e.op === op ? [...flat(e.a, op), ...flat(e.b, op)] : [e]);
    const valOf = (txt) => { if (!S.rt) return undefined; try { return S.rt.watchAny(txt); } catch (e) { return undefined; } };
    function node(e) {
      if (["name", "field", "index", "addr", "bit", "num", "bool", "time", "enumref"].includes(e.e)) {
        const t = WQPLC.exprText(e);
        return { h: 26, w: Math.max(54, t.length * 7 + 12), draw(x, y, w) { const v = valOf(t); return { svg: `<text x="${x + w - 4}" y="${y + 17}" class="fv${v === true ? " on" : ""}" text-anchor="end">${esc(t)}</text>`, out: [x + w, y + 13] }; } };
      }
      let label, kids, neg = null;
      if (e.e === "not") { const k = node(e.a); return { h: k.h, w: k.w + 14, draw(x, y) { const r = k.draw(x, y, k.w); return { svg: r.svg + `<circle cx="${r.out[0] + 5}" cy="${r.out[1]}" r="4" class="neg"/>`, out: [r.out[0] + 9, r.out[1]] }; } }; }
      if (e.e === "bin") {
        const op = e.op;
        kids = ["AND", "OR", "XOR"].includes(op) ? flat(e, op) : [e.a, e.b];
        label = { AND: "&", OR: "≥1", XOR: "=1", "+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV", MOD: "MOD", "**": "EXPT" }[op] || op;
      } else if (e.e === "call") { const ins = e.args.filter((a) => a.v); kids = ins.map((a) => a.v); label = WQPLC.exprText(e.f); var pinNames = ins.map((a) => a.name || ""); var outNames = e.args.filter((a) => a.out).map((a) => a.name); }
      else if (e.e === "neg") { kids = [e.a]; label = "NEG"; }
      else return { h: 26, w: 60, draw(x, y) { return { svg: `<text x="${x}" y="${y + 17}" class="fv">?</text>`, out: [x + 60, y + 13] }; } };
      const ks = kids.map(node);
      const kw = Math.max(...ks.map((k) => k.w));
      const kh = ks.reduce((s, k) => s + k.h, 0);
      const BW2 = (typeof pinNames !== "undefined" && pinNames.some((x) => x)) ? 70 : 44;
      const pn = typeof pinNames !== "undefined" ? pinNames : [], on = typeof outNames !== "undefined" ? outNames : [];
      return { h: Math.max(kh, 34), w: kw + 18 + BW2, draw(x, y) {
        let svg = "", yy = y;
        const pins = [];
        ks.forEach((k) => { const r = k.draw(x, yy, kw); svg += r.svg; pins.push(r.out); yy += k.h; });
        const bx = x + kw + 14, by = y + 2, bh = Math.max(kh, 34) - 4;
        pins.forEach(([px, py], i) => { svg += `<polyline points="${px},${py} ${bx - 6},${py} ${bx},${py}" class="w" fill="none"/>`; if (pn[i]) svg += `<text x="${bx + 4}" y="${py + 4}" class="pin">${esc(pn[i])}</text>`; });
        svg += `<rect x="${bx}" y="${by}" width="${BW2}" height="${bh}" class="fb"/><text x="${bx + BW2 / 2}" y="${by + 15}" class="fl">${esc(label)}</text>`;
        on.forEach((nm, i) => { svg += `<text x="${bx + BW2 - 4}" y="${by + bh / 2 + 4 + i * 14}" class="pin" text-anchor="end">${esc(nm)}</text>`; });
        return { svg, out: [bx + BW2, by + bh / 2] };
      } };
    }
    return node(x);
  }
  function paintFbd() {
    fbdNets.innerHTML = "";
    S.fbd.forEach((n, k) => {
      const box = el("div", "fbdnet");
      const hd = el("div", "runghead");
      hd.append(el("span", "rungno", String(k + 1)));
      const cm = el("input", "rungcm"); cm.type = "text"; cm.placeholder = T("网络注释", "Network comment"); cm.value = n.comment || "";
      cm.addEventListener("input", () => { n.comment = cm.value; persist(); });
      const del = el("button", "btn chip", "✕"); del.title = T("删除网络", "Delete network");
      del.addEventListener("click", () => { S.fbd.splice(k, 1); if (!S.fbd.length) S.fbd.push({ comment: "", text: "" }); persist(); paintFbd(); });
      hd.append(cm, del);
      const inp = el("input", "fbdtext"); inp.type = "text"; inp.value = n.text; inp.placeholder = T("如：M1_Run := (S1_Start OR M1_Run) AND S2_Stop", "e.g. M1_Run := (S1_Start OR M1_Run) AND S2_Stop");
      inp.addEventListener("change", () => { n.text = inp.value; persist(); paintFbd(); });
      const pic = el("div", "fbdpic");
      box.append(hd, inp, pic);
      fbdNets.appendChild(box);
      drawNet(n, pic);
    });
  }
  function drawNet(n, pic) {
    if (!n.text.trim()) { pic.innerHTML = ""; return; }
    let stmt;
    try { stmt = WQPLC.parse(`PROGRAM X\n${n.text.trim().replace(/;?$/, ";")}\nEND_PROGRAM`).pous[0].body[0]; } catch (e) { pic.textContent = errText(e); return; }
    if (!stmt) { pic.innerHTML = ""; return; }
    let tree, target;
    if (stmt.s === "assign") { tree = fbdBlocks(stmt.v); target = WQPLC.exprText(stmt.target); }
    else if (stmt.s === "call") { tree = fbdBlocks(stmt.call); target = (stmt.call.args.filter((a) => a.out).map((a) => WQPLC.exprText(a.out)).join(", ")); }
    else { pic.textContent = T("一个网络写一条赋值或一次功能块调用。", "One assignment or one block call per network."); return; }
    const r = tree.draw(6, 6, tree.w);
    const tv = S.rt ? S.rt.watchAny(target) : undefined;
    const w = tree.w + 30 + target.length * 7 + 40, h = tree.h + 12;
    pic.innerHTML = `<svg viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">${r.svg}<line x1="${r.out[0]}" y1="${r.out[1]}" x2="${r.out[0] + 24}" y2="${r.out[1]}" class="w${tv === true ? " on" : ""}"/><text x="${r.out[0] + 28}" y="${r.out[1] + 4}" class="fv${tv === true ? " on" : ""}">${target.replace(/&/g, "&amp;").replace(/</g, "&lt;")}</text></svg>`;
  }
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
  const bRev = biText(el("button", "btn"), ["程序检查", "Review the program"]);
  const revList = el("ul", "plcreview");
  testv.firstChild.insertBefore(bRev, testv.firstChild.children[1]);
  testv.appendChild(revList);
  bRev.addEventListener("click", runReview);
  function runReview() {
    const prog = source();
    const res = WQPLC.review(prog, io);
    revList.innerHTML = "";
    if (!res.length) revList.appendChild(biText(el("li", "ok"), ["没有发现问题。", "No findings."]));
    res.forEach((r) => {
      const li = el("li", r.level);
      li.append(el("span", "lv", { error: "✗", warning: "!", info: "i" }[r.level]), biText(el("span"), [(r.line ? `第 ${r.line} 行：` : "") + r.msg[0], (r.line ? `Line ${r.line}: ` : "") + r.msg[1]]));
      revList.appendChild(li);
    });
    if (!res.some((r) => r.level === "error")) def.tasks.filter((k) => k.review).forEach((k) => api.done(k.id));
    return res;
  }
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
      const names = p.names || [p.name];   // names: one button holding several inputs (e.g. both hand buttons at once)
      if (p.kind === "switch") {
        b.setAttribute("aria-pressed", String(!!S.panel[p.name]));
        b.addEventListener("click", () => { S.panel[p.name] = !S.panel[p.name]; b.setAttribute("aria-pressed", String(S.panel[p.name])); });
      } else if (p.kind === "estop") {      // latching e-stop with an NC contact: press to latch (input 0), press again to release (twist-to-release)
        if (S.panel[p.name] === undefined) S.panel[p.name] = true;
        b.setAttribute("aria-pressed", String(!S.panel[p.name]));
        b.addEventListener("click", () => { S.panel[p.name] = !S.panel[p.name]; b.setAttribute("aria-pressed", String(!S.panel[p.name])); });
      } else {
        const down = () => { names.forEach((n) => { S.panel[n] = p.kind !== "nc-push"; }); b.classList.add("down"); };
        const up = () => { names.forEach((n) => { S.panel[n] = p.kind === "nc-push"; }); b.classList.remove("down"); };
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
    const base = { io, cycle: cfg.cycle || 10, filter: cfg.filter || 0, budget: cfg.budget || 100000, scanModel: cfg.scanModel || null,
                   cycleMode: cfg.cycleMode || "fixed", watchdog: cfg.watchdog || 0 };
    try {
      const o = Object.assign(base, source()); new WQPLC.Runtime(o); return o;
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
    const ins = {};
    io.forEach((x) => {
      if (x.dir !== "in") return;
      const v = x.name in S.panel ? S.panel[x.name] : x.name in fromPlant ? fromPlant[x.name] : undefined;
      if (v !== undefined) { rt.phys[x.addr] = v; ins[x.name] = v; }
    });
    for (const k in S.panel) if (!(k in ins) && !io.some((x) => x.name === k)) ins[k] = S.panel[k];   // operator actions on the machine
    const t0 = rt.now;
    const ok = rt.scan();
    if (plant.step) plant.step(ok ? rt.now - t0 : rt.cycle, rt.outputs(), S.ps, ins);
    S.lastDt = ok ? rt.now - t0 : rt.cycle;
    if (!ok) {
      api.running = false; say(T("PLC 停机（STOP）：", "PLC stopped: ") + errText(rt.error), "bad");
      if (def.check) def.check(api, S.ps);   // readouts (and with them the lab's check) stop once the run ends: let the check see the stop
    }
    return ok;
  }
  function paintStatus() {
    const rt = S.rt;
    const st = !rt ? ["未下载", "No program"] : rt.error ? ["故障 STOP", "FAULT STOP"] : api.running ? ["运行 RUN", "RUN"] : ["停止 STOP", "STOP"];
    const sm = rt && rt.scanModel && rt.scans ? T(` · 扫描时间 ${rt.lastScan.toFixed(2)} ms（最长 ${rt.maxScan.toFixed(2)}）` + (rt.overruns ? ` · 超时 ${rt.overruns} 次` : ""),
                                                   ` · scan ${rt.lastScan.toFixed(2)} ms (max ${rt.maxScan.toFixed(2)})` + (rt.overruns ? ` · ${rt.overruns} overruns` : "")) : "";
    status.textContent = P(st) + (rt ? T(` · 扫描 ${rt.scans} 次 · 周期 ${rt.cycle} ms`, ` · ${rt.scans} scans · cycle ${rt.cycle} ms`) + sm : "");
    status.className = "plcstatus " + (!rt || rt.error ? "bad" : api.running ? "run" : "");
  }

  // the kit's hooks
  def.reset = () => { if (S.rt) { const o = rtOptions(); if (o) { S.rt = new WQPLC.Runtime(o); S.rt.startTrace(io.map((x) => x.name).concat(watchList).slice(0, 14), 3000); api.plc.rt = S.rt; } } resetPlant(); syncIo(); paintStatus(); paintIo(); };
  def.start = () => { if (!S.rt || S.rt.error) load(); if (!S.rt) { api.running = false; return; } };
  def.update = (dt) => {
    if (!S.rt) { api.running = false; return; }
    S.acc += dt * 1000 * S.speed;
    let n = 0;
    while (S.acc >= (S.rt.scanModel ? Math.max(0.05, S.rt.lastScan || S.rt.cycle) : S.rt.cycle) && n < 2000) {   // variable scans (Ch. 4): consume the time each scan really took
      const ok = scanOnce(); n++; S.acc -= S.lastDt; if (!ok) break;
    }
    syncIo();
  };
  def.action = (id) => {
    if (id === "stop") { api.running = false; }
    else if (id === "step") { if (!S.rt) load(); if (S.rt) { api.running = false; scanOnce(); syncIo(); } }
    else if (id === "slow") { S.speed = S.speed === 1 ? 0.1 : 1; }
    else if (id === "power" && S.rt) {   // power off and on: outputs drop, RETAIN variables survive, the machine stays where it is
      S.rt.restart(); syncIo();
      say(T("已断电再上电：输出全部断开，保持型（RETAIN）变量保留，其余变量回到初值。", "Power cycled: outputs off, RETAIN variables kept, the rest back to initial values."), "ok");
    }
    paintStatus();
  };
  // a task's demo (the automatic trial run, WQ.demo): {program: {st} | {sfc}, faults, tests: true, review: true, run: true, panel: {name: v}, release: ms, wait: s}
  def.plcDemo = (d) => {
    if (d.program) {
      if (d.program.sfc != null) { S.sfc = d.program.sfc; setLang("SFC"); } else { S.st = d.program.st; setLang("ST"); }
      ta.value = S.lang === "SFC" ? S.sfc : S.st; paintGutter();
    }
    Object.assign(S.faults, d.faults || {}); paintPanel();
    load();
    if (d.tests) runTests();
    if (d.review) runReview();
    if (d.panel) {
      Object.assign(S.panel, d.panel);
      if (d.release) setTimeout(() => { Object.keys(d.panel).forEach((k) => { S.panel[k] = !d.panel[k]; }); }, d.release);
    }
    if (d.run && S.rt) api.running = true;
    return d.wait || 5;
  };
  const userReadouts = def.readouts;
  def.readouts = (a, s) => {
    paintStatus();
    if (!document.hidden) { if (S.tab === "io") paintIo(); if (S.tab === "trace") drawTrace(); if (S.tab === "prog" && S.rt && (api.running || !S.drawnOnce)) { S.drawnOnce = true; paintLadderLive(); } }
    if (def.check) def.check(api, S.ps);
    return userReadouts ? userReadouts(a, S.ps) : [];
  };
  let lastLive = 0;
  function paintLadderLive() {
    const t = performance.now();
    if (t - lastLive < 150) return;
    lastLive = t;
    if (S.lang === "LD") paintLadder();
    else if (S.lang === "SFC") paintSfc();
    else if (S.lang === "FBD") fbdNets.querySelectorAll(".fbdpic").forEach((pic, k) => drawNet(S.fbd[k], pic));
  }
  const userDraw = def.draw;
  if (plant.build3d) {
    // the machine in 3D: the kit treats the lab as a 3D lab (it resizes and renders L.st every frame)
    if (!window.WQ3D) throw new Error("this page has no 3D engine (a PLC lab on WQPLANTS needs it)");
    const E3 = window.WQ3D;
    const st = E3.stage(L.dom.canvas, { width: 800, height: 500, theme: "light" });
    L.st = st;
    S.view3d = plant.build3d(st, E3.THREE);
    try {
      L.orbit = new E3.OrbitControls(st.camera, L.dom.canvas);
      L.orbit.enableDamping = true;
      if (st.target) { L.orbit.target.set(...st.target); L.orbit.update(); }
    } catch (e) { /* view rotation is optional */ }
    api.st = st;
    def.draw = (a) => { plant.draw3d(S.view3d, S.ps, api.plc.io); if (userDraw) userDraw(a, S.ps); };
    L.ready = true;
  } else def.draw = (a) => userDraw(a, S.ps);

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
