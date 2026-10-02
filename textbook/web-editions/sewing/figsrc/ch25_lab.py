# -*- coding: utf-8 -*-
"""生成虚拟实验 25-1（凸轮廓线误差与磨削补偿）的中英两版：src/zh/labs/cam.html、src/en/labs/cam.html。
页面模型与 ch25_model.py 相同（同一组参数、同样的谱方法求导、同样的补偿率）。"""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)

S = {
 'title': ('凸轮廓线误差与磨削补偿', 'Cam profile error and grinding compensation'),
 'sub': ('《缝纫机设计与制造》第 25 章 · 虚拟实验 25-1 · 几微米的廓线误差，在高速下会变成多大的加速度误差？补偿磨削能修掉哪些？',
         'Sewing Machine Design and Manufacturing, Chapter 25 · Virtual lab 25-1 · How much acceleration error do a few microns of profile error cause at speed, and what can compensation grinding remove?'),
 'p_cam': ('凸轮与误差放大图：灰线为名义廓线，红线为实际廓线（误差放大显示）；橙色为砂轮', 'Cam and magnified error: grey = nominal profile, red = actual profile (error magnified); orange = wheel'),
 'p_err': ('升程误差（μm，已去掉平均值）：虚线为磨后、实线为当前（补偿后）', 'Lift error (μm, mean removed): dashed = as ground, solid = current (after compensation)'),
 'p_spec': ('误差谐波幅值（μm）：浅色为磨后，深色为当前', 'Error harmonics (μm): light = as ground, dark = current'),
 'p_spd': ('加速度误差峰值随转速的变化（m/s²）', 'Peak acceleration error versus speed (m/s²)'),
 'p_sig': ('当前转速下的接触应力（MPa，示意）：灰线为名义廓线，橙线计入误差', 'Contact stress at the current speed (MPa, illustrative): grey = nominal, orange = with error'),
 'note': ('模型（与正文 25.8 节相同，示意值）：对心直动滚子从动件；升程误差 = 一阶偏心 1 μm + 热处理变形（2、3 阶）× 0.25^精磨次数 + 机床误差谐波 + 砂轮半径没更新时的 d/cos α；评定取 1–50 阶；补偿磨削一轮把第 k 阶误差修掉 85%·exp(−(k/20)²)；加速度误差 = 升程误差对转角的二阶导数 × ω²；接触应力按赫兹线接触，载荷 = 工作载荷 + 折算质量 × |加速度|。',
          'Model (same as Section 25.8, illustrative): central translating roller follower; lift error = 1 μm first-order eccentricity + heat-treatment distortion (orders 2, 3) × 0.25^passes + one machine-error harmonic + d/cos α when the wheel radius is not updated; evaluated over orders 1–50; one compensation round removes 85%·exp(−(k/20)²) of order k; acceleration error = second derivative of lift error × ω²; Hertzian line contact with load = working load + equivalent mass × |acceleration|.'),
 'checks': ('判据', 'Criteria'), 'ctrl': ('调整', 'Settings'), 'tasks': ('任务', 'Tasks'),
 'l_cam': ('凸轮', 'Cam'), 'l_law': ('运动规律', 'Motion law'), 'l_ht': ('热处理', 'Heat treatment'),
 'l_pass': ('精磨走刀次数（每次把上一次的形状误差缩小到 25%）', 'Finish passes (each cuts the previous shape error to 25%)'),
 'l_k': ('机床误差谐波阶次 k', 'Machine-error harmonic order k'), 'l_ek': ('该谐波幅值（μm）', 'Its amplitude (μm)'),
 'l_R': ('砂轮修整后的实际半径（mm；控制器里是 200.00）', 'Actual wheel radius after dressing (mm; controller holds 200.00)'),
 'l_rc': ('修整后测量并更新砂轮半径', 'Measure and update the wheel radius after dressing'),
 'l_n': ('当前转速（r/min）', 'Current speed (r/min)'),
 'b_comp': ('补偿磨削一轮', 'One compensation round'), 'b_regrind': ('重磨（不补偿）', 'Regrind (no compensation)'),
 'b_reset': ('恢复标准', 'Reset to standard'), 'b_chat': ('振纹：24 阶 2 μm', 'Chatter: order 24, 2 μm'),
 'nm_lab': ('允许最高转速：', 'Allowed maximum speed:'), 'chk': ('核对', 'Check'),
 'back': ('返回教材', 'Back to the book'),
}
J = {
 'c_size': ('尺寸偏差（升程误差的平均值）', 'Size error (mean lift error)'), 'l_size': ('|偏差| ≤ 10 μm', '|error| ≤ 10 μm'),
 'c_pv': ('升程形状误差 P-V（1–50 阶）', 'Lift shape error P-V (orders 1–50)'), 'l_pv': ('≤ 10 μm', '≤ 10 μm'),
 'c_acc': ('最高转速下的加速度误差峰值', 'Peak acceleration error at maximum speed'), 'l_acc': ('≤ 名义峰值加速度的 10%：', '≤ 10% of nominal peak acceleration:'),
 'i_now': ('当前转速下：加速度误差', 'At current speed: acceleration error'), 'i_sig': ('最大接触应力', 'max contact stress'),
 'i_nal': ('按加速度判据允许的最高转速', 'max speed allowed by the acceleration criterion'),
 'i_rounds': ('已做补偿磨削', 'Compensation rounds done'), 'i_r': ('轮', ''),
 'mag': ('误差放大', 'error ×'), 'grind': ('磨削点', 'grinding point'), 'limit': ('限值', 'limit'), 'nmax': ('最高转速', 'max speed'),
 'deg': ('凸轮转角（°）', 'cam angle (°)'), 'order': ('阶次 k', 'order k'), 'rpm': ('转速（r/min）', 'speed (r/min)'),
 'done': ('✓ 完成', '✓ Done'), 'notdone': ('○ 未完成', '○ Not done'),
 't1': ('弯针凸轮、修正梯形、默认误差源（渗碳淬火、精磨 1 次、6 阶 3 μm、砂轮半径已更新）下，磨后的升程形状误差超差。只做一轮补偿磨削，使三条判据全部满足。',
        'Looper cam, modified trapezoid, default error sources (carburised, 1 finish pass, order 6 at 3 μm, wheel radius updated): the as-ground lift shape error is out of limit. Use exactly one compensation round to satisfy all three criteria.'),
 'd1': ('也试一试：不补偿、把精磨次数加到 2 或 3 次，哪些误差变小了，哪些没变？', 'Also try: no compensation but 2 or 3 finish passes. Which errors shrink, which do not?'),
 't2': ('砂轮修整后实际半径降到 199.85 mm 以下，控制器里还是 200.00。先不更新半径做一轮补偿磨削，看尺寸偏差能否合格；再勾选“更新砂轮半径”，使三条判据全部满足。',
        'After dressing, the actual wheel radius drops below 199.85 mm while the controller still holds 200.00. First do one compensation round without updating the radius and see whether the size passes; then tick “update the wheel radius” and satisfy all three criteria.'),
 'd2': ('砂轮小了 d、程序没改，工件处处多留 d：尺寸差 d，形状差 d(1/cos α − 1)。补偿磨削按比例修正，修不干净尺寸。',
        'A wheel smaller by d with an unchanged program leaves d extra everywhere: size error d, shape error d(1/cos α − 1). Compensation corrects only a fraction of it.'),
 't3': ('弯针凸轮上把机床误差设成 24 阶、2 μm（磨床振纹，可用按钮），做一轮补偿磨削，算出按加速度误差判据允许的最高转速，填在下面。',
        'On the looper cam set the machine error to order 24, 2 μm (grinder chatter; use the button), do one compensation round, and work out the maximum speed allowed by the acceleration criterion. Enter it below.'),
 'd3': ('加速度误差与转速平方成正比：n = n₀ √(限值 / a₀)。允许 ±3%。', 'Acceleration error scales with speed squared: n = n₀ √(limit / a₀). ±3% accepted.'),
 'm_pre': ('先把条件设好：弯针凸轮，24 阶 2 μm，补偿磨削一轮。', 'Set the conditions first: looper cam, order 24 at 2 μm, one compensation round.'),
 'm_ok': ('正确：约 {n} r/min。振纹的阶次高，补偿一轮只修掉约 20%，剩下的只能靠工艺（修整砂轮、减振、光磨）去掉，或者降速。',
          'Correct: about {n} r/min. The chatter order is high, one round removes only about 20%; the rest must be removed by the process (dressing, damping, spark-out) or by lowering the speed.'),
 'm_no': ('还不对：先读出最高转速下的加速度误差 a₀，n = n₀ √(限值 / a₀)。', 'Not yet: read the acceleration error a₀ at maximum speed, then n = n₀ √(limit / a₀).'),
}

