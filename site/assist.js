/* 问渠客服小组件（第 87 轮）：页面右下角一个按钮，点开问问题。接口 POST /api/v1/public/assist。
   页面里加一行即可：<script src="/assist.js" defer></script>（国内版官网用 /assets/assist.js）。
   语言跟着页面 <html lang> 走；答案带出处，AI 生成的回答标“AI 生成”。 */
(function () {
  if (window.__wqAssist) return;
  window.__wqAssist = true;
  var API = (window.WQ_ASSIST_API || "") + "/api/v1/public/assist";
  var T = {
    zh: { btn: "问问问渠", title: "问渠客服", ph: "问一个问题，例如：数控编程怎么出 G 代码？", send: "问",
          hello: "你好！我按问渠的使用说明回答问题。可以问某个模块是什么、怎么用、在哪里打开。",
          ai: "AI 生成，依据下面的资料", faq: "常见问题（人工整理）", search: "摘自使用说明原文（非 AI 生成）", src: "出处",
          none: "这个问题资料里没有。请留下联系方式，我们回复你。",
          unsure: "这个我不确定。", contact: "联系我们 / 预约演示", busy: "正在找……", err: "出错了，请稍后再试。",
          price: "价格、合同请预约演示，我们当面谈。", close: "关闭" },
    en: { btn: "Ask WenQuest", title: "WenQuest assistant", ph: "Ask a question, e.g. how do I generate G-code?", send: "Ask",
          hello: "Hi! I answer from WenQuest's user guides. Ask what a module is, how to use it, or where to open it.",
          ai: "AI-generated, based on the sources below", faq: "Common question (written by our team)",
          search: "Quoted from the user guides (not AI-generated)", src: "Sources",
          none: "Our guides don't cover this. Leave your details and we'll get back to you.", unsure: "I'm not sure about this.", contact: "Contact us / book a demo",
          busy: "Looking…", err: "Something went wrong — please try again later.", price: "", close: "Close" }
  };
  function L() { return (document.documentElement.lang || "zh").toLowerCase().indexOf("en") === 0 ? "en" : "zh"; }
  var css = ".wqa-b{position:fixed;right:16px;bottom:16px;z-index:2147483000;border:0;border-radius:999px;padding:11px 16px;" +
    "font:600 15px/1 system-ui,'PingFang SC','Microsoft YaHei',sans-serif;color:#fff;background:linear-gradient(135deg,#2563eb,#7c3aed);" +
    "box-shadow:0 6px 20px rgba(37,99,235,.35);cursor:pointer}.wqa-b:focus-visible{outline:3px solid #f59e0b;outline-offset:2px}" +
    ".wqa-p{position:fixed;right:16px;bottom:70px;z-index:2147483001;width:min(380px,calc(100vw - 32px));height:min(540px,calc(100vh - 100px));" +
    "display:none;flex-direction:column;background:#fff;color:#14202a;border:1px solid #d6dbe1;border-radius:14px;overflow:hidden;" +
    "box-shadow:0 12px 40px rgba(0,0,0,.22);font:14.5px/1.6 system-ui,'PingFang SC','Microsoft YaHei',sans-serif}" +
    ".wqa-p.on{display:flex}.wqa-h{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;color:#fff;" +
    "background:linear-gradient(135deg,#2563eb,#7c3aed);font-weight:600}.wqa-h button{background:none;border:0;color:#fff;font-size:20px;cursor:pointer}" +
    ".wqa-m{flex:1;overflow-y:auto;padding:12px 14px}.wqa-q{margin:10px 0 6px auto;max-width:85%;width:fit-content;background:#e8effe;" +
    "border-radius:12px 12px 2px 12px;padding:6px 10px}.wqa-a{margin:6px 0 12px;padding:8px 10px;background:#f5f6f8;border-radius:12px 12px 12px 2px}" +
    ".wqa-a .tag{display:inline-block;font-size:12px;color:#6b4bd8;margin-bottom:4px}.wqa-a ul{margin:4px 0;padding-left:18px}" +
    ".wqa-a .s{font-size:13px;color:#4b5a66;margin-top:6px}.wqa-a .s b{display:block;color:#14202a}.wqa-a a{color:#2563eb}" +
    ".wqa-a .sn{font-size:12.5px;color:#5c6b75}.wqa-f{display:flex;gap:6px;padding:10px;border-top:1px solid #e3e6ea}" +
    ".wqa-f input{flex:1;min-width:0;border:1px solid #c9d0d8;border-radius:8px;padding:8px 10px;font:inherit;color:inherit;background:#fff}" +
    ".wqa-f button{border:0;border-radius:8px;padding:0 14px;background:#2563eb;color:#fff;font:600 14px system-ui;cursor:pointer}" +
    "@media (prefers-color-scheme:dark){.wqa-p{background:#111a20;color:#e3e9ec;border-color:#2a3a41}.wqa-a{background:#1a252c}" +
    ".wqa-q{background:#1d2c4a}.wqa-a .s,.wqa-a .sn{color:#9aaab2}.wqa-a .s b{color:#e3e9ec}.wqa-a a{color:#7aa7ff}" +
    ".wqa-f{border-color:#2a3a41}.wqa-f input{background:#0c1418;border-color:#33444c}}" +
    "@media print{.wqa-b,.wqa-p{display:none!important}}";
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

  function init() {
    var st = el("style"); st.textContent = css; document.head.appendChild(st);
    var b = el("button", "wqa-b"); b.type = "button"; b.setAttribute("aria-haspopup", "dialog");
    var p = el("div", "wqa-p"); p.setAttribute("role", "dialog");
    var h = el("div", "wqa-h"), ht = el("span"), x = el("button", "", "×"); x.type = "button";
    h.appendChild(ht); h.appendChild(x);
    var m = el("div", "wqa-m"); m.setAttribute("aria-live", "polite");
    var f = el("form", "wqa-f"), inp = el("input"), go = el("button"); inp.maxLength = 300; go.type = "submit";
    f.appendChild(inp); f.appendChild(go);
    p.appendChild(h); p.appendChild(m); p.appendChild(f);
    document.body.appendChild(b); document.body.appendChild(p);
    var greeted = false;
    function labels() { var t = T[L()]; b.textContent = "💬 " + t.btn; ht.textContent = t.title; inp.placeholder = t.ph; go.textContent = t.send;
      x.setAttribute("aria-label", t.close); p.setAttribute("aria-label", t.title); }
    labels();
    new MutationObserver(labels).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
    function open(on) { p.classList.toggle("on", on); b.setAttribute("aria-expanded", on ? "true" : "false");
      if (on) { if (!greeted) { greeted = true; var a = el("div", "wqa-a", T[L()].hello); m.appendChild(a); } inp.focus(); } }
    b.onclick = function () { open(!p.classList.contains("on")); };
    x.onclick = function () { open(false); b.focus(); };
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && p.classList.contains("on")) { open(false); b.focus(); } });

    function render(a, r, q) {
      var t = T[L()]; a.textContent = "";
      if (!r.sources.length && !r.answer) {             // 没找到就说没找到，不堆片段
        a.appendChild(el("div", "", t.none));
        var c0 = el("a", "", "→ " + t.contact); c0.href = r.contact || "/#contact"; a.appendChild(c0);
        return;
      }
      a.appendChild(el("span", "tag", r.mode === "ai" ? t.ai : r.mode === "faq" ? t.faq : t.search));
      if (r.answer) {
        r.answer.split(/\n+/).forEach(function (line) { if (line.trim()) a.appendChild(el("div", "", line)); });
      } else if (!r.sources.length) {
        a.appendChild(el("div", "", t.none));
      }
      if (r.unsure) a.appendChild(el("div", "", t.unsure));
      if (r.sources.length) {
        var s = el("div", "s"); s.appendChild(el("b", "", t.src));
        var ul = el("ul");
        r.sources.forEach(function (x) {
          var li = el("li");
          if (x.url) { var k = el("a", "", x.title); k.href = x.url; if (/^https?:/.test(x.url)) { k.target = "_blank"; k.rel = "noopener"; } li.appendChild(k); }
          else li.appendChild(el("span", "", x.title));
          if (r.mode === "search" && x.snippet && !r.answer) li.appendChild(el("div", "sn", x.snippet));
          ul.appendChild(li);
        });
        s.appendChild(ul); a.appendChild(s);
      }
      if (r.unsure || !r.sources.length || /价|多少钱|费用|报价|price|cost|quote/i.test(q)) {
        if (t.price && r.mode !== "faq" && /价|多少钱|费用|报价/.test(q)) a.appendChild(el("div", "", t.price));
        var c = el("a", "", "→ " + t.contact); c.href = r.contact || "/#contact"; a.appendChild(c);
      }
    }
    f.onsubmit = function (e) {
      e.preventDefault();
      var q = inp.value.trim(); if (!q) return;
      inp.value = ""; m.appendChild(el("div", "wqa-q", q));
      var a = el("div", "wqa-a", T[L()].busy); m.appendChild(a); m.scrollTop = m.scrollHeight;
      fetch(API, { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ q: q, page: location.pathname, lang: L() }) })
        .then(function (res) { return res.json().then(function (j) { if (!res.ok) throw new Error(j.detail || res.status); return j; }); })
        .then(function (r) { render(a, r, q); })
        .catch(function (err) { a.textContent = (err && err.message && !/^\d+$/.test(err.message) ? err.message : T[L()].err); })
        .then(function () { m.scrollTop = m.scrollHeight; });
    };
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
