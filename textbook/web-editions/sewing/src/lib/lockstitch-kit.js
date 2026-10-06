/* 平缝机机构库 WQLS（第 20 轮）。《缝纫机设计与制造》第 3–8 章的机构模型，从实验 3-1、4-1、5-1、6-1、7-1、8-1 原样抽出：
   公式、常数、算例数值一律不改（改前改后各实验的读数与判定逐项一致，见 tools/labsnap.py）。
   虚拟样机、实验 8-2 综合调机和以后的包缝机、花样机都用它。实验页里写
   一个带 data-inline 的 script 标签（见 inline.py），构建时内联进单个 HTML 文件（课程包要求单文件）。
   角度单位：度，主轴转角 0° = 针杆上止点。长度 mm。 */
(function(root){
const DEG=Math.PI/180;

/* ---------- 第 3 章 针杆曲柄滑块（算例 r = 15.5 mm，l = 55 mm） ---------- */
const needle=(()=>{
  const RN=15.5, LN=55, LAM=RN/LN;
  const xN=f=>{const a=f*DEG,l=RN/LN;return RN*(1-Math.cos(a))-LN*(1-Math.sqrt(1-(l*Math.sin(a))**2));};
  const rise=f=>xN(180)-xN(f);
  // 实验 3-1 的一般形式：任意 r、l、n（原样，D 为度换弧度）
  const D=DEG;
  const X=(f,r_=r,l_=l)=>{const p=f*D,la=r_/l_;return r_*(1-Math.cos(p))-l_*(1-Math.sqrt(1-la*la*Math.sin(p)**2));};
  const V=(f,r_=r,l_=l,n_=n)=>{const w=n_*Math.PI/30,p=f*D,la=r_/l_,S=Math.sqrt(1-la*la*Math.sin(p)**2);return w*r_*Math.sin(p)*(1-la*Math.cos(p)/S)/1000;};
  const A=(f,r_=r,l_=l,n_=n)=>{const w=n_*Math.PI/30,p=f*D,la=r_/l_,S=Math.sqrt(1-la*la*Math.sin(p)**2);return w*w*r_*(Math.cos(p)-la*(Math.cos(2*p)+la*la*Math.sin(p)**4)/S**3)/1000;};
  const aN=(f,w)=>{const a=f*DEG,S=Math.sqrt(1-LAM*LAM*Math.sin(a)**2);return RN*1e-3*w*w*(Math.cos(a)-LAM*(Math.cos(2*a)+LAM**2*Math.sin(a)**4)/S**3);};
  // 钩线时刻：机针回升 2 mm 的转角（二分 60 次，同实验 5-1）
  let PHC0=206;{let a=181,b=240;for(let i=0;i<60;i++){const m=(a+b)/2;if(rise(m)<2)a=m;else b=m;}PHC0=(a+b)/2;}
  return {RN,LN,LAM,xN,rise,X,V,A,aN,PHC0};
})();

/* ---------- 第 4 章 挑线机构：供线量与耗线量（实验 4-1） ---------- */
const takeup=(()=>{
  const xN=needle.xN, RN=needle.RN, LN=needle.LN;
  const RH=13.5, RC=11.0, EYE_TDC=20, TIP_TDC=18;
  const YP=xN(206)-8;                       // needle-plate top above hook centre: beak passes 1.5 mm above the eye at a 206° catch
  function hullPerim(pts){
    const p=pts.map(q=>[q[0],q[1]]).sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
    if(p.length<2)return 0;
    const cr=(o,a,b)=>(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);
    const lo=[],up=[];
    for(const q of p){while(lo.length>=2&&cr(lo[lo.length-2],lo[lo.length-1],q)<=0)lo.pop();lo.push(q);}
    for(let i=p.length-1;i>=0;i--){const q=p[i];while(up.length>=2&&cr(up[up.length-2],up[up.length-1],q)<=0)up.pop();up.push(q);}
    const h=lo.slice(0,-1).concat(up.slice(0,-1));let s=0;
    for(let i=0;i<h.length;i++){const a=h[i],b=h[(i+1)%h.length];s+=Math.hypot(b[0]-a[0],b[1]-a[1]);}
    return s;
  }
  const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u);};
  function loopPts(f,t,phc){
    const x=xN(f),e=EYE_TDC-t-x,F=[0,YP+t],th=(90-2*(f-phc))*DEG,H=[RH*Math.cos(th),RH*Math.sin(th)];
    const pts=[F,H],sw=2*(f-phc);
    for(let a=0;a<sw;a+=1){const q=(90-a)*DEG;pts.push([RC*Math.cos(q),RC*Math.sin(q)]);}
    if(e<0)pts.push([0,YP+t+e]);
    return {pts,e,x,H,F};
  }
  function demandRaw(f,t,phc){
    const x=xN(f),e=EYE_TDC-t-x;
    if(f<phc)return 2*Math.max(0,-e);
    const L=loopPts(f,t,phc),P=hullPerim(L.pts),tail=e<0?P+e:e+P;
    return x+tail-(EYE_TDC-t);
  }
  function demand(f,t,s,phc){
    const bot=phc+90,off=phc+135,c=s+t;
    if(f<=bot)return demandRaw(f,t,phc);
    if(f<=off){const Lb=demandRaw(bot,t,phc),u=smooth((f-bot)/(off-bot));return Lb*(1-u)+c*u;}
    return c;
  }
  // ---------- take-up four-bar (worked example; coordinates in mm, origin = upper shaft centre, z to the right, y up) ----------
  const LK0={r:20.7,d:-6.8,Qz:21.5,Qy:-45.5,a:43.4,b:40.9,c:65.7,al:2.8};
  const AC=[122.2,-45.7], ADIR=[Math.cos(285.2*DEG),Math.sin(285.2*DEG)], B=[66.4,-117.7];
  const T_DISC=[178,-60], K_PIV=[158,-88], K_ARM=24;
  function linkPose(f,lk){
    const q=(f+lk.d)*DEG,P=[-lk.r*Math.sin(q),-lk.r*Math.cos(q)],Q=[lk.Qz,lk.Qy];
    const dz=Q[0]-P[0],dy=Q[1]-P[1],D=Math.hypot(dz,dy),tt=(lk.a*lk.a-lk.b*lk.b+D*D)/(2*D),h2=lk.a*lk.a-tt*tt;
    if(!(h2>0))return null;
    const h=Math.sqrt(h2),mz=P[0]+tt*dz/D,my=P[1]+tt*dy/D,M=[mz-h*dy/D,my+h*dz/D];
    const uz=(M[0]-P[0])/lk.a,uy=(M[1]-P[1])/lk.a,ca=Math.cos(lk.al*DEG),sa=Math.sin(lk.al*DEG);
    const E=[P[0]+lk.c*(uz*ca-uy*sa),P[1]+lk.c*(uz*sa+uy*ca)];
    const w1=[P[0]-M[0],P[1]-M[1]],w2=[Q[0]-M[0],Q[1]-M[1]];
    const mu=Math.acos(Math.max(-1,Math.min(1,(w1[0]*w2[0]+w1[1]*w2[1])/lk.a/lk.b)))/DEG;
    return {P,M,E,Q,mu};
  }
  function pchipPeriodic(ys){
    const n=ys.length,h=30,dl=[];for(let i=0;i<n;i++)dl.push((ys[(i+1)%n]-ys[i])/h);
    const m=[];for(let i=0;i<n;i++){const a=dl[(i-1+n)%n],b=dl[i];m.push(a*b<=0?0:2/(1/a+1/b));}
    return f=>{f=((f%360)+360)%360;const i=Math.floor(f/h)%n,u=(f-i*h)/h,y0=ys[i],y1=ys[(i+1)%n],m0=m[i]*h,m1=m[(i+1)%n]*h;
      const u2=u*u,u3=u2*u;return (2*u3-3*u2+1)*y0+(u3-2*u2+u)*m0+(-2*u3+3*u2)*y1+(u3-u2)*m1;};
  }
  function compute(ST,camPts){
    const N=360,ph=[],S=new Array(N),D=new Array(N),E=[],mu=[];
    let ok=true;
    const A=[AC[0]+ST.u*ADIR[0],AC[1]+ST.u*ADIR[1]];
    if(ST.mode==='link'){
      const Lp=[];
      for(let i=0;i<N;i++){const p=linkPose(i,ST.lk);if(!p){ok=false;break;}E.push(p.E);mu.push(p.mu);
        Lp.push(Math.hypot(p.E[0]-A[0],p.E[1]-A[1])+Math.hypot(p.E[0]-B[0],p.E[1]-B[1]));}
      if(!ok)return {ok:false};
      const mx=Math.max(...Lp);for(let i=0;i<N;i++)S[i]=mx-Lp[i];
    }else{
      const fn=pchipPeriodic(camPts);for(let i=0;i<N;i++)S[i]=Math.max(0,fn(i));
      const mn=Math.min(...S);for(let i=0;i<N;i++)S[i]-=mn;
    }
    let top=0;for(let i=1;i<N;i++)if(S[i]<S[top])top=i;
    let bot=0;for(let i=1;i<N;i++)if(S[i]>S[bot])bot=i;
    const c=ST.s+ST.t;
    for(let i=0;i<N;i++)D[i]=i<top?c:demand(i,ST.t,ST.s,ST.phc);
    const sl=S.map((v,i)=>v-D[i]);
    let fin=0;while(fin<180&&xN(fin)<EYE_TDC-ST.t)fin++;   // needle eye enters the fabric
    let margin=1e9,at=0;for(let i=ST.phc;i<=Math.min(359,ST.phc+135);i++)if(sl[i]<margin){margin=sl[i];at=i;}
    let waste=-1e9;for(let i=ST.phc;i<=Math.min(359,ST.phc+90);i++)waste=Math.max(waste,sl[i]);
    let pre=-1e9;for(let i=top;i<=fin;i++)pre=Math.max(pre,sl[i]);
    let neg=0;for(let i=fin;i<ST.phc;i++)neg=Math.max(neg,-sl[i]);
    // thread acceleration at ST.rpm: second difference of S
    const w=ST.rpm*2*Math.PI/60;let acc=0;
    for(let i=0;i<N;i++){const d2=(S[(i+1)%N]-2*S[i]+S[(i-1+N)%N])/(DEG*DEG);acc=Math.max(acc,Math.abs(d2));}
    const R={ok:true,S,D,sl,top,bot,fin,margin,at,waste,pre,neg,entry:sl[fin],c,Smax:S[bot],acc:acc*w*w/1000,
       mu:mu.length?[Math.min(...mu),Math.max(...mu)]:null,E,A};
    return R;
  }
  return {RH,RC,EYE_TDC,TIP_TDC,YP,hullPerim,smooth,loopPts,demandRaw,demand,LK0,AC,ADIR,B,T_DISC,K_PIV,K_ARM,linkPose,pchipPeriodic,compute};
})();