TEMPLATE = r'''<!doctype html>
<html lang="{{htmllang}}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
</head>
<body>
<title>{{title}}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@700&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
:root{
  --bg:#f3f5f4; --sheet:#ffffff; --ink:#1b2430; --muted:#5a6570; --rule:#d7dde1; --soft:#eef1f2;
  --nt:#2a5fb8; --bt:#d9622b; --cam:#e9f0fc; --accent:#0f6e74; --ok:#1e8449; --bad:#c0392b; --warn:#b7791f; --pur:#7444b4;
  --f-display:"Noto Serif SC","Songti SC",serif; --f-body:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif; --f-mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#11161b;--sheet:#182029;--ink:#e2e7ec;--muted:#9aa6b2;--rule:#2b3540;--soft:#1e2731;--nt:#7fa9f2;--bt:#f08c58;--cam:#1f2d40;--accent:#4cc3c9;--ok:#5fd08a;--bad:#ff7b6b;--warn:#e8b04b;--pur:#b593ef}}
:root[data-theme="dark"]{--bg:#11161b;--sheet:#182029;--ink:#e2e7ec;--muted:#9aa6b2;--rule:#2b3540;--soft:#1e2731;--nt:#7fa9f2;--bt:#f08c58;--cam:#1f2d40;--accent:#4cc3c9;--ok:#5fd08a;--bad:#ff7b6b;--warn:#e8b04b;--pur:#b593ef}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:15px;line-height:1.6}
.wrap{max-width:1360px;margin:0 auto;padding-inline:16px;padding-block:18px 36px}
header{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 16px;margin-bottom:12px}
h1{font-family:var(--f-display);font-size:1.5rem;margin:0}
.sub{color:var(--muted);font-size:.9rem}
button,select{font:inherit;font-size:.86rem;border:1px solid var(--rule);background:var(--sheet);color:var(--ink);border-radius:6px;padding:5px 12px;cursor:pointer}
button:hover{border-color:var(--accent)}
button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
input[type=number]{font:inherit;font-size:.86rem;border:1px solid var(--rule);background:var(--sheet);color:var(--ink);border-radius:6px;padding:4px 8px;width:6em;font-family:var(--f-mono)}
.grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,350px);gap:14px;align-items:start}
@media (max-width:1000px){.grid{grid-template-columns:minmax(0,1fr)}}
.col{display:flex;flex-direction:column;gap:14px;min-width:0}
.panel{background:var(--sheet);border:1px solid var(--rule);border-radius:10px;padding:12px;min-width:0}
.panel h3{margin:0 0 8px;font-size:.78rem;letter-spacing:.06em;color:var(--muted);font-weight:600}
canvas{display:block;width:100%;height:auto;border-radius:6px}
.two{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,3fr);gap:12px}
.two2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px}
@media (max-width:700px){.two,.two2{grid-template-columns:minmax(0,1fr)}}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:10px}
.note{font-size:.8rem;color:var(--muted);margin:8px 0 0}
.prm{display:grid;grid-template-columns:minmax(0,1fr) 5.6em;gap:2px 10px;align-items:center;font-size:.84rem}
.prm label{grid-column:1/-1;color:var(--muted);margin-top:6px}
.prm select{grid-column:1/-1}
.prm output{font-family:var(--f-mono);font-variant-numeric:tabular-nums;text-align:right}
.prm .cb{grid-column:1/-1;display:flex;gap:6px;align-items:center;color:var(--ink);margin-top:6px}
input[type=range]{accent-color:var(--accent);width:100%}
.checks{display:flex;flex-direction:column;gap:6px;font-size:.84rem}
.checks div{display:grid;grid-template-columns:1.4em minmax(0,1fr) auto;gap:6px;align-items:baseline;border-bottom:1px solid var(--rule);padding-bottom:4px}
.checks b{font-family:var(--f-mono);font-variant-numeric:tabular-nums}
.checks .ok{color:var(--ok)} .checks .bad{color:var(--bad)}
.checks small{display:block;color:var(--muted);font-size:.74rem}
.info{font-size:.8rem;color:var(--muted);margin-top:8px;line-height:1.5}
.info b{color:var(--ink);font-family:var(--f-mono);font-weight:600}
.task{border-top:1px solid var(--rule);padding:8px 0 4px;font-size:.86rem}
.task .st{font-family:var(--f-mono);font-weight:600}
.task .st.ok{color:var(--ok)} .task .st.no{color:var(--muted)}
.task small{display:block;color:var(--muted);font-size:.78rem}
.msg{font-size:.82rem;margin-top:6px;min-height:1.3em}
</style>
<div class="wrap">
<header><h1>{{title}}</h1><span class="sub">{{sub}}</span></header>
<div class="grid">
  <div class="col">
    <section class="panel">
      <div class="two">
        <div><h3>{{p_cam}}</h3><canvas id="cv_cam" width="400" height="400" aria-label="{{p_cam}}"></canvas></div>
        <div><h3>{{p_err}}</h3><canvas id="cv_err" width="580" height="400" aria-label="{{p_err}}"></canvas></div>
      </div>
    </section>
    <section class="panel">
      <div class="two2">
        <div><h3>{{p_spec}}</h3><canvas id="cv_spec" width="480" height="290" aria-label="{{p_spec}}"></canvas></div>
        <div><h3>{{p_spd}}</h3><canvas id="cv_spd" width="480" height="290" aria-label="{{p_spd}}"></canvas></div>
      </div>
    </section>
    <section class="panel">
      <h3>{{p_sig}}</h3><canvas id="cv_sig" width="980" height="200" aria-label="{{p_sig}}"></canvas>
      <p class="note">{{note}}</p>
    </section>
  </div>
  <div class="col">
    <section class="panel"><h3>{{checks}}</h3><div class="checks" id="checks"></div><div class="info" id="info"></div></section>
    <section class="panel">
      <h3>{{ctrl}}</h3>
      <div class="prm">
        <label for="cam">{{l_cam}}</label><select id="cam"></select>
        <label for="law">{{l_law}}</label><select id="law"></select>
        <label for="ht">{{l_ht}}</label><select id="ht"></select>
        <label for="passes">{{l_pass}}</label><input id="passes" type="range" min="1" max="4" step="1"><output id="passesv"></output>
        <label for="k">{{l_k}}</label><input id="k" type="range" min="1" max="40" step="1"><output id="kv"></output>
        <label for="ek">{{l_ek}}</label><input id="ek" type="range" min="0" max="10" step="0.5"><output id="ekv"></output>
        <label for="R">{{l_R}}</label><input id="R" type="range" min="199.5" max="200" step="0.01"><output id="Rv"></output>
        <span class="cb"><input id="rcomp" type="checkbox"><label for="rcomp" style="margin:0;color:var(--ink)">{{l_rc}}</label></span>
        <label for="n">{{l_n}}</label><input id="n" type="range" min="500" max="8000" step="100"><output id="nv"></output>
      </div>
      <div class="row"><button id="comp" type="button">{{b_comp}}</button><button id="regrind" type="button">{{b_regrind}}</button></div>
      <div class="row"><button id="chat" type="button">{{b_chat}}</button><button id="reset" type="button">{{b_reset}}</button></div>
    </section>
    <section class="panel">
      <h3>{{tasks}}</h3><div id="tasks"></div>
      <div class="row" style="font-size:.84rem">{{nm_lab}}<input id="nm" type="number" step="10" aria-label="{{nm_lab}}"> r/min<button id="nmChk" type="button">{{chk}}</button></div>
      <div class="msg" id="msg"></div>
    </section>
  </div>
</div>
</div>
<script>
(()=>{
const LANG='{{lang}}', T={{J}};
const $=id=>document.getElementById(id);
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
function ctx(id){const c=$(id),g=c.getContext('2d');g.clearRect(0,0,c.width,c.height);return [c,g];}
const t=k=>T[k];
// ---------------- model (same as figsrc/ch25_model.py)
const N=720,KMAX=50,NY=N/2,PHI=Array.from({length:N},(_,i)=>2*Math.PI*i/N);
const CAMS={{CAMS}};
const LAWS={{LAWS}}, HT={{HT}};
const EPS=0.25,E1=1.0,PH={p1:60,p2:30,p3:100,pk:0},R_PROG=200.0,D_RES=0.002,E_STAR=210e9/(2*(1-0.09));
const rad=d=>d*Math.PI/180, omega=n=>2*Math.PI*n/60;
let MT=null;
function mtrap(T){if(!MT){const n=8000,a=new Float64Array(n);for(let i=0;i<n;i++){const x=(i+.5)/n;a[i]=x<1/8?Math.sin(4*Math.PI*x):x<3/8?1:x<5/8?Math.cos(4*Math.PI*(x-3/8)):x<7/8?-1:-Math.sin(4*Math.PI*(1-x));}
  const v=new Float64Array(n+1);for(let i=0;i<n;i++)v[i+1]=v[i]+a[i]/n;const s=new Float64Array(n+1);for(let i=0;i<n;i++)s[i+1]=s[i]+(v[i+1]+v[i])/2/n;const S=s[n];for(let i=0;i<=n;i++)s[i]/=S;MT={n,s};}
  const x=Math.min(1,Math.max(0,T))*MT.n,i=Math.min(MT.n-1,Math.floor(x)),f=x-i;return MT.s[i]*(1-f)+MT.s[i+1]*f;}
function lawU(law,T){T=Math.min(1,Math.max(0,T));if(law==='harm')return (1-Math.cos(Math.PI*T))/2;if(law==='cyc')return T-Math.sin(2*Math.PI*T)/(2*Math.PI);return mtrap(T);}
function lift(c,law){return PHI.map(p=>{const f=((p*180/Math.PI)%360+360)%360,r1=c.rise,d1=c.dwell,r2=c.ret,h=c.h;
  if(f<r1)return h*lawU(law,f/r1);if(f<r1+d1)return h;if(f<r1+d1+r2)return h*(1-lawU(law,(f-r1-d1)/r2));return 0;});}
// real DFT (k = 0..kmax), and synthesis matching numpy irfft
function dft(y,kmax){const re=new Float64Array(kmax+1),im=new Float64Array(kmax+1);for(let k=0;k<=kmax;k++){let a=0,b=0;for(let i=0;i<N;i++){const q=2*Math.PI*k*i/N;a+=y[i]*Math.cos(q);b-=y[i]*Math.sin(q);}re[k]=a;im[k]=b;}return {re,im};}
function synth(S,p,mult){// p = derivative order, mult(k) extra real factor
  const kmax=S.re.length-1,out=new Float64Array(N);
  for(let k=0;k<=kmax;k++){let a=S.re[k],b=S.im[k];const m=mult?mult(k):1;a*=m;b*=m;
    for(let j=0;j<p;j++){const na=-b*k,nb=a*k;a=na;b=nb;} // multiply by (ik)^p
    const w=(k===0||k===NY)?1:2;
    if(k===NY){for(let i=0;i<N;i++)out[i]+=a*Math.cos(k*PHI[i])/N;}
    else for(let i=0;i<N;i++)out[i]+=w*(a*Math.cos(k*PHI[i])-b*Math.sin(k*PHI[i]))/N;}
  return out;}
function nominal(c,law){const s=lift(c,law),S=dft(s,NY),s1=synth(S,1),s2=synth(S,2);
  const Rp=s.map(v=>c.r0+c.rr+v),alpha=Rp.map((r,i)=>Math.atan2(s1[i],r)),rho=Rp.map((r,i)=>Math.pow(r*r+s1[i]*s1[i],1.5)/(r*r+2*s1[i]*s1[i]-r*s2[i])-c.rr);
  return {s,s1,s2,Rp,alpha,rho};}
const eta=k=>0.85*Math.exp(-Math.pow(k/20,2));
const NOMC={};
function nomOf(cam,law){const key=cam+'|'+law;if(!NOMC[key])NOMC[key]=nominal(CAMS[cam],law);return NOMC[key];}
function aLimit(cam){const c=CAMS[cam],nm=nomOf(cam,c.law);return 0.10*Math.max(...nm.s2.map(Math.abs))*1e-3*omega(c.nmax)**2;}
function errorCurve(p){const c=CAMS[p.cam],nm=nomOf(p.cam,p.law),h=HT[p.ht],r=Math.pow(EPS,p.passes);
  const dw=p.rcomp?D_RES:(R_PROG-p.R);
  return PHI.map((f,i)=>E1*Math.cos(f+rad(PH.p1))+r*h.d2*Math.cos(2*f+rad(PH.p2))+r*h.d3*Math.cos(3*f+rad(PH.p3))+p.ek*Math.cos(p.k*f+rad(PH.pk))+dw*1e3/Math.cos(nm.alpha[i]));}
function evaluate(p,rounds,n){const c=CAMS[p.cam],nm=nomOf(p.cam,p.law);const S=dft(errorCurve(p),KMAX);
  const m=k=>Math.pow(1-eta(k),rounds);
  const ef=synth(S,0,m),size=ef.reduce((a,b)=>a+b,0)/N,shape=Array.from(ef,v=>v-size);
  const pv=Math.max(...shape)-Math.min(...shape);
  const a2=synth(S,2,k=>k===0?0:m(k));const w2=omega(n)**2;
  const ae=Array.from(a2,v=>v*1e-6*w2),aemax=Math.max(...ae.map(Math.abs));
  const an=nm.s2.map(v=>v*1e-3*w2);
  const sig=an.map((a,i)=>{const F=c.Fw+c.m*Math.abs(a+ae[i]),inv=1/(nm.rho[i]*1e-3)+1/(c.rr*1e-3);return Math.sqrt(F*E_STAR*inv/(Math.PI*c.L*1e-3))/1e6;});
  const sig0=an.map((a,i)=>{const F=c.Fw+c.m*Math.abs(a),inv=1/(nm.rho[i]*1e-3)+1/(c.rr*1e-3);return Math.sqrt(F*E_STAR*inv/(Math.PI*c.L*1e-3))/1e6;});
  const amp=k=>k===0?Math.abs(S.re[0])/N:2*Math.hypot(S.re[k],S.im[k])/N*m(k);
  return {size,shape,pv,ae,aemax,sig,sig0,amp,S};}
function nAllow(p,rounds){const c=CAMS[p.cam],r=evaluate(p,rounds,c.nmax);return c.nmax*Math.sqrt(aLimit(p.cam)/r.aemax);}
// ---------------- state
const STD={cam:'looper',law:'mtrap',ht:'carb',passes:1,k:6,ek:3,R:200,rcomp:true,n:6000};
const ST={...STD};let rounds=0;let R0=null,R1=null,RN=null;
const LIM={size:10,pv:10};
function run(){const c=CAMS[ST.cam];R0=evaluate(ST,0,c.nmax);R1=evaluate(ST,rounds,c.nmax);RN=evaluate(ST,rounds,ST.n);
  const al=aLimit(ST.cam);
  const C=[{n:t('c_size'),v:`${R1.size>=0?'+':''}${R1.size.toFixed(1)} μm`,ok:Math.abs(R1.size)<=LIM.size,lim:t('l_size')},
    {n:t('c_pv'),v:`${R1.pv.toFixed(1)} μm`,ok:R1.pv<=LIM.pv,lim:t('l_pv')},
    {n:t('c_acc')+` (${c.nmax} r/min)`,v:`${R1.aemax.toFixed(0)} m/s²`,ok:R1.aemax<=al,lim:`${t('l_acc')} ${al.toFixed(0)} m/s²`}];
  return {C,allOK:C.every(x=>x.ok),al};}
let E=null;
function render(){$('checks').innerHTML=E.C.map(c=>`<div><span class="${c.ok?'ok':'bad'}">${c.ok?'✓':'✗'}</span><span>${c.n}<small>${c.lim}</small></span><b class="${c.ok?'ok':'bad'}">${c.v}</b></div>`).join('');
  $('info').innerHTML=`${t('i_now')} <b>${RN.aemax.toFixed(0)} m/s²</b>；${t('i_sig')} <b>${Math.max(...RN.sig).toFixed(0)} MPa</b><br>${t('i_nal')} <b>${nAllow(ST,rounds).toFixed(0)} r/min</b>；${t('i_rounds')} <b>${rounds}</b> ${t('i_r')}`.split('；').join(LANG==='en'?'; ':'；');}
// ---------------- drawing
function axes(g,x0,x1,y0,y1,ymin,ymax,step,fmt){const Y=v=>y1-(y1-y0)*(v-ymin)/(ymax-ymin);g.strokeStyle=css('--rule');g.fillStyle=css('--muted');g.font='12px '+css('--f-body');g.lineWidth=1;
  for(let v=Math.ceil(ymin/step)*step;v<=ymax+1e-9;v+=step){g.beginPath();g.moveTo(x0,Y(v));g.lineTo(x1,Y(v));g.stroke();g.textAlign='end';g.fillText(fmt?fmt(v):(+v.toFixed(2)),x0-6,Y(v)+4);}g.textAlign='start';return Y;}
function line(g,X,Y,arr,col,w,dash){g.strokeStyle=col;g.lineWidth=w||2;g.setLineDash(dash||[]);g.beginPath();arr.forEach((v,i)=>i?g.lineTo(X(i),Y(v)):g.moveTo(X(i),Y(v)));g.stroke();g.setLineDash([]);}
function nice(m){const e=Math.pow(10,Math.floor(Math.log10(m)));for(const f of [1,2,2.5,5,10])if(f*e>=m)return f*e;return 10*e;}
function drawCam(){const [c,g]=ctx('cv_cam'),W=c.width,H=c.height,cm=CAMS[ST.cam],nm=nomOf(ST.cam,ST.law);
  const rmax=cm.r0+cm.h,sc=(W/2-60)/rmax,cx=W/2-20,cy=H/2;
  const emax=Math.max(1,...R1.shape.map(Math.abs).concat([Math.abs(R1.size)])),mag=Math.max(50,Math.round(18/(emax*1e-3*sc)/50)*50);
  // actual profile from pitch curve offset; draw nominal and magnified actual (radial approx.)
  const pts=(scale)=>PHI.map((f,i)=>{const ps=Math.PI/2-f,Rp=nm.Rp[i];const x=Rp*Math.cos(ps),y=Rp*Math.sin(ps);return [x,y];});
  const P=pts();const prof=[];for(let i=0;i<N;i++){const a=P[(i-1+N)%N],b=P[(i+1)%N];let tx=b[0]-a[0],ty=b[1]-a[1],L=Math.hypot(tx,ty),nx=ty/L,ny=-tx/L;if(nx*P[i][0]+ny*P[i][1]<0){nx=-nx;ny=-ny;}prof.push([P[i][0]-cm.rr*nx,P[i][1]-cm.rr*ny,nx,ny]);}
  const XY=(x,y)=>[cx+x*sc,cy-y*sc];
  g.fillStyle=css('--cam');g.strokeStyle=css('--muted');g.lineWidth=1.5;g.beginPath();prof.forEach((q,i)=>{const [X,Y]=XY(q[0],q[1]);i?g.lineTo(X,Y):g.moveTo(X,Y);});g.closePath();g.fill();g.stroke();
  g.strokeStyle=css('--bad');g.lineWidth=2;g.beginPath();prof.forEach((q,i)=>{const e=(R1.shape[i]+R1.size)*1e-3*mag*Math.cos(nm.alpha[i]);const [X,Y]=XY(q[0]+e*q[2],q[1]+e*q[3]);i?g.lineTo(X,Y):g.moveTo(X,Y);});g.closePath();g.stroke();
  g.fillStyle=css('--ink');g.beginPath();g.arc(cx,cy,4,0,7);g.fill();
  // roller follower at top (cam angle 0 position) and grinding wheel on the right
  const i0=0,[rx,ry]=XY(prof[i0][0]+cm.rr*prof[i0][2],prof[i0][1]+cm.rr*prof[i0][3]);
  g.strokeStyle=css('--nt');g.lineWidth=2;g.beginPath();g.arc(rx,ry,cm.rr*sc,0,7);g.stroke();g.beginPath();g.moveTo(rx,ry-cm.rr*sc);g.lineTo(rx,6);g.stroke();
  // wheel: find profile point whose wheel-centre direction is +x (angle 0) for Rg=200 (drawn as an arc)
  let best=0,bd=9;for(let i=0;i<N;i++){const wx=prof[i][0]+200*prof[i][2],wy=prof[i][1]+200*prof[i][3];const d=Math.abs(Math.atan2(wy,wx));if(d<bd){bd=d;best=i;}}
  const q=prof[best],wcx=q[0]+200*q[2],wcy=q[1]+200*q[3],[gx,gy]=XY(q[0],q[1]);
  g.strokeStyle=css('--bt');g.lineWidth=3;g.beginPath();const [WX,WY]=XY(wcx,wcy);g.arc(WX,WY,200*sc,Math.PI-0.12,Math.PI+0.12);g.stroke();
  g.fillStyle=css('--bt');g.beginPath();g.arc(gx,gy,4,0,7);g.fill();g.font='12px '+css('--f-body');g.fillText(t('grind'),gx+8,gy-8);
  g.fillStyle=css('--muted');g.fillText(`${t('mag')} ${mag}`,10,H-12);}
function drawErr(){const [c,g]=ctx('cv_err'),W=c.width,H=c.height,x0=50,x1=W-22,y0=12,y1=H-36;
  const all=R0.shape.concat(R1.shape),m=Math.max(6,...all.map(Math.abs))*1.15,st=nice(m/3);
  const Y=axes(g,x0,x1,y0,y1,-m,m,st),X=i=>x0+(x1-x0)*i/N;
  g.fillStyle=css('--ok');g.globalAlpha=.08;g.fillRect(x0,Y(LIM.pv/2),x1-x0,Y(-LIM.pv/2)-Y(LIM.pv/2));g.globalAlpha=1;
  if(rounds>0)line(g,X,Y,R0.shape,css('--bad'),1.6,[6,4]);
  line(g,X,Y,R1.shape,rounds>0?css('--ok'):css('--bad'),2.2);
  g.fillStyle=css('--muted');g.textAlign='center';for(let d=0;d<=360;d+=90)g.fillText(d+'°',X(d*2),H-18);g.fillText(t('deg'),(x0+x1)/2,H-3);g.textAlign='start';
  g.fillStyle=css('--ok');g.fillText(`P-V ≤ ${LIM.pv} μm`,x0+6,Y(LIM.pv/2)-4);}
function drawSpec(){const [c,g]=ctx('cv_spec'),W=c.width,H=c.height,x0=46,x1=W-10,y0=12,y1=H-36,K=40;
  const a0=[],a1=[];for(let k=1;k<=K;k++){a0.push(R0.amp(k));a1.push(R1.amp(k));}
  const m=Math.max(2,...a0)*1.1,Y=axes(g,x0,x1,y0,y1,0,m,nice(m/4)),bw=(x1-x0)/K;
  for(let k=1;k<=K;k++){const X=x0+(k-1)*bw;g.fillStyle=css('--bad');g.globalAlpha=.25;g.fillRect(X+1,Y(a0[k-1]),bw-2,y1-Y(a0[k-1]));g.globalAlpha=1;g.fillStyle=css('--bad');g.fillRect(X+bw*.25,Y(a1[k-1]),bw*.5,y1-Y(a1[k-1]));}
  g.fillStyle=css('--muted');g.textAlign='center';for(const k of [1,10,20,30,40])g.fillText(k,x0+(k-.5)*bw,H-18);g.fillText(t('order'),(x0+x1)/2,H-3);g.textAlign='start';}
function drawSpd(){const [c,g]=ctx('cv_spd'),W=c.width,H=c.height,x0=52,x1=W-24,y0=12,y1=H-36,nmx=8000,cm=CAMS[ST.cam];
  const a6=R1.aemax,al=E.al,f=n=>a6*(n/cm.nmax)**2,ym=Math.max(al*2,f(nmx)>al*4?al*4:f(nmx))*1.05;
  const Y=axes(g,x0,x1,y0,y1,0,ym,nice(ym/4)),X=n=>x0+(x1-x0)*n/nmx;
  g.save();g.beginPath();g.rect(x0,y0,x1-x0,y1-y0);g.clip();
  if(rounds>0){const b=R0.aemax;g.strokeStyle=css('--bad');g.setLineDash([6,4]);g.lineWidth=1.6;g.beginPath();for(let n=0;n<=nmx;n+=100){const v=b*(n/cm.nmax)**2;n?g.lineTo(X(n),Y(v)):g.moveTo(X(n),Y(v));}g.stroke();g.setLineDash([]);}
  g.strokeStyle=rounds>0?css('--ok'):css('--bad');g.lineWidth=2.4;g.beginPath();for(let n=0;n<=nmx;n+=100){n?g.lineTo(X(n),Y(f(n))):g.moveTo(X(n),Y(f(n)));}g.stroke();g.restore();
  g.strokeStyle=css('--warn');g.setLineDash([5,4]);g.beginPath();g.moveTo(x0,Y(al));g.lineTo(x1,Y(al));g.stroke();g.beginPath();g.moveTo(X(cm.nmax),y0);g.lineTo(X(cm.nmax),y1);g.stroke();g.setLineDash([]);
  g.fillStyle=css('--warn');g.font='12px '+css('--f-body');g.fillText(`${t('limit')} ${al.toFixed(0)}`,x0+6,Y(al)-5);g.fillText(`${t('nmax')} ${cm.nmax}`,X(cm.nmax)+5,y0+14);
  const na=nAllow(ST,rounds);if(na<nmx){g.fillStyle=css('--pur');g.beginPath();g.arc(X(na),Y(al),5,0,7);g.fill();g.fillText(na.toFixed(0),X(na)-38,Y(al)+18);}
  g.fillStyle=css('--nt');g.beginPath();g.arc(X(ST.n),Y(Math.min(ym,f(ST.n))),4,0,7);g.fill();
  g.fillStyle=css('--muted');g.textAlign='center';for(let n=0;n<=nmx;n+=2000)g.fillText(n,X(n),H-18);g.fillText(t('rpm'),(x0+x1)/2,H-3);g.textAlign='start';}
function drawSig(){const [c,g]=ctx('cv_sig'),W=c.width,H=c.height,x0=52,x1=W-12,y0=10,y1=H-34;
  const m=Math.max(...RN.sig,...RN.sig0)*1.1,Y=axes(g,x0,x1,y0,y1,0,m,nice(m/4)),X=i=>x0+(x1-x0)*i/N;
  line(g,X,Y,RN.sig0,css('--muted'),1.6);line(g,X,Y,RN.sig,css('--bt'),1.8);
  g.fillStyle=css('--muted');g.textAlign='center';for(let d=0;d<=360;d+=45)g.fillText(d+'°',X(d*2),H-16);g.fillText(t('deg'),(x0+x1)/2,H-2);g.textAlign='start';}
// ---------------- UI
const SEL={cam:Object.keys(CAMS).map(k=>[k,CAMS[k][LANG]]),law:Object.keys(LAWS).map(k=>[k,LAWS[k][LANG==='zh'?0:1]]),ht:Object.keys(HT).map(k=>[k,HT[k][LANG]])};
for(const k in SEL)$(k).innerHTML=SEL[k].map(([v,l])=>`<option value="${v}">${l}</option>`).join('');
const fmt={passes:v=>v.toFixed(0),k:v=>v.toFixed(0),ek:v=>v.toFixed(1),R:v=>v.toFixed(2),n:v=>v.toFixed(0)};
function syncUI(){for(const k in fmt){$(k).value=ST[k];$(k+'v').textContent=fmt[k](ST[k]);}for(const k in SEL)$(k).value=ST[k];$('rcomp').checked=ST.rcomp;}
function changed(){syncUI();E=run();render();drawCam();drawErr();drawSpec();drawSpd();drawSig();note();checkTasks();}
for(const k in fmt)$(k).addEventListener('input',()=>{ST[k]=+$(k).value;changed();});
$('law').onchange=()=>{ST.law=$('law').value;changed();};$('ht').onchange=()=>{ST.ht=$('ht').value;changed();};
$('cam').onchange=()=>{ST.cam=$('cam').value;ST.law=CAMS[ST.cam].law;ST.n=CAMS[ST.cam].nmax;rounds=0;changed();};
$('rcomp').onchange=()=>{ST.rcomp=$('rcomp').checked;changed();};
$('comp').onclick=()=>{rounds=Math.min(3,rounds+1);changed();};$('regrind').onclick=()=>{rounds=0;changed();};
$('chat').onclick=()=>{ST.k=24;ST.ek=2;changed();};
$('reset').onclick=()=>{Object.assign(ST,STD);rounds=0;changed();};
// ---------------- tasks
const seen={t1:false,t2a:false,t2:false,t3:false};
function isDefaultSrc(){return ST.cam==='looper'&&ST.law==='mtrap'&&ST.ht==='carb'&&ST.passes===1&&ST.k===6&&ST.ek===3&&(ST.rcomp||ST.R>=199.995);}
function note(){if(isDefaultSrc()&&rounds===1&&E.allOK)seen.t1=true;
  if(ST.R<=199.85&&!ST.rcomp&&rounds>=1&&!E.C[0].ok)seen.t2a=true;
  if(seen.t2a&&ST.R<=199.85&&ST.rcomp&&E.allOK)seen.t2=true;}
const TASKS=[{t:t('t1'),d:t('d1'),ok:()=>seen.t1},{t:t('t2'),d:t('d2'),ok:()=>seen.t2},{t:t('t3'),d:t('d3'),ok:()=>seen.t3}];
const done=new Set();
function checkTasks(){TASKS.forEach((k,i)=>{if(k.ok())done.add(i);});
  $('tasks').innerHTML=TASKS.map((k,i)=>`<div class="task"><span class="st ${done.has(i)?'ok':'no'}">${done.has(i)?t('done'):t('notdone')}</span> ${k.t}<small>${k.d}</small></div>`).join('');}
$('nmChk').onclick=()=>{if(!(ST.cam==='looper'&&ST.k===24&&ST.ek===2&&rounds===1)){$('msg').textContent=t('m_pre');return;}
  const m=nAllow(ST,rounds),v=+$('nm').value;
  if($('nm').value!==''&&Math.abs(v-m)/m<=0.03){seen.t3=true;$('msg').textContent=t('m_ok').replace('{n}',m.toFixed(0));}else $('msg').textContent=t('m_no');checkTasks();};
window.__api={ST,STD,evaluate,errorCurve,nAllow,aLimit,run,changed,done,seen,get rounds(){return rounds;},set rounds(v){rounds=v;},
  comp:()=>$('comp').click(),nm:v=>{$('nm').value=v;$('nmChk').click();}};
changed();
})();
</script><a href="../index.html" style="position:fixed;right:12px;bottom:12px;z-index:99;font:13px system-ui,sans-serif;background:rgba(20,30,40,.78);color:#fff;padding:6px 10px;border-radius:6px;text-decoration:none">{{back}}</a>
</body>
</html>
'''

def build():
    import sys; sys.path.insert(0, HERE)
    from ch25_model import CAMS, LAWS, HT
    for i, L in enumerate(('zh', 'en')):
        h = TEMPLATE
        for k, v in S.items():
            h = h.replace('{{' + k + '}}', v[i])
        h = h.replace('{{htmllang}}', 'zh-CN' if L == 'zh' else 'en').replace('{{lang}}', L)
        h = h.replace('{{J}}', json.dumps({k: v[i] for k, v in J.items()}, ensure_ascii=False))
        h = h.replace('{{CAMS}}', json.dumps(CAMS, ensure_ascii=False))
        h = h.replace('{{LAWS}}', json.dumps(LAWS, ensure_ascii=False)).replace('{{HT}}', json.dumps(HT, ensure_ascii=False))
        assert '{{' not in h, h[h.find('{{'):h.find('{{') + 40]
        d = os.path.join(ROOT, 'src', L, 'labs'); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'cam.html'), 'w').write(h); print('wrote', L)

if __name__ == '__main__':
    build()
