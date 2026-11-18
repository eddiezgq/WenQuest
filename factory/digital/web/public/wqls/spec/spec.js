(function(){
var b=document.body,side=document.querySelector('nav.side');
document.getElementById('menu').onclick=function(){b.classList.toggle('nav')};
side.addEventListener('click',function(e){if(e.target.closest('a'))b.classList.remove('nav')});
var cur=side.querySelector('a.cur');if(cur)cur.scrollIntoView({block:'center'});
// 读到哪一节，左右两个目录跟着高亮
var hs=[].slice.call(document.querySelectorAll('article h1[id],article h2[id],article h3[id]'));
var links={};[].forEach.call(document.querySelectorAll('nav.side ul a,aside.toc a'),function(a){var h=a.getAttribute('href').split('#')[1];(links[h]=links[h]||[]).push(a)});
var last=null;
function spy(){var y=window.scrollY+90,id=hs.length?hs[0].id:null;for(var i=0;i<hs.length;i++){if(hs[i].offsetTop<=y)id=hs[i].id;else break}
 if(id===last)return;if(last&&links[last])links[last].forEach(function(a){a.classList.remove('on')});last=id;
 if(id&&links[id])links[id].forEach(function(a){a.classList.add('on');var box=a.closest('nav.side,aside.toc');var r=a.getBoundingClientRect(),rb=box.getBoundingClientRect();if(r.top<rb.top+40||r.bottom>rb.bottom-40)box.scrollTop+=r.top-rb.top-rb.height/2});
 document.getElementById('totop').classList.toggle('show',window.scrollY>600)}
window.addEventListener('scroll',spy,{passive:true});spy();
document.getElementById('totop').onclick=function(){window.scrollTo({top:0,behavior:'smooth'})};
// 全文搜索
var q=document.getElementById('q'),res=document.getElementById('res'),idx=null,t=null;
function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function run(){var s=q.value.trim();if(!s){b.classList.remove('searching');return}
 if(!idx){fetch('search.json').then(function(r){return r.json()}).then(function(d){idx=d;run()});return}
 var ws=s.toLowerCase().split(/\s+/),out=[],n=0;
 idx.forEach(function(e){var x=e.x.toLowerCase(),tt=e.t.toLowerCase();if(!ws.every(function(w){return x.indexOf(w)>=0||tt.indexOf(w)>=0}))return;
  var p=x.indexOf(ws[0]),a=Math.max(0,p-40),snip=(a?'…':'')+e.x.substr(a,140)+'…';
  var hl=esc(snip);ws.forEach(function(w){hl=hl.replace(new RegExp(w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'gi'),function(m){return'<mark>'+m+'</mark>'})});
  if(n++<200)out.push('<a class="r" href="'+e.u+'#'+e.id+'"><b>'+esc(e.t)+'</b><span>'+esc(e.p)+'</span><span>'+hl+'</span></a>')});
 res.innerHTML='<p class="mut">“'+esc(s)+'”：'+n+' 处'+(n>200?'（只列前 200 处）':'')+'。按 Esc 清除。</p>'+out.join('');b.classList.add('searching');window.scrollTo(0,0)}
q.addEventListener('input',function(){clearTimeout(t);t=setTimeout(run,180)});
q.addEventListener('keydown',function(e){if(e.key==='Escape'){q.value='';run()}});
document.addEventListener('keydown',function(e){if(e.key==='/'&&document.activeElement!==q){e.preventDefault();q.focus()}});
var m=location.search.match(/[?&]q=([^&]+)/);if(m){q.value=decodeURIComponent(m[1]);run()}
})();
