/* 问渠科技 · 国内版官网脚本（第 48 轮）：菜单、首屏“数字主线”动画、预约演示表单。 */
(function () {
  'use strict';

  // ---------- 菜单 ----------
  var burger = document.querySelector('.burger');
  var nav = document.querySelector('nav.main');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  document.querySelectorAll('.dd > button').forEach(function (b) {
    b.addEventListener('click', function (e) {
      var dd = b.parentElement;
      var open = !dd.classList.contains('open');
      document.querySelectorAll('.dd.open').forEach(function (x) { x.classList.remove('open'); });
      if (open) dd.classList.add('open');
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
      e.stopPropagation();
    });
  });
  document.addEventListener('click', function () {
    document.querySelectorAll('.dd.open').forEach(function (x) { x.classList.remove('open'); });
  });

  // ---------- 首屏：一条“渠”把八个模块连起来，数据像水一样流过，AI 在节点处点亮 ----------
  var cv = document.getElementById('thread');
  if (cv && cv.getContext) {
    var ctx = cv.getContext('2d');
    var NODES = ['CAD', '审批', 'ERP', 'MRP', 'MES', 'CAM', '质量', '厂情中枢'];
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var W = 0, H = 0, dpr = 1, pts = [], drops = [], t0 = performance.now();
    function layout() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = cv.clientWidth; H = cv.clientHeight;
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      pts = [];
      var narrow = W < 700;
      for (var i = 0; i < NODES.length; i++) {
        var u = i / (NODES.length - 1);
        var x = narrow ? W * (0.1 + 0.8 * u) : W * (0.62 + 0.34 * u);
        var y = narrow ? 62 + 16 * Math.sin(u * Math.PI * 2) : H * (0.10 + 0.50 * u + 0.05 * Math.sin(u * Math.PI * 2.2));
        pts.push([x, y]);
      }
      drops = [];
      for (var k = 0; k < (narrow ? 26 : 60); k++) drops.push({ s: Math.random(), v: 0.035 + Math.random() * 0.05, o: (Math.random() - 0.5) * 10 });
    }
    function at(s) { // 沿折线插值
      var n = pts.length - 1, f = Math.min(Math.max(s, 0), 1) * n, i = Math.min(Math.floor(f), n - 1), r = f - i;
      return [pts[i][0] + (pts[i + 1][0] - pts[i][0]) * r, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * r];
    }
    function frame(now) {
      var t = (now - t0) / 1000;
      ctx.clearRect(0, 0, W, H);
      // 渠：两条平行的细线
      ctx.lineWidth = 1;
      for (var side = -1; side <= 1; side += 2) {
        ctx.strokeStyle = 'rgba(28,156,143,0.35)';
        ctx.beginPath();
        for (var i = 0; i < pts.length; i++) {
          var x = pts[i][0], y = pts[i][1] + side * 9;
          if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }
      // 水滴（数据）
      for (var k = 0; k < drops.length; k++) {
        var d = drops[k];
        if (!reduce) d.s += d.v / 60;
        if (d.s > 1) d.s -= 1;
        var p = at(d.s);
        ctx.fillStyle = 'rgba(79,209,193,' + (0.25 + 0.6 * Math.sin(d.s * Math.PI)) + ')';
        ctx.beginPath(); ctx.arc(p[0], p[1] + d.o * 0.6, 1.8, 0, Math.PI * 2); ctx.fill();
      }
      // 节点：AI 依次点亮（起草），稍后变成琥珀色（人批准）
      var active = reduce ? -1 : Math.floor(t / 1.1) % pts.length;
      ctx.font = '500 12px "Noto Sans SC", system-ui, sans-serif';
      ctx.textAlign = 'center';
      for (var j = 0; j < pts.length; j++) {
        var q = pts[j], on = j === active, phase = reduce ? 0 : (t / 1.1) % 1;
        ctx.fillStyle = '#08141b';
        ctx.strokeStyle = on ? (phase < 0.55 ? '#4fd1c1' : '#e8a50b') : 'rgba(142,164,172,0.6)';
        ctx.lineWidth = on ? 2 : 1;
        ctx.beginPath(); ctx.arc(q[0], q[1], on ? 9 : 6, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        if (on) {
          ctx.strokeStyle = 'rgba(79,209,193,' + (0.5 * (1 - phase)) + ')';
          ctx.beginPath(); ctx.arc(q[0], q[1], 9 + 26 * phase, 0, Math.PI * 2); ctx.stroke();
        }
        ctx.fillStyle = on ? '#e8f0f2' : 'rgba(200,214,218,0.7)';
        ctx.fillText(NODES[j], q[0], q[1] - 16);
        if (on) {
          ctx.fillStyle = phase < 0.55 ? '#4fd1c1' : '#e8a50b';
          ctx.fillText(phase < 0.55 ? 'AI 起草' : '人批准', q[0], q[1] + 26);
        }
      }
      if (!reduce) requestAnimationFrame(frame);
    }
    layout();
    window.addEventListener('resize', function () { layout(); if (reduce) frame(performance.now()); });
    requestAnimationFrame(frame);
  }

  // ---------- 预约演示表单 ----------
  var form = document.getElementById('demo-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var msg = form.querySelector('.msg');
      var fd = new FormData(form);
      var body = {
        org: (fd.get('org') || '').trim(), name: (fd.get('name') || '').trim(), phone: (fd.get('phone') || '').trim(),
        email: (fd.get('email') || '').trim(), industry: (fd.get('industry') || '').trim(),
        products: fd.getAll('products'), note: (fd.get('note') || '').trim(),
        consent: !!fd.get('consent'), website: fd.get('website') || ''
      };
      msg.className = 'msg'; msg.textContent = '正在提交…';
      fetch('/api/v1/public/demo-request', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
        .then(function (r) { return r.json().then(function (j) { return [r.ok, j]; }); })
        .then(function (res) {
          if (res[0]) { msg.className = 'msg ok'; msg.textContent = '已收到，我们会在 2 个工作日内联系你。'; form.reset(); }
          else { msg.className = 'msg err'; msg.textContent = (res[1] && typeof res[1].detail === 'string' && res[1].detail) || '提交没有成功，请检查后再试，或直接打电话、发邮件给我们。'; }
        })
        .catch(function () { msg.className = 'msg err'; msg.textContent = '网络不通，请稍后再试，或直接打电话、发邮件给我们。'; });
    });
  }
})();
