function rng(seed){let s=seed>>>0;return ()=>{s=(s+0x6D2B79F5)>>>0;let t=s;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296;};}
function gauss(r){let u=r();while(u===0)u=r();const v=r();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}
function fleet(sigma,n=200,days=180,frac=0.5,T=30,k=0.1,seed=11){const r=rng(seed),M=[];for(let i=0;i<n;i++){const deg=r()<frac,t0=deg?30+Math.floor(r()*121):null,sig=new Float64Array(days);
  for(let d=0;d<days;d++){let x=1+sigma*gauss(r);if(deg&&d>=t0)x+=(Math.exp(k*(d-t0))-1)/(Math.exp(k*T)-1);sig[d]=x;}M.push({deg,t0,fail:deg?t0+T:null,sig});}return M;}
function alarms(M,thr,w,days=180){let det=0,lead=0,fal=0,ndeg=0,hd=0;const marks=[];for(const m of M){const s=m.sig;let armed=true,caught=false,sum=0;const end=m.deg&&m.fail<days?m.fail:days;if(m.deg)ndeg++;const mk=[];
  for(let d=0;d<end;d++){sum+=s[d];if(d>=w)sum-=s[d-w];if(d<w-1)continue;const ma=sum/w,healthy=!m.deg||d<m.t0;if(healthy)hd++;
    if(ma>thr&&armed){armed=false;mk.push(d);if(healthy)fal++;else if(!caught){caught=true;det++;lead+=m.fail-d;}}else if(ma<=thr)armed=true;}marks.push(mk);}
  return {det:det/Math.max(ndeg,1),lead:lead/Math.max(det,1),fpm:fal/Math.max(hd,1)*30,ndeg,marks};}
const M=fleet(0.08);
const out={machines:[],curves:{}};
const r=alarms(M,1.12,3);
M.forEach((m,i)=>{if(m.deg&&m.t0>=95&&m.t0<=102)out.machines.push({i,t0:m.t0,fail:m.fail,marks:r.marks[i],sig:Array.from(m.sig)});});
for(const w of [1,3,7]){const c=[];for(let t=1.0;t<=2.0001;t+=0.005){const a=alarms(M,t,w);c.push([+t.toFixed(3),a.fpm,a.lead,a.det]);}out.curves[w]=c;}
console.log(JSON.stringify(out));
