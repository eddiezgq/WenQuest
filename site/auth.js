/* WenQuest site-wide sign-in state for the academy website (round 3, step C).
   Fills every [data-wq-auth] element with "Sign in / Sign up" or "Name · Learning platform".
   The sign-in cookie is shared across wenquestrobotics.com; /api/v1/auth/whoami reads it. */
(function () {
  var els = document.querySelectorAll("[data-wq-auth]");
  if (!els.length) return;
  var host = location.hostname.replace(/^www\./, "");
  var local = host === "localhost" || host === "127.0.0.1" || location.protocol === "file:";
  var learn = local ? "http://localhost:8088" : location.protocol + "//learn." + host;
  var here = encodeURIComponent(location.href);
  var css = document.createElement("style");
  css.textContent =
    ".wq-auth{display:inline-flex;align-items:center;gap:14px;white-space:nowrap;font-size:14px}" +
    ".wq-auth a{color:inherit;text-decoration:none}.wq-auth a:hover{text-decoration:underline}" +
    ".wq-auth a.wq-up{background:#f2b705;color:#121c21;font-weight:600;padding:6px 14px;border-radius:999px;text-decoration:none}" +
    ".wq-auth a.wq-me{display:inline-flex;align-items:center;gap:8px}" +
    ".wq-auth .wq-av{width:24px;height:24px;border-radius:50%;background:#f2b705;color:#121c21;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:12px}" +
    'html:not([lang="en"]) .wq-auth [data-en],html[lang="en"] .wq-auth [data-zh]{display:none}';
  document.head.appendChild(css);
  var T = function (zh, en) { return "<span data-zh>" + zh + "</span><span data-en>" + en + "</span>"; };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return "&#" + c.charCodeAt(0) + ";"; }); };

  function render(user) {
    var html = user
      ? '<a class="wq-me" href="' + learn + '/pages/courses/courses"><span class="wq-av">' + esc((user.fullname || "?").trim().slice(0, 1)) +
        "</span>" + esc(user.fullname) + "</a>" +
        '<a class="wq-up" href="' + learn + '/pages/courses/courses">' + T("进入学习平台", "Learning platform") + "</a>" +
        '<a href="#" data-wq-out>' + T("退出", "Sign out") + "</a>"
      : '<a href="' + learn + "/pages/login/login?back=" + here + '">' + T("登录", "Sign in") + "</a>" +
        '<a class="wq-up" href="' + learn + "/pages/register/register?back=" + here + '">' + T("注册", "Sign up") + "</a>";
    for (var i = 0; i < els.length; i++) {
      els[i].classList.add("wq-auth");
      els[i].innerHTML = html;
      var out = els[i].querySelector("[data-wq-out]");
      if (out) out.addEventListener("click", signOut);
    }
  }
  // Sign out everywhere: clearing the shared cookie also signs the learning platform out the next time it opens.
  function signOut(e) {
    e.preventDefault();
    fetch("/api/v1/auth/logout", { method: "POST", credentials: "same-origin" })
      .catch(function () {})
      .then(function () { render(null); });
  }
  render(null);
  if (local) return;
  fetch("/api/v1/auth/whoami", { credentials: "same-origin" })
    .then(function (r) { return r.ok ? r.json() : { user: null }; })
    .then(function (d) { if (d && d.user) render(d.user); })
    .catch(function () {});
})();
