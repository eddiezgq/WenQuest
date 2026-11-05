/* 官网“看视频认识问渠”（第 80 轮）：读 /data/videos.json（工作流 site-videos.yml 每天从 YouTube 播放列表生成，只含公开视频），
   把视频画成卡片；点画面才加载 YouTube 播放器（youtube-nocookie），页面不因视频变慢。
   用法：WQVideos.render({pop: 元素, sew: 元素, popN: 3（中英各几期，0 = 全部）, sewLatest: 1, pinned: [...], all: false}) */
(function () {
  var EN = function () { return document.documentElement.lang === 'en'; };
  function T(zh, en) { return '<span data-zh>' + zh + '</span><span data-en>' + en + '</span>'; }
  function esc(s) { return String(s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function dur(iso) {
    var m = /PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/.exec(iso || '');
    if (!m) return '';
    var h = +m[1] || 0, mi = +m[2] || 0, s = +m[3] || 0;
    return (h ? h + ':' + String(mi).padStart(2, '0') : mi) + ':' + String(s).padStart(2, '0');
  }
  function card(v, extra) {
    var bv = v.bv ? ' · <a href="https://www.bilibili.com/video/' + esc(v.bv) + '" target="_blank" rel="noopener">B 站</a>' : '';
    return '<div class="vcard"><button class="play" type="button" data-yt="' + esc(v.id) + '" aria-label="' + esc(v.title) + '"' +
      ' style="background-image:url(https://i.ytimg.com/vi/' + esc(v.id) + '/hqdefault.jpg)"></button>' +
      '<div class="cap">' + esc(v.title) + '<small>' + (extra || '') + (v.date ? esc(v.date) : '') + (v.dur ? ' · ' + dur(v.dur) : '') +
      ' · <a href="https://www.youtube.com/watch?v=' + esc(v.id) + '" target="_blank" rel="noopener">YouTube</a>' + bv + '</small></div></div>';
  }
  function empty(channel) {
    return '<div class="vempty">' + T('即将上线：视频在 YouTube 上公开后会自动出现在这里。', 'Coming soon: videos appear here as soon as they are public on YouTube.') +
      (channel ? ' <a href="' + esc(channel) + '" target="_blank" rel="noopener">' + T('去频道看看 →', 'Visit the channel →') + '</a>' : '') + '</div>';
  }
  function wire(root) {
    root.addEventListener('click', function (e) {
      var b = e.target.closest && e.target.closest('button.play');
      if (!b) return;
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(b.dataset.yt) + '?autoplay=1&rel=0';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      f.title = b.getAttribute('aria-label') || 'video';
      b.replaceWith(f);
    });
  }
  function render(o) {
    fetch('/data/videos.json', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; }).then(function (d) {
      var L = (d && d.lists) || {}, ch = (d && d.channel) || '';
      var pz = L.pop_zh || [], pe = L.pop_en || [], sz = L.sew_zh || [], se = L.sew_en || [];
      if (o.pop) {
        var n = o.popN || 0, list = [];
        if (n) { list = pz.slice(0, n).concat(pe.slice(0, n)); }
        else { list = pz.concat(pe).sort(function (a, b) { return a.date < b.date ? 1 : -1; }); }
        o.pop.innerHTML = list.length ? list.map(function (v) { return card(v); }).join('') : empty(ch);
        wire(o.pop);
      }
      if (o.sew) {
        var pub = {}; sz.concat(se).forEach(function (v) { pub[v.id] = v; });
        var shown = [], used = {};
        if (!o.all) {
          (o.pinned || []).forEach(function (p) {
            var ids = [p.yt, EN() ? p.yt_en : p.yt_zh, p.yt_zh, p.yt_en].filter(Boolean);
            for (var i = 0; i < ids.length; i++) {
              if (pub[ids[i]]) { shown.push(Object.assign({}, pub[ids[i]], { bv: p.bv })); used[ids[i]] = 1; return; }
            }
          });
          sz.concat(se).sort(function (a, b) { return a.date < b.date ? 1 : -1; })
            .filter(function (v) { return !used[v.id]; }).slice(0, Math.max(o.sewLatest || 1, 3 - shown.length))
            .forEach(function (v) { shown.push(v); });
        } else {
          shown = sz.concat(se).sort(function (a, b) { return a.date < b.date ? 1 : -1; });
        }
        o.sew.innerHTML = shown.length ? shown.map(function (v) { return card(v); }).join('') : empty(ch);
        wire(o.sew);
      }
    });
  }
  window.WQVideos = { render: render };
})();