/* ---------- 第 5 章 旋梭定时、针杆高度与梭尖间隙（实验 5-1；线环模型为示意） ---------- */
const hook=(()=>{
  const rise=needle.rise, PHC0=needle.PHC0;
  const H0=2.2, TB=0.15, D_REF=0.9, RH=13.5;
  const fLoop=h=>{h=Math.max(h,0);return (h/H0)**2*Math.exp(2*(1-h/H0));};
  const yTop=h=>0.5+0.9*Math.max(h,0);
  const FAB={woven:{W:0.75,sd:0.10},knit:{W:0.5,sd:0.15}};
  const ST={psi:0,dz:0,g:0.08,d:0.9,fab:'woven',phi:180,play:true};
  function geom(o){
    const fc=PHC0+o.psi/2, h=rise(fc), D=1.0-o.dz-(h-2.0), g=o.g-(o.d-D_REF)/2, W=FAB[o.fab].W;
    const yt=yTop(h), y=D+0.15, wAt=(y>0&&y<yt)?W*fLoop(h)*Math.sin(Math.PI*y/yt):0;
    let res;
    if(g<=0.02)res='hit';else if(D<0.2)res='cut';else res=(wAt-(g+TB)>=0)?'ok':'skip';
    return {fc,h,D,g,W,yt,wAt,margin:wAt-(g+TB),res};
  }
  // 试缝一针：在 geom 的结果上叠加随机波动（gauss 由调用者给，实验 5-1 用 LCG 种子 7）
  function stitch(g0,o,gauss){
    const sd=FAB[o.fab].sd,dh=0.08*gauss(),dg=0.015*gauss(),kW=1+sd*gauss();
    const h=g0.h+dh,D=1.0-o.dz-(h-2.0),g=g0.g+dg,yt=yTop(h),y=D+0.15;
    const w=(y>0&&y<yt)?g0.W*kW*fLoop(h)*Math.sin(Math.PI*y/yt):0;
    return g<=0.02?'hit':D<0.2?'cut':(w-(g+TB)>=0?'ok':'skip');
  }
  // 实验 5-1 的随机数（glibc 式 LCG，按 JS 双精度运算，种子 7）
  function lcg(seed){const rnd=()=>{seed=(seed*1103515245+12345)%2147483648;return seed/2147483648;};
    const gauss=()=>{let u=0,v=0;while(!u)u=rnd();while(!v)v=rnd();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);};return {rnd,gauss};}
  return {PHC0,H0,TB,D_REF,RH,fLoop,yTop,FAB,geom,stitch,lcg};
})();

