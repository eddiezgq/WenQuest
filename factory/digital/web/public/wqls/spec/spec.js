(function(){
var b=document.body,side=document.querySelector('nav.side');
var mb=document.getElementById('menu');if(mb)mb.onclick=function(){b.classList.toggle('nav')};
if(side){side.addEventListener('click',function(e){if(e.target.closest('a'))b.classList.remove('nav')});var cur=side.querySelector('a.cur');if(cur)cur.scrollIntoView({block:'center'});}
// 深浅色
var th=document.getElementById('theme');function setT(v){if(v)document.documentElement.setAttribute('data-theme',v);else document.documentElement.removeAttribute('data-theme');}
try{setT(localStorage.getItem('wq-spec-theme'))}catch(e){}
if(th)th.onclick=function(){var d=document.documentElement.getAttribute('data-theme'),dark=d?d==='dark':matchMedia('(prefers-color-scheme: dark)').matches,v=dark?'light':'dark';setT(v);try{localStorage.setItem('wq-spec-theme',v)}catch(e){}};
// 互动块：点“在本页运行”才载入（章首和首页的自动载入，滚到附近再载）
function run(s){if(s.classList.contains('on'))return;s.classList.add('on');var f=document.createElement('iframe');f.src=s.dataset.src;f.loading='lazy';f.allow='fullscreen';f.title=(s.querySelector('h4')||{}).textContent||'';s.querySelector('.lab-frame').appendChild(f);}
document.querySelectorAll('section.lab').forEach(function(s){s.querySelector('.run').onclick=function(){run(s)};
 s.querySelector('.fs').onclick=function(){run(s);var f=s.querySelector('iframe');(f.requestFullscreen||f.webkitRequestFullscreen||function(){}).call(f)};});
var auto=[].slice.call(document.querySelectorAll('section.lab[data-auto], .hero[data-src]'));
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){io.unobserve(e.target);if(e.target.classList.contains('hero')){var f=e.target.querySelector('iframe');if(!f.src)f.src=e.target.dataset.src;}else run(e.target);}})},{rootMargin:'200px'});auto.forEach(function(s){io.observe(s)});}
else auto.forEach(function(s){if(s.classList.contains('hero'))s.querySelector('iframe').src=s.dataset.src;else run(s)});
// 读到哪一节，左右目录跟着高亮
var hs=[].slice.call(document.querySelectorAll('article h1[id],article h2[id],article h3[id]'));
var links={};[].forEach.call(document.querySelectorAll('nav.side ul a,aside.toc a'),function(a){var h=a.getAttribute('href').split('#')[1];(links[h]=links[h]||[]).push(a)});
var last=null,tt=document.getElementById('totop');
function spy(){var y=window.scrollY+100,id=hs.length?hs[0].id:null;for(var i=0;i<hs.length;i++){if(hs[i].getBoundingClientRect().top+window.scrollY<=y)id=hs[i].id;else break}
 if(tt)tt.classList.toggle('show',window.scrollY>600);
 if(id===last)return;if(last&&links[last])links[last].forEach(function(a){a.classList.remove('on')});last=id;
 if(id&&links[id])links[id].forEach(function(a){a.classList.add('on');var box=a.closest('nav.side,aside.toc');if(!box)return;var r=a.getBoundingClientRect(),rb=box.getBoundingClientRect();if(r.top<rb.top+40||r.bottom>rb.bottom-40)box.scrollTop+=r.top-rb.top-rb.height/2});}
window.addEventListener('scroll',spy,{passive:true});spy();
if(tt)tt.onclick=function(){window.scrollTo({top:0,behavior:'smooth'})};
// 全文搜索
var q=document.getElementById('q'),res=document.getElementById('res'),idx=null,t=null;if(!q)return;
function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function go(){var s=q.value.trim();if(!s){b.classList.remove('searching');return}
 if(!res){location.href='index.html?q='+encodeURIComponent(s);return}
 if(!idx){fetch('search.json').then(function(r){return r.json()}).then(function(d){idx=d;go()});return}
 var ws=s.toLowerCase().split(/\s+/),out=[],n=0;
 idx.forEach(function(e){var x=e.x.toLowerCase(),tl=e.t.toLowerCase();if(!ws.every(function(w){return x.indexOf(w)>=0||tl.indexOf(w)>=0}))return;
  var p=x.indexOf(ws[0]),a=Math.max(0,p-40),snip=(a?'…':'')+e.x.substr(a,140)+'…';
  var hl=esc(snip);ws.forEach(function(w){hl=hl.replace(new RegExp(w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'gi'),function(m){return'<mark>'+m+'</mark>'})});
  if(n++<200)out.push('<a class="r" href="'+e.u+'#'+e.id+'"><b>'+esc(e.t)+'</b><span>'+esc(e.p)+'</span><span>'+hl+'</span></a>')});
 res.innerHTML='<p class="mut">“'+esc(s)+'”：'+n+' 处'+(n>200?'（只列前 200 处）':'')+'。按 Esc 清除。</p>'+out.join('');b.classList.add('searching');window.scrollTo(0,0)}
q.addEventListener('input',function(){clearTimeout(t);t=setTimeout(go,180)});
q.addEventListener('keydown',function(e){if(e.key==='Escape'){q.value='';go()}if(e.key==='Enter')go()});
document.addEventListener('keydown',function(e){if(e.key==='/'&&document.activeElement!==q){e.preventDefault();q.focus()}});
var m=location.search.match(/[?&]q=([^&]+)/);if(m){q.value=decodeURIComponent(m[1]);go()}
})();
