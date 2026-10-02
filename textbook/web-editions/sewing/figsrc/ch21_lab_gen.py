# -*- coding: utf-8 -*-
"""生成虚拟实验 21-1（中英两版）：python3 figsrc/ch21_lab_gen.py
输出 src/zh/labs/proto-fk.html 与 src/en/labs/proto-fk.html。模型与 figsrc/ch21_calc.py 相同。"""
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TPL = r'''<!doctype html>
<html lang="%%lang%%">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
</head>
<body>
<title>%%title%%</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;600;700&family=Noto+Serif+SC:wght@600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: left = bed animation, error strip, needle zoom; right = checks, parameters, tasks. Stacks on narrow screens. */
:root{
  --bg:#eef1f4; --sheet:#f9fafb; --ink:#1d2a36; --muted:#5d6b7a; --rule:#d2d9e0; --soft:#e6eaee;
  --accent:#0f6e74; --ok:#1e8449; --bad:#c0392b; --warn:#b7791f; --acc:#1e8449; --win:#c48a17;
  --cmd:#2a6fdb; --fire:#8a5cc7; --act:#e0662f; --bed:#c9d0d6; --car:#4b5560; --spd:#14797f;
  --f-display:"Noto Serif SC","Songti SC",serif; --f-body:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif; --f-mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#11161c;--sheet:#18202a;--ink:#dde5ee;--muted:#93a2b3;--rule:#2b3643;--soft:#1f2833;--accent:#4cc3c9;--ok:#5fd08a;--bad:#ff6b7d;--warn:#e8b04b;--acc:#5fd08a;--win:#e8b04b;--cmd:#6ea8ff;--fire:#b48cf0;--act:#ff8c55;--bed:#3a4652;--car:#8b97a4;--spd:#4cc3c9;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#11161c;--sheet:#18202a;--ink:#dde5ee;--muted:#93a2b3;--rule:#2b3643;--soft:#1f2833;--accent:#4cc3c9;--ok:#5fd08a;--bad:#ff6b7d;--warn:#e8b04b;--acc:#5fd08a;--win:#e8b04b;--cmd:#6ea8ff;--fire:#b48cf0;--act:#ff8c55;--bed:#3a4652;--car:#8b97a4;--spd:#4cc3c9;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:15px;line-height:1.55;margin:0}
.wrap{max-width:1360px;margin:0 auto;padding-inline:16px;padding-block:18px 40px}
header{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 16px;margin-bottom:12px}
h1{font-family:var(--f-display);font-size:1.5rem;margin:0}
.sub{color:var(--muted);font-size:.9rem}
.grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,370px);gap:14px;align-items:start}
@media (max-width:1000px){.grid{grid-template-columns:minmax(0,1fr)}}
.col{display:flex;flex-direction:column;gap:14px;min-width:0}
.panel{background:var(--sheet);border:1px solid var(--rule);border-radius:10px;padding:12px;min-width:0}
.panel h3{margin:0 0 8px;font-size:.78rem;letter-spacing:.08em;color:var(--muted);font-weight:600}
canvas{display:block;width:100%;height:auto;border-radius:6px}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:10px}
button,select{font:inherit;font-size:.86rem;border:1px solid var(--rule);background:var(--sheet);color:var(--ink);border-radius:6px;padding:4px 10px;cursor:pointer}
button:hover{border-color:var(--accent)} button.primary{background:var(--accent);color:var(--sheet);border-color:var(--accent)}
button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.prm{display:grid;grid-template-columns:minmax(0,1fr) 6.2em;gap:2px 10px;align-items:center;font-size:.84rem}
.prm label{grid-column:1/-1;color:var(--muted);margin-top:6px}
.prm output{font-family:var(--f-mono);font-variant-numeric:tabular-nums;text-align:right}
.prm select{grid-column:1/-1}
input[type=range]{accent-color:var(--accent);width:100%}
input[type=range]:disabled{opacity:.4}
.checks{display:flex;flex-direction:column;gap:6px;font-size:.84rem}
.checks div{display:grid;grid-template-columns:1.3em minmax(0,1fr) auto;gap:6px;align-items:baseline;border-bottom:1px solid var(--rule);padding-bottom:4px}
.checks b{font-family:var(--f-mono);font-variant-numeric:tabular-nums}
.checks small{display:block;color:var(--muted);font-size:.74rem}
.ok{color:var(--ok)} .bad{color:var(--bad)} .warn{color:var(--warn)}
.kpi{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:8px}
@media (max-width:600px){.kpi{grid-template-columns:repeat(2,minmax(0,1fr))}}
.kpi div{border-top:1px solid var(--rule);padding-top:4px}
.kpi b{display:block;font-family:var(--f-mono);font-size:1rem;font-variant-numeric:tabular-nums}
.kpi small{color:var(--muted);font-size:.74rem;line-height:1.3;display:block}
.task{border-top:1px solid var(--rule);padding:8px 0 4px;font-size:.86rem}
.task .st{font-family:var(--f-mono);font-weight:600}
.task .st.ok{color:var(--ok)} .task .st.no{color:var(--muted)}
.task small{display:block;color:var(--muted);font-size:.78rem}
.note{font-size:.78rem;color:var(--muted);margin:6px 0 0}
.legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:.76rem;color:var(--muted);margin-top:6px}
.legend i{display:inline-block;width:12px;height:10px;border-radius:2px;margin-right:4px;vertical-align:-1px}
</style>
<div class="wrap">
<header><h1>%%title%%</h1><span class="sub">%%sub%%</span></header>
<div class="grid">
  <div class="col">
    <section class="panel">
      <h3>%%h_bed%%</h3>
      <canvas id="bed" width="1100" height="270" aria-label="%%h_bed%%"></canvas>
      <div class="row">
        <button id="play" class="primary" type="button">%%b_play%%</button>
        <button id="stat" type="button">%%b_stat%%</button>
        <label class="note" style="margin:0" for="slow">%%l_slow%%</label>
        <select id="slow"><option value="5">1/5</option><option value="20" selected>1/20</option><option value="80">1/80</option></select>
      </div>
    </section>
    <section class="panel">
      <h3>%%h_err%%</h3>
      <canvas id="err" width="1100" height="300" aria-label="%%h_err%%"></canvas>
      <div class="legend"><span><i style="background:color-mix(in srgb,var(--acc) 30%,transparent)"></i>%%lg_acc%%</span><span><i style="background:color-mix(in srgb,var(--win) 25%,transparent)"></i>%%lg_win%%</span><span><i style="background:var(--muted)"></i>%%lg_bar%%</span><span><i style="background:var(--act)"></i>%%lg_dot%%</span></div>
    </section>
    <section class="panel">
      <h3>%%h_zoom%%</h3>
      <canvas id="zoom" width="1100" height="190" aria-label="%%h_zoom%%"></canvas>
    </section>
    <p class="note">%%model%%</p>
  </div>
  <div class="col">
    <section class="panel"><h3>%%h_chk%%</h3><div class="checks" id="checks"></div>
      <div class="kpi" id="kpi"></div></section>
    <section class="panel">
      <h3>%%h_prm%%</h3>
      <div class="prm">
        <label for="E">%%p_E%%</label><select id="E"><option value="5">E5（p = 5.08 mm）</option><option value="6">E6（p = 4.23 mm）</option><option value="7">E7（p = 3.63 mm）</option></select>
        <label for="vmax">%%p_v%%</label><input id="vmax" type="range" min="0.1" max="3" step="0.01"><output id="vmaxv"></output>
        <label for="a">%%p_a%%</label><input id="a" type="range" min="2" max="20" step="1"><output id="av"></output>
        <label for="c">%%p_c%%</label><input id="c" type="range" min="10" max="120" step="1"><output id="cv"></output>
        <label for="Tr">%%p_Tr%%</label><input id="Tr" type="range" min="0.2" max="3" step="0.05"><output id="Trv"></output>
        <label for="J">%%p_J%%</label><input id="J" type="range" min="0" max="0.6" step="0.01"><output id="Jv"></output>
        <label for="ctrl">%%p_ctrl%%</label><select id="ctrl"><option value="mcu">%%o_mcu%%</option><option value="fpga">%%o_fpga%%</option></select>
        <label for="Tctrl">%%p_Tc%%</label><input id="Tctrl" type="range" min="0.1" max="2" step="0.05"><output id="Tctrlv"></output>
        <label for="seg">%%p_seg%%</label><select id="seg"><option value="1">1</option><option value="2">2</option><option value="4">4</option><option value="8">8</option></select>
        <label for="mode">%%p_mode%%</label><select id="mode"><option value="rt">%%o_rt%%</option><option value="fixed">%%o_fixed%%</option><option value="none">%%o_none%%</option></select>
        <label for="Lf">%%p_Lf%%</label><input id="Lf" type="range" min="0" max="4" step="0.01"><output id="Lfv"></output>
      </div>
      <div class="row"><button id="reset" type="button">%%b_reset%%</button><button id="tofpga" type="button">%%b_fpga%%</button><button id="cal" type="button">%%b_cal%%</button></div>
      <p class="note">%%prm_note%%</p>
    </section>
    <section class="panel"><h3>%%h_task%%</h3><div id="tasks"></div></section>
  </div>
</div>
</div>
<script>
(()=>{
const L=%%L%%;
const $=id=>document.getElementById(id);
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
// ---------------- model (same as figsrc/ch21_calc.py) ----------------
const STD={E:5,N:60,vmax:0.6,a:10,c:40,Lk:80,Tr:1.5,J:0.3,Tctrl:1.0,fpga:false,res:0.01,seg:8,mode:'rt',Lf:1.2,trev:0.10};
const P={...STD};
const pitch=Q=>25.4/Q.E;
const stroke=Q=>2*Q.c+Q.N*pitch(Q)+Q.Lk;
function kin(Q){const D=stroke(Q)/1000,a=Q.a,v=Q.vmax;
  if(D<=v*v/a){const vp=Math.sqrt(a*D),ta=vp/a;return {D,vp,ta,tc:0,T:2*ta};}
  const ta=v/a,tc=(D-v*v/a)/v;return {D,vp:v,ta,tc,T:2*ta+tc};}
function xOfT(Q,K,t){const a=Q.a,{D,vp,ta,tc,T}=K;
  if(t<=0)return 0; if(t<=ta)return .5*a*t*t*1000; if(t<=ta+tc)return (.5*a*ta*ta+vp*(t-ta))*1000;
  if(t<=T){const td=t-ta-tc;return (.5*a*ta*ta+vp*tc+vp*td-.5*a*td*td)*1000;} return D*1000;}
function vOfT(Q,K,t){const a=Q.a,{vp,ta,tc,T}=K;
  if(t<=0)return 0; if(t<=ta)return a*t; if(t<=ta+tc)return vp; if(t<=T)return Math.max(0,vp-a*(t-ta-tc)); return 0;}
function tOfX(Q,K,x){const a=Q.a,{D,vp,ta,tc,T}=K;x/=1000;const xa=.5*a*ta*ta;
  if(x<=0)return 0; if(x<=xa)return Math.sqrt(2*x/a); if(x<=xa+vp*tc)return ta+(x-xa)/vp; if(x>=D)return T;
  const r=x-xa-vp*tc;const disc=Math.max(0,vp*vp-2*a*r);return ta+tc+(vp-Math.sqrt(disc))/a;}
const needleX=(Q,i)=>Q.c+(i+.5)*pitch(Q);
const qtime=(Q,u)=>Q.fpga?(Q.res/1000)/Math.max(u,1e-4):Q.Tctrl/1000;
function leadMm(Q,u){const q=qtime(Q,u);if(Q.mode==='rt')return u*(Q.Tr/1000+q/2)*1000;if(Q.mode==='fixed')return Q.Lf;return 0;}
function needleErr(Q,K,i,qf,jf){const xi=needleX(Q,i);let xc=xi,tc,u;
  for(let k=0;k<4;k++){tc=tOfX(Q,K,Math.max(0,xc));u=vOfT(Q,K,tc);xc=xi-leadMm(Q,u);}
  tc=tOfX(Q,K,Math.max(0,xc));u=vOfT(Q,K,tc);const q=qtime(Q,Math.max(u,1e-3));
  const tf=tc+qf*q, tact=tf+Q.Tr/1000+jf*Q.J/1000;
  return {e:xOfT(Q,K,tact)-xi,u,xc,tf,q};}
function bounds(Q,K,i){let lo=1e9,hi=-1e9;for(const qf of [0,1])for(const jf of [-1,1]){const e=needleErr(Q,K,i,qf,jf).e;lo=Math.min(lo,e);hi=Math.max(hi,e);}return [lo,hi];}
function segOk(Q,K,i){const u=vOfT(Q,K,tOfX(Q,K,needleX(Q,i)));return Q.seg*pitch(Q)/1000/Math.max(u,1e-6)>=2*Q.Tr/1000;}
function evaluate(Q){const K=kin(Q),p=pitch(Q);let worst=0,badAcc=0,segBad=0;const nb=[];
  for(let i=0;i<Q.N;i++){const [lo,hi]=bounds(Q,K,i);const w=Math.max(Math.abs(lo),Math.abs(hi));worst=Math.max(worst,w);
    const so=segOk(Q,K,i);if(!so)segBad++;if(w>0.1*p||!so)badAcc++;nb.push({lo,hi,so,u:vOfT(Q,K,tOfX(Q,K,needleX(Q,i)))});}
  const trow=K.T+Q.trev;return {K,p,worst,worstP:worst/p,badAcc,segBad,nb,trow,rph:3600/trow};}
function sampleRow(Q,R){const p=R.p;return R.nb.map((b,i)=>{const s=needleErr(Q,R.K,i,Math.random(),Math.random()*2-1);return {...s,mis:Math.abs(s.e)>0.25*p||!b.so};});}
function stat1000(Q,R){let bad=0;for(let r=0;r<1000;r++){for(const s of sampleRow(Q,R))if(s.mis)bad++;}return bad;}
function vmaxFor(Q){let lo=0.05,hi=4;for(let k=0;k<40;k++){const m=(lo+hi)/2;if(evaluate({...Q,vmax:m}).badAcc===0)lo=m;else hi=m;}return lo;}
// ---------------- UI ----------------
const fmt={vmax:v=>v.toFixed(2)+' m/s',a:v=>v.toFixed(0)+' m/s²',c:v=>v.toFixed(0)+' mm',Tr:v=>v.toFixed(2)+' ms',J:v=>'±'+v.toFixed(2)+' ms',Tctrl:v=>v.toFixed(2)+' ms',Lf:v=>v.toFixed(2)+' mm'};
let R=null,row=null,stat=null,anim=null;
function syncUI(){for(const k in fmt){$(k).value=P[k];$(k+'v').textContent=fmt[k](P[k]);}
  $('E').value=P.E;$('seg').value=P.seg;$('mode').value=P.mode;$('ctrl').value=P.fpga?'fpga':'mcu';
  $('Tctrl').disabled=P.fpga;$('Lf').disabled=P.mode!=='fixed';}
function changed(){syncUI();R=evaluate(P);row=null;stat=null;anim=null;render();}
for(const k in fmt)$(k).addEventListener('input',()=>{P[k]=+$(k).value;changed();});
$('E').addEventListener('change',()=>{P.E=+$('E').value;changed();});
$('seg').addEventListener('change',()=>{P.seg=+$('seg').value;changed();});
$('mode').addEventListener('change',()=>{P.mode=$('mode').value;changed();});
$('ctrl').addEventListener('change',()=>{P.fpga=$('ctrl').value==='fpga';changed();});
$('reset').onclick=()=>{Object.assign(P,STD);changed();};
$('tofpga').onclick=()=>{P.fpga=true;changed();};
$('cal').onclick=()=>{const u=P.vmax;P.Lf=+(u*(P.Tr+(P.fpga?P.res/u:P.Tctrl)/2)).toFixed(2);changed();};
$('stat').onclick=()=>{stat=stat1000(P,R);render();};
$('play').onclick=()=>{row=sampleRow(P,R);anim={t:0,last:0,cur:-1};requestAnimationFrame(tick);};
function tick(ts){if(!anim)return;if(!anim.last)anim.last=ts;const dt=Math.min(.05,(ts-anim.last)/1000)/+$('slow').value;anim.last=ts;anim.t+=dt;
  const x=xOfT(P,R.K,anim.t);for(let i=0;i<P.N;i++)if(needleX(P,i)<=x)anim.cur=i;
  render();if(anim.t<R.K.T)requestAnimationFrame(tick);else{anim.done=true;render();}}
// ---------------- drawing ----------------
function drawBed(){const c=$('bed'),g=c.getContext('2d'),W=c.width,H=c.height;g.clearRect(0,0,W,H);
  const D=stroke(P),x0=40,x1=W-20,X=mm=>x0+(x1-x0)*mm/D,p=pitch(P);
  // speed profile
  const yb=110,yt=22,vmx=Math.max(0.2,R.K.vp*1.15);const Y=v=>yb-(yb-yt)*v/vmx;
  g.strokeStyle=css('--rule');g.lineWidth=1;g.beginPath();g.moveTo(x0,yb);g.lineTo(x1,yb);g.stroke();
  g.strokeStyle=css('--spd');g.lineWidth=2;g.beginPath();
  for(let k=0;k<=200;k++){const t=R.K.T*k/200;const xx=X(xOfT(P,R.K,t)),vv=vOfT(P,R.K,t);k?g.lineTo(xx,Y(vv)):g.moveTo(xx,Y(vv));}g.stroke();
  g.fillStyle=css('--muted');g.font='14px '+css('--f-body');g.fillText(L.speed+'  '+L.peak+' '+R.K.vp.toFixed(2)+' m/s',x0+4,yt-6);
  // reversal zones
  g.fillStyle=css('--soft');g.fillRect(X(0),150,X(P.c)-X(0),70);g.fillRect(X(P.c+P.N*p),150,X(D)-X(P.c+P.N*p),70);
  g.fillStyle=css('--muted');g.font='13px '+css('--f-body');g.fillText('c',X(P.c/2)-3,240);g.fillText(L.lk+' + c',X(P.c+P.N*p)+4,240);
  // bed + needles
  g.fillStyle=css('--bed');g.fillRect(X(P.c),160,X(P.c+P.N*p)-X(P.c),50);
  for(let i=0;i<P.N;i++){const xi=X(needleX(P,i));let col=css('--car');let up=0;
    if(row&&anim&&i<=anim.cur){const s=row[i];col=s.mis?css('--bad'):(Math.abs(s.e)>0.1*R.p?css('--warn'):css('--ok'));up=10;}
    else if(!R.nb[i].so||Math.max(Math.abs(R.nb[i].lo),Math.abs(R.nb[i].hi))>0.1*R.p){col=css('--bad');}
    g.strokeStyle=col;g.lineWidth=2;g.beginPath();g.moveTo(xi,205);g.lineTo(xi,168-up);g.stroke();
    if(R.nb[i].u&&i%8===0){g.fillStyle=css('--spd');g.beginPath();g.arc(xi,Y(R.nb[i].u),2.5,0,7);g.fill();}}
  // carriage
  const xs=anim?xOfT(P,R.K,anim.t):P.c-10;const cx=X(xs);
  g.fillStyle=css('--car');g.globalAlpha=.25;g.fillRect(X(xs-P.Lk),140,X(xs)-X(xs-P.Lk),90);g.globalAlpha=1;
  g.strokeStyle=css('--car');g.lineWidth=1.5;g.strokeRect(X(xs-P.Lk),140,X(xs)-X(xs-P.Lk),90);
  g.strokeStyle=css('--bad');g.lineWidth=2;g.beginPath();g.moveTo(cx,132);g.lineTo(cx,236);g.stroke();
  g.fillStyle=css('--ink');g.font='13px '+css('--f-body');g.textAlign=cx>W-160?'right':'left';
  const vnow=anim?vOfT(P,R.K,anim.t):0;g.fillText(L.selpt+'  '+vnow.toFixed(2)+' m/s',cx+(cx>W-160?-6:6),132);g.textAlign='left';
  g.fillStyle=css('--muted');g.fillText(`${L.stroke} ${D.toFixed(1)} mm · ${L.cam} ${P.Lk} mm · ${L.dir} →`,x0,H-8);}
function drawErr(){const c=$('err'),g=c.getContext('2d'),W=c.width,H=c.height;g.clearRect(0,0,W,H);
  const x0=60,x1=W-16,y0=14,y1=H-34,ym=0.4,p=R.p;const X=i=>x0+(x1-x0)*(i+.5)/P.N,Y=e=>(y0+y1)/2-(y1-y0)/2*e/ym;
  g.fillStyle=css('--win');g.globalAlpha=.16;g.fillRect(x0,Y(.25),x1-x0,Y(-.25)-Y(.25));g.globalAlpha=1;
  g.fillStyle=css('--acc');g.globalAlpha=.22;g.fillRect(x0,Y(.1),x1-x0,Y(-.1)-Y(.1));g.globalAlpha=1;
  g.strokeStyle=css('--rule');g.fillStyle=css('--muted');g.font='13px '+css('--f-body');g.lineWidth=1;
  for(const e of [-.4,-.25,-.1,0,.1,.25,.4]){g.beginPath();g.moveTo(x0,Y(e));g.lineTo(x1,Y(e));g.stroke();g.textAlign='right';g.fillText((e>0?'+':'')+e.toFixed(2)+'p',x0-6,Y(e)+4);}
  g.textAlign='center';for(let i=0;i<P.N;i+=5)g.fillText(i,X(i),H-14);g.textAlign='left';g.fillText(L.needle,x1-60,H-2);
  R.nb.forEach((b,i)=>{const lo=Math.max(-ym,b.lo/p),hi=Math.min(ym,b.hi/p);const bad=!b.so||Math.max(Math.abs(b.lo),Math.abs(b.hi))>.1*p;
    g.fillStyle=bad?css('--bad'):css('--muted');g.globalAlpha=.55;g.fillRect(X(i)-3,Y(hi),6,Math.max(2,Y(lo)-Y(hi)));g.globalAlpha=1;
    if(!b.so){g.fillStyle=css('--bad');g.fillText('×',X(i)-4,y0+10);}});
  if(row){row.forEach((s,i)=>{if(anim&&i>anim.cur)return;g.fillStyle=s.mis?css('--bad'):css('--act');g.beginPath();g.arc(X(i),Y(Math.max(-ym,Math.min(ym,s.e/p))),4,0,7);g.fill();});}}
function drawZoom(){const c=$('zoom'),g=c.getContext('2d'),W=c.width,H=c.height;g.clearRect(0,0,W,H);
  const i=anim&&anim.cur>=0?anim.cur:Math.round(P.N/2);const p=R.p;const b=R.nb[i];
  const mid=needleErr(P,R.K,i,.5,0);const lead=needleX(P,i)-mid.xc;
  const lo=Math.min(-lead,b.lo,-.25*p)-.15*p,hi=Math.max(b.hi,.25*p)+.15*p;const x0=170,x1=W-20;const X=d=>x0+(x1-x0)*(d-lo)/(hi-lo);
  g.fillStyle=css('--win');g.globalAlpha=.16;g.fillRect(X(-.25*p),8,X(.25*p)-X(-.25*p),H-40);g.globalAlpha=1;
  g.fillStyle=css('--acc');g.globalAlpha=.22;g.fillRect(X(-.1*p),8,X(.1*p)-X(-.1*p),H-40);g.globalAlpha=1;
  g.strokeStyle=css('--ink');g.lineWidth=1.5;g.beginPath();g.moveTo(X(0),6);g.lineTo(X(0),H-30);g.stroke();
  g.font='13px '+css('--f-body');g.fillStyle=css('--ink');g.fillText(`${L.needle} ${i}: x_i`,X(0)+5,20);
  const yc=46,yf=86,ya=126;
  g.fillStyle=css('--muted');g.fillText(L.cmd,10,yc+5);g.fillText(L.fire,10,yf+5);g.fillText(L.act,10,ya+5);
  g.strokeStyle=css('--rule');g.lineWidth=1;for(const y of [yc,yf,ya]){g.beginPath();g.moveTo(x0,y);g.lineTo(x1,y);g.stroke();}
  g.fillStyle=css('--cmd');g.fillRect(X(-lead)-2,yc-10,4,20);g.fillText(`−${lead.toFixed(2)} mm = ${(lead/p).toFixed(2)} p`,X(-lead)+8,yc-4);
  const qmm=mid.u*mid.q*1000;g.fillStyle=css('--fire');g.globalAlpha=.5;g.fillRect(X(-lead),yf-8,Math.max(3,X(-lead+qmm)-X(-lead)),16);g.globalAlpha=1;
  g.fillText(`0 ~ ${qmm.toFixed(3)} mm`,Math.max(X(-lead+qmm),X(-lead)+3)+8,yf-4);
  g.fillStyle=css('--act');g.globalAlpha=.55;g.fillRect(X(b.lo),ya-8,Math.max(3,X(b.hi)-X(b.lo)),16);g.globalAlpha=1;
  g.fillStyle=css('--act');const tx=`${b.lo.toFixed(3)} ~ ${b.hi.toFixed(3)} mm`;const tw=g.measureText(tx).width;g.fillText(tx,Math.min(X(b.hi)+8,W-tw-6),ya-12);
  if(row&&anim&&anim.cur>=i){const s=row[i];g.fillStyle=s.mis?css('--bad'):css('--ink');g.beginPath();g.arc(X(s.e),ya,5,0,7);g.fill();}
  g.fillStyle=css('--muted');g.fillText(`±0.1p = ±${(.1*p).toFixed(3)} mm   ±0.25p = ±${(.25*p).toFixed(3)} mm   ${L.speedat} ${b.u.toFixed(2)} m/s`,x0,H-8);}
function render(){if(!R)return;
  const p=R.p,vp=R.K.vp;
  const C=[
   {ok:R.worst<=0.1*p,n:L.c_acc,v:`${R.worst.toFixed(3)} mm = ${R.worstP.toFixed(3)} p`,lim:L.c_acc_l},
   {ok:R.badAcc===0,n:L.c_bad,v:`${R.badAcc} / ${P.N}`,lim:L.c_bad_l},
   {ok:R.segBad===0,n:L.c_seg,v:`${(P.seg*p/vp).toFixed(1)} ms`,lim:`${L.c_seg_l} ${(2*P.Tr).toFixed(1)} ms`},
   {ok:!row||row.every(s=>!s.mis),warn:!row,n:L.c_row,v:row?`${row.filter(s=>s.mis).length}`:'—',lim:L.c_row_l}];
  $('checks').innerHTML=C.map(c=>`<div><span class="${c.warn?'warn':c.ok?'ok':'bad'}">${c.warn?'○':c.ok?'✓':'✗'}</span><span>${c.n}<small>${c.lim}</small></span><b class="${c.warn?'':c.ok?'ok':'bad'}">${c.v}</b></div>`).join('');
  const K=[[ p.toFixed(2)+' mm',L.k_p],[(p/vp).toFixed(2)+' ms',L.k_tn],[leadMm(P,vp).toFixed(2)+' mm',L.k_lead],[vp.toFixed(2)+' m/s',L.k_vp],
    [R.trow.toFixed(3)+' s',L.k_row],[Math.round(R.rph)+'',L.k_rph],[stat===null?'—':(stat+' ('+(stat/600).toFixed(2)+'%)'),L.k_stat],[(20*R.trow).toFixed(1)+' s',L.k_20]];
  $('kpi').innerHTML=K.map(k=>`<div><b>${k[0]}</b><small>${k[1]}</small></div>`).join('');
  drawBed();drawErr();drawZoom();checkTasks();}
// ---------------- tasks ----------------
const base=()=>P.E===5&&P.Tr===1.5&&P.J===0.3&&P.mode==='rt'&&P.seg===8;
const TASKS=[
 {t:L.t1,d:L.t1d,ok:()=>base()&&!P.fpga&&P.Tctrl===1&&R.badAcc===0&&P.vmax>=0.62},
 {t:L.t2,d:L.t2d,ok:()=>base()&&P.fpga&&R.badAcc===0&&P.vmax>=1.62},
 {t:L.t3,d:L.t3d,ok:()=>P.E===7&&P.fpga&&P.mode==='fixed'&&P.Tr===1.5&&P.J===0.3&&P.seg===8&&P.vmax>=0.99&&P.c<=50&&R.badAcc===0}];
const done=new Set();
function checkTasks(){TASKS.forEach((k,i)=>{if(k.ok())done.add(i);});
  $('tasks').innerHTML=TASKS.map((k,i)=>`<div class="task"><span class="st ${done.has(i)?'ok':'no'}">${done.has(i)?L.done:L.notdone}</span> ${k.t}<small>${k.d}</small></div>`).join('');}
window.__api={P,STD,evaluate,changed,done,vmaxFor,stat1000:()=>stat1000(P,R),get R(){return R;},set:(o)=>{Object.assign(P,o);changed();},tasks:()=>TASKS.map(k=>k.ok())};
changed();
})();
</script><a href="../index.html" style="position:fixed;right:12px;bottom:12px;z-index:99;font:13px system-ui,sans-serif;background:rgba(20,30,40,.78);color:#fff;padding:6px 10px;border-radius:6px;text-decoration:none">%%back%%</a>
</body>
</html>
'''