/* ---------- 第 6 章 送布牙轨迹与送布时序（实验 6-1；面料参数为示意） ---------- */
const feed=(()=>{
  const RN=15.5,LN=55,TIP0=18,EYE=2;
  const xN=f=>{const a=f*DEG,l=RN/LN;return RN*(1-Math.cos(a))-LN*(1-Math.sqrt(1-(l*Math.sin(a))**2));};
  const tip=f=>TIP0-xN(f);
  const cross=(lv)=>{let a=0,b=180;for(let i=0;i<60;i++){const m=(a+b)/2;if(tip(m)>lv)a=m;else b=m;}return (a+b)/2;};
  const FE=cross(-EYE);                 // needle-eye top reaches plate: 114.2°
  const A=1.1,H0=0.8,HALF0=Math.acos((A-H0)/A)/DEG,PHL0=FE-HALF0,EFF0=(1-Math.cos(2*HALF0*DEG))/2;
  const FAB={lining:{t:0.4,mud:0.55,muf:0.15,F0:0.32,K:10,hreq:0.7,hmax:0.85,Pmark:1.4,name:'衬里滑料'},
             cotton:{t:1.5,mud:0.80,muf:0.25,F0:0.30,K:50,hreq:0.75,hmax:1.1,Pmark:2.0,name:'棉布'},
             denim:{t:4.0,mud:0.85,muf:0.30,F0:0.75,K:40,hreq:0.95,hmax:1.5,Pmark:2.5,name:'牛仔布'}};
  const MODEF={drop:1.0,needle:0.3,compound:0.08};
  const STD={s:3,dT:0,dP:0,h:0.8,P:1.0};
  function model(o){const f=FAB[o.fab];
    const half=Math.acos(Math.max(-1,Math.min(1,(A-o.h)/A)))/DEG;
    let phL,phF;if(o.mode==='drop'){phL=PHL0+o.dT;phF=FE+o.dT+o.dP;}else{phL=180;phF=180+half;}
    const rise=phL-half,drop=phL+half,S=o.s/EFF0;
    const X=p=>(S/2)*Math.cos((p-phF)*DEG),Y=p=>(o.h-A)+A*Math.cos((p-phL)*DEG);
    const ain=cross(f.t),aout=360-ain;
    let drag=0,back=0;const n=720,sg=o.s>=0?1:-1;
    for(let i=0;i<n;i++){const p0=rise+(drop-rise)*i/n,p1=rise+(drop-rise)*(i+1)/n,dx=X(p1)-X(p0),pm=(((p0+p1)/2)%360+360)%360;
      if(o.mode==='drop'&&pm>ain&&pm<aout)drag+=Math.abs(dx);if(dx*sg<0)back+=Math.abs(dx);}
    const net=X(drop)-X(rise);
    const mud=f.mud*Math.min(1,o.h/f.hreq);
    const Pmin=o.mode==='compound'?f.F0/mud:f.F0/Math.max(mud-f.muf,1e-6);
    const eps=Math.min(1,o.P/Pmin),act=eps*net;
    const ply=f.muf*o.P/f.K*MODEF[o.mode]*400;
    const marks=[];if(o.h>f.hmax+1e-9)marks.push('dog');if(o.P>f.Pmark+1e-9)marks.push('foot');
    const eyeAtDrop=tip(((drop%360)+360)%360)+EYE;
    return {half,phL,phF,rise:((rise%360)+360)%360,drop:((drop%360)+360)%360,riseRaw:rise,dropRaw:drop,S,X,Y,ain,aout,drag,back,net,act,eps,Pmin,ply,marks,eyeAtDrop,t:f.t};
  }
  // fabric (lower ply) position within one revolution starting at phi=0: follows dog while gripped
  function fabPos(M,phi){ // displacement accumulated from 0..phi (deg), eps applied
    let pos=0;const n=Math.max(2,Math.round(phi*2));
    for(let i=0;i<n;i++){const p0=phi*i/n,p1=phi*(i+1)/n;if(M.Y((p0+p1)/2)>=0)pos+=M.X(p1)-M.X(p0);}return pos*M.eps;}
  const mod=a=>((a%360)+360)%360;
  const inWin=(M,p)=>{const q=mod(p-M.riseRaw);return q<=M.dropRaw-M.riseRaw;};
  return {RN,LN,TIP0,EYE,tip,cross,FE,A,H0,HALF0,PHL0,EFF0,FAB,MODEF,STD,model,fabPos,mod,inWin};
})();

