// usage: node shot3d.js <lang> '<json for window.__set>' <out>
const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{const [,,lang,js,out,patch]=process.argv;
const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1280,height:800},deviceScaleFactor:2});
await p.route(/cdnjs\.cloudflare\.com.*three.*\.js/, r => r.fulfill({body: fs.readFileSync('/home/claude/sm/node_modules/three/build/three.min.js'), contentType:'application/javascript'}));
await p.route(/fonts\.(googleapis|gstatic)\.com/, r => r.fulfill({body:'', contentType:'text/css'}));
p.on('pageerror',e=>console.log('ERR',String(e)));
let url='file://'+path.resolve(`src/${lang}/labs/model-flatknit.html`);
if(patch){ // move label offsets: {"Label text":[dx,dy]} — works on a temporary copy, the lab itself is untouched
  let h=fs.readFileSync(path.resolve(`src/${lang}/labs/model-flatknit.html`),'utf8');
  for(const [k,v] of Object.entries(JSON.parse(patch))){const re=new RegExp("(\\['"+k.replace(/[()]/g,'\\$&')+"'.*?\\]),\\[-?\\d+,-?\\d+\\]\\],");h=h.replace(re,`$1,[${v[0]},${v[1]}]],`);}
  const tmp=path.join(path.dirname(path.resolve(out)),'_lab_'+process.pid+'.html');fs.writeFileSync(tmp,h);url='file://'+tmp;process.on('exit',()=>{try{fs.unlinkSync(tmp)}catch(e){}});}
await p.goto(url+'#capture',{waitUntil:'networkidle'});
await p.addStyleTag({content:'a[href*="index"]{display:none!important}'});
await p.waitForTimeout(1500);
await p.evaluate(o=>window.__set(o),JSON.parse(js));
await p.waitForTimeout(3000);
await p.screenshot({path:out,timeout:200000});await b.close();})();
