const { chromium } = require('playwright'); const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+path.resolve('src/zh/labs/timing.html'));await p.waitForTimeout(500);
const r=await p.evaluate(()=>{const A=window.__api;const STD=A.STD;const R=A.timing(Object.assign({},STD));
 const S=[],D=[];for(let i=0;i<360;i++){S.push(R.S(i));D.push(i<R.top?4.5:R.Dt[i]);}
 const F={};for(const n of [4000,5000,6000]){F[n]={};for(let k=0;k<=100;k+=1){const f=A.forces(Object.assign({},STD,{n,k:k/100}));F[n][k]=Math.max(...f.map(v=>Math.hypot(v[0],v[1])));}}
 const fr={};for(const k of [0,0.45,1])fr[k]=A.forces(Object.assign({},STD,{n:5000,k}));
 const win={};for(const key of ['dh','dt','dT']){win[key]=[];for(let d=-60;d<=20;d+=0.1){const o=Object.assign({},STD);o[key]=Math.round(d*10)/10;try{const t=A.timing(o);win[key].push([o[key],t.C.map(c=>c.ok)]);}catch(e){}}}
 return {S,D,top:R.top,F,fr,win};});
require('fs').writeFileSync('figsrc/en78/lab.json',JSON.stringify(r));await b.close();console.log('ok');})();