/* ---------- 第 7 章 线张力与线迹（实验 7-1；模型为示意） ---------- */
const tension=(()=>{
  const GUIDE=Math.exp(0.2*1.0), EYEK=Math.exp(-0.35*Math.PI), KN=GUIDE*EYEK;
  const THREAD={t18:{name:'Tex 18',F:700,el:0.14},t24:{name:'Tex 24',F:1000,el:0.15},t40:{name:'Tex 40',F:1700,el:0.16}};
  const FAB={lining:{name:'衬里两层',t:0.4,Tmin:20,pf:0.30,B:1.8,jam:'t24',plim:0.15},
             cotton:{name:'衬衫棉布两层',t:1.0,Tmin:35,pf:0.60,B:2.2,jam:'t40',plim:0.3},
             denim:{name:'牛仔布四层',t:4.0,Tmin:100,pf:4.0,B:3.0,jam:'t40',plim:0.3}};
  const ORDER=['t18','t24','t40'];
  const DEF={Td:100,Tb:40,s:3,n:5000};
  function ev(o){const f=FAB[o.fab],T=THREAD[o.th];
    const Tn=KN*o.Td,r=Tn/o.Tb,z=0.5+0.5*Math.max(-1,Math.min(1,Math.log(r)/Math.log(f.B)));
    const EA=T.F/T.el,lam=(o.s+f.t)/o.s,shrink=100*(Tn+o.Tb)/2/EA*lam,pucker=Math.max(0,shrink-f.pf);
    const peak=o.Td*GUIDE*(1+0.15*(o.n/5000)**2),sf=0.5*T.F/peak,loose=Math.min(Tn,o.Tb)<f.Tmin,jam=ORDER.indexOf(o.th)>ORDER.indexOf(f.jam);
    const bal=z>=0.4&&z<=0.6,brk=sf<1.5,pk=pucker>f.plim;
    return {Tn,r,z,shrink,pucker,peak,sf,loose,jam,bal,brk,pk,good:bal&&!loose&&!brk&&!pk&&!jam,f};}
  return {GUIDE,EYEK,KN,THREAD,FAB,ORDER,DEF,ev};
})();