ZH = dict(lang='zh-CN', title='缩比横机原型：机头速度与选针时序',
  sub='《缝纫机设计与制造》第 21 章 · 虚拟实验 21-1 · 原型该选多快的机头、多快的选针器、多短的控制周期？用时序预算回答',
  h_bed='针床与机头（单系统 60 针，机头 → 方向；上方为机头速度曲线，青点为每 8 针的选针速度）',
  b_play='织一行（动画）', b_stat='统计 1000 行', l_slow='慢放',
  h_err='每枚针的选针误差（单位：针距 p；正 = 衔铁动作晚于针到位）',
  lg_acc='验收 ±0.1p', lg_win='允许窗口 ±0.25p（超出即错选）', lg_bar='误差范围（量化 × 抖动最坏组合）', lg_dot='本行实际（随机抽样）',
  h_zoom='放大：当前这枚针的命令点、触发点与衔铁动作位置（横轴为机头位置，单位 mm）',
  model='模型：机头按梯形（行程短时三角形）速度曲线走完一趟 D = 2c + 60p + L<sub>k</sub>（L<sub>k</sub> = 80 mm 三角座跨度），每端换向停顿 0.1 s（度目、纱嘴）。第 i 枚针在 x<sub>i</sub> = c + (i + ½)p 处应当被选中。控制器在机头到达 x<sub>i</sub> − 提前量时“该发命令”，但只有在下一个控制周期（MCU）或下一个编码器计数（FPGA，0.01 mm）才真正发出；再经选针器响应 T<sub>r</sub> ± J 衔铁动作。误差 = 衔铁动作时的机头位置 − x<sub>i</sub>。实时提前量 = v(T<sub>r</sub> + 量化/2)。|误差| ≤ 0.1p 为验收合格，> 0.25p 为错选。同段两次动作间隔 n<sub>段</sub>·p/v 须 ≥ 2T<sub>r</sub>（吸合 + 释放），否则按最坏花型记为错选。参数为示意值，与正文第 21.6 节算例及 figsrc/ch21_calc.py 相同。',
  h_chk='判据', h_prm='调整',
  p_E='针距（机号）', p_v='机头最高速度 v', p_a='机头加速度 a', p_c='换向余量 c（选针点在第 0 针前多远起步）',
  p_Tr='选针器响应时间 T<sub>r</sub>（命令到衔铁动作）', p_J='响应时间离散（抖动）±J', p_ctrl='逐针触发由谁做',
  o_mcu='MCU：每个控制周期查一次位置', o_fpga='FPGA：每个编码器计数比较一次',
  p_Tc='MCU 控制周期 T<sub>c</sub>', p_seg='选针器段数（相邻针分给不同段）', p_mode='提前量',
  o_rt='按实时速度计算', o_fixed='固定提前量（下方设定）', o_none='不补偿', p_Lf='固定提前量 L<sub>f</sub>',
  b_reset='恢复标准', b_fpga='改用 FPGA', b_cal='按当前最高速度整定 L<sub>f</sub>',
  prm_note='标准参数：E5、0.6 m/s、10 m/s²、c = 40 mm、T<sub>r</sub> = 1.5 ± 0.3 ms、MCU 1 ms、8 段、实时提前量。',
  h_task='任务（自动判定）',
  t1='任务 1：标准参数（MCU 1 ms，T<sub>r</sub> = 1.5 ± 0.3 ms，E5，实时提前量，8 段）下，找出整行 60 针都满足验收（≤ 0.1p）的最高机头速度，把速度滑块停在这个值上（精确到 0.01 m/s）。',
  t1d='最坏误差 ≈ v(T<sub>c</sub>/2 + J)。先估算再微调；超过一点点，判据第 1 条就变红。',
  t2='任务 2：其余不变，改用 FPGA 逐计数触发，再找最高机头速度（精确到 0.01 m/s）。对比任务 1，每小时行数提高了多少？',
  t2d='量化误差从 v·T<sub>c</sub>/2 降到半个编码器计数，剩下的主要是选针器自身的抖动。速度提高了约 2.6 倍，行数却没有——看看加减速和换向停顿占了多少。',
  t3='任务 3：换 E7 针床（p = 3.63 mm），用 FPGA、固定提前量，机头速度 1.00 m/s。调固定提前量 L<sub>f</sub> 和换向余量 c（c ≤ 50 mm），让 60 针全部满足验收。',
  t3d='提前量按时间算（≈ v·T<sub>r</sub>），与针距无关；但 0.1p 的带宽变窄了，固定提前量只在接近全速的针上对，所以要让第一枚针前留够加速距离。',
  done='✓ 完成', notdone='○ 未完成', back='返回教材',
  L=dict(speed='机头速度', peak='峰值', lk='三角跨度', selpt='选针点', stroke='一趟行程', cam='三角座跨度', dir='方向', needle='针号',
    cmd='命令点', fire='触发（量化）', act='衔铁动作', speedat='该针处机头速度',
    c_acc='一行中最坏选针误差', c_acc_l='验收：≤ 0.1 个针距', c_bad='超出验收的针数', c_bad_l='应为 0（含选针器来不及复位的针）',
    c_seg='同段两次动作间隔', c_seg_l='须 ≥ 吸合 + 释放 =', c_row='本行错选针数（动画抽样）', c_row_l='|误差| > 0.25p 即错选；点“织一行”抽样',
    k_p='针距 p', k_tn='每针时间 p/v', k_lead='全速时提前量', k_vp='实际峰值速度', k_row='一行用时（含换向 0.1 s）', k_rph='每小时行数',
    k_stat='1000 行错选针数', k_20='织 20 行样片用时', done='✓ 完成', notdone='○ 未完成'))

