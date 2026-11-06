/* 问渠质量 ERP 试点企业注册（第 97 轮）：凭邀请链接 /pilot/?t=<邀请码> 填写、邮箱验证码确认、等待自动开通。
   国内版官网和美国官网共用；页面里放 <div id="pilot"></div>，语言跟邀请（?lang=en 或邀请里的语言）。 */
(function () {
  var box = document.getElementById("pilot");
  if (!box) return;
  var Q = new URLSearchParams(location.search), token = Q.get("t") || "";
  var API = "/api/v1/public/pilot/" + encodeURIComponent(token);
  var T = {
    zh: { title: "开通问渠质量 ERP 试点", lead: "免费试用 3 个月。每家单位一套独立的系统，数据单独隔离。填好下面几项，用受邀邮箱收验证码确认，系统自动开通（约 15 分钟），账号发到你的邮箱。",
      bad: "邀请链接无效或已过期，请联系邀请你的人重新发送。", used: "这个邀请已经用过了。", company: "单位全称", id: "简称（网址里用，小写字母、数字或 -，3–20 位）",
      contact: "联系人姓名（系统里的老板账号）", code: "邮箱验证码", send: "发验证码到", go: "提交开通", sent: "验证码已发到 ", url: "你的网址：",
      queued: "已提交，排队开通中……", installing: "正在开通，大约 10–15 分钟，可以关掉这页，好了会发邮件给你。", active: "已开通！账号和初始密码已发到你的邮箱。打开：",
      failed: "开通没有成功，我们已收到通知，会尽快联系你。", stopped: "这家试点已停用。", err: "出错了，请稍后再试。" },
    en: { title: "Open your WenQuest Ops pilot", lead: "Free for 3 months - your own separate installation. Fill in the form, confirm with the code we email to the invited address, and it is set up automatically (about 15 minutes); the sign-in is emailed to you.",
      bad: "This invitation link is not valid or has expired. Ask whoever invited you to send a new one.", used: "This invitation has been used.", company: "Company name",
      id: "Short name (used in your web address: lower-case letters, digits or -, 3-20)", contact: "Your name (the owner account)", code: "Code from the email",
      send: "Send the code to", go: "Open it", sent: "Code sent to ", url: "Your address: ", queued: "Submitted - waiting to be set up…",
      installing: "Being set up - about 10-15 minutes. You can close this page; we will email you.", active: "Ready! The sign-in has been emailed to you. Open: ",
      failed: "The setup did not succeed. We have been told and will contact you.", stopped: "This pilot has been stopped.", err: "Something went wrong - please try again later." }
  };
  var t = T.zh, info = null, timer = 0;
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function call(path, body) {
    return fetch(API + path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {})
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw j; return j; }); });
  }
  function msg(e) { return (e && typeof e.detail === "string" && e.detail) || t.err; }
  function status(s) {
    box.textContent = "";
    box.appendChild(el("h1", "", t.title));
    var p = el("p", "pl-status " + (s.status || ""), t[s.status] || t.queued);
    if (s.url) { var a = el("a", "", s.url); a.href = s.url; p.appendChild(a); }
    box.appendChild(p);
    clearTimeout(timer);
    if (s.status === "queued" || s.status === "installing") timer = setTimeout(poll, 20000);
  }
  function poll() { call("/status").then(status).catch(function () { timer = setTimeout(poll, 30000); }); }
  function form() {
    box.textContent = "";
    box.appendChild(el("h1", "", t.title));
    box.appendChild(el("p", "lead", t.lead));
    var f = el("form", "pl-form"), err = el("p", "pl-err"), fields = {};
    [["company", 100], ["id", 20], ["contact", 40]].forEach(function (x) {
      var l = el("label", "", t[x[0]]), i = el("input"); i.name = x[0]; i.maxLength = x[1]; i.required = true;
      if (x[0] === "company" && info.company) i.value = info.company;
      if (x[0] === "id") { i.pattern = "[a-z][a-z0-9\\-]{2,19}"; i.autocapitalize = "off"; i.spellcheck = false; }
      l.appendChild(i); f.appendChild(l); fields[x[0]] = i;
    });
    var hint = el("p", "pl-hint", "");
    fields.id.addEventListener("input", function () {
      fields.id.value = fields.id.value.toLowerCase().replace(/[^a-z0-9-]/g, "");
      hint.textContent = fields.id.value ? t.url + "https://" + info.domain.replace("<编号>", fields.id.value) : "";
    });
    f.insertBefore(hint, fields.contact.parentNode);
    var row = el("div", "pl-code"), cl = el("label", "", t.code), ci = el("input"); ci.name = "code"; ci.maxLength = 6; ci.inputMode = "numeric"; ci.required = true;
    cl.appendChild(ci); row.appendChild(cl);
    var sb = el("button", "btn", t.send + " " + info.email); sb.type = "button";
    sb.onclick = function () {
      sb.disabled = true; err.className = "pl-err"; err.textContent = "";
      call("/code", {}).then(function (r) { err.className = "pl-ok"; err.textContent = t.sent + r.email; setTimeout(function () { sb.disabled = false; }, 60000); })
        .catch(function (e) { err.textContent = msg(e); sb.disabled = false; });
    };
    row.appendChild(sb); f.appendChild(row);
    var go = el("button", "btn solid", t.go); go.type = "submit"; f.appendChild(go); f.appendChild(err);
    f.onsubmit = function (ev) {
      ev.preventDefault(); go.disabled = true; err.className = "pl-err"; err.textContent = "";
      call("/apply", { company: fields.company.value.trim(), id: fields.id.value.trim(), contact: fields.contact.value.trim(), code: ci.value.trim() })
        .then(function () { poll(); })
        .catch(function (e) { err.textContent = msg(e); go.disabled = false; });
    };
    box.appendChild(f);
  }
  if (!token) { box.appendChild(el("p", "pl-err", T[Q.get("lang") === "en" ? "en" : "zh"].bad)); return; }
  fetch(API).then(function (r) { return r.json().then(function (j) { if (!r.ok) throw j; return j; }); })
    .then(function (j) {
      info = j; t = T[(Q.get("lang") || j.lang) === "en" ? "en" : "zh"];
      document.documentElement.lang = t === T.en ? "en" : "zh-CN";
      if (j.status) poll(); else if (j.used) box.appendChild(el("p", "pl-err", t.used)); else form();
    })
    .catch(function (e) { t = T[Q.get("lang") === "en" ? "en" : "zh"]; box.textContent = ""; box.appendChild(el("p", "pl-err", (e && typeof e.detail === "string" && e.detail) || t.bad)); });
})();