/* ---------- 第 8 章 全机时序与整机惯性力（实验 8-1） ---------- */
const timing=(()=>{
  const {RN,xN,rise,aN}=needle, PHC0=206.067;
  // 供线量 S0 与耗线量 D（布厚 1.5、针距 3、标准挑线机构），保留 3 位小数，同第 4 章算例程序 course/calc/ch04.py
  const r3=v=>Math.round(v*1000)/1000;
  let T=null;
  function table(){
    if(T)return T;
    const R=takeup.compute({mode:'link',u:0,t:1.5,s:3,phc:206,rpm:5000,lk:Object.assign({},takeup.LK0)},null);
    const D={};for(let k=194;k<=218;k++){const a=[];for(let i=0;i<360;i++)a.push(r3(takeup.demand(i,1.5,3,k)));D[String(k)]=a;}
    let fin=0;while(fin<180&&xN(fin)<takeup.EYE_TDC-1.5)fin++;
    T={S0:R.S.map(r3),D,top0:R.top,FIN:fin};return T;
  }
  // ---------- take-up linkage (chapter 4) ----------
  const LK={r:20.7,d:-6.8,Qz:21.5,Qy:-45.5,a:43.4,b:40.9,c:65.7,al:2.8*DEG};
  function link(ph){const f=(ph+LK.d)*DEG,P=[-LK.r*Math.sin(f),-LK.r*Math.cos(f)],Q=[LK.Qz,LK.Qy];
    const d=[Q[0]-P[0],Q[1]-P[1]],D=Math.hypot(d[0],d[1]),t=(LK.a*LK.a-LK.b*LK.b+D*D)/(2*D),h=Math.sqrt(Math.max(0,LK.a*LK.a-t*t));
    const m=[P[0]+t*d[0]/D,P[1]+t*d[1]/D],M=[m[0]-h*d[1]/D,m[1]+h*d[0]/D],u=[(M[0]-P[0])/LK.a,(M[1]-P[1])/LK.a];
    const v=[u[0]*Math.cos(LK.al)-u[1]*Math.sin(LK.al),u[0]*Math.sin(LK.al)+u[1]*Math.cos(LK.al)];return {P,E:[P[0]+LK.c*v[0],P[1]+LK.c*v[1]]};}
  const com=ph=>{const L=link(ph);return [(L.P[0]+0.45*(L.E[0]-L.P[0]))*1e-3,(L.P[1]+0.45*(L.E[1]-L.P[1]))*1e-3];};
  // ---------- feed (chapter 6) ----------
  const A6=1.1,H6=0.8,FE=114.179,HALF=Math.acos((A6-H6)/A6)/DEG,PHL0=FE-HALF,EFF=(1-Math.cos(2*HALF*DEG))/2,S6=3/EFF;
  function feed(dT){const phL=PHL0+dT,phF=FE+dT,rise=phL-HALF,drop=phL+HALF,X=p=>(S6/2)*Math.cos((p-phF)*DEG);
    let drag=0;const n=720;for(let i=0;i<n;i++){const p0=rise+(drop-rise)*i/n,p1=p0+(drop-rise)/n,pm=(((p0+p1)/2)%360+360)%360;if(pm>101.67&&pm<258.33)drag+=Math.abs(X(p1)-X(p0));}
    return {rise:((rise%360)+360)%360,drop:((drop%360)+360)%360,riseRaw:rise,dropRaw:drop,drag,phL,phF,X,Y:p=>(H6-A6)+A6*Math.cos((p-phL)*DEG)};}
  const STD={dh:0,dt:0,dT:0,n:5000,k:0.3};
  // 六条判据的数值部分（文字由实验页给）
  function core(o){const T=table(),FIN=T.FIN;const phc=206+o.dh,top=((T.top0+o.dt)%360+360)%360;
    const S=i=>T.S0[(((i-o.dt)%360)+360)%360],Dt=T.D[String(phc)],sl=[];for(let i=0;i<360;i++){const d=i<top?4.5:Dt[i];sl.push(S(i)-d);}
    let margin=1e9,pre=-1e9,neg=-1e9;for(let i=phc;i<=phc+135;i++)margin=Math.min(margin,sl[i%360]);for(let i=top;i<=FIN;i++)pre=Math.max(pre,sl[i]);for(let i=FIN;i<phc;i++)neg=Math.max(neg,-sl[i]);
    const rc=rise(PHC0+o.dh),F=feed(o.dT),fr=((F.rise-258.3+360)%360);
    return {phc,top,sl,S,Dt,margin,pre,neg,rc,F,feedrise:fr,
      ok:{rise:rc>=1.6&&rc<=2.5,margin:margin>=1,pre:pre<=10,neg:neg<=1,drag:F.drag<=0.05,feedrise:fr>=20&&fr<180}};}
  function forces(o){const w=2*Math.PI*o.n/60,out=[],Fd=feed(o.dT);
    for(let f=0;f<360;f++){const an=aN(f,w),ay=-an,apin=[-w*w*RN*1e-3*Math.sin(f*DEG),-w*w*RN*1e-3*Math.cos(f*DEG)];
      const g=f-o.dt,d=0.5,c0=com(g-d),c1=com(g),c2=com(g+d),dt=d*DEG/w,atk=[(c2[0]-2*c1[0]+c0[0])/dt/dt,(c2[1]-2*c1[1]+c0[1])/dt/dt];
      const afx=-(S6/2)*1e-3*w*w*Math.cos((f-Fd.phF)*DEG),afy=-1.1e-3*w*w*Math.cos((f-Fd.phL)*DEG);
      const mr=0.12,mo=0.06,mt=0.025,mf=0.05,cw=mo+o.k*mr;
      const sx=mo*apin[0]+cw*(-apin[0])+mt*atk[0]+mf*afx, sy=mr*ay+mo*apin[1]+cw*(-apin[1])+mt*atk[1]+mf*afy;
      out.push([-sx,-sy]);}
    return out;}
  return {PHC0,table,LK,link,com,A6,H6,FE,HALF,PHL0,EFF,S6,feed,STD,core,forces};
})();

/* ---------- 线环与供线（第 20 轮，动画 2-1、虚拟样机、综合调机共用） ----------
   线环成形：机针回升时凹口一侧的面线被布夹住，鼓成线环；大小随回升量的规律沿用动画 2-1 的示意模型（回升 2.2 mm 时最大）。
   供线：由第 4 章挑线机构算出（takeup.compute）。针眼入布后到钩线之前，机针要的线比挑线杆放下的多（欠线 neg），
   差 1 mm 以内靠线的弹性伸长消化（实验 4-1 的判据），超过 1 mm 线环开始张不开，到 3 mm 完全张不开（示意）。
   钩线以后绕梭需要的线（耗线量 D）若超过挑线杆放下的线（最小余量 margin < 0），旋梭硬拉面线，易断线。 */
