// Re-render fig_ol3d_iso / fig_ol3d_xray from the English 3D lab. Usage: node figsrc/en_fig_ol3d.js
const DIST=+(process.env.DIST||680);
const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{const b=await chromium.launch();
for(const [mode,out,phi] of [['solid','img/en/fig_ol3d_iso.png',+(process.env.PHI_ISO||0)],['xray','img/en/fig_ol3d_xray.png',+(process.env.PHI_X||270)]]){
 const p=await b.newPage({viewport:{width:1280,height:800},deviceScaleFactor:2});
 await p.route(/three.*\.js/, r => r.fulfill({body: fs.readFileSync(path.resolve('node_modules/three/build/three.min.js')), contentType:'application/javascript'}));
 await p.route(/katex.*\.js/, r => r.fulfill({body: fs.readFileSync(path.resolve('node_modules/katex/dist/katex.min.js')), contentType:'application/javascript'}));
 await p.route(/fonts\.(googleapis|gstatic)\.com/, r => r.fulfill({body:'', contentType:'text/css'}));
 p.on('pageerror',e=>console.log('ERR',String(e)));
 await p.goto('file://'+path.resolve('src/en/labs/model-overlock.html')+'#capture',{waitUntil:'networkidle'});
 await p.waitForTimeout(800);
 await p.evaluate(([m,phi,DIST])=>{window.__still=true;document.querySelectorAll('a[href="../index.html"]').forEach(a=>a.remove());window.__set({mode:m,view:'iso',cam:[-0.65,0.42,+DIST],phi,labels:true,paths:true,foot:true});},[mode,phi,DIST]);
 await p.waitForTimeout(800);
 await p.screenshot({path:out}); await p.close(); console.log('ok',out);}
await b.close();})();
