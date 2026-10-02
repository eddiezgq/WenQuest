// ---- model (model21.py) ----
const OPS=[[1,'后片锁边','OL',0.45,[]],[2,'收后省','SN',0.40,[1]],[3,'开后袋','SN',1.20,[2]],[4,'后袋袋布缉合','SN',0.60,[3]],[5,'后袋口套结','BT',0.25,[4]],
[6,'前片锁边','OL',0.45,[]],[7,'做斜插袋','SN',0.90,[6]],[8,'袋口压明线','SN',0.50,[7]],[9,'门襟里襟锁边','OL',0.35,[]],[10,'绱拉链','SN',0.70,[6,9]],[11,'门襟压明线','SN',0.55,[10]],
[12,'合前后裆','OL',0.50,[5,11]],[13,'合侧缝','OL',0.80,[8,12]],[14,'侧缝压明线','SN',0.60,[13]],[15,'合下裆','OL',0.70,[14]],[16,'做串带','CS',0.25,[]],[17,'绱腰头','SN',1.30,[15,16]],
[18,'做腰头两端','SN',0.60,[17]],[19,'钉串带','BT',0.55,[18]],[20,'卷裤脚','SN',0.55,[15]],[21,'锁眼','BH',0.20,[18]],[22,'钉扣','BS',0.20,[21]],[23,'剪线头检验','HD',0.60,[19,20,22]]];
const MN={SN:'平缝机',OL:'包缝机',CS:'链缝机',BT:'套结机',BH:'锁眼机',BS:'钉扣机',HD:'手工',AP:'自动开袋机',WB:'绱腰机'};
const IMP={3:['开后袋（自动开袋机）','AP',0.45],17:['绱腰头（绱腰机）','WB',0.80]};
const MCOL={SN:'--nt',OL:'--bt',CS:'--win',BT:'--warn',BH:'--accent',BS:'--accent',HD:'--muted',AP:'--bad',WB:'--bad'};
function ops(imp){const o={};OPS.forEach(([i,n,m,s,p])=>{if(imp&&IMP[i])[n,m,s]=IMP[i];o[i]={id:i,name:n,m,sam:s,pre:p};});return o;}
function succW(by){const S={};for(const i in by)S[i]=new Set();for(const i in by)by[i].pre.forEach(p=>S[p].add(+i));const memo={};
  const all=i=>{if(memo[i])return memo[i];let r=new Set();S[i].forEach(j=>{r.add(j);all(j).forEach(x=>r.add(x));});return memo[i]=r;};const W={};for(const i in by){let s=by[i].sam;all(+i).forEach(j=>s+=by[j].sam);W[i]=s;}return W;}
function topo(by){const W=succW(by),done=[],s=new Set();const ids=Object.keys(by).map(Number);while(done.length<ids.length){const av=ids.filter(i=>!s.has(i)&&by[i].pre.every(p=>s.has(p)));
  av.sort((a,b)=>(W[b]-W[a])||(a-b));done.push(av[0]);s.add(av[0]);}return done;}
const types=(by,g)=>new Set(g.map(i=>by[i].m).filter(m=>m!=='HD'));
function groups(by,seq,cuts,takt){const gs=[];let cur=[];seq.forEach((i,k)=>{cur.push(i);if(cuts.has(i)||k===seq.length-1){gs.push(cur);cur=[];}});
  return gs.map(g=>{const ld=g.reduce((a,i)=>a+by[i].sam,0);return {ops:g,ld,k:Math.max(1,Math.ceil(ld/takt-1e-9))};});}
function metrics(by,gs){const loads=gs.map(g=>g.ld/g.k),N=gs.reduce((a,g)=>a+g.k,0),mx=Math.max(...loads),T=Object.values(by).reduce((a,o)=>a+o.sam,0),mach={};
  gs.forEach(g=>{const sm={};g.ops.forEach(i=>{const m=by[i].m;if(m!=='HD')sm[m]=(sm[m]||0)+by[i].sam;});for(const m in sm)mach[m]=(mach[m]||0)+Math.min(g.k,Math.ceil(sm[m]/mx-1e-9));});
  return {N,mx,out:60/mx,bal:T/(N*mx),T,loads,mach};}