const loop=(()=>{
  const W=(f,phc)=>{const r=f>180?needle.rise(f):0;return r<=0?0:Math.exp(-(((r-2.2)/1.0)**2));};
  const cache=new Map();
  function supply(o){
    const u=o.u||0,t=o.t==null?1.5:o.t,s=o.s==null?3:o.s,phc=Math.round(o.phc==null?206:o.phc),key=[u,t,s,phc].join('|');
    if(cache.has(key))return cache.get(key);
    const R=takeup.compute({mode:'link',u,t,s,phc,rpm:5000,lk:Object.assign({},takeup.LK0)},null);
    const k=R.ok?Math.max(0,Math.min(1,(3-R.neg)/2)):0;
    const r={ok:R.ok,neg:R.ok?R.neg:NaN,margin:R.ok?R.margin:NaN,pre:R.ok?R.pre:NaN,k,short:R.ok&&R.margin<0,R};
    if(cache.size>400)cache.clear();cache.set(key,r);return r;
  }
  return {W,supply};
})();

/* ---------- 整机：一套调机参数 → 各机构的判定（第 20 轮；虚拟样机的调机面板、实验 8-2 综合调机共用） ----------
   每个机构仍用它自己那一章的模型（实验 4-1、5-1、6-1、7-1、8-1），这里只把同一套参数分给它们，再把判定汇总成
   “故障 + 部位 + 原因 + 去哪个实验细看”。面料：lining 衬里、cotton 棉布、denim 牛仔（钩线模型按梭织物）。 */