EN = dict(lang='en', title='Scaled flat-knitting prototype: carriage speed and selection timing',
  sub='Sewing Machine Design and Manufacturing, Chapter 21 · Virtual lab 21-1 · How fast a carriage, how fast a selector and how short a control period should the prototype have? Answer with a timing budget',
  h_bed='Needle bed and carriage (single system, 60 needles, carriage moving →; top: carriage speed profile, teal dots = speed at every 8th needle)',
  b_play='Knit one course (animation)', b_stat='Run 1000 courses', l_slow='Slow motion',
  h_err='Selection error of each needle (in pitches p; positive = armature acts after the needle position)',
  lg_acc='acceptance ±0.1p', lg_win='window ±0.25p (beyond = mis-selection)', lg_bar='error range (worst combination of quantisation and jitter)', lg_dot='this course (random sample)',
  h_zoom='Zoom: command point, firing point and armature action for the current needle (horizontal axis = carriage position, mm)',
  model='Model: the carriage runs a trapezoidal (triangular on short strokes) speed profile over D = 2c + 60p + L<sub>k</sub> (L<sub>k</sub> = 80 mm cam span), with a 0.1 s dwell at each reversal (stitch cams, carriers). Needle i must be selected at x<sub>i</sub> = c + (i + ½)p. The controller "should" issue the command when the carriage reaches x<sub>i</sub> − lead, but actually issues it at the next control tick (MCU) or the next encoder count (FPGA, 0.01 mm); the armature then acts after the selector response T<sub>r</sub> ± J. Error = carriage position when the armature acts − x<sub>i</sub>. Real-time lead = v(T<sub>r</sub> + quantisation/2). |error| ≤ 0.1p passes acceptance; > 0.25p is a mis-selection. Successive actions of one selector step, n<sub>steps</sub>·p/v apart, need ≥ 2T<sub>r</sub> (pull + release), otherwise they count as mis-selections for the worst-case pattern. Illustrative values, identical to the worked example in Section 21.6 and figsrc/ch21_calc.py.',
  h_chk='Criteria', h_prm='Parameters',
  p_E='Gauge (pitch)', p_v='Carriage top speed v', p_a='Carriage acceleration a', p_c='Reversal margin c (run-up before needle 0)',
  p_Tr='Selector response T<sub>r</sub> (command to armature action)', p_J='Response scatter (jitter) ±J', p_ctrl='Who fires each needle',
  o_mcu='MCU: polls position each period', o_fpga='FPGA: compares at every count',
  p_Tc='MCU control period T<sub>c</sub>', p_seg='Selector steps (neighbouring needles go to different steps)', p_mode='Lead',
  o_rt='From live speed', o_fixed='Fixed lead (set below)', o_none='No compensation', p_Lf='Fixed lead L<sub>f</sub>',
  b_reset='Reset to standard', b_fpga='Switch to FPGA', b_cal='Set L<sub>f</sub> for current top speed',
  prm_note='Standard: E5, 0.6 m/s, 10 m/s², c = 40 mm, T<sub>r</sub> = 1.5 ± 0.3 ms, MCU 1 ms, 8 steps, real-time lead.',
  h_task='Tasks (auto-checked)',
  t1='Task 1: with the standard set-up (MCU 1 ms, T<sub>r</sub> = 1.5 ± 0.3 ms, E5, real-time lead, 8 steps), find the highest carriage speed at which all 60 needles pass acceptance (≤ 0.1p) and leave the speed slider there (to 0.01 m/s).',
  t1d='Worst error ≈ v(T<sub>c</sub>/2 + J). Estimate first, then fine-tune; go a hair too far and criterion 1 turns red.',
  t2='Task 2: keep everything else, switch to FPGA per-count firing and find the highest speed again (to 0.01 m/s). Compared with Task 1, how many more courses per hour do you get?',
  t2d='Quantisation error falls from v·T<sub>c</sub>/2 to half an encoder count; what is left is mostly the selector\'s own jitter. Speed rises about 2.6×, courses per hour do not — see how much acceleration and reversal dwell cost.',
  t3='Task 3: change to an E7 bed (p = 3.63 mm), FPGA, fixed lead, top speed 1.00 m/s. Adjust the fixed lead L<sub>f</sub> and the reversal margin c (c ≤ 50 mm) so that all 60 needles pass acceptance.',
  t3d='The lead is a time (≈ v·T<sub>r</sub>) and does not depend on pitch; but the 0.1p band is narrower, and a fixed lead is right only for needles passed near full speed — so leave enough run-up before the first needle.',
  done='✓ Done', notdone='○ Not done', back='Back to the book',
  L=dict(speed='carriage speed', peak='peak', lk='cam span', selpt='selection point', stroke='stroke', cam='cam span', dir='direction', needle='needle',
    cmd='command', fire='firing (quantised)', act='armature acts', speedat='carriage speed here',
    c_acc='Worst selection error in the course', c_acc_l='acceptance: ≤ 0.1 pitch', c_bad='Needles failing acceptance', c_bad_l='must be 0 (includes steps that cannot recover in time)',
    c_seg='Interval between actions of one step', c_seg_l='must be ≥ pull + release =', c_row='Mis-selections this course (animated sample)', c_row_l='|error| > 0.25p is a mis-selection; press "Knit one course"',
    k_p='pitch p', k_tn='time per needle p/v', k_lead='lead at top speed', k_vp='actual peak speed', k_row='course time (incl. 0.1 s reversal)', k_rph='courses per hour',
    k_stat='mis-selections in 1000 courses', k_20='time for a 20-course swatch', done='✓ Done', notdone='○ Not done'))

def build(d, out):
    s = TPL
    for k, v in d.items():
        if k == 'L': continue
        s = s.replace('%%' + k + '%%', v)
    LL = dict(d['L']); LL.update({k: d[k] for k in ('t1', 't1d', 't2', 't2d', 't3', 't3d')})
    s = s.replace('%%L%%', json.dumps(LL, ensure_ascii=False))
    assert '%%' not in s, s[s.index('%%'):s.index('%%') + 30]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write(s); print('ok', out)

if __name__ == '__main__':
    build(ZH, os.path.join(ROOT, 'src', 'zh', 'labs', 'proto-fk.html'))
    build(EN, os.path.join(ROOT, 'src', 'en', 'labs', 'proto-fk.html'))