function dp(by,seq,takt){const n=seq.length,best=new Array(n+1).fill(null),arg=new Array(n+1);best[0]=[0,0];
  for(let j=1;j<=n;j++)for(let i=Math.max(0,j-4);i<j;i++){const g=seq.slice(i,j),ld=g.reduce((a,x)=>a+by[x].sam,0);if(types(by,g).size>2)continue;const k=Math.max(1,Math.ceil(ld/takt-1e-9));if(k>4||!best[i])continue;
    const c=[best[i][0]+k,Math.max(best[i][1],ld/k)];if(!best[j]||c[0]<best[j][0]||(c[0]===best[j][0]&&c[1]<best[j][1]-1e-12)){best[j]=c;arg[j]=i;}}
  const cuts=new Set();let j=n;while(j>0){cuts.add(seq[j-1]);j=arg[j];}return cuts;}

const WAGE=0.5;
function mm(n,a,t,w,mr){const C=Math.max(n*(a+w),a+t);return {C,out:60*n/C,uo:n*(a+w)/C,um:(a+t)/C,cost:(WAGE+n*mr)*C/n};}
const ALPHA=(2.5+0.15)/6e-4;
function seamTime(st,nmax,nsoft=400,ks=3,ntrim=300){const al=ALPHA*0.6,dt=2e-4;let th=0,w=nsoft*2*Math.PI/60,t=0;const wm=nmax*2*Math.PI/60,wt=ntrim*2*Math.PI/60;let ph='soft';
  for(let it=0;it<1e6;it++){const s=th/(2*Math.PI);if(ph==='soft'&&s>=ks)ph='run';
    if(ph==='run'){const rem=(st-1)*2*Math.PI-th;if((w*w-wt*wt)/(2*al)>=rem)ph='dec';else w=Math.min(wm,w+al*dt);}
    if(ph==='dec'){w=Math.max(wt,w-al*dt);if(th>=(st-1)*2*Math.PI)ph='trim';}
    if(ph==='trim'&&th>=st*2*Math.PI+55*Math.PI/180)ph='stop';
    if(ph==='stop'){w=Math.max(0,w-ALPHA*dt);if(w===0)return t;}th+=w*dt;t+=dt;}return t;}

const out={};
for(const imp of [0,1]){const by=ops(imp);const seq=topo(by);out['seq'+imp]=seq;out['by'+imp]=by;
 for(const tgt of [120]){const takt=60/tgt;
  const one=groups(by,seq,new Set(seq),takt);out['one'+imp]={gs:one,m:metrics(by,one)};
  const d=groups(by,seq,dp(by,seq,takt),takt);out['dp'+imp]={gs:d,m:metrics(by,d)};
  const t2=0.55;const d2=groups(by,seq,dp(by,seq,t2),t2);out['dp055_'+imp]={gs:d2,m:metrics(by,d2)};
 }}
const sm={};for(const n of [3000,4000,5000,6000]){sm[n]=[];for(let st=10;st<=590;st+=5)sm[n].push([st,seamTime(st,n)]);}
out.seam=sm;out.s333=[seamTime(333,4000),seamTime(333,5000)];out.s40=[seamTime(40,4000),seamTime(40,6000)];
require('fs').writeFileSync('figsrc/en_c2628/line.json',JSON.stringify(out));
console.log(JSON.stringify(out.seq0),JSON.stringify(out.one0.m),JSON.stringify(out.dp0.m),JSON.stringify(out.dp055_0.m),JSON.stringify(out.dp1.m),out.s333,out.s40);
for(const k of ['one0','dp0','dp055_0','dp1'])console.log(k,out[k].gs.map(g=>g.ops.join('+')+':'+g.k).join(' | '));