const machine=(()=>{
  const STD={psi:0,dz:0,g:0.08,d:0.9,u:0,stroke:10,fab:'cotton',th:'t24',Td:100,Tb:40,dT:0,dP:0,h:0.8,P:1.0,s:3,n:5000,k:0.3,mode:'drop'};
  const FT={lining:0.4,cotton:1.5,denim:4.0};
  const L=(zh,en)=>({zh,en});
  function evaluate(c0){
    const c=Object.assign({},STD,c0||{}),out=[];
    const add=(key,sev,part,lab,title,cause)=>out.push({key,sev,part,lab,title,cause});
    // 钩线（第 5 章）与供线（第 4 章）
    const g=hook.geom({psi:c.psi,dz:c.dz,g:c.g,d:c.d,fab:'woven'});
    const sup=loop.supply({u:c.u,t:FT[c.fab],s:c.s,phc:g.fc});
    const margin=g.wAt*sup.k-(g.g+hook.TB);
    let res=g.res; if(res==='ok'&&margin<0)res='skip';
    if(res==='hit')add('hit','bad','hook','5-1',L('梭尖碰针','Hook point hits the needle'),L(`梭尖与机针的间隙只有 ${g.g.toFixed(2)} mm：响声、针尖起毛刺、断针。换了粗针（Nm ${Math.round(c.d*100)}）没有重调间隙最常见。`,`Hook-to-needle clearance only ${g.g.toFixed(2)} mm: noise, burred needle, broken needle. Most often a thicker needle (Nm ${Math.round(c.d*100)}) without resetting the clearance.`));
    else if(res==='cut')add('cut','bad','hook','5-1',L('梭尖划线（劈线、断线）','Hook point splits the thread'),L(`梭尖比针眼上沿只高 ${g.D.toFixed(2)} mm，从针眼附近划过：针杆太高，或钩线太晚。`,`The hook point passes only ${g.D.toFixed(2)} mm above the eye: needle bar too high, or catching too late.`));
    else if(res==='skip'){
      const why=sup.k<1&&g.margin>=0?L(`挑线杆供线不够：针眼入布后欠线 ${sup.neg.toFixed(1)} mm，线环张不开。`,`Take-up supply too short: ${sup.neg.toFixed(1)} mm short after the eye enters the fabric, so the loop cannot open.`)
        :g.h<2?L(`钩线太早：梭尖到达时机针只回升了 ${g.h.toFixed(2)} mm，线环还没张开。`,`Hook too early: the needle has risen only ${g.h.toFixed(2)} mm when the point arrives; the loop is not open yet.`)
        :g.h>2.5?L(`钩线太晚：机针已回升 ${g.h.toFixed(2)} mm，线环已在收缩。`,`Hook too late: the needle has risen ${g.h.toFixed(2)} mm; the loop is shrinking.`)
        :g.g>0.1?L(`梭尖离机针太远（间隙 ${g.g.toFixed(2)} mm），从线环外面滑过。`,`Hook point too far from the needle (clearance ${g.g.toFixed(2)} mm); it slides past outside the loop.`)
        :L(`梭尖高度不在线环里（梭尖高于针眼上沿 ${g.D.toFixed(2)} mm）：针杆高度不对。`,`The hook point is not at the height of the loop (${g.D.toFixed(2)} mm above the eye): needle-bar height is wrong.`);
      add('skip','bad','hook',sup.k<1&&g.margin>=0?'4-1':'5-1',L('跳针','Skipped stitches'),why);}
    if(sup.ok&&sup.margin<0)add('short','bad','tklever','4-1',L('绕梭时线不够（断线）','Thread too short round the bobbin case (breaks)'),L(`钩线到脱环之间，旋梭要的线比挑线杆放下的多 ${(-sup.margin).toFixed(1)} mm：旋梭硬拉面线，容易断线、线迹不匀。`,`Between catch and release the hook needs ${(-sup.margin).toFixed(1)} mm more thread than the take-up lever gives: it drags the upper thread, which breaks or tightens unevenly.`));
    if(sup.ok&&sup.pre>c.stroke)add('slack','warn','tklever','4-1',L('针眼入布前面线松垮','Upper thread slack before the eye enters'),L(`挑线杆放下的线多出挑线簧行程 ${(sup.pre-c.stroke).toFixed(1)} mm，面线松垮，可能被机针刺穿或绕住。`,`The lever releases ${(sup.pre-c.stroke).toFixed(1)} mm more than the check spring can hold: the thread goes slack and may be pierced or tangled.`));
    // 张力（第 7 章）
    const E=tension.ev({fab:c.fab,th:c.th,Td:c.Td,Tb:c.Tb,s:c.s,n:c.n});
    if(E.jam)add('jam','bad','tension','7-1',L('线太粗：结构性起皱','Thread too coarse: structural pucker'),L('这种布织得密，粗线和相应的粗针把纱线挤开、把布撑皱。换细一号的线和针。','This fabric is tightly woven; the coarse thread and needle push the yarns apart. Use a finer thread and needle.'));
    if(E.brk)add('tbreak','bad','tension','7-1',L('张力太大：断线','Tension too high: thread breaks'),L(`收紧时峰值张力 ${E.peak.toFixed(0)} cN，超过线的名义强力的三分之一。`,`Peak tension ${E.peak.toFixed(0)} cN exceeds a third of the thread strength.`));
    if(E.z>0.6)add('bobup','warn','tension','7-1',L('底线被拉到正面','Bobbin thread pulled to the top'),L('面线相对太紧或底线太松，交织点被拉向布面。','Upper thread relatively too tight (or bobbin too loose): the interlock is pulled to the top.'));
    else if(E.z<0.4)add('float','warn','tension','7-1',L('面线被拉到反面（浮线）','Upper thread pulled to the back (loops underneath)'),L('底线相对太紧或面线太松，交织点被拉向布底。','Bobbin thread relatively too tight (or upper too loose): the interlock is pulled to the underside.'));
    if(E.loose)add('loose','warn','tension','7-1',L('线迹太松','Loose stitches'),L(`较小的张力只有 ${Math.min(E.Tn,c.Tb).toFixed(0)} cN，收不紧线迹。`,`The lower of the two tensions is only ${Math.min(E.Tn,c.Tb).toFixed(0)} cN: the stitch is not pulled in.`));
    if(E.pk)add('pucker','bad','tension','7-1',L('张力起皱','Tension pucker'),L(`两根线的张力都偏高，缝线被拉长 ${E.shrink.toFixed(2)}%，缝好后回缩把布拉皱。`,`Both tensions too high: the thread is stretched ${E.shrink.toFixed(2)}% and shrinks back, puckering the seam.`));
    // 送布（第 6 章）
    const F=feed.model({fab:c.fab,mode:c.mode,s:c.s,dT:c.dT,dP:c.dP,h:c.h,P:c.P});
    if(F.marks.includes('dog'))add('dogmark','warn','dog','6-1',L('牙痕','Feed-dog marks'),L('牙太高，布上留下牙痕。','Teeth too high: marks on the fabric.'));
    if(F.marks.includes('foot'))add('footmark','warn','presser','6-1',L('压痕','Presser-foot marks'),L('压脚压力太大，布上留下压痕。','Foot pressure too high: marks on the fabric.'));
    if(F.eps<0.999)add('slip','warn','dog','6-1',L('打滑：针距变短','Slipping: stitches too short'),L(`压脚压力低于不打滑所需的 ${F.Pmin.toFixed(2)}，布只走了牙行程的 ${(F.eps*100).toFixed(0)}%。`,`Foot pressure below the ${F.Pmin.toFixed(2)} needed; the fabric moves only ${(F.eps*100).toFixed(0)}% of the dog stroke.`));
    if(F.drag>0.05)add('drag','bad','dog','6-1',L('机针在布中时布还在动（断针）','Fabric moves while the needle is in it (needle breaks)'),L(`布在针里被推着走了 ${F.drag.toFixed(2)} mm：针被带弯，重则撞上旋梭而断针。送布太晚。`,`The fabric is pushed ${F.drag.toFixed(2)} mm with the needle in it: the needle bends and may hit the hook. Feed too late.`));
    if(F.back>0.05)add('back','warn','dog','6-1',L('回拖','Back-drag'),L(`牙把布往回带了 ${F.back.toFixed(2)} mm，针距不匀。`,`The dog drags the fabric back ${F.back.toFixed(2)} mm; uneven stitches.`));
    if(F.ply>3)add('ply','warn','presser','6-1',L('上层布越缝越长：缝皱','Upper ply creeps: seam pucker'),L(`缝 40 cm 上层多出 ${F.ply.toFixed(1)} mm，多出的上层布在线迹之间拱起。`,`Over 40 cm the upper ply ends ${F.ply.toFixed(1)} mm longer and bulges between the stitches.`));
    // 整机惯性力（第 8 章）
    let fmax=0;for(const [x,y] of timing.forces({dt:0,dT:c.dT,n:c.n,k:c.k}))fmax=Math.max(fmax,Math.hypot(x,y));
    if(fmax>550)add('vib','warn','upper','8-1',L('振动大','Strong vibration'),L(`整机惯性力最大 ${fmax.toFixed(0)} N（${c.n} r/min，平衡率 ${c.k}）：平衡块与转速不配。`,`Peak inertia force ${fmax.toFixed(0)} N (${c.n} r/min, balance ratio ${c.k}): counterweight and speed do not match.`));
    return {cfg:c,faults:out,ok:!out.some(f=>f.sev==='bad'),hook:g,catch:res,supply:sup,tension:E,feed:F,fmax};
  }
  // 试缝 N 针：钩线带随机波动（同实验 5-1 的做法），其余机构的判定对每一针相同
  function trial(c0,n,seed){
    const ev=evaluate(c0),c=ev.cfg,R=hook.lcg(seed==null?7:seed),res=[];
    const g0=Object.assign({},ev.hook);
    for(let i=0;i<(n||30);i++){let r=hook.stitch(g0,{fab:'woven',dz:c.dz},R.gauss);
      if(r==='ok'&&ev.supply.k<1&&R.rnd()>ev.supply.k)r='skip';
      if(r==='ok'&&(ev.faults.some(f=>f.key==='short'||f.key==='tbreak'))&&R.rnd()<0.25)r='break';
      res.push(r);}
    return {ev,res};
  }
  // 综合调机（实验 8-2）的故障库：每种故障把一个参数改到出毛病的范围里（范围按上面的判据选定，保证试缝看得出来）
  const FAULTS=[
    {key:'hookEarly',p:'psi',lo:-22,hi:-15,zh:'旋梭定时太早',en:'Hook timed too early'},
    {key:'hookLate',p:'psi',lo:14,hi:20,zh:'旋梭定时太晚',en:'Hook timed too late'},
    {key:'barHigh',p:'dz',lo:0.75,hi:1.0,zh:'针杆太高',en:'Needle bar too high'},
    {key:'barLow',p:'dz',lo:-1.0,hi:-0.9,zh:'针杆太低',en:'Needle bar too low'},
    {key:'thickNeedle',p:'d',set:1.1,zh:'换了粗针没重调梭尖间隙',en:'Thicker needle fitted without resetting the hook clearance'},
    {key:'spring',p:'stroke',lo:5,hi:7,zh:'挑线簧行程太小',en:'Check-spring stroke too short'},
    {key:'guide',p:'u',lo:-12,hi:-9,zh:'过线板位置不对（放线太少）',en:'Thread guide set wrong (too little thread)'},
    {key:'upperTight',p:'Td',lo:220,hi:260,zh:'夹线器太紧',en:'Upper tension too tight'},
    {key:'upperLoose',p:'Td',lo:40,hi:50,zh:'夹线器太松',en:'Upper tension too loose'},
    {key:'bobbinLoose',p:'Tb',lo:14,hi:19,zh:'底线太松',en:'Bobbin tension too loose'},
    {key:'feedLate',p:'dT',lo:15,hi:25,zh:'送布定时太晚',en:'Feed timed too late'},
    {key:'dogLow',p:'h',lo:0.3,hi:0.5,zh:'送布牙太低',en:'Feed dog set too low'},
    {key:'footLight',p:'P',lo:0.4,hi:0.5,zh:'压脚压力不足',en:'Presser-foot pressure too low'},
    {key:'balance',p:'k',lo:0.9,hi:1.0,zh:'平衡块装错（平衡率太大）',en:'Wrong counterweight (balance ratio too high)'},
    {key:'balanceLow',p:'k',lo:0,hi:0.05,zh:'平衡块装错（平衡率太小）',en:'Wrong counterweight (balance ratio too low)'}];
  // 没收进故障库的：梭尖间隙偏大、送布定时偏早——在本模型里试缝看不出毛病（标准布料上钩线余量够大；牙提前落下不妨碍机针），出了题学生也无从诊断
  // 出题：level 个故障，同一参数不出两次；种子可复现（老师指定种子即同一台故障机）
  function generate(level,seed){
    const R=hook.lcg(seed>>>0||1);
    for(let attempt=0;attempt<50;attempt++){
      const pick=[],used=new Set();let guard=0;
      while(pick.length<level&&guard++<200){const f=FAULTS[Math.floor(R.rnd()*FAULTS.length)];if(used.has(f.p))continue;used.add(f.p);pick.push(f);}
      const c=Object.assign({},STD);
      for(const f of pick){c[f.p]=f.set!=null?f.set:Math.round((f.lo+R.rnd()*(f.hi-f.lo))*100)/100;}
      // 两个故障可能互相抵消（如针杆低又钩线晚）：试缝看不出毛病的不出，换一组
      const t=trial(c,30,seed);
      if(t.ev.faults.length||t.res.some(r=>r!=='ok'))return {cfg:c,faults:pick.map(f=>f.key)};
    }
    return {cfg:Object.assign({},STD,{psi:-18}),faults:['hookEarly']};
  }
  // 标准值附近的容差：调好以后，没有故障的参数应在这个范围里，否则算“乱调”
  const TOL={psi:3,dz:0.15,g:0.03,d:0,u:3,stroke:1.5,Td:20,Tb:8,dT:5,dP:5,h:0.1,P:0.2,s:0.3,n:0,k:0.1};
  return {STD,FT,evaluate,trial,FAULTS,generate,TOL};
})();

root.WQLS={DEG,needle,takeup,hook,feed,tension,timing,loop,machine,version:'2026-10-05'};
})(typeof window!=='undefined'?window:globalThis);
